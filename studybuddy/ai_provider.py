import os
from dataclasses import dataclass
from typing import Protocol


class StudyContentProvider(Protocol):
    def generate_flashcards(self, text: str) -> list[dict]:
        ...


@dataclass
class LocalProvider:
    def generate_flashcards(self, text: str) -> list[dict]:
        words = [w.strip('.,!?') for w in text.split() if len(w.strip('.,!?')) > 4]
        unique = []
        for w in words:
            lw = w.lower()
            if lw not in unique:
                unique.append(lw)
            if len(unique) == 3:
                break
        return [{"question": f"Define: {w}", "answer": "(Fill this in while reviewing)"} for w in unique] or [
            {"question": "Main idea?", "answer": "Write a concise summary."}
        ]


@dataclass
class ClaudeProvider:
    api_key: str

    def generate_flashcards(self, text: str) -> list[dict]:
        # Placeholder integration point to keep MVP local-first by default.
        # If enabled, this should call Anthropic API and parse structured JSON output.
        return [{
            "question": "Claude provider configured",
            "answer": "Implement remote call in a future secure integration step.",
        }]


def load_provider() -> StudyContentProvider:
    api_key = os.getenv("CLAUDE_API_KEY", "").strip()
    if api_key:
        return ClaudeProvider(api_key=api_key)
    return LocalProvider()
