# ADR-003: Dedykowany DeviceManager dla M1/M2

**Status**: Aktywna (critical component)  
**Date**: 2025-01-10  
**Deciders**: Team  
**Tags**: architecture, apple-silicon, mps, performance

## Context

PyTorch MPS backend ma problemy z kompatybilnością (SparseMPS errors). OpenAI Whisper przy próbie użycia GPU M1 rzuca exception. Użytkownicy M1/M2 oczekują akceleracji GPU (wszak mają "Neural Engine"). Manualny fallback w każdym miejscu kodu to anti-pattern.

## Problem Statement

Jak zapewnić stabilne działanie aplikacji na Apple Silicon (M1/M2/M3) przy jednoczesnym wykorzystaniu akceleracji GPU, gdy:
- PyTorch MPS backend jest niestabilny
- Whisper nie zawsze działa z MPS
- Potrzebujemy graceful degradation do CPU

## Decision

Utworzenie centralnego `DeviceManager` + `MPSOptimizer` do zarządzania urządzeniami z:
- Automatycznym testowaniem capabilities przy starcie
- Historią sukcesu/porażki operacji
- Inteligentnym fallback MPS → CPU
- Przyjaznym error handling (komunikaty po polsku)

## Alternatives Considered

### 1. Try-catch w każdym miejscu
**Odrzucone** - boilerplate code

**Pros:**
- Prosty approach
- Lokalna kontrola

**Cons:**
- ❌ Code duplication wszędzie
- ❌ Inconsistent error handling
- ❌ Brak shared learning (każdy try-catch osobno)
- ❌ Trudne do testowania

### 2. Tylko CPU (disable MPS całkowicie)
**Odrzucone** - użytkownicy chcą GPU

**Pros:**
- Zero problemów z MPS
- Stabilność

**Cons:**
- ❌ Wolniejsza transkrypcja
- ❌ Nie wykorzystuje M1/M2 capabilities
- ❌ Bad UX (users paid for Neural Engine)

### 3. PyTorch autograd detect
**Odrzucone** - nie rozwiązuje problemu Whisper

**Pros:**
- Native PyTorch mechanism

**Cons:**
- ❌ Nie przewiduje Whisper-specific issues
- ❌ No learning from failures
- ❌ Brak user-friendly messages

### 4. Centralized DeviceManager (CHOSEN)
**Wybrane** - best balance

**Pros:**
- ✅ Single source of truth
- ✅ Shared learning across operations
- ✅ Graceful degradation
- ✅ User-friendly error messages
- ✅ Testable

## Consequences

### Positive

- ✅ **Stabilność** - graceful degradation bez crashy
- ✅ **Performance** - używa GPU gdy możliwe, CPU gdy konieczne
- ✅ **UX** - przyjazne komunikaty zamiast stack traces
- ✅ **Maintainability** - centralna logika device management
- ✅ **Testability** - można mockować DeviceManager w testach
- ✅ **Intelligence** - uczy się które operacje działają na MPS
- ✅ **Reusability** - pattern reusable w innych PyTorch projects

### Negative

- ❌ Dodatkowa warstwa abstrakcji
- ❌ Więcej kodu do maintenance
- ❌ Testing capabilities przy starcie dodaje ~2s do launch time
- ❌ Zależność między modułami (coupling)
- ❌ Learning curve dla nowych developerów

### Neutral

- Wymaga rozumienia PyTorch device management
- Success rate tracking requires memory

## Implementation

### Architecture

```python
EnhancedDeviceManager
    ├── DeviceManager (core logic)
    │   ├── get_device_for_operation()
    │   ├── handle_device_error()
    │   └── register_operation_success()
    ├── MPSOptimizer (M1/M2 optimizations)
    │   ├── get_optimal_whisper_settings()
    │   └── optimize_model_for_m1()
    └── MPSErrorHandler (error categorization)
        ├── categorize_error()
        └── get_user_friendly_message()
```

### Usage Pattern

**Before ADR-003 (bad code):**
```python
try:
    model = load_model("base", device="mps")
except:
    model = load_model("base", device="cpu")  # Duplikacja wszędzie
```

**After ADR-003 (good code):**
```python
device_manager = EnhancedDeviceManager()
device = device_manager.get_device_for_operation(
    OperationType.MODEL_LOADING, 
    "base"
)
model = load_model("base", device=device)
device_manager.optimize_model(model, device)
```

### Operation History Tracking

```python
operation_history: Dict[Tuple[str, str], List[bool]]
# Example: {("mps", "model_loading"): [True, True, False, True, True]}

# Decision logic:
recent_successes = operation_history[history_key][-5:]
success_rate = sum(recent_successes) / len(recent_successes)

if success_rate > 0.8:
    return device  # Safe to use
else:
    return fallback_device  # Too many failures
```

### Device Preference Order

1. **MPS** (if Apple Silicon and capable)
2. **CUDA** (if NVIDIA GPU available)
3. **CPU** (always available as fallback)

### Capabilities Testing

```python
def _test_basic_operations(device: str) -> DeviceCapability:
    """Test prostych operacji tensor (matrix add/multiply)"""
    # Quick sanity check
    
def _test_model_loading_capability(device: str) -> DeviceCapability:
    """Test operacji podobnych do Whisper (conv1d, linear)"""
    # Actual Whisper-like operations
```

## Error Handling

### MPS Error Types

```python
class MPSErrorType(Enum):
    SPARSE_BACKEND = "sparse_backend"       # SparseMPS errors
    MEMORY_FORMAT = "memory_format"         # aten::empty.memory_format
    OUT_OF_MEMORY = "out_of_memory"         # MPS OOM
    UNSUPPORTED_OP = "unsupported_operation"
    UNKNOWN = "unknown"
```

### User-Friendly Messages (Polish)

```python
SPARSE_BACKEND → "Wykryto problem kompatybilności z GPU M1. Przełączam na CPU."
OUT_OF_MEMORY → "Brak pamięci GPU. Używam CPU (będzie wolniej)."
UNSUPPORTED_OP → "Ta operacja nie jest obsługiwana przez GPU M1. Używam CPU."
```

## Optimizations for M1/M2

### Whisper Settings

**MPS (M1/M2):**
```python
{
    "fp16": True,              # Half precision (faster)
    "beam_size": 1,            # Szybsze dekodowanie
    "condition_on_previous_text": False  # Mniej pamięci
}
```

**CPU:**
```python
{
    "fp16": False,             # CPU doesn't benefit from fp16
    "beam_size": 5,            # Better quality for tiny/base
    "condition_on_previous_text": True  # Better context
}
```

### Model Optimization

```python
def optimize_model_for_m1(model, device: str):
    if device == "mps":
        # Enable MPS fallback dla unsupported ops
        os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
        
        # Inference mode
        model.eval()
        
        # Disable gradients
        for param in model.parameters():
            param.requires_grad = False
```

## Monitoring & Review

### Success Metrics
- MPS success rate (should be >80% for stable operations)
- Fallback frequency (lower is better after learning)
- User complaints about performance (should decrease)

### Performance Impact
- Launch time: +2s (capabilities testing)
- Runtime: Negligible (cached decisions)
- Memory: ~10KB (operation history)

### Review Schedule
- Monitor MPS success rates monthly
- Re-evaluate when PyTorch releases major updates
- Review device preference order quarterly

## Related

- [ADR-001: Dual Implementations](./ADR-001-dual-implementations.md)
- [ADR-002: Offline Processing](./ADR-002-offline-processing.md)
- [Implementation Details](../IMPLEMENTATION.md)
- [Performance Tuning](../PERFORMANCE.md) *(planned)*

## Notes

Rozwiązuje ~80% problemów M1 users. W przyszłości: podobny pattern dla CUDA (NVIDIA). Potencjał do reuse w innych projektach PyTorch na M1.

**Known Issues:**
- Launch time increase (2s) - acceptable trade-off
- Learning requires multiple runs - improves over time
- Cannot predict all MPS failures - but handles them gracefully

**Future Improvements:**
- Persistent operation history (survive app restarts)
- Cloud-based capability database (if users opt-in)
- Auto-tuning based on device performance

**Update 2025-10-10**: Status remains active and critical. This component is core to M1/M2 support.
