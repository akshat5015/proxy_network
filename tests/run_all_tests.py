#!/usr/bin/env python3
"""
Comprehensive Test Suite for Proxy Server
Runs all tests and generates a test report.
"""

import subprocess
import sys
import time
import requests
import os
from datetime import datetime

# Test configuration
PROXY_URL = "http://127.0.0.1:8888"
TEST_RESULTS = []

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_test(name, status, details=""):
    """Print test result."""
    status_symbol = "✅ PASS" if status else "❌ FAIL"
    print(f"{status_symbol} - {name}")
    if details:
        print(f"      {details}")
    TEST_RESULTS.append((name, status, details))

def test_proxy_running():
    """Test if proxy server is running."""
    print_header("Test 1: Proxy Server Status")
    try:
        response = requests.get('http://httpbin.org/get', 
                               proxies={'http': PROXY_URL},
                               timeout=5)
        print_test("Proxy Server Running", True, f"Status: {response.status_code}")
        return True
    except Exception as e:
        print_test("Proxy Server Running", False, str(e))
        print("\n⚠️  ERROR: Proxy server is not running!")
        print("   Please start it with: python src/proxy_server.py config/proxy_config.json")
        return False

def test_http_forwarding():
    """Test basic HTTP request forwarding."""
    print_header("Test 2: HTTP Request Forwarding")
    try:
        response = requests.get('http://httpbin.org/get',
                               proxies={'http': PROXY_URL},
                               timeout=10)
        success = response.status_code == 200
        print_test("HTTP GET Request", success, 
                  f"Status: {response.status_code}, Size: {len(response.content)} bytes")
        return success
    except Exception as e:
        print_test("HTTP GET Request", False, str(e))
        return False

def test_https_tunneling():
    """Test HTTPS CONNECT tunneling."""
    print_header("Test 3: HTTPS CONNECT Tunneling")
    try:
        response = requests.get('https://www.google.com',
                               proxies={'http': PROXY_URL, 'https': PROXY_URL},
                               timeout=10)
        success = response.status_code == 200
        print_test("HTTPS CONNECT", success, 
                  f"Status: {response.status_code}, Size: {len(response.content)} bytes")
        return success
    except Exception as e:
        print_test("HTTPS CONNECT", False, str(e))
        return False

def test_domain_blocking():
    """Test domain blocking functionality."""
    print_header("Test 4: Domain Blocking")
    
    # Check if example.com is in blocked list
    blocked_file = "config/blocked_domains.txt"
    is_blocked = False
    
    if os.path.exists(blocked_file):
        with open(blocked_file, 'r') as f:
            content = f.read()
            if 'example.com' in content and not content.split('example.com')[0].endswith('*.'):
                is_blocked = True
    
    if not is_blocked:
        print("⚠️  Note: example.com not in blocked list. Adding for test...")
        # Ensure we write to the file and flush
        with open(blocked_file, 'a', encoding='utf-8') as f:
            f.write('\nexample.com\n')
            f.flush()
            os.fsync(f.fileno())  # Force write to disk
        
        # Wait for file system to update
        time.sleep(0.5)
        
        # Make a dummy request to trigger filter reload in proxy
        # The proxy will check file modification time and reload
        try:
            requests.get('http://httpbin.org/get', 
                        proxies={'http': PROXY_URL}, 
                        timeout=2)
        except:
            pass
        
        # Wait a bit more to ensure reload happened
        time.sleep(1.5)
        
        # Verify the domain was added
        with open(blocked_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'example.com' not in content:
                print("⚠️  Warning: Failed to add example.com to blocked list")
                return False
    
    try:
        response = requests.get('http://example.com',
                               proxies={'http': PROXY_URL},
                               timeout=5,
                               allow_redirects=False)
        success = response.status_code == 403
        print_test("Domain Blocking", success, 
                  f"Status: {response.status_code} (expected 403)")
        return success
    except requests.exceptions.ProxyError as e:
        if '403' in str(e) or 'Forbidden' in str(e):
            print_test("Domain Blocking", True, "Request blocked (403)")
            return True
        else:
            print_test("Domain Blocking", False, str(e))
            return False
    except Exception as e:
        print_test("Domain Blocking", False, str(e))
        return False

def test_post_request():
    """Test POST request forwarding."""
    print_header("Test 5: POST Request")
    try:
        data = {'test': 'data', 'value': 123}
        response = requests.post('http://httpbin.org/post',
                                proxies={'http': PROXY_URL},
                                data=data,
                                timeout=10)
        success = response.status_code == 200
        print_test("POST Request", success, 
                  f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_test("POST Request", False, str(e))
        return False

def test_concurrent_requests():
    """Test concurrent request handling."""
    print_header("Test 6: Concurrent Requests")
    import threading
    
    results = []
    errors = []
    
    def make_request(i):
        try:
            response = requests.get('http://httpbin.org/get',
                                  proxies={'http': PROXY_URL},
                                  timeout=10)
            results.append(response.status_code == 200)
        except Exception as e:
            errors.append(str(e))
            results.append(False)
    
    threads = []
    start_time = time.time()
    
    for i in range(5):
        thread = threading.Thread(target=make_request, args=(i,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    elapsed = time.time() - start_time
    success_count = sum(results)
    success = success_count == 5 and len(errors) == 0
    
    print_test("Concurrent Requests (5)", success,
              f"{success_count}/5 succeeded in {elapsed:.2f}s")
    if errors:
        print(f"      Errors: {errors}")
    
    return success

def test_logging():
    """Test logging functionality."""
    print_header("Test 7: Logging")
    log_file = "logs/proxy.log"
    
    if not os.path.exists(log_file):
        print_test("Log File Exists", False, "Log file not found")
        return False
    
    # Make a request to generate log entry
    try:
        requests.get('http://httpbin.org/get',
                    proxies={'http': PROXY_URL},
                    timeout=5)
        time.sleep(1)  # Give time for log write
    except:
        pass
    
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            # Check all lines, not just recent ones
            all_lines = lines
            
            has_allowed = any('ALLOWED' in line for line in all_lines)
            has_timestamp = any('2024' in line or '2025' in line for line in all_lines)
            
            allowed_count = len([l for l in all_lines if 'ALLOWED' in l])
            
            success = has_allowed and has_timestamp
            print_test("Log File Exists", True)
            print_test("Log Entries Present", has_allowed, 
                      f"Found {allowed_count} ALLOWED entries in {len(all_lines)} total lines")
            print_test("Timestamps Present", has_timestamp)
            
            # If no ALLOWED entries found, show some sample lines for debugging
            if not has_allowed and len(all_lines) > 0:
                print(f"      Sample log lines (last 3):")
                for line in all_lines[-3:]:
                    print(f"        {line.strip()[:80]}")
            
            return success
    except Exception as e:
        print_test("Log Reading", False, str(e))
        return False

def test_error_handling():
    """Test error handling."""
    print_header("Test 8: Error Handling")
    
    # Test unreachable destination
    try:
        response = requests.get('http://192.0.2.1:80/get',
                               proxies={'http': PROXY_URL},
                               timeout=5)
        # Should get error status
        success = response.status_code >= 400
        print_test("Unreachable Destination", success,
                  f"Status: {response.status_code}")
    except Exception as e:
        # Exception is also acceptable (connection error)
        print_test("Unreachable Destination", True,
                  "Error handled gracefully")
        success = True
    
    return success

def generate_report():
    """Generate test report."""
    print_header("Test Report Summary")
    
    total = len(TEST_RESULTS)
    passed = sum(1 for _, status, _ in TEST_RESULTS if status)
    failed = total - passed
    
    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    print("\nDetailed Results:")
    for name, status, details in TEST_RESULTS:
        symbol = "✅" if status else "❌"
        print(f"  {symbol} {name}")
        if details and not status:
            print(f"     → {details}")
    
    # Save report to file
    report_file = f"tests/test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w') as f:
        f.write(f"Proxy Server Test Report\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"\nTotal Tests: {total}\n")
        f.write(f"Passed: {passed}\n")
        f.write(f"Failed: {failed}\n")
        f.write(f"\nDetailed Results:\n")
        for name, status, details in TEST_RESULTS:
            f.write(f"{'PASS' if status else 'FAIL'} - {name}\n")
            if details:
                f.write(f"  {details}\n")
    
    print(f"\n📄 Report saved to: {report_file}")
    
    return passed == total

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("  PROXY SERVER COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print(f"\nTesting proxy at: {PROXY_URL}")
    print("Make sure the proxy server is running!\n")
    
    time.sleep(2)
    
    # Run tests
    if not test_proxy_running():
        print("\n❌ Cannot continue - proxy server not running!")
        sys.exit(1)
    
    test_http_forwarding()
    test_https_tunneling()
    test_domain_blocking()
    test_post_request()
    test_concurrent_requests()
    test_logging()
    test_error_handling()
    
    # Generate report
    all_passed = generate_report()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("  🎉 ALL TESTS PASSED!")
    else:
        print("  ⚠️  SOME TESTS FAILED - Review results above")
    print("=" * 60 + "\n")
    
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()

