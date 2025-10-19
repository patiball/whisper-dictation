# FILE INVENTORY

**Project:** whisper-dictation  
**Generated:** 2025-10-10  
**Purpose:** Complete inventory of all source files in the project

---

## 1. Introduction

This document provides a comprehensive inventory of all source files in the whisper-dictation project. It includes line counts, file types, and descriptions to help developers quickly understand the project structure.

---

## 2. Main Application Files

| File | Type | Lines | Description |
|------|------|-------|-------------|
| `whisper-dictation.py` | Main | 374 | Main application using Python-based Whisper transcription with GPU support (MPS/CUDA) |
| `whisper-dictation-fast.py` | Main | 325 | Fast implementation using whisper.cpp for C++ acceleration |
| `whisper-dictation-optimized.py` | Main | 375 | Optimized version with language caching and performance improvements |
| `whisper-dictation-wrapper.sh` | Shell | 3 | Wrapper script to launch the application |

**Notes:**
- All main files support macOS status bar integration via rumps
- Keyboard shortcuts: double-Cmd for start, single-Cmd to stop
- Support for multilingual dictation (English/Polish)

---

## 3. Core Modules

| File | Type | Lines | Description |
|------|------|-------|-------------|
| `recorder.py` | Module | 221 | TDD-compatible audio recording module with timestamp tracking |
| `transcriber.py` | Module | 296 | TDD-compatible speech transcriber with language detection |
| `device_manager.py` | Module | 271 | Centralized device management for M1/M2 optimization with intelligent fallback |
| `mps_optimizer.py` | Module | 250 | M1/M2 specific optimizations and MPS error handling |

**Key Features:**
- `recorder.py`: Provides recording with precise timestamp tracking for TDD tests
- `transcriber.py`: Wraps Whisper functionality with enhanced device management
- `device_manager.py`: Handles MPS/CUDA/CPU device selection and fallback logic
- `mps_optimizer.py`: Specialized error handling for Apple Silicon GPU issues

---

## 4. Test Files

### Main Test Directory (`tests/`)

| File | Type | Lines | Description |
|------|------|-------|-------------|
| `tests/conftest.py` | Test Config | 95 | pytest fixtures and configuration for all tests |
| `tests/record_test_samples.py` | Test Utility | 211 | Records sample audio files for testing (Polish/English) |
| `tests/test_language_detection.py` | Test Suite | 224 | Tests for language detection accuracy and text completeness |
| `tests/test_performance.py` | Test Suite | 310 | Tests for transcription speed and GPU acceleration |
| `tests/test_recording_quality.py` | Test Suite | 298 | Tests for audio clipping detection and recording delays |

### Root Test Files (Legacy/Development)

| File | Type | Lines | Description |
|------|------|-------|-------------|
| `test_language_detection.py` | Test | 155 | Root-level copy of language detection tests |
| `test_performance.py` | Test | 216 | Root-level copy of performance tests |
| `test_recording_advanced.py` | Test | 169 | Advanced recording quality tests |
| `test_simple.py` | Test | 28 | Simple smoke test for basic functionality |
| `test_whisper_performance.py` | Test | 271 | Whisper-specific performance benchmarks |
| `_test_recording_advanced.py` | Test | 169 | Backup/archive of recording tests |
| `_test_simple.py` | Test | 28 | Backup/archive of simple tests |
| `_test_whisper_performance.py` | Test | 271 | Backup/archive of performance tests |

**Total Test Files:** 11  
**Total Test Lines:** 1,138 (in `tests/`) + additional root-level tests

---

## 5. Utility Scripts

| File | Type | Lines | Description |
|------|------|-------|-------------|
| `check_models.py` | Utility | 47 | Checks available Whisper models and prevents unwanted downloads |
| `debug_transcriptions.py` | Debug | 72 | Debug script to see actual transcription results from test files |
| `run_tdd_red_phase.py` | TDD Runner | 213 | TDD Red Phase Runner - executes all tests to verify failures before implementation |
| `run.sh` | Shell | 4 | Quick launch script for the application |
| `start_whisper.sh` | Shell | 32 | Main startup script with environment setup |

### Scripts Directory (`scripts/`)

| File | Type | Lines | Description |
|------|------|-------|-------------|
| `scripts/check-links.py` | Utility | 18 | Validates documentation links |
| `scripts/setup-docs-mvp.sh` | Shell | 67 | Sets up documentation structure (MVP) |
| `scripts/warp-run.sh` | Shell | 34 | Warp terminal integration script |

**Total Script Files:** 8  
**Total Script Lines:** 487

---

## 6. Configuration Files

| File | Type | Lines | Description |
|------|------|-------|-------------|
| `pyproject.toml` | Config | 34 | Python project metadata and build configuration |
| `requirements.txt` | Config | 9 | Python package dependencies |
| `.gitignore` | Config | 11 | Git ignore rules for Python and macOS |

**Dependencies (from requirements.txt):**
- openai-whisper
- pyaudio
- numpy
- rumps (macOS status bar)
- pynput (keyboard input)
- torch (PyTorch)

---

## 7. Documentation Files

### Main Documentation (`docs/`)

| File | Type | Description |
|------|------|-------------|
| `docs/README.md` | Main | Project overview and quick start |
| `docs/PROJECT_OVERVIEW.md` | Spec | Detailed project overview |
| `docs/ARCHITECTURE.md` | Spec | System architecture documentation |
| `docs/DATA_FLOW.md` | Spec | Data flow and processing pipeline |
| `docs/DOCUMENTATION_PLAN.md` | Plan | Documentation organization plan |

### Task Documentation (`docs/.tasks/`)

| File | Purpose |
|------|---------|
| `docs/.tasks/20251010_1420_ARCHITECTURE.md` | Architecture documentation task |
| `docs/.tasks/20251010_1425_ARCH_main_doc.md` | Main architecture document task |
| `docs/.tasks/20251010_1426_DATA_FLOW.md` | Data flow documentation task |
| `docs/.tasks/20251010_1434_API_INTERFACES.md` | API interfaces documentation task |
| `docs/.tasks/20251010_1434_DEBT_REFACTOR.md` | Technical debt and refactoring task |
| `docs/.tasks/20251010_1434_FILE_INVENTORY.md` | This file inventory task (completed) |
| `docs/.tasks/20251010_1434_MODULES.md` | Module documentation task |
| `docs/.tasks/STATUS.md` | Task status tracking |

### Working Documents (`docs/`)

| File | Purpose |
|------|---------|
| `docs/.agent-task.md` | AI agent working document |
| `docs/.cleanup-task.md` | Cleanup task notes |
| `docs/.commit-task.md` | Commit organization notes |

---

## 8. Project Statistics

### Code Summary

| Category | Files | Lines | Percentage |
|----------|-------|-------|------------|
| Main Applications | 4 | 1,077 | 28.7% |
| Core Modules | 4 | 1,038 | 27.7% |
| Tests | 11+ | 2,289+ | 61.0% |
| Utilities | 8 | 487 | 13.0% |
| Configuration | 3 | 54 | 1.4% |
| **Total** | **30+** | **~5,000** | **100%** |

### File Types

| Type | Count | Primary Purpose |
|------|-------|-----------------|
| `.py` | 28 | Python source code |
| `.sh` | 5 | Shell scripts |
| `.toml` | 1 | Project configuration |
| `.txt` | 1 | Dependencies |
| `.gitignore` | 1 | Git configuration |
| `.md` | 15+ | Documentation |

---

## 9. Key Architectural Components

### Audio Processing Pipeline

```
User Input (Keyboard) → Recorder → Audio Buffer → Transcriber → Device Manager → Whisper Model → Text Output
                           ↓                          ↓                ↓
                    Sound Player              MPS Optimizer    CPU/MPS/CUDA
```

### Device Management Hierarchy

1. **DeviceManager** (`device_manager.py`)
   - Base device selection and capability testing
   - Operation-specific device routing
   - Error tracking and fallback logic

2. **MPSOptimizer** (`mps_optimizer.py`)
   - M1/M2 specific optimizations
   - MPS error categorization and handling
   - Performance tuning for Apple Silicon

3. **EnhancedDeviceManager** (in `transcriber.py`)
   - Integrates DeviceManager + MPSOptimizer
   - User-friendly error messages
   - Intelligent retry logic

---

## 10. Files to Investigate

The following files warrant further investigation or cleanup:

### Duplicate Test Files
- `test_*.py` (root) vs `tests/test_*.py` - **[TO INVESTIGATE]**
  - Determine which are canonical
  - Consider removing duplicates
  - May be development snapshots

### Underscore-Prefixed Tests
- `_test_*.py` files - **[TO INVESTIGATE]**
  - Appear to be backups or disabled tests
  - Should be archived or removed

### Multiple Main Files
- Three main implementations exist - **[TO INVESTIGATE]**
  - `whisper-dictation.py` (Python Whisper)
  - `whisper-dictation-fast.py` (whisper.cpp)
  - `whisper-dictation-optimized.py` (optimized variant)
  - Clarify which is production-ready
  - Consider consolidating or documenting differences

### Documentation Organization
- Working documents (`.agent-task.md`, etc.) - **[TO INVESTIGATE]**
  - Should these be in docs/ root or a subdirectory?
  - Consider moving to `docs/.working/`

---

## 11. Recommended Actions

### Cleanup
1. Remove or archive duplicate test files
2. Remove underscore-prefixed backup tests
3. Consolidate or document main application variants
4. Organize working documentation into subdirectory

### Documentation
1. Document differences between main implementations
2. Add inline documentation for complex algorithms
3. Create API reference from module docstrings
4. Document testing strategy and TDD workflow

### Testing
1. Standardize on single test suite location
2. Add integration tests
3. Add CI/CD configuration
4. Document test data generation process

### Development
1. Add version tracking (semver)
2. Add changelog
3. Add contributing guidelines
4. Add code style guide (Black/Flake8)

---

## 12. Directory Structure

```
whisper-dictation/
├── whisper-dictation.py          # Main app (Python Whisper)
├── whisper-dictation-fast.py     # Main app (whisper.cpp)
├── whisper-dictation-optimized.py # Main app (optimized)
├── whisper-dictation-wrapper.sh  # Launch wrapper
├── recorder.py                   # Recording module
├── transcriber.py                # Transcription module
├── device_manager.py             # Device management
├── mps_optimizer.py              # M1/M2 optimizations
├── check_models.py               # Model checker utility
├── debug_transcriptions.py       # Debug utility
├── run_tdd_red_phase.py          # TDD runner
├── run.sh                        # Quick launcher
├── start_whisper.sh              # Main launcher
├── pyproject.toml                # Project config
├── requirements.txt              # Dependencies
├── .gitignore                    # Git config
├── test_*.py                     # Root test files (legacy?)
├── _test_*.py                    # Backup test files
├── tests/                        # Main test directory
│   ├── conftest.py
│   ├── record_test_samples.py
│   ├── test_language_detection.py
│   ├── test_performance.py
│   └── test_recording_quality.py
├── scripts/                      # Utility scripts
│   ├── check-links.py
│   ├── setup-docs-mvp.sh
│   └── warp-run.sh
└── docs/                         # Documentation
    ├── README.md
    ├── PROJECT_OVERVIEW.md
    ├── ARCHITECTURE.md
    ├── DATA_FLOW.md
    ├── DOCUMENTATION_PLAN.md
    ├── FILE_INVENTORY.md         # This file
    ├── .agent-task.md
    ├── .cleanup-task.md
    ├── .commit-task.md
    └── .tasks/                   # Task tracking
        ├── 20251010_*.md
        └── STATUS.md
```

---

## 13. Maintenance Notes

### Last Updated
- **Date:** 2025-10-10
- **By:** Automated inventory generation
- **Reason:** Initial file inventory creation

### Update Frequency
- This document should be updated when:
  - New source files are added
  - Files are removed or renamed
  - Major refactoring occurs
  - Project structure changes

### Automation
- Consider adding a script to auto-generate/update this inventory
- Use `wc -l` for line counts
- Use `find` for file discovery
- Parse git history for file metadata

---

## 14. Quick Reference

### Finding Specific Functionality

| Looking for... | Check file... |
|----------------|---------------|
| Main entry point | `whisper-dictation*.py` |
| Audio recording | `recorder.py` |
| Transcription logic | `transcriber.py` |
| GPU/CPU device handling | `device_manager.py` |
| M1 optimizations | `mps_optimizer.py` |
| Language detection tests | `tests/test_language_detection.py` |
| Performance benchmarks | `tests/test_performance.py` |
| Model management | `check_models.py` |
| Debug output | `debug_transcriptions.py` |

### Common Tasks

| Task | Command/File |
|------|--------------|
| Run tests | `python -m pytest tests/` |
| Check models | `python check_models.py` |
| Debug transcriptions | `python debug_transcriptions.py` |
| Run TDD red phase | `python run_tdd_red_phase.py` |
| Start application | `./start_whisper.sh` or `./run.sh` |
| Record test samples | `python tests/record_test_samples.py` |

---

## Metadata

**Wersja dokumentu**: 1.1  
**Data utworzenia**: 2025-10-10  
**Ostatnia aktualizacja**: 2025-10-19  
**Autor**: AI Agent  
**Status**: ✅ Ukończone  

**Changelog**:
- 2025-10-19: Aktualizacja daty ostatniej aktualizacji.
- 2025-10-10: Initial file inventory creation.

---

**End of File Inventory**
