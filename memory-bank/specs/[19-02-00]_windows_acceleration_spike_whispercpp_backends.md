# Issue: Windows Acceleration Spike (whisper.cpp Backends)

**Status**: Implemented  
**Priority**: High  
**Estimated Complexity**: Medium  
**Created**: 2026-02-09  
**Last Updated**: 2026-02-09  
**Parent Epic**: `[19-00-00]`

## 0) One-line Summary
Run hardware-aware spike for whisper.cpp acceleration options on Windows and choose primary path.

## 2) Scope
### In Scope
- Validate `whisper.cpp` availability on target environment.
- Compare candidate acceleration paths (e.g., Vulkan/OpenVINO if available).
- Benchmark against current Python backend baseline.

### Out of Scope / Non-goals (MANDATORY)
- No default backend switch in this issue.
- No final production rollout decision in this issue.

## 5) Acceptance Criteria (MANDATORY, Testable)
- [x] AC1: Benchmark report created (latency + qualitative output).
- [x] AC2: Clear recommended backend strategy for this hardware profile.
- [x] AC3: Known setup constraints are documented.

## 15) Test Plan (MANDATORY)
### Minimal verification (fast)
- backend presence checks (`whisper-cli --help` or equivalent)
- one short-file transcription benchmark

### Full verification (slower)
- repeated runs for median and p95 latency
- manual quality spot-check

## 16) Implementation Notes
- Benchmark harness added: `scripts/windows_acceleration_benchmark.py`
- Default corpus path: `tests/audio/test_*.wav`
- Report output path: `memory-bank/docs/benchmarks/`
- Report formats: JSON + Markdown (includes recommendation stub)
- First smoke benchmark generated:
  - `memory-bank/docs/benchmarks/windows_acceleration_benchmark_20260209_145330.json`
  - `memory-bank/docs/benchmarks/windows_acceleration_benchmark_20260209_145330.md`
- OpenVINO setup completed for Windows:
  - built `whisper.cpp` with `WHISPER_OPENVINO=1`
  - generated `ggml-base.en-encoder-openvino.xml/.bin`
  - validated runtime with `-oved GPU` and `OPENVINO = 1` in logs
- Reproducible setup script added: `scripts/setup_whisper_openvino_windows.ps1`
- Setup default now uses multilingual model (`base`) to avoid PL quality regression from `base.en`.
- Benchmark harness now supports cpp-only execution (`--skip-python`).
- Dedicated no-build runner added: `scripts/run_whispercpp_openvino_benchmark.ps1`.
- Additional benchmark artifacts captured:
  - `memory-bank/docs/benchmarks/windows_acceleration_benchmark_20260209_182542.json/.md`
  - `memory-bank/docs/benchmarks/windows_acceleration_benchmark_20260209_182952.json/.md`
  - `memory-bank/docs/benchmarks/windows_acceleration_benchmark_20260209_184015.json/.md`
- Constraint observed: using `ggml-base.en.bin` with PL/EN corpus produces strong latency but quality below threshold.

## 17) Benchmark Run Command (Current)
- Baseline + optional whisper.cpp candidates:
  - `.\.venv\Scripts\python.exe scripts/windows_acceleration_benchmark.py --python-model medium --runs 3`
- Example with explicit whisper.cpp candidate and model:
  - `.\.venv\Scripts\python.exe scripts/windows_acceleration_benchmark.py --python-model medium --runs 3 --whispercpp-cli whisper-cli --whispercpp-model "<PATH_TO_GGML_MODEL_BIN>" --whispercpp-candidate "default=-l en -otxt"`
- cpp-only rerun (no Python baseline):
  - `.\.venv\Scripts\python.exe scripts/windows_acceleration_benchmark.py --skip-python --runs 3 --whispercpp-cli "$env:WHISPER_CLI_BIN" --whispercpp-model "$env:WHISPER_CLI_MODEL" --whispercpp-candidate "whispercpp-openvino-gpu=-otxt -l auto -oved GPU"`
- convenience runner (no build):
  - `powershell -ExecutionPolicy Bypass -File scripts/run_whispercpp_openvino_benchmark.ps1 -Runs 3`

## 20) Brittleness Analysis (MANDATORY before Status = Ready)
**BRITTLENESS ANALYSIS:**
- Over-specified elements: none (no hard lock to a single backend before data)
- Under-specified elements: exact benchmark dataset paths
- Flexibility score: Medium
- Fixes applied: benchmark-driven decision explicitly required
- Recommendation: Add detail (fixed benchmark corpus) before Ready
