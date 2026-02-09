# Task: Event Logging Points

**ID**: 13-04-02
**User Story**: [13-04-00] Enhanced Logging & Diagnostics
**Complexity**: Simple
**Estimate**: 8 minutes

---

## What

Add logging statements at key diagnostic points throughout the application to capture major events and errors.

---

## Event Categories

**Startup & Initialization:**
- Application start with PID
- Lock file creation/validation
- Microphone access test result
- Watchdog thread initialization
- Device selection decision

**Audio Operations:**
- Recording session start (with configuration)
- Recording session end (with duration)
- Warm-up buffer usage (DEBUG level)
- Audio errors or warnings

**Transcription Operations:**
- Transcription start (model, device, language)
- Command execution details (DEBUG level)
- Transcription completion (duration, text length)
- Transcription errors with context

**Monitoring & Recovery:**
- Watchdog thread start
- Stall detection warnings
- Stream restart attempts and results

**Shutdown:**
- Shutdown signal reception
- Cleanup completion
- Final shutdown message

---

## Log Levels

**DEBUG:** Detailed diagnostic info (heartbeat updates, buffer details, command output)
**INFO:** Normal operations (startup, recording, transcription, shutdown)
**WARNING:** Issues that don't prevent operation (permission denied, stale lock, stall detected)
**ERROR:** Failures that impact functionality (transcription failed, restart failed)

---

## Integration Points

**Main Application (whisper-dictation.py):**
- Startup logging in main block
- Lock file operations in setup_lock_file()
- Microphone check in test_microphone_access()
- Signal handler in signal_handler()

**Recorder:**
- Recording start/end in record_duration()
- Buffer configuration in initialization
- Audio errors during read operations

**Transcriber:**
- Device selection in SpeechTranscriber.__init__()
- Transcription lifecycle in transcribe()
- Command execution errors

**Watchdog:**
- Thread start in watchdog_monitor()
- Stall detection in monitoring loop
- Stream restart in restart_audio_stream()

---

## Acceptance Criteria

- [ ] Startup events logged (PID, lock file, mic check, watchdog)
- [ ] Recording events logged (start, end, duration, config)
- [ ] Transcription events logged (start, end, model, device, errors)
- [ ] Watchdog events logged (start, stall, restart)
- [ ] Shutdown events logged (signal, cleanup, final message)
- [ ] Errors logged with full traceback (ERROR level)
- [ ] Warnings logged for non-fatal issues
- [ ] DEBUG level provides detailed diagnostics
- [ ] All major components instrumented

---

## Implementation Context (Not Part of Spec)

**Example Logging Statements:**
```python
logging.info(f"Application started, PID={os.getpid()}")
logging.info("Lock file created")
logging.warning(f"Microphone access test failed: {e}")
logging.info(f"Recording started, frames_per_buffer={frames_per_buffer}")
logging.info(f"Transcription complete, duration={duration:.2f}s, text_length={len(text)}")
logging.warning(f"Audio system stalled! No heartbeat for {time_since:.1f}s")
logging.error(f"Transcription failed: {e}")
```
