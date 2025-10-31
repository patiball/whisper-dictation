# Analysis of Pytest Process Hang

**Date**: 2025-10-31

## 1. Initial Observation

The `pytest` process was not terminating after completing test execution, requiring a manual cancellation after several minutes. This occurred even when the tests themselves ran for a short duration (e.g., 10-15 seconds).

## 2. Initial Hypothesis & Fix Attempts

- **Hypothesis 1**: Lingering threads from `tests/test_audio_watchdog.py` were the cause.
- **Attempt 1**: A comprehensive refactoring of `test_audio_watchdog.py` was performed to replace manual thread management with robust `pytest` fixtures (`watchdog_test_harness`, `thread_manager`).
- **Result 1**: The process hang persisted, disproving the hypothesis that the issue was *only* the implementation within that file.

- **Hypothesis 2**: A global, auto-use fixture in `conftest.py` (`reset_logging_state`) was causing a deadlock during its teardown phase (`handler.close()`).
- **Attempt 2**: The `reset_logging_state` fixture was temporarily commented out.
- **Result 2**: The process hang persisted, disproving the hypothesis that this fixture was the root cause.

## 3. Systematic Isolation Strategy

A systematic, group-based isolation strategy was employed to locate the source of the hang.

| Test Group | Command | Result | Conclusion |
| :--- | :--- | :--- | :--- |
| **Unit Tests** | `pytest -m "unit"` | **HANG** | The problem is within the `unit` test group. |
| **Integration Tests** | `pytest -m "integration"` | **OK** | The problem is NOT in the `integration` test group. |
| **Unmarked Tests** | `pytest -m "not unit and not integration"` | **OK** | The problem is NOT in the `unmarked` test group. |

This confirmed the issue was isolated to one or more tests marked as `unit`.

## 4. Final Isolation

The `unit` test group was subdivided to isolate the primary suspect.

| Test Group | Command | Result | Conclusion |
| :--- | :--- | :--- | :--- |
| **Watchdog Test Only** | `pytest tests/test_audio_watchdog.py` | **HANG** | Confirmed as a source of the hang. |
| **Other Unit Tests** | `pytest -m "unit" --ignore=...watchdog.py` | **OK** | All other unit tests exit cleanly. |

## 5. Final Conclusion

The process hanging issue is **unequivocally and exclusively isolated to the `tests/test_audio_watchdog.py` file**.

Despite previous refactoring attempts, a fundamental issue with thread or resource management within this specific test file prevents the `pytest` process from terminating cleanly. The next step is to use a targeted debugging tool (`pytest-timeout`) on this single file to pinpoint the exact line of code causing the deadlock or hang.
