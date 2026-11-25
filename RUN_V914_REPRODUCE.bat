@echo off
setlocal
pushd "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  py -3 us914_validate.py --full
) else (
  python us914_validate.py --full
)
set "EXITCODE=%ERRORLEVEL%"
popd
if not "%EXITCODE%"=="0" echo V9.14 REPRODUCTION FAILED. Install requirements-v914.txt and inspect the errors.
exit /b %EXITCODE%
