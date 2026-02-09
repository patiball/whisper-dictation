# Feature: macOS Portability Improvements

**Status**: Ready
**Priority**: High
**Complexity**: Simple

## Overview

Enable whisper-dictation to work on both Intel and Apple Silicon Macs without modification. Currently, the C++ version (whisper-dictation-fast.py) fails on Intel Macs due to hard-coded Apple Silicon Homebrew paths.

## Problem

The application has architecture-specific hard-coded paths that prevent portability:

1. **whisper-cli binary path** - Hard-coded `/opt/homebrew/bin/whisper-cli` (Apple Silicon only)
2. **Launch scripts** - Contain user-specific paths `/Users/mprzybyszewski/...`

**Impact**: C++ version completely broken on Intel Macs (Homebrew uses `/usr/local` instead of `/opt/homebrew`)

## Acceptance Criteria

### Phase 1: whisper-cli Detection (CRITICAL)

- [ ] Auto-detect whisper-cli location (check PATH, then common Homebrew locations)
- [ ] Support environment variable override: `WHISPER_CLI_PATH`
- [ ] Clear error message when whisper-cli not found
- [ ] Works on both Intel and Apple Silicon Macs

### Phase 2: Launch Scripts (MEDIUM)

- [ ] Replace hard-coded user paths with `$HOME` variable
- [ ] Use relative paths for project directory
- [ ] Scripts work without modification on any user account

### Phase 3: Documentation (LOW)

- [ ] Document Intel vs Apple Silicon differences in README
- [ ] Add troubleshooting section for path detection
- [ ] Document `WHISPER_CLI_PATH` environment variable

## File Changes Required

**whisper-dictation-fast.py:**
- Replace hard-coded `/opt/homebrew/bin/whisper-cli` with auto-detection
- Check environment variable, then PATH, then common locations
- Line 43 (whisper-cli path in cmd list)

**scripts/start_whisper.sh:**
- Replace `/Users/mprzybyszewski/...` with `$HOME`
- Use `$(dirname)` for relative project path
- Lines 4, 14, 29

**scripts/whisper-dictation-wrapper.sh:**
- Replace hard-coded path with relative path
- Line 2

**README.md:**
- Add "Platform Support" section
- Document architecture differences
- Add troubleshooting guide

## Integration Points

- Python `shutil.which()` for PATH detection
- `os.getenv()` for environment variable override
- Fallback chain: ENV → PATH → Apple Silicon → Intel
- Error handling when binary not found

## Behavior Examples

**Current behavior (Apple Silicon only):**
```
# Apple Silicon M1/M2 - WORKS
whisper-cli at: /opt/homebrew/bin/whisper-cli ✅

# Intel Mac - FAILS
FileNotFoundError: /opt/homebrew/bin/whisper-cli ❌
```

**Expected behavior (Universal):**
```
# Apple Silicon M1/M2
Auto-detected whisper-cli at: /opt/homebrew/bin/whisper-cli ✅

# Intel Mac
Auto-detected whisper-cli at: /usr/local/bin/whisper-cli ✅

# Custom installation
Using WHISPER_CLI_PATH: /custom/path/whisper-cli ✅
```

## Notes

- Python version already portable (no hard-coded paths)
- Only C++ version affected by whisper-cli path issue
- macOS-only by design (rumps dependency) - cross-platform not in scope
- Estimated effort: 30-45 minutes total

---

**Expected Outcome**: Application works out-of-box on both Intel and Apple Silicon Macs without configuration.
