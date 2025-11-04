# User Story: Normalization and Fuzzy Matching Framework

**ID**: 17-02-00
**Epic**: [17-00-00] Transcription Test Robustness
**Status**: Draft
**Priority**: High
**Complexity**: Medium
**Estimate**: 3–4 hours

## User Story
As a developer, I want reusable utilities for normalizing and comparing transcriptions with fuzzy matching, so tests tolerate minor variations but detect real regressions.

## Background
- Exact string matching causes false negatives.
- Variations to tolerate: punctuation, case, whitespace, timestamps, number format.

## Acceptance Criteria
- [ ] Provide normalization utility (remove timestamps, normalize punctuation/case/whitespace).
- [ ] Provide optional number normalization (written numbers → digits) toggle.
- [ ] Provide fuzzy matching with configurable threshold (default 0.85).
- [ ] Clear assertion helpers with meaningful failure messages (similarity score, diffs).
- [ ] Unit tests for utilities (positive and negative cases).

## Behavior Examples
- "This is an English language test, numbers 1, 2, 3" ≈ "This is an English language test. Numbers one, two, three".
- Polish examples accept digit formatting and minor rephrasing.

## Files Affected
- tests/utils/transcription_assertions.py (new)
- tests/test_whisper_cpp.py (migrate selected assertions to use helpers)

## Implementation Context (Not Part of Spec)
- Use `difflib.SequenceMatcher` for similarity.
- Provide `assert_transcription_similar(expected, actual, threshold=0.85, options=...)`.