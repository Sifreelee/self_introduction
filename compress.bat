@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Compressing photos, please wait...
echo.
"C:\Users\lenovo\.workbuddy\binaries\python\versions\3.13.12\python.exe" "%~dp0compress.py"
echo.
echo Done. Press any key to close this window.
pause >nul
