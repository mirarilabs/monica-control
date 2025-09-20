#!/usr/bin/env python3
"""
Test script for local Monica pathing processing
"""

from monica_pathing import song_planner

def test_pathing():
    """Test the local pathing functionality"""
    print("Testing local Monica pathing processing...")
    
    try:
        # Test all available songs
        songs = ["showcase", "original", "simple", "range_test"]
        
        for song_name in songs:
            print(f"\n--- Testing song: {song_name} ---")
            duties_dict, path = song_planner.plan_song_by_name(song_name)
            
            print(f"✓ Successfully processed {song_name}")
            print(f"  - Duties: {len(duties_dict)}")
            print(f"  - Path positions: {len(path)}")
            print(f"  - Duration: {duties_dict[-1]['start_ms'] + duties_dict[-1]['duration_ms']}ms")
            print(f"  - Cart positions used: {sorted(set(path))}")
            
            # Check for volume variations
            volumes = [d['volume_percent'] for d in duties_dict if d['volume_percent'] is not None]
            if volumes:
                print(f"  - Volume range: {min(volumes)}% - {max(volumes)}%")
                print(f"  - Volume changes: {len(volumes)} duties with volume")
            else:
                print(f"  - Volume: No volume variations found")
            
            # Verify duty structure with volume info
            for i, duty in enumerate(duties_dict[:3]):  # Check first 3 duties
                volume_str = f", vol={duty['volume_percent']}%" if duty['volume_percent'] is not None else ""
                print(f"    Duty {i}: {duty['start_ms']}ms, {duty['duration_ms']}ms, chord='{duty['chord']}'{volume_str}")
        
        print(f"\n✓ All {len(songs)} songs processed successfully!")
        print("Local pathing is working correctly.")
        
    except Exception as e:
        print(f"✗ Error testing pathing: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_pathing()
    exit(0 if success else 1)


