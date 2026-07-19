"""AUTOPAD Bluetooth Server - RFCOMM Connection"""

import asyncio
import threading
from typing import Callable, Optional

try:
    from bleak import BleakServer, BleakGATTCharacteristic
    BLEAK_AVAILABLE = True
except ImportError:
    BLEAK_AVAILABLE = False

try:
    import bluetooth
    PYBLUEZ_AVAILABLE = True
except ImportError:
    PYBLUEZ_AVAILABLE = False


class BluetoothServer:
    def __init__(self, name: str = "AUTOPAD", uuid: str = "00001101-0000-1000-8000-00805f9b34fb"):
        self._name = name
        self._uuid = uuid
        self._running = False
        self._on_message: Optional[Callable] = None
        self._on_connect: Optional[Callable] = None
        self._on_disconnect: Optional[Callable] = None
        self._server_sock = None
        self._client_sock = None
        self._client_info = None

    def set_callbacks(self, on_message=None, on_connect=None, on_disconnect=None):
        self._on_message = on_message
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect

    def _handle_client(self, client_sock, client_addr):
        self._client_sock = client_sock
        self._client_info = client_addr
        if self._on_connect:
            self._on_connect(f"Bluetooth:{client_addr}")
        try:
            while self._running:
                data = client_sock.recv(4096)
                if not data:
                    break
                message = data.decode("utf-8")
                if self._on_message:
                    self._on_message(message, self)
        except Exception:
            pass
        finally:
            self._client_sock = None
            if self._on_disconnect:
                self._on_disconnect(f"Bluetooth:{client_addr}")

    def start(self):
        if not PYBLUEZ_AVAILABLE:
            return "Bluetooth: pybluez not available, install with: pip install pybluez"
        try:
            self._server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self._server_sock.bind(("", bluetooth.PORT_ANY))
            self._server_sock.listen(1)
            bluetooth.advertise_service(
                self._server_sock,
                self._name,
                service_id=self._uuid,
                service_classes=[self._uuid, bluetooth.SERIAL_PORT_CLASS],
                profiles=[bluetooth.SERIAL_PORT_PROFILE],
            )
            self._running = True
            self._thread = threading.Thread(target=self._accept_loop, daemon=True)
            self._thread.start()
            return f"Bluetooth Server '{self._name}' started"
        except Exception as e:
            return f"Bluetooth Error: {e}"

    def _accept_loop(self):
        while self._running:
            try:
                client_sock, client_addr = self._server_sock.accept()
                threading.Thread(
                    target=self._handle_client,
                    args=(client_sock, client_addr),
                    daemon=True
                ).start()
            except Exception:
                if self._running:
                    continue
                break

    def stop(self):
        self._running = False
        try:
            if self._client_sock:
                self._client_sock.close()
            if self._server_sock:
                self._server_sock.close()
        except Exception:
            pass

    async def send(self, message: str):
        if self._client_sock:
            try:
                self._client_sock.send(message.encode("utf-8"))
            except Exception:
                pass

    def is_connected(self) -> bool:
        return self._client_sock is not None
