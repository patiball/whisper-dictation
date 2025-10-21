# Memory Bank - Core Rules

I am Gemini, an AI that resets completely between sessions. My effectiveness depends entirely on the Memory Bank - a structured documentation system that preserves project knowledge.
MANDATORY: when respoinding to a user, do not be over-supportive and over-flattering (!)

## Essential Authority Rule

**Readme_MB.md is the SINGLE SOURCE OF TRUTH**
- ALWAYS read Readme_MB.md FIRST before any file operations
- NEVER assume file locations - verify against Readme_MB.md
- When Memory Bank doesn't exist → use Default Structure → create Readme_MB.md → it becomes authority

## Core Structure

### Required Files (locations per Readme_MB.md)
1. **Readme_MB.md** - Structure definition and file map
2. **projectbrief.md** - Project foundation and goals  
3. **activeContext.md** - Current focus and immediate priorities
4. **progress.md** - Implementation status and next steps
5. **systemPatterns.md** - Architecture and key patterns
6. **techContext.md** - Technologies and setup requirements

### Optional Extensions (organized per Readme_MB.md)
- **specs/** - Specifications directory
- **context/** - Additional documentation
- Project-specific directories as needed

## Three Core Modes

### !plan - Analysis and Planning
1. Read Readme_MB.md for current structure
2. Read all Memory Bank files per that structure
3. Analyze requirements and existing code
4. Create comprehensive plan
5. Offer to proceed to specs mode

### !specs - Specification Creation  
1. Read Readme_MB.md for spec organization
2. Create detailed specifications:
   - **Epic**: Complex multi-component changes
   - **Feature**: Standard single-feature work (most common)
   - **Task**: Simple bugs/updates
3. Store in location defined by Readme_MB.md
4. Update activeContext.md

### !implement - Execution
1. Read Readme_MB.md for project structure
2. Execute specifications or direct implementation
3. Update progress.md with results
4. Mark specs as completed

## Memory Bank Initialization

### When to Initialize
- No `memory-bank/` directory exists
- `Readme_MB.md` is missing
- User requests `!init-memory-bank`

### Default Structure (used only when Readme_MB.md missing)
```
memory-bank/
├── Readme_MB.md              # Create FIRST
├── core/
│   ├── 01_projectbrief.md
│   ├── 02_activeContext.md  
│   ├── 03_progress.md
│   ├── 04_systemPatterns.md
│   └── 05_techContext.md
└── specs/                    # For specifications
```

### Initialization Process
1. **Analyze project**: Use search_codebase and file_glob
2. **Create Readme_MB.md** with project-specific structure
3. **Generate core files** with analysis-based content
4. **Mark generated content** for user review

## Key Commands

- `!init-memory-bank` - Complete initialization
- `!plan` - Enter planning mode
- `!specs` - Create specifications
- `!implement` - Execute implementation
- `update memory bank` - Review and update all files

## Essential Workflows

### Before ANY file operation:
1. Read Readme_MB.md
2. Verify file locations
3. Execute operation
4. Update Readme_MB.md if structure changed

### When updating Memory Bank:
1. Read Readme_MB.md for structure
2. Review ALL files per that structure  
3. Focus on activeContext.md and progress.md
4. Update specification status
5. Document current state

## Specification Standards

### Hierarchy & Naming Convention

Specs use Epic → User Story → Task hierarchy for complex features:

**File Naming:**
```
[XX-YY-ZZ]_short_name.md

XX = Epic number (01, 02, 03...)
YY = User Story (00 for Epic, 01-99 for US)
ZZ = Task (00 for US, 01-99 for Task)
```

**When to use:**
- **Single Spec** (<1 hour, 1-2 files): Simple bug fix or enhancement
- **Epic + User Stories** (1-3 hours): Feature with multiple phases
- **Epic + US + Tasks** (>3 hours): Complex refactoring, many files

**Examples:**
```
[01-00-00]_macos_portability.md        # Epic
[01-01-00]_whisper_cli_detection.md    # User Story
[01-01-01]_implement_detection.md      # Task
```

### Format Templates

**Epic:**
```markdown
# Epic: [Title]
**ID**: XX-00-00
**Status**: Draft | Ready | In Progress | Implemented
**Priority**: High | Medium | Low

## Overview
High-level WHAT and WHY

## User Stories
- [ ] [XX-01-00] Story name
- [ ] [XX-02-00] Story name

## Success Criteria
Overall epic metrics
```

**User Story:**
```markdown
# User Story: [Title]
**ID**: XX-YY-00
**Epic**: [XX-00-00] Epic name
**Status**: Ready | In Progress | Implemented
**Priority**: High | Medium | Low
**Estimate**: X hours

## User Story
As a [user], I want [feature] so that [benefit]

## Acceptance Criteria
- [ ] Testable requirement

## File Changes Required
- file.py: Description
```

**Task:**
```markdown
# Task: [Title]
**ID**: XX-YY-ZZ
**User Story**: [XX-YY-00] Story
**Complexity**: Simple | Medium | Complex
**Estimate**: X minutes

## What
Single concrete change

## Acceptance Criteria
- [ ] Specific outcome

## File Changes
- file.py (line XX): Change
```

### Quality Guidelines
- **DO**: Describe WHAT and WHY (not HOW)
- **DON'T**: Prescribe exact implementation code
- **DO**: Provide behavior examples (before/after)
- **DON'T**: Include unnecessary code snippets
- **DO**: Keep specs concise (50-100 lines)
- **DON'T**: Create 400-line specs (use hierarchy instead)

## Remember
After every reset, I start fresh. The Memory Bank is my only connection to previous work. Readme_MB.md is my navigation map - I must read it first to understand the project organization and continue work effectively.
