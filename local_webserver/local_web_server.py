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
import os
from werkzeug.utils import secure_filename
from monica_pathing import song_planner
from midi_processor import midi_processor
from local_duty_calculator import local_duty_calculator

app = Flask(__name__)

# MIDI upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mid', 'midi'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Pico configuration
PICO_IP = "192.168.1.120"  # Fixed Pico IP address
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

# MIDI processing state
processed_midi_data = {}  # Store processed MIDI data in memory

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    local_pathing = data.get('local_pathing', False)
    
    if local_pathing:
        # Process pathing locally
        try:
            print(f"Processing song pathing locally for: {song_name}")
            duties_dict, path = song_planner.plan_song_by_name(song_name)
            
            # Send pre-processed pathing to Pico
            response = pico_client.send_command({
                "type": "play_performance_with_pathing",
                "song": song_name,
                "duties": duties_dict,
                "path": path
            })
            return jsonify(response)
        except Exception as e:
            print(f"Local pathing failed: {e}")
            # Fall back to Pico pathing
            response = pico_client.send_command({
                "type": "play_performance",
                "song": song_name
            })
            return jsonify(response)
    else:
        # Use Pico pathing (original method)
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
    key = data.get('key')  # Optional: key letter for local calculation
    
    # Check if local duty calculation is enabled
    use_local = data.get('local_duty', False)
    
    if use_local and key:
        # Use local duty calculation
        try:
            response = local_duty_calculator.key_down(key)
            response['method'] = 'local'
            
            # Also send the actual command to Pico for physical movement
            pico_response = pico_client.send_command({
                "type": "key_down",
                "finger": finger,
                "position": position
            })
            response['pico_response'] = pico_response
            
            return jsonify(response)
        except Exception as e:
            print(f"Local duty calculation failed: {e}")
            # Fall back to network control
    
    # Network control (original method)
    response = pico_client.send_command({
        "type": "key_down",
        "finger": finger,
        "position": position
    })
    response['method'] = 'network'
    return jsonify(response)

@app.route('/api/key_up', methods=['POST'])
def key_up():
    """Key released"""
    data = request.get_json()
    finger = data.get('finger')
    key = data.get('key')  # Optional: key letter for local calculation
    
    # Check if local duty calculation is enabled
    use_local = data.get('local_duty', False)
    
    if use_local and key:
        # Use local duty calculation
        try:
            response = local_duty_calculator.key_up(key)
            response['method'] = 'local'
            
            # Also send the actual command to Pico for physical movement
            pico_response = pico_client.send_command({
                "type": "key_up",
                "finger": finger
            })
            response['pico_response'] = pico_response
            
            return jsonify(response)
        except Exception as e:
            print(f"Local duty calculation failed: {e}")
            # Fall back to network control
    
    # Network control (original method)
    response = pico_client.send_command({
        "type": "key_up",
        "finger": finger
    })
    response['method'] = 'network'
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
    """Get volume presets - raw user percentages (mapped to 20-60% servo on Pico)"""
    presets = {
        "silence": 0,    # Raw user percentage (mapped on Pico)
        "whisper": 10,   # Raw user percentage (mapped on Pico)
        "quiet": 20,     # Raw user percentage (mapped on Pico)
        "soft": 30,      # Raw user percentage (mapped on Pico)
        "normal": 50,    # Raw user percentage (mapped on Pico)
        "medium": 70,    # Raw user percentage (mapped on Pico)
        "loud": 85,      # Raw user percentage (mapped on Pico)
        "forte": 95,     # Raw user percentage (mapped on Pico)
        "maximum": 100   # Raw user percentage (mapped on Pico)
    }
    return jsonify({"success": True, "presets": presets})

@app.route('/api/home_all', methods=['POST'])
def home_all():
    """Home all systems"""
    data = request.get_json() or {}
    use_local = data.get('local_duty', False)
    
    if use_local:
        # Reset local duty calculator
        try:
            response = local_duty_calculator.home_all()
            response['method'] = 'local'
            return jsonify(response)
        except Exception as e:
            print(f"Local duty calculation failed: {e}")
            # Fall back to network control
    
    # Network control (original method)
    response = pico_client.send_command({"type": "home_all"})
    response['method'] = 'network'
    return jsonify(response)

@app.route('/api/local_duty_status', methods=['GET'])
def local_duty_status():
    """Get status of local duty calculator"""
    try:
        status = local_duty_calculator.get_status()
        return jsonify({"success": True, "status": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/set_cart_position', methods=['POST'])
def set_cart_position():
    """Set cart position (for local duty calculation)"""
    data = request.get_json()
    position = data.get('position')
    
    if position is None:
        return jsonify({"error": "Missing position"})
    
    try:
        response = local_duty_calculator.set_cart_position(position)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/config')
def config():
    """Configuration page"""
    return render_template('config.html', pico_ip=PICO_IP, pico_port=PICO_PORT)

@app.route('/api/upload_midi', methods=['POST'])
def upload_midi():
    """Upload and process MIDI file"""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Secure the filename
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save uploaded file
            file.save(filepath)
            
            # Get MIDI file information
            info = midi_processor.get_midi_info(filepath)
            
            return jsonify({
                "success": True,
                "message": f"MIDI file '{filename}' uploaded successfully",
                "filename": filename,
                "info": info
            })
            
        except Exception as e:
            # Clean up file on error
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"error": f"Error processing MIDI file: {str(e)}"}), 500
    
    return jsonify({"error": "Invalid file type. Please upload .mid or .midi files"}), 400

@app.route('/api/process_midi', methods=['POST'])
def process_midi():
    """Process uploaded MIDI file to duties and path"""
    data = request.get_json()
    filename = data.get('filename')
    
    if not filename:
        return jsonify({"error": "No filename provided"}), 400
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
    
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
    
    try:
        # Process MIDI file
        duties_dict, path, metadata = midi_processor.process_midi_file(filepath)
        
        # Store processed data in memory
        processed_midi_data[filename] = {
            'duties': duties_dict,
            'path': path,
            'metadata': metadata
        }
        
        return jsonify({
            "success": True,
            "message": f"MIDI file processed successfully",
            "metadata": metadata,
            "duty_count": len(duties_dict),
            "path_length": len(path)
        })
        
    except Exception as e:
        return jsonify({"error": f"Error processing MIDI file: {str(e)}"}), 500

@app.route('/api/play_midi', methods=['POST'])
def play_midi():
    """Play processed MIDI file as Monica performance"""
    data = request.get_json()
    filename = data.get('filename')
    
    if not filename:
        return jsonify({"error": "No filename provided"}), 400
    
    if filename not in processed_midi_data:
        return jsonify({"error": "MIDI file not processed. Please process it first."}), 400
    
    try:
        midi_data = processed_midi_data[filename]
        
        # Send MIDI performance to Pico using existing command type
        response = pico_client.send_command({
            "type": "play_performance_with_pathing",
            "song": f"midi_{filename}",  # Use filename as song identifier
            "duties": midi_data['duties'],
            "path": midi_data['path']
        })
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": f"Error playing MIDI file: {str(e)}"}), 500

@app.route('/api/list_midi_files')
def list_midi_files():
    """List uploaded MIDI files"""
    try:
        files = []
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if allowed_file(filename):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file_size = os.path.getsize(filepath)
                is_processed = filename in processed_midi_data
                
                files.append({
                    'filename': filename,
                    'size': file_size,
                    'processed': is_processed,
                    'metadata': processed_midi_data[filename]['metadata'] if is_processed else None
                })
        
        return jsonify({"success": True, "files": files})
        
    except Exception as e:
        return jsonify({"error": f"Error listing files: {str(e)}"}), 500

@app.route('/api/delete_midi', methods=['POST'])
def delete_midi():
    """Delete uploaded MIDI file"""
    data = request.get_json()
    filename = data.get('filename')
    
    if not filename:
        return jsonify({"error": "No filename provided"}), 400
    
    try:
        # Remove from memory
        if filename in processed_midi_data:
            del processed_midi_data[filename]
        
        # Remove file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify({"success": True, "message": f"File '{filename}' deleted successfully"})
        
    except Exception as e:
        return jsonify({"error": f"Error deleting file: {str(e)}"}), 500

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
