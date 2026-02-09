# Windows Acceleration Benchmark Report

- Generated: 2026-02-09T16:44:42
- Host platform: win32
- Corpus files: 1
- Runs per file: 1

## Corpus
- tests\audio\test_english_5s_20250630_094048.wav (4.992s)

## Backend Summary
- python-whisper: median=0.4033s, p95=0.4033s, samples=1, failures=0
  quality: median=0.4118, p10=0.4118, evaluated=1, below_0.6=1

## Recommendation
No backend meets quality threshold (median similarity >= 0.6). Keep python-whisper as default and improve whisper.cpp language/task configuration.
