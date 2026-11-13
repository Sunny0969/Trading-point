@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
echo ========================================================
echo  FundedNext SMC AI Live Micro-Scalper Engine (Port 5000)
echo  Endpoint: http://127.0.0.1:5000/api/ai-signal
echo  Broker: FundedNext-Server 3 | Login: 35402925
echo ========================================================

set "PYTHON_CMD=C:\Users\SP\AppData\Local\Python\pythoncore-3.11-64\python.exe"
if not exist "!PYTHON_CMD!" (
    set PYTHON_CMD=python
)

"!PYTHON_CMD!" run_bridge.py
pause
endlocal
