<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# CLAUDE.md

This file provides guidance for Claude Code when working with this repository, with emphasis on Memory Bank workflows and specification standards.

## Quick Reference

**For project overview, setup, running commands, and development notes:**
→ See `memory-bank/core/01_projectbrief.md` and `memory-bank/core/05_techContext.md`

**For architecture and code patterns:**
→ See `memory-bank/core/04_systemPatterns.md`

**For current focus and priorities:**
→ See `memory-bank/core/02_activeContext.md`

## Memory Bank System

**Readme_MB.md is the SINGLE SOURCE OF TRUTH**
- ALWAYS read `memory-bank/Readme_MB.md` FIRST before any file operations
- NEVER assume file locations - verify against Readme_MB.md
- Core files are the authority for project state

### Memory Bank Core Files

1. **01_projectbrief.md** - Project overview, features, version comparison
2. **02_activeContext.md** - Current focus and immediate priorities
3. **03_progress.md** - Implementation milestones and backlog
4. **04_systemPatterns.md** - Architecture, code organization, design patterns
5. **05_techContext.md** - Setup, dependencies, running commands, technical notes

### Before Any Work

1. Read `memory-bank/Readme_MB.md` to understand structure
2. Review relevant core files (usually 02_activeContext.md + others)
3. Execute your work
4. Update memory-bank/core files if context changes

---

## Specifications

The `memory-bank/specs/` directory contains all feature specifications following hierarchical naming: `[XX-YY-ZZ]_name.md`

**Hierarchy:**
- **[XX-00-00]**: Epic or Standalone User Story
- **[XX-YY-00]**: User Story within Epic XX
- **[XX-YY-ZZ]**: Task within User Story XX-YY
- **YYYYMMDD_*.md**: Hotfixes only (emergency production fixes)

**Spec Structure (DO):**
- Describe WHAT and WHY (not HOW)
- Use testable acceptance criteria
- Include behavior examples (before/after)
- Explain design decisions
- Add TDD test cases BEFORE implementation

**Spec Quality (DON'T):**
- DON'T prescribe exact implementation code
- DON'T include full function definitions
- DON'T write test cases in spec (those go in tests/)
- DON'T create 400-line specs (use Epic/US/Task hierarchy)

#### User Story Format (80-120 lines)

```markdown
# User Story: [Title]

**ID**: XX-YY-00
**Epic**: [XX-00-00] Epic name (if applicable)
**Priority**: High | Medium | Low
**Complexity**: Simple | Medium | Complex
**Estimate**: [Total minutes - sum of related Tasks]

## User Story
As a [role], I want [feature], so that [benefit]

## Acceptance Criteria
- [ ] Main criterion 1 (testable)
- [ ] Main criterion 2 (testable)
- [ ] Main criterion 3 (testable)

## Behavior Examples
Brief examples showing expected behavior before/after

## Key Assumptions
- Main assumption 1 and validation
- Main assumption 2 and validation

## Related Tasks
- [XX-YY-01] Task 1 name
- [XX-YY-02] Task 2 name

## Implementation Context (Not Part of Spec)
**Affected Components**: Brief list
**Related Systems**: Brief list
```

**When to create User Story:**
- Feature/requirement is too large for single implementation session (>30 minutes)
- Multiple distinct tasks needed
- Clear user value proposition
- Can be estimated in hours not minutes

#### Task Format (60-80 lines)

```markdown
# Task: [Specific Objective]

**ID**: XX-YY-ZZ
**User Story**: [XX-YY-00] Story name
**Complexity**: Simple | Medium
**Estimate**: 15-30 minutes

## What
Single, concrete objective to implement.

## Design Approach
Key design decisions and approach (not prescriptive code)

## Failure Modes
- Key failure mode 1: Detection, Consequence, Prevention, Mitigation
- Key failure mode 2: Detection, Consequence, Prevention, Mitigation

## Acceptance Criteria
- [ ] Specific testable outcome 1
- [ ] Specific testable outcome 2

## Implementation Context (Not Part of Spec)
**Current Location**: Brief reference to where in codebase
**Key Variables/Functions**: Current patterns
```

**When to create Task:**
- User Story > 150 lines
- Implementation estimate > 30 minutes
- Multiple distinct implementation phases
- Technical details too lengthy for User Story section

**Task Sizing Rules:**
- If Task estimate > 30 minutes → split further or re-scope
- Each Task should be independently testable
- Task Tests should all pass independently of other Tasks in same US

#### Sizing Guidelines

| Type | Lines | Time | When |
|------|-------|------|------|
| Simple Task | 60-70 | 15-20 min | Single focused change |
| Medium Task | 70-80 | 20-30 min | Multi-step implementation |
| User Story | 80-120 | 30-120 min | Multiple Tasks needed |
| Epic | 150-250 | 2-8 hours | Multiple User Stories |

#### Abstraction & Durability Guidelines

**Why This Matters**: Specs must remain valid across code refactoring, file path changes, and version updates. "Brittle" specs become obsolete quickly and create maintenance burden.

**Key Principle**: Specs describe **BEHAVIOR and REQUIREMENTS**, not implementation details. A spec should be valid 2 years from now even if the codebase changes significantly.

**DO - Write Durable Specs:**

- **Use abstraction**: "Call setup_lock_file() at application startup" (not "add code at line 245")
- **Use structural names**: "In the Recorder class" (not "in whisper-dictation.py line 123")
- **Describe outcomes**: "User cannot start second instance" (not "lock file exists at ~/.whisper-dictation.lock")
- **Use relative paths**: "in user's home directory" (not "~/.whisper-dictation.lock")
- **Separate concerns**: Separate "WHAT must happen" from "WHERE it currently happens"
- **Add context diagrams**: Show relationships without implementation details

**DON'T - Avoid Brittle Specs:**

- ❌ **Line numbers**: "Line 245 in fast.py" → ✅ "In StatusBarApp.start_recording()"
- ❌ **Exact file paths**: "~/.whisper-dictation.log" → ✅ "Log file in user's home directory"
- ❌ **Variable names as requirements**: "Set watchdog_active = False" → ✅ "Stop watchdog monitoring"
- ❌ **Hard-coded values as constraints**: "5 backup files" → ✅ "Configurable number of backups (default 5)"
- ❌ **Current code structure as requirement**: "In Recorder._record_impl()" → ✅ "During audio recording loop"

**Implementation Notes Pattern**:

For specs that DO need implementation context (line numbers, current structure), use a separate section:

```markdown
## Implementation Context (Not Part of Spec)

**Current Location**: `whisper-dictation.py`, class `Recorder`, method `_record_impl()`
**Current Variables**: `frames_per_buffer`, `watchdog_active`
**Note**: These implementation details change. The spec above remains stable.

**Current Line References** (for review purposes only):
- Lock file creation: whisper-dictation.py:45-50
- Signal handler registration: whisper-dictation.py:78-85
```

This allows developers to find code quickly during review, but keeps the spec itself stable.

**When to Apply Abstraction**:

| Spec Type | Apply Abstraction | Rationale |
|-----------|------------------|-----------|
| Epic (XX-00-00) | **REQUIRED** | Long-lived, multiple refactors expected |
| User Story (XX-YY-00) | **REQUIRED** | Developers change implementation details |
| Task (XX-YY-ZZ) | **Optional** | Short-lived, usually 1 dev touches it |
| Bug Fix | **Optional** | One-off, may not need future updates |
| Hotfix (YYYYMMDD_*.md) | **Optional** | Emergency, durability less important |

**Checklist for Durable Specs**:

Before finalizing a spec, ask:
- [ ] Does spec mention specific line numbers? → Move to "Implementation Notes"
- [ ] Does spec hardcode file paths? → Use "user's home directory" instead
- [ ] Does spec prescribe variable names? → Describe outcome instead
- [ ] Does spec assume current code structure? → Describe requirement abstractly
- [ ] Would spec be valid if codebase restructured tomorrow? → If not, make it more abstract

---

#### Important Notes

**Hotfixes only:** Date-based format `YYYYMMDD_*.md` is reserved exclusively for emergency production fixes.

**All planned work:** Use hierarchical format `[XX-00-00]_name.md` (standalone US) or `[XX-YY-ZZ]_name.md` (Epic/US/Task).

**Numbering:** Assign next available number sequentially (01, 02, 03...). Check existing specs with `ls specs/\[*-00-00\]*` to find the last number.

## Common Patterns

### Adding New CLI Flags
1. Add argument to `parse_args()` in whisper-dictation.py
2. Pass to relevant component constructor
3. Document in README.md

### Implementing New Diagnostics
1. Create script in `scripts/` directory
2. Use TDD recorder/transcriber for consistency
3. Save test audio in root with descriptive name
4. Document findings in memory-bank or specs

### Device Management Changes
1. Modify base logic in `device_manager.py`
2. Add MPS-specific handling in `mps_optimizer.py`
3. Update both main app and TDD transcriber
4. Test with CPU/MPS device switching

### Audio Processing Changes
1. Core recording logic is duplicated in:
   - `whisper-dictation.py` (Recorder class)
   - `recorder.py` (TDD-compatible version)
2. Keep both in sync for parameters like:
   - `frames_per_buffer`, `warmup_buffers`, `exception_on_overflow`
   - Auto-fallback logic
   - Debug logging
