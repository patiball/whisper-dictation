# User Story: Microphone Proactive Check

**ID**: 13-02-00
**Epic**: [13-00-00] Lessons Learned Foundation
**Status**: Draft
**Priority**: High
**Complexity**: Simple
**Estimate**: 10-15 minutes

---

## User Story

**As a** whisper-dictation user,
**I want** the application to check microphone access permissions on startup,
**So that** I get early feedback if microphone is not available, instead of failing silently during first recording attempt.

---

## Background

### Current Situation
- Microphone permission errors occur during recording (too late)
- User has no feedback about permission issues on startup
- macOS may prompt for permission at first record attempt (disruptive)

### Why This Matters
- **Early Detection**: Catch permission issues before user tries to record
- **Better UX**: User knows immediately if microphone is accessible
- **Debugging**: Helps diagnose permission issues in logs

---

## What We're Building

Simple one-time check at startup using sounddevice to verify:
1. Microphone exists
2. User has permission to access it
3. Settings are valid

Check happens once on startup, not on every recording.

---

## Key Assumptions

**A1: sounddevice.check_input_settings() is Sufficient**
- Function detects permission issues
- Risk: Might not catch all permission types
- Mitigation: Add try/except for any exception

**A2: Check Doesn't Block Startup**
- Check completes in <100ms
- Risk: Slow check blocks app launch
- Mitigation: Documented as acceptable for v1

**A3: Silent Failure is Acceptable**
- App continues even if check fails (with warning)
- Risk: User misses the warning
- Mitigation: Log at WARNING level

---

## Acceptance Criteria

### Microphone Check Execution
- [ ] **A1** Function called on startup before recording listener
- [ ] **A2** Function completes in <100ms
- [ ] **A3** Check happens once per startup
- [ ] **A4** Uses `sounddevice.check_input_settings()`

### Logging & Feedback
- [ ] **L1** Success: log INFO message
- [ ] **L2** Failure: log WARNING with error message
- [ ] **L3** Error message includes reason
- [ ] **L4** Message printed to console

### No Regressions
- [ ] **R1** Recording still works
- [ ] **R2** Existing tests still pass
- [ ] **R3** Works in both whisper-dictation.py and whisper-dictation-fast.py

---

## Behavior Examples

### Example 1: Microphone Accessible
```bash
$ python whisper-dictation.py --k_double_cmd
[14:23:45.123] Lock file created
[14:23:45.124] Microphone access test passed
[14:23:45.125] Listening...
```

### Example 2: Permission Denied
```bash
$ python whisper-dictation.py --k_double_cmd
[14:23:45.123] Lock file created
[14:23:45.124] WARNING: Microphone access test failed: PermissionError: Access denied
[14:23:45.125] Listening...  <- App still starts!
```

User can check System Preferences → Privacy → Microphone and enable whisper-dictation.

### Example 3: No Microphone Device
```bash
$ python whisper-dictation.py --k_double_cmd
[14:23:45.123] Lock file created
[14:23:45.124] WARNING: Microphone access test failed: No audio input devices found
[14:23:45.125] Listening...
```

---

## Related Tasks

- [ ] [13-02-01] Microphone Verification Function
- [ ] [13-02-02] Microphone Check Tests

---

## Implementation Context (Not Part of Spec)

**Current Implementation:**
- Function: `test_microphone_access()`
- Audio library: `sounddevice.check_input_settings()`
- Logging: INFO and WARNING levels
- Called after lock file setup, before event loop

**Note**: This implementation context documents current choices which may evolve. The specification above describes stable requirements independent of these implementation details.
