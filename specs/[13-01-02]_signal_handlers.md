# Task: Signal Handlers for Graceful Shutdown

**ID**: 13-01-02
**User Story**: [13-01-00] Lock File + Signal Handling
**Complexity**: Medium
**Estimate**: 8 minutes

---

## What

Register signal handlers to ensure graceful cleanup when application receives termination signals (Ctrl+C, SIGTERM).

---

## Design Approach

**Signal Registration:**
- Register handlers for SIGINT (Ctrl+C) and SIGTERM
- Register during main initialization before event loop starts
- Use `signal.signal()` for handler registration

**Handler Implementation:**
- Log signal reception with signal number
- Set cleanup flag to prevent reentrant execution
- Stop monitoring threads (watchdog, etc.)
- Stop recording operations
- Close audio stream
- Remove lock file
- Log shutdown complete
- Exit with code 0 (success)

**Cleanup Order:**
1. Stop active operations (recording, monitoring)
2. Release audio resources (close stream)
3. Release file resources (remove lock file)
4. Log final message
5. Exit cleanly

**Guard Against Duplicate Cleanup:**
- Use `cleanup_in_progress` flag
- Check flag at handler entry, skip if already set
- Set flag before cleanup operations
- Prevents issues if multiple signals received

---

## Failure Modes

**Signal During Critical Cleanup:**
- User sends multiple Ctrl+C during shutdown
- Mitigation: Guard flag prevents reentrant execution
- Handler checks flag before proceeding

**Cleanup Conflicts (atexit vs signal):**
- Both atexit and signal handler attempt cleanup
- Consequence: Second cleanup on non-existent files
- Mitigation: Guard flag ensures cleanup runs once
- Operations are idempotent (removing missing file is safe)

**Hanging in Cleanup:**
- Process hangs in system call during cleanup
- Risk: Signal delivery blocked
- Mitigation: Keep cleanup operations simple and fast
- Document force-kill procedures for users

---

## Acceptance Criteria

- [ ] Signal handler registered for SIGINT (Ctrl+C)
- [ ] Signal handler registered for SIGTERM
- [ ] Handler logs signal reception before cleanup
- [ ] Recording operations stopped cleanly
- [ ] Audio stream closed without errors
- [ ] Lock file removed during shutdown
- [ ] No processes left behind after shutdown
- [ ] Exit code 0 on successful shutdown
- [ ] Guard flag prevents duplicate cleanup
- [ ] Compatible with StatusBarApp (rumps) shutdown

---

## Implementation Context (Not Part of Spec)

**Current Implementation:**
- Signal registration: `signal.signal(signal.SIGINT, signal_handler)`
- Cleanup registration: `atexit.register(cleanup_handler)`
- Guard flag: `cleanup_in_progress = False`
- Cleanup in signal handler: `os._exit(0)` for immediate termination
