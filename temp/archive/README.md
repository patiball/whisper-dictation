# Archive - Historical Files

This directory contains archived files from earlier development phases. These files are kept for historical reference but are no longer actively used in the project.

## 📁 Directory Structure

```
archive/
├── README.md                    # This file
├── root-context/                # Old context/task files from root directory
│   ├── current_context.md      # Historical project context (2025-06-30)
│   ├── fix_remaining_tests.md  # Test fixing action plan (2025-06-30)
│   ├── model_loading_fix.md    # Model loading fix documentation (2025-06-30)
│   ├── testy.md                # Old test planning document
│   └── Wcześniej               # Empty artifact file
└── docs-tasks/                  # Old documentation task tracking
    ├── .tasks/                  # Task files from Oct 2025 docs generation
    ├── .agent-task.md          # AI agent task tracking
    ├── .cleanup-task.md        # Cleanup task tracking
    └── .commit-task.md         # Commit task tracking
```

---

## 📝 Root Context Files (root-context/)

### `current_context.md` (2025-06-30)
**Historical Snapshot**: Project status during TDD implementation phase
- Documents: TDD RED/GREEN/REFACTOR phases
- Test pass rates (64%, 87.5%)
- Model loading fixes
- **Superseded by**: `memory-bank/core/02_activeContext.md`

### `fix_remaining_tests.md` (2025-06-30)
**Action Plan**: Fixing failing tests (10/14 → 14/14 pass rate)
- GPU vs CPU acceleration issues
- Audio signal timing adjustments
- Microphone debug procedures
- **Status**: Issues resolved, tests now in `tests/` directory

### `model_loading_fix.md` (2025-06-30)
**Fix Documentation**: Model loading performance issue
- Problem: Download time vs cache loading time
- Solution: Pre-check local cache before timing
- Download optimization with user prompts
- **Status**: Fixed and integrated into `transcriber.py`

### `testy.md`
**Test Planning**: Original TDD test planning document
- **Status**: Replaced by pytest suite in `tests/`

### `Wcześniej`
Empty artifact file, no content

---

## 🗂️ Documentation Task Files (docs-tasks/)

### `.tasks/` Directory (33+ files)
**Task Tracking**: Documentation generation tasks from October 2025
- Architecture documentation generation
- Data flow diagrams
- API interface documentation
- QA reviews and fixes
- **Superseded by**: Memory Bank system (`memory-bank/`)

**File Pattern**:
```
20251010_HHMM_TASK_NAME.md  # Timestamped task files
QA_REPORT_*.md              # Quality assurance reports
STATUS.md                   # Task status tracking
```

### Hidden Task Files
- `.agent-task.md` - AI agent task coordination
- `.cleanup-task.md` - Cleanup task tracking
- `.commit-task.md` - Commit task tracking

**Note**: These were part of an earlier task tracking system, now replaced by Memory Bank.

---

## 🔄 Why These Files Were Archived

### Replaced by Better Systems

1. **Context Tracking**: Old `.md` files → Memory Bank (`memory-bank/core/`)
2. **Task Management**: `.tasks/` files → Memory Bank specs & progress
3. **Test Planning**: Old test docs → pytest suite (`tests/`)

### Historical Value

While no longer actively used, these files provide:
- Insight into project evolution
- Historical decision-making context
- Implementation timeline
- Problem-solving approaches

---

## ⚠️ Important Notes

- **Do NOT use these files** for current project information
- **Do NOT update** these archived files
- For current status, see:
  - `memory-bank/core/02_activeContext.md` (current focus)
  - `memory-bank/core/03_progress.md` (implementation status)
  - `memory-bank/issues-backlog.md` (active issues)

---

## 🗑️ Cleanup Policy

These files can be safely deleted if:
1. No historical reference is needed
2. All information has been migrated to Memory Bank
3. Repository size optimization is required

**Recommendation**: Keep for now as historical reference, review for deletion after 3-6 months.

---

**Archive Created**: 2025-10-21
**Archived By**: Repository cleanup initiative
**Related**: Repository organization to industry standards
