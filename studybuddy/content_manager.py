import json
from datetime import datetime
from pathlib import Path


class ContentManager:
    """Local storage for notes, flashcards, and quiz outputs."""

    def __init__(self, data_file: str = "studybuddy/data/content_log.json") -> None:
        self.path = Path(data_file)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text(json.dumps({"notes": [], "flashcards": [], "quizzes": []}, indent=2), encoding="utf-8")

    def add_note(self, text: str) -> None:
        payload = self._read()
        payload["notes"].append({"created_at": datetime.now().isoformat(), "text": text})
        self._write(payload)

    def add_flashcards(self, source_text: str, cards: list[dict]) -> None:
        payload = self._read()
        payload["flashcards"].append(
            {"created_at": datetime.now().isoformat(), "source_text": source_text, "cards": cards}
        )
        self._write(payload)

    def _read(self) -> dict:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, payload: dict) -> None:
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
