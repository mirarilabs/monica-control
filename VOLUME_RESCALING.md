# Monica Volume Rescaling System

## Overview

Monica's volume system has been enhanced with intelligent rescaling that maps the user-friendly 0-100% range to the practical servo operating range of 30-70%, eliminating unusable volume levels and providing better control resolution.

## 🎚️ Volume Rescaling Logic

### **User Range → Servo Range Mapping**

| **User Input** | **Servo Position** | **Effect** |
|----------------|-------------------|------------|
| **0%** | **0%** | True silence (servo minimum) |
| **1-100%** | **30-70%** | Practical volume range |

### **Mathematical Formula**
```python
def map_volume_percentage(user_percent):
    if user_percent <= 0:
        return 0.0  # True silence
    
    # Map 0-100% user input to 30-70% servo range  
    servo_percent = 30 + (user_percent * 40 / 100)
    return servo_percent / 100.0  # Convert to 0-1 for servo
```

### **Example Mappings**
```
User  0% → Servo  0% (0.00) → PWM 1500 → Silence
User 25% → Servo 40% (0.40) → PWM 4340 → Quiet
User 50% → Servo 50% (0.50) → PWM 5050 → Normal  
User 75% → Servo 60% (0.60) → PWM 5760 → Loud
User 100% → Servo 70% (0.70) → PWM 6470 → Maximum
```

## 🎯 Benefits of Rescaling

### **Eliminates Dead Range**
- **Old system**: 0-30% servo = barely audible/unusable
- **New system**: 0% = silence, 1%+ = immediately usable
- **Better resolution**: Full 0-100% user range maps to usable servo range

### **Improved Control Resolution**
- **Old system**: Large servo range wasted on unusable volumes
- **New system**: Every 1% user input = meaningful volume change
- **Better precision**: 100 steps across usable range vs scattered

### **Intuitive Operation**
- **0% = Silence**: Clear, predictable silence
- **100% = Maximum**: Maximum practical volume (not servo maximum)
- **Linear feel**: Each increment feels proportionally louder
- **No dead zones**: Every percentage produces audible change

## 🔧 Technical Implementation

### **Servo Enhancement**
```python
# StandardServo now includes volume mapping
def _map_volume_percentage(self, user_percent: float) -> float:
    if user_percent <= 0:
        return 0.0  # Silence
    
    # Map 0-100% user to 30-70% servo
    servo_percent = 30 + (user_percent * 40 / 100)
    return servo_percent / 100.0
```

### **Automatic Integration**
- **Integer input**: `servo.go_to(75)` automatically uses rescaling
- **Percentage method**: `servo.go_to_percent(75)` uses rescaling
- **Float input**: `servo.go_to(0.75)` bypasses rescaling (direct servo position)
- **Named positions**: `servo.go_to("Home")` unchanged

### **Web Interface Display**
```javascript
// Shows both user percentage and actual servo position
User Volume: 75%
Servo Position: 60%  // Calculated: 30 + (75 * 40/100) = 60%
```

## 🎵 Musical Impact

### **Volume Range Optimization**
- **Practical minimum**: 1% user = 30% servo = first audible level
- **Practical maximum**: 100% user = 70% servo = maximum usable volume
- **No wasted range**: Every user percentage produces useful volume
- **Better dynamics**: More control resolution in usable range

### **Performance Benefits**
- **Immediate response**: 1% volume = immediate audible change
- **Linear dynamics**: Volume changes feel proportional
- **Predictable behavior**: 50% always sounds like "half volume"
- **Professional control**: Like real audio equipment

### **Updated Presets**
```
silence (0%)  → servo 0%  → True silence
whisper (10%) → servo 34% → Very quiet
quiet (20%)   → servo 38% → Quiet practice
soft (30%)    → servo 42% → Soft performance
normal (50%)  → servo 50% → Balanced default
medium (70%)  → servo 58% → Medium volume
loud (85%)    → servo 64% → Strong performance
forte (95%)   → servo 68% → Very loud
maximum (100%) → servo 70% → Practical maximum
```

## 📊 Comparison: Old vs New System

### **Old System (Direct Mapping)**
```
User 0%   → Servo 0%   → Silence ✓
User 30%  → Servo 30%  → Barely audible ✗
User 50%  → Servo 50%  → Moderate ✓
User 70%  → Servo 70%  → Good volume ✓
User 100% → Servo 100% → Too loud/distorted ✗
```

### **New System (Rescaled Mapping)**
```
User 0%   → Servo 0%   → Silence ✓
User 30%  → Servo 42%  → Clear, usable volume ✓
User 50%  → Servo 50%  → Moderate (same as before) ✓
User 70%  → Servo 58%  → Good volume ✓
User 100% → Servo 70%  → Maximum practical volume ✓
```

## 🎯 Practical Usage

### **Volume Setting Guidelines**
- **0-20%**: Quiet practice, background ambiance
- **20-40%**: Soft performances, intimate settings
- **40-60%**: Normal performances, balanced sound
- **60-80%**: Strong performances, larger rooms
- **80-100%**: Maximum impact, dramatic effects

### **Musical Applications**
- **Dynamics**: Use full 0-100% range for musical expression
- **Recording**: Consistent levels using exact percentages
- **Performance**: Adjust for room acoustics and audience size
- **Practice**: Lower volumes for quiet practice sessions

## 🔍 Visual Feedback

### **Web Interface Shows**
- **User volume**: What you set (0-100%)
- **Servo position**: Actual servo position (0-70%)
- **Mapping explanation**: Clear indication of rescaling
- **Preset highlighting**: Active preset based on user percentage

### **Console Output**
```
Setting pump to 75% volume
Servo position: 60% (mapped from 75% user input)
```

## ⚙️ Technical Details

### **PWM Duty Cycle Calculation**
```
User 50% → Servo 0.50 → PWM duty = (1-0.50)*1500 + 0.50*8600 = 5050
User 75% → Servo 0.60 → PWM duty = (1-0.60)*1500 + 0.60*8600 = 5760
User 100% → Servo 0.70 → PWM duty = (1-0.70)*1500 + 0.70*8600 = 6470
```

### **Backward Compatibility**
- **Named positions**: "Home" and "Silence" still work
- **Float input**: Direct servo positions (0.0-1.0) bypass rescaling
- **Legacy API**: Existing code continues to work
- **Gradual migration**: Can update components individually

This rescaling system provides a much more intuitive and practical volume control experience while maintaining all the precision and flexibility of the percentage-based system!
