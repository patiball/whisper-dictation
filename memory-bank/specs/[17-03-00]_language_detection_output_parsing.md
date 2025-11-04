# User Story: Language Detection Output Parsing

**ID**: 17-03-00
**Epic**: [17-00-00] Transcription Test Robustness
**Status**: Draft
**Priority**: High
**Complexity**: Medium
**Estimate**: 2–3 hours

## User Story
As a developer, I want the language detection tests to parse the current `whisper-cli` output format reliably, so that language detection tests reflect actual functionality instead of failing on format differences.

## Background
- `--detect-language` returns empty stdout in the current environment.
- Confidence printing format may differ or be unsupported.

## Acceptance Criteria
- [ ] Investigate and document current `whisper-cli --detect-language` output.
- [ ] Update tests to parse language from the correct output stream (stdout/stderr) or file.
- [ ] If confidence is not available, skip confidence assertions with clear rationale.
- [ ] Tests pass for both English and Polish samples.
- [ ] Backward-compatible approach if CLI behavior differs across versions.

## Behavior Examples
- If CLI prints language code on stderr, parse it from there.
- If CLI writes to file or prints additional info, adapt parsing accordingly.

## Files Affected
- tests/test_whisper_cpp.py
- tests/utils/whisper_cli_runner.py (optional helper)

## Implementation Context (Not Part of Spec)
- Capture both stdout and stderr when running CLI.
- Add logging of raw outputs during test debug mode.