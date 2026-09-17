@echo off
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0"
echo.
echo   Image compressor - compress in place, no backup kept.
echo   Drag a folder onto this file, or press Enter for assets\images
echo.

if "%~1"=="" (
  "C:\Users\lenovo\.workbuddy\binaries\python\versions\3.13.12\python.exe" "%~dp0compress.py"
) else (
  "C:\Users\lenovo\.workbuddy\binaries\python\versions\3.13.12\python.exe" "%~dp0compress.py" --dir "%~1"
)

echo.
echo Done. Press any key to close this window.
pause >nul
