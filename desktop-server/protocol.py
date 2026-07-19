"""AUTOPAD Communication Protocol"""

import json
import time
from enum import Enum
from typing import Any, Optional


class MessageType(str, Enum):
    # Mouse
    MOUSE_MOVE = "MOUSE_MOVE"
    MOUSE_CLICK = "MOUSE_CLICK"
    MOUSE_DOUBLE_CLICK = "MOUSE_DOUBLE_CLICK"
    MOUSE_SCROLL = "MOUSE_SCROLL"
    MOUSE_DOWN = "MOUSE_DOWN"
    MOUSE_UP = "MOUSE_UP"

    # Keyboard
    KEY_PRESS = "KEY_PRESS"
    KEY_RELEASE = "KEY_RELEASE"
    KEY_COMBO = "KEY_COMBO"
    KEY_TEXT = "KEY_TEXT"

    # Media
    MEDIA_PLAY_PAUSE = "MEDIA_PLAY_PAUSE"
    MEDIA_NEXT = "MEDIA_NEXT"
    MEDIA_PREVIOUS = "MEDIA_PREVIOUS"
    MEDIA_STOP = "MEDIA_STOP"
    VOLUME_UP = "VOLUME_UP"
    VOLUME_DOWN = "VOLUME_DOWN"
    VOLUME_SET = "VOLUME_SET"
    VOLUME_MUTE = "VOLUME_MUTE"

    # Clipboard
    CLIPBOARD_SYNC = "CLIPBOARD_SYNC"
    CLIPBOARD_PUSH = "CLIPBOARD_PUSH"
    CLIPBOARD_PULL = "CLIPBOARD_PULL"
    CLIPBOARD_CHANGED = "CLIPBOARD_CHANGED"

    # System
    PING = "PING"
    PONG = "PONG"
    CONNECT = "CONNECT"
    DISCONNECT = "DISCONNECT"
    DEVICE_INFO = "DEVICE_INFO"


class Message:
    def __init__(self, msg_type: str, data: Optional[dict] = None):
        self.type = msg_type
        self.data = data or {}
        self.timestamp = int(time.time() * 1000)

    def to_json(self) -> str:
        return json.dumps({
            "type": self.type,
            "data": self.data,
            "timestamp": self.timestamp
        })

    @classmethod
    def from_json(cls, json_str: str) -> "Message":
        try:
            obj = json.loads(json_str)
            return cls(
                msg_type=obj.get("type", ""),
                data=obj.get("data", {})
            )
        except (json.JSONDecodeError, KeyError):
            return None

    @staticmethod
    def create(msg_type: str, **kwargs) -> "Message":
        return Message(msg_type, kwargs)

    @staticmethod
    def pong() -> "Message":
        return Message(MessageType.PONG)

    @staticmethod
    def ping() -> "Message":
        return Message(MessageType.PING)

    @staticmethod
    def connect(device_info: dict) -> "Message":
        return Message(MessageType.CONNECT, {"device_info": device_info})

    @staticmethod
    def disconnect() -> "Message":
        return Message(MessageType.DISCONNECT)

    @staticmethod
    def clipboard_sync(content: str, source: str, content_type: str = "text") -> "Message":
        return Message(MessageType.CLIPBOARD_SYNC, {
            "content": content,
            "source": source,
            "content_type": content_type
        })

    @staticmethod
    def clipboard_changed(content: str, source: str) -> "Message":
        return Message(MessageType.CLIPBOARD_CHANGED, {
            "content": content,
            "source": source
        })

    @staticmethod
    def mouse_move(delta_x: int, delta_y: int) -> "Message":
        return Message(MessageType.MOUSE_MOVE, {"delta_x": delta_x, "delta_y": delta_y})

    @staticmethod
    def mouse_click(button: str = "left") -> "Message":
        return Message(MessageType.MOUSE_CLICK, {"button": button})

    @staticmethod
    def mouse_double_click(button: str = "left") -> "Message":
        return Message(MessageType.MOUSE_DOUBLE_CLICK, {"button": button})

    @staticmethod
    def mouse_scroll(delta: int) -> "Message":
        return Message(MessageType.MOUSE_SCROLL, {"delta": delta})

    @staticmethod
    def mouse_down(button: str = "left") -> "Message":
        return Message(MessageType.MOUSE_DOWN, {"button": button})

    @staticmethod
    def mouse_up(button: str = "left") -> "Message":
        return Message(MessageType.MOUSE_UP, {"button": button})

    @staticmethod
    def key_press(key: str) -> "Message":
        return Message(MessageType.KEY_PRESS, {"key": key})

    @staticmethod
    def key_release(key: str) -> "Message":
        return Message(MessageType.KEY_RELEASE, {"key": key})

    @staticmethod
    def key_combo(keys: list) -> "Message":
        return Message(MessageType.KEY_COMBO, {"keys": keys})

    @staticmethod
    def key_text(text: str) -> "Message":
        return Message(MessageType.KEY_TEXT, {"text": text})

    @staticmethod
    def media_play_pause() -> "Message":
        return Message(MessageType.MEDIA_PLAY_PAUSE)

    @staticmethod
    def media_next() -> "Message":
        return Message(MessageType.MEDIA_NEXT)

    @staticmethod
    def media_previous() -> "Message":
        return Message(MessageType.MEDIA_PREVIOUS)

    @staticmethod
    def media_stop() -> "Message":
        return Message(MessageType.MEDIA_STOP)

    @staticmethod
    def volume_up() -> "Message":
        return Message(MessageType.VOLUME_UP)

    @staticmethod
    def volume_down() -> "Message":
        return Message(MessageType.VOLUME_DOWN)

    @staticmethod
    def volume_set(level: int) -> "Message":
        return Message(MessageType.VOLUME_SET, {"level": level})

    @staticmethod
    def volume_mute() -> "Message":
        return Message(MessageType.VOLUME_MUTE)

    @staticmethod
    def device_info(info: dict) -> "Message":
        return Message(MessageType.DEVICE_INFO, info)

    def __repr__(self):
        return f"Message(type={self.type}, data={self.data})"
