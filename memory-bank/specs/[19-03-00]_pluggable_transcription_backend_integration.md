# Issue: Pluggable Transcription Backend Integration

**Status**: Draft  
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
- [ ] AC1: Both backends implement shared interface and pass contract tests.
- [ ] AC2: `--backend python` and `--backend whispercpp` both execute end-to-end flow.
- [ ] AC3: Default path remains stable and reversible.

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

