# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Multilingual dictation app based on OpenAI Whisper ASR models for accurate speech-to-text conversion. Runs in background, triggered via keyboard shortcuts, entirely offline. Features two implementations:

- **Python Version (whisper-dictation.py)**: Production-ready, CPU-only on M1 (MPS incompatibility)
- **C++ Version (whisper-dictation-fast.py)**: Production-ready with M1 GPU support via whisper.cpp (Metal)

## Development Environment

### Setup
```bash
# Install system dependencies (macOS)
brew install portaudio llvm

# Install Python dependencies
poetry install
poetry shell

# OR without poetry:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Testing
```bash
# Run all tests with coverage
poetry run pytest

# Run specific test file
poetry run pytest tests/test_language_detection.py

# Run with verbose output
poetry run pytest -v

# Skip whisper.cpp tests
poetry run pytest -m "not whisper_cpp"

# Run with retries (configured for 1 retry)
poetry run pytest --reruns 1
```

### Running the Application
```bash
# Python version (CPU-only on M1/M2)
poetry run python whisper-dictation.py --k_double_cmd

# Python with specific model and language
poetry run python whisper-dictation.py -m large -k cmd_r+shift -l en

# C++ version (GPU-accelerated on M1/M2 via Metal)
poetry run python whisper-dictation-fast.py --k_double_cmd

# C++ with model selection (tiny/base/small/medium/large)
poetry run python whisper-dictation-fast.py -m medium --k_double_cmd  # Best quality
poetry run python whisper-dictation-fast.py -m small --k_double_cmd   # Balanced
poetry run python whisper-dictation-fast.py -m base --k_double_cmd    # Default (141MB)
poetry run python whisper-dictation-fast.py -m tiny --k_double_cmd    # Fastest (74MB)

# C++ with language specification
poetry run python whisper-dictation-fast.py -m medium --k_double_cmd -l pl
poetry run python whisper-dictation-fast.py -m medium --k_double_cmd --allowed_languages en,pl

# Audio recording configuration (frames_per_buffer)
poetry run python whisper-dictation.py --frames-per-buffer 512  # Default
poetry run python whisper-dictation.py --frames-per-buffer 1024 # For systems with clipping

# Override via environment variable
WHISPER_FRAMES_PER_BUFFER=1024 poetry run python whisper-dictation.py

# Warm-up buffers (discard initial buffers to stabilize stream)
poetry run python whisper-dictation.py --warmup-buffers 2  # Default

# Enable debug logging for recorder
poetry run python whisper-dictation.py --debug-recorder
# OR via environment
WHISPER_DEBUG_RECORDER=1 poetry run python whisper-dictation.py
```

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

## Code Architecture

### Core Components

1. **whisper-dictation.py** - Main application entry point
   - `SpeechTranscriber`: Handles transcription, types output via keyboard simulation
   - `Recorder`: Audio recording with PyAudio, warm-up buffers, auto-fallback on errors
   - `StatusBarApp`: macOS menu bar integration (rumps)
   - `GlobalKeyListener`/`DoubleCommandKeyListener`: Keyboard shortcut handlers

2. **recorder.py** - TDD-compatible recording module
   - Provides timestamp tracking for diagnostics
   - `start_recording_with_timestamp()`: Returns actual start time
   - `record_duration()`: Fixed-length recording
   - `get_recording_delay()`: Measures startup latency
   - `save_recording()`: WAV file export

3. **transcriber.py** - TDD-compatible transcription wrapper
   - `SpeechTranscriber`: Model loading, device management integration
   - `TranscriptionResult`: Container for text, language, timing
   - `transcribe()`: File-based transcription
   - `transcribe_audio_data()`: Raw numpy array transcription

4. **Device Management System** (M1/M2 optimization)
   - **device_manager.py**: Core device selection and fallback logic
     - `DeviceManager`: Tests capabilities, tracks operation history, intelligent device selection
     - `OperationType`: MODEL_LOADING, TRANSCRIPTION, BASIC_TENSOR
     - `DeviceCapability`: Stores test results and performance scores
   - **mps_optimizer.py**: MPS-specific error handling and optimization
     - `MPSErrorHandler`: Categorizes errors, provides user-friendly messages in Polish
     - `MPSOptimizer`: Device/model-specific Whisper settings (fp16, beam_size, etc.)
     - `EnhancedDeviceManager`: Combines base device manager with MPS optimizations

### Audio Recording Flow

1. **Stream Initialization**: PyAudio stream with configurable `frames_per_buffer` (256/512/1024)
2. **Warm-up Phase**: Discards initial N buffers (`warmup_buffers`, default 2) to stabilize stream
3. **Recording Loop**: Reads audio with `exception_on_overflow=False` to prevent crashes
4. **Auto-Fallback**: If ≥3 errors in first 10 reads, escalates to `frames_per_buffer=1024`
5. **Post-processing**: Converts int16 → float32, normalizes to [-1, 1]

### Device Management Flow

1. **Initialization**: Tests device capabilities (basic ops, model-like ops)
2. **Device Selection**: Chooses device based on capabilities and operation history
3. **Error Handling**: On MPS failure, categorizes error and falls back to CPU
4. **Optimization**: Applies device-specific settings (fp16 on MPS, beam_size tuning)

### Key Design Patterns

- **Graceful Degradation**: MPS → CPU fallback for known incompatibilities
- **Operation Tracking**: Success/failure history guides future device selection
- **Test-Driven Design**: Separate TDD modules (recorder.py, transcriber.py) for testing
- **User-Friendly Errors**: Polish language messages explain technical issues

## Important Development Notes

### M1/M2 GPU Support
- **Python Whisper**: No MPS support due to PyTorch SparseMPS incompatibility
  - **Solution**: `DeviceManager` auto-detects and falls back to CPU on M1/M2
  - **Status**: Production-ready CPU implementation
- **C++ whisper.cpp**: ✅ Full M1/M2 GPU support via Metal Performance Shaders
  - **Command**: `whisper-dictation-fast.py -m medium --k_double_cmd`
  - **Status**: Production-ready, all quality issues resolved (Oct 2025)
- **Recommendation**: Use C++ version on M1/M2 for best performance
- **Details**: See specs/20250130_m1_support_fix.md and specs/20250130_whisper_cpp_quality_fix.md

### Audio Clipping Issues
- **Problem**: Initial audio frames may be clipped/contain noise on some systems
- **Solutions**:
  - Warm-up buffers: Discard first N buffers after stream open (default 2)
  - `exception_on_overflow=False`: Prevent crashes on buffer overflow
  - Auto-fallback: Escalate to larger buffer size (1024) if early errors detected
  - CLI flags: `--frames-per-buffer`, `--warmup-buffers`, `--debug-recorder`
  - ENV overrides: `WHISPER_FRAMES_PER_BUFFER`, `WHISPER_DEBUG_RECORDER`
- **Diagnostics**: See scripts/tmp_rovodev_measure_start_silence.py for PoC script
- **Status**: See specs/20251020_audio_clipping_warmup_fix.md for full spec

### Testing Strategy
- Unit tests in `tests/` directory
- Manual tests in `temp/manual_tests/` (preserved for reference)
- pytest configured with coverage and reruns
- Tests use TDD-compatible recorder/transcriber modules
- Mark whisper.cpp tests with `@pytest.mark.whisper_cpp` to allow selective skipping

### Memory Bank System

**Readme_MB.md is the SINGLE SOURCE OF TRUTH**
- ALWAYS read Readme_MB.md FIRST before any file operations
- NEVER assume file locations - verify against Readme_MB.md
- When Memory Bank doesn't exist → use Default Structure → create Readme_MB.md → it becomes authority

#### Core Structure

**Required Files (locations per Readme_MB.md)**
1. **Readme_MB.md** - Structure definition and file map
2. **projectbrief.md** - Project foundation and goals
3. **activeContext.md** - Current focus and immediate priorities
4. **progress.md** - Implementation status and next steps
5. **systemPatterns.md** - Architecture and key patterns
6. **techContext.md** - Technologies and setup requirements

**Optional Extensions (organized per Readme_MB.md)**
- **specs/** - Specifications directory
- **context/** - Additional documentation
- Project-specific directories as needed

#### Essential Workflows

**Before ANY file operation:**
1. Read Readme_MB.md
2. Verify file locations
3. Execute operation
4. Update Readme_MB.md if structure changed

**When updating Memory Bank:**
1. Read Readme_MB.md for structure
2. Review ALL files per that structure
3. Focus on activeContext.md and progress.md
4. Update specification status
5. Document current state

### Specifications

The `specs/` directory contains feature specifications organized hierarchically.

#### Specification Hierarchy & Naming

**ALL specifications use hierarchical format `[XX-YY-ZZ]_short_name.md`:**

```
[XX-YY-ZZ]_short_name.md

XX = Epic/US number (01, 02, 03...)
YY = User Story number (00 for standalone US or Epic, 01-99 for US in Epic)
ZZ = Task number (00 for US, 01-99 for Task)
```

**Exception: Hotfixes only**
```
YYYYMMDD_emergency_fix.md  ← ONLY for unplanned, critical production fixes
```

**When to use which level:**

| Level | Format | When to Use | Effort | Example |
|-------|--------|-------------|--------|---------|
| **Standalone US** | `[XX-00-00]_name.md` | Simple feature, 1-2 files, <3 hours | Quick/Medium | Bug fix, small feature |
| **Epic + User Stories** | `[XX-00-00]_epic.md`<br>`[XX-01-00]_us.md` | Multiple related features, 3-8 hours | Medium | Feature with phases |
| **Epic + US + Tasks** | `[XX-00-00]_epic.md`<br>`[XX-01-00]_us.md`<br>`[XX-01-01]_task.md` | Complex feature, >8 hours, many files | Large | Major refactoring |
| **Hotfix** | `YYYYMMDD_fix.md` | Emergency production fix | Any | Critical crash fix |

**Hierarchy Examples:**
```
specs/
├── [01-00-00]_m1_support_fix.md                 # Standalone US 01
├── [02-00-00]_macos_portability.md              # Epic 02
├── [02-01-00]_whisper_cli_detection.md          # Epic 02 → US 1
├── [02-01-01]_implement_detection.md            # Epic 02 → US 1 → Task 1
├── [02-01-02]_update_fast_py.md                 # Epic 02 → US 1 → Task 2
├── [02-02-00]_portable_scripts.md               # Epic 02 → US 2
├── [03-00-00]_transcription_timestamps.md       # Standalone US 03
└── 20251023_critical_crash_fix.md               # Hotfix (emergency only)
```

**Grep Examples:**
```bash
ls specs/\[*-00-00\]*      # All standalone US and Epics
ls specs/\[02-*-00\]*      # All user stories for epic 02
ls specs/\[02-01-*\]       # All tasks for US 02.01
ls specs/202*.md           # All hotfixes
```

#### Specification Format

**Epic Format:**
```markdown
# Epic: [Title]

**ID**: XX-00-00
**Created**: YYYY-MM-DD
**Status**: Draft | Ready | In Progress | Implemented
**Priority**: High | Medium | Low

## Overview
High-level WHAT and WHY

## User Stories
- [ ] [XX-01-00] User story 1 name
- [ ] [XX-02-00] User story 2 name

## Success Criteria
Overall epic success metrics
```

**User Story Format:**
```markdown
# User Story: [Title]

**ID**: XX-YY-00
**Epic**: [XX-00-00] Epic name
**Status**: Ready | In Progress | Implemented
**Priority**: High | Medium | Low
**Estimate**: X hours/minutes

## User Story
As a [user type], I want [feature] so that [benefit]

## Acceptance Criteria
- [ ] Specific testable requirement 1
- [ ] Specific testable requirement 2

## Tasks (if needed)
- [ ] [XX-YY-01] Task 1 name
- [ ] [XX-YY-02] Task 2 name

## File Changes Required
- file.py: Brief description
```

**Task Format:**
```markdown
# Task: [Title]

**ID**: XX-YY-ZZ
**User Story**: [XX-YY-00] Story name
**Complexity**: Simple | Medium | Complex
**Estimate**: X minutes

## What
Single, concrete change to be made

## Acceptance Criteria
- [ ] Specific testable outcome

## File Changes
- file.py (line XX): Exact change needed
```

#### Quality Guidelines

**DO:**
- Describe WHAT and WHY (not HOW)
- Provide behavior examples (before/after)
- Keep specs concise (50-100 lines for single spec)
- Use hierarchy (Epic/US/Task) for complex features
- Include testable acceptance criteria

**DON'T:**
- Prescribe exact implementation code
- Include full function definitions
- Write test cases in spec (those go in tests/)
- Create 400-line specs (use Epic/US/Task instead)

#### Important Notes

**Hotfixes only:** Date-based format `YYYYMMDD_*.md` is reserved exclusively for emergency production fixes.

**All planned work:** Use hierarchical format `[XX-00-00]_name.md` (standalone US) or `[XX-YY-ZZ]_name.md` (Epic/US/Task).

**Numbering:** Assign next available number sequentially (01, 02, 03...). Check existing specs with `ls specs/\[*-00-00\]*` to find the last number.

## Common Patterns

### Adding New CLI Flags
1. Add argument to `parse_args()` in whisper-dictation.py
2. Pass to relevant component constructor
3. Document in README.md

### Implementing New Diagnostics
1. Create script in `scripts/` directory
2. Use TDD recorder/transcriber for consistency
3. Save test audio in root with descriptive name
4. Document findings in memory-bank or specs

### Device Management Changes
1. Modify base logic in `device_manager.py`
2. Add MPS-specific handling in `mps_optimizer.py`
3. Update both main app and TDD transcriber
4. Test with CPU/MPS device switching

### Audio Processing Changes
1. Core recording logic is duplicated in:
   - `whisper-dictation.py` (Recorder class)
   - `recorder.py` (TDD-compatible version)
2. Keep both in sync for parameters like:
   - `frames_per_buffer`, `warmup_buffers`, `exception_on_overflow`
   - Auto-fallback logic
   - Debug logging
