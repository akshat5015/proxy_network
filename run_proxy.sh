#!/bin/bash
# Linux/Mac shell script to run the proxy server
echo "Starting Custom Network Proxy Server..."
echo ""
python3 src/proxy_server.py config/proxy_config.json

