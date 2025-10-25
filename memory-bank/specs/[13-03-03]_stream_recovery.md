# Task: Stream Recovery Mechanism

**ID**: 13-03-03
**User Story**: [13-03-00] Audio Stream Watchdog
**Complexity**: Medium
**Estimate**: 10 minutes

---

## What

Implement stream restart logic that safely stops, closes, and reinitializes audio stream for recovery from stalls.

---

## Design Approach

**Restart Sequence:**
1. Log restart attempt at INFO level
2. Stop current audio stream
3. Close stream and release resources
4. Reinitialize stream with same parameters
5. Start new stream
6. Log success or failure
7. Reset heartbeat to current time

**Error Handling:**
- Wrap entire sequence in try/except
- Log ERROR if restart fails
- Don't crash app on failure
- Allow watchdog to retry (with backoff - future)

**Restart Parameters:**
- Use same configuration as original stream
- Same sample rate, channels, format
- Same frames_per_buffer setting
- Preserve all audio settings

**Thread Safety:**
- Access to stream object must be synchronized
- Consider lock if concurrent access possible
- Current: Recording flag prevents conflicts

---

## Failure Modes

**Stream Restart Hangs:**
- Hardware or driver issue blocks restart
- Consequence: Watchdog thread hangs
- Mitigation: Timeout on operations (future enhancement)
- Current: Accept rare edge case

**Persistent Stall Loop:**
- Stream repeatedly stalls and restart fails
- Consequence: High CPU usage, poor responsiveness
- Mitigation: Limit restart attempts (3 max, future)
- Current: Log errors for diagnosis

**Stream Initialization Failure:**
- Audio subsystem unavailable during restart
- Consequence: Restart fails, recording cannot continue
- Mitigation: Clear error logging
- Recovery: User must restart application

---

## Acceptance Criteria

- [ ] `restart_audio_stream()` function implemented
- [ ] Stops current stream safely
- [ ] Closes and releases resources
- [ ] Reinitializes with same parameters
- [ ] Starts new stream
- [ ] Logs restart attempt and result
- [ ] Resets heartbeat after successful restart
- [ ] Error handling prevents crashes
- [ ] Works with existing audio setup

---

## Implementation Context (Not Part of Spec)

**Current Implementation:**
```python
def restart_audio_stream():
    global stream, last_heartbeat
    try:
        logging.info("Restarting audio stream...")
        stream.stop_stream()
        stream.close()

        # Reinitialize with same params
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=FRAMES_PER_BUFFER
        )
        stream.start_stream()

        last_heartbeat = datetime.now()
        logging.info("Audio stream restarted successfully")
    except Exception as e:
        logging.error(f"Failed to restart audio stream: {e}")
```
