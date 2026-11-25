@echo off
setlocal
pushd "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  py -3 us9141_repo_check.py && py -3 us914_validate.py --full
) else (
  python us9141_repo_check.py && python us914_validate.py --full
)
set "RC=%ERRORLEVEL%"
popd
if not "%RC%"=="0" echo VALIDATION FAILED. Confirm Python 3.11+ and pip install -r requirements-v914.txt
exit /b %RC%
