#!/usr/bin/env python3
"""
Web Interface for Proxy Server Testing
Provides a web-based UI to test and monitor the proxy server.
"""

from flask import Flask, render_template_string, request, jsonify, Response
import requests
import json
import os
from datetime import datetime
import threading
import time

app = Flask(__name__)

# Proxy configuration
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 8888
PROXY_URL = f"http://{PROXY_HOST}:{PROXY_PORT}"
LOG_FILE = "logs/proxy.log"

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Proxy Server Test Interface</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header p {
            opacity: 0.9;
            font-size: 1.1em;
        }
        .content {
            padding: 30px;
        }
        .section {
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        .section h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.5em;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
        }
        input[type="text"], input[type="url"], select {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus, input[type="url"]:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        .button-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        button {
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-primary {
            background: #667eea;
            color: white;
        }
        .btn-primary:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        .btn-secondary:hover {
            background: #5a6268;
        }
        .btn-success {
            background: #28a745;
            color: white;
        }
        .btn-success:hover {
            background: #218838;
        }
        .result-box {
            margin-top: 20px;
            padding: 20px;
            background: white;
            border-radius: 8px;
            border: 2px solid #ddd;
            min-height: 100px;
            max-height: 400px;
            overflow-y: auto;
        }
        .result-box pre {
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
        .status-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 10px;
        }
        .status-success {
            background: #d4edda;
            color: #155724;
        }
        .status-error {
            background: #f8d7da;
            color: #721c24;
        }
        .status-blocked {
            background: #fff3cd;
            color: #856404;
        }
        .log-entry {
            padding: 10px;
            margin-bottom: 5px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }
        .log-allowed {
            background: #d4edda;
            border-left: 3px solid #28a745;
        }
        .log-blocked {
            background: #fff3cd;
            border-left: 3px solid #ffc107;
        }
        .log-error {
            background: #f8d7da;
            border-left: 3px solid #dc3545;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .alert-info {
            background: #d1ecf1;
            color: #0c5460;
            border-left: 4px solid #17a2b8;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Proxy Server Test Interface</h1>
            <p>Test and monitor your custom network proxy server</p>
        </div>
        
        <div class="content">
            <!-- Proxy Status -->
            <div class="section">
                <h2>Proxy Status</h2>
                <div id="proxy-status">
                    <div class="loading" id="status-loading">
                        <div class="spinner"></div>
                        <p>Checking proxy status...</p>
                    </div>
                    <div id="status-result"></div>
                </div>
                <button class="btn-secondary" onclick="checkStatus()">Refresh Status</button>
            </div>

            <!-- Test Request -->
            <div class="section">
                <h2>Test Proxy Request</h2>
                <div class="form-group">
                    <label for="test-url">Enter URL to test:</label>
                    <input type="url" id="test-url" placeholder="http://httpbin.org/get" value="http://httpbin.org/get">
                </div>
                <div class="form-group">
                    <label for="test-method">HTTP Method:</label>
                    <select id="test-method">
                        <option value="GET">GET</option>
                        <option value="POST">POST</option>
                        <option value="HEAD">HEAD</option>
                    </select>
                </div>
                <div class="button-group">
                    <button class="btn-primary" onclick="testRequest()">Test Request</button>
                    <button class="btn-secondary" onclick="clearResult()">Clear Result</button>
                </div>
                <div class="loading" id="request-loading">
                    <div class="spinner"></div>
                    <p>Making request through proxy...</p>
                </div>
                <div id="request-result"></div>
            </div>

            <!-- View Logs -->
            <div class="section">
                <h2>Proxy Logs</h2>
                <div class="button-group">
                    <button class="btn-success" onclick="loadLogs()">Load Logs</button>
                    <button class="btn-secondary" onclick="clearLogs()">Clear View</button>
                    <button class="btn-secondary" onclick="startAutoRefresh()">Auto-Refresh</button>
                    <button class="btn-secondary" onclick="stopAutoRefresh()">Stop Auto-Refresh</button>
                </div>
                <div id="logs-container" class="result-box"></div>
            </div>

            <!-- Statistics -->
            <div class="section">
                <h2>Statistics</h2>
                <button class="btn-secondary" onclick="loadStats()">Refresh Statistics</button>
                <div id="stats-container" class="stats-grid"></div>
            </div>
        </div>
    </div>

    <script>
        let autoRefreshInterval = null;

        function checkStatus() {
            document.getElementById('status-loading').style.display = 'block';
            document.getElementById('status-result').innerHTML = '';
            
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('status-loading').style.display = 'none';
                    const statusDiv = document.getElementById('status-result');
                    if (data.running) {
                        statusDiv.innerHTML = `
                            <div class="status-badge status-success">✓ Proxy Server Running</div>
                            <p><strong>Host:</strong> ${data.host}</p>
                            <p><strong>Port:</strong> ${data.port}</p>
                            <p><strong>Thread Pool Size:</strong> ${data.thread_pool_size}</p>
                        `;
                    } else {
                        statusDiv.innerHTML = `
                            <div class="status-badge status-error">✗ Proxy Server Not Running</div>
                            <p>Please start the proxy server first:</p>
                            <pre>python src/proxy_server.py config/proxy_config.json</pre>
                        `;
                    }
                })
                .catch(error => {
                    document.getElementById('status-loading').style.display = 'none';
                    document.getElementById('status-result').innerHTML = `
                        <div class="status-badge status-error">✗ Error: ${error.message}</div>
                    `;
                });
        }

        function testRequest() {
            const url = document.getElementById('test-url').value;
            const method = document.getElementById('test-method').value;
            const resultDiv = document.getElementById('request-result');
            const loadingDiv = document.getElementById('request-loading');
            
            if (!url) {
                resultDiv.innerHTML = '<div class="alert alert-info">Please enter a URL</div>';
                return;
            }
            
            loadingDiv.style.display = 'block';
            resultDiv.innerHTML = '';
            
            fetch('/api/test', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url, method: method })
            })
            .then(response => response.json())
            .then(data => {
                loadingDiv.style.display = 'none';
                let statusClass = 'status-success';
                if (data.status >= 400) {
                    statusClass = 'status-error';
                } else if (data.blocked) {
                    statusClass = 'status-blocked';
                }
                
                resultDiv.innerHTML = `
                    <div class="status-badge ${statusClass}">
                        ${data.blocked ? 'BLOCKED' : 'Status: ' + data.status}
                    </div>
                    <p><strong>URL:</strong> ${data.url}</p>
                    <p><strong>Method:</strong> ${data.method}</p>
                    <p><strong>Response Time:</strong> ${data.response_time}ms</p>
                    <p><strong>Response Size:</strong> ${data.size} bytes</p>
                    <details>
                        <summary><strong>Response Headers</strong></summary>
                        <pre>${JSON.stringify(data.headers, null, 2)}</pre>
                    </details>
                    <details>
                        <summary><strong>Response Body (first 1000 chars)</strong></summary>
                        <pre>${data.body.substring(0, 1000)}${data.body.length > 1000 ? '...' : ''}</pre>
                    </details>
                `;
                
                // Auto-reload logs after a short delay to allow log write to complete
                setTimeout(() => {
                    loadLogs();
                }, 500); // 500ms delay to allow proxy to write log
            })
            .catch(error => {
                loadingDiv.style.display = 'none';
                resultDiv.innerHTML = `
                    <div class="status-badge status-error">Error: ${error.message}</div>
                    <p>Make sure the proxy server is running!</p>
                `;
            });
        }

        function loadLogs(retryCount = 0) {
            const container = document.getElementById('logs-container');
            if (retryCount === 0) {
                container.innerHTML = '<p>Loading logs...</p>';
            }
            
            fetch('/api/logs')
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.error) {
                        // Retry once if file is locked
                        if (data.error.includes('locked') && retryCount < 1) {
                            setTimeout(() => loadLogs(retryCount + 1), 300);
                            return;
                        }
                        container.innerHTML = `<p>Error: ${data.error}</p>
                                               <p><small>The log file may be locked. Try again in a moment.</small></p>`;
                        return;
                    }
                    
                    if (data.logs.length === 0) {
                        if (data.message) {
                            container.innerHTML = `<p>${data.message}</p>`;
                        } else {
                            container.innerHTML = '<p>No logs found. Make some requests first!</p>';
                        }
                        return;
                    }
                    
                    let html = '';
                    data.logs.forEach(log => {
                        let logClass = 'log-entry';
                        if (log.includes('ALLOWED')) {
                            logClass += ' log-allowed';
                        } else if (log.includes('BLOCKED')) {
                            logClass += ' log-blocked';
                        } else if (log.includes('ERROR')) {
                            logClass += ' log-error';
                        }
                        html += `<div class="${logClass}">${log}</div>`;
                    });
                    container.innerHTML = html;
                    container.scrollTop = container.scrollHeight;
                })
                .catch(error => {
                    console.error('Error loading logs:', error);
                    // Retry once on network errors
                    if (retryCount < 1) {
                        setTimeout(() => loadLogs(retryCount + 1), 300);
                        return;
                    }
                    container.innerHTML = 
                        `<p>Error loading logs: ${error.message}</p>
                         <p><small>Make sure the web interface server is running on port 5000</small></p>`;
                });
        }

        function loadStats() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('stats-container');
                    container.innerHTML = `
                        <div class="stat-card">
                            <div class="stat-value">${data.total_requests}</div>
                            <div class="stat-label">Total Requests</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${data.allowed_requests}</div>
                            <div class="stat-label">Allowed</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${data.blocked_requests}</div>
                            <div class="stat-label">Blocked</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${data.total_bytes}</div>
                            <div class="stat-label">Total Bytes</div>
                        </div>
                    `;
                })
                .catch(error => {
                    document.getElementById('stats-container').innerHTML = 
                        `<p>Error loading stats: ${error.message}</p>`;
                });
        }

        function clearResult() {
            document.getElementById('request-result').innerHTML = '';
        }

        function clearLogs() {
            document.getElementById('logs-container').innerHTML = '';
        }

        function startAutoRefresh() {
            if (autoRefreshInterval) {
                clearInterval(autoRefreshInterval);
            }
            autoRefreshInterval = setInterval(() => {
                loadLogs();
                loadStats();
            }, 3000); // Refresh every 3 seconds
            alert('Auto-refresh started (every 3 seconds)');
            // Load immediately
            loadLogs();
            loadStats();
        }

        function stopAutoRefresh() {
            if (autoRefreshInterval) {
                clearInterval(autoRefreshInterval);
                autoRefreshInterval = null;
                alert('Auto-refresh stopped');
            }
        }

        // Check status on page load
        window.onload = function() {
            checkStatus();
            loadStats();
        };
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main page."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def get_status():
    """Check if proxy server is running."""
    try:
        # Try to connect to proxy
        response = requests.get('http://httpbin.org/get', 
                              proxies={'http': PROXY_URL, 'https': PROXY_URL},
                              timeout=5)
        return jsonify({
            'running': True,
            'host': PROXY_HOST,
            'port': PROXY_PORT,
            'thread_pool_size': 10  # Default, could be read from config
        })
    except:
        return jsonify({
            'running': False,
            'host': PROXY_HOST,
            'port': PROXY_PORT
        })

@app.route('/api/test', methods=['POST'])
def test_proxy():
    """Test a request through the proxy."""
    data = request.json
    url = data.get('url', '')
    method = data.get('method', 'GET')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    proxies = {
        'http': PROXY_URL,
        'https': PROXY_URL
    }
    
    start_time = time.time()
    
    try:
        # Make request through proxy
        if method == 'GET':
            response = requests.get(url, proxies=proxies, timeout=30, allow_redirects=True)
        elif method == 'POST':
            response = requests.post(url, proxies=proxies, timeout=30, allow_redirects=True)
        elif method == 'HEAD':
            response = requests.head(url, proxies=proxies, timeout=30, allow_redirects=True)
        else:
            return jsonify({'error': 'Unsupported method'}), 400
        
        response_time = int((time.time() - start_time) * 1000)
        
        return jsonify({
            'url': url,
            'method': method,
            'status': response.status_code,
            'headers': dict(response.headers),
            'body': response.text[:5000],  # Limit body size
            'size': len(response.content),
            'response_time': response_time,
            'blocked': False
        })
    except requests.exceptions.ProxyError as e:
        # Check if it's a 403 (blocked)
        if '403' in str(e):
            return jsonify({
                'url': url,
                'method': method,
                'status': 403,
                'blocked': True,
                'response_time': int((time.time() - start_time) * 1000),
                'size': 0
            })
        return jsonify({
            'error': f'Proxy error: {str(e)}',
            'url': url,
            'method': method,
            'blocked': False
        }), 500
    except Exception as e:
        return jsonify({
            'error': str(e),
            'url': url,
            'method': method,
            'blocked': False
        }), 500

@app.route('/api/logs')
def get_logs():
    """Get recent log entries."""
    import time
    max_retries = 3
    retry_delay = 0.1  # 100ms
    
    log_path = LOG_FILE
    # Handle both relative and absolute paths
    if not os.path.isabs(log_path):
        # Get the directory where the script is running from
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_path = os.path.join(base_dir, LOG_FILE)
    
    # Retry logic to handle file locking
    for attempt in range(max_retries):
        try:
            if os.path.exists(log_path):
                # Try to read the file with retry on lock
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    # Read all lines
                    lines = f.readlines()
                    # Get last 50 lines
                    recent_lines = lines[-50:] if len(lines) > 50 else lines
                    return jsonify({
                        'logs': [line.strip() for line in recent_lines if line.strip()]
                    })
            else:
                # Log file doesn't exist yet
                return jsonify({
                    'logs': [],
                    'message': f'Log file not found at: {log_path}. Make some requests through the proxy first.'
                })
        except (IOError, PermissionError, OSError) as e:
            # File might be locked by the proxy server writing to it
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            else:
                # Last attempt failed, return error
                return jsonify({
                    'error': f'Could not read log file (file may be locked): {str(e)}',
                    'logs': []
                }), 500
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in get_logs: {error_details}")  # Debug output to console
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'logs': [], 'error': 'Failed to read log file after retries'}), 500

@app.route('/api/stats')
def get_stats():
    """Get statistics from logs."""
    try:
        if not os.path.exists(LOG_FILE):
            return jsonify({
                'total_requests': 0,
                'allowed_requests': 0,
                'blocked_requests': 0,
                'total_bytes': 0
            })
        
        total_requests = 0
        allowed_requests = 0
        blocked_requests = 0
        total_bytes = 0
        
        with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if 'ALLOWED' in line:
                    allowed_requests += 1
                    total_requests += 1
                    # Extract bytes from log line
                    if 'bytes' in line:
                        try:
                            bytes_part = line.split('bytes')[0].split()[-1]
                            total_bytes += int(bytes_part)
                        except:
                            pass
                elif 'BLOCKED' in line:
                    blocked_requests += 1
                    total_requests += 1
        
        return jsonify({
            'total_requests': total_requests,
            'allowed_requests': allowed_requests,
            'blocked_requests': blocked_requests,
            'total_bytes': total_bytes
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("Proxy Server Web Interface")
    print("=" * 60)
    print(f"Starting web interface on http://127.0.0.1:5000")
    print(f"Make sure the proxy server is running on {PROXY_URL}")
    print("=" * 60)
    app.run(host='127.0.0.1', port=5000, debug=True)

