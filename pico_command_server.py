import socket
import uasyncio
import json
import device
import monica
import gc
from network_init import network_manager

class PicoCommandServer:
    def __init__(self, port=8080):
        self.port = port
        self.server_socket = None
        self.running = False
        self.current_position = 0
        self.volume_levels = ["Silence", "Low", "Normal", "High"]
        self.current_volume_index = 2
        
        # Track finger states (True = at home/neutral, False = at position)
        self.finger_states = [True] * 7  # 7 fingers, all start at home
        
    async def start(self):
        """Start the command server"""
        if not network_manager.is_connected():
            print("Error: Not connected to network")
            return False
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(2)
            self.server_socket.setblocking(False)
            
            self.running = True
            ip = network_manager.get_ip_address()
            print(f"Command server started at {ip}:{self.port}")
            
            # Initialize hardware
            await self._init_hardware()
            
            # Start accepting connections
            uasyncio.create_task(self._accept_connections())
            return True
            
        except Exception as e:
            print(f"Failed to start command server: {e}")
            return False
    
    async def _init_hardware(self):
        """Initialize hardware for manual control"""
        print("Initializing hardware...")
        device.pump.go_home()
        await device.pump.wait("ReachedHome")
        device.pump.go_to("Normal")
        device.fingers_rig.go_home()
        await device.fingers_rig.cautionary_wait()
        device.servo_rig.go_home()
        await device.stepper.wait("Homed")
        print("Hardware ready for commands")
    
    async def _accept_connections(self):
        """Accept command connections"""
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                client_socket.setblocking(False)
                print(f"Command client: {addr[0]}")
                uasyncio.create_task(self._handle_command_client(client_socket))
            except OSError:
                await uasyncio.sleep(0.1)
    
    async def _handle_command_client(self, client_socket):
        """Handle command requests optimized for speed"""
        try:
            # Optimize socket for low latency
            client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            client_socket.settimeout(2)  # Shorter timeout for faster response
            
            # Read command with optimized timeout handling
            data = b""
            timeout_count = 0
            max_timeouts = 20  # 0.2 seconds total - much faster
            
            while timeout_count < max_timeouts:
                try:
                    chunk = client_socket.recv(512)
                    if chunk:
                        data += chunk
                        timeout_count = 0  # Reset on successful read
                        if b'\n' in data:
                            break
                    else:
                        # Connection closed by client
                        print("Client closed connection")
                        return
                except OSError as e:
                    timeout_count += 1
                    await uasyncio.sleep(0.01)
            
            if not data:
                print("No command data received")
                return
            
            try:
                command_str = data.decode().strip()
                print(f"Command: {command_str}")
            except UnicodeDecodeError:
                print("Invalid UTF-8 data received")
                await self._send_response(client_socket, {"error": "Invalid UTF-8 data"})
                return
            
            # Parse JSON command
            try:
                command = json.loads(command_str)
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                await self._send_response(client_socket, {"error": f"Invalid JSON: {str(e)}"})
                return
            
            # Execute command
            try:
                response = await self._execute_command(command)
                await self._send_response(client_socket, response)
            except Exception as e:
                print(f"Command execution error: {e}")
                await self._send_response(client_socket, {"error": f"Execution error: {str(e)}"})
            
        except Exception as e:
            print(f"Client handler error: {e}")
            try:
                await self._send_response(client_socket, {"error": f"Server error: {str(e)}"})
            except:
                pass  # If we can't send error response, just log it
        finally:
            try:
                client_socket.close()
            except:
                pass  # Ignore close errors
            gc.collect()
    
    async def _execute_command(self, command):
        """Execute a command and return response"""
        cmd_type = command.get("type")
        
        if cmd_type == "status":
            return {
                "success": True,
                "position": self.current_position,
                "volume": self.volume_levels[self.current_volume_index],
                "memory": gc.mem_free(),
                "fingers": {
                    "states": self.finger_states,
                    "all_home": all(self.finger_states),
                    "active_count": sum(1 for state in self.finger_states if not state)
                }
            }
        
        elif cmd_type == "play_performance":
            print("Starting Monica performance...")
            uasyncio.create_task(monica.run())
            return {"success": True, "message": "Performance started"}
        
        elif cmd_type == "key_down":
            finger = command.get("finger")
            position = command.get("position")  # 0=Left, 1=Right
            if finger is not None and position is not None:
                # Safety check: ensure target finger is at home first
                if not self.finger_states[finger]:
                    print(f"Safety: Finger {finger} not at home, moving to neutral first")
                    device.fingers[finger].go_home()
                    await uasyncio.sleep_ms(50)  # Brief wait for safety
                
                target = "Left" if position == 0 else "Right"
                # Move finger to position and hold
                device.fingers[finger].go_to(target)
                self.finger_states[finger] = False  # Mark as not at home
                return {"success": True, "message": f"Finger {finger} -> {target} (held)"}
            return {"error": "Missing finger or position"}
        
        elif cmd_type == "key_up":
            finger = command.get("finger")
            if finger is not None:
                # Return finger to home position
                device.fingers[finger].go_home()
                self.finger_states[finger] = True  # Mark as home
                return {"success": True, "message": f"Finger {finger} -> Home"}
            return {"error": "Missing finger"}
        
        elif cmd_type == "press_key":
            # Legacy support for quick press/release
            finger = command.get("finger")
            position = command.get("position")  # 0=Left, 1=Right
            if finger is not None and position is not None:
                # Safety check: ensure target finger is at home first
                if not self.finger_states[finger]:
                    print(f"Safety: Finger {finger} not at home, moving to neutral first")
                    device.fingers[finger].go_home()
                    await uasyncio.sleep_ms(50)  # Brief wait for safety
                
                target = "Left" if position == 0 else "Right"
                device.fingers[finger].go_to(target)
                self.finger_states[finger] = False  # Mark as not at home
                # Auto-return to home after brief delay
                uasyncio.create_task(self._return_finger_home(finger))
                return {"success": True, "message": f"Finger {finger} -> {target} (quick press)"}
            return {"error": "Missing finger or position"}
        
        elif cmd_type == "move_cart":
            direction = command.get("direction")  # -1=left, 1=right
            if direction is not None:
                # Safety check: ensure all fingers are at home before moving cart
                fingers_moved = await self._ensure_all_fingers_home()
                
                new_pos = max(0, min(monica.wagon.valid_positions - 1, 
                                   self.current_position + direction))
                if new_pos != self.current_position:
                    print(f"Moving cart from position {self.current_position} to {new_pos}")
                    steps = monica.wagon.calculate_steps(new_pos)
                    device.stepper.set_target(steps)
                    await device.stepper.wait("ReachedTarget")
                    self.current_position = new_pos
                
                message = f"Cart at position {self.current_position}"
                if fingers_moved > 0:
                    message += f" (moved {fingers_moved} fingers to neutral first)"
                
                return {"success": True, "position": self.current_position, "message": message}
            return {"error": "Missing direction"}
        
        elif cmd_type == "set_volume":
            direction = command.get("direction")  # -1=down, 1=up
            if direction is not None:
                new_idx = max(0, min(len(self.volume_levels) - 1,
                                   self.current_volume_index + direction))
                if new_idx != self.current_volume_index:
                    self.current_volume_index = new_idx
                    volume = self.volume_levels[self.current_volume_index]
                    device.pump.go_to(volume)
                    await device.pump.wait("ReachedTarget")
                return {"success": True, "volume": self.volume_levels[self.current_volume_index]}
            return {"error": "Missing direction"}
        
        elif cmd_type == "home_all":
            print("Homing all systems with safety checks...")
            await self._init_hardware()
            self.current_position = 0
            self.current_volume_index = 0
            # Reset all finger states to home
            self.finger_states = [True] * 7
            return {"success": True, "message": "All systems homed safely"}
        
        else:
            return {"error": f"Unknown command type: {cmd_type}"}
    
    async def _return_finger_home(self, finger):
        """Return finger to home position after brief delay"""
        await uasyncio.sleep_ms(50)  # Shorter delay for faster response
        device.fingers[finger].go_home()
        self.finger_states[finger] = True  # Mark as home
    
    async def _ensure_all_fingers_home(self):
        """Ensure all fingers are at neutral/home position before movement"""
        fingers_to_home = []
        
        # Check which fingers need to go home
        for i, is_home in enumerate(self.finger_states):
            if not is_home:
                fingers_to_home.append(i)
        
        if fingers_to_home:
            print(f"Safety: Moving fingers {fingers_to_home} to home position first")
            
            # Move all non-home fingers to home
            for finger in fingers_to_home:
                device.fingers[finger].go_home()
                self.finger_states[finger] = True
            
            # Wait for fingers to reach home position
            await uasyncio.sleep_ms(100)  # Brief wait for safety
            print("All fingers now at neutral position")
        
        return len(fingers_to_home)
    
    async def _send_response(self, client_socket, response):
        """Send JSON response with error handling"""
        try:
            response_str = json.dumps(response) + "\n"
            response_bytes = response_str.encode()
            
            # Send in chunks if needed
            total_sent = 0
            while total_sent < len(response_bytes):
                try:
                    sent = client_socket.send(response_bytes[total_sent:])
                    if sent == 0:
                        print("Socket connection broken during send")
                        break
                    total_sent += sent
                except OSError as e:
                    print(f"Send error: {e}")
                    break
                    
        except Exception as e:
            print(f"Response send error: {e}")
    
    def stop(self):
        """Stop the command server with proper cleanup"""
        print("Stopping command server...")
        self.running = False
        
        if self.server_socket:
            try:
                self.server_socket.close()
                print("Command server socket closed")
            except Exception as e:
                print(f"Error closing server socket: {e}")
        
        # Force garbage collection to free memory
        gc.collect()
        print("Command server stopped")

# Global instance
command_server = PicoCommandServer()
