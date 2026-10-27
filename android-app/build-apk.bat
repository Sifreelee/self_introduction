@echo off
setlocal
chcp 65001 >nul
REM ===========================================================
REM  LuQingYueFei  -  Android APK build script
REM  Double click this file to build a signed release APK.
REM  Output: dist\LuQingYueFei-v1.1.0.apk
REM ===========================================================

set "JAVA_HOME=C:\Program Files\Java\jdk-17.0.2"
set "ANDROID_HOME=F:\android-sdk"
set "GRADLE_BIN=F:\android-build\gradle-8.9\bin\gradle.bat"
set "PROJ=%~dp0"
set "APPNAME=LuQingYueFei-v1.1.4.apk"

if not exist "%JAVA_HOME%\bin\java.exe" goto no_java
if not exist "%ANDROID_HOME%\platforms\android-34\android.jar" goto no_sdk
if not exist "%GRADLE_BIN%" goto no_gradle
if not exist "%PROJ%local.properties" goto no_props

set "PATH=%JAVA_HOME%\bin;%PATH%"
cd /d "%PROJ%"

echo [1/3] Building release APK, please wait ...
call "%GRADLE_BIN%" clean assembleRelease
if errorlevel 1 goto build_fail

echo [2/3] Copying APK to dist ...
if not exist "%PROJ%dist" mkdir "%PROJ%dist"
copy /Y "%PROJ%app\build\outputs\apk\release\app-release.apk" "%PROJ%dist\%APPNAME%" >nul
if errorlevel 1 goto copy_fail

echo [3/3] Success.
echo.
echo APK file: %PROJ%dist\%APPNAME%
echo.
pause
exit /b 0

:no_java
echo [ERROR] Java not found at %JAVA_HOME%
echo Install JDK 17 and fix JAVA_HOME at the top of this file.
pause
exit /b 1

:no_sdk
echo [ERROR] Android SDK not found at %ANDROID_HOME%
echo Install platform android-34 and build-tools 34.0.0, or fix ANDROID_HOME.
pause
exit /b 1

:no_gradle
echo [ERROR] Gradle not found at %GRADLE_BIN%
echo Fix GRADLE_BIN at the top of this file.
pause
exit /b 1

:no_props
echo [ERROR] local.properties is missing. It must contain: sdk.dir=F:\\android-sdk
pause
exit /b 1

:build_fail
echo [ERROR] Gradle build failed. See the log above.
pause
exit /b 1

:copy_fail
echo [ERROR] Copy step failed.
pause
exit /b 1
