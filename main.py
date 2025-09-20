import device
import monica
import uasyncio
import gc
from emergency_cleanup import safe_shutdown, emergency_network_cleanup

# Lazy imports to save memory
network_manager = None
web_server = None
command_server = None


async def main():
	"""Main application with network connectivity options"""
	global network_manager, web_server, command_server
	
	print("=== Monica Robotic Harmonica Starting ===")
	print("Free memory:", gc.mem_free())
	
	# Run network command server mode by default
	print("Starting network command server...")
	mode = "2"
	
	if mode == "2":
		print("Loading command server...")
		gc.collect()
		
		try:
			from network_init import network_manager as nm
			from pico_command_server import command_server as cs
			network_manager = nm
			command_server = cs
			
			print("Free memory after imports:", gc.mem_free())
			
			# Connect to WiFi
			if await network_manager.connect_wifi():
				print("Network connected successfully!")
				
				# Start command server
				if await command_server.start():
					print("Command server ready!")
					print(f"Run local_web_server.py on your computer")
					print(f"Set Pico IP to: {network_manager.get_ip_address()}")
					
					# Keep running
					try:
						while True:
							await uasyncio.sleep(1)
					except KeyboardInterrupt:
						print("\nShutting down...")
					finally:
						print("Cleaning up network and hardware...")
						command_server.stop()
						if network_manager and network_manager.is_connected():
							print("Disconnecting WiFi...")
							network_manager.disconnect()
						device.reset_peripherals()
				else:
					print("Failed to start command server. Falling back to original mode.")
					mode = "1"
			else:
				print("WiFi connection failed. Falling back to original mode.")
				mode = "1"
		
		except MemoryError:
			print("Not enough memory for command server. Falling back to original mode.")
			mode = "1"
		except Exception as e:
			print(f"Error: {e}. Falling back to original mode.")
			mode = "1"
	
	elif mode == "3":
		print("Loading full web interface...")
		gc.collect()
		
		try:
			from network_init import network_manager as nm
			from web_server import web_server as ws
			network_manager = nm
			web_server = ws
			
			print("Free memory after imports:", gc.mem_free())
			
			# Connect to WiFi
			if await network_manager.connect_wifi():
				print("Network connected successfully!")
				
				# Start web server
				if await web_server.start():
					print("Web server started successfully!")
					print(f"Access Monica at: http://{network_manager.get_ip_address()}")
				else:
					print("Failed to start web server, continuing without web interface...")
			else:
				print("Failed to connect to WiFi, continuing without web interface...")
			
			# Keep running
			try:
				while True:
					await uasyncio.sleep(1)
			except KeyboardInterrupt:
				print("\nShutting down...")
			finally:
				print("Cleaning up network and hardware...")
				if web_server:
					web_server.stop()
				if network_manager and network_manager.is_connected():
					print("Disconnecting WiFi...")
					network_manager.disconnect()
				device.reset_peripherals()
		
		except MemoryError:
			print("Not enough memory for full web interface. Try mode 2 (command server).")
			mode = "1"
		except Exception as e:
			print(f"Error starting web interface: {e}. Falling back to original mode.")
			mode = "1"
	
	if mode == "1":
		print("Starting original Monica performance mode...")
		gc.collect()
		print("Free memory:", gc.mem_free())
		
		# Run original Monica performance
		try:
			await monica.run()
		except KeyboardInterrupt:
			print("\nStopping Monica...")
		finally:
			device.reset_peripherals()


if __name__ == "__main__":
	try:
		uasyncio.run(main())
	except KeyboardInterrupt:
		print("\nForced shutdown detected!")
		try:
			# Use emergency cleanup for forced shutdown
			emergency_network_cleanup()
		except:
			pass  # Don't let cleanup errors prevent shutdown
	finally:
		try:
			device.reset_peripherals()
		except:
			pass  # Don't let cleanup errors prevent shutdown

