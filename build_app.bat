@echo off
REM === Clean old builds ===
rmdir /s /q build
rmdir /s /q dist

REM === Build ===
pyinstaller ^
  --onefile ^
  --noconsole ^
  --name "ChakraAnalyzer" ^
  --icon=app_icon.ico ^
  main.py

echo Build complete! Find your exe in the "dist" folder.
pause
