from __future__ import annotations


def run() -> None:
    """Run the app with Tkinter if available, otherwise print setup guidance."""
    try:
        import tkinter as tk
        from tkinter import messagebox
        import cv2
    except ModuleNotFoundError as exc:
        missing = getattr(exc, "name", "")
        if missing == "_tkinter" or "tkinter" in str(exc).lower():
            print("StudyBuddy AI requires a Python build that includes Tk support.")
            print("Detected missing module: _tkinter")
            print("\nmacOS quick fix options:")
            print("1) Install python.org Python (includes Tk) and recreate your venv.")
            print("2) If using Homebrew Python, install Tcl/Tk and rebuild/reinstall Python with Tk support.")
            print("\nThen run: python main.py")
            return
        raise

    from .alert_manager import AlertManager
    from .detection import DistractionDetector
    from .session_manager import SessionManager
    from .webcam_tracker import WebcamTracker

    class StudyBuddyApp:
        def __init__(self, root: tk.Tk) -> None:
            self.root = root
            self.root.title("StudyBuddy AI")
            self.root.geometry("320x220")

            self.session = SessionManager()
            self.alerts = AlertManager(cooldown_seconds=20)
            self.detector = DistractionDetector(missing_face_threshold=10.0, downward_threshold=10.0)
            self.webcam: WebcamTracker | None = None

            self.status_text = tk.StringVar(value="Idle")
            self.timer_text = tk.StringVar(value="00:00")
            self.distraction_text = tk.StringVar(value="Distractions: 0")

            self._build_ui()
            self.polling = False

        def _build_ui(self) -> None:
            tk.Label(self.root, text="StudyBuddy AI", font=("Arial", 16, "bold")).pack(pady=8)
            tk.Label(self.root, textvariable=self.timer_text, font=("Arial", 18)).pack(pady=4)
            tk.Label(self.root, textvariable=self.status_text, font=("Arial", 12)).pack(pady=4)
            tk.Label(self.root, textvariable=self.distraction_text, font=("Arial", 11)).pack(pady=2)
            self.toggle_btn = tk.Button(self.root, text="Start Session", command=self.toggle_session)
            self.toggle_btn.pack(pady=12)

        def toggle_session(self) -> None:
            if not self.session.is_active():
                self.start_session()
            else:
                self.stop_session()

        def start_session(self) -> None:
            self.session.start_session()
            try:
                self.webcam = WebcamTracker()
            except Exception as exc:
                self.status_text.set("Idle")
                messagebox.showerror("Webcam Error", str(exc))
                return

            self.toggle_btn.config(text="Stop Session")
            self.status_text.set("Focused")
            self.distraction_text.set("Distractions: 0")
            self.polling = True
            self._tick()

        def stop_session(self, show_summary: bool = True) -> None:
            record = self.session.end_session() if self.session.is_active() else None
            self.polling = False
            if self.webcam:
                self.webcam.close()
                self.webcam = None
            cv2.destroyAllWindows()

            self.toggle_btn.config(text="Start Session")
            self.status_text.set("Idle")
            if record and show_summary:
                messagebox.showinfo("Session Saved", f"Duration: {record.duration_minutes} min\nDistractions: {record.distraction_events}")

        def on_close(self) -> None:
            self.stop_session(show_summary=False)
            self.root.destroy()

        def _tick(self) -> None:
            if not self.polling:
                return
            elapsed = self.session.elapsed_seconds()
            mins, secs = divmod(elapsed, 60)
            self.timer_text.set(f"{mins:02d}:{secs:02d}")

            if self.webcam:
                payload = self.webcam.get_state()
                if payload:
                    state, now_ts = payload
                    distracted, reason = self.detector.update(state, now_ts)
                    if distracted:
                        msg = self.alerts.trigger_alert()
                        if msg:
                            self.session.increment_distraction()
                            self.distraction_text.set(f"Distractions: {self.session.distraction_events}")
                        self.status_text.set("Distracted")
                    else:
                        self.status_text.set("Focused")
                    self.webcam.preview_frame(self.status_text.get())
                else:
                    self.status_text.set("Distracted")

            self.root.after(500, self._tick)

    root = tk.Tk()
    app = StudyBuddyApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
