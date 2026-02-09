# Active Context

**Current Focus:** Windows 11 MVP stabilization + next epic planning (cross-platform acceleration)

**Primary Epic:** `memory-bank/specs/[19-00-00]_cross_platform_unified_app_and_acceleration_strategy.md`

## What is actively in scope

1. Manually verify Windows tray behavior (`Start/Stop/Exit`) on target machine.
2. Manually verify global hotkey stability (`ctrl+alt` default).
3. Manually verify start/stop sound cues on Windows audio stack.
4. Confirm first-run `-m medium` download and second-run cache reuse.
5. Prepare test-gated incremental implementation plan from epic `[19-00-00]`.

## What is intentionally deferred

- full `whisper.cpp` Windows optimization and packaging
- performance optimization of Python transcription path on Windows (current latency around ~8-10s with `medium`)
- broader backlog cleanups not impacting Windows MVP
- large test-architecture epics unless blocking MVP

## Working set

- Epic: `memory-bank/specs/[19-00-00]_cross_platform_unified_app_and_acceleration_strategy.md`
- Issues:
  - `memory-bank/specs/[19-01-00]_shared_runtime_contract_and_test_gate.md`
  - `memory-bank/specs/[19-02-00]_windows_acceleration_spike_whispercpp_backends.md`
  - `memory-bank/specs/[19-03-00]_pluggable_transcription_backend_integration.md`
  - `memory-bank/specs/[19-04-00]_safe_fallback_and_incremental_release_controls.md`
  - `memory-bank/specs/[19-05-00]_benchmark_gate_and_windows_runbook_for_acceleration.md`
- Previous Epic (stabilization): `memory-bank/specs/[18-00-00]_windows11_minimal_runtime.md`
- Backlog: `memory-bank/issues-backlog.md`
- Tech context: `memory-bank/core/05_techContext.md`
