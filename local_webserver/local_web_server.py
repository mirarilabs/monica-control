#!/usr/bin/env python3
"""
Local Web Server for Monica Control
Runs on your computer and communicates with Pico over network
"""

from flask import Flask, render_template, request, jsonify
import socket
import json
import threading
import time

app = Flask(__name__)

# Pico configuration
PICO_IP = "192.168.1.100"  # Replace with your Pico's IP
PICO_PORT = 8080

class PicoClient:
    def __init__(self, pico_ip, pico_port):
        self.pico_ip = pico_ip
        self.pico_port = pico_port
    
    def send_command(self, command, retries=2):
        """Send command to Pico and get response with optimized speed"""
        last_error = None
        
        for attempt in range(retries):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # Optimize socket for low latency
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                sock.settimeout(3)  # Reduced timeout for faster failure detection
                sock.connect((self.pico_ip, self.pico_port))
                
                # Send command
                command_str = json.dumps(command) + "\n"
                sock.send(command_str.encode())
                
                # Receive response with optimized timeout
                response_data = b""
                sock.settimeout(1)  # Much shorter timeout for reading
                
                while True:
                    try:
                        chunk = sock.recv(512)  # Smaller chunks for faster processing
                        if not chunk:
                            break
                        response_data += chunk
                        if b'\n' in response_data:
                            break
                    except socket.timeout:
                        break
                
                sock.close()
                
                if response_data:
                    try:
                        return json.loads(response_data.decode().strip())
                    except json.JSONDecodeError:
                        return {"error": f"Invalid JSON response: {response_data.decode()[:100]}"}
                else:
                    return {"error": "No response from Pico"}
                    
            except ConnectionRefusedError:
                last_error = "Connection refused - is the Pico command server running?"
            except socket.timeout:
                last_error = "Connection timeout - check network connection"
            except OSError as e:
                if e.winerror == 10054:
                    last_error = "Connection forcibly closed by Pico - server may have crashed"
                else:
                    last_error = f"Network error: {e}"
            except Exception as e:
                last_error = f"Unexpected error: {e}"
            
            # Minimal wait before retry (except on last attempt)
            if attempt < retries - 1:
                time.sleep(0.1)  # Much shorter retry delay
                print(f"Quick retry {attempt + 1}/{retries} after error: {last_error}")
        
        return {"error": f"Connection failed after {retries} attempts: {last_error}"}

pico_client = PicoClient(PICO_IP, PICO_PORT)

@app.route('/')
def index():
    """Main control interface"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Get Pico status"""
    response = pico_client.send_command({"type": "status"})
    return jsonify(response)

@app.route('/api/list_songs')
def list_songs():
    """Get list of available songs"""
    response = pico_client.send_command({"type": "list_songs"})
    return jsonify(response)

@app.route('/api/start_performance', methods=['POST'])
def start_performance():
    """Start Monica performance with selected song"""
    data = request.get_json() or {}
    song_name = data.get('song', 'showcase')
    
    response = pico_client.send_command({
        "type": "play_performance",
        "song": song_name
    })
    return jsonify(response)

@app.route('/api/key_down', methods=['POST'])
def key_down():
    """Key pressed down (sustain)"""
    data = request.get_json()
    finger = data.get('finger')
    position = data.get('position')
    
    response = pico_client.send_command({
        "type": "key_down",
        "finger": finger,
        "position": position
    })
    return jsonify(response)

@app.route('/api/key_up', methods=['POST'])
def key_up():
    """Key released"""
    data = request.get_json()
    finger = data.get('finger')
    
    response = pico_client.send_command({
        "type": "key_up",
        "finger": finger
    })
    return jsonify(response)

@app.route('/api/press_key', methods=['POST'])
def press_key():
    """Press a key (legacy - quick press/release)"""
    data = request.get_json()
    finger = data.get('finger')
    position = data.get('position')
    
    response = pico_client.send_command({
        "type": "press_key",
        "finger": finger,
        "position": position
    })
    return jsonify(response)

@app.route('/api/move_cart', methods=['POST'])
def move_cart():
    """Move cart"""
    data = request.get_json()
    direction = data.get('direction')
    
    response = pico_client.send_command({
        "type": "move_cart",
        "direction": direction
    })
    return jsonify(response)

@app.route('/api/set_volume', methods=['POST'])
def set_volume():
    """Set volume - supports both direction and direct percentage"""
    data = request.get_json()
    direction = data.get('direction')
    volume_percent = data.get('volume_percent')
    
    command = {"type": "set_volume"}
    
    if volume_percent is not None:
        # Direct percentage setting
        command["volume_percent"] = volume_percent
    elif direction is not None:
        # Direction-based adjustment
        command["direction"] = direction
    else:
        return jsonify({"error": "Must provide either 'direction' or 'volume_percent'"})
    
    response = pico_client.send_command(command)
    return jsonify(response)

@app.route('/api/volume_presets')
def volume_presets():
    """Get volume presets - rescaled for 40-90% servo range"""
    presets = {
        "silence": 0,    # Maps to servo 0% (true silence)
        "whisper": 10,   # Maps to servo 45% (very quiet)
        "quiet": 20,     # Maps to servo 50% (quiet)
        "soft": 30,      # Maps to servo 55% (soft)
        "normal": 50,    # Maps to servo 65% (balanced)
        "medium": 70,    # Maps to servo 75% (medium)
        "loud": 85,      # Maps to servo 82.5% (loud)
        "forte": 95,     # Maps to servo 87.5% (very loud)
        "maximum": 100   # Maps to servo 90% (practical maximum)
    }
    return jsonify({"success": True, "presets": presets})

@app.route('/api/home_all', methods=['POST'])
def home_all():
    """Home all systems"""
    response = pico_client.send_command({"type": "home_all"})
    return jsonify(response)

@app.route('/config')
def config():
    """Configuration page"""
    return render_template('config.html', pico_ip=PICO_IP, pico_port=PICO_PORT)

@app.route('/api/set_pico_address', methods=['POST'])
def set_pico_address():
    """Update Pico IP address"""
    global PICO_IP, pico_client
    data = request.get_json()
    new_ip = data.get('ip')
    
    if new_ip:
        PICO_IP = new_ip
        pico_client = PicoClient(PICO_IP, PICO_PORT)
        return jsonify({"success": True, "message": f"Pico IP updated to {new_ip}"})
    else:
        return jsonify({"error": "No IP provided"})

if __name__ == '__main__':
    print("Monica Local Web Server")
    print("=" * 30)
    print(f"Pico IP: {PICO_IP}:{PICO_PORT}")
    print("Web Interface: http://localhost:5000")
    print("Config: http://localhost:5000/config")
    print("\nStarting server...")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
