#!/usr/bin/env python3
"""
Manual test script to verify domain blocking works.
Run this to debug blocking issues.
"""

import requests
import time
import os

PROXY_URL = "http://127.0.0.1:8888"
BLOCKED_FILE = "config/blocked_domains.txt"

print("=" * 60)
print("Domain Blocking Manual Test")
print("=" * 60)

# Step 1: Check current blocked list
print("\n1. Checking blocked domains file...")
if os.path.exists(BLOCKED_FILE):
    with open(BLOCKED_FILE, 'r') as f:
        content = f.read()
        print(f"   File exists. Content:\n{content}")
        has_example = 'example.com' in content
        print(f"   Contains 'example.com': {has_example}")
else:
    print("   File does not exist!")

# Step 2: Add example.com if not present
print("\n2. Ensuring example.com is in blocked list...")
with open(BLOCKED_FILE, 'a', encoding='utf-8') as f:
    f.write('\nexample.com\n')
    f.flush()
    os.fsync(f.fileno())

time.sleep(0.5)

# Step 3: Verify it was added
print("\n3. Verifying addition...")
with open(BLOCKED_FILE, 'r') as f:
    content = f.read()
    if 'example.com' in content:
        print("   ✓ example.com found in file")
    else:
        print("   ✗ example.com NOT found in file")
        exit(1)

# Step 4: Make a dummy request to trigger reload
print("\n4. Making dummy request to trigger filter reload...")
try:
    response = requests.get('http://httpbin.org/get', 
                          proxies={'http': PROXY_URL}, 
                          timeout=5)
    print(f"   ✓ Dummy request completed (status: {response.status_code})")
except Exception as e:
    print(f"   ⚠ Dummy request failed: {e}")

time.sleep(2)  # Wait for reload

# Step 5: Test blocking
print("\n5. Testing if example.com is blocked...")
try:
    response = requests.get('http://example.com',
                          proxies={'http': PROXY_URL},
                          timeout=5,
                          allow_redirects=False)
    
    print(f"   Status Code: {response.status_code}")
    print(f"   Response: {response.text[:100]}")
    
    if response.status_code == 403:
        print("   ✅ SUCCESS: Domain is blocked!")
    else:
        print(f"   ❌ FAIL: Expected 403, got {response.status_code}")
        print("   The proxy is not blocking the domain.")
        
except requests.exceptions.ProxyError as e:
    if '403' in str(e) or 'Forbidden' in str(e):
        print("   ✅ SUCCESS: Domain is blocked (403 in error)")
    else:
        print(f"   ⚠ Proxy error: {e}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)

