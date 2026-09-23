# LM Studio Agent

## VS Code
- Command Pallete  CTL-SHFT-P (windows)  cmd-shft-p(MAC)
- Create Environment
## Create Virutal Environment

```zsh
python -m venv .venv
source .venv/bin/activate
pip install ....
pip install -r requirements.txt
pip freeze > requirements.txt
deactivate
python app.py
```
If using VS Code, make sure that your pointing to the python in your venv


## Test Queries Using Popular Legal Words

Create a contract that binds me to deliver a 1 hours talk online. I will be paid for the talk.  I must be able to share notes from the talk online.

## System Prompt

You are a precise, helpful AI assistant. Answer the user's question accurately, concisely, and directly. 

Rules:
- Rely only on clear facts. Do not invent or guess information if you do not know.
- Keep your answers short unless the user asks for detailed explanations.
- Use clear formatting like bullet points when listing multiple items.
- Avoid filler words, polite fluff, or repeating the user's question back to them.			

Legal Prompt: Create a contract that binds me to deliver a 1 hours talk online. I will be paid for the talk.  I must be able to share notes from the talk online.

Save to folder: Save to my Legal folder

## PyInstaller Executable

### Apple

#### Clear Previous PyInstaller Build if Exists

```bash
rm -rf build/ dist/ app.spec
```
#### Run Pyinstaller

```bash
pyinstaller --onefile \
  --add-data "static:static" \
  --distpath ./apple-dist/knowledge_assistant \
  app.py
```

#### Run app
```bash
./apple-dist/knowledge_assistant/app
```

### Windows

#### Run installer with ; instead of :
```
pyinstaller --onefile --windowed --add-data "static;static" --distpath .\windows-dist\knowledge_assistant app.py
```

#### Add windows icon
```
pyinstaller --onefile --windowed --icon=logo.ico --add-data "static;static" --distpath .\windows-dist\knowledge_assistant app.py
```

#### Build Windows using build_win.bat
```
@echo off
echo Cleaning up old build files...
rmdir /s /q build dist
del /q app.spec
echo Starting PyInstaller Build...
pyinstaller --onefile --windowed --add-data "static;static" --distpath .\windows-dist\knowledge_assistant app.py
echo Build Complete! Check the windows-dist folder.
pause
```
1. Open the Command Prompt (search for cmd in the Windows Start Menu).
2. Navigate to your project directory using the cd command (e.g., cd path\to\your\project).
3. Make sure you clear out the old cache folders (build/, dist/, and any .spec files) just like you did on the Mac before running the new command.
4. Run the Windows compilation command (remembering to use the semicolon ; for --add-data).





### Apple Can Have Problems with PyInstaller
Use this code to ensure you get the executable stored in the correct location.  You can set up the directory structure as you chose.

```bash
pyinstaller --distpath ./apple-dist app.py
```


```
chmod +x apple-dist/knowledge_assistant
```

- Clear Apple Quarantine

```
xattr -d com.apple.quarantine apple-dist/knowledge_assistant
```