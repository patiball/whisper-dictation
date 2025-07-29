# Technical Context

## Dependencies

- **Python:** 3.10+ (as per `pyproject.toml`)
- **Poetry:** Used for dependency management.
- **PyAudio:** For audio recording.
- **OpenAI Whisper:** The core speech-to-text engine.
- **Rumps:** For the macOS status bar application.
- **Pynput:** For global hotkey management.
- **PyTorch:** For the Whisper model.

## Setup

1.  **Install Prerequisites:** `brew install portaudio llvm`
2.  **Clone Repository:** `git clone https://github.com/foges/whisper-dictation.git`
3.  **Install Dependencies:** `poetry install`

## Running the Application

- **Run:** `python whisper-dictation.py`
- **Customization:** The application can be customized with command-line arguments for the model, language, and keyboard shortcuts.
