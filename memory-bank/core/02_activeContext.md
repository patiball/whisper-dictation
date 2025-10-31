# Active Context

**Current Focus:** 🟠 **EPIC 16 ACTIVE - Stabilizing Test Infrastructure**

**Status:** 🔴 **CRITICAL ISSUES IDENTIFIED** - Analysis of the last test run (`test_results.log`) revealed that Epic 15 was not successful. While tests no longer hang mid-execution, the process fails to terminate due to lingering threads. Additionally, 14 tests are failing, and code coverage is below the required threshold.

**Active Epic:** [16-00-00] Post-Epic 15 Test Infrastructure & Functional Fixes
- **Priority:** High
- **Goal:** To resolve all outstanding issues from Epic 15 and achieve a stable, reliable, and fully functional test infrastructure.
- **Justification:** The application cannot be reliably tested or developed further until the test suite is stable and trustworthy.

**Immediate Priorities (from Epic 16):**
1.  **[16-01-00] Thread Cleanup Fix** (Priority: Critical)
    -   **Problem:** `pytest` process hangs for over 10 minutes after tests complete due to lingering threads from `test_audio_watchdog`.
2.  **[16-02-00] Sys Import Regression Fix** (Priority: High)
    -   **Problem:** A test is failing with `NameError: name 'sys' is not defined`, a regression that was supposedly fixed.
3.  **[16-03-00] Stabilize Logging Tests** (Priority: High)
    -   **Problem:** Multiple logging tests are failing due to issues with log capture.
4.  **[16-04-00] Whisper.cpp Integration Fixes** (Priority: High)
    -   **Problem:** Core C++ backend functionality like language detection and transcription accuracy is failing in tests.
5.  **[16-07-00] Verify and Enforce GPU Usage in C++ Tests** (Priority: High)
    -   **Problem:** User observation suggests tests may be incorrectly using the CPU instead of the GPU.

**Analysis Artifacts:**
- See: `test_results.log` for the full output of the last failed test run.
- See: `memory-bank/specs/[16-00-00]_post_epic_15_fixes.md` for the full plan for the active epic.

---

**Previous Context (Superseded):**
- The belief that Epic 15 was complete has been proven incorrect by test results. The "Next Development Phase" is now superseded by the critical fixes required in Epic 16.
