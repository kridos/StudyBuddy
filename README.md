# StudyBuddy AI (MVP)

Local-first desktop app to track study sessions and detect basic distraction via webcam.

## Features (MVP)

- Start/stop study sessions
- Local JSON session logging with:
  - date
  - duration_minutes
  - distraction_events
- Webcam monitoring with MediaPipe:
  - face present / missing
  - simple head-down heuristic
- Distraction alerts with cooldown and randomized messages
- Minimal Tkinter UI showing:
  - session timer
  - focused/distracted status
  - live distraction counter

## Project Structure

- `main.py` - app entrypoint
- `studybuddy/session_manager.py` - session lifecycle + JSON storage
- `studybuddy/webcam_tracker.py` - OpenCV + MediaPipe state extraction
- `studybuddy/detection.py` - distraction heuristics
- `studybuddy/alert_manager.py` - alert randomization + cooldown
- `studybuddy/ui.py` - Tkinter app and Tk fallback guidance
- `studybuddy/data/sessions.json` - generated session storage

## Run Locally

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start app:

```bash
python main.py
```

## Important: Tkinter on macOS/Linux

- `tkinter` is **not** installed from pip (`pip install tk` / `pip install tkinter` will not fix `_tkinter`).
- Tkinter is part of your **Python build**.
- If you get `ModuleNotFoundError: No module named '_tkinter'`, install a Python distribution that includes Tk (for example python.org installer on macOS), then recreate your venv and reinstall requirements.

## Notes

- This MVP runs fully local (no cloud APIs).
- Alert playback defaults to console messages unless you pass a sound file path into `AlertManager`.
- Webcam is active only during a running session.
- MediaPipe is pinned to `0.10.14` because newer/incompatible environment builds may not expose `mediapipe.solutions` consistently.



## Notes / Flashcards Logging

- Use the in-app input to save notes and generate placeholder flashcards.
- All generated content is stored locally in `studybuddy/data/content_log.json`.
- No cloud dependency is required for this logging flow.

## Optional .env for API keys

- If you later add non-local providers (e.g., Claude), place keys in a local `.env` file.
- `.env` is git-ignored; use `.env.example` as the template.
