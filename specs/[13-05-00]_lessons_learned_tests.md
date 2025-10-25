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

## Test Organization Structure

**Test Directory Hierarchy:**
- Root test directory with shared configuration
- Separate test modules for each major feature
- Integration test subdirectory for end-to-end scenarios
- Manual test documentation subdirectory

**Feature Coverage:**
- Lock file mechanism (basics, multi-instance, signal handling, stale files)
- Microphone access check (basics, timing, integration)
- Audio watchdog (heartbeat, stall detection, thread safety, restart)
- Logging system (setup, rotation, events, format, fallback)
- Integration scenarios (multi-instance, shutdown, watchdog recovery, full flow)

---

## Unit Test Scenarios

### Lock File Tests
**Lock file creation:**
- Lock file should exist after initialization
- Lock file should contain valid process ID
- Cleanup should remove lock file

**Dead PID handling:**
- Lock file with non-existent PID should allow startup
- Lock file should be updated with current PID
- Warning should be logged about stale lock file

### Watchdog Tests
**Heartbeat tracking:**
- Heartbeat update should change timestamp
- Multiple updates should show progression
- Timestamp should be accessible for monitoring

**Stall detection:**
- Long period without heartbeat should trigger warning
- Stall should initiate recovery sequence
- Recovery should be logged appropriately

### Logging Tests
**Setup and configuration:**
- Log file should be created at specified location
- Log level should be configurable
- Multiple log levels should filter correctly

**Rotation behavior:**
- Large volume of logs should trigger rotation
- Backup files should be created
- Old backups should be deleted when limit exceeded

---

## Integration Test Scenarios

### Multi-Instance Behavior
**Second instance handling:**
- Starting application when already running should prevent second instance
- Second instance should exit gracefully with appropriate message
- Lock file should remain valid for first instance
- First instance cleanup should work correctly

**Process cleanup:**
- Terminated instance should release lock
- New instance should start successfully after previous cleanup
- Crashed instance should leave detectable stale lock

### Full Recording Flow
**End-to-end operation:**
- Complete recording, transcription, and output cycle
- All components interact correctly
- Logging captures full sequence
- No resource leaks or hangs

### Watchdog Recovery
**Stall detection and recovery:**
- Simulated stall triggers watchdog
- Recovery sequence executes correctly
- Application continues operation after recovery
- All events logged appropriately

---

## Manual Test Scenarios

### Test 1: Lock File Behavior

**Setup Requirements:**
- Clean system with no running instances
- Lock file should not exist initially

**Scenario A: Normal Startup and Shutdown**
1. Start application
2. Verify lock file created with valid PID
3. Verify application enters listening state
4. Send shutdown signal
5. Verify lock file removed cleanly
6. Expected: Clean startup and shutdown cycle

**Scenario B: Second Instance Prevention**
1. Start first instance
2. Attempt to start second instance
3. Verify second instance exits with error message
4. Shutdown first instance
5. Verify new instance can now start
6. Expected: Only one instance runs at a time

**Scenario C: Stale Lock File Recovery**
1. Create lock file with invalid (very high) PID
2. Start application
3. Verify application starts successfully
4. Verify lock file updated with current PID
5. Expected: Application recovers from stale lock

### Test 2: Audio Watchdog

**Setup Requirements:**
- Debug logging enabled
- Log monitoring active

**Scenario A: Normal Operation**
1. Start application with debug logging
2. Perform several recording operations
3. Verify no stall warnings in logs
4. Verify heartbeat updates visible (debug level)
5. Expected: Normal operation without watchdog intervention

**Scenario B: Watchdog Monitoring**
1. Start application with debug logging
2. Verify watchdog initialization logged
3. Record audio and check for heartbeat updates
4. Expected: Watchdog actively monitoring

### Test 3: Microphone Access

**Scenario A: Microphone Available**
1. Start application normally
2. Verify microphone check passes
3. Verify recording functionality works
4. Expected: Normal microphone operation

**Scenario B: Permission Denied**
1. Revoke microphone permissions via system settings
2. Start application
3. Verify access test failure logged
4. Re-enable permissions
5. Restart and verify recovery
6. Expected: Graceful handling of permission issues

### Test 4: Logging System

**Scenario A: Log File Creation**
1. Remove existing log file
2. Start application
3. Verify log file created in expected location
4. Verify startup message present
5. Expected: Log file created and populated

**Scenario B: Log Rotation**
1. Generate high volume of log entries
2. Monitor log file size
3. Verify rotation occurs at size limit
4. Verify backup files created
5. Verify old backups deleted
6. Expected: Rotation prevents unbounded growth

**Scenario C: Log Level Filtering**
1. Test with DEBUG level (very verbose)
2. Test with WARNING level (errors/warnings only)
3. Verify appropriate filtering
4. Expected: Log levels control verbosity correctly

---

## Test Fixtures Strategy

### Shared Test Infrastructure

**Temporary Directory Fixtures:**
- Provide isolated directories for log files during testing
- Ensure no contamination of user's home directory
- Automatic cleanup after test completion

**Mock Audio Fixtures:**
- Mock audio hardware interfaces for testing without physical devices
- Provide configurable mock responses
- Simulate success and failure scenarios

**Cleanup Fixtures:**
- Clean lock files before and after tests
- Clean log files before and after tests
- Prevent test contamination
- Ensure repeatable test execution

### Fixture Categories

**Resource Isolation:**
- Temporary directories
- Mock hardware interfaces
- Isolated configuration

**State Management:**
- Pre-test cleanup
- Post-test cleanup
- State verification

**Test Utilities:**
- Common assertion helpers
- Data generation utilities
- Mock configuration helpers

---

## Test Framework Configuration

### Test Discovery
- Test files should follow naming convention
- Test classes should follow naming convention
- Test functions should follow naming convention
- Tests organized in designated test directory

### Execution Options
- Verbose output for detailed feedback
- Short traceback format for readability
- Strict marker enforcement
- Summary of all test results
- Coverage reporting in multiple formats

### Test Markers
- **unit**: Fast tests with mocked dependencies
- **integration**: Slower tests with real components
- **manual**: Manual test scenarios requiring human verification
- **whisper_cpp**: Tests specific to C++ implementation

### Coverage Configuration
- HTML reports for detailed analysis
- Terminal reports for immediate feedback
- Coverage of application code (excluding tests)

---

## Test Execution Methods

### Test Scope Options
- **All tests**: Run entire test suite
- **Unit tests only**: Run fast, isolated tests
- **Integration tests only**: Run end-to-end scenarios
- **Specific test file**: Run tests for single module
- **Specific test class/function**: Run individual test

### Coverage Options
- **With coverage**: Generate coverage reports
- **HTML reports**: Detailed interactive coverage analysis
- **Terminal reports**: Immediate coverage feedback
- **Coverage thresholds**: Fail if coverage drops below target

### Development Workflows
- **Watch mode**: Automatically rerun tests on file changes
- **Parallel execution**: Run tests concurrently for speed
- **Verbose mode**: Detailed output for debugging
- **Quiet mode**: Minimal output for CI/CD

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

## CI/CD Integration Strategy

### Continuous Integration Requirements

**Build Pipeline:**
- Checkout source code
- Set up Python environment
- Install dependencies via package manager
- Run test suite
- Generate coverage reports
- Upload coverage data

**Test Execution:**
- Run unit tests (fast feedback)
- Run integration tests (comprehensive validation)
- Fail build on test failures
- Fail build on coverage regression

**Artifact Management:**
- Store coverage reports
- Store test results
- Archive build artifacts
- Publish coverage trends

### CI/CD Platform Configuration

**Platform Requirements:**
- macOS runner for platform-specific testing
- Python environment support
- Coverage reporting integration
- Artifact storage

**Quality Gates:**
- All tests must pass
- Coverage must meet threshold
- No critical issues in static analysis
- Build must complete successfully

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

### Failure Mode 1: Tests Coupled to Implementation Details
**What Happens**: Tests break when internal implementation changes, even though behavior unchanged
**Impact**: High maintenance burden, resistance to refactoring
**Prevention**: Test observable behavior and public interfaces, not internal mechanics
**Recovery**: Decouple tests by using boundary mocks and behavioral assertions

### Failure Mode 2: Non-Deterministic Test Results
**What Happens**: Tests pass or fail randomly due to timing, race conditions, or uncontrolled state
**Impact**: Loss of confidence in test suite, wasted debugging time
**Prevention**: Use deterministic delays, seed random generators, isolate test state
**Recovery**: Mark flaky tests, implement retry logic, fix root cause

### Failure Mode 3: Filesystem Contamination
**What Happens**: Tests modify user files or leave artifacts that affect subsequent tests
**Impact**: Tests fail when run in different order, user data corruption risk
**Prevention**: Use temporary directories, implement cleanup fixtures
**Recovery**: Pre/post-test cleanup, isolated test environments

### Failure Mode 4: Slow Test Execution
**What Happens**: Test suite takes too long, slowing development feedback loop
**Impact**: Developers skip running tests, CI/CD pipeline bottleneck
**Prevention**: Keep unit tests fast, separate slow integration tests
**Recovery**: Parallel execution, selective test running, optimization

### Failure Mode 5: Mock-Reality Divergence
**What Happens**: Mocks behave differently than real components they replace
**Impact**: Tests pass but production code fails, false confidence
**Prevention**: Regularly verify mock behavior matches reality
**Recovery**: Integration tests with real components, contract testing

---

## Success Metrics

- ✅ All tests pass in CI
- ✅ Coverage >85% for stability code
- ✅ New features have tests BEFORE implementation
- ✅ No regressions in existing tests
- ✅ Test suite runs in <2 minutes
- ✅ Manual test scenarios documented and verified

---

## Implementation Approach

### Foundation Phase
**Goal**: Establish basic test infrastructure and simple tests
- Implement shared fixtures and utilities
- Write tests for straightforward components (lock file, microphone check)
- Verify test execution and reporting works
- Achieve initial coverage baseline

### Complex Component Phase
**Goal**: Test concurrent and stateful components
- Write tests for watchdog (threading, timing)
- Write tests for logging (rotation, levels)
- Use mocking for complex dependencies
- Increase coverage of critical paths

### Integration Phase
**Goal**: Validate end-to-end functionality
- Implement integration tests for key workflows
- Document manual test scenarios
- Verify all automated tests pass
- Execute manual test scenarios

### Continuous Integration Phase
**Goal**: Automate test execution in CI/CD pipeline
- Configure CI/CD platform workflow
- Implement quality gates (test pass, coverage threshold)
- Monitor coverage trends over time
- Require passing tests for merge approval

---

## Acceptance Criteria (Ready to Implement)

- [ ] All TDD test cases written (unit + integration)
- [ ] Unit tests all pass
- [ ] Integration tests all pass
- [ ] Coverage exceeds target threshold
- [ ] Manual test scenarios documented
- [ ] CI/CD workflow configured
- [ ] No regressions in existing tests

---

## Implementation Context (Not Part of Spec)

**Current Testing Framework:**
The project currently uses pytest as the test framework with some existing tests in the `tests/` directory for audio and transcription functionality.

**Example Test Structure:**
Tests would be organized with files like `test_lock_file.py`, `test_audio_watchdog.py`, `test_logging.py`, etc. Each test file would contain classes like `TestLockFileBasics`, `TestHeartbeatTracking`, etc., with individual test methods following the pattern `test_<behavior>`.

**Fixture Implementation:**
A `conftest.py` file would provide shared fixtures:
- `temp_log_dir`: Creates temporary directory for test logs
- `mock_pyaudio`: Mocks PyAudio for hardware-independent testing
- `clean_lock_file`: Ensures lock file is cleaned before/after tests
- `clean_log_file`: Ensures log file is cleaned before/after tests

**pytest.ini Configuration:**
Configuration would specify test discovery patterns (`test_*.py`), markers (unit, integration, manual, whisper_cpp), and coverage reporting options (HTML and terminal output).

**CI/CD Workflow:**
A GitHub Actions workflow file (`.github/workflows/tests.yml`) would run on push and pull requests, executing tests on macOS runners with Python environment setup, dependency installation via poetry, test execution, and coverage reporting.

**Example Commands:**
- Run all tests: `poetry run pytest`
- Run unit tests only: `poetry run pytest -m unit`
- Run with coverage: `poetry run pytest --cov=whisper_dictation --cov-report=html`
- Run specific file: `poetry run pytest tests/test_lock_file.py`

**Note**: This implementation context documents current patterns which may evolve. The specification above focuses on WHAT testing should achieve, not HOW to implement it.

