# Volume Range Update: 20-60% Servo Range

## Overview

The Monica volume system has been updated to use a 20-60% servo range instead of the previous 25-80% range. This change provides a more conservative volume range while maintaining good resolution and musical expression.

## Changes Made

### 1. Controller Level (Pico) - `peripherals/standard_servo.py`
- **Updated volume mapping formula**: `servo_percent = 20 + (user_percent * 40 / 100)`
- **New range**: 0-100% user input → 0-60% servo (20-60% for non-zero volumes)
- **Benefits**: More conservative volume range, better mechanical safety, good resolution

### 2. Webserver Level - `local_webserver/local_web_server.py`
- **Simplified volume presets**: Now sends raw user percentages (0-100%)
- **Removed volume mapping**: All mapping is now handled on the Pico
- **Cleaner API**: Webserver just passes through user input

### 3. Frontend - `templates/index.html`
- **Removed servo position calculation**: No longer calculates servo position in JavaScript
- **Simplified UI**: Shows raw user percentage, mapping happens on Pico
- **Updated help text**: Reflects that mapping happens on Pico

### 4. Configuration - `config.py`
- **Updated comments**: Reflects new 20-60% servo range

## Volume Mapping Details

### New Mapping Formula
```
if user_percent <= 0:
    servo_percent = 0% (silence)
else:
    servo_percent = 20 + (user_percent * 40 / 100)
```

### Examples
- **0% user** → **0% servo** (silence)
- **25% user** → **30% servo** (quiet)
- **50% user** → **40% servo** (normal)
- **75% user** → **50% servo** (loud)
- **100% user** → **60% servo** (maximum)

## Benefits of Controller-Level Mapping

1. **Centralized Logic**: All volume mapping happens in one place (Pico)
2. **Consistency**: Same mapping used regardless of input source
3. **Simplified Webserver**: No need to duplicate mapping logic
4. **Better Performance**: Less computation on webserver
5. **Easier Maintenance**: Changes only need to be made in one place

## Files Modified

1. **`peripherals/standard_servo.py`** - Updated volume mapping formula
2. **`local_webserver/local_web_server.py`** - Simplified volume presets
3. **`templates/index.html`** - Removed servo position calculation
4. **`config.py`** - Updated documentation

## Testing

To test the new volume range:
1. Set volume to 0% - should be silent
2. Set volume to 50% - should be normal volume
3. Set volume to 100% - should be maximum usable volume
4. All intermediate values should provide smooth volume transitions

## Backward Compatibility

This change is **not backward compatible** with older Pico firmware that uses the 40-90% range. The Pico must be updated with the new `standard_servo.py` file to work correctly with the updated webserver.

