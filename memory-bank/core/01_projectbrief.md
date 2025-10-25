# Project Brief: Whisper Dictation

## Overview

Multilingual dictation application based on OpenAI Whisper ASR models for accurate speech-to-text conversion. Runs in background, triggered via keyboard shortcuts, entirely offline. Features two implementations:

- **Python Version (whisper-dictation.py)**: Production-ready, CPU-only on M1 (MPS incompatibility)
- **C++ Version (whisper-dictation-fast.py)**: Production-ready with M1 GPU support via whisper.cpp (Metal)

## Key Features

- **Offline:** Runs entirely offline, ensuring data privacy.
- **Background Operation:** Runs in the background and is triggered by a keyboard shortcut.
- **Customizable:** Allows users to set their own keyboard combinations, choose from different Whisper models, and select languages.
- **Cross-Platform:** Works on macOS and other platforms.
- **Multilingual:** Supports automatic language detection and transcription in 99+ languages.
- **GPU Accelerated:** C++ version provides Metal Performance Shaders support on M1/M2 Macs.

## Version Comparison

### Python vs C++ Implementation

| Feature | Python (whisper-dictation.py) | C++ (whisper-dictation-fast.py) |
|---------|-------------------------------|----------------------------------|
| **Backend** | PyTorch + Whisper | whisper.cpp (Metal) |
| **GPU Support (M1/M2)** | ❌ CPU only | ✅ GPU-accelerated |
| **Model Format** | PyTorch (.pt) | GGML (.bin) |
| **Model Location** | Auto-downloaded by Whisper | `~/.whisper-models/` |
| **Available Models** | tiny, base, small, medium, large | tiny, base, small, medium, large |
| **Model Sizes** | Varies | 74MB (tiny) → 1.4GB (medium) |
| **Status** | ✅ Production-ready | ✅ Production-ready |
| **Quality Issues** | None | ✅ Fixed (Oct 2025) |
| **Best For** | Intel Macs, accuracy priority | M1/M2 Macs, speed priority |

### Recent Fixes (Oct 2025)

C++ version quality improvements:
- ✅ **Audio Pipeline**: Start sound delayed 0.1s to prevent interference
- ✅ **Language Detection**: Fixed with `-l auto` flag for correct Polish transcription
- ✅ **Translation Mode**: Verified defaults to transcription (not translation)

## Technical Stack

- **Language:** Python 3.10+
- **Speech Recognition:** OpenAI Whisper (PyTorch backend) + whisper.cpp (C++ Metal backend)
- **Audio I/O:** PyAudio for recording
- **GUI:** Rumps for macOS status bar application
- **Keyboard:** Pynput for global hotkey management
- **ML Framework:** PyTorch (Python version), whisper.cpp with Metal (C++ version)
- **Package Manager:** Poetry for Python dependency management
- **Testing:** pytest with coverage and reruns
