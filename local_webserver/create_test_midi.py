#!/usr/bin/env python3
"""
Create a test MIDI file for testing the upload functionality
"""

import mido
from mido import MidiFile, MidiTrack, Message

def create_test_midi_file():
    """Create a simple test MIDI file"""
    # Create a new MIDI file
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    
    # Add some musical content
    # C major chord (C4, E4, G4)
    track.append(Message('note_on', channel=0, note=60, velocity=64, time=0))  # C4
    track.append(Message('note_on', channel=0, note=64, velocity=64, time=0))  # E4
    track.append(Message('note_on', channel=0, note=67, velocity=64, time=0))  # G4
    
    # Hold the chord for 1 beat
    track.append(Message('note_off', channel=0, note=60, velocity=64, time=480))  # C4
    track.append(Message('note_off', channel=0, note=64, velocity=64, time=0))    # E4
    track.append(Message('note_off', channel=0, note=67, velocity=64, time=0))    # G4
    
    # Single note melody
    track.append(Message('note_on', channel=0, note=72, velocity=80, time=480))   # C5
    track.append(Message('note_off', channel=0, note=72, velocity=80, time=480))
    
    track.append(Message('note_on', channel=0, note=74, velocity=80, time=0))     # D5
    track.append(Message('note_off', channel=0, note=74, velocity=80, time=480))
    
    track.append(Message('note_on', channel=0, note=76, velocity=80, time=0))     # E5
    track.append(Message('note_off', channel=0, note=76, velocity=80, time=480))
    
    # Final chord (F major - F4, A4, C5)
    track.append(Message('note_on', channel=0, note=65, velocity=70, time=480))   # F4
    track.append(Message('note_on', channel=0, note=69, velocity=70, time=0))     # A4
    track.append(Message('note_on', channel=0, note=72, velocity=70, time=0))     # C5
    
    track.append(Message('note_off', channel=0, note=65, velocity=70, time=960))  # F4
    track.append(Message('note_off', channel=0, note=69, velocity=70, time=0))    # A4
    track.append(Message('note_off', channel=0, note=72, velocity=70, time=0))    # C5
    
    # Save the file
    filename = 'test_song.mid'
    mid.save(filename)
    print(f"Created test MIDI file: {filename}")
    print("This file contains:")
    print("- C major chord (C4, E4, G4)")
    print("- Melodic sequence (C5, D5, E5)")
    print("- F major chord (F4, A4, C5)")
    print("- Duration: ~4 seconds")
    print(f"\nYou can now upload this file at: http://localhost:5000")
    print("Click '🎵 Select & Play Song' → '📁 Upload MIDI File'")
    
    return filename

if __name__ == "__main__":
    create_test_midi_file()
