# Proxy Server Demonstration Guide

This document provides step-by-step instructions for demonstrating the Custom Network Proxy Server.

## Prerequisites

1. Python 3.6 or higher installed
2. curl installed (for testing)
3. Internet connection

## Step 1: Start the Proxy Server

### Windows:
```cmd
python src/proxy_server.py config/proxy_config.json
```

Or use the batch file:
```cmd
run_proxy.bat
```

### Linux/Mac:
```bash
python3 src/proxy_server.py config/proxy_config.json
```

Or use the shell script:
```bash
chmod +x run_proxy.sh
./run_proxy.sh
```

You should see:
```
Proxy server listening on 127.0.0.1:8888
```

## Step 2: Test Basic HTTP Forwarding

Open a new terminal and run:

```bash
curl -x http://127.0.0.1:8888 http://httpbin.org/get
```

**Expected Result:**
- JSON response from httpbin.org
- Log entry in `logs/proxy.log` showing the request was ALLOWED

## Step 3: Test HTTPS Tunneling

```bash
curl -x http://127.0.0.1:8888 https://www.google.com
```

**Expected Result:**
- HTML content from Google
- Log entry showing CONNECT method was used

## Step 4: Test Domain Blocking

1. Edit `config/blocked_domains.txt` and add:
   ```
   example.com
   ```

2. Save the file (the server will reload filters on next request)

3. Test the blocked domain:
   ```bash
   curl -x http://127.0.0.1:8888 http://example.com
   ```

**Expected Result:**
- HTTP 403 Forbidden response
- Log entry showing the request was BLOCKED

## Step 5: Test Concurrent Requests

Run multiple requests simultaneously:

### PowerShell (Windows):
```powershell
1..5 | ForEach-Object -Parallel { curl -x http://127.0.0.1:8888 http://httpbin.org/get }
```

### Bash (Linux/Mac):
```bash
for i in {1..5}; do curl -x http://127.0.0.1:8888 http://httpbin.org/get & done
wait
```

**Expected Result:**
- All requests complete successfully
- Multiple log entries showing concurrent handling

## Step 6: View Logs

### Windows PowerShell:
```powershell
Get-Content logs/proxy.log -Tail 20
```

### Linux/Mac:
```bash
tail -20 logs/proxy.log
```

**Expected Log Format:**
```
2024-01-15 10:30:45 - INFO - ALLOWED | 127.0.0.1:54321 -> httpbin.org:80 | GET http://httpbin.org/get HTTP/1.1 | 200 | 1234 bytes
2024-01-15 10:30:50 - WARNING - BLOCKED | 127.0.0.1:54322 -> example.com:80 | GET http://example.com/ HTTP/1.1
```

## Step 7: Test Different HTTP Methods

### GET Request:
```bash
curl -x http://127.0.0.1:8888 http://httpbin.org/get
```

### POST Request:
```bash
curl -x http://127.0.0.1:8888 -X POST -d "test=data" http://httpbin.org/post
```

### HEAD Request:
```bash
curl -x http://127.0.0.1:8888 -I http://httpbin.org/get
```

## Step 8: Test with Browser

1. Configure browser proxy settings:
   - **HTTP Proxy**: 127.0.0.1
   - **Port**: 8888

2. Browse to any HTTP website

3. Check logs to see requests being forwarded

## Step 9: Test Wildcard Blocking

1. Edit `config/blocked_domains.txt` and add:
   ```
   *.example.com
   ```

2. Test:
   ```bash
   curl -x http://127.0.0.1:8888 http://subdomain.example.com
   ```

**Expected Result:**
- Request blocked (403 Forbidden)

## Step 10: Monitor Real-Time Activity

### Windows PowerShell:
```powershell
Get-Content logs/proxy.log -Tail 0 -Wait
```

### Linux/Mac:
```bash
tail -f logs/proxy.log
```

Then make requests in another terminal to see real-time logging.

## Troubleshooting

### Port Already in Use
- Change port in `config/proxy_config.json`
- Or stop the process using port 8888

### Connection Refused
- Ensure proxy server is running
- Check firewall settings
- Verify host/port in configuration

### Requests Timing Out
- Check internet connectivity
- Verify destination servers are reachable
- Increase timeout values if needed

## Sample Test Session

Here's a complete test session:

```bash
# Terminal 1: Start proxy
python src/proxy_server.py config/proxy_config.json

# Terminal 2: Run tests
curl -x http://127.0.0.1:8888 http://httpbin.org/get
curl -x http://127.0.0.1:8888 https://www.google.com
curl -x http://127.0.0.1:8888 http://example.com  # After adding to blocked list

# Terminal 3: Monitor logs
tail -f logs/proxy.log
```

## Expected Outcomes

1. **HTTP Forwarding**: ✓ Requests forwarded successfully
2. **HTTPS Tunneling**: ✓ CONNECT method works correctly
3. **Blocking**: ✓ Blocked domains return 403
4. **Concurrency**: ✓ Multiple requests handled simultaneously
5. **Logging**: ✓ All requests logged with details

## Performance Notes

- Thread pool limits concurrent connections (default: 10)
- Each request is logged with timestamp and details
- Blocked requests are logged as warnings
- Server handles graceful shutdown on Ctrl+C

