# Task: Microphone Verification Function

**ID**: 13-02-01
**User Story**: [13-02-00] Microphone Proactive Check
**Complexity**: Simple
**Estimate**: 7 minutes

---

## What

Implement single verification function that tests microphone capability on startup without blocking the application.

---

## Design Approach

**Verification Logic:**
1. Use `sounddevice.check_input_settings()` to query audio system
2. Wrap call in try/except to handle all exception types
3. Log INFO on success, WARNING on failure
4. Print message to console for user visibility
5. Never raise exceptions (graceful degradation)
6. Complete in <100ms

**Integration Point:**
- Called during application initialization
- After lock file setup but before main event loop
- Early in startup sequence for immediate feedback
- Called exactly once per startup

**Error Handling:**
- PermissionError: "Microphone access denied"
- RuntimeError: "No audio input devices found"
- Any other exception: Generic "Microphone access test failed"
- All errors logged with full exception message
- Application continues regardless of result

---

## Failure Modes

**OS Permission Dialog:**
- System displays permission dialog during first check
- Consequence: User must respond to proceed
- Mitigation: Expected behavior, document in README

**Missing Audio Subsystem:**
- sounddevice module not available or broken
- Consequence: Check fails, warning logged
- Recovery: Clear error message helps user install dependency

**Slow Check:**
- Audio subsystem check hangs (rare system issue)
- Risk: App startup stalls
- Mitigation: Documented as acceptable for v1 (future: add timeout)

---

## Acceptance Criteria

- [ ] Function `test_microphone_access()` implemented
- [ ] Uses `sounddevice.check_input_settings()`
- [ ] Success logged at INFO level
- [ ] Failure logged at WARNING level with error message
- [ ] Message printed to console
- [ ] Never raises exceptions
- [ ] Completes in <100ms (measured)
- [ ] Integrated in both whisper-dictation.py and whisper-dictation-fast.py

---

## Implementation Context (Not Part of Spec)

**Current Implementation:**
```python
def test_microphone_access():
    try:
        sd.check_input_settings()
        logging.info("Microphone access test passed.")
        print("Microphone access test passed.")
    except Exception as e:
        logging.warning(f"Microphone access test failed: {e}")
        print(f"WARNING: Microphone access test failed: {e}")
```

Called in main block after lock file setup.
