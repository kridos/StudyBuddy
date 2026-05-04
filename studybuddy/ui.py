from __future__ import annotations


def run() -> None:
    try:
        import tkinter as tk
        from tkinter import messagebox
        import cv2
        from PIL import Image, ImageTk
    except ModuleNotFoundError as exc:
        missing = getattr(exc, "name", "")
        if missing == "_tkinter" or "tkinter" in str(exc).lower():
            print("StudyBuddy AI requires a Python build that includes Tk support.")
            return
        raise

    from .activity_tracker import ActivityTracker
    from .alert_manager import AlertManager
    from .ai_provider import load_provider
    from .content_manager import ContentManager
    from .detection import DistractionDetector
    from .session_manager import SessionManager
    from .webcam_tracker import WebcamTracker

    STATUS_COLORS = {"Focused": "#16a34a", "Distracted": "#dc2626", "Idle": "#6b7280", "Camera unavailable": "#6b7280"}

    class StudyBuddyApp:
        def __init__(self, root: tk.Tk) -> None:
            self.root = root
            self.root.title("StudyBuddy AI")
            self.root.geometry("520x700")
            self.root.configure(bg="#f3f4f6")

            self.session = SessionManager()
            self.alerts = AlertManager(cooldown_seconds=20)
            self.detector = DistractionDetector(missing_face_threshold=10.0, downward_threshold=10.0)
            self.webcam: WebcamTracker | None = None
            self.activity: ActivityTracker | None = None
            self.content = ContentManager()
            self.provider = load_provider()

            self.status_text = tk.StringVar(value="Idle")
            self.timer_text = tk.StringVar(value="00:00")
            self.distraction_text = tk.StringVar(value="Distractions: 0")
            self.content_status = tk.StringVar(value="Ready")
            self.status_label: tk.Label | None = None
            self.video_label: tk.Label | None = None
            self.polling = False

            self._build_ui()

        def _build_ui(self) -> None:
            card = tk.Frame(self.root, bg="white", bd=1, relief="solid")
            card.pack(fill="both", expand=True, padx=12, pady=8)

            tk.Label(card, text="StudyBuddy AI", font=("Helvetica", 20, "bold"), bg="white").pack(padx=12, pady=8)
            tk.Label(card, textvariable=self.timer_text, font=("Helvetica", 30, "bold"), bg="white").pack(padx=12, pady=8)

            self.status_label = tk.Label(card, textvariable=self.status_text, font=("Helvetica", 12), bg="white", fg=STATUS_COLORS["Idle"])
            self.status_label.pack(padx=12, pady=8)

            video_frame = tk.Frame(card, bg="#e5e7eb", bd=1, relief="solid", width=320, height=240)
            video_frame.pack(padx=12, pady=8)
            video_frame.pack_propagate(False)
            self.video_label = tk.Label(video_frame, bg="#000000", width=320, height=240, text="Camera unavailable", fg="white")
            self.video_label.pack()

            tk.Label(card, textvariable=self.distraction_text, font=("Helvetica", 11), bg="white").pack(padx=12, pady=8)

            self.toggle_btn = tk.Button(card, text="Start Session", command=self.toggle_session, bg="#2563eb", fg="white", relief="flat", padx=12, pady=8)
            self.toggle_btn.pack(padx=12, pady=8)

            tk.Label(card, text="Notes", font=("Helvetica", 11, "bold"), bg="white").pack(padx=12, pady=8)
            self.notes_entry = tk.Entry(card, width=48)
            self.notes_entry.pack(padx=12, pady=8)

            row = tk.Frame(card, bg="white")
            row.pack(padx=12, pady=8)
            tk.Button(row, text="Save Note", command=self.save_note, bg="#10b981", fg="white", relief="flat", padx=12, pady=8).pack(side="left", padx=6)
            tk.Button(row, text="Make Flashcards", command=self.make_flashcards, bg="#7c3aed", fg="white", relief="flat", padx=12, pady=8).pack(side="left", padx=6)

            tk.Label(card, textvariable=self.content_status, font=("Helvetica", 10), bg="white", fg="#6b7280").pack(padx=12, pady=8)

        def _set_status(self, status: str) -> None:
            self.status_text.set(status)
            if self.status_label:
                self.status_label.config(fg=STATUS_COLORS.get(status, "#6b7280"))

        def save_note(self) -> None:
            text = self.notes_entry.get().strip()
            if not text:
                self.content_status.set("Enter note text first")
                return
            self.content.add_note(text)
            self.notes_entry.delete(0, tk.END)
            self.content_status.set("✅ Note saved")

        def make_flashcards(self) -> None:
            text = self.notes_entry.get().strip()
            if not text:
                self.content_status.set("Enter text to create flashcards")
                return
            cards = self.provider.generate_flashcards(text)
            self.content.add_flashcards(text, cards)
            self.notes_entry.delete(0, tk.END)
            self.content_status.set(f"✅ Saved {len(cards)} flashcards")

        def toggle_session(self) -> None:
            if not self.session.is_active():
                self.start_session()
            else:
                self.stop_session()

        def start_session(self) -> None:
            self.session.start_session()
            try:
                self.activity = ActivityTracker()
                self.activity.start()
                self.webcam = WebcamTracker()
            except Exception as exc:
                self._set_status("Camera unavailable")
                messagebox.showerror("Startup Error", str(exc))
                self.activity = None
                self.webcam = None
                return

            self.toggle_btn.config(text="Stop Session", bg="#dc2626")
            self._set_status("Focused")
            self.distraction_text.set("Distractions: 0")
            self.polling = True
            self._tick()

        def stop_session(self, show_summary: bool = True) -> None:
            record = self.session.end_session() if self.session.is_active() else None
            self.polling = False
            if self.webcam:
                self.webcam.close()
                self.webcam = None
            if self.activity:
                self.activity.stop()
                self.activity = None
            self.toggle_btn.config(text="Start Session", bg="#2563eb")
            self._set_status("Idle")
            if self.video_label:
                self.video_label.config(image="", text="Camera unavailable")
            if record and show_summary:
                messagebox.showinfo("Session Saved", f"Duration: {record.duration_minutes} min\nDistractions: {record.distraction_events}")

        def on_close(self) -> None:
            self.stop_session(show_summary=False)
            self.root.destroy()

        def _tick(self) -> None:
            if not self.polling:
                return
            try:
                elapsed = self.session.elapsed_seconds()
                mins, secs = divmod(elapsed, 60)
                self.timer_text.set(f"{mins:02d}:{secs:02d}")

                if self.webcam:
                    payload = self.webcam.get_state()
                    if payload is None or payload[0] is None:
                        self._set_status("Camera unavailable")
                        if self.video_label:
                            self.video_label.config(image="", text="Camera unavailable")
                        self.root.after(500, self._tick)
                        return

                    frame, state, now_ts = payload
                    state.idle_seconds = self.activity.idle_seconds() if self.activity else 0.0
                    distracted, _ = self.detector.update(state, now_ts)

                    if distracted:
                        msg = self.alerts.trigger_alert()
                        if msg:
                            self.session.increment_distraction()
                            self.distraction_text.set(f"Distractions: {self.session.distraction_events}")
                        self._set_status("Distracted")
                    else:
                        self._set_status("Focused")

                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = cv2.resize(frame, (320, 240))
                    img = ImageTk.PhotoImage(Image.fromarray(frame))
                    if self.video_label:
                        self.video_label.config(image=img, text="")
                        self.video_label.image = img
            except Exception:
                self._set_status("Camera unavailable")

            self.root.after(500, self._tick)

    root = tk.Tk()
    app = StudyBuddyApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
