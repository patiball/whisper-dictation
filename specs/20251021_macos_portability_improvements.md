# Feature: macOS Portability Improvements (Intel + Apple Silicon)

**Status**: Ready
**Priority**: High
**Complexity**: Simple
**Created**: 2025-10-21
**Target**: Universal macOS support (Intel + Apple Silicon)

## Overview

Improve portability across different macOS configurations by removing hard-coded paths and adding auto-detection for system-specific paths. Currently, the C++ version fails on Intel Macs due to hard-coded Apple Silicon Homebrew paths.

## Problem Statement

### Current Portability Issues

1. **Hard-coded whisper-cli path** (CRITICAL)
   - Code: `/opt/homebrew/bin/whisper-cli`
   - Works: Apple Silicon (M1/M2) only
   - Fails: Intel Macs (use `/usr/local/bin/`)
   - Impact: C++ version completely broken on Intel Macs

2. **Hard-coded user paths in scripts** (MEDIUM)
   - Scripts contain `/Users/mprzybyszewski/...`
   - Requires manual editing for each user
   - Impact: Launch scripts don't work out-of-box

3. **Platform-specific sound API** (LOW)
   - Uses `afplay` and `/System/Library/Sounds/`
   - Already macOS-only by design (rumps dependency)
   - Impact: None (acceptable limitation)

## Acceptance Criteria

### Phase 1: whisper-cli Auto-Detection (CRITICAL)

- [ ] whisper-cli path automatically detected using `shutil.which()`
- [ ] Fallback to common locations if not in PATH
- [ ] Support for ENV override: `WHISPER_CLI_PATH`
- [ ] Works on both Intel (`/usr/local`) and Apple Silicon (`/opt/homebrew`)
- [ ] Tested on both architectures

### Phase 2: Launch Scripts Portability (MEDIUM)

- [ ] Remove hard-coded user paths from `scripts/start_whisper.sh`
- [ ] Remove hard-coded user paths from `scripts/whisper-dictation-wrapper.sh`
- [ ] Use `$HOME` environment variable
- [ ] Use relative paths where possible
- [ ] Scripts work without modification on any macOS user account

### Phase 3: Documentation Updates (LOW)

- [ ] Add "Platform Support" section to README
- [ ] Document Intel vs Apple Silicon differences
- [ ] Add troubleshooting for path detection issues
- [ ] Document ENV overrides for power users

## Implementation Plan

### Phase 1: whisper-cli Path Detection

**File:** `whisper-dictation-fast.py`

**Current Code (line 43):**
```python
cmd = [
    '/opt/homebrew/bin/whisper-cli',  # HARD-CODED Apple Silicon path
    '-m', self.model_path,
    ...
]
```

**New Code:**
```python
import shutil
import os

# At module level (after imports)
def get_whisper_cli_path():
    """
    Auto-detect whisper-cli binary location.

    Priority:
    1. WHISPER_CLI_PATH environment variable
    2. whisper-cli in system PATH
    3. Apple Silicon default (/opt/homebrew)
    4. Intel Mac default (/usr/local)

    Returns:
        str: Path to whisper-cli binary

    Raises:
        FileNotFoundError: If whisper-cli not found in any location
    """
    # 1. ENV override
    env_path = os.getenv('WHISPER_CLI_PATH')
    if env_path and os.path.isfile(env_path):
        return env_path

    # 2. Auto-detect in PATH
    path_binary = shutil.which('whisper-cli')
    if path_binary:
        return path_binary

    # 3. Common Homebrew locations
    common_paths = [
        '/opt/homebrew/bin/whisper-cli',  # Apple Silicon
        '/usr/local/bin/whisper-cli',     # Intel Mac
    ]

    for path in common_paths:
        if os.path.isfile(path):
            return path

    # 4. Not found
    raise FileNotFoundError(
        "whisper-cli not found. Install with: brew install whisper-cpp\n"
        "Or set WHISPER_CLI_PATH environment variable."
    )

# Cache the path at module load
WHISPER_CLI_PATH = get_whisper_cli_path()

# In SpeechTranscriber.transcribe():
cmd = [
    WHISPER_CLI_PATH,  # Use auto-detected path
    '-m', self.model_path,
    ...
]
```

**Error Handling:**
```python
# In main or __init__
try:
    WHISPER_CLI_PATH = get_whisper_cli_path()
    print(f"Found whisper-cli at: {WHISPER_CLI_PATH}")
except FileNotFoundError as e:
    print(f"ERROR: {e}")
    sys.exit(1)
```

### Phase 2: Launch Scripts Fixes

**File:** `scripts/start_whisper.sh`

**Current:**
```bash
#!/bin/bash
export PATH="/Users/mprzybyszewski/.local/bin:/Users/mprzybyszewski/.pyenv/shims:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
cd /Users/mprzybyszewski/whisper-dictation
/Users/mprzybyszewski/.local/bin/poetry run python whisper-dictation-optimized.py \
    --k_double_cmd \
    -m medium \
    -l en,pl
```

**New:**
```bash
#!/bin/bash
set -e

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Add user bin to PATH
export PATH="${HOME}/.local/bin:${HOME}/.pyenv/shims:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

# Change to project directory
cd "${PROJECT_DIR}"

# Run with poetry (will find it in PATH)
poetry run python whisper-dictation.py \
    --k_double_cmd \
    -m medium \
    -l en,pl
```

**File:** `scripts/whisper-dictation-wrapper.sh`

**Current:**
```bash
cd /Users/mprzybyszewski/whisper-dictation
```

**New:**
```bash
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_DIR}"
```

### Phase 3: Documentation Updates

**Add to README.md:**

```markdown
## Platform Support

### Supported Platforms

- ✅ **macOS (Apple Silicon M1/M2)** - Primary development platform
- ✅ **macOS (Intel)** - Fully supported with auto-detection
- ❌ **Linux/Windows** - Not supported (rumps library is macOS-only)

### Architecture-Specific Notes

The application automatically detects your Mac architecture:

| Component | Intel Mac | Apple Silicon | Detection |
|-----------|-----------|---------------|-----------|
| Homebrew | `/usr/local` | `/opt/homebrew` | Auto-detected |
| whisper-cli | `/usr/local/bin/` | `/opt/homebrew/bin/` | Auto-detected |
| Python | System/pyenv | System/pyenv | Standard |

### Troubleshooting

**whisper-cli not found:**
```bash
# Verify installation
which whisper-cli

# If not found, install:
brew install whisper-cpp

# Override detection (if needed):
export WHISPER_CLI_PATH=/path/to/whisper-cli
```

**Intel Mac Setup:**
```bash
# Homebrew should be in /usr/local
brew --prefix  # Should show: /usr/local

# Install dependencies
brew install portaudio llvm whisper-cpp

# whisper-cli will be auto-detected at:
# /usr/local/bin/whisper-cli
```

### Environment Variables

Advanced users can override auto-detection:

- `WHISPER_CLI_PATH` - Override whisper-cli binary location
- `WHISPER_FRAMES_PER_BUFFER` - Override audio buffer size
- `WHISPER_DEBUG_RECORDER` - Enable recorder debug logging
```

## Testing Strategy

### Test Matrix

| Mac Type | Python Version | C++ Version | Expected Result |
|----------|---------------|-------------|-----------------|
| Apple Silicon (M1/M2) | ✅ Works | ✅ Works | Full support |
| Intel Mac | ✅ Works | ✅ Works (after fix) | Full support |

### Test Cases

```python
def test_whisper_cli_detection_apple_silicon():
    """Test auto-detection on Apple Silicon"""
    # Mock environment for M1/M2
    path = get_whisper_cli_path()
    assert path in [
        '/opt/homebrew/bin/whisper-cli',
        shutil.which('whisper-cli')
    ]

def test_whisper_cli_detection_intel():
    """Test auto-detection on Intel Mac"""
    # Mock environment for Intel
    path = get_whisper_cli_path()
    assert path in [
        '/usr/local/bin/whisper-cli',
        shutil.which('whisper-cli')
    ]

def test_whisper_cli_env_override():
    """Test WHISPER_CLI_PATH environment variable"""
    os.environ['WHISPER_CLI_PATH'] = '/custom/path/whisper-cli'
    # Mock file existence
    path = get_whisper_cli_path()
    assert path == '/custom/path/whisper-cli'

def test_whisper_cli_not_found():
    """Test error handling when whisper-cli not installed"""
    # Mock: no whisper-cli anywhere
    with pytest.raises(FileNotFoundError) as exc:
        get_whisper_cli_path()
    assert "brew install whisper-cpp" in str(exc.value)
```

### Manual Testing

**On Intel Mac:**
1. Clone repo
2. `brew install portaudio llvm whisper-cpp`
3. `poetry install && poetry shell`
4. `poetry run python whisper-dictation-fast.py --k_double_cmd`
5. Verify whisper-cli detected at `/usr/local/bin/whisper-cli`
6. Record and transcribe test audio
7. Verify Polish transcription works correctly

**On Apple Silicon:**
1. Same steps as Intel
2. Verify whisper-cli detected at `/opt/homebrew/bin/whisper-cli`
3. Verify M1 GPU acceleration works

## File Changes Required

### Core Implementation

- **whisper-dictation-fast.py**
  - Add `get_whisper_cli_path()` function
  - Replace hard-coded path with `WHISPER_CLI_PATH`
  - Add error handling for missing binary

### Launch Scripts

- **scripts/start_whisper.sh**
  - Replace user-specific paths with `$HOME`
  - Use relative paths for project directory
  - Add proper error handling (`set -e`)

- **scripts/whisper-dictation-wrapper.sh**
  - Same fixes as start_whisper.sh

### Documentation

- **README.md**
  - Add "Platform Support" section
  - Document Intel vs Apple Silicon differences
  - Add troubleshooting guide
  - Document environment variable overrides

## Risk Assessment

### Low Risk

- Auto-detection logic (standard Python libraries)
- Shell script fixes (basic bash)
- Documentation updates

### Mitigation

- Extensive testing on both architectures
- Fallback to common paths if auto-detection fails
- Clear error messages guide users to solutions
- ENV overrides for edge cases

## Success Metrics

### Before Fix

- Apple Silicon: ✅ C++ version works
- Intel Mac: ❌ C++ version fails (hard-coded path)
- Portability score: 3/5

### After Fix

- Apple Silicon: ✅ C++ version works
- Intel Mac: ✅ C++ version works
- Portability score: 5/5

## Related Issues

- memory-bank/issues-backlog.md (add portability note)
- specs/20250130_whisper_cpp_quality_fix.md (C++ version improvements)

## Notes

- Python version already works on both architectures (no hard-coded paths)
- Only C++ version affected by whisper-cli path issue
- rumps library limitation (macOS-only) is acceptable by design
- This spec focuses on macOS portability, not cross-platform support

---

**Expected Outcome:** 🎯 Universal macOS support - works out-of-box on both Intel and Apple Silicon Macs without manual configuration.
