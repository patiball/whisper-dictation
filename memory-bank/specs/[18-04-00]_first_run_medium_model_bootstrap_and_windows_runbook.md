# User Story: First-Run Medium Model Bootstrap and Windows Runbook

**ID**: 18-04-00
**Epic**: [18-00-00] Windows 11 Minimal Runtime (Hotkey + Auto Model Download + Sound Cues)
**Status**: Implemented (pending manual Windows verification)
**Priority**: High
**Complexity**: Medium
**Estimate**: 1-2 hours

## User Story
As a Windows 11 user, I want the app to auto-download `medium` model on first run and have clear local setup instructions, so I can start dictating without manual model bootstrapping.

## Background
- User target is practical day-one Windows usage.
- Model bootstrap should happen automatically when missing.

## Acceptance Criteria
- [x] Running with `-m medium` auto-downloads model when not present locally.
- [x] User sees clear progress or status while model is loading/downloading.
- [x] On subsequent runs with cached model, app starts without re-download.
- [x] README contains a tested Windows 11 setup/run section for MVP flow.

## Behavior Examples
- First run: `python whisper-dictation.py -m medium -k ctrl+alt` -> download then ready.
- Next run: starts directly with cached model.

## Files Affected
- `whisper-dictation.py`
- `README.md`

## Implementation Context (Not Part of Spec)
- Reuse Whisper's native model cache behavior; do not introduce a custom downloader unless required.
