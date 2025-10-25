# Epic: Wdrażanie Lessons Learned z macos-dictate

**ID**: 13-00-00
**Status**: Draft
**Priority**: High
**Created**: 2025-10-25
**Target Sprint**: Next (2-3 dni)

---

## Wprowadzenie

Ten epic implementuje 5 filarów stabilności i profesjonalizmu oprogramowania z projektu `macos-dictate`, mających na celu stworzenie solidnego fundamentu dla `whisper-dictation` jako produkcyjnej aplikacji macOS działającej w tle.

## Cel Ogólny

**WHAT**: Implementacja mechanizmów zapobiegających konfliktom zasobów, awariom strumienia audio, brakowi uprawnień, oraz zapewnienie kompleksowego logowania diagnostycznego.

**WHY**: Aplikacja działająca w tle wymaga niezawodności równej poziomowi produkcyjnemu. Bez tych filarów narażeni jesteśmy na:
- Wiele instancji jednocześnie (konflikty mikrofonu, unpredictable behavior)
- Zawieszenia strumienia audio (dead application)
- Zabiłości zasobów (zombie procesy, memory leaks)
- Brak diagnozy problemów (niemożliwy debug)

---

## User Stories (Planned)

- [ ] **[13-01-00]** Lock File + Signal Handling - Zapobieganie konfliktom wieloinstancji i prawidłowe czyszczenie
- [ ] **[13-02-00]** Microphone Proactive Check - Test dostępu do mikrofonu na starcie
- [ ] **[13-03-00]** Audio Stream Watchdog - Monitorowanie i restart zawieszenia strumienia
- [ ] **[13-04-00]** Enhanced Logging & Diagnostics - Rozszerzone logi dla diagnostyki
- [ ] **[13-05-00]** Lessons Learned Tests Suite - Kompleksowe testy TDD dla wszystkich filarów

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                  whisper-dictation                      │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────┐         ┌────────────────────┐   │
│  │  Lock File       │         │  Signal Handler    │   │
│  │  [13-01-00]      │◄────────│  [13-01-00]        │   │
│  └──────────────────┘         └────────────────────┘   │
│           ▲                             ▲               │
│           │                             │               │
│  ┌────────┴───────────┬─────────────────┴────────────┐  │
│  │                    │                              │  │
│  ▼                    ▼                              ▼  │
│ ┌──────────────────────────────────────────────────┐   │
│ │          Enhanced Logging System                 │   │
│ │          (Central diagnostic hub)                │   │
│ │          [13-04-00] + [13-02-00]                │   │
│ └──────────────────────────────────────────────────┘   │
│  ▲         ▲                       ▲                    │
│  │         │                       │                    │
│  │         ▼                       ▼                    │
│  │  ┌──────────────┐      ┌──────────────────┐        │
│  │  │ Microphone   │      │  Audio Watchdog  │        │
│  │  │ Check        │      │  Thread          │        │
│  │  │ [13-02-00]   │      │  [13-03-00]      │        │
│  │  └──────────────┘      └──────────────────┘        │
│  │                                                     │
│  └──────────────────────────────────────────────────┘  │
│           ▲                              ▲             │
│           │                              │             │
│  ┌────────┴──────────────┬───────────────┴──────────┐ │
│  │                       │                          │ │
│  ▼                       ▼                          ▼ │
│ ┌─────────────────────────────────────────────────┐  │
│ │  Core Recording/Transcription Loop              │  │
│ │  (Now with stability & diagnostics)             │  │
│ └─────────────────────────────────────────────────┘  │
│                                                       │
└─────────────────────────────────────────────────────────┘
```

---

## Implementacja w Dwóch Wersjach

Wszystkie zmiany dotyczą OBU wersji aplikacji:
- `whisper-dictation.py` (Python + PyTorch)
- `whisper-dictation-fast.py` (C++ + whisper.cpp via whisper-cli)

Utrzymanie parity między wersjami jest KRYTYCZNE.

---

## Success Criteria (Epic Level)

- [x] **Zero konfliktów wieloinstancji** - druga instancja shutdownuje gracefully
- [x] **Strumień audio praktycznie nigdy się nie zawieszenia** - watchdog restartuje w <2s
- [x] **Brak memory leaks** - zasoby prawidłowo czyszczone przy shutdown
- [x] **Każdy błąd diagnosowalny** - wszystkie eventy zalogowane do pliku
- [x] **TDD compliance** - testy piszemy PRZED implementacją
- [x] **Brak regresji** - wszystkie istniejące testy przechodzą

---

## Key Design Decisions

### 1. Lock File Location
- **Gdzie**: `~/.whisper-dictation.lock` (hidden, user home)
- **Why**: Persistent across shutdowns, easy cleanup, standard Unix pattern

### 2. Logging Location
- **Gdzie**: `~/.whisper-dictation.log` (rotating, 5 files x 5MB)
- **Why**: User home hidden files = standard for background apps, rotation = disk space safe

### 3. Watchdog Timeout
- **Value**: 10 seconds bez heartbeatu = audio stalled
- **Why**: Enough time dla slow transcription, short enough to detect hang quickly

### 4. Thread Safety
- **Approach**: Python's `threading.Lock` dla shared resources
- **Why**: Simple, built-in, no new dependencies

---

## Implementation Phases

### Phase 1: Fundamenty (Lock + Signals)
**Duration**: 60-70 min
**Value**: Stabilność operacyjna
**User Stories**: [13-01-00], [13-02-00]

### Phase 2: Odporność (Watchdog)
**Duration**: 45-60 min
**Value**: Long-running stability
**User Stories**: [13-03-00], [13-04-00]

### Phase 3: Testowanie & Walidacja
**Duration**: 30-40 min
**Value**: Confidence + CI/CD
**User Stories**: [13-05-00]

---

## Integration with Current Roadmap

```
TERAZ (Oct 25):  [13-*] Lessons Learned (2.5h)
  ↓
NASTĘPNIE:       [10-00] Transcription Timestamps (0.75h)
  ↓
PÓŹNIEJ:         [09-00] macOS Portability (0.75h)
  ↓
BACKLOG:         Performance benchmarking (slow vs fast)
```

**Rationale**: Lessons Learned zapewnia stabilny fundament dla wszystkich kolejnych features.

---

## Brittleness Analysis (Epic Level)

### 1. Multi-Instance Conflicts
**Failure Mode**: Dwie instancje czytają z tego samego mikrofonu
- **Detection**: Licznik otwartych stream = 2+
- **Consequence**: Audio corruption, unpredictable behavior
- **Prevention**: Lock file checked on startup
- **Recovery**: Second instance exits gracefully

### 2. Audio Stream Stall
**Failure Mode**: Strumień zawieszony, aplikacja "żyje" ale nie nagrawa
- **Detection**: Brak heartbeat > 10s
- **Consequence**: User czeka bez feedback, no transcription
- **Prevention**: Watchdog thread monitors
- **Recovery**: Automatic restart lub user force-quit

### 3. Resource Leak (Lock File)
**Failure Mode**: Lock file nie usunięty, następny start nie działa
- **Detection**: Old lock file exists but PID doesn't
- **Consequence**: Can't start application
- **Prevention**: Check PID validity before blocking
- **Recovery**: Auto-cleanup if process doesn't exist

### 4. Microphone Permission Changes
**Failure Mode**: User removes microphone permission while app running
- **Detection**: sounddevice.check_input_settings() fails mid-run
- **Consequence**: Recording fails silently
- **Prevention**: Proactive check on startup
- **Recovery**: Graceful error message in logs

### 5. Logging Disk Space
**Failure Mode**: Log file grows unbounded → fills disk
- **Detection**: Available disk < 100MB
- **Consequence**: Application fails, no logging
- **Prevention**: RotatingFileHandler (5 x 5MB)
- **Recovery**: Old logs auto-deleted

### 6. Signal Handling Race Condition
**Failure Mode**: Ctrl+C during cleanup → partial resource release
- **Detection**: File descriptor check after shutdown
- **Consequence**: Zombie processes, leaked streams
- **Prevention**: Signal handler sets flags atomically
- **Recovery**: atexit handlers registered in correct order

---

## Dependencies (No New External)

- `psutil` - PID existence check (already in requirements)
- `threading` - Watchdog thread (stdlib)
- `logging` - Rotating file handler (stdlib)
- `atexit` - Cleanup on exit (stdlib)
- `signal` - Signal handling (stdlib)

---

## Testing Strategy (TDD-First)

Każda User Story zawiera:
1. **Test Cases** - napisane PRZED kodem
2. **Unit Tests** - dla poszczególnych komponentów
3. **Integration Tests** - flow end-to-end
4. **Manual Scenarios** - real-world testing

Więcej szczegółów w [13-05-00] Tests Suite spec.

---

## Rollout & Validation

### Phase 1 Rollout (Lock + Signals)
```
1. Write all unit tests (TDD)
2. Implement lock file mechanism
3. Implement signal handlers
4. Run tests locally
5. Manual test 2 instances scenario
6. Code review
```

### Phase 2 Rollout (Watchdog)
```
1. Write watchdog tests
2. Implement watchdog thread
3. Integrate with recording loop
4. Run full test suite
5. Manual stress test (long recordings)
6. Code review
```

### Phase 3 Validation (All Together)
```
1. Run full TDD test suite (pytest)
2. Manual multi-scenario testing
3. Verify no regressions in existing features
4. Update README with new logging locations
5. Final code review + merge
```

---

## Files Modified (High-Level)

```
whisper-dictation.py       ← Lock file + Signal handlers + Watchdog + Logging
whisper-dictation-fast.py  ← Same changes (sync both)
recorder.py                ← TDD recorder sync
tests/                     ← New test files (TDD)
```

---

## Success Metrics (Measurable)

- ✅ 0% failed startup due to lock file conflicts (automated test)
- ✅ 100% signal handlers cleanup resources (manual + CI test)
- ✅ Watchdog detects stall <2 seconds (stress test)
- ✅ Log rotation works: 5 files max, each <5MB (CI test)
- ✅ All TDD tests pass (100% coverage for new code)
- ✅ Existing tests still pass (no regressions)

---

## Out of Scope (Future Enhancements)

- [ ] Remote logging (send errors to server)
- [ ] Structured JSON logging
- [ ] Performance metrics logging (transcription time)
- [ ] Watchdog with ML-based stall detection
- [ ] Automatic recovery strategies (restart model, fallback device)

---

## Timeline Estimate

| Phase | Task | Duration | Owner |
|-------|------|----------|-------|
| 1 | [13-01-00] Lock + Signals | 20-25 min | Claude |
| 1 | [13-02-00] Microphone Check | 10-15 min | Claude |
| 2 | [13-03-00] Watchdog | 30-40 min | Claude |
| 2 | [13-04-00] Enhanced Logging | 15-20 min | Claude |
| 3 | [13-05-00] Tests Suite | 30-40 min | Claude |
| 3 | Code Review & Validation | 15-20 min | User |
| **TOTAL** | | **135-170 min** | |

---

## Acceptance Criteria (Epic-Level)

- [ ] Wszystkie 5 User Stories mają status "Completed"
- [ ] Brak otwartych blockerów w żadnej US
- [ ] TDD test coverage >90% dla nowych komponentów
- [ ] Integracyjne testy przechodzą w CI
- [ ] Dokumentacja README zaktualizowana o nowe logi lokacje
- [ ] Kod review approved przez maintainera

---

## Next Steps (For User Review)

1. User zatwierdza Epic plan
2. Claude tworzy 5 User Story specs ([13-01-00] do [13-05-00])
3. Dla każdej US:
   - Szczegółowe acceptance criteria
   - Test cases (TDD-first)
   - Design z pseudo-kodem
   - Brittleness analysis
   - File changes required
4. User zatwierdza specs
5. Implementacja w kolejności: [13-01-00] → [13-02-00] → [13-03-00] → [13-04-00] → [13-05-00]

---

## References

- Memory Bank: lessons_learned/recommendations_from_macos_dictate.md
- CLAUDE.md: TDD patterns, spec hierarchy
- Existing specs: [08-00-00] (audio clipping), [10-00-00] (timestamps)

