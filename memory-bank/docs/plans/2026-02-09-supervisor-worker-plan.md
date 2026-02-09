# Plan: [19-06-00] Supervisor + Worker Runtime for Model Switching

Date: 2026-02-09
Owner: Codex
Status: Planned

## Scope Summary
Implement Option D as a full Supervisor+Worker architecture on Windows:
- Supervisor owns tray UI and worker lifecycle.
- Worker runs dictation runtime in headless mode.
- Model/backend switching happens by controlled worker restart (no rebuild).
- Include crash autorestart guardrails and operator logging.

## Assumptions
- Existing `whisper-dictation.py` remains the worker entrypoint.
- OpenVINO whisper.cpp binaries/models are already provisioned externally.
- pystray/Pillow are available on Windows runtime environment.

## Phased Plan

### Phase 1: Contracts and Specs
- Write Memory Bank issue spec `[19-06-00]` with acceptance criteria and brittleness analysis.
- Write OpenSpec change proposal (`proposal.md`, `design.md`, `tasks.md`, delta spec).

Verification:
- Manual review: requirements are testable and include rollback path.

### Phase 2: Worker Runtime Mode Support
- Add explicit runtime-mode control (`auto` / `headless` / `tray`) to `whisper-dictation.py`.
- Ensure worker can run headless on Windows while retaining hotkey flow.

Verification:
- `python -m py_compile whisper-dictation.py runtime_contracts.py`
- `pytest tests/test_whisper_dictation_args.py tests/test_runtime_contracts.py`

### Phase 3: Supervisor Core
- Add a dedicated supervisor module with:
  - worker profile abstraction,
  - command builder,
  - start/stop/restart/switch operations,
  - bounded crash autorestart logic,
  - status snapshot for UI/logging.

Verification:
- `pytest tests/test_supervisor_worker.py`

### Phase 4: Supervisor Tray Entrypoint
- Add `whisper-dictation-supervisor.py` as tray process.
- Add model/backend menu actions that switch profile via controlled restart.

Verification:
- `python -m py_compile whisper-dictation-supervisor.py supervisor_worker.py`
- Manual smoke on Windows: start, stop, switch profile, exit.

### Phase 5: Docs and Memory Bank Reconcile
- Update README and scripts docs with supervisor command examples.
- Update Memory Bank active context/progress/spec index/backlog.

Verification:
- `pytest tests/test_whisper_dictation_args.py tests/test_supervisor_worker.py tests/test_runtime_contracts.py tests/test_transcription_backends.py`

## Risks and Mitigations
- Risk: orphaned worker process after supervisor crash.
  - Mitigation: stop-on-exit best effort + clear PID/status logs.
- Risk: invalid model path during profile switch.
  - Mitigation: preflight validation + explicit error logs, no silent fallback.
- Risk: restart loops on persistent worker failure.
  - Mitigation: bounded autorestart attempts and cooldown.

## Rollback
- Keep direct worker command path unchanged (`whisper-dictation.py ...`).
- Supervisor is additive and can be bypassed immediately.
