# User Story: Whisper.cpp Integration Fixes
**ID**: 16-04-00
**Epic**: [16-00-00] Post-Epic 15 Test Infrastructure & Functional Fixes
**Status**: Ready
**Priority**: High
**Estimate**: 45-60 minutes

## User Story
As a developer, I want the `whisper.cpp` integration tests to pass, so that I can ensure the C++ backend for transcription is functioning correctly.

## Acceptance Criteria
- [ ] `test_audio_cutting_regression` passes, correctly transcribing the test audio.
- [ ] `test_language_auto_detection` and `test_language_auto_detection_polish` pass, correctly identifying the language.
- [ ] `test_language_detection_with_confidence` passes, correctly parsing the output format.
- [ ] `test_whisper_cli_internal_timeout` passes, with the process exiting with a non-zero code as expected.

## File Changes Required
- `tests/test_whisper_cpp.py`: Investigate the root cause of each failure. This may involve adjusting test assertions, fixing how the `whisper-cli` process is called, or parsing its output differently.
- `transcriber.py`: Potentially adjust the `Transcriber` class if the issue lies in how it interacts with `whisper-cli`.
