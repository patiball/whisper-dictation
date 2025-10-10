# Moduły Aplikacji whisper-dictation

## 1. Wprowadzenie

Ten dokument stanowi indeks głównych modułów aplikacji whisper-dictation. Każdy moduł ma jasno określoną odpowiedzialność i publiczne API, umożliwiając łatwą nawigację i zrozumienie architektury systemu.

Aplikacja whisper-dictation jest zbudowana modularnie, gdzie każdy komponent odpowiada za konkretny aspekt funkcjonalności: nagrywanie audio, transkrypcję mowy oraz zarządzanie urządzeniami przetwarzającymi (GPU/CPU).

## 2. Tabela Modułów

| Moduł | Odpowiedzialność | Dokumentacja |
|-------|------------------|--------------|
| recorder | Nagrywanie audio z mikrofonu | [recorder.md](./modules/recorder.md) |
| transcriber | Transkrypcja audio przy użyciu Whisper | [transcriber.md](./modules/transcriber.md) |
| device_manager | Zarządzanie GPU/CPU i optymalizacja dla M1/M2 | [device_manager.md](./modules/device_manager.md) |

## 3. Graf Zależności

```
┌─────────────────┐
│  whisper-       │
│  dictation.py   │  (Główna aplikacja)
└────────┬────────┘
         │
         ├─────────────┐
         │             │
    ┌────▼────┐   ┌────▼──────────┐
    │ recorder│   │ transcriber   │
    └────┬────┘   └────┬──────────┘
         │             │
         │        ┌────▼──────────────┐
         │        │ device_manager    │
         │        │ (DeviceManager)   │
         │        └────┬──────────────┘
         │             │
         │        ┌────▼──────────────┐
         │        │ mps_optimizer     │
         │        │ (Enhanced Manager)│
         │        └───────────────────┘
         │
         └──────────► (audio data) ─────────┘
```

### Przepływ danych:

1. **recorder** nagrywa audio z mikrofonu i przekazuje surowe dane audio
2. **transcriber** otrzymuje dane audio i wykorzystuje Whisper do transkrypcji
3. **device_manager** zarządza wyborem urządzenia (MPS/CUDA/CPU) i optymalizacjami
4. **mps_optimizer** dostarcza zaawansowane optymalizacje dla chipów Apple M1/M2

### Kluczowe zależności:

- **transcriber** → **device_manager**: Transkryber używa DeviceManager do wyboru optymalnego urządzenia
- **transcriber** → **mps_optimizer**: Transkryber używa EnhancedDeviceManager dla zaawansowanej obsługi błędów
- **recorder** → **transcriber** (opcjonalnie): Recorder może przyjąć instancję transkrybera do automatycznej transkrypcji

## 4. Powiązane Dokumenty

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Szczegółowy opis architektury systemu
- **[API_INTERFACES.md](./API_INTERFACES.md)** - Dokumentacja publicznych interfejsów API
- **[DATA_FLOW.md](./DATA_FLOW.md)** - Szczegółowy przepływ danych w systemie
- **[DOCUMENTATION_PLAN.md](./DOCUMENTATION_PLAN.md)** - Plan i status dokumentacji projektu

## 5. Wersjonowanie i Kompatybilność

Wszystkie moduły są zaprojektowane z myślą o TDD (Test-Driven Development) i posiadają:
- Jasne publiczne API
- Możliwość testowania jednostkowego
- Kompatybilność z różnymi urządzeniami (CPU, CUDA, MPS)

## 6. Rozpoczęcie Pracy

Aby rozpocząć pracę z modułami:

1. Sprawdź dokumentację konkretnego modułu w katalogu `docs/modules/`
2. Zobacz przykłady użycia w plikach testowych (`tests/`)
3. Przeczytaj ARCHITECTURE.md dla zrozumienia kontekstu systemowego

## 7. Rozwój i Rozszerzanie

Przy dodawaniu nowych modułów:
- Stwórz odpowiednią dokumentację w `docs/modules/`
- Zaktualizuj ten plik (MODULES.md) dodając wpis w tabeli
- Zaktualizuj graf zależności
- Dodaj testy jednostkowe dla nowego modułu
