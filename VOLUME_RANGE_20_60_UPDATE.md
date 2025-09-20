# Volume Range Update: 20-60% Servo Range

## Summary

The Monica volume system has been updated from 25-80% to **20-60% servo range** for more conservative volume control.

## New Volume Mapping

### Formula
```
if user_percent <= 0:
    servo_percent = 0% (silence)
else:
    servo_percent = 20 + (user_percent * 40 / 100)
```

### Volume Examples
| User Input | Servo Output | Musical Level |
|------------|--------------|---------------|
| 0%         | 0%           | Silence       |
| 25%        | 30%          | Quiet         |
| 50%        | 40%          | Normal        |
| 75%        | 50%          | Loud          |
| 100%       | 60%          | Maximum       |

## Benefits of 20-60% Range

1. **More Conservative**: Lower maximum volume reduces mechanical stress
2. **Better Safety**: Reduced risk of overdriving the system
3. **Good Resolution**: Still provides 40% servo range for dynamic expression
4. **Musical Suitability**: Adequate range for expressive performance
5. **Mechanical Longevity**: Gentler on hardware components

## Files Updated

1. **`peripherals/standard_servo.py`** - Updated mapping formula and documentation
2. **`local_webserver/local_web_server.py`** - Updated API documentation
3. **`templates/index.html`** - Updated user interface help text
4. **`config.py`** - Updated configuration documentation
5. **`VOLUME_RANGE_UPDATE.md`** - Updated comprehensive documentation
6. **`VOLUME_DYNAMICS_IMPLEMENTATION.md`** - Updated volume mapping examples

## Backward Compatibility

This change requires updating the Pico firmware with the new `standard_servo.py` file. The webserver will continue to send 0-100% user percentages, but the Pico will now map them to the 20-60% servo range.

## Testing

To verify the new volume range:
1. Set volume to 0% - should be silent
2. Set volume to 50% - should be normal volume (40% servo)
3. Set volume to 100% - should be maximum volume (60% servo)
4. All intermediate values should provide smooth transitions within the 20-60% range
