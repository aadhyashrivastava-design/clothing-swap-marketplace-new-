@echo off
setlocal enabledelayedexpansion
title EcoSwap - Push to GitHub
echo ===================================================
echo             Push EcoSwap to GitHub                 
echo ===================================================
echo.
echo Make sure you have created an empty repository on GitHub first!
echo (e.g. visit https://github.com/new and create 'clothing-swap-marketplace')
echo.
set /p REPO_URL="Enter your GitHub repository URL (e.g. https://github.com/username/clothing-swap-marketplace.git): "

if "%REPO_URL%"=="" (
    echo Error: Repository URL cannot be empty.
    pause
    exit /b 1
)

echo.
echo Configuring remote origin...
"C:\Users\dell\AppData\Local\GitHubDesktop\app-3.6.3\resources\app\git\cmd\git.exe" remote remove origin 2>nul
"C:\Users\dell\AppData\Local\GitHubDesktop\app-3.6.3\resources\app\git\cmd\git.exe" remote add origin %REPO_URL%
"C:\Users\dell\AppData\Local\GitHubDesktop\app-3.6.3\resources\app\git\cmd\git.exe" branch -M main

echo.
echo Pushing code to GitHub...
"C:\Users\dell\AppData\Local\GitHubDesktop\app-3.6.3\resources\app\git\cmd\git.exe" push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ===================================================
    echo   SUCCESS! Your project is now live on GitHub!    
    echo ===================================================
) else (
    echo.
    echo Push encountered an issue. Check your credentials or branch permissions.
)

pause
