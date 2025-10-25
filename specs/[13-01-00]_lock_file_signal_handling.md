# User Story: Lock File + Signal Handling

**ID**: 13-01-00
**Epic**: [13-00-00] Lessons Learned Foundation
**Status**: Draft
**Priority**: High
**Complexity**: Medium
**Estimate**: 20-25 minutes

---

## User Story

**As a** whisper-dictation user,
**I want** the application to prevent multiple simultaneous instances and properly clean up resources when shutting down,
**So that** I avoid microphone conflicts and resource leaks (zombie processes, unclosed streams).

---

## Background

### Current Situation
- Aplikacja może być uruchomiona wiele razy jednocześnie
- Wiele instancji prowadzi do konfliktów dostępu do mikrofonu
- Przy Ctrl+C zasoby (audio streams, lock files) mogą nie być zwolnione
- Brak mechanizmu zapobiegającego takim sytuacjom

### Why This Matters
- **Microphone Conflict**: Dwie instancje czytające z tego samego mikrofonu = audio corruption
- **Resource Leaks**: Niezamknięte stream'y = memory drain, zombie procesy
- **User Impact**: Aplikacja "hangs", nie można jej restartować bez force-kill

### Pattern from macos-dictate
Projekt `macos-dictate` rozwiązuje to poprzez:
1. Lock file w `/tmp/dictate.lock` - prosta flaga "aplikacja już działa"
2. PID validation - sprawdzenie czy proces z lock file'a jeszcze żyje
3. Signal handlers - obsługa Ctrl+C, SIGTERM, SIGKILL
4. atexit handlers - funkcje czyszczące przy shutdown

---

## What We're Building

### Lock File Mechanism
```python
LOCK_FILE = Path.home() / ".whisper-dictation.lock"

def setup_lock_file():
    """Check if already running, create lock file"""
    if LOCK_FILE.exists():
        old_pid = int(LOCK_FILE.read_text().strip())
        if psutil.pid_exists(old_pid):
            logging.error(f"Already running (PID {old_pid}), exiting")
            sys.exit(1)
    LOCK_FILE.write_text(str(os.getpid()))
    logging.info("Lock file created")

def cleanup_lock_file():
    """Remove lock file at shutdown"""
    if LOCK_FILE.exists():
        LOCK_FILE.unlink()
        logging.info("Lock file removed")
```

### Signal Handlers
```python
def signal_exit_handler(signum, frame):
    """Handle Ctrl+C, SIGTERM gracefully"""
    logging.info(f"Signal {signum} received, shutting down...")

    # Set flags to stop recording/transcribing
    global watchdog_active
    watchdog_active = False

    # Cleanup in reverse order
    cleanup_audio_stream()
    cleanup_lock_file()

    logging.info("Shutdown complete")
    sys._exit(0)

# Register handlers
signal.signal(signal.SIGINT, signal_exit_handler)   # Ctrl+C
signal.signal(signal.SIGTERM, signal_exit_handler)  # kill -TERM
```

---

## Assumptions & Validation

### A1: PID File Based Locking is Sufficient
- Assumption: File-based PID checking is safe for this use case
- Validation: Verify `psutil.pid_exists()` correctly detects dead processes in macOS
- Risk: PID reuse (unlikely but possible) - mitigation: check lock file timestamp

### A2: Signal Handlers Receive Control
- Assumption: SIGINT/SIGTERM handlers will be called before hard shutdown
- Validation: Manual test with Ctrl+C and `kill -TERM $(pgrep whisper-dictation)`
- Risk: If process hangs in C call, signal may not be delivered - mitigation: user can force-kill

### A3: atexit Handlers Run Before Exit
- Assumption: Python's atexit module is reliable for cleanup
- Validation: Test that functions registered with atexit are called
- Risk: If signal handler calls `os._exit()`, atexit bypassed - mitigation: use `sys.exit()` instead

---

## Acceptance Criteria

### Lock File Behavior
- [ ] **A1** Lock file created at `~/.whisper-dictation.lock` on startup
- [ ] **A2** Lock file contains current process PID
- [ ] **A3** On startup, if lock file exists with valid PID: app exits with message "Already running (PID X)"
- [ ] **A4** On startup, if lock file exists with dead PID: app continues and updates lock file
- [ ] **A5** Lock file removed when application exits gracefully (Ctrl+C, SIGTERM)
- [ ] **A6** Lock file persists if app crashes (so user must manually clean or restart)

### Signal Handling
- [ ] **S1** Ctrl+C causes graceful shutdown (no errors)
- [ ] **S2** SIGTERM causes graceful shutdown
- [ ] **S3** During shutdown, no processes left behind (ps aux | grep whisper-dictation)
- [ ] **S4** Lock file removed during shutdown
- [ ] **S5** Audio stream closed during shutdown (no hanging file descriptors)
- [ ] **S6** Application logs shutdown events before exit

### Integration with Existing Code
- [ ] **I1** Works with both whisper-dictation.py and whisper-dictation-fast.py
- [ ] **I2** Compatible with StatusBarApp (rumps) - menu bar shutdown works too
- [ ] **I3** Compatible with recorder thread - recordings stop cleanly
- [ ] **I4** Compatible with existing device management code

### No Regressions
- [ ] **R1** Normal startup/stop flow unchanged
- [ ] **R2** Recording still works
- [ ] **R3** Transcription still works
- [ ] **R4** Existing tests still pass

---

## Behavior Examples

### Example 1: Normal Startup
```bash
$ python whisper-dictation.py --k_double_cmd
[14:23:45.123] Lock file created
[14:23:45.124] Microphone test passed
[14:23:45.125] Listening...
```

Lock file exists: `~/.whisper-dictation.lock` contains PID (e.g., 12345)

### Example 2: Try to Start Second Instance
```bash
# Terminal 1 - still running
$ python whisper-dictation.py --k_double_cmd

# Terminal 2 - try to start again
$ python whisper-dictation.py --k_double_cmd
[14:23:50.001] Lock file found (PID 12345)
[14:23:50.002] Process 12345 is alive, aborting
Already running (PID 12345), exiting.
```

Terminal 2 exits with code 1.

### Example 3: Previous Instance Crashed
```bash
# Old lock file exists from crashed instance
$ cat ~/.whisper-dictation.lock
12999  # Dead process

# New startup
$ python whisper-dictation.py --k_double_cmd
[14:23:45.123] Lock file found (PID 12999)
[14:23:45.124] Process 12999 is dead, removing stale lock
[14:23:45.125] Lock file created (PID 13001)
[14:23:45.126] Listening...
```

Application starts successfully, old lock replaced.

### Example 4: Graceful Shutdown
```bash
# Running
[14:23:45.123] Listening...

# User presses Ctrl+C
^C[14:24:00.000] Signal 2 (SIGINT) received
[14:24:00.001] Stopping recording...
[14:24:00.002] Closing audio stream
[14:24:00.003] Lock file removed
[14:24:00.004] Shutdown complete

$ echo $?
0
```

Exit code 0 (success), lock file gone.

---

## Design & Implementation

### File Structure
```
whisper-dictation.py (and fast version)
├── Imports
│   ├── psutil (for PID checking)
│   ├── signal (for handlers)
│   ├── atexit (for cleanup)
│   └── logging (for messages)
│
├── Constants
│   └── LOCK_FILE = Path.home() / ".whisper-dictation.lock"
│
├── Functions (Global)
│   ├── setup_lock_file()         [NEW]
│   ├── cleanup_lock_file()       [NEW]
│   ├── cleanup_audio_stream()    [NEW]
│   └── signal_exit_handler()     [NEW]
│
├── Main Execution
│   ├── setup_lock_file()         [CALL ON STARTUP]
│   ├── signal.signal(..., handler)  [REGISTER ON STARTUP]
│   ├── atexit.register(cleanup)  [REGISTER ON STARTUP]
│   └── try/except main loop
│
└── Classes (Unchanged)
    ├── SpeechTranscriber
    ├── Recorder
    ├── StatusBarApp
    └── ...
```

### Pseudo-Code

**Module-level (top of file):**
```python
import psutil
import signal
import atexit
import os
import sys
import logging
from pathlib import Path

LOCK_FILE = Path.home() / ".whisper-dictation.lock"

def setup_lock_file():
    """
    Check if already running, create/update lock file.
    Exit if another instance is alive.
    """
    if LOCK_FILE.exists():
        try:
            old_pid = int(LOCK_FILE.read_text().strip())
            if psutil.pid_exists(old_pid):
                logging.error(f"Another instance is already running (PID {old_pid})")
                print(f"Another instance is already running (PID {old_pid}), exiting.")
                sys.exit(1)
            else:
                logging.warning(f"Stale lock file found (PID {old_pid} is dead), removing")
        except (ValueError, OSError) as e:
            logging.warning(f"Invalid lock file: {e}, removing")

    # Write current PID to lock file
    LOCK_FILE.write_text(str(os.getpid()))
    logging.info("Lock file created")

def cleanup_lock_file():
    """Remove lock file at shutdown."""
    try:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()
            logging.info("Lock file removed")
    except OSError as e:
        logging.warning(f"Failed to remove lock file: {e}")

def cleanup_audio_stream():
    """Close audio stream if open."""
    global recorder
    if recorder is not None:
        try:
            recorder.stop()
            logging.info("Audio stream stopped")
        except Exception as e:
            logging.warning(f"Error stopping recorder: {e}")

def signal_exit_handler(signum, frame):
    """Handle signals gracefully."""
    logging.info(f"Signal {signum} received, shutting down...")

    # Set global flags to stop loops
    global watchdog_active, recording, transcribing
    watchdog_active = False
    recording = False
    transcribing = False

    # Call cleanup functions (in order)
    cleanup_audio_stream()
    cleanup_lock_file()

    logging.info("Shutdown complete")
    sys._exit(0)
```

**In main execution (before the try/except loop):**
```python
if __name__ == "__main__":
    # Setup logging first
    logging.basicConfig(...)

    # Lock file handling
    setup_lock_file()

    # Register cleanup on normal exit
    atexit.register(cleanup_lock_file)
    atexit.register(cleanup_audio_stream)

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_exit_handler)
    signal.signal(signal.SIGTERM, signal_exit_handler)

    # Rest of initialization
    app = StatusBarApp()

    try:
        # Main event loop
        app.run()
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
```

---

## Test Cases (TDD - Write Tests FIRST)

### Test Suite: `tests/test_lock_file.py`

```python
import pytest
import os
from pathlib import Path
import psutil
import subprocess
import sys
import time

# Imports from whisper-dictation.py (need to be exposed)
from whisper_dictation_module import setup_lock_file, cleanup_lock_file, LOCK_FILE

class TestLockFileBasics:
    """Test lock file creation and cleanup"""

    def test_lock_file_created_on_startup(self):
        """Lock file should be created with current PID"""
        setup_lock_file()
        assert LOCK_FILE.exists()
        pid = int(LOCK_FILE.read_text().strip())
        assert pid == os.getpid()
        cleanup_lock_file()

    def test_lock_file_cleaned_up_on_exit(self):
        """Lock file should be removed on cleanup"""
        setup_lock_file()
        assert LOCK_FILE.exists()
        cleanup_lock_file()
        assert not LOCK_FILE.exists()

    def test_dead_pid_allows_startup(self):
        """If lock file PID is dead, app should start"""
        # Write a dead PID
        dead_pid = 99999999
        LOCK_FILE.write_text(str(dead_pid))

        # Should not crash, should create new lock
        setup_lock_file()

        assert LOCK_FILE.exists()
        new_pid = int(LOCK_FILE.read_text().strip())
        assert new_pid == os.getpid()
        cleanup_lock_file()

class TestLockFileMultiInstance:
    """Test behavior with multiple instances"""

    def test_second_instance_cannot_start(self):
        """Second instance should exit when first is running"""
        # This test requires subprocess - see integration test below
        pass  # Deferred to integration test

class TestSignalHandling:
    """Test signal handlers"""

    def test_signal_handler_registered(self):
        """Signal handlers should be registered"""
        import signal
        # Get current handler
        handler = signal.signal(signal.SIGINT, signal.SIG_DFL)
        # Restore original
        signal.signal(signal.SIGINT, handler)
        # Handler should not be default
        assert handler != signal.SIG_DFL

    def test_cleanup_on_signal(self):
        """Cleanup should be called on signal"""
        setup_lock_file()
        assert LOCK_FILE.exists()

        # Simulate signal handler cleanup
        cleanup_audio_stream()
        cleanup_lock_file()

        assert not LOCK_FILE.exists()

class TestStaleFiles:
    """Test handling of corrupted lock files"""

    def test_invalid_pid_in_lock_file(self):
        """Invalid PID should be treated as stale"""
        LOCK_FILE.write_text("not_a_number")

        # Should handle gracefully
        setup_lock_file()

        # Should create new valid lock
        assert LOCK_FILE.exists()
        pid = int(LOCK_FILE.read_text().strip())
        assert pid == os.getpid()
        cleanup_lock_file()

    def test_empty_lock_file(self):
        """Empty lock file should be treated as stale"""
        LOCK_FILE.write_text("")

        # Should handle gracefully
        setup_lock_file()

        assert LOCK_FILE.exists()
        cleanup_lock_file()
```

### Integration Test: `tests/test_lock_file_integration.py`

```python
import pytest
import subprocess
import sys
import time
from pathlib import Path

LOCK_FILE = Path.home() / ".whisper-dictation.lock"

class TestMultiInstanceIntegration:
    """Integration tests with real processes"""

    def test_second_instance_exits_gracefully(self):
        """Start app twice, second should exit with code 1"""
        # Clean up first
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()

        # Start first instance (in background)
        proc1 = subprocess.Popen(
            [sys.executable, "whisper-dictation.py", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(0.5)  # Let it create lock file

        # Try to start second instance
        proc2 = subprocess.run(
            [sys.executable, "whisper-dictation.py", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Second should exit with code 1
        assert proc2.returncode == 1
        assert b"already running" in proc2.stderr.lower() or b"Already running" in proc2.stdout

        # Clean up
        proc1.terminate()
        proc1.wait(timeout=5)
        assert not LOCK_FILE.exists()

    def test_ctrl_c_removes_lock_file(self):
        """Ctrl+C should remove lock file"""
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()

        # Start process
        proc = subprocess.Popen(
            [sys.executable, "whisper-dictation.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(0.5)  # Let it start
        assert LOCK_FILE.exists()

        # Send Ctrl+C
        proc.send_signal(signal.SIGINT)
        proc.wait(timeout=5)

        # Lock file should be gone
        assert not LOCK_FILE.exists()
```

---

## File Changes Required

### `whisper-dictation.py`

**Add at top (after imports):**
```python
import psutil
import signal
import atexit
from pathlib import Path

LOCK_FILE = Path.home() / ".whisper-dictation.lock"
```

**Add these functions (before main class definitions):**
```python
def setup_lock_file():
    """Check if already running, create lock file"""
    if LOCK_FILE.exists():
        try:
            old_pid = int(LOCK_FILE.read_text().strip())
            if psutil.pid_exists(old_pid):
                logging.error(f"Another instance is already running (PID {old_pid})")
                print(f"Another instance is already running (PID {old_pid}), exiting.")
                sys.exit(1)
            else:
                logging.warning(f"Stale lock file found (PID {old_pid} is dead), removing")
        except (ValueError, OSError) as e:
            logging.warning(f"Invalid lock file: {e}, removing")

    LOCK_FILE.write_text(str(os.getpid()))
    logging.info("Lock file created")

def cleanup_lock_file():
    """Remove lock file at shutdown"""
    try:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()
            logging.info("Lock file removed")
    except OSError as e:
        logging.warning(f"Failed to remove lock file: {e}")

def cleanup_audio_stream():
    """Close audio stream if open"""
    global recorder
    if 'recorder' in globals() and recorder is not None:
        try:
            recorder.stop()
            logging.info("Audio stream stopped")
        except Exception as e:
            logging.warning(f"Error stopping recorder: {e}")

def signal_exit_handler(signum, frame):
    """Handle signals gracefully"""
    logging.info(f"Signal {signum} received, shutting down...")
    global watchdog_active, recording, transcribing
    watchdog_active = False
    if 'recording' in globals():
        recording = False
    if 'transcribing' in globals():
        transcribing = False
    cleanup_audio_stream()
    cleanup_lock_file()
    logging.info("Shutdown complete")
    os._exit(0)
```

**In main block (before app.run()):**
```python
if __name__ == "__main__":
    setup_lock_file()
    atexit.register(cleanup_lock_file)
    atexit.register(cleanup_audio_stream)
    signal.signal(signal.SIGINT, signal_exit_handler)
    signal.signal(signal.SIGTERM, signal_exit_handler)

    app = StatusBarApp()
    app.run()
```

### `whisper-dictation-fast.py`

**Identyczne zmiany jak wyżej** (must keep both versions in sync)

### `requirements.txt`

Verify `psutil` is already there (should be):
```
psutil>=5.9.0
```

---

## Brittleness Analysis

### Failure Mode 1: Lock File on Shared Storage
**Scenario**: User home on NFS → lock file flaky
**Detection**: Lock file write timeouts
**Consequence**: Race condition where two instances start
**Prevention**: Use reliable check (stat before write)
**Recovery**: Retry lock file creation 3x before giving up
**Mitigation**: Add retry logic with exponential backoff

### Failure Mode 2: Permission Denied Removing Lock
**Scenario**: Running as different user, can't delete lock file from previous user
**Detection**: OSError on unlink
**Consequence**: Cleanup incomplete, stale lock persists
**Prevention**: Check permissions before creating lock file
**Recovery**: Log warning, don't crash
**Mitigation**: Implemented in cleanup_lock_file() with try/except

### Failure Mode 3: Signal Handler Interrupts During Cleanup
**Scenario**: User presses Ctrl+C twice during shutdown
**Detection**: Signal handler reentrancy
**Consequence**: Cleanup called twice, potential race condition
**Prevention**: Set flag before calling cleanup
**Recovery**: Check flag, skip if already cleaning
**Mitigation**: Use atomic flag (e.g., `cleanup_in_progress`)

### Failure Mode 4: atexit vs signal Handler
**Scenario**: Both atexit and signal handler try to cleanup lock file
**Detection**: Double removal
**Consequence**: Error in logs but harmless
**Prevention**: Use flag to prevent double cleanup
**Recovery**: Already handled with try/except
**Mitigation**: Add guard flag `_cleanup_done`

### Failure Mode 5: Lock File PID Reuse
**Scenario**: Old PID recycled by OS for new process
**Detection**: Different process with same old PID
**Consequence**: Block new instance of whisper-dictation
**Prevention**: Check PID + lock file timestamp (age < 1 hour)
**Recovery**: Assume stale if >1 hour old
**Mitigation**: Add timestamp check in lock file content

### Failure Mode 6: Running as sudo
**Scenario**: `sudo python whisper-dictation.py` → lock file owned by root
**Detection**: Permission denied for next user
**Consequence**: Second instance (different user) can't start
**Prevention**: Document not to use sudo
**Recovery**: Manual cleanup `sudo rm ~/.whisper-dictation.lock`
**Mitigation**: Add check for euid, warn if running as root

---

## Rollout Strategy

### Phase 1: Development & Testing
1. Write all test cases first (TDD)
2. Implement lock file mechanism
3. Implement signal handlers
4. Run pytest tests locally
5. Manual test: 2 instances scenario
6. Manual test: Ctrl+C shutdown

### Phase 2: Integration
1. Merge with other Lessons Learned features
2. Run full test suite
3. Manual end-to-end test

### Phase 3: Validation
1. Monitor for lock file issues in real usage
2. Collect feedback
3. Adjust if needed

---

## Performance Impact

- **Lock file creation**: <1ms (single file write)
- **Lock file check**: <5ms (read + PID lookup via psutil)
- **Signal handler registration**: <1ms (one-time at startup)
- **Signal handler execution**: <100ms (cleanup operations)

**Total startup impact**: <10ms

**Negligible.**

---

## Documentation Updates Required

### README.md - Add Section

```markdown
### Troubleshooting

#### "Another instance is already running (PID X)"

If you see this error when starting whisper-dictation, it means an instance is already running.

**Solutions:**
1. If it's running, kill it: `pkill -f whisper-dictation`
2. If it crashed, remove the lock file: `rm ~/.whisper-dictation.lock`
3. To see if process is alive: `ps aux | grep whisper-dictation`

#### Stale Lock File

If the app crashed and the lock file wasn't cleaned up:
```bash
rm ~/.whisper-dictation.lock
```
(The app checks if the PID is alive, so this shouldn't block startup)
```

---

## Acceptance Criteria (Ready to Implement)

- [ ] All TDD tests written BEFORE implementation starts
- [ ] Lock file mechanism works (A1-A6)
- [ ] Signal handlers work (S1-S6)
- [ ] Integration tests pass
- [ ] Manual testing scenarios pass
- [ ] No regressions in existing tests
- [ ] README updated with troubleshooting

---

## Dependencies

- `psutil>=5.9.0` (already in requirements)
- `signal` (stdlib)
- `atexit` (stdlib)
- `pathlib` (stdlib)
- `logging` (stdlib)

No new external dependencies.

