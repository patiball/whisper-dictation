# Task: Fix Indefinite Deadlock in test_deadlock_prevention
**ID**: 16-01-04
**User Story**: [16-01-00] Thread Cleanup Fix
**Complexity**: Medium
**Estimate**: 15 minutes

## What
The `test_deadlock_prevention` test was intentionally creating a permanent, unrecoverable deadlock at the C-level of the `threading` module. This caused the entire `pytest` process to hang post-execution, as the test teardown fixtures could not join the deadlocked threads, and the process was unable to respond to any signals (`SIGINT`, `SIGALRM`).

The fix involves refactoring the test to use non-blocking `lock.acquire(timeout=...)` calls instead of a `with lock:` statement. This change prevents the threads from blocking indefinitely. The threads will now attempt to acquire a lock, time out if it's held by the other thread (detecting the deadlock), and then exit gracefully. The test now correctly asserts that this deadlock condition was detected, rather than creating an unrecoverable hang.

## Acceptance Criteria
- [ ] The `test_deadlock_prevention` test is refactored to use non-blocking, timed lock acquisitions.
- [ ] The test correctly asserts that a deadlock condition is detected.
- [ ] Running `pytest tests/test_audio_watchdog.py` completes and the process exits cleanly without hanging.
