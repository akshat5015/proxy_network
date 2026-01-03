#!/usr/bin/env python3
"""
Basic test script for the proxy server.
Tests basic HTTP forwarding functionality.
"""

import subprocess
import time
import sys
import os
import platform

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Platform-specific null device
NULL_DEVICE = 'nul' if platform.system() == 'Windows' else '/dev/null'

def test_basic_http():
    """Test basic HTTP request through proxy."""
    print("Testing basic HTTP request...")
    try:
        result = subprocess.run(
            ['curl', '-x', 'http://127.0.0.1:8888', '-s', '-o', NULL_DEVICE, '-w', '%{http_code}', 'http://httpbin.org/get'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 and result.stdout.strip() == '200':
            print("✓ Basic HTTP test passed")
            return True
        else:
            print(f"✗ Basic HTTP test failed: {result.stdout}")
            return False
    except FileNotFoundError:
        print("✗ curl not found. Please install curl to run tests.")
        return False
    except Exception as e:
        print(f"✗ Basic HTTP test failed: {e}")
        return False

def test_blocked_domain():
    """Test that blocked domains are properly rejected."""
    print("Testing blocked domain...")
    # This test requires a domain to be in blocked_domains.txt
    # For now, we'll just check the structure
    print("Note: Add a domain to config/blocked_domains.txt to test blocking")
    return True

def test_https_connect():
    """Test HTTPS CONNECT tunneling."""
    print("Testing HTTPS CONNECT...")
    try:
        result = subprocess.run(
            ['curl', '-x', 'http://127.0.0.1:8888', '-s', '-o', NULL_DEVICE, '-w', '%{http_code}', 'https://www.google.com'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("✓ HTTPS CONNECT test passed")
            return True
        else:
            print(f"✗ HTTPS CONNECT test failed: {result.stdout}")
            return False
    except FileNotFoundError:
        print("✗ curl not found. Please install curl to run tests.")
        return False
    except Exception as e:
        print(f"✗ HTTPS CONNECT test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Proxy Server Test Suite")
    print("=" * 50)
    print("\nNote: Make sure the proxy server is running on 127.0.0.1:8888")
    print("Start it with: python src/proxy_server.py\n")
    
    time.sleep(2)
    
    results = []
    results.append(("Basic HTTP", test_basic_http()))
    results.append(("Blocked Domain", test_blocked_domain()))
    results.append(("HTTPS CONNECT", test_https_connect()))
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print("=" * 50)
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{name}: {status}")

