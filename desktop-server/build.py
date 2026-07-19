"""AUTOPAD - Build standalone .exe using PyInstaller"""

import subprocess
import sys
import os


def install_pyinstaller():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])


def build():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "AUTOPAD-Server",
        "--clean",
        "--noconfirm",
        "--add-data", f"{os.path.join(script_dir, 'connection')};connection",
        "--hidden-import", "pyautogui",
        "--hidden-import", "pynput",
        "--hidden-import", "pycaw",
        "--hidden-import", "comtypes",
        "--hidden-import", "websockets",
        "--hidden-import", "keyboard",
        "--hidden-import", "pyperclip",
        os.path.join(script_dir, "gui_server.py")
    ]

    print("Building AUTOPAD Server...")
    print(f"Command: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, cwd=script_dir)

    if result.returncode == 0:
        exe_path = os.path.join(script_dir, "dist", "AUTOPAD-Server.exe")
        print()
        print("=" * 50)
        print("BUILD SUCCESSFUL!")
        print(f"Output: {exe_path}")
        print("=" * 50)
    else:
        print()
        print("BUILD FAILED!")
        sys.exit(1)


if __name__ == "__main__":
    install_pyinstaller()
    build()
