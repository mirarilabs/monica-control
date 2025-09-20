#!/usr/bin/env python3
"""
Connection diagnostic tool for Monica Pico
Run this to test and diagnose connection issues
"""

import socket
import json
import time
import sys

def test_basic_connection(ip, port=8080):
    """Test basic TCP connection"""
    print(f"Testing basic TCP connection to {ip}:{port}")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((ip, port))
        sock.close()
        
        if result == 0:
            print("✓ TCP connection successful")
            return True
        else:
            print(f"✗ TCP connection failed: Error {result}")
            return False
    except Exception as e:
        print(f"✗ TCP connection error: {e}")
        return False

def test_command_response(ip, port=8080):
    """Test sending a command and getting response"""
    print(f"Testing command/response to {ip}:{port}")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((ip, port))
        
        # Send status command
        command = {"type": "status"}
        command_str = json.dumps(command) + "\n"
        print(f"Sending: {command_str.strip()}")
        
        sock.send(command_str.encode())
        
        # Receive response
        response_data = b""
        sock.settimeout(5)
        
        while True:
            try:
                chunk = sock.recv(1024)
                if not chunk:
                    break
                response_data += chunk
                if b'\n' in response_data:
                    break
            except socket.timeout:
                break
        
        sock.close()
        
        if response_data:
            response_str = response_data.decode().strip()
            print(f"Response: {response_str}")
            
            try:
                response_json = json.loads(response_str)
                if response_json.get("success"):
                    print("✓ Command/response test successful")
                    return True
                else:
                    print(f"✗ Command failed: {response_json.get('error', 'Unknown error')}")
                    return False
            except json.JSONDecodeError:
                print(f"✗ Invalid JSON response: {response_str}")
                return False
        else:
            print("✗ No response received")
            return False
            
    except ConnectionRefusedError:
        print("✗ Connection refused - is the Pico command server running?")
        return False
    except socket.timeout:
        print("✗ Connection timeout")
        return False
    except OSError as e:
        if hasattr(e, 'winerror') and e.winerror == 10054:
            print("✗ Connection forcibly closed by Pico - server may have crashed")
        else:
            print(f"✗ Network error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_multiple_commands(ip, port=8080, count=5):
    """Test multiple rapid commands"""
    print(f"Testing {count} rapid commands to {ip}:{port}")
    
    success_count = 0
    for i in range(count):
        print(f"Command {i+1}/{count}:", end=" ")
        if test_command_response(ip, port):
            success_count += 1
        time.sleep(0.5)  # Brief pause between commands
    
    print(f"Success rate: {success_count}/{count} ({success_count/count*100:.1f}%)")
    return success_count == count

def main():
    if len(sys.argv) > 1:
        pico_ip = sys.argv[1]
    else:
        pico_ip = input("Enter Pico IP address: ").strip()
    
    if not pico_ip:
        print("No IP address provided")
        return
    
    print(f"Monica Pico Connection Diagnostic")
    print(f"Target: {pico_ip}:8080")
    print("=" * 50)
    
    # Test 1: Basic connection
    if not test_basic_connection(pico_ip):
        print("\n❌ Basic connection failed. Check:")
        print("  - Is the Pico powered on?")
        print("  - Is the Pico connected to WiFi?")
        print("  - Is the command server running (Mode 2)?")
        print("  - Are both devices on the same network?")
        return
    
    print()
    
    # Test 2: Command/Response
    if not test_command_response(pico_ip):
        print("\n❌ Command/response failed. Check:")
        print("  - Is the Pico command server responding?")
        print("  - Check Pico console for error messages")
        print("  - Try restarting the Pico")
        return
    
    print()
    
    # Test 3: Multiple commands
    if not test_multiple_commands(pico_ip):
        print("\n⚠️ Some commands failed. This may indicate:")
        print("  - Network instability")
        print("  - Pico memory issues")
        print("  - Server overload")
    else:
        print("\n✅ All tests passed! Connection is stable.")
    
    print("\nDiagnostic complete.")

if __name__ == "__main__":
    main()
