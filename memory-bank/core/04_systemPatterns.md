# System Patterns

## Core Components

- **SpeechTranscriber:** This class is the core of the application, responsible for loading the Whisper model and performing the transcription. It's designed to be modular and can be used independently of the GUI.

- **Recorder:** This class handles the audio recording functionality. It uses PyAudio to capture audio from the microphone and provides methods to start and stop recording.

- **StatusBarApp:** This class, built on the `rumps` library, creates the user interface for the application on macOS. It provides a menu for changing settings and quitting the app.

- **Key Listeners:** The `GlobalKeyListener` and `DoubleCommandKeyListener` classes are responsible for listening for global keyboard shortcuts to trigger the dictation.

## Design Patterns

- **Observer Pattern:** The `Recorder` and `SpeechTranscriber` classes work together in a way that resembles the Observer pattern. The `Recorder` records the audio, and then the `SpeechTranscriber` is notified to transcribe it.

- **Strategy Pattern:** The use of different Whisper models (tiny, base, medium, etc.) can be seen as a form of the Strategy pattern. The user can choose which model to use, and the `SpeechTranscriber` will use that model to perform the transcription.
