# User Story: Verify and Enforce GPU Usage in C++ Tests
**ID**: 16-07-00
**Epic**: [16-00-00] Post-Epic 15 Test Infrastructure & Functional Fixes
**Status**: Ready
**Priority**: High
**Estimate**: 30-45 minutes

## User Story
As a developer, I want to be certain that the `whisper.cpp` integration tests are using the GPU, so that we are accurately testing the performance and behavior of the accelerated backend.

## Acceptance Criteria
- [ ] It is confirmed that all tests in `tests/test_whisper_cpp.py` utilize the Metal GPU on Apple Silicon hardware.
- [ ] A mechanism is in place to detect and fail tests that incorrectly fall back to CPU.
- [ ] Any configuration errors preventing GPU usage are identified and fixed.

## File Changes Required
- `tests/test_whisper_cpp.py`: Modify tests to parse the `stderr` from `whisper-cli` and assert that `use gpu = 1` and `ggml_metal_device_init` messages are present.
- `transcriber.py`: Ensure the `Transcriber` class correctly passes GPU-related flags to the `whisper-cli` process during tests.
