@echo off
cd /d "%~dp0"
python us917_validate.py --inputs-only || exit /b 1
python us915_methane.py || exit /b 1
python us916_coupled.py || exit /b 1
python us917_evidence.py || exit /b 1
python us917_figures.py || exit /b 1
python us917_validate.py || exit /b 1
