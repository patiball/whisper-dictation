## Context
Profile switching already works, but runtime health is opaque. Missing OpenVINO artifacts can silently degrade performance, which appears as "model switch did not apply" to users.

## Goals / Non-Goals
- Goals:
  - Clearly report model used per transcription.
  - Clearly flag CPU fallback risk in supervisor.
- Non-Goals:
  - Automatic OpenVINO artifact generation in this change.
  - New benchmark policies.

## Decisions
- Decision: parse whispercpp output and emit a structured one-line status event.
  - Why: low-complexity integration point between worker and supervisor.
- Decision: add preflight artifact checks in supervisor for OpenVINO mode.
  - Why: catches the most common slow-path cause before transcription begins.

## Risks / Trade-offs
- Output parsing depends on current whisper.cpp messages.
  - Mitigation: keep parser tolerant and default to `unknown`.

## Migration Plan
1. Add backend status parser + event output.
2. Add supervisor preflight + status ingestion.
3. Add tests and docs.
