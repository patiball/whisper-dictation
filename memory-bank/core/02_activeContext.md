# Active Context

**Current Focus:** Epic 19 execution - post-19-07 quality/performance validation

**Primary Epic:** `memory-bank/specs/[19-00-00]_cross_platform_unified_app_and_acceleration_strategy.md`

## What is actively in scope

1. Validate quality impact of larger whisper.cpp models (PL/EN, auto-detect) using benchmark gate workflow.
2. Use new Supervisor+Worker runtime for operational profile switching without rebuild.
3. Use supervisor warning/telemetry to detect CPU fallback quickly during model switches.
4. Decide default backend/model policy based on combined latency + quality evidence.
5. Close remaining automation gap for OpenVINO encoder artifact provisioning.

## What is intentionally deferred

- full production rollout/default switch to accelerated backend
- deep packaging/distribution work for whisper.cpp on Windows
- broader backlog cleanups not impacting Windows MVP
- large test-architecture epics unless blocking MVP

## Working set

- Epic: `memory-bank/specs/[19-00-00]_cross_platform_unified_app_and_acceleration_strategy.md`
- Issues:
  - `memory-bank/specs/[19-01-00]_shared_runtime_contract_and_test_gate.md` (implemented)
  - `memory-bank/specs/[19-02-00]_windows_acceleration_spike_whispercpp_backends.md` (implemented)
  - `memory-bank/specs/[19-03-00]_pluggable_transcription_backend_integration.md` (implemented)
  - `memory-bank/specs/[19-04-00]_safe_fallback_and_incremental_release_controls.md` (implemented)
  - `memory-bank/specs/[19-05-00]_benchmark_gate_and_windows_runbook_for_acceleration.md` (implemented)
  - `memory-bank/specs/[19-06-00]_supervisor_worker_runtime_for_model_switching.md` (implemented)
  - `memory-bank/specs/[19-07-00]_supervisor_gpu_warning_and_model_confirmation.md` (implemented)
- Previous Epic (stabilization): `memory-bank/specs/[18-00-00]_windows11_minimal_runtime.md`
- Backlog: `memory-bank/issues-backlog.md`
- Tech context: `memory-bank/core/05_techContext.md`

## Immediate Execution Plan (2026-02-09)

1. Run A/B benchmark for `small` and `medium` whisper.cpp models against python baseline on PL/EN quality set.
2. Keep using `scripts/run_supervisor.ps1` for rapid model switching during manual checks.
3. Implement auto-provision/self-heal path for missing OpenVINO encoder artifacts (manual provisioning now verified).
4. Update rollout recommendation and benchmark gate thresholds only if evidence requires it.
