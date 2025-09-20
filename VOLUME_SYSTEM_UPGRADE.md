# Monica Volume System Upgrade

## Overview

Monica's volume system has been completely reworked from named levels (Silence, Low, Normal, High) to a precise percentage-based system (0-100%), providing much finer control over air pump intensity and musical dynamics.

## 🎚️ New Volume System

### **Percentage-Based Control**
- **Range**: 0% (silence) to 100% (maximum)
- **Precision**: 1% increments for fine control
- **Intuitive**: Standard percentage system everyone understands
- **Flexible**: Easy to set exact volume levels

### **Multiple Control Methods**
- **Slider control**: Drag slider for precise setting
- **Button control**: ±5% increments with arrow buttons
- **Direct setting**: API supports exact percentage values
- **Keyboard control**: Arrow keys for quick adjustments

## 🔧 Technical Implementation

### **Configuration Changes**
```python
# config.py - Updated pump configuration
controller = {
    "volume_percent": 45  # Default volume as percentage (0-100%)
}

pump = {
    "pin": 7,
    "min_duty": 1500,
    "max_duty": 8600,
    "max_flight_time": 0.33,
    "pwm_freq": 50,
    "named_positions": {"Home": 0, "Silence": 0},  # Simplified
    "volume_range": (0, 100),  # Volume percentage range
    "volume_curve": "linear"   # Volume curve type
}
```

### **Servo Enhancement**
```python
# StandardServo now supports percentage input
servo.go_to(45)        # 45% position
servo.go_to_percent(75)  # 75% position (explicit method)
servo.go_to(0.75)      # 75% position (float 0-1)
servo.go_to("Home")    # Named position (unchanged)
```

### **Controller Updates**
```python
# monica/controller.py - Updated volume handling
volume_percent = config.controller["volume_percent"]  # 45% default

# Usage in performance
device.pump.go_to(volume_percent)  # Set to percentage
device.pump.go_to(0)              # Silence (0%)
```

## 🎹 User Interface Enhancements

### **Volume Slider**
- **Visual control**: Drag slider from 0% to 100%
- **Real-time feedback**: Shows percentage as you drag
- **Instant update**: Changes volume immediately when released
- **Synchronized display**: Slider and status always match

### **Button Controls**
- **Arrow buttons**: ±5% increments for quick adjustments
- **Keyboard arrows**: ↑↓ keys for volume control
- **Consistent behavior**: All methods update slider and display

### **Status Display**
- **Percentage format**: Shows "45%" instead of "Normal"
- **Real-time updates**: Volume display updates every 2 seconds
- **Synchronized**: All controls show same value

## 🎵 Musical Benefits

### **Precise Dynamics**
- **Fine control**: 1% increments for subtle changes
- **Musical expression**: Gradual crescendos and diminuendos
- **Performance flexibility**: Exact volume for different song styles
- **Consistent levels**: Repeatable volume settings

### **Professional Control**
- **Industry standard**: Percentage-based like professional audio equipment
- **Easy communication**: "Set volume to 75%" is clear
- **Mixing capability**: Precise levels for recording/performance
- **Dynamic range**: Full 0-100% range available

### **Song Integration**
- **Default performance volume**: 45% (good balance)
- **Silence for pauses**: 0% for clean breaks
- **Volume override**: Songs can specify custom volumes
- **Automatic silence**: System returns to 0% after performance

## 🔧 API Changes

### **New Volume Commands**
```json
// Set exact percentage
{"type": "set_volume", "volume_percent": 75}

// Increment/decrement by 5%
{"type": "set_volume", "direction": 1}   // +5%
{"type": "set_volume", "direction": -1}  // -5%
```

### **Status Response**
```json
{
  "success": true,
  "position": 3,
  "volume_percent": 75,  // New percentage field
  "memory": 28000,
  "fingers": {...}
}
```

### **Performance Commands**
```json
// Start performance with default volume
{"type": "play_performance", "song": "showcase"}

// Future: Start with custom volume
{"type": "play_performance", "song": "showcase", "volume": 60}
```

## 🎯 Usage Examples

### **Precise Volume Setting**
1. **Drag slider** to desired percentage (e.g., 65%)
2. **Volume updates** immediately on Monica
3. **All displays** show synchronized 65%
4. **Performance uses** this volume level

### **Quick Adjustments**
1. **Press ↑ arrow** (or +Vol button) for +5%
2. **Press ↓ arrow** (or -Vol button) for -5%
3. **Slider updates** to reflect new value
4. **Status display** shows new percentage

### **Performance Volume**
1. **Set desired volume** before performance (e.g., 80%)
2. **Start song** - uses current volume setting
3. **Volume maintained** throughout performance
4. **Returns to 0%** after song completion

## 🚀 Benefits

### **User Experience**
- **Intuitive control**: Everyone understands percentages
- **Visual feedback**: Slider shows exact position
- **Precise setting**: No guessing between "Low" and "Normal"
- **Professional feel**: Like real audio equipment

### **Musical Expression**
- **Dynamic control**: Fine-tune volume for musical effect
- **Consistent levels**: Repeatable settings for recordings
- **Performance flexibility**: Different volumes for different songs
- **Professional dynamics**: Gradual volume changes

### **Technical Advantages**
- **Exact values**: No ambiguity about volume levels
- **API clarity**: Clear percentage values in commands
- **Extensible**: Easy to add volume curves, presets, etc.
- **Compatible**: Maintains backward compatibility where needed

## 🔄 Migration Notes

### **What Changed**
- **Volume levels**: Named levels → Percentage values
- **Default volume**: "Normal" → 45%
- **Silence**: "Silence" → 0%
- **API responses**: "volume" → "volume_percent"

### **Backward Compatibility**
- **Named positions**: "Home" and "Silence" still work
- **Float values**: 0.0-1.0 range still supported
- **Legacy API**: Old volume commands still function

### **Configuration**
- **Update config.py**: Change volume settings to percentages
- **Update songs**: Use percentage values in custom songs
- **Update scripts**: Use new volume_percent fields

This volume system upgrade provides professional-level control over Monica's dynamics while maintaining the simplicity and reliability of the original system!
