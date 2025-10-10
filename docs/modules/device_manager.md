# Moduł: Device Manager

## Odpowiedzialność

Moduł `device_manager` zapewnia scentralizowane zarządzanie urządzeniami (CPU, MPS, CUDA) z inteligentnym wyborem urządzenia, testowaniem zdolności, obsługą błędów i optymalizacją dla chipów Apple M1/M2. Jest kluczowy dla stabilności i wydajności aplikacji na różnych platformach.

## Publiczne API

### Klasa: `DeviceManager`

Podstawowy manager urządzeń z testowaniem zdolności i fallbackiem.

#### Konstruktor

```python
def __init__(self, enable_logging: bool = True)
```

**Parametry:**
- `enable_logging` (bool): Włącz/wyłącz logowanie operacji

**Inicjalizacja:**
- Wykrywa kolejność preferencji urządzeń (MPS → CUDA → CPU)
- Testuje podstawowe operacje tensorowe
- Testuje operacje podobne do ładowania modelu
- Zapisuje wyniki testów w `capabilities`

#### Główne Metody

##### `get_device_for_operation(operation: OperationType, model_size: str | None = None) -> str`

Wybiera najlepsze urządzenie dla danej operacji.

**Parametry:**
- `operation`: Typ operacji (`MODEL_LOADING`, `TRANSCRIPTION`, `BASIC_TENSOR`)
- `model_size`: Rozmiar modelu (dla rozważań pamięciowych)

**Zwraca:** Nazwa urządzenia (np. `'mps'`, `'cpu'`)

**Logika:**
- Sprawdza historię sukcesu operacji na każdym urządzeniu
- Jeśli wskaźnik sukcesu > 80%, wybiera to urządzenie
- Fallback na kolejne urządzenia w razie problemów
- Ostateczny fallback: CPU

##### `handle_device_error(error: Exception, operation: OperationType, current_device: str) -> str`

Obsługuje błędy urządzenia i zwraca urządzenie zastępcze.

**Parametry:**
- `error`: Wyjątek, który wystąpił
- `operation`: Operacja, która się nie powiodła
- `current_device`: Urządzenie, na którym wystąpił błąd

**Zwraca:** Urządzenie fallback

**Zachowanie:**
- Loguje błąd i rejestruje porażkę w historii
- Rozpoznaje znane problemy MPS (SparseMPS, memory_format)
- Wyłącza problematyczne urządzenie dla danej operacji
- Wybiera następne dostępne urządzenie

##### `register_operation_success(device: str, operation: OperationType)`

Rejestruje sukces operacji dla przyszłych decyzji.

##### `should_retry_with_fallback(error: Exception) -> bool`

Określa, czy błąd uzasadnia automatyczny retry z fallbackiem.

**Zwraca:** `True` dla znanych błędów MPS (SparseMPS, aten::empty.memory_format, itp.)

##### `get_device_status_report() -> Dict`

Zwraca raport o statusie urządzeń (do debugowania).

### Enum: `DeviceType`

- `CPU = "cpu"`
- `MPS = "mps"`
- `CUDA = "cuda"`

### Enum: `OperationType`

- `MODEL_LOADING`: Ładowanie modelu
- `TRANSCRIPTION`: Transkrypcja audio
- `BASIC_TENSOR`: Podstawowe operacje tensorowe

### Klasa: `DeviceCapability`

Reprezentuje wynik oceny zdolności urządzenia.

**Atrybuty:**
- `device` (str): Nazwa urządzenia
- `available` (bool): Czy urządzenie działa
- `tested` (bool): Czy zostało przetestowane
- `error` (str | None): Komunikat błędu (jeśli wystąpił)
- `performance_score` (float): Wynik wydajności
- `last_test_time` (float): Timestamp ostatniego testu

## Moduł Rozszerzony: `mps_optimizer.py`

### Klasa: `EnhancedDeviceManager`

Rozszerzona wersja `DeviceManager` z dedykowaną obsługą błędów MPS i optymalizacjami M1/M2.

#### Konstruktor

```python
def __init__(self, enable_logging: bool = True)
```

Tworzy instancję `DeviceManager`, `MPSErrorHandler`, `MPSOptimizer`.

#### Metody

##### `handle_device_error_enhanced(error: Exception, operation: OperationType, current_device: str) -> tuple[str, str]`

Rozszerzona obsługa błędów z przyjaznymi komunikatami po polsku.

**Zwraca:** `(fallback_device, user_friendly_message)`

##### `get_optimized_settings(device: str, model_size: str) -> Dict[str, Any]`

Zwraca optymalne ustawienia Whisper dla urządzenia i modelu:
- MPS: fp16, beam_size=1, condition_on_previous_text=False
- CPU: fp16=False, adaptive beam_size

##### `optimize_model(model, device: str)`

Stosuje optymalizacje specyficzne dla urządzenia (np. włącza MPS fallback, ustawia eval mode).

##### `get_comprehensive_status() -> Dict[str, Any]`

Raport obejmujący status urządzeń, statystyki błędów, informacje o pamięci.

### Klasa: `MPSErrorHandler`

Kategoryzuje błędy MPS i dostarcza przyjazne komunikaty.

#### Metody:
- `categorize_error(error: Exception) -> MPSErrorType`
- `should_retry_with_cpu(error: Exception) -> bool`
- `get_user_friendly_message(error: Exception) -> str` (po polsku)
- `get_error_statistics() -> Dict[str, int]`

### Enum: `MPSErrorType`

- `SPARSE_BACKEND`
- `MEMORY_FORMAT`
- `OUT_OF_MEMORY`
- `UNSUPPORTED_OP`
- `UNKNOWN`

### Klasa: `MPSOptimizer`

Optymalizacje M1/M2 dla Whisper.

#### Metody:
- `get_optimal_whisper_settings(device: str, model_size: str) -> Dict[str, Any]`
- `optimize_model_for_m1(model, device: str)`
- `get_memory_usage_info(device: str) -> Dict[str, Any]`

## Zależności

### Zależy od:
- `torch`: Backend PyTorch, wykrywanie urządzeń (MPS, CUDA)
- `logging`: Logowanie operacji i błędów
- `psutil` (opcjonalnie): Informacje o pamięci systemowej

### Używany przez:
- `transcriber.SpeechTranscriber`: Wybór urządzenia, optymalizacja, fallback
- `mps_optimizer.EnhancedDeviceManager`: Rozszerzenie funkcjonalności

## Przykład Użycia

### Podstawowe użycie DeviceManager

```python
from device_manager import DeviceManager, OperationType

manager = DeviceManager()

# Wybierz urządzenie do ładowania modelu
device = manager.get_device_for_operation(OperationType.MODEL_LOADING, "base")
print(f"Using device: {device}")

# Zarejestruj sukces
manager.register_operation_success(device, OperationType.MODEL_LOADING)
```

### Obsługa błędów z fallbackiem

```python
from device_manager import DeviceManager, OperationType

manager = DeviceManager()
device = "mps"

try:
    # Próba operacji na MPS
    model.transcribe(audio, device=device)
except Exception as e:
    if manager.should_retry_with_fallback(e):
        fallback_device = manager.handle_device_error(e, OperationType.TRANSCRIPTION, device)
        print(f"Falling back to: {fallback_device}")
        model.transcribe(audio, device=fallback_device)
```

### Użycie EnhancedDeviceManager

```python
from mps_optimizer import EnhancedDeviceManager
from device_manager import OperationType

enhanced = EnhancedDeviceManager()

# Pobierz optymalne ustawienia
device = enhanced.get_device_for_operation(OperationType.TRANSCRIPTION)
settings = enhanced.get_optimized_settings(device, "base")

# Załaduj model
model = whisper.load_model("base", device=device)
enhanced.optimize_model(model, device)

# Transkrypcja z fallbackiem
try:
    result = model.transcribe(audio, **settings)
except Exception as e:
    fallback_device, message = enhanced.handle_device_error_enhanced(
        e, OperationType.TRANSCRIPTION, device
    )
    print(f"🔄 {message}")
    # Retry z fallback
```

### Raport statusu urządzeń

```python
from mps_optimizer import EnhancedDeviceManager

enhanced = EnhancedDeviceManager()
status = enhanced.get_comprehensive_status()

print("Preferred devices:", status["preferred_devices"])
print("Capabilities:", status["capabilities"])
print("Error statistics:", status["error_statistics"])
```

## Szczegóły Implementacji

### Testowanie Zdolności

Przy inicjalizacji `DeviceManager` testuje:
1. **Podstawowe operacje**: Proste operacje tensorowe (add, sum)
2. **Operacje podobne do modelu**: Conv1d, linear na kształtach używanych przez Whisper

Wyniki są cache'owane w `capabilities`.

### Historia Operacji

`operation_history` śledzi ostatnie 10 wyników dla każdej kombinacji (device, operation). Wskaźnik sukcesu > 80% preferuje to urządzenie.

### Znane Problemy MPS

DeviceManager rozpoznaje i obsługuje:
- `SparseMPS backend errors`
- `aten::empty.memory_format` errors
- `MPS out of memory`
- `Unsupported operations`

### Optymalizacje M1/M2

- **fp16**: Half-precision dla szybszej inferencji na GPU
- **beam_size=1**: Szybsze dekodowanie
- **condition_on_previous_text=False**: Mniejsze zużycie pamięci
- **MPS fallback**: Automatyczne przejście na CPU dla nieobsługiwanych operacji

## TODO/FIXME

Brak znanych TODO/FIXME w kodzie device_manager.

## Znane Ograniczenia

1. **Lightweight Tests**: Testy zdolności są uproszczone; nie ładują rzeczywistych modeli Whisper
2. **History Size**: Historia operacji ograniczona do 10 ostatnich wyników
3. **MPS Pattern Matching**: Rozpoznawanie błędów opiera się na wzorcach tekstowych

## Powiązane Dokumenty

- [MODULES.md](../MODULES.md) - Przegląd wszystkich modułów
- [transcriber.md](./transcriber.md) - Moduł transkrypcji (główny konsument)
- [ARCHITECTURE.md](../ARCHITECTURE.md) - Architektura systemu
- [DATA_FLOW.md](../DATA_FLOW.md) - Przepływ danych
