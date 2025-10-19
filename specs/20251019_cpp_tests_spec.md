# Feature: Zautomatyzowane testy dla implementacji C++ (whisper-cli)
**Status**: Draft
**Priority**: Critical
**Complexity**: Medium
**Last Updated**: 2025-10-19

## Overview
Celem jest stworzenie zestawu zautomatyzowanych testów w `pytest` dla zewnętrznego narzędzia `whisper-cli` (implementacji C++). Testy te muszą w pierwszej kolejności odtwarzać znane błędy (tzw. testy regresji), takie jak ucinanie audio i błędny tryb transkrypcji. Następnie, po naprawieniu błędów, testy te posłużą jako siatka bezpieczeństwa, chroniąca przed przyszłymi regresjami.

## Acceptance Criteria
- [ ] Istnieje test, który sprawdza, czy transkrypcja audio nie jest ucinana na początku ani na końcu; weryfikacja przez obecność „kotwic” z początku i końca nagrania w oknach ~20% długości (min 0.3 s, max 0.8 s). Test powinien zakończyć się niepowodzeniem na obecnej, wadliwej wersji `whisper-cli`.
- [ ] Test „transkrypcja ≠ tłumaczenie” (PL): przy autodetekcji 'pl' i bez ustawiania trybu tłumaczenia, wynik ma być po polsku; weryfikacja heurystyczna (przewaga polskich tokenów/diakrytyków, brak treści w pełni przetłumaczonej na angielski). Test powinien obecnie zawodzić (regresja).

<!-- UWAGA (Heurystyka języka): Implementacja będzie musiała określić konkretną metodę weryfikacji "przewagi polskich tokenów", np. poprzez zliczenie wystąpień znaków [ąćęłńóśźż] w stosunku do całej treści. -->
- [ ] Detekcja języka (PL): kod 'pl' z confidence ≥ 0.90 (jeśli CLI raportuje confidence) dla próbki polskiej.
- [ ] Detekcja języka (EN): kod 'en' z confidence ≥ 0.90 (jeśli CLI raportuje confidence) dla próbki angielskiej.

<!-- UWAGA (Confidence Level): Należy zweryfikować podczas implementacji, czy `whisper-cli` faktycznie zwraca metrykę 'confidence'. Jeśli nie, kryterium będzie musiało zostać uproszczone do samej weryfikacji kodu języka. -->
- [ ] Wszystkie nowe testy są zintegrowane z `pytest` i uruchamiają się razem z istniejącymi testami dla wersji pythonowej.
- [ ] Testy wykorzystują próbki audio z katalogu `tests/audio/`, wybierane dynamicznie wg charakterystyk (bez twardych nazw); możliwe nadpisanie przez zmienne środowiskowe.
- [ ] Integracja z pytest: markery np. `@pytest.mark.whisper_cpp` i możliwość selektywnego uruchamiania.
- [ ] Bezpieczeństwo w CI i równoległości: brak kolizji plików tymczasowych/wyjściowych; testy skipowane gdy binarka/model niedostępne.

## File Changes Required
- Test file for C++ whisper-cli: Główny plik z logiką testów dla `whisper-cli` w katalogu `tests/`.
- `tests/conftest.py` (modyfikacja): Możliwa potrzeba dodania nowych fixture'ów lub funkcji pomocniczych do uruchamiania `whisper-cli` i przechwytywania jego wyniku.

## Audio Test Data
Testy powinny wykorzystywać próbki audio dostępne w katalogu `tests/audio/` z następującymi charakterystykami:
- Próbka polskojęzyczna (~5-10 sekund): zawierająca treść do transkrypcji
- Próbka anglojęzyczna (~5-10 sekund): zawierająca treść do detekcji języka
- Próbka z treścią na początku i końcu: do testowania ucinania audio

Implementacja powinna być elastyczna w wyborze konkretnych plików - mogą być wybierane dynamicznie na podstawie wzorca nazwy lub daty modyfikacji.

## Integration Points
- Testy muszą być w stanie lokalizować i uruchamiać narzędzie `whisper-cli`. Implementacja powinna sprawdzić dostępność w systemowej ścieżce `PATH` lub pozwolić na konfigurację lokalizacji.
- Logika testów powinna uruchomić `whisper-cli` z odpowiednimi flagami i przeanalizować wynik (stdout/stderr). Implementacja może wykorzystać `subprocess` lub inne, równoważne podejście.
- W przypadku niedostępności `whisper-cli`, test powinien zostać pominięty (pytest.skip) lub zgłosić błąd z jasną wiadomością.

## Error Handling Requirements
- **Brakujący binary**: Graceful handling i skip test z informacją o braku `whisper-cli`
- **Timeout**: Obsługa timeoutu przy przetwarzaniu audio (sugerowany timeout ~30s dla pliku ~10 sekund)
- **Brakujące pliki audio**: Wyraźny komunikat błędu, jeśli test audio nie istnieje
- **stderr output**: Jeśli `whisper-cli` zwrócił błąd na stderr, test powinien go zalogować i zareagować odpowiednio

## Test Invocation Contract
- Lokalizacja binarki: przez PATH lub zmienną środowiskową `WHISPER_CLI_BIN`.
- Model: ścieżka do modelu przez `WHISPER_CLI_MODEL` (jeśli wymagana). Brak modelu w CI -> `pytest.skip`.
- Tryb: wymuszona transkrypcja (nie tłumaczenie). Jeśli narzędzie wspiera jawny wybór, użyć odpowiednika 'task=transcribe'.
- Format wyjścia: preferowany ustrukturyzowany (JSON) jeśli wspierany; inaczej parsowanie tekstu. Minimalnie: tekst; jeśli dostępne: kod języka i confidence.

## Verification Methods and Metrics
- Nieucinanie audio: asercje na obecność kotwic start/koniec po normalizacji tekstu; fuzzy match ≥ 0.7.
- Transkrypcja, nie tłumaczenie: przy autodetekcji 'pl' treść wyjściowa ma być w języku polskim (heurystyki lingwistyczne dopuszczalne; implementacja wybiera metodę).
- Detekcja języka: sukces, gdy kod ∈ {'pl','en'} oraz confidence ≥ 0.90 (jeśli CLI raportuje confidence).

## Flakiness i Równoległość
- Retries: opcjonalnie 1 ponowna próba dla testów wrażliwych, z ostrzeżeniem przy pierwszym niepowodzeniu.
- Polityka timeout: `timeout_sec = max(10, 5 + 3 * długość_audio_w_sek)`; nadpisywalne `WHISPER_CLI_TIMEOUT_SEC`.
- Równoległość: unikalne katalogi tymczasowe na test; brak stałych nazw plików wyjściowych.

## Konfiguracja (ENV)
- `WHISPER_CLI_BIN` – ścieżka do binarki (nadpisuje PATH)
- `WHISPER_CLI_MODEL` – ścieżka do modelu (jeśli wymagana)
- `WHISPER_CLI_TIMEOUT_SEC` – nadpisanie timeoutu
- `WHISPER_CPP_SKIP` – gdy ustawione, testy są pomijane
## Notes
- Testy regresji powinny być oznaczone i będą wstępnie zawodzić na obecnej, buggy wersji `whisper-cli`
- Po naprawieniu błędów w `whisper-cli`, testy będą służyć jako siatka bezpieczeństwa
