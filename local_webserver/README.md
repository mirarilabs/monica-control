# Monica Local Web Server

This directory contains the local web server that runs on your computer to control Monica over the network.

## Files

- `local_web_server.py` - Flask web server for controlling Monica
- `requirements.txt` - Python dependencies 
- `templates/` - HTML templates for web interface
  - `index.html` - Main control interface
  - `config.html` - Configuration page

## Setup

1. **Install dependencies:**
   ```bash
   cd local_webserver
   pip install -r requirements.txt
   ```

2. **Run the web server:**
   ```bash
   python local_web_server.py
   ```

3. **Configure Pico IP:**
   - Open http://localhost:5000/config
   - Enter your Pico's IP address
   - Test connection

4. **Control Monica:**
   - Open http://localhost:5000
   - Use keyboard or click virtual keys

## Features

- **Real-time keyboard control** (A-K, W-I keys)
- **Cart movement** (arrow keys ← →)
- **Volume control** (arrow keys ↑ ↓)
- **Home all systems** (space bar)
- **Performance mode** (start original Monica songs)
- **Connection monitoring** and status display

## Network Requirements

- Pico must be running in **Mode 2** (Network command server)
- Both computer and Pico on same WiFi network
- Pico must be accessible on port 8080

## Configuration

Edit `local_web_server.py` to change:
- Default Pico IP address
- Web server port (default: 5000)
- Connection timeout settings


