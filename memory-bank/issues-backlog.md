# Issues & Backlog (Active)

Last Updated: 2026-02-09
Focus: Windows 11 MVP only

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

## Not Active Now

- Full `whisper.cpp` Windows support
- Full macOS/Windows UI parity
- Historical test-infra epics unless they block Windows MVP

## Archive Pointer

Previous broad backlog moved to:
`memory-bank/archive/2026-02-09-windows11-focus/issues-backlog-pre-windows11-focus.md`
