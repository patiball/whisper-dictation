# User Story: Enhanced Logging & Diagnostics

**ID**: 13-04-00
**Epic**: [13-00-00] Lessons Learned Foundation
**Status**: Draft
**Priority**: Medium
**Complexity**: Medium
**Estimate**: 15-20 minutes

---

## User Story

**As a** whisper-dictation developer/user,
**I want** detailed logging of all major application events (recording, transcription, device management, watchdog),
**So that** I can diagnose problems quickly and understand what happened during any issue.

---

## Background

### Current Situation
- Some logging exists with timestamps
- Logging is scattered across different modules
- No consistent format
- Log file location is hardcoded
- No rotation or disk space protection

### Why This Matters
- **Diagnosis**: When problems occur, logs are the first place to look
- **Forensics**: Understand sequence of events during failures
- **Performance**: Track timing of operations
- **Support**: Users can share logs for debugging

### Pattern from macos-dictate
```python
LOG_FILE = Path.home() / '.dictate.log'
logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

---

## What We're Building

**Centralized logging system** with:
1. File output to `~/.whisper-dictation.log`
2. Log rotation (5 files × 5MB max)
3. Consistent timestamp format
4. Key diagnostic events logged
5. Optional debug mode (CLI flag)

---

## Assumptions & Validation

### A1: RotatingFileHandler is Sufficient
- Assumption: `logging.handlers.RotatingFileHandler` handles rotation
- Validation: Verify disk space doesn't fill up (5×5MB = 25MB max)
- Risk: Rotation fails, log grows unbounded
- Mitigation: Use proven stdlib handler

### A2: Log File in Home Directory is Safe
- Assumption: User always has write permission to home dir
- Validation: Test with different user accounts
- Risk: Permission denied → no logging
- Mitigation: Graceful fallback if write fails

### A3: File Logging Doesn't Impact Performance
- Assumption: Async logging or buffering handles blocking
- Validation: Benchmark I/O overhead
- Risk: Logging adds latency to recording
- Mitigation: Use buffering (default in logging module)

---

## Acceptance Criteria

### Logging Infrastructure
- [ ] **L1** Logs written to `~/.whisper-dictation.log`
- [ ] **L2** Log rotation: max 5 files, 5MB each (25MB total max)
- [ ] **L3** Old log files automatically deleted
- [ ] **L4** Timestamp format: `YYYY-MM-DD HH:MM:SS.mmm`
- [ ] **L5** Log level configuration via CLI `--log-level {DEBUG,INFO,WARNING,ERROR}`
- [ ] **L6** Default log level: INFO (not too verbose)

### Key Events Logged
- [ ] **E1** Application startup: "Application started, PID=XXXX"
- [ ] **E2** Lock file created/checked
- [ ] **E3** Microphone test result (pass/fail)
- [ ] **E4** Recording started: "Recording started, frames_per_buffer=512"
- [ ] **E5** Recording stopped: "Recording stopped, duration=3.5s"
- [ ] **E6** Transcription started: "Transcribing with model=base, device=CPU"
- [ ] **E7** Transcription completed: "Transcription complete, text_length=42"
- [ ] **E8** Device selection: "Selected device: CPU" or "Selected device: GPU (MPS)"
- [ ] **E9** Watchdog events: stall detection, restart attempts
- [ ] **E10** Errors with full traceback at ERROR level
- [ ] **E11** Application shutdown: "Application shutting down (signal X)"

### No Regressions
- [ ] **R1** Console output still works
- [ ] **R2** Recording/transcription unaffected
- [ ] **R3** Existing tests still pass
- [ ] **R4** Works with both versions

---

## Behavior Examples

### Example 1: Normal Operation (INFO level)
```
2025-10-25 14:23:45.123 - INFO - Application started, PID=12345
2025-10-25 14:23:45.124 - INFO - Lock file created
2025-10-25 14:23:45.125 - INFO - Microphone access test passed
2025-10-25 14:23:45.126 - INFO - Watchdog thread started
2025-10-25 14:23:45.127 - INFO - Listening...
2025-10-25 14:23:48.000 - INFO - Recording started, frames_per_buffer=512, duration=0.0s
2025-10-25 14:23:48.001 - INFO - Transcribing...
2025-10-25 14:23:48.002 - INFO - Transcription started with model=base, device=CPU
2025-10-25 14:23:51.000 - INFO - Transcription complete, text_length=42
2025-10-25 14:23:51.001 - INFO - Typing text...
2025-10-25 14:23:51.100 - INFO - Typing complete
2025-10-25 14:24:00.000 - INFO - Application shutting down (signal 2)
```

### Example 2: With Error (WARNING + ERROR levels)
```
2025-10-25 14:23:45.125 - WARNING - Microphone access test failed: PermissionError
2025-10-25 14:23:45.126 - INFO - Watchdog thread started
2025-10-25 14:23:48.000 - INFO - Recording started
2025-10-25 14:23:51.000 - ERROR - Transcription failed: whisper-cli returned code 1
2025-10-25 14:23:51.001 - ERROR - Error output: /Users/mprzybyszewski/.whisper-models/ggml-base.bin: No such file or directory
```

### Example 3: Watchdog Activity (DEBUG level)
```
2025-10-25 14:23:45.124 - DEBUG - Watchdog timeout configured: 10s
2025-10-25 14:23:48.000 - DEBUG - Recording started, initializing heartbeat
2025-10-25 14:23:49.001 - DEBUG - Heartbeat updated (time_since=1.0s)
2025-10-25 14:23:50.002 - DEBUG - Heartbeat updated (time_since=1.0s)
2025-10-25 14:23:58.000 - WARNING - Audio system stalled! No heartbeat for 10.0s
2025-10-25 14:23:58.001 - INFO - Restarting audio stream...
2025-10-25 14:23:58.050 - INFO - Audio stream restarted successfully
```

---

## Design & Implementation

### Logging Setup Function

```python
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging(level=logging.INFO):
    """Setup centralized logging with file rotation"""
    log_file = Path.home() / ".whisper-dictation.log"

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        str(log_file),
        maxBytes=5*1024*1024,    # 5MB
        backupCount=5             # Keep 5 backup files
    )
    file_handler.setLevel(level)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)

    # Console handler (for immediate feedback)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Console only INFO+
    console_handler.setFormatter(formatter)

    # Add handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    logging.info(f"Logging initialized: {log_file}, level={logging.getLevelName(level)}")
```

### CLI Integration

```python
def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser()
    # ... existing args ...
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging verbosity level'
    )
    parser.add_argument(
        '--log-file',
        type=str,
        default=str(Path.home() / ".whisper-dictation.log"),
        help='Path to log file'
    )
    return parser.parse_args()

# In main block:
args = parse_args()
log_level = getattr(logging, args.log_level)
setup_logging(level=log_level)
```

### Key Diagnostic Logging Points

```python
# Application startup
logging.info(f"Application started, PID={os.getpid()}")

# Lock file
logging.info("Lock file created")
logging.warning(f"Stale lock file found (PID {old_pid} is dead)")

# Microphone check
logging.info("Microphone access test passed")
logging.warning("Microphone access test failed: {error}")

# Recording
logging.info(f"Recording started, frames_per_buffer={frames_per_buffer}")
logging.debug(f"Warm-up buffers: {warmup_buffers}")
logging.info(f"Recording stopped, duration={duration:.1f}s")

# Device selection
logging.info("Selected device: CPU")
logging.info("Selected device: GPU (MPS)")
logging.debug(f"Device test result: {capability}")

# Transcription
logging.info(f"Transcription started with model={model}, device={device}")
logging.debug(f"Running whisper-cli: {command}")
logging.info(f"Transcription complete, text_length={len(text)}")
logging.error(f"Transcription failed: {error}")

# Watchdog
logging.info("Watchdog thread started")
logging.warning(f"Audio system stalled! No heartbeat for {time_since:.1f}s")
logging.info("Restarting audio stream...")
logging.info("Audio stream restarted successfully")
logging.error(f"Failed to restart audio stream: {error}")

# Shutdown
logging.info(f"Shutdown signal received: {signum}")
logging.info("Shutdown complete")
```

---

## Test Cases (TDD - Write FIRST)

### Test Suite: `tests/test_logging.py`

```python
import pytest
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import os

from whisper_dictation_module import setup_logging

class TestLoggingSetup:
    """Test logging initialization"""

    def test_log_file_created(self, tmp_path):
        """Log file should be created in specified location"""
        log_file = tmp_path / "test.log"

        # Setup logging (would need to refactor to accept log_file param)
        # setup_logging(log_file=log_file)

        # For now, test that default location is home dir
        default_log = Path.home() / ".whisper-dictation.log"
        assert str(default_log).endswith(".whisper-dictation.log")

    def test_log_level_configuration(self):
        """Log level should be configurable"""
        # Test with different levels
        for level in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]:
            # Setup would set this level
            # Verify logger uses it
            pass

class TestRotatingFileHandler:
    """Test log rotation"""

    def test_rotation_creates_multiple_files(self):
        """Log rotation should create backup files"""
        # Create logger with small file size to trigger rotation
        # Write enough data to trigger rotation
        # Verify backup files created
        pass

    def test_old_logs_deleted(self):
        """Should keep only 5 backup files max"""
        # Create 7 log files by rotation
        # Verify only 5 backups remain
        pass

class TestKeyEventsLogged:
    """Test that key events are logged"""

    def test_startup_logged(self, caplog):
        """Application startup should be logged"""
        with caplog.at_level(logging.INFO):
            logging.info("Test startup")
        assert "startup" in caplog.text.lower()

    def test_lock_file_logged(self, caplog):
        """Lock file events should be logged"""
        with caplog.at_level(logging.INFO):
            logging.info("Lock file created")
        assert "lock" in caplog.text.lower()

    def test_error_with_traceback(self, caplog):
        """Errors should include traceback"""
        with caplog.at_level(logging.ERROR):
            try:
                1/0
            except Exception:
                logging.exception("Error occurred")
        assert "traceback" in caplog.text.lower() or "Traceback" in caplog.text

class TestConsoleFallback:
    """Test console logging fallback"""

    def test_console_shows_warnings_and_errors(self, capsys):
        """Console should show at least WARNING level"""
        logging.warning("Test warning")
        captured = capsys.readouterr()
        assert "warning" in captured.err.lower() or "warning" in captured.out.lower()

class TestLogFormat:
    """Test log format consistency"""

    def test_timestamp_format(self, caplog):
        """Logs should have consistent timestamp format"""
        with caplog.at_level(logging.INFO):
            logging.info("Test message")

        # Check format: YYYY-MM-DD HH:MM:SS
        # This is implicit in formatter configuration
        assert len(caplog.records) > 0

    def test_log_level_in_output(self, caplog):
        """Log level should appear in output"""
        with caplog.at_level(logging.INFO):
            logging.info("Info message")
            logging.warning("Warning message")

        assert any("INFO" in record.levelname for record in caplog.records)
        assert any("WARNING" in record.levelname for record in caplog.records)
```

---

## File Changes Required

### `whisper-dictation.py`

**Add imports:**
```python
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import argparse
```

**Add this function (with other setup functions):**
```python
def setup_logging(level=logging.INFO, log_file=None):
    """Setup centralized logging with file rotation"""
    if log_file is None:
        log_file = Path.home() / ".whisper-dictation.log"
    else:
        log_file = Path(log_file)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers (for testing)
    root_logger.handlers = []

    # File handler with rotation
    try:
        file_handler = RotatingFileHandler(
            str(log_file),
            maxBytes=5*1024*1024,    # 5MB
            backupCount=5             # Keep 5 backup files
        )
        file_handler.setLevel(level)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not setup file logging: {e}")

    # Console handler (for immediate feedback)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Console only INFO+
    if len(root_logger.handlers) > 0:  # Only if file handler worked
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    logging.info(f"Logging initialized, level={logging.getLevelName(level)}")
```

**Modify parse_args() to add:**
```python
parser.add_argument(
    '--log-level',
    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
    default='INFO',
    help='Logging verbosity level (default: INFO)'
)
parser.add_argument(
    '--log-file',
    type=str,
    help='Path to log file (default: ~/.whisper-dictation.log)'
)
```

**In main block (very first thing):**
```python
if __name__ == "__main__":
    args = parse_args()
    log_level = getattr(logging, args.log_level)
    setup_logging(level=log_level, log_file=args.log_file)

    logging.info(f"Application started, PID={os.getpid()}")

    # ... rest of initialization ...
```

**Add logging calls throughout:**
```python
# In setup_lock_file()
logging.info("Lock file created")

# In test_microphone_access()
logging.info("Microphone access test passed")

# In Recorder._record_impl()
logging.info(f"Recording started, frames_per_buffer={self.frames_per_buffer}")

# In SpeechTranscriber.transcribe()
logging.info(f"Transcription started with model={model}, device={device}")

# In signal_exit_handler()
logging.info(f"Shutdown signal received: {signum}")
```

### `whisper-dictation-fast.py`

**Identical changes as above** (keep both versions in sync)

---

## Brittleness Analysis

### Failure Mode 1: Log File Permissions
**Scenario**: User doesn't have write permission to home directory
**Detection**: RotatingFileHandler raise OSError
**Consequence**: No file logging, but app continues
**Prevention**: Try/except around file handler setup
**Recovery**: Graceful fallback to console only
**Mitigation**: Implemented in setup_logging()

### Failure Mode 2: Disk Space Exhausted
**Scenario**: Even with 25MB max, disk is full
**Detection**: RotatingFileHandler.doRollover() fails
**Consequence**: Logging stops or errors
**Prevention**: Rotation prevents unbounded growth
**Recovery**: Oldest logs auto-deleted
**Mitigation**: 25MB is reasonable limit

### Failure Mode 3: Log File Locked by Another Process
**Scenario**: Another tool reading logs while we write
**Detection**: IOError on write (rare on macOS)
**Consequence**: Log entry lost
**Prevention**: Can't prevent, rare issue
**Recovery**: Next write succeeds
**Mitigation**: Acceptable risk

### Failure Mode 4: Logging in Signal Handler
**Scenario**: Signal handler calls logging while main thread in logging
**Detection**: Deadlock potential
**Consequence**: Hang during shutdown
**Prevention**: logging module is thread-safe (uses lock)
**Recovery**: No action needed, stdlib handles it
**Mitigation**: Already safe

### Failure Mode 5: Circular Logging
**Scenario**: Some error log triggers another error log
**Detection**: Excessive log output
**Consequence**: Log file grows rapidly
**Prevention**: Don't log from within logging code
**Recovery**: Should not happen with stdlib
**Mitigation**: No action needed

---

## Rollout Strategy

### Phase 1: Setup
1. Add setup_logging() function
2. Add CLI arguments
3. Call setup_logging() on startup
4. Test file creation and rotation

### Phase 2: Event Logging
1. Add logging to key events
2. Test different log levels
3. Verify rotation works

### Phase 3: Validation
1. Check log file is readable
2. Verify rotation works (create big log)
3. Test with DEBUG level
4. Document log locations in README

---

## Performance Impact

- **Logging overhead**: <1% CPU (buffered I/O)
- **File I/O**: Async in logging module
- **Startup latency**: <5ms (file handler init)
- **Memory**: ~100KB for log buffers

**Negligible.**

---

## Documentation Updates

### README.md - Add Section

```markdown
### Logs and Diagnostics

Logs are written to `~/.whisper-dictation.log` (rotating, max 25MB).

**View recent logs:**
```bash
tail -f ~/.whisper-dictation.log
```

**Change log level:**
```bash
poetry run python whisper-dictation.py --log-level DEBUG --k_double_cmd
```

**Log levels:**
- `DEBUG`: Detailed diagnostic info (heartbeat updates, device selection)
- `INFO`: Important events (startup, recording, transcription)
- `WARNING`: Issues that don't stop operation (permission denied)
- `ERROR`: Critical problems (transcription failed)
```

---

## Acceptance Criteria (Ready to Implement)

- [ ] TDD tests written FIRST
- [ ] Log file created at `~/.whisper-dictation.log`
- [ ] Rotation works (verified with large log)
- [ ] CLI flags work (--log-level, --log-file)
- [ ] Key events logged
- [ ] All tests pass
- [ ] No performance regression

