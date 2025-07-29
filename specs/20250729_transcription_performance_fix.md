# Task: Optymalizacja procesu transkrypcji w celu uniknięcia podwójnego przetwarzania
**Status**: Ready
**Priority**: High
**Complexity**: Medium

## Overview
Obecny proces transkrypcji w `transcriber.py` jest nieefektywny, ponieważ wykonuje transkrypcję dwukrotnie, gdy język nie jest określony, ale istnieje lista dozwolonych języków. Pierwsze przejście służy do wykrywania języka, a drugie do właściwej transkrypcji. To podwaja czas przetwarzania i powoduje znaczne spowolnienie aplikacji.

## Acceptance Criteria
- [ ] Metoda `transcribe` w `transcriber.py` powinna wywoływać `self.model.transcribe()` tylko raz na jedno wejście audio.
- [ ] Detekcja języka powinna nadal działać poprawnie, gdy język nie jest określony.
- [ ] Jeśli podano `allowed_languages`, ostateczna transkrypcja powinna uwzględniać tę listę bez ponownego przetwarzania dźwięku.
- [ ] Istniejące testy muszą zakończyć się powodzeniem po wprowadzeniu zmiany.
- [ ] Wydajność aplikacji powinna zauważalnie wzrosnąć, a czas transkrypcji powinien zostać zredukowany o około połowę.

## File Changes Required
- **`transcriber.py`**: Zmodyfikowanie metody `transcribe` w celu wyeliminowania podwójnego przetwarzania.

## Integration Points
Zmiana wpłynie na każdą część aplikacji, która wywołuje `SpeechTranscriber.transcribe()`, głównie na logikę w `whisper-dictation.py` oraz na testy jednostkowe i wydajnościowe.
