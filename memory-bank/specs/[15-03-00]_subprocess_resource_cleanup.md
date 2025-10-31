# User Story: Fix Subprocess Resource Cleanup

**ID**: 15-03-00
**Epic**: [15-00-00] Test Infrastructure Repair
**Priority**: CRITICAL
**Complexity**: Medium
**Estimate**: 40 minutes

## User Story

As a test runner, I want subprocess resources to be guaranteed cleanup on test completion so that no zombie processes remain and tests complete in reasonable time.

## Acceptance Criteria

- [ ] All subprocess.Popen() calls have guaranteed cleanup (try/finally blocks)
- [ ] test_lock_file_integration.py completes in < 25 seconds
- [ ] No zombie processes left after tests complete
- [ ] All 5 integration tests pass
- [ ] subprocess.communicate() calls have appropriate timeouts

## Behavior Examples

### Before
Subprocess spawned → communicate(timeout=5) called → If timeout, process never terminated → Zombie remains

### After
Subprocess spawned in try block → communicate(timeout=5) called → Cleanup in finally ensures terminate() always called

## Key Assumptions

- Proper finally blocks will catch all exception paths
- 10-second subprocess timeouts are excessive; can be reduced
- Concurrent subprocess test with 5 processes should be serialized or limited

## Related Tasks

- [15-03-01] Add try/finally cleanup to subprocess tests
- [15-03-02] Reduce concurrent process count in test_multiple_concurrent_instances
- [15-03-03] Verify test_lock_file_integration.py passes

## Implementation Context (Not Part of Spec)

**Current Issues**: test_lock_file_integration.py has multiple Popen() calls without guaranteed cleanup. test_multiple_concurrent_instances spawns 5 concurrent processes × 10s timeout = 50+ seconds.

**Location**: `tests/test_lock_file_integration.py` - 5 subprocess integration tests
