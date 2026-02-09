# Windows Acceleration Benchmark Report

- Generated: 2026-02-09T16:38:12
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
- python-whisper: median=7.9608s, p95=22.892s, samples=24, failures=0
- whispercpp-default: median=1.4703s, p95=8.0989s, samples=24, failures=0

## Recommendation
Use whispercpp-default as primary acceleration candidate for next integration step (Issue [19-03-00]), with fallback to python-whisper.
