# Task: Przywrócenie odtwarzania dźwięków i naprawa skrótów klawiszowych
**Status**: Ready
**Priority**: High
**Complexity**: Medium

## Overview
Po tymczasowym wyłączeniu odtwarzania dźwięków w celu naprawy problemu z ucinaniem nagrania, konieczne jest przywrócenie tej funkcjonalności w sposób, który nie będzie blokował procesu nagrywania. Dodatkowo, należy naprawić niedziałające skróty klawiszowe do rozpoczynania i zatrzymywania nagrywania.

## Acceptance Criteria
- [ ] Odtwarzanie dźwięku przy rozpoczęciu i zakończeniu nagrywania musi zostać przywrócone.
- [ ] Odtwarzanie dźwięku nie może blokować głównego wątku i powodować opóźnień w nagrywaniu.
- [ ] Skróty klawiszowe do rozpoczynania i zatrzymywania nagrywania muszą działać poprawnie.
- [ ] Aplikacja musi pozostać stabilna i wydajna.

## File Changes Required
- **`whisper-dictation.py`**: Zmodyfikowanie klasy `Recorder` w celu asynchronicznego odtwarzania dźwięków. Zmiany w `GlobalKeyListener` lub `DoubleCommandKeyListener` w celu naprawy skrótów.
- **`recorder.py`**: Potencjalne zmiany w celu lepszej integracji z `whisper-dictation.py`.

## Integration Points
Zmiany wpłyną na interakcję użytkownika z aplikacją, zarówno poprzez dźwięki, jak i skróty klawiszowe. Należy przetestować oba te aspeky.
