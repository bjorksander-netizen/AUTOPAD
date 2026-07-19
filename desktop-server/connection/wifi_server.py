"""AUTOPAD WebSocket Server - WiFi/Hotspot Connection"""

import asyncio
import json
import socket
import websockets
from typing import Callable, Optional


class WiFiServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self._host = host
        self._port = port
        self._server = None
        self._clients = set()
        self._on_message: Optional[Callable] = None
        self._on_connect: Optional[Callable] = None
        self._on_disconnect: Optional[Callable] = None

    def set_callbacks(self, on_message=None, on_connect=None, on_disconnect=None):
        self._on_message = on_message
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect

    def get_local_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    async def _handler(self, websocket):
        self._clients.add(websocket)
        client_info = f"{websocket.remote_address}"
        if self._on_connect:
            self._on_connect(client_info)
        try:
            async for message in websocket:
                if self._on_message:
                    self._on_message(message, websocket)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self._clients.discard(websocket)
            if self._on_disconnect:
                self._on_disconnect(client_info)

    async def start(self):
        self._server = await websockets.serve(
            self._handler,
            self._host,
            self._port
        )
        local_ip = self.get_local_ip()
        return f"WiFi Server running on ws://{local_ip}:{self._port}"

    async def stop(self):
        if self._server:
            self._server.close()
            await self._server.wait_closed()

    async def send_to_all(self, message: str):
        if self._clients:
            await asyncio.gather(
                *[client.send(message) for client in self._clients.copy()],
                return_exceptions=True
            )

    async def send_to(self, websocket, message: str):
        try:
            await websocket.send(message)
        except Exception:
            pass

    def get_client_count(self) -> int:
        return len(self._clients)
