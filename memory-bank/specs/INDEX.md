# Specs Index

Last Updated: 2026-02-09 (19-02..19-07 implemented, quality follow-up pending)

## Active

- `[19-00-00]` Cross-Platform Unified App and Acceleration Strategy  
  File: `memory-bank/specs/[19-00-00]_cross_platform_unified_app_and_acceleration_strategy.md`  
  Status: Draft
- `[19-01-00]` Shared Runtime Contract and Test Gate  
  File: `memory-bank/specs/[19-01-00]_shared_runtime_contract_and_test_gate.md`  
  Status: Implemented
- `[19-02-00]` Windows Acceleration Spike (whisper.cpp Backends)  
  File: `memory-bank/specs/[19-02-00]_windows_acceleration_spike_whispercpp_backends.md`  
  Status: Implemented
- `[19-03-00]` Pluggable Transcription Backend Integration  
  File: `memory-bank/specs/[19-03-00]_pluggable_transcription_backend_integration.md`  
  Status: Implemented
- `[19-04-00]` Safe Fallback and Incremental Release Controls  
  File: `memory-bank/specs/[19-04-00]_safe_fallback_and_incremental_release_controls.md`  
  Status: Implemented
- `[19-05-00]` Benchmark Gate and Windows Runbook for Acceleration  
  File: `memory-bank/specs/[19-05-00]_benchmark_gate_and_windows_runbook_for_acceleration.md`  
  Status: Implemented
- `[19-06-00]` Supervisor + Worker Runtime for Fast Model/Backend Switching  
  File: `memory-bank/specs/[19-06-00]_supervisor_worker_runtime_for_model_switching.md`  
  Status: Implemented
- `[19-07-00]` Supervisor GPU Warning + whisper.cpp Model Confirmation  
  File: `memory-bank/specs/[19-07-00]_supervisor_gpu_warning_and_model_confirmation.md`  
  Status: Implemented
- `[18-00-00]` Windows 11 Minimal Runtime (Hotkey + Tray + Sound Cues + Auto Model Download)  
  File: `memory-bank/specs/[18-00-00]_windows11_minimal_runtime.md`  
  Status: Implemented (verified on Windows)
- `[18-01-00]` Windows Runtime Bootstrap Without macOS UI Dependency  
  File: `memory-bank/specs/[18-01-00]_windows_runtime_bootstrap_without_macos_ui_dependency.md`  
  Status: Implemented (verified on Windows)
- `[18-02-00]` Windows Tray Icon and Basic Controls  
  File: `memory-bank/specs/[18-02-00]_windows_tray_icon_and_basic_controls.md`  
  Status: Implemented (verified on Windows)
- `[18-03-00]` Windows Start/Stop Sound Cues  
  File: `memory-bank/specs/[18-03-00]_windows_start_stop_sound_cues.md`  
  Status: Implemented (verified on Windows)
- `[18-04-00]` First-Run Medium Model Bootstrap and Windows Runbook  
  File: `memory-bank/specs/[18-04-00]_first_run_medium_model_bootstrap_and_windows_runbook.md`  
  Status: Implemented (verified on Windows)

## Legacy / Historical

- `[01-00-00]` through `[17-04-00]` are historical epics/stories/tasks from previous phases.
- Keep for reference unless they directly block current Windows 11 MVP.

## Notes

- Current execution focus is quality follow-up after acceleration rollout safeguards.
- Benchmark workflow now supports no-build cpp-only reruns via
  `scripts/run_whispercpp_openvino_benchmark.ps1` and
  `scripts/windows_acceleration_benchmark.py --skip-python`.
- Supervisor+Worker runtime is available via `whisper-dictation-supervisor.py`
  and `scripts/run_supervisor.ps1` for faster profile switching without rebuild.
- Supervisor now surfaces CPU fallback risk and worker-reported model/acceleration
  state for easier debugging of slow whisper.cpp runs.
- Supervisor defaults now start whisper.cpp on `medium` for better startup ergonomics.
- Detailed historical analysis artifacts were moved to:
  `memory-bank/archive/2026-02-09-windows11-focus/`
