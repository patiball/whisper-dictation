# Windows Acceleration Benchmark Report

- Generated: 2026-02-09T15:09:09
- Host platform: win32
- Corpus files: 1
- Runs per file: 1

## Corpus
- tests\audio\test_english_5s_20250630_094048.wav (4.992s)

## Backend Summary
- python-whisper: median=0.432s, p95=0.432s, samples=1, failures=0
- whispercpp-default: median=1.3761s, p95=1.3761s, samples=1, failures=0

## Recommendation
Python baseline remains fastest/reliable on this profile; keep it as default for now.
