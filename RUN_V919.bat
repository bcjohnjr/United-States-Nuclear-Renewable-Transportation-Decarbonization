@echo off
cd /d "%~dp0"
python us919_sweetspot.py || exit /b 1
python us919_figures.py || exit /b 1
python us919_map_reproduce.py || exit /b 1
python us919_validate.py || exit /b 1
