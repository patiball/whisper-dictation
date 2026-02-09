# Task: Audio Clipping Root Cause Diagnosis

**Status**: Ready  
**Priority**: High  
**Estimated Complexity**: Medium  
**Created**: 2025-10-19  
**Last Updated**: 2025-10-19  

---

## Overview

Audio is being clipped at the beginning of recordings in `whisper-dictation-fast.py` (C++ version with Metal GPU). The problem must be systematically isolated through instrumentation and testing rather than assumption.

**Suspected root causes** (in order of likelihood):
1. PyAudio stream initialization delay (~50-100ms)
2. Sound effect blocking - `play_start_sound()` is async, recording starts before sound completes
3. Double command key timing/debouncing issues
4. Audio frame buffering/warmup requirements
5. Something else entirely (unknown)

---

## Acceptance Criteria

- [ ] Create instrumented version of `Recorder` class that logs all timing events
- [ ] Capture raw audio samples WITH known timing markers
- [ ] Isolate each suspected cause independently
- [ ] Identify which component actually causes clipping
- [ ] Document exact timestamp when clipping occurs
- [ ] Provide clear evidence pointing to root cause
- [ ] Enable fix without guessing

---

## File Changes Required

- `tests/diagnose_audio_clipping.py` - NEW: Diagnostic test suite
- `recorder_instrumented.py` - NEW: Instrumented Recorder with detailed logging
- `tests/audio/diagnostic_recordings/` - NEW: Directory for diagnostic captures

---

## Diagnostic Strategy

### Phase 1: Timing Instrumentation (Isolate Stream Initialization)

**Goal**: Measure exact timing of each component startup

**Steps**:
1. Instrument `Recorder._record_impl()` with timestamps:
   - T0: Method entry
   - T1: After `play_start_sound()` call
   - T2: After PyAudio stream opens
   - T3: After first `stream.read()`
   - T4: After 5 frames captured

2. Log CPU time with microsecond precision using `time.perf_counter()`

3. Print human-readable timing report showing:
   ```
   Sound effect delay: T1-T0 = Xms
   Stream initialization: T2-T1 = Yms
   First frame available: T3-T2 = Zms
   Initial buffering time: T4-T3 = Ams
   ```

### Phase 2: Audio Content Inspection (Check What's Actually Captured)

**Goal**: Determine if silence/clipping is in the actual audio data or downstream

**Steps**:
1. Modify `Recorder._record_impl()` to save RAW audio to WAV file BEFORE transcription
2. Save test audio files with pattern: `diagnostic_raw_<timestamp>.wav`
3. For each recording session:
   - Save raw audio buffer
   - Run analysis: detect silence duration at start
   - Measure audio level changes

4. Use librosa to analyze:
   ```python
   audio, sr = librosa.load('diagnostic_raw_*.wav', sr=16000)
   # Find first non-silent frame (threshold: -60dB)
   # Report: "Silence at start: X milliseconds"
   ```

### Phase 3: Component Isolation Tests

**Test A: PyAudio Stream Warmup**
- Open stream, immediately read frames WITHOUT playing sound effect
- Expected: First frame should have minimal/no delay
- If clipping still occurs: PyAudio is the culprit
- If no clipping: Issue is elsewhere

**Test B: Sound Effect Blocking**
- Add explicit `sleep(0.5)` after `play_start_sound()` before stream opens
- Expected: If sound blocking matters, this should fix it
- If clipping persists: Sound effect timing is not the issue

**Test C: Key Detection Timing**
- Log exact timestamps of key press → `on_key_press()` → `start_app()` → `recorder.start()`
- Measure total latency from key event to stream.read() start
- Compare against expected ~100ms human reaction time

**Test D: Direct Mic Input Verification**
- Use `afrecord` command-line tool (macOS native) to record audio directly
- Compare: afrecord output vs. Python PyAudio output
- If afrecord has no clipping: Python/PyAudio is the issue
- If afrecord also clips: Mic driver or system-level issue

### Phase 4: Evidence Collection

For each test:
1. Record 5-10 samples
2. Save timing logs
3. Analyze audio content
4. Document findings in structured format:

```
TEST: PyAudio Stream Warmup
├─ Sound effect blocking: ENABLED/DISABLED
├─ Average delay to first frame: 150ms
├─ Audio clipping observed: YES/NO
├─ Silence at start: 0ms / 200ms / 400ms
└─ Conclusion: Likely/Unlikely cause
```

---

## Implementation Approach

### Create `tests/diagnose_audio_clipping.py`

```python
# Pseudocode structure:
class AudioClippingDiagnostics:
    def test_stream_initialization_timing(self)
    def test_sound_effect_blocking(self)
    def test_raw_audio_content(self)
    def test_direct_afrecord_comparison(self)
    def analyze_captured_audio(wav_path)
    def generate_diagnostic_report()
```

### Create `recorder_instrumented.py`

Extend `Recorder` with:
- `_record_impl_with_logging()` - instrumented version
- Microsecond-precision timestamps
- Raw audio file capture before/after conversion
- Summary statistics output

---

## Success Criteria

After running diagnostics, you will have:

1. **Clear timing profile**: Exact ms for each startup phase
2. **Audio analysis**: Exact duration of silence/clipping at start
3. **Component identification**: Which of the 5 suspects is causing the issue
4. **Evidence file**: Raw audio samples showing the problem
5. **Recommendation**: Specific fix target (e.g., "Add 200ms delay after stream open")

---

## Testing Instructions

```bash
cd /Users/mprzybyszewski/dev/ai-projects/whisper-dictation

# Phase 1: Run timing diagnostics
poetry run python tests/diagnose_audio_clipping.py --phase timing

# Phase 2: Run audio content analysis
poetry run python tests/diagnose_audio_clipping.py --phase content

# Phase 3: Run component isolation
poetry run python tests/diagnose_audio_clipping.py --phase isolation

# Phase 4: Generate full report
poetry run python tests/diagnose_audio_clipping.py --report
```

---

## Key Questions Answered by This Spec

- **Q**: How long is the delay from sound effect to first audio capture?  
  **A**: Will be measured in Phase 1

- **Q**: Is clipping in the raw captured data or introduced elsewhere?  
  **A**: Will be determined in Phase 2 by analyzing saved WAV files

- **Q**: Does direct `afrecord` have the same problem?  
  **A**: Will be tested in Phase 4 to isolate Python/PyAudio from system

- **Q**: What's the actual duration of lost audio?  
  **A**: Will be measured in milliseconds in Phase 2

---

## Notes

- **No fixes yet**: This spec is diagnostic only - identifies problem, doesn't fix it
- **Evidence-based**: All claims will be backed by actual timing measurements and audio analysis
- **Reproducible**: All tests can be re-run to verify findings
- **Tool selection**: Uses `librosa` (already in dev dependencies) for audio analysis

---

## Brittleness Analysis

✅ **Good balance achieved:**
- Specifies WHAT to measure (timing, audio content) not HOW exactly
- Allows flexible implementation of timing instrumentation
- Diagnostic approach is language/tool agnostic
- Clear success criteria enable any developer to know when complete
- Avoids prescribing exact code structure

---

## Related Documents

- `current_context.md` - Known issues with C++ version
- `DATA_FLOW.md` - Recording component details
- Audio clipping mentioned in README.md under "Known Issues with C++ Version"
