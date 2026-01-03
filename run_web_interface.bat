@echo off
REM Windows batch script to run the web interface
echo Starting Proxy Server Web Interface...
echo.
echo Make sure the proxy server is running first:
echo   python src/proxy_server.py config/proxy_config.json
echo.
echo Then open your browser to: http://127.0.0.1:5000
echo.
python src/web_interface.py
pause

