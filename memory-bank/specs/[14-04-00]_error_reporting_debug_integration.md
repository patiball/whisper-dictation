# User Story: Error Reporting and Debug Integration

**ID**: 14-04-00
**Epic**: [14-00-00] Sequential Test Runner for Human-Friendly Execution
**Priority**: High
**Complexity**: Simple
**Estimate**: 10-15 minutes

## User Story
As a developer debugging test failures, I want detailed error context and actionable debugging commands, so that I can quickly investigate and fix failing tests without manual command construction.

## Acceptance Criteria
- [ ] Failed tests show specific test method name that failed
- [ ] Error messages display the actual assertion or exception details
- [ ] File location and line number provided for failed assertions
- [ ] Auto-generated debugging commands for re-running specific failed tests
- [ ] Error context includes relevant test parameters and fixtures
- [ ] Stack traces formatted for readability (truncated to relevant frames)
- [ ] Suggestions for common failure patterns and solutions

## Behavior Examples

### Detailed Failure Report:
```
[3/9] 🐕 Audio Watchdog Tests (test_audio_watchdog.py)...
❌ FAILED (0.8s) - Test: TestStallDetection::test_stall_detection_timeout

🔍 ERROR DETAILS:
   Type: AssertionError
   Message: Expected timeout < 10s, got 15.2s
   Location: tests/test_audio_watchdog.py:145
   Function: test_stall_detection_timeout

📋 TEST CONTEXT:
   Test File: tests/test_audio_watchdog.py
   Test Class: TestStallDetection
   Test Method: test_stall_detection_timeout
   Markers: @pytest.mark.unit

💡 DEBUGGING COMMANDS:
   # Re-run just this test with verbose output:
   poetry run pytest tests/test_audio_watchdog.py::TestStallDetection::test_stall_detection_timeout -v -s

   # Re-run with debugging enabled:
   poetry run pytest tests/test_audio_watchdog.py::TestStallDetection::test_stall_detection_timeout -v -s --pdb

   # Run all tests in this class:
   poetry run pytest tests/test_audio_watchdog.py::TestStallDetection -v

🔧 COMMON SOLUTIONS:
   • Check if timeout threshold needs adjustment
   • Verify heartbeat tracking implementation
   • Review test timing and mock behavior
```

### Integration Test Failure:
```
[9/9] 🔗 Integration Tests (test_integration_recording.py)...
❌ FAILED (2.1s) - Test: TestFullRecordingFlow::test_complete_recording_cycle

🔍 ERROR DETAILS:
   Type: subprocess.TimeoutExpired
   Message: Command 'python whisper-dictation.py' timed out after 30 seconds
   Location: tests/test_integration_recording.py:89
   Function: test_complete_recording_cycle

📋 TEST CONTEXT:
   Test File: tests/test_integration_recording.py
   Test Class: TestFullRecordingFlow
   Test Method: test_complete_recording_cycle
   Markers: @pytest.mark.integration

💡 DEBUGGING COMMANDS:
   # Re-run with longer timeout:
   poetry run pytest tests/test_integration_recording.py::TestFullRecordingFlow::test_complete_recording_cycle -v -s

   # Check application logs:
   tail -f ~/.whisper-dictation.log

   # Run integration tests manually:
   python scripts/run_sequential_tests.py --category integration --continue

🔧 COMMON SOLUTIONS:
   • Check if application is hanging during startup
   • Verify microphone permissions and device availability
   • Review lock file cleanup from previous runs
```

## Key Assumptions
- **Assumption**: Developers want immediate, actionable debugging information
- **Validation**: Reduces time spent constructing debug commands manually
- **Assumption**: Common failure patterns can be identified and suggested
- **Validation**: Pattern recognition speeds up problem resolution

## Related Tasks
- [14-04-01] Parse pytest output for structured error extraction
- [14-04-02] Generate debugging commands based on test context
- [14-04-03] Create common failure pattern suggestion system
- [14-04-04] Format stack traces for readability and relevance

## Implementation Context (Not Part of Spec)

**Current Location**: Error reporting module within `scripts/run_sequential_tests.py`
**Key Variables**: Error parsing patterns, command templates, suggestion database
**Note**: These implementation details change. The spec above remains stable.

**Current Line References** (for review purposes only):
- Pytest error output format: pytest.ini:17-19
- Test markers for context: pytest.ini:8-13
- Existing test structure: tests/ directory organization
