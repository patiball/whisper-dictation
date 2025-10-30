# Task: Manual Test Scenarios

**ID**: 13-05-03
**User Story**: [13-05-00] Lessons Learned Tests Suite
**Status**: ✅ **COMPLETED**
**Estimate**: 5 minutes

---

## What

Document manual test scenarios for features that require human verification or are difficult to automate.

---

## Manual Test Procedures

**Test 1: Lock File Behavior**

Scenario A - Normal Startup and Shutdown:
1. Start application
2. Verify lock file created with valid PID
3. Verify application enters listening state
4. Send shutdown signal (Ctrl+C)
5. Verify lock file removed cleanly
6. Expected: Clean startup and shutdown cycle

Scenario B - Second Instance Prevention:
1. Start first instance
2. Attempt to start second instance
3. Verify second instance exits with error message
4. Shutdown first instance
5. Verify new instance can now start
6. Expected: Only one instance runs at a time

Scenario C - Stale Lock Recovery:
1. Create lock file with invalid (very high) PID
2. Start application
3. Verify application starts successfully
4. Verify lock file updated with current PID
5. Expected: Application recovers from stale lock

**Test 2: Microphone Access**

Scenario A - Microphone Available:
1. Start application normally
2. Verify microphone check passes
3. Verify recording functionality works
4. Expected: Normal microphone operation

Scenario B - Permission Denied:
1. Revoke microphone permissions via system settings
2. Start application
3. Verify access test failure logged
4. Re-enable permissions and restart
5. Expected: Graceful handling of permission issues

**Test 3: Logging System**

Scenario A - Log File Creation:
1. Remove existing log file
2. Start application
3. Verify log file created in expected location
4. Verify startup message present
5. Expected: Log file created and populated

Scenario B - Log Level Filtering:
1. Test with DEBUG level (very verbose)
2. Test with WARNING level (errors/warnings only)
3. Verify appropriate filtering
4. Expected: Log levels control verbosity correctly

---

## Documentation Format

Manual tests documented in:
- `tests/manual/README.md` - Overview and instructions
- `tests/manual/lock_file_scenarios.md` - Lock file test cards
- `tests/manual/microphone_scenarios.md` - Microphone test cards
- `tests/manual/logging_scenarios.md` - Logging test cards

Each scenario includes:
- Setup requirements
- Step-by-step procedure
- Expected outcomes
- Pass/fail criteria

---

## Acceptance Criteria

- [ ] Manual test scenarios documented
- [ ] Test cards created for lock file, microphone, logging
- [ ] Setup requirements clearly specified
- [ ] Expected outcomes clearly defined
- [ ] Pass/fail criteria objective
- [ ] Tests executable by any developer

---

## Implementation Context (Not Part of Spec)

**Documentation Files:**
- `tests/manual/README.md`
- `tests/manual/lock_file_scenarios.md`
- `tests/manual/microphone_scenarios.md`
- `tests/manual/logging_scenarios.md`
