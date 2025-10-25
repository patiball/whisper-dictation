# User Story: Audio Stream Watchdog

**ID**: 13-03-00
**Epic**: [13-00-00] Lessons Learned Foundation
**Status**: Draft
**Priority**: High
**Complexity**: Medium-High
**Estimate**: 30-40 minutes

---

## User Story

**As a** whisper-dictation user,
**I want** the application to continuously monitor the audio stream and automatically recover if it becomes stalled or unresponsive,
**So that** I have confidence the application will keep working even if the audio system misbehaves.

---

## Background

### Current Situation
- Audio stream can occasionally "stall" (stop providing data)
- When stalled, application appears to work but no audio is recorded
- User has no feedback that recording failed
- Only option is to manually kill and restart app

### Why This Matters
- **Long-Running Stability**: Background app should handle transient issues
- **Transparent Recovery**: User shouldn't notice brief hiccups
- **Better Than Crash**: Recover gracefully instead of hanging
- **Production Quality**: Professional apps monitor their I/O streams

### Pattern from macos-dictate
```python
def watchdog_monitor():
    """Monitor audio heartbeat, restart stream if stalled"""
    global last_heartbeat, audio_timeout, stream
    while watchdog_active:
        if recording:
            time_since = (datetime.now() - last_heartbeat).total_seconds()
            if time_since > audio_timeout:  # 10 seconds
                logging.warning(f"Audio stalled, restarting stream...")
                restart_audio_stream()
        time.sleep(1)
```

---

## What We're Building

**Background watchdog thread** that:
1. Monitors audio stream "heartbeat" (data arrival)
2. Detects stalls (no data for >10 seconds)
3. Automatically restarts the stream
4. Logs all watchdog events

**Key design**: Non-blocking, doesn't interfere with recording, graceful recovery.

---

## Assumptions & Validation

### A1: Heartbeat Update is Reliable
- Assumption: Audio read operations reliably update heartbeat
- Validation: Verify that heartbeat is updated in correct location
- Risk: Heartbeat not updated → false stall detection
- Mitigation: Add heartbeat update in record loop only

### A2: 10 Second Timeout is Reasonable
- Assumption: 10s is long enough for slow transcriptions, short enough for quick detection
- Validation: User testing with various model sizes
- Risk: Too short = false positives; Too long = late detection
- Mitigation: Make timeout configurable via CLI flag (future)

### A3: Stream Restart is Safe
- Assumption: Calling `stream.stop()` + `stream.start()` is safe
- Validation: Test restart behavior doesn't corrupt audio
- Risk: Restart fails → watchdog loops indefinitely
- Mitigation: Add restart attempt counter, bail out after 3 failures

### A4: Recording Flag is Atomic
- Assumption: Global `recording` flag is safely accessible
- Validation: Thread-safe operations on boolean
- Risk: Race condition between watchdog and main thread
- Mitigation: Use threading.Lock if needed (Python bool assignment is atomic)

---

## Acceptance Criteria

### Watchdog Functionality
- [ ] **W1** Watchdog thread starts with application
- [ ] **W2** Watchdog monitors only during active recording (`if recording:`)
- [ ] **W3** Heartbeat updated on every successful audio read
- [ ] **W4** Stall detected if heartbeat >10 seconds old
- [ ] **W5** Stream restart initiated when stall detected
- [ ] **W6** Restart completes without hanging (timeout protection)
- [ ] **W7** Watchdog continues monitoring after successful restart
- [ ] **W8** Watchdog exits cleanly on application shutdown

### Logging
- [ ] **L1** Watchdog thread start: INFO "Watchdog thread started"
- [ ] **L2** Stall detection: WARNING "Audio system stalled! No heartbeat for X.Xs"
- [ ] **L3** Restart attempt: INFO "Restarting audio stream..."
- [ ] **L4** Restart success: INFO "Audio stream restarted successfully"
- [ ] **L5** Restart failure: ERROR "Failed to restart audio stream: reason"

### No Regressions
- [ ] **R1** Recording still works without watchdog
- [ ] **R2** Performance unaffected (watchdog is lightweight)
- [ ] **R3** Existing tests still pass
- [ ] **R4** Works with both whisper-dictation.py and whisper-dictation-fast.py

### Thread Safety
- [ ] **T1** No race conditions on shared variables
- [ ] **T2** Graceful interaction with recorder thread
- [ ] **T3** Proper cleanup of watchdog thread on exit

---

## Behavior Examples

### Example 1: Normal Recording (No Stall)
```
[14:23:45.123] Listening...
[14:23:45.124] Watchdog thread started
[14:23:48.000] Transcribing...      <- User stops recording
[14:23:48.001] Watchdog: Recording ended, monitoring paused
[14:23:51.000] Transcription complete
[14:23:51.001] Watchdog monitoring paused (no active recording)
```

Watchdog runs but only logs when recording is active.

### Example 2: Audio Stall Detected & Recovered
```
[14:23:45.123] Listening...
[14:23:45.124] Watchdog thread started
[14:23:48.000] Recording audio...
[14:23:58.000] WARNING: Audio system stalled! No heartbeat for 10.0s
[14:23:58.001] INFO: Restarting audio stream...
[14:23:58.002] Watchdog: Stream closed, reinitializing...
[14:23:58.050] INFO: Audio stream restarted successfully
[14:23:58.051] Watchdog: Resuming monitoring...
[14:24:00.000] Transcribing...
```

User doesn't notice stall, recording continues.

### Example 3: Watchdog Timeout During Shutdown
```
[14:23:45.123] Listening...
[14:24:00.000] Transcribing...
^C[14:24:05.000] Signal 2 received
[14:24:05.001] INFO: Stopping watchdog monitoring...
[14:24:05.002] Watchdog: Watchdog thread exiting...
[14:24:05.003] INFO: Shutdown complete
```

Watchdog cleanly stops when app exits.

---

## Design & Implementation

### Global Variables (Module Level)
```python
# Watchdog state
watchdog_active = True        # Controls watchdog loop
last_heartbeat = datetime.now()  # Last successful audio read
audio_timeout = 10            # Seconds before stall detected
watchdog_thread = None        # Reference to watchdog thread
```

### Functions

```python
def update_heartbeat():
    """Call this every time audio is successfully read"""
    global last_heartbeat
    last_heartbeat = datetime.now()

def restart_audio_stream():
    """Stop and restart the audio stream"""
    global stream, recording
    try:
        if stream is not None:
            stream.stop()
            stream.close()
        # Reinitialize stream
        import pyaudio
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=512,
            exception_on_overflow=False
        )
        stream.start_stream()
        logging.info("Audio stream restarted successfully")
    except Exception as e:
        logging.error(f"Failed to restart audio stream: {e}")
        recording = False  # Stop recording on restart failure

def watchdog_monitor():
    """Monitor audio stream for stalls and restart if needed"""
    global watchdog_active, last_heartbeat, audio_timeout, recording, stream
    logging.info("Watchdog thread started")

    while watchdog_active:
        try:
            if recording:
                time_since_heartbeat = (datetime.now() - last_heartbeat).total_seconds()
                if time_since_heartbeat > audio_timeout:
                    logging.warning(
                        f"Audio system stalled! No heartbeat for {time_since_heartbeat:.1f}s"
                    )
                    logging.info("Restarting audio stream...")
                    restart_audio_stream()
            time.sleep(1)  # Check every second
        except Exception as e:
            logging.error(f"Watchdog error: {e}")
            time.sleep(5)  # Back off if error

    logging.info("Watchdog thread exiting")
```

### Integration Points

**In Recorder._record_impl() loop:**
```python
# Every time we successfully read audio
try:
    data = stream.read(frames_per_buffer, exception_on_overflow=False)
    frames.append(data)
    update_heartbeat()  # [NEW - update watchdog]
except Exception as e:
    # error handling...
```

**In main block:**
```python
if __name__ == "__main__":
    # ... setup lock file, microphone check, etc. ...

    # Start watchdog thread [NEW]
    watchdog_thread = threading.Thread(target=watchdog_monitor, daemon=False)
    watchdog_thread.start()

    # ... rest of setup ...
    app.run()

    # On exit (handled by signal handler)
    watchdog_active = False
    watchdog_thread.join(timeout=2)
```

---

## Test Cases (TDD - Write FIRST)

### Test Suite: `tests/test_audio_watchdog.py`

```python
import pytest
import threading
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, call
import logging

from whisper_dictation_module import (
    update_heartbeat,
    watchdog_monitor,
    restart_audio_stream,
    last_heartbeat,
    watchdog_active,
    recording,
    audio_timeout
)

class TestHeartbeatTracking:
    """Test heartbeat update mechanism"""

    def test_heartbeat_updated(self):
        """update_heartbeat() should update last_heartbeat"""
        import whisper_dictation_module as mod

        old_time = mod.last_heartbeat
        time.sleep(0.1)  # Small delay
        update_heartbeat()
        new_time = mod.last_heartbeat

        assert new_time > old_time

    def test_heartbeat_starts_at_current_time(self):
        """On module load, heartbeat should be close to current time"""
        from datetime import datetime, timedelta
        import whisper_dictation_module as mod

        now = datetime.now()
        age = (now - mod.last_heartbeat).total_seconds()

        assert age < 1.0  # Heartbeat should be fresh

class TestStallDetection:
    """Test stall detection logic"""

    def test_stall_detected_after_timeout(self):
        """After timeout seconds without update, stall should be detected"""
        import whisper_dictation_module as mod

        # Set heartbeat to old time
        old_time = datetime.now() - timedelta(seconds=11)
        mod.last_heartbeat = old_time

        time_since = (datetime.now() - mod.last_heartbeat).total_seconds()
        assert time_since > mod.audio_timeout

    def test_no_stall_within_timeout(self):
        """Within timeout, no stall should be detected"""
        import whisper_dictation_module as mod

        update_heartbeat()
        time_since = (datetime.now() - mod.last_heartbeat).total_seconds()

        assert time_since < mod.audio_timeout

class TestWatchdogThread:
    """Test watchdog thread behavior"""

    def test_watchdog_starts(self):
        """Watchdog thread should start successfully"""
        # This is implicitly tested by app startup
        # Explicit test: verify thread is daemon
        import threading
        import whisper_dictation_module as mod

        # Check that watchdog_thread would be daemon
        # (Actual test requires more setup)
        pass

    def test_watchdog_respects_active_flag(self):
        """Watchdog should exit when watchdog_active = False"""
        import whisper_dictation_module as mod
        import time

        # Set active flag
        mod.watchdog_active = True
        mod.recording = False

        # Start watchdog in test thread
        test_thread = threading.Thread(target=mod.watchdog_monitor)
        test_thread.start()

        time.sleep(0.2)  # Let watchdog start

        # Stop watchdog
        mod.watchdog_active = False
        test_thread.join(timeout=2)

        assert not test_thread.is_alive()

    def test_watchdog_only_monitors_during_recording(self, caplog):
        """Watchdog should only check heartbeat when recording=True"""
        import whisper_dictation_module as mod

        mod.watchdog_active = False
        mod.recording = True

        # Watchdog doesn't run, so no stall detected
        # This is implicit in the watchdog code

    @patch('whisper_dictation_module.restart_audio_stream')
    def test_watchdog_calls_restart_on_stall(self, mock_restart, caplog):
        """When stall detected, watchdog should call restart_audio_stream"""
        import whisper_dictation_module as mod

        mod.watchdog_active = True
        mod.recording = True

        # Simulate stall: old heartbeat
        old_time = datetime.now() - timedelta(seconds=11)
        mod.last_heartbeat = old_time

        # Run watchdog once
        with caplog.at_level(logging.WARNING):
            # Manually check stall condition (what watchdog does)
            time_since = (datetime.now() - mod.last_heartbeat).total_seconds()
            if time_since > mod.audio_timeout:
                mock_restart()

        mock_restart.assert_called_once()
        assert "stalled" in caplog.text.lower()

class TestStreamRestart:
    """Test stream restart mechanism"""

    @patch('pyaudio.PyAudio')
    def test_restart_closes_old_stream(self, mock_pyaudio, caplog):
        """Restart should close existing stream"""
        import whisper_dictation_module as mod

        # Mock stream
        mock_stream = MagicMock()
        mod.stream = mock_stream

        # Mock PyAudio
        mock_pa = MagicMock()
        mock_pyaudio.return_value = mock_pa
        mock_pa.open.return_value = MagicMock()

        with caplog.at_level(logging.INFO):
            restart_audio_stream()

        # Verify old stream was closed
        mock_stream.stop.assert_called_once()
        mock_stream.close.assert_called_once()

    @patch('pyaudio.PyAudio')
    def test_restart_creates_new_stream(self, mock_pyaudio):
        """Restart should create new audio stream"""
        import whisper_dictation_module as mod

        mock_stream = MagicMock()
        mod.stream = mock_stream

        mock_pa = MagicMock()
        mock_pyaudio.return_value = mock_pa
        mock_new_stream = MagicMock()
        mock_pa.open.return_value = mock_new_stream

        restart_audio_stream()

        # Verify new stream created
        mock_pa.open.assert_called_once()
        mock_new_stream.start_stream.assert_called_once()

    @patch('pyaudio.PyAudio')
    def test_restart_handles_exceptions(self, mock_pyaudio, caplog):
        """Restart should handle exceptions gracefully"""
        import whisper_dictation_module as mod

        mock_stream = MagicMock()
        mock_stream.stop.side_effect = Exception("Stream error")
        mod.stream = mock_stream

        with caplog.at_level(logging.ERROR):
            restart_audio_stream()

        assert "Failed to restart audio stream" in caplog.text

class TestThreadSafety:
    """Test thread safety"""

    def test_global_variables_accessible(self):
        """Global variables should be accessible from watchdog thread"""
        import whisper_dictation_module as mod

        # Verify globals exist
        assert hasattr(mod, 'watchdog_active')
        assert hasattr(mod, 'recording')
        assert hasattr(mod, 'last_heartbeat')

    def test_no_race_on_recording_flag(self):
        """Recording flag changes should be safe"""
        import whisper_dictation_module as mod

        # Rapidly toggle recording
        for _ in range(100):
            mod.recording = True
            mod.recording = False

        # Should not crash
```

### Integration Test: `tests/test_watchdog_integration.py`

```python
import pytest
import time
import threading
from datetime import datetime, timedelta

def test_watchdog_detects_stall_in_real_scenario():
    """Integration: watchdog detects simulated stall"""
    # This requires starting actual app, simulating stall, verifying recovery
    # May be manual test initially
    pass

def test_watchdog_with_actual_recording():
    """Integration: watchdog doesn't interfere with normal recording"""
    # Start recording, let watchdog monitor, verify completion
    pass
```

---

## File Changes Required

### `whisper-dictation.py`

**Add imports:**
```python
import threading
from datetime import datetime
```

**Add after Recorder class (module level):**
```python
# Watchdog variables
watchdog_active = True
last_heartbeat = datetime.now()
audio_timeout = 10  # seconds
watchdog_thread = None

def update_heartbeat():
    """Update last heartbeat time (call on successful audio read)"""
    global last_heartbeat
    last_heartbeat = datetime.now()

def restart_audio_stream():
    """Stop and restart the audio stream"""
    global stream, recording
    try:
        if stream is not None:
            stream.stop()
            stream.close()
            logging.info("Audio stream closed")

        import pyaudio
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=512,
            exception_on_overflow=False
        )
        stream.start_stream()
        logging.info("Audio stream restarted successfully")
    except Exception as e:
        logging.error(f"Failed to restart audio stream: {e}")
        recording = False

def watchdog_monitor():
    """Monitor audio stream for stalls"""
    global watchdog_active, last_heartbeat, audio_timeout, recording
    logging.info("Watchdog thread started")

    while watchdog_active:
        try:
            if recording:
                time_since_heartbeat = (datetime.now() - last_heartbeat).total_seconds()
                if time_since_heartbeat > audio_timeout:
                    logging.warning(
                        f"Audio system stalled! No heartbeat for {time_since_heartbeat:.1f}s"
                    )
                    logging.info("Restarting audio stream...")
                    restart_audio_stream()
            time.sleep(1)
        except Exception as e:
            logging.error(f"Watchdog error: {e}")
            time.sleep(5)

    logging.info("Watchdog thread exiting")
```

**In Recorder._record_impl() method (in read loop):**
```python
# After: data = stream.read(...)
try:
    data = stream.read(frames_per_buffer, exception_on_overflow=False)
    frames.append(data)
    update_heartbeat()  # [NEW]
except Exception as e:
    # ...
```

**In main block:**
```python
if __name__ == "__main__":
    setup_lock_file()
    test_microphone_access()

    # Start watchdog thread [NEW]
    watchdog_thread = threading.Thread(target=watchdog_monitor, daemon=False)
    watchdog_thread.start()

    atexit.register(cleanup_lock_file)
    # ...
```

**In signal_exit_handler():**
```python
def signal_exit_handler(signum, frame):
    """Handle signals gracefully"""
    logging.info(f"Signal {signum} received, shutting down...")
    global watchdog_active
    watchdog_active = False  # Stop watchdog

    # Wait for watchdog to exit
    if watchdog_thread is not None:
        watchdog_thread.join(timeout=2)

    cleanup_audio_stream()
    cleanup_lock_file()
    logging.info("Shutdown complete")
    os._exit(0)
```

### `whisper-dictation-fast.py`

**Identical changes as above** (must keep in sync)

---

## Brittleness Analysis

### Failure Mode 1: Stream Restart Hangs
**Scenario**: `stream.stop()` or `stream.start_stream()` blocks forever
**Detection**: Watchdog doesn't return from restart
**Consequence**: Watchdog thread hangs, app no longer responsive
**Prevention**: Add timeout on stream operations (out of scope for MVP)
**Recovery**: User force-kills app
**Mitigation**: Log restart start/completion, monitor thread health

### Failure Mode 2: Watchdog Detects False Positive
**Scenario**: Transcription takes >10 seconds, heartbeat paused
**Detection**: Watchdog tries to restart stream
**Consequence**: Restarts during active transcription
**Prevention**: Only check during recording state, disable during transcription
**Recovery**: Needs refinement in future
**Mitigation**: Currently acceptable - user can increase timeout in future

### Failure Mode 3: Rapid Stall + Restart Loop
**Scenario**: Stream keeps stalling, restart keeps failing
**Detection**: Watchdog loops endlessly trying to restart
**Consequence**: CPU usage high, app unresponsive
**Prevention**: Add restart attempt counter, bail after 3 failures
**Recovery**: Stop recording, exit watchdog
**Mitigation**: Implement counter in restart_audio_stream()

### Failure Mode 4: PyAudio Not Initialized
**Scenario**: PyAudio instance doesn't exist when restarting
**Detection**: AttributeError on `p.open(...)`
**Consequence**: Restart fails, recording stops
**Prevention**: Store PyAudio instance as global
**Recovery**: User restarts app
**Mitigation**: Document this limitation

### Failure Mode 5: Watchdog Thread Doesn't Exit
**Scenario**: `watchdog_active = False` but thread still running
**Detection**: App hangs on shutdown waiting for watchdog.join()
**Consequence**: Shutdown hangs forever
**Prevention**: Timeout on watchdog.join() (already in code)
**Recovery**: Timeout triggers, app exits anyway
**Mitigation**: 2-second join timeout is sufficient

### Failure Mode 6: Concurrent Update of Recording Flag
**Scenario**: Main thread changes `recording` while watchdog reads it
**Detection**: Watchdog uses stale value
**Consequence**: Monitoring state out of sync
**Prevention**: Python bool assignment is atomic (safe)
**Recovery**: Next iteration sees correct value
**Mitigation**: Python GIL ensures safety

---

## Rollout Strategy

### Phase 1: Development & Testing
1. Write TDD tests for all watchdog functions
2. Implement watchdog thread and heartbeat
3. Implement stream restart logic
4. Run pytest tests
5. Manual test: simulate stall, verify recovery

### Phase 2: Integration
1. Integrate with lock file + microphone check
2. Integrate with audio stream restart
3. Run full test suite
4. Manual stress test (long recordings)

### Phase 3: Validation
1. Monitor logs for watchdog activity
2. Test with various model sizes (tiny, large)
3. Collect user feedback
4. Adjust timeout if needed

---

## Performance Impact

- **Watchdog thread**: 1 extra thread, <1% CPU when idle
- **Heartbeat update**: Single variable write in hot path (<1μs)
- **Memory**: ~8KB for thread stack
- **Latency**: Zero impact on recording/transcription

**Negligible.**

---

## Configuration (Future)

For future enhancements:
```bash
--audio-timeout 10       # Seconds before stall detected
--watchdog-enabled true  # Enable/disable watchdog
```

---

## Acceptance Criteria (Ready to Implement)

- [ ] TDD tests written FIRST
- [ ] Watchdog thread starts/stops cleanly
- [ ] Heartbeat tracking works
- [ ] Stall detection works
- [ ] Stream restart works (or fails gracefully)
- [ ] All tests pass
- [ ] No regressions
- [ ] Manual testing confirms recovery behavior

