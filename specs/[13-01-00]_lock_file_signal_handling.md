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

**Core Behavior:**
1. On application startup, check if lock file exists
2. If lock file exists, verify the process it references is still alive
3. If process is alive, exit with error message (another instance is running)
4. If process is dead, remove stale lock file and continue
5. Create new lock file with current process ID
6. On shutdown, remove lock file

**Lock File Content:**
- Simple text file containing the process ID of the running instance
- Located in user's home directory with hidden file naming convention

### Signal Handlers

**Core Behavior:**
1. Register handlers for common termination signals (Ctrl+C, SIGTERM, etc.)
2. On signal receipt, log the shutdown event
3. Stop all monitoring threads and recording operations
4. Execute cleanup operations in correct order
5. Release all file locks and resources
6. Exit cleanly without leaving processes or files behind

**Cleanup Order:**
- Stop monitoring/recording operations
- Release audio resources
- Remove lock file
- Log final shutdown message
- Exit with appropriate code

---

## Assumptions & Validations

### A1: Process Validity Can Be Determined from Lock File
- **Assumption**: Lock file contains sufficient information to determine if original process still exists
- **Validation**: PID lookup mechanism correctly identifies dead processes on target OS
- **Risk**: PID reuse could allow new process to be blocked by very old lock file
- **Mitigation**: Lock file should include timestamp to detect stale entries

### A2: Signal Handlers Receive Control for Graceful Shutdown
- **Assumption**: Operating system will deliver termination signals before hard process kill
- **Validation**: Test graceful shutdown with both programmatic and user-initiated signals
- **Risk**: Process hanging in system calls could prevent signal delivery
- **Mitigation**: Provide user documentation for force-kill procedures

### A3: Cleanup Handlers Execute in Correct Order
- **Assumption**: Cleanup handlers registered properly and execute before process termination
- **Validation**: Verify all registered cleanup handlers execute and lock file is removed
- **Risk**: Conflicting cleanup operations (e.g., atexit vs signal handlers) could cause issues
- **Mitigation**: Use guard flags to prevent duplicate cleanup execution

---

## Acceptance Criteria

### Lock File Behavior
- [ ] **A1** Lock file created in user's home directory on startup
- [ ] **A2** Lock file contains current process identifier
- [ ] **A3** On startup, if lock file references active process: app exits with error message
- [ ] **A4** On startup, if lock file references dead process: app removes stale lock and continues
- [ ] **A5** Lock file removed when application shuts down gracefully
- [ ] **A6** Lock file persists if app crashes without cleanup (stale lock scenario)

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

## Design Principles

### Modular Cleanup
- Separate concerns: Lock file cleanup, audio resource cleanup, logging
- Cleanup functions can be called independently
- Guard against repeated cleanup attempts

### Signal Safety
- Signal handlers should be minimal and non-blocking
- Use atomic flags to communicate with main loop
- Ensure all registered handlers execute before process termination

### Error Handling
- File operations should gracefully handle missing files (don't error on re-cleanup)
- Process validation should handle invalid lock file content
- Cleanup should not prevent shutdown (errors logged but not fatal)

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

## Affected Components

The following components require modifications to implement lock file and signal handling:

- **Application Entry Point**: Initialize lock file on startup before main loop
- **Main Event Loop**: Register signal handlers on initialization
- **Shutdown Path**: Ensure cleanup handlers are registered and execute on exit
- **Both Versions**: Changes must be synchronized between Python and C++ entry points
- **Dependencies**: Verify required process management and signal handling libraries available

### Integration Points

1. **On Startup**: Lock file created before any other initialization (earliest possible point)
2. **Before Main Loop**: Signal handlers registered for graceful termination
3. **During Shutdown**: Cleanup handlers execute in reverse order of registration
4. **Error Path**: Cleanup executed even if exception occurs before normal exit

---

## Failure Modes & Durability

### Failure Mode 1: Concurrent File System Access
**Scenario**: Multiple processes attempt lock file creation simultaneously
- **Detection**: Race condition where both processes see file doesn't exist
- **Consequence**: Both instances start, microphone conflicts occur
- **Prevention**: Atomic lock file operations with validation
- **Recovery**: File system semantics prevent simultaneous writes
- **Mitigation**: Verify lock file content after creation, check PID again after write

### Failure Mode 2: Permission Issues on Lock File
**Scenario**: Lock file ownership changed (e.g., different user or elevated privileges)
- **Detection**: Permission error when attempting cleanup
- **Consequence**: Stale lock remains but non-fatal (next startup resolves it)
- **Prevention**: Lock file in user's home directory avoids cross-user issues
- **Recovery**: Graceful error handling in cleanup (log warning, continue)
- **Mitigation**: Document sudo usage not supported

### Failure Mode 3: Duplicate Cleanup Execution
**Scenario**: Both signal handler and atexit handler attempt cleanup
- **Detection**: Second cleanup attempt on already-removed lock file
- **Consequence**: File not found error (harmless but logs noise)
- **Prevention**: Guard flag prevents reentrant execution
- **Recovery**: Cleanup operations idempotent (remove non-existent files is safe)
- **Mitigation**: Use guard flag `_cleanup_done` to prevent duplicate execution

### Failure Mode 4: PID Reuse by Operating System
**Scenario**: Old process PID recycled for completely unrelated process
- **Detection**: New unrelated process has same PID as old lock file
- **Consequence**: New whisper-dictation instance blocked incorrectly
- **Prevention**: Include timestamp in lock file to detect stale entries
- **Recovery**: Treat lock file as stale if creation time significantly in past
- **Mitigation**: Add timestamp validation (consider >1 hour old as stale)

### Failure Mode 5: Signal During Critical Cleanup
**Scenario**: User sends multiple signals (e.g., repeated Ctrl+C) during shutdown
- **Detection**: Signal handler called while previous handler still executing
- **Consequence**: Potential race condition in cleanup
- **Prevention**: Use atomic flags for cleanup coordination
- **Recovery**: Guard flag ensures cleanup executes once
- **Mitigation**: Signal handler checks flag before proceeding

---

## Implementation Approach

### TDD-First Testing
- Write comprehensive test suite before implementation
- Test coverage includes: normal operation, edge cases, error conditions
- Integration tests verify behavior with real process spawning

### Phased Implementation
1. **Lock File Mechanism**: Implement PID-based mutual exclusion
2. **Signal Handlers**: Register and execute cleanup handlers
3. **Integration**: Verify both mechanisms work together without conflicts

### Validation Strategy
- Unit tests verify lock file creation, validation, cleanup
- Integration tests verify multi-instance scenarios
- Manual tests verify user-visible behavior (startup messages, cleanup)
- Stress tests verify no resource leaks

---

## Performance Impact

- **Lock file creation**: <1ms (single file write)
- **Lock file check**: <5ms (read + PID lookup via psutil)
- **Signal handler registration**: <1ms (one-time at startup)
- **Signal handler execution**: <100ms (cleanup operations)

**Total startup impact**: <10ms

**Negligible.**

---

## Documentation Requirements

- **Troubleshooting Guide**: Explain "already running" error and how to resolve
- **Lock File Location**: Document where lock file is stored
- **Manual Cleanup**: Document how to manually remove stale lock file if needed
- **Multi-Instance Behavior**: Clarify that only one instance can run at a time

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

## Technical Requirements

- **Process Management Capability**: Ability to check if a process with given ID is still alive
- **Signal Handling**: Operating system support for signal handlers (SIGINT, SIGTERM, etc.)
- **Cleanup Registration**: Mechanism to register cleanup handlers on program exit
- **File Operations**: Write, read, and delete files in user's home directory
- **No New External Dependencies**: Use existing or stdlib modules

---

## Implementation Context (Not Part of Spec)

**Current Implementation Structure:**
- Lock file path: `~/.whisper-dictation.lock` (user's home directory)
- Process checking: `psutil.pid_exists()` for PID validation
- Signal registration: `signal.signal()` for SIGINT/SIGTERM handlers
- Cleanup registration: `atexit.register()` for exit-time cleanup
- Cleanup in signal handler: `os._exit()` for immediate termination
- Guard flag: `cleanup_in_progress` to prevent reentrant cleanup

**Note**: This implementation context documents current choices which may evolve. The specification above describes stable requirements independent of these implementation details.

