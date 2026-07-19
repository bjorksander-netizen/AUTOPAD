"""AUTOPAD Clipboard Monitor - Bidirectional Clipboard Sync"""

import time
import threading
import pyperclip
from typing import Callable, Optional


class ClipboardMonitor:
    def __init__(self, poll_interval: float = 0.25, max_length: int = 10000):
        self._poll_interval = poll_interval
        self._max_length = max_length
        self._last_clipboard = ""
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._on_change: Optional[Callable] = None
        self._enabled = True

    def set_callback(self, callback: Callable):
        self._on_change = callback

    def set_enabled(self, enabled: bool):
        self._enabled = enabled

    def is_enabled(self) -> bool:
        return self._enabled

    def get_clipboard(self) -> str:
        try:
            text = pyperclip.paste()
            if len(text) > self._max_length:
                return text[:self._max_length]
            return text
        except Exception:
            return ""

    def set_clipboard(self, text: str):
        try:
            pyperclip.copy(text)
            self._last_clipboard = text
        except Exception:
            pass

    def _poll_loop(self):
        while self._running:
            if self._enabled:
                try:
                    current = pyperclip.paste()
                    if current != self._last_clipboard and current:
                        self._last_clipboard = current
                        if self._on_change:
                            self._on_change(current)
                except Exception:
                    pass
            time.sleep(self._poll_interval)

    def start(self):
        if self._running:
            return
        self._running = True
        self._last_clipboard = self.get_clipboard()
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None
