# Logging System Manual Test Scenarios

## Test 1: Log File Creation

### Scenario A - Log File Initialization

**Setup Requirements:**
- Clean home directory (no existing log files)
- Terminal access
- Text editor for log inspection

**Test Steps:**
1. Verify no existing log file: `ls -la ~/.whisper-dictation.log`
2. Open terminal
3. Run application: `python whisper-dictation.py`
4. Wait for application to start (status bar icon appears)
5. Check if log file was created: `ls -la ~/.whisper-dictation.log`
6. Inspect log file contents: `cat ~/.whisper-dictation.log`
7. Verify startup messages are present
8. Shutdown application: Ctrl+C
9. Check final log file contents

**Expected Outcomes:**
- Log file created in home directory
- File has appropriate permissions (readable by user)
- Contains startup timestamp and initialization messages
- Contains shutdown message
- No sensitive information logged
- File size is reasonable (not excessively large)

**Actual Results:**
- Log file created: [ ] Yes [ ] No
- File permissions correct: [ ] Yes [ ] No
- Startup messages present: [ ] Yes [ ] No
- Shutdown message present: [ ] Yes [ ] No
- No sensitive data: [ ] Yes [ ] No
- Reasonable file size: [ ] Yes [ ] No

**Log File Size:** _____ KB
**Pass/Fail Criteria:**
- **Pass**: All expected outcomes achieved
- **Fail**: Any expected outcome not achieved

---

## Test 2: Log Level Filtering

### Scenario B - Log Level Configuration

**Setup Requirements:**
- Terminal access
- Understanding of log levels (DEBUG, INFO, WARNING, ERROR)

**Test Steps:**
1. Remove existing log file: `rm ~/.whisper-dictation.log`
2. Start application with DEBUG logging (if configurable)
3. Perform basic recording operation
4. Shutdown application
5. Inspect log file: `cat ~/.whisper-dictation.log`
6. Count messages by level: `grep -c "DEBUG" ~/.whisper-dictation.log`
7. Repeat with INFO level logging
8. Compare verbosity between levels

**Expected Outcomes:**
- DEBUG level shows detailed messages including heartbeat updates
- INFO level shows essential messages without excessive detail
- WARNING level shows only warnings and errors
- ERROR level shows only critical errors
- Level filtering works correctly
- Performance impact is minimal

**Actual Results:**
- DEBUG filtering works: [ ] Yes [ ] No
- INFO filtering works: [ ] Yes [ ] No
- WARNING filtering works: [ ] Yes [ ] No
- ERROR filtering works: [ ] Yes [ ] No
- Performance acceptable: [ ] Yes [ ] No

**Message Counts:**
- DEBUG: _____ messages
- INFO: _____ messages
- WARNING: _____ messages
- ERROR: _____ messages

**Pass/Fail Criteria:**
- **Pass**: Log level filtering works as expected
- **Fail**: Filtering not working or causing issues

---

## Test 3: Log Rotation

### Scenario C - Log File Size Management

**Setup Requirements:**
- Terminal access
- Ability to generate large amounts of log data

**Test Steps:**
1. Configure log rotation to small size for testing (if possible)
2. Remove existing log files: `rm ~/.whisper-dictation.log*`
3. Start application: `python whisper-dictation.py`
4. Generate extensive logging by performing many operations:
   - Start/stop recording multiple times
   - Trigger various error conditions
   - Let application run for extended period
5. Monitor log file growth: `watch -n 1 'ls -la ~/.whisper-dictation.log*'`
6. Observe rotation behavior when size limit reached
7. Verify backup files are created
8. Check that old backups are cleaned up

**Expected Outcomes:**
- Log rotation occurs at configured size limit
- Backup files created with .1, .2, .3 extensions
- Number of backup files limited by configuration
- Oldest backups deleted when limit exceeded
- Current log file resets after rotation
- No data loss during rotation

**Actual Results:**
- Rotation occurs: [ ] Yes [ ] No
- Backups created: [ ] Yes [ ] No
- Backup limit enforced: [ ] Yes [ ] No
- Old backups deleted: [ ] Yes [ ] No
- No data loss: [ ] Yes [ ] No

**Rotation Size Limit:** _____ MB
**Max Backup Files:** _____
**Pass/Fail Criteria:**
- **Pass**: Log rotation works correctly
- **Fail**: Rotation not working or causing data loss

---

## Test 4: Event Logging

### Scenario D - Comprehensive Event Coverage

**Setup Requirements:**
- Terminal access
- Application with all features functional

**Test Steps:**
1. Clear log file: `rm ~/.whisper-dictation.log`
2. Start application: `python whisper-dictation.py`
3. Perform complete application lifecycle:
   - Startup and initialization
   - Microphone check
   - Recording session
   - Transcription
   - Error conditions (if possible)
   - Shutdown
4. Inspect log file: `cat ~/.whisper-dictation.log`
5. Verify all major events are logged
6. Check log message clarity and usefulness
7. Verify timestamps are present and accurate

**Expected Outcomes:**
- All major application events logged
- Log messages are clear and informative
- Timestamps present and in chronological order
- Error conditions logged with appropriate severity
- Performance metrics included (if applicable)
- No gaps in event coverage

**Actual Results:**
- All events logged: [ ] Yes [ ] No
- Messages clear: [ ] Yes [ ] No
- Timestamps accurate: [ ] Yes [ ] No
- Error severity correct: [ ] Yes [ ] No
- No gaps in coverage: [ ] Yes [ ] No

**Missing Events:**
__________________________________________________

**Pass/Fail Criteria:**
- **Pass**: Comprehensive event logging
- **Fail**: Missing events or poor log quality

---

## Test 5: Error Logging

### Scenario E - Error Condition Logging

**Setup Requirements:**
- Terminal access
- Ability to trigger error conditions

**Test Steps:**
1. Clear log file: `rm ~/.whisper-dictation.log`
2. Start application: `python whisper-dictation.py`
3. Trigger various error conditions:
   - Microphone permission denied
   - No audio devices available
   - Network issues (if applicable)
   - File system permission errors
   - Invalid configuration
4. Inspect log file for error messages: `grep "ERROR\|WARNING" ~/.whisper-dictation.log`
5. Verify error messages are informative
6. Check that errors include context and stack traces (if appropriate)
7. Verify application continues running after non-critical errors

**Expected Outcomes:**
- All error conditions logged appropriately
- Error messages include useful context
- Critical errors include stack traces
- Non-critical errors logged as warnings
- Application doesn't crash on logged errors
- Error severity levels are appropriate

**Actual Results:**
- Errors logged: [ ] Yes [ ] No
- Messages informative: [ ] Yes [ ] No
- Stack traces present: [ ] Yes [ ] No
- Severity appropriate: [ ] Yes [ ] No
- Application stable: [ ] Yes [ ] No

**Error Messages Found:**
__________________________________________________

**Pass/Fail Criteria:**
- **Pass**: Error logging comprehensive and useful
- **Fail**: Poor error logging or missing error information

---

## Test 6: Performance Impact

### Scenario F - Logging Performance Test

**Setup Requirements:**
- Terminal access
- Timing tools
- Application with heavy logging

**Test Steps:**
1. Measure application startup time without logging: `time python whisper-dictation.py`
2. Measure application startup time with normal logging
3. Measure application startup time with DEBUG logging
4. Generate high-frequency logging (rapid recording sessions)
5. Monitor system resources during heavy logging
6. Check if logging causes noticeable delays
7. Verify log file I/O doesn't block application

**Expected Outcomes:**
- Logging adds minimal startup overhead (<100ms)
- DEBUG logging doesn't significantly impact performance
- Heavy logging doesn't cause UI delays
- Log file I/O is asynchronous or non-blocking
- Memory usage remains reasonable during heavy logging
- Application remains responsive during logging

**Actual Results:**
- Startup overhead <100ms: [ ] Yes [ ] No
- DEBUG performance acceptable: [ ] Yes [ ] No
- No UI delays: [ ] Yes [ ] No
- Asynchronous I/O: [ ] Yes [ ] No
- Memory usage reasonable: [ ] Yes [ ] No

**Timing Measurements:**
- No logging: _____ ms
- Normal logging: _____ ms
- DEBUG logging: _____ ms

**Pass/Fail Criteria:**
- **Pass**: Logging performance impact is minimal
- **Fail**: Logging causes significant performance issues

---

## Test Summary

**Tests Passed:** _____ / 6
**Tests Failed:** _____ / 6
**Critical Issues:** _________________________________

**Logging Quality Assessment:**
[ ] Excellent - Comprehensive, clear, performant logging
[ ] Good - Minor issues with verbosity or performance
[ ] Fair - Basic logging works, some gaps or performance issues
[ ] Poor - Significant logging problems

**Performance Impact:**
[ ] Minimal - No noticeable impact
[ ] Minor - Small but acceptable impact
[ ] Significant - Noticeable delays
[ ] Severe - Major performance degradation

**Overall Assessment:**
[ ] All logging functionality working correctly
[ ] Minor issues detected (non-critical)
[ ] Major issues detected (needs attention)
[ ] Critical failures (blocking release)

**Notes and Observations:**
__________________________________________________
__________________________________________________
__________________________________________________
