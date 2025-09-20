"""
Emergency cleanup functions for Monica
Can be imported and called from anywhere for safe shutdown
"""

import gc

def emergency_network_cleanup():
    """Emergency WiFi disconnection and cleanup"""
    try:
        print("Emergency network cleanup...")
        
        # Try to import and disconnect network
        try:
            from network_init import network_manager
            if network_manager and network_manager.is_connected():
                network_manager.disconnect()
        except Exception as e:
            print(f"Error during network cleanup: {e}")
            
            # Fallback: direct network cleanup
            try:
                import network
                wlan = network.WLAN(network.STA_IF)
                if wlan.isconnected():
                    print("Fallback: Direct WiFi disconnect...")
                    wlan.disconnect()
                    wlan.active(False)
                    print("Direct WiFi cleanup complete")
            except Exception as e2:
                print(f"Fallback network cleanup failed: {e2}")
        
        # Force garbage collection
        gc.collect()
        print("Emergency network cleanup complete")
        
    except Exception as e:
        print(f"Critical error in emergency cleanup: {e}")

def emergency_hardware_cleanup():
    """Emergency hardware cleanup"""
    try:
        print("Emergency hardware cleanup...")
        
        # Try to reset peripherals
        try:
            import device
            device.reset_peripherals()
            print("Hardware peripherals reset")
        except Exception as e:
            print(f"Error resetting peripherals: {e}")
        
        # Force garbage collection
        gc.collect()
        print("Emergency hardware cleanup complete")
        
    except Exception as e:
        print(f"Critical error in hardware cleanup: {e}")

def emergency_full_cleanup():
    """Complete emergency cleanup - network and hardware"""
    print("=== EMERGENCY CLEANUP ===")
    emergency_network_cleanup()
    emergency_hardware_cleanup()
    print("=== EMERGENCY CLEANUP COMPLETE ===")

def safe_shutdown():
    """Safe shutdown sequence"""
    print("Initiating safe shutdown sequence...")
    
    # Stop command server if running
    try:
        from pico_command_server import command_server
        if command_server and command_server.running:
            command_server.stop()
    except:
        pass
    
    # Stop web server if running  
    try:
        from web_server import web_server
        if web_server and hasattr(web_server, 'running') and web_server.running:
            web_server.stop()
    except:
        pass
    
    # Full cleanup
    emergency_full_cleanup()
    
    print("Safe shutdown complete")

