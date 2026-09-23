@echo off
echo Cleaning up old build files...
rmdir /s /q build dist
del /q app.spec
echo Starting PyInstaller Build...
pyinstaller --onefile --windowed --add-data "static;static" --distpath .\windows-dist\knowledge_assistant app.py
echo Build Complete! Check the windows-dist folder.
pause
