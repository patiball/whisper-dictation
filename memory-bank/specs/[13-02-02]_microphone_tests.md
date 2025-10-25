# Task: Microphone Check Test Suite

**ID**: 13-02-02
**User Story**: [13-02-00] Microphone Proactive Check
**Complexity**: Simple
**Estimate**: 6 minutes

---

## What

TDD test suite for microphone capability check, covering success, failure, and timing scenarios.

---

## Test Strategy

**Unit Tests (`tests/test_microphone_check.py`):**
- Mock sounddevice to simulate various scenarios
- Test success case (log INFO)
- Test permission denied (log WARNING)
- Test no device found (log WARNING)
- Test generic exception handling
- Test that function never raises exceptions
- Test timing (completes in <100ms)

**Integration Tests:**
- Test with real sounddevice (if microphone available)
- Skip if no microphone present

**Test Fixtures:**
- Mock sounddevice.check_input_settings()
- Capture log output with caplog
- Time measurement utilities

---

## Test Coverage

**TestMicrophoneCheckBasics:**
- `test_check_succeeds_when_microphone_available`: Verify INFO log
- `test_check_logs_warning_on_permission_denied`: Mock PermissionError
- `test_check_handles_no_device_error`: Mock RuntimeError
- `test_check_handles_generic_exception`: Mock generic Exception
- `test_check_does_not_raise_exception`: Verify no exception propagates

**TestMicrophoneCheckTiming:**
- `test_check_completes_in_reasonable_time`: Measure <100ms
- `test_check_doesnt_block_indefinitely`: Verify function returns

**TestMicrophoneCheckIntegration:**
- `test_real_microphone_check`: Test with actual sounddevice (skip if unavailable)

---

## Acceptance Criteria

- [ ] All unit tests pass
- [ ] Integration test passes (or skips if no mic)
- [ ] Coverage >95% for microphone check code
- [ ] Tests use mocking for sounddevice
- [ ] Timing test verifies <100ms completion
- [ ] Exception handling tests verify graceful degradation

---

## Implementation Context (Not Part of Spec)

**Test File:**
- `tests/test_microphone_check.py`

**Test Execution:**
- Run: `poetry run pytest tests/test_microphone_check.py`
- With coverage: `poetry run pytest tests/test_microphone_check.py --cov`
