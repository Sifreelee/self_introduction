@echo off
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0"
setlocal EnableDelayedExpansion

rem Usage 1: drag a "*_重命名对照表.csv" file onto this bat
rem Usage 2: double click, then paste the csv path

set "CSV=%~1"
if "%CSV%"=="" (
  echo.
  echo   Restore original file names  (其一/其二 -> original)
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

set "PY=C:\Users\lenovo\.workbuddy\binaries\python\versions\3.13.12\python.exe"
if not exist "%PY%" set "PY=python"

"%PY%" "%~dp0rename_qi.py" --rollback "%CSV%"

echo.
echo Done. Press any key to close this window.
pause >nul
endlocal
