from dataclasses import dataclass


@dataclass
class AppState:
    focus_status: str = "Idle"
    focus_score: int = 0
    distractions: int = 0
    session_seconds: int = 0
    debug: dict | None = None
