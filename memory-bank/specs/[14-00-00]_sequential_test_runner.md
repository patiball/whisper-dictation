# Epic: Sequential Test Runner for Human-Friendly Execution

**ID**: 14-00-00
**Priority**: High
**Complexity**: Medium
**Estimate**: 45-60 minutes

## Epic Overview

As a developer working on the whisper-dictation project, I want a sequential test runner that executes tests one at a time with clear human-readable output, so that I can easily track progress and identify failures during development.

## Problem Statement

The current pytest configuration runs tests in parallel, making it difficult for humans to:
- Track which specific test is currently running
- Immediately identify when a test fails
- Understand the context of failures without complex log analysis
- Get clear guidance on how to debug failed tests

## Acceptance Criteria

- [ ] Tests execute sequentially (one at a time, not in parallel)
- [ ] Clear progress indicators show current test number and total (e.g., "3/9")
- [ ] Each test displays its name, category, and execution time
- [ ] Color-coded output: ✅ green for pass, ❌ red for fail, ⚠️ yellow for warnings
- [ ] Test failures stop execution with detailed error context and debugging hints
- [ ] Option to continue on failure for full suite analysis
- [ ] Logical test ordering: stability features first, then core functionality
- [ ] Summary report shows total passed/failed and execution time
- [ ] Command-line options for running specific categories or individual test files

## Behavior Examples

### Before (Current Parallel Execution):
```
$ poetry run pytest
============================= test session starts ==============================
collected 70 items

tests/test_lock_file.py ....                                            [ 5%]
tests/test_microphone_check.py ...                                      [10%]
tests/test_audio_watchdog.py ............F....                          [25%]
tests/test_logging.py ....                                              [30%]
...
=================== FAILURES ===================
________________ TestStallDetection.test_stall_detection_timeout ________________
...
```

### After (Sequential Human-Friendly Execution):
```
$ python scripts/run_sequential_tests.py

🧪 SEQUENTIAL TEST RUNNER - Whisper Dictation Tests
====================================================

[1/9] 🔒 Lock File Tests (test_lock_file.py)...
✅ PASSED (2.3s) - 4/4 tests

[2/9] 🎤 Microphone Check Tests (test_microphone_check.py)...
✅ PASSED (1.1s) - 3/3 tests

[3/9] 🐕 Audio Watchdog Tests (test_audio_watchdog.py)...
❌ FAILED (0.8s) - Test: test_stall_detection_timeout
   Error: AssertionError: Expected timeout < 10s, got 15.2s
   Location: tests/test_audio_watchdog.py:145
   💡 Debug: poetry run pytest tests/test_audio_watchdog.py::TestStallDetection::test_stall_detection_timeout -v

⚠️  STOPPING ON FAILURE (use --continue to run all tests)

📊 SUMMARY: 2/9 passed, 1 failed, 6 skipped
⏱️  TOTAL TIME: 4.2s
```

## Key Assumptions

- **Assumption**: Developers want immediate feedback on test failures rather than waiting for full parallel execution
- **Validation**: Sequential execution is acceptable for development workflow where human monitoring is primary
- **Assumption**: Color output is supported in development terminals
- **Validation**: Fallback to plain text if color not available
- **Assumption**: Test execution time is acceptable when run sequentially
- **Validation**: Current test suite completes in under 2 minutes even when sequential

## Related User Stories

- [14-01-00] Sequential Test Execution Engine
- [14-02-00] Human-Readable Output Formatting  
- [14-03-00] Test Category Organization and Ordering
- [14-04-00] Error Reporting and Debug Integration
- [14-05-00] Command-Line Interface and Configuration

## Implementation Context (Not Part of Spec)

**Affected Components**: 
- New script in `scripts/run_sequential_tests.py`
- Integration with existing pytest configuration
- Uses existing test markers and fixtures

**Related Systems**: 
- Current test infrastructure (conftest.py, pytest.ini)
- Existing test categories and organization
- Development workflow and CI/CD pipeline

**Current Test Categories**:
- Stability tests: lock file, microphone check, audio watchdog, logging
- Core functionality: performance, language detection, recording quality
- Integration tests: full recording flow, C++ implementation

**Integration Points**:
- Leverages existing `@pytest.mark.unit`, `@pytest.mark.integration` markers
- Uses existing fixtures like `temp_home`, `clean_lock_file`
- Compatible with current test file structure and naming
