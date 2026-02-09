# Epic: Test Infrastructure Repair

**ID**: 15-00-00
**Priority**: CRITICAL
**Complexity**: Complex
**Estimate**: 240 minutes (4 hours)

## Epic Goal

Eliminate test hangs, configuration conflicts, and resource cleanup issues in the test suite. Current test runs hang indefinitely or take 160+ seconds due to thread cleanup anti-patterns, logging handler pollution, subprocess resource leaks, and missing timeouts.

## Problem Statement

The test suite has accumulated critical issues preventing reliable test execution:

1. **Thread cleanup anti-patterns** cause 80+ second hangs (test_audio_watchdog.py)
2. **Logging handler pollution** causes 11 tests to interfere with each other (test_logging.py)
3. **Subprocess resource leaks** cause 50+ second hangs (test_lock_file_integration.py)
4. **Infinite thread hangs** prevent test completion (test_integration_recording.py)
5. **Configuration conflicts** between pytest.ini and pyproject.toml
6. **Environment variable pollution** causes cross-test interference (conftest.py)

**Impact**: Test runs take 170+ seconds or hang indefinitely, blocking development workflow

## Desired Outcome

- All 93 tests complete within 60 seconds
- No infinite hangs or zombie processes
- Tests can run in any order with reproducible results
- Pytest configuration unified and conflict-free
- Thread and subprocess resources properly cleaned up

## Success Criteria

- [ ] test_audio_watchdog.py: 16 tests complete in < 30 seconds (no thread._stop() calls)
- [ ] test_logging.py: 13 tests complete in < 20 seconds (no handler pollution)
- [ ] test_lock_file_integration.py: 5 tests complete in < 25 seconds (cleanup in place)
- [ ] test_integration_recording.py: 7 tests complete in < 15 seconds (no infinite hangs)
- [ ] All custom markers (unit, integration, manual, slow) recognized by pytest
- [ ] Environment variables isolated per test (using monkeypatch)
- [ ] No zombie processes left after test run
- [ ] Test suite runs consistently with same time regardless of order

## Related User Stories

- [15-01-00] Fix Thread Cleanup and Timeouts ✅ COMPLETED
- [15-02-00] Fix Logging Handler Pollution + File Persistence ✅ COMPLETED
- [15-03-00] Fix Subprocess Resource Cleanup + Missing Import ✅ COMPLETED
- [15-04-00] Fix Infinite Thread Hangs + Missing Import ✅ COMPLETED
- [15-05-00] Fix Configuration Conflicts and Environment Isolation + Variable Scoping ✅ COMPLETED

**Note**: Tasks for missing imports and variable scoping discovered during verification are integrated into user stories [15-03-00], [15-04-00], and [15-05-00] respectively.

## Implementation Context (Not Part of Spec)

**Current Issues Summary**:
- test_audio_watchdog.py: 499 lines, 16 tests, uses deprecated thread._stop()
- test_logging.py: 522 lines, 13 tests, multiple basicConfig() calls
- test_lock_file_integration.py: 505 lines, 5 tests, 5 concurrent subprocess test
- test_integration_recording.py: 549 lines, 7 tests, thread.join() without timeout
- conftest.py: 207 lines, modifies os.environ directly
- pytest.ini: 40 lines, conflicts with pyproject.toml

**Root Causes**:
- No test isolation mechanisms
- Missing timeout controls
- Fixture design anti-patterns
- No resource cleanup patterns
- Conflicting configuration sources

---

## Breakdown by User Story

### [15-01-00] Fix Thread Cleanup and Timeouts
**Estimate**: 45 minutes
**Impact**: Remove 80+ second hangs
**Criticality**: CRITICAL

### [15-02-00] Fix Logging Handler Pollution
**Estimate**: 50 minutes
**Impact**: Stop 11 tests from interfering
**Criticality**: CRITICAL

### [15-03-00] Fix Subprocess Resource Cleanup
**Estimate**: 40 minutes
**Impact**: Remove 50+ second hangs, prevent zombie processes
**Criticality**: CRITICAL

### [15-04-00] Fix Infinite Thread Hangs
**Estimate**: 30 minutes
**Impact**: Prevent infinite hangs
**Criticality**: CRITICAL

### [15-05-00] Fix Configuration Conflicts
**Estimate**: 40 minutes (35 min config + 5 min max_bytes variable)
**Impact**: Unified config, proper environment isolation, configuration parameters properly scoped
**Criticality**: HIGH

---

## Deployment Notes

- All changes are to test infrastructure only - no production code changes
- Tests should be run after each user story completion
- Use pytest with `-v` flag to verify individual test success
- No database migrations or schema changes needed
- Can be deployed in multiple pull requests or single comprehensive PR

---

## Lessons Learned Reference

See `memory-bank/lessons_learned/test_infrastructure_conflicts_analysis.md` for comprehensive analysis of all issues, hang points, and affected tests.
