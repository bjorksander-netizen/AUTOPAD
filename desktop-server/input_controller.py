"""AUTOPAD Input Controller - Mouse & Keyboard Simulation"""

import pyautogui
import time
from typing import Optional


class InputController:
    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0
        self._mouse_sensitivity = 1.0
        self._scroll_sensitivity = 1.0

    def set_sensitivity(self, mouse: float = 1.0, scroll: float = 1.0):
        self._mouse_sensitivity = mouse
        self._scroll_sensitivity = scroll

    def mouse_move(self, delta_x: int, delta_y: int):
        dx = int(delta_x * self._mouse_sensitivity)
        dy = int(delta_y * self._mouse_sensitivity)
        pyautogui.moveRel(dx, dy, _pause=False)

    def mouse_click(self, button: str = "left"):
        pyautogui.click(button=button, _pause=False)

    def mouse_double_click(self, button: str = "left"):
        pyautogui.doubleClick(button=button, _pause=False)

    def mouse_scroll(self, delta: int):
        scroll_amount = int(delta * self._scroll_sensitivity)
        pyautogui.scroll(scroll_amount, _pause=False)

    def mouse_down(self, button: str = "left"):
        pyautogui.mouseDown(button=button, _pause=False)

    def mouse_up(self, button: str = "left"):
        pyautogui.mouseUp(button=button, _pause=False)

    def key_press(self, key: str):
        try:
            pyautogui.press(key, _pause=False)
        except Exception:
            pass

    def key_down(self, key: str):
        try:
            pyautogui.keyDown(key, _pause=False)
        except Exception:
            pass

    def key_up(self, key: str):
        try:
            pyautogui.keyUp(key, _pause=False)
        except Exception:
            pass

    def key_combo(self, keys: list):
        try:
            pyautogui.hotkey(*keys, _pause=False)
        except Exception:
            pass

    def key_text(self, text: str):
        try:
            pyautogui.typewrite(text, interval=0, _pause=False)
        except Exception:
            for char in text:
                try:
                    pyautogui.press(char, _pause=False)
                except Exception:
                    pass

    def get_screen_size(self) -> tuple:
        return pyautogui.size()
