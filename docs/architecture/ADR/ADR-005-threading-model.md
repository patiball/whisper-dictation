# ADR-005: Threading model (Background recording + UI thread)

**Status**: Aktywna (wystarczająca dla use case)  
**Date**: 2025-01-10  
**Deciders**: Team  
**Tags**: architecture, concurrency, performance

## Context

Nagrywanie audio to blocking I/O operation. macOS menu bar UI musi być responsive. PyAudio działa w trybie blocking (stream.read()). Transkrypcja może trwać 5-10s (dla large model).

## Problem Statement

Jak zapewnić responsywność interfejsu użytkownika (menu bar) podczas długotrwałych operacji blokujących, takich jak nagrywanie audio i transkrypcja mowy?

## Decision

Threading model:
- **Main thread** - `rumps` event loop (UI)
- **Recording thread** - PyAudio stream reading
- **Transcription** - w recording thread (po zakończeniu nagrywania)

## Alternatives Considered

### 1. Single-threaded
**Odrzucone** - UI freeze

**Pros:**
- Prosta implementacja
- Brak problemów z synchronizacją

**Cons:**
- ❌ UI staje się niereaktywne podczas nagrywania/transkrypcji
- ❌ Złe doświadczenie użytkownika

### 2. Multiprocessing
**Odrzucone** - overkill (IPC overhead)

**Pros:**
- Izolacja procesów (brak GIL issues)
- Lepsze wykorzystanie wielu rdzeni CPU

**Cons:**
- ❌ Wysoki narzut komunikacji międzyprocesowej (IPC)
- ❌ Złożoność zarządzania procesami
- ❌ Większe zużycie pamięci

### 3. Async/await
**Odrzucone** - PyAudio nie jest async-friendly

**Pros:**
- Elegancki sposób na obsługę współbieżności
- Niskie zużycie zasobów

**Cons:**
- ❌ Wymaga, aby wszystkie biblioteki były async-friendly
- ❌ PyAudio jest blocking I/O
- ❌ Złożoność konwersji blocking code na async

### 4. Threading (CHOSEN)
**Wybrane** - balance simplicity/performance

**Pros:**
- ✅ UI pozostaje responsive during recording
- ✅ Prosty model (jeden thread per recording)
- ✅ Thread safety - recorder ma własny state
- ✅ Cancel possible przez `self.recording = False`
- ✅ Niskie zużycie zasobów w porównaniu do multiprocessing

## Consequences

### Positive

- ✅ UI pozostaje responsive during recording
- ✅ Prosty model (jeden thread per recording)
- ✅ Thread safety - recorder ma własny state
- ✅ Cancel possible przez `self.recording = False`
- ✅ Dobre doświadczenie użytkownika

### Negative

- ❌ Thread creation overhead (~1ms per start)
- ❌ Nie można anulować transkrypcji (once started, must finish)
- ❌ Race conditions możliwe (ale w praktyce nie występują)
- ❌ GIL limitations (though PyAudio releases GIL for I/O)
- ❌ Złożoność debugowania problemów współbieżności

### Neutral

- Wymaga ostrożnego zarządzania stanem współdzielonym
- Konieczność użycia `threading.Lock` dla krytycznych sekcji

## Implementation Notes

### Recorder Thread
```python
def start(self, language=None):
    # Nie blokuj UI thread
    thread = threading.Thread(target=self._record_impl, args=(language,))
    thread.start()

def _record_impl(self, language):
    # Ten kod działa w background thread
    while self.recording:
        data = stream.read(frames_per_buffer)  # Blocking OK
        frames.append(data)
    
    stream.close()
    self.sound_player.play_stop_sound()     # Hook 2
    
    # Transkrypcja też w tym samym thread
    self.transcriber.transcribe(audio_data, language)
```

### UI Thread
- `rumps.App.run()` blokuje główny wątek
- Wszystkie akcje menu i timery są obsługiwane w tym wątku
- Długotrwałe operacje (np. transkrypcja) muszą być delegowane do innych wątków

## Monitoring & Review

### Success Metrics
- Responsywność UI (brak zacięć)
- Brak race conditions w logach
- Stabilność aplikacji

### Review Schedule
- Re-evaluate if UI becomes unresponsive
- Review if new blocking operations are introduced
- Consider `asyncio` + `aiortc` for streaming transcription in the future

## Related

- [ADR-004: Rumps dla menu bar (zamiast native AppKit)](./ADR-004-rumps-for-menu-bar.md)
- [Concurrency Documentation](../CONCURRENCY.md) *(planned)*

## Notes

Obecnie: threading model działa świetnie. Thread pool nie potrzebny (max 1 recording at time).

**Update 2025-10-10**: Status remains active. The threading model is sufficient for the current use case.
