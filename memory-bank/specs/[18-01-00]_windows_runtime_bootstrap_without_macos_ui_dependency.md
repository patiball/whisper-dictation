# User Story: Windows Runtime Bootstrap Without macOS UI Dependency

**ID**: 18-01-00
**Epic**: [18-00-00] Windows 11 Minimal Runtime (Hotkey + Auto Model Download + Sound Cues)
**Status**: Implemented (pending manual Windows verification)
**Priority**: High
**Complexity**: Medium
**Estimate**: 1-2 hours

## User Story
As a Windows 11 user, I want the app to start and run without macOS-only UI dependencies, so the core dictation runtime is usable on Windows.

## Background
- Current runtime path imports `rumps`, which is macOS-only.
- Windows MVP does not require full menu-bar parity.

## Acceptance Criteria
- [x] App startup on Windows does not require `rumps`.
- [x] Runtime path remains available on macOS (no intentional regression).
- [x] Existing hotkey listener path can still toggle start/stop recording on Windows.
- [x] Failure mode is clear if required Windows dependencies are missing.

## Behavior Examples
- Windows run: app starts in background process mode without status bar dependency.
- macOS run: existing status bar behavior remains available.

## Files Affected
- `whisper-dictation.py`
- `requirements.txt` (if dependency split is needed)

## Implementation Context (Not Part of Spec)
- Prefer conditional platform import/use rather than hard fork of code path.
