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
- Application can run multiple instances simultaneously
- Multiple instances lead to microphone access conflicts
- Resources (audio streams, lock files) may not be released on Ctrl+C
- No mechanism to prevent these issues

### Why This Matters
- **Microphone Conflict**: Two instances reading from same microphone causes audio corruption
- **Resource Leaks**: Unclosed streams lead to memory drain, zombie processes
- **User Impact**: Application hangs, cannot restart without force-kill

---

## What We're Building

### Lock File Mechanism
1. Check for lock file on startup, validate PID
2. Exit if another instance is running
3. Remove stale lock files (dead PID)
4. Create lock file with current PID
5. Remove lock file on shutdown

### Signal Handlers
1. Register handlers for termination signals (Ctrl+C, SIGTERM)
2. Execute cleanup in correct order when signal received
3. Release all resources before exit

---

## Key Assumptions

**A1: PID Lookup Identifies Dead Processes**
- Lock file PID validation correctly identifies stale processes
- Risk: PID reuse could block new instance
- Mitigation: Include timestamp validation

**A2: Signal Handlers Execute Before Hard Kill**
- OS delivers signals for graceful shutdown
- Risk: Hanging processes may not receive signals
- Mitigation: Document force-kill procedures

**A3: Cleanup Handlers Execute Correctly**
- Handlers registered properly and execute before termination
- Risk: Conflicting cleanup operations (atexit vs signal handlers)
- Mitigation: Guard flags prevent duplicate execution

---

## Acceptance Criteria

### Lock File Behavior
- [ ] **A1** Lock file created in user's home directory on startup
- [ ] **A2** Lock file contains current process identifier
- [ ] **A3** App exits with error if lock file references active process
- [ ] **A4** App removes stale lock and continues if PID is dead
- [ ] **A5** Lock file removed on graceful shutdown
- [ ] **A6** Lock file persists if app crashes (stale lock scenario)

### Signal Handling
- [ ] **S1** Ctrl+C causes graceful shutdown (no errors)
- [ ] **S2** SIGTERM causes graceful shutdown
- [ ] **S3** No processes left behind on shutdown
- [ ] **S4** Lock file removed during shutdown
- [ ] **S5** Audio stream closed during shutdown
- [ ] **S6** Application logs shutdown events

### Integration
- [ ] **I1** Works with both whisper-dictation.py and whisper-dictation-fast.py
- [ ] **I2** Compatible with StatusBarApp (rumps)
- [ ] **I3** Compatible with recorder thread
- [ ] **I4** No regressions in existing tests

---

## Behavior Examples

### Example 1: Normal Startup
```bash
$ python whisper-dictation.py --k_double_cmd
[14:23:45.123] Lock file created
[14:23:45.124] Microphone test passed
[14:23:45.125] Listening...
```

### Example 2: Second Instance Blocked
```bash
# Terminal 2
$ python whisper-dictation.py --k_double_cmd
[14:23:50.001] Lock file found (PID 12345)
[14:23:50.002] Process 12345 is alive, aborting
Already running (PID 12345), exiting.
```

### Example 3: Stale Lock Recovery
```bash
$ python whisper-dictation.py --k_double_cmd
[14:23:45.123] Lock file found (PID 12999)
[14:23:45.124] Process 12999 is dead, removing stale lock
[14:23:45.125] Lock file created (PID 13001)
```

### Example 4: Graceful Shutdown
```bash
^C[14:24:00.000] Signal 2 (SIGINT) received
[14:24:00.001] Stopping recording...
[14:24:00.002] Closing audio stream
[14:24:00.003] Lock file removed
[14:24:00.004] Shutdown complete
```

---

## Related Tasks

- [ ] [13-01-01] Lock File Mechanism
- [ ] [13-01-02] Signal Handlers
- [ ] [13-01-03] Lock File Tests

---

## Implementation Context (Not Part of Spec)

**Current Implementation Structure:**
- Lock file path: `~/.whisper-dictation.lock`
- Process checking: `psutil.pid_exists()`
- Signal registration: `signal.signal()` for SIGINT/SIGTERM
- Cleanup registration: `atexit.register()`
- Guard flag: `cleanup_in_progress` to prevent reentrant cleanup

**Note**: This implementation context documents current choices which may evolve. The specification above describes stable requirements independent of these implementation details.

