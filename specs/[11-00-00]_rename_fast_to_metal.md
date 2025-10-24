# Backlog: Rename whisper-dictation-fast.py to whisper-dictation-metal.py

**Status**: Backlog
**Priority**: Low
**Complexity**: Simple
**Estimate**: 15-20 minutes

## Problem

Current naming is confusing:
- `whisper-dictation.py` vs `whisper-dictation-fast.py` doesn't clearly communicate technical differences
- "-fast" only suggests speed, not the actual backend (C++/Metal vs Python/PyTorch)
- Users don't know which version to use on Intel vs M1/M2

## Proposed Change

Rename files to reflect technical implementation:
- `whisper-dictation.py` → keep as-is (Python/PyTorch, CPU)
- `whisper-dictation-fast.py` → `whisper-dictation-metal.py` (C++/whisper.cpp, Metal GPU)

## File Changes Required

- Rename `whisper-dictation-fast.py` → `whisper-dictation-metal.py`
- Update README.md examples
- Update CLAUDE.md references
- Update any scripts in `scripts/` directory
- Consider adding symlink for backward compatibility

## Acceptance Criteria

- [ ] File renamed
- [ ] All documentation updated
- [ ] Scripts updated
- [ ] Application still runs correctly
- [ ] Clear indication which version uses GPU (Metal) vs CPU
