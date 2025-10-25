# Technical Context

## System Requirements

- **Operating System:** macOS (primary), Linux/Windows (experimental)
- **Python:** 3.10+ (as per `pyproject.toml`)
- **System Dependencies:** portaudio, llvm

## Dependencies

### Core Libraries
- **Poetry:** Dependency management
- **PyAudio:** Audio recording and device management
- **OpenAI Whisper:** Speech-to-text engine (Python version)
- **whisper.cpp:** Optimized Whisper implementation with Metal support (C++ version)
- **Rumps:** macOS status bar application
- **Pynput:** Global keyboard hotkey management
- **PyTorch:** ML framework for Whisper model (Python version)
- **psutil:** Process utilities (for lock file management)
- **sounddevice:** Audio device checking (for microphone proactive checks)

### Testing & Development
- **pytest:** Testing framework
- **pytest-reruns:** Retry failed tests
- **coverage:** Code coverage reporting

## Project Repository Status

This project is a **fork** of the original whisper-dictation project:
- **Original Repository:** https://github.com/foges/whisper-dictation
- **Our Fork:** https://github.com/patiball/whisper-dictation
- **Fork configured:** 2025-01-29

### Git Configuration
- `origin` remote → Our fork: https://github.com/patiball/whisper-dictation
- `upstream` remote → Original: https://github.com/foges/whisper-dictation
- Authentication configured with Personal Access Token

**For setup, running commands, and testing procedures see: `README.md`**

## Important Development Notes

### M1/M2 GPU Support

**Python Whisper Version:**
- No native MPS support due to PyTorch SparseMPS incompatibility
- Solution: `DeviceManager` auto-detects and falls back to CPU on M1/M2
- Status: Production-ready CPU implementation

**C++ whisper.cpp Version:**
- ✅ Full M1/M2 GPU support via Metal Performance Shaders
- Command: `whisper-dictation-fast.py -m medium --k_double_cmd`
- Status: Production-ready, all quality issues resolved (Oct 2025)
- Recommendation: Use C++ version on M1/M2 for best performance

### Audio Quality & Configuration

Audio clipping and recording configuration details available in: `specs/[08-00-00]_audio_clipping_warmup_fix.md`

CLI flags: `--frames-per-buffer`, `--warmup-buffers`, `--debug-recorder`
ENV overrides: `WHISPER_FRAMES_PER_BUFFER`, `WHISPER_DEBUG_RECORDER`

### Code Architecture Overview

The application follows modular design patterns:

1. **whisper-dictation.py** & **whisper-dictation-fast.py** - Main entry points
2. **recorder.py** - TDD-compatible audio recording module
3. **transcriber.py** - TDD-compatible transcription wrapper
4. **device_manager.py** - CPU/GPU device selection and optimization
5. **mps_optimizer.py** - M1/M2 specific optimizations

For detailed architecture see: `memory-bank/core/04_systemPatterns.md`

### Testing Strategy

- **Unit tests** in `tests/` directory
- **Manual tests** in `temp/manual_tests/` (preserved for reference)
- **pytest** configured with coverage and reruns
- Tests use TDD-compatible recorder/transcriber modules
- Mark whisper.cpp tests with `@pytest.mark.whisper_cpp` for selective skipping
