# Feature: Zautomatyzowane testy dla implementacji C++ (whisper-cli)
**Status**: Draft
**Priority**: Critical
**Complexity**: Medium

## Overview
Celem jest stworzenie zestawu zautomatyzowanych testów w `pytest` dla zewnętrznego narzędzia `whisper-cli` (implementacji C++). Testy te muszą w pierwszej kolejności odtwarzać znane błędy (tzw. testy regresji), takie jak ucinanie audio i błędny tryb transkrypcji. Następnie, po naprawieniu błędów, testy te posłużą jako siatka bezpieczeństwa, chroniąca przed przyszłymi regresjami.

## Acceptance Criteria
- [ ] Istnieje test, który sprawdza, czy transkrypcja audio nie jest ucinana na początku ani na końcu. Test powinien zakończyć się niepowodzeniem na obecnej, wadliwej wersji `whisper-cli`.
- [ ] Istnieje test, który weryfikuje, że `whisper-cli` poprawnie wykonuje transkrypcję (a nie tłumaczenie) dla języka polskiego, gdy język nie jest jawnie specificznie podany. Test powinien zakończyć się niepowodzeniem na obecnej wersji.
- [ ] Istnieje test weryfikujący poprawną detekcję języka dla próbki w języku polskim.
- [ ] Istnieje test weryfikujący poprawną detekcję języka dla próbki w języku angielskim.
- [ ] Wszystkie nowe testy są zintegrowane z `pytest` i uruchamiają się razem z istniejącymi testami dla wersji pythonowej.
- [ ] Testy wykorzystują te same próbki audio z katalogu `tests/audio/`, które są używane przez testy wersji pythonowej.

## File Changes Required
- `tests/test_whisper_cpp.py` (nowy plik): Główny plik z logiką testów dla `whisper-cli`.
- `tests/conftest.py` (modyfikacja): Możliwa potrzeba dodania nowych fixture'ów lub funkcji pomocniczych do uruchamiania `whisper-cli` jako subprocesu i przechwytywania jego wyniku.

## Integration Points
- Testy będą musiały w bezpieczny sposób lokalizować i uruchamiać plik wykonywalny `whisper-cli`. Należy przyjąć strategię, że znajduje się on w systemowej ścieżce `PATH` (zainstalowany np. przez Homebrew).
- Logika testów będzie opierać się na uruchomieniu `whisper-cli` z odpowiednimi flagami jako subprocesu (`subprocess`), a następnie na analizie i asercjach na podstawie przechwyconego standardowego wyjścia (`stdout`) i wyjścia błędów (`stderr`).
