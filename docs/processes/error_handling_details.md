# Obsługa Błędów - Szczegóły

Ten dokument szczegółowo opisuje mechanizmy obsługi błędów w aplikacji Whisper Dictation.

## 1. Typy błędów

### 1.1. Błędy inicjalizacji

| Błąd                   | Przyczyna                               | Obsługa                       |
|------------------------|-----------------------------------------|-------------------------------|
| **Model nie załadowany** | Brak pliku w cache, błąd pobierania     | Komunikat + pytanie o pobranie |
| **Urządzenie niedostępne** | MPS/CUDA nie działa                     | Automatyczny fallback na CPU  |
| **Brak pamięci**       | Model za duży dla urządzenia            | Fallback + komunikat          |

**Kod obsługi**: W `whisper-dictation.py` (linie 337-353) zaimplementowano obsługę błędów inicjalizacji modelu z automatycznym fallbackiem na CPU w przypadku problemów z urządzeniem.

### 1.2. Błędy nagrywania

| Błąd                 | Przyczyna                               | Obsługa                       |
|----------------------|-----------------------------------------|-------------------------------|
| **Brak mikrofonu**   | Mikrofon odłączony/zajęty               | PyAudio exception → komunikat |
| **Stream overflow**  | Bufor przepełniony                      | `exception_on_overflow=False` |
| **Brak uprawnień**   | System nie zezwala na dostęp            | Komunikat systemowy macOS     |

**Kod obsługi**: W `recorder.py` (linie 147-152) błędy nagrywania są przechwytywane, a w przypadku przepełnienia bufora (`exception_on_overflow=False`) nagrywanie jest kontynuowane.

### 1.3. Błędy transkrypcji

| Błąd                  | Przyczyna                               | Obsługa                       |
|-----------------------|-----------------------------------------|-------------------------------|
| **OOM (Out of Memory)** | Audio za długie dla urządzenia          | Fallback CPU + retry          |
| **Timeout**           | Model zawiesił się                      | Timeout nie zaimplementowany (TODO) |
| **Invalid audio**     | Pusta/nieprawidłowa próbka              | Cichy błąd (brak wyjścia)     |
| **Language mismatch** | Język poza `allowed_languages`          | Wymuszenie pierwszego z allowed |

**Kod obsługi detekcji języka**: W `whisper-dictation.py` (linie 47-59) zaimplementowano logikę nadpisywania wykrytego języka, jeśli nie znajduje się on na liście `allowed_languages`.

**Kod obsługi fallback**: W `transcriber.py` (linie 145-169) zaimplementowano mechanizm automatycznego fallbacku urządzenia w przypadku błędów transkrypcji, z możliwością ponowienia próby na innym urządzeniu.

### 1.4. Błędy wklejania tekstu

| Błąd                   | Przyczyna                               | Obsługa                       |
|------------------------|-----------------------------------------|-------------------------------|
| **Keyboard input blocked** | Brak uprawnień accessibility            | `try-except pass` - cichy błąd |
| **Special characters** | Znaki niedostępne na klawiaturze        | `try-except pass`             |

**Kod obsługi**: W `whisper-dictation.py` (linie 69-73) błędy wklejania tekstu są cicho ignorowane (`try-except pass`), aby nie przerywać działania aplikacji.

## 2. Strategia odzyskiwania (Recovery Strategy)

### 2.1. Device Fallback Chain
```
MPS (M1/M2 GPU) → CUDA (NVIDIA GPU) → CPU
```

**DeviceManager** śledzi:
- Historię błędów dla każdego urządzenia
- Licznik sukcesów dla operacji (MODEL_LOADING, TRANSCRIPTION)
- Automatyczny wybór urządzenia na podstawie kontekstu

### 2.2. Enhanced Error Messages
DeviceManager dostarcza przyjazne komunikaty po polsku:
- "🔄 Wykryto problem z MPS. Przełączam na CPU dla stabilności."
- "✅ Model załadowany pomyślnie na urządzeniu: cpu"

## Powiązane Dokumenty

- [DATA_FLOW.md](../DATA_FLOW.md) - Główny przepływ danych
- [ARCHITECTURE.md](../../ARCHITECTURE.md) - Architektura systemu
