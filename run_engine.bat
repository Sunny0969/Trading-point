@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
echo ========================================================
echo Starting Gemini SMC AI Live Signal Engine (Port 5000)...
echo Endpoint: http://127.0.0.1:5000/api/ai-signal
echo ========================================================

set PYTHON_CMD=python
if exist "C:\Users\SP\AppData\Local\Programs\Python\Python312\python.exe" (
    set "PYTHON_CMD=C:\Users\SP\AppData\Local\Programs\Python\Python312\python.exe"
)

"!PYTHON_CMD!" gemini_smc_engine.py
pause
endlocal
