# Task: Stall Detection Logic

**ID**: 13-03-02
**User Story**: [13-03-00] Audio Stream Watchdog
**Complexity**: Medium
**Estimate**: 10 minutes

---

## What

Implement background monitoring loop that detects audio stalls by checking heartbeat age and triggers recovery.

---

## Design Approach

**Watchdog Thread:**
- Background daemon thread running continuously
- Monitors only when `recording` flag is True
- Checks heartbeat age every 1 second
- Exits when `watchdog_active` flag is False

**Stall Detection Logic:**
1. Calculate time since last heartbeat: `(now - last_heartbeat).total_seconds()`
2. Compare against timeout threshold (10 seconds)
3. If exceeded, log WARNING with elapsed time
4. Call stream restart function
5. Continue monitoring after restart

**Control Flags:**
- `watchdog_active`: Controls thread lifecycle (start/stop)
- `recording`: Only monitor during active recording
- Both flags checked each iteration

**Thread Lifecycle:**
- Started after other initialization
- Runs as daemon (doesn't prevent app exit)
- Stopped during shutdown with timeout join

---

## Failure Modes

**False Stall Detection:**
- Legitimate long operation pauses heartbeat
- Consequence: Unnecessary stream restart
- Mitigation: Disable monitoring during transcription (future)
- Current: Timeout tuned to avoid false positives

**Watchdog Doesn't Exit:**
- Shutdown flag ignored or not seen
- Consequence: App hangs waiting for thread
- Mitigation: Use timeout on thread join (2 seconds)

---

## Acceptance Criteria

- [ ] Watchdog thread implemented as daemon
- [ ] Monitors only when `recording == True`
- [ ] Checks heartbeat age every 1 second
- [ ] Detects stall when age > 10 seconds
- [ ] Logs WARNING with elapsed time
- [ ] Calls restart function on stall
- [ ] Exits when `watchdog_active == False`
- [ ] Thread started after initialization
- [ ] Clean shutdown with timeout

---

## Implementation Context (Not Part of Spec)

**Current Implementation:**
```python
def watchdog_monitor():
    global last_heartbeat, watchdog_active, recording
    while watchdog_active:
        if recording:
            time_since = (datetime.now() - last_heartbeat).total_seconds()
            if time_since > audio_timeout:
                logging.warning(f"Audio stalled! No heartbeat for {time_since:.1f}s")
                restart_audio_stream()
        time.sleep(1)
```

Thread start:
```python
watchdog_thread = threading.Thread(target=watchdog_monitor, daemon=True)
watchdog_thread.start()
```
