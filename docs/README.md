# Dokumentacja projektu Whisper Dictation

Kompleksowa dokumentacja techniczna aplikacji do wielojęzycznego dyktowania opartej na OpenAI Whisper.

## 📋 Spis treści

### 🎯 Dokumenty podstawowe
- **[Przegląd projektu](./PROJECT_OVERVIEW.md)** - Cel, stos technologiczny, struktura, funkcjonalności
- **[Plan dokumentacji](./DOCUMENTATION_PLAN.md)** - Strategia i struktura dokumentacji

### 🏗️ Architektura i przepływy
- **[Diagram integracji systemu](./SYSTEM_INTEGRATION.md)** - Kompletny przegląd wszystkich komponentów współpracujących ze sobą
- **[Architektura systemu](./ARCHITECTURE.md)** *(40KB)* - Warstwy, komponenty, wzorce projektowe, decyzje architektoniczne
- **[Przepływy danych](./DATA_FLOW.md)** *(23KB)* - Główne przepływy, scenariusze, obsługa błędów

### 🔌 API i moduły
- **[Interfejsy API](./API_INTERFACES.md)** *(37KB)* - Publiczne API modułów, kontrakty, sygnatury metod
- **[Indeks modułów](./MODULES.md)** - Przegląd wszystkich modułów projektu
  - [recorder.md](./modules/recorder.md) - Moduł nagrywania audio
  - [transcriber.md](./modules/transcriber.md) - Moduł transkrypcji Whisper
  - [device_manager.md](./modules/device_manager.md) - Zarządzanie urządzeniami M1/M2

### 🛠️ Zarządzanie projektem
- **[Dług techniczny](./TECHNICAL_DEBT.md)** *(16KB)* - Inwentarz długu + plan refaktoryzacji
- **[Inwentarz plików](./FILE_INVENTORY.md)** *(13KB)* - Lista wszystkich plików źródłowych

### 📊 Diagramy (Mermaid)
- [system-overview.mmd](./diagrams/system-overview.mmd) - Przegląd systemu (high-level)
- [architecture-layers.mmd](./diagrams/architecture-layers.mmd) - Warstwy architektury
- [sequence-main-flow.mmd](./diagrams/sequence-main-flow.mmd) - Główny przepływ (happy path)
- [sequence-error-handling.mmd](./diagrams/sequence-error-handling.mmd) - Obsługa błędów

## 🚀 Jak czytać dokumentację

### Dla nowych użytkowników
1. **Start**: [Przegląd projektu](./PROJECT_OVERVIEW.md) - Zrozum cel i możliwości aplikacji
2. [Diagram systemowy](./diagrams/system-overview.mmd) - Zobacz komponenty wizualnie
3. Główny [README.md](../README.md) - Instrukcje instalacji i użycia

### Dla deweloperów
1. **Architektura**: [ARCHITECTURE.md](./ARCHITECTURE.md) - Zrozum strukturę systemu
2. **Przepływy**: [DATA_FLOW.md](./DATA_FLOW.md) - Zobacz jak działa aplikacja
3. **API**: [API_INTERFACES.md](./API_INTERFACES.md) - Poznaj interfejsy modułów
4. **Moduły**: [MODULES.md](./MODULES.md) + [modules/](./modules/) - Szczegóły implementacji

### Dla maintainerów
1. **Dług techniczny**: [TECHNICAL_DEBT.md](./TECHNICAL_DEBT.md) - Co wymaga poprawy
2. **Inwentarz**: [FILE_INVENTORY.md](./FILE_INVENTORY.md) - Przegląd plików projektu
3. **Plan**: [DOCUMENTATION_PLAN.md](./DOCUMENTATION_PLAN.md) - Strategia rozwoju

## 📊 Statystyki dokumentacji

- **Dokumentów**: 15 plików (~185 KB)
- **Diagramów**: 4 pliki Mermaid
- **Modułów**: 3 udokumentowane moduły
- **Język**: Polski
- **Status linków**: ✅ Wszystkie zweryfikowane
- **Wygenerowano**: 2025-10-10 (równolegle, 6 agentów Warp CLI)

## 🔗 Struktura powiązań

```
README.md (TEN PLIK)
    ↓
    ├─→ PROJECT_OVERVIEW.md ──→ Główny README.md
    ├─→ ARCHITECTURE.md ──→ DATA_FLOW.md ──→ API_INTERFACES.md
    ├─→ MODULES.md ──→ modules/*.md
    ├─→ TECHNICAL_DEBT.md
    └─→ diagrams/*.mmd
```

## ⚙️ Narzędzia

- **Walidacja linków**: `python3 ../scripts/check-links.py`
- **Generowanie dokumentacji**: Zobacz `../scripts/setup-docs-mvp.sh`
- **Zadania agentów**: Zobacz `.tasks/` dla historii generowania

## 📝 Uwagi

- Dokumentacja bazuje na **rzeczywistym kodzie** projektu
- Elementy niejasne oznaczone jako `[TO INVESTIGATE]`
- Diagramy Mermaid renderują się automatycznie na GitHubie
- Wszystkie ścieżki są względne dla łatwej nawigacji