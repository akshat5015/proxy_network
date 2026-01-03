#!/usr/bin/env python3
"""
Custom Network Proxy Server
Main proxy server implementation with concurrent request handling.
"""

import socket
import threading
import logging
import sys
import signal
from typing import Optional, Tuple
from http_parser import HTTPParser
from filter_manager import FilterManager
from logger import ProxyLogger
from config_loader import ConfigLoader


class ProxyServer:
    """Main proxy server class that handles client connections."""
    
    def __init__(self, config_path: str = "config/proxy_config.json"):
        """Initialize the proxy server with configuration."""
        self.config = ConfigLoader.load(config_path)
        self.filter_manager = FilterManager(self.config.get('blocked_domains_file', 'config/blocked_domains.txt'))
        self.logger = ProxyLogger(self.config.get('log_file', 'logs/proxy.log'))
        self.running = False
        self.server_socket: Optional[socket.socket] = None
        self.thread_pool = []
        self.thread_pool_size = self.config.get('thread_pool_size', 10)
        self.semaphore = threading.Semaphore(self.thread_pool_size)
        
    def start(self):
        """Start the proxy server and begin accepting connections."""
        try:
            # Create server socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind to address and port
            host = self.config.get('host', '127.0.0.1')
            port = self.config.get('port', 8888)
            self.server_socket.bind((host, port))
            self.server_socket.listen(self.config.get('backlog', 100))
            self.server_socket.settimeout(1.0)  # Allow periodic checks for shutdown
            
            self.running = True
            self.logger.log_info(f"Proxy server started on {host}:{port}")
            print(f"Proxy server listening on {host}:{port}")
            
            # Handle graceful shutdown
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            # Main accept loop
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    self.logger.log_info(f"New connection from {client_address[0]}:{client_address[1]}")
                    
                    # Use semaphore to limit concurrent connections
                    if self.semaphore.acquire(blocking=False):
                        thread = threading.Thread(
                            target=self._handle_client,
                            args=(client_socket, client_address),
                            daemon=True
                        )
                        thread.start()
                        self.thread_pool.append(thread)
                    else:
                        # Connection limit reached, reject
                        client_socket.close()
                        self.logger.log_warning(f"Connection rejected: thread pool full")
                        
                except socket.timeout:
                    continue
                except OSError as e:
                    if self.running:
                        self.logger.log_error(f"Error accepting connection: {e}")
                        
        except Exception as e:
            self.logger.log_error(f"Failed to start server: {e}")
            raise
        finally:
            self.shutdown()
    
    def _handle_client(self, client_socket: socket.socket, client_address: Tuple[str, int]):
        """Handle a single client connection in a separate thread."""
        try:
            # Set socket timeout
            client_socket.settimeout(30.0)
            
            # Receive and parse HTTP request
            parser = HTTPParser()
            request_data = self._receive_request(client_socket)
            
            if not request_data:
                return
            
            parsed_request = parser.parse_request(request_data)
            if not parsed_request:
                self.logger.log_error(f"Failed to parse request from {client_address}")
                client_socket.close()
                return
            
            method = parsed_request['method']
            host = parsed_request['host']
            port = parsed_request['port']
            path = parsed_request['path']
            
            # Reload filters if file changed (auto-reload)
            self.filter_manager.reload_if_changed()
            
            # Check if request should be blocked
            if self.filter_manager.is_blocked(host):
                self.logger.log_blocked(
                    client_address[0], client_address[1],
                    host, port, parsed_request['request_line']
                )
                response = "HTTP/1.1 403 Forbidden\r\n"
                response += "Content-Type: text/plain\r\n"
                response += "Content-Length: 13\r\n"
                response += "Connection: close\r\n\r\n"
                response += "Access Denied"
                client_socket.sendall(response.encode())
                client_socket.close()
                return
            
            # Handle CONNECT method for HTTPS tunneling
            if method == 'CONNECT':
                self._handle_connect(client_socket, client_address, host, port, parsed_request)
            else:
                # Handle regular HTTP requests
                self._handle_http_request(client_socket, client_address, host, port, parsed_request, request_data)
                
        except Exception as e:
            self.logger.log_error(f"Error handling client {client_address}: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass
            self.semaphore.release()
    
    def _receive_request(self, client_socket: socket.socket, max_size: int = 8192) -> Optional[bytes]:
        """Receive HTTP request from client, handling partial reads."""
        data = b''
        client_socket.settimeout(5.0)
        
        while len(data) < max_size:
            try:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                data += chunk
                # Check if we've received complete headers
                if b'\r\n\r\n' in data:
                    # Check for Content-Length
                    header_end = data.find(b'\r\n\r\n')
                    headers = data[:header_end].decode('utf-8', errors='ignore')
                    
                    # Extract Content-Length if present
                    content_length = 0
                    for line in headers.split('\r\n'):
                        if line.lower().startswith('content-length:'):
                            try:
                                content_length = int(line.split(':', 1)[1].strip())
                                break
                            except ValueError:
                                pass
                    
                    # If there's a body, read it
                    if content_length > 0:
                        body_start = header_end + 4
                        body_received = len(data) - body_start
                        while body_received < content_length:
                            chunk = client_socket.recv(min(4096, content_length - body_received))
                            if not chunk:
                                break
                            data += chunk
                            body_received += len(chunk)
                    
                    break
            except socket.timeout:
                if data:
                    break
                return None
            except Exception as e:
                self.logger.log_error(f"Error receiving request: {e}")
                return None
        
        return data if data else None
    
    def _handle_connect(self, client_socket: socket.socket, client_address: Tuple[str, int],
                       host: str, port: int, parsed_request: dict):
        """Handle HTTPS CONNECT tunneling."""
        try:
            # Connect to destination server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.settimeout(10.0)
            server_socket.connect((host, port))
            
            # Send 200 Connection Established
            response = "HTTP/1.1 200 Connection Established\r\n\r\n"
            client_socket.sendall(response.encode())
            
            self.logger.log_allowed(
                client_address[0], client_address[1],
                host, port, parsed_request['request_line'],
                "200", 0
            )
            
            # Bidirectional forwarding
            self._tunnel_connection(client_socket, server_socket)
            
        except socket.timeout:
            self.logger.log_error(f"Timeout connecting to {host}:{port}")
            error_response = "HTTP/1.1 504 Gateway Timeout\r\n\r\n"
            client_socket.sendall(error_response.encode())
        except Exception as e:
            self.logger.log_error(f"Error in CONNECT to {host}:{port}: {e}")
            error_response = "HTTP/1.1 502 Bad Gateway\r\n\r\n"
            client_socket.sendall(error_response.encode())
        finally:
            try:
                server_socket.close()
            except:
                pass
    
    def _handle_http_request(self, client_socket: socket.socket, client_address: Tuple[str, int],
                            host: str, port: int, parsed_request: dict, request_data: bytes):
        """Handle regular HTTP requests (GET, POST, etc.)."""
        server_socket = None
        try:
            # Connect to destination server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.settimeout(30.0)
            server_socket.connect((host, port))
            
            # Forward request to server
            server_socket.sendall(request_data)
            
            # Forward response from server to client
            response_size = 0
            status_code = "000"
            
            while True:
                chunk = server_socket.recv(4096)
                if not chunk:
                    break
                
                # Extract status code from first chunk
                if response_size == 0:
                    try:
                        status_line = chunk.decode('utf-8', errors='ignore').split('\r\n')[0]
                        if 'HTTP' in status_line:
                            parts = status_line.split()
                            if len(parts) >= 2:
                                status_code = parts[1]
                    except:
                        pass
                
                client_socket.sendall(chunk)
                response_size += len(chunk)
            
            self.logger.log_allowed(
                client_address[0], client_address[1],
                host, port, parsed_request['request_line'],
                status_code, response_size
            )
            
        except socket.timeout:
            self.logger.log_error(f"Timeout connecting to {host}:{port}")
            error_response = "HTTP/1.1 504 Gateway Timeout\r\n\r\n"
            client_socket.sendall(error_response.encode())
        except Exception as e:
            self.logger.log_error(f"Error forwarding request to {host}:{port}: {e}")
            error_response = "HTTP/1.1 502 Bad Gateway\r\n\r\n"
            client_socket.sendall(error_response.encode())
        finally:
            if server_socket:
                try:
                    server_socket.close()
                except:
                    pass
    
    def _tunnel_connection(self, client_socket: socket.socket, server_socket: socket.socket):
        """Tunnel data bidirectionally between client and server."""
        import select
        import platform
        
        sockets = [client_socket, server_socket]
        timeout = 300  # 5 minutes timeout
        
        # Use threading for Windows compatibility (select doesn't work well with sockets on Windows)
        if platform.system() == 'Windows':
            import threading
            
            def forward_data(source, dest, direction):
                try:
                    while True:
                        data = source.recv(4096)
                        if not data:
                            break
                        dest.sendall(data)
                except:
                    pass
            
            # Start two threads for bidirectional forwarding
            t1 = threading.Thread(target=forward_data, args=(client_socket, server_socket, 'client->server'), daemon=True)
            t2 = threading.Thread(target=forward_data, args=(server_socket, client_socket, 'server->client'), daemon=True)
            
            t1.start()
            t2.start()
            
            # Wait for either thread to finish
            t1.join(timeout=timeout)
            t2.join(timeout=0.1)
        else:
            # Use select on Unix-like systems
            while True:
                try:
                    readable, _, exceptional = select.select(sockets, [], sockets, timeout)
                    
                    if exceptional:
                        break
                    
                    if not readable:
                        break
                    
                    for sock in readable:
                        data = sock.recv(4096)
                        if not data:
                            return
                        
                        if sock is client_socket:
                            server_socket.sendall(data)
                        else:
                            client_socket.sendall(data)
                            
                except Exception as e:
                    self.logger.log_error(f"Error in tunnel: {e}")
                    break
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.log_info("Received shutdown signal, shutting down...")
        self.running = False
    
    def shutdown(self):
        """Shutdown the proxy server and cleanup resources."""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        self.logger.log_info("Proxy server shut down")


def main():
    """Main entry point for the proxy server."""
    import sys
    
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/proxy_config.json"
    
    try:
        server = ProxyServer(config_path)
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

