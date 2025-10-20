# Issues & Backlog - Whisper Dictation C++ Version

**Last Updated**: 2025-10-20  
**Status**: Active Issues Identified  

---

## 🔴 CRITICAL ISSUES

### Issue 1: Audio Clipping at Start (Intermittent)
**Status**: Under Investigation  
**Priority**: High  
**Description**: First 50-200ms of audio is sometimes lost, causing beginning of speech to be cut off  
**Evidence**: Occurs intermittently - not 100% reproducible  
**Root Cause**: Diagnostic spec created - see `memory-bank/specs/task-audio-clipping-diagnosis.md`  
**Related Files**: `whisper-dictation-fast.py` (lines 134-162, `Recorder._record_impl()`)  
**Diagnosis Status**: 
- [ ] Phase 1: Timing instrumentation (measure stream initialization delay)
- [ ] Phase 2: Audio content analysis (inspect captured WAV files)
- [ ] Phase 3: Component isolation tests
- [ ] Phase 4: Root cause confirmation

---

### Issue 2: First Two Words Joined (Text Processing)
**Status**: NEW - Needs Investigation  
**Priority**: High  
**Description**: First two words are concatenated without space  
- **Example**: "Długi tekst" appears as "Długitekst"
- **Affects**: Every recording - consistent behavior
- **Symptom**: Missing space between word 1 and word 2 only
- **Scope**: Only impacts first two words, rest of text is fine

**Possible Root Causes**:
1. Transcription model issue (whisper.cpp returning text without space?)
2. Text processing in `SpeechTranscriber.transcribe()` (lines 22-94)
3. Keyboard input simulation issue in `pykeyboard.type()` (lines 70-81)
4. WAV file encoding issue (first frames contain partial data)

**Investigation Needed**:
- [ ] Capture raw transcription output from whisper-cli before keyboard input
- [ ] Check if space character is being skipped (lines 71-75 show special handling)
- [ ] Compare against Python version behavior
- [ ] Test with different languages (PL, EN, etc.)

**Files to Check**:
- `whisper-dictation-fast.py:22-94` - Transcription logic
- `whisper-dictation-fast.py:70-81` - Keyboard typing logic (special space handling?)

---

### Issue 3: Silent Stop - No User Feedback on Max Recording Time
**Status**: NEW - UX/Safety Issue  
**Priority**: High  
**Description**: When recording reaches max time limit, recording silently stops WITHOUT notifying user
- **Behavior**: User continues speaking, but audio is no longer being captured
- **User Experience**: User has no way to know recording stopped
- **Current Max Time**: 30 seconds (hardcoded default in line 297)

**Impact**:
- User dictates what they think is being recorded, but it's not
- Wasted time and frustration
- No error recovery

**Possible Solutions**:
1. Add visual/audio feedback when max time is reached
   - Play system sound (like Pop.aiff)
   - Update status bar icon to indicate max time reached
2. Increase default max time or make it configurable per session
3. Show countdown timer as recording approaches limit

**Related Code**:
- `whisper-dictation-fast.py:224-226` - Timer creation and max_time handling
- `whisper-dictation-fast.py:247-252` - Timer display (shows elapsed time in title)
- `whisper-dictation-fast.py:297-298` - Max time default is 30 seconds

**Files to Modify**:
- `whisper-dictation-fast.py` - Add max-time-reached feedback
- `StatusBarApp.stop_app()` - Add notification logic

---

## 🟡 SECONDARY ISSUES

### Issue 4: Long Transcription Time
**Status**: Known/Expected  
**Priority**: Low (Acknowledged as secondary)  
**Description**: Model transcription takes significant time for longer audio (medium model)
- **Scope**: Using medium model (1.4GB) with Metal GPU
- **Expected**: Longer than base model, but still reasonable for medium quality
- **Acceptable**: User acknowledged this as secondary concern

**Current Performance** (needs measurement):
- [ ] Measure actual transcription time for 10s, 20s, 30s audio
- [ ] Compare: Python version vs C++ version
- [ ] Verify Metal GPU is actually being used during transcription

---

## 📋 INVESTIGATION CHECKLIST

### For Issue 2 (First Two Words Joined):
```
[ ] Run test dictation and capture raw whisper-cli output
[ ] Check if space between words 1-2 exists in raw output
[ ] If exists: problem is in keyboard typing
[ ] If missing: problem is in transcription
[ ] Test with: en, pl, mixed languages
[ ] Compare: Python version behavior
```

### For Issue 3 (Silent Stop):
```
[ ] Measure actual max time enforcement
[ ] Test with 30s, 60s recordings
[ ] Confirm no user feedback when stopping
[ ] Check StatusBarApp state transitions
```

---

## 📁 Related Documentation

- **Diagnostic Spec**: `memory-bank/specs/task-audio-clipping-diagnosis.md`
- **Data Flow**: `docs/DATA_FLOW.md`
- **Current Context**: `current_context.md`
- **README**: Known issues section

---

## 🔧 Next Steps

1. **Immediate**: Implement diagnostics for Issue 1 (audio clipping)
2. **Parallel**: Investigate Issue 2 (joined words) - simpler to debug
3. **Quick Fix**: Add max-time feedback for Issue 3
4. **Later**: Optimize transcription time if needed

---

## Test Cases to Create

```python
def test_first_two_words_spacing():
    """Verify that first two words are properly spaced"""
    # Record: "Pierwsza druga trzecia słowa"
    # Expected: "Pierwsza druga trzecia słowa"
    # Actual: "Pierwszadruga trzecia słowa" ?

def test_max_time_feedback():
    """Verify user gets feedback when max time is reached"""
    # Record for 30+ seconds
    # Expected: Audio stops at 30s with notification
    # Actual: Audio stops silently?

def test_audio_clipping_consistency():
    """Measure how often clipping occurs"""
    # Record 10 samples
    # Measure silence duration at start
    # Calculate: clipping rate, average loss duration
```

---

## Metadata

**Created**: 2025-10-20  
**Session**: Audio Issues Review  
**Reporter**: User (Marcin Przybyszewski)  
**Status**: Active - Ready for Investigation
