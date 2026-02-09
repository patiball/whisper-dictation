# Issue: Supervisor GPU Warning and whisper.cpp Model Confirmation

**Status**: Implemented  
**Priority**: High  
**Estimated Complexity**: Medium  
**Created**: 2026-02-09  
**Last Updated**: 2026-02-09  
**Parent Epic**: `[19-00-00]`

## 0) One-line Summary
Expose explicit runtime confirmation of whisper.cpp model/acceleration and show supervisor warning when selected profile likely falls back to CPU.

## 1) Overview (What & Why)
### Problem
- Profile switching works, but when OpenVINO artifacts are missing, runtime becomes slow and appears like model-switch failure.
- Current supervisor status does not clearly show acceleration degradation risk.

### Goal
- Provide immediate visibility of:
  - selected vs actually loaded model,
  - acceleration state (`gpu_openvino`, `cpu_fallback`, `unknown`).

## 2) Scope
### In Scope
- whisper.cpp diagnostics parsing and status emission.
- supervisor preflight warning for missing OpenVINO encoder artifacts.
- supervisor status update from worker runtime status lines.

### Out of Scope / Non-goals (MANDATORY)
- Auto-generation of missing OpenVINO artifacts.
- Backend quality policy changes.

## 4) Requirements
### Functional Requirements
- FR1: worker emits machine-readable whispercpp status event with model+acceleration.
- FR2: worker prints human-readable model/acceleration confirmation after transcription.
- FR3: supervisor warns when OpenVINO GPU mode is requested but encoder artifacts are missing.
- FR4: supervisor status reflects runtime `cpu_fallback` warning from worker events.

### Constraints (Hard Rules)
- Existing profile switching flow must remain unchanged.
- If diagnostics cannot be parsed, state must degrade to `unknown` (not crash).

## 5) Acceptance Criteria (MANDATORY, Testable)
- [x] AC1: Switching to `cpp-medium` with missing encoder artifacts triggers explicit supervisor warning.
- [x] AC2: whispercpp transcription logs include model and acceleration summary.
- [x] AC3: supervisor status snapshot includes warning/acceleration fields.
- [x] AC4: unit tests cover parser/warning/status behavior.

## 15) Test Plan (MANDATORY)
### Minimal verification (fast)
- `python -m py_compile transcription_backends.py supervisor_worker.py whisper-dictation-supervisor.py`

### Full verification (slower)
- `pytest tests/test_transcription_backends.py tests/test_supervisor_worker.py tests/test_whisper_dictation_args.py tests/test_runtime_contracts.py`

## 19) Change Log (Keep short)
- 2026-02-09: Draft created.
- 2026-02-09: Implemented diagnostics parser, supervisor warnings, tests, and docs updates.

## 20) Brittleness Analysis (MANDATORY before Status = Ready)
**BRITTLENESS ANALYSIS:**
- Over-specified elements:
  - none; status format is compact and parser-tolerant.
- Under-specified elements:
  - future non-OpenVINO acceleration types.
- Flexibility score: Medium
- Fixes applied:
  - unknown-state fallback for parser misses.
- Recommendation: Good balance for immediate UX fix.
