import time


class ActivityTracker:
    """Safe stub tracker: avoids OS-level input hooks for cross-platform stability."""

    def __init__(self) -> None:
        self.last_input_ts = time.time()

    def start(self) -> None:
        # Intentionally no-op (no global input listeners).
        return

    def stop(self) -> None:
        return

    def idle_seconds(self) -> float:
        return 0.0
