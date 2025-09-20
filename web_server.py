import socket
import uasyncio
import monica
from network_init import network_manager

class SimpleWebServer:
    def __init__(self, port=80):
        self.port = port
        self.server_socket = None
        self.running = False
    
    async def start(self):
        """Start the web server"""
        if not network_manager.is_connected():
            print("Error: Not connected to network. Cannot start web server.")
            return False
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(5)
            self.server_socket.setblocking(False)
            
            self.running = True
            ip = network_manager.get_ip_address()
            print(f"Web server started at http://{ip}:{self.port}")
            
            # Start accepting connections
            uasyncio.create_task(self._accept_connections())
            return True
            
        except Exception as e:
            print(f"Failed to start web server: {e}")
            return False
    
    async def _accept_connections(self):
        """Accept and handle incoming connections"""
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                client_socket.setblocking(False)
                print(f"Client connected from {addr[0]}:{addr[1]}")
                uasyncio.create_task(self._handle_client(client_socket))
            except OSError:
                # No connection available, sleep briefly
                await uasyncio.sleep(0.1)
    
    async def _handle_client(self, client_socket):
        """Handle individual client requests"""
        try:
            # Read the HTTP request
            request_data = b""
            while True:
                try:
                    chunk = client_socket.recv(1024)
                    if not chunk:
                        break
                    request_data += chunk
                    if b"\r\n\r\n" in request_data:
                        break
                except OSError:
                    await uasyncio.sleep(0.01)
                    continue
            
            request = request_data.decode('utf-8')
            print(f"Request: {request.split()[0:2] if request.split() else 'Invalid'}")
            
            # Route the request
            if request.startswith('GET /'):
                path = request.split()[1]
                if path == '/':
                    await self._serve_home_page(client_socket)
                elif path == '/start':
                    await self._handle_start_command(client_socket)
                else:
                    await self._send_404(client_socket)
            else:
                await self._send_404(client_socket)
                
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()
    
    async def _serve_home_page(self, client_socket):
        """Serve the main control page"""
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Monica Robotic Harmonica</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            text-align: center; 
            margin: 50px;
            background-color: #f0f0f0;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h1 { 
            color: #333; 
            margin-bottom: 30px;
        }
        .start-button {
            background-color: #4CAF50;
            color: white;
            padding: 15px 30px;
            font-size: 18px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin: 20px;
            text-decoration: none;
            display: inline-block;
            transition: background-color 0.3s;
        }
        .start-button:hover {
            background-color: #45a049;
        }
        .info {
            background-color: #e7f3ff;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            border-left: 4px solid #2196F3;
        }
        .status {
            color: #666;
            font-size: 14px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 Monica Robotic Harmonica</h1>
        
        <div class="info">
            <strong>Welcome to Monica!</strong><br>
            Click the button below to start playing the harmonica performance.
        </div>
        
        <a href="/start" class="start-button">▶️ Start Performance</a>
        
        <div class="status">
            Status: Ready to play<br>
            IP: """ + str(network_manager.get_ip_address()) + """
        </div>
    </div>
    
    <script>
        // Simple feedback for button clicks
        document.addEventListener('DOMContentLoaded', function() {
            const startButton = document.querySelector('.start-button');
            startButton.addEventListener('click', function(e) {
                e.target.innerHTML = '🎵 Starting...';
                e.target.style.backgroundColor = '#ff9800';
            });
        });
    </script>
</body>
</html>"""
        
        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n{html}"
        client_socket.send(response.encode())
    
    async def _handle_start_command(self, client_socket):
        """Handle the start command - trigger Monica performance"""
        try:
            print("Web command received: Starting Monica performance")
            
            # Send immediate response
            response = """HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n
<!DOCTYPE html>
<html>
<head>
    <title>Monica - Performance Started</title>
    <meta http-equiv="refresh" content="3;url=/">
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin: 50px; background-color: #f0f0f0; }
        .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        .success { color: #4CAF50; font-size: 24px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="success">🎵 Performance Started!</div>
        <p>Monica is now playing. You will be redirected back to the main page in 3 seconds.</p>
        <p><a href="/">← Back to Control Panel</a></p>
    </div>
</body>
</html>"""
            client_socket.send(response.encode())
            
            # Start Monica performance in background
            uasyncio.create_task(self._run_monica_performance())
            
        except Exception as e:
            print(f"Error starting performance: {e}")
            await self._send_error(client_socket, f"Error starting performance: {e}")
    
    async def _run_monica_performance(self):
        """Run the Monica performance (the original program logic)"""
        try:
            print("Starting Monica performance via web interface...")
            await monica.run()
            print("Monica performance completed.")
        except Exception as e:
            print(f"Error during Monica performance: {e}")
    
    async def _send_404(self, client_socket):
        """Send 404 Not Found response"""
        response = """HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n
<!DOCTYPE html>
<html>
<head><title>404 - Not Found</title></head>
<body>
    <h1>404 - Page Not Found</h1>
    <p><a href="/">← Back to Monica Control Panel</a></p>
</body>
</html>"""
        client_socket.send(response.encode())
    
    async def _send_error(self, client_socket, error_message):
        """Send error response"""
        response = f"""HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n
<!DOCTYPE html>
<html>
<head><title>Error</title></head>
<body>
    <h1>Error</h1>
    <p>{error_message}</p>
    <p><a href="/">← Back to Monica Control Panel</a></p>
</body>
</html>"""
        client_socket.send(response.encode())
    
    def stop(self):
        """Stop the web server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()

# Global web server instance
web_server = SimpleWebServer()
