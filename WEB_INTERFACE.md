# Web Interface Guide

The web interface provides an easy way to test and monitor your proxy server without using command-line tools.

## Setup

### 1. Install Dependencies

First, install the required Python packages:

```bash
pip install flask requests
```

Or use the requirements file:

```bash
pip install -r requirements.txt
```

### 2. Start the Proxy Server

In one terminal, start the proxy server:

```bash
python src/proxy_server.py config/proxy_config.json
```

### 3. Start the Web Interface

In another terminal, start the web interface:

**Windows:**
```cmd
python src/web_interface.py
```

Or use the batch file:
```cmd
run_web_interface.bat
```

**Linux/Mac:**
```bash
python3 src/web_interface.py
```

Or use the shell script:
```bash
chmod +x run_web_interface.sh
./run_web_interface.sh
```

### 4. Open in Browser

Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

## Features

### 1. Proxy Status

- Check if the proxy server is running
- View proxy configuration (host, port, thread pool size)
- Refresh status button

### 2. Test Proxy Request

- Enter any URL to test through the proxy
- Select HTTP method (GET, POST, HEAD)
- View response status, headers, and body
- See response time and size
- Test blocked domains (shows 403 Forbidden)

**Example URLs to test:**
- `http://httpbin.org/get` - Simple GET request
- `http://httpbin.org/post` - POST request
- `https://www.google.com` - HTTPS request (uses CONNECT)
- `http://example.com` - Test blocking (if added to blocked list)

### 3. View Logs

- View recent proxy server logs
- Color-coded entries:
  - Green: Allowed requests
  - Yellow: Blocked requests
  - Red: Errors
- Auto-refresh option (updates every 3 seconds)
- Scrollable log viewer

### 4. Statistics

- Total requests processed
- Allowed requests count
- Blocked requests count
- Total bytes transferred
- Refresh button to update stats

## Usage Examples

### Testing a Simple Request

1. Enter URL: `http://httpbin.org/get`
2. Select Method: `GET`
3. Click "Test Request"
4. View the response in the result box

### Testing HTTPS

1. Enter URL: `https://www.google.com`
2. Click "Test Request"
3. The proxy will use CONNECT tunneling
4. View the response

### Testing Blocking

1. Add a domain to `config/blocked_domains.txt`:
   ```
   example.com
   ```

2. In the web interface, enter: `http://example.com`

3. Click "Test Request"

4. You should see:
   - Status: 403
   - "BLOCKED" badge
   - The request was denied

### Monitoring Logs

1. Click "Load Logs" to view recent entries
2. Click "Auto-Refresh" to update every 3 seconds
3. Make requests through the interface or using curl
4. Watch logs update in real-time

## Troubleshooting

### "Proxy Server Not Running" Error

- Make sure the proxy server is started first
- Check that it's running on `127.0.0.1:8888`
- Verify the proxy server terminal shows "Proxy server listening..."

### Connection Errors

- Ensure both proxy server and web interface are running
- Check firewall settings
- Verify ports 8888 (proxy) and 5000 (web interface) are available

### No Logs Showing

- Make some requests first (logs are generated when requests are made)
- Check that `logs/proxy.log` file exists
- Verify file permissions

### Flask Not Found

Install Flask:
```bash
pip install flask requests
```

## Architecture

The web interface:
- Runs on port 5000 (separate from proxy on 8888)
- Uses Flask for the web server
- Makes requests through the proxy server
- Reads logs from `logs/proxy.log`
- Provides a REST API for the frontend

## API Endpoints

- `GET /` - Main web interface
- `GET /api/status` - Check proxy server status
- `POST /api/test` - Test a request through proxy
- `GET /api/logs` - Get recent log entries
- `GET /api/stats` - Get statistics from logs

## Tips

1. **Keep both terminals open**: One for proxy server, one for web interface
2. **Use Auto-Refresh**: Enable it to see logs update automatically
3. **Test different URLs**: Try various sites to see how the proxy handles them
4. **Monitor Statistics**: Check stats after making several requests
5. **View Full Responses**: Expand the response body section to see full content

## Next Steps

After testing with the web interface, you can:
- Use curl commands for automated testing
- Configure your browser to use the proxy
- Add more domains to the blocked list
- Review the design document for architecture details

