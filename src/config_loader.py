#!/usr/bin/env python3
"""
Configuration Loader
Loads and validates proxy server configuration from JSON file.
"""

import json
import os
from typing import Dict, Any


class ConfigLoader:
    """Loads configuration from JSON file."""
    
    @staticmethod
    def load(config_path: str) -> Dict[str, Any]:
        """
        Load configuration from JSON file.
        
        Args:
            config_path: Path to configuration JSON file
            
        Returns:
            Dictionary containing configuration values
        """
        default_config = {
            'host': '127.0.0.1',
            'port': 8888,
            'thread_pool_size': 10,
            'backlog': 100,
            'blocked_domains_file': 'config/blocked_domains.txt',
            'log_file': 'logs/proxy.log'
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON in config file: {e}")
                print("Using default configuration")
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
                print("Using default configuration")
        else:
            # Create default config file
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
            print(f"Created default configuration file: {config_path}")
        
        return default_config

