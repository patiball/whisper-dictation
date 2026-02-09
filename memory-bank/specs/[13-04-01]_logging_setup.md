# Task: Logging Setup & Configuration

**ID**: 13-04-01
**User Story**: [13-04-00] Enhanced Logging & Diagnostics
**Complexity**: Simple
**Estimate**: 7 minutes

---

## What

Configure centralized logging infrastructure with file rotation, consistent formatting, and CLI configuration options.

---

## Design Approach

**Logging Infrastructure:**
- Use Python's standard `logging` module
- Use `RotatingFileHandler` for automatic rotation
- Configure during application initialization (early)
- Set up both file and console handlers

**File Handler Configuration:**
- Log file location: `~/.whisper-dictation.log`
- Max file size: 5MB per file
- Backup files: 5 backups (25MB total)
- Rotation: Automatic when size exceeded
- Old backups deleted when limit reached

**Log Format:**
- Timestamp: Date, time, milliseconds
- Log level: INFO, WARNING, ERROR, DEBUG
- Message: Clear, concise description
- Format string: `%(asctime)s - %(levelname)s - %(message)s`

**CLI Integration:**
- Add `--log-level` argument to parse_args()
- Choices: DEBUG, INFO, WARNING, ERROR
- Default: INFO (balance verbosity with usability)
- Optional `--log-file` to override default path

**Error Handling:**
- Wrap file handler setup in try/except
- Graceful fallback to console-only if file write fails
- Log warning if file logging unavailable
- Don't crash app if logging setup fails

---

## Failure Modes

**Log File Write Permission:**
- User lacks write permission to log directory
- Consequence: File logging unavailable
- Mitigation: Fall back to console-only logging

**Disk Space Exhaustion:**
- Disk fills despite rotation limits
- Consequence: Log writes fail
- Mitigation: Size limits prevent unbounded growth

---

## Acceptance Criteria

- [ ] `RotatingFileHandler` configured with 5MB size, 5 backups
- [ ] Log file created in `~/.whisper-dictation.log`
- [ ] Timestamp format includes milliseconds
- [ ] CLI argument `--log-level` functional
- [ ] Default log level is INFO
- [ ] Graceful fallback if file write fails
- [ ] Both file and console output work
- [ ] Initialization happens early in startup

---

## Implementation Context (Not Part of Spec)

**Current Implementation:**
```python
from logging.handlers import RotatingFileHandler
import logging

def setup_logging(log_level='INFO', log_file=None):
    if log_file is None:
        log_file = Path.home() / ".whisper-dictation.log"

    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5),
            logging.StreamHandler()
        ]
    )
```
