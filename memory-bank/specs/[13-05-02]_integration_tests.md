# Task: Integration Tests for Lessons Learned Features

**ID**: 13-05-02
**User Story**: [13-05-00] Lessons Learned Tests Suite
**Status**: ✅ **COMPLETED**
**Estimate**: 10 minutes

---

## What

Implement integration tests that verify end-to-end functionality of stability features with real components.

---

## Test Scenarios

**Multi-Instance Behavior (`tests/test_lock_file_integration.py`):**
- Second instance exits when first is running
- Lock file removed on Ctrl+C
- Stale lock recovery with real processes
- Uses subprocess.Popen to spawn actual processes

**Full Recording Flow (`tests/test_integration_recording.py`):**
- Complete recording, transcription, output cycle
- All components interact correctly
- Logging captures full sequence
- No resource leaks or hangs

**Watchdog Recovery (`tests/test_integration_watchdog.py`):**
- Simulated stall triggers watchdog
- Recovery sequence executes correctly
- Application continues after recovery
- Events logged appropriately

**Log Rotation (`tests/test_integration_logging.py`):**
- Generate high volume of log entries
- Verify rotation occurs at size limit
- Verify backup files created
- Verify old backups deleted

---

## Testing Approach

**Real Component Usage:**
- Spawn actual processes (subprocess)
- Use real file system operations
- Use real audio devices (when available)
- Verify behavior with real timing

**Cleanup Strategy:**
- Clean up spawned processes
- Remove temporary files
- Restore system state
- Use pytest fixtures for teardown

**Skip Conditions:**
- Skip if no microphone available
- Skip if running in CI without audio
- Use pytest.mark.skipif appropriately

---

## Acceptance Criteria

- [ ] All integration test files created
- [ ] Multi-instance scenario verified
- [ ] Watchdog recovery verified
- [ ] Log rotation verified
- [ ] All tests pass
- [ ] Tests clean up after themselves
- [ ] Tests skip gracefully when resources unavailable
- [ ] Execution time reasonable (<2 minutes)

---

## Implementation Context (Not Part of Spec)

**Test Files:**
- `tests/test_lock_file_integration.py`
- `tests/test_integration_recording.py`
- `tests/test_integration_watchdog.py`
- `tests/test_integration_logging.py`

**Execution:**
- Run: `poetry run pytest -m integration`
