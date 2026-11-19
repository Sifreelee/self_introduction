@echo off
cd /d "%~dp0"
set "TEMP=%~dp0.build\temp"
set "TMP=%TEMP%"
set "PYTHONPYCACHEPREFIX=%~dp0.build\pycache"
set "PYTHONUTF8=1"
if not exist "%TEMP%" mkdir "%TEMP%"
python app.py
if errorlevel 1 pause
