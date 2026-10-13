@echo off
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0"

rem Usage 1: double click -> a folder picker window opens
rem Usage 2: drag a folder onto this bat -> rename that folder right away
rem (always shows a preview list and asks for confirmation first)

set "PY=C:\Users\lenovo\.workbuddy\binaries\python\versions\3.13.12\python.exe"
if not exist "%PY%" set "PY=python"

"%PY%" "%~dp0rename_qi.py" %*

echo.
echo Done. Press any key to close this window.
pause >nul
