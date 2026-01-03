# Comprehensive Testing Guide

This guide provides step-by-step instructions to fully test your proxy server and verify it meets all requirements.

## 📋 Test Checklist

Use this checklist to ensure all features are tested:

- [ ] Basic HTTP request forwarding
- [ ] HTTPS CONNECT tunneling
- [ ] Domain blocking functionality
- [ ] IP address blocking
- [ ] Wildcard domain blocking
- [ ] Concurrent request handling
- [ ] Malformed request handling
- [ ] Logging functionality
- [ ] Configuration management
- [ ] Error handling
- [ ] Graceful shutdown
- [ ] Different HTTP methods (GET, POST, HEAD)
- [ ] Response streaming
- [ ] Large file handling

## 🚀 Setup for Testing

### Prerequisites

1. **Install dependencies:**
   ```bash
   pip install flask requests
   ```

2. **Start the proxy server:**
   ```bash
   python src/proxy_server.py config/proxy_config.json
   ```
   Keep this terminal open!

3. **Verify proxy is running:**
   - You should see: `Proxy server listening on 127.0.0.1:8888`
   - Check logs directory exists: `logs/proxy.log`

## ✅ Test 1: Basic HTTP Request Forwarding

### Objective
Verify the proxy correctly forwards HTTP requests and returns responses.

### Steps

1. **Test with curl:**
   ```bash
   curl -x http://127.0.0.1:8888 http://httpbin.org/get
   ```

2. **Expected Result:**
   - JSON response from httpbin.org
   - Status code: 200
   - Response contains request information

3. **Verify in logs:**
   ```bash
   # Windows
   Get-Content logs/proxy.log -Tail 5
   
   # Linux/Mac
   tail -5 logs/proxy.log
   ```
   Should show: `ALLOWED | ... -> httpbin.org:80 | GET ... | 200 | ... bytes`

4. **Test with web interface:**
   - Start web interface: `python src/web_interface.py`
   - Open browser: `http://127.0.0.1:5000`
   - Enter URL: `http://httpbin.org/get`
   - Click "Test Request"
   - Verify status 200 and response body

### ✅ Pass Criteria
- Request successfully forwarded
- Correct response received
- Log entry shows ALLOWED status
- Response time reasonable (< 5 seconds)

---

## ✅ Test 2: HTTPS CONNECT Tunneling

### Objective
Verify the proxy handles HTTPS requests using CONNECT method.

### Steps

1. **Test HTTPS request:**
   ```bash
   curl -x http://127.0.0.1:8888 https://www.google.com
   ```

2. **Expected Result:**
   - HTML content from Google
   - No SSL errors
   - Connection established successfully

3. **Verify in logs:**
   - Should show CONNECT method
   - Status 200 (Connection Established)
   - Host and port correctly logged

4. **Test with web interface:**
   - Enter URL: `https://www.google.com`
   - Click "Test Request"
   - Verify response received

### ✅ Pass Criteria
- HTTPS request succeeds
- CONNECT method used
- Encrypted tunnel established
- No certificate errors

---

## ✅ Test 3: Domain Blocking

### Objective
Verify the proxy blocks specified domains.

### Steps

1. **Add domain to blocked list:**
   - Edit `config/blocked_domains.txt`
   - Add: `example.com`
   - Save file

2. **Test blocked domain:**
   ```bash
   curl -x http://127.0.0.1:8888 http://example.com
   ```

3. **Expected Result:**
   - HTTP 403 Forbidden response
   - Response body: "Access Denied"
   - Request NOT forwarded to destination

4. **Verify in logs:**
   - Should show: `BLOCKED | ... -> example.com:80 | ...`
   - Log level: WARNING

5. **Test with web interface:**
   - Enter URL: `http://example.com`
   - Click "Test Request"
   - Verify "BLOCKED" badge and 403 status

### ✅ Pass Criteria
- Blocked domain returns 403
- Request not forwarded
- Log entry shows BLOCKED
- Response time is fast (no network delay)

---

## ✅ Test 4: IP Address Blocking

### Objective
Verify the proxy blocks specific IP addresses.

### Steps

1. **Find an IP to test:**
   ```bash
   # Get IP of a test domain
   nslookup httpbin.org
   ```

2. **Add IP to blocked list:**
   - Edit `config/blocked_domains.txt`
   - Add the IP address (e.g., `54.175.219.8`)
   - Save file

3. **Test blocked IP:**
   ```bash
   curl -x http://127.0.0.1:8888 http://httpbin.org/get
   ```

4. **Expected Result:**
   - HTTP 403 Forbidden
   - Request blocked even though domain not in list

5. **Verify in logs:**
   - Should show BLOCKED entry

### ✅ Pass Criteria
- IP blocking works
- Both domain and IP blocking functional
- Logs reflect blocking

---

## ✅ Test 5: Wildcard Domain Blocking

### Objective
Verify wildcard blocking (e.g., `*.example.com`).

### Steps

1. **Add wildcard to blocked list:**
   - Edit `config/blocked_domains.txt`
   - Add: `*.example.com`
   - Save file

2. **Test subdomain:**
   ```bash
   curl -x http://127.0.0.1:8888 http://subdomain.example.com
   ```

3. **Expected Result:**
   - HTTP 403 Forbidden
   - All subdomains of example.com blocked

4. **Test exact domain:**
   ```bash
   curl -x http://127.0.0.1:8888 http://example.com
   ```
   - Should also be blocked

### ✅ Pass Criteria
- Wildcard blocking works
- Subdomains blocked correctly
- Exact domain also blocked

---

## ✅ Test 6: Concurrent Request Handling

### Objective
Verify the proxy handles multiple simultaneous requests.

### Steps

1. **Test with multiple curl processes:**
   ```bash
   # Windows PowerShell
   1..10 | ForEach-Object -Parallel { 
       curl -x http://127.0.0.1:8888 http://httpbin.org/get 
   }
   
   # Linux/Mac
   for i in {1..10}; do 
       curl -x http://127.0.0.1:8888 http://httpbin.org/get &
   done
   wait
   ```

2. **Expected Result:**
   - All requests complete successfully
   - No connection refused errors
   - All responses received

3. **Verify in logs:**
   - Multiple ALLOWED entries
   - Timestamps show concurrent processing
   - No errors or timeouts

4. **Test with Python script:**
   ```bash
   python tests/test_concurrent.py
   ```

5. **Monitor thread pool:**
   - Check that thread pool size limits are respected
   - Verify no resource exhaustion

### ✅ Pass Criteria
- All concurrent requests succeed
- No connection errors
- Thread pool handles load correctly
- Response times reasonable

---

## ✅ Test 7: Different HTTP Methods

### Objective
Verify the proxy handles GET, POST, HEAD methods.

### Steps

1. **Test GET:**
   ```bash
   curl -x http://127.0.0.1:8888 http://httpbin.org/get
   ```
   - Should return 200 with response body

2. **Test POST:**
   ```bash
   curl -x http://127.0.0.1:8888 -X POST -d "test=data" http://httpbin.org/post
   ```
   - Should return 200 with posted data in response

3. **Test HEAD:**
   ```bash
   curl -x http://127.0.0.1:8888 -I http://httpbin.org/get
   ```
   - Should return 200 with headers only (no body)

4. **Verify in logs:**
   - Each method logged correctly
   - Request line shows correct method

### ✅ Pass Criteria
- All methods work correctly
- Request bodies forwarded for POST
- HEAD returns headers only
- Logs show correct methods

---

## ✅ Test 8: Malformed Request Handling

### Objective
Verify the proxy handles invalid/malformed requests gracefully.

### Steps

1. **Test with netcat (raw socket):**
   ```bash
   # Send invalid request
   echo -e "INVALID REQUEST\r\n\r\n" | nc 127.0.0.1 8888
   ```

2. **Test with incomplete request:**
   ```bash
   echo -e "GET /" | nc 127.0.0.1 8888
   ```

3. **Test with missing headers:**
   ```bash
   echo -e "GET http://example.com HTTP/1.1\r\n\r\n" | nc 127.0.0.1 8888
   ```

4. **Expected Result:**
   - Proxy doesn't crash
   - Connection closed gracefully
   - Error logged appropriately

5. **Verify in logs:**
   - Error entries for malformed requests
   - No server crashes

### ✅ Pass Criteria
- Proxy handles errors gracefully
- No crashes or exceptions
- Errors logged appropriately
- Connections closed properly

---

## ✅ Test 9: Logging Functionality

### Objective
Verify comprehensive logging of all activities.

### Steps

1. **Make various requests:**
   ```bash
   curl -x http://127.0.0.1:8888 http://httpbin.org/get
   curl -x http://127.0.0.1:8888 http://example.com  # if blocked
   curl -x http://127.0.0.1:8888 https://www.google.com
   ```

2. **Check log file:**
   ```bash
   # Windows
   Get-Content logs/proxy.log
   
   # Linux/Mac
   cat logs/proxy.log
   ```

3. **Verify log entries contain:**
   - Timestamp
   - Client IP:port
   - Destination host:port
   - Request line
   - Action (ALLOWED/BLOCKED)
   - Status code
   - Response size (for allowed)

4. **Check log format:**
   - Consistent format
   - Readable timestamps
   - All required information present

### ✅ Pass Criteria
- All requests logged
- Log format consistent
- Timestamps accurate
- All required fields present
- Logs readable and parseable

---

## ✅ Test 10: Configuration Management

### Objective
Verify configuration file loading and settings.

### Steps

1. **Test default configuration:**
   - Start proxy without config file
   - Verify defaults used (port 8888, etc.)

2. **Modify configuration:**
   - Edit `config/proxy_config.json`
   - Change port to 9999
   - Change thread_pool_size to 5

3. **Restart proxy:**
   ```bash
   python src/proxy_server.py config/proxy_config.json
   ```

4. **Test with new port:**
   ```bash
   curl -x http://127.0.0.1:9999 http://httpbin.org/get
   ```

5. **Verify settings applied:**
   - Proxy listens on new port
   - Thread pool size changed
   - Other settings respected

### ✅ Pass Criteria
- Configuration loaded correctly
- Settings applied
- Defaults work if config missing
- Invalid config handled gracefully

---

## ✅ Test 11: Error Handling

### Objective
Verify proxy handles various error conditions.

### Steps

1. **Test unreachable destination:**
   ```bash
   curl -x http://127.0.0.1:8888 http://192.0.2.1:80/get
   ```
   - Should return 502 or 504 error
   - Error logged

2. **Test timeout:**
   - Request to slow/unresponsive server
   - Verify timeout handling

3. **Test invalid hostname:**
   ```bash
   curl -x http://127.0.0.1:8888 http://nonexistent-domain-12345.com
   ```
   - Should handle DNS error gracefully

4. **Verify error responses:**
   - Appropriate HTTP error codes
   - Error messages in logs
   - No crashes

### ✅ Pass Criteria
- Errors handled gracefully
- Appropriate error codes returned
- Errors logged
- No crashes or hangs

---

## ✅ Test 12: Graceful Shutdown

### Objective
Verify proxy shuts down cleanly.

### Steps

1. **Start proxy with active connections:**
   ```bash
   python src/proxy_server.py config/proxy_config.json
   ```

2. **Make a request (keep it running):**
   ```bash
   curl -x http://127.0.0.1:8888 http://httpbin.org/delay/5
   ```

3. **Send shutdown signal:**
   - Press `Ctrl+C` in proxy terminal

4. **Expected Result:**
   - Shutdown message logged
   - Active connections closed
   - Resources cleaned up
   - No errors or exceptions

### ✅ Pass Criteria
- Clean shutdown
- Resources released
- Logs show shutdown message
- No resource leaks

---

## ✅ Test 13: Response Streaming

### Objective
Verify large responses are streamed correctly.

### Steps

1. **Test large response:**
   ```bash
   curl -x http://127.0.0.1:8888 http://httpbin.org/bytes/100000
   ```
   - Should receive 100KB of data
   - Response streamed (not buffered entirely)

2. **Monitor memory usage:**
   - Check proxy doesn't buffer entire response
   - Verify streaming behavior

3. **Test with web interface:**
   - Request large file
   - Verify response received correctly

### ✅ Pass Criteria
- Large responses handled
- Streaming works correctly
- No memory issues
- Response complete

---

## ✅ Test 14: Request with Headers

### Objective
Verify custom headers are forwarded correctly.

### Steps

1. **Test with custom headers:**
   ```bash
   curl -x http://127.0.0.1:8888 \
        -H "Custom-Header: test-value" \
        -H "User-Agent: CustomAgent/1.0" \
        http://httpbin.org/headers
   ```

2. **Expected Result:**
   - Response shows forwarded headers
   - Custom headers preserved
   - User-Agent updated

3. **Verify in response:**
   - Headers present in httpbin response
   - Values correct

### ✅ Pass Criteria
- Headers forwarded correctly
- Custom headers preserved
- No header loss or corruption

---

## 📊 Automated Test Suite

Run the automated test suite:

```bash
# Basic tests
python tests/test_basic.py

# Concurrent tests
python tests/test_concurrent.py
```

## 🎯 Complete Test Matrix

| Test Case | Method | Expected Result | Status |
|-----------|--------|----------------|--------|
| HTTP GET | curl | 200 OK, response body | ⬜ |
| HTTPS CONNECT | curl | 200 OK, HTML content | ⬜ |
| Domain Block | curl | 403 Forbidden | ⬜ |
| IP Block | curl | 403 Forbidden | ⬜ |
| Wildcard Block | curl | 403 Forbidden | ⬜ |
| Concurrent (10) | script | All succeed | ⬜ |
| GET Method | curl | 200 OK | ⬜ |
| POST Method | curl | 200 OK, data echoed | ⬜ |
| HEAD Method | curl | 200 OK, headers only | ⬜ |
| Malformed Request | netcat | Graceful error | ⬜ |
| Logging | file | All entries present | ⬜ |
| Configuration | config | Settings applied | ⬜ |
| Error Handling | curl | Appropriate errors | ⬜ |
| Shutdown | Ctrl+C | Clean exit | ⬜ |
| Large Response | curl | Streamed correctly | ⬜ |

## 📝 Test Report Template

After completing tests, document results:

```
Test Date: __________
Tester: __________

Test Results:
- Basic HTTP: ✅ / ❌
- HTTPS: ✅ / ❌
- Blocking: ✅ / ❌
- Concurrency: ✅ / ❌
- Error Handling: ✅ / ❌
- Logging: ✅ / ❌

Issues Found:
1. __________
2. __________

Overall Status: PASS / FAIL
```

## 🎓 Verification Checklist

Before considering testing complete, verify:

- [ ] All test cases executed
- [ ] Expected results match actual results
- [ ] Logs reviewed and correct
- [ ] No crashes or exceptions
- [ ] Error handling works
- [ ] Configuration changes applied
- [ ] Concurrent requests handled
- [ ] Blocking works correctly
- [ ] HTTPS tunneling functional
- [ ] Documentation matches behavior

## 🚨 Common Issues and Solutions

### Issue: Connection Refused
- **Solution**: Ensure proxy server is running
- **Check**: Port 8888 not in use by another process

### Issue: 403 on All Requests
- **Solution**: Check blocked_domains.txt for overly broad rules
- **Check**: Filter manager logic

### Issue: Timeout Errors
- **Solution**: Check internet connectivity
- **Solution**: Increase timeout values in code

### Issue: No Logs Generated
- **Solution**: Check logs directory exists
- **Solution**: Verify file permissions

### Issue: HTTPS Not Working
- **Solution**: Verify CONNECT method handling
- **Solution**: Check tunnel implementation

## ✅ Final Verification

Once all tests pass:

1. ✅ Proxy forwards HTTP requests correctly
2. ✅ Proxy handles HTTPS with CONNECT
3. ✅ Blocking works for domains and IPs
4. ✅ Concurrent requests handled properly
5. ✅ Malformed requests don't crash server
6. ✅ Comprehensive logging functional
7. ✅ Configuration management works
8. ✅ Error handling robust
9. ✅ Graceful shutdown implemented
10. ✅ All requirements met

**Congratulations! Your proxy server is fully tested and ready! 🎉**

