# Monica Project Structure

## Directory Organization

```
monica-interface/
├── 📁 Pico Files (Upload to Pico)
│   ├── main.py                     # Main entry point with mode selection
│   ├── config.py                   # Hardware configuration
│   ├── device.py                   # Hardware device initialization
│   ├── network_credentials.py     # WiFi credentials (keep private)
│   ├── network_init.py            # Network connection management
│   ├── pico_command_server.py     # Network command server for Pico
│   │
│   ├── monica/                    # Core Monica logic
│   │   ├── __init__.py
│   │   ├── controller.py          # Performance control logic
│   │   ├── duty.py               # Musical duty definitions
│   │   ├── keystra.py            # Path planning algorithm
│   │   ├── planner.py            # Song planning
│   │   ├── songwriter.py         # Song definitions
│   │   └── wagon.py              # Wagon movement logic
│   │
│   ├── peripherals/              # Hardware peripheral drivers
│   │   ├── __init__.py
│   │   ├── abstractions/         # Base classes
│   │   ├── button.py
│   │   ├── buzzer.py
│   │   ├── fingers_rig.py
│   │   ├── fuzzy_encoder.py
│   │   ├── joystick.py
│   │   ├── rotary_encoder.py
│   │   ├── servo_rig.py
│   │   ├── standard_servo.py
│   │   ├── stepper_servo.py
│   │   └── stepper.py
│   │
│   └── utils/                    # Utility modules
│       ├── debug.py
│       ├── events/               # Event system
│       ├── iterables.py
│       ├── linear_kinematics/    # Movement calculations
│       ├── math.py
│       ├── music/                # Musical theory
│       ├── pin_debugger.py
│       └── time.py
│
├── 📁 Computer Files (Local Web Server)
│   └── local_webserver/
│       ├── local_web_server.py    # Flask web server
│       ├── requirements.txt       # Python dependencies
│       ├── README.md             # Local webserver docs
│       └── templates/            # HTML templates
│           ├── index.html        # Main control interface
│           └── config.html       # Configuration page
│
├── 📁 Documentation
│   ├── README.md                 # Main project README
│   ├── README_NETWORK_CONTROL.md # Network control system docs
│   ├── README_WEB_SETUP.md       # Web setup documentation
│   ├── PROJECT_STRUCTURE.md      # This file
│   └── TODO                      # Development notes
│
└── 📁 Legacy/Unused Files
    └── web_server.py             # Old full web interface (memory heavy)
```

## What Goes Where

### 🎯 **Upload to Pico** (Essential Files Only)
```bash
# Core files
main.py
config.py
device.py
network_credentials.py
network_init.py
pico_command_server.py

# Directories (entire folders)
monica/
peripherals/
utils/
```

### 💻 **Keep on Computer** (Local Web Server)
```bash
local_webserver/
├── local_web_server.py
├── requirements.txt
├── README.md
└── templates/
    ├── index.html
    └── config.html
```

### 📚 **Documentation** (Reference Only)
- All `README*.md` files
- `TODO` file
- `PROJECT_STRUCTURE.md`

## Usage Modes

### **Mode 1: Original Performance** (Minimal Memory)
- Uses: Core Monica files only
- Memory: ~15-20KB
- Features: Original automated performance

### **Mode 2: Network Command Server** (Recommended)
- Uses: Core files + network files + command server
- Memory: ~25-35KB
- Features: Full keyboard control via network

### **Mode 3: Full Web Interface** (High Memory)
- Uses: All Pico files including web_server.py
- Memory: ~45-60KB
- Features: Web interface directly on Pico (may cause memory issues)

## Quick Setup Commands

### **Setup Pico:**
```bash
# Upload essential files to Pico
# (Use your preferred method: Thonny, ampy, etc.)
```

### **Setup Computer:**
```bash
cd local_webserver
pip install -r requirements.txt
python local_web_server.py
```

This structure separates concerns clearly: Pico handles hardware control, computer handles user interface.


