"""
DeviceManager - Centralized device management for M1/M2 optimization
Part of M1 Support Fix - Phase 2 implementation
"""

import torch
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum
import time

class DeviceType(Enum):
    """Supported device types"""
    CPU = "cpu"
    MPS = "mps"
    CUDA = "cuda"

class OperationType(Enum):
    """Different operation types that may have different device requirements"""
    MODEL_LOADING = "model_loading"
    TRANSCRIPTION = "transcription"
    BASIC_TENSOR = "basic_tensor"

class DeviceCapability:
    """Device capability assessment result"""
    def __init__(self, device: str, available: bool, tested: bool = False, 
                 error: Optional[str] = None, performance_score: float = 0.0):
        self.device = device
        self.available = available
        self.tested = tested
        self.error = error
        self.performance_score = performance_score
        self.last_test_time = time.time()

class DeviceManager:
    """
    Centralized device management for M1/M2 optimization with intelligent fallback.
    
    This class handles:
    - Smart device detection with capability testing
    - Operation-specific device selection
    - Graceful fallback when operations fail
    - Performance tracking and optimization
    """
    
    def __init__(self, enable_logging: bool = True):
        self.logger = self._setup_logging(enable_logging)
        
        # Device capabilities cache
        self.capabilities: Dict[str, DeviceCapability] = {}
        
        # Operation success tracking
        self.operation_history: Dict[Tuple[str, str], List[bool]] = {}  # (device, operation) -> [success_history]
        
        # Current device preferences
        self.preferred_devices = self._detect_device_preference_order()
        
        # Fallback device (always CPU as most reliable)
        self.fallback_device = DeviceType.CPU.value
        
        # Test device capabilities on initialization
        self._initialize_device_capabilities()
        
        self.logger.info(f"DeviceManager initialized. Preferred order: {self.preferred_devices}")
    
    def _setup_logging(self, enable: bool) -> logging.Logger:
        """Setup logging for device management"""
        logger = logging.getLogger("DeviceManager")
        if enable and not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _detect_device_preference_order(self) -> List[str]:
        """Detect optimal device preference order based on hardware"""
        devices = []
        
        # Check MPS (Apple Silicon)
        if torch.backends.mps.is_available() and torch.backends.mps.is_built():
            devices.append(DeviceType.MPS.value)
            self.logger.info("MPS (Apple Silicon GPU) detected")
        
        # Check CUDA (NVIDIA)
        if torch.cuda.is_available():
            devices.append(DeviceType.CUDA.value)
            self.logger.info("CUDA (NVIDIA GPU) detected")
        
        # CPU is always available as fallback
        devices.append(DeviceType.CPU.value)
        
        return devices
    
    def _initialize_device_capabilities(self):
        """Test and cache device capabilities for different operations"""
        for device in self.preferred_devices:
            self.logger.info(f"Testing capabilities for device: {device}")
            
            # Test basic tensor operations
            basic_capability = self._test_basic_operations(device)
            self.capabilities[f"{device}_basic"] = basic_capability
            
            # Test model loading capability (lightweight test)
            model_capability = self._test_model_loading_capability(device)
            self.capabilities[f"{device}_model"] = model_capability
            
            self.logger.info(f"Device {device} - Basic: {'✅' if basic_capability.available else '❌'}, "
                           f"Model: {'✅' if model_capability.available else '❌'}")
    
    def _test_basic_operations(self, device: str) -> DeviceCapability:
        """Test basic tensor operations on device"""
        try:
            # Simple tensor operations test
            x = torch.randn(10, 10, device=device)
            y = torch.randn(10, 10, device=device)
            z = x + y
            _ = z.sum()
            
            return DeviceCapability(device, True, True, performance_score=1.0)
        except Exception as e:
            error_msg = str(e)[:100] + "..." if len(str(e)) > 100 else str(e)
            self.logger.warning(f"Basic operations failed on {device}: {error_msg}")
            return DeviceCapability(device, False, True, error=error_msg)
    
    def _test_model_loading_capability(self, device: str) -> DeviceCapability:
        """Test model loading capability (without actually loading Whisper)"""
        try:
            # Test with a simple model-like operation that might trigger similar issues
            # This is a lightweight test to avoid downloading models
            x = torch.randn(1, 80, 3000, device=device)  # Whisper-like tensor shape
            
            # Test operations that Whisper commonly uses
            y = torch.nn.functional.conv1d(x, torch.randn(512, 80, 3, device=device))
            z = torch.nn.functional.linear(y.transpose(1, 2), torch.randn(512, 256, device=device))
            _ = z.sum()
            
            return DeviceCapability(device, True, True, performance_score=1.0)
        except Exception as e:
            error_msg = str(e)[:100] + "..." if len(str(e)) > 100 else str(e)
            self.logger.warning(f"Model-like operations failed on {device}: {error_msg}")
            return DeviceCapability(device, False, True, error=error_msg)
    
    def get_device_for_operation(self, operation: OperationType, model_size: Optional[str] = None) -> str:
        """
        Get the best device for a specific operation type.
        
        Args:
            operation: Type of operation (MODEL_LOADING, TRANSCRIPTION, etc.)
            model_size: Optional model size for memory considerations
            
        Returns:
            Device string (e.g., "mps", "cpu")
        """
        operation_key = operation.value
        
        # Check operation history for each device
        for device in self.preferred_devices:
            capability_key = f"{device}_{operation_key}" if operation != OperationType.BASIC_TENSOR else f"{device}_basic"
            
            # Check if device has required capability
            if capability_key in self.capabilities and self.capabilities[capability_key].available:
                # Check recent success rate
                history_key = (device, operation_key)
                if history_key in self.operation_history:
                    recent_successes = self.operation_history[history_key][-5:]  # Last 5 attempts
                    success_rate = sum(recent_successes) / len(recent_successes)
                    
                    # If success rate is good (>80%), use this device
                    if success_rate > 0.8:
                        self.logger.debug(f"Selected {device} for {operation_key} (success rate: {success_rate:.2f})")
                        return device
                else:
                    # No history yet, try this device
                    self.logger.debug(f"Selected {device} for {operation_key} (no history, trying)")
                    return device
        
        # Fallback to CPU
        self.logger.info(f"Falling back to {self.fallback_device} for {operation_key}")
        return self.fallback_device
    
    def handle_device_error(self, error: Exception, operation: OperationType, 
                          current_device: str) -> str:
        """
        Handle device error and provide fallback device.
        
        Args:
            error: The exception that occurred
            operation: Operation type that failed
            current_device: Device that failed
            
        Returns:
            Fallback device string
        """
        error_str = str(error)
        operation_key = operation.value
        
        # Log the error
        self.logger.warning(f"Device error on {current_device} for {operation_key}: {error_str[:100]}...")
        
        # Record failure in history
        history_key = (current_device, operation_key)
        if history_key not in self.operation_history:
            self.operation_history[history_key] = []
        self.operation_history[history_key].append(False)
        
        # Update capability if this is a known MPS issue
        if "SparseMPS" in error_str or "aten::empty.memory_format" in error_str:
            capability_key = f"{current_device}_{operation_key}"
            if capability_key in self.capabilities:
                self.capabilities[capability_key].available = False
                self.capabilities[capability_key].error = error_str[:100]
            
            self.logger.error(f"Known MPS compatibility issue detected. Disabling {current_device} for {operation_key}")
        
        # Find next best device
        remaining_devices = [d for d in self.preferred_devices if d != current_device]
        for device in remaining_devices:
            capability_key = f"{device}_{operation_key}" if operation != OperationType.BASIC_TENSOR else f"{device}_basic"
            if capability_key in self.capabilities and self.capabilities[capability_key].available:
                self.logger.info(f"Falling back from {current_device} to {device} for {operation_key}")
                return device
        
        # Ultimate fallback
        self.logger.info(f"Ultimate fallback to {self.fallback_device} for {operation_key}")
        return self.fallback_device
    
    def register_operation_success(self, device: str, operation: OperationType):
        """Register successful operation for future device selection"""
        history_key = (device, operation.value)
        if history_key not in self.operation_history:
            self.operation_history[history_key] = []
        self.operation_history[history_key].append(True)
        
        # Keep only last 10 results
        if len(self.operation_history[history_key]) > 10:
            self.operation_history[history_key] = self.operation_history[history_key][-10:]
    
    def get_device_status_report(self) -> Dict:
        """Get comprehensive device status report for debugging"""
        report = {
            "preferred_devices": self.preferred_devices,
            "fallback_device": self.fallback_device,
            "capabilities": {},
            "operation_history": dict(self.operation_history)
        }
        
        for key, capability in self.capabilities.items():
            report["capabilities"][key] = {
                "device": capability.device,
                "available": capability.available,
                "tested": capability.tested,
                "error": capability.error,
                "performance_score": capability.performance_score
            }
        
        return report
    
    def should_retry_with_fallback(self, error: Exception) -> bool:
        """Determine if error warrants automatic fallback retry"""
        error_str = str(error).lower()
        
        # Known MPS issues that should trigger fallback
        mps_error_patterns = [
            "sparsemps",
            "aten::empty.memory_format",
            "mps backend",
            "metal performance shaders"
        ]
        
        return any(pattern in error_str for pattern in mps_error_patterns)