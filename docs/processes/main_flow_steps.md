# Główny Przepływ - Kroki Realizacji

Ten dokument szczegółowo opisuje kroki realizacji głównego przepływu (Happy Path) w aplikacji Whisper Dictation.

## 1. Inicjalizacja aplikacji
   - Ładowanie modelu Whisper (tiny/base/small/medium/large)
   - Wybór optymalnego urządzenia (CPU/MPS/CUDA) przez DeviceManager
   - Optymalizacja modelu dla wybranego urządzenia
   - Rejestracja listenera klawiatury

## 2. Użytkownik naciska skrót klawiszowy
   - Domyślnie: `Cmd+Option` (macOS) lub `Ctrl+Alt` (inne)
   - Alternatywnie: podwójne naciśnięcie `Right Command` (--k_double_cmd)

## 3. Rozpoczęcie nagrywania
   - StatusBarApp wywołuje `recorder.start(language)`
   - Odtwarzanie dźwięku "Tink.aiff" (start recording)
   - Timer rozpoczyna odliczanie w ikonie paska menu (🔴)
   - Opcjonalny limit czasu (domyślnie 30s)

## 4. Nagrywanie audio
   - Otwiercie strumienia PyAudio:
     - Format: 16-bit PCM (paInt16)
     - Kanały: 1 (mono)
     - Częstotliwość: 16000 Hz
     - Bufor: 1024 próbki na ramkę
   - Ciągłe zapisywanie ramek audio do listy `frames[]`

## 5. Użytkownik zatrzymuje nagrywanie
   - Zwolnienie skrótu klawiszowego lub upływ max_time
   - StatusBarApp wywołuje `recorder.stop()`

## 6. Przetwarzanie audio
   - Zamknięcie strumienia PyAudio
   - Odtwarzanie dźwięku "Pop.aiff" (stop recording)
   - Konwersja: `bytes` → `np.int16` → `np.float32` (normalizacja przez 32768.0)

## 7. Transkrypcja
   - Wywołanie `transcriber.transcribe(audio_data, language)`
   - Detekcja języka (jeśli nie określono)
   - Walidacja języka względem `allowed_languages` (jeśli ustawione)
   - Model Whisper przetwarza audio z optymalizacjami:
     - FP16 na MPS/CUDA
     - Progi: `no_speech_threshold=0.6`, `logprob_threshold=-1.0`
     - Obsługa błędów z automatycznym fallback (MPS→CPU)

## 8. Wklejanie tekstu
   - Iteracja przez każdy znak w `result["text"]`
   - Pomijanie pierwszej spacji
   - Symulacja wpisywania przez `pykeyboard.type(element)`
   - Opóźnienie 2.5ms między znakami (`time.sleep(0.0025)`)

## 9. Powrót do stanu gotowości
   - Ikona w pasku menu wraca do "⏯"
   - Menu "Start Recording" aktywne ponownie

## Powiązane Dokumenty

- [DATA_FLOW.md](../DATA_FLOW.md) - Główny przepływ danych
- [ARCHITECTURE.md](../../ARCHITECTURE.md) - Architektura systemu
