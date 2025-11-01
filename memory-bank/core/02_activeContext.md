# Active Context

**Current Focus:** 🟢 **EPIC 16 - Implementing Fixes**

**Status:** **CI pipeline and logging tests stabilized.** All dependency, formatting, and logging test issues are resolved. The CI pipeline is now more resilient.

> Bezpieczeństwo (2025-11-01): Aktualizacja CI: usuwamy Python 3.9 z macOS matrix w testach i wymuszamy 'poetry env use' na interpreterze z setup-python, aby uniknąć fallbacku do 3.12 i błędów budowy (numpy/multidict). Zakres: konfiguracja CI, brak zmian kodu. — MP

> Bezpieczeństwo (2025-11-01): Przed wprowadzeniem hotfixu formatowania standaryzujemy Black/isort w `pyproject.toml` i poprawiamy format w 2 testach tak, aby Black w CI przechodził. Zakres: wyłącznie format/konfiguracja — bez zmian funkcjonalnych. — MP

> Aktualizacja (2025-11-01): Dodano sekcje `[tool.black]` i `[tool.isort]` w `pyproject.toml`, wykonano `isort .` i `black .`; lokalnie `black --check .` przechodzi. Oczekiwany zielony lint w CI. — MP

> Bezpieczeństwo (2025-11-01): Zmiany w testach (stabilność i portabilność):
> - test_logging.py: import logging.handlers na poziomie modułu; usunięto import wewnątrz funkcji (naprawa AttributeError/UnboundLocalError)
> - test_audio_watchdog.py: próg czasu restartu podniesiony do 200ms ze względu na zmienność środowiska CI
> - Wszystkie pliki testów: dodano pytestmark = pytest.mark.unit do test_language_detection.py, test_performance.py, test_recording_quality.py; dodano pytest.mark.unit do listy w test_whisper_cpp.py. Przywraca kolekcję z 53 do 76 testów unit.
> Zakres: tylko testy, brak zmian funkcjonalnych w kodzie aplikacji. — MP

**Active Epic:** [16-00-00] Post-Epic 15 Test Infrastructure & Functional Fixes
- **Priority:** High
- **Goal:** To resolve all outstanding issues from Epic 15 and achieve a stable, reliable, and fully functional test infrastructure.

**Completed User Stories:**
- ✅ **[16-01-00] Thread Cleanup Fix** (Priority: Critical) - **COMPLETED**
- ✅ **[16-02-00] Sys Import Regression Fix** (Priority: High) - **COMPLETED**
- ✅ **[16-03-00] Stabilize Logging Tests** (Priority: High) - **COMPLETED**

**Immediate Priorities (from Epic 16):**
1.  **[16-04-00] Whisper.cpp Integration Fixes** (Priority: High)
    -   **Problem:** Core C++ backend functionality is failing in tests.
    -   **Status:** 🟡 **ACTIVE**
2.  **[16-07-00] Verify and Enforce GPU Usage in C++ Tests** (Priority: High)
    -   **Problem:** User observation suggests tests may be incorrectly using the CPU instead of the GPU.
