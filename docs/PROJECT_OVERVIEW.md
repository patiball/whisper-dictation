# Przegląd projektu Whisper Dictation

## Cel aplikacji

Wielojęzyczna aplikacja dyktowania oparta na potężnym modelu OpenAI Whisper ASR, zapewniająca dokładną i efektywną konwersję mowy na tekst w dowolnej aplikacji. Aplikacja działa w tle, uruchamiana przez skróty klawiszowe, i funkcjonuje całkowicie offline bez udostępniania danych, gwarantując prywatność użytkownika.

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

## Kluczowe funkcjonalności

- **Wielojęzyczne rozpoznawanie mowy** - wsparcie dla wielu języków dzięki modelowi Whisper
- **Działanie w tle** - aplikacja działa nieprzerwanie z globalnym dostępem przez skróty klawiszowe
- **Całkowicie offline** - brak wysyłania danych, pełna prywatność
- **Wybór modeli Whisper** - możliwość wyboru spośród tiny, base, small, medium, large
- **Dwie implementacje**:
  - Python: dokładna transkrypcja, CPU
  - C++ (whisper.cpp): eksperymentalne wsparcie GPU M1, w trakcie optymalizacji
- **Integracja z systemem macOS** - ikona w menu bar, dźwięki systemowe
- **Automatyczne wykrywanie języka** - inteligentne rozpoznawanie języka mówionego
- **Zarządzanie urządzeniami** - optymalizacja dla Apple Silicon (M1/M2)
- **Konfigurowalne skróty** - możliwość dostosowania klawiszy aktywacji

## Powiązane dokumenty

- [README](../README.md) - szczegółowa dokumentacja projektu, instalacja i użycie
- [Diagram systemowy](./diagrams/system-overview.mmd) - architektura systemu
