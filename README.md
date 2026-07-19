# AUTOPAD

**Remote Control App — Phone → Desktop Windows 10**

Turn your Android phone into a wireless trackpad, keyboard, media control, and clipboard sync for your Windows desktop. Connect via WiFi/Hotspot, Bluetooth, or USB.

---

## Features

| Feature | Description |
|---------|-------------|
| **Trackpad** | Swipe to move cursor, tap = click, long press = right click, double tap = double click |
| **Keyboard** | Full QWERTY keyboard with function keys (F1-F12), modifiers (Ctrl/Alt/Shift/Win), and special keys |
| **Media Control** | Play/Pause, Previous/Next track, Volume slider, Mute |
| **Mouse Buttons** | Left/Middle/Right click with dedicated buttons |
| **Clipboard Sync** | Bi-directional real-time clipboard synchronization between phone and desktop |

## Connection Methods

| Method | How it Works |
|--------|-------------|
| **WiFi/Hotspot** | WebSocket connection over local network (auto-discovery) |
| **Bluetooth** | RFCOMM serial connection (pairing-based) |
| **USB** | ADB reverse tunnel (phone connected via USB cable) |

## Tech Stack

### Desktop Server
- Python 3.10+
- websockets — WebSocket server
- pyautogui — Mouse/keyboard simulation
- pycaw — Windows audio control
- pyperclip — Clipboard access
- bleak / pybluez — Bluetooth support

### Android App
- Kotlin
- OkHttp3 — WebSocket client
- Material Design 3 — UI components
- Coroutines — Async operations

---

## Quick Start

### 1. Desktop Server Setup

```bash
cd desktop-server
pip install -r requirements.txt
python server.py
```

The server will display:
- WiFi connection URL (e.g., `ws://192.168.1.100:8765`)
- Bluetooth name (`AUTOPAD`)
- Auth token

### 2. Android App Setup

**Option A: Build from source**
```bash
cd android-app
./gradlew assembleDebug
adb install app/build/outputs/apk/debug/app-debug.apk
```

**Option B: Install APK** (if pre-built)

### 3. Connect

1. Open AUTOPAD app on your phone
2. Tap **Connect to Desktop**
3. Enter the server IP address shown on desktop
4. Tap **Connect**

### 4. Use

Navigate between Trackpad, Keyboard, Media, and Clipboard tabs using the bottom navigation bar.

---

## Connection Guide

### WiFi/Hotspot
1. Ensure phone and desktop are on the same network
2. Find your desktop IP: the server prints it on startup
3. Enter IP in the app and connect

### Bluetooth
1. Pair your phone with desktop via Bluetooth settings
2. Open AUTOPAD app
3. Select Bluetooth connection and choose your desktop

### USB
1. Enable USB Debugging on your phone
2. Connect phone to desktop via USB cable
3. The server auto-detects and sets up ADB reverse tunnel
4. Select USB connection in the app

---

## Project Structure

```
AUTOPAD/
├── README.md
├── desktop-server/              # Python server for Windows
│   ├── server.py               # Main entry point
│   ├── protocol.py             # Message protocol
│   ├── config.py               # Configuration
│   ├── input_controller.py     # Mouse & keyboard simulation
│   ├── media_controller.py     # Media playback control
│   ├── clipboard_monitor.py    # Clipboard sync
│   ├── requirements.txt        # Python dependencies
│   └── connection/
│       ├── wifi_server.py      # WebSocket server
│       ├── bluetooth_server.py # Bluetooth RFCOMM
│       └── usb_server.py       # USB via ADB
├── android-app/                # Android Kotlin app
│   ├── app/src/main/
│   │   ├── java/com/autopad/
│   │   │   ├── MainActivity.kt
│   │   │   ├── ui/             # UI Fragments
│   │   │   ├── connection/     # Connection managers
│   │   │   ├── protocol/       # Message protocol
│   │   │   └── service/        # Background service
│   │   ├── res/                # Resources (dark theme)
│   │   └── AndroidManifest.xml
│   ├── build.gradle.kts
│   └── settings.gradle.kts
└── docs/
```

---

## Configuration

Edit `desktop-server/config.py` to customize:

```python
WS_PORT = 8765           # WebSocket port
AUTH_TOKEN = "autopad-secure-token"  # Auth token
DEVICE_NAME = "Windows Desktop"      # Device name
MOUSE_SENSITIVITY = 1.0  # Mouse sensitivity
SCROLL_SENSITIVITY = 1.0 # Scroll sensitivity
```

---

## Dark Theme

AUTOPAD uses a dark theme with:
- **Primary BG**: `#121212`
- **Accent**: `#00D9FF` (Cyan)
- **Secondary Accent**: `#7C4DFF` (Purple)
- **Success**: `#00E676` (Green)
- **Error**: `#FF5252` (Red)

---

## Security

- Token-based authentication on connection
- Local network only (no external access)
- User control over clipboard sync
- Connection whitelist support

---

## License

MIT License

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

## Credits

Built with Python + Kotlin + Material Design 3
