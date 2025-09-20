# Monica Connection Troubleshooting

## Error: WinError 10054 - Connection Forcibly Closed

This error means the Pico is closing the connection unexpectedly. Here's how to fix it:

### 🔍 **Immediate Diagnostics**

1. **Run the diagnostic tool**:
   ```bash
   cd local_webserver
   python test_connection.py [PICO_IP]
   ```

2. **Check Pico console** for error messages like:
   - Memory allocation errors
   - JSON decode errors
   - Hardware command failures

### 🛠️ **Common Fixes**

#### **1. Restart the Pico**
- **Why**: Memory fragmentation or crashed command server
- **How**: Unplug and replug the Pico, then run `python main.py`

#### **2. Check Network Stability**
- **WiFi signal strength**: Ensure Pico has good WiFi signal
- **Network congestion**: Try during off-peak hours
- **Router issues**: Restart your WiFi router if needed

#### **3. Memory Issues**
- **Check free memory**: Look at the startup message showing available memory
- **If low memory**: Restart Pico to clear fragmentation
- **Monitor memory**: Web interface shows current memory usage

#### **4. Firewall/Antivirus**
- **Windows Firewall**: May block connections to port 8080
- **Antivirus**: Some antivirus software blocks local network connections
- **Test**: Temporarily disable firewall to test

### 🔄 **Improved Error Handling**

The updated system now includes:

#### **Local Web Server**:
- ✅ **Automatic retries** (3 attempts)
- ✅ **Better timeout handling**
- ✅ **Specific error messages** for different failure types
- ✅ **Connection status monitoring**

#### **Pico Command Server**:
- ✅ **Improved socket handling**
- ✅ **Better error logging** on Pico console
- ✅ **Graceful connection cleanup**
- ✅ **Memory management** after each request

### 📊 **Diagnostic Steps**

#### **Step 1: Basic Connection Test**
```bash
cd local_webserver
python test_connection.py 192.168.1.100
```

Expected output:
```
✓ TCP connection successful
✓ Command/response test successful  
✓ All tests passed! Connection is stable.
```

#### **Step 2: Check Pico Console**
Look for messages like:
```
Command client: 192.168.1.101
Command: {"type": "status"}
```

#### **Step 3: Web Interface Test**
1. Open http://localhost:5000
2. Check connection status (should show "✓ Connected")
3. Try pressing a key or moving cart

### 🚨 **If Problems Persist**

#### **Network-Level Issues**:
1. **Ping test**: `ping [PICO_IP]` from command prompt
2. **Port scan**: Use `telnet [PICO_IP] 8080` to test port
3. **Different network**: Try connecting both devices to phone hotspot

#### **Pico-Level Issues**:
1. **Different mode**: Try Mode 1 (original performance) to test hardware
2. **Fresh upload**: Re-upload all files to Pico
3. **Different Pico**: Test with another Pico if available

#### **Computer-Level Issues**:
1. **Different computer**: Test from another device
2. **Python version**: Ensure Python 3.7+ with proper Flask installation
3. **Virtual environment**: Try running in a clean Python environment

### 📈 **Performance Optimization**

#### **For Stable Connections**:
- **Reduce request frequency**: Don't spam commands too quickly
- **Monitor memory**: Keep an eye on Pico memory usage
- **Network quality**: Use 5GHz WiFi if available for less congestion

#### **Error Recovery**:
- **Auto-reconnect**: Web interface will retry failed connections
- **Status monitoring**: Connection status updates every 2 seconds
- **Graceful degradation**: System continues working even with occasional failures

### 🔧 **Advanced Debugging**

#### **Enable Debug Logging**:
Add to `local_web_server.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### **Monitor Network Traffic**:
Use Wireshark or similar to monitor packets between computer and Pico.

#### **Pico Memory Monitoring**:
Watch the memory values in the web interface - if they drop significantly, restart the Pico.

Most connection issues are resolved by restarting the Pico and ensuring both devices have stable network connections.


