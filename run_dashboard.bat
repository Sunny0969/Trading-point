@echo off
setlocal
cd /d "%~dp0"
echo ========================================================
echo Starting TradingPoint Local High-Performance Server...
echo Terminal URL: http://localhost:8080/#terminal
echo Dashboard URL: http://localhost:8080/
echo ========================================================
start "" "http://localhost:8080/#terminal"
"C:\Users\SP\AppData\Local\Programs\Python\Python312\python.exe" web_server.py
pause
endlocal
