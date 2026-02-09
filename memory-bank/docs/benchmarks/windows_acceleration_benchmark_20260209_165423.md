# Windows Acceleration Benchmark Report

- Generated: 2026-02-09T16:54:23
- Host platform: win32
- Corpus files: 8
- Runs per file: 3

## Corpus
- tests\audio\test_english_10s_20250630_094136.wav (9.984s)
- tests\audio\test_english_20250630_085152.wav (4.992s)
- tests\audio\test_english_5s_20250630_094048.wav (4.992s)
- tests\audio\test_immediate_start_20250630_094111.wav (2.944s)
- tests\audio\test_mixed_5s_20250630_094059.wav (4.992s)
- tests\audio\test_polish_10s_20250630_094120.wav (9.984s)
- tests\audio\test_polish_20250630_083944.wav (9.984s)
- tests\audio\test_polish_5s_20250630_094037.wav (4.992s)

## Backend Summary
- python-whisper: median=7.821s, p95=9.714s, samples=24, failures=0
  quality: median=1.0, p10=0.875, evaluated=12, below_0.6=0
- whispercpp-auto: median=1.7583s, p95=8.6286s, samples=24, failures=0
  quality: median=0.527, p10=0.0, evaluated=12, below_0.6=6
- whispercpp-en: median=1.7482s, p95=8.0948s, samples=24, failures=0
  quality: median=0.527, p10=0.0, evaluated=12, below_0.6=6
- whispercpp-pl: median=1.878s, p95=8.1614s, samples=24, failures=0
  quality: median=0.527, p10=0.0, evaluated=12, below_0.6=6

## Recommendation
Python baseline remains fastest/reliable on this profile; keep it as default for now.
