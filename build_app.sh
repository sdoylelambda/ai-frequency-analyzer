#!/bin/bash
# === Clean old builds ===
rm -rf build dist

# === Build ===
pyinstaller \
  --onefile \
  --noconsole \
  --name "ChakraAnalyzer" \
  --icon app_icon.icns \
  main.py

echo "Build complete! Find your app in the dist folder."
