# User Story: Windows Tray Icon and Basic Controls

**ID**: 18-02-00
**Epic**: [18-00-00] Windows 11 Minimal Runtime (Hotkey + Auto Model Download + Sound Cues)
**Status**: Implemented (pending manual Windows verification)
**Priority**: High
**Complexity**: Medium
**Estimate**: 2-3 hours

## User Story
As a Windows 11 user, I want a tray icon while the app is running, so I can confirm the app state and access minimal controls.

## Background
- MVP requires app visibility in system tray.
- Full UI parity is out of scope; only essential controls are needed.

## Acceptance Criteria
- [x] App shows a visible tray icon on Windows while running.
- [x] Tray menu exposes at least: Start Recording, Stop Recording, Exit.
- [x] Tray controls call the same recorder state transitions as hotkey flow.
- [x] Exiting from tray performs clean shutdown (listener + audio resources).

## Behavior Examples
- User clicks tray icon menu -> Start Recording -> app enters listening state.
- User clicks Exit -> process terminates cleanly without orphan listeners.

## Files Affected
- `whisper-dictation.py`
- `requirements.txt` (if tray library is added)

## Implementation Context (Not Part of Spec)
- `pystray` is the preferred candidate for Windows tray integration.
