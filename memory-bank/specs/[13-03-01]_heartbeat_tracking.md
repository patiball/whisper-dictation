# Task: Heartbeat Tracking Mechanism

**ID**: 13-03-01
**User Story**: [13-03-00] Audio Stream Watchdog
**Status**: ✅ **COMPLETED**
**Estimate**: 7 minutes

---

## What

Implement timestamp tracking mechanism that updates on every successful audio read to enable stall detection.

---

## Design Approach

**Heartbeat Variable:**
- Global variable `last_heartbeat` storing datetime timestamp
- Initialized to current time on module load
- Updated after each successful audio frame read

**Update Mechanism:**
- `update_heartbeat()` function sets `last_heartbeat = datetime.now()`
- Called in audio read loop after successful frame read
- Minimal overhead (single timestamp update)
- No blocking operations

**Integration Point:**
- Called within `Recorder._record_impl()` after `stream.read()`
- Only updated during active recording
- Not updated during transcription or idle periods

---

## Failure Modes

**Heartbeat Not Updated:**
- Heartbeat update missed in code
- Consequence: False stall detection
- Mitigation: Add update in single, correct location

**Clock Skew:**
- System clock changes during operation
- Consequence: Incorrect stall detection
- Mitigation: Accept rare edge case (clock changes are uncommon)

---

## Acceptance Criteria

- [ ] Global variable `last_heartbeat` defined
- [ ] Initialized to current time on module load
- [ ] `update_heartbeat()` function implemented
- [ ] Called after every successful audio read
- [ ] Timestamp is accessible to watchdog thread
- [ ] No performance impact (<1μs per update)

---

## Implementation Context (Not Part of Spec)

**Current Implementation:**
```python
from datetime import datetime

last_heartbeat = datetime.now()

def update_heartbeat():
    global last_heartbeat
    last_heartbeat = datetime.now()
```

Called in recording loop:
```python
data = stream.read(num_frames)
update_heartbeat()  # After successful read
```
