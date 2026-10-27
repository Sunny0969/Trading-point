@echo off
setlocal
cd /d "%~dp0"
echo Starting Local Forex MCP Server...
"C:\Users\SP\AppData\Local\Programs\Python\Python312\python.exe" server.py
endlocal
