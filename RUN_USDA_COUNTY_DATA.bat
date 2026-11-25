@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if not errorlevel 1 (set "PY=py -3") else (set "PY=python")
echo USDA NASS 2022 and 2023 county harvest acreage, optional cross-check
%PY% us99_usda_quickstats_download.py
set "ERR=%ERRORLEVEL%"
pause
exit /b %ERR%
