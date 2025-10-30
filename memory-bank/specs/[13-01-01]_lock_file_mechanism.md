# Task: Lock File Mechanism

**ID**: 13-01-01
**User Story**: [13-01-00] Lock File + Signal Handling
**Status**: ✅ **COMPLETED**
**Estimate**: 10 minutes

---

## What

Implement PID-based lock file mechanism to prevent multiple simultaneous instances from running.

---

## Design Approach

**Lock File Location:**
- User's home directory: `~/.whisper-dictation.lock`
- Hidden file (starts with dot)
- Contains single line: process ID (PID)

**Startup Logic:**
1. Check if lock file exists
2. If exists, read PID and validate with `psutil.pid_exists()`
3. If PID is alive, exit with error code 1 and message
4. If PID is dead, log warning about stale lock and remove file
5. Create new lock file with current PID
6. Continue with normal startup

**Shutdown Logic:**
1. Remove lock file during cleanup
2. Handle file not found gracefully (already cleaned up)
3. Log any errors but don't block shutdown

**Error Handling:**
- Invalid PID in lock file (not a number): treat as stale
- Empty lock file: treat as stale
- Permission errors: log and continue (user can manually clean)
- Missing file during cleanup: ignore (already cleaned)

---

## Failure Modes

**Concurrent File Access:**
- Multiple processes create lock file simultaneously
- Mitigation: Verify PID after write, check again if mismatch

**Permission Issues:**
- Lock file owned by different user
- Consequence: Stale lock persists but is non-fatal
- Recovery: Next startup with correct permissions resolves

**PID Reuse:**
- OS recycles old PID for unrelated process
- Mitigation: Add timestamp to lock file (future enhancement)
- Current: Accept small risk window

---

## Acceptance Criteria

- [ ] Lock file created in `~/.whisper-dictation.lock` on startup
- [ ] Lock file contains current process ID
- [ ] Second instance exits with code 1 when first is running
- [ ] Stale lock file (dead PID) is removed and logged
- [ ] Invalid lock file content is handled gracefully
- [ ] Lock file removed on normal shutdown
- [ ] Works with both whisper-dictation.py and whisper-dictation-fast.py

---

## Implementation Context (Not Part of Spec)

**Current Implementation:**
- Lock file path: `Path.home() / ".whisper-dictation.lock"`
- PID validation: `psutil.pid_exists(pid)`
- Functions: `setup_lock_file()`, `cleanup_lock_file()`
- Guard flag: `_cleanup_done` prevents duplicate cleanup
