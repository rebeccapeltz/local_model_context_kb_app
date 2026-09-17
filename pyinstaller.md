From your project folder (containing app.py, tool.py, tool_execution.py, context.py, static/index.html), 
run: 

macOS/Linux: 
pyinstaller --onefile --name knowledge_assistant --add-data "static:static" app.py

Windows: 
pyinstaller --onefile --name knowledge_assistant --add-data "static;static" app.py 

The only difference is the separator in --add-data (colon vs semicolon) — this is a longstanding PyInstaller quirk, not a typo.

