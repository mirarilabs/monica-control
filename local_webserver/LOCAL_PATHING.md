# Local Song Pathing Processing

## Overview

Monica's local web server now supports processing song pathing locally on your computer instead of on the Pico. This feature provides faster performance and reduces the computational load on the Pico.

## Features

- **Local Pathing Processing**: Calculate optimal cart movement paths on your computer
- **Selected by Default**: The option is enabled by default for better performance
- **Fallback Support**: Automatically falls back to Pico pathing if local processing fails
- **All Songs Supported**: Works with all available Monica songs (showcase, original, simple, range_test)

## How It Works

### Traditional Method (Pico Pathing)
1. Web server sends song name to Pico
2. Pico calculates optimal pathing using its onboard planner
3. Pico executes the performance

### New Method (Local Pathing)
1. Web server calculates optimal pathing locally using Python implementation
2. Web server sends pre-processed pathing data to Pico
3. Pico executes the performance using the pre-calculated path

## Benefits

- **Faster Performance**: No pathing calculation delay on the Pico
- **Reduced Pico Load**: Less computational work on the microcontroller
- **Better Reliability**: More robust pathing calculation on full computer
- **Consistent Results**: Same pathing algorithm as Pico, but faster execution

## Usage

### Web Interface
1. Open the Monica web interface (http://localhost:5000)
2. The "Process song pathing locally" checkbox is selected by default
3. Select and play any song - pathing will be processed locally
4. The interface shows whether local or Pico pathing was used

### Programmatic Usage
```python
from monica_pathing import song_planner

# Process pathing locally
duties_dict, path = song_planner.plan_song_by_name("showcase")

# Send to Pico with pre-processed pathing
response = pico_client.send_command({
    "type": "play_performance_with_pathing",
    "song": "showcase",
    "duties": duties_dict,
    "path": path
})
```

## Technical Details

### Local Pathing Implementation
- **File**: `monica_pathing.py`
- **Algorithm**: Simplified but compatible version of Monica's Keystra pathfinding
- **Output**: JSON-serializable duties and path data
- **Fallback**: Automatic fallback to Pico pathing on errors

### Pico Integration
- **New Command**: `play_performance_with_pathing`
- **Data Format**: JSON duties and path arrays
- **Conversion**: Pico converts JSON back to native Duty objects
- **Execution**: Same performance execution as regular pathing

### Song Support
All Monica songs are supported:
- **showcase**: Full demonstration with cart movement
- **original**: "Por lo que yo te quiero" - Original Monica song
- **simple**: Basic test song with simple chords
- **range_test**: Explores all cart positions

## Configuration

### Default Settings
- Local pathing is **enabled by default**
- Checkbox is **selected** in the web interface
- Automatic fallback to Pico pathing on errors

### Disabling Local Pathing
To use traditional Pico pathing:
1. Uncheck "Process song pathing locally" in the web interface
2. Or modify the default in `index.html` (line 378): `checked` → `unchecked`

## Testing

Run the test script to verify local pathing works:
```bash
cd local_webserver
python test_pathing.py
```

This will test all songs and verify the pathing calculation works correctly.

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure `monica_pathing.py` is in the same directory as `local_web_server.py`

2. **Pathing Failures**: If local pathing fails, the system automatically falls back to Pico pathing

3. **Performance Issues**: Local pathing should be faster, but if you experience issues, try disabling it

### Error Messages
- **"Local pathing failed"**: Falls back to Pico pathing automatically
- **"Connection error"**: Check network connection to Pico
- **"Unknown song"**: Song name not recognized, falls back to "showcase"

## Future Enhancements

Potential improvements for local pathing:
- **Custom Songs**: Support for user-uploaded songs
- **Real-time Pathing**: Live pathing calculation during performance
- **Pathing Visualization**: Visual representation of calculated paths
- **Performance Metrics**: Timing comparison between local and Pico pathing


