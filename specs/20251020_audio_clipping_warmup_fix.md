# Spec: Redukcja clippingu na starcie nagrania — mniejsze bufory + warm-up

Status: Ready
Priorytet: High
Zakres: Python (whisper-dictation.py — Recorder)

## 1. Tło i problem
Podczas nagrań sporadycznie ucinane są pierwsze 50–200 ms mowy (clipping początku). Hipoteza: efekt opóźnień inicjalizacji strumienia audio (PyAudio/PortAudio) i/lub pierwszych niestabilnych buforów po starcie. W aktualnym kodzie nie ma celowego odrzucania pierwszej sekundy na potrzeby detekcji języka — clipping nie wynika z logiki transkrypcji.

## 2. Założenia i walidacja (Assumptions & Validation)
- A0: Główną przyczyną clippingu jest niestabilność pierwszych buforów po otwarciu strumienia (nie logika transkrypcji).
- Weryfikacja: Po wdrożeniu zmian zbieramy metryki start_delay/start_silence_ms. Jeśli w ≥20% przypadków występuje >30 ms ciszy na starcie lub brak kotwicy, wracamy do pełnej diagnostyki zgodnie z `memory-bank/specs/plan-audio-clipping-root-cause.md`.

## 3. Cel
- Zmniejszyć opóźnienia i ustabilizować pierwszy odczyt tak, aby zredukować clipping do poziomu niezauważalnego w praktyce.
- Nie wprowadzać istotnego obciążenia ani złożoności — quick, safe fix.

## 4. Zakres zmian
Dotyczy wyłącznie Pythonowej implementacji aplikacji (plik `whisper-dictation.py`, klasa `Recorder`).
- Zmiana wielkości bufora audio (`frames_per_buffer`): 1024 → 512 (opcjonalnie 256, jeśli testy wykażą poprawę bez dropów).
- Wymuszenie bezpiecznego odczytu: `stream.read(..., exception_on_overflow=False)` — redukcja ryzyka dropów na starcie.
- Warm-up po otwarciu strumienia: wykonać 2 pierwsze odczyty i je odrzucić, zanim zaczniemy akumulować ramki do końcowego nagrania.
- Auto-fallback: jeśli w pierwszych 10 odczytach wystąpi ≥3 błędy/overflosy, automatycznie zwiększ `frames_per_buffer` do następnego progu (512→1024) i raz zrestartuj nagranie (z logiem ostrzegawczym).
- Dźwięki start/stop zostają w oddzielnym wątku — bez zmian (nie blokują).

## 5. Kryteria akceptacji (Acceptance Criteria)
- A1: Subiektywnie brak słyszalnego ucinania pierwszych sylab w ≥27/30 powtórzeniach (manualny test krótkich fraz, np. pojedyncze słowo tuż po starcie).
- A2: start_silence_ms ≤ 30 ms w ≥24/30 powtórzeniach, liczony jako: czas od pierwszej zapisanej ramki (po warm-up) do pierwszej próbki o amplitudzie > 10% z maksimum amplitudy w pierwszej sekundzie nagrania (alternatywnie RMS > -40 dBFS). Dokładnie ten algorytm stosujemy w skrypcie pomiarowym.
- A3: Brak zwiększonej częstości błędów nagrywania (overflow/underflow) po zmianach względem stanu bazowego.
- A4: Brak regresji w standardowym przepływie nagrywanie → transkrypcja.

## 6. Projekt rozwiązania (Design)
- Buforowanie:
  - `frames_per_buffer = 512` przy `rate=16000` oznacza ~32 ms latencji na bufor (zamiast ~64 ms przy 1024). Szybszy pierwszy „pełny” blok danych.
- Warm-up (domyślnie odrzucenie):
  - Po `p.open(...)` wykonać:
    - `stream.read(frames_per_buffer, exception_on_overflow=False)` (odrzucić)
    - powtórzyć drugi raz (odrzucić)
  - Odczyty warm-up NIE są dodawane do `frames`.
- Alternatywa (opcjonalna, później):
  - Zamiast odrzucać, zapisać warm-up do bufora tymczasowego i, jeśli wykryto w nich sygnał powyżej progu, dołączyć je do początku nagrania (wymaga prostej detekcji progu i może zwiększyć złożoność — nie w MVP).
- Czytanie właściwe:
  - Pętla `while self.recording:` czyta z `exception_on_overflow=False` i dopisuje do `frames`.
- Auto-fallback:
  - Licznik błędów w pierwszych 10 odczytach; jeśli ≥3, zwiększ bufor i zrestartuj nagranie raz (bez zapętlania).

Pseudo-diff (fragment):
- frames_per_buffer = 512
- stream = p.open(..., frames_per_buffer=frames_per_buffer, input=True)
- warm-up (discard):
```
try:
    _ = stream.read(frames_per_buffer, exception_on_overflow=False)
    _ = stream.read(frames_per_buffer, exception_on_overflow=False)
except Exception:
    pass
```
- main loop:
```
errors = 0
reads = 0
while self.recording:
    try:
        data = stream.read(frames_per_buffer, exception_on_overflow=False)
        frames.append(data)
    except Exception:
        errors += 1
    reads += 1
    if reads <= 10 and errors >= 3 and frames_per_buffer < 1024:
        # escalate buffer and restart once
        escalate_and_restart()
        break
```

## 7. Konfiguracja (MVP)
- CLI:
  - `--frames-per-buffer {256|512|1024}` (domyślnie 512)
  - `--warmup-buffers {0..3}` (domyślnie 2)
- ENV override:
  - `WHISPER_FRAMES_PER_BUFFER` — jeśli ustawione, nadpisuje wartość domyślną/CLI.
- Tryb debug (ENV/CLI):
  - logowanie timestampów: tuż po `open()`, po warm-up, po pierwszym prawidłowym `read()`; log „auto-fallback engaged”.

## 8. Plan testów
- T1 (manualny): 30 krótkich nagrań (1–2 s), wypowiedzenie pierwszego słowa natychmiast po starcie; ocena słyszalnego początku (A1).
- T2 (metryczny): skrypt pomiarowy liczący `start_silence_ms` wg algorytmu z A2; oczekiwanie A2.
- T3 (kotwice/anchor): nagrania z frazami kotwiczącymi (np. „zero one two...”), heurystyczna weryfikacja obecności początku („ze-” z „zero”) w pierwszych 100 ms; ≥27/30 sukcesów.
- T4 (regresyjny): standardowy flow w aplikacji (start/stop, transkrypcja) bez wyjątków i anomalii czasu (A4).

## 9. Rollout
- Wprowadzić zmianę jako domyślną (512 + warm-up 2) z możliwością override przez CLI/ENV.
- Jeśli raporty pokażą wciąż sporadyczny clipping, rozważyć 256 prób na bufor lub zwiększyć `warmup-buffers` do 3; w razie overflow włączyć auto-fallback.

## 10. Ryzyka i mitigacje
- Zbyt mały bufor może zwiększyć obciążenie CPU lub ryzyko overflow — mitigacja: `exception_on_overflow=False`, auto-fallback 512→1024.
- Warm-up odrzuca ~64 ms audio (2×32 ms) — jeśli użytkownik zacznie mówić w 0 ms, to może ściąć pierwsze ~64 ms. Mitigacja: możliwość ustawienia `--warmup-buffers 0` lub wariant z buforem tymczasowym (sekcja 6).

## 11. Zmiany w plikach
- `whisper-dictation.py` — klasa `Recorder`, metoda `_record_impl`:
  - Ustawić `frames_per_buffer = 512` (z odczytem z CLI/ENV i auto-fallbackiem).
  - Dodać warm-up (2 odczyty z `exception_on_overflow=False`).
  - W pętli głównej ustawić `exception_on_overflow=False` i licznik błędów/reads do auto-fallbacku.
  - Dodać (opcjonalnie) minimalne logi debug (gdy włączony tryb debug).
- (Out of Scope) `whisper-dictation-fast.py` — analogiczne zmiany zostaną rozważone w osobnej specyfikacji, jeżeli problem występuje także w wersji C++.

## 12. Kryteria zakończenia
- Potwierdzone spełnienie A1–A4.
- Brak nowych błędów w logach.
- Po 1–2 dniach użycia brak raportów o ucinaniu pierwszych sylab.

## 13. Telemetria/Instrumentacja (opcjonalnie)
- Logi timestampów i auto-fallback events (lokalnie, bez wysyłki).
- Porównanie `start_silence_ms` przed/po wdrożeniu (jeśli istnieją dane sprzed zmiany).

## 14. Follow-up
- Rozszerzenie testów automatycznych (pytest) o heurystyczny test clippingu (wg `specs/20251019_cpp_tests_spec.md`).
- Rozważenie wariantu warm-up z buforem tymczasowym (sekcja 6, alternatywa).
