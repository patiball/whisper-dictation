# Architecture Decision Records (ADR)

Ten katalog zawiera Architecture Decision Records (ADR) dla projektu Whisper Dictation. ADR-y dokumentują ważne decyzje architektoniczne, ich kontekst, rozważane alternatywy oraz konsekwencje.

## Cel

ADR-y służą jako historyczny zapis kluczowych wyborów projektowych, pomagając nowym członkom zespołu zrozumieć motywacje stojące za obecną architekturą oraz zapewniając spójność w przyszłym rozwoju.

## Istniejące ADR-y

| ID | Tytuł | Status | Data | Opis |
|----|-------|--------|------|------|
| [ADR-001](./ADR-001-dual-implementations.md) | Dwie równoległe implementacje (Python vs C++) | Aktywna | 2025-01-10 | Decyzja o utrzymaniu dwóch wersji aplikacji. |
| [ADR-002](./ADR-002-offline-processing.md) | Całkowicie offline processing | Aktywna | 2025-01-10 | Decyzja o przetwarzaniu danych wyłącznie lokalnie. |
| [ADR-003](./ADR-003-device-manager.md) | Dedykowany DeviceManager dla M1/M2 | Aktywna | 2025-01-10 | Decyzja o stworzeniu centralnego menedżera urządzeń. |

## Szablon ADR

Każdy ADR powinien być zgodny z następującym szablonem:

```markdown
# ADR-XXX: [Tytuł Decyzji]

**Status**: Proposed | Accepted | Deprecated | Superseded
**Date**: YYYY-MM-DD
**Deciders**: [Lista osób/zespołów, które podjęły decyzję]
**Tags**: [Słowa kluczowe, np. architecture, performance, security]

## Context

[Opis problemu lub sytuacji, która doprowadziła do podjęcia decyzji. Dlaczego ta decyzja jest ważna?]

## Problem Statement

[Jasne sformułowanie problemu, który ADR ma rozwiązać.]

## Decision

[Jasne i zwięzłe stwierdzenie podjętej decyzji.]

## Alternatives Considered

[Lista alternatywnych rozwiązań, które były brane pod uwagę, wraz z ich zaletami i wadami.]

## Consequences

[Pozytywne i negatywne konsekwencje podjętej decyzji. Jak wpływa na system, zespół, przyszły rozwój?]

## Implementation Notes

[Krótkie uwagi dotyczące implementacji decyzji, jeśli są istotne.]

## Monitoring & Review

[Jak będziemy monitorować skuteczność decyzji i kiedy zostanie ona ponownie oceniona.]

## Related

[Linki do innych ADR-ów, dokumentacji, specyfikacji, które są powiązane z tą decyzją.]

## Notes

[Dodatkowe uwagi, które nie pasują do innych sekcji.]
```

## Powiązane Dokumenty

- [ARCHITECTURE.md](../../ARCHITECTURE.md) - Główna dokumentacja architektury
- [TECHNICAL_DEBT.md](../../TECHNICAL_DEBT.md) - Dług techniczny (często wynikający z decyzji architektonicznych)
