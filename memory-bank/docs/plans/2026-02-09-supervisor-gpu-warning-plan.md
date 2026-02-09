# Plan: [19-07-00] Supervisor GPU Warning + Model Confirmation

Date: 2026-02-09
Owner: Codex
Status: Planned

## Scope Summary
Address ambiguity during whisper.cpp profile switching by surfacing whether the selected model is actually used and whether acceleration degraded to CPU/fallback.

## Verified Root Cause
- Supervisor correctly switched to `cpp-medium` command.
- `ggml-medium-encoder-openvino.xml/.bin` were missing.
- Whisper CLI failed OpenVINO encoder init and ran much slower.

## Phases

### Phase 1: Specs + contract updates
- Add issue spec `[19-07-00]` with explicit acceptance criteria.
- Add OpenSpec change proposal + tasks + delta requirement.

### Phase 2: Worker diagnostics emission
- Parse whisper.cpp stdout/stderr for:
  - loaded model path,
  - OpenVINO load success/failure.
- Print structured status line for supervisor consumption.
- Add human-readable confirmation print after each transcription.

### Phase 3: Supervisor warning/status UX
- Add preflight warning for missing OpenVINO encoder artifacts when `-oved GPU` is requested.
- Parse structured worker status lines from worker log and expose in supervisor status snapshot.
- Show warning/acceleration state in tray status text.

### Phase 4: Tests + docs + memory bank
- Add tests for diagnostics parsing and supervisor warnings.
- Update runbook/docs and memory bank context/progress/index.

## Verification
- `python -m py_compile transcription_backends.py supervisor_worker.py whisper-dictation-supervisor.py`
- `pytest tests/test_transcription_backends.py tests/test_supervisor_worker.py tests/test_whisper_dictation_args.py tests/test_runtime_contracts.py`

## Risks / Mitigation
- Log parsing brittleness due upstream whisper.cpp output changes.
  - Mitigation: use conservative regex + fallback to `unknown` state.
- False warning risk if custom backends are used.
  - Mitigation: preflight warning only when OpenVINO GPU flag is explicitly requested.
