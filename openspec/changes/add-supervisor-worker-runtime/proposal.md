# Change: Add Supervisor + Worker Runtime Architecture

## Why
Users need fast model/backend switching without long command lines and without rebuilding whisper.cpp artifacts. The current single-process runtime also makes failure recovery less controlled.

## What Changes
- Add a dedicated supervisor process that manages a headless worker process.
- Add explicit worker runtime mode selection (`auto`, `headless`, `tray`).
- Add supervisor tray controls for worker start/stop/restart and profile switching.
- Add bounded worker crash autorestart behavior.
- Add tests for supervisor command/lifecycle behavior.

## Impact
- Affected specs: `runtime-supervision` (new capability)
- Affected code:
  - `whisper-dictation.py`
  - `runtime_contracts.py`
  - `README.md`
  - `scripts/README.md`
  - `supervisor_worker.py` (new)
  - `whisper-dictation-supervisor.py` (new)
  - `tests/test_supervisor_worker.py` (new)
