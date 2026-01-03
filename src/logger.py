#!/usr/bin/env python3
"""
Proxy Logger
Handles logging of proxy requests, responses, and events.
"""

import os
import logging
from datetime import datetime
from typing import Optional


class ProxyLogger:
    """Logger for proxy server events and requests."""
    
    def __init__(self, log_file: str = "logs/proxy.log"):
        """
        Initialize logger.
        
        Args:
            log_file: Path to log file
        """
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Configure logging
        self.logger = logging.getLogger('ProxyServer')
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        self.logger.handlers = []
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.log_file = log_file
    
    def log_info(self, message: str):
        """Log an info message."""
        self.logger.info(message)
    
    def log_error(self, message: str):
        """Log an error message."""
        self.logger.error(message)
    
    def log_warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)
    
    def log_allowed(self, client_ip: str, client_port: int, 
                   host: str, port: int, request_line: str,
                   status_code: str, response_size: int):
        """
        Log an allowed request.
        
        Args:
            client_ip: Client IP address
            client_port: Client port
            host: Destination host
            port: Destination port
            request_line: HTTP request line
            status_code: HTTP response status code
            response_size: Size of response in bytes
        """
        message = f"ALLOWED | {client_ip}:{client_port} -> {host}:{port} | {request_line} | {status_code} | {response_size} bytes"
        self.logger.info(message)
    
    def log_blocked(self, client_ip: str, client_port: int,
                   host: str, port: int, request_line: str):
        """
        Log a blocked request.
        
        Args:
            client_ip: Client IP address
            client_port: Client port
            host: Destination host
            port: Destination port
            request_line: HTTP request line
        """
        message = f"BLOCKED | {client_ip}:{client_port} -> {host}:{port} | {request_line}"
        self.logger.warning(message)

