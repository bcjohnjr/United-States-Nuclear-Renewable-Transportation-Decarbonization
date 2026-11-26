@echo off
cd /d "%~dp0"
python us915_methane.py > us915_validation.txt
if errorlevel 1 exit /b 1
python us915_figures.py
if errorlevel 1 exit /b 1
echo V9.15 methane extension reproduced. Existing corrected figures remain unchanged.
