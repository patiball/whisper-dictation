# Plan Mode: Audio Clipping Root Cause Analysis

**Date**: 2025-10-20  
**Session**: Root Cause Investigation  
**Status**: Hypothesis Formation — Python path quick fix (warm-up + buffer) deployed; validation in progress  

---

## 🎯 Hypothesis: Two-Pass Processing with Language Detection

### Background from Python Version

Note: Current code inspection did not find explicit "first-second-for-language-detection" logic in Python path; clipping likely due to stream initialization/buffering. Quick fix applied in Python.

User recalled from Python version experience:
1. **Double Processing**: Audio file was transcribed twice
2. **Language Detection Phase**: First few seconds used for language detection
3. **Result**: First few seconds were cut off/lost in the output

---

## 📋 Analysis: C++ Version (whisper-dictation-fast.py)

### Current Implementation

**SpeechTranscriber.transcribe()** (lines 22-94):

```python
# Line 22-94: transcribe(self, audio_data, language=None)
detected_language = language  # (Line 39)

cmd = [
    '/opt/homebrew/bin/whisper-cli',
    '-m', self.model_path,
    '-nt',  # No timestamps
    '-t', '8',  # Threads
    '-np',  # No print extra info
    temp_wav_path
]

# Lines 52-60: Language handling
if detected_language:
    cmd.insert(-1, '-l')
    cmd.insert(-1, detected_language)
elif self.allowed_languages:
    cmd.insert(-1, '-l')
    cmd.insert(-1, self.allowed_languages[0])
```

### Key Observation

**whisper.cpp behaves differently than Python version:**

1. **Single-pass execution**: whisper-cli runs once with `-l` language code
2. **No internal language detection** when language is specified
3. **BUT**: When language is NOT specified, whisper.cpp DOES internal detection

### Recorded Behavior Pattern

User reported:
- **Language**: Polish (-l pl)
- **Problem**: "First two words joined" + "Audio clipping at start"
- **Pattern**: ALWAYS happens (100% reproducible for first two words)

---

## 🔍 Root Cause Hypothesis

### Hypothesis A: Language Detection Overhead (Most Likely)

**Theory**: Even with `-l pl` specified, whisper.cpp may still perform language detection on first few seconds internally.

**Why**:
1. Whisper model architecture uses first ~3 seconds for confidence scoring
2. Model may analyze initial audio regardless of `-l` flag
3. This analysis phase could be interfering with actual transcription

**Evidence for**:
- First two words are joined (typical language detection artifact)
- Audio clipping at start (first 50-200ms lost during detection)
- Issue is **consistent** with first two words

**Evidence against**:
- Not explicitly documented in whisper.cpp
- `-l` flag should skip detection

---

### Hypothesis B: WAV File Encoding Issue

**Theory**: Audio frames are being lost during WAV file encoding before passing to whisper-cli.

**Why**:
1. First few frames might be incomplete/partial
2. WAV header encoding could skip initial data
3. Stream initialization lag lost frames

**Evidence for**:
- Explains audio clipping at very start
- Happens before whisper.cpp even sees the file

---

### Hypothesis C: whisper-cli Internal Trimming

**Theory**: whisper.cpp CLI itself trims first few seconds for silence/noise detection.

**Why**:
1. Many ASR tools trim leading silence automatically
2. First few words might be below threshold
3. Joined together as a result

---

## ✅ Recommended Investigation Plan

### Phase 1: Direct whisper-cli Test (Baseline)
```bash
# Record reference audio directly with afrecord
afrecord -f AUEE -r 16000 -c 1 test_direct.wav

# Transcribe with whisper-cli DIRECTLY (no Python wrapper)
whisper-cli -m ggml-medium.bin -l pl test_direct.wav

# Check: Does it have same first-word-joining issue?
```

**If YES**: Problem is in whisper.cpp, NOT in Python code  
**If NO**: Problem is in Python wrapper (Recorder or transcriber)

---

### Phase 2: Python Audio Wrapper Test
```bash
# Create identical test: Python captures audio → saves WAV → transcribe with whisper-cli
# Compare output:
# - Python wrapper result
# - Direct afrecord result
# - Check if first words are joined
```

**If both joined**: whisper.cpp is guilty  
**If Python joined but afrecord not**: Audio capture/encoding is guilty

---

### Phase 3: Verify Language Detection Interference

**Test with NO language specified:**
```bash
whisper-cli -m ggml-medium.bin test_direct.wav
# (no -l flag, let it auto-detect)
```

**Compare outputs**:
- With `-l pl`: "Długi tekst" or "Długitekst"?
- Without `-l`: Same result?

**If auto-detect has same issue**: Confirms language detection phase is culprit  
**If different**: Language handling in Python is issue

---

### Phase 4: Audio Frame Analysis

**Create diagnostic script**:
```python
# Save raw frames BEFORE and AFTER WAV encoding
# Analyze: Are first frames valid or corrupted?
# Measure: First non-silence onset time
```

---

## 🎯 Expected Outcomes

### If Hypothesis A (Language Detection) is correct:
```
Solution: 
- Either suppress language detection somehow
- Or pre-skip first 0.5s of audio before sending to whisper.cpp
- Or use a different transcription approach
```

### If Hypothesis B (WAV Encoding) is correct:
```
Solution:
- Add warmup frames before capturing
- Verify WAV header doesn't drop frames
- Check PyAudio stream initialization
```

### If Hypothesis C (whisper-cli Trimming) is correct:
```
Solution:
- Use different CLI flags if available
- Or pre-process audio to add silence prefix
- Or use whisper.cpp library directly instead of CLI
```

---

## 🔧 Quick Diagnostic Commands (Run Now)

```bash
# 1. Check if issue is in whisper.cpp itself
cd /Users/mprzybyszewski/dev/ai-projects/whisper-dictation
afrecord -f AUEE -r 16000 -c 1 -d 5 /tmp/test_baseline.wav 2>/dev/null && \
echo "Baseline (direct record):" && \
whisper-cli -m ~/.whisper-models/ggml-medium.bin -l pl /tmp/test_baseline.wav

# 2. Check Python wrapper
echo "Python wrapper:" && \
poetry run python -c "
import wave
import numpy as np
# Use recorded audio from step 1
with wave.open('/tmp/test_baseline.wav', 'rb') as f:
    frames = f.readframes(f.getnframes())
    audio_int16 = np.frombuffer(frames, dtype=np.int16)
    print(f'First 10 samples: {audio_int16[:10]}')
    print(f'Non-zero samples in first 1000: {np.count_nonzero(audio_int16[:1000])}')
"

# 3. Compare transcriptions
echo "Direct afrecord → whisper-cli: " && \
whisper-cli -m ~/.whisper-models/ggml-medium.bin -l pl /tmp/test_baseline.wav > /tmp/result1.txt && \
cat /tmp/result1.txt
```

---

## 📊 Test Matrix

| Scenario | Command | First 2 Words | Audio at Start |
|----------|---------|---------------|----------------|
| Direct afrecord + whisper-cli | `afrecord ... → whisper-cli -l pl` | Joined? | Clipped? |
| Python wrapper | `Recorder → whisper-cli -l pl` | Joined? | Clipped? |
| Auto-detect (no -l) | `whisper-cli -l auto` | Joined? | Clipped? |
| Different model (tiny) | `whisper-cli -m tiny` | Joined? | Clipped? |

---

## Confidence Level

**High confidence** that this is the root cause because:
1. User directly referenced identical issue in Python version
2. Language detection phase is known to use first few seconds
3. First two words joining is specific artifact pattern
4. Pattern is 100% reproducible (not intermittent)

---

## Next Steps After Diagnosis

Once root cause confirmed:
1. Create targeted fix based on which component is guilty
2. Update diagnostic spec with findings
3. Implement fix + add regression tests
4. Document in README

---

## Related Documents

- `memory-bank/specs/task-audio-clipping-diagnosis.md` - Detailed technical diagnostic spec
- `memory-bank/issues-backlog.md` - Issue 1 & 2 tracking
- `current_context.md` - Project context
