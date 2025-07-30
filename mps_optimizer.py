"""
MPS Optimizer - M1/M2 specific optimizations and error handling
Part of M1 Support Fix - Phase 3 & 4 implementation
"""

import torch
import logging
from typing import Dict, Any, Optional
from enum import Enum

class MPSErrorType(Enum):
    """Categories of MPS errors for targeted handling"""
    SPARSE_BACKEND = "sparse_backend"
    MEMORY_FORMAT = "memory_format" 
    OUT_OF_MEMORY = "out_of_memory"
    UNSUPPORTED_OP = "unsupported_operation"
    UNKNOWN = "unknown"

class MPSErrorHandler:
    """Enhanced error handling for MPS backend issues"""
    
    # Known MPS error patterns and their categories
    ERROR_PATTERNS = {
        MPSErrorType.SPARSE_BACKEND: [
            "sparsemps backend",
            "could not run 'aten::empty.memory_format' with arguments from the 'sparsemps' backend"
        ],
        MPSErrorType.MEMORY_FORMAT: [
            "aten::empty.memory_format",
            "memory_format"
        ],
        MPSErrorType.OUT_OF_MEMORY: [
            "mps backend out of memory",
            "metal out of memory"
        ],
        MPSErrorType.UNSUPPORTED_OP: [
            "operation not supported",
            "not implemented for mps"
        ]
    }
    
    def __init__(self, enable_logging: bool = True):
        self.logger = self._setup_logging(enable_logging)
        self.error_counts = {error_type: 0 for error_type in MPSErrorType}
    
    def _setup_logging(self, enable: bool) -> logging.Logger:
        """Setup logging for MPS error handling"""
        logger = logging.getLogger("MPSErrorHandler")
        if enable and not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def categorize_error(self, error: Exception) -> MPSErrorType:
        """Categorize MPS error for appropriate handling"""
        error_str = str(error).lower()
        
        for error_type, patterns in self.ERROR_PATTERNS.items():
            if any(pattern in error_str for pattern in patterns):
                self.error_counts[error_type] += 1
                self.logger.debug(f"Categorized error as {error_type.value}: {error_str[:50]}...")
                return error_type
        
        self.error_counts[MPSErrorType.UNKNOWN] += 1
        return MPSErrorType.UNKNOWN
    
    def should_retry_with_cpu(self, error: Exception) -> bool:
        """Determine if error should trigger CPU fallback"""
        error_type = self.categorize_error(error)
        
        # These error types should always fallback to CPU
        cpu_fallback_errors = {
            MPSErrorType.SPARSE_BACKEND,
            MPSErrorType.MEMORY_FORMAT,
            MPSErrorType.UNSUPPORTED_OP
        }
        
        return error_type in cpu_fallback_errors
    
    def get_user_friendly_message(self, error: Exception) -> str:
        """Get user-friendly error message in Polish"""
        error_type = self.categorize_error(error)
        
        messages = {
            MPSErrorType.SPARSE_BACKEND: 
                "Wykryto problem kompatybilności z GPU M1. Przełączam na CPU dla stabilności.",
            MPSErrorType.MEMORY_FORMAT:
                "Problem z formatem pamięci GPU M1. Używam CPU jako alternatywy.",
            MPSErrorType.OUT_OF_MEMORY:
                "Brak pamięci GPU. Przełączam na CPU.",
            MPSErrorType.UNSUPPORTED_OP:
                "Operacja nieobsługiwana przez GPU M1. Używam CPU.",
            MPSErrorType.UNKNOWN:
                "Nieznany problem z GPU M1. Przełączam na CPU dla bezpieczeństwa."
        }
        
        return messages.get(error_type, messages[MPSErrorType.UNKNOWN])
    
    def get_error_statistics(self) -> Dict[str, int]:
        """Get error statistics for debugging"""
        return {error_type.value: count for error_type, count in self.error_counts.items()}

class MPSOptimizer:
    """M1/M2 specific optimizations for Whisper performance"""
    
    def __init__(self):
        self.logger = logging.getLogger("MPSOptimizer")
    
    def get_optimal_whisper_settings(self, device: str, model_size: str) -> Dict[str, Any]:
        """Get optimal Whisper transcription settings for M1/M2"""
        
        # Base settings
        settings = {
            "task": "transcribe",
            "no_speech_threshold": 0.6,
            "logprob_threshold": -1.0,
            "compression_ratio_threshold": 2.4,
            "temperature": 0.0  # Deterministic results
        }
        
        if device == "mps":
            # M1/M2 specific optimizations
            settings.update({
                "fp16": True,  # Use half precision for better performance
                "condition_on_previous_text": False,  # Reduce memory usage
                "beam_size": 1,  # Faster decoding
                "best_of": 1,  # Single pass for speed
                "patience": 1.0  # Less aggressive beam search
            })
            
            # Model size specific optimizations
            if model_size in ["medium", "large"]:
                # For larger models on M1, be more conservative
                settings.update({
                    "no_speech_threshold": 0.7,  # Higher threshold
                    "compression_ratio_threshold": 2.0  # More conservative
                })
                
        elif device == "cpu":
            # CPU optimizations
            settings.update({
                "fp16": False,  # CPU doesn't benefit from fp16
                "condition_on_previous_text": True,  # Better accuracy on CPU
                "beam_size": 5 if model_size in ["tiny", "base"] else 1,  # Adaptive beam size
                "best_of": 5 if model_size == "tiny" else 1
            })
        
        self.logger.debug(f"Optimized settings for {device}/{model_size}: {settings}")
        return settings
    
    def optimize_model_for_m1(self, model, device: str) -> None:
        """Apply M1-specific model optimizations"""
        if device != "mps":
            return
        
        try:
            # Enable MPS optimizations if available
            if hasattr(torch.backends.mps, 'enable_fallback'):
                torch.backends.mps.enable_fallback(True)
                self.logger.info("Enabled MPS fallback for unsupported operations")
            
            # Set model to eval mode for inference
            model.eval()
            
            # Disable gradient computation for inference
            for param in model.parameters():
                param.requires_grad_(False)
                
            self.logger.info("Applied M1 optimizations to model")
            
        except Exception as e:
            self.logger.warning(f"Could not apply all M1 optimizations: {e}")
    
    def get_memory_usage_info(self, device: str) -> Dict[str, Any]:
        """Get memory usage information for device"""
        info = {"device": device}
        
        if device == "mps":
            try:
                # MPS memory info (if available in PyTorch version)
                if hasattr(torch.mps, 'current_allocated_memory'):
                    info["allocated_memory"] = torch.mps.current_allocated_memory()
                    info["cached_memory"] = torch.mps.driver_allocated_memory()
                else:
                    info["memory_info"] = "MPS memory tracking not available"
            except Exception as e:
                info["memory_error"] = str(e)
        
        elif device == "cpu":
            import psutil
            info["system_memory"] = {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent
            }
        
        return info

class EnhancedDeviceManager:
    """Enhanced DeviceManager with MPS optimization and error handling"""
    
    def __init__(self, enable_logging: bool = True):
        # Import here to avoid circular imports
        from device_manager import DeviceManager
        
        self.base_manager = DeviceManager(enable_logging)
        self.error_handler = MPSErrorHandler(enable_logging)
        self.optimizer = MPSOptimizer()
        self.logger = logging.getLogger("EnhancedDeviceManager")
    
    def get_device_for_operation(self, operation, model_size: Optional[str] = None) -> str:
        """Enhanced device selection with error history"""
        return self.base_manager.get_device_for_operation(operation, model_size)
    
    def handle_device_error_enhanced(self, error: Exception, operation, current_device: str) -> tuple[str, str]:
        """Enhanced error handling with user-friendly messages"""
        
        # Get user-friendly message
        user_message = self.error_handler.get_user_friendly_message(error)
        
        # Get fallback device using base manager
        fallback_device = self.base_manager.handle_device_error(error, operation, current_device)
        
        # Log enhanced error info
        error_type = self.error_handler.categorize_error(error)
        self.logger.info(f"Enhanced error handling: {error_type.value} -> {fallback_device}")
        
        return fallback_device, user_message
    
    def get_optimized_settings(self, device: str, model_size: str) -> Dict[str, Any]:
        """Get optimized settings for device and model"""
        return self.optimizer.get_optimal_whisper_settings(device, model_size)
    
    def optimize_model(self, model, device: str) -> None:
        """Apply device-specific optimizations to model"""
        self.optimizer.optimize_model_for_m1(model, device)
    
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive status including error statistics"""
        base_status = self.base_manager.get_device_status_report()
        
        base_status["error_statistics"] = self.error_handler.get_error_statistics()
        base_status["memory_info"] = {}
        
        for device in self.base_manager.preferred_devices:
            base_status["memory_info"][device] = self.optimizer.get_memory_usage_info(device)
        
        return base_status