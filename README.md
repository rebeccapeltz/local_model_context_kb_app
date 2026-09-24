# LM Studio Knowledge Assistant

A Flask web app for a local, agent-based learning assistant. Ask a
question, get a markdown answer from a local model (via LM Studio),
and optionally save the answer as a markdown note in a local
knowledge base.

Originally a CLI tool; reworked as a Flask app with a browser UI so it
can be packaged as a single executable for non-technical users
(students) to double-click and run.

## Prerequisites

- Python 3.10+
- [LM Studio](https://lmstudio.ai) installed, with a model loaded and
  its local server running on `http://localhost:1234`. **The app will
  start fine without this, but every question will fail** — LM Studio
  is a separate program and isn't bundled by anything below.

## Running from source

```zsh
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open **http://localhost:5500/** — not `5000`. Port 5000 is commonly
claimed by macOS's AirPlay Receiver, so the app defaults to 5500
instead.

The page auto-starts a session, lets you choose whether to load
`context_files/` into memory, and gives you a chat box. Both
`context_files/` and `my_knowledge_base/` are created automatically
next to `app.py` the first time they're needed — nothing to set up by
hand.

To save an answer, just ask in plain language, e.g.:

### Save to a folder under `my_knowledge_base`
For example, if you want to save the LLM Response dealing with a legal question, prompt with:
`Save that to a folder called Legal`

## Building a standalone executable

Students should only ever need **one file** — the built executable.
None of the source, `static/`, or a Python install needs to travel
with it; `--add-data` bundles `static/index.html` directly into the
binary.

**Clear any previous build first**, using whatever `--name` you built
with last time (the generated `.spec` file is named after it, not
always `app.spec`):

```bash
rm -rf build dist *.spec        # macOS/Linux
# rmdir /s /q build dist && del /q *.spec      Windows (cmd)
```

### macOS

```bash
pyinstaller --onefile --name=app-mac --distpath=. --add-data "static:static" app.py
./app-mac
```

If you downloaded a pre-built binary rather than building it
yourself, macOS may attach a quarantine flag that blocks it from
running:

```bash
chmod +x app-mac
xattr -d com.apple.quarantine app-mac
```

### Windows

```
pyinstaller --onefile --name=app-windows --distpath=. --add-data "static;static" app.py
```

Run the result by double-clicking `app-windows.exe`.

> **The `--add-data` flag is required.** Without it, the exe starts
> with no errors but the browser can't find the page — `static/`
> never got bundled in. This is the one thing most worth
> double-checking if a build "runs but the page 404s."
>
> Also note the separator differs by OS: `:` on macOS/Linux, `;` on
> Windows.

Optional: `--icon=logo.ico` adds a custom icon on Windows. A batch
file (`build-win.bat`) wrapping the clean + build steps is handy if
you're rebuilding often:

```bat
@echo off
echo Cleaning up old build files...
rmdir /s /q build dist
del /q app-windows.spec
echo Starting PyInstaller Build...
pyinstaller --onefile --name=app-windows --distpath=. --add-data "static;static" app.py
echo Build Complete!
pause
```

### Distributing to students

Each student needs only the single executable — download it, place
it in any folder, make sure LM Studio is running, double-click.
`context_files/` and `my_knowledge_base/` will appear next to it
automatically. If you want students to start with reference material
already loaded, include a `context_files/` folder (that exact name)
alongside the exe with your `.md` files in it.

Distribute built executables via **GitHub Releases**, not the repo
itself — they're too large for git (100MB+) and don't belong in
version control. Build artifacts (`build/`, `dist/`, `*.spec`,
`__pycache__/`) should be gitignored too:

```
build/
dist/
__pycache__/
*.pyc
```

## Example prompt

> Create a contract that binds me to deliver a 1 hour talk online. I
> will be paid for the talk. I must be able to share notes from the
> talk online.
>
> Save to folder: Legal

## VS Code setup

- Command Palette: `Cmd+Shift+P` (Mac) / `Ctrl+Shift+P` (Windows) →
  "Python: Create Environment"
- Make sure VS Code's selected Python interpreter points at
  `.venv`, not a system Python
