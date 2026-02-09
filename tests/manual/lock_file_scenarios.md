# Lock File Manual Test Scenarios

## Test 1: Normal Startup and Shutdown

### Scenario A - Clean Startup and Shutdown Cycle

**Setup Requirements:**
- No existing whisper-dictation processes running
- Clean home directory (no `.whisper-dictation.lock` file)
- Terminal access

**Test Steps:**
1. Open terminal
2. Run `python whisper-dictation.py` (or `whisper-dictation-fast.py`)
3. Wait for application to enter listening state (status bar icon appears)
4. Check home directory for lock file: `ls -la ~/.whisper-dictation.lock`
5. Verify lock file contents: `cat ~/.whisper-dictation.lock`
6. Send shutdown signal: Press Ctrl+C in terminal
7. Verify lock file is removed: `ls -la ~/.whisper-dictation.lock`

**Expected Outcomes:**
- Lock file created during startup with valid PID
- Lock file contains JSON with pid, start_time, version fields
- Application enters normal listening state
- Lock file removed cleanly on shutdown
- No error messages during startup/shutdown

**Actual Results:**
- Lock file created: [ ] Yes [ ] No
- Lock file content valid: [ ] Yes [ ] No  
- Clean shutdown: [ ] Yes [ ] No
- Error messages: [ ] None [ ] Specify: ____________

**Pass/Fail Criteria:**
- **Pass**: All expected outcomes achieved
- **Fail**: Any expected outcome not achieved

---

## Test 2: Second Instance Prevention

### Scenario B - Multiple Instance Conflict

**Setup Requirements:**
- Terminal with multiple tabs/windows
- No existing whisper-dictation processes

**Test Steps:**
1. Open first terminal tab
2. Start first instance: `python whisper-dictation.py`
3. Wait for first instance to start (status bar icon appears)
4. Open second terminal tab
5. Attempt to start second instance: `python whisper-dictation.py`
6. Observe second instance behavior
7. Verify first instance still running
8. Shutdown first instance: Ctrl+C in first terminal
9. Try starting new instance in second terminal

**Expected Outcomes:**
- First instance starts successfully
- Second instance exits with error message about existing instance
- Error message is clear and informative
- First instance continues running normally
- After first instance shutdown, new instance can start

**Actual Results:**
- First instance starts: [ ] Yes [ ] No
- Second instance blocked: [ ] Yes [ ] No
- Error message clear: [ ] Yes [ ] No
- First instance stable: [ ] Yes [ ] No
- New instance after cleanup: [ ] Yes [ ] No

**Error Message Observed:**
__________________________________________________

**Pass/Fail Criteria:**
- **Pass**: All expected outcomes achieved
- **Fail**: Second instance starts or crashes first instance

---

## Test 3: Stale Lock Recovery

### Scenario C - Recovery from Crashed Instance

**Setup Requirements:**
- Terminal access
- Text editor
- Understanding of process IDs

**Test Steps:**
1. Ensure no whisper-dictation processes are running
2. Create fake lock file: `echo '{"pid": 99999, "start_time": 1234567890, "version": "1.0.0"}' > ~/.whisper-dictation.lock`
3. Verify lock file exists: `ls -la ~/.whisper-dictation.lock`
4. Attempt to start application: `python whisper-dictation.py`
5. Observe startup behavior
6. Check if lock file was updated: `cat ~/.whisper-dictation.lock`
7. Verify application is running (status bar icon)
8. Shutdown application normally

**Expected Outcomes:**
- Application detects stale lock (PID 99999 doesn't exist)
- Application removes stale lock and creates new one
- New lock file contains current process PID
- Application starts successfully
- No confusing error messages

**Actual Results:**
- Stale lock detected: [ ] Yes [ ] No
- New lock created: [ ] Yes [ ] No
- Current PID in lock: [ ] Yes [ ] No
- Application starts: [ ] Yes [ ] No
- Clear behavior: [ ] Yes [ ] No

**Pass/Fail Criteria:**
- **Pass**: Application recovers gracefully and starts
- **Fail**: Application fails to start or gives confusing error

---

## Test 4: Lock File Permissions

### Scenario D - Permission Handling

**Setup Requirements:**
- Terminal with sudo access
- Understanding of file permissions

**Test Steps:**
1. Create lock file with restricted permissions: `sudo touch ~/.whisper-dictation.lock && sudo chmod 000 ~/.whisper-dictation.lock`
2. Verify permissions: `ls -la ~/.whisper-dictation.lock`
3. Attempt to start application: `python whisper-dictation.py`
4. Observe error handling
5. Clean up: `sudo rm ~/.whisper-dictation.lock`
6. Try starting application again

**Expected Outcomes:**
- Application handles permission error gracefully
- Clear error message about lock file permissions
- Application doesn't crash or hang
- After cleanup, application starts normally

**Actual Results:**
- Permission error handled: [ ] Yes [ ] No
- Clear error message: [ ] Yes [ ] No
- No crash/hang: [ ] Yes [ ] No
- Starts after cleanup: [ ] Yes [ ] No

**Error Message Observed:**
__________________________________________________

**Pass/Fail Criteria:**
- **Pass**: Graceful handling with clear error message
- **Fail**: Crash, hang, or confusing error message

---

## Test 5: Concurrent Access Stress

### Scenario E - Race Condition Testing

**Setup Requirements:**
- Multiple terminal windows
- Script execution capability

**Test Steps:**
1. Create test script to start multiple instances rapidly:
```bash
#!/bin/bash
for i in {1..10}; do
    python whisper-dictation.py &
    sleep 0.1
done
wait
```
2. Make script executable: `chmod +x test_concurrent.sh`
3. Run script: `./test_concurrent.sh`
4. Monitor system processes: `ps aux | grep whisper-dictation`
5. Check lock file state: `cat ~/.whisper-dictation.lock`
6. Kill any remaining processes: `pkill -f whisper-dictation`
7. Clean up lock file: `rm ~/.whisper-dictation.lock`

**Expected Outcomes:**
- Only one instance successfully starts
- Other instances exit cleanly with appropriate error messages
- Lock file contains valid PID of running instance
- No zombie processes remain
- System remains stable

**Actual Results:**
- Single instance running: [ ] Yes [ ] No
- Others exit cleanly: [ ] Yes [ ] No
- Valid lock file: [ ] Yes [ ] No
- No zombie processes: [ ] Yes [ ] No
- System stable: [ ] Yes [ ] No

**Number of Instances Started:___________**
**Number Still Running:___________**

**Pass/Fail Criteria:**
- **Pass**: Exactly one instance running, others handled gracefully
- **Fail**: Multiple instances running or system instability

---

## Test Summary

**Tests Passed:** _____ / 5
**Tests Failed:** _____ / 5
**Critical Issues:** _________________________________

**Overall Assessment:**
[ ] All lock file mechanisms working correctly
[ ] Minor issues detected (non-critical)
[ ] Major issues detected (needs attention)
[ ] Critical failures (blocking release)

**Notes and Observations:**
__________________________________________________
__________________________________________________
__________________________________________________
