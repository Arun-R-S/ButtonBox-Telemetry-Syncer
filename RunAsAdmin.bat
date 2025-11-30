@echo off
:: Check for admin rights
openfiles >nul 2>&1 || (
    echo Requesting administrative privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"
echo Starting ETS2 Telemetry Sync...
python app.py
echo.
echo App exited. Press any key to close.
pause >nul