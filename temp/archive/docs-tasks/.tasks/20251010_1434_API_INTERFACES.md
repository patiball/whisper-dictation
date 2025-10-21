# Zadanie: API_INTERFACES.md

## Data: 2025-10-10 14:34
## Priorytet: HIGH

## Cel
Utworzyć `/Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/API_INTERFACES.md`

## Pliki do przeczytania
- `/Users/mprzybyszewski/dev/ai-projects/whisper-dictation/recorder.py`
- `/Users/mprzybyszewski/dev/ai-projects/whisper-dictation/transcriber.py`
- `/Users/mprzybyszewski/dev/ai-projects/whisper-dictation/device_manager.py`

## Zawartość

### 1. Wprowadzenie
Publiczne interfejsy modułów aplikacji.

### 2. Recorder API
**Klasa**: `Recorder`
- **Metody publiczne**:
  - `start_recording()` - rozpocznij nagrywanie
  - `stop_recording()` - zatrzymaj i zwróć audio
  - `is_recording()` - sprawdź status
- **Parametry**: sample_rate, channels
- **Zwracane typy**: numpy.ndarray
- **Błędy**: MicrophoneError, BufferOverflowError

### 3. Transcriber API
**Klasa**: `SpeechTranscriber`
- **Metody**:
  - `transcribe(audio_data, language=None)` - transkrybuj audio
  - `load_model(model_name)` - załaduj model
  - `detect_language(audio)` - wykryj język
- **Parametry**: model, device, language
- **Zwracane**: string (tekst)
- **Błędy**: ModelNotLoadedError, TranscriptionError

### 4. DeviceManager API
**Klasa**: `DeviceManager`
- **Metody**:
  - `get_optimal_device()` - zwróć najlepsze urządzenie
  - `is_mps_available()` - sprawdź MPS
  - `fallback_to_cpu()` - przełącz na CPU
- **Parametry**: force_cpu
- **Zwracane**: torch.device

### 5. Kontrakty między komponentami
- **Recorder → Transcriber**: numpy array (float32, 16kHz)
- **Transcriber → Clipboard**: string (UTF-8)
- **DeviceManager → Transcriber**: torch.device

### 6. Powiązane dokumenty
```markdown
## Powiązane dokumenty
- [Architektura](./ARCHITECTURE.md)
- [Przepływy danych](./DATA_FLOW.md)
- [Moduły](./MODULES.md)
```

## Wymagania
- Język: Polski
- Format: Markdown
- Długość: 400-600 linii
- Precyzyjne sygnatury metod z kodu
