#!/usr/bin/env python3
"""
Test script to verify the timing overlap fix works correctly
"""

import mido
from mido import MidiFile, MidiTrack, Message
from midi_processor import midi_processor

def create_overlapping_midi():
    """Create a MIDI file with overlapping notes to test timing resolution"""
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    
    # Create overlapping notes that would cause timing conflicts
    # Note 1: starts at 0ms, duration 1000ms
    track.append(Message('note_on', channel=0, note=60, velocity=64, time=0))
    track.append(Message('note_off', channel=0, note=60, velocity=64, time=1000))
    
    # Note 2: starts at 500ms (overlaps with note 1), duration 800ms
    track.append(Message('note_on', channel=0, note=64, velocity=64, time=500))
    track.append(Message('note_off', channel=0, note=64, velocity=64, time=800))
    
    # Note 3: starts at 900ms (overlaps with both), duration 600ms
    track.append(Message('note_on', channel=0, note=67, velocity=64, time=400))
    track.append(Message('note_off', channel=0, note=67, velocity=64, time=600))
    
    # Note 4: starts at 1200ms (should be fine), duration 500ms
    track.append(Message('note_on', channel=0, note=72, velocity=64, time=500))
    track.append(Message('note_off', channel=0, note=72, velocity=64, time=500))
    
    filename = 'test_overlapping.mid'
    mid.save(filename)
    print(f"Created overlapping MIDI file: {filename}")
    return filename

def test_timing_resolution():
    """Test that overlapping duties are properly resolved"""
    print("Testing Timing Resolution Fix")
    print("=" * 40)
    
    # Create test file with overlapping notes
    test_file = create_overlapping_midi()
    
    try:
        # Process the MIDI file
        print(f"\nProcessing {test_file}...")
        duties, path, metadata = midi_processor.process_midi_file(test_file)
        
        print(f"✅ Successfully processed {len(duties)} duties")
        print(f"✅ Generated path with {len(path)} positions")
        print(f"✅ Total duration: {metadata['duration_ms']/1000:.1f} seconds")
        
        # Check that duties are properly ordered (duties are now dictionaries)
        print(f"\nDuty timing verification:")
        for i, duty_dict in enumerate(duties[:5]):  # Show first 5 duties
            start_ms = duty_dict['start_ms']
            duration_ms = duty_dict['duration_ms']
            end_ms = start_ms + duration_ms
            print(f"  Duty {i+1}: {start_ms}ms - {end_ms}ms "
                  f"(duration: {duration_ms}ms, chord: {duty_dict['chord']})")
        
        # Verify no overlapping duties
        overlaps_found = 0
        for i in range(len(duties) - 1):
            current_end = duties[i]['start_ms'] + duties[i]['duration_ms']
            next_start = duties[i+1]['start_ms']
            if current_end > next_start:
                overlaps_found += 1
                print(f"❌ Overlap found: duty {i+1} ends at {current_end}ms, "
                      f"duty {i+2} starts at {next_start}ms")
        
        if overlaps_found == 0:
            print("✅ No overlapping duties found - timing resolution working correctly!")
        else:
            print(f"❌ Found {overlaps_found} overlapping duties")
        
        return overlaps_found == 0
        
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
    success = test_timing_resolution()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 Timing resolution test PASSED!")
        print("The MIDI processing fix is working correctly.")
    else:
        print("❌ Timing resolution test FAILED!")
        print("There may still be issues with duty timing.")
