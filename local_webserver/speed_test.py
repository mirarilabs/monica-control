#!/usr/bin/env python3
"""
Speed test tool for Monica Pico
Measures latency and throughput
"""

import socket
import json
import time
import statistics
import sys

def measure_command_latency(ip, port=8080, count=10):
    """Measure latency for key press commands"""
    print(f"Measuring key press latency to {ip}:{port}")
    print(f"Testing {count} commands...")
    
    latencies = []
    
    for i in range(count):
        try:
            start_time = time.time()
            
            # Create optimized socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sock.settimeout(3)
            sock.connect((ip, port))
            
            # Send key press command
            command = {"type": "press_key", "finger": 0, "position": 0}
            command_str = json.dumps(command) + "\n"
            sock.send(command_str.encode())
            
            # Receive response
            response_data = b""
            while True:
                chunk = sock.recv(512)
                if not chunk:
                    break
                response_data += chunk
                if b'\n' in response_data:
                    break
            
            end_time = time.time()
            sock.close()
            
            if response_data:
                latency = (end_time - start_time) * 1000  # Convert to ms
                latencies.append(latency)
                print(f"Command {i+1:2d}: {latency:.1f} ms")
            else:
                print(f"Command {i+1:2d}: No response")
                
        except Exception as e:
            print(f"Command {i+1:2d}: Error - {e}")
        
        # Brief pause between commands
        time.sleep(0.1)
    
    if latencies:
        print(f"\nLatency Statistics:")
        print(f"  Count: {len(latencies)}")
        print(f"  Average: {statistics.mean(latencies):.1f} ms")
        print(f"  Median: {statistics.median(latencies):.1f} ms")
        print(f"  Min: {min(latencies):.1f} ms")
        print(f"  Max: {max(latencies):.1f} ms")
        print(f"  Std Dev: {statistics.stdev(latencies) if len(latencies) > 1 else 0:.1f} ms")
        
        # Performance assessment
        avg_latency = statistics.mean(latencies)
        if avg_latency < 50:
            print(f"  🟢 Excellent response time!")
        elif avg_latency < 100:
            print(f"  🟡 Good response time")
        elif avg_latency < 200:
            print(f"  🟠 Acceptable response time")
        else:
            print(f"  🔴 High latency - optimization needed")
    
    return latencies

def measure_throughput(ip, port=8080, duration=5):
    """Measure command throughput"""
    print(f"\nMeasuring throughput for {duration} seconds...")
    
    start_time = time.time()
    command_count = 0
    errors = 0
    
    while time.time() - start_time < duration:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sock.settimeout(1)
            sock.connect((ip, port))
            
            command = {"type": "status"}
            command_str = json.dumps(command) + "\n"
            sock.send(command_str.encode())
            
            # Quick read
            response_data = sock.recv(512)
            sock.close()
            
            if response_data:
                command_count += 1
            else:
                errors += 1
                
        except:
            errors += 1
        
        # Small delay to prevent overwhelming
        time.sleep(0.01)
    
    elapsed = time.time() - start_time
    throughput = command_count / elapsed
    
    print(f"Throughput Results:")
    print(f"  Duration: {elapsed:.1f} seconds")
    print(f"  Successful commands: {command_count}")
    print(f"  Errors: {errors}")
    print(f"  Throughput: {throughput:.1f} commands/second")
    
    return throughput

def test_network_ping(ip):
    """Test basic network connectivity"""
    import subprocess
    import platform
    
    print(f"\nTesting network ping to {ip}...")
    
    try:
        # Use appropriate ping command for OS
        if platform.system().lower() == "windows":
            result = subprocess.run(["ping", "-n", "4", ip], 
                                  capture_output=True, text=True, timeout=10)
        else:
            result = subprocess.run(["ping", "-c", "4", ip], 
                                  capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✓ Network ping successful")
            # Extract average ping time if possible
            output = result.stdout
            if "Average" in output:
                print(f"Network latency info: {output.split('Average')[1].split('=')[1].strip()}")
        else:
            print("✗ Network ping failed")
            print(result.stderr)
            
    except Exception as e:
        print(f"✗ Ping test error: {e}")

def main():
    if len(sys.argv) > 1:
        pico_ip = sys.argv[1]
    else:
        pico_ip = input("Enter Pico IP address: ").strip()
    
    if not pico_ip:
        print("No IP address provided")
        return
    
    print(f"Monica Speed Test")
    print(f"Target: {pico_ip}:8080")
    print("=" * 50)
    
    # Test network connectivity first
    test_network_ping(pico_ip)
    
    # Test command latency
    latencies = measure_command_latency(pico_ip)
    
    # Test throughput
    if latencies:
        measure_throughput(pico_ip)
    
    print("\nSpeed test complete!")
    
    # Recommendations
    if latencies:
        avg_latency = statistics.mean(latencies)
        print(f"\nRecommendations:")
        if avg_latency > 100:
            print("- Check WiFi signal strength")
            print("- Restart Pico to clear memory")
            print("- Try 5GHz WiFi network")
            print("- Check for network congestion")

if __name__ == "__main__":
    main()


