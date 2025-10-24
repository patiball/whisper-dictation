# Backlog: Centralized Logging System

**Status**: Backlog
**Priority**: Medium
**Complexity**: Medium
**Estimate**: 1-2 hours

## Problem

Currently, logging is scattered across the codebase using `print()` statements:
- No log levels (DEBUG, INFO, WARNING, ERROR)
- Cannot easily disable/enable verbose output
- Timestamps manually added to each print statement
- No file logging capability
- Hard to filter console output
- No structured logging format

**Examples of current scattered logging:**
```python
print(f'{get_timestamp()} Listening...')
print(f'{get_timestamp()} Transcription complete')
print("Pusty rezultat transkrypcji")
print(f"Błąd whisper.cpp: {result.stderr}")
```

## Goal

Create a centralized logging system with:
- Consistent log levels (DEBUG, INFO, WARNING, ERROR)
- Automatic timestamp formatting
- Configurable verbosity via CLI flags
- Optional file output for diagnostics
- Structured format for easy parsing

## Proposed Solution

Create `Logger` class or use Python's built-in `logging` module with custom configuration:

```python
from logging import getLogger, StreamHandler, FileHandler, Formatter

class WhisperLogger:
    def __init__(self, name, level='INFO', log_file=None):
        self.logger = getLogger(name)
        self.logger.setLevel(level)

        # Console handler with timestamps
        console_handler = StreamHandler()
        console_handler.setFormatter(
            Formatter('[%(asctime)s.%(msecs)03d] %(levelname)s: %(message)s',
                     datefmt='%H:%M:%S')
        )
        self.logger.addHandler(console_handler)

        # Optional file handler
        if log_file:
            file_handler = FileHandler(log_file)
            file_handler.setFormatter(...)
            self.logger.addHandler(file_handler)

    def info(self, msg): ...
    def debug(self, msg): ...
    def warning(self, msg): ...
    def error(self, msg): ...
```

**Usage:**
```python
logger = WhisperLogger('whisper-dictation', level='INFO')

logger.info('Listening...')           # [14:23:45.123] INFO: Listening...
logger.debug('Buffer size: 512')      # Only shown if level=DEBUG
logger.error('Transcription failed')  # [14:23:51.789] ERROR: Transcription failed
```

## Acceptance Criteria

- [ ] `Logger` class or configured Python logging module
- [ ] Log levels: DEBUG, INFO, WARNING, ERROR
- [ ] Automatic timestamp formatting (HH:MM:SS.mmm)
- [ ] CLI flags: `--log-level {DEBUG,INFO,WARNING,ERROR}`, `--log-file PATH`
- [ ] Replace all `print()` statements with logger calls
- [ ] Backward compatible console output (INFO level by default)
- [ ] Optional file logging for diagnostics
- [ ] Works in both whisper-dictation.py and whisper-dictation-fast.py

## File Changes Required

**New file: `logger.py`**
- Logger class or configuration

**whisper-dictation.py and whisper-dictation-fast.py:**
- Import logger
- Replace `print()` with `logger.info()`, `logger.debug()`, etc.
- Add CLI arguments: `--log-level`, `--log-file`
- Pass logger to components (Recorder, SpeechTranscriber, StatusBarApp)

**Other affected files:**
- `recorder.py` (TDD module)
- `transcriber.py` (TDD module)
- Any other modules using print()

## Benefits

1. **Verbosity Control**: `--log-level DEBUG` for diagnostics, `WARNING` for quiet mode
2. **File Logging**: Save logs for bug reports (`--log-file ~/whisper-debug.log`)
3. **Structured Output**: Consistent format, easier to parse/grep
4. **Maintainability**: Single source of truth for logging configuration
5. **Performance**: Can disable debug logging in production

## Examples

**Debug mode:**
```bash
poetry run python whisper-dictation-fast.py --k_double_cmd --log-level DEBUG
```

Output:
```
[14:23:45.123] INFO: Listening...
[14:23:45.124] DEBUG: Opening PyAudio stream with buffer=512
[14:23:45.125] DEBUG: Warm-up buffers: 2
[14:23:48.456] INFO: Transcribing...
[14:23:48.457] DEBUG: Running whisper-cli with model=base
[14:23:51.789] INFO: Transcription complete
[14:23:51.790] DEBUG: Transcribed text length: 42 chars
[14:23:51.790] INFO: Typing text...
```

**Quiet mode:**
```bash
poetry run python whisper-dictation-fast.py --k_double_cmd --log-level WARNING
```

Output:
```
(only warnings/errors shown)
```

## Future Enhancements (Out of Scope)

- Structured logging (JSON format) for machine parsing
- Log rotation for file output
- Remote logging (send errors to server)
- Performance metrics logging (transcription time, typing speed)

## Notes

- Use Python's built-in `logging` module (stdlib, no new dependencies)
- Consider thread-safety for logging from Recorder thread
- Preserve current timestamp format `[HH:MM:SS.mmm]` for consistency
- Default to INFO level to maintain current user experience

---

**Expected Outcome:** Professional, configurable logging system replacing scattered print() statements, enabling better diagnostics and user control over verbosity.
