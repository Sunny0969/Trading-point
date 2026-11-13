@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
echo ========================================================
echo  Starting FundedNext MT5 SMC Scalper Bridge (Port 5000)...
echo ========================================================
set "PYTHON_CMD=C:\Users\SP\AppData\Local\Python\pythoncore-3.11-64\python.exe"
if not exist "!PYTHON_CMD!" (
    set PYTHON_CMD=python
)
"!PYTHON_CMD!" run_bridge.py
pause
endlocal
