import os
import time
from typing import Optional

from .detection import DetectionState

# Reduce MediaPipe/TFLite logging noise.
os.environ.setdefault("GLOG_minloglevel", "2")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")


def _get_facemesh_constructor():
    """Return a FaceMesh constructor compatible with multiple MediaPipe layouts."""
    try:
        import mediapipe as mp  # type: ignore

        solutions = getattr(mp, "solutions", None)
        if solutions and hasattr(solutions, "face_mesh"):
            return solutions.face_mesh.FaceMesh
    except Exception:
        pass

    try:
        from mediapipe.python.solutions.face_mesh import FaceMesh  # type: ignore

        return FaceMesh
    except Exception as exc:
        raise RuntimeError(
            "MediaPipe FaceMesh is unavailable. Reinstall with `pip install mediapipe==0.10.14`."
        ) from exc


class WebcamTracker:
    def __init__(self, camera_index: int = 0) -> None:
        # Lazy import OpenCV to avoid startup crashes on some macOS envs.
        import cv2

        self.cv2 = cv2
        self.cap = self.cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise RuntimeError("Could not open webcam. Check camera permissions or camera index.")

        face_mesh_ctor = _get_facemesh_constructor()
        self.face_mesh = face_mesh_ctor(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def close(self) -> None:
        if self.cap:
            self.cap.release()
        if self.face_mesh:
            self.face_mesh.close()

    def get_state(self) -> Optional[tuple[DetectionState, float]]:
        ok, frame = self.cap.read()
        if not ok:
            return None

        frame_rgb = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2RGB)
        result = self.face_mesh.process(frame_rgb)
        now_ts = time.time()

        if not result.multi_face_landmarks:
            return DetectionState(face_present=False, downward_head=False, looking_away=False), now_ts

        landmarks = result.multi_face_landmarks[0].landmark
        left_eye = landmarks[33]
        right_eye = landmarks[263]
        nose_tip = landmarks[1]

        eye_center_y = (left_eye.y + right_eye.y) / 2.0
        downward_head = (nose_tip.y - eye_center_y) > 0.12

        eye_center_x = (left_eye.x + right_eye.x) / 2.0
        looking_away = abs(nose_tip.x - eye_center_x) > 0.08

        return DetectionState(face_present=True, downward_head=downward_head, looking_away=looking_away), now_ts
