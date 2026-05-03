from dataclasses import dataclass
from typing import Optional


@dataclass
class DetectionState:
    face_present: bool
    downward_head: bool
    looking_away: bool = False
    idle_seconds: float = 0.0


class DistractionDetector:
    def __init__(
        self,
        missing_face_threshold: float = 10.0,
        downward_threshold: float = 10.0,
        away_threshold: float = 6.0,
        idle_threshold: float = 20.0,
    ) -> None:
        self.missing_face_threshold = missing_face_threshold
        self.downward_threshold = downward_threshold
        self.away_threshold = away_threshold
        self.idle_threshold = idle_threshold

        self._missing_since: Optional[float] = None
        self._downward_since: Optional[float] = None
        self._away_since: Optional[float] = None

    def update(self, state: DetectionState, now_ts: float) -> tuple[bool, str]:
        reason = ""
        distracted = False

        if not state.face_present:
            if self._missing_since is None:
                self._missing_since = now_ts
            elif now_ts - self._missing_since > self.missing_face_threshold:
                distracted = True
                reason = "face_missing"
        else:
            self._missing_since = None

        if state.downward_head:
            if self._downward_since is None:
                self._downward_since = now_ts
            elif now_ts - self._downward_since > self.downward_threshold:
                distracted = True
                reason = reason or "head_down"
        else:
            self._downward_since = None

        if state.looking_away:
            if self._away_since is None:
                self._away_since = now_ts
            elif now_ts - self._away_since > self.away_threshold:
                distracted = True
                reason = reason or "looking_away"
        else:
            self._away_since = None

        if state.idle_seconds > self.idle_threshold:
            distracted = True
            reason = reason or "idle"

        return distracted, reason
