# User Story: Sys Import Regression Fix
**ID**: 16-02-00
**Epic**: [16-00-00] Post-Epic 15 Test Infrastructure & Functional Fixes
**Status**: Ready
**Priority**: High
**Estimate**: 10-15 minutes

## User Story
As a developer, I want the `test_lock_file_cleanup_on_process_crash` test to pass, so that I can be confident in the stale lock file recovery mechanism.

## Acceptance Criteria
- [ ] The `test_lock_file_cleanup_on_process_crash` test passes.
- [ ] The fix involves adding the missing `import sys` statement to the temporary Python script created by the test.

## File Changes Required
- `tests/test_lock_file_integration.py`: Locate the test helper script within the `test_lock_file_cleanup_on_process_crash` function and add `import sys` to its content.
