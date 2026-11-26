@echo off
cd /d "%~dp0"
python -m pip install -r requirements-v917.txt || exit /b 1
