"""
Flask web app for the Personal Knowledge Assistant.

This exposes the same agent-based chat flow that used to run as a CLI
loop (see the original main.py), as a small set of JSON endpoints plus
a minimal browser UI for trying it out.

Session model
-------------
Flask's request/response cycle is stateless, but the agent needs a
running `messages` list (system prompt + turns + tool calls) per user.
This is handled with a lightweight in-memory session store:

  POST /api/session          -> start a new conversation, get a session_id
  POST /api/context          -> optionally load ./context_files into that
                                 session's history (mirrors the CLI's
                                 yes/no prompt; the read itself is always
                                 deterministic)
  POST /api/chat             -> send a user message, run the agent loop
                                 (including any tool calls), get the reply
  GET  /api/history/<id>     -> fetch the full transcript for a session

NOTE: SESSIONS is a plain process-local dict, which is fine for local
development (`flask run`, a single process). It will NOT survive a
restart and will NOT be shared correctly across multiple worker
processes (e.g. `gunicorn -w 4`). For anything beyond a local demo,
replace SESSIONS with a real store (Redis, a database, flask-session)
keyed the same way by session_id.
"""

import sys
import uuid
from pathlib import Path

import bleach
import markdown
from flask import Flask, jsonify, request
from openai import OpenAI

import context
import tool
import tool_execution


def resource_path(relative_path: str) -> str:
  """Resolve a bundled resource (like the static/ folder) whether running
  from source or from a PyInstaller-built executable.

  PyInstaller's --onefile mode extracts everything into a temporary
  directory at startup and exposes that location as sys._MEIPASS. When
  running normally from source, that attribute doesn't exist, so this
  falls back to the current directory. Only used for bundled, read-only
  assets (static/) — NOT for the knowledge base or context files, which
  intentionally stay relative to wherever the user launches the app from
  (see KB_DIR / CONTEXT_DIR below).
  """
  # base_path = getattr(sys, "_MEIPASS", Path(".").resolve())
  # return str(Path(base_path) / relative_path)
  if getattr(sys, 'frozen', False):
    base_path = Path(sys._MEIPASS)
  else:
    base_path = Path(__file__).resolve().parent
  return str(base_path / relative_path)

# Tags/attributes allowed through to the browser after markdown rendering.
# Keeps things like headings, code blocks, tables, and links, while
# stripping anything a model (or injected context file) could use to run
# script in the page — <script>, inline event handlers, javascript: URLs.
_ALLOWED_TAGS = [
    "p", "br", "hr",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "strong", "em", "b", "i", "code", "pre", "blockquote",
    "ul", "ol", "li",
    "a", "img",
    "table", "thead", "tbody", "tr", "th", "td",
]
_ALLOWED_ATTRS = {
    "a": ["href", "title", "rel", "target"],
    "img": ["src", "alt", "title"],
}


def render_markdown_safe(md_text: str) -> str:
  """Convert markdown to HTML for display, then sanitize it.

  The raw markdown itself is never modified — this is only used to build
  the `response_html` field returned to the browser. session["messages"]
  and anything saved to disk always keep the original markdown string.
  """
  html = markdown.markdown(
      md_text or "",
      extensions=["fenced_code", "tables", "sane_lists", "nl2br"],
  )
  return bleach.clean(html, tags=_ALLOWED_TAGS, attributes=_ALLOWED_ATTRS)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CONTEXT_DIR = Path("./context_files").resolve()
CONTEXT_DIR.mkdir(parents=True, exist_ok=True)

SYSTEM_INSTRUCTION = (
    "You are a personal learning assistant. Your goal is to explain concepts "
    "clearly. "
    "You have access to a tool (`save_note_to_disk`) that saves markdown "
    "notes on disk. "
    "NEVER call `save_note_to_disk` unless the user explicitly requests to "
    "save, log, or archive."
)

# session_id -> {"messages": [...]}
SESSIONS: dict[str, dict] = {}

# Shared client pointed at the local LM Studio server.
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

# app = Flask(__name__, static_folder=resource_path("static"), static_url_path="")
# Initialize Flask with the safe resource paths
app = Flask(
    __name__, 
    static_folder=resource_path("static"), 
    static_url_path=""
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _get_session(session_id):
  return SESSIONS.get(session_id)


def _total_content_size(messages: list) -> int:
  """Rough character count across all messages with string content
  (mirrors the original CLI's total_content_size)."""
  size = 0
  for item in messages:
    content = item.get("content")
    if isinstance(content, str):
      size += len(content)
  return size


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
  return app.send_static_file("index.html")


@app.route("/api/session", methods=["POST"])
def create_session():
  """Start a new conversation."""
  session_id = str(uuid.uuid4())
  SESSIONS[session_id] = {
      "messages": [{"role": "system", "content": SYSTEM_INSTRUCTION}],
  }
  return jsonify({"session_id": session_id})


@app.route("/api/context", methods=["POST"])
def load_context():
  """
  Equivalent of the CLI's "Would you like to load local context files?"
  prompt: the user decides whether to run the read; the read itself is
  always the same deterministic scan of ./context_files.
  """
  data = request.get_json(silent=True) or {}
  session_id = data.get("session_id")
  want_context = bool(data.get("load_context", False))

  session = _get_session(session_id)
  if session is None:
    return jsonify({"error": "Unknown session_id"}), 404

  if not want_context:
    return jsonify({"loaded": False, "message": "Context loading skipped."})

  context_string = context.load_context(CONTEXT_DIR)
  if not context_string:
    return jsonify({
        "loaded": False,
        "message": f"No markdown files found in {CONTEXT_DIR}.",
    })

  session["messages"].append({
      "role": "user",
      "content": f"Here is my reference context for our session:\n\n{context_string}",
  })
  session["messages"].append({
      "role": "assistant",
      "content": (
          "Thank you. I have loaded all context files into memory and am "
          "ready to answer your questions using this information."
      ),
  })
  return jsonify({"loaded": True, "message": "Context loaded successfully."})


@app.route("/api/chat", methods=["POST"])
def chat():
  """Send a user message, run the agent loop (including tool calls),
  and return the assistant's reply."""
  data = request.get_json(silent=True) or {}
  session_id = data.get("session_id")
  user_input = (data.get("message") or "").strip()

  session = _get_session(session_id)
  if session is None:
    return jsonify({"error": "Unknown session_id"}), 404
  if not user_input:
    return jsonify({"error": "message is required"}), 400

  session["messages"].append({"role": "user", "content": user_input})

  try:
    ai_response = tool_execution.process_agent_turn(
        client,
        session["messages"],
        tool.tools,
        tool.available_functions,
        tool_choice="auto",
    )
  except Exception as e:
    return jsonify({"error": f"Agent error: {e}"}), 500

  return jsonify({
      "response": ai_response,               # raw markdown — unchanged
      "response_html": render_markdown_safe(ai_response),  # for display only
      "content_size": _total_content_size(session["messages"]),
  })


@app.route("/api/history/<session_id>", methods=["GET"])
def history(session_id):
  session = _get_session(session_id)
  if session is None:
    return jsonify({"error": "Unknown session_id"}), 404
  return jsonify({"messages": session["messages"]})


if __name__ == "__main__":
  # Port 5000 is claimed by macOS's AirPlay Receiver on many Macs, so this
  # defaults to 5500 instead. Whatever port you use, open the app through
  # Flask itself (http://localhost:5500/) rather than opening static/index.html
  # directly or via a separate static file server — the page's fetch() calls
  # are relative paths and need to hit this same Flask server.
  PORT = 5500
  IS_FROZEN = getattr(sys, "frozen", False)  # True inside a PyInstaller build

  if IS_FROZEN:
    # debug=True's auto-reloader re-executes the running process on file
    # changes, which doesn't make sense (and can misbehave) inside a
    # bundled executable — there's no source file for it to watch anyway.
    import threading
    import webbrowser

    def _open_browser():
      webbrowser.open(f"http://localhost:{PORT}/")

    # Give the server a moment to start listening before opening the tab.
    threading.Timer(1.0, _open_browser).start()
    app.run(debug=False, port=PORT)
  else:
    app.run(debug=True, port=PORT)
