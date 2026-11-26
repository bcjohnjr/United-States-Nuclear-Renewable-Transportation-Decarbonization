@echo off
cd /d "%~dp0"
python VERIFY_GITHUB_V918.py %*
if errorlevel 1 exit /b 1
