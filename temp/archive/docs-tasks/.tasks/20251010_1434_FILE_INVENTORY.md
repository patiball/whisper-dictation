# Zadanie: FILE_INVENTORY.md

## Data: 2025-10-10 14:34
## Priorytet: LOW

## Cel
Utworzyć `/Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/FILE_INVENTORY.md`

## Zawartość

### 1. Wprowadzenie
Inwentarz wszystkich plików źródłowych projektu.

### 2. Pliki główne

| Plik | Typ | Linie | Opis |
|------|-----|-------|------|
| whisper-dictation.py | Main | ~500 | Główna aplikacja (Python) |
| whisper-dictation-fast.py | Main | ~400 | Implementacja C++ |
| recorder.py | Module | ~200 | Nagrywanie audio |
| transcriber.py | Module | ~300 | Transkrypcja |
| device_manager.py | Module | ~250 | Zarządzanie urządzeniami |
| ... | | | |

### 3. Testy
Lista plików testowych.

### 4. Skrypty
Lista skryptów pomocniczych.

### 5. Konfiguracja
- pyproject.toml
- requirements.txt
- .gitignore

### 6. Pliki do zbadania
Lista plików z `[TO INVESTIGATE]` dla niejasnych elementów.

## Wymagania
- Automatycznie wygenerowana tabela
- Oblicz linie kodu: `wc -l *.py`
- Dodaj krótki opis dla każdego pliku
