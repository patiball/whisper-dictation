# Szczegóły Implementacji Architektury

Ten dokument zawiera szczegółowe informacje dotyczące implementacji kluczowych aspektów architektury aplikacji Whisper Dictation.

## Cel

Celem tego dokumentu jest uzupełnienie wysokopoziomowego opisu architektury o konkretne detale implementacyjne, przykłady kodu oraz techniczne wyjaśnienia, które zostały przeniesione z głównego dokumentu ARCHITECTURE.md w celu zachowania jego zwięzłości.

## Spis Treści

1.  [Implementacja Wzorców Projektowych](#implementacja-wzorców-projektowych)
2.  [Szczegóły Komponentów Głównych](#szczegóły-komponentów-głównych)
3.  [Optymalizacje Specyficzne dla Urządzeń](#optymalizacje-specyficzne-dla-urządzeń)
4.  [Obsługa Błędów i Fallback](#obsługa-błędów-i-fallback)
5.  [Przykłady Użycia i Konfiguracji](#przykłady-użycia-i-konfiguracji)

## Implementacja Wzorców Projektowych

### Singleton (Implicit)

**Gdzie**: `DeviceManager`, `EnhancedDeviceManager`

**Implementacja**: Choć nie klasyczny Singleton, te komponenty są tworzone raz przy starcie aplikacji i współdzielone przez wszystkie moduły.

```mermaid
classDiagram
    class EnhancedDeviceManager
    class DeviceManager
    class SpeechTranscriber
    class Recorder

    EnhancedDeviceManager --|> DeviceManager
    SpeechTranscriber --o EnhancedDeviceManager : uses
    Recorder --o SpeechTranscriber : uses

    note for EnhancedDeviceManager "Jedna instancja tworzona przy starcie aplikacji"
```

**Uzasadnienie**: Centralizacja zarządzania urządzeniami i historii operacji wymaga pojedynczej instancji.

### Strategy

**Gdzie**: `DeviceManager.get_device_for_operation()`

**Implementacja**: Wybór strategii (CPU/MPS/CUDA) na podstawie typu operacji i historii:

```mermaid
flowchart TD
    A[get_device_for_operation] --> B{Sprawdź historię operacji}
    B -->|Success Rate > 80%| C[Wybierz urządzenie z historią]
    B -->|Brak historii| D[Wybierz urządzenie z preferencji]
    C --> E[Zwróć wybrane urządzenie]
    D --> E
```

**Uzasadnienie**: Różne operacje (ładowanie modelu vs transkrypcja) mogą preferować różne urządzenia.

### Observer (Event-based)

**Gdzie**: `KeyListener` → `StatusBarApp` → `Recorder`

**Implementacja**: Wzorzec obserwatora przez callbacks:

```mermaid
sequenceDiagram
    participant KL as KeyListener
    participant SBA as StatusBarApp
    participant REC as Recorder

    KL->>SBA: on_key_press(key)
    SBA->>SBA: toggle()
    alt if started
        SBA->>REC: stop_app()
    else
        SBA->>REC: start_app()
    end
```

**Uzasadnienie**: Luźne powiązanie między warstwą kontroli a warstwą biznesową.

### Factory (Model Loading)

**Gdzie**: Ładowanie modeli Whisper

**Implementacja**: Factory pattern dla różnych rozmiarów modeli:

```mermaid
classDiagram
    class WhisperModelFactory {
        +load_model(model_name, device)
    }
    class TinyModel
    class BaseModel
    class LargeModel

    WhisperModelFactory ..> TinyModel : creates
    WhisperModelFactory ..> BaseModel : creates
    WhisperModelFactory ..> LargeModel : creates

    note for WhisperModelFactory "whisper.load_model() działa jako factory"
```

**Uzasadnienie**: Ukrycie złożoności tworzenia różnych wariantów modeli za prostym interfejsem.

### Template Method

**Gdzie**: `Recorder.start()` → `_record_impl()`

**Implementacja**: Szkielet algorytmu z customizowalnymi krokami:

```mermaid
flowchart TD
    A[Recorder.start] --> B[_record_impl]
    B --> C[sound_player.play_start_sound]
    C[sound_player.play_start_sound] --> D[Główny algorytm nagrywania]
    D --> E[sound_player.play_stop_sound]
    E --> F[transcriber.transcribe_audio_data]
    F --> G[Koniec]

    subgraph _record_impl
        C -- Hook 1 --> D
        E -- Hook 2 --> F
        F -- Hook 3 --> G
    end
```

**Uzasadnienie**: Stały przepływ nagrywania z możliwością customizacji (dźwięki, transkrypcja).

### Adapter

**Gdzie**: `recorder.py` jako adapter między PyAudio a resztą aplikacji

**Implementacja**: Opakowuje PyAudio API w prosty interfejs:

```mermaid
classDiagram
    class Recorder {
        +start_recording_with_timestamp()
        +stop_recording()
    }
    class PyAudioAPI {
        +open_stream()
        +read_stream()
        +close_stream()
    }

    Recorder --> PyAudioAPI : adapts

    note for Recorder "Ukrywa złożoność PyAudio za prostym interfejsem"
```

**Uzasadnienie**: Izoluje resztę kodu od szczegółów implementacji PyAudio.

### Chain of Responsibility

**Gdzie**: Device fallback chain w `DeviceManager`

**Implementacja**: Próba urządzeń w kolejności do pierwszego sukcesu:

```mermaid
flowchart TD
    A[handle_device_error] --> B{Current Device Failed?}
    B -->|Yes| C[Try Next Preferred Device]
    C --> D{Device Capable?}
    D -->|Yes| E[Return Device]
    D -->|No| C
    C --> F[Return Fallback Device (CPU)]
```

**Uzasadnienie**: Graceful degradation - jeśli MPS zawiedzie, próbuj CUDA, potem CPU.

## Powiązane Dokumenty

- [ARCHITECTURE.md](../ARCHITECTURE.md) - Główna dokumentacja architektury
- [MODULES.md](../../MODULES.md) - Indeks modułów
