@echo off
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0"
setlocal EnableDelayedExpansion

rem ============================================================
rem   Photo tools launcher
rem     1) Compress            resize + convert everything to jpg
rem     2) Rename              number the photos + build the list
rem     3) Compress, then rename
rem     0) Exit
rem   Tip: drag a folder onto this bat to set the target folder.
rem ============================================================

set "PY=C:\Users\lenovo\.workbuddy\binaries\python\versions\3.13.12\python.exe"
set "FOLDER="
set "SEL="

rem First argument: either a folder (drag & drop) or a menu number
if not "%~1"=="" (
  if exist "%~1\" ( set "FOLDER=%~1" ) else ( set "SEL=%~1" )
)

:MENU
cls
echo.
echo   ==================================================
echo     Photo tools
echo   ==================================================
echo.
echo      1) Compress                 resize + to jpg
echo      2) Rename                   number + list
echo      3) Compress, then rename
echo      0) Exit
echo.
if defined FOLDER echo   Target folder: "%FOLDER%"
echo.
rem Default is 0 (= exit), so an empty input can never loop forever
set "SEL=0"
set /p "SEL=Pick 1 / 2 / 3 / 0 : "
if "%SEL%"=="0" goto END
if "%SEL%"=="1" goto ASK_DIR
if "%SEL%"=="2" goto DO_RENAME
if "%SEL%"=="3" goto ASK_DIR
echo   Unknown option: %SEL%
pause >nul
goto MENU

:ASK_DIR
if defined FOLDER goto RUN_STEP
echo.
echo   Leave it empty to use assets\images
echo.
set /p "FOLDER=Folder to compress: "
set "FOLDER=%FOLDER:"=%"
if not defined FOLDER set "FOLDER=%CD%\assets\images"
if not exist "%FOLDER%\" (
  echo.
  echo   Folder not found: "%FOLDER%"
  pause >nul
  set "FOLDER="
  goto MENU
)

:RUN_STEP
echo.
echo --------------------------------------------------
echo   Step 1 / 2 : Compressing
echo --------------------------------------------------
"%PY%" "%~dp0compress.py" --dir "%FOLDER%" --no-dialog
if errorlevel 1 goto FAILED
if "%SEL%"=="1" goto DONE
echo.
echo --------------------------------------------------
echo   Step 2 / 2 : Renaming
echo --------------------------------------------------
if /i not "%FOLDER%"=="%CD%\assets\images" (
  echo   The renamer will ask for a folder again, paste this:
  echo     %FOLDER%
)
"%PY%" "%~dp0rename_album.py"
if errorlevel 1 goto FAILED
goto DONE

:DO_RENAME
echo.
echo --------------------------------------------------
echo   Renaming
echo --------------------------------------------------
"%PY%" "%~dp0rename_album.py"
if errorlevel 1 goto FAILED
goto DONE

:FAILED
echo.
echo   Something went wrong - see the message above.
pause >nul
goto MENU

:DONE
echo.
echo   Done. Press any key to go back to the menu.
pause >nul
set "FOLDER="
goto MENU

:END
endlocal
