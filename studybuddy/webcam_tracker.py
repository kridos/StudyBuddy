import time
from typing import Optional

import cv2
import mediapipe as mp

from .detection import DetectionState


class WebcamTracker:
    def __init__(self, camera_index: int = 0) -> None:
        self.cap = cv2.VideoCapture(camera_index)
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def close(self) -> None:
        if self.cap:
            self.cap.release()
        self.face_mesh.close()

    def get_state(self) -> Optional[tuple[DetectionState, float]]:
        ok, frame = self.cap.read()
        if not ok:
            return None

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.face_mesh.process(frame_rgb)
        now_ts = time.time()

        if not result.multi_face_landmarks:
            return DetectionState(face_present=False, downward_head=False), now_ts

        landmarks = result.multi_face_landmarks[0].landmark
        # Simple head-down approximation using relative y positions:
        # if nose tip is significantly lower than eye center, we consider it downward tilt.
        left_eye = landmarks[33]
        right_eye = landmarks[263]
        nose_tip = landmarks[1]

        eye_center_y = (left_eye.y + right_eye.y) / 2.0
        downward_head = (nose_tip.y - eye_center_y) > 0.12

        return DetectionState(face_present=True, downward_head=downward_head), now_ts
