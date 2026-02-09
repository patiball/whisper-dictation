# Issue: Shared Runtime Contract and Test Gate

**Status**: Draft  
**Priority**: High  
**Estimated Complexity**: Medium  
**Created**: 2026-02-09  
**Last Updated**: 2026-02-09  
**Parent Epic**: `[19-00-00]`

## 0) One-line Summary
Define shared runtime interfaces and add test gate so each next step is safe and reversible.

## 2) Scope
### In Scope
- Runtime contract for app controller (start/stop/toggle/run).
- Transcription backend contract.
- Baseline smoke/unit checks as precondition for subsequent issues.

### Out of Scope / Non-goals (MANDATORY)
- No backend optimization in this issue.
- No major behavior changes for end users.

## 5) Acceptance Criteria (MANDATORY, Testable)
- [ ] AC1: Contracts are documented and reflected in code-level abstractions.
- [ ] AC2: Contract tests exist and pass.
- [ ] AC3: Existing MVP flow works unchanged with default backend.
- [ ] AC4: Small rollback instructions are captured.

## 15) Test Plan (MANDATORY)
### Minimal verification (fast)
- `python -m py_compile whisper-dictation.py`
- targeted unit tests for contract behavior

### Full verification (slower)
- manual start/stop/tray smoke test on Windows

## 20) Brittleness Analysis (MANDATORY before Status = Ready)
**BRITTLENESS ANALYSIS:**
- Over-specified elements: none
- Under-specified elements: exact class/module placement (left flexible)
- Flexibility score: High
- Fixes applied: requirements defined by behavior, not file layout
- Recommendation: Good balance

