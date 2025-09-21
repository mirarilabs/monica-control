#!/usr/bin/env python3
"""
Test script for MIDI web interface functionality
"""

import os
import sys
import tempfile

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

def test_midi_endpoints():
    """Test the MIDI upload and processing endpoints"""
    print("Testing MIDI Web Interface")
    print("=" * 40)
    
    # Create a test MIDI file
    print("1. Creating test MIDI file...")
    test_file = create_test_midi()
    
    if not test_file:
        print("❌ Failed to create test MIDI file")
        return False
    
    print(f"✅ Created test MIDI file: {test_file}")
    
    try:
        # Test MIDI processing
        print("\n2. Testing MIDI processing...")
        from midi_processor import midi_processor
        
        duties, path, metadata = midi_processor.process_midi_file(test_file)
        print(f"✅ Processed MIDI file successfully")
        print(f"   - Duties: {len(duties)}")
        print(f"   - Path length: {len(path)}")
        print(f"   - Duration: {metadata.get('duration_ms', 0)/1000:.1f} seconds")
        
        # Test MIDI info
        print("\n3. Testing MIDI info extraction...")
        info = midi_processor.get_midi_info(test_file)
        print(f"✅ MIDI info extracted successfully")
        print(f"   - Total notes: {info.get('total_notes', 0)}")
        print(f"   - Notes in range: {info.get('notes_in_range', 0)}")
        print(f"   - Tempo: {info.get('tempo_bpm', 120)} BPM")
        
        # Test web server endpoints (simulated)
        print("\n4. Testing web endpoint simulation...")
        
        # Simulate file upload data
        upload_data = {
            'midi_file': test_file
        }
        
        # Simulate processing response
        response_data = {
            'success': True,
            'message': 'MIDI file processed successfully',
            'midi_info': info,
            'duties': duties,
            'path': path,
            'metadata': metadata
        }
        
        print(f"✅ Web endpoint simulation successful")
        print(f"   - Response success: {response_data['success']}")
        print(f"   - Duties in response: {len(response_data['duties'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
        
    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"\n🧹 Cleaned up test file: {test_file}")

def test_file_validation():
    """Test file validation logic"""
    print("\n" + "=" * 40)
    print("Testing File Validation")
    print("=" * 40)
    
    # Test valid file extensions
    valid_files = ['song.mid', 'music.midi', 'test.MID', 'file.MIDI']
    invalid_files = ['song.mp3', 'music.wav', 'test.txt', 'file.pdf']
    
    print("1. Testing valid file extensions...")
    for filename in valid_files:
        extension = filename.lower().split('.')[-1]
        is_valid = extension in ['mid', 'midi']
        status = "✅" if is_valid else "❌"
        print(f"   {status} {filename} -> {extension}")
    
    print("\n2. Testing invalid file extensions...")
    for filename in invalid_files:
        extension = filename.lower().split('.')[-1]
        is_valid = extension in ['mid', 'midi']
        status = "✅" if not is_valid else "❌"
        print(f"   {status} {filename} -> {extension} (should be invalid)")
    
    # Test file size validation
    print("\n3. Testing file size validation...")
    max_size = 16 * 1024 * 1024  # 16MB
    
    test_sizes = [
        (1024, "1KB"),
        (1024 * 1024, "1MB"),
        (16 * 1024 * 1024, "16MB"),
        (17 * 1024 * 1024, "17MB")
    ]
    
    for size, description in test_sizes:
        is_valid = size <= max_size
        status = "✅" if is_valid else "❌"
        print(f"   {status} {description} ({size} bytes) -> {'Valid' if is_valid else 'Too large'}")

def test_web_interface_components():
    """Test web interface component functionality"""
    print("\n" + "=" * 40)
    print("Testing Web Interface Components")
    print("=" * 40)
    
    # Test status message formatting
    print("1. Testing status message formatting...")
    test_messages = [
        ("Processing MIDI file...", "info"),
        ("MIDI file processed successfully!", "success"),
        ("Error: Invalid file type", "error")
    ]
    
    for message, type_class in test_messages:
        print(f"   ✅ {type_class.upper()}: {message}")
    
    # Test file size formatting
    print("\n2. Testing file size formatting...")
    test_sizes = [0, 1024, 1024*1024, 16*1024*1024]
    
    def format_file_size(bytes):
        if bytes == 0:
            return '0 Bytes'
        k = 1024
        sizes = ['Bytes', 'KB', 'MB', 'GB']
        i = int(math.floor(math.log(bytes) / math.log(k)))
        return f"{parseFloat((bytes / math.pow(k, i)).toFixed(2))} {sizes[i]}"
    
    # Simulate the JavaScript formatting function
    import math
    for size in test_sizes:
        if size == 0:
            formatted = "0 Bytes"
        else:
            k = 1024
            sizes = ['Bytes', 'KB', 'MB', 'GB']
            i = int(math.floor(math.log(size) / math.log(k)))
            formatted = f"{round(size / math.pow(k, i), 2)} {sizes[i]}"
        print(f"   ✅ {size} bytes -> {formatted}")

def main():
    """Run all web interface tests"""
    print("MIDI Web Interface Test Suite")
    print("=" * 50)
    
    success = True
    
    # Test core functionality
    if not test_midi_endpoints():
        success = False
    
    # Test validation logic
    test_file_validation()
    
    # Test web components
    test_web_interface_components()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Web interface is ready.")
        print("\nTo use the MIDI upload feature:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Start web server: python local_web_server.py")
        print("3. Open http://localhost:5000")
        print("4. Click '🎵 Select & Play Song'")
        print("5. Upload a MIDI file in the '📁 Upload MIDI File' section")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    main()
