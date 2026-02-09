# ADR-002: Całkowicie offline processing

**Status**: Aktywna (niezmienne wymaganie)  
**Date**: 2025-01-10  
**Deciders**: Team  
**Tags**: privacy, security, architecture

## Context

Rozpoznawanie mowy wymaga przetwarzania audio użytkownika. Wysyłanie audio do cloud (np. Google Speech API) byłoby szybsze i prostsze. Jednak użytkownicy mogą dyktować poufne informacje (hasła, dane osobowe, medyczne). Istnieje brak zaufania do cloud providers w kontekście prywatności.

## Problem Statement

Jak zapewnić użytkownikom pełną prywatność i kontrolę nad ich danymi głosowymi, przy jednoczesnym zachowaniu funkcjonalności rozpoznawania mowy?

## Decision

**Wszystkie operacje (nagrywanie, transkrypcja, przetwarzanie) wykonywane lokalnie bez wysyłania danych.**

- Nagrywanie audio tylko lokalnie
- Model Whisper działa on-device
- Żadne dane audio nie opuszczają urządzenia
- Brak połączeń sieciowych podczas transkrypcji

## Alternatives Considered

### 1. Cloud API (Google/Azure Speech)
**Odrzucone** - privacy concerns

**Pros:**
- Szybsza transkrypcja (cloud infrastructure)
- Brak wymagań sprzętowych lokalnie
- Lepsza jakość dla niektórych języków
- Automatyczne updates modeli

**Cons:**
- ❌ **Brak prywatności** - audio wysyłane do cloud
- ❌ Wymaga internetu
- ❌ Koszty API ($0.006/15s dla Google Speech)
- ❌ Rate limiting
- ❌ Vendor lock-in
- ❌ GDPR compliance challenges

### 2. Hybrydowe (lokalne dla krótkich, cloud dla długich)
**Odrzucone** - niespójne privacy guarantees

**Pros:**
- Optymalizacja kosztu/performance
- Fallback gdy lokalne nie działa

**Cons:**
- ❌ Niespójne privacy model
- ❌ Użytkownik nie wie kiedy data goes to cloud
- ❌ Zwiększona złożoność
- ❌ Nadal wymaga internetu dla długich nagrań

### 3. Opcjonalny cloud (user choice)
**Odrzucone** - zwiększa attack surface

**Pros:**
- Użytkownik decyduje
- Flexibility

**Cons:**
- ❌ Zwiększony attack surface
- ❌ Więcej kodu do maintenance (2 paths)
- ❌ Ryzyko przypadkowego wysłania danych
- ❌ Wymaga API key management

## Consequences

### Positive

- ✅ **100% prywatności** - dane nigdy nie opuszczają urządzenia
- ✅ Działa bez internetu (np. w samolocie, w podróży)
- ✅ Brak kosztów API (zero recurring costs)
- ✅ Brak limitów rate-limiting
- ✅ Zgodność z GDPR bez effort
- ✅ Brak vendor lock-in
- ✅ Użytkownik ma pełną kontrolę nad danymi
- ✅ Marketing advantage: "Your voice never leaves your device"
- ✅ Trust building z privacy-conscious users

### Negative

- ❌ Wymaga mocnego CPU/GPU lokalnie
- ❌ Pobieranie modeli (75MB - 3GB) przy pierwszym użyciu
- ❌ Brak cloud features (np. speaker diarization, advanced NLP)
- ❌ Wolniejsze na starszych maszynach vs cloud API
- ❌ Brak automatic model updates (user must update app)
- ❌ Większe wymagania dyskowe (local model storage)

### Neutral

- Użytkownik musi mieć wystarczająco mocny komputer
- One-time model download required
- Updates require app update (not automatic)

## Implementation Notes

### Local Processing Stack
```
Audio Input → PyAudio → Local Buffer → Whisper (local) → Text Output
                ↓
         Never leaves device
```

### Model Storage
- Models cached in `~/.cache/whisper/`
- Downloaded once, reused forever
- User controls cache location

### No Network Requirements
- App działa offline
- Tylko model download wymaga internetu (first time)
- No telemetry, no analytics, no cloud sync

### Privacy Guarantees
- ✅ Audio never stored to disk (in-memory only)
- ✅ No network requests during transcription
- ✅ No telemetry or usage tracking
- ✅ No cloud dependencies

## Security Considerations

- **Data at rest**: Audio never persisted (memory only)
- **Data in transit**: No network transmission
- **Third-party access**: Impossible (no cloud)
- **Compliance**: GDPR, HIPAA-friendly (no PHI transmission)

## Monitoring & Review

### Success Metrics
- User trust and satisfaction
- Privacy-focused user adoption
- Zero data breach incidents (by design)

### Review Schedule
- This decision is **immutable** - core value proposition
- Any change would be breach of user trust
- Only review: performance optimizations of local processing

## Related

- [ADR-003: DeviceManager dla M1/M2](./ADR-003-device-manager.md) - optimizes local processing
- [Security Documentation](../SECURITY.md) *(planned)*

## Notes

**Core value proposition aplikacji**: "Your voice never leaves your device"

To nie jest feature - to jest fundamentalna gwarancja prywatności. Zmiana tej decyzji byłaby breach of trust z użytkownikami.

Marketing messaging:
- "100% offline, 100% private"
- "What you say stays on your device"
- "No cloud, no tracking, no data sharing"

**Update 2025-10-10**: Status remains active and immutable. This is non-negotiable design principle.