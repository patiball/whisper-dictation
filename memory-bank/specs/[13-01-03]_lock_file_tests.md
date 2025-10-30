# Task: Lock File Test Suite

**ID**: 13-01-03
**User Story**: [13-01-00] Lock File + Signal Handling
**Status**: ✅ **COMPLETED**
**Estimate**: 7 minutes

---

## What

TDD test suite for lock file mechanism and signal handling, covering creation, validation, cleanup, and multi-instance scenarios.

---

## Test Strategy

**Unit Tests (`tests/test_lock_file.py`):**
- Lock file creation and content validation
- Lock file cleanup
- Stale lock file handling (dead PID)
- Invalid lock file content handling
- Signal handler registration verification

**Integration Tests (`tests/test_lock_file_integration.py`):**
- Multi-instance scenario (second instance exits)
- Ctrl+C cleanup (lock file removed)
- Stale lock recovery with real processes

**Test Fixtures:**
- `clean_lock_file`: Remove lock file before/after tests
- `temp_home`: Temporary directory for lock files (optional)

---

## Test Coverage

**TestLockFileBasics:**
- `test_lock_file_created_on_startup`: Verify file created with PID
- `test_lock_file_cleaned_up_on_exit`: Verify file removed
- `test_dead_pid_allows_startup`: Stale lock removed, new lock created

**TestStaleFiles:**
- `test_invalid_pid_in_lock_file`: Handle non-numeric PID gracefully
- `test_empty_lock_file`: Handle empty file gracefully

**TestSignalHandling:**
- `test_signal_handler_registered`: Verify SIGINT handler not default
- `test_cleanup_on_signal`: Verify cleanup called on signal

**TestMultiInstanceIntegration:**
- `test_second_instance_exits_gracefully`: Second instance gets code 1
- `test_ctrl_c_removes_lock_file`: Lock file removed on SIGINT

---

## Acceptance Criteria

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Coverage >90% for lock file code
- [ ] Tests use fixtures for cleanup
- [ ] Tests don't modify user's actual lock file
- [ ] Integration tests spawn real processes
- [ ] Signal handler tests verify registration
- [ ] Stale lock tests verify recovery

---

## Implementation Context (Not Part of Spec)

**Test Files:**
- `tests/test_lock_file.py`: Unit tests
- `tests/test_lock_file_integration.py`: Integration tests
- `tests/conftest.py`: Shared fixtures

**Test Execution:**
- Run all: `poetry run pytest tests/test_lock_file*.py`
- Run with coverage: `poetry run pytest tests/test_lock_file*.py --cov`
