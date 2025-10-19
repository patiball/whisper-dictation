# ADR-004: Rumps dla menu bar (zamiast native AppKit)

**Status**: Aktywna (działa dobrze dla obecnych potrzeb)  
**Date**: 2025-01-10  
**Deciders**: Team  
**Tags**: ui, macos, framework

## Context

Aplikacja potrzebuje ikony w macOS menu bar. Native AppKit (Objective-C/Swift) dałoby pełną kontrolę. Python to główny język projektu (nie Swift). Trzeba szybko zbudować MVP.

## Problem Statement

Jak zaimplementować interfejs użytkownika w pasku menu macOS, wykorzystując głównie Python, w sposób szybki i efektywny, bez konieczności głębokiego zanurzania się w natywne API macOS?

## Decision

Użycie biblioteki `rumps` (Ridiculously Uncomplicated macOS Python Statusbar apps) dla menu bar.

## Alternatives Considered

### 1. PyObjC + AppKit
**Odrzucone** - zbyt złożone

**Pros:**
- Pełna kontrola nad UI
- Dostęp do wszystkich natywnych funkcji

**Cons:**
- ❌ Wysoka krzywa uczenia (Objective-C/Swift concepts)
- ❌ Więcej boilerplate code
- ❌ Trudniejsze debugowanie

### 2. Swift app + Python backend
**Odrzucone** - wymaga bridge

**Pros:**
- Najlepsze UX (natywne)
- Separacja frontend/backend

**Cons:**
- ❌ Wymaga stworzenia bridge między Swift a Python
- ❌ Dwa języki do maintenance
- ❌ Zwiększona złożoność deploymentu

### 3. Electron app
**Odrzucone** - overkill (200MB+ bundle)

**Pros:**
- Cross-platform
- Znane technologie webowe (HTML/CSS/JS)

**Cons:**
- ❌ Duży rozmiar aplikacji
- ❌ Wysokie zużycie zasobów (RAM/CPU)
- ❌ Nie natywny wygląd i odczucia

### 4. rumps (CHOSEN)
**Wybrane** - prosty i pythonowy

**Pros:**
- ✅ **Szybki rozwój** - menu bar w <100 linii kodu
- ✅ **Pythonowy** - nie trzeba uczyć się Objective-C
- ✅ **Prosty API** - dekoratory `@rumps.clicked`
- ✅ **Lightweight** - małe zużycie pamięci
- ✅ Działa dobrze dla prostych menu bar apps

## Consequences

### Positive

- ✅ Szybkie prototypowanie i rozwój UI
- ✅ Niskie zużycie zasobów
- ✅ Łatwa integracja z istniejącym kodem Python
- ✅ Minimalny wpływ na rozmiar aplikacji

### Negative

- ❌ Ograniczone możliwości UI (vs native)
- ❌ Zależność od unmaintained library (ostatni commit 2019)
- ❌ Brak advanced features (np. custom views, animations)
- ❌ MacOS only (vendor lock-in)
- ❌ Potencjalne problemy z kompatybilnością z przyszłymi wersjami macOS

### Neutral

- Wymaga instalacji `rumps` jako zależności
- Prosty UI jest wystarczający dla obecnych potrzeb

## Implementation Notes

### Key `rumps` features used
- `@rumps.clicked` decorator for menu item actions
- `rumps.App` for main application loop
- `rumps.Timer` for updating status icon
- `rumps.notification` for system notifications

### Example usage
```python
import rumps

class AwesomeStatusBarApp(rumps.App):
    def __init__(self):
        super(AwesomeStatusBarApp, self).__init__("Awesome App", icon="icon.png")
        self.menu = ["Start", "Stop", "Quit"]

    @rumps.clicked("Start")
    def start_app(self, sender):
        rumps.notification("App", "Started", "App has started!")

    @rumps.clicked("Quit")
    def quit_app(self, sender):
        rumps.quit_application()

if __name__ == "__main__":
    AwesomeStatusBarApp().run()
```

## Monitoring & Review

### Success Metrics
- Stability of menu bar UI across macOS versions
- Ease of adding new menu items
- User feedback on UI responsiveness

### Review Schedule
- Re-evaluate if `rumps` becomes problematic (e.g., crashes, compatibility issues)
- Consider migration to `PyObjC` if advanced UI features are required in the future

## Related

- [ADR-005: Threading model (Background recording + UI thread)](./ADR-005-threading-model.md)
- [UI/UX Documentation](../UI_UX.md) *(planned)*

## Notes

Obecnie: `rumps` wystarcza (prosty UI, ikona, menu). Future: custom view dla visualize waveform during recording? Jeśli `rumps` stanie się problematyczne → migrate do `PyObjC`.

**Update 2025-10-10**: Status remains active. `rumps` continues to meet current requirements.
