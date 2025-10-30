# User Story: Enhanced Logging & Diagnostics

**ID**: 13-04-00
**Epic**: [13-00-00] Lessons Learned Foundation
**Status**: ✅ **COMPLETED**
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

---

## What We're Building

Centralized logging system with:
1. File output to user's home directory
2. Log rotation with size limits
3. Consistent timestamp format
4. Key diagnostic events logged across all major components
5. Configurable log levels via CLI

---

## Key Assumptions

**A1: Standard Library Rotation is Sufficient**
- RotatingFileHandler handles rotation reliably
- Risk: Rotation fails, log grows unbounded
- Mitigation: Use proven standard library components

**A2: Home Directory is Writable**
- User always has write permission to home directory
- Risk: Permission denied prevents logging
- Mitigation: Graceful fallback if write fails

**A3: File I/O Doesn't Impact Performance**
- Buffered I/O handles logging without blocking
- Risk: Logging adds latency
- Mitigation: Use buffering (default in logging infrastructure)

---

## Acceptance Criteria

### Logging Infrastructure
- [ ] **L1** Logs written to file in user's home directory
- [ ] **L2** Log rotation configured with size limits
- [ ] **L3** Old log files automatically deleted when backup limit exceeded
- [ ] **L4** Timestamp format includes date, time, milliseconds
- [ ] **L5** Log level configurable via CLI
- [ ] **L6** Default log level balances verbosity with usability

### Key Events Logged
- [ ] **E1** Application startup with PID
- [ ] **E2** Lock file operations
- [ ] **E3** Microphone access test results
- [ ] **E4** Recording session start with configuration
- [ ] **E5** Recording session end with duration
- [ ] **E6** Transcription start with model and device
- [ ] **E7** Transcription completion with metadata
- [ ] **E8** Device selection decisions
- [ ] **E9** Watchdog events (stall, restart)
- [ ] **E10** Errors with full traceback
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
2025-10-25 14:23:48.000 - INFO - Recording started, frames_per_buffer=512
2025-10-25 14:23:51.000 - INFO - Transcription complete, text_length=42
```

### Example 2: With Errors
```
2025-10-25 14:23:45.125 - WARNING - Microphone access test failed: PermissionError
2025-10-25 14:23:51.000 - ERROR - Transcription failed: whisper-cli returned code 1
```

---

## Related Tasks

- [ ] [13-04-01] Logging Setup & Configuration
- [ ] [13-04-02] Event Logging Points
- [ ] [13-04-03] Logging Tests

---

## Implementation Context (Not Part of Spec)

**Current Implementation:**
- Log file: `~/.whisper-dictation.log`
- Rotation: 5MB per file, 5 backup files (25MB total)
- Format: `%(asctime)s - %(levelname)s - %(message)s`
- CLI: `--log-level` with choices DEBUG, INFO, WARNING, ERROR
- Setup: `RotatingFileHandler` from `logging.handlers`

**Note**: This implementation context documents current choices which may evolve. The specification above describes stable requirements independent of these implementation details.
