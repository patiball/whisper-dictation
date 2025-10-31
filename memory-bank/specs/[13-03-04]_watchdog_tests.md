# Task: Watchdog Test Suite

**ID**: 13-03-04
**User Story**: [13-03-00] Audio Stream Watchdog
**Status**: ✅ **COMPLETED**
**Estimate**: 13 minutes

---

## What

TDD test suite for watchdog functionality covering heartbeat tracking, stall detection, stream recovery, and thread safety.

---

## Test Strategy

**Unit Tests (`tests/test_audio_watchdog.py`):**
- Mock audio streams and threading
- Test heartbeat update mechanism
- Test stall detection logic
- Test stream restart sequence
- Test thread lifecycle management
- Test with various timing scenarios

**Integration Tests:**
- Test watchdog with simulated stall
- Test watchdog doesn't interfere with normal recording
- Test cleanup on shutdown

**Test Fixtures:**
- Mock audio stream objects
- Mock datetime for time control
- Cleanup watchdog thread after tests

---

## Test Coverage

**TestHeartbeatTracking:**
- `test_heartbeat_updated`: Verify timestamp changes
- `test_heartbeat_starts_at_current_time`: Initial value is recent

**TestStallDetection:**
- `test_stall_detected_after_timeout`: Old heartbeat triggers detection
- `test_no_stall_within_timeout`: Recent heartbeat doesn't trigger

**TestWatchdogThread:**
- `test_watchdog_respects_active_flag`: Exits when flag set False
- `test_watchdog_only_monitors_during_recording`: Checks recording flag
- `test_watchdog_calls_restart_on_stall`: Restart triggered correctly

**TestStreamRestart:**
- `test_restart_closes_old_stream`: Verify stop() and close() called
- `test_restart_creates_new_stream`: Verify new stream created
- `test_restart_handles_exceptions`: Graceful error handling

**TestThreadSafety:**
- `test_global_variables_accessible`: Verify watchdog can access flags
- `test_no_race_on_recording_flag`: Rapid toggling doesn't crash

---

## Acceptance Criteria

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Coverage >85% for watchdog code
- [ ] Tests use mocking for audio streams
- [ ] Thread lifecycle tests verify clean start/stop
- [ ] Stall detection tests verify correct timing
- [ ] Stream restart tests verify sequence

---

## Implementation Context (Not Part of Spec)

**Test File:**
- `tests/test_audio_watchdog.py`

**Test Execution:**
- Run all: `poetry run pytest tests/test_audio_watchdog.py`
- With coverage: `poetry run pytest tests/test_audio_watchdog.py --cov`
