@echo off
cd /d "%~dp0"
echo Starting ETS2 Telemetry Sync...
python app.py
echo.
echo App exited. Press any key to close.
pause >nul