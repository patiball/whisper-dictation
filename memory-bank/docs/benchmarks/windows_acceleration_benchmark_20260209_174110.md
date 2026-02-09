# Windows Acceleration Benchmark Report

- Generated: 2026-02-09T17:41:10
- Host platform: win32
- Corpus files: 1
- Runs per file: 1

## Corpus
- tests\audio\test_english_5s_20250630_094048.wav (4.992s)

## Backend Summary
- python-whisper: median=0.4001s, p95=0.4001s, samples=1, failures=0
  quality: median=1.0, p10=1.0, evaluated=1, below_0.6=0
- whispercpp-openvino-gpu: median=0.9851s, p95=0.9851s, samples=1, failures=0
  quality: median=1.0, p10=1.0, evaluated=1, below_0.6=0

## Recommendation
Python baseline remains fastest/reliable on this profile; keep it as default for now.
