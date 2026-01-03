#!/usr/bin/env python3
"""
HTTP Request Parser
Parses HTTP requests to extract method, host, port, path, and headers.
"""

import re
from typing import Optional, Dict


class HTTPParser:
    """Parser for HTTP requests."""
    
    def __init__(self):
        self.request_line_pattern = re.compile(
            r'^([A-Z]+)\s+(.+?)\s+(HTTP/\d\.\d)$',
            re.IGNORECASE
        )
    
    def parse_request(self, request_data: bytes) -> Optional[Dict]:
        """
        Parse HTTP request and return dictionary with parsed components.
        
        Returns:
            Dictionary with keys: method, host, port, path, request_line, headers
            Returns None if parsing fails.
        """
        try:
            request_text = request_data.decode('utf-8', errors='ignore')
            lines = request_text.split('\r\n')
            
            if not lines:
                return None
            
            # Parse request line
            request_line = lines[0]
            match = self.request_line_pattern.match(request_line)
            if not match:
                return None
            
            method = match.group(1).upper()
            target = match.group(2)
            version = match.group(3)
            
            # Parse headers
            headers = {}
            header_end = request_text.find('\r\n\r\n')
            if header_end != -1:
                header_text = request_text[:header_end]
                for line in header_text.split('\r\n')[1:]:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        headers[key.strip().lower()] = value.strip()
            
            # Extract host and port
            host = None
            port = 80  # Default HTTP port
            
            # Check if target is absolute URI
            if target.startswith('http://') or target.startswith('https://'):
                # Absolute URI
                from urllib.parse import urlparse
                parsed = urlparse(target)
                host = parsed.hostname
                if parsed.port:
                    port = parsed.port
                elif parsed.scheme == 'https':
                    port = 443
                path = parsed.path or '/'
                if parsed.query:
                    path += '?' + parsed.query
            else:
                # Relative URI, get host from Host header
                host_header = headers.get('host', '')
                if ':' in host_header:
                    host, port_str = host_header.rsplit(':', 1)
                    try:
                        port = int(port_str)
                    except ValueError:
                        port = 80
                else:
                    host = host_header
                path = target
            
            if not host:
                return None
            
            return {
                'method': method,
                'host': host,
                'port': port,
                'path': path,
                'request_line': request_line,
                'headers': headers,
                'version': version
            }
            
        except Exception as e:
            return None

