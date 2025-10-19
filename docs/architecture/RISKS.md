# Analiza Ryzyk Architektury

Ten dokument zawiera szczegółową analizę ryzyk związanych z architekturą aplikacji Whisper Dictation, wraz z proponowanymi strategiami mitygacji.

## Cel

Celem tego dokumentu jest zidentyfikowanie potencjalnych problemów, które mogą wpłynąć na stabilność, wydajność, bezpieczeństwo lub rozwój systemu, oraz przedstawienie planów zarządzania tymi ryzykami.

## Spis Treści

1.  [Ryzyka Wydajnościowe](#ryzyka-wydajnościowe)
2.  [Ryzyka Związane z Zużyciem Pamięci](#ryzyka-związane-z-zużyciem-pamięci)
3.  [Ryzyka Związane z Bezpieczeństwem Wątków](#ryzyka-związane-z-bezpieczeństwem-wątków)
4.  [Ryzyka Kompatybilności MPS](#ryzyka-kompatybilności-mps)
5.  [Ryzyka Związane z Urządzeniami Audio](#ryzyka-związane-z-urządzeniami-audio)
6.  [Ryzyka Związane z Miejscem na Dysku](#ryzyka-związane-z-miejscem-na-dysku)

## Ryzyka Wydajnościowe

### Ryzyko: Ładowanie modeli Whisper

**Opis**: Pierwsze ładowanie modelu (szczególnie medium/large) może trwać 10-30s:
- Pobieranie z internetu (model large = 3GB)
- Deserializacja PyTorch checkpoint
- Przeniesienie na urządzenie (CPU/MPS)

**Mitygacja**:
- ✅ Cache modeli w `~/.cache/whisper/` (tylko pierwsze użycie jest wolne)
- ✅ Prompt użytkownika przed pobieraniem (informed consent)
- ✅ Lazy loading - model ładowany dopiero przy pierwszym użyciu
- 🔄 TODO: Progressbar dla pobierania modelu

**Waga Ryzyka**: ⚠️ **Medium** (tylko first-time user experience)

## Ryzyka Związane z Zużyciem Pamięci

### Ryzyko: Duże modele Whisper zajmują dużo RAM

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

**Mitygacja**:
- ✅ Default to `base` model (145MB) - good balance
- ✅ Warning w README about memory requirements
- ✅ Graceful OOM handling w DeviceManager
- ⚠️ MISSING: Runtime memory monitoring & warnings

**Waga Ryzyka**: ⚠️ **Medium** (user can choose smaller model)

**Zalecana akcja**:
```python
# TODO: Add memory check before model loading
def check_available_memory(required_mb: int) -> bool:
    import psutil
    available = psutil.virtual_memory().available / (1024**2)
    return available > required_mb * 1.5  # 50% margin
```

## Ryzyka Związane z Bezpieczeństwem Wątków

### Ryzyko: Nagrywanie vs transkrypcja w shared state

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

**Obecna ochrona**:
```python
# StatusBarApp prevents double-start
if self.started:
    return  # Ignore second start
```

**Brakująca ochrona**:
- Brak lock w `Recorder.start()` - możliwe dwa równoczesne nagrywania
- Brak queue dla pending transcriptions

**Mitygacja**:
- ✅ UI-level protection w StatusBarApp (sufficient for normal use)
- ⚠️ Brak thread-level lock w Recorder
- ⚠️ Brak queue dla batch transcriptions

**Waga Ryzyka**: 🟡 **Low-Medium** (wymaga świadomego abuse przez użytkownika)

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

## Ryzyka Kompatybilności MPS

### Ryzyko: Nowe wersje PyTorch mogą zmieniać MPS backend behavior

**Opis**:
Apple MPS backend jest stosunkowo nowy (PyTorch 1.12+) i wciąż ewoluuje:
- SparseMPS błędy w PyTorch 2.0
- Nowe operacje dodawane stopniowo
- Breaking changes między minor versions

**Obecna ochrona**:
- ✅ `DeviceManager` z automatic fallback MPS → CPU
- ✅ Capabilities testing przy starcie
- ✅ Historia operacji (learning from failures)

**Brakująca ochrona**:
- Brak pinned version PyTorch w `pyproject.toml` - może złamać się przy update
- Brak version detection (np. PyTorch 2.0 vs 2.1 may behave differently)

**Mitygacja**:
- ✅ Graceful fallback obecny
- ⚠️ TODO: Pin PyTorch version lub test against multiple versions
- ⚠️ TODO: Version-specific workarounds

**Waga Ryzyka**: ⚠️ **Medium** (może złamać working installation przy update)

**Zalecana akcja**:
```toml
# pyproject.toml - TODO: pin versions
[tool.poetry.dependencies]
torch = "^2.1.0,<2.2"  # Explicit range
openai-whisper = "^20231117"  # Pin known-good version
```

## Ryzyka Związane z Urządzeniami Audio

### Ryzyko: Brak mikrofonu lub błędy PyAudio

**Opis**:
Potencjalne problemy:
- Brak dostępu do mikrofonu (permissions not granted)
- Mikrofon używany przez inną aplikację (Zoom, Teams)
- Bluetooth headset disconnect w trakcie nagrywania
- Nieprawidłowa konfiguracja audio (48kHz device vs 16kHz recording)

**Obecna obsługa**:
```python
# Brak graceful error handling w Recorder
stream = p.open(...)  # Może rzucić exception
```

**Brakująca ochrona**:
- Brak sprawdzenia uprawnień przed startem
- Brak listy dostępnych mikrofonów
- Brak fallback na default device
- Brak recovery po disconnect

**Mitygacja**:
- ⚠️ TODO: Check microphone permissions before recording
- ⚠️ TODO: List available input devices i wybór default
- ⚠️ TODO: Handle device errors gracefully
- ✅ Exception catching w thread nie crashuje app

**Waga Ryzyka**: 🔴 **High** (częste w production)

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

## Ryzyka Związane z Miejscem na Dysku

### Ryzyko: Brak miejsca na dysku dla modeli

**Opis**:
Models cache w `~/.cache/whisper/`:
- tiny: 75MB
- base: 145MB
- small: 483MB
- medium: 1.5GB
- large: 3GB

Jeśli użytkownik ma wszystkie modele: **~5.3GB**

**Obecna obsługa**:
- Whisper download bez sprawdzenia dostępnego miejsca
- Może się nie udać w połowie (partial download)

**Mitygacja**:
- ✅ Prompt przed pobieraniem (user awareness)
- ⚠️ Brak sprawdzenia free space
- ⚠️ Brak cleanup old/unused models

**Waga Ryzyka**: 🟡 **Low** (rzadkie na nowoczesnych Macach z 256GB+ SSD)

**Zalecana akcja**:
```python
# TODO: Add disk space check
import shutil
def check_disk_space(required_mb: int) -> bool:
    stat = shutil.disk_usage(os.path.expanduser("~/.cache"))
    free_mb = stat.free / (1024**2)
    return free_mb > required_mb
```

## Powiązane Dokumenty

- [ARCHITECTURE.md](../ARCHITECTURE.md) - Główna dokumentacja architektury
- [TECHNICAL_DEBT.md](../../TECHNICAL_DEBT.md) - Dług techniczny (często wynikający z ryzyk)
