# Task: Project File Cleanup and Organization

**Status**: Ready
**Priority**: Medium
**Complexity**: Medium

## Overview
This task aims to clean up the main project directory by moving test-related files and other temporary/unnecessary files to appropriate subdirectories or deleting them. This will improve project clarity and maintainability.

## Acceptance Criteria
- [ ] All identified test-related `.py` and `.wav` files are moved from the root directory to `tests/` or `tests/audio/`.
- [ ] Duplicate test files in the root directory are removed if they exist in `tests/`.
- [ ] Utility/debug scripts are moved to a new `scripts/` directory.
- [ ] The `Wcześniej/` directory is moved to a new `archive/` directory or deleted if confirmed unnecessary.
- [ ] No critical project functionality is broken by these changes.
- [ ] All relevant code references (if any) to moved files are updated.

## File Changes Required

### 1. Create new directories
- Create `/Users/mprzybyszewski/whisper-dictation-documentation/scripts/`
- Create `/Users/mprzybyszewski/whisper-dictation-documentation/archive/`

### 2. Move test files to `tests/` or `tests/audio/`
- Move `/Users/mprzybyszewski/whisper-dictation-documentation/_test_recording_advanced.py` to `/Users/mprzybyszewski/whisper-dictation-documentation/tests/_test_recording_advanced.py`
- Move `/Users/mprzybyszewski/whisper-dictation-documentation/_test_simple.py` to `/Users/mprzybyszewski/whisper-dictation-documentation/tests/_test_simple.py`
- Move `/Users/mprzybyszewski/whisper-dictation-documentation/_test_whisper_performance.py` to `/Users/mprzybyszewski/whisper-dictation-documentation/tests/_test_whisper_performance.py`
- Move `/Users/mprzybyszewski/whisper-dictation-documentation/test_english_20250630_085152.wav` to `/Users/mprzybyszewski/whisper-dictation-documentation/tests/audio/test_english_20250630_085152.wav`
- Move `/Users/mprzybyszewski/whisper-dictation-documentation/test_polish_20250630_083944.wav` to `/Users/mprzybyszewski/whisper-dictation-documentation/tests/audio/test_polish_20250630_083944.wav`
- Move `/Users/mprzybyszewski/whisper-dictation-documentation/testy.md` to `/Users/mprzybyszewski/whisper-dictation-documentation/tests/testy.md` (assuming it's test-related notes)

### 3. Move utility/debug scripts to `scripts/`
- Move `/Users/mprzybyszewski/whisper-dictation-documentation/check_models.py` to `/Users/mprzybyszewski/whisper-dictation-documentation/scripts/check_models.py`
- Move `/Users/mprzybyszewski/whisper-dictation-documentation/debug_transcriptions.py` to `/Users/mprzybyszewski/whisper-dictation-documentation/scripts/debug_transcriptions.py`
- Move `/Users/mprzybyszewski/whisper-dictation-documentation/run_tdd_red_phase.py` to `/Users/mprzybyszewski/whisper-dictation-documentation/scripts/run_tdd_red_phase.py`

### 4. Handle duplicate/old test files (requires verification)
- **Verify and potentially delete:**
    - `/Users/mprzybyszewski/whisper-dictation-documentation/test_language_detection.py` (compare with `tests/test_language_detection.py`)
    - `/Users/mprzybyszewski/whisper-dictation-documentation/test_performance.py` (compare with `tests/test_performance.py`)
    - `/Users/mprzybyszewski/whisper-dictation-documentation/test_recording_advanced.py` (compare with `tests/test_recording_advanced.py`)
    - `/Users/mprzybyszewski/whisper-dictation-documentation/test_simple.py` (compare with `tests/test_simple.py`)
    - `/Users/mprzybyszewski/whisper-dictation-documentation/test_whisper_performance.py` (compare with `tests/test_whisper_performance.py`)
    *Action*: If content is identical or older, delete the root version. If different, merge or decide which to keep.

### 5. Handle `Wcześniej/` directory
- Move `/Users/mprzybyszewski/whisper-dictation-documentation/Wcześniej/` to `/Users/mprzybyszewski/whisper-dictation-documentation/archive/Wcześniej/` (for safekeeping until confirmed unnecessary)

## Integration Points
- After moving files, any scripts or configurations that directly reference these files by their old paths will need to be updated. This includes `pyproject.toml`, `run.sh`, `start_whisper.sh`, `whisper-dictation-wrapper.sh`, and potentially other internal Python imports if the moved scripts are imported elsewhere.
- The `poetry.lock` file might need to be regenerated if any moved files were part of the poetry project structure in a way that affects dependencies.
- Running tests (`pytest`) should be verified after changes.
