#!/usr/bin/env python3
"""
Concurrent test script for the proxy server.
Tests the proxy's ability to handle multiple simultaneous requests.
"""

import subprocess
import threading
import time
import sys
import platform

# Platform-specific null device
NULL_DEVICE = 'nul' if platform.system() == 'Windows' else '/dev/null'

def make_request(url, proxy, request_id):
    """Make a single HTTP request through the proxy."""
    try:
        result = subprocess.run(
            ['curl', '-x', f'http://{proxy}', '-s', '-o', NULL_DEVICE, '-w', f'{request_id}:%{{http_code}}\n', url],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip()
    except FileNotFoundError:
        return f"{request_id}:ERROR - curl not found"
    except Exception as e:
        return f"{request_id}:ERROR - {e}"

def test_concurrent_requests(num_requests=10):
    """Test concurrent requests."""
    print(f"Testing {num_requests} concurrent requests...")
    
    proxy = "127.0.0.1:8888"
    url = "http://httpbin.org/get"
    
    threads = []
    results = []
    
    def worker(request_id):
        result = make_request(url, proxy, request_id)
        results.append(result)
    
    # Start all threads
    start_time = time.time()
    for i in range(num_requests):
        thread = threading.Thread(target=worker, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    # Print results
    print(f"\nCompleted {num_requests} requests in {elapsed:.2f} seconds")
    print(f"Average: {elapsed/num_requests:.2f} seconds per request")
    print("\nResults:")
    for result in sorted(results):
        print(f"  {result}")
    
    # Count successes
    successes = sum(1 for r in results if '200' in r)
    print(f"\nSuccess rate: {successes}/{num_requests} ({100*successes/num_requests:.1f}%)")
    
    return successes == num_requests

if __name__ == "__main__":
    print("=" * 50)
    print("Concurrent Request Test")
    print("=" * 50)
    print("\nNote: Make sure the proxy server is running on 127.0.0.1:8888")
    print("Start it with: python src/proxy_server.py\n")
    
    time.sleep(2)
    
    test_concurrent_requests(10)

