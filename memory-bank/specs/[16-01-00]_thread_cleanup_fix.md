# User Story: Thread Cleanup Fix
**ID**: 16-01-00
**Epic**: [16-00-00] Post-Epic 15 Test Infrastructure & Functional Fixes
**Status**: Ready
**Priority**: Critical
**Estimate**: 45-60 minutes

## User Story
As a developer, I want the test suite to properly clean up all spawned threads after execution, so that the `pytest` process terminates promptly and does not hang.

## Acceptance Criteria
- [ ] The `pytest` process exits within 10 seconds of printing the final test summary.
- [ ] No "Thread ... still running after test session completion" warnings are present in the test logs.
- [ ] Running the test suite does not leave any orphaned `whisper-dictation` or `whisper-cli` processes.

## File Changes Required
- `tests/test_audio_watchdog.py`: Investigate and fix the teardown logic for tests that use background threads.
- `conftest.py`: Potentially add session-level fixtures to manage thread cleanup globally.
