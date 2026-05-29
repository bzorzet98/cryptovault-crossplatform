@echo off
:: compile_windows.bat

pyinstaller --onefile --windowed ^
            --name="my_app" ^
            --add-data="assets;assets" ^
            src/main.py

echo Build complete.
pause