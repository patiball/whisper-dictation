# Technical Context

## Dependencies

- **Python:** 3.10+ (as per `pyproject.toml`)
- **Poetry:** Used for dependency management.
- **PyAudio:** For audio recording.
- **OpenAI Whisper:** The core speech-to-text engine.
- **Rumps:** For the macOS status bar application.
- **Pynput:** For global hotkey management.
- **PyTorch:** For the Whisper model.

## Project Repository Status

This project is a **fork** of the original whisper-dictation project:
- **Original Repository:** https://github.com/foges/whisper-dictation
- **Our Fork:** https://github.com/patiball/whisper-dictation
- **Fork configured:** 2025-01-29

### Git Configuration
- `origin` remote → Our fork: https://github.com/patiball/whisper-dictation
- `upstream` remote → Original: https://github.com/foges/whisper-dictation
- Authentication configured with Personal Access Token

## Setup

1.  **Install Prerequisites:** `brew install portaudio llvm`
2.  **Clone Repository:** `git clone https://github.com/patiball/whisper-dictation.git`
3.  **Install Dependencies:** `poetry install`

## Running the Application

- **Run:** `python whisper-dictation.py`
- **Customization:** The application can be customized with command-line arguments for the model, language, and keyboard shortcuts.
