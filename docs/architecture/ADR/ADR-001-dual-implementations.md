# ADR-001: Dwie równoległe implementacje (Python vs C++)

**Status**: Aktywna  
**Date**: 2025-01-10  
**Deciders**: Team  
**Tags**: architecture, whisper, implementation

## Context

Model OpenAI Whisper w wersji Python działa tylko na CPU z M1/M2 (problem z PyTorch MPS backend). Wersja C++ (whisper.cpp) oferuje natywną akcelerację GPU M1, ale ma problemy z jakością. Użytkownicy potrzebują wyboru między dokładnością a szybkością.

## Problem Statement

Jak zapewnić użytkownikom możliwość wyboru między:
- Wysoką jakością transkrypcji (Python + Whisper) vs
- Szybką transkrypcją z GPU M1/M2 (C++ whisper.cpp)

przy zachowaniu stabilności i możliwości rozwoju?

## Decision

Utrzymanie dwóch równoległych implementacji:
- **whisper-dictation.py** - wersja Python (dokładna, CPU only)
- **whisper-dictation-fast.py** - wersja C++ (GPU M1, eksperymentalna)

## Alternatives Considered

### 1. Tylko wersja Python
**Odrzucone** - brak GPU acceleration dla M1/M2 users

**Pros:**
- Jeden codebase do maintenance
- Stabilna jakość transkrypcji

**Cons:**
- Wolniejsza transkrypcja na Apple Silicon
- Brak możliwości wykorzystania Neural Engine

### 2. Tylko wersja C++
**Odrzucone** - problemy z jakością transkrypcji

**Pros:**
- Natywna akceleracja GPU M1
- Szybsza transkrypcja

**Cons:**
- Gorsza jakość vs Python Whisper
- Mniej stabilna (whisper.cpp jest community project)

### 3. Hybrydowa (Python + whisper.cpp bindings)
**Odrzucone** - zbyt złożone

**Pros:**
- Jedna aplikacja z wyborem backend

**Cons:**
- Trudne bindings Python ↔ C++
- Zwiększona złożoność buildu
- Potencjalne problemy z kompatybilnością

## Consequences

### Positive

- ✅ Użytkownik wybiera trade-off (jakość vs szybkość)
- ✅ Można rozwijać obie implementacje niezależnie
- ✅ Fallback na Python gdy C++ ma problemy
- ✅ Eksperymentowanie z whisper.cpp bez ryzyka dla main branch
- ✅ Różne use cases (Python = produkcja, C++ = quick notes)

### Negative

- ❌ Duplikacja kodu (StatusBarApp, KeyListeners, itp.)
- ❌ Dwa razy więcej maintenance
- ❌ Dokumentacja musi opisywać obie wersje
- ❌ Potencjalne rozbieżności w funkcjonalnościach
- ❌ Większy package size (oba executables)

### Neutral

- Użytkownicy muszą świadomie wybrać którą wersję uruchomić
- Zwiększone wymagania dyskowe (dwa zestawy zależności)

## Implementation Notes

### Python version (whisper-dictation.py)
- Rekomendowana dla produkcji
- Pełna funkcjonalność
- CPU only (z próbami MPS)

### C++ version (whisper-dictation-fast.py)
- Tylko do testów i eksperymentów
- Może mieć niepełną funkcjonalność
- GPU M1/M2 acceleration

### Shared components
- StatusBarApp interface
- KeyListener logic
- Audio recording (PyAudio)

## Monitoring & Review

### Success Metrics
- User satisfaction z jakości transkrypcji
- Performance benchmarks (CPU vs GPU)
- Bug reports frequency (Python vs C++)

### Review Schedule
- Quarterly review of maintenance burden
- Re-evaluate when PyTorch MPS becomes stable
- Monitor whisper.cpp quality improvements

## Related

- [ADR-003: DeviceManager dla M1/M2](./ADR-003-device-manager.md)
- [Performance Documentation](../PERFORMANCE.md) *(planned)*

## Notes

W przyszłości: możliwe połączenie gdy PyTorch MPS będzie stabilne. Do tego czasu utrzymujemy obie implementacje jako separate entry points.

**Update 2025-10-10**: Status remains active. Python version is primary, C++ version is experimental.
