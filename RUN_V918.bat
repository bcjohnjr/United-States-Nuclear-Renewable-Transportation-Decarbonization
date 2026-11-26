@echo off
cd /d "%~dp0"
call RUN_V917.bat || exit /b 1
python us918_evidence.py || exit /b 1
python us918_figures.py || exit /b 1
python us918_validate.py || exit /b 1
