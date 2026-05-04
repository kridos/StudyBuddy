from .focus_score import compute_focus_score
from .state import AppState
from studybuddy.detection import DistractionDetector
from studybuddy.session_manager import SessionManager


class StudyEngine:
    def __init__(self) -> None:
        self.session = SessionManager()
        self.detector = DistractionDetector(missing_face_threshold=10.0, downward_threshold=10.0)
        self.state = AppState(debug={})

    def start(self) -> None:
        self.session.start_session()
        self.state.focus_status = "Focused"

    def stop(self):
        rec = self.session.end_session() if self.session.is_active() else None
        self.state.focus_status = "Idle"
        return rec

    def update(self, sensor_state, now_ts: float) -> AppState:
        self.state.session_seconds = self.session.elapsed_seconds()
        if sensor_state is None:
            self.state.focus_status = "Camera unavailable"
            self.state.focus_score = 0
            return self.state

        distracted, reason = self.detector.update(sensor_state, now_ts)
        if distracted:
            self.state.focus_status = "Distracted"
            self.session.increment_distraction()
        else:
            self.state.focus_status = "Focused"

        self.state.distractions = self.session.distraction_events
        self.state.focus_score = compute_focus_score(
            self.session.is_active(),
            sensor_state.face_present,
            sensor_state.looking_away,
            distracted,
        )
        self.state.debug = {
            "face_present": sensor_state.face_present,
            "looking_away": sensor_state.looking_away,
            "downward_head": sensor_state.downward_head,
            "reason": reason,
        }
        return self.state
