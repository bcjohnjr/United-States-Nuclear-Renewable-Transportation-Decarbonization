@echo off
cd /d "%~dp0"
python us915_methane.py || exit /b 1
python us916_coupled.py || exit /b 1
python us916_figures.py || exit /b 1
python us916_validate.py || exit /b 1
