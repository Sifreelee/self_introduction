@echo off
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0"
echo.
echo   Album photo renamer - answer the questions, press Enter to confirm.
echo.
"C:\Users\lenovo\.workbuddy\binaries\python\versions\3.13.12\python.exe" "%~dp0rename_album.py"
echo.
echo Done. Press any key to close this window.
pause >nul
