# Epic: Windows 11 Minimal Runtime (Hotkey + Auto Model Download + Sound Cues)
**ID**: 18-00-00
**Status**: Implemented (pending manual Windows verification)
**Priority**: High
**Complexity**: Medium
**Estimate**: 4-8 hours

## Overview
Enable a minimal Windows 11 runtime path for dictation without full UI parity with macOS. The user can start/stop recording with a global hotkey, see an app icon in the system tray, hear start/stop sound cues, and run with automatic model download (default target: `medium`) if the model is not present locally.

## Problem Statement
The current project is macOS-first and depends on components that do not work on Windows (`rumps`, macOS-centric shortcuts, `brew` assumptions). This blocks practical day-to-day use on Windows 11 for the core dictation workflow.

## Goal
Deliver a "just works" Windows 11 path for:
- Global start/stop toggle via keyboard shortcut
- Tray icon presence for running app visibility
- Audible start/stop feedback
- Automatic Whisper model acquisition on first run

## User Stories
- [x] [18-01-00] Windows Runtime Bootstrap Without macOS UI Dependency
- [x] [18-02-00] Windows Tray Icon and Basic Controls
- [x] [18-03-00] Windows Start/Stop Sound Cues
- [x] [18-04-00] First-Run Medium Model Bootstrap and Windows Runbook

## Scope
### In Scope
- Minimal runtime support for Windows 11 in existing Python entrypoint.
- Hotkey-driven start/stop recording flow.
- Windows system tray icon for app visibility and basic control surface.
- Sound feedback for both recording start and stop on Windows.
- First-run model auto-download behavior using existing Whisper loading flow.
- Updated run instructions for Windows 11 (venv + pip path).

### Out of Scope
- Full tray/status bar parity with macOS.
- Full `whisper.cpp` Windows portability and packaging.
- Installer/distribution work (MSI/EXE/service/autostart polish).
- Deep UI/UX redesign.

## Acceptance Criteria
- [x] App can run on Windows 11 without `rumps`-driven UI dependency.
- [x] One global hotkey combination toggles recording start/stop.
- [x] App exposes a visible icon in Windows system tray while running.
- [x] Start recording plays a sound cue on Windows.
- [x] Stop recording plays a sound cue on Windows.
- [x] Running with `-m medium` downloads model automatically when missing, then proceeds.
- [x] Basic Windows run instructions are documented in README.

## Risks
- Global hotkey behavior can vary across keyboard layouts and elevated applications.
- Windows audio device permissions/configuration can cause false negatives during first run.
- `pyaudio`/PortAudio environment setup can be a friction point.

## Related Files
- `whisper-dictation.py`
- `README.md`
- `requirements.txt`
