import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk

from sensors.webcam_service import WebcamService
from study_engine.engine import StudyEngine


class StudyBuddyApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("StudyBuddy AI")
        self.root.geometry("540x760")
        self.root.configure(bg="#f3f4f6")

        self.engine = StudyEngine()
        self.webcam: WebcamService | None = None
        self.polling = False
        self.debug_mode = tk.BooleanVar(value=False)

        self.status_text = tk.StringVar(value="Idle")
        self.timer_text = tk.StringVar(value="00:00")
        self.score_text = tk.StringVar(value="Focus Score: 0")
        self.distraction_text = tk.StringVar(value="Distractions: 0")
        self.debug_text = tk.StringVar(value="")

        self._build_ui()

    def _build_ui(self):
        card = tk.Frame(self.root, bg="white", bd=1, relief="solid")
        card.pack(fill="both", expand=True, padx=14, pady=12)

        tk.Label(card, text="StudyBuddy AI", font=("Helvetica", 20, "bold"), bg="white").pack(padx=12, pady=8)
        tk.Label(card, textvariable=self.timer_text, font=("Helvetica", 30, "bold"), bg="white").pack(padx=12, pady=8)
        self.status_bar = tk.Label(card, textvariable=self.status_text, font=("Helvetica", 12), bg="#6b7280", fg="white", pady=4)
        self.status_bar.pack(fill="x", padx=12, pady=8)

        frame_wrap = tk.Frame(card, bg="#e5e7eb", bd=1, relief="solid", width=320, height=240)
        frame_wrap.pack(padx=12, pady=8)
        frame_wrap.pack_propagate(False)
        self.video_label = tk.Label(frame_wrap, bg="#000", text="Camera unavailable", fg="white")
        self.video_label.pack(fill="both", expand=True)

        tk.Label(card, textvariable=self.score_text, font=("Helvetica", 11), bg="white").pack(padx=12, pady=4)
        tk.Label(card, textvariable=self.distraction_text, font=("Helvetica", 11), bg="white").pack(padx=12, pady=4)

        row = tk.Frame(card, bg="white")
        row.pack(padx=12, pady=8)
        self.toggle_btn = tk.Button(row, text="Start Session", bg="#2563eb", fg="white", command=self.toggle)
        self.toggle_btn.pack(side="left", padx=6)
        tk.Checkbutton(row, text="Debug Mode", variable=self.debug_mode, bg="white").pack(side="left", padx=6)

        tk.Label(card, textvariable=self.debug_text, font=("Helvetica", 10), bg="white", fg="#6b7280", justify="left").pack(padx=12, pady=8)

    def toggle(self):
        if not self.engine.session.is_active():
            self.start()
        else:
            self.stop()

    def start(self):
        try:
            self.webcam = WebcamService()
            self.engine.start()
            self.polling = True
            self.toggle_btn.config(text="Stop Session", bg="#dc2626")
            self.loop()
        except Exception as e:
            messagebox.showerror("Startup Error", str(e))

    def stop(self):
        rec = self.engine.stop()
        self.polling = False
        if self.webcam:
            self.webcam.close()
            self.webcam = None
        self.toggle_btn.config(text="Start Session", bg="#2563eb")
        if rec:
            messagebox.showinfo("Session Saved", f"Duration: {rec.duration_minutes} min\nDistractions: {rec.distraction_events}")

    def loop(self):
        if not self.polling:
            return
        try:
            frame, features, ts = self.webcam.read_frame_and_features() if self.webcam else (None, None, 0)
            state = self.engine.update(features, ts)
            mins, secs = divmod(state.session_seconds, 60)
            self.timer_text.set(f"{mins:02d}:{secs:02d}")
            self.status_text.set(state.focus_status)
            self.score_text.set(f"Focus Score: {state.focus_score}")
            self.distraction_text.set(f"Distractions: {state.distractions}")
            colors = {"Focused": "#16a34a", "Distracted": "#dc2626", "Idle": "#6b7280", "Camera unavailable": "#6b7280"}
            self.status_bar.config(bg=colors.get(state.focus_status, "#6b7280"))

            if frame is not None:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgb = cv2.resize(rgb, (320, 240))
                img = ImageTk.PhotoImage(Image.fromarray(rgb))
                self.video_label.config(image=img, text="")
                self.video_label.image = img
            else:
                self.video_label.config(image="", text="Camera unavailable")

            self.debug_text.set(str(state.debug) if self.debug_mode.get() else "")
        except Exception:
            self.status_text.set("Camera unavailable")
        self.root.after(500, self.loop)


def run() -> None:
    root = tk.Tk()
    app = StudyBuddyApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop(), root.destroy()))
    root.mainloop()
