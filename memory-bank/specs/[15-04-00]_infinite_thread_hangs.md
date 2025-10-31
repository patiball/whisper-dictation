# User Story: Fix Infinite Thread Hangs

**ID**: 15-04-00
**Epic**: [15-00-00] Test Infrastructure Repair
**Priority**: CRITICAL
**Complexity**: Simple
**Estimate**: 30 minutes

## User Story

As a test runner, I want thread.join() calls to have explicit timeouts so that tests can never hang indefinitely waiting for a thread to exit.

## Acceptance Criteria

- [ ] All thread.join() calls have explicit timeout <= 5.0 seconds
- [ ] test_integration_recording.py completes in < 15 seconds
- [ ] All 7 integration recording tests pass
- [ ] No infinite waits in test code

## Behavior Examples

### Before
Thread created → thread.join() with no timeout → If thread blocked, test hangs forever

### After
Thread created → thread.join(timeout=5.0) → Test completes or logs timeout warning

## Key Assumptions

- Proper timeout prevents infinite hangs
- 5.0 second timeout is appropriate for integration tests
- Tests with thread waits should timeout gracefully

## Related Tasks

- [15-04-01] Add timeouts to thread.join() in test_integration_recording.py
- [15-04-02] Verify test_integration_recording.py passes

## Implementation Context (Not Part of Spec)

**Current Issue**: test_integration_recording.py has thread.join() calls without timeout (lines 303), allowing infinite hangs if thread blocks.

**Location**: `tests/test_integration_recording.py` - 7 tests with threading/subprocess patterns
