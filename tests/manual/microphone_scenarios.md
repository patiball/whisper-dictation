# Microphone Access Manual Test Scenarios

## Test 1: Microphone Available

### Scenario A - Normal Microphone Operation

**Setup Requirements:**
- macOS system with built-in microphone
- Microphone permissions granted to Terminal/Python
- Quiet environment for testing

**Test Steps:**
1. Open System Preferences > Security & Privacy > Privacy > Microphone
2. Ensure Terminal (or your terminal app) has microphone permission
3. Open terminal
4. Run application: `python whisper-dictation.py`
5. Observe startup messages for microphone check
6. Trigger recording (keyboard shortcut or menu)
7. Speak for 5-10 seconds
8. Observe transcription output
9. Check log file for microphone-related messages: `tail -f ~/.whisper-dictation.log`

**Expected Outcomes:**
- Microphone check passes during startup
- Recording starts successfully when triggered
- Audio levels indicate microphone is working
- Transcription produces text output
- No microphone-related error messages
- Log shows successful microphone initialization

**Actual Results:**
- Microphone check passes: [ ] Yes [ ] No
- Recording starts: [ ] Yes [ ] No
- Audio detected: [ ] Yes [ ] No
- Transcription works: [ ] Yes [ ] No
- No errors: [ ] Yes [ ] No

**Pass/Fail Criteria:**
- **Pass**: All microphone operations work correctly
- **Fail**: Any microphone operation fails or shows errors

---

## Test 2: Permission Denied

### Scenario B - Microphone Permission Revoked

**Setup Requirements:**
- macOS system with microphone access controls
- Terminal app without microphone permission

**Test Steps:**
1. Open System Preferences > Security & Privacy > Privacy > Microphone
2. Remove microphone permission from Terminal (uncheck the box)
3. Open terminal
4. Run application: `python whisper-dictation.py`
5. Observe startup behavior and error messages
6. Check log file: `tail -f ~/.whisper-dictation.log`
7. Restore microphone permission in System Preferences
8. Restart application and verify it works

**Expected Outcomes:**
- Application detects missing microphone permission
- Clear error message about permission requirement
- Application either exits gracefully or continues with warning
- Log file records permission issue
- After permission restore, application works normally

**Actual Results:**
- Permission detected missing: [ ] Yes [ ] No
- Clear error message: [ ] Yes [ ] No
- Graceful handling: [ ] Yes [ ] No
- Logged correctly: [ ] Yes [ ] No
- Works after restore: [ ] Yes [ ] No

**Error Message Observed:**
__________________________________________________

**Pass/Fail Criteria:**
- **Pass**: Clear error handling, no crashes
- **Fail**: Application crashes or gives confusing error

---

## Test 3: No Microphone Device

### Scenario C - No Audio Input Devices

**Setup Requirements:**
- macOS system (virtual machine or without microphone)
- Terminal access

**Test Steps:**
1. Disconnect any external microphones
2. If on virtual machine, ensure no audio input devices are configured
3. Open terminal
4. Run application: `python whisper-dictation.py`
5. Observe startup messages
6. Check log file for device detection messages
7. Try to trigger recording if application allows
8. Observe behavior when recording attempted

**Expected Outcomes:**
- Application detects no available input devices
- Clear message about lack of microphone devices
- Application either exits or continues with clear limitation
- Recording attempts fail gracefully with informative message
- No crashes or hangs

**Actual Results:**
- No devices detected: [ ] Yes [ ] No
- Clear message: [ ] Yes [ ] No
- Graceful handling: [ ] Yes [ ] No
- Recording fails cleanly: [ ] Yes [ ] No
- No crashes: [ ] Yes [ ] No

**Pass/Fail Criteria:**
- **Pass**: Appropriate handling of missing hardware
- **Fail**: Crash or confusing behavior

---

## Test 4: External Microphone

### Scenario D - External USB Microphone

**Setup Requirements:**
- USB microphone or external audio device
- macOS system with USB ports

**Test Steps:**
1. Connect external microphone to USB port
2. Wait for system to recognize the device
3. Open System Preferences > Sound > Input
4. Verify external microphone appears and is selected
5. Open terminal
6. Run application: `python whisper-dictation.py`
7. Observe microphone detection messages
8. Trigger recording and speak into external microphone
9. Verify audio is captured from external device
10. Check transcription quality

**Expected Outcomes:**
- Application detects external microphone
- Recording uses external microphone (not built-in)
- Audio quality is good with external device
- Transcription works correctly
- Log file shows external device selection

**Actual Results:**
- External mic detected: [ ] Yes [ ] No
- Uses external device: [ ] Yes [ ] No
- Good audio quality: [ ] Yes [ ] No
- Transcription works: [ ] Yes [ ] No
- Logged correctly: [ ] Yes [ ] No

**Pass/Fail Criteria:**
- **Pass**: External microphone works correctly
- **Fail**: External microphone not used or poor quality

---

## Test 5: Microphone Hotplug

### Scenario E - Microphone Connect/Disconnect During Operation

**Setup Requirements:**
- USB microphone
- Application running

**Test Steps:**
1. Start application with built-in microphone: `python whisper-dictation.py`
2. Verify application is running normally
3. Connect external microphone while application is running
4. Observe application behavior (any messages, status changes)
5. Try recording with external microphone
6. Disconnect external microphone while application is running
7. Try recording with built-in microphone
8. Check log file for device change messages

**Expected Outcomes:**
- Application handles device connection/disconnection gracefully
- Either automatically switches devices or provides clear guidance
- No crashes or hangs during device changes
- Recording works with available device
- Log file records device changes

**Actual Results:**
- Handles connect: [ ] Yes [ ] No
- Handles disconnect: [ ] Yes [ ] No
- No crashes: [ ] Yes [ ] No
- Recording works: [ ] Yes [ ] No
- Logged changes: [ ] Yes [ ] No

**Pass/Fail Criteria:**
- **Pass**: Graceful handling of device changes
- **Fail**: Crash, hang, or device not usable after change

---

## Test 6: Microphone Quality Test

### Scenario F - Audio Quality Assessment

**Setup Requirements:**
- Quiet environment
- Good quality microphone
- Text to read for testing

**Test Steps:**
1. Prepare test text (e.g., "The quick brown fox jumps over the lazy dog. 1234567890.")
2. Set up microphone in optimal position
3. Start application: `python whisper-dictation.py`
4. Record the test text clearly
5. Compare transcription with original text
6. Note any accuracy issues
7. Test with different speaking volumes (soft, normal, loud)
8. Test with different distances from microphone

**Expected Outcomes:**
- Transcription accuracy >90% for clear speech
- Handles different volumes reasonably well
- Works at normal speaking distance (6-12 inches)
- No significant quality degradation

**Actual Results:**
- Accuracy >90%: [ ] Yes [ ] No
- Volume handling: [ ] Good [ ] Fair [ ] Poor
- Distance handling: [ ] Good [ ] Fair [ ] Poor
- Overall quality: [ ] Good [ ] Fair [ ] Poor

**Transcription Accuracy:**
Original: ________________________________________________
Transcribed: ______________________________________________
Accuracy: _____%

**Pass/Fail Criteria:**
- **Pass**: Good accuracy and handling of variations
- **Fail**: Poor accuracy or very limited operating range

---

## Test Summary

**Tests Passed:** _____ / 6
**Tests Failed:** _____ / 6
**Critical Issues:** _________________________________

**Microphone Quality Assessment:**
[ ] Excellent - Works perfectly in all scenarios
[ ] Good - Minor issues in edge cases
[ ] Fair - Works in basic scenarios, struggles with edge cases
[ ] Poor - Significant issues even in basic usage

**Overall Assessment:**
[ ] All microphone functionality working correctly
[ ] Minor issues detected (non-critical)
[ ] Major issues detected (needs attention)
[ ] Critical failures (blocking release)

**Notes and Observations:**
__________________________________________________
__________________________________________________
__________________________________________________
