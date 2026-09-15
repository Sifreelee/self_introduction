@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title One-click GitHub Upload

echo ============================================================
echo   One-click GitHub Upload  (personal-website)
echo ============================================================
echo.

rem ---------- 1. locate git.exe ----------
set "GITEXE="
for %%P in (
  "C:\Program Files\Git\bin\git.exe"
  "C:\Program Files\Git\cmd\git.exe"
  "C:\Program Files (x86)\Git\bin\git.exe"
  "C:\Program Files (x86)\Git\cmd\git.exe"
) do if not defined GITEXE if exist "%%~P" set "GITEXE=%%~P"
if not defined GITEXE for /f "delims=" %%P in ('where git 2^>nul') do if not defined GITEXE set "GITEXE=%%P"
if not defined GITEXE (
  echo [ERROR] Git is not installed on this computer.
  echo Please install it from: https://git-scm.com/
  echo.
  pause
  exit /b 1
)
echo Git found: !GITEXE!
echo.

rem ---------- 2. init repository if needed ----------
if not exist ".git" (
  echo First run: creating a git repository here...
  "!GITEXE!" init
  "!GITEXE!" branch -M main
  echo Done.
  echo.
)

rem ---------- 3. git identity (needed for the first commit) ----------
"!GITEXE!" config user.email >nul 2>nul
if errorlevel 1 (
  echo Tell git who you are ^(only once, saved forever^):
  set "GNAME="
  set /p GNAME=  Your name : 
  set "GMAIL="
  set /p GMAIL=  Your email: 
  "!GITEXE!" config user.name "!GNAME!"
  "!GITEXE!" config user.email "!GMAIL!"
  echo Saved.
  echo.
)

rem ---------- 4. remote address ----------
echo Folder: %CD%
set "CURURL="
for /f "delims=" %%U in ('"!GITEXE!" config --get remote.origin.url 2^>nul') do set "CURURL=%%U"
if defined CURURL (
  echo Already linked to GitHub:
  echo   !CURURL!
  set "KEEP=y"
  set /p KEEP=Use this repo? Y/n: 
  if /i "!KEEP!"=="n" (
    set "NEWURL="
    set /p NEWURL=Paste the new repo URL: 
    if defined NEWURL (
      "!GITEXE!" remote set-url origin !NEWURL!
      set "CURURL=!NEWURL!"
      echo Address updated.
    ) else (
      echo Keeping the old address.
    )
  )
  echo.
) else (
  echo Not linked to any GitHub repo yet.
  echo Paste your repo URL, for example:
  echo   https://github.com/yourname/my-site.git
  echo.
  set "CURURL="
  set /p CURURL=Repo URL: 
  if not defined CURURL (
    echo.
    echo [ERROR] No URL entered. Nothing was uploaded.
    pause
    exit /b 1
  )
  "!GITEXE!" remote add origin !CURURL! >nul 2>nul
  if errorlevel 1 (
    "!GITEXE!" remote set-url origin !CURURL!
  )
  echo Linked.
  echo.
)

rem ---------- 4b. current branch ----------
set "BRANCH=main"
for /f "delims=" %%B in ('"!GITEXE!" rev-parse --abbrev-ref HEAD 2^>nul') do set "BRANCH=%%B"

rem ---------- 5. reject oversized files (GitHub limit) ----------
echo Checking for files over 25MB...
powershell -NoProfile -ExecutionPolicy Bypass -Command "if (Get-ChildItem -Path . -Recurse -File -Force -ErrorAction SilentlyContinue | Where-Object { $_.FullName -notmatch '\\.git\\' -and $_.Length -gt 25MB }) { exit 1 } else { exit 0 }"
if not errorlevel 1 goto SIZE_OK
echo.
echo [STOPPED] These files are too big for GitHub:
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-ChildItem -Path . -Recurse -File -Force -ErrorAction SilentlyContinue | Where-Object { $_.FullName -notmatch '\\.git\\' -and $_.Length -gt 25MB } | ForEach-Object { Write-Host ('   ' + [math]::Round($_.Length/1MB,1) + ' MB  ' + $_.FullName) }"
echo.
echo Please run compress.bat first, then run this again.
echo.
pause
exit /b 1
:SIZE_OK

rem ---------- 6. commit message ----------
set "MSG="
set /p MSG=Commit note (press Enter to use "site update"): 
if not defined MSG set "MSG=site update"

rem ---------- 7. add / commit / push ----------
echo.
echo Adding all files...
"!GITEXE!" add -A

"!GITEXE!" diff --cached --quiet
if not errorlevel 1 goto NO_COMMIT

echo Creating commit...
"!GITEXE!" commit -m "!MSG!"
if not errorlevel 1 goto DO_PUSH
echo.
echo [ERROR] Commit failed. Nothing was uploaded.
echo.
pause
exit /b 1

:NO_COMMIT
echo No new changes to commit.
set "AHEAD=0"
for /f "delims=" %%C in ('"!GITEXE!" rev-list --count origin/!BRANCH!..HEAD 2^>nul') do set "AHEAD=%%C"
if "!AHEAD!"=="0" goto NOTHING_TODO
echo.
echo Found !AHEAD! commit(s) that were never uploaded. Sending them now...
goto DO_PUSH

:NOTHING_TODO
echo.
echo Nothing changed since the last upload. Nothing to do.
echo.
pause
exit /b 0

:DO_PUSH
echo.
echo Uploading to GitHub (branch !BRANCH!) ...
echo If a login window pops up, sign in with your GitHub account.
echo.
"!GITEXE!" push -u origin !BRANCH!
if not errorlevel 1 goto PUSH_OK

echo.
echo ============================================================
echo  The GitHub repo already has files from an earlier upload.
echo  How do you want to continue?
echo ============================================================
echo.
echo   1 = Keep my version, merge the old files in  (recommended)
echo   2 = Replace everything on GitHub with mine   (old files deleted)
echo   3 = Cancel, upload nothing
echo.
echo  Note: your website address stays the same either way.
echo.
set "CHOICE=1"
set /p CHOICE=Enter 1, 2 or 3 (default 1): 
if "!CHOICE!"=="2" goto FORCE_PUSH
if "!CHOICE!"=="1" goto MERGE_PUSH
if "!CHOICE!"=="" goto MERGE_PUSH
echo.
echo Cancelled. Nothing was uploaded.
echo.
pause
exit /b 1

:MERGE_PUSH
echo.
echo Merging. Where a file differs, YOUR local version wins...
echo.
"!GITEXE!" pull origin !BRANCH! --allow-unrelated-histories -X ours --no-edit
if errorlevel 1 (
  "!GITEXE!" merge --abort >nul 2>nul
  echo.
  echo [ERROR] Merge failed. Possible reasons:
  echo   1. Not logged in - sign in when the window pops up.
  echo   2. No network / proxy problem - try again in a moment.
  echo   3. Repo does not exist - create it on GitHub first.
  echo.
  echo Nothing was changed. Your files are safe.
  echo.
  pause
  exit /b 1
)
"!GITEXE!" push -u origin !BRANCH!
if errorlevel 1 (
  echo.
  echo [ERROR] Upload failed after merging.
  echo.
  pause
  exit /b 1
)
goto PUSH_OK

:FORCE_PUSH
echo.
echo Replacing everything on GitHub with your local version...
echo.
"!GITEXE!" push --force -u origin !BRANCH!
if errorlevel 1 (
  echo.
  echo [ERROR] Replace failed. GitHub may block forced uploads.
  echo Run this script again and choose option 1 instead.
  echo.
  pause
  exit /b 1
)
goto PUSH_OK

:PUSH_OK
echo.
echo ============================================================
echo   [OK] Uploaded successfully!
echo ============================================================
echo.
echo Next: open your repo on GitHub, go to Settings ^> Pages,
echo choose branch "!BRANCH!" and folder "/ (root)", then Save.
echo Your website address will appear there in a minute.
echo.
pause
