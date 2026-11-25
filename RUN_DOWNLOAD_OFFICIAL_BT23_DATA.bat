@echo off
cd /d "%~dp0"
echo V9.10 strict official-export evidence check is now the authoritative importer.
call RUN_V910_CHECK_BT23_EXPORT.bat %*
