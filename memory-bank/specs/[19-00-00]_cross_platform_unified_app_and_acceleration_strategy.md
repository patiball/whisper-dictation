# Epic: Cross-Platform Unified App and Acceleration Strategy

**Status**: Draft  
**Priority**: High  
**Estimated Complexity**: Complex  
**Created**: 2026-02-09  
**Last Updated**: 2026-02-09

---

## 0) One-line Summary
Deliver one unified app architecture for macOS and Windows with pluggable transcription backends and Windows acceleration path.

## 1) Overview (What & Why)
### Problem
- Current implementation is usable on Windows but still tightly coupled to platform-specific pieces.
- Python Whisper path on Windows is too slow for target workflow.
- Building separate apps for macOS/Windows would increase maintenance risk.

### Goal
- Keep one product and one shared runtime flow.
- Isolate platform differences behind thin adapters.
- Add accelerated backend path for Windows without destabilizing current MVP.

### Success Metrics
- Same start/stop/tray/hotkey UX contract on macOS and Windows.
- Windows transcription median latency reduced versus current Python medium baseline.
- Each increment releasable with a rollback path.

---

## 2) Scope
### In Scope
- Shared core runtime contract for both OSes.
- Backend abstraction (`python-whisper`, `whisper.cpp`) with feature flag and fallback.
- Hardware-aware backend selection on Windows.
- Test-first incremental delivery model.

### Out of Scope / Non-goals (MANDATORY)
- Full installer/distribution system.
- Full parity of every macOS-only UX detail on Windows.
- CPU micro-optimization of current Python backend as primary strategy.

---

## 4) Requirements
### Functional Requirements
- FR1: Introduce shared app contracts for runtime state and transcription backend.
- FR2: Implement backend selection and fallback without changing user-facing flow.
- FR3: Keep stable CLI semantics while adding backend choice controls.

### Non-functional Requirements
- Performance: measurable latency improvements on Windows via accelerated backend path.
- Reliability: safe fallback to stable backend on backend failures.
- Compatibility: no intentional regression to existing macOS runtime.

### Constraints (Hard Rules)
- Must be implemented in small increments with green checks between steps.
- Must keep a reversible path (feature flag / fallback) at all times.
- Must define verification commands before each implementation step.

---

## 5) Acceptance Criteria (MANDATORY, Testable)
- [ ] AC1: New epic issues are defined with small-scope, testable checkpoints.
- [ ] AC2: Each issue contains minimal fast verification and rollback notes.
- [ ] AC3: Shared core + adapter pattern is documented and implementable by another agent.
- [ ] AC4: Windows acceleration strategy is benchmark-driven, not assumption-driven.

---

## 13) Proposed Approach (Constraints > Implementation Details)
- Phase A: Define contracts and tests first.
- Phase B: Add backend abstraction under existing flow.
- Phase C: Integrate Windows accelerated backend (`whisper.cpp`) behind feature flag.
- Phase D: Benchmark, tune, and set default policy with safe fallback.

---

## 15) Test Plan (MANDATORY)
### Minimal verification (fast)
- Command(s): `python -m py_compile whisper-dictation.py`
- Expected outcome: No syntax regressions while introducing abstractions.

### Full verification (slower)
- Manual smoke on Windows/macOS:
  - start/stop via hotkey
  - tray/menu controls
  - transcription + typing output
  - fallback behavior on backend failure

### New/updated tests needed
- Unit: backend contract tests, selector tests, fallback tests.
- Integration: end-to-end recording-to-transcription flow with mocked backend.
- E2E: manual hardware benchmark checklist on Windows.

---

## 17) Risks & Mitigations
- Risk: Over-refactor before value delivery -> Mitigation: vertical slices and commit-per-slice.
- Risk: Backend quality/perf tradeoffs -> Mitigation: benchmark gate before default switch.
- Risk: Platform regressions -> Mitigation: adapter boundaries + smoke matrix per OS.

---

## 19) Change Log (Keep short)
- 2026-02-09: Draft created.

---

## 20) Brittleness Analysis (MANDATORY before Status = Ready)
**BRITTLENESS ANALYSIS:**
- Over-specified elements:
  - none; avoids hardcoding exact file names for final architecture.
- Under-specified elements:
  - exact benchmark thresholds to be finalized during spike.
- Flexibility score: Medium
- Fixes applied:
  - enforced incremental/test-gated approach and fallback requirement.
- Recommendation: Add detail (quantitative performance thresholds) after spike.

