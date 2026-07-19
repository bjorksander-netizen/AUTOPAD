# AUTOPAD

**Remote Control App — Phone → Desktop Windows 10**

Turn your Android phone into a wireless trackpad, keyboard, media control, and clipboard sync for your Windows desktop.

---

## Quick Start (Easiest Way)

### Option 1: Run the batch file (Recommended)
1. Double-click `run.bat` in `desktop-server/`
2. It will auto-install Python dependencies and launch the GUI
3. Note the IP address shown in the GUI
4. Open AUTOPAD app on your phone and connect

### Option 2: Build standalone .exe
1. Double-click `build.bat` in `desktop-server/`
2. Wait for the build to finish
3. Run `desktop-server/dist/AUTOPAD-Server.exe`
4. No Python installation needed on target machine

### Option 3: Run manually
```bash
cd desktop-server
pip install -r requirements.txt
python gui_server.py
```

---

## Features

| Feature | Description |
|---------|-------------|
| **Trackpad** | Swipe to move cursor, tap = click, long press = right click |
| **Keyboard** | Full QWERTY with F1-F12, Ctrl/Alt/Shift/Win modifiers |
| **Media Control** | Play/Pause, Previous/Next, Volume slider, Mute |
| **Mouse Buttons** | Left/Middle/Right click |
| **Clipboard Sync** | Bi-directional real-time clipboard sync |

## Connection Methods

| Method | How it Works |
|--------|-------------|
| **WiFi/Hotspot** | WebSocket over local network |
| **Bluetooth** | RFCOMM serial connection |
| **USB** | ADB reverse tunnel |

---

## Desktop GUI

The desktop server now comes with a GUI application:

```
+-----------------------------------------------+
|              AUTOPAD Server v1.1.0             |
+-----------------------------------------------+
|  [green dot] Running                          |
|             IP: 192.168.1.100:8765            |
+-----------------------------------------------+
|  Bluetooth: Ready                             |
|  USB/ADB: No device                           |
+-----------------------------------------------+
|         [  STOP SERVER  ]                     |
+-----------------------------------------------+
|  Connected Clients                            |
|  +------------------------------------------+ |
|  | 192.168.1.105:54321                       | |
|  +------------------------------------------+ |
+-----------------------------------------------+
|  Server Log                                   |
|  +------------------------------------------+ |
|  | [Server started successfully]             | |
|  | [Client connected: 192.168.1.105:54321]   | |
|  | [Clipboard synced (42 chars)]             | |
|  +------------------------------------------+ |
+-----------------------------------------------+
```

---

## Project Structure

```
AUTOPAD/
├── README.md
├── desktop-server/
│   ├── gui_server.py        # GUI application (main entry)
│   ├── server.py            # CLI server (alternative)
│   ├── run.bat              # Auto-setup & run
│   ├── build.py             # Build .exe script
│   ├── protocol.py          # Message protocol
│   ├── config.py            # Configuration
│   ├── input_controller.py  # Mouse & keyboard simulation
│   ├── media_controller.py  # Media playback control
│   ├── clipboard_monitor.py # Clipboard sync
│   ├── requirements.txt     # Python dependencies
│   └── connection/
│       ├── wifi_server.py   # WebSocket server
│       ├── bluetooth_server.py
│       └── usb_server.py
├── android-app/             # Android Kotlin app
│   ├── app/src/main/
│   │   ├── java/com/autopad/
│   │   └── res/
│   └── build.gradle.kts
└── .github/workflows/
    └── build.yml            # CI: Build APK
```

---

## Android App

Build the APK via GitHub Actions:
1. Go to https://github.com/bjorksander-netizen/AUTOPAD/actions
2. Click latest workflow run
3. Download `AUTOPAD-debug-apk` artifact

---

## Configuration

Edit `config.py` to customize:
```python
WS_PORT = 8765
AUTH_TOKEN = "autopad-secure-token"
DEVICE_NAME = "Windows Desktop"
```

---

## Tech Stack

- **Desktop**: Python, tkinter, websockets, pyautogui, pycaw
- **Android**: Kotlin, OkHttp3, Material Design 3

---

## License

MIT License
