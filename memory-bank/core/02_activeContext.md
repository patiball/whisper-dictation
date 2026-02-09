# Active Context

**Current Focus:** Epic 19 execution - Windows acceleration spike benchmark (`[19-02-00]`)

**Primary Epic:** `memory-bank/specs/[19-00-00]_cross_platform_unified_app_and_acceleration_strategy.md`

## What is actively in scope

1. Run baseline benchmark for Python backend on fixed WAV corpus.
2. Validate whisper.cpp presence and candidate backend modes on Windows.
3. Capture median and p95 latency for repeated runs.
4. Produce benchmark report with recommendation for next issue `[19-03-00]`.
5. Keep current UX unchanged while gathering acceleration evidence.
6. Execute Windows OpenVINO enablement plan for Intel Arc GPU:
   - install required Windows build toolchain
   - build whisper.cpp with OpenVINO backend enabled
   - generate OpenVINO encoder artifacts for selected model
   - validate GPU path and capture run command in project scripts

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

1. Add project script `scripts/setup_whisper_openvino_windows.ps1` (idempotent installer/build helper).
2. Install prerequisites (`cmake`, Visual C++ Build Tools if missing, Python deps for conversion).
3. Clone/update `whisper.cpp` source under local tooling directory.
4. Build Release with `WHISPER_OPENVINO=1`.
5. Generate OpenVINO model artifacts and run `whisper-cli` smoke test with `-oved GPU`.
6. Persist resolved binary/model paths for benchmark and next Epic 19 steps.
