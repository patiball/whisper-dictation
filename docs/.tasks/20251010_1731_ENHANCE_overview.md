# Zadanie: Rozszerz PROJECT_OVERVIEW.md

## Data: 2025-10-10 17:31
## Priorytet: HIGH
## Źródło: User feedback - dokument zbyt podstawowy

## Problem
PROJECT_OVERVIEW.md jest za krótki (60 linii, 2.9KB) - brakuje szczegółów porównywanych z profesjonalną dokumentacją.

## Cel
Rozszerzyć dokument do poziomu profesjonalnej dokumentacji technicznej (~150-200 linii).

## Nowe sekcje do dodania

### 1. Wprowadzenie (na początku, przed "Cel aplikacji")
```markdown
# Przegląd projektu Whisper Dictation

## Wprowadzenie

Whisper Dictation to opensource'owa aplikacja do dyktowania dla macOS, wykorzystująca najnowocześniejszy model rozpoznawania mowy OpenAI Whisper. Projekt powstał jako odpowiedź na potrzebę prywatnego, offline'owego narzędzia do transkrypcji, które nie wymaga połączenia z chmurą ani wysyłania danych osobowych do zewnętrznych serwerów.

Aplikacja jest szczególnie zoptymalizowana dla procesorów Apple Silicon (M1/M2), oferując dwie implementacje: stabilną wersję Python oraz eksperymentalną wersję wykorzystującą whisper.cpp z akceleracją GPU.
```

### 2. Status projektu (po "Cel aplikacji")
```markdown
## Status projektu

- **Wersja aktualna**: 1.0 (beta)
- **Platformy**: macOS 11.0+ (Big Sur i nowsze)
- **Architektura**: Intel x86_64 + Apple Silicon (M1/M2)
- **Licencja**: MIT
- **Aktywny rozwój**: Tak
- **Repozytorium**: [GitHub](https://github.com/patiball/whisper-dictation)
```

### 3. Wymagania systemowe (po "Status projektu")
```markdown
## Wymagania systemowe

### Minimalne
- macOS 11.0 (Big Sur) lub nowszy
- 4 GB RAM
- 2 GB wolnego miejsca na dysku (dla modelu `base`)
- Mikrofon (wbudowany lub USB)
- Python 3.8+

### Zalecane
- macOS 13.0 (Ventura) lub nowszy
- 8 GB RAM (16 GB dla dużych modeli)
- 10 GB wolnego miejsca (dla modelu `large`)
- Wysokiej jakości mikrofon USB
- Apple Silicon (M1/M2) dla lepszej wydajności
- Python 3.10+

### Zależności systemowe
- PortAudio (`brew install portaudio`)
- LLVM (`brew install llvm`)
- Uprawnienia: Dostęp do mikrofonu + Accessibility (dla global hotkeys)
```

### 4. Architektura wysokopoziomowa (po "Struktura folderów")
```markdown
## Architektura wysokopoziomowa

### Warstwy systemu
1. **Prezentacja**: Rumps menu bar, ikony statusu
2. **Kontrola**: GlobalKeyListener, StatusBarApp, pętla zdarzeń
3. **Biznesowa**: Recorder, Transcriber, DeviceManager
4. **Dane**: Audio buffer, model cache
5. **Integracja**: PyAudio, PyTorch, Whisper API

Szczegółowy opis znajduje się w [ARCHITECTURE.md](./ARCHITECTURE.md).

### Przepływ danych
```
Użytkownik → Skrót klawiszowy → Recorder → Audio Buffer → Transcriber → Whisper → Tekst → Clipboard
```

Szczegółowe diagramy w [DATA_FLOW.md](./DATA_FLOW.md).
```

### 5. Modele Whisper (po "Kluczowe funkcjonalności")
```markdown
## Dostępne modele Whisper

| Model | Parametry | Wymagana pamięć | Szybkość | Dokładność |
|-------|-----------|-----------------|----------|------------|
| tiny | 39M | ~1 GB | Bardzo szybki | Podstawowa |
| base | 74M | ~1 GB | Szybki | Dobra |
| small | 244M | ~2 GB | Średni | Bardzo dobra |
| medium | 769M | ~5 GB | Wolny | Doskonała |
| large | 1550M | ~10 GB | Bardzo wolny | Najlepsza |

**Rekomendacja**: Model `base` dla codziennego użytku, `medium` dla wymagających zastosowań.
```

### 6. Ograniczenia znane (przed "Powiązane dokumenty")
```markdown
## Znane ograniczenia

- **M1/M2 GPU**: Wersja C++ (whisper.cpp) ma problemy z jakością - zalecana wersja Python (CPU)
- **Czas ładowania**: Duże modele (medium/large) mogą ładować się do 30 sekund
- **Brak realtime**: Transkrypcja rozpoczyna się po zakończeniu nagrywania
- **macOS tylko**: Brak wsparcia dla Windows/Linux
- **Słabsza jakość audio**: Przy złych warunkach akustycznych lub odległym mikrofonie

Szczegółowa lista w [TECHNICAL_DEBT.md](./TECHNICAL_DEBT.md).
```

### 7. Roadmap (przed "Powiązane dokumenty")
```markdown
## Roadmap

### v1.1 (Q1 2025)
- [ ] Poprawa jakości wersji C++ (GPU M1)
- [ ] Wsparcie dla większej liczby języków
- [ ] Eksport transkrypcji do pliku

### v1.2 (Q2 2025)
- [ ] Realtime transcription (streaming)
- [ ] Custom vocabulary/słownik
- [ ] Plugin system

### v2.0 (Q3 2025)
- [ ] Linux support
- [ ] Windows support (WSL)
- [ ] Web interface (opcjonalnie)

Szczegóły w [REFACTORING_PLAN](./TECHNICAL_DEBT.md#roadmap).
```

## Akcja
Zaktualizuj `/Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/PROJECT_OVERVIEW.md` dodając powyższe sekcje.

## Walidacja
- Dokument ma >150 linii
- Wszystkie nowe sekcje dodane
- Tabela modeli sformatowana poprawnie
- Linki wewnętrzne działają
- Styl spójny z resztą dokumentacji
