# Epic: Naprawa wsparcia M1 - Metal Performance Shaders (MPS) Backend
**Status**: Ready  
**Priority**: Critical  
**Complexity**: High  
**Created**: 2025-01-30  
**Target**: Production Ready M1 Support  

## Overview
Aplikacja whisper-dictation ma problemy z wykorzystaniem Metal Performance Shaders (MPS) na procesorach Apple M1/M2. Błąd `Could not run 'aten::empty.memory_format' with arguments from the 'SparseMPS' backend` wskazuje na problemy kompatybilności między PyTorch 2.0.1, OpenAI Whisper i MPS backend. Celem tego epiku jest zapewnienie stabilnego, wydajnego wsparcia dla chipów Apple Silicon.

## Problem Analysis

### Current Error Pattern
```bash
Próbuję użyć Metal Performance Shaders (GPU) na M1: mps
Loading model...
Błąd z MPS: Could not run 'aten::empty.memory_format' with arguments from the 'SparseMPS' backend. This could be...
Przełączam na CPU jako fallback
base model loaded on cpu
Używam Metal Performance Shaders (GPU) na M1: mps  # ❌ Inconsistent state!
```

### Root Causes Identified
1. **PyTorch Version Issue**: PyTorch 2.0.1 ma znane problemy z MPS dla niektórych operacji Whisper
2. **Inconsistent Device Management**: Różne moduły (`whisper-dictation.py` vs `transcriber.py`) mają różną logikę device selection
3. **Incomplete Fallback**: Model loading failuje na MPS → CPU, ale transcription nadal próbuje MPS
4. **Missing Error Context**: Brak szczegółowych informacji o błędach MPS dla debugowania

### Current Architecture Issues
```python
# whisper-dictation.py - Device detection #1
if torch.backends.mps.is_available() and torch.backends.mps.is_built():
    device = "mps"

# transcriber.py - Device detection #2 (duplicate logic)
if torch.backends.mps.is_available() and torch.backends.mps.is_built():
    self.device = "mps"

# SpeechTranscriber class - Device detection #3 (another duplicate)
if torch.backends.mps.is_available() and torch.backends.mps.is_built():
    self.device = "mps"
```

## Acceptance Criteria

### Phase 1: Dependency Upgrade (Critical)
- [ ] PyTorch upgraded to 2.1+ with improved MPS support
- [ ] OpenAI Whisper upgraded to latest stable version
- [ ] Compatibility matrix tested and documented
- [ ] No breaking changes to existing API

### Phase 2: Unified Device Management (Critical)
- [ ] Single `DeviceManager` class handling all device logic
- [ ] Consistent device state across all modules
- [ ] Smart fallback mechanism with state persistence
- [ ] Device capability detection and validation

### Phase 3: Robust Error Handling (High)
- [ ] Graceful degradation when MPS operations fail
- [ ] Detailed error logging with actionable information
- [ ] User-friendly error messages in Polish/English
- [ ] Automatic retry logic with exponential backoff

### Phase 4: Performance Optimization (Medium)
- [ ] MPS-specific optimizations (fp16, memory management)
- [ ] Benchmark suite for different device configurations
- [ ] Memory usage optimization for M1 constraints
- [ ] Performance regression prevention

### Phase 5: Testing & Validation (High)
- [ ] M1-specific test suite with real hardware validation
- [ ] Cross-device compatibility tests (Intel Mac, M1, M2)
- [ ] Performance benchmarks with baseline comparisons
- [ ] Integration tests for all supported model sizes

## Detailed Implementation Plan

### 1. Dependency Upgrade Strategy
```toml
# pyproject.toml - Target versions
torch = "^2.1.0"  # Improved MPS support
torchvision = "^0.16.0"
torchaudio = "^2.1.0"
openai-whisper = "^20231117"  # Latest stable
```

**Migration Steps:**
1. Create compatibility test suite
2. Upgrade in isolated environment
3. Test all model sizes (tiny → large)
4. Validate performance benchmarks
5. Update CI/CD pipeline

### 2. DeviceManager Implementation
```python
# New file: device_manager.py
class DeviceManager:
    """Centralized device management for M1/M2 optimization"""
    
    def __init__(self):
        self.preferred_device = self._detect_optimal_device()
        self.fallback_device = "cpu"
        self.current_device = None
        self.device_capabilities = self._test_device_capabilities()
    
    def _detect_optimal_device(self) -> str:
        """Smart device detection with capability testing"""
        
    def get_device_for_operation(self, operation_type: str) -> str:
        """Get best device for specific operation (loading, transcription, etc.)"""
        
    def handle_device_error(self, error: Exception, operation: str) -> str:
        """Intelligent fallback with error context"""
        
    def validate_device_compatibility(self, model_size: str) -> bool:
        """Test if device can handle specific model size"""
```

### 3. Error Handling & Fallback Logic
```python
# Enhanced error handling pattern
class MPSErrorHandler:
    KNOWN_MPS_ERRORS = [
        "aten::empty.memory_format",
        "SparseMPS backend",
        "MPS backend out of memory"
    ]
    
    def handle_mps_error(self, error: Exception) -> DeviceFallbackStrategy:
        """Categorize MPS errors and provide appropriate fallback"""
        
    def should_retry_with_cpu(self, error: Exception) -> bool:
        """Determine if CPU fallback is appropriate"""
```

### 4. Performance Optimization Features
```python
# MPS-specific optimizations
class MPSOptimizer:
    def optimize_for_m1(self, model, model_size: str):
        """Apply M1-specific optimizations"""
        # fp16 precision for supported operations
        # Memory pool management
        # Batch size optimization
        
    def get_optimal_settings(self, device: str, model_size: str) -> dict:
        """Return optimal transcription settings per device/model"""
```

## File Changes Required

### Core Implementation Files
- **`device_manager.py`** (NEW): Centralized device management
- **`mps_optimizer.py`** (NEW): M1-specific optimizations  
- **`whisper-dictation.py`**: Integration with DeviceManager
- **`transcriber.py`**: Remove duplicate device logic, use DeviceManager
- **`pyproject.toml`**: Dependency upgrades

### Testing Files
- **`tests/test_device_management.py`** (NEW): Device detection and fallback tests
- **`tests/test_m1_compatibility.py`** (NEW): M1-specific validation
- **`tests/test_performance_regression.py`** (NEW): Performance benchmarks

### Documentation Files
- **`docs/M1_SETUP.md`** (NEW): M1-specific setup instructions
- **`docs/TROUBLESHOOTING.md`** (NEW): Common M1 issues and solutions

## Integration Points

### 1. Model Loading Integration
```python
# Before (problematic)
model = load_model(model_name, device=device)

# After (robust)
device_manager = DeviceManager()
device = device_manager.get_device_for_operation("model_loading")
try:
    model = load_model(model_name, device=device)
    device_manager.register_success("model_loading", device)
except Exception as e:
    fallback_device = device_manager.handle_device_error(e, "model_loading")
    model = load_model(model_name, device=fallback_device)
```

### 2. Transcription Integration
```python
# Enhanced transcription with device awareness
def transcribe(self, audio_data, language=None):
    device = self.device_manager.get_device_for_operation("transcription")
    options = self.mps_optimizer.get_optimal_settings(device, self.model_size)
    
    try:
        result = self.model.transcribe(audio_data, **options)
        self.device_manager.register_success("transcription", device)
        return result
    except Exception as e:
        if self.device_manager.should_retry_with_fallback(e):
            fallback_device = self.device_manager.handle_device_error(e, "transcription")
            options = self.mps_optimizer.get_optimal_settings(fallback_device, self.model_size)
            return self.model.transcribe(audio_data, **options)
        raise e
```

## Risk Assessment & Mitigation

### High Risk: Dependency Breaking Changes
**Risk**: PyTorch/Whisper upgrade breaks existing functionality  
**Mitigation**: 
- Comprehensive test suite before upgrade
- Staged rollout with rollback plan
- Version pinning for stable releases

### Medium Risk: Performance Regression
**Risk**: New device management adds overhead  
**Mitigation**:
- Performance benchmarks as acceptance criteria
- Lazy initialization of device manager
- Caching of device capabilities

### Low Risk: M1 Hardware Variations
**Risk**: Different M1/M2 chips behave differently  
**Mitigation**:
- Test matrix across M1/M2/M3 variants
- Adaptive optimization based on chip detection
- Community feedback integration

## Success Metrics

### Performance Targets
- **Model Loading**: < 5s for base model on M1 (vs current CPU fallback)
- **Transcription Speed**: 2-3x faster than CPU on M1 for real-time audio
- **Memory Usage**: < 2GB RAM for base model on M1
- **Error Rate**: < 1% MPS fallback rate in production

### Quality Targets
- **Transcription Accuracy**: No degradation vs CPU baseline
- **Language Detection**: Maintain current accuracy levels
- **Stability**: Zero crashes due to device switching

### User Experience Targets
- **Transparent Operation**: Users shouldn't notice device switching
- **Clear Feedback**: Informative messages when fallback occurs
- **Consistent Performance**: Predictable behavior across sessions

## Testing Strategy

### Unit Tests
```python
def test_device_manager_m1_detection():
    """Test M1 chip detection and capability assessment"""

def test_mps_error_fallback():
    """Test graceful fallback when MPS operations fail"""

def test_device_state_consistency():
    """Ensure device state remains consistent across modules"""
```

### Integration Tests
```python
def test_full_transcription_pipeline_m1():
    """End-to-end test on M1 hardware"""

def test_model_loading_all_sizes_m1():
    """Test all model sizes (tiny→large) on M1"""

def test_cross_device_compatibility():
    """Test same codebase on Intel Mac and M1"""
```

### Performance Tests
```python
def test_m1_vs_cpu_performance():
    """Benchmark M1 MPS vs CPU performance"""

def test_memory_usage_m1():
    """Monitor memory consumption on M1"""

def test_transcription_speed_realtime():
    """Ensure real-time transcription capability"""
```

## Rollout Plan

### Phase 1: Foundation (Week 1)
1. Dependency upgrade in isolated branch
2. DeviceManager implementation
3. Basic error handling

### Phase 2: Integration (Week 2)  
1. Integrate DeviceManager into existing code
2. Remove duplicate device logic
3. Implement fallback mechanisms

### Phase 3: Optimization (Week 3)
1. M1-specific optimizations
2. Performance tuning
3. Memory management improvements

### Phase 4: Testing & Validation (Week 4)
1. Comprehensive test suite
2. M1 hardware validation
3. Performance benchmarking

### Phase 5: Documentation & Release (Week 5)
1. User documentation
2. Troubleshooting guides
3. Release preparation

## Monitoring & Maintenance

### Telemetry Collection
- Device usage statistics (MPS vs CPU usage rates)
- Error frequency and types
- Performance metrics per device type
- Model loading success rates

### Maintenance Tasks
- Regular PyTorch/Whisper compatibility testing
- Performance regression monitoring
- Community feedback integration
- Hardware compatibility updates for new Apple chips

## Dependencies & Prerequisites

### Hardware Requirements
- Apple M1/M2/M3 Mac for testing
- Minimum 8GB RAM (16GB recommended for large models)
- macOS 12.0+ (for optimal MPS support)

### Software Requirements
- Python 3.10+ (as per current pyproject.toml)
- Poetry for dependency management
- Access to PyTorch 2.1+ with MPS support
- OpenAI Whisper latest stable release

### Development Environment
- M1 Mac for primary development
- Intel Mac for cross-compatibility testing
- CI/CD pipeline with M1 runners (if available)

---

**Expected Outcome**: 🎯 **PRODUCTION READY M1 SUPPORT** - Stable, fast, and reliable MPS backend with intelligent CPU fallback, delivering 2-3x performance improvement on Apple Silicon while maintaining 100% compatibility and reliability.