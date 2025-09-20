# Volume Dynamics Implementation

## Overview

Monica's songs now include dynamic volume variations that change throughout each performance, creating more expressive and musical performances. Volume levels are specified per duty (musical event) and automatically applied during song execution.

## Implementation Details

### 1. Enhanced Duty Class (`monica/duty.py`)

**New Field**: `volume_percent` (Optional[int])
- `None`: Use current volume (no change)
- `int`: Set volume to specific percentage (0-100%)

**Updated Methods**:
- `Duty()` constructor now accepts `volume_percent` parameter
- `Duty.silence()` now accepts `volume_percent` parameter
- String representation includes volume information

### 2. Controller Integration (`monica/controller.py`)

**Volume Change Logic**:
```python
# Handle volume change if specified in duty
if duty.volume_percent is not None and duty.volume_percent != current_volume:
    device.pump.go_to(duty.volume_percent)
    current_volume = duty.volume_percent
    print(f"Volume changed to {current_volume}%")
```

**Features**:
- Automatic volume changes during performance
- Volume changes only when different from current volume
- Maintains volume state throughout song
- Logs volume changes for debugging

### 3. Local Pathing Support (`local_webserver/monica_pathing.py`)

**Updated Local Implementation**:
- `Duty` class includes `volume_percent` field
- `to_dict()` and `from_dict()` methods handle volume serialization
- All song implementations include volume variations

### 4. Pico Command Server (`pico_command_server.py`)

**Enhanced Duty Conversion**:
- Converts JSON volume data back to native Duty objects
- Supports both local and Pico pathing with volume dynamics

## Song Volume Implementations

### 1. Monica Showcase Song
**Volume Progression**: 30% → 100% → 70%
- **Opening**: Soft start (30-40%)
- **Development**: Building intensity (50-80%)
- **Rhythmic Section**: Dynamic contrast (50-85%)
- **Climax**: Peak volume (90-100%)
- **Finale**: Gentle conclusion (70%)

**Musical Structure**:
- Piano (30-40%): Soft opening
- Mezzo (50-65%): Building sections
- Forte (70-85%): Strong sections
- Fortissimo (90-100%): Climactic moments

### 2. Original Song ("Por lo que yo te quiero")
**Volume Progression**: 40% → 85% → 50%
- **Verse 1**: Soft start (40-60%)
- **Bridge**: Building (70-75%)
- **Verse 2**: Peak intensity (80-85%)
- **Ending**: Gentle fade (50-70%)

### 3. Simple Song (song1)
**Volume Pattern**: 40% → 90% → 55%
- Progressive crescendo with peak on final high note
- Volume range: 40-90%

### 4. Range Test Song (song6)
**Volume Pattern**: 50% → 80% → 75%
- Crescendo pattern for range demonstration
- Volume range: 50-80%

### 5. Simple Test Songs (song2-5)
**Volume Levels**:
- song2: 50% (single note)
- song3: 60% (single note)
- song4: 70% (high note)
- song5: 40% → 80% (contrast)

## Volume Mapping

**User Volume Range**: 0-100%
**Servo Range**: 0-60% (20-60% for non-zero volumes)
**Formula**: `servo_percent = 20 + (user_percent * 40 / 100)`

**Examples**:
- 30% user → 32% servo (piano)
- 50% user → 40% servo (mezzo)
- 70% user → 48% servo (forte)
- 100% user → 60% servo (fortissimo)

## Technical Features

### 1. Automatic Volume Management
- Volume changes only when specified in duty
- Efficient volume updates (no unnecessary changes)
- Maintains volume state throughout performance

### 2. Musical Expression
- Dynamic contrast between sections
- Crescendo and decrescendo patterns
- Appropriate volume for musical context
- Peak volumes at climactic moments

### 3. Backward Compatibility
- Songs without volume specification use current volume
- Existing songs work without modification
- Graceful handling of missing volume data

### 4. Performance Optimization
- Volume changes processed efficiently
- Minimal impact on timing
- Clear logging for debugging

## Usage Examples

### Creating Volume Variations
```python
# Soft opening
duty1 = Duty(0, 1000, chord, volume_percent=30)

# Building intensity
duty2 = Duty(1000, 1000, chord, volume_percent=60)

# Peak volume
duty3 = Duty(2000, 1000, chord, volume_percent=90)

# No volume change (use current)
duty4 = Duty(3000, 1000, chord)  # volume_percent=None
```

### Volume in Song Sequences
```python
musical_sequence = [
    ("F3", 0, 800, 30, "Soft start"),
    ("G3_B3", 1000, 1000, 50, "Building"),
    ("C4_E4_G4", 2000, 1000, 80, "Forte"),
]
```

## Testing

Run the test script to verify volume implementation:
```bash
cd local_webserver
python test_pathing.py
```

**Test Output Includes**:
- Volume range for each song
- Number of duties with volume changes
- Sample duty structure with volume info

## Benefits

1. **Musical Expression**: Dynamic volume creates more engaging performances
2. **Automatic Control**: No manual volume adjustment needed during songs
3. **Consistent Mapping**: Same volume system across all songs
4. **Flexible Design**: Easy to add volume variations to new songs
5. **Performance Optimized**: Efficient volume change processing

## Future Enhancements

Potential improvements:
- **Volume Curves**: Smooth volume transitions between duties
- **Dynamic Markings**: Support for musical dynamic markings (pp, p, mp, mf, f, ff)
- **Volume Automation**: Automatic volume based on note/chord complexity
- **User Control**: Option to disable/enable volume dynamics
- **Volume Visualization**: Visual representation of volume changes in web interface
