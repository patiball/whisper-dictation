# Przegląd projektu Whisper Dictation

## Wprowadzenie

Whisper Dictation to opensource'owa aplikacja do dyktowania dla macOS, wykorzystująca najnowocześniejszy model rozpoznawania mowy OpenAI Whisper. Projekt powstał jako odpowiedź na potrzebę prywatnego, offline'owego narzędzia do transkrypcji, które nie wymaga połączenia z chmurą ani wysyłania danych osobowych do zewnętrznych serwerów.

Aplikacja jest szczególnie zoptymalizowana dla procesorów Apple Silicon (M1/M2), oferując dwie implementacje: stabilną wersję Python oraz eksperymentalną wersję wykorzystującą whisper.cpp z akceleracją GPU.

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
  - Wersja Python (rekomendowana, CPU)
  - Wersja whisper.cpp (eksperymentalna, GPU M1)
- **PyTorch** - framework uczenia maszynowego
- **PyAudio / PortAudio** - obsługa nagrywania audio
- **Poetry** - zarządzanie zależnościami
- **Pynput** - globalne skróty klawiszowe
- **Rumps** - integracja z paskiem menu macOS
- **macOS** - platforma docelowa (wsparcie dla M1/M2)

## Struktura folderów

```
whisper-dictation/
├── docs/                    # Dokumentacja projektu
│   ├── diagrams/           # Diagramy systemowe
│   └── context/            # Pliki kontekstowe
├── memory-bank/            # Bank pamięci agenta AI
│   ├── core/              # Podstawowe pliki dokumentacji
│   └── specs/             # Specyfikacje szczegółowe
├── scripts/                # Skrypty automatyzacji i setup
├── specs/                  # Specyfikacje funkcjonalne
├── tests/                  # Testy jednostkowe i integracyjne
│   └── audio/             # Próbki audio do testów
├── whisper-dictation.py           # Główna implementacja (Python)
├── whisper-dictation-fast.py     # Implementacja C++ (eksperymentalna)
├── recorder.py             # Moduł nagrywania audio
├── transcriber.py          # Moduł transkrypcji
├── device_manager.py       # Zarządzanie urządzeniami M1/M2
└── pyproject.toml          # Konfiguracja projektu (Poetry)
```

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

### Podstawowe możliwości

- **Wielojęzyczne rozpoznawanie mowy** - wsparcie dla wielu języków dzięki modelowi Whisper
  - Automatyczna detekcja języka lub wybór manualny
  - Wysokiej jakości transkrypcja w czasie rzeczywistym
  - Wsparcie dla języków z różnymi systemami pisma

- **Działanie w tle** - aplikacja działa nieprzerwanie z globalnym dostępem przez skróty klawiszowe
  - Minimalne zużycie zasobów w trybie czuwania
  - Natychmiastowa reakcja na wywołanie skrótu
  - Integracja z paskiem menu macOS dla łatwego dostępu

- **Całkowicie offline** - brak wysyłania danych, pełna prywatność
  - Wszystkie operacje wykonywane lokalnie
  - Żadne dane nie opuszczają komputera użytkownika
  - Brak wymagań dotyczących połączenia internetowego

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

- **Wybór modeli Whisper** - możliwość wyboru spośród tiny, base, small, medium, large
  - Tiny: najszybszy, podstawowa dokładność (~75MB)
  - Base: zrównoważony wybór dla większości przypadków (~140MB)
  - Small: lepsza dokładność przy umiarkowanym czasie (~470MB)
  - Medium: wysoka dokładność dla profesjonalnego użytku (~1.5GB)
  - Large: najwyższa jakość transkrypcji (~3GB)

- **Dwie implementacje**:
  - Python: dokładna transkrypcja, CPU, stabilna i przetestowana
  - C++ (whisper.cpp): eksperymentalne wsparcie GPU M1, w trakcie optymalizacji

### Integracja i personalizacja

- **Integracja z systemem macOS**
  - Ikona w menu bar z menu kontekstowym
  - Dźwięki systemowe jako feedback dla użytkownika
  - Automatyczne uruchamianie przy starcie systemu (opcjonalnie)

- **Automatyczne wykrywanie języka** - inteligentne rozpoznawanie języka mówionego
  - Bez potrzeby ręcznego przełączania między językami
  - Wspiera wielojęzyczne dyktowanie w jednej sesji

- **Zarządzanie urządzeniami** - optymalizacja dla Apple Silicon (M1/M2)
  - Automatyczne wykrywanie dostępnych akceleratorów
  - Efektywne wykorzystanie Neural Engine

- **Konfigurowalne skróty** - możliwość dostosowania klawiszy aktywacji
  - Elastyczne przypisywanie skrótów klawiszowych
  - Wsparcie dla różnych kombinacji modyfikatorów

### System wstawiania tekstu

- **Automatyczne wklejanie** - transkrybowany tekst automatycznie pojawia się w aktywnej aplikacji
- **Zachowanie formatowania** - inteligentna obsługa znaków interpunkcyjnych i spacji
- **Kontrola jakości** - filtrowanie niepewnych wyników przed wstawieniem

## Architektura techniczna

### Przepływ danych audio

```
1. Mikrofon → PyAudio/PortAudio (przechwytywanie)
2. Buffer audio → Preprocessor (normalizacja, redukcja szumów)
3. Preprocessed audio → Whisper Model (transkrypcja)
4. Raw transcription → Post-processor (czyszczenie, formatowanie)
5. Formatted text → System clipboard/Keyboard emulation
6. Finalized text → Aktywna aplikacja
```

### Komponenty systemu

**recorder.py** - Moduł nagrywania
- Konfiguracja urządzeń audio
- Zarządzanie buforem nagrywania
- Detekcja aktywności głosowej (VAD)
- Kontrola jakości sygnału

**transcriber.py** - Silnik transkrypcji
- Ładowanie i zarządzanie modelami Whisper
- Optymalizacja parametrów transkrypcji
- Cache wyników dla poprawy wydajności
- Obsługa błędów i retry logic

**device_manager.py** - Zarządzanie sprzętem
- Wykrywanie Apple Silicon
- Konfiguracja akceleracji sprzętowej
- Monitoring zasobów systemowych
- Fallback do CPU przy problemach z GPU

**Main Application** - Orkiestracja
- Obsługa skrótów klawiszowych globalnych
- Zarządzanie stanem aplikacji
- Interfejs menu bar
- Koordynacja między komponentami

### Kluczowe technologie

- **OpenAI Whisper**: State-of-the-art model ASR z wysoką dokładnością
- **PyTorch**: Backend dla modeli deep learning
- **PyAudio**: Cross-platform audio I/O
- **Pynput**: Globalne przechwytywanie i emulacja klawiatury
- **Rumps**: Framework dla aplikacji menu bar w macOS

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

- Optymalizacja implementacji whisper.cpp
- Pełne wsparcie GPU dla Apple Silicon
- Zaawansowana redukcja szumów
- System aktualizacji automatycznych
- Rozszerzona konfiguracja UI
- Poprawa jakości wersji C++ (GPU M1)
- Wsparcie dla większej liczby języków

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

- **Implementacja whisper.cpp**: Wersja C++ (GPU M1) wymaga dalszej optymalizacji i ma problemy z jakością - zalecana wersja Python (CPU)
- **Wymagania zasobów**: Większe modele (medium/large) wymagają znacznych zasobów RAM i mogą ładować się do 30 sekund
- **Czas transkrypcji**: Rośnie liniowo z długością audio, brak wsparcia dla realtime (transkrypcja rozpoczyna się po zakończeniu nagrywania)
- **Wsparcie platform**: Brak wsparcia dla systemów innych niż macOS (Windows/Linux)
- **Jakość audio**: Zależna od jakości mikrofonu i środowiska akustycznego - słabsza przy złych warunkach lub odległym mikrofonie

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
