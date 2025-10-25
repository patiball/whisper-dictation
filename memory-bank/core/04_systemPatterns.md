# System Patterns

## Core Architecture

### Module Organization

```mermaid
graph TB
    Main["whisper-dictation.py<br/>(Main Entry Point)"]

    Main -->|imports| Recorder["Recorder<br/>(Audio Capture)"]
    Main -->|imports| Transcriber["SpeechTranscriber<br/>(Speech-to-Text)"]
    Main -->|imports| StatusBar["StatusBarApp<br/>(macOS GUI)"]
    Main -->|imports| KeyListener["GlobalKeyListener<br/>(Hotkey Binding)"]

    Recorder -->|uses| PyAudio["PyAudio Stream"]
    Transcriber -->|uses| DeviceManager["DeviceManager<br/>(CPU/GPU Selection)"]
    DeviceManager -->|fallback| MPSOptimizer["MPSOptimizer<br/>(M1/M2 Support)"]
    Transcriber -->|loads| WhisperModel["Whisper Model<br/>(PyTorch or C++)"]

    StatusBar -->|triggers| Recorder
    KeyListener -->|notifies| Recorder
    Recorder -->|completed| Transcriber
    Transcriber -->|output| StatusBar

    style Main fill:#4a90e2
    style Recorder fill:#50c878
    style Transcriber fill:#f5a623
    style StatusBar fill:#b8e986
```

## Core Components

### SpeechTranscriber
- **Purpose:** Core transcription engine
- **Responsibilities:** Model loading, device management, text processing
- **Modular Design:** Can be used independently of GUI
- **Supports:** Both Python (PyTorch) and C++ (whisper.cpp) backends

### Recorder
- **Purpose:** Audio capture and processing
- **Responsibilities:** Stream management, buffer handling, warm-up buffers
- **Features:** Auto-fallback on errors, configurable frame size
- **TDD Module:** recorder.py for testing

### StatusBarApp
- **Purpose:** macOS integration and user interface
- **Framework:** Built on `rumps` library
- **Features:** Menu bar application, settings menu
- **Responsibilities:** UI state, user interactions, clipboard management

### Key Listeners
- **GlobalKeyListener:** Generic keyboard shortcut binding
- **DoubleCommandKeyListener:** Specialized double-tap detection
- **Purpose:** Global hotkey activation (works across all applications)

## Application Flow

```mermaid
sequenceDiagram
    participant User
    participant KeyListener
    participant Recorder
    participant SpeechTranscriber
    participant Whisper
    participant Keyboard

    User->>KeyListener: Press hotkey
    KeyListener->>Recorder: start_recording()
    Recorder->>Recorder: Initialize PyAudio stream
    Recorder->>Recorder: Warm-up buffers
    Recorder->>Recorder: Capture audio
    User->>KeyListener: Release hotkey
    KeyListener->>Recorder: stop_recording()
    Recorder->>SpeechTranscriber: transcribe(audio_data)
    SpeechTranscriber->>Whisper: Model inference
    Whisper->>SpeechTranscriber: Text output
    SpeechTranscriber->>Keyboard: Type text
    Keyboard->>User: Text appears in application
```

## Design Patterns

### Observer Pattern
**Classes:** Recorder ↔ SpeechTranscriber
- Recorder captures audio events
- Notifies SpeechTranscriber when recording complete
- Decoupled components, can be tested independently

### Strategy Pattern
**Implementation:** Whisper Model Selection
- Multiple models available: tiny, base, small, medium, large
- User can choose strategy at runtime
- SwappableBackends: Python (PyTorch) vs C++ (whisper.cpp)

### Adapter Pattern
**Implementation:** Device Management
- DeviceManager adapts PyTorch to different hardware (CPU/MPS)
- Transparent fallback for unsupported operations
- Abstract device selection from core logic

## Device Management Flow

```mermaid
graph TD
    App["Application Startup"]
    App -->|test capabilities| TestBasic["Test Basic Tensor Ops"]
    TestBasic -->|PASS| SelectGPU["GPU Available?"]
    TestBasic -->|FAIL| UseCPU1["Use CPU"]

    SelectGPU -->|YES| TestModel["Test Model Load on MPS"]
    SelectGPU -->|NO| UseCPU1

    TestModel -->|PASS| UseMPS["Use MPS (GPU)"]
    TestModel -->|FAIL| Fallback["Fallback to CPU"]

    UseMPS -->|Error during inference| ErrorHandle["Log Error & Fallback"]
    ErrorHandle -->|Operation supported on CPU| UseCPU2["Switch to CPU"]
    ErrorHandle -->|Unrecoverable| ShowError["Show Error Message"]

    UseCPU1 --> Ready["Ready for Transcription"]
    UseCPU2 --> Ready
    UseMPS --> Ready
    ShowError --> Ready

    style UseMPS fill:#50c878
    style UseCPU1 fill:#f5a623
    style UseCPU2 fill:#f5a623
    style Fallback fill:#e74c3c
```

## Code Lifecycle & Maintenance

### Active Components
- **whisper-dictation.py**: Main Python implementation (active)
- **whisper-dictation-fast.py**: C++ implementation via whisper-cli (active)
- **recorder.py**: TDD-compatible module (maintained)
- **transcriber.py**: TDD-compatible wrapper (maintained)

### Obsolete Code Handling
- Old/experimental scripts → `temp/manual_tests/` folder
- Preserved as reference for future automated tests
- Not executed in normal workflows
- Gradually replaced with pytest equivalents
