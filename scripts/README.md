# Scripts Directory

This directory contains utility scripts and tools for development, testing, and diagnostics.

## 🚀 Application Launch Scripts

### `run.sh`
**Purpose**: Start the whisper-dictation application
**Usage**:
```bash
./scripts/run.sh
```
**Description**: Main launcher script for the application

### `start_whisper.sh`
**Purpose**: Alternative launcher for whisper-dictation
**Usage**:
```bash
./scripts/start_whisper.sh
```

### `whisper-dictation-wrapper.sh`
**Purpose**: Wrapper script for whisper-dictation with additional setup
**Usage**:
```bash
./scripts/whisper-dictation-wrapper.sh
```

---

## 🔧 Utility Scripts (Python)

### `check_models.py`
**Purpose**: Check which Whisper models are available locally
**Usage**:
```bash
poetry run python scripts/check_models.py
```
**Description**: Lists locally cached Whisper models and their sizes. Useful for verifying model availability before running tests.

### `debug_transcriptions.py`
**Purpose**: Debug transcription pipeline
**Usage**:
```bash
poetry run python scripts/debug_transcriptions.py
```
**Description**: Debugging tool for transcription issues. Helps diagnose problems with audio processing and model inference.

### `run_tdd_red_phase.py`
**Purpose**: Run TDD red phase (failing tests)
**Usage**:
```bash
poetry run python scripts/run_tdd_red_phase.py
```
**Description**: TDD development tool. Runs tests expected to fail as part of test-driven development workflow.

### `check-links.py`
**Purpose**: Validate links in documentation
**Usage**:
```bash
poetry run python scripts/check-links.py
```
**Description**: Scans documentation files for broken links. Useful for maintaining documentation quality.

---

## 📊 Diagnostic Scripts

### `tmp_rovodev_measure_start_silence.py`
**Purpose**: Measure start silence in audio recordings (PoC diagnostic)
**Usage**:
```bash
poetry run python scripts/tmp_rovodev_measure_start_silence.py
```
**Description**: Proof-of-concept script to measure silence duration at the start of recordings. Created to diagnose audio clipping issues. See `specs/20251020_audio_clipping_warmup_fix.md` for context.

**Related**:
- Issue: Audio clipping at recording start
- Spec: `specs/20251020_audio_clipping_warmup_fix.md`
- Memory Bank: `memory-bank/issues-backlog.md` (Issue #1)

---

## 🛠️ Development Setup Scripts

### `setup-docs-mvp.sh`
**Purpose**: Set up documentation MVP
**Usage**:
```bash
./scripts/setup-docs-mvp.sh
```
**Description**: Initializes or updates documentation structure

### `warp-run.sh`
**Purpose**: Run commands in Warp terminal context
**Usage**:
```bash
./scripts/warp-run.sh [command]
```
**Description**: Helper for running commands in Warp terminal environment

---

## 📁 Directory Organization

```
scripts/
├── README.md                              # This file
├── run.sh                                 # Main launcher
├── start_whisper.sh                       # Alt launcher
├── whisper-dictation-wrapper.sh           # Wrapper launcher
├── check_models.py                        # Model checking utility
├── debug_transcriptions.py                # Transcription debugger
├── run_tdd_red_phase.py                   # TDD red phase runner
├── check-links.py                         # Documentation link checker
├── tmp_rovodev_measure_start_silence.py   # Audio clipping diagnostic
├── setup-docs-mvp.sh                      # Docs setup
└── warp-run.sh                            # Warp terminal helper
```

---

## 💡 Common Workflows

### Check Available Models Before Testing
```bash
poetry run python scripts/check_models.py
```

### Debug Transcription Issues
```bash
poetry run python scripts/debug_transcriptions.py
```

### Measure Audio Start Silence (Clipping Diagnosis)
```bash
poetry run python scripts/tmp_rovodev_measure_start_silence.py
```

### Validate Documentation Links
```bash
poetry run python scripts/check-links.py
```

---

## 📝 Notes

- All Python scripts should be run with `poetry run python` to ensure correct environment
- Shell scripts (`.sh`) should be executable (`chmod +x`)
- Diagnostic scripts prefixed with `tmp_` are proof-of-concept/temporary tools
- For more information on specific issues, see `memory-bank/issues-backlog.md`
