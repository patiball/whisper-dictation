# Project Brief: Speech2Text (Whisper Dictation)

## Product Direction

Primary near-term goal is a practical Windows 11 runtime path.
Full cross-platform parity is not required in this phase.

## Current Objective (MVP)

Enable daily use on Windows 11 with:
- global hotkey start/stop
- tray icon visibility
- start/stop sound feedback
- automatic Whisper model download on first run (target: `medium`)

## Non-Goals (Current Phase)

- complete macOS-to-Windows UI parity
- full `whisper.cpp` portability work on Windows
- installer/distribution hardening

## Source of Truth

- Active epic: `memory-bank/specs/[18-00-00]_windows11_minimal_runtime.md`
- Active context: `memory-bank/core/02_activeContext.md`
