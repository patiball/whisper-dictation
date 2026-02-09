Last Update: 2026-02-09

## Current Status

- Windows 11 MVP epic added as spec: `[18-00-00]`.
- Memory Bank cleaned to reduce non-active noise.
- Legacy analysis and stale backlog moved to archive.
- Windows MVP implementation manually verified on Windows 11.
- New follow-up epic `[19-00-00]` created for cross-platform unified architecture and acceleration strategy.
- Issue `[19-01-00]` implemented (shared runtime/transcription contracts + contract tests).
- Pytest environment on Windows stabilized for local execution (`pytest`, `pytest-cov`, `pytest-rerunfailures`, `pytest-timeout`, `librosa` installed in `.venv`).
- Issue `[19-02-00]` started with benchmark harness scaffold in `scripts/windows_acceleration_benchmark.py`.
- Smoke benchmark executed successfully with Python baseline; report files generated under `memory-bank/docs/benchmarks/`.
- Constraint identified for acceleration measurement: `whisper-cli` binary/model not yet configured in current environment.
- OpenVINO-enabled `whisper.cpp` build completed on Windows (VS Build Tools + CMake).
- OpenVINO encoder artifacts generated for `ggml-base.en` and validated with `-oved GPU`.
- Reproducible setup script added: `scripts/setup_whisper_openvino_windows.ps1`.
- `WHISPER_CLI_BIN` now points to stable OpenVINO build location:
  `C:\Users\mprzybyszewski1\AppData\Local\whispercpp\openvino\bin\whisper-cli.exe`.
- Benchmark harness extended with `--skip-python` for cpp-only reruns.
- Added no-build benchmark runner: `scripts/run_whispercpp_openvino_benchmark.ps1`.
- Setup script default model changed to multilingual `base` (instead of `base.en`) to match PL/EN usage.
- Added warning in setup script when English-only model (`*.en`) is selected.

## Completed in this update

1. Added platform-specific runtime selection so Windows path no longer depends on `rumps`.
2. Implemented Windows tray runtime with `Start Recording`, `Stop Recording`, and `Exit`.
3. Added Windows start/stop sound cues via built-in `winsound` (non-blocking).
4. Added clearer model-load messaging for first-run auto-download behavior.
5. Updated Windows MVP documentation in `README.md`.
6. Updated dependency markers for platform-specific libraries.
7. Added Epic `[19-00-00]` and issues `[19-01-00]`..`[19-05-00]` for test-gated acceleration rollout.
8. Added shared runtime/backend contracts and factory wiring for issue `[19-01-00]`.
9. Added contract tests (`tests/test_runtime_contracts.py`) and verified passing locally.
10. Added benchmark harness for `[19-02-00]` with JSON+Markdown report output.
11. Added cpp-only execution path and runner script to avoid rebuild loop between benchmark runs.
12. Added unit tests for benchmark candidate parsing and `--skip-python` behavior.

## Next Execution Step

Execute issue `[19-02-00]` with multilingual model (`ggml-base.bin`): run cpp-only benchmark harness on Windows hardware, capture median/p95 + quality, and finalize backend recommendation for `[19-03-00]`.
