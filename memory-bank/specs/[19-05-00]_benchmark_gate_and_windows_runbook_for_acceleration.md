# Issue: Benchmark Gate and Windows Runbook for Acceleration

**Status**: Implemented  
**Priority**: Medium  
**Estimated Complexity**: Medium  
**Created**: 2026-02-09  
**Last Updated**: 2026-02-09  
**Parent Epic**: `[19-00-00]`

## 0) One-line Summary
Define benchmark acceptance gate and operational runbook for accelerated backend on Windows.

## 2) Scope
### In Scope
- Benchmark procedure and pass/fail thresholds.
- Updated Windows runbook for backend setup and diagnostics.
- Post-implementation verification checklist.

### Out of Scope / Non-goals (MANDATORY)
- No new runtime features.
- No backend code changes beyond measurement hooks.

## 5) Acceptance Criteria (MANDATORY, Testable)
- [x] AC1: Benchmark checklist includes baseline vs accelerated backend comparison.
- [x] AC2: README/runbook documents setup, fallback, and troubleshooting.
- [x] AC3: Deployment decision criteria are explicit.

## 16) Implementation Notes
- Added benchmark gate script:
  - `scripts/benchmark_gate_check.py`
- Gate validates:
  - candidate/python median ratio (`--max-median-ratio`, default `0.35`)
  - candidate quality p10 (`--min-quality-p10`, default `0.60`)
  - candidate low-quality sample count (`--max-below-threshold-count`, default `1`)
  - candidate failure count (`failure_count == 0`)
- Added tests:
  - `tests/test_benchmark_gate_check.py`
- Added Windows acceleration runbook:
  - `docs/windows_acceleration_runbook.md`
- Updated operator documentation:
  - `README.md` (backend launch + benchmark gate usage)
  - `scripts/README.md` (gate script usage)

## 15) Test Plan (MANDATORY)
### Minimal verification (fast)
- run benchmark script/checklist on one reference sample

### Full verification (slower)
- run benchmark set on multiple samples and summarize median/p95

## 20) Brittleness Analysis (MANDATORY before Status = Ready)
**BRITTLENESS ANALYSIS:**
- Over-specified elements: no hardcoding to one hardware SKU
- Under-specified elements: exact threshold values pending spike results
- Flexibility score: Medium
- Fixes applied: thresholds deferred but benchmark structure fixed
- Recommendation: Add detail after issue `[19-02-00]`
