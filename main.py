import device
import monica
import uasyncio
from network_init import network_manager
from web_server import web_server


async def main():
	"""Main application with network connectivity and web interface"""
	print("=== Monica Robotic Harmonica Starting ===")
	
	# Initialize network connection
	print("Connecting to WiFi...")
	if await network_manager.connect_wifi():
		print("Network connected successfully!")
		
		# Start web server
		print("Starting web server...")
		if await web_server.start():
			print("Web server started successfully!")
			print(f"Access Monica at: http://{network_manager.get_ip_address()}")
		else:
			print("Failed to start web server, continuing without web interface...")
	else:
		print("Failed to connect to WiFi, continuing without web interface...")
	
	# Keep the system running (web server runs in background tasks)
	print("Monica system ready. Press Ctrl+C to stop.")
	try:
		# Keep main loop alive - web server handles requests in background
		while True:
			await uasyncio.sleep(1)
	except KeyboardInterrupt:
		print("\nShutting down Monica...")
	finally:
		print("Cleaning up...")
		web_server.stop()
		device.reset_peripherals()


if __name__ == "__main__":
	try:
		uasyncio.run(main())
	except KeyboardInterrupt:
		print("\nForced shutdown")
	finally:
		device.reset_peripherals()

