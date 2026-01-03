# Custom Network Proxy Server

A custom network proxy server implementation that handles HTTP traffic over TCP, demonstrating fundamental systems and networking concepts including socket programming, concurrency, request parsing, forwarding logic, logging, and rule-based filtering.

## Features

- **HTTP Proxy**: Forwards HTTP requests and responses
- **HTTPS Tunneling**: Supports CONNECT method for HTTPS traffic
- **Domain/IP Filtering**: Configurable blocking of domains and IP addresses
- **Concurrent Handling**: Thread pool-based concurrency for multiple clients
- **Request Logging**: Comprehensive logging of all proxy activity
- **Configurable**: JSON-based configuration file

## Project Structure

```
proxy-project/
├── src/                    # Source files
│   ├── proxy_server.py    # Main proxy server
│   ├── http_parser.py     # HTTP request parser
│   ├── filter_manager.py  # Domain/IP filtering
│   ├── logger.py          # Logging system
│   └── config_loader.py   # Configuration loader
├── config/                # Configuration files
│   ├── proxy_config.json  # Server configuration
│   └── blocked_domains.txt # Blocked domains/IPs
├── tests/                 # Test scripts
│   ├── test_basic.py      # Basic functionality tests
│   └── test_concurrent.py # Concurrent request tests
├── docs/                  # Documentation
│   └── DESIGN.md          # Design document
├── logs/                  # Log files (generated)
├── Makefile              # Build and run commands
└── README.md             # This file
```

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only standard library)

## Installation

1. Clone or download this repository
2. Ensure Python 3 is installed:
   ```bash
   python3 --version
   ```

## Configuration

Edit `config/proxy_config.json` to configure the server:

```json
{
    "host": "127.0.0.1",
    "port": 8888,
    "thread_pool_size": 10,
    "backlog": 100,
    "blocked_domains_file": "config/blocked_domains.txt",
    "log_file": "logs/proxy.log"
}
```

### Blocking Domains/IPs

Edit `config/blocked_domains.txt` to add blocked domains or IPs:

```
# Blocked domains and IPs
example.com
badsite.org
*.malicious.com
192.0.2.5
```

- One entry per line
- Lines starting with `#` are comments
- Use `*.example.com` to block all subdomains

## Usage

### Starting the Server

Using Makefile:
```bash
make run
```

Or directly:
```bash
python3 src/proxy_server.py config/proxy_config.json
```

The server will start listening on the configured host and port (default: 127.0.0.1:8888).

### Web Interface (Recommended for Testing)

For easier testing, use the web interface:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the proxy server** (in one terminal):
   ```bash
   python src/proxy_server.py config/proxy_config.json
   ```

3. **Start the web interface** (in another terminal):
   ```bash
   python src/web_interface.py
   ```

4. **Open your browser** to: `http://127.0.0.1:5000`

The web interface allows you to:
- Test requests through the proxy
- View logs in real-time
- See statistics
- Test blocking functionality

See `docs/WEB_INTERFACE.md` for detailed web interface documentation.

### Using the Proxy

#### HTTP Requests

```bash
curl -x http://127.0.0.1:8888 http://example.com
```

#### HTTPS Requests

```bash
curl -x http://127.0.0.1:8888 https://www.google.com
```

#### Configure Browser

- **Chrome/Edge**: Settings → Advanced → System → Open proxy settings
- **Firefox**: Settings → Network Settings → Manual proxy configuration
  - HTTP Proxy: `127.0.0.1`
  - Port: `8888`

## Testing

### Comprehensive Testing

For complete testing, see the **Comprehensive Testing Guide**:
```bash
# Read the guide
cat docs/COMPREHENSIVE_TESTING_GUIDE.md
```

### Automated Test Suite

Run the complete automated test suite:
```bash
python tests/run_all_tests.py
```

This will test:
- HTTP request forwarding
- HTTPS CONNECT tunneling
- Domain blocking
- Concurrent requests
- Error handling
- Logging functionality
- And more...

### Basic Tests

```bash
make test-basic
```

Or:
```bash
python3 tests/test_basic.py
```

### Concurrent Tests

```bash
make test-concurrent
```

Or:
```bash
python3 tests/test_concurrent.py
```

### Manual Testing

1. **Test HTTP forwarding**:
   ```bash
   curl -x http://127.0.0.1:8888 http://httpbin.org/get
   ```

2. **Test blocking**:
   - Add a domain to `config/blocked_domains.txt`
   - Try to access it:
     ```bash
     curl -x http://127.0.0.1:8888 http://blocked-domain.com
     ```
   - Should return `403 Forbidden`

3. **Test HTTPS**:
   ```bash
   curl -x http://127.0.0.1:8888 https://www.google.com
   ```

## Logging

Logs are written to `logs/proxy.log` (configurable). Each entry includes:
- Timestamp
- Client IP:port
- Destination host:port
- Request line
- Action (ALLOWED/BLOCKED)
- Response status code
- Response size

Example log entry:
```
2024-01-15 10:30:45 - INFO - ALLOWED | 127.0.0.1:54321 -> example.com:80 | GET http://example.com/ HTTP/1.1 | 200 | 1234 bytes
```

## Architecture

See `docs/DESIGN.md` for detailed architecture documentation.

### Key Components

1. **ProxyServer**: Main server class handling connections
2. **HTTPParser**: Parses HTTP requests
3. **FilterManager**: Manages blocking rules
4. **ProxyLogger**: Handles logging
5. **ConfigLoader**: Loads configuration

### Concurrency Model

The server uses a **thread pool** model:
- Fixed-size thread pool (configurable)
- Semaphore-based connection limiting
- One thread per client connection
- Graceful shutdown handling

## Limitations

- Does not handle HTTP/2
- Chunked transfer encoding is forwarded transparently (not parsed)
- No caching implementation (optional extension)
- No authentication (optional extension)
- Persistent connections (keep-alive) are not fully optimized

## Security Considerations

- Input validation for configuration files
- Timeout handling to prevent resource exhaustion
- Connection limits via thread pool
- Proper error handling and logging

## Extensions (Optional)

The following features can be added as extensions:

1. **Caching**: Implement LRU cache for HTTP responses
2. **Authentication**: Add user authentication mechanisms
3. **Advanced Filtering**: Regex-based rules, time-based blocking
4. **Metrics**: Request rate, top domains, bandwidth usage
5. **Web Interface**: Admin interface for configuration

## Troubleshooting

### Port Already in Use

If you get "Address already in use" error:
- Change the port in `config/proxy_config.json`
- Or stop the process using the port

### Connection Refused

- Ensure the proxy server is running
- Check firewall settings
- Verify the host and port in configuration

### Requests Timing Out

- Check internet connectivity
- Verify destination servers are reachable
- Increase timeout values if needed

## License

This project is for educational purposes.

## Author

Custom Network Proxy Server - Educational Project

