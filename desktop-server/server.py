"""AUTOPAD - Main Server Entry Point"""

import asyncio
import sys
import signal
import socket
import json
from protocol import Message, MessageType
from input_controller import InputController
from media_controller import MediaController
from clipboard_monitor import ClipboardMonitor
from connection.wifi_server import WiFiServer
from connection.bluetooth_server import BluetoothServer
from connection.usb_server import USBServer
import config
from functools import partial


class AutopadServer:
    def __init__(self):
        self.input_ctrl = InputController()
        self.media_ctrl = MediaController()
        self.clipboard = ClipboardMonitor(
            poll_interval=config.CLIPBOARD_POLL_INTERVAL,
            max_length=config.CLIPBOARD_MAX_LENGTH
        )
        self.wifi = WiFiServer(host=config.WS_HOST, port=config.WS_PORT)
        self.bluetooth = BluetoothServer(
            name=config.BLUETOOTH_NAME,
            uuid=config.BLUETOOTH_UUID
        )
        self.usb = USBServer(ws_port=config.WS_PORT)
        self._active_ws = None
        self._loop = None

    def _log(self, msg: str):
        print(f"[AUTOPAD] {msg}")

    def _handle_message(self, raw_msg: str, source=None):
        msg = Message.from_json(raw_msg)
        if msg is None:
            return

        self._process_message(msg, source)

    def _process_message(self, msg: Message, source=None):
        t = msg.type
        d = msg.data

        if t == MessageType.PING:
            self._send_to(source, Message.pong().to_json())

        elif t == MessageType.CONNECT:
            token = d.get("token", "")
            if token == config.AUTH_TOKEN:
                self._send_to(source, Message.connect({
                    "name": config.DEVICE_NAME,
                    "version": config.VERSION
                }).to_json())
                self._log("Client authenticated successfully")
            else:
                self._log("Authentication failed")

        elif t == MessageType.MOUSE_MOVE:
            self.input_ctrl.mouse_move(d.get("delta_x", 0), d.get("delta_y", 0))

        elif t == MessageType.MOUSE_CLICK:
            self.input_ctrl.mouse_click(d.get("button", "left"))

        elif t == MessageType.MOUSE_DOUBLE_CLICK:
            self.input_ctrl.mouse_double_click(d.get("button", "left"))

        elif t == MessageType.MOUSE_SCROLL:
            self.input_ctrl.mouse_scroll(d.get("delta", 0))

        elif t == MessageType.MOUSE_DOWN:
            self.input_ctrl.mouse_down(d.get("button", "left"))

        elif t == MessageType.MOUSE_UP:
            self.input_ctrl.mouse_up(d.get("button", "left"))

        elif t == MessageType.KEY_PRESS:
            self.input_ctrl.key_press(d.get("key", ""))

        elif t == MessageType.KEY_RELEASE:
            self.input_ctrl.key_up(d.get("key", ""))

        elif t == MessageType.KEY_COMBO:
            self.input_ctrl.key_combo(d.get("keys", []))

        elif t == MessageType.KEY_TEXT:
            self.input_ctrl.key_text(d.get("text", ""))

        elif t == MessageType.MEDIA_PLAY_PAUSE:
            self.media_ctrl.play_pause()

        elif t == MessageType.MEDIA_NEXT:
            self.media_ctrl.next_track()

        elif t == MessageType.MEDIA_PREVIOUS:
            self.media_ctrl.previous_track()

        elif t == MessageType.MEDIA_STOP:
            self.media_ctrl.stop()

        elif t == MessageType.VOLUME_UP:
            self.media_ctrl.volume_up()

        elif t == MessageType.VOLUME_DOWN:
            self.media_ctrl.volume_down()

        elif t == MessageType.VOLUME_SET:
            self.media_ctrl.volume_set(d.get("level", 50))

        elif t == MessageType.VOLUME_MUTE:
            self.media_ctrl.volume_mute()

        elif t == MessageType.CLIPBOARD_SYNC:
            content = d.get("content", "")
            self.clipboard.set_clipboard(content)
            self._log(f"Clipboard synced ({len(content)} chars)")

        elif t == MessageType.CLIPBOARD_PUSH:
            content = self.clipboard.get_clipboard()
            response = Message.clipboard_sync(content, "windows")
            self._send_to(source, response.to_json())

        elif t == MessageType.CLIPBOARD_PULL:
            content = self.clipboard.get_clipboard()
            response = Message.clipboard_sync(content, "windows")
            self._send_to(source, response.to_json())

    def _send_to(self, target, message: str):
        if target is not None:
            coro = self.wifi.send_to(target, message)
        else:
            coro = self.wifi.send_to_all(message)
        if self._loop is not None and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(coro, self._loop)

    def _on_clipboard_changed(self, content: str):
        msg = Message.clipboard_changed(content, "windows")
        if self._loop is not None and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(self.wifi.send_to_all(msg.to_json()), self._loop)

    def _on_client_connect(self, client_info: str):
        self._log(f"Client connected: {client_info}")

    def _on_client_disconnect(self, client_info: str):
        self._log(f"Client disconnected: {client_info}")

    async def start(self):
        print(r"""
    ___       ____________  __  _________
   /   |     / ____/ ____ \/  |/  / ___/
  / /| |    / __/ / / __ `/ /|_/ /\__ \
 / ___ |   / /___/ / / / / /  / /___/ /
/_/  |_|  /_____/_/ /_/ /_/  /_//____/
        Remote Control v""" + config.VERSION
        """)

        self.wifi.set_callbacks(
            on_message=self._handle_message,
            on_connect=self._on_client_connect,
            on_disconnect=self._on_client_disconnect
        )

        local_ip = self.wifi.get_local_ip()
        self._log(f"Starting WiFi server on {local_ip}:{config.WS_PORT}")
        result = await self.wifi.start()
        self._log(result)

        self._log(f"Starting Bluetooth server...")
        bt_result = self.bluetooth.start()
        self._log(bt_result)

        self._log(f"Checking USB/ADB...")
        adb_status = self.usb.get_status()
        if adb_status["adb_available"] and adb_status["devices"]:
            self._log(f"ADB devices found: {adb_status['devices']}")
            adb_result = self.usb.setup_adb_reverse()
            self._log(adb_result)
        else:
            self._log("No ADB devices found (USB mode available when phone connected)")

        self.clipboard.set_callback(self._on_clipboard_changed)
        self.clipboard.start()
        self._log("Clipboard monitor started")

        self._log("=" * 50)
        self._log(f"  AUTOPAD Server is running!")
        self._log(f"  WiFi: ws://{local_ip}:{config.WS_PORT}")
        self._log(f"  Bluetooth: {config.BLUETOOTH_NAME}")
        self._log(f"  USB/ADB: {'Ready' if adb_status.get('devices') else 'Waiting for device'}")
        self._log(f"  Token: {config.AUTH_TOKEN}")
        self._log("=" * 50)

    async def stop(self):
        self._log("Shutting down AUTOPAD server...")
        self.clipboard.stop()
        self.bluetooth.stop()
        self.usb.cleanup()
        await self.wifi.stop()
        self._log("Server stopped")


async def main():
    server = AutopadServer()
    loop = asyncio.get_running_loop()
    server._loop = loop

    def signal_handler():
        raise KeyboardInterrupt()

    if sys.platform == "win32":
        signal.signal(signal.SIGINT, lambda *_: loop.call_soon_threadsafe(lambda: None))
    else:
        loop.add_signal_handler(signal.SIGINT, signal_handler)

    try:
        await server.start()
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())
