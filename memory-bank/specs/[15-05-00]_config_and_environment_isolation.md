# User Story: Fix Configuration Conflicts and Environment Isolation

**ID**: 15-05-00
**Epic**: [15-00-00] Test Infrastructure Repair
**Priority**: HIGH
**Complexity**: Medium
**Estimate**: 40 minutes (35 min config + 5 min max_bytes variable fix)

## User Story

As a developer, I want unified pytest configuration and proper environment variable isolation so that tests run consistently without configuration conflicts or cross-test contamination.

## Acceptance Criteria

- [ ] pytest.ini deleted (unified to pyproject.toml)
- [ ] All custom markers (unit, integration, manual, slow, whisper_cpp) recognized and properly defined
- [ ] Environment variables modified via monkeypatch (not direct os.environ)
- [ ] No HOME environment variable pollution between tests
- [ ] Configuration parameters (like max_bytes) properly scoped in fixtures
- [ ] Tests can run in any order with reproducible results

## Behavior Examples

### Before
pytest.ini and pyproject.toml conflict → pyproject.toml wins → custom markers unrecognized → tests fail or run with warnings

### After
Single pyproject.toml source → All markers work → Tests properly organized

## Key Assumptions

- pyproject.toml is modern standard, pytest.ini is legacy
- monkeypatch fixture provides test isolation for environment variables
- All markers are actually used in test suite

## Related Tasks

- [15-05-01] Consolidate pytest configuration to pyproject.toml
- [15-05-02] Replace os.environ modifications with monkeypatch in conftest.py
- [15-05-03] Verify configuration and markers work correctly
- [15-05-04] Fix max_bytes variable scoping in logging fixture

## Implementation Context (Not Part of Spec)

**Current Issues**:
- pytest.ini defines unit/integration/manual/slow markers
- pyproject.toml only defines whisper_cpp marker
- pyproject.toml overrides pytest.ini, custom markers not recognized
- conftest.py modifies os.environ['HOME'] directly instead of using monkeypatch

**Locations**:
- `pytest.ini` (should delete)
- `pyproject.toml` (consolidate to here)
- `tests/conftest.py` (use monkeypatch in temp_home fixture)
