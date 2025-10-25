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

## Design Approach

### Microphone Capability Verification

**Core Behavior:**
1. Single verification function that tests microphone capability
2. Function queries audio system for available input devices
3. Attempts to validate default input device settings
4. Gracefully handles all failure cases without stopping startup
5. Logs result at appropriate level (INFO for success, WARNING for failure)

### Integration Point

**Timing:** Called during application initialization
- After lock file setup but before main event loop
- Early in startup sequence to provide immediate feedback
- Called exactly once per startup (not on every recording)

**Error Handling:**
- No exceptions propagate to caller
- All errors logged and communicated to user
- Application continues regardless of result

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

## Affected Components

The following components require modifications:

- **Main Application Initialization**: Call microphone check early in startup sequence
- **Setup Functions**: Add microphone verification function alongside other setup functions
- **Logging Output**: Log results to both logging system and console
- **Error Handling**: Gracefully handle all audio subsystem errors
- **Both Versions**: Changes must be synchronized across Python and C++ implementations

### Dependencies

- Audio input capability verification library (must be in project dependencies)
- Logging system for capturing results
- No new external dependencies (use existing)

---

## Failure Modes & Durability

### Failure Mode 1: OS Permission Dialog on First Use
**Scenario**: Operating system displays permission dialog during first capability check
- **Detection**: User sees system dialog on startup
- **Consequence**: User must respond to dialog to proceed
- **Prevention**: Cannot prevent on first use (OS-level requirement)
- **Recovery**: Dialog is expected and documented
- **Mitigation**: Document expected behavior in README

### Failure Mode 2: Missing Audio Subsystem Capability
**Scenario**: Audio library or module not available in environment
- **Detection**: Import or initialization error
- **Consequence**: Microphone check fails, app logs warning and continues
- **Prevention**: Verify dependency is in project requirements
- **Recovery**: User installs missing dependency
- **Mitigation**: Clear error message helps user resolve issue

### Failure Mode 3: Timeout During Capability Check
**Scenario**: Audio subsystem check hangs indefinitely (system-level issue)
- **Detection**: App startup stalls, no timeout occurs
- **Consequence**: App appears frozen
- **Prevention**: Capability check completes quickly in normal conditions
- **Recovery**: User can force-terminate with Ctrl+C
- **Mitigation**: Consider async check or timeout in future iterations (out of scope)

### Failure Mode 4: Permission Revocation During Runtime
**Scenario**: User removes microphone permissions while app is running
- **Detection**: Check passed on startup but permission removed later
- **Consequence**: Recording fails when attempted
- **Prevention**: Would require continuous polling (performance overhead)
- **Recovery**: App gracefully handles recording error
- **Mitigation**: Permissions are typically stable during app session

### Failure Mode 5: Multiple Audio Devices with Different Permissions
**Scenario**: System has multiple input devices, some disabled or restricted
- **Detection**: Default device may have different access status than alternative devices
- **Consequence**: Check may return false negative if default is unavailable
- **Prevention**: Check queries default input device (expected system behavior)
- **Recovery**: User can configure default device in OS settings
- **Mitigation**: Log which device is being checked for user visibility

---

## Implementation Approach

### TDD-First Development
- Write comprehensive test suite covering success and failure cases
- Test with actual microphone availability
- Test with permission-denied scenarios
- Test timeout and error handling

### Testing Phases
1. Unit tests for verification logic
2. Integration tests with audio subsystem
3. Manual testing with various microphone configurations
4. Timing verification (startup latency)

### Documentation Requirements
- Explain expected startup messages
- Document microphone permission issues and resolution steps
- Clarify that app continues even if check fails
- Provide OS-specific setup instructions

---

## Performance Impact

- **Check duration**: <10ms (sounddevice internal check)
- **Memory impact**: Negligible
- **Startup latency**: <10ms added

**Negligible.**

---

## Implementation Context (Not Part of Spec)

**Current Implementation Structure:**
- Verification function: `test_microphone_access()` (or similar name)
- Audio library: `sounddevice` module with `check_input_settings()` method
- Logging: Uses Python's logging system at INFO and WARNING levels
- Console output: Prints messages to stdout for user visibility
- Called in main block: Right after lock file setup, before event loop

**Note**: This implementation context documents current choices which may evolve. The specification above describes stable requirements independent of these implementation details.

---

## Acceptance Criteria (Ready to Implement)

- [ ] TDD tests written BEFORE implementation
- [ ] Verification function implemented and integrated into startup
- [ ] Works with both whisper-dictation.py and whisper-dictation-fast.py
- [ ] All tests pass (unit, integration, manual)
- [ ] Startup latency verified (<100ms)
- [ ] No regressions in existing tests

