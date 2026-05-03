import os
import time
from typing import Optional

import cv2

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
        self.cap = cv2.VideoCapture(camera_index)
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
        self.last_frame = None

    def close(self) -> None:
        if self.cap:
            self.cap.release()
        if self.face_mesh:
            self.face_mesh.close()

    def get_state(self) -> Optional[tuple[DetectionState, float]]:
        ok, frame = self.cap.read()
        if not ok:
            return None

        self.last_frame = frame.copy()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.face_mesh.process(frame_rgb)
        now_ts = time.time()

        if not result.multi_face_landmarks:
            return DetectionState(face_present=False, downward_head=False), now_ts

        landmarks = result.multi_face_landmarks[0].landmark
        left_eye = landmarks[33]
        right_eye = landmarks[263]
        nose_tip = landmarks[1]

        eye_center_y = (left_eye.y + right_eye.y) / 2.0
        downward_head = (nose_tip.y - eye_center_y) > 0.12

        return DetectionState(face_present=True, downward_head=downward_head), now_ts

    def preview_frame(self, status_text: str) -> None:
        if self.last_frame is None:
            return
        frame = self.last_frame.copy()
        cv2.putText(frame, f"Status: {status_text}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow("StudyBuddy Webcam", frame)
        cv2.waitKey(1)
