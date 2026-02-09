# Issue: Supervisor + Worker Runtime for Fast Model/Backend Switching

**Status**: Implemented  
**Priority**: High  
**Estimated Complexity**: Complex  
**Created**: 2026-02-09  
**Last Updated**: 2026-02-09  
**Parent Epic**: `[19-00-00]`

## 0) One-line Summary
Introduce a full Supervisor+Worker runtime so users can switch backend/model from tray controls by restarting only the worker process (without rebuild).

## 1) Overview (What & Why)
### Problem
- Current app runs runtime UI, hotkey logic, and transcription backend in one process.
- Switching backend/model requires long manual command invocation and manual process restarts.
- A crash in the runtime process can fully drop user control until manual recovery.

### Goal
- Split responsibilities:
  - Supervisor process: tray UX + worker lifecycle.
  - Worker process: dictation runtime only.
- Make model/backend switching fast and repeatable via tray menu.

### Success Metrics
- Worker profile switch can be triggered from tray and completes via controlled restart.
- Direct command path remains available as rollback path.
- Crash recovery attempts are bounded and visible in logs.

## 2) Scope
### In Scope
- Worker headless runtime mode.
- Supervisor module with process lifecycle management.
- Supervisor tray entrypoint with backend/model profile actions.
- Process crash autorestart guardrails and logs.
- Tests for supervisor process logic and runtime-mode argument handling.

### Out of Scope / Non-goals (MANDATORY)
- No installer/service packaging.
- No dynamic model downloads in supervisor.
- No quality/performance policy change by itself.

## 3) Current State (Brief)
- `whisper-dictation.py` owns tray + hotkeys + backend in one process.
- `transcription_backends.py` already supports python/whispercpp + fallback.
- Operator scripts exist for no-build benchmark and OpenVINO setup.

## 4) Requirements
### Functional Requirements
- FR1: Worker runtime must support explicit headless mode on Windows.
- FR2: Supervisor must manage worker lifecycle (start, stop, restart, switch profile).
- FR3: Supervisor tray must expose profile switching actions for backend/model presets.
- FR4: Supervisor must apply bounded crash autorestart for unexpected worker exits.

### Non-functional Requirements
- Reliability: intentional stop must not trigger autorestart.
- Compatibility: existing direct `whisper-dictation.py` launch remains valid.
- Operational: all worker launch commands and failures are logged.

### Constraints (Hard Rules)
- Supervisor and worker must be separate OS processes.
- Profile switch must not rebuild whisper.cpp artifacts.
- Rollback to direct runtime must require no code edits.

## 5) Acceptance Criteria (MANDATORY, Testable)
- [x] AC1: `whisper-dictation.py` accepts runtime mode and can run headless on Windows.
- [x] AC2: Supervisor can start/stop/restart worker and switch profile by controlled restart.
- [x] AC3: Unexpected worker exit triggers bounded autorestart attempts.
- [x] AC4: Unit tests cover command building and lifecycle guardrails.
- [x] AC5: Docs include short command path for running supervisor and direct worker fallback.

## 6) CLI Contract
- New worker arg: `--runtime-mode {auto,headless,tray}`.
- New supervisor entrypoint: `whisper-dictation-supervisor.py`.
- Supervisor launches worker with `--runtime-mode headless`.

## 7) Examples
### Example 1: Start supervisor with whisper.cpp defaults
- Input: `python whisper-dictation-supervisor.py --backend whispercpp --cpp-model large-v3`
- Output: tray appears, worker starts headless with selected profile.

### Example 2: Switch to Python medium from tray
- Input: tray menu action `Python medium`.
- Output: supervisor restarts worker with `--backend python -m medium`.

## 8) Integration Points & Dependencies
- `whisper-dictation.py` (worker runtime)
- `runtime_contracts.py` (runtime app selection)
- `pystray` + `Pillow` (Windows tray)
- `subprocess` process management

## 10) Error Handling & Edge Cases (MANDATORY)
- Missing worker executable/script path -> fail fast with clear message.
- Invalid profile model path -> reject switch, keep existing worker.
- Worker exits repeatedly -> bounded retries then stop autorestart.

## 11) Observability
- Supervisor log file records start/stop/switch/restart decisions.
- Worker command line is logged (without sensitive values).

## 13) Proposed Approach
1. Add runtime-mode override to worker.
2. Add supervisor core module (profiles + process manager).
3. Add tray entrypoint controlling supervisor core.
4. Add tests and docs; update Memory Bank state files.

## 14) Areas Likely Touched
- `whisper-dictation.py`
- `runtime_contracts.py`
- `README.md`
- `scripts/README.md`
- new: `supervisor_worker.py`
- new: `whisper-dictation-supervisor.py`
- new: `tests/test_supervisor_worker.py`

## 15) Test Plan (MANDATORY)
### Minimal verification (fast)
- `python -m py_compile whisper-dictation.py whisper-dictation-supervisor.py supervisor_worker.py`
- `pytest tests/test_whisper_dictation_args.py tests/test_supervisor_worker.py`

### Full verification (slower)
- `pytest tests/test_runtime_contracts.py tests/test_transcription_backends.py`

### New/updated tests needed
- Unit: supervisor command builder + lifecycle transitions.
- Unit: runtime-mode arg behavior.
- Manual: tray switch flow and restart behavior on Windows.

## 16) Rollout / Migration / Rollback
- Rollout: additive path, opt-in supervisor command.
- Rollback: run worker directly (`python whisper-dictation.py ...`).

## 17) Risks & Mitigations
- Rapid crash loops -> max restart limit with cooldown.
- Tray dependency issues -> explicit startup error with fallback instruction.
- Lock-file interaction -> controlled stop before restart.

## 19) Change Log (Keep short)
- 2026-02-09: Spec drafted.
- 2026-02-09: Implemented with tests, docs, and memory-bank updates.

## 20) Brittleness Analysis (MANDATORY before Status = Ready)
**BRITTLENESS ANALYSIS:**
- Over-specified elements:
  - none; profile names are configurable and not hard-coded into worker internals.
- Under-specified elements:
  - final menu breadth for advanced profiles (can expand later).
- Flexibility score: Medium
- Fixes applied:
  - made supervisor additive with explicit rollback to direct worker launch.
- Recommendation: Good balance for first production slice.
