# Issue: Safe Fallback and Incremental Release Controls

**Status**: Implemented  
**Priority**: High  
**Estimated Complexity**: Medium  
**Created**: 2026-02-09  
**Last Updated**: 2026-02-09  
**Parent Epic**: `[19-00-00]`

## 0) One-line Summary
Add strict fallback and release controls so acceleration rollout cannot break core dictation workflow.

## 2) Scope
### In Scope
- Fallback rules when selected backend fails at startup/runtime.
- Logging and user-facing diagnostics for backend selection/fallback.
- Rollback instructions and guarded default switching.

### Out of Scope / Non-goals (MANDATORY)
- No performance tuning in this issue.
- No hardware-specific deep optimization.

## 5) Acceptance Criteria (MANDATORY, Testable)
- [x] AC1: Backend failure triggers deterministic fallback to stable backend.
- [x] AC2: Fallback reason is visible in logs.
- [x] AC3: Release can be toggled back without code changes.

## 16) Implementation Notes
- Added deterministic fallback wrapper in `transcription_backends.py`:
  - `DeterministicFallbackTranscriber`
  - `create_backend_with_fallback(...)`
- Startup fallback implemented:
  - if selected backend fails to initialize and fallback is enabled, app switches to fallback backend.
- Runtime fallback implemented:
  - if selected backend fails during `transcribe(...)`, app switches to fallback backend once and retries.
- Added fallback controls in `whisper-dictation.py`:
  - `--fallback-backend {python,whispercpp,none}`
  - `--disable-backend-fallback`
  - env toggle: `WHISPER_DISABLE_BACKEND_FALLBACK=1`
- Added logging for:
  - selected backend + fallback policy at startup
  - startup fallback activation reason
  - runtime fallback activation reason
- Added tests:
  - startup fallback failure path
  - runtime fallback switch path
  - fallback disabled path

## 15) Test Plan (MANDATORY)
### Minimal verification (fast)
- simulated backend failure unit tests
- fallback path tests

### Full verification (slower)
- manual forced-failure scenarios on Windows

## 20) Brittleness Analysis (MANDATORY before Status = Ready)
**BRITTLENESS ANALYSIS:**
- Over-specified elements: none
- Under-specified elements: exact log message schema
- Flexibility score: High
- Fixes applied: behavior-level guarantees prioritized
- Recommendation: Good balance
