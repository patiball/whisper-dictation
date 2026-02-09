# User Story: Windows Start/Stop Sound Cues

**ID**: 18-03-00
**Epic**: [18-00-00] Windows 11 Minimal Runtime (Hotkey + Auto Model Download + Sound Cues)
**Status**: Implemented (pending manual Windows verification)
**Priority**: High
**Complexity**: Simple
**Estimate**: 1 hour

## User Story
As a Windows 11 user, I want audible cues for recording start and stop, so I always know whether dictation is active.

## Background
- Existing sound behavior is implemented for macOS.
- MVP requires equivalent start/stop feedback on Windows.

## Acceptance Criteria
- [x] Start recording emits an audible cue on Windows.
- [x] Stop recording emits an audible cue on Windows.
- [x] Sound playback does not block recording/transcription path.
- [x] Sound failures degrade gracefully (no crash of dictation flow).

## Behavior Examples
- Hotkey start -> immediate short "start" cue.
- Hotkey stop -> immediate short "stop" cue, then transcription proceeds.

## Files Affected
- `whisper-dictation.py`

## Implementation Context (Not Part of Spec)
- Prefer built-in `winsound` for minimal dependency overhead.
