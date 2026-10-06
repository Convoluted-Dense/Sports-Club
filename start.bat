@echo off
title Sports Club DBMS - Management Cockpit
echo ========================================================
echo   SPORTS CLUB MEMBERSHIP & TOURNAMENT DBMS SYSTEM
echo ========================================================
echo.
echo Initializing Local Database and Starting Web Application...
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8+ to run the local server.
    pause
    exit /b 1
)

python db_manager.py
python app.py
pause
