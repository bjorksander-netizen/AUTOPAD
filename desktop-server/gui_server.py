"""AUTOPAD Desktop Server - GUI Application"""

import asyncio
import sys
import os
import threading
import socket
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from protocol import Message, MessageType
from input_controller import InputController
from media_controller import MediaController
from clipboard_monitor import ClipboardMonitor
from connection.wifi_server import WiFiServer
from connection.bluetooth_server import BluetoothServer
from connection.usb_server import USBServer
import config

BG_DARK = "#121212"
BG_SECONDARY = "#1E1E1E"
BG_TERTIARY = "#2C2C2C"
ACCENT_CYAN = "#00D9FF"
ACCENT_PURPLE = "#7C4DFF"
TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#B0B0B0"
SUCCESS_GREEN = "#00E676"
ERROR_RED = "#FF5252"
WARNING_YELLOW = "#FFD600"


class AutopadServerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"AUTOPAD Server v{config.VERSION}")
        self.root.geometry("520x680")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(False, False)

        self.server = None
        self.loop = None
        self.server_thread = None
        self.running = False
        self.clients = []

        self._build_ui()
        self._detect_ip()

    def _build_ui(self):
        title_frame = tk.Frame(self.root, bg=BG_SECONDARY)
        title_frame.pack(fill=tk.X)

        tk.Label(title_frame, text="AUTOPAD", font=("Segoe UI", 24, "bold"),
                 fg=ACCENT_CYAN, bg=BG_SECONDARY).pack(pady=(15, 0))
        tk.Label(title_frame, text=f"Desktop Server v{config.VERSION}",
                 font=("Segoe UI", 10), fg=TEXT_SECONDARY, bg=BG_SECONDARY).pack(pady=(0, 15))

        status_frame = tk.Frame(self.root, bg=BG_TERTIARY, highlightbackground="#333333",
                                highlightthickness=1)
        status_frame.pack(fill=tk.X, padx=20, pady=(20, 10))

        self.status_dot = tk.Canvas(status_frame, width=14, height=14,
                                    bg=BG_TERTIARY, highlightthickness=0)
        self.status_dot.pack(side=tk.LEFT, padx=(15, 8), pady=15)
        self.status_dot.create_oval(2, 2, 12, 12, fill=ERROR_RED, outline="", tags="dot")

        status_text_frame = tk.Frame(status_frame, bg=BG_TERTIARY)
        status_text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=12)

        self.lbl_status = tk.Label(status_text_frame, text="Stopped",
                                   font=("Segoe UI", 13, "bold"), fg=TEXT_PRIMARY, bg=BG_TERTIARY)
        self.lbl_status.pack(anchor=tk.W)

        self.lbl_ip = tk.Label(status_text_frame, text="IP: --",
                               font=("Segoe UI", 9), fg=TEXT_SECONDARY, bg=BG_TERTIARY)
        self.lbl_ip.pack(anchor=tk.W)

        info_frame = tk.Frame(self.root, bg=BG_TERTIARY, highlightbackground="#333333",
                              highlightthickness=1)
        info_frame.pack(fill=tk.X, padx=20, pady=5)

        self.lbl_bt = tk.Label(info_frame, text="Bluetooth: Ready",
                               font=("Segoe UI", 9), fg=TEXT_SECONDARY, bg=BG_TERTIARY,
                               anchor=tk.W)
        self.lbl_bt.pack(fill=tk.X, padx=15, pady=(10, 2))

        self.lbl_usb = tk.Label(info_frame, text="USB/ADB: Waiting",
                                font=("Segoe UI", 9), fg=TEXT_SECONDARY, bg=BG_TERTIARY,
                                anchor=tk.W)
        self.lbl_usb.pack(fill=tk.X, padx=15, pady=(2, 10))

        btn_frame = tk.Frame(self.root, bg=BG_DARK)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        self.btn_start = tk.Button(btn_frame, text="START SERVER", font=("Segoe UI", 12, "bold"),
                                   fg="#000000", bg=ACCENT_CYAN, activebackground="#00B8D9",
                                   activeforeground="#000000", relief=tk.FLAT, cursor="hand2",
                                   height=2, command=self._toggle_server)
        self.btn_start.pack(fill=tk.X)

        clients_frame = tk.LabelFrame(self.root, text=" Connected Clients ",
                                      font=("Segoe UI", 9), fg=TEXT_SECONDARY, bg=BG_DARK,
                                      labelanchor="n")
        clients_frame.pack(fill=tk.X, padx=20, pady=(5, 5))

        self.clients_listbox = tk.Listbox(clients_frame, bg=BG_TERTIARY, fg=TEXT_PRIMARY,
                                          font=("Consolas", 9), relief=tk.FLAT,
                                          selectbackground=BG_TERTIARY, height=3)
        self.clients_listbox.pack(fill=tk.X, padx=5, pady=5)

        log_frame = tk.LabelFrame(self.root, text=" Server Log ",
                                  font=("Segoe UI", 9), fg=TEXT_SECONDARY, bg=BG_DARK,
                                  labelanchor="n")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 15))

        self.log_text = scrolledtext.ScrolledText(log_frame, bg=BG_TERTIARY, fg=TEXT_PRIMARY,
                                                  font=("Consolas", 9), relief=tk.FLAT,
                                                  insertbackground=TEXT_PRIMARY, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _detect_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            self.lbl_ip.config(text=f"IP: {ip}:{config.WS_PORT}")
        except Exception:
            self.lbl_ip.config(text=f"IP: 127.0.0.1:{config.WS_PORT}")

    def _log(self, msg: str):
        if self.root:
            self.root.after(0, self._append_log, msg)

    def _append_log(self, msg: str):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{msg}]\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _set_status(self, connected: bool, text: str):
        self.root.after(0, self._update_status, connected, text)

    def _update_status(self, connected: bool, text: str):
        self.lbl_status.config(text=text)
        color = SUCCESS_GREEN if connected else ERROR_RED
        self.status_dot.delete("dot")
        self.status_dot.create_oval(2, 2, 12, 12, fill=color, outline="", tags="dot")

    def _set_clients(self, clients: list):
        self.root.after(0, self._update_clients, clients)

    def _update_clients(self, clients: list):
        self.clients_listbox.delete(0, tk.END)
        for c in clients:
            self.clients_listbox.insert(tk.END, c)
        if not clients:
            self.clients_listbox.insert(tk.END, "No clients connected")

    def _toggle_server(self):
        if self.running:
            self._stop_server()
        else:
            self._start_server()

    def _start_server(self):
        self.running = True
        self.btn_start.config(text="STOP SERVER", bg=ERROR_RED, activebackground="#D32F2F")
        self._set_status(False, "Starting...")

        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()

    def _stop_server(self):
        self.running = False
        self.btn_start.config(text="START SERVER", bg=ACCENT_CYAN, activebackground="#00B8D9")
        self._set_status(False, "Stopped")
        self._set_clients([])

        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self._async_stop(), self.loop)

    def _run_server(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.server = AutopadServerGUIHandler(self)
        self.loop.run_until_complete(self.server.start())

        self._set_status(True, "Running")
        self._log("Server started successfully")

        self.loop.run_forever()

    async def _async_stop(self):
        if self.server:
            await self.server.stop()
        self.loop.call_soon_threadsafe(self.loop.stop)

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _on_close(self):
        if self.running:
            self._stop_server()
        self.root.destroy()


class AutopadServerGUIHandler:
    def __init__(self, gui: AutopadServerGUI):
        self.gui = gui
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
        self.connected_clients = []

    def _log(self, msg: str):
        self.gui._log(msg)

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
                self._log("Client authenticated")
            else:
                self._log("Auth failed")
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
            self._send_to(source, Message.clipboard_sync(content, "windows").to_json())
        elif t == MessageType.CLIPBOARD_PULL:
            content = self.clipboard.get_clipboard()
            self._send_to(source, Message.clipboard_sync(content, "windows").to_json())

    def _send_to(self, target, message: str):
        if target is not None:
            coro = self.wifi.send_to(target, message)
        else:
            coro = self.wifi.send_to_all(message)
        if self.gui.loop is not None and self.gui.loop.is_running():
            asyncio.run_coroutine_threadsafe(coro, self.gui.loop)

    def _on_clipboard_changed(self, content: str):
        msg = Message.clipboard_changed(content, "windows")
        if self.gui.loop is not None and self.gui.loop.is_running():
            asyncio.run_coroutine_threadsafe(self.wifi.send_to_all(msg.to_json()), self.gui.loop)

    def _on_client_connect(self, client_info: str):
        self.connected_clients.append(client_info)
        self.gui._set_clients(self.connected_clients)
        self._log(f"Connected: {client_info}")

    def _on_client_disconnect(self, client_info: str):
        if client_info in self.connected_clients:
            self.connected_clients.remove(client_info)
        self.gui._set_clients(self.connected_clients)
        self._log(f"Disconnected: {client_info}")

    async def start(self):
        self._log("Initializing AUTOPAD Server...")

        self.wifi.set_callbacks(
            on_message=self._handle_message,
            on_connect=self._on_client_connect,
            on_disconnect=self._on_client_disconnect
        )

        local_ip = self.wifi.get_local_ip()
        self._log(f"WiFi: ws://{local_ip}:{config.WS_PORT}")

        await self.wifi.start()
        self._log("WebSocket server started")

        self._log("Starting Bluetooth...")
        bt_result = self.bluetooth.start()
        self._log(bt_result)

        adb_status = self.usb.get_status()
        usb_text = f"Found: {adb_status['devices']}" if adb_status.get("devices") else "No device"
        self.gui.root.after(0, lambda: self.gui.lbl_usb.config(text=f"USB/ADB: {usb_text}"))
        self._log(f"USB/ADB: {usb_text}")

        if adb_status["adb_available"] and adb_status["devices"]:
            adb_result = self.usb.setup_adb_reverse()
            self._log(adb_result)

        self.clipboard.set_callback(self._on_clipboard_changed)
        self.clipboard.start()
        self._log("Clipboard monitor started")

        self.gui._set_status(True, "Running")
        self.gui._set_clients(["Waiting for connections..."])

        self._log(f"Token: {config.AUTH_TOKEN}")
        self._log("Ready for connections!")

    async def stop(self):
        self._log("Shutting down...")
        self.clipboard.stop()
        self.bluetooth.stop()
        self.usb.cleanup()
        await self.wifi.stop()
        self._log("Server stopped")


def main():
    app = AutopadServerGUI()
    app.run()


if __name__ == "__main__":
    main()
