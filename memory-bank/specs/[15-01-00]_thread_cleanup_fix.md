# User Story: Fix Thread Cleanup and Timeouts

**ID**: 15-01-00
**Epic**: [15-00-00] Test Infrastructure Repair
**Priority**: CRITICAL
**Complexity**: Medium
**Estimate**: 45 minutes

## User Story

As a developer running the test suite, I want the thread cleanup fixture to properly manage test threads with appropriate timeouts so that test execution completes in reasonable time without hanging indefinitely.

## Acceptance Criteria

- [ ] Deprecated `thread._stop()` method completely removed from cleanup fixture
- [ ] All `thread.join()` calls in cleanup have explicit timeout (1.0 second maximum)
- [ ] Cleanup fixture logs warnings instead of force-stopping daemon threads
- [ ] test_audio_watchdog.py completes in < 30 seconds (currently 80+ seconds)
- [ ] No threads left running after test completion
- [ ] All 16 tests in test_audio_watchdog.py pass successfully
- [ ] No timeout warnings or exceeded timeout messages in test output

## Behavior Examples

### Before
```
test_audio_watchdog.py::test_heartbeat_thread_safety
  Creates 5 threads, each takes 2+ seconds to join with timeout
  Cleanup iteration 1: 2 seconds
  Cleanup iteration 2: 2 seconds
  ... total: 80+ seconds
  Result: Test takes 5+ seconds due to cleanup alone
```

### After
```
test_audio_watchdog.py::test_heartbeat_thread_safety
  Creates 5 threads, each takes 1 second to join with short timeout
  Cleanup iteration 1: 1 second
  Cleanup iteration 2: 0.5 seconds
  ... total: < 3 seconds cleanup overhead
  Result: Test completes in < 1 second
```

## Key Assumptions

1. **Thread safety is not compromised**: Removing force-stop is safe because proper threads will exit on their own with short timeouts
2. **Daemon threads are acceptable**: Daemon threads that don't exit are logged as warnings, not force-stopped
3. **1.0 second timeout is sufficient**: Based on analysis, most test threads complete in < 500ms
4. **Warning logging is acceptable**: Logging threads that time out helps identify test issues without corrupting state

## Related Tasks

- [15-01-01] Remove deprecated thread._stop() method
- [15-01-02] Add explicit 1.0 second timeout to thread.join() calls
- [15-01-03] Verify test_audio_watchdog.py completion

## Implementation Context (Not Part of Spec)

**Current Location**: `tests/conftest.py` or `tests/test_audio_watchdog.py`

**Key Issues**:
- Lines 42-46: Force-stopping daemon threads using private `_stop()` method
- Line 45: `thread.join(timeout=2.0)` - too long per thread, accumulates
- Multiple test functions create tracked threads without short timeouts

**Current Pattern**:
```python
@pytest.fixture(autouse=True)
def cleanup_threads():
    yield
    for thread in _active_threads[:]:
        if thread.is_alive():
            thread.join(timeout=2.0)  # TOO LONG
        _active_threads.remove(thread)

    for thread in threading.enumerate():
        if thread.daemon:
            try:
                thread._stop()  # DEPRECATED AND DANGEROUS
            except:
                pass
```

**Tests Affected** (all 16 tests in test_audio_watchdog.py):
1. test_heartbeat_thread_safety (5 threads)
2. test_global_variable_access (5 threads)
3. test_multiple_heartbeat_updates (multiple)
4. test_watchdog_thread_creation
5. test_watchdog_monitoring_loop
6. test_race_condition_prevention (10 threads)
7-16. Eight other thread-creation tests

---

## Cleanup Implementation Pattern

**WHAT should happen**:
- Track test-created threads (keep tracking mechanism)
- Join all tracked threads with 1.0 second timeout
- If thread doesn't exit after timeout, log warning (not force-stop)
- Don't attempt to force-stop daemon threads
- Let daemon threads exit naturally or remain as non-critical

**WHERE it happens**:
- In the autouse fixture that runs after each test
- Before test isolation is complete

**Key Design Decisions**:
1. Use timeout to prevent indefinite waits
2. Log instead of force-stop to maintain process integrity
3. Keep tracking mechanism (it works well)
4. Focus on properly exiting created threads, not forcing cleanup
