# Fix: Dodaj docs/modules/README.md

## Data: 2025-10-10 17:26
## Priorytet: HIGH
## QA Issue: #3

## Problem
Brak pliku README.md w katalogu `docs/modules/` - trudno zorientować się w strukturze dla nowych osób.

## Cel
Utworzyć `docs/modules/README.md` wyjaśniający strukturę i konwencje dokumentacji modułowej.

## Zawartość

```markdown
# Dokumentacja modułowa

Ten katalog zawiera szczegółową dokumentację poszczególnych modułów projektu whisper-dictation.

## Cel dokumentacji modułowej

Każdy moduł ma osobny plik dokumentacji zawierający:
- Odpowiedzialność modułu
- Publiczne API (klasy, metody)
- Zależności (depends on / depended by)
- Przykłady użycia
- TODO/FIXME z kodu
- Sugestie refaktoryzacji

## Struktura dokumentu modułu

### Szablon:

\`\`\`markdown
# Moduł: [Nazwa]

## Odpowiedzialność
[1-2 zdania opisujące cel modułu]

## Publiczne API
[Lista klas i ich metod]

## Zależności
- **Zależy od**: X, Y, Z
- **Używany przez**: A, B, C

## Przykład użycia
\`\`\`python
# Przykład z rzeczywistego kodu
\`\`\`

## TODO/FIXME
[Lista z komentarzy w kodzie]

## Powiązane dokumenty
- [API Interfaces](../API_INTERFACES.md)
- [Architektura](../ARCHITECTURE.md)
\`\`\`

## Istniejące moduły

| Moduł | Odpowiedzialność | Dokumentacja |
|-------|------------------|--------------|
| recorder | Nagrywanie audio z mikrofonu | [recorder.md](./recorder.md) |
| transcriber | Transkrypcja audio używając Whisper | [transcriber.md](./transcriber.md) |
| device_manager | Zarządzanie urządzeniami M1/M2 | [device_manager.md](./device_manager.md) |

## Dodawanie nowego modułu

1. Utwórz plik `[nazwa_modułu].md` w tym katalogu
2. Użyj szablonu powyżej
3. Dodaj wpis do tabeli w tym README
4. Zaktualizuj [MODULES.md](../MODULES.md)
5. Dodaj link w sekcji "Powiązane dokumenty" w [API_INTERFACES.md](../API_INTERFACES.md)

## Powiązane dokumenty

- [MODULES.md](../MODULES.md) - Indeks wszystkich modułów
- [API_INTERFACES.md](../API_INTERFACES.md) - Publiczne interfejsy
- [ARCHITECTURE.md](../ARCHITECTURE.md) - Architektura systemu
```

## Akcja
Utwórz plik `/Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/modules/README.md` z powyższą zawartością.

## Walidacja
- Plik utworzony w docs/modules/
- Zawiera szablon dokumentacji
- Lista istniejących modułów jest kompletna
- Linki działają
