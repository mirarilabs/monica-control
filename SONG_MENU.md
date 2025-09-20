# Monica Song Selection Menu

## Overview

Monica's web interface now features a comprehensive song selection menu that allows you to choose between preloaded songs and provides a placeholder for future upload functionality.

## 🎵 Song Selection Features

### **Song Menu Interface**
- **Modal dialog** with professional design
- **Song list** showing all available performances
- **Song descriptions** explaining each performance
- **Visual selection** with hover and selection states
- **Upload placeholder** for future custom songs

### **Available Songs**

#### **1. "showcase" (Default)**
- **Monica Showcase** - Full demonstration with cart movement
- **Features**: Single notes, chords, full range, cart movement
- **Duration**: ~18.4 seconds
- **Best for**: Demonstrating Monica's full capabilities

#### **2. "original"**
- **Por lo que yo te quiero** - Original Monica song
- **Features**: Traditional harmonica melody
- **Duration**: Variable based on tempo
- **Best for**: Musical performance, traditional sound

#### **3. "simple"**
- **Simple Song** - Basic test song
- **Features**: Simple chord progression
- **Duration**: Short
- **Best for**: Quick testing, basic demonstration

#### **4. "range_test"**
- **Range Test** - Explores all positions
- **Features**: Tests every cart position and note
- **Duration**: Extended
- **Best for**: Hardware testing, calibration verification

## 🎹 How to Use

### **Song Selection Process**
1. **Click "🎵 Select & Play Song"** button
2. **Song menu opens** with available options
3. **Click on desired song** to select it
4. **Song highlights** and start button updates
5. **Click "▶️ Start [Song] Performance"** to begin
6. **Menu closes** and performance starts

### **Song Information Display**
Each song shows:
- **Song name** (e.g., "showcase", "original")
- **Description** explaining the song's features
- **Visual selection** highlighting chosen song
- **Dynamic start button** showing selected song name

## 🔧 Technical Implementation

### **API Endpoints**

#### **Get Song List**
```http
GET /api/list_songs
```
Response:
```json
{
  "success": true,
  "songs": {
    "showcase": "Monica Showcase - Full demonstration with cart movement",
    "original": "Por lo que yo te quiero - Original Monica song",
    "simple": "Simple Song - Basic test song", 
    "range_test": "Range Test - Explores all positions"
  }
}
```

#### **Start Selected Performance**
```http
POST /api/start_performance
Content-Type: application/json

{
  "song": "showcase"
}
```

### **Pico Command Protocol**
```json
{"type": "list_songs"}
{"type": "play_performance", "song": "showcase"}
```

### **Song Planning System**
```python
# On Pico - plan specific song
duties, path = monica.planner.plan_song_by_name("showcase")

# Available songs defined in planner
songs = {
    "showcase": monica_showcase,
    "original": por_lo_que_yo_te_quiero, 
    "simple": song1,
    "range_test": song6
}
```

## 🚀 User Experience

### **Song Selection Flow**
1. **Open menu**: Click song selection button
2. **Browse options**: See all available songs with descriptions
3. **Preview info**: Read about each song's features
4. **Select song**: Click to choose (visual feedback)
5. **Start performance**: Click start button with song name
6. **Performance begins**: Selected song plays on Monica

### **Visual Design**
- **Professional modal**: Clean, modern design
- **Responsive layout**: Works on desktop, tablet, mobile
- **Clear organization**: Preloaded vs upload sections
- **Visual feedback**: Hover effects, selection highlighting
- **Intuitive controls**: Easy song selection and starting

### **Future Upload Section**
- **Placeholder design**: Shows coming features
- **Feature preview**: Lists planned upload capabilities
- **Professional appearance**: Maintains design consistency
- **User expectations**: Sets clear expectations for future

## 📁 Upload Functionality Preview

### **Planned Features** (Not Yet Implemented)
- **MIDI file upload** - Convert MIDI to Monica format
- **Web composer** - Create songs directly in browser
- **Music notation import** - Upload sheet music
- **Song library** - Save and manage custom songs
- **Song sharing** - Export/import song files

### **Upload Interface Design**
- **Drag & drop area** for file uploads
- **Format validation** for supported file types
- **Progress indicators** during upload/conversion
- **Song preview** before saving to Monica
- **Library management** for custom songs

## 🎯 Benefits

### **User Experience**
- **Easy song selection** - clear interface for choosing performances
- **Song information** - know what each song offers
- **Professional feel** - polished interface design
- **Future ready** - prepared for upload functionality

### **Musical Flexibility**
- **Multiple options** - different songs for different purposes
- **Easy switching** - change songs without restarting system
- **Performance variety** - from simple tests to complex showcases
- **Expandable** - ready for custom songs when upload is implemented

### **Development Benefits**
- **Modular design** - easy to add new songs
- **Clean API** - consistent command structure
- **Extensible** - ready for upload features
- **Professional** - production-ready interface

This song selection system transforms Monica from a single-song player into a versatile performance system with multiple musical options and a professional user interface!
