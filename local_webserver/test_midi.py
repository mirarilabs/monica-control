#!/usr/bin/env python3
"""
Test script for MIDI processing functionality
"""

import os
import sys
import json
from midi_processor import midi_processor, MIDIToDutyConverter, MIDINoteMapper

def create_test_midi():
    """Create a simple test MIDI file using mido"""
    try:
        import mido
        from mido import MidiFile, MidiTrack, Message
        
        # Create a simple test MIDI file
        mid = MidiFile()
        track = MidiTrack()
        mid.tracks.append(track)
        
        # Add some simple notes
        track.append(Message('note_on', channel=0, note=60, velocity=64, time=0))  # C4
        track.append(Message('note_off', channel=0, note=60, velocity=64, time=480))  # 1 beat
        
        track.append(Message('note_on', channel=0, note=64, velocity=64, time=0))  # E4
        track.append(Message('note_off', channel=0, note=64, velocity=64, time=480))
        
        track.append(Message('note_on', channel=0, note=67, velocity=64, time=0))  # G4
        track.append(Message('note_off', channel=0, note=67, velocity=64, time=960))  # 2 beats
        
        # Save test file
        test_file = 'test_simple.mid'
        mid.save(test_file)
        print(f"Created test MIDI file: {test_file}")
        return test_file
        
    except ImportError:
        print("mido library not available. Install with: pip install mido")
        return None

def test_note_mapping():
    """Test MIDI note to Monica note mapping"""
    print("\n=== Testing Note Mapping ===")
    
    mapper = MIDINoteMapper()
    
    # Test various MIDI notes
    test_notes = [60, 64, 67, 72, 76, 79, 84, 53, 84]  # C4, E4, G4, C5, E5, G5, C6, F3, C6
    
    for midi_note in test_notes:
        monica_note = mapper.midi_to_monica_note(midi_note)
        status = "✓" if monica_note else "✗ (out of range)"
        print(f"  MIDI {midi_note:3d} -> {monica_note:4s} {status}")
    
    # Test range filtering
    midi_notes = [50, 60, 70, 80, 90]  # Some in range, some out
    filtered = mapper.filter_notes_in_range([
        type('Note', (), {'note_number': n})() for n in midi_notes
    ])
    print(f"\n  Filtered notes in range: {[n.note_number for n in filtered]}")

def test_midi_processing():
    """Test MIDI file processing"""
    print("\n=== Testing MIDI Processing ===")
    
    # Create test MIDI file
    test_file = create_test_midi()
    if not test_file:
        return
    
    try:
        # Test getting MIDI info
        print(f"Getting info for: {test_file}")
        info = midi_processor.get_midi_info(test_file)
        print(f"MIDI Info:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        # Test processing
        print(f"\nProcessing: {test_file}")
        duties, path, metadata = midi_processor.process_midi_file(test_file)
        
        print(f"\nResults:")
        print(f"  Duties created: {len(duties)}")
        print(f"  Path length: {len(path)}")
        print(f"  Duration: {metadata.get('duration_ms', 0)/1000:.1f} seconds")
        
        # Show first few duties
        print(f"\nFirst 3 duties:")
        for i, duty in enumerate(duties[:3]):
            print(f"  {i+1}: {duty}")
        
        # Test pathing
        if path:
            print(f"\nPath positions: {path[:10]}{'...' if len(path) > 10 else ''}")
        
    except Exception as e:
        print(f"Error processing MIDI: {e}")
    
    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"\nCleaned up test file: {test_file}")

def test_chord_detection():
    """Test chord detection functionality"""
    print("\n=== Testing Chord Detection ===")
    
    from midi_processor import MIDINote, MIDIChordDetector, MIDITimingConverter
    
    # Create test notes
    notes = [
        MIDINote(60, 64, 0, 480, 0),    # C4 at time 0
        MIDINote(64, 64, 0, 480, 0),    # E4 at time 0 (chord with C4)
        MIDINote(67, 64, 0, 480, 0),    # G4 at time 0 (chord with C4, E4)
        MIDINote(72, 64, 960, 480, 0),  # C5 at time 960 (separate)
    ]
    
    # Test chord detection
    detector = MIDIChordDetector(time_window_ms=50)
    timing_converter = MIDITimingConverter()
    timing_converter.ticks_per_quarter = 480
    timing_converter.tempo_bpm = 120
    
    chords = detector.detect_chords(notes, timing_converter)
    
    print(f"  Input notes: {len(notes)}")
    print(f"  Detected chords: {len(chords)}")
    
    for i, chord in enumerate(chords):
        note_names = [MIDINoteMapper.midi_to_monica_note(n.note_number) for n in chord.notes]
        print(f"    Chord {i+1}: {note_names} (start: {chord.start_time}ms)")

def main():
    """Run all tests"""
    print("MIDI Processing Test Suite")
    print("=" * 40)
    
    # Test note mapping
    test_note_mapping()
    
    # Test chord detection
    test_chord_detection()
    
    # Test full processing
    test_midi_processing()
    
    print("\n" + "=" * 40)
    print("Test suite completed!")

if __name__ == "__main__":
    main()
