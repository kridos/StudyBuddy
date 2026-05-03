import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class SessionRecord:
    date: str
    duration_minutes: int
    distraction_events: int


class SessionManager:
    def __init__(self, data_file: str = "studybuddy/data/sessions.json") -> None:
        self.data_path = Path(data_file)
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.distraction_events: int = 0

        if not self.data_path.exists():
            self.data_path.write_text("[]", encoding="utf-8")

    def start_session(self) -> None:
        self.start_time = datetime.now()
        self.end_time = None
        self.distraction_events = 0

    def increment_distraction(self) -> None:
        self.distraction_events += 1

    def is_active(self) -> bool:
        return self.start_time is not None and self.end_time is None

    def elapsed_seconds(self) -> int:
        if not self.start_time:
            return 0
        end_ref = self.end_time or datetime.now()
        return int((end_ref - self.start_time).total_seconds())

    def end_session(self) -> Optional[SessionRecord]:
        if not self.start_time:
            return None

        self.end_time = datetime.now()
        duration_minutes = int(self.elapsed_seconds() / 60)

        record = SessionRecord(
            date=self.start_time.isoformat(),
            duration_minutes=duration_minutes,
            distraction_events=self.distraction_events,
        )

        existing = self._read_records()
        existing.append(record.__dict__)
        self.data_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")

        return record

    def _read_records(self) -> list:
        try:
            raw = self.data_path.read_text(encoding="utf-8")
            return json.loads(raw)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
