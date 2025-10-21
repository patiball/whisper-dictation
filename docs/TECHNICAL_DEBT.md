# TECHNICAL DEBT - Inwentarz długu technicznego

**Data utworzenia**: 2025-10-10
**Ostatnia aktualizacja**: 2025-10-21
**Projekt**: whisper-dictation
**Wersja**: 1.1

---

## 1. Wprowadzenie

Ten dokument stanowi kompleksowy inwentarz długu technicznego w projekcie whisper-dictation. Identyfikuje problemy dotyczące jakości kodu, architektury, wydajności, testowania i dokumentacji, które mogą wpłynąć na przyszły rozwój i utrzymanie projektu.

### Cel dokumentu
- Identyfikacja i kategoryzacja długu technicznego
- Priorytetyzacja prac refaktoryzacyjnych
- Śledzenie postępu w redukcji długu
- Transparentność dla zespołu i stakeholderów

### Jak używać tego dokumentu
1. Zapoznaj się z kategoriami długu (Sekcja 2)
2. Przejrzyj tabelę długu z priorytetami (Sekcja 3)
3. Sprawdź rekomendacje i plan działania (Sekcja 4)
4. Zapoznaj się z metrykami długu (Sekcja 5)

---

## 2. Kategorie długu technicznego

### 2.1. Code Quality (Jakość kodu)
Duplikacje kodu, złożoność cyklomatyczna, code smells, brak separation of concerns.

### 2.2. Performance (Wydajność)
Bottlenecki wydajnościowe, nieoptymalne algorytmy, problemy z pamięcią.

### 2.3. Testing (Testowanie)
Brak testów, niewystarczające pokrycie, brak testów integracyjnych.

### 2.4. Documentation (Dokumentacja)
Brakujące lub nieaktualne docstringi, brak dokumentacji API, niejasne komentarze.

### 2.5. Architecture (Architektura)
Design smells, problemy z dependency injection, tight coupling, brak modularności.

### 2.6. Security & Safety (Bezpieczeństwo)
Problemy z obsługą błędów, brak walidacji, potencjalne wycieki pamięci.

---

## 3. Tabela długu technicznego

| ID | Kategoria | Opis | Lokalizacja | Ryzyko | Wpływ | Priorytet | Status |
|----|-----------|------|-------------|--------|-------|-----------|--------|
| **TD-001** | Code Quality | Duplikacja kodu device detection w 3 miejscach | `whisper-dictation.py`, `transcriber.py`, `device_manager.py` | High | High | **Must** | ✅ Częściowo (DeviceManager istnieje, ale duplikacje pozostały) |
| **TD-002** | Code Quality | Duplikacja logiki SoundPlayer w 3 wersjach aplikacji | `whisper-dictation.py:75-97`, `whisper-dictation-fast.py:96-120`, `whisper-dictation-optimized.py:134-158` | Medium | Medium | **Should** | 🔴 Open |
| **TD-003** | Code Quality | Duplikacja klasy Recorder w 3 wersjach | `whisper-dictation.py:99-142`, `whisper-dictation-fast.py:121-163`, `whisper-dictation-optimized.py:159-213` | Medium | High | **Should** | 🔴 Open |
| **TD-004** | Code Quality | Duplikacja klasy StatusBarApp w 3 wersjach | `whisper-dictation.py:192-267`, `whisper-dictation-fast.py:184-259`, `whisper-dictation-optimized.py:234-309` | Medium | High | **Should** | 🔴 Open |
| **TD-005** | Code Quality | Duplikacja key listener logic (GlobalKeyListener, DoubleCommandKeyListener) | `whisper-dictation.py:144-191`, `whisper-dictation-fast.py:164-183` | Low | Medium | **Could** | 🔴 Open |
| **TD-006** | Architecture | Brak modularyzacji - 3 monolityczne pliki aplikacji zamiast shared modules | `whisper-dictation*.py` (375, 326, 376 linii) | High | High | **Must** | 🔴 Open |
| **TD-007** | Testing | Brak testów dla DeviceManager error handling | `device_manager.py:183-227` | High | Medium | **Should** | 🔴 Open |
| **TD-008** | Testing | Brak testów dla MPSErrorHandler | `mps_optimizer.py:19-104` | Medium | Medium | **Should** | 🔴 Open |
| **TD-009** | Testing | Brak testów dla SoundPlayer (odtwarzanie dźwięków) | `whisper-dictation.py:75-97` | Low | Low | **Could** | 🔴 Open |
| **TD-010** | Testing | Brak testów thread safety dla Recorder | `recorder.py`, `whisper-dictation.py:99-142` | Medium | High | **Should** | 🔴 Open |
| **TD-011** | Documentation | Brak docstringów w klasach SpeechTranscriber (3 wersje) | `whisper-dictation.py:14-74`, `whisper-dictation-fast.py:15-95` | Medium | Low | **Could** | 🔴 Open |
| **TD-012** | Documentation | Brak docstringów w klasie Recorder (oryginalna wersja) | `whisper-dictation.py:99-142` | Medium | Low | **Could** | 🔴 Open |
| **TD-013** | Documentation | Brak dokumentacji API dla DeviceManager public methods | `device_manager.py` | Medium | Medium | **Should** | 🟡 Partial (niektóre metody mają docstringi) |
| **TD-014** | Performance | Brak memory monitoring dla dużych modeli | `transcriber.py`, `whisper-dictation.py` | Medium | Medium | **Should** | 🔴 Open |
| **TD-015** | Performance | Model loading bez sprawdzenia dostępnej pamięci RAM | `transcriber.py:69-78` | Medium | High | **Should** | 🔴 Open |
| **TD-016** | Performance | Brak disk space check przed pobieraniem modeli | `transcriber.py:62-68`, `whisper-dictation-fast.py:260-282` | Low | Medium | **Could** | 🔴 Open |
| **TD-017** | Security & Safety | Brak lock w Recorder.start() - możliwe równoczesne nagrywania | `recorder.py:125-139`, `whisper-dictation.py:105-108` | Medium | Medium | **Should** | 🔴 Open |
| **TD-018** | Security & Safety | Brak graceful error handling przy brakach uprawnień mikrofonu | `recorder.py:56-72`, `whisper-dictation.py:113-126` | High | High | **Must** | 🔴 Open |
| **TD-019** | Security & Safety | Brak sprawdzenia dostępności mikrofonu przed nagraniem | `recorder.py`, `whisper-dictation.py` | High | High | **Must** | 🔴 Open |
| **TD-020** | Security & Safety | Exception catching zbyt szeroki (bare except) | `whisper-dictation.py:72-73`, `whisper-dictation-fast.py:80-81` | Low | Medium | **Could** | 🔴 Open |
| **TD-021** | Code Quality | Magic numbers w kodzie (timeouts, delays, thresholds) | `whisper-dictation.py:71`, `whisper-dictation-optimized.py:179`, `transcriber.py:65` | Low | Low | **Could** | 🔴 Open |
| **TD-022** | Architecture | Tight coupling SpeechTranscriber - pykeyboard | `whisper-dictation.py:17`, `transcriber.py` | Medium | Medium | **Should** | 🔴 Open |
| **TD-023** | Architecture | Brak dependency injection w głównych klasach | `whisper-dictation.py`, wszystkie wersje | Medium | High | **Should** | 🔴 Open |
| **TD-024** | Code Quality | Brak type hints w większości funkcji | Wszystkie pliki `.py` (szczególnie legacy code) | Medium | Medium | **Should** | 🔴 Open |
| **TD-025** | Performance | Synchroniczne odtwarzanie dźwięków może blokować | `whisper-dictation.py:79-83`, `whisper-dictation-fast.py:105-108` | Low | Low | **Could** | 🟡 Partial (używane threading) |
| **TD-026** | Testing | Brak testów dla whisper-dictation-fast.py | `whisper-dictation-fast.py` (326 linii) | High | High | **Must** | ✅ Zrobione (październik 2025) |
| **TD-027** | Testing | Brak testów dla whisper-dictation-optimized.py | `whisper-dictation-optimized.py` (376 linii) | High | High | **Must** | ✅ Usunięte (plik usunięty, skonsolidowano do fast.py) |
| **TD-028** | Architecture | Brak konfiguracji zewnętrznej (wszystko hardcoded) | Wszystkie pliki główne | Medium | Medium | **Should** | 🔴 Open |
| **TD-029** | Code Quality | Niespójne nazewnictwo (snake_case vs camelCase w tym samym pliku) | `whisper-dictation.py`, `device_manager.py` | Low | Low | **Won't** | 🔴 Open |
| **TD-030** | Performance | Brak cachowania wyników language detection | `transcriber.py:106-196`, `whisper-dictation.py:29-74` | Low | Medium | **Could** | 🟡 Partial (w whisper-optimized) |
| **TD-031** | Architecture | Model download logic duplikowana | `whisper-dictation-fast.py:260-282`, `whisper-dictation-optimized.py:310-332` | Medium | Medium | **Should** | 🔴 Open |
| **TD-032** | Security & Safety | Brak timeout handling dla subprocess calls | `whisper-dictation-fast.py:64`, `whisper-dictation-optimized.py:87` | Medium | Medium | **Should** | 🟡 Partial (jest timeout=30) |
| **TD-033** | Documentation | TODO comments wskazujące na niekompletną implementację | `docs/ARCHITECTURE.md:935,967,1013,1049,1056,1088,1097,1138` | Medium | High | **Should** | 🔴 Open |
| **TD-034** | Testing | Brak regression tests dla MPS compatibility | `device_manager.py`, `mps_optimizer.py` | High | High | **Must** | 🔴 Open |
| **TD-035** | Code Quality | Zbyt długie metody (>50 linii) wymagające ekstrakcji | `transcriber.py:106-196`, `whisper-dictation.py:113-142` | Medium | Medium | **Should** | 🔴 Open |
| **TD-036** | Quality | C++ version - audio cutting during recording | `whisper-dictation-fast.py` | High | High | **Must** | ✅ Rozwiązane (październik 2025) |
| **TD-037** | Quality | C++ version - translation instead of transcription | `whisper-dictation-fast.py` | High | High | **Must** | ✅ Rozwiązane (październik 2025) |
| **TD-038** | Quality | C++ version - language detection issues (Polish → English) | `whisper-dictation-fast.py` | High | High | **Must** | ✅ Rozwiązane (październik 2025) |

---

## 3.1. Rozwiązane problemy (Październik 2025)

### C++ Implementation Quality Fixes ✅

**TD-036: Audio cutting during recording**
- **Problem**: Start sound interfered with recording, cutting initial audio
- **Rozwiązanie**: Delayed start sound by 0.1s using threading.Timer
- **Status**: ✅ Zaimplementowane w `whisper-dictation-fast.py:148`

**TD-037: Translation instead of transcription**
- **Problem**: Whisper-cli was translating to English instead of transcribing
- **Rozwiązanie**: Verified default behavior (no `--translate` flag = transcription mode)
- **Status**: ✅ Zweryfikowane

**TD-038: Language detection issues**
- **Problem**: Polish audio transcribed to English text
- **Rozwiązanie**: Implemented `-l auto` flag for proper language detection
- **Status**: ✅ Zaimplementowane w `whisper-dictation-fast.py:52-61`

**TD-026: Missing tests for C++ version**
- **Rozwiązanie**: Created comprehensive pytest test suite in `tests/test_whisper_cpp.py`
- **Pokrycie**: Language detection, timeout handling, error logging, retries
- **Status**: ✅ Zaimplementowane

**TD-027: whisper-dictation-optimized.py**
- **Rozwiązanie**: File removed, functionality consolidated into `whisper-dictation-fast.py`
- **Status**: ✅ Usunięte

---

## 4. Rekomendacje i priorytetyzacja (MoSCoW)

### 4.1. Must Have (Krytyczne - do wykonania w pierwszej kolejności)

#### TD-001: Unifikacja device detection logic ⚠️ CZĘŚCIOWO ZROBIONE
**Czas realizacji**: 1 dzień  
**Ryzyko**: Niskie (DeviceManager już istnieje)  
**Akcja**:
- Usunąć duplikaty device detection z `whisper-dictation.py` i `transcriber.py`
- Wszędzie używać `DeviceManager.get_device_for_operation()`
- Dodać testy jednostkowe dla pokrycia edge cases

#### TD-006: Modularyzacja aplikacji
**Czas realizacji**: 3-5 dni  
**Ryzyko**: Średnie (duże zmiany strukturalne)  
**Akcja**:
- Wydzielić wspólne moduły: `sound_player.py`, `recorder_base.py`, `status_bar_app_base.py`
- Stworzyć `shared/` lub `common/` folder
- Refaktorować 3 wersje aplikacji do używania wspólnych modułów
- Dodać integration tests

**Priorytet**: Najwyższy - eliminuje TD-002, TD-003, TD-004, TD-005

#### TD-018: Microphone permissions handling
**Czas realizacji**: 1 dzień  
**Ryzyko**: Niskie  
**Akcja**:
```python
def check_microphone_permissions() -> tuple[bool, str]:
    """Check if microphone access is granted."""
    try:
        p = pyaudio.PyAudio()
        device_info = p.get_default_input_device_info()
        p.terminate()
        return True, "OK"
    except OSError as e:
        return False, f"Brak dostępu do mikrofonu: {e}"
```

#### TD-019: Audio device availability check
**Czas realizacji**: 1 dzień  
**Ryzyko**: Niskie  
**Akcja**: Rozszerzyć TD-018 o sprawdzenie dostępności urządzeń przed rozpoczęciem nagrania

#### TD-026, TD-027: Testy dla wersji fast i optimized ✅ ZROBIONE
**Czas realizacji**: 2-3 dni (każda wersja)
**Ryzyko**: Średnie
**Status**: ✅ Ukończone (październik 2025)
**Wykonane akcje**:
- ✅ Stworzono test suite dla wersji fast (`tests/test_whisper_cpp.py`)
- ✅ Usunięto whisper-dictation-optimized.py (skonsolidowano do fast.py)
- ✅ Naprawiono problemy jakości (audio cutting, language detection, translation mode)

#### TD-034: MPS compatibility regression tests
**Czas realizacji**: 2 dni  
**Ryzyko**: Średnie  
**Akcja**:
- Testy dla wszystkich known MPS errors
- Mock PyTorch exceptions
- Testy fallback logic

---

### 4.2. Should Have (Ważne - drugorzędny priorytet)

#### TD-007, TD-008: Testy dla device management
**Czas realizacji**: 2 dni  
**Akcja**: Unit tests dla `DeviceManager` i `MPSErrorHandler`

#### TD-010: Thread safety tests dla Recorder
**Czas realizacji**: 1 dzień  
**Akcja**: 
- Testy concurrent recording attempts
- Testy race conditions
- Dodać `threading.Lock` w Recorder (TD-017)

#### TD-013: Dokumentacja API dla DeviceManager
**Czas realizacji**: 0.5 dnia  
**Akcja**: Dodać docstringi do wszystkich public methods

#### TD-014, TD-015: Memory monitoring
**Czas realizacji**: 2 dni  
**Akcja**:
```python
def check_available_memory(required_mb: int) -> bool:
    import psutil
    available = psutil.virtual_memory().available / (1024**2)
    return available > required_mb * 1.5  # 50% margin
```

#### TD-017: Threading.Lock w Recorder
**Czas realizacji**: 0.5 dnia  
**Akcja**: Dodać lock do zapobiegania równoczesnym nagraniom

#### TD-022, TD-023: Architecture improvements (DI, decoupling)
**Czas realizacji**: 3-4 dni  
**Akcja**:
- Wprowadzić dependency injection
- Rozdzielić SpeechTranscriber od keyboard typing
- Stworzyć abstraction layers

#### TD-024: Type hints
**Czas realizacji**: 2-3 dni  
**Akcja**: Dodać type hints do wszystkich funkcji, użyć mypy do walidacji

#### TD-028: Zewnętrzna konfiguracja
**Czas realizacji**: 2 dni  
**Akcja**: Stworzyć `config.yaml` dla parametrów (timeouts, thresholds, etc.)

#### TD-031: Unifikacja model download logic
**Czas realizacji**: 1 dzień  
**Akcja**: Wydzielić do `model_downloader.py`

#### TD-033: Implementacja TODO z ARCHITECTURE.md
**Czas realizacji**: 5-7 dni (rozproszone)  
**Akcja**: Systematycznie implementować TODOs z dokumentacji architektonicznej

#### TD-035: Refactoring długich metod
**Czas realizacji**: 2-3 dni  
**Akcja**: Extract method refactoring dla metod >50 linii

---

### 4.3. Could Have (Nice to have - niższy priorytet)

#### TD-005: Refactoring key listener logic
**Czas realizacji**: 1 dzień

#### TD-009: Testy SoundPlayer
**Czas realizacji**: 0.5 dnia

#### TD-011, TD-012: Docstringi w legacy code
**Czas realizacji**: 1-2 dni

#### TD-016: Disk space check
**Czas realizacji**: 0.5 dnia

#### TD-020: Poprawki bare except
**Czas realizacji**: 0.5 dnia

#### TD-021: Eliminacja magic numbers
**Czas realizacji**: 1 dzień

#### TD-025: Async sound playback (już częściowo zrobione)
**Czas realizacji**: 0.5 dnia (weryfikacja)

#### TD-030: Language detection caching
**Czas realizacji**: 1 dzień

---

### 4.4. Won't Have (Do pominięcia)

#### TD-029: Niespójne nazewnictwo
**Uzasadnienie**: Zbyt dużo pracy przy małym zysku, Python community akceptuje obydwa style

---

## 5. Metryki długu technicznego

### 5.1. Stan obecny (2025-10-10)

| Metryka | Wartość | Target | Status |
|---------|---------|--------|--------|
| **Całkowita liczba items długu** | 35 | < 15 | 🔴 |
| **Must Have items** | 9 | 0 | 🔴 |
| **Should Have items** | 15 | < 5 | 🔴 |
| **Could Have items** | 10 | N/A | 🟡 |
| **Items zamknięte** | 0 | > 20 | 🔴 |
| **Duplikacja kodu (szacunkowo)** | ~40% | < 10% | 🔴 |
| **Test coverage (szacunkowo)** | ~30% | > 80% | 🔴 |
| **Brakujące docstringi** | ~60% | < 10% | 🔴 |

### 5.2. Metryki jakościowe

#### Złożoność cyklomatyczna (szacunkowo):
- `whisper-dictation.py`: **Średnia** (~15-20 per function dla większych metod)
- `device_manager.py`: **Niska-Średnia** (~10-15)
- `transcriber.py`: **Średnia** (~15-20)

#### Długość plików:
- `whisper-dictation.py`: **375 linii** (OK)
- `whisper-dictation-fast.py`: **326 linii** (OK)
- `whisper-dictation-optimized.py`: **376 linii** (OK)
- `device_manager.py`: **272 linii** (OK)
- `mps_optimizer.py`: **251 linii** (OK)
- `transcriber.py`: **297 linii** (OK)

**Ocena**: Pliki nie są zbyt długie, ale brak modularyzacji zwiększa duplikację.

### 5.3. Dependency metrics
- **Circular dependencies**: 0 ✅
- **Tight coupling spots**: 5-7 (TD-022, TD-023)
- **Missing abstractions**: 3-4

---

## 6. Roadmap eliminacji długu

### Sprint 1 (Tydzień 1-2): Foundation & Safety
**Cel**: Stabilność i bezpieczeństwo  
**Items**: TD-018, TD-019, TD-001, TD-034  
**Effort**: 5-7 dni  

### Sprint 2 (Tydzień 3-4): Modularization
**Cel**: Eliminacja duplikacji  
**Items**: TD-006, TD-002, TD-003, TD-004, TD-031  
**Effort**: 5-7 dni  

### Sprint 3 (Tydzień 5-6): Testing Coverage
**Cel**: Zwiększenie pokrycia testami  
**Items**: TD-026, TD-027, TD-007, TD-008, TD-010  
**Effort**: 7-10 dni  

### Sprint 4 (Tydzień 7-8): Architecture & Performance
**Cel**: Poprawa architektury i wydajności  
**Items**: TD-014, TD-015, TD-017, TD-022, TD-023  
**Effort**: 5-7 dni  

### Sprint 5 (Tydzień 9-10): Documentation & Polish
**Cel**: Dokumentacja i dopracowanie  
**Items**: TD-013, TD-024, TD-028, TD-033, TD-035  
**Effort**: 5-7 dni  

### Sprint 6+ (Maintenance): Nice to have
**Items**: TD-005, TD-009, TD-011, TD-012, TD-016, TD-020, TD-021, TD-025, TD-030

---

## 7. Monitoring postępu

### Tracking
- Review tego dokumentu **co 2 tygodnie**
- Update statusów items po każdym sprint review
- Dodawanie nowych items gdy zostaną zidentyfikowane
- Archiwizacja zamkniętych items (sekcja Appendix)

### Definicje statusów:
- 🔴 **Open**: Nie rozpoczęto prac
- 🟡 **Partial**: Częściowo zaimplementowane
- 🟢 **In Progress**: Aktywnie rozwiązywane
- ✅ **Done**: Zamknięte i zweryfikowane

### Metryki sukcesu (3 miesiące):
- [ ] Redukcja Must Have items do 0
- [ ] Redukcja Should Have items o 50%
- [ ] Test coverage > 60%
- [ ] Duplikacja kodu < 20%
- [ ] Dokumentacja (docstringi) > 70%

---

## 8. Powiązane dokumenty

- **REFACTORING_PLAN.md**: Szczegółowy plan refaktoryzacji
- **docs/ARCHITECTURE.md**: Dokumentacja architektury (TODO markers)
- **specs/20250130_m1_support_fix.md**: Spec dla M1 support
- **specs/20250130_whisper_cpp_quality_fix.md**: Spec dla whisper.cpp fixes

---

## 9. Changelog

| Data | Autor | Zmiana |
|------|-------|--------|
| 2025-10-10 | AI Agent | Utworzenie dokumentu - initial inventory |

---

**Ostatnia aktualizacja**: 2025-10-19  
**Następny review**: 2025-11-02

---

## Metadata

**Wersja dokumentu**: 1.1  
**Data utworzenia**: 2025-10-10  
**Ostatnia aktualizacja**: 2025-10-19  
**Autor**: AI Agent  
**Status**: ✅ Ukończone  

**Changelog**:
- 2025-10-19: Aktualizacja daty ostatniej aktualizacji.
- 2025-10-10: Utworzenie dokumentu - initial inventory.
