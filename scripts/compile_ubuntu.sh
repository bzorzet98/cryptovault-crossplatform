#!/bin/bash
# compile_ubuntu.sh

# --onefile: bundle into one file
# --windowed: no terminal window
# --add-data: includes assets folder (format: source:destination)
pyinstaller --onefile --windowed \
            --name="my_app" \
            --add-data="assets:assets" \
            src/main.py

echo "Build complete. Check the dist/ folder."