import network
import uasyncio
import network_credentials

class NetworkManager:
    def __init__(self):
        self.wlan = None
        self.ip_address = None
        self.connected = False
    
    async def connect_wifi(self):
        """Connect to WiFi network using credentials from network_credentials.py"""
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        
        print(f"Connecting to WiFi: {network_credentials.WIFI_SSID}")
        self.wlan.connect(network_credentials.WIFI_SSID, network_credentials.WIFI_PASSWORD)
        
        # Wait for connection with timeout
        timeout = 10
        while not self.wlan.isconnected() and timeout > 0:
            print(".", end="")
            await uasyncio.sleep(1)
            timeout -= 1
        
        if self.wlan.isconnected():
            self.connected = True
            self.ip_address = self.wlan.ifconfig()[0]
            print(f"\nWiFi connected successfully!")
            print(f"IP Address: {self.ip_address}")
            print(f"Network config: {self.wlan.ifconfig()}")
            return True
        else:
            print(f"\nFailed to connect to WiFi: {network_credentials.WIFI_SSID}")
            return False
    
    def get_ip_address(self):
        """Get current IP address"""
        return self.ip_address
    
    def is_connected(self):
        """Check if WiFi is connected"""
        return self.connected and self.wlan and self.wlan.isconnected()

# Global network manager instance
network_manager = NetworkManager()
