@echo off
REM Windows batch script to run the proxy server
echo Starting Custom Network Proxy Server...
echo.
python src/proxy_server.py config/proxy_config.json
pause

