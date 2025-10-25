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

## Development Environment Setup

### 1. Install System Dependencies (macOS)

```bash
brew install portaudio llvm
```

### 2. Clone Repository

```bash
git clone https://github.com/patiball/whisper-dictation.git
cd whisper-dictation
```

### 3. Install Python Dependencies

**Option A: Using Poetry (Recommended)**
```bash
poetry install
poetry shell
```

**Option B: Using venv**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the Application

### Python Version (CPU-only on M1/M2)

```bash
# Basic usage
poetry run python whisper-dictation.py --k_double_cmd

# With specific model and language
poetry run python whisper-dictation.py -m large -k cmd_r+shift -l en
```

### C++ Version (GPU-accelerated on M1/M2 via Metal)

```bash
# Basic usage (uses default base model)
poetry run python whisper-dictation-fast.py --k_double_cmd

# Model selection (tiny/base/small/medium/large)
poetry run python whisper-dictation-fast.py -m medium --k_double_cmd  # Best quality
poetry run python whisper-dictation-fast.py -m small --k_double_cmd   # Balanced
poetry run python whisper-dictation-fast.py -m base --k_double_cmd    # Default (141MB)
poetry run python whisper-dictation-fast.py -m tiny --k_double_cmd    # Fastest (74MB)
```

### Audio Configuration

```bash
# Configure audio buffer size (for clipping issues)
poetry run python whisper-dictation.py --frames-per-buffer 512  # Default
poetry run python whisper-dictation.py --frames-per-buffer 1024 # For clipping

# Configure warm-up buffers
poetry run python whisper-dictation.py --warmup-buffers 2  # Default

# Enable debug logging
poetry run python whisper-dictation.py --debug-recorder

# Or via environment variable
WHISPER_FRAMES_PER_BUFFER=1024 poetry run python whisper-dictation.py
WHISPER_DEBUG_RECORDER=1 poetry run python whisper-dictation.py
```

### Language & Multilingual Support

```bash
# Polish language (C++ version)
poetry run python whisper-dictation-fast.py -m medium --k_double_cmd -l pl

# Multiple allowed languages
poetry run python whisper-dictation-fast.py --allowed_languages en,pl

# Auto-detect language
poetry run python whisper-dictation-fast.py -l auto
```

## Testing

### Run All Tests
```bash
poetry run pytest
```

### Run Specific Test File
```bash
poetry run pytest tests/test_language_detection.py
```

### Run with Verbose Output
```bash
poetry run pytest -v
```

### Skip C++ Specific Tests
```bash
poetry run pytest -m "not whisper_cpp"
```

### Run with Coverage
```bash
poetry run pytest --cov=. --cov-report=html
```

### Run with Retries (configured for 1 retry)
```bash
poetry run pytest --reruns 1
```

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

### Audio Clipping Issues

**Problem:** Initial audio frames may be clipped/contain noise on some systems

**Solutions:**
- Warm-up buffers: Discard first N buffers after stream open (default 2)
- `exception_on_overflow=False`: Prevent crashes on buffer overflow
- Auto-fallback: Escalate to larger buffer size (1024) if early errors detected
- CLI flags: `--frames-per-buffer`, `--warmup-buffers`, `--debug-recorder`
- ENV overrides: `WHISPER_FRAMES_PER_BUFFER`, `WHISPER_DEBUG_RECORDER`

For details see: `specs/[08-00-00]_audio_clipping_warmup_fix.md`

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
