# Project Context

## Purpose

Whisper Dictation is a multilingual, offline speech-to-text application for macOS that runs in the background and is triggered via keyboard shortcuts. It uses OpenAI Whisper ASR (automatic speech recognition) models for accurate transcription in 99+ languages. The project maintains two production implementations:

- **Python Version**: CPU-based transcription (PyTorch backend)
- **C++ Version**: GPU-accelerated transcription for M1/M2 Macs (whisper.cpp with Metal Performance Shaders)

**Core Goal**: Enable fast, private, offline dictation that automatically types transcribed text into any application.

## Tech Stack

### Core Technologies
- **Language**: Python 3.10+
- **Speech Recognition**: OpenAI Whisper (PyTorch backend) + whisper.cpp (C++ with Metal)
- **Audio I/O**: PyAudio for recording and device management
- **GUI Framework**: Rumps (macOS status bar application)
- **Keyboard Management**: Pynput (global hotkey detection)
- **ML Framework**: PyTorch (Python version only)
- **Package Manager**: Poetry for Python dependency management
- **Testing**: pytest with coverage and reruns

### Key External Dependencies
- **OpenAI Whisper**: Speech recognition models
- **whisper.cpp**: Optimized Whisper implementation with Metal support
- **PyAudio**: Audio stream handling
- **Rumps**: macOS menu bar integration
- **Pynput**: Cross-platform keyboard event capture
- **PyTorch**: Tensor operations and model inference (Python version)

## Project Conventions

### Code Style

**Python Code:**
- Follow PEP 8 conventions
- Use type hints for function signatures
- Keep functions focused and under 40 lines where possible
- Use descriptive variable names (avoid single letters except loop indices)
- Document complex logic with inline comments

**File Organization:**
- Main entry points: `whisper-dictation.py`, `whisper-dictation-fast.py`
- Core modules: `recorder.py`, `transcriber.py`, `device_manager.py`, `mps_optimizer.py`
- Tests: `tests/` directory with pytest configuration
- Manual/reference tests: `temp/manual_tests/` (not executed in CI)

### Architecture Patterns

**Observer Pattern:**
- Recorder captures audio events and notifies SpeechTranscriber when complete
- Allows independent testing of components

**Strategy Pattern:**
- Multiple Whisper model sizes (tiny, base, small, medium, large)
- User can select at runtime via CLI flags
- Swappable backends: Python (PyTorch) vs C++ (whisper.cpp)

**Adapter Pattern:**
- DeviceManager abstracts PyTorch to different hardware (CPU/MPS)
- Transparent fallback to CPU when operations unsupported
- MPSOptimizer handles M1/M2 specific optimizations

**Modular Design:**
- Core transcription logic (`SpeechTranscriber`) independent of GUI
- Audio recording (`Recorder`) can be tested separately
- Status bar integration (`StatusBarApp`) isolated from core logic

**Important Architecture Notes:**
- Audio recording logic is duplicated in `whisper-dictation.py` (Recorder class) and `recorder.py` (TDD-compatible version)—keep both in sync when modifying recording parameters
- Device management uses capability testing: check basic tensor ops → test model load → handle runtime errors
- Fallback on error is critical: MPS failures must gracefully fallback to CPU

### Testing Strategy

**Testing Approach:**
- Use pytest as primary testing framework
- TDD-compatible modules: `recorder.py` and `transcriber.py` for unit testing
- Mark whisper.cpp specific tests with `@pytest.mark.whisper_cpp` for selective execution
- Use `pytest-reruns` to handle flaky audio tests (retry up to 3 times)
- Measure code coverage (target: >70% for core modules)

**Test Organization:**
- Unit tests in `tests/` directory
- Manual tests in `temp/manual_tests/` preserved for reference
- Core modules should have independent, testable interfaces
- Integration tests should use real Whisper models (small or tiny to keep fast)

**Important Test Notes:**
- Audio tests are inherently flaky due to system state dependencies
- Tests using real Whisper inference should use small model to keep CI fast
- TDD modules are designed to be used without the macOS GUI (cross-platform compatibility)

### Git Workflow

**Branching Strategy:**
- **main**: Production-ready code (protected branch)
- **feature branches**: Feature development (kebab-case: `add-language-selection`, `fix-mps-fallback`)
- OpenSpec specs-driven: proposal → review → implementation

**Commit Conventions:**
- Use clear, imperative messages: "Add M1/M2 GPU support" (not "Added support")
- Reference related specs/issues: "Fix audio clipping (#08-00-00)"
- Group related changes: don't mix refactoring with features
- One logical change per commit
- **IMPORTANT**: Do NOT automatically add "Generated with Claude Code" to commits unless explicitly requested by user

**PR Process:**
- PRs require spec approval before implementation
- Include spec ID in PR title: `[SPEC-09-00-00] Add language auto-detection`
- Link to approved proposal in PR description
- Tests and linting must pass before merge

## Domain Context

### Speech Recognition Specifics
- **Whisper Models**: Supports tiny (40MB), base (140MB), small (500MB), medium (1.5GB), large (3GB)
- **Language Detection**: Automatic via Whisper or configurable with `-l` flag
- **Translation**: Application defaults to transcription, not translation
- **Quality**: Whisper is multilingual but quality varies by language (best for English, good for major languages)

### Audio Processing Details
- **Buffer Management**: Configurable with `--frames-per-buffer` (default determined by system)
- **Warmup Buffers**: Silence at start prevents interference with detection (0.1s delay for C++ version)
- **Sample Rate**: PyAudio auto-detects; ensure microphone is available before startup
- **Error Handling**: Auto-fallback on audio errors; preserve user experience

### M1/M2 GPU Considerations
- **Python Version**: PyTorch SparseMMS incompatibility → CPU-only, handled gracefully
- **C++ Version**: Full GPU support via Metal, dramatically faster transcription
- **Recommendation**: Use C++ version on Apple Silicon for 3-5x speedup
- **Fallback**: Always gracefully fallback to CPU if GPU operations fail

### Keyboard & Global Hotkeys
- **Hotkey Binding**: Pynput requires elevated permissions (handled by Rumps framework)
- **Double-Tap Detection**: DoubleCommandKeyListener for special shortcuts (e.g., double-tap Command)
- **Cross-Application**: Hotkeys work even when app is not focused

### Lock File & Single Instance
- **Purpose**: Prevent multiple instances from recording simultaneously
- **Location**: User's home directory (`~/.whisper-dictation.lock`)
- **Signal Handling**: SIGINT/SIGTERM cleanup with proper lock file removal

## Important Constraints

### Platform Constraints
- **Primary**: macOS (M1/M2 and Intel)
- **Secondary**: Linux/Windows (experimental, untested)
- **macOS Permissions**: Microphone access and accessibility required

### Performance Constraints
- **Model Loading**: First load takes 5-30 seconds depending on model size
- **Inference**: CPU inference slow on Intel; use smallest adequate model
- **GPU**: M1/M2 GPU can transcribe 60-second audio in ~3 seconds

### Backward Compatibility
- **Config Format**: Must maintain compatibility with existing user configs
- **Model Downloads**: Respect existing Whisper model cache locations
- **CLI Flags**: Maintain existing flag names and defaults

### Development Constraints
- **Dual Code**: Audio recording duplicated in main app and TDD module—must stay synchronized
- **Testing Audio**: Flaky tests due to system state; use reruns and selective marking
- **CI/CD**: Must run on GitHub Actions (Linux-based runners for testing)

## External Dependencies

### Services & Systems
- **OpenAI Whisper Models**: Downloaded and cached locally (no internet required after cache)
- **PyAudio**: System portaudio library (installed via Homebrew on macOS)
- **LLVM**: Required for certain PyAudio installations

### Important Notes
- **No Cloud Dependencies**: All processing is offline after model download
- **Model Caching**: Models cached in `~/.cache/` (PyTorch) or `~/.whisper-models/` (C++ version)
- **Privacy**: User audio never leaves the computer

## Spec Organization & Naming

All specifications follow hierarchical naming in `openspec/specs/`:

- **[XX-00-00]**: Epic (major feature, multiple related stories)
- **[XX-YY-00]**: User Story (feature with clear acceptance criteria)
- **[XX-YY-ZZ]**: Task (implementation task within a story)

**Example**: `[08-00-00]_audio_quality.md` (Epic) → `[08-01-00]_warmup_buffers.md` (Story) → `[08-01-01]_implement_warmup.md` (Task)

Changes in progress are proposed in `openspec/changes/[change-id]/` and archived after deployment.
