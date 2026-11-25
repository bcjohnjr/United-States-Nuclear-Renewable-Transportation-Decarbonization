@echo off
setlocal EnableExtensions
cd /d "%~dp0"
echo ==========================================================
echo DOE/ORNL BT23 V9.10 COUNTY-RESOURCE DATA CHECK
 echo This tool cannot log in on your behalf.
echo ==========================================================
echo.
set "BT23_PATH=%~1"
if not defined BT23_PATH set "BT23_PATH=BT23_EXPORTS.zip"
if not exist "%BT23_PATH%" if exist "BT23_EXPORTS" set "BT23_PATH=BT23_EXPORTS"
if not exist "%BT23_PATH%" (
 echo No export found. Open the official ORNL site and save the actual downloaded CSV files in BT23_EXPORTS.
 echo https://bioenergykdf.ornl.gov/bt23-agricultural-download
 start "" "https://bioenergykdf.ornl.gov/bt23-agricultural-download"
 pause
 exit /b 2
)
where py >nul 2>&1
if %errorlevel%==0 (py -3 us910_bt23_evidence_gate.py --inspect "%BT23_PATH%") else (python us910_bt23_evidence_gate.py --inspect "%BT23_PATH%")
set "RC=%errorlevel%"
echo.
echo Status report: BT23_V910_EVIDENCE_STATUS.json
if not "%RC%"=="0" echo No official regional quantities have been loaded into the model.
echo After approval, rerun using the official CSV/ZIP exports.
pause
exit /b %RC%
