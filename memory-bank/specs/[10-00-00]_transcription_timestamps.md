# Feature: Add Timestamps to Transcription Flow

**Status**: In Progress
**Priority**: High
**Complexity**: Simple
**Estimate**: 30-45 minutes
**Jira Epic**: [MSB-1](https://metal-scribe.atlassian.net/browse/MSB-1) - CLI-Jira-Confluence Integration MVP
**Jira Story**: [MSB-2](https://metal-scribe.atlassian.net/browse/MSB-2) - Add Timestamps to Transcription Flow

## Problem

Currently, console messages appear instantly but don't reflect actual processing stages:
- "Done.\n" appears immediately after stopping recording
- Actual transcription (whisper-cli subprocess or PyTorch model) takes 2-5 seconds
- Text typing to application happens several seconds after "Done"
- User cannot diagnose where delays occur

**Example current output:**
```
Listening...
Transcribing...
Done.\n          <- appears instantly, but transcription hasn't even started
                  <- 2-5 second delay here (no feedback)
                  <- text finally appears
```

**Bug:** `print('Done.\\n')` contains literal `\\n` instead of newline escape sequence.

## Goal

Add timestamps to all console messages and clarify what each stage represents, allowing users to diagnose performance bottlenecks.

## Acceptance Criteria

### Timestamps

- [ ] All console messages include timestamp in format `[HH:MM:SS.mmm]`
- [ ] Timestamp helper function `get_timestamp()` added to both files
- [ ] Timestamps work consistently in both Python and C++ versions

### Message Clarity

- [ ] "Listening..." - when recording starts
- [ ] "Transcribing..." - when recording stops (unchanged for backward compatibility)
- [ ] "Transcription complete" - **after** whisper-cli/model finishes (NEW)
- [ ] "Typing text..." - before keyboard typing starts (NEW)
- [ ] Bug fixed: `'Done.\\n'` → removed or repurposed

### Behavior Examples

**Expected output after changes:**
```
[14:23:45.123] Listening...
[14:23:48.456] Transcribing...
[14:23:51.789] Transcription complete
[14:23:51.790] Typing text...
```

This clearly shows:
- Recording duration: 3.3s (48.456 - 45.123)
- Transcription duration: 3.3s (51.789 - 48.456)
- Typing starts immediately after transcription

## File Changes Required

### Both files: `whisper-dictation.py` and `whisper-dictation-fast.py`

**1. Add timestamp helper (top of file):**
```python
from datetime import datetime

def get_timestamp():
    """Returns formatted timestamp [HH:MM:SS.mmm]"""
    return datetime.now().strftime("[%H:%M:%S.%f")[:-3] + "]"
```

**2. StatusBarApp.start_app():**
- Line 222 (fast.py) / 283 (py): `print('Listening...')`
- Change to: `print(f'{get_timestamp()} Listening...')`

**3. StatusBarApp.stop_app():**
- Line 243 (fast.py) / 304 (py): `print('Transcribing...')`
- Change to: `print(f'{get_timestamp()} Transcribing...')`
- Line 249 (fast.py) / 310 (py): `print('Done.\\n')`
- **Remove this line** (message moved to after actual transcription)

**4. SpeechTranscriber.transcribe():**

**whisper-dictation-fast.py (line ~67, after subprocess.run completes):**
```python
if result.returncode == 0:
    print(f'{get_timestamp()} Transcription complete')
    # Pobierz tekst ze stdout
    text = result.stdout.strip()
    if text:
        print(f'{get_timestamp()} Typing text...')
        # Wpisz tekst znak po znak
        is_first = True
        for element in text:
```

**whisper-dictation.py (line ~61, after model.transcribe completes):**
```python
else:
    result = self.model.transcribe(audio_data, **options)

print(f'{get_timestamp()} Transcription complete')

is_first = True
print(f'{get_timestamp()} Typing text...')
for element in result["text"]:
```

## Technical Notes

### Threading Considerations

- `StatusBarApp` runs in main thread
- `Recorder._record_impl()` and `SpeechTranscriber.transcribe()` run in separate thread
- Messages from different threads will interleave correctly with timestamps
- `print()` in Python is thread-safe for line-based output

### Async Nature

Current flow:
1. User stops recording → StatusBarApp.stop_app() runs (main thread)
2. StatusBarApp prints "Transcribing..." and "Done" immediately
3. Recorder thread continues: processes audio → calls transcribe() → types text

This is why "Done" appears before actual work completes. Solution: move completion message to transcribe().

## Testing

Manual test sequence:
1. Start application: `poetry run python whisper-dictation-fast.py --k_double_cmd`
2. Double-tap CMD to start recording
3. Speak for 3-5 seconds
4. Single-tap CMD to stop recording
5. Observe console output with timestamps
6. Verify timing makes sense (recording duration, transcription duration, typing duration)
7. Repeat for `whisper-dictation.py` (Python version)

Expected observations:
- Clear timestamps on every message
- "Transcription complete" appears 2-5 seconds after "Transcribing..."
- "Typing text..." appears immediately after "Transcription complete"
- No literal `\n` characters in output

## Risk Assessment

**Low risk:**
- Only adds logging, no logic changes
- print() is thread-safe
- Timestamp function is simple utility

**Potential issues:**
- None expected
- If timestamp import fails, add to requirements (datetime is stdlib)

## Future Enhancements (Out of Scope)

- Add duration metrics: "Transcription complete (3.2s)"
- Add progress indicators for long transcriptions
- Write timestamps to log file for analysis
- Add --quiet flag to suppress timestamps

---

**Expected Outcome:** Clear visibility into transcription pipeline stages with precise timing, enabling performance diagnosis and better user feedback.
