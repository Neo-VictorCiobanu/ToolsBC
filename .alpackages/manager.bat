@echo off
echo Starting Server Management System...

REM Check if Python is available
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Try to run the script
cd /d "%~dp0"
python Translation_Tool.py
if %ERRORLEVEL% neq 0 (
    echo An error occurred while running the script
    pause
    exit /b 1
)

pause