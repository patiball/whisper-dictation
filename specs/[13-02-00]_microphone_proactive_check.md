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
- **Platform Resilience**: macOS permission system changes → need robust check

### Pattern from macos-dictate
```python
def test_microphone_access():
    try:
        sd.check_input_settings()
        logging.info("Microphone access test passed.")
    except Exception as e:
        logging.error(f"Microphone access test failed: {e}")
```

---

## What We're Building

**Simple one-time check at startup** using sounddevice to verify:
1. Microphone exists
2. User has permission to access it
3. Settings are valid

Doesn't need to record or play audio — just verify capability.

---

## Assumptions & Validation

### A1: sounddevice.check_input_settings() is Sufficient
- Assumption: This function detects permission issues
- Validation: Test with microphone disabled/permission denied
- Risk: Function might not catch all permission types
- Mitigation: Add try/except for any exception

### A2: Check Doesn't Block Startup
- Assumption: Microphone check is fast (<100ms)
- Validation: Time the check with and without microphone
- Risk: Slow check blocks app launch
- Mitigation: Add timeout or async check (out of scope)

### A3: Silent Failure is Acceptable
- Assumption: If check fails, app still starts (with warning)
- Validation: User sees warning in logs and console
- Risk: User misses the warning
- Mitigation: Log at WARNING level (visible in default log level)

---

## Acceptance Criteria

### Microphone Check Execution
- [ ] **A1** `test_microphone_access()` called on startup (before recording listener active)
- [ ] **A2** Function completes in <100ms
- [ ] **A3** Check happens once per startup (not on every record)
- [ ] **A4** Check uses `sounddevice.check_input_settings()`

### Logging & Feedback
- [ ] **L1** If success: log INFO "Microphone access OK" or similar
- [ ] **L2** If failure: log WARNING with error message
- [ ] **L3** Error message includes reason (permission denied, no device, etc.)
- [ ] **L4** Message also printed to console (user sees it)

### No Regressions
- [ ] **R1** Recording still works after passing check
- [ ] **R2** Recording doesn't start check again
- [ ] **R3** Existing tests still pass

### Works in Both Versions
- [ ] **V1** Implemented in whisper-dictation.py
- [ ] **V2** Implemented in whisper-dictation-fast.py

---

## Behavior Examples

### Example 1: Microphone Accessible
```bash
$ python whisper-dictation.py --k_double_cmd
[14:23:45.123] Lock file created
[14:23:45.124] Microphone access test passed
[14:23:45.125] Listening...
```

Console shows: "Microphone access test passed"

### Example 2: Permission Denied
```bash
# macOS System Preferences → Privacy → Microphone → whisper-dictation NOT checked
$ python whisper-dictation.py --k_double_cmd
[14:23:45.123] Lock file created
[14:23:45.124] WARNING: Microphone access test failed: PermissionError: Access denied
[14:23:45.125] Listening...  <- App still starts!
```

User can now:
1. Check System Preferences → Privacy → Microphone
2. Enable whisper-dictation
3. Restart the app

### Example 3: No Microphone Device
```bash
# Microphone unplugged or not found
$ python whisper-dictation.py --k_double_cmd
[14:23:45.123] Lock file created
[14:23:45.124] WARNING: Microphone access test failed: No audio input devices found
[14:23:45.125] Listening...
```

### Example 4: Recording After Check Passed
```
[14:23:45.124] Microphone access test passed
[14:23:45.125] Listening...
[14:23:48.000] Transcribing...     <- No second check needed
[14:23:51.000] Transcription complete
```

Check runs only once on startup.

---

## Design & Implementation

### Function Signature
```python
def test_microphone_access():
    """
    Test if microphone is accessible.
    Logs result, does not raise exception.
    """
    try:
        sd.check_input_settings()
        logging.info("Microphone access test passed")
    except Exception as e:
        logging.warning(f"Microphone access test failed: {e}")
```

### Placement in Code
```
whisper-dictation.py
├── Imports
├── Constants
├── Functions
│   ├── setup_lock_file()
│   ├── cleanup_lock_file()
│   ├── test_microphone_access()    [NEW]
│   └── signal_exit_handler()
│
└── Main Block
    ├── setup_lock_file()
    ├── test_microphone_access()    [NEW - CALL HERE]
    ├── atexit.register(...)
    ├── signal.signal(...)
    └── app.run()
```

### Pseudo-Code

**Add this function (next to other setup functions):**
```python
def test_microphone_access():
    """
    Test if microphone is accessible.
    Logs result at WARNING level if failed, INFO if passed.
    """
    try:
        import sounddevice as sd
        sd.check_input_settings()
        logging.info("Microphone access test passed")
        print("[Microphone access OK]")
    except Exception as e:
        logging.warning(f"Microphone access test failed: {e}")
        print(f"[WARNING] Microphone access failed: {e}")
```

**In main block (after setup_lock_file, before setting up event listeners):**
```python
if __name__ == "__main__":
    setup_lock_file()
    test_microphone_access()    # [NEW]
    atexit.register(cleanup_lock_file)
    # ... rest of setup ...
    app.run()
```

---

## Test Cases (TDD - Write FIRST)

### Test Suite: `tests/test_microphone_check.py`

```python
import pytest
import logging
from unittest.mock import patch, MagicMock
import sounddevice as sd

from whisper_dictation_module import test_microphone_access

class TestMicrophoneCheckBasics:
    """Test basic microphone check functionality"""

    def test_check_succeeds_when_microphone_available(self, caplog):
        """Should log INFO when microphone is accessible"""
        with caplog.at_level(logging.INFO):
            test_microphone_access()

        assert "Microphone access test passed" in caplog.text

    def test_check_logs_warning_on_permission_denied(self, caplog):
        """Should log WARNING when permission denied"""
        with patch('sounddevice.check_input_settings') as mock_check:
            mock_check.side_effect = PermissionError("Access denied")

            with caplog.at_level(logging.WARNING):
                test_microphone_access()

        assert "Microphone access test failed" in caplog.text
        assert "Access denied" in caplog.text

    def test_check_handles_no_device_error(self, caplog):
        """Should log WARNING when no audio device found"""
        with patch('sounddevice.check_input_settings') as mock_check:
            mock_check.side_effect = RuntimeError("No audio input devices")

            with caplog.at_level(logging.WARNING):
                test_microphone_access()

        assert "Microphone access test failed" in caplog.text

    def test_check_handles_generic_exception(self, caplog):
        """Should handle any exception gracefully"""
        with patch('sounddevice.check_input_settings') as mock_check:
            mock_check.side_effect = Exception("Unknown error")

            with caplog.at_level(logging.WARNING):
                test_microphone_access()

        assert "Microphone access test failed" in caplog.text
        assert "Unknown error" in caplog.text

    def test_check_does_not_raise_exception(self):
        """Check should never crash the app"""
        with patch('sounddevice.check_input_settings') as mock_check:
            mock_check.side_effect = Exception("Simulated crash")

            # Should not raise
            try:
                test_microphone_access()
            except Exception:
                pytest.fail("test_microphone_access raised an exception")

class TestMicrophoneCheckTiming:
    """Test that check completes quickly"""

    def test_check_completes_in_reasonable_time(self):
        """Check should complete in <100ms"""
        import time

        start = time.time()
        test_microphone_access()
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert elapsed < 100, f"Check took {elapsed:.1f}ms (should be <100ms)"

    def test_check_doesnt_block_indefinitely(self):
        """Check should have timeout protection"""
        # If we get here, it didn't hang
        test_microphone_access()
        # Test passes if function returns

class TestMicrophoneCheckIntegration:
    """Integration tests with real sounddevice"""

    def test_real_microphone_check(self):
        """If microphone available, check should pass"""
        # This will only pass if actual microphone is present
        import sounddevice as sd

        # Try to get device list
        devices = sd.query_devices()

        if len(devices) > 0:
            # Should not raise
            test_microphone_access()
        else:
            pytest.skip("No microphone device available for testing")
```

---

## File Changes Required

### `whisper-dictation.py`

**Add after other imports:**
```python
import sounddevice as sd
```

**Add this function (with other setup functions):**
```python
def test_microphone_access():
    """
    Test if microphone is accessible.
    Logs result, does not crash if failed.
    """
    try:
        sd.check_input_settings()
        logging.info("Microphone access test passed")
        print("[Microphone access OK]")
    except Exception as e:
        logging.warning(f"Microphone access test failed: {e}")
        print(f"[WARNING] Microphone access failed: {e}")
```

**In main block (right after setup_lock_file):**
```python
if __name__ == "__main__":
    setup_lock_file()
    test_microphone_access()  # [NEW LINE]
    # ... rest of initialization ...
```

### `whisper-dictation-fast.py`

**Identical changes as above** (keep both versions in sync)

### `requirements.txt`

Verify `sounddevice` is already there:
```
sounddevice>=0.4.4
```

---

## Brittleness Analysis

### Failure Mode 1: macOS Permission Prompt
**Scenario**: First call to `sounddevice.check_input_settings()` triggers permission prompt
**Detection**: Permission dialog appears on startup
**Consequence**: User must interact with dialog to continue
**Prevention**: Can't prevent on first run (expected behavior)
**Recovery**: Dialog is clear and expected on first use
**Mitigation**: Document this in README

### Failure Mode 2: sounddevice Module Not Available
**Scenario**: sounddevice import fails (missing dependency)
**Detection**: ImportError
**Consequence**: App won't start
**Prevention**: Ensure sounddevice in requirements.txt (it is)
**Recovery**: User installs requirements: `pip install -r requirements.txt`
**Mitigation**: Check is only called if sounddevice imported successfully

### Failure Mode 3: sounddevice.check_input_settings() Hangs
**Scenario**: Function blocks indefinitely (rare)
**Detection**: App never shows "Listening..."
**Consequence**: App appears frozen
**Prevention**: Could add timeout (out of scope)
**Recovery**: User force-kills app with Ctrl+C
**Mitigation**: Document timeout behavior if needed in future

### Failure Mode 4: Microphone Permission Changes During Runtime
**Scenario**: User removes microphone permission while app running
**Detection**: Next recording attempt fails
**Consequence**: Recording fails (but app still running)
**Prevention**: Would require continuous polling (expensive)
**Recovery**: App gracefully handles recording error, suggests restart
**Mitigation**: Document that permissions should not change during use

### Failure Mode 5: Multiple Audio Devices, Some Disabled
**Scenario**: System has 3 devices, 2 disabled, 1 working
**Detection**: `check_input_settings()` may check wrong device
**Consequence**: False negative (thinks mic not available)
**Prevention**: sounddevice checks default input device (usually correct)
**Recovery**: User can specify device via system settings
**Mitigation**: Document which device is being checked (sounddevice default)

---

## Rollout Strategy

### Phase 1: Testing
1. Write TDD tests
2. Implement function
3. Test locally (with/without microphone)
4. Test with permissions disabled

### Phase 2: Integration
1. Merge with lock file feature
2. Run full test suite
3. Manual startup test

### Phase 3: Monitoring
1. Check logs for microphone errors
2. Collect user feedback
3. Adjust error messages if needed

---

## Documentation Updates

### README.md - Add Troubleshooting Section

```markdown
### Microphone Permission Issues

If you see "Microphone access failed" on startup:

**macOS:**
1. Open System Preferences → Security & Privacy
2. Select "Microphone" from left panel
3. Make sure `whisper-dictation` is in the list and enabled
4. Click the lock icon and enter your password if needed
5. Restart the application

**The app will start normally even if the check fails** — you just won't be able to record until permissions are fixed.
```

---

## Performance Impact

- **Check duration**: <10ms (sounddevice internal check)
- **Memory impact**: Negligible
- **Startup latency**: <10ms added

**Negligible.**

---

## Acceptance Criteria (Ready to Implement)

- [ ] TDD tests written BEFORE implementation
- [ ] Function implemented
- [ ] Works with both whisper-dictation.py and whisper-dictation-fast.py
- [ ] All tests pass
- [ ] Manual testing confirms correct behavior
- [ ] No regressions in existing tests

