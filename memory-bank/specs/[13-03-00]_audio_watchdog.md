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
- Audio stream can occasionally stall (stop providing data)
- When stalled, application appears to work but no audio is recorded
- User has no feedback that recording failed
- Only option is to manually kill and restart app

### Why This Matters
- **Long-Running Stability**: Background app should handle transient issues
- **Transparent Recovery**: User shouldn't notice brief hiccups
- **Better Than Crash**: Recover gracefully instead of hanging
- **Production Quality**: Professional apps monitor their I/O streams

---

## What We're Building

Background watchdog thread that:
1. Monitors audio stream "heartbeat" (data arrival)
2. Detects stalls (no data for >10 seconds)
3. Automatically restarts the stream
4. Logs all watchdog events

Key design: Non-blocking, doesn't interfere with recording, graceful recovery.

---

## Key Assumptions

**A1: Heartbeat Update is Reliable**
- Audio read operations reliably update heartbeat
- Risk: Heartbeat not updated causes false stall detection
- Mitigation: Add heartbeat update in correct location only

**A2: 10 Second Timeout is Reasonable**
- Long enough for slow transcriptions, short enough for quick detection
- Risk: Too short = false positives; Too long = late detection
- Mitigation: Make timeout configurable (future)

**A3: Stream Restart is Safe**
- Calling stream.stop() + stream.start() is safe
- Risk: Restart fails causing infinite loop
- Mitigation: Add restart attempt counter, bail out after 3 failures

**A4: Recording Flag is Atomic**
- Global recording flag is safely accessible
- Risk: Race condition between watchdog and main thread
- Mitigation: Python bool assignment is atomic

---

## Acceptance Criteria

### Watchdog Functionality
- [ ] **W1** Watchdog thread starts with application
- [ ] **W2** Watchdog monitors only during active recording
- [ ] **W3** Heartbeat updated on every successful audio read
- [ ] **W4** Stall detected if heartbeat >10 seconds old
- [ ] **W5** Stream restart initiated when stall detected
- [ ] **W6** Watchdog continues monitoring after restart
- [ ] **W7** Watchdog exits cleanly on shutdown

### Logging
- [ ] **L1** Watchdog start: INFO "Watchdog thread started"
- [ ] **L2** Stall detection: WARNING "Audio system stalled! No heartbeat for X.Xs"
- [ ] **L3** Restart attempt: INFO "Restarting audio stream..."
- [ ] **L4** Restart success: INFO "Audio stream restarted successfully"

### No Regressions
- [ ] **R1** Recording still works
- [ ] **R2** Performance unaffected
- [ ] **R3** Works with both implementations

---

## Behavior Examples

### Example 1: Normal Recording (No Stall)
```
[14:23:45.124] Watchdog thread started
[14:23:48.000] Transcribing...
[14:23:51.000] Transcription complete
```

### Example 2: Audio Stall Detected & Recovered
```
[14:23:45.124] Watchdog thread started
[14:23:58.000] WARNING: Audio system stalled! No heartbeat for 10.0s
[14:23:58.001] INFO: Restarting audio stream...
[14:23:58.050] INFO: Audio stream restarted successfully
[14:24:00.000] Transcribing...
```

User doesn't notice stall, recording continues.

---

## Related Tasks

- [ ] [13-03-01] Heartbeat Tracking
- [ ] [13-03-02] Stall Detection
- [ ] [13-03-03] Stream Recovery
- [ ] [13-03-04] Watchdog Tests

---

## Implementation Context (Not Part of Spec)

**Current Implementation:**
- Watchdog thread: Runs continuously, checks every 1 second
- Heartbeat: `last_heartbeat` timestamp updated after audio read
- Timeout: `audio_timeout = 10` seconds
- Stream restart: Stop → Close → Reinitialize → Start
- Thread management: `watchdog_active` flag, `join(timeout=2)` on shutdown

**Note**: This implementation context documents current choices which may evolve. The specification above describes stable requirements independent of these implementation details.
