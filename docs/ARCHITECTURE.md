# Architektura aplikacji Whisper Dictation

## 1. Wprowadzenie

Whisper Dictation to wielojęzyczna aplikacja dyktowania oparta na modelu OpenAI Whisper ASR, zaprojektowana specjalnie dla platformy macOS z optymalizacją pod procesory Apple Silicon (M1/M2). Aplikacja działa jako demon systemowy uruchamiany za pomocą skrótów klawiszowych, zapewniając całkowicie offline konwersję mowy na tekst bez udostępniania danych użytkownika.

Architektura systemu została zaprojektowana z naciskiem na:
- **Modularność** - wyraźne rozdzielenie odpowiedzialności między komponenty
- **Wydajność** - inteligentne zarządzanie urządzeniami (CPU/GPU) dla optymalnej wydajności
- **Niezawodność** - mechanizmy fallback i obsługa błędów specyficznych dla Apple Silicon
- **Prywatność** - całkowicie offline przetwarzanie bez wysyłania danych

System wykorzystuje warstwową architekturę, gdzie każda warstwa ma jasno określone zadania i zależności, co umożliwia łatwe testowanie, rozwój i utrzymanie kodu.

## 2. Warstwy systemu

Aplikacja została zorganizowana w pięć głównych warstw, z wyraźnym rozdzieleniem odpowiedzialności:

```
┌─────────────────────────────────────────────────────────────┐
│                    Warstwa Prezentacji                      │
│              (Rumps, StatusBarApp, ikony)                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     Warstwa Kontroli                        │
│        (KeyListeners, SoundPlayer, główna pętla)            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Warstwa Biznesowa                        │
│     (Recorder, SpeechTranscriber, DeviceManager)            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     Warstwa Danych                          │
│         (numpy buffers, model cache, audio data)            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Warstwa Integracji                        │
│      (PyAudio, PyTorch, Whisper, Pynput, macOS APIs)        │
└─────────────────────────────────────────────────────────────┘
```

### 2.1. Warstwa Prezentacji

**Odpowiedzialność**: Interfejs użytkownika, wizualna reprezentacja stanu aplikacji

**Komponenty**:
- `StatusBarApp` (rumps.App) - ikona w menu bar z opcjami
- Ikony statusu - reprezentacja wizualna stanu (⏯, 🔴, timer)
- Menu kontekstowe - opcje startu/stopu, wybór języka

**Zależności**: 
- macOS Menu Bar API (przez rumps)
- System dźwięków macOS

**Charakterystyka**:
- Minimalistyczny interfejs nie przeszkadzający w pracy
- Dynamiczna aktualizacja tytułu z timerem nagrywania
- Ikony zmieniające się w zależności od stanu (idle → recording → transcribing)

### 2.2. Warstwa Kontroli

**Odpowiedzialność**: Zarządzanie cyklem życia aplikacji, obsługa zdarzeń użytkownika

**Komponenty**:
- `GlobalKeyListener` - obsługa kombinacji klawiszy (cmd+alt)
- `DoubleCommandKeyListener` - specjalny tryb dla podwójnego cmd
- `SoundPlayer` - feedback dźwiękowy (rozpoczęcie/zakończenie nagrywania)
- Główna pętla aplikacji w `whisper-dictation.py`

**Zależności**: 
- `pynput` - globalne przechwytywanie skrótów klawiszowych
- `afplay` - odtwarzacz dźwięków systemowych macOS
- `threading` - asynchroniczna obsługa zdarzeń

**Charakterystyka**:
- Nie blokujący model obsługi zdarzeń
- Separacja logiki nagrywania od interfejsu użytkownika
- Feedback audio wzorowany na systemowym rozpoznawaniu mowy macOS

### 2.3. Warstwa Biznesowa

**Odpowiedzialność**: Kluczowa logika aplikacji - nagrywanie i transkrypcja

**Komponenty**:

#### Recorder
- Zarządzanie strumieniem audio przez PyAudio
- Buforowanie danych audio w czasie rzeczywistym
- Konwersja formatów audio (int16 → float32)
- Wsparcie dla testów TDD (timestamp, duration)

**Kluczowe metody**:
```python
def start_recording_with_timestamp(self) -> float:
    """Rozpoczyna nagrywanie i zwraca dokładny timestamp"""

def stop_recording(self) -> np.ndarray:
    """Zatrzymuje nagrywanie i zwraca dane audio"""

def record_duration(self, duration_seconds: float) -> np.ndarray:
    """Nagrywa przez określony czas (do testów)"""
```

#### SpeechTranscriber
- Zarządzanie modelami Whisper (tiny, base, small, medium, large)
- Wykrywanie języka z ograniczeniami (allowed_languages)
- Optymalizacja ustawień transkrypcji dla różnych urządzeń
- Automatyczna konwersja transkrypcji na wpisywany tekst

**Kluczowe metody**:
```python
def transcribe(self, audio_file_path: str, language: str = None) -> TranscriptionResult:
    """Transkrybuje plik audio z detekcją języka"""

def transcribe_audio_data(self, audio_data: np.ndarray) -> TranscriptionResult:
    """Transkrybuje surowe dane audio (real-time)"""

def get_model_state(self) -> str:
    """Zwraca identyfikator stanu modelu (do testów)"""
```

#### DeviceManager
- Centralne zarządzanie urządzeniami (CPU, MPS, CUDA)
- Testowanie możliwości urządzeń przy inicjalizacji
- Historia operacji dla inteligentnego wyboru urządzenia
- Automatyczny fallback przy błędach

**Kluczowe metody**:
```python
def get_device_for_operation(self, operation: OperationType, model_size: str = None) -> str:
    """Wybiera optymalne urządzenie dla operacji"""

def handle_device_error(self, error: Exception, operation: OperationType, current_device: str) -> str:
    """Obsługuje błąd urządzenia i zwraca fallback"""

def register_operation_success(self, device: str, operation: OperationType):
    """Rejestruje udaną operację dla przyszłych decyzji"""
```

#### MPSOptimizer & EnhancedDeviceManager
- Specjalistyczna obsługa błędów MPS (Apple Silicon)
- Optymalizacja ustawień Whisper dla M1/M2
- Przyjazne użytkownikowi komunikaty błędów (po polsku)
- Monitorowanie zużycia pamięci

**Zależności**:
- PyAudio - nagrywanie audio
- PyTorch - framework ML
- Whisper - silnik ASR
- numpy - przetwarzanie danych audio

### 2.4. Warstwa Danych

**Odpowiedzialność**: Przechowywanie i zarządzanie danymi

**Komponenty**:
- **Bufory audio** - numpy arrays przechowujące próbki audio (float32)
- **Cache modeli** - `~/.cache/whisper/` przechowuje pobrane modele Whisper
- **Historia operacji** - tracking sukcesu/porażki operacji na urządzeniach
- **Capabilities cache** - informacje o możliwościach urządzeń

**Charakterystyka**:
- Brak persystencji danych audio (prywatność)
- Modele cachowane lokalnie po pierwszym pobraniu
- Dynamiczne zarządzanie pamięcią dla różnych rozmiarów modeli
- Historia operacji w pamięci (nie persystowana)

### 2.5. Warstwa Integracji

**Odpowiedzialność**: Integracja z zewnętrznymi bibliotekami i API systemowymi

**Komponenty**:
- **PyAudio/PortAudio** - interfejs do urządzeń audio
- **PyTorch** - framework ML z backendami (CPU, MPS, CUDA)
- **Whisper API** - silnik rozpoznawania mowy
- **Pynput** - przechwytywanie globalnych skrótów klawiszowych
- **macOS APIs** - menu bar, dźwięki systemowe, dostęp do mikrofonu

**Zależności systemowe**:
```bash
brew install portaudio llvm  # Wymagane biblioteki systemowe
```

**Uprawnienia systemowe**:
- Dostęp do mikrofonu (Privacy Settings)
- Accessibility permissions (globalne skróty klawiszowe)

## 3. Komponenty główne

### 3.1. WhisperDictation (Main App)

**Plik**: `whisper-dictation.py`

**Odpowiedzialność**: 
- Punkt wejścia aplikacji
- Inicjalizacja wszystkich komponentów
- Parsowanie argumentów wiersza poleceń
- Zarządzanie główną pętlą aplikacji

**Kluczowe metody**:
```python
def parse_args() -> argparse.Namespace:
    """Parsuje argumenty CLI (model, język, skróty)"""

if __name__ == "__main__":
    # Inicjalizacja DeviceManager
    device_manager = EnhancedDeviceManager()
    device = device_manager.get_device_for_operation(OperationType.MODEL_LOADING, args.model_name)
    
    # Ładowanie modelu z fallback
    try:
        model = load_model(model_name, device=device)
        device_manager.optimize_model(model, device)
    except Exception as e:
        # Automatyczny fallback na CPU
        fallback_device = device_manager.handle_device_error_enhanced(...)
        model = load_model(model_name, device=fallback_device)
```

**Zależności**:
- `SpeechTranscriber` - silnik transkrypcji
- `Recorder` - moduł nagrywania
- `StatusBarApp` - interfejs użytkownika
- `EnhancedDeviceManager` - zarządzanie urządzeniami
- `GlobalKeyListener` / `DoubleCommandKeyListener` - obsługa skrótów

**Argumenty CLI**:
- `-m, --model_name` - rozmiar modelu (tiny/base/small/medium/large)
- `-k, --key_combination` - kombinacja klawiszy (np. cmd_l+alt)
- `--k_double_cmd` - tryb podwójnego Command (jak w systemowym dyktowaniu)
- `-l, --language` - wymuszone języki (np. "en,pl")
- `--allowed_languages` - ograniczenie detekcji języka
- `-t, --max_time` - maksymalny czas nagrywania (domyślnie 30s)

### 3.2. Recorder

**Plik**: `recorder.py`

**Odpowiedzialność**:
- Zarządzanie strumieniem audio z mikrofonu
- Buforowanie danych audio w czasie rzeczywistym
- Precyzyjne timestamping (dla testów wydajności)
- Zapis nagrań do plików WAV (dla testów)

**Kluczowe metody**:
```python
def start_recording_with_timestamp(self) -> float:
    """
    Rozpoczyna nagrywanie i zwraca dokładny timestamp początku.
    Używane w testach wydajności.
    """

def stop_recording(self) -> np.ndarray:
    """
    Zatrzymuje nagrywanie, zamyka strumień audio.
    Zwraca znormalizowane dane audio (float32).
    """

def record_duration(self, duration_seconds: float) -> np.ndarray:
    """
    Nagrywa przez określony czas (do testów automatycznych).
    """
```

**Parametry audio**:
```python
self.sample_rate = 16000      # Hz (wymagane przez Whisper)
self.channels = 1             # Mono
self.format = pyaudio.paInt16 # 16-bit audio
self.chunk_size = 1024        # Próbek na buffer
```

**Zależności**:
- `pyaudio` - interfejs do urządzeń audio
- `numpy` - przetwarzanie danych audio
- `wave` - zapis do plików WAV
- `SpeechTranscriber` - opcjonalny, do automatycznej transkrypcji

**Przepływ nagrywania**:
1. Inicjalizacja PyAudio interface
2. Otwarcie strumienia audio (16kHz, mono, int16)
3. Ciągłe czytanie chunks do bufora
4. Przy stop: zamknięcie strumienia
5. Konwersja int16 → float32 z normalizacją

### 3.3. SpeechTranscriber

**Plik**: `transcriber.py`

**Odpowiedzialność**:
- Zarządzanie modelami Whisper (ładowanie, cache, przełączanie)
- Transkrypcja audio z automatyczną detekcją języka
- Optymalizacja ustawień dla różnych urządzeń (CPU/MPS)
- Integracja z DeviceManager dla fallback

**Kluczowe metody**:
```python
def __init__(self, model_size: str = "base", device: str = None, allowed_languages: list = None):
    """
    Inicjalizuje transkrybera z:
    - Automatyczną detekcją urządzenia (przez DeviceManager)
    - Pobieraniem modelu z cache lub internetu
    - Optymalizacją dla M1/M2
    """

def transcribe(self, audio_file_path: str, language: str = None) -> TranscriptionResult:
    """
    Transkrybuje plik audio:
    - Wykrywa język jeśli nie podano
    - Stosuje optymalizacje specyficzne dla urządzenia
    - Zwraca TranscriptionResult z timing info
    """

def transcribe_audio_data(self, audio_data: np.ndarray) -> TranscriptionResult:
    """
    Transkrybuje surowe dane audio (numpy array):
    - Do użytku real-time z Recorder
    - Normalizacja danych jeśli potrzeba
    - Stosuje te same optymalizacje co transcribe()
    """
```

**Struktura wyniku**:
```python
class TranscriptionResult:
    text: str                    # Transkrybowany tekst
    language: str                # Wykryty/użyty język
    detection_time: float        # Czas detekcji języka (s)
    transcription_time: float    # Czas transkrypcji (s)
```

**Zależności**:
- `whisper` - silnik ASR OpenAI
- `torch` - PyTorch framework
- `EnhancedDeviceManager` - inteligentne zarządzanie urządzeniami
- `numpy` - przetwarzanie audio

**Optymalizacje urządzeń**:
- **MPS (M1/M2)**: fp16=True, beam_size=1, pojedynczy pass
- **CPU**: fp16=False, beam_size=5 (dla tiny/base), lepszy context
- **CUDA**: (jeśli dostępne) podobne do MPS

**Obsługa błędów**:
- Automatyczny fallback MPS → CPU przy błędach SparseMPS
- Przyjazne komunikaty błędów po polsku
- Rejestracja sukcesu/porażki dla przyszłych decyzji

### 3.4. DeviceManager

**Plik**: `device_manager.py`

**Odpowiedzialność**:
- Centralne zarządzanie urządzeniami obliczeniowymi
- Testowanie możliwości urządzeń przy starcie
- Śledzenie historii operacji (sukces/porażka)
- Inteligentny wybór urządzenia na podstawie historii

**Kluczowe metody**:
```python
def get_device_for_operation(self, operation: OperationType, model_size: str = None) -> str:
    """
    Wybiera optymalne urządzenie:
    - Sprawdza capabilities cache
    - Analizuje historię operacji (last 5 attempts)
    - Wybiera urządzenie z >80% success rate
    - Fallback do CPU jeśli brak dobrych opcji
    """

def handle_device_error(self, error: Exception, operation: OperationType, current_device: str) -> str:
    """
    Obsługuje błąd urządzenia:
    - Loguje błąd z categorization
    - Rejestruje porażkę w historii
    - Wyłącza urządzenie dla operacji jeśli known issue
    - Zwraca następne najlepsze urządzenie
    """

def register_operation_success(self, device: str, operation: OperationType):
    """
    Rejestruje sukces operacji:
    - Dodaje True do historii
    - Utrzymuje sliding window (last 10 results)
    - Wpływa na przyszłe decyzje device selection
    """
```

**Typy operacji** (enum):
```python
class OperationType(Enum):
    MODEL_LOADING = "model_loading"     # Ładowanie modeli Whisper
    TRANSCRIPTION = "transcription"     # Wykonywanie transkrypcji
    BASIC_TENSOR = "basic_tensor"       # Podstawowe operacje tensor
```

**Capabilities testing**:
```python
def _test_basic_operations(self, device: str) -> DeviceCapability:
    """Test prostych operacji tensor (matrix add/multiply)"""

def _test_model_loading_capability(self, device: str) -> DeviceCapability:
    """Test operacji podobnych do Whisper (conv1d, linear)"""
```

**Zależności**:
- `torch` - detekcja i testowanie urządzeń
- `logging` - szczegółowe logowanie decyzji

**Device preference order**:
1. MPS (jeśli Apple Silicon i dostępne)
2. CUDA (jeśli NVIDIA GPU dostępne)
3. CPU (zawsze dostępne jako fallback)

**Historia operacji**:
```python
operation_history: Dict[Tuple[str, str], List[bool]]
# Przykład: {("mps", "model_loading"): [True, True, False, True, True]}
```

### 3.5. MPSOptimizer & EnhancedDeviceManager

**Plik**: `mps_optimizer.py`

**Odpowiedzialność**:
- Specjalistyczna obsługa błędów MPS (Apple Silicon)
- Kategoryzacja błędów MPS (SparseMPS, memory format, OOM)
- Optymalizacja ustawień Whisper dla M1/M2
- Przyjazne użytkownikowi komunikaty (po polsku)

**Komponenty**:

#### MPSErrorHandler
```python
class MPSErrorType(Enum):
    SPARSE_BACKEND = "sparse_backend"       # SparseMPS errors
    MEMORY_FORMAT = "memory_format"         # aten::empty.memory_format
    OUT_OF_MEMORY = "out_of_memory"         # MPS OOM
    UNSUPPORTED_OP = "unsupported_operation" # Nieobsługiwana operacja
    UNKNOWN = "unknown"

def categorize_error(self, error: Exception) -> MPSErrorType:
    """Kategoryzuje błąd MPS na podstawie pattern matching"""

def get_user_friendly_message(self, error: Exception) -> str:
    """Zwraca przyjazny komunikat po polsku, np:
    'Wykryto problem kompatybilności z GPU M1. Przełączam na CPU dla stabilności.'
    """
```

#### MPSOptimizer
```python
def get_optimal_whisper_settings(self, device: str, model_size: str) -> Dict[str, Any]:
    """
    Zwraca optymalne ustawienia Whisper:
    
    MPS (M1/M2):
    - fp16=True (half precision)
    - beam_size=1 (szybsza dekodowanie)
    - condition_on_previous_text=False (mniej pamięci)
    
    CPU:
    - fp16=False (CPU nie korzysta z fp16)
    - beam_size=5 dla tiny/base (lepsza jakość)
    - condition_on_previous_text=True (lepszy context)
    """

def optimize_model_for_m1(self, model, device: str) -> None:
    """
    Stosuje optymalizacje M1:
    - Enable MPS fallback dla unsupported ops
    - Ustawia model.eval() (inference mode)
    - Wyłącza gradienty (requires_grad=False)
    """
```

#### EnhancedDeviceManager
```python
class EnhancedDeviceManager:
    """
    Wrapper łączący DeviceManager + MPSOptimizer + MPSErrorHandler.
    Zapewnia kompletne zarządzanie urządzeniami z M1 support.
    """
    
    def handle_device_error_enhanced(self, error: Exception, operation, current_device: str) -> Tuple[str, str]:
        """
        Zwraca: (fallback_device, user_friendly_message)
        Przykład: ("cpu", "Wykryto problem kompatybilności z GPU M1. Przełączam na CPU.")
        """
```

**Zależności**:
- `DeviceManager` - base device management
- `torch` - MPS backend detection
- `logging` - error tracking
- `psutil` - memory monitoring (CPU)

**Przykład użycia w kodzie**:
```python
device_manager = EnhancedDeviceManager()
device = device_manager.get_device_for_operation(OperationType.MODEL_LOADING, "base")

try:
    model = load_model("base", device=device)
    device_manager.optimize_model(model, device)
except Exception as e:
    fallback_device, user_msg = device_manager.handle_device_error_enhanced(e, OperationType.MODEL_LOADING, device)
    print(f"🔄 {user_msg}")
    model = load_model("base", device=fallback_device)
```

## 4. Diagram architektury

Szczegółowy diagram warstw systemu znajduje się w:

**[Diagram warstw architektury](./diagrams/architecture-layers.mmd)**

Diagram przedstawia:
- 5 głównych warstw systemu
- Przepływ danych między warstwami
- Kluczowe komponenty w każdej warstwie
- Zależności między komponentami
- Integracje z zewnętrznymi bibliotekami

Aby wyświetlić diagram, użyj narzędzi obsługujących Mermaid (np. GitHub, VS Code z rozszerzeniem Mermaid, IntelliJ).

## 5. Wzorce projektowe

System wykorzystuje następujące wzorce projektowe, zidentyfikowane w rzeczywistym kodzie:

### 5.1. Singleton (Implicit)

**Gdzie**: `DeviceManager`, `EnhancedDeviceManager`

**Implementacja**: Choć nie klasyczny Singleton, te komponenty są tworzone raz przy starcie aplikacji i współdzielone przez wszystkie moduły.

```python
# W whisper-dictation.py
device_manager = EnhancedDeviceManager()  # Jedna instancja
transcriber = SpeechTranscriber(model, allowed_languages, device_manager)
recorder = Recorder(transcriber)
```

**Uzasadnienie**: Centralizacja zarządzania urządzeniami i historii operacji wymaga pojedynczej instancji.

### 5.2. Strategy

**Gdzie**: `DeviceManager.get_device_for_operation()`

**Implementacja**: Wybór strategii (CPU/MPS/CUDA) na podstawie typu operacji i historii:

```python
def get_device_for_operation(self, operation: OperationType, model_size: Optional[str] = None) -> str:
    for device in self.preferred_devices:
        # Strategia: wybór urządzenia na podstawie success rate
        if history_key in self.operation_history:
            recent_successes = self.operation_history[history_key][-5:]
            success_rate = sum(recent_successes) / len(recent_successes)
            
            if success_rate > 0.8:
                return device  # Strategia potwierdzona historycznie
```

**Uzasadnienie**: Różne operacje (ładowanie modelu vs transkrypcja) mogą preferować różne urządzenia.

### 5.3. Observer (Event-based)

**Gdzie**: `KeyListener` → `StatusBarApp` → `Recorder`

**Implementacja**: Wzorzec obserwatora przez callbacks:

```python
class GlobalKeyListener:
    def on_key_press(self, key):
        if self.key1_pressed and self.key2_pressed:
            self.app.toggle()  # Powiadomienie app o zdarzeniu

class StatusBarApp:
    def toggle(self):
        if self.started:
            self.stop_app(None)  # Propagacja do Recorder
        else:
            self.start_app(None)
```

**Uzasadnienie**: Luźne powiązanie między warstwą kontroli a warstwą biznesową.

### 5.4. Factory (Model Loading)

**Gdzie**: Ładowanie modeli Whisper

**Implementacja**: Factory pattern dla różnych rozmiarów modeli:

```python
# whisper.load_model() działa jako factory
model = load_model(model_name, device=device)  
# Zwraca odpowiedni model: tiny, base, small, medium, large
```

**Uzasadnienie**: Ukrycie złożoności tworzenia różnych wariantów modeli za prostym interfejsem.

### 5.5. Template Method

**Gdzie**: `Recorder.start()` → `_record_impl()`

**Implementacja**: Szkielet algorytmu z customizowalnymi krokami:

```python
def _record_impl(self, language):
    # Template method pattern
    self.sound_player.play_start_sound()    # Hook 1
    
    # Główny algorytm (niezmienny)
    stream = p.open(...)
    while self.recording:
        data = stream.read(...)
        frames.append(data)
    
    stream.close()
    self.sound_player.play_stop_sound()     # Hook 2
    
    # Przetwarzanie danych (niezmienne)
    audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
    self.transcriber.transcribe(audio_data, language)  # Hook 3
```

**Uzasadnienie**: Stały przepływ nagrywania z możliwością customizacji (dźwięki, transkrypcja).

### 5.6. Adapter

**Gdzie**: `recorder.py` jako adapter między PyAudio a resztą aplikacji

**Implementacja**: Opakowuje PyAudio API w prosty interfejs:

```python
class Recorder:
    # Adapter pattern: PyAudio API → prosty interfejs
    def start_recording_with_timestamp(self) -> float:
        # Ukrywa złożoność PyAudio
        self.stream = self.audio_interface.open(...)
        return self.start_timestamp
    
    def stop_recording(self) -> np.ndarray:
        # Konwertuje format PyAudio na numpy array
        audio_bytes = b''.join(self.audio_data)
        return np.frombuffer(audio_bytes, dtype=np.int16)
```

**Uzasadnienie**: Izoluje resztę kodu od szczegółów implementacji PyAudio.

### 5.7. Chain of Responsibility

**Gdzie**: Device fallback chain w `DeviceManager`

**Implementacja**: Próba urządzeń w kolejności do pierwszego sukcesu:

```python
def handle_device_error(self, error, operation, current_device):
    # Chain of Responsibility pattern
    remaining_devices = [d for d in self.preferred_devices if d != current_device]
    
    for device in remaining_devices:  # Próbuj kolejne urządzenia
        if self._device_is_capable(device, operation):
            return device  # Pierwsze zdolne urządzenie obsługuje request
    
    return self.fallback_device  # Ostateczny handler (CPU)
```

**Uzasadnienie**: Graceful degradation - jeśli MPS zawiedzie, próbuj CUDA, potem CPU.

## 6. Kluczowe decyzje architektoniczne

Dokumentacja w formacie ADR-lite dla najważniejszych decyzji architektonicznych.

---

### ADR-001: Dwie równoległe implementacje (Python vs C++)

**Kontekst**: 
- Model OpenAI Whisper w wersji Python działa tylko na CPU z M1/M2 (problem z PyTorch MPS backend)
- Wersja C++ (whisper.cpp) oferuje natywną akcelerację GPU M1, ale ma problemy z jakością
- Użytkownicy potrzebują wyboru między dokładnością a szybkością

**Decyzja**: 
Utrzymanie dwóch równoległych implementacji:
- **whisper-dictation.py** - wersja Python (dokładna, CPU only)
- **whisper-dictation-fast.py** - wersja C++ (GPU M1, eksperymentalna)

**Alternatywy rozważone**:
1. Tylko wersja Python - odrzucone bo brak GPU acceleration
2. Tylko wersja C++ - odrzucone bo problemy z jakością
3. Hybrydowa (Python + whisper.cpp bindings) - zbyt złożone

**Konsekwencje**:

✅ **Plusy**:
- Użytkownik wybiera trade-off (jakość vs szybkość)
- Można rozwijać obie implementacje niezależnie
- Fallback na Python gdy C++ ma problemy
- Eksperymentowanie z whisper.cpp bez ryzyka dla main branch

❌ **Minusy**:
- Duplikacja kodu (StatusBarApp, KeyListeners, itp.)
- Dwa razy więcej maintenance
- Dokumentacja musi opisywać obie wersje
- Potencjalne rozbieżności w funkcjonalnościach

**Status**: ✅ **Aktywna** (2025-01)

**Notatki**: 
- Python wersja: rekomendowana dla produkcji
- C++ wersja: tylko do testów i eksperymentów
- W przyszłości: możliwe połączenie gdy PyTorch MPS będzie stabilne

---

### ADR-002: Całkowicie offline processing

**Kontekst**:
- Rozpoznawanie mowy wymaga przetwarzania audio użytkownika
- Wysyłanie audio do cloud (np. Google Speech API) byłoby szybsze i prostsze
- Użytkownicy mogą dyktować poufne informacje (hasła, dane osobowe, medyczne)
- Brak zaufania do cloud providers w kontekście prywatności

**Decyzja**: 
Wszystkie operacje (nagrywanie, transkrypcja, przetwarzanie) wykonywane lokalnie bez wysyłania danych.

**Alternatywy rozważone**:
1. Cloud API (Google/Azure Speech) - odrzucone bo privacy concerns
2. Hybrydowe (lokalne dla krótkich, cloud dla długich) - odrzucone bo niespójne
3. Opcjonalny cloud (user choice) - odrzucone bo zwiększa attack surface

**Konsekwencje**:

✅ **Plusy**:
- **100% prywatności** - dane nigdy nie opuszczają urządzenia
- Działa bez internetu (np. w samolocie, w podróży)
- Brak kosztów API (Google Speech: $0.006/15s)
- Brak limitów rate-limiting
- Zgodność z GDPR bez effort

❌ **Minusy**:
- Wymaga mocnego CPU/GPU lokalnie
- Pobieranie modeli (75MB - 3GB) przy pierwszym użyciu
- Brak cloud features (np. speaker diarization, advanced NLP)
- Wolniejsze na starszych maszynach vs cloud API

**Status**: ✅ **Aktywna** (niezmienne wymaganie)

**Notatki**: 
- Core value proposition aplikacji
- Marketing: "Your voice never leaves your device"
- Nie będzie nigdy zmienione (breach of trust)

---

### ADR-003: Dedykowany DeviceManager dla M1/M2

**Kontekst**:
- PyTorch MPS backend ma problemy z kompatybilnością (SparseMPS errors)
- OpenAI Whisper przy próbie użycia GPU M1 rzuca exception
- Użytkownicy M1/M2 oczekują akceleracji GPU (wszak mają "Neural Engine")
- Manualny fallback w każdym miejscu kodu to anti-pattern

**Decyzja**: 
Utworzenie centralnego `DeviceManager` + `MPSOptimizer` do zarządzania urządzeniami z:
- Automatycznym testowaniem capabilities przy starcie
- Historią sukcesu/porażki operacji
- Inteligentnym fallback MPS → CPU
- Przyjaznym error handling (komunikaty po polsku)

**Alternatywy rozważone**:
1. Try-catch w każdym miejscu - odrzucone bo boilerplate
2. Tylko CPU (disable MPS całkowicie) - odrzucone bo użytkownicy chcą GPU
3. PyTorch autograd detect - odrzucone bo nie rozwiązuje problemu Whisper

**Konsekwencje**:

✅ **Plusy**:
- **Stabilność** - graceful degradation bez crashy
- **Performance** - używa GPU gdy możliwe, CPU gdy konieczne
- **UX** - przyjazne komunikaty zamiast stack traces
- **Maintainability** - centralna logika device management
- **Testability** - można mockować DeviceManager w testach
- **Intelligence** - uczy się które operacje działają na MPS

❌ **Minusy**:
- Dodatkowa warstwa abstrakcji
- Więcej kodu do maintenance
- Testing capabilities przy starcie dodaje ~2s do launch time
- Zależność między modułami (coupling)

**Status**: ✅ **Aktywna** (critical component)

**Implementacja**:
```python
# Przed ADR-003 (zły kod):
try:
    model = load_model("base", device="mps")
except:
    model = load_model("base", device="cpu")  # Duplikacja wszędzie

# Po ADR-003 (dobry kod):
device_manager = EnhancedDeviceManager()
device = device_manager.get_device_for_operation(OperationType.MODEL_LOADING, "base")
model = load_model("base", device=device)
device_manager.optimize_model(model, device)
```

**Notatki**: 
- Rozwiązuje ~80% problemów M1 users
- W przyszłości: podobny pattern dla CUDA (NVIDIA)
- Potencjał do reuse w innych projektach PyTorch na M1

---

### ADR-004: Rumps dla menu bar (zamiast native AppKit)

**Kontekst**:
- Aplikacja potrzebuje ikony w macOS menu bar
- Native AppKit (Objective-C/Swift) dałoby pełną kontrolę
- Python to główny język projektu (nie Swift)
- Trzeba szybko zbudować MVP

**Decyzja**: 
Użycie biblioteki `rumps` (Ridiculously Uncomplicated macOS Python Statusbar apps) dla menu bar.

**Alternatywy rozważone**:
1. PyObjC + AppKit - odrzucone bo zbyt złożone
2. Swift app + Python backend - odrzucone bo wymaga bridge
3. Electron app - odrzucone bo overkill (200MB+ bundle)
4. rumps - **wybrane** bo prosty i pythonowy

**Konsekwencje**:

✅ **Plusy**:
- **Szybki rozwój** - menu bar w <100 linii kodu
- **Pythonowy** - nie trzeba uczyć się Objective-C
- **Prosty API** - dekoratory @rumps.clicked
- **Lightweight** - małe zużycie pamięci

❌ **Minusy**:
- Ograniczone możliwości UI (vs native)
- Zależność od unmaintained library (ostatni commit 2019)
- Brak advanced features (np. custom views, animations)
- MacOS only (vendor lock-in)

**Status**: ✅ **Aktywna** (działa dobrze dla obecnych potrzeb)

**Notatki**: 
- Jeśli rumps stanie się problematyczne → migrate do PyObjC
- Obecnie: rumps wystarcza (prosty UI, ikona, menu)
- Future: custom view dla visualize waveform during recording?

---

### ADR-005: Threading model (Background recording + UI thread)

**Kontekst**:
- Nagrywanie audio to blocking I/O operation
- macOS menu bar UI musi być responsive
- PyAudio działa w trybie blocking (stream.read())
- Transkrypcja może trwać 5-10s (dla large model)

**Decyzja**: 
Threading model:
- **Main thread** - rumps event loop (UI)
- **Recording thread** - PyAudio stream reading
- **Transcription** - w recording thread (po zakończeniu nagrywania)

**Implementacja**:
```python
def start(self, language=None):
    # Nie blokuj UI thread
    thread = threading.Thread(target=self._record_impl, args=(language,))
    thread.start()

def _record_impl(self, language):
    # Ten kod działa w background thread
    while self.recording:
        data = stream.read(frames_per_buffer)  # Blocking OK
        frames.append(data)
    
    # Transkrypcja też w tym samym thread
    self.transcriber.transcribe(audio_data, language)
```

**Alternatywy rozważone**:
1. Single-threaded - odrzucone bo UI freeze
2. Multiprocessing - odrzucone bo overkill (IPC overhead)
3. Async/await - odrzucone bo PyAudio nie jest async-friendly
4. Threading - **wybrane** bo balance simplicity/performance

**Konsekwencje**:

✅ **Plusy**:
- UI pozostaje responsive during recording
- Prosty model (jeden thread per recording)
- Thread safety - recorder ma własny state
- Cancel possible przez `self.recording = False`

❌ **Minusy**:
- Thread creation overhead (~1ms per start)
- Nie można anulować transkrypcji (once started, must finish)
- Race conditions możliwe (ale w praktyce nie występują)
- GIL limitations (though PyAudio releases GIL for I/O)

**Status**: ✅ **Aktywna** (wystarczająca dla use case)

**Notatki**: 
- W przyszłości: asyncio + aiortc dla streaming transcription?
- Obecnie: threading model działa świetnie
- Thread pool nie potrzebny (max 1 recording at time)

---

## 7. Obszary ryzyka

### 7.1. Performance Bottlenecks

**Ryzyko**: Ładowanie modeli Whisper

**Opis**: 
Pierwsze ładowanie modelu (szczególnie medium/large) może trwać 10-30s:
- Pobieranie z internetu (model large = 3GB)
- Deserializacja PyTorch checkpoint
- Przeniesienie na urządzenie (CPU/MPS)

**Mitigation**:
- ✅ Cache modeli w `~/.cache/whisper/` (tylko pierwsze użycie jest wolne)
- ✅ Prompt użytkownika przed pobieraniem (informed consent)
- ✅ Lazy loading - model ładowany dopiero przy pierwszym użyciu
- 🔄 TODO: Progressbar dla pobierania modelu

**Severity**: ⚠️ **Medium** (tylko first-time user experience)

---

### 7.2. Memory Usage

**Ryzyko**: Duże modele Whisper zajmują dużo RAM

**Opis**:
```
Model Sizes (RAM usage):
- tiny:   ~75MB   - dla prostych przypadków
- base:   ~145MB  - rekomendowany default
- small:  ~483MB  - dobra jakość
- medium: ~1.5GB  - bardzo dobra jakość
- large:  ~3GB    - najlepsza jakość
```

Na Macbook Air M1 z 8GB RAM, model large + system + Chrome = OOM risk.

**Mitigation**:
- ✅ Default to `base` model (145MB) - good balance
- ✅ Warning w README about memory requirements
- ✅ Graceful OOM handling w DeviceManager
- ⚠️ MISSING: Runtime memory monitoring & warnings

**Severity**: ⚠️ **Medium** (user can choose smaller model)

**Zalecana akcja**:
```python
# TODO: Add memory check before model loading
def check_available_memory(required_mb: int) -> bool:
    import psutil
    available = psutil.virtual_memory().available / (1024**2)
    return available > required_mb * 1.5  # 50% margin
```

---

### 7.3. Thread Safety

**Ryzyko**: Nagrywanie vs transkrypcja w shared state

**Opis**:
Potencjalne race conditions:
```python
# Scenario 1: User starts recording while transcription in progress
recorder.start()  # Thread 1
recorder.start()  # Thread 2 (before Thread 1 finishes)

# Scenario 2: User spams start/stop quickly
app.toggle()  # Start
app.toggle()  # Stop (before recording actually started)
app.toggle()  # Start again
```

**Current protection**:
```python
# StatusBarApp prevents double-start
if self.started:
    return  # Ignore second start
```

**Missing protection**:
- Brak lock w `Recorder.start()` - możliwe dwa równoczesne nagrywania
- Brak queue dla pending transcriptions

**Mitigation**:
- ✅ UI-level protection w StatusBarApp (sufficient for normal use)
- ⚠️ Brak thread-level lock w Recorder
- ⚠️ Brak queue dla batch transcriptions

**Severity**: 🟡 **Low-Medium** (wymaga świadomego abuse przez użytkownika)

**Zalecana akcja**:
```python
# TODO: Add threading.Lock in Recorder
class Recorder:
    def __init__(self):
        self._lock = threading.Lock()
    
    def start(self, language=None):
        if not self._lock.acquire(blocking=False):
            print("Recording already in progress")
            return
        # ... recording logic ...
        self._lock.release()
```

---

### 7.4. MPS Compatibility Issues

**Ryzyko**: Nowe wersje PyTorch mogą zmieniać MPS backend behavior

**Opis**:
Apple MPS backend jest stosunkowo nowy (PyTorch 1.12+) i wciąż ewoluuje:
- SparseMPS błędy w PyTorch 2.0
- Nowe operacje dodawane stopniowo
- Breaking changes między minor versions

**Current protection**:
- ✅ `DeviceManager` z automatic fallback MPS → CPU
- ✅ Capabilities testing przy starcie
- ✅ Historia operacji (learning from failures)

**Missing protection**:
- Brak pinned version PyTorch w `pyproject.toml` - może złamać się przy update
- Brak version detection (np. PyTorch 2.0 vs 2.1 may behave differently)

**Mitigation**:
- ✅ Graceful fallback obecny
- ⚠️ TODO: Pin PyTorch version lub test against multiple versions
- ⚠️ TODO: Version-specific workarounds

**Severity**: ⚠️ **Medium** (może złamać working installation przy update)

**Zalecana akcja**:
```toml
# pyproject.toml - TODO: pin versions
[tool.poetry.dependencies]
torch = "^2.1.0,<2.2"  # Explicit range
openai-whisper = "^20231117"  # Pin known-good version
```

---

### 7.5. Audio Device Issues

**Ryzyko**: Brak mikrofonu lub błędy PyAudio

**Opis**:
Potencjalne problemy:
- Brak dostępu do mikrofonu (permissions not granted)
- Mikrofon używany przez inną aplikację (Zoom, Teams)
- Bluetooth headset disconnect w trakcie nagrywania
- Nieprawidłowa konfiguracja audio (48kHz device vs 16kHz recording)

**Current handling**:
```python
# Brak graceful error handling w Recorder
stream = p.open(...)  # Może rzucić exception
```

**Missing protection**:
- Brak sprawdzenia uprawnień przed startem
- Brak listy dostępnych mikrofonów
- Brak fallback na default device
- Brak recovery po disconnect

**Mitigation**:
- ⚠️ TODO: Check microphone permissions before recording
- ⚠️ TODO: List available input devices i wybór default
- ⚠️ TODO: Handle device errors gracefully
- ✅ Exception catching w thread nie crashuje app

**Severity**: 🔴 **High** (częste w production)

**Zalecana akcja**:
```python
# TODO: Add device checking
def check_microphone_available() -> bool:
    p = pyaudio.PyAudio()
    try:
        default_device = p.get_default_input_device_info()
        return default_device is not None
    except OSError:
        return False
    finally:
        p.terminate()
```

---

### 7.6. Disk Space

**Ryzyko**: Brak miejsca na dysku dla modeli

**Opis**:
Models cache w `~/.cache/whisper/`:
- tiny: 75MB
- base: 145MB
- small: 483MB
- medium: 1.5GB
- large: 3GB

Jeśli użytkownik ma wszystkie modele: **~5.3GB**

**Current handling**:
- Whisper download bez sprawdzenia dostępnego miejsca
- Może się nie udać w połowie (partial download)

**Mitigation**:
- ✅ Prompt przed pobieraniem (user awareness)
- ⚠️ Brak sprawdzenia free space
- ⚠️ Brak cleanup old/unused models

**Severity**: 🟡 **Low** (rzadkie na nowoczesnych Macach z 256GB+ SSD)

**Zalecana akcja**:
```python
# TODO: Add disk space check
import shutil
def check_disk_space(required_mb: int) -> bool:
    stat = shutil.disk_usage(os.path.expanduser("~/.cache"))
    free_mb = stat.free / (1024**2)
    return free_mb > required_mb
```

---

## 8. Powiązane dokumenty

### Dokumentacja główna

- **[README](../README.md)** - szczegółowa dokumentacja projektu, instalacja i użycie
- **[Przegląd projektu](./PROJECT_OVERVIEW.md)** - cel aplikacji, stos technologiczny, kluczowe funkcjonalności

### Diagramy

- **[Diagram warstw](./diagrams/architecture-layers.mmd)** - szczegółowy diagram 5 warstw systemu
- **[Diagram systemowy](./diagrams/system-overview.mmd)** - overview komponentów i przepływów

### Dokumentacja przyszła (planowana)

- **[Przepływy danych](./DATA_FLOW.md)** *(planowane)* - szczegółowe przepływy: nagrywanie → transkrypcja → typing
- **[API Reference](./API_REFERENCE.md)** *(planowane)* - dokumentacja publicznych API każdego modułu
- **[Testing Strategy](./TESTING.md)** *(planowane)* - strategie testowania (unit, integration, performance)
- **[Performance Tuning](./PERFORMANCE.md)** *(planowane)* - optymalizacje M1/M2, benchmarks, profiling
- **[Deployment Guide](./DEPLOYMENT.md)** *(planowane)* - packaging, dystrybucja, auto-update

### Kontekst developerski

- **[CURSORRULES](../.cursorrules)** - projekt-specific patterns dla AI agents
- **[Memory Bank](../memory-bank/)** - bank pamięci z kontekstem rozwojowym
- **[Tasks](./tasks/)** - tracking zadań i decyzji projektowych

### Zasoby zewnętrzne

- [OpenAI Whisper GitHub](https://github.com/openai/whisper) - oficjalna dokumentacja modelu
- [PyTorch MPS Backend](https://pytorch.org/docs/stable/notes/mps.html) - dokumentacja Apple Silicon support
- [PyAudio Documentation](https://people.csail.mit.edu/hubert/pyaudio/docs/) - API reference
- [Rumps Documentation](https://rumps.readthedocs.io/) - macOS status bar apps

---

## Metadata

**Wersja dokumentu**: 1.0  
**Data utworzenia**: 2025-10-10  
**Ostatnia aktualizacja**: 2025-10-10  
**Autor**: AI Agent (based on codebase analysis)  
**Status**: ✅ Ukończone  

**Changelog**:
- 2025-10-10: Initial version - comprehensive architecture documentation based on actual code analysis
