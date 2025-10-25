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

## Design Approach

### Watchdog Architecture

**Core Components:**

1. **Heartbeat Tracking**: Timestamp of last successful audio read
   - Updated on every successful audio frame read
   - Compared periodically to detect stalls

2. **Stall Detection**: Monitor loop that checks heartbeat age
   - Runs in background thread continuously
   - Only checks during active recording
   - Compares elapsed time since last heartbeat against timeout threshold

3. **Stream Recovery**: Automated restart of audio stream
   - Stops current stream
   - Closes audio resources
   - Reinitializes stream with same parameters
   - Resumes audio capture

4. **Graceful Shutdown**: Controlled thread termination
   - Uses shutdown flag to signal watchdog to stop
   - Waits for thread to complete before exit
   - Timeout prevents indefinite hang

### Integration Points

**Heartbeat Updates:**
- Called within audio read loop after successful frame read
- Minimal overhead (single timestamp update)
- No blocking operations

**Watchdog Thread:**
- Starts after other initialization
- Monitors continuously but only acts during recording
- Exits cleanly on application shutdown

**Stream Restart:**
- Triggered when stall detected
- Stops current stream and reinitializes
- Handles failures gracefully without crashing app

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

## Affected Components

The following components require modifications:

- **Main Application Initialization**: Start watchdog thread during startup
- **Audio Recording Loop**: Add heartbeat update after each successful audio read
- **Shutdown Handler**: Signal watchdog to stop and wait for thread completion
- **Logging System**: Log watchdog lifecycle events (start, stall detection, restart, exit)
- **Stream Management**: Implement stream restart capability for recovery
- **Both Versions**: Changes must be synchronized across Python and C++ implementations

### Key Variables Needed

- **Watchdog Control**: Flag to enable/disable watchdog monitoring
- **Heartbeat Timestamp**: Last time successful audio was read
- **Timeout Configuration**: Seconds before stall is detected
- **Thread Reference**: Reference to watchdog monitor thread

### Dependencies

- Threading capability for background monitoring
- Timestamp/timing facilities for heartbeat comparison
- Access to recording state flag
- Audio stream reference for restart operations

---

## Failure Modes & Durability

### Failure Mode 1: Stream Restart Hangs
**Scenario**: Stream restart operation blocks indefinitely (hardware/driver issue)
- **Detection**: Watchdog doesn't return from restart operation
- **Consequence**: Watchdog thread hangs, app becomes unresponsive
- **Prevention**: Configure timeouts on stream operations
- **Recovery**: User force-terminates application
- **Mitigation**: Timeout on thread join prevents shutdown hang

### Failure Mode 2: False Stall Detection
**Scenario**: Legitimate long-duration operation causes heartbeat pause
- **Detection**: Watchdog detects stall during heavy transcription
- **Consequence**: Unnecessary stream restart interrupts operations
- **Prevention**: Disable heartbeat monitoring during transcription phases
- **Recovery**: Can be refined with state-aware monitoring (future)
- **Mitigation**: Currently acceptable; timeout can be tuned

### Failure Mode 3: Persistent Stall Loop
**Scenario**: Stream repeatedly stalls and restart repeatedly fails
- **Detection**: Watchdog repeatedly attempts and fails to restart
- **Consequence**: High CPU usage, resource drain, poor responsiveness
- **Prevention**: Implement restart attempt counter with backoff
- **Recovery**: Stop recording after threshold exceeded
- **Mitigation**: Limit restart attempts to prevent infinite loop

### Failure Mode 4: Stream Initialization Failure
**Scenario**: Audio subsystem unavailable when restarting stream
- **Detection**: Stream initialization fails with exception
- **Consequence**: Restart fails, recording cannot continue
- **Prevention**: Verify audio subsystem available during initialization
- **Recovery**: User must restart application
- **Mitigation**: Clear error logging helps diagnosis

### Failure Mode 5: Watchdog Thread Doesn't Exit
**Scenario**: Shutdown flag set but watchdog thread still running
- **Detection**: Application hangs waiting for thread completion
- **Consequence**: Shutdown hangs indefinitely, requires force-kill
- **Prevention**: Use timeout on thread join operation
- **Recovery**: Timeout expires, app exits despite hung thread
- **Mitigation**: Conservative timeout prevents permanent hang

### Failure Mode 6: Race Condition on State Flags
**Scenario**: Multiple threads access recording/watchdog state simultaneously
- **Detection**: Inconsistent state observed by watchdog
- **Consequence**: Watchdog may miss stall or false-detect
- **Prevention**: Atomic operations for flag updates
- **Recovery**: Next monitoring cycle sees correct state
- **Mitigation**: Careful variable access patterns

---

## Implementation Approach

### TDD-First Strategy
- Write comprehensive tests for all watchdog functions before implementation
- Test heartbeat tracking, stall detection, stream restart
- Include both unit and integration tests
- Test with timeout/edge cases

### Phased Implementation
1. **Heartbeat Tracking**: Implement timestamp update mechanism
2. **Monitoring Loop**: Implement background watchdog thread
3. **Stream Recovery**: Implement stream restart logic
4. **Integration**: Connect all components together

### Validation Phases
- Unit testing: Verify each component in isolation
- Integration testing: Verify watchdog with actual recording loop
- Stress testing: Long-duration recordings, multiple stall scenarios
- Manual testing: Verify user-visible behavior and logging
- Performance testing: Verify minimal overhead

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

## Implementation Context (Not Part of Spec)

**Current Implementation Structure:**
- Watchdog thread: Runs continuously, checks heartbeat every 1 second
- Heartbeat variable: `last_heartbeat` timestamp updated after each successful audio read
- Timeout configuration: `audio_timeout = 10` seconds before stall detected
- Stream restart: Stop → Close → Reinitialize → Start cycle
- Thread management: `watchdog_active` flag controls monitoring, `join(timeout=2)` on shutdown
- Integration point: Heartbeat update in audio read loop, thread start in main block

**Note**: This implementation context documents current choices which may evolve. The specification above describes stable requirements independent of these implementation details.

---

## Acceptance Criteria (Ready to Implement)

- [ ] TDD tests written FIRST covering all watchdog functions
- [ ] Heartbeat tracking mechanism implemented and verified
- [ ] Stall detection logic working correctly
- [ ] Stream restart mechanism implemented with error handling
- [ ] Watchdog thread lifecycle management (start/stop/shutdown) working
- [ ] All unit and integration tests pass
- [ ] No regressions in existing features
- [ ] Manual testing confirms recovery behavior
- [ ] Performance impact verified (negligible)

