# Manual Test Scenarios for Whisper Dictation

This directory contains manual test scenarios for features that require human verification or are difficult to automate.

## Overview

Manual tests are organized by feature area:
- `lock_file_scenarios.md` - Lock file behavior tests
- `microphone_scenarios.md` - Microphone access tests  
- `logging_scenarios.md` - Logging system tests

## Test Execution Guidelines

### Preparation
1. Ensure whisper-dictation is properly installed
2. Test on target macOS version (Intel and Apple Silicon)
3. Have terminal and text editor ready for verification
4. Backup any existing configuration files

### Test Environment
- **Required**: macOS with microphone access
- **Optional**: External microphone for testing
- **Tools**: Terminal, text editor, system preferences

### Documentation Format
Each test scenario includes:
- **Setup**: What needs to be prepared before testing
- **Steps**: Detailed step-by-step procedure
- **Expected**: What should happen if the feature works correctly
- **Actual**: Space to record what actually happened
- **Pass/Fail**: Clear criteria for test success

## Running Tests

1. Navigate to the specific test file for the feature you want to test
2. Follow the setup instructions
3. Execute the test steps precisely
4. Record actual results
5. Determine pass/fail based on expected outcomes
6. Document any issues or unexpected behavior

## Reporting Issues

For any test failures:
1. Document the exact steps taken
2. Include system information (macOS version, hardware)
3. Capture error messages or logs
4. Note any environmental factors that might affect the test
5. Report issues in the project issue tracker

## Test Frequency

- **Before releases**: Run full manual test suite
- **After major changes**: Test affected features
- **Regular maintenance**: Test critical paths monthly
- **Bug reports**: Test specific scenarios as needed

## Safety Notes

- These tests may create temporary files in your home directory
- Tests may affect system audio settings
- Always ensure proper cleanup after testing
- Test in a non-production environment when possible
