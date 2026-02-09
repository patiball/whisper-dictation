# Task: Add 1.0 Second Timeout to thread.join() Calls

**ID**: 15-01-02
**User Story**: [15-01-00] Fix Thread Cleanup and Timeouts
**Complexity**: Simple
**Estimate**: 15 minutes

## What

Add explicit 1.0 second timeout to all `thread.join()` calls in the cleanup fixture. Currently uses 2.0 second timeout which accumulates across multiple threads.

## Design Approach

1. Identify all `thread.join(timeout=...)` calls in cleanup fixtures
2. Change timeout value from 2.0 to 1.0 seconds
3. Verify this doesn't break any test assumptions (tests should exit in < 500ms)
4. Add logging to track actual thread exit times
5. If any test regularly exceeds 1.0 second, investigate and fix the test

**Rationale for 1.0 second**:
- Most test threads complete in < 500ms
- 1.0 second provides buffer without being excessive
- Prevents accumulation: 16 tests × 1.0s = 16s max overhead
- Previously with 2.0s: 16 tests × 2.0s = 32+ seconds overhead

## Failure Modes

- **Failure Mode 1: Tests timeout prematurely**
  - Detection: Tests complete but thread.join(timeout=1.0) returns False
  - Consequence: Test cleanup incomplete, but test passes
  - Prevention: Verify tests don't create long-running threads
  - Mitigation: Increase timeout or fix test

- **Failure Mode 2: Timeout too aggressive**
  - Detection: Warning logs show many threads exceeding timeout
  - Consequence: Test suite less stable
  - Prevention: Analyze test thread patterns first
  - Mitigation: Adjust timeout based on actual thread exit times

## Acceptance Criteria

- [ ] All `thread.join()` calls use explicit timeout <= 1.0 seconds
- [ ] No timeout=None or infinite waits remain
- [ ] Cleanup fixture has logging to track join() results
- [ ] test_audio_watchdog.py completes in < 30 seconds
- [ ] No change to test results (same tests pass/fail)

## Implementation Context (Not Part of Spec)

**Current Pattern** (in cleanup fixture):
```python
for thread in _active_threads[:]:
    if thread.is_alive():
        thread.join(timeout=2.0)  # CHANGE TO 1.0
    _active_threads.remove(thread)
```

**Updated Pattern**:
```python
for thread in _active_threads[:]:
    if thread.is_alive():
        thread.join(timeout=1.0)  # Changed from 2.0
        if thread.is_alive():
            logger.warning(f"Thread {thread.name} did not exit after 1.0s timeout")
    _active_threads.remove(thread)
```

**Also check for**:
- `stall_detected.wait(timeout=2.0)` in test functions
- `watchdog_thread.join(timeout=1.0)` in cleanup code
- Any other join() calls with long timeouts

**Affected Tests**: All 16 tests in test_audio_watchdog.py (they all use cleanup fixture)

**Verification**:
```bash
# Run tests with timing info
pytest tests/test_audio_watchdog.py -v --tb=short

# Should complete in < 30 seconds total
# Check for warning logs about threads exceeding timeout
```
