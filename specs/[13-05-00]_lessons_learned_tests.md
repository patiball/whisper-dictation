# User Story: Lessons Learned Tests Suite

**ID**: 13-05-00
**Epic**: [13-00-00] Lessons Learned Foundation
**Status**: Draft
**Priority**: High
**Complexity**: Medium
**Estimate**: 30-40 minutes

---

## User Story

**As a** whisper-dictation developer,
**I want** a comprehensive TDD test suite covering all Lessons Learned features (lock file, watchdog, logging, etc.),
**So that** I can confidently maintain and refactor these critical systems, and ensure they work correctly in CI/CD.

---

## Background

### Current Situation
- Tests exist for audio and transcription
- Stability features (lock file, watchdog) are untested
- No CI/CD pipeline testing stability features
- Risk of regressions

### Why This Matters
- **Confidence**: Tests verify features work as designed
- **Regression Prevention**: Catch breakage early
- **CI/CD Integration**: Automated validation on each commit
- **Documentation**: Tests are executable specs

### TDD Philosophy
**Tests FIRST, code SECOND** - We write test cases before implementation.

---

## What We're Building

TDD test suite with:
1. Unit tests for each component
2. Integration tests for end-to-end flows
3. Manual test scenarios (documented)
4. CI configuration
5. Coverage reporting

---

## Key Assumptions

**A1: pytest Framework is Sufficient**
- pytest covers all test types
- Risk: None identified
- Mitigation: Already in use successfully

**A2: Mocking is Safe**
- Can mock PyAudio, sounddevice, subprocess safely
- Risk: Mocks diverge from reality
- Mitigation: Integration tests with real objects

**A3: 100% Coverage Not Required**
- Focus on critical paths
- Target: >90% coverage for stability code, >70% overall
- Risk: Untested edge cases
- Mitigation: Code review + manual testing

---

## Acceptance Criteria

### Test Organization
- [ ] **T1** Tests organized by feature
- [ ] **T2** Each test file corresponds to a module
- [ ] **T3** Clear test naming: `test_<feature>_<behavior>`
- [ ] **T4** All tests in `tests/` directory

### Unit Test Coverage
- [ ] **U1** Lock file creation/cleanup
- [ ] **U2** Lock file with dead PID
- [ ] **U3** Signal handlers
- [ ] **U4** Microphone check success/failure
- [ ] **U5** Heartbeat update
- [ ] **U6** Stall detection
- [ ] **U7** Stream restart
- [ ] **U8** Logging file creation/rotation

### Integration Tests
- [ ] **I1** Two instances scenario
- [ ] **I2** Ctrl+C shutdown
- [ ] **I3** Watchdog detects and recovers from stall
- [ ] **I4** Recording works end-to-end
- [ ] **I5** Log file grows and rotates

### CI/CD Integration
- [ ] **C1** All tests run in CI (GitHub Actions)
- [ ] **C2** Tests must pass before merge
- [ ] **C3** Coverage report generated
- [ ] **C4** Failed tests block deployment

### No Regressions
- [ ] **R1** All existing tests still pass
- [ ] **R2** No performance regression
- [ ] **R3** Test suite doesn't modify user files

---

## Coverage Goals

| Component | Target | Rationale |
|-----------|--------|-----------|
| Lock file | 95% | Critical safety feature |
| Signal handling | 90% | Complex control flow |
| Watchdog | 85% | Thread-based, harder to test |
| Logging | 80% | Mostly setup, less logic |
| Microphone check | 95% | Simple wrapper |
| **Overall** | **85%** | Professional standard |

---

## Related Tasks

- [ ] [13-05-01] Unit Tests
- [ ] [13-05-02] Integration Tests
- [ ] [13-05-03] Manual Tests
- [ ] [13-05-04] Test Infrastructure (CI/CD, fixtures)

---

## Implementation Context (Not Part of Spec)

**Current Testing Framework:**
- Test framework: pytest
- Test directory: `tests/`
- Fixtures: `conftest.py`
- CI/CD: GitHub Actions (`.github/workflows/tests.yml`)

**Test Execution:**
- All tests: `poetry run pytest`
- Unit only: `poetry run pytest -m unit`
- With coverage: `poetry run pytest --cov --cov-report=html`

**Note**: This implementation context documents current choices which may evolve. The specification above describes stable requirements independent of these implementation details.
