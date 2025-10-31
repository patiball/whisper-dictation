# Epic: Post-Epic 15 Test Infrastructure & Functional Fixes
**ID**: 16-00-00
**Status**: Draft
**Priority**: High

## Overview
This epic addresses critical issues remaining after the completion of Epic 15. Despite previous fixes, the test suite is still unstable, exhibiting problems with lingering threads causing post-test hangs, significant test failures, and insufficient code coverage. The goal of this epic is to resolve these outstanding issues to finally achieve a stable, reliable, and fully functional test infrastructure.

## User Stories
- [ ] [16-01-00] Thread Cleanup Fix
- [ ] [16-02-00] Sys Import Regression Fix
- [ ] [16-03-00] Stabilize Logging Tests
- [ ] [16-04-00] Whisper.cpp Integration Fixes
- [ ] [16-05-00] Review Audio Quality Metrics
- [ ] [16-06-00] Increase Code Coverage
- [ ] [16-07-00] Verify and Enforce GPU Usage in C++ Tests

## Success Criteria
- The `pytest` process exits cleanly with a return code of 0 within 10 seconds of completing all tests.
- All tests (89/89) pass successfully.
- Code coverage meets or exceeds the 70% threshold.
- All `whisper.cpp` integration tests correctly utilize the GPU (Metal) on Apple Silicon hardware.
