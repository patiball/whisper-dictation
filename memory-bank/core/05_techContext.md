# Technical Context

## Target Environment

- OS: Windows 11
- Python: 3.10+ (recommended: 3.11)
- Audio stack: PortAudio + PyAudio
- ASR runtime: `openai-whisper` (Python path for MVP)

## Current Dependencies (Relevant to MVP)

- `openai-whisper`
- `torch`
- `pyaudio`
- `pynput`
- `keyboard`
- tray icon library to be selected in implementation (`pystray` candidate)

## Operational Constraints

- Global hotkeys may be affected by keyboard layout and app privilege level.
- First-run model download requires internet and enough disk space.
- `medium` model is large; startup/download time must be expected.

## Practical Run Shape (Windows)

1. Create/activate venv.
2. Install Python dependencies.
3. Start app with hotkey configuration and `-m medium`.
4. App remains visible via tray icon and can toggle recording.
