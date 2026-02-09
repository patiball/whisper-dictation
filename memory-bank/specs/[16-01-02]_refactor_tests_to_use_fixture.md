# Task: Refactor Tests to Use Fixture
**ID**: 16-01-02
**User Story**: [16-01-00] Thread Cleanup Fix
**Complexity**: Medium
**Estimate**: 15 minutes

## What
Refactor all tests within `tests/test_audio_watchdog.py` that currently manage threads manually. These tests should be updated to use the new `managed_watchdog_thread` fixture.

## Acceptance Criteria
- [ ] All tests in `TestWatchdogThread` and any other relevant tests in the file are updated to use the `managed_watchdog_thread` fixture.
- [ ] Manual thread creation (`WatchdogThread(...)`), starting (`.start()`), and stopping (`.stop()`, `.join()`) calls are removed from the test functions themselves and replaced by the fixture.
