# Monica Network Control System

## Overview

This system allows you to control Monica over the network using a local web server on your computer that communicates with a simple command server on the Pico. This approach provides full keyboard control while using minimal memory on the Pico.

## Architecture

```
Browser → Local Web Server (Computer) → Network → Pico Command Server
```

**Benefits:**
- ✅ Full keyboard control interface
- ✅ Minimal memory usage on Pico (~25-35KB)
- ✅ Rich web interface with modern features
- ✅ Network-based control (no USB required)
- ✅ Real-time status updates
- ✅ Automatic connection management

## Setup Instructions

### Step 1: Configure Pico (Command Server)

1. **Update WiFi credentials** in `network_credentials.py`:
   ```python
   WIFI_SSID = "YourNetworkName"
   WIFI_PASSWORD = "YourPassword"
   ```

2. **Run Monica on Pico**:
   ```bash
   python main.py
   # Select option 2: Network command server
   ```

3. **Note the IP address** displayed:
   ```
   Command server started at 192.168.1.100:8080
   Run local_web_server.py on your computer
   Set Pico IP to: 192.168.1.100
   ```

### Step 2: Setup Local Web Server (Computer)

1. **Navigate to local webserver directory**:
   ```bash
   cd local_webserver
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the local web server**:
   ```bash
   python local_web_server.py
   ```

3. **Configure Pico IP**:
   - Open http://localhost:5000/config
   - Enter the Pico's IP address
   - Click "Update IP Address"
   - Click "Test Connection"

### Step 3: Control Monica

1. **Open web interface**: http://localhost:5000
2. **Verify connection**: Should show "✓ Connected to Monica"
3. **Control Monica**:
   - Click keys or use keyboard
   - Use arrow keys for movement and volume
   - Space bar to home all systems

## Features

### **Keyboard Control**
- **Keys**: A-K (lower row), W-I (upper row)
- **Movement**: Arrow keys ← → (cart position)
- **Volume**: Arrow keys ↑ ↓ (air pump)
- **Home**: Space bar (return to home position)

### **Web Interface**
- **Real-time status**: Position, volume, memory usage
- **Connection monitoring**: Shows connection status
- **Visual feedback**: Keys highlight when pressed
- **Mobile friendly**: Works on tablets and phones

### **Performance Mode**
- **Start Performance**: Triggers original Monica song
- **Background execution**: Performance runs independently
- **Status updates**: Monitor performance progress

## Command Protocol

The system uses simple JSON commands over TCP:

### **Commands Sent to Pico:**
```json
{"type": "status"}
{"type": "play_performance"}
{"type": "press_key", "finger": 0, "position": 1}
{"type": "move_cart", "direction": -1}
{"type": "set_volume", "direction": 1}
{"type": "home_all"}
```

### **Responses from Pico:**
```json
{"success": true, "position": 5, "volume": "Normal", "memory": 45000}
{"success": true, "message": "Performance started"}
{"error": "Invalid command"}
```

## File Structure

### **On Pico:**
- `pico_command_server.py` - Command server for Pico
- `network_init.py` - Network connection management
- `main.py` - Updated with command server mode

### **On Computer:**
- `local_webserver/` folder:
  - `local_web_server.py` - Flask web server
  - `templates/index.html` - Main control interface
  - `templates/config.html` - Configuration page
  - `requirements.txt` - Python dependencies
  - `README.md` - Local webserver documentation

## Troubleshooting

### **Connection Issues**
1. **Check network**: Ensure both devices are on same WiFi
2. **Verify IP**: Use config page to test connection
3. **Firewall**: Check if port 8080 is blocked
4. **Memory**: Try restarting Pico if memory is low

### **Keyboard Not Working**
1. **Check connection status**: Should show "Connected"
2. **Test individual keys**: Try clicking keys with mouse
3. **Check console**: Look for error messages in browser dev tools
4. **Refresh page**: Sometimes helps with connection issues

### **Performance Issues**
1. **Memory**: Monitor memory usage on status bar
2. **Network latency**: Commands may have slight delay
3. **Multiple clients**: Only one browser should control at a time

## Network Requirements

- **Same WiFi network**: Both Pico and computer must be connected
- **Port 8080**: Must be accessible on Pico
- **Port 5000**: Local web server on computer
- **Stable connection**: WiFi should be reliable for real-time control

## Security Notes

- **Local network only**: System designed for local network use
- **No authentication**: Anyone on network can access if they know IPs
- **Firewall friendly**: Uses standard HTTP/TCP protocols

This system provides the best of both worlds: full-featured control interface with minimal Pico memory usage!
