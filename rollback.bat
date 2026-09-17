@echo off
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0"
setlocal EnableDelayedExpansion

rem Usage 1: drag a "*_mapping.csv" file onto this bat
rem Usage 2: double click, then paste the csv path

set "CSV=%~1"
if "%CSV%"=="" (
  echo.
  echo   Restore original file names
  echo   Drag a mapping csv onto this file, or paste its path below.
  echo.
  set /p "CSV=mapping csv path: "
)
set "CSV=%CSV:"=%"

if "%CSV%"=="" (
  echo.
  echo   No csv given. Cancelled.
  pause >nul
  exit /b 1
)

if not exist "%CSV%" (
  echo.
  echo   File not found: %CSV%
  pause >nul
  exit /b 1
)

"C:\Users\lenovo\.workbuddy\binaries\python\versions\3.13.12\python.exe" "%~dp0rename_album.py" --rollback "%CSV%"
echo.
echo Done. Press any key to close this window.
pause >nul
endlocal
