#!/usr/bin/env python3
"""
Filter Manager
Manages domain and IP filtering rules for blocking requests.
"""

import os
import ipaddress
from typing import Set, List
from pathlib import Path


class FilterManager:
    """Manages filtering rules for blocking domains and IPs."""
    
    def __init__(self, filter_file: str = "config/blocked_domains.txt"):
        """
        Initialize filter manager with rules from file.
        
        Args:
            filter_file: Path to file containing blocked domains/IPs (one per line)
        """
        self.filter_file = filter_file
        self.blocked_domains: Set[str] = set()
        self.blocked_ips: Set[str] = set()
        self.blocked_suffixes: List[str] = []  # For wildcard matching like *.example.com
        self._last_modified = 0
        
        if os.path.exists(filter_file):
            self.load_filters(filter_file)
        else:
            # Create default empty filter file
            os.makedirs(os.path.dirname(filter_file), exist_ok=True)
            with open(filter_file, 'w') as f:
                f.write("# Blocked domains and IPs\n")
                f.write("# One entry per line\n")
                f.write("# Lines starting with # are comments\n")
    
    def load_filters(self, filter_file: str = None):
        """Load filtering rules from file."""
        if filter_file is None:
            filter_file = self.filter_file
        
        try:
            # Clear existing filters
            self.blocked_domains.clear()
            self.blocked_ips.clear()
            self.blocked_suffixes.clear()
            
            with open(filter_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Check if it's an IP address
                    try:
                        ipaddress.ip_address(line)
                        self.blocked_ips.add(line)
                    except ValueError:
                        # Not an IP, treat as domain
                        domain = line.lower()
                        if domain.startswith('*.'):
                            # Wildcard suffix
                            self.blocked_suffixes.append(domain[2:])
                        else:
                            self.blocked_domains.add(domain)
            
            # Update last modified time
            if os.path.exists(filter_file):
                self._last_modified = os.path.getmtime(filter_file)
            
        except Exception as e:
            print(f"Warning: Could not load filter file {filter_file}: {e}")
    
    def reload_if_changed(self):
        """Reload filters if the file has been modified."""
        if not os.path.exists(self.filter_file):
            return False
        
        try:
            current_modified = os.path.getmtime(self.filter_file)
            # Use a small tolerance to handle filesystem timing issues
            if current_modified > self._last_modified + 0.1:  # 100ms tolerance
                self.load_filters()
                return True
        except (OSError, ValueError):
            # File might have been deleted or is inaccessible
            pass
        return False
    
    def force_reload(self):
        """Force a reload of filters from file."""
        if os.path.exists(self.filter_file):
            self.load_filters()
            return True
        return False
    
    def is_blocked(self, host: str) -> bool:
        """
        Check if a host (domain or IP) is blocked.
        
        Args:
            host: Hostname or IP address to check
            
        Returns:
            True if host is blocked, False otherwise
        """
        if not host:
            return False
        
        host = host.lower().strip()
        
        # Check exact IP match
        if host in self.blocked_ips:
            return True
        
        # Check if host is an IP and matches blocked IPs
        try:
            host_ip = ipaddress.ip_address(host)
            if str(host_ip) in self.blocked_ips:
                return True
        except ValueError:
            pass  # Not an IP, continue with domain checks
        
        # Check exact domain match
        if host in self.blocked_domains:
            return True
        
        # Check suffix matches (e.g., *.example.com)
        for suffix in self.blocked_suffixes:
            if host.endswith('.' + suffix) or host == suffix:
                return True
        
        return False
    
    def add_blocked_domain(self, domain: str):
        """Add a domain to the blocked list."""
        self.blocked_domains.add(domain.lower().strip())
    
    def add_blocked_ip(self, ip: str):
        """Add an IP to the blocked list."""
        try:
            ipaddress.ip_address(ip)  # Validate
            self.blocked_ips.add(ip)
        except ValueError:
            raise ValueError(f"Invalid IP address: {ip}")

