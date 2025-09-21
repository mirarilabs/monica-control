# Monica MIDI Processing System

## Overview

The Monica MIDI Processing System allows you to convert arbitrary MIDI files into Monica's pathing system, enabling the harmonica robot to play any MIDI composition. This system processes MIDI files locally on your computer and generates optimal cart movement paths for Monica.

## 🎵 Features

### **Core Capabilities**
- **MIDI File Support**: Process standard .mid and .midi files
- **Note Range Mapping**: Automatically maps MIDI notes to Monica's supported range (F3-C6)
- **Chord Detection**: Groups simultaneous notes into chords
- **Timing Conversion**: Converts MIDI timing to Monica's millisecond-based system
- **Volume Mapping**: Maps MIDI velocity to Monica's volume system
- **Path Optimization**: Uses Monica's existing Keystra pathfinding algorithm

### **Web Interface Integration**
- **File Upload**: Upload MIDI files through the web interface
- **Real-time Processing**: Process and play MIDI files instantly
- **File Management**: Automatic cleanup of uploaded files
- **Error Handling**: Comprehensive error reporting and fallback

## 🔧 Technical Architecture

### **System Components**

#### **1. MIDI Parser (`MIDIParser`)**
- Parses MIDI files using the `mido` library
- Extracts note events, timing, and metadata
- Handles tempo changes and multiple tracks
- Converts MIDI ticks to milliseconds

#### **2. Note Mapper (`MIDINoteMapper`)**
- Maps MIDI note numbers to Monica note names
- Filters notes to Monica's supported range (F3-C6)
- Handles note transposition and range validation

#### **3. Chord Detector (`MIDIChordDetector`)**
- Groups simultaneous notes into chords
- Uses configurable time windows for chord detection
- Handles polyphony limitations

#### **4. Duty Converter (`MIDIToDutyConverter`)**
- Converts MIDI chords to Monica Duty objects
- Maps velocity to volume percentages
- Integrates with Monica's pathing system

#### **5. Main Processor (`MIDIProcessor`)**
- Orchestrates the entire processing pipeline
- Provides high-level interface for MIDI processing
- Returns duties, path, and metadata

## 📁 File Structure

```
local_webserver/
├── midi_processor.py          # Core MIDI processing module
├── monica_pathing.py          # Updated with MIDI integration
├── local_web_server.py        # Updated with MIDI endpoints
├── test_midi.py              # Test suite for MIDI processing
├── requirements.txt          # Python dependencies
└── uploads/                  # Temporary MIDI file storage
```

## 🚀 Usage

### **1. Installation**

Install required dependencies:
```bash
cd local_webserver
pip install -r requirements.txt
```

### **2. Web Interface Usage**

1. **Start the web server**:
   ```bash
   python local_web_server.py
   ```

2. **Upload MIDI file**:
   - Navigate to http://localhost:5000
   - Use the MIDI upload interface
   - Select your .mid or .midi file
   - Click "Process MIDI"

3. **Play the processed MIDI**:
   - The system automatically processes the file
   - Click "Play MIDI Performance" to start Monica

### **3. Programmatic Usage**

```python
from midi_processor import midi_processor

# Process a MIDI file
duties, path, metadata = midi_processor.process_midi_file("song.mid")

# Get MIDI file information
info = midi_processor.get_midi_info("song.mid")
print(f"Duration: {info['duration_ms']/1000:.1f} seconds")
print(f"Notes in range: {info['notes_in_range']}/{info['total_notes']}")
```

### **4. Testing**

Run the test suite:
```bash
python test_midi.py
```

## 🎼 MIDI Processing Pipeline

### **Step 1: MIDI Parsing**
1. Parse MIDI file using `mido` library
2. Extract note events, timing, and metadata
3. Handle tempo changes and multiple tracks
4. Convert MIDI ticks to milliseconds

### **Step 2: Note Filtering**
1. Filter notes to Monica's supported range (F3-C6)
2. Remove notes outside the harmonica's physical range
3. Report filtering statistics

### **Step 3: Chord Detection**
1. Group simultaneous notes using time windows
2. Handle polyphony limitations (max 6 simultaneous notes)
3. Create chord objects with timing information

### **Step 4: Duty Conversion**
1. Convert MIDI chords to Monica Chord objects
2. Map MIDI velocity to Monica volume percentages
3. Create Duty objects with proper timing
4. Fill gaps with silence duties

### **Step 5: Path Generation**
1. Use Monica's existing Keystra pathfinding algorithm
2. Generate optimal cart movement paths
3. Return duties, path, and metadata

## 🎹 Note Range and Mapping

### **Monica's Supported Range**
- **Lowest Note**: F3 (MIDI note 53)
- **Highest Note**: C6 (MIDI note 84)
- **Total Range**: 32 semitones (2.67 octaves)

### **MIDI Note Mapping**
```
MIDI Note 53 (F3)  -> F3
MIDI Note 60 (C4)  -> C4
MIDI Note 72 (C5)  -> C5
MIDI Note 84 (C6)  -> C6
```

### **Automatic Filtering**
- Notes below F3 are automatically filtered out
- Notes above C6 are automatically filtered out
- System reports how many notes were filtered

## 🔧 Configuration Options

### **Chord Detection**
```python
detector = MIDIChordDetector(time_window_ms=50)  # 50ms window for chord detection
```

### **Polyphony Limits**
```python
converter = MIDIToDutyConverter(max_polyphony=6)  # Max 6 simultaneous notes
```

### **Volume Mapping**
- MIDI velocity (0-127) → Monica volume (0-100%)
- Linear mapping preserves dynamics

### **File Upload Limits**
- Maximum file size: 16MB
- Supported formats: .mid, .midi
- Automatic cleanup after 1 hour

## 🌐 API Endpoints

### **Upload MIDI File**
```http
POST /api/upload_midi
Content-Type: multipart/form-data

midi_file: [MIDI file]
```

**Response:**
```json
{
  "success": true,
  "message": "MIDI file processed successfully",
  "midi_info": {
    "tempo_bpm": 120,
    "total_notes": 45,
    "notes_in_range": 42
  },
  "duties": [...],
  "path": [...],
  "metadata": {...}
}
```

### **Play Processed MIDI**
```http
POST /api/play_midi
Content-Type: application/json

{
  "duties": [...],
  "path": [...],
  "song_name": "custom_midi"
}
```

## 🐛 Error Handling

### **Common Issues**

1. **Missing mido library**:
   ```
   Error: mido library required. Install with: pip install mido
   ```

2. **No notes in range**:
   ```
   Error: No notes found in Monica's supported range (F3-C6)
   ```

3. **Invalid file format**:
   ```
   Error: Invalid file type. Please upload .mid or .midi files
   ```

4. **File too large**:
   ```
   Error: File exceeds 16MB limit
   ```

### **Fallback Behavior**
- If MIDI processing fails, system reports error
- Web interface shows detailed error messages
- Automatic cleanup of temporary files

## 🧪 Testing

### **Test Suite Features**
- **Note Mapping Tests**: Verify MIDI to Monica note conversion
- **Chord Detection Tests**: Test simultaneous note grouping
- **Full Processing Tests**: End-to-end MIDI processing
- **Range Filtering Tests**: Verify note range handling

### **Running Tests**
```bash
python test_midi.py
```

### **Test Output**
```
MIDI Processing Test Suite
========================================

=== Testing Note Mapping ===
  MIDI  60 -> C4   ✓
  MIDI  64 -> E4   ✓
  MIDI  67 -> G4   ✓

=== Testing Chord Detection ===
  Input notes: 4
  Detected chords: 2

=== Testing MIDI Processing ===
Created test MIDI file: test_simple.mid
Getting info for: test_simple.mid
Processing: test_simple.mid

Results:
  Duties created: 3
  Path length: 4
  Duration: 2.0 seconds
```

## 🔮 Future Enhancements

### **Planned Features**
1. **Advanced Chord Analysis**: Better chord recognition and voicing
2. **Tempo Following**: Dynamic tempo changes during playback
3. **Multi-track Support**: Handle complex MIDI arrangements
4. **Note Prioritization**: Smart note selection for polyphony limits
5. **Transposition**: Automatic key transposition for better range utilization

### **Performance Optimizations**
1. **Caching**: Cache processed MIDI files
2. **Streaming**: Process large MIDI files in chunks
3. **Parallel Processing**: Multi-threaded MIDI processing

## 📚 Dependencies

### **Required Libraries**
- **Flask**: Web framework for API endpoints
- **mido**: MIDI file parsing and manipulation
- **Werkzeug**: File upload handling

### **Installation**
```bash
pip install Flask==2.3.3 mido==1.3.0 Werkzeug==2.3.7
```

## 🤝 Integration with Monica

The MIDI processing system seamlessly integrates with Monica's existing architecture:

1. **Uses existing pathing system**: Leverages Monica's proven Keystra algorithm
2. **Compatible data structures**: Generates standard Duty objects
3. **Web interface integration**: Extends existing web interface
4. **Pico communication**: Uses existing command protocol

This ensures that MIDI-processed songs work exactly like Monica's built-in songs, with the same performance quality and reliability.
