# Issue: Pluggable Transcription Backend Integration

**Status**: Implemented  
**Priority**: High  
**Estimated Complexity**: Complex  
**Created**: 2026-02-09  
**Last Updated**: 2026-02-09  
**Parent Epic**: `[19-00-00]`

## 0) One-line Summary
Integrate `python-whisper` and `whisper.cpp` behind one backend interface while preserving current UX.

## 2) Scope
### In Scope
- Add backend selector (`--backend`) and default behavior policy.
- Wire both backend implementations into existing recording flow.
- Keep typing/hotkey/tray behavior unchanged.

### Out of Scope / Non-goals (MANDATORY)
- No broad UI redesign.
- No removal of existing Python backend.

## 5) Acceptance Criteria (MANDATORY, Testable)
- [x] AC1: Both backends implement shared interface and pass contract tests.
- [x] AC2: `--backend python` and `--backend whispercpp` both execute end-to-end flow.
- [x] AC3: Default path remains stable and reversible.

## 16) Implementation Notes
- Added pluggable backend helper module: `transcription_backends.py`
  - `create_transcription_backend(...)`
  - `WhisperCppTranscriber`
  - `validate_whispercpp_paths(...)`
- Added CLI selector and backend-specific options in `whisper-dictation.py`:
  - `--backend {python,whispercpp}` (default `python`)
  - `--whispercpp-cli`
  - `--whispercpp-model`
  - `--whispercpp-args`
  - `--whispercpp-timeout-sec`
- Main runtime now builds selected backend via explicit factory wiring while keeping existing recorder/hotkey/tray flow unchanged.
- Added tests:
  - `tests/test_transcription_backends.py`
  - `tests/test_whisper_dictation_args.py`
- Manual E2E smoke verified on Windows for both backends:
  - `--backend python`: passed
  - `--backend whispercpp`: passed
- Observation from manual smoke:
  - whisper.cpp path is significantly faster than python baseline
  - quality is visibly worse for some utterances; requires model-quality follow-up

## 15) Test Plan (MANDATORY)
### Minimal verification (fast)
- parse/selection tests for backend CLI option
- backend interface unit tests

### Full verification (slower)
- manual end-to-end runs for both backends on Windows
- regression smoke on macOS path

## 20) Brittleness Analysis (MANDATORY before Status = Ready)
**BRITTLENESS ANALYSIS:**
- Over-specified elements: no specific final class filenames mandated
- Under-specified elements: concrete timeout/queue sizing knobs
- Flexibility score: Medium
- Fixes applied: constraints focus on behavior and reversibility
- Recommendation: Add detail for operational defaults during implementation
