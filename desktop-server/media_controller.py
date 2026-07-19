"""AUTOPAD Media Controller - Windows Audio & Media Keys"""

import ctypes
from ctypes import wintypes

try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL
    PYCAW_AVAILABLE = True
except ImportError:
    PYCAW_AVAILABLE = False


class MediaController:
    VK_MEDIA_PLAY_PAUSE = 0xB3
    VK_MEDIA_NEXT_TRACK = 0xB0
    VK_MEDIA_PREV_TRACK = 0xB1
    VK_MEDIA_STOP = 0xB2
    VK_VOLUME_UP = 0xAF
    VK_VOLUME_DOWN = 0xAE
    VK_VOLUME_MUTE = 0xAD

    KEYEVENTF_KEYUP = 0x0002
    KEYEVENTF_EXTENDEDKEY = 0x0001

    def __init__(self):
        self.user32 = ctypes.windll.user32

    def _send_key(self, vk_code: int):
        self.user32.keybd_event(vk_code, 0, self.KEYEVENTF_EXTENDEDKEY, 0)
        self.user32.keybd_event(vk_code, 0, self.KEYEVENTF_EXTENDEDKEY | self.KEYEVENTF_KEYUP, 0)

    def play_pause(self):
        self._send_key(self.VK_MEDIA_PLAY_PAUSE)

    def next_track(self):
        self._send_key(self.VK_MEDIA_NEXT_TRACK)

    def previous_track(self):
        self._send_key(self.VK_MEDIA_PREV_TRACK)

    def stop(self):
        self._send_key(self.VK_MEDIA_STOP)

    def volume_up(self):
        self._send_key(self.VK_VOLUME_UP)

    def volume_down(self):
        self._send_key(self.VK_VOLUME_DOWN)

    def volume_mute(self):
        self._send_key(self.VK_VOLUME_MUTE)

    def volume_set(self, level: int):
        if not PYCAW_AVAILABLE:
            return
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            normalized = max(0.0, min(1.0, level / 100.0))
            volume.SetMasterVolumeLevelScalar(normalized, None)
        except Exception:
            pass

    def get_volume(self) -> int:
        if not PYCAW_AVAILABLE:
            return 50
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            scalar = volume.GetMasterVolumeLevelScalar()
            return int(scalar * 100)
        except Exception:
            return 50

    def is_muted(self) -> bool:
        if not PYCAW_AVAILABLE:
            return False
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            return volume.GetMute()
        except Exception:
            return False
