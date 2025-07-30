# Active Context

**Current Focus:** 🚨 **CRITICAL: M1 Support Fix** - Naprawa wsparcia Metal Performance Shaders (MPS) na Apple Silicon

**Critical Issue Identified:**
- **MPS Backend Failure**: `Could not run 'aten::empty.memory_format' with arguments from the 'SparseMPS' backend`
- **Root Cause**: PyTorch 2.0.1 compatibility issues with OpenAI Whisper on M1/M2
- **Impact**: M1 users forced to use CPU fallback, losing 2-3x performance potential

**Recent Completed Tasks:**
- ✅ **M1 Support Analysis & Specification (2025-01-30):** Comprehensive analysis of MPS backend issues and 5-phase implementation plan
- ✅ **Przywrócenie odtwarzania dźwięków i naprawa skrótów klawiszowych (2025-07-30):** Dźwięki są odtwarzane w osobnym wątku, a skróty klawiszowe działają poprawnie.
- ✅ **Naprawa ucinania początku nagrania (2025-07-30):** Tymczasowo wyłączono odtwarzanie dźwięków, co rozwiązało problem.
- ✅ **Optymalizacja wydajności transkrypcji (2025-07-30):** Usunięto podwójne przetwarzanie audio w `transcriber.py`.
- ✅ **Repository Configuration (2025-01-29):** Skonfigurowano projekt jako fork oryginalnego repozytorium `foges/whisper-dictation`

**Immediate Priorities:**

1. **🚨 M1 Support Fix (CRITICAL)**: Implement 5-phase plan from specs/20250130_m1_support_fix.md
2. **Dependency Upgrade**: PyTorch 2.1+ and latest OpenAI Whisper
3. **DeviceManager**: Centralized device handling with intelligent fallback
4. **Performance Optimization**: Leverage full M1/M2 GPU capabilities
