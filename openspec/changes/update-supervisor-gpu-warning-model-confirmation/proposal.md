# Change: Update Supervisor UX with GPU Warning and Model Confirmation

## Why
Users need immediate visibility when whisper.cpp runs slower due CPU/fallback behavior and confidence that selected profile/model was actually used.

## What Changes
- Add runtime diagnostics in whispercpp backend for model-used and acceleration state.
- Emit structured status lines from worker logs.
- Add supervisor preflight warning for missing OpenVINO encoder artifacts.
- Surface acceleration/warning state in supervisor status output.

## Impact
- Affected specs: `runtime-supervision`
- Affected code:
  - `transcription_backends.py`
  - `supervisor_worker.py`
  - `whisper-dictation-supervisor.py`
  - tests for backend and supervisor
