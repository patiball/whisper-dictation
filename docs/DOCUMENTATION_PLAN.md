# Plan docelowej dokumentacji (Whisper Dictation)

Cel: spójna (coherent), łatwa do nawigacji dokumentacja dla ludzi, z minimalną liczbą „sierotek” i konsekwentnymi linkami między sekcjami. Dokumentacja opiera się na rzeczywistym kodzie i artefaktach generowanych przez proces automatyzacji.

## Zasady ogólne
- Język: polski.
- Spójność: każdy dokument zawiera sekcję „Powiązane dokumenty” z odnośnikami do najbliższych, sąsiednich treści.
- Linki: ścieżki względne w obrębie katalogu docs/.
- Diagramy: Mermaid (.mmd) w docs/diagrams/ (osobne pliki, osadzane w MD referencją).
- „[TO INVESTIGATE]”: jawnie oznaczamy niepewności z audytu.
- Prawda źródłowa: kod w repo + wygenerowane/zweryfikowane artefakty.

## Struktura katalogów
- docs/
  - README.md – główny indeks i mapa całej dokumentacji.
  - PROJECT_OVERVIEW.md – przegląd projektu.
  - ARCHITECTURE.md – architektura systemu.
  - DATA_FLOW.md – przepływy danych i sekwencje.
  - API_INTERFACES.md – kontrakty i publiczne API modułów.
  - MODULES.md – indeks dokumentacji modułowej.
  - REFACTORING_PLAN.md – plan refaktoryzacji.
  - TECHNICAL_DEBT.md – dług techniczny.
  - FILE_INVENTORY.md – inwentarz plików źródłowych.
  - diagrams/ – wszystkie diagramy Mermaid.
  - modules/ – dokumenty per moduł.
  - processes/ – kluczowe ścieżki użytkownika i operacje.
  - context/ – podsumowania pod Memory Bank (dla AI; generowane po audycie).

## Zawartość poszczególnych dokumentów

### 1) docs/README.md (indeks i nawigacja)
- Opis celu dokumentacji i jak z niej korzystać.
- Spis treści z linkami do: PROJECT_OVERVIEW.md, ARCHITECTURE.md, DATA_FLOW.md, API_INTERFACES.md, MODULES.md, REFACTORING_PLAN.md, TECHNICAL_DEBT.md, FILE_INVENTORY.md, processes/ i diagrams/.
- Sekcja „Jak czytać” (rekomendowana kolejność).
- Sekcja „Powiązane dokumenty”.

### 2) docs/PROJECT_OVERVIEW.md
- Cel aplikacji i główne funkcjonalności (krótko, konkretnie).
- Stos technologiczny: języki, frameworki, biblioteki, narzędzia.
- Wysokopoziomowa struktura katalogów z opisem ról.
- Punkty wejścia (entry points) aplikacji i narzędzi.
- Zakres wsparcia platform (np. macOS), wymagania systemowe.
- Sekcja „Current State Assessment” (z audytu).
- Sekcja „Powiązane dokumenty”.

### 3) docs/ARCHITECTURE.md
- Opis architektury (warstwy, komponenty, odpowiedzialności).
- Diagramy:
  - diagrams/architecture-layers.mmd – warstwy i relacje.
  - diagrams/system-overview.mmd – widok high-level systemu (linkowany też z README/Overview).
- Wzorce projektowe i miejsca użycia.
- Kluczowe decyzje architektoniczne (ADR-lite: założenia, kompromisy, konsekwencje).
- Obszary ryzyka i granice kontekstu (bounded contexts, jeśli dotyczy).
- Sekcja „Powiązane dokumenty”.

### 4) docs/DATA_FLOW.md
- Opis głównych przepływów danych: nagrywanie → przetwarzanie Whisper → wynik/akcje.
- Diagramy sekwencji:
  - diagrams/sequence-main-flow.mmd – scenariusz „happy path”.
  - diagrams/sequence-error-handling.mmd – obsługa błędów i retriale.
- Mapowanie zdarzeń i danych (formaty, kontrakty danych).
- Sekcja „Powiązane dokumenty”.

### 5) docs/API_INTERFACES.md
- Publiczne interfejsy każdego modułu (klasy/protokoły/serwisy) – nazwa, odpowiedzialność, metody.
- Kontrakty między komponentami (wejścia/wyjścia, DTO/typy, błędy).
- Stabilność i wersjonowanie interfejsów (jeśli dotyczy).
- Sekcja „Powiązane dokumenty”.

### 6) docs/MODULES.md (indeks)
- Tabela/Lista modułów z krótkim opisem.
- Linki do plików w docs/modules/<moduł>.md.
- Zależności między modułami (mapka referencji do diagramów klas/komponentów).

### 7) docs/modules/<moduł>.md (szablon per moduł)
- Nazwa i odpowiedzialność modułu.
- Publiczne API (sygnatury, krótkie przykłady użycia).
- Diagram klas (Mermaid): diagrams/class-<moduł>.mmd.
- Zależności (depends on / depended by).
- Miejsca użycia w kodzie (ważne entry points).
- TODO/FIXME/HACK (automatycznie wykryte z komentarzy).
- Sugestie refaktoryzacji (lokalne do modułu).
- „Powiązane dokumenty”.

### 8) docs/REFACTORING_PLAN.md
- Lista problemów (code smells, anti-patterns) z priorytetyzacją MoSCoW.
- Roadmapa refaktoryzacji (kamienie milowe, przybliżone estymacje).
- Quick wins – szybkie usprawnienia o dużym wpływie.
- Ryzyka i mitigacje.
- „Powiązane dokumenty”.

### 9) docs/TECHNICAL_DEBT.md
- Inwentarz długu technicznego (opis, ryzyko High/Medium/Low, wpływ, właściciel).
- Proponowane działania porządkujące (mapowane do planu refaktoryzacji).
- „Powiązane dokumenty”.

### 10) docs/FILE_INVENTORY.md
- Automatycznie generowana lista plików źródłowych z krótkim opisem roli.
- Oznaczenia braków/opisów jako [TO INVESTIGATE].
- „Powiązane dokumenty”.

### 11) docs/processes/
- Opisy kluczowych procesów/ścieżek użycia (np. nagrywanie, transkrypcja, eksport, skróty klawiszowe).
- Dla każdego procesu: cel, kroki, błędy/edge cases, punkty integracji.
- Linki do sekwencji i modułów.

### 12) docs/diagrams/
- system-overview.mmd – widok systemu high-level.
- architecture-layers.mmd – warstwy architektury.
- sequence-main-flow.mmd – główny przepływ.
- sequence-error-handling.mmd – obsługa błędów.
- class-<moduł>.mmd – per-modułowe diagramy klas/komponentów.

### 13) docs/context/ (dla Memory Bank – po audycie)
- PROJECT_SUMMARY.md – esencja projektu (<= 1000 linii).
- ARCHITECTURE_RULES.md – zasady architektury (istniejące + proponowane).
- CONVENTIONS.md – konwencje stylu, nazewnictwa, organizacji plików.
- MEMORY_BANK_INDEX.md – spis kontekstu i relacje między plikami.

## Koherencja i linkowanie
- Każdy dokument kończy się sekcją „Powiązane dokumenty” z linkami do:
  - README.md,
  - dokumentów sąsiednich (np. ARCHITECTURE ↔ DATA_FLOW ↔ API_INTERFACES),
  - powiązanych modułów/diagramów.
- README pełni rolę centralnego indeksu i zawiera mapę wszystkich sekcji.

## Walidacja i jakość
- Link-check (skrypt) uruchamiany po generacji lub w CI.
- Wyszukiwanie znaczników [TO INVESTIGATE] – lista do ręcznego przeglądu.
- Konwencje formatowania (nagłówki, listy, bloki Mermaid) – zgodne między dokumentami.

## Minimalne wymagania „Definition of Done” dla pełnej dokumentacji
- Wygenerowane i zweryfikowane: PROJECT_OVERVIEW.md, ARCHITECTURE.md, DATA_FLOW.md, API_INTERFACES.md, MODULES.md + min. 2 moduły w docs/modules/.
- Diagramy: system-overview, architecture-layers, sequence-main-flow, sequence-error-handling, min. 2 class-*.mmd.
- Uzupełnione REFACTORING_PLAN.md i TECHNICAL_DEBT.md.
- FILE_INVENTORY.md pokrywa >90% plików źródłowych.
- Brak martwych linków; sekcje „Powiązane dokumenty” obecne w każdym pliku.

## Następne kroki (po MVP)
- Rozszerzenie automatyzacji do pełnych faz (architektura, moduły, refaktoryzacja).
- Integracja z Memory Bank po akceptacji treści z docs/context/.
- Opcjonalnie: Makefile i smart-bootstrap.sh do powtarzalnego uruchamiania.

