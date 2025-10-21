# Przegląd projektu Whisper Dictation

## Wprowadzenie

Whisper Dictation to opensource'owa aplikacja do dyktowania dla macOS, wykorzystująca najnowocześniejszy model rozpoznawania mowy OpenAI Whisper. Projekt powstał jako odpowiedź na potrzebę prywatnego, offline'owego narzędzia do transkrypcji, które nie wymaga połączenia z chmurą ani wysyłania danych osobowych do zewnętrznych serwerów.

Aplikacja jest szczególnie zoptymalizowana dla procesorów Apple Silicon (M1/M2), oferując dwie implementacje produkcyjne: wersję Python (CPU) oraz wersję C++ wykorzystującą whisper.cpp z pełną akceleracją GPU przez Metal.

## Cel aplikacji

Wielojęzyczna aplikacja dyktowania oparta na potężnym modelu OpenAI Whisper ASR, zapewniająca dokładną i efektywną konwersję mowy na tekst w dowolnej aplikacji. Aplikacja działa w tle, uruchamiana przez skróty klawiszowe, i funkcjonuje całkowicie offline bez udostępniania danych, gwarantując prywatność użytkownika.

## Status projektu

- **Wersja aktualna**: 1.0 (beta)
- **Platformy**: macOS 11.0+ (Big Sur i nowsze)
- **Architektura**: Intel x86_64 + Apple Silicon (M1/M2)
- **Licencja**: MIT
- **Aktywny rozwój**: Tak
- **Repozytorium**: [GitHub](https://github.com/patiball/whisper-dictation)

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

## Stos technologiczny

- **Python 3.x** - język programowania
- **OpenAI Whisper** - silnik rozpoznawania mowy (ASR)
  - Wersja Python (produkcyjna, CPU)
  - Wersja whisper.cpp (produkcyjna, GPU M1/M2 przez Metal)
- **PyTorch** - framework uczenia maszynowego
- **PyAudio / PortAudio** - obsługa nagrywania audio
- **Poetry** - zarządzanie zależnościami
- **Pynput** - globalne skróty klawiszowe
- **Rumps** - integracja z paskiem menu macOS
- **macOS** - platforma docelowa (wsparcie dla M1/M2)

## Struktura folderów

Projekt `whisper-dictation` jest zorganizowany w logiczne katalogi, które odzwierciedlają jego modułową architekturę. Główne katalogi to:

- `docs/`: Zawiera całą dokumentację projektu, w tym diagramy, kontekst i specyfikacje.
- `memory-bank/`: Przechowuje bank pamięci agenta AI, z podstawowymi plikami dokumentacji i specyfikacjami.
- `scripts/`: Skrypty pomocnicze do automatyzacji i konfiguracji.
- `specs/`: Specyfikacje funkcjonalne i techniczne.
- `tests/`: Testy jednostkowe i integracyjne, wraz z próbkami audio.
- Główne pliki źródłowe, takie jak `whisper-dictation.py`, `recorder.py`, `transcriber.py`, `device_manager.py`.

Szczegółowy inwentarz plików i ich przeznaczenie znajduje się w dokumencie [FILE_INVENTORY.md](./FILE_INVENTORY.md).

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

## Kluczowe funkcjonalności

Aplikacja oferuje szereg kluczowych funkcjonalności, które zapewniają wydajne i prywatne dyktowanie:

- **Wielojęzyczne rozpoznawanie mowy**: Wykorzystuje model OpenAI Whisper do dokładnej transkrypcji w wielu językach, z automatyczną detekcją języka.
- **Działanie w tle i integracja z macOS**: Aplikacja działa jako demon systemowy, dostępny przez konfigurowalne skróty klawiszowe i zintegrowany z paskiem menu macOS.
- **Całkowicie offline**: Wszystkie operacje przetwarzania mowy na tekst odbywają się lokalnie, gwarantując pełną prywatność i brak wysyłania danych.
- **Optymalizacja dla Apple Silicon (M1/M2)**: Inteligentne zarządzanie urządzeniami (CPU/GPU) zapewnia optymalną wydajność na procesorach Apple Silicon.
- **System wstawiania tekstu**: Transkrybowany tekst jest automatycznie wklejany do aktywnej aplikacji, z inteligentną obsługą formatowania.

Szczegółowe informacje na temat dostępnych modeli Whisper i ich charakterystyki znajdują się w sekcji [Dostępne modele Whisper](#dostępne-modele-whisper) oraz w dokumentacji modułu [SpeechTranscriber](../docs/modules/transcriber.md).
Więcej o integracji z systemem macOS i personalizacji skrótów znajdziesz w [MODULES.md](../MODULES.md) oraz [API_INTERFACES.md](./API_INTERFACES.md).

## Dostępne modele Whisper

| Model | Parametry | Wymagana pamięć | Szybkość | Dokładność |
|-------|-----------|-----------------|----------|------------|
| tiny | 39M | ~1 GB | Bardzo szybki | Podstawowa |
| base | 74M | ~1 GB | Szybki | Dobra |
| small | 244M | ~2 GB | Średni | Bardzo dobra |
| medium | 769M | ~5 GB | Wolny | Doskonała |
| large | 1550M | ~10 GB | Bardzo wolny | Najlepsza |

**Rekomendacja**: Model `base` dla codziennego użytku, `medium` dla wymagających zastosowań.

### Opcje modeli i implementacji

Aplikacja wspiera wybór różnych modeli Whisper oraz oferuje dwie implementacje:

- **Wybór modeli Whisper**: Możliwość wyboru spośród modeli `tiny`, `base`, `small`, `medium`, `large`, z różnymi kompromisami między szybkością a dokładnością.
- **Dwie implementacje produkcyjne**:
  - **Python**: Stabilna implementacja, wykorzystująca CPU (wszystkie platformy).
  - **C++ (whisper.cpp)**: Stabilna implementacja z akceleracją GPU M1/M2 przez Metal (✅ problemy jakości rozwiązane, październik 2025).

Szczegóły dotyczące konfiguracji modeli i implementacji znajdują się w [transcriber.md](../docs/modules/transcriber.md) oraz [API_INTERFACES.md](./API_INTERFACES.md).

### Integracja i personalizacja

Aplikacja integruje się z systemem macOS i oferuje szerokie możliwości personalizacji:

- **Integracja z systemem macOS**: Ikona w menu bar z menu kontekstowym, dźwięki systemowe jako feedback.
- **Automatyczne wykrywanie języka**: Inteligentne rozpoznawanie języka mówionego, wspierające wielojęzyczne dyktowanie.
- **Zarządzanie urządzeniami**: Optymalizacja dla Apple Silicon (M1/M2) z automatycznym wykrywaniem akceleratorów.
- **Konfigurowalne skróty**: Możliwość dostosowania klawiszy aktywacji dla elastycznego użytkowania.

Więcej informacji o integracji i personalizacji znajdziesz w [MODULES.md](../docs/MODULES.md) oraz [API_INTERFACES.md](./API_INTERFACES.md).

### System wstawiania tekstu

Transkrybowany tekst jest automatycznie wklejany do aktywnej aplikacji, z inteligentną obsługą formatowania i kontrolą jakości. Szczegóły implementacji znajdują się w [DATA_FLOW.md](./DATA_FLOW.md).

## Architektura techniczna

Architektura techniczna aplikacji opiera się na modułowej strukturze, która zapewnia elastyczność, skalowalność i łatwość utrzymania. Kluczowe aspekty to:

- **Przepływ danych audio**: Od mikrofonu, przez przetwarzanie, transkrypcję, aż po wstawienie tekstu do aktywnej aplikacji.
- **Komponenty systemu**: Główne moduły takie jak `recorder.py`, `transcriber.py`, `device_manager.py` oraz główna aplikacja, każdy z jasno zdefiniowaną odpowiedzialnością.
- **Kluczowe technologie**: Wykorzystanie OpenAI Whisper, PyTorch, PyAudio, Pynput i Rumps do realizacji funkcjonalności.

Szczegółowy opis architektury, przepływu danych i komponentów systemu znajduje się w [ARCHITECTURE.md](./ARCHITECTURE.md) oraz [DATA_FLOW.md](./DATA_FLOW.md).

## Charakterystyka wydajnościowa

### Wydajność modeli Whisper

| Model  | Rozmiar | RAM    | Czas transkrypcji* | Dokładność |
|--------|---------|--------|-------------------|------------|
| Tiny   | 75MB    | ~1GB   | ~2-3s             | Dobra      |
| Base   | 140MB   | ~1GB   | ~3-5s             | Bardzo dobra |
| Small  | 470MB   | ~2GB   | ~8-12s            | Wysoka     |
| Medium | 1.5GB   | ~5GB   | ~20-30s           | Bardzo wysoka |
| Large  | 3GB     | ~10GB  | ~40-60s           | Najwyższa  |

*Dla 30-sekundowego fragmentu audio na M1 Pro

### Zużycie zasobów

**W trybie czuwania:**
- CPU: <1%
- RAM: ~100-200MB
- Brak aktywności GPU

**Podczas transkrypcji (model Base):**
- CPU: 80-150% (zależnie od konfiguracji)
- RAM: ~1.5GB
- GPU: Opcjonalne przyspieszenie na M1/M2

### Opóźnienia

- **Czas reakcji**: <100ms od naciśnięcia skrótu do rozpoczęcia nagrywania
- **Latencja transkrypcji**: Zależy od modelu i długości nagrania
- **Wstawianie tekstu**: <50ms po zakończeniu transkrypcji

### Optymalizacja dla Apple Silicon

- Natywne wsparcie dla architektury ARM64
- Wykorzystanie Neural Engine (eksperymentalne)
- Optymalizacja wykorzystania unified memory
- Efektywne zarządzanie energią

## Scenariusze użycia

### Pisanie emaili
- Szybkie dyktowanie wiadomości bez dotykania klawiatury
- Idealne do długich odpowiedzi lub korespondencji
- Wsparcie dla języka formalnego i nieformalnego

### Tworzenie dokumentacji
- Efektywne dokumentowanie procesów i procedur
- Przyspieszenie pisania raportów i specyfikacji
- Transkrypcja notatek z spotkań

### Notowanie w czasie spotkań
- Szybkie przechwytywanie kluczowych punktów
- Transkrypcja pytań i odpowiedzi
- Dokumentowanie decyzji i action items

### Komentarze w kodzie
- Dyktowanie opisów funkcji i klas
- Tworzenie dokumentacji inline
- Wyjaśnianie złożonej logiki biznesowej

### Wykorzystanie ogólne
- Wypełnianie formularzy online
- Pisanie postów w mediach społecznościowych
- Tworzenie list zadań i przypomnień
- Dyktowanie wyszukiwań i zapytań

## Opcje konfiguracji

### Dostępne ustawienia

**Wybór modelu:**
- Wybór między modelami tiny/base/small/medium/large
- Automatyczne pobieranie brakujących modeli
- Cache modeli dla szybszego ładowania

**Konfiguracja audio:**
- Wybór urządzenia wejściowego
- Dostosowanie poziomu czułości mikrofonu
- Konfiguracja redukcji szumów
- Ustawienia VAD (Voice Activity Detection)

**Język i transkrypcja:**
- Automatyczna detekcja lub wymuszony język
- Włączanie/wyłączanie znaki interpunkcyjnych
- Formatowanie wielkich liter
- Opcje post-processingu tekstu

**Skróty klawiszowe:**
- Konfiguracja triggera nagrywania
- Ustawienia modyfikatorów (Cmd, Ctrl, Shift, Alt)
- Skróty do szybkiej zmiany modelu

### Konfiguracja środowiska

**Plik konfiguracyjny** (`config.yaml`):
```yaml
model: base
language: auto
audio:
  device: default
  sample_rate: 16000
shortcuts:
  record: cmd+shift+space
performance:
  use_gpu: auto
  threads: 4
```

**Zmienne środowiskowe:**
- `WHISPER_MODEL_DIR`: Lokalizacja modeli
- `WHISPER_DEVICE`: Wymuszenie CPU/GPU
- `WHISPER_THREADS`: Liczba wątków procesora

## Roadmapa rozwoju

### Zrealizowane funkcje ✅

- Podstawowa transkrypcja z modelem Python Whisper
- Integracja z menu bar macOS
- Globalne skróty klawiszowe
- Automatyczne wstawianie tekstu
- Wybór modeli Whisper
- Detekcja języka
- Podstawowa obsługa urządzeń M1/M2

### W trakcie realizacji 🚧

- Zaawansowana redukcja szumów
- System aktualizacji automatycznych
- Rozszerzona konfiguracja UI
- Wsparcie dla większej liczby języków
- Dokumentacja w języku angielskim

### Planowane usprawnienia 📋

#### v1.x (2025)
- Wsparcie dla komend głosowych (formatowanie, poprawki)
- Integracja z popularnymi aplikacjami (Slack, Discord, etc.)
- Profile użytkownika (praca, osobiste, kodowanie)
- Historia transkrypcji z możliwością wyszukiwania
- Eksport transkrypcji do pliku
- Wsparcie dla macros i snippets
- Synchronizacja ustawień przez iCloud
- Custom vocabulary/słownik
- Plugin system

#### v2.0 (Q3 2025)
- Realtime transcription (streaming)
- Linux support
- Windows support (WSL)
- Web interface (opcjonalnie)

## Znane ograniczenia ⚠️

- **Wymagania zasobów**: Większe modele (medium/large) wymagają znacznych zasobów RAM i mogą ładować się do 30 sekund
- **Czas transkrypcji**: Rośnie liniowo z długością audio, brak wsparcia dla realtime (transkrypcja rozpoczyna się po zakończeniu nagrywania)
- **Wsparcie platform**: Brak wsparcia dla systemów innych niż macOS (Windows/Linux)
- **Jakość audio**: Zależna od jakości mikrofonu i środowiska akustycznego - słabsza przy złych warunkach lub odległym mikrofonie
- **GPU Python**: Wersja Python nie wspiera GPU M1/M2 (PyTorch MPS incompatibility) - użyj wersji C++ dla akceleracji GPU

Szczegółowa lista w [TECHNICAL_DEBT.md](./TECHNICAL_DEBT.md).

## Powiązane dokumenty

- [README](../README.md) - szczegółowa dokumentacja projektu, instalacja i użycie
- [Diagram systemowy](./diagrams/system-overview.mmd) - architektura systemu

---

## Metadata

**Wersja dokumentu**: 1.0  
**Data utworzenia**: 2025-10-10  
**Ostatnia aktualizacja**: 2025-10-19  
**Autor**: AI Agent  
**Status**: ✅ Ukończone  
