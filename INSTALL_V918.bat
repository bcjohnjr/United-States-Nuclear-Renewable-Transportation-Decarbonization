@echo off
cd /d "%~dp0"
python -m pip install -r requirements-v918.txt || exit /b 1
