# Task: Test Infrastructure (CI/CD, Fixtures, Configuration)

**ID**: 13-05-04
**User Story**: [13-05-00] Lessons Learned Tests Suite
**Complexity**: Medium
**Estimate**: 13 minutes

---

## What

Set up test infrastructure including shared fixtures, pytest configuration, and CI/CD pipeline integration.

---

## Shared Fixtures (`tests/conftest.py`)

**Temporary Directory Fixtures:**
- `temp_log_dir`: Temporary directory for test logs
- `temp_home`: Temporary home directory for lock files
- Automatic cleanup after test completion

**Mock Audio Fixtures:**
- `mock_pyaudio`: Mock PyAudio for hardware-independent testing
- `mock_sounddevice`: Mock sounddevice for microphone tests
- Configurable mock responses

**Cleanup Fixtures:**
- `clean_lock_file`: Remove lock file before/after tests
- `clean_log_file`: Remove log file before/after tests
- Prevent test contamination

**Utility Fixtures:**
- `caplog`: pytest built-in for capturing logs
- `tmp_path`: pytest built-in for temporary directories

---

## pytest Configuration (`pytest.ini`)

**Test Discovery:**
- Test file pattern: `test_*.py`
- Test class pattern: `Test*`
- Test function pattern: `test_*`

**Markers:**
- `unit`: Fast tests with mocked dependencies
- `integration`: Slower tests with real components
- `manual`: Manual test scenarios requiring human verification
- `whisper_cpp`: Tests specific to C++ implementation

**Coverage Options:**
- Source: Application code (exclude tests)
- Reports: HTML and terminal
- Threshold: 85% for stability code

**Execution Options:**
- Verbose output for detailed feedback
- Short traceback format for readability
- Strict marker enforcement

---

## CI/CD Pipeline (`.github/workflows/tests.yml`)

**Build Steps:**
1. Checkout source code
2. Set up Python environment (3.9+)
3. Install dependencies via poetry
4. Run test suite with coverage
5. Upload coverage reports

**Test Execution:**
- Run all tests: unit and integration
- Generate coverage reports
- Fail build on test failures
- Fail build on coverage regression

**Quality Gates:**
- All tests must pass
- Coverage must meet threshold (85%)
- No critical issues in static analysis

**Platform:**
- macOS runner for platform-specific testing
- Python 3.9+ environment
- Coverage reporting integration

---

## Acceptance Criteria

- [ ] `conftest.py` with shared fixtures created
- [ ] `pytest.ini` with configuration created
- [ ] CI/CD workflow configured in GitHub Actions
- [ ] All fixtures working correctly
- [ ] Test markers functional
- [ ] Coverage reporting configured
- [ ] CI pipeline runs on push and PR
- [ ] Quality gates enforced

---

## Implementation Context (Not Part of Spec)

**Configuration Files:**
- `tests/conftest.py`: Shared fixtures
- `pytest.ini`: pytest configuration
- `.github/workflows/tests.yml`: CI/CD pipeline

**Example Fixture:**
```python
@pytest.fixture
def temp_log_dir(tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    yield log_dir
    # Cleanup automatic via tmp_path
```

**Example CI Workflow:**
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: poetry install
      - run: poetry run pytest --cov
```
