"""AUTOPAD USB Server - ADB Reverse Tunnel Connection"""

import asyncio
import subprocess
import os
from typing import Callable, Optional


class USBServer:
    def __init__(self, ws_port: int = 8765):
        self._ws_port = ws_port
        self._adb_reverse_active = False
        self._on_message: Optional[Callable] = None

    def set_callback(self, on_message=None):
        self._on_message = on_message

    def setup_adb_reverse(self) -> str:
        try:
            result = subprocess.run(
                ["adb", "reverse", f"tcp:{self._ws_port}", f"tcp:{self._ws_port}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self._adb_reverse_active = True
                return f"ADB Reverse established on port {self._ws_port}"
            else:
                return f"ADB Error: {result.stderr}"
        except FileNotFoundError:
            return "ADB not found. Install Android SDK Platform Tools."
        except subprocess.TimeoutExpired:
            return "ADB command timed out"
        except Exception as e:
            return f"ADB Error: {e}"

    def check_adb_devices(self) -> list:
        try:
            result = subprocess.run(
                ["adb", "devices"],
                capture_output=True,
                text=True,
                timeout=5
            )
            devices = []
            lines = result.stdout.strip().split("\n")[1:]
            for line in lines:
                if line.strip() and "\tdevice" in line:
                    device_id = line.split("\t")[0]
                    devices.append(device_id)
            return devices
        except Exception:
            return []

    def is_adb_available(self) -> bool:
        try:
            result = subprocess.run(
                ["adb", "version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def cleanup(self):
        if self._adb_reverse_active:
            try:
                subprocess.run(
                    ["adb", "reverse", "--remove", f"tcp:{self._ws_port}"],
                    capture_output=True,
                    timeout=5
                )
            except Exception:
                pass
            self._adb_reverse_active = False

    def get_status(self) -> dict:
        adb_available = self.is_adb_available()
        devices = self.check_adb_devices() if adb_available else []
        return {
            "adb_available": adb_available,
            "devices": devices,
            "reverse_active": self._adb_reverse_active,
            "ws_port": self._ws_port
        }
