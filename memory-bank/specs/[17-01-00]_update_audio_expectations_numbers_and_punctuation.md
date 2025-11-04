# User Story: Update Audio Expectations (Numbers and Punctuation)

**ID**: 17-01-00
**Epic**: [17-00-00] Transcription Test Robustness
**Status**: Draft
**Priority**: Medium
**Complexity**: Low
**Estimate**: 1–2 hours

## User Story
As a developer, I want the expected transcriptions to reflect the model's standard output (digits for numbers, minor punctuation differences), so tests don't fail on harmless formatting variations.

## Background
- Current expectations use written numbers ("one, two, three") and strict punctuation.
- Whisper outputs digits and may vary in punctuation.

## Acceptance Criteria
- [ ] JSON expectations updated to use digits instead of written numbers.
- [ ] Punctuation in expectations aligned with actual model output where appropriate.
- [ ] No change to semantic content of expectations.
- [ ] All tests that only differ in number format/punctuation pass without introducing fuzzy matching.

## Behavior Examples
- Before: "Numbers: one, two, three, four, five" → After: "Numbers 1, 2, 3, 4, 5"
- Before: "language test." → After: "language test, numbers 1, 2, 3, 4, 5."

## Files Affected
- tests/audio/test_english_5s_20250630_094048.json
- tests/audio/test_english_10s_20250630_094136.json
- tests/audio/test_polish_5s_20250630_094037.json
- tests/audio/test_polish_10s_20250630_094120.json

## Implementation Context (Not Part of Spec)
- Verify current outputs with `whisper-cli` and update JSON accordingly.
- Keep a note of model version used for expectations.