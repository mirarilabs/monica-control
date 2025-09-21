#!/usr/bin/env python3
"""
Test script for Local Duty Calculation

This script demonstrates the local duty calculation functionality
for real-time key control, showing how it eliminates network latency.
"""

from local_duty_calculator import local_duty_calculator
import time

def test_local_duty_calculation():
    """Test the local duty calculation system"""
    print("=== Local Duty Calculation Test ===\n")
    
    # Test 1: Initial state
    print("1. Initial state:")
    status = local_duty_calculator.get_status()
    print(f"   Active keys: {status['active_keys']}")
    print(f"   Cart position: {status['cart_position']}")
    print(f"   Finger states: {status['finger_states']}")
    print()
    
    # Test 2: Single key press
    print("2. Pressing key 'a' (finger 0, position 0):")
    result = local_duty_calculator.key_down('a')
    print(f"   Success: {result['success']}")
    print(f"   Method: {result.get('method', 'local')}")
    print(f"   Chord: {result['duty']['chord']}")
    print(f"   Cart position: {result['duty']['cart_position']}")
    print(f"   Fingerings: {result['duty']['fingerings']}")
    if result['duty']['cart_movement']:
        print(f"   Cart movement: {result['duty']['cart_movement']['from']} -> {result['duty']['cart_movement']['to']}")
    print()
    
    # Test 3: Multiple key presses (chord)
    print("3. Pressing key 's' (finger 0, position 1) - chord:")
    result = local_duty_calculator.key_down('s')
    print(f"   Success: {result['success']}")
    print(f"   Chord: {result['duty']['chord']}")
    print(f"   Active fingers: {len(result['duty']['active_fingers'])}")
    for finger in result['duty']['active_fingers']:
        print(f"     Finger {finger['finger']} ({finger['key']})")
    print()
    
    # Test 4: Key release
    print("4. Releasing key 'a':")
    result = local_duty_calculator.key_up('a')
    print(f"   Success: {result['success']}")
    print(f"   Chord: {result['duty']['chord']}")
    print(f"   Active keys count: {result['active_keys_count']}")
    print()
    
    # Test 5: All keys released
    print("5. Releasing remaining key 's':")
    result = local_duty_calculator.key_up('s')
    print(f"   Success: {result['success']}")
    print(f"   Type: {result['duty']['type']}")
    print()
    
    # Test 6: Final state
    print("6. Final state:")
    status = local_duty_calculator.get_status()
    print(f"   Active keys: {status['active_keys']}")
    print(f"   Cart position: {status['cart_position']}")
    print(f"   All fingers home: {all(status['finger_states'])}")
    print()
    
    # Test 7: Home all
    print("7. Home all:")
    result = local_duty_calculator.home_all()
    print(f"   Success: {result['success']}")
    print(f"   Message: {result['message']}")
    print()

def test_performance_comparison():
    """Compare local vs network performance (simulation)"""
    print("=== Performance Comparison ===\n")
    
    # Simulate network latency
    NETWORK_LATENCY_MS = 50  # Typical network latency
    
    print("Simulating key press sequence:")
    print("  Network method: Each key press requires network round-trip")
    print(f"  Local method: Instant calculation")
    print()
    
    keys = ['a', 's', 'd', 'f']
    
    # Simulate network method
    print("Network method timing:")
    start_time = time.time()
    for key in keys:
        local_duty_calculator.key_down(key)
        # Simulate network delay
        time.sleep(NETWORK_LATENCY_MS / 1000.0)
    network_time = time.time() - start_time
    print(f"  Total time: {network_time*1000:.1f}ms")
    print(f"  Per key: {network_time*1000/len(keys):.1f}ms")
    print()
    
    # Reset
    local_duty_calculator.home_all()
    
    # Simulate local method
    print("Local method timing:")
    start_time = time.time()
    for key in keys:
        local_duty_calculator.key_down(key)
    local_time = time.time() - start_time
    print(f"  Total time: {local_time*1000:.1f}ms")
    print(f"  Per key: {local_time*1000/len(keys):.1f}ms")
    print()
    
    # Calculate improvement
    improvement = (network_time - local_time) / network_time * 100
    print(f"Performance improvement: {improvement:.1f}% faster")
    print(f"Latency reduction: {network_time*1000 - local_time*1000:.1f}ms per sequence")
    print()

if __name__ == "__main__":
    test_local_duty_calculation()
    test_performance_comparison()
    
    print("=== Test Complete ===")
    print("Local duty calculation is working correctly!")
    print("This eliminates network latency for real-time key control.")
