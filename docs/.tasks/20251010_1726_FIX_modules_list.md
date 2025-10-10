# Fix: Uzupełnij MODULES.md

## Data: 2025-10-10 17:26
## Priorytet: HIGH  
## QA Issue: #6

## Problem
`docs/MODULES.md` nie wymienia wszystkich modułów - brakuje `mps_optimizer.py` i głównej aplikacji.

## Cel
Dodać brakujące moduły do tabeli w MODULES.md.

## Akcja
Zaktualizuj tabelę modułów w `/Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/MODULES.md` dodając:

### 1. mps_optimizer  
**Lokalizacja w pliku**: Po device_manager w tabeli

```markdown
| mps_optimizer | Optymalizacje M1/M2 GPU i obsługa błędów MPS | *[Zintegrowane z device_manager.md](./modules/device_manager.md)* |
```

### 2. whisper-dictation (główna aplikacja)
**Lokalizacja w pliku**: Na początku tabeli (przed recorder)

```markdown
| whisper-dictation | Główna aplikacja - punkt wejścia, StatusBarApp, pętla zdarzeń | *W przygotowaniu* |
```

## Oczekiwana tabela po zmianach:

```markdown
| Moduł | Odpowiedzialność | Dokumentacja |
|-------|------------------|--------------|
| whisper-dictation | Główna aplikacja - punkt wejścia, StatusBarApp, pętla zdarzeń | *W przygotowaniu* |
| recorder | Nagrywanie audio z mikrofonu | [recorder.md](./modules/recorder.md) |
| transcriber | Transkrypcja audio używając Whisper | [transcriber.md](./modules/transcriber.md) |
| device_manager | Zarządzanie urządzeniami M1/M2 | [device_manager.md](./modules/device_manager.md) |
| mps_optimizer | Optymalizacje M1/M2 GPU i obsługa błędów MPS | *Zintegrowane z device_manager.md* |
```

## Dodatkowe
Jeśli w sekcji "Graf zależności" trzeba zaktualizować - dodaj że whisper-dictation używa wszystkich innych modułów.

## Walidacja
- Tabela zawiera 5 wpisów
- Kolejność logiczna (główna app → moduły)
- Linki poprawne
- Format spójny
