# Issues & Backlog (Active)

Last Updated: 2026-02-09
Focus: Windows 11 MVP stabilization + Epic [19] planning

## High Priority

### 1. Windows runtime without macOS-only UI dependency
- Status: Implemented (pending manual verification)
- Why: Current code imports macOS UI path (`rumps`) in main flow.
- Done when: App starts on Windows 11 without requiring macOS status bar framework.

### 2. Tray icon for MVP visibility and control
- Status: Implemented (pending manual verification)
- Why: User wants minimal app presence and control in tray.
- Done when: Running app exposes tray icon with at least start/stop and exit actions.

### 3. Windows start/stop sound cues
- Status: Implemented (pending manual verification)
- Why: Recording state must be obvious to user.
- Done when: Start and stop recording both emit audible cues on Windows.

### 4. First-run model bootstrap (`medium`)
- Status: Implemented (pending manual verification)
- Why: User should not perform manual model setup.
- Done when: Running with `-m medium` downloads missing model and continues automatically.

## Medium Priority

### 5. Windows runbook sanity in README
- Status: Implemented (pending manual verification)
- Why: Current instructions are macOS-heavy.
- Done when: README includes a verified Windows 11 section for MVP path.

## New High Priority (Planned Epic [19])

### 6. Shared runtime contract + test gate
- Status: Implemented
- Why: Need safe, incremental delivery without five-hour breakage loops.
- Done when: Contract tests and minimal verification gate exist before deeper changes.

### 7. Windows acceleration spike (`whisper.cpp` backend options)
- Status: Implemented
- Why: Current Python path on Windows is too slow.
- Done when: Benchmark-backed recommendation selects acceleration path.

### 8. Pluggable backend integration (`python` + `whisper.cpp`)
- Status: Implemented
- Why: One app should support multiple engines without UX split.
- Done when: `--backend` path works end-to-end with current hotkey/tray flow.

### 9. Safe fallback and rollout controls
- Status: Implemented
- Why: New backend must not break dictation workflow.
- Done when: Automatic fallback and clear diagnostics are verified.

### 10. Benchmark gate + Windows acceleration runbook
- Status: Implemented
- Why: Need objective go/no-go and repeatable deployment checklist.
- Done when: Baseline vs accelerated metrics and operator docs are complete.

### 11. Supervisor + Worker architecture for fast model/backend switching
- Status: Implemented
- Why: Long manual restart commands slowed iteration and mixed control plane with runtime process.
- Done when: Dedicated tray supervisor manages headless worker with start/stop/restart/profile-switch and bounded crash autorestart.

### 12. Supervisor warning + model confirmation for whispercpp runtime
- Status: Implemented
- Why: Without explicit acceleration/model telemetry, CPU fallback looked like profile-switch failure.
- Done when: supervisor surfaces CPU fallback warnings and worker emits model+acceleration confirmation lines.

## Not Active Now

- Full `whisper.cpp` Windows support
- Full macOS/Windows UI parity
- Historical test-infra epics unless they block Windows MVP

## Quick Todos

### Q1. Evaluate larger whisper.cpp model for quality recovery
- Status: In Progress
- Why: `whispercpp` is much faster but manual E2E shows lower transcription quality versus python backend.
- Done when: A/B benchmark and manual spot-check are completed for a larger multilingual model (e.g. `small`), with updated recommendation for default backend policy.
  Prereq update: `ggml-small.bin` plus OpenVINO encoder artifacts for `base`/`medium`/`small` are now provisioned locally.

### Q2. Auto-provision OpenVINO encoder artifacts for selected whisper.cpp model
- Status: Planned
- Why: Switching `WHISPER_CLI_MODEL` to a new model (e.g. `large-v3`) currently requires manual conversion/copy of `*-encoder-openvino.xml/.bin`; missing artifacts can silently degrade runtime performance.
- Done when: runtime/setup path automatically verifies encoder artifacts for the selected model and generates them (or provides one-command self-heal) before first transcription run.

### Q3. Persist last selected supervisor profile
- Status: Planned
- Why: Supervisor currently starts from CLI/default profile each run; preserving the last used profile would reduce setup friction.
- Done when: supervisor stores and restores last successful profile selection across restarts.

## Archive Pointer

Previous broad backlog moved to:
`memory-bank/archive/2026-02-09-windows11-focus/issues-backlog-pre-windows11-focus.md`
