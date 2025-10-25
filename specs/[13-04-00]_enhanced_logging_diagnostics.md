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

### Inspiration
Similar dictation applications use centralized logging with rotating file handlers, consistent timestamp formats, and configurable log levels to balance verbosity with disk usage.

---

## What We're Building

**Centralized logging system** with:
1. File output to user's home directory
2. Log rotation with size limits
3. Consistent timestamp format
4. Key diagnostic events logged across all major components
5. Configurable log levels via command-line interface

---

## Assumptions & Validation

### A1: Standard Library Rotation is Sufficient
- Assumption: Standard library's rotating file handler handles rotation reliably
- Validation: Verify disk space doesn't fill up with reasonable file size limits
- Risk: Rotation mechanism fails, log grows unbounded
- Mitigation: Use proven standard library components

### A2: Home Directory is Writable
- Assumption: User always has write permission to home directory
- Validation: Test with different user accounts and permission configurations
- Risk: Permission denied prevents logging entirely
- Mitigation: Graceful fallback if write fails

### A3: File I/O Doesn't Impact Performance
- Assumption: Buffered I/O handles logging without blocking critical operations
- Validation: Benchmark I/O overhead during recording and transcription
- Risk: Logging adds latency to audio processing
- Mitigation: Use buffering (default in logging infrastructure)

---

## Acceptance Criteria

### Logging Infrastructure
- [ ] **L1** Logs written to designated file in user's home directory
- [ ] **L2** Log rotation configured with reasonable size limits per file and maximum number of backup files
- [ ] **L3** Old log files automatically deleted when backup limit exceeded
- [ ] **L4** Timestamp format includes date, time, and milliseconds
- [ ] **L5** Log level configuration available via command-line interface
- [ ] **L6** Default log level balances verbosity with usability

### Key Events Logged
- [ ] **E1** Application startup with process identification
- [ ] **E2** Lock file operations (creation, validation, cleanup)
- [ ] **E3** Microphone access test results
- [ ] **E4** Recording session start with configuration details
- [ ] **E5** Recording session end with duration information
- [ ] **E6** Transcription start with model and device information
- [ ] **E7** Transcription completion with result metadata
- [ ] **E8** Device selection decisions (CPU vs GPU)
- [ ] **E9** Watchdog events (stall detection, restart attempts)
- [ ] **E10** Errors with full traceback at appropriate severity level
- [ ] **E11** Application shutdown with reason

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

## Design Concepts

### Logging Infrastructure Setup

The system should establish centralized logging during initialization:
- Configure root logger with appropriate level
- Set up file handler with rotation capabilities
- Define consistent timestamp and message formatting
- Optionally configure console output for immediate feedback
- Gracefully handle failures in file handler setup

### CLI Integration

Command-line interface should provide:
- Option to configure log verbosity level
- Option to override default log file location
- Validation of user-provided log level choices

### Key Diagnostic Logging Points

The following major application events should be logged:

**Startup & Initialization:**
- Application startup with process identification
- Lock file operations
- Microphone access test results

**Audio Operations:**
- Recording session start with buffer configuration
- Recording session end with duration
- Warm-up buffer usage (debug level)

**Transcription Operations:**
- Device selection decision and rationale
- Transcription start with model and device
- Command execution details (debug level)
- Transcription completion with metadata
- Transcription errors with context

**Monitoring & Recovery:**
- Watchdog thread initialization
- Stall detection warnings
- Stream restart attempts and outcomes

**Shutdown:**
- Shutdown signal reception
- Cleanup completion

---

## Test Strategy

### Test Coverage Areas

**Logging Infrastructure Tests:**
- Log file creation in expected location
- Log level configuration (DEBUG, INFO, WARNING, ERROR)
- Rotation mechanism creates backup files
- Old logs deleted when backup limit exceeded
- Graceful fallback when file writing fails

**Log Format Tests:**
- Timestamp format consistency
- Log level appears in output
- Message format follows specification

**Event Logging Tests:**
- Application startup events logged
- Lock file operations logged
- Microphone test results logged
- Recording events logged with configuration
- Transcription events logged with metadata
- Error events logged with full traceback
- Shutdown events logged

**Integration Tests:**
- Console output continues to work alongside file logging
- Log rotation works with actual file I/O
- Different log levels filter messages correctly

---

## Affected Components

### Main Application Scripts
Both Python and C++ implementation entry points require:
- Import of logging infrastructure
- Initialization of logging system early in startup
- Integration of CLI arguments for log configuration
- Addition of log statements at key diagnostic points

### Component Integration Points

**Startup & Configuration:**
- Command-line argument parsing
- Logging infrastructure initialization
- Early startup sequence

**Lock File Management:**
- Lock file creation events
- Lock file validation events
- Stale lock file detection

**Audio System:**
- Recording session lifecycle
- Buffer configuration
- Microphone access testing

**Transcription System:**
- Device selection logic
- Transcription session lifecycle
- Error handling

**Monitoring System:**
- Watchdog thread operations
- Stall detection
- Recovery attempts

**Shutdown Handling:**
- Signal reception
- Cleanup operations

### Dependencies

**Standard Library:**
- logging module
- logging.handlers (RotatingFileHandler)
- argparse (argument parsing)

---

## Brittleness Analysis

### Failure Mode 1: Log File Write Permission Issues
**What Happens**: User lacks write permission to log directory
**Impact**: File logging unavailable, but application continues
**Detection**: Exception during file handler initialization
**Prevention**: Wrap file handler setup in error handling
**Recovery**: Graceful fallback to console-only logging

### Failure Mode 2: Disk Space Exhaustion
**What Happens**: Disk fills despite rotation limits
**Impact**: Log writes fail, rotation mechanism cannot create new files
**Detection**: I/O errors during write or rotation
**Prevention**: Size limits prevent unbounded growth
**Recovery**: Oldest logs deleted automatically when space allows

### Failure Mode 3: Concurrent Access to Log Files
**What Happens**: External process holds lock on log file
**Impact**: Individual log entries may be lost
**Detection**: I/O errors on write operations (rare on Unix-like systems)
**Prevention**: Not preventable, uncommon scenario
**Recovery**: Subsequent writes succeed after lock released

### Failure Mode 4: Thread Safety in Signal Handlers
**What Happens**: Signal handler attempts logging while main thread holds logging lock
**Impact**: Potential deadlock during shutdown
**Detection**: Application hang during signal handling
**Prevention**: Logging infrastructure uses thread-safe primitives
**Recovery**: Standard library handles synchronization

### Failure Mode 5: Recursive Logging Errors
**What Happens**: Error during logging triggers additional log attempt
**Impact**: Rapid log growth or stack overflow
**Detection**: Excessive log volume or application crash
**Prevention**: Avoid logging operations within logging infrastructure
**Recovery**: Standard library prevents common recursion patterns

---

## Implementation Approach

### Initial Setup Phase
**Goal**: Establish logging infrastructure without breaking existing functionality
- Implement logging setup function with error handling
- Add command-line arguments for configuration
- Initialize logging early in application startup
- Validate file creation and basic operation

### Event Integration Phase
**Goal**: Add diagnostic logging throughout application
- Instrument startup and shutdown sequences
- Add logging to lock file operations
- Instrument audio recording lifecycle
- Instrument transcription operations
- Add logging to monitoring and recovery systems

### Validation Phase
**Goal**: Verify complete logging functionality
- Confirm log files created and readable
- Exercise rotation mechanism with high-volume logging
- Test different log levels filter correctly
- Verify error handling and fallback behavior
- Update user documentation

---

## Performance Impact

- **CPU overhead**: Minimal due to buffered I/O
- **I/O operations**: Handled asynchronously by logging infrastructure
- **Startup latency**: Negligible file handler initialization
- **Memory footprint**: Small buffer space for log messages

Expected impact on application performance is negligible.

---

## Documentation Requirements

### User Documentation Updates

Documentation should explain:
- Log file location in user's home directory
- How to view logs (tail command or text editor)
- Available log levels and their purposes
- How to configure log level via command-line
- Rotation behavior and disk space limits
- What events are logged at each level

---

## Acceptance Criteria (Ready to Implement)

- [ ] TDD tests written FIRST
- [ ] Log file created in user's home directory
- [ ] Rotation works (verified with high-volume logging)
- [ ] CLI configuration options functional
- [ ] All key events logged per specification
- [ ] All tests pass
- [ ] No performance regression
- [ ] Documentation updated

---

## Implementation Context (Not Part of Spec)

**Current Implementation Structure:**
The codebase currently has two main entry points:
- `whisper-dictation.py` (Python implementation)
- `whisper-dictation-fast.py` (C++ implementation via whisper.cpp)

Both implementations share similar structure with classes like `SpeechTranscriber`, `Recorder`, and `StatusBarApp`.

**Example Implementation Pattern:**
A logging setup function would configure Python's standard `logging` module with `RotatingFileHandler` from `logging.handlers`. Default configuration might use 5MB per file with 5 backup files (25MB total). The log file path could default to `~/.whisper-dictation.log` in the user's home directory.

CLI integration would extend the existing `parse_args()` function to add arguments like `--log-level` with choices `['DEBUG', 'INFO', 'WARNING', 'ERROR']` and optionally `--log-file` to override the default path.

Logging calls would be inserted at strategic points:
- In `setup_lock_file()` for lock management
- In `test_microphone_access()` for microphone checks
- In `Recorder._record_impl()` for recording events
- In `SpeechTranscriber.transcribe()` for transcription events
- In signal handlers for shutdown events

**Note**: This implementation context documents current choices which may evolve. The specification above focuses on WHAT should be achieved, not HOW to implement it.

