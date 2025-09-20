# Monica Sustained Note Feature

## Overview

Monica now supports **sustained notes** - holding down a key keeps the finger in position, creating continuous notes like a real harmonica!

## 🎵 How It Works

### **Key Hold Behavior:**
- **Press and hold** a key → Finger moves to position and stays there
- **Release the key** → Finger returns to home position
- **Multiple keys** → Can hold multiple fingers simultaneously for chords

### **Controls:**

#### **Keyboard:**
- **Hold any key** (A-K, W-I) to sustain the note
- **Release the key** to stop the note
- **Multiple keys** can be held simultaneously

#### **Mouse/Touch:**
- **Click and hold** a virtual key to sustain
- **Release or move mouse away** to stop the note
- **Touch and hold** on mobile devices

## 🎹 Musical Benefits

### **Real Harmonica Feel:**
- **Sustained notes** like a real harmonica player
- **Chord playing** by holding multiple keys
- **Expressive control** over note duration
- **Natural breathing patterns** with note sustain

### **Performance Techniques:**
- **Long notes** for melodic lines
- **Chord sustains** for harmony
- **Staccato** by quick key presses
- **Legato** by overlapping key holds

## 🔧 Technical Implementation

### **Three Command Types:**

#### **1. Key Down (`/api/key_down`)**
```json
{"type": "key_down", "finger": 0, "position": 1}
```
- Moves finger to position and holds
- Used for sustained notes

#### **2. Key Up (`/api/key_up`)**
```json
{"type": "key_up", "finger": 0}
```
- Returns finger to home position
- Used when key is released

#### **3. Press Key (`/api/press_key`)**
```json
{"type": "press_key", "finger": 0, "position": 1}
```
- Quick press/release (legacy mode)
- Auto-returns to home after brief delay

### **Behavior Changes:**

| **Action** | **Old Behavior** | **New Behavior** |
|------------|------------------|------------------|
| **Key press** | Quick press + auto-return | Hold position until release |
| **Key hold** | No effect | Sustains note |
| **Key release** | No effect | Returns finger to home |
| **Mouse click** | Quick press | Hold until mouse up/leave |

## 🎯 Usage Examples

### **Single Note Sustain:**
1. Press and hold `A` key
2. Finger 0 moves to Left position and stays
3. Note plays continuously
4. Release `A` key
5. Finger 0 returns to Home position

### **Chord Playing:**
1. Press and hold `A`, `D`, and `G` keys
2. Fingers 0, 1, and 2 move to positions and stay
3. Chord plays continuously
4. Release keys individually or together
5. Fingers return to home as keys are released

### **Melodic Playing:**
1. Hold `A` for 2 seconds (sustained note)
2. Release `A`, immediately press `S` (legato transition)
3. Hold `S` for 1 second
4. Quick tap `D` (staccato note)
5. Hold `F` and `H` together (chord ending)

## 🚀 Performance Tips

### **For Best Musical Results:**
- **Practice timing** - hold keys for musical durations
- **Use chords** - hold multiple keys for harmony
- **Mix techniques** - combine sustained and quick notes
- **Breathing simulation** - pause between phrases like a real player

### **Technical Tips:**
- **Smooth transitions** - release one key while pressing another
- **Multiple fingers** - can sustain up to 7 notes simultaneously
- **Visual feedback** - web interface shows which keys are active
- **Low latency** - optimized for real-time musical performance

## 🎼 Musical Applications

### **Song Styles:**
- **Ballads** - Long sustained notes for emotional expression
- **Folk music** - Natural breathing patterns with sustained phrases
- **Blues** - Expressive note bending with sustained tones
- **Classical** - Precise note control and chord voicing

### **Performance Techniques:**
- **Vibrato** - Slight finger movements while sustaining
- **Dynamics** - Volume control while sustaining notes
- **Articulation** - Mix of sustained and quick notes
- **Phrasing** - Musical sentences with natural breathing

This feature transforms Monica from a robotic player into an expressive musical instrument that responds to your touch and timing!


