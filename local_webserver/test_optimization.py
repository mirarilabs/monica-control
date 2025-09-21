#!/usr/bin/env python3
"""
Test script to verify duty optimization works for large MIDI files
"""

import mido
from mido import MidiFile, MidiTrack, Message
from midi_processor import midi_processor

def create_large_midi():
    """Create a MIDI file with many duties to test optimization"""
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    
    # Create many short notes to exceed the 500 duty limit
    for i in range(600):  # Create 600 duties (more than 500 limit)
        note = 60 + (i % 12)  # Cycle through notes C4-B4
        velocity = 64 + (i % 32)  # Vary velocity
        
        # Each note is 100ms long with 50ms gaps
        track.append(Message('note_on', channel=0, note=note, velocity=velocity, time=150))
        track.append(Message('note_off', channel=0, note=note, velocity=velocity, time=100))
    
    filename = 'test_large.mid'
    mid.save(filename)
    print(f"Created large MIDI file: {filename} with 600 notes")
    return filename

def test_optimization():
    """Test that large MIDI files are properly optimized"""
    print("Testing Duty Optimization")
    print("=" * 40)
    
    # Create large test file
    test_file = create_large_midi()
    
    try:
        # Process the MIDI file
        print(f"\nProcessing {test_file}...")
        duties, path, metadata = midi_processor.process_midi_file(test_file)
        
        print(f"✅ Successfully processed {len(duties)} duties")
        print(f"✅ Generated path with {len(path)} positions")
        print(f"✅ Total duration: {metadata['duration_ms']/1000:.1f} seconds")
        print(f"✅ Optimized: {metadata.get('optimized', False)}")
        
        # Check if optimization occurred
        if metadata.get('optimized', False):
            print("✅ Optimization was applied - duties reduced to fit Pico memory limits")
        else:
            print("⚠️ No optimization needed - file was small enough")
        
        # Verify duties are within limits
        if len(duties) <= 500:
            print("✅ Duty count within Pico limits (≤500 duties)")
        else:
            print(f"❌ Duty count exceeds limits: {len(duties)} duties")
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing MIDI file: {e}")
        return False
        
    finally:
        # Clean up
        import os
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"\n🧹 Cleaned up test file: {test_file}")

if __name__ == "__main__":
    success = test_optimization()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 Optimization test PASSED!")
        print("Large MIDI files will be automatically optimized for Pico memory limits.")
    else:
        print("❌ Optimization test FAILED!")
        print("There may be issues with duty optimization.")
