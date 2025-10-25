# Task: Logging Test Suite

**ID**: 13-04-03
**User Story**: [13-04-00] Enhanced Logging & Diagnostics
**Complexity**: Simple
**Estimate**: 5 minutes

---

## What

TDD test suite for logging infrastructure covering setup, rotation, event logging, and format validation.

---

## Test Strategy

**Unit Tests (`tests/test_logging.py`):**
- Mock file system for safe testing
- Test log file creation
- Test rotation mechanism
- Test log level filtering
- Test format consistency
- Test error handling

**Integration Tests:**
- Test log rotation with actual file I/O
- Test console and file output together
- Test CLI configuration options

**Test Fixtures:**
- `temp_log_dir`: Temporary directory for test logs
- `clean_log_file`: Remove test logs after tests
- `caplog`: pytest fixture for capturing logs

---

## Test Coverage

**TestLoggingSetup:**
- `test_log_file_created`: Verify file created in expected location
- `test_log_level_configuration`: Test DEBUG, INFO, WARNING, ERROR
- `test_fallback_on_permission_error`: Graceful degradation if write fails

**TestLogRotation:**
- `test_rotation_creates_backup`: Verify backups created when size exceeded
- `test_old_logs_deleted`: Verify oldest deleted when backup limit reached

**TestLogFormat:**
- `test_timestamp_format`: Verify timestamp includes milliseconds
- `test_log_level_in_output`: Verify level appears in message

**TestEventLogging:**
- `test_startup_events_logged`: Verify startup messages present
- `test_error_events_logged`: Verify errors logged with traceback

---

## Acceptance Criteria

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Coverage >80% for logging code
- [ ] Tests use temporary directories
- [ ] Rotation mechanism verified
- [ ] Log level filtering verified
- [ ] Format consistency verified

---

## Implementation Context (Not Part of Spec)

**Test File:**
- `tests/test_logging.py`

**Test Execution:**
- Run: `poetry run pytest tests/test_logging.py`
- With coverage: `poetry run pytest tests/test_logging.py --cov`
