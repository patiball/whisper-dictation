# User Story: Fix Logging Handler Pollution

**ID**: 15-02-00
**Epic**: [15-00-00] Test Infrastructure Repair
**Priority**: CRITICAL
**Complexity**: Medium
**Estimate**: 60 minutes (50 min handler isolation + 10 min file persistence)

## User Story

As a test runner, I want logging configuration to reset between tests so that each test has isolated logging state and tests don't interfere with each other.

## Acceptance Criteria

- [ ] Logging handlers are cleared before each test in test_logging.py
- [ ] All 13 logging tests pass without interference
- [ ] File handles don't leak across tests
- [ ] RotatingFileHandler properly flushes/closes to persist logs to disk
- [ ] Log file assertions pass (8 tests that verify file content)
- [ ] Test completion time < 20 seconds
- [ ] Tests can run in any order with same results

## Behavior Examples

### Before
Test 1 configures logging with handler A → Test 2 tries to configure with handler B → Handler B never activates because basicConfig() only works once

### After
Test 1 configures logging, cleanup → Test 2 configures fresh logging, cleanup → Each test has clean state

## Key Assumptions

- basicConfig() can only be called once per process
- Proper fixture-based cleanup can reset handler state
- Each test needs independent logging configuration

## Related Tasks

- [15-02-01] Create logging reset fixture
- [15-02-02] Apply fixture to test_logging.py
- [15-02-03] Verify test_logging.py passes
- [15-02-04] Fix logging file persistence (RotatingFileHandler flush/close)

## Implementation Context (Not Part of Spec)

**Current Issue**: `logging.basicConfig()` called multiple times in test_logging.py without proper handler cleanup between tests. Multiple FileHandlers leak across tests.

**Location**: `tests/test_logging.py` - approximately 13 tests that all configure logging

**Pattern Needed**: Fixture that clears all handlers and resets logging configuration before each test
