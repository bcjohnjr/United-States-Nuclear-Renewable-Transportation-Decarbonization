@echo off
setlocal
pushd "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  py -3 us914_validate.py
) else (
  python us914_validate.py
)
set "EXITCODE=%ERRORLEVEL%"
popd
exit /b %EXITCODE%
