## Context
The runtime currently combines control plane and data plane into one process. For quick profile switching and stronger fault isolation, the control plane should move to a supervisor process while dictation remains in a worker process.

## Goals / Non-Goals
- Goals:
  - Separate control plane (tray + lifecycle) from dictation worker.
  - Allow profile switching by restart without rebuild.
  - Keep direct worker launch as rollback path.
- Non-Goals:
  - Windows service packaging.
  - Automatic model downloads/provisioning.
  - Backend quality policy changes.

## Decisions
- Decision: Keep `whisper-dictation.py` as worker entrypoint.
  - Why: minimizes migration risk and preserves existing tested flow.
- Decision: Add `--runtime-mode` to force headless worker mode.
  - Why: needed to run worker without a second tray icon on Windows.
- Decision: Implement bounded autorestart in supervisor.
  - Why: provides resilience without allowing infinite restart loops.

## Alternatives considered
- In-process model switching only:
  - Simpler, but keeps fault isolation weak and mixes control/data responsibilities.
- Separate shell wrapper without process manager logic:
  - Too brittle for crash handling and runtime visibility.

## Risks / Trade-offs
- Added complexity from a second process.
  - Mitigation: isolate logic in `supervisor_worker.py` and cover with unit tests.
- Potential lock-file interactions during rapid restart.
  - Mitigation: controlled stop-then-start sequencing and timeout handling.

## Migration Plan
1. Add runtime-mode support.
2. Add supervisor module and tray entrypoint.
3. Add docs and tests.
4. Use supervisor path as opt-in.

## Open Questions
- Should future version persist last selected profile across reboots? (deferred)
