from studybuddy.webcam_tracker import WebcamTracker


class WebcamService:
    def __init__(self) -> None:
        self.tracker = WebcamTracker()

    def read_frame_and_features(self):
        frame, state, ts = self.tracker.get_state()
        return frame, state, ts

    def close(self) -> None:
        self.tracker.close()
