# User Story: Test Category Organization and Ordering

**ID**: 14-03-00
**Epic**: [14-00-00] Sequential Test Runner for Human-Friendly Execution
**Priority**: Medium
**Complexity**: Simple
**Estimate**: 10-15 minutes

## User Story
As a developer running tests, I want tests executed in a logical order from stability to functionality, so that I can validate foundational features before testing more complex integrations.

## Acceptance Criteria
- [ ] Tests execute in logical progression: stability features first, then core functionality
- [ ] Lock file tests run first (foundation for multiple instance prevention)
- [ ] Microphone check tests run second (hardware validation foundation)
- [ ] Audio watchdog tests run third (stream monitoring foundation)
- [ ] Logging system tests run fourth (diagnostics foundation)
- [ ] Core functionality tests run after stability tests (performance, language detection)
- [ ] Integration tests run last (full system validation)
- [ ] C++ tests run conditionally based on whisper-cli availability
- [ ] Option to run specific categories independently

## Behavior Examples

### Default Logical Order:
```
🧪 SEQUENTIAL TEST RUNNER - Whisper Dictation Tests
====================================================

[1/9] 🔒 Lock File Tests (test_lock_file.py)...
✅ PASSED (2.3s) - 4/4 tests

[2/9] 🔒 Lock File Integration (test_lock_file_integration.py)...
✅ PASSED (3.1s) - 3/3 tests

[3/9] 🎤 Microphone Check Tests (test_microphone_check.py)...
✅ PASSED (1.1s) - 3/3 tests

[4/9] 🐕 Audio Watchdog Tests (test_audio_watchdog.py)...
✅ PASSED (2.8s) - 4/4 tests

[5/9] 📝 Logging Tests (test_logging.py)...
✅ PASSED (1.5s) - 3/3 tests

[6/9] ⚡ Performance Tests (test_performance.py)...
✅ PASSED (4.2s) - 2/2 tests

[7/9] 🌍 Language Detection Tests (test_language_detection.py)...
✅ PASSED (3.7s) - 2/2 tests

[8/9] 🎵 Recording Quality Tests (test_recording_quality.py)...
✅ PASSED (2.9s) - 2/2 tests

[9/9] 🔗 Integration Tests (test_integration_recording.py)...
✅ PASSED (5.1s) - 3/3 tests
```

### Category-Specific Execution:
```bash
# Run only stability tests
python scripts/run_sequential_tests.py --category stability

[1/4] 🔒 Lock File Tests (test_lock_file.py)...
[2/4] 🔒 Lock File Integration (test_lock_file_integration.py)...
[3/4] 🎤 Microphone Check Tests (test_microphone_check.py)...
[4/4] 🐕 Audio Watchdog Tests (test_audio_watchdog.py)...

# Run only core functionality tests  
python scripts/run_sequential_tests.py --category core

[1/4] ⚡ Performance Tests (test_performance.py)...
[2/4] 🌍 Language Detection Tests (test_language_detection.py)...
[3/4] 🎵 Recording Quality Tests (test_recording_quality.py)...
[4/4] 📝 Logging Tests (test_logging.py)...
```

## Key Assumptions
- **Assumption**: Logical test ordering provides better debugging experience
- **Validation**: Foundation failures are caught early before complex integrations
- **Assumption**: Developers want to run specific categories during development
- **Validation**: Category selection speeds up iterative development cycles

## Related Tasks
- [14-03-01] Define test category mappings and execution order
- [14-03-02] Implement category filtering command-line options
- [14-03-03] Create stability test category (lock file, microphone, watchdog, logging)
- [14-03-04] Create core functionality category (performance, language, quality)
- [14-03-05] Create integration category (full flow, C++ implementation)

## Implementation Context (Not Part of Spec)

**Current Location**: Test configuration within `scripts/run_sequential_tests.py`
**Key Variables**: Category definitions, test file mappings, execution order
**Note**: These implementation details change. The spec above remains stable.

**Current Line References** (for review purposes only):
- Test file discovery: pytest.ini:3-5
- Test markers: pytest.ini:8-13
- Existing test organization: tests/ directory structure
