import time
from pynput import keyboard, mouse


class ActivityTracker:
    def __init__(self) -> None:
        self.last_input_ts = time.time()
        self._mouse_listener = mouse.Listener(on_move=self._touch, on_click=self._touch, on_scroll=self._touch)
        self._keyboard_listener = keyboard.Listener(on_press=self._touch)

    def start(self) -> None:
        self._mouse_listener.start()
        self._keyboard_listener.start()

    def stop(self) -> None:
        self._mouse_listener.stop()
        self._keyboard_listener.stop()

    def _touch(self, *args, **kwargs):
        self.last_input_ts = time.time()

    def idle_seconds(self) -> float:
        return time.time() - self.last_input_ts
