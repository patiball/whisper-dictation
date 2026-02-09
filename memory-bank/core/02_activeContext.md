# Active Context

**Current Focus:** Epic 19 execution - Windows acceleration spike benchmark (`[19-02-00]`)

**Primary Epic:** `memory-bank/specs/[19-00-00]_cross_platform_unified_app_and_acceleration_strategy.md`

## What is actively in scope

1. Run cpp-only benchmark loops for OpenVINO GPU candidate without re-running full setup/build.
2. Validate quality and latency on English + Polish corpus with multilingual model path.
3. Capture median and p95 latency for repeated runs.
4. Produce benchmark report with recommendation for next issue `[19-03-00]`.
5. Keep current UX unchanged while gathering acceleration evidence.
6. Keep setup/build separate from benchmark execution:
   - setup script for install/build/conversion only
   - dedicated benchmark runner for no-build test reruns

## What is intentionally deferred

- full production rollout/default switch to accelerated backend
- deep packaging/distribution work for whisper.cpp on Windows
- broader backlog cleanups not impacting Windows MVP
- large test-architecture epics unless blocking MVP

## Working set

- Epic: `memory-bank/specs/[19-00-00]_cross_platform_unified_app_and_acceleration_strategy.md`
- Issues:
  - `memory-bank/specs/[19-01-00]_shared_runtime_contract_and_test_gate.md` (implemented)
  - `memory-bank/specs/[19-02-00]_windows_acceleration_spike_whispercpp_backends.md`
  - `memory-bank/specs/[19-03-00]_pluggable_transcription_backend_integration.md`
  - `memory-bank/specs/[19-04-00]_safe_fallback_and_incremental_release_controls.md`
  - `memory-bank/specs/[19-05-00]_benchmark_gate_and_windows_runbook_for_acceleration.md`
- Previous Epic (stabilization): `memory-bank/specs/[18-00-00]_windows11_minimal_runtime.md`
- Backlog: `memory-bank/issues-backlog.md`
- Tech context: `memory-bank/core/05_techContext.md`

## Immediate Execution Plan (2026-02-09)

1. Ensure benchmark uses multilingual model (`ggml-base.bin`) for PL/EN corpus quality checks.
2. Run `scripts/run_whispercpp_openvino_benchmark.ps1` for cpp-only measurements.
3. Compare repeated benchmark reports and confirm stable median/p95.
4. Finalize `[19-02-00]` recommendation with explicit quality caveats and next actions.
