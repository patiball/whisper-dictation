# Rekomendacje dla projektu `whisper-dictation` na podstawie `macos-dictate`

## Wprowadzenie
Ten dokument podsumowuje kluczowe elementy z projektu `macos-dictate`, które mogą zostać zaadaptowane do `whisper-dictation` w celu zwiększenia jego stabilności, niezawodności i dojrzałości jako aplikacji działającej w tle na macOS. Rekomendacje te koncentrują się na aspektach inżynierii oprogramowania, które poprawiają zarządzanie zasobami systemowymi i odporność na błędy.

---

## 1. Mechanizm pliku blokady (Lock File)

### Ogólne wyjaśnienie
Plik blokady to prosty mechanizm zapobiegający uruchomieniu wielu instancji tej samej aplikacji jednocześnie. Jest to kluczowe dla aplikacji działających w tle, aby uniknąć konfliktów zasobów (np. dostępu do mikrofonu) i nieprzewidzianych zachowań. Jeśli aplikacja wykryje istniejący plik blokady, oznacza to, że inna instancja już działa, i powinna się zakończyć.

### Przykład implementacji z `macos-dictate/dictate.py`

```python
import os
import sys
import psutil
import atexit

LOCK_FILE = "/tmp/dictate.lock"

def setup_lock_file():
    if os.path.exists(LOCK_FILE):
        with open(LOCK_FILE, "r") as f:
            old_pid = int(f.read().strip())
            if psutil.pid_exists(old_pid):
                print(f"Another instance is already running with PID {old_pid}. Exiting.")
                sys.exit(0)
    
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))

def cleanup_lock_file():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
        print("Lock file removed.")

# Użycie w głównym bloku:
# setup_lock_file()
# atexit.register(cleanup_lock_file)
```

---

## 2. Watchdog strumienia audio

### Ogólne wyjaśnienie
Watchdog strumienia audio to mechanizm monitorujący ciągłość i poprawność działania wejścia audio. Aplikacje do dyktowania są wrażliwe na przerwy w strumieniu audio. Watchdog regularnie sprawdza, czy dane audio są odbierane. Jeśli strumień "zawieje się" (stalls), watchdog próbuje go zrestartować, co znacznie zwiększa stabilność aplikacji podczas długotrwałego użytkowania.

### Przykład implementacji z `macos-dictate/dictate.py`

```python
import time
from datetime import datetime
import logging
# ... (importy dla sounddevice, show_notification, restart_audio_stream) ...

# Globalne zmienne do monitorowania
last_heartbeat = datetime.now()
audio_timeout = 10  # sekundy
watchdog_active = True # Zmienna kontrolująca działanie wątku watchdog

def update_heartbeat():
    global last_heartbeat
    last_heartbeat = datetime.now()

def watchdog_monitor():
    global watchdog_active, recording, transcribing, stream, stream_healthy
    logging.info("Watchdog thread started")
    while watchdog_active:
        try:
            if recording: # Monitoruj tylko gdy nagrywanie jest aktywne
                time_since_heartbeat = (datetime.now() - last_heartbeat).total_seconds()
                if time_since_heartbeat > audio_timeout:
                    logging.warning(f"Audio system stalled! No heartbeat for {time_since_heartbeat:.1f}s")
                    # show_notification("Dictation Error", "Audio system stalled, recovering...")
                    # restart_audio_stream() # Funkcja do zaimplementowania
            time.sleep(1) # Sprawdzaj co sekundę
        except Exception as e:
            logging.error(f"Watchdog error: {e}")
            time.sleep(5) # Poczekaj dłużej po błędzie

# Funkcja restart_audio_stream() wymagałaby pełnego kontekstu aplikacji
# i dostępu do globalnych zmiennych stream, recording, transcribing, audio_queue.
# Jej implementacja jest dłuższa i zależy od konkretnej architektury.
```

---

## 3. Proaktywne sprawdzanie dostępu do mikrofonu

### Ogólne wyjaśnienie
W systemie macOS aplikacje potrzebują uprawnień do dostępu do mikrofonu. Proaktywne sprawdzenie tych uprawnień na starcie aplikacji pozwala na wczesne wykrycie problemów i ewentualne wyświetlenie monitu o uprawnienia, zanim użytkownik napotka błędy podczas próby nagrywania.

### Przykład implementacji z `macos-dictate/dictate.py`

```python
import sounddevice as sd
import logging

def test_microphone_access():
    try:
        sd.check_input_settings()
        logging.info("Microphone access test passed.")
    except Exception as e:
        logging.error(f"Microphone access test failed: {e}")
        # Można dodać powiadomienie dla użytkownika
        # show_notification("Dictation Error", "Brak dostępu do mikrofonu")

# Użycie w głównym bloku:
# test_microphone_access()
```

---

## 4. Solidna obsługa sygnałów i czyszczenie zasobów

### Ogólne wyjaśnienie
Aplikacje działające w tle powinny prawidłowo reagować na sygnały systemowe (np. Ctrl+C w terminalu, sygnały zakończenia procesu). Zapewnienie, że zasoby (takie jak pliki blokady, otwarte strumienie audio) są prawidłowo zwalniane przy zakończeniu działania, jest kluczowe dla czystości systemu i zapobiegania błędom.

### Przykład implementacji z `macos-dictate/dictate.py`

```python
import signal
import atexit
import os
import logging
# ... (def cleanup_lock_file() i inne funkcje czyszczące) ...

# Przykład funkcji czyszczącej strumień audio (wymaga globalnej zmiennej 'stream')
def cleanup_audio_stream():
    global stream
    if stream is not None:
        try:
            stream.stop()
            stream.close()
            logging.info("Audio stream closed during shutdown.")
        except Exception as e:
            logging.warning(f"Error closing stream during shutdown: {e}")

def signal_exit_handler(signum, frame):
    logging.info(f"Received signal {signum}, shutting down...")
    global watchdog_active # Jeśli używasz watchdoga
    watchdog_active = False
    cleanup_lock_file()
    cleanup_audio_stream() # Wywołaj funkcję czyszczącą strumień
    os._exit(0) # Użycie os._exit(0) zamiast sys.exit(0) w handlerach sygnałów

# Użycie w głównym bloku:
# atexit.register(cleanup_lock_file)
# atexit.register(cleanup_audio_stream) # Zarejestruj czyszczenie strumienia
# signal.signal(signal.SIGINT, signal_exit_handler)
# signal.signal(signal.SIGTERM, signal_exit_handler)
```

---

## 5. Kompleksowe logowanie do pliku

### Ogólne wyjaśnienie
Dla aplikacji działających w tle, które nie mają interfejsu graficznego, logowanie do pliku jest podstawowym narzędziem do monitorowania ich działania, diagnozowania problemów i zrozumienia, co dzieje się w tle. Zapisywanie logów z datą i godziną, poziomem ważności i szczegółowymi komunikatami jest niezbędne.

### Przykład implementacji z `macos-dictate/dictate.py`

```python
import logging
from pathlib import Path

LOG_FILE = Path.home() / '.dictate.log' # Logi w katalogu domowym użytkownika

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO, # Można zmienić na DEBUG dla bardziej szczegółowych logów
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Przykładowe użycie:
# logging.info("Aplikacja uruchomiona.")
# logging.warning("Wykryto problem.")
# logging.error("Wystąpił krytyczny błąd.")
```