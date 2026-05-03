import random
import threading
import time


class AlertManager:
    def __init__(self, cooldown_seconds: int = 20, sound_file: str | None = None) -> None:
        self.cooldown_seconds = cooldown_seconds
        self.sound_file = sound_file
        self.last_alert_ts = 0.0
        self.messages = [
            "Get back to work.",
            "You're distracted.",
            "Stay focused.",
            "Eyes on the task.",
        ]

    def can_alert(self) -> bool:
        return time.time() - self.last_alert_ts >= self.cooldown_seconds

    def trigger_alert(self) -> str | None:
        if not self.can_alert():
            return None

        self.last_alert_ts = time.time()
        message = random.choice(self.messages)

        if self.sound_file:
            try:
                from playsound import playsound

                threading.Thread(target=playsound, args=(self.sound_file,), daemon=True).start()
            except Exception:
                print(f"ALERT: {message}")
        else:
            print(f"ALERT: {message}")

        return message
