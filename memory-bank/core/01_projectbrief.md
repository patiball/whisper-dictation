# Project Brief: Whisper Dictation

This project is a multilingual dictation application based on the OpenAI Whisper ASR model. It provides accurate and efficient speech-to-text conversion in any application.

## Key Features

- **Offline:** Runs entirely offline, ensuring data privacy.
- **Background Operation:** Runs in the background and is triggered by a keyboard shortcut.
- **Customizable:** Allows users to set their own keyboard combinations, choose from different Whisper models, and select languages.
- **Cross-Platform:** Works on macOS and other platforms.

## Technical Stack

- **Python:** The core application is written in Python.
- **OpenAI Whisper:** The speech-to-text engine.
- **PyAudio:** For audio recording.
- **Rumps:** For the macOS status bar application.
- **Pynput:** For global hotkey management.
- **PyTorch:** For the Whisper model.
- **Poetry:** For dependency management.
