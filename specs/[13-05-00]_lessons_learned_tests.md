# User Story: Lessons Learned Tests Suite

**ID**: 13-05-00
**Epic**: [13-00-00] Lessons Learned Foundation
**Status**: Draft
**Priority**: High
**Complexity**: Medium
**Estimate**: 30-40 minutes

---

## User Story

**As a** whisper-dictation developer,
**I want** a comprehensive TDD test suite covering all Lessons Learned features (lock file, watchdog, logging, etc.),
**So that** I can confidently maintain and refactor these critical systems, and ensure they work correctly in CI/CD.

---

## Background

### Current Situation
- Tests exist for audio and transcription
- Stability features (lock file, watchdog) are untested
- No CI/CD pipeline testing stability features
- Risk of regressions

### Why This Matters
- **Confidence**: Tests verify features work as designed
- **Regression Prevention**: Catch breakage early
- **CI/CD Integration**: Automated validation on each commit
- **Documentation**: Tests are executable specs

### TDD Philosophy
**Tests FIRST, code SECOND** - We write test cases before implementation.

---

## What We're Building

**TDD test suite** with:
1. Unit tests for each component
2. Integration tests for end-to-end flows
3. Manual test scenarios (documented)
4. CI configuration
5. Coverage reporting

---

## Assumptions & Validation

### A1: pytest Framework is Sufficient
- Assumption: pytest is adequate for our needs
- Validation: Already in use, covers all test types
- Risk: None identified
- Mitigation: N/A

### A2: Mocking is Safe for This Code
- Assumption: Can mock PyAudio, sounddevice, subprocess safely
- Validation: Test mocks match real behavior
- Risk: Mocks diverge from reality
- Mitigation: Integration tests with real objects

### A3: 100% Coverage Not Required
- Assumption: Focus on critical paths, not every branch
- Validation: >90% coverage for stability code, >70% overall
- Risk: Untested edge cases
- Mitigation: Code review + manual testing

---

## Acceptance Criteria

### Test Organization
- [ ] **T1** Tests organized by feature (lock_file, watchdog, logging, etc.)
- [ ] **T2** Each test file corresponds to a module
- [ ] **T3** Clear test naming convention: `test_<feature>_<behavior>`
- [ ] **T4** All tests in `tests/` directory

### Unit Test Coverage
- [ ] **U1** Lock file creation/cleanup
- [ ] **U2** Lock file with dead PID
- [ ] **U3** Signal handlers
- [ ] **U4** Microphone check success/failure
- [ ] **U5** Heartbeat update
- [ ] **U6** Stall detection
- [ ] **U7** Stream restart
- [ ] **U8** Logging file creation/rotation

### Integration Tests
- [ ] **I1** Two instances scenario (second exits)
- [ ] **I2** Ctrl+C shutdown (lock file removed)
- [ ] **I3** Watchdog detects and recovers from stall
- [ ] **I4** Recording works end-to-end
- [ ] **I5** Transcription works end-to-end
- [ ] **I6** Log file grows and rotates

### Manual Tests
- [ ] **M1** Documented scenarios for manual testing
- [ ] **M2** Test cards for: startup, shutdown, stall recovery
- [ ] **M3** Checklist for system integration testing

### CI/CD Integration
- [ ] **C1** All tests run in CI (GitHub Actions)
- [ ] **C2** Tests must pass before merge
- [ ] **C3** Coverage report generated
- [ ] **C4** Failed tests block deployment

### No Regressions
- [ ] **R1** All existing tests still pass
- [ ] **R2** No performance regression from test overhead
- [ ] **R3** Test suite doesn't modify user files (uses temp dirs)

---

## Test Files Structure

```
tests/
├── __init__.py
├── conftest.py                          # Shared fixtures
│
├── test_lock_file.py                    # [13-01-00]
│   ├── TestLockFileBasics
│   ├── TestLockFileMultiInstance
│   ├── TestSignalHandling
│   └── TestStaleFiles
│
├── test_microphone_check.py             # [13-02-00]
│   ├── TestMicrophoneCheckBasics
│   ├── TestMicrophoneCheckTiming
│   └── TestMicrophoneCheckIntegration
│
├── test_audio_watchdog.py               # [13-03-00]
│   ├── TestHeartbeatTracking
│   ├── TestStallDetection
│   ├── TestWatchdogThread
│   ├── TestStreamRestart
│   └── TestThreadSafety
│
├── test_logging.py                      # [13-04-00]
│   ├── TestLoggingSetup
│   ├── TestRotatingFileHandler
│   ├── TestKeyEventsLogged
│   ├── TestConsoleFallback
│   └── TestLogFormat
│
├── integration/
│   ├── __init__.py
│   ├── test_lock_file_integration.py
│   ├── test_watchdog_integration.py
│   └── test_full_flow.py
│
└── manual_tests/
    ├── README.md                        # Manual test guide
    └── test_scenarios.md                # Test cards/scenarios
```

---

## Unit Test Examples

### test_lock_file.py (Abbreviated)
```python
"""Tests for lock file mechanism"""
import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

class TestLockFileBasics:
    def test_lock_file_created_on_startup(self):
        """Lock file should exist after setup_lock_file()"""
        from whisper_dictation import setup_lock_file, cleanup_lock_file, LOCK_FILE
        setup_lock_file()
        assert LOCK_FILE.exists()
        cleanup_lock_file()

    def test_dead_pid_allows_startup(self):
        """Dead PID in lock file should be overwritten"""
        from whisper_dictation import setup_lock_file, LOCK_FILE
        LOCK_FILE.write_text("99999999")
        setup_lock_file()  # Should not raise
        assert int(LOCK_FILE.read_text().strip()) == os.getpid()
```

### test_audio_watchdog.py (Abbreviated)
```python
"""Tests for audio watchdog"""
import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import patch

class TestHeartbeatTracking:
    def test_heartbeat_updated(self):
        """update_heartbeat() should update last_heartbeat"""
        from whisper_dictation import update_heartbeat, last_heartbeat as old_time
        time.sleep(0.05)
        update_heartbeat()
        from whisper_dictation import last_heartbeat as new_time
        assert new_time > old_time
```

### test_logging.py (Abbreviated)
```python
"""Tests for logging system"""
import pytest
import logging
from pathlib import Path

class TestLoggingSetup:
    def test_log_file_created(self):
        """setup_logging() should create log file"""
        from whisper_dictation import setup_logging
        setup_logging()
        log_file = Path.home() / ".whisper-dictation.log"
        assert log_file.exists()
```

---

## Integration Test Examples

### integration/test_lock_file_integration.py
```python
"""Integration tests for lock file with real processes"""
import pytest
import subprocess
import sys
import time
from pathlib import Path

class TestMultiInstanceIntegration:
    def test_second_instance_exits(self):
        """Starting app twice should exit second instance gracefully"""
        # Start first instance in background
        proc1 = subprocess.Popen([sys.executable, "whisper-dictation.py"])
        time.sleep(0.5)

        # Try to start second instance
        proc2 = subprocess.run(
            [sys.executable, "whisper-dictation.py"],
            capture_output=True
        )

        # Second should exit with code 1
        assert proc2.returncode == 1
        assert b"already running" in proc2.stderr

        # Clean up
        proc1.terminate()
```

### integration/test_full_flow.py
```python
"""End-to-end integration tests"""
import pytest

@pytest.mark.integration
class TestFullRecordingFlow:
    def test_record_and_transcribe(self):
        """Full flow: record audio, transcribe, type text"""
        # This requires the full app context
        # Typically requires manual setup or mock audio
        pass
```

---

## Manual Test Scenarios

### Manual Test Guide: `manual_tests/test_scenarios.md`

```markdown
# Manual Test Scenarios

## Test 1: Lock File Behavior

### Setup
- Start with clean system
- Ensure no whisper-dictation processes running
- Check lock file doesn't exist: `ls -la ~/.whisper-dictation.lock`

### Scenario A: Normal Startup
1. Start app: `poetry run python whisper-dictation.py --k_double_cmd`
2. Verify lock file created: `cat ~/.whisper-dictation.lock` (should show PID)
3. Verify app shows "Listening..."
4. Press Ctrl+C
5. Verify lock file removed: `ls -la ~/.whisper-dictation.lock` (should not exist)
6. ✅ PASS

### Scenario B: Second Instance
1. Start first app: Terminal 1
2. Attempt start second app: Terminal 2
3. Verify Terminal 2 shows "Already running (PID X)"
4. Kill Terminal 1: Ctrl+C
5. Verify Terminal 2 can now start
6. ✅ PASS

### Scenario C: Crashed App Recovery
1. Run: `echo 99999999 > ~/.whisper-dictation.lock`
2. Start app: should start successfully (recognizes dead PID)
3. Verify: `cat ~/.whisper-dictation.lock` (shows NEW PID)
4. ✅ PASS

---

## Test 2: Audio Watchdog

### Setup
- Run with `--log-level DEBUG` to see watchdog activity
- Monitor logs: `tail -f ~/.whisper-dictation.log`

### Scenario A: Normal Recording (No Stall)
1. Start app
2. Record for 5 seconds
3. Verify "Audio OK" or no stall warnings
4. Verify logs show heartbeat updates
5. ✅ PASS

### Scenario B: Watchdog Monitoring
1. Start app with DEBUG level
2. Look for "Watchdog thread started" in logs
3. Record brief audio
4. Look for "Heartbeat updated" entries
5. ✅ PASS

### Scenario C: Stall Detection (Simulated)
[This would require code instrumentation]
1. Patch recorder to not update heartbeat
2. Let watchdog run >10 seconds
3. Verify "Audio system stalled" warning
4. Verify restart attempted
5. ✅ PASS

---

## Test 3: Microphone Check

### Setup
- None required

### Scenario A: Microphone Available
1. Start app normally
2. Verify "Microphone access OK" in logs
3. Recording works
4. ✅ PASS

### Scenario B: Microphone Permission Denied
[Requires System Preferences change]
1. System Preferences → Security & Privacy → Microphone
2. Remove whisper-dictation from approved list
3. Start app
4. Verify "Microphone access test failed" in logs
5. Re-enable permissions
6. Restart app
7. ✅ PASS

---

## Test 4: Logging System

### Scenario A: Log File Creation
1. Delete existing log: `rm ~/.whisper-dictation.log`
2. Start app
3. Verify log file created: `ls -la ~/.whisper-dictation.log`
4. Verify contains start message: `grep "Application started" ~/.whisper-dictation.log`
5. ✅ PASS

### Scenario B: Log Rotation
1. Generate large log: Fill with 20+ recordings
2. Monitor log file size: `ls -lah ~/.whisper-dictation.log*`
3. Verify max size ~5MB
4. Verify backup files created: `~/.whisper-dictation.log.1`, `.log.2`, etc.
5. Verify old logs deleted (max 5 backups)
6. ✅ PASS

### Scenario C: Log Levels
1. `--log-level DEBUG`: Verify very verbose output
2. `--log-level WARNING`: Verify only warnings/errors shown
3. ✅ PASS
```

---

## Test Fixtures (conftest.py)

```python
"""Shared pytest fixtures"""
import pytest
import tempfile
from pathlib import Path

@pytest.fixture
def temp_log_dir():
    """Temporary directory for test logs"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def mock_pyaudio():
    """Mock PyAudio for testing without audio hardware"""
    from unittest.mock import MagicMock
    with patch('pyaudio.PyAudio') as mock:
        mock.return_value.open.return_value = MagicMock()
        yield mock

@pytest.fixture
def mock_recorder():
    """Mock audio recorder"""
    from unittest.mock import MagicMock
    recorder = MagicMock()
    recorder.record.return_value = b'\x00' * 1024
    return recorder

@pytest.fixture
def clean_lock_file():
    """Ensure lock file is clean before/after test"""
    from pathlib import Path
    lock_file = Path.home() / ".whisper-dictation.lock"
    if lock_file.exists():
        lock_file.unlink()
    yield
    if lock_file.exists():
        lock_file.unlink()

@pytest.fixture
def clean_log_file():
    """Ensure log file is clean before/after test"""
    from pathlib import Path
    log_file = Path.home() / ".whisper-dictation.log"
    if log_file.exists():
        log_file.unlink()
    yield
    if log_file.exists():
        log_file.unlink()
```

---

## pytest Configuration (pytest.ini)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --tb=short
    --strict-markers
    -ra
    --cov=.
    --cov-report=html
    --cov-report=term-missing
markers =
    unit: Unit tests (fast, mocked)
    integration: Integration tests (slower, real objects)
    manual: Manual test scenarios
    whisper_cpp: Tests specific to C++ version
```

---

## Running Tests

### All Tests
```bash
poetry run pytest
```

### Unit Tests Only
```bash
poetry run pytest -m unit
```

### Integration Tests Only
```bash
poetry run pytest -m integration
```

### With Coverage
```bash
poetry run pytest --cov=whisper_dictation --cov-report=html
```

### Specific Test File
```bash
poetry run pytest tests/test_lock_file.py
```

### Watch Mode (on change, rerun tests)
```bash
poetry run pytest-watch
```

---

## Coverage Goals

| Component | Target | Rationale |
|-----------|--------|-----------|
| Lock file | 95% | Critical safety feature |
| Signal handling | 90% | Complex control flow |
| Watchdog | 85% | Thread-based, harder to test |
| Logging | 80% | Mostly setup, less logic |
| Microphone check | 95% | Simple wrapper |
| **Overall** | **85%** | Professional standard |

---

## CI/CD Integration

### GitHub Actions Workflow: `.github/workflows/tests.yml`

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: macos-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9

    - name: Install dependencies
      run: |
        poetry install

    - name: Run unit tests
      run: |
        poetry run pytest -m unit -v

    - name: Run integration tests
      run: |
        poetry run pytest -m integration -v

    - name: Coverage report
      run: |
        poetry run pytest --cov=. --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

---

## Test Maintenance

### Adding New Tests
1. Create test function following naming convention
2. Add docstring explaining what is tested
3. Use mocks for external dependencies
4. Add appropriate pytest markers (@pytest.mark.unit, etc.)
5. Run test locally before commit
6. Ensure coverage doesn't decrease

### Debugging Failed Tests
1. Run test with `-vv` (very verbose)
2. Run test with `-s` (don't capture output)
3. Use `pytest --pdb` to drop into debugger
4. Check logs in `~/.whisper-dictation.log`

### Updating Tests for Changes
1. When code changes, run tests first
2. Update tests to match new behavior
3. Ensure old tests still pass (regression)
4. Add new tests for new features

---

## Brittleness Analysis

### Failure Mode 1: Tests Too Tightly Coupled to Implementation
**Prevention**: Test behavior, not implementation details
**Mitigation**: Use mocks at boundaries, not internal functions

### Failure Mode 2: Flaky Tests (Non-Deterministic)
**Prevention**: Use fixed delays instead of timeouts, seed randomness
**Mitigation**: Mark flaky tests with @pytest.mark.flaky, retry

### Failure Mode 3: Tests Contaminating Filesystem
**Prevention**: Use temp directories, clean up before/after
**Mitigation**: Fixtures with cleanup (clean_lock_file, clean_log_file)

### Failure Mode 4: Test Suite Takes Too Long
**Prevention**: Keep unit tests fast (<1s), integration tests separate
**Mitigation**: Run unit tests in CI, integration tests only in nightly

### Failure Mode 5: Mock Diverges from Reality
**Prevention**: Compare mock behavior to real objects periodically
**Mitigation**: Integration tests with real objects, documentation

---

## Success Metrics

- ✅ All tests pass in CI
- ✅ Coverage >85% for stability code
- ✅ New features have tests BEFORE implementation
- ✅ No regressions in existing tests
- ✅ Test suite runs in <2 minutes
- ✅ Manual test scenarios documented and verified

---

## Rollout Strategy

### Phase 1: Foundation Tests
1. Write lock file tests
2. Write microphone check tests
3. Run and pass

### Phase 2: Complex Tests
1. Write watchdog tests (with mocks)
2. Write logging tests
3. Run and pass

### Phase 3: Integration
1. Write end-to-end integration tests
2. Document manual test scenarios
3. Verify all pass

### Phase 4: CI/CD
1. Set up GitHub Actions workflow
2. Require tests to pass before merge
3. Monitor coverage trends

---

## Acceptance Criteria (Ready to Implement)

- [ ] All TDD test cases written (unit + integration)
- [ ] Unit tests all pass
- [ ] Integration tests all pass
- [ ] Coverage >85%
- [ ] Manual test scenarios documented
- [ ] CI/CD workflow configured
- [ ] No regressions in existing tests

---

## References

- pytest documentation: https://docs.pytest.org/
- Coverage.py: https://coverage.readthedocs.io/
- GitHub Actions: https://docs.github.com/en/actions
- TDD Best Practices: https://kent.doddad.com/blog/make-your-test-useful

