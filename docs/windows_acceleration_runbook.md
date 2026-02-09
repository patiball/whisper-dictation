# Windows Acceleration Runbook

This runbook defines a repeatable workflow for validating and operating the
`whispercpp-openvino-gpu` backend on Windows.

## 1) Prerequisites

- `WHISPER_CLI_BIN` points to a working `whisper-cli.exe`
- `WHISPER_CLI_MODEL` points to multilingual model, recommended:
  `%LOCALAPPDATA%\whispercpp\models\ggml-base.bin`
- OpenVINO encoder artifacts for the selected model exist:
  - `ggml-base-encoder-openvino.xml`
  - `ggml-base-encoder-openvino.bin`

## 2) Benchmark Procedure (Baseline vs Accelerated)

Run benchmark with both backends:

```powershell
.\.venv\Scripts\python.exe scripts/windows_acceleration_benchmark.py `
  --python-model medium `
  --runs 3 `
  --audio-pattern "test_*.wav" `
  --quality-files "test_english*.wav" `
  --quality-files "test_polish_10s*.wav" `
  --quality-files "test_polish_5s*.wav" `
  --whispercpp-cli "$env:WHISPER_CLI_BIN" `
  --whispercpp-model "$env:LOCALAPPDATA\whispercpp\models\ggml-base.bin" `
  --whispercpp-candidate "whispercpp-openvino-gpu=-otxt -l auto -oved GPU"
```

## 3) Gate Criteria (Go / No-Go)

Evaluate report using gate checker:

```powershell
.\.venv\Scripts\python.exe scripts/benchmark_gate_check.py `
  --report "<PATH_TO_REPORT_JSON>" `
  --candidate-backend whispercpp-openvino-gpu `
  --max-median-ratio 0.35 `
  --min-quality-p10 0.60 `
  --max-below-threshold-count 1
```

Pass requires all:

- accelerated/backend median ratio <= `0.35`
- candidate quality `p10 >= 0.60`
- candidate `below_0_6_count <= 1`
- candidate `failure_count == 0`

## 4) Runtime Launch

Primary accelerated mode:

```powershell
.\.venv\Scripts\python.exe .\whisper-dictation.py `
  --backend whispercpp `
  --whispercpp-cli "$env:WHISPER_CLI_BIN" `
  --whispercpp-model "$env:LOCALAPPDATA\whispercpp\models\ggml-base.bin" `
  --whispercpp-args "-otxt -l auto -oved GPU" `
  --fallback-backend python `
  -k "ctrl_l+alt_l"
```

Rollback without code changes:

```powershell
.\.venv\Scripts\python.exe .\whisper-dictation.py --backend python -k "ctrl_l+alt_l"
```

Or keep backend selection but disable fallback:

```powershell
.\.venv\Scripts\python.exe .\whisper-dictation.py `
  --backend whispercpp `
  --disable-backend-fallback
```

## 5) Troubleshooting

- If `whispercpp` startup fails, app should log fallback activation and continue on `python`.
- If runtime transcription fails on `whispercpp`, app should log runtime fallback reason and continue on `python`.
- If fallback is disabled, failures are expected to abort transcribe path.
