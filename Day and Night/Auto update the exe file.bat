@echo off
python -m PyInstaller --onefile --add-data "Assets;Assets" "Day and night.py"
pause