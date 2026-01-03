# Design Document: Custom Network Proxy Server

## 1. High-Level Architecture

### System Overview

The proxy server acts as an intermediary between clients and destination servers, forwarding HTTP/HTTPS requests and responses. The system is designed with modularity and extensibility in mind.

```
┌─────────┐         ┌──────────────┐         ┌─────────────┐
│ Client  │────────▶│ Proxy Server │────────▶│  Server     │
│         │◀────────│              │◀────────│             │
└─────────┘         └──────────────┘         └─────────────┘
```

### Component Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    ProxyServer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ HTTPParser   │  │FilterManager │  │ProxyLogger    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Thread Pool (Concurrent Handling)        │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
    ConfigLoader      Socket Operations    Log Files
```

## 2. Component Descriptions

### 2.1 ProxyServer (proxy_server.py)

**Responsibilities:**
- Create and manage listening socket
- Accept incoming client connections
- Dispatch connections to worker threads
- Coordinate with other components
- Handle graceful shutdown

**Key Methods:**
- `start()`: Initialize and start the server
- `_handle_client()`: Process a single client connection
- `_handle_connect()`: Handle HTTPS CONNECT tunneling
- `_handle_http_request()`: Handle regular HTTP requests
- `_tunnel_connection()`: Bidirectional data forwarding for HTTPS

### 2.2 HTTPParser (http_parser.py)

**Responsibilities:**
- Parse HTTP request lines
- Extract method, URI, version
- Parse HTTP headers
- Handle both absolute and relative URIs
- Extract host and port information

**Key Methods:**
- `parse_request()`: Main parsing function

**Parsing Logic:**
1. Extract request line (method, target, version)
2. Parse headers into dictionary
3. Determine if target is absolute URI or relative path
4. Extract host from URI or Host header
5. Extract port (default: 80 for HTTP, 443 for HTTPS)

### 2.3 FilterManager (filter_manager.py)

**Responsibilities:**
- Load filtering rules from file
- Check if domains/IPs are blocked
- Support exact matches and wildcard suffixes
- Validate IP addresses

**Key Methods:**
- `load_filters()`: Load rules from file
- `is_blocked()`: Check if host is blocked

**Filtering Rules:**
- Exact domain matching
- Exact IP matching
- Wildcard suffix matching (e.g., `*.example.com`)

### 2.4 ProxyLogger (logger.py)

**Responsibilities:**
- Log all proxy events
- Format log entries consistently
- Write to file and console
- Track allowed and blocked requests

**Log Format:**
```
TIMESTAMP - LEVEL - MESSAGE
ALLOWED | CLIENT_IP:PORT -> HOST:PORT | REQUEST_LINE | STATUS | SIZE
BLOCKED | CLIENT_IP:PORT -> HOST:PORT | REQUEST_LINE
```

### 2.5 ConfigLoader (config_loader.py)

**Responsibilities:**
- Load configuration from JSON file
- Provide default values
- Validate configuration
- Create default config if missing

## 3. Concurrency Model

### Thread Pool Architecture

The server uses a **thread pool** model with the following characteristics:

1. **Fixed-size pool**: Configurable number of worker threads (default: 10)
2. **Semaphore-based limiting**: Prevents resource exhaustion
3. **One thread per connection**: Each client connection handled in separate thread
4. **Daemon threads**: Automatically cleaned up on shutdown

### Rationale

**Why Thread Pool over Thread-per-Connection?**
- Better resource control
- Prevents unbounded thread creation
- More predictable performance under load

**Why Thread Pool over Event Loop?**
- Simpler implementation
- Easier to understand and debug
- Sufficient for moderate concurrency
- No external dependencies

### Thread Lifecycle

```
Client Connection
      │
      ▼
Accept Connection
      │
      ▼
Acquire Semaphore
      │
      ▼
Create Worker Thread
      │
      ▼
Handle Request
      │
      ▼
Release Semaphore
      │
      ▼
Thread Terminates
```

## 4. Data Flow

### 4.1 Incoming Request Handling

```
1. Client connects to proxy
   │
2. Proxy accepts connection
   │
3. Receive request data (headers + body)
   │
4. Parse HTTP request
   │
5. Extract destination (host, port)
   │
6. Check filter rules
   │
   ├─→ Blocked? → Send 403 → Close connection
   │
   └─→ Allowed? → Continue
       │
7. Determine request type
   │
   ├─→ CONNECT? → Handle HTTPS tunneling
   │
   └─→ HTTP? → Forward request
```

### 4.2 HTTP Request Forwarding

```
1. Connect to destination server
   │
2. Send client's request (as received)
   │
3. Receive response from server
   │
4. Forward response to client (streaming)
   │
5. Close connections
   │
6. Log transaction
```

### 4.3 HTTPS CONNECT Tunneling

```
1. Receive CONNECT request
   │
2. Connect to destination server
   │
3. Send "200 Connection Established"
   │
4. Enter bidirectional forwarding mode
   │
   ├─→ Client → Server (forward bytes)
   │
   └─→ Server → Client (forward bytes)
   │
5. Continue until connection closes
   │
6. Log transaction
```

## 5. Error Handling

### Connection Errors

- **Connection refused**: Log error, send 502 Bad Gateway
- **Timeout**: Log error, send 504 Gateway Timeout
- **Network errors**: Log error, close connection gracefully

### Parsing Errors

- **Invalid request**: Log error, close connection
- **Missing headers**: Use defaults where possible
- **Malformed data**: Log warning, attempt to continue

### Resource Errors

- **Thread pool full**: Reject new connections
- **File I/O errors**: Log error, continue with defaults
- **Memory issues**: Log error, close connection

### Graceful Shutdown

- Handle SIGINT/SIGTERM signals
- Stop accepting new connections
- Wait for existing connections to complete
- Close all sockets
- Flush logs

## 6. Limitations

### Current Limitations

1. **HTTP/1.1 Only**: No HTTP/2 support
2. **Chunked Encoding**: Forwarded transparently, not parsed
3. **Persistent Connections**: Not fully optimized (closes after request)
4. **No Caching**: Every request forwarded to origin
5. **No Authentication**: All clients allowed
6. **Limited Error Recovery**: Some errors cause connection termination

### Performance Considerations

- Thread overhead limits scalability
- No connection pooling to destination servers
- Synchronous I/O operations
- Memory usage grows with concurrent connections

## 7. Security Considerations

### Input Validation

- Validate configuration file format
- Sanitize log output to prevent injection
- Validate hostnames and IPs before use

### Resource Limits

- Thread pool size limits concurrent connections
- Socket timeouts prevent resource exhaustion
- Connection backlog limits pending connections

### Network Security

- No encryption of proxy traffic
- No authentication mechanism
- Logs may contain sensitive information

### Recommendations

1. Run proxy in isolated network environment
2. Implement authentication for production use
3. Encrypt logs if containing sensitive data
4. Implement rate limiting
5. Add request size limits
6. Monitor for suspicious activity

## 8. Testing Strategy

### Unit Testing

- Test HTTP parsing with various request formats
- Test filtering logic with different rules
- Test configuration loading

### Integration Testing

- Test end-to-end request forwarding
- Test CONNECT tunneling
- Test blocking functionality

### Load Testing

- Concurrent request handling
- Thread pool behavior under load
- Resource usage monitoring

### Test Cases

1. **Basic HTTP**: Simple GET request
2. **HTTPS**: CONNECT tunneling
3. **Blocking**: Verify blocked domains return 403
4. **Concurrent**: Multiple simultaneous requests
5. **Malformed**: Invalid requests handled gracefully
6. **Timeout**: Server timeout scenarios

## 9. Future Extensions

### Caching

- Implement LRU cache
- Cache key: normalized request URI
- Cache metadata: headers, timestamp, size
- Eviction policy: LRU with size limits

### Authentication

- Basic authentication
- Token-based authentication
- Per-user filtering rules

### Advanced Filtering

- Regex-based rules
- Time-based blocking
- Rate limiting per domain
- Content filtering

### Metrics and Monitoring

- Request rate statistics
- Top requested domains
- Bandwidth usage
- Error rates
- Response time metrics

### Web Interface

- Admin dashboard
- Real-time statistics
- Configuration management
- Log viewing interface

## 10. Conclusion

This proxy server implementation demonstrates core networking concepts including socket programming, concurrent request handling, HTTP protocol parsing, and rule-based filtering. The modular design allows for easy extension with additional features such as caching, authentication, and advanced filtering mechanisms.

The thread pool concurrency model provides a good balance between simplicity and performance for moderate-scale deployments, while the comprehensive logging and error handling ensure reliability and debuggability.

