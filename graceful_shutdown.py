"""
Graceful shutdown handler for Monica
Handles various shutdown signals and ensures clean network disconnection
"""

import uasyncio
from emergency_cleanup import safe_shutdown

class GracefulShutdown:
    def __init__(self):
        self.shutdown_requested = False
        self.shutdown_callbacks = []
    
    def register_cleanup_callback(self, callback):
        """Register a callback to be called during shutdown"""
        self.shutdown_callbacks.append(callback)
    
    def request_shutdown(self):
        """Request graceful shutdown"""
        if not self.shutdown_requested:
            print("Graceful shutdown requested...")
            self.shutdown_requested = True
            
            # Call all registered cleanup callbacks
            for callback in self.shutdown_callbacks:
                try:
                    callback()
                except Exception as e:
                    print(f"Error in shutdown callback: {e}")
            
            # Perform safe shutdown
            try:
                safe_shutdown()
            except Exception as e:
                print(f"Error in safe shutdown: {e}")
    
    def is_shutdown_requested(self):
        """Check if shutdown has been requested"""
        return self.shutdown_requested

# Global shutdown handler
shutdown_handler = GracefulShutdown()

async def shutdown_monitor():
    """Monitor for shutdown conditions"""
    while not shutdown_handler.is_shutdown_requested():
        await uasyncio.sleep(1)
    
    print("Shutdown monitor detected shutdown request")

def setup_shutdown_monitoring():
    """Setup shutdown monitoring task"""
    uasyncio.create_task(shutdown_monitor())
    print("Shutdown monitoring active")

