# Active Context

**Current Focus:** Windows 11 MVP verification and stabilization

**Primary Epic:** `memory-bank/specs/[18-00-00]_windows11_minimal_runtime.md`

## What is actively in scope

1. Manually verify Windows tray behavior (`Start/Stop/Exit`) on target machine.
2. Manually verify global hotkey stability (`ctrl+alt` default).
3. Manually verify start/stop sound cues on Windows audio stack.
4. Confirm first-run `-m medium` download and second-run cache reuse.
5. Apply any small fixes discovered during manual verification.

## What is intentionally deferred

- full `whisper.cpp` Windows optimization and packaging
- performance optimization of Python transcription path on Windows (current latency around ~8-10s with `medium`)
- broader backlog cleanups not impacting Windows MVP
- large test-architecture epics unless blocking MVP

## Working set

- Spec: `memory-bank/specs/[18-00-00]_windows11_minimal_runtime.md`
- Stories:
  - `memory-bank/specs/[18-01-00]_windows_runtime_bootstrap_without_macos_ui_dependency.md`
  - `memory-bank/specs/[18-02-00]_windows_tray_icon_and_basic_controls.md`
  - `memory-bank/specs/[18-03-00]_windows_start_stop_sound_cues.md`
  - `memory-bank/specs/[18-04-00]_first_run_medium_model_bootstrap_and_windows_runbook.md`
- Backlog: `memory-bank/issues-backlog.md`
- Tech context: `memory-bank/core/05_techContext.md`
