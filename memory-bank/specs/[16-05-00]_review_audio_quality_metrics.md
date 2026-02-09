# User Story: Review Audio Quality Metrics
**ID**: 16-05-00
**Epic**: [16-00-00] Post-Epic 15 Test Infrastructure & Functional Fixes
**Status**: Ready
**Priority**: Medium
**Estimate**: 20-30 minutes

## User Story
As a developer, I want the audio quality tests to provide reliable and meaningful results, so that I can accurately assess the quality of recorded audio samples.

## Acceptance Criteria
- [ ] The `test_audio_quality_metrics` test passes.
- [ ] The thresholds for RMS, silence ratio, and other metrics are reviewed and determined to be appropriate for the test audio files.
- [ ] If the audio files are genuinely low quality, they are replaced with new, higher-quality reference recordings.

## File Changes Required
- `tests/test_recording_quality.py`: Adjust the assertion thresholds within `test_audio_quality_metrics`.
- `tests/audio/`: If necessary, replace the problematic `.wav` files (`test_polish_20250630_083944.wav`, `test_english_20250630_085152.wav`).
