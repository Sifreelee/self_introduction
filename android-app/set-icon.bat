@echo off
setlocal
chcp 65001 >nul
REM ===========================================================
REM  Change the app icon and rebuild the APK in one step.
REM
REM  How to use:
REM    1) Drag an image file onto this bat file, or
REM    2) Double click it and pick the image in the dialog.
REM
REM  Output goes to the dist folder.
REM ===========================================================

set "PY=C:\Users\lenovo\.workbuddy\binaries\python\envs\default\Scripts\python.exe"
set "PROJ=%~dp0"
set "TMPF=%TEMP%\icon_pick.txt"

if not exist "%PY%" goto no_python

set "SRC=%~1"
if not "%SRC%"=="" goto have_src

echo No image given. Opening file picker ...
if exist "%TMPF%" del "%TMPF%" >nul 2>&1
powershell -NoProfile -STA -Command "Add-Type -AssemblyName System.Windows.Forms; $d = New-Object System.Windows.Forms.OpenFileDialog; $d.Title = 'Select icon image'; $d.Filter = 'Images|*.png;*.jpg;*.jpeg;*.webp;*.bmp'; if ($d.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) { [IO.File]::WriteAllText($env:TEMP + '\icon_pick.txt', $d.FileName) }"
if not exist "%TMPF%" goto cancelled

"%PY%" "%PROJ%set_icon.py" --pick "%TMPF%"
if errorlevel 1 goto build_fail
del "%TMPF%" >nul 2>&1
echo.
pause
exit /b 0

:have_src
if not exist "%SRC%" goto bad_src
"%PY%" "%PROJ%set_icon.py" "%SRC%"
if errorlevel 1 goto build_fail
echo.
pause
exit /b 0

:cancelled
echo No image selected.
echo If the picker did not open, drag an image file onto this bat instead.
pause
exit /b 1

:bad_src
echo [ERROR] File not found: %SRC%
pause
exit /b 1

:no_python
echo [ERROR] Python not found at:
echo   %PY%
pause
exit /b 1

:build_fail
echo [ERROR] Failed. See the log above.
pause
exit /b 1
