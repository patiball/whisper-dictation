# Epic: Transcription Test Robustness

**ID**: 17-00-00
**Status**: Draft
**Priority**: Medium
**Complexity**: Medium
**Estimate**: 8–12 hours

## Epic Overview

As a developer maintaining transcription tests, I want the test suite to tolerate normal Whisper model variations (number format, punctuation, minor rephrasing) and reflect real regressions, so that CI is stable and failures are actionable.

## Problem Statement

The whisper-cpp integration tests are failing due to overly strict text matching expectations that don't account for normal model behavior variations. Tests expect exact string matches but Whisper models naturally produce minor variations in:

- Number format (digits vs. words: "1, 2, 3" vs. "one, two, three")
- Punctuation (commas vs. periods)
- Capitalization and spacing
- Language detection returning empty strings instead of language codes

Current failure rate: 6/9 whisper-cpp tests failing due to expectation mismatches, not actual functionality issues.

## Analysis

### Root Cause
Test expectations were created with different model versions or manual transcription, leading to exact-string-match assertions that fail on legitimate model output variations.

### Current Failing Tests
1. **Language Detection Tests**: Return empty strings instead of 'en'/'pl'
2. **Audio Content Tests**: Expect specific punctuation/number formatting
3. **Confidence Tests**: Expect specific output format that changed

### Impact
- False negative test results
- Developer confusion about actual vs. test failures  
- Reduced confidence in test suite reliability
- CI/CD pipeline disruption

## Proposed Solution

### Phase 1: Update Expected Values (Quick Fix)
**Goal**: Align test expectations with current model output

**Tasks**:
1. Update JSON expectation files to use digits instead of written numbers
2. Update punctuation expectations to match current model output
3. Fix incomplete/incorrect expected text in regression tests

**Files to Modify**:
- `tests/audio/test_english_5s_20250630_094048.json`
- `tests/audio/test_english_10s_20250630_094136.json` 
- `tests/audio/test_polish_5s_20250630_094037.json`
- `tests/audio/test_polish_10s_20250630_094120.json`

### Phase 2: Implement Fuzzy Matching (Robust Fix)
**Goal**: Create test infrastructure tolerant of expected variations

**Components**:

1. **Text Normalization Function**
   ```python
   def normalize_transcription(text: str) -> str:
       # Remove timestamps, normalize punctuation, whitespace, case
   ```

2. **Fuzzy Matching Function**  
   ```python
   def fuzzy_transcription_match(expected: str, actual: str, threshold: float = 0.85) -> bool:
       # Use difflib.SequenceMatcher for similarity comparison
   ```

3. **Number Format Tolerance**
   ```python
   def normalize_numbers(text: str) -> str:
       # Convert written numbers to digits for comparison
   ```

### Phase 3: Fix Language Detection (Command Investigation)
**Goal**: Understand why language detection returns empty strings

**Tasks**:
1. Debug `--detect-language` flag behavior manually
2. Check if flag syntax changed in whisper-cli version
3. Update test command construction if needed
4. Fix confidence detection output parsing

### Phase 4: Test Framework Integration (Long-term)
**Goal**: Make robust testing the default approach

**Tasks**:
1. Create `TranscriptionTestConfig` class for configurable tolerance
2. Add helper fixtures for common test patterns
3. Update existing tests to use new framework
4. Document best practices for transcription testing

## Implementation Plan

### Stage 1: Quick Fixes (1-2 hours)
- [ ] Update JSON expectation files with current model outputs
- [ ] Fix `test_audio_cutting_regression` expected text
- [ ] Manual verification of updated expectations

### Stage 2: Fuzzy Matching (3-4 hours)  
- [ ] Implement normalization functions
- [ ] Implement fuzzy matching with configurable threshold
- [ ] Create unit tests for fuzzy matching functions
- [ ] Update failing transcription tests to use fuzzy matching

### Stage 3: Language Detection Fix (2-3 hours)
- [ ] Manual testing of `--detect-language` commands
- [ ] Debug empty string return issue
- [ ] Fix command construction or parsing
- [ ] Update confidence detection tests

### Stage 4: Framework Integration (4-5 hours)
- [ ] Create test configuration classes
- [ ] Add helper fixtures and utilities
- [ ] Update test documentation
- [ ] Create examples for future transcription tests

## Acceptance Criteria

### Functional Requirements
- [ ] All whisper-cpp tests pass with realistic expectations
- [ ] Tests tolerate normal model variations (numbers, punctuation)
- [ ] Language detection returns proper language codes
- [ ] Fuzzy matching threshold configurable (default 85%)
- [ ] Tests still catch real transcription problems

### Quality Requirements  
- [ ] Test execution time not significantly increased
- [ ] Clear error messages when tests fail legitimately
- [ ] Backward compatibility with existing test structure
- [ ] Documentation for new testing patterns

### Verification Methods
- [ ] All 9 whisper-cpp tests pass
- [ ] Manual verification with different audio samples
- [ ] Fuzzy matching unit tests pass
- [ ] Integration test with modified audio expectations

## Risk Assessment

**Low Risk**: Changes are isolated to test infrastructure, not production code

**Mitigation Strategies**:
- Implement changes incrementally with verification at each stage
- Maintain ability to use exact matching when needed
- Preserve original test expectations as reference
- Add logging to show similarity scores during debugging

## Dependencies

- Existing whisper-cli installation and model files
- Current test audio files in `tests/audio/`
- Python `difflib` library (standard library)
- pytest testing framework

## Success Metrics

- Whisper-cpp test success rate: 0/9 → 9/9
- False positive reduction: Eliminate expectation-mismatch failures
- Maintainability: New audio files can be tested without exact transcription
- Developer experience: Clear pass/fail reasons in test output

## Future Considerations

- **Model Version Tolerance**: Framework should handle future whisper model updates
- **Language Support**: Fuzzy matching should work across different languages  
- **Performance Testing**: Extend framework to performance/quality regression tests
- **Audio Quality**: Consider audio file standardization for consistent results

## Related Work

- Links to: `[15-00-00]_test_infrastructure_repair.md` (test stability foundation)
- Links to: `memory-bank/lessons_learned/test_status_comprehensive_analysis.md` (current state)
- Addresses issues identified in Epic 16 post-repair verification