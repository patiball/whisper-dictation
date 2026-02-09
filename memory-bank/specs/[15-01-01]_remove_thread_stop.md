# Task: Remove Deprecated thread._stop() Method

**ID**: 15-01-01
**User Story**: [15-01-00] Fix Thread Cleanup and Timeouts
**Complexity**: Simple
**Estimate**: 10 minutes

## What

Remove all uses of the deprecated private `thread._stop()` method from the thread cleanup fixture. The `_stop()` method is not part of Python's public threading API and is unreliable.

## Design Approach

Rather than force-stopping threads:

1. Allow tracked threads to exit naturally through their join() timeout
2. Log a warning if a thread doesn't exit after timeout (instead of force-stopping)
3. Don't attempt any force-stop mechanisms on daemon threads
4. Keep the thread tracking mechanism intact (it works well)

The safety argument: If a test thread doesn't exit after a reasonable timeout (1.0 second), there's a problem in the test itself - forcing the thread to stop corrupts the application state. Better to let it time out and log a warning.

## Failure Modes

- **Failure Mode 1: Threads still not exiting**
  - Detection: Test output shows "WARNING: Thread X did not exit after timeout"
  - Consequence: Test completes but thread lingers
  - Prevention: Set appropriate timeout (1.0 second) based on test patterns
  - Mitigation: Log warnings to help identify problematic tests

- **Failure Mode 2: Process state corruption**
  - Detection: Subsequent tests fail with unexpected errors
  - Consequence: Test suite becomes unreliable
  - Prevention: Never force-stop threads (remove _stop() entirely)
  - Mitigation: Use proper timeouts instead

## Acceptance Criteria

- [ ] All `thread._stop()` calls removed from codebase
- [ ] No remaining references to private thread methods
- [ ] Cleanup fixture uses only public threading API
- [ ] Warning logs added for threads exceeding timeout
- [ ] Code review confirms no force-stop mechanisms remain

## Implementation Context (Not Part of Spec)

**Current Location**: `tests/conftest.py` (or check if in test_audio_watchdog.py)

**Code to Remove** (lines 42-46 or similar):
```python
for thread in threading.enumerate():
    if thread.name.startswith('Thread-') and thread.is_alive() and thread != threading.main_thread():
        if thread.daemon:
            try:
                thread._stop()  # REMOVE THIS ENTIRE BLOCK
            except:
                pass
```

**Replacement Pattern**:
```python
for thread in threading.enumerate():
    if thread.name.startswith('Thread-') and thread.is_alive() and thread != threading.main_thread():
        if thread.daemon:
            logger.warning(f"Daemon thread {thread.name} did not exit after cleanup")
            # Do NOT force-stop, just log and continue
```

**Testing**: Run test_audio_watchdog.py with `-v` flag and verify:
- No force-stop exceptions
- No AttributeError about _stop()
- All tests complete
