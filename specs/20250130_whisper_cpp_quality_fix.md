# Epic: Whisper.cpp Quality Fix - Audio Cutting & Translation Issues
**Status**: Ready  
**Priority**: Critical  
**Complexity**: Medium  
**Created**: 2025-01-30  
**Target**: Production-ready whisper.cpp with M1 GPU support  

## Overview
Whisper.cpp implementation (`whisper-dictation-fast.py`) ma identyczne problemy do tych które naprawiliśmy w Python version:
1. **Audio Cutting**: Dźwięki odtwarzane podczas/zaraz po nagraniu zakłócają audio
2. **Translation vs Transcription**: Brak proper flag powoduje tłumaczenie zamiast transkrypcji  
3. **Language Detection Issues**: Wymuszanie pierwszego allowed_language zamiast proper detection

Te problemy są **identyczne** z tymi naprawionymi w specs/20250729_transcription_performance_fix.md i specs/20250730_sound_and_shortcut_fix.md.

## Root Cause Analysis

### 1. Audio Cutting Problem
```python
# PROBLEM: Dźwięki zakłócają nagranie
def _record_impl(self, language):
    self.recording = True
    self.sound_player.play_start_sound()  # ← ZAKŁÓCA POCZĄTEK NAGRANIA
    
    # ... nagrywanie ...
    
    self.sound_player.play_stop_sound()   # ← MOŻE UCINAĆ KOŃCÓWKĘ
    audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
```

**Rozwiązanie**: Delay dźwięków jak w Python version.

### 2. Translation vs Transcription Problem  
```python
# PROBLEM: Brak explicit transcription mode
cmd = ['/opt/homebrew/bin/whisper-cli', '-m', self.model_path, '-nt', '-t', '8', '-np', temp_wav_path]

# BRAKUJE: --translate flag control
# whisper-cli domyślnie może robić translation dla non-English audio
```

**Rozwiązanie**: Dodać explicit `--translate false` lub equivalent flag.

### 3. Language Detection Problem
```python
# PROBLEM: Wymuszanie języka zamiast detection
elif self.allowed_languages:
    cmd.insert(-1, '-l')
    cmd.insert(-1, self.allowed_languages[0])  # ← WYMUSZA en, nie wykrywa!
```

**Rozwiązanie**: Użyć auto-detection z post-processing validation.

## Acceptance Criteria

### Audio Quality Fix
- [ ] Dźwięki nie zakłócają nagrania (delay jak w Python version)
- [ ] Pełne audio jest przetwarzane (brak cutting na początku/końcu)
- [ ] Audio recording pipeline identyczny z working Python version

### Transcription Mode Fix  
- [ ] Explicit transcription mode (nie translation)
- [ ] Sprawdzić whisper-cli flags dla transcription vs translation
- [ ] Test: Polish audio → Polish text (nie English translation)

### Language Detection Fix
- [ ] Auto-detection języka zamiast wymuszania pierwszego allowed_language
- [ ] Proper handling allowed_languages list (validation post-transcription)
- [ ] Consistent behavior z Python version

### Performance Validation
- [ ] M1 GPU acceleration working (verify via Activity Monitor)
- [ ] Quality równa Python version na tym samym audio
- [ ] Speed improvement vs Python version measured

## Implementation Plan

### Phase 1: Audio Pipeline Fix
```python
# Fix recording pipeline - delay sounds like in Python version
def _record_impl(self, language):
    self.recording = True
    
    # Start recording FIRST
    frames_per_buffer = 1024
    p = pyaudio.PyAudio()
    stream = p.open(...)
    frames = []
    
    # DELAY sound to not interfere with recording
    threading.Timer(0.1, self.sound_player.play_start_sound).start()
    
    while self.recording:
        data = stream.read(frames_per_buffer)
        frames.append(data)
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # Process audio BEFORE stop sound
    audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
    audio_data_fp32 = audio_data.astype(np.float32) / 32768.0
    
    # DELAY stop sound
    threading.Timer(0.1, self.sound_player.play_stop_sound).start()
    
    # Transcribe
    self.transcriber.transcribe(audio_data_fp32, language)
```

### Phase 2: Transcription Mode Fix
```python
# Research whisper-cli flags for transcription vs translation
# Check: --translate, --task, or similar flags
cmd = [
    '/opt/homebrew/bin/whisper-cli',
    '-m', self.model_path,
    '-nt',  # No timestamps
    '-t', '8',  # 8 threads for M1
    '-np',  # No prints
    '--task', 'transcribe',  # EXPLICIT transcription mode
    # OR: '--translate', 'false'
    temp_wav_path
]
```

### Phase 3: Language Detection Fix
```python
# Use auto-detection with post-validation (like Python version)
def transcribe(self, audio_data, language=None):
    # ... save audio to temp file ...
    
    cmd = ['/opt/homebrew/bin/whisper-cli', '-m', self.model_path, '-nt', '-t', '8', '-np']
    
    # Let whisper auto-detect language
    if language:
        cmd.extend(['-l', language])
    # Don't force language if allowed_languages - let it auto-detect
    
    cmd.append(temp_wav_path)
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    
    if result.returncode == 0:
        text = result.stdout.strip()
        
        # Post-process: validate against allowed_languages if needed
        if self.allowed_languages and not language:
            # Could add language detection validation here
            # For now, trust whisper's auto-detection
            pass
            
        # Type text...
```

## Testing Strategy

### Comparison Tests
```python
# Test same audio file with both versions
def test_python_vs_cpp_quality():
    audio_file = "test_polish_sample.wav"
    
    # Python version result
    python_result = python_transcriber.transcribe(audio_file)
    
    # C++ version result  
    cpp_result = cpp_transcriber.transcribe(audio_file)
    
    # Compare quality, language detection, etc.
    assert python_result.language == cpp_result.language
    assert similarity(python_result.text, cpp_result.text) > 0.9
```

### Audio Pipeline Tests
```python
def test_audio_cutting_fix():
    # Record 5-second sample
    # Verify full 5 seconds are processed
    # Check for audio artifacts at beginning/end
```

### M1 GPU Verification
```python
def test_m1_gpu_usage():
    # Monitor GPU usage during transcription
    # Verify Metal Performance Shaders active
    # Measure speed improvement vs CPU
```

## File Changes Required

### Core Implementation
- **`whisper-dictation-fast.py`**: Fix audio pipeline, transcription mode, language detection
- **`whisper-dictation-optimized.py`**: Apply same fixes if needed

### Testing
- **`tests/test_whisper_cpp_quality.py`** (NEW): Quality comparison tests
- **`tests/test_whisper_cpp_audio.py`** (NEW): Audio pipeline tests

## Success Metrics

### Quality Targets
- **Transcription Accuracy**: Match Python version (>95% similarity)
- **Language Detection**: Correct language detection rate >90%
- **Audio Completeness**: Zero audio cutting issues

### Performance Targets  
- **M1 GPU Utilization**: Verified via Activity Monitor
- **Speed Improvement**: 2-3x faster than Python version
- **Memory Usage**: Lower than Python version

### User Experience
- **No Translation Issues**: Polish audio → Polish text
- **No Audio Cutting**: Complete audio processed
- **Consistent Quality**: Reliable as Python version

## Risk Assessment

### Low Risk
- Audio pipeline fix (proven solution from Python version)
- Sound delay implementation (already working pattern)

### Medium Risk  
- whisper-cli flag research (need to verify correct transcription flags)
- Language detection changes (need to maintain compatibility)

### Mitigation
- Test extensively with known audio samples
- Keep Python version as fallback
- Gradual rollout with user choice

---

**Expected Outcome**: 🎯 **PRODUCTION READY WHISPER.CPP** - M1 GPU acceleration with Python-level quality and reliability.