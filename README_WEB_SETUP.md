# Monica Web Interface Setup

## Quick Start

1. **Configure WiFi credentials** in `network_credentials.py`:
   ```python
   WIFI_SSID = "YourNetworkName"
   WIFI_PASSWORD = "YourPassword"
   ```

2. **Run Monica with web interface**:
   ```bash
   python main.py
   ```

3. **Access the web interface**:
   - Look for the IP address in the startup messages
   - Open your browser to `http://[IP_ADDRESS]`
   - Click "Start Performance" to run Monica

## Files Added

- `network_credentials.py` - WiFi configuration (keep private!)
- `network_init.py` - Network connection management
- `web_server.py` - Simple web server with control interface
- `main.py` - Updated to include network and web server startup

## Features

- **Simple web interface** with start button
- **Automatic WiFi connection** on startup
- **Background performance execution** - web interface remains responsive
- **Graceful error handling** - continues without web interface if network fails
- **Clean shutdown** - properly closes network connections

## Usage

1. The system starts and connects to WiFi automatically
2. Web server starts on port 80
3. Access the web interface from any device on the same network
4. Click "Start Performance" to trigger `monica.run()`
5. The original Monica performance runs in the background
6. Web interface shows confirmation and redirects back to main page

## Network Requirements

- Raspberry Pi Pico W (with WiFi capability)
- Local WiFi network
- Devices on same network can access the web interface

## Troubleshooting

- If WiFi connection fails, Monica continues without web interface
- Check `network_credentials.py` for correct SSID and password
- Ensure Pico W is within WiFi range
- Check router settings if connection issues persist
