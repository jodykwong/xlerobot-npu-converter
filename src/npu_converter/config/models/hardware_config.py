"""
Hardware Configuration Model

Extended hardware configuration model for NPU converter.
Extends Story 1.3 core framework with NPU-specific capabilities.

Implements the data layer of the configuration architecture as defined
in the architecture document.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from pathlib import Path

from npu_converter.core.models.config_model import HardwareConfig as CoreHardwareConfig


@dataclass
class NPUConfig:
    """NPU-specific configuration parameters."""
    target_device: str = "horizon_x5"
    device_type: str = "npu"
    compute_units: int = 10
    memory_bandwidth: str = "25.6GB/s"
    power_consumption: str = "15W"
    thermal_design_power: str = "10W"
    operating_temperature_range: str = "-40°C to 85°C"
    interface: str = "PCIe 4.0 x4"


@dataclass
class OptimizationConfig:
    """Optimization configuration for NPU deployment."""
    optimization_level: str = "O2"  # O0, O1, O2, O3
    enable_quantization: bool = True
    quantization_precision: str = "int8"  # int8, int16, float16
    enable_fusion: bool = True
    enable_pruning: bool = False
    enable_weight_sharing: bool = False
    enable_dynamic_shapes: bool = False


@dataclass
class MemoryConfig:
    """Memory configuration for NPU operations."""
    total_memory: str = "8GB"
    cache_size: str = "256MB"
    buffer_size: str = "64MB"
    workspace_size: str = "128MB"
    max_model_size: str = "2GB"
    enable_memory_optimization: bool = True


@dataclass
class HardwareConfigModel(CoreHardwareConfig):
    """
    Extended hardware configuration model for NPU converter.

    Extends Story 1.3 HardwareConfig with NPU-specific functionality
    as defined in the architecture document.
    """

    npu_config: NPUConfig = field(default_factory=NPUConfig)
    optimization_config: OptimizationConfig = field(default_factory=OptimizationConfig)
    memory_config: MemoryConfig = field(default_factory=MemoryConfig)
    supported_devices: List[str] = field(default_factory=lambda: ["horizon_x5"])
    device_specific: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize hardware config after dataclass creation."""
        super().__post_init__()
        self._setup_device_specific_configs()

    def _setup_device_specific_configs(self) -> None:
        """Setup device-specific configuration defaults."""
        self.device_specific.update({
            "horizon_x5": {
                "architecture": "ARMv8",
                "cores": 8,
                "frequency": "2.0GHz",
                "cache": "L1: 64KB, L2: 1MB",
                "accelerators": {
                    "npu": {
                        "count": 1,
                        "tops": 10,
                        "precision": "int8",
                        "memory": "8GB HBM2e"
                    }
                },
                "toolchain_version": "5.0.0",
                "supported_ops": [
                    "conv2d", "conv1d", "depthwise_conv2d",
                    "batch_norm", "relu", "relu6",
                    "max_pool2d", "avg_pool2d",
                    "reshape", "flatten", "concat",
                    "add", "subtract", "multiply"
                ]
            }
        })

    def get_npu_capability_summary(self) -> Dict[str, Any]:
        """Get NPU capability summary."""
        device = self.npu_config.target_device
        device_config = self.device_specific.get(device, {})

        return {
            "device": device,
            "architecture": device_config.get("architecture"),
            "cores": device_config.get("cores"),
            "frequency": device_config.get("frequency"),
            "tops": device_config.get("accelerators", {}).get("npu", {}).get("tops"),
            "precision": device_config.get("accelerators", {}).get("npu", {}).get("precision"),
            "memory": device_config.get("accelerators", {}).get("npu", {}).get("memory"),
            "supported_ops": device_config.get("supported_ops", [])
        }

    def validate_hardware_config(self) -> List[str]:
        """
        Validate hardware configuration.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Validate NPU config
        if self.npu_config.target_device not in self.supported_devices:
            errors.append(f"Unsupported NPU device: {self.npu_config.target_device}")

        if self.npu_config.compute_units < 1:
            errors.append("Compute units must be positive")

        # Validate optimization config
        if self.optimization_config.optimization_level not in ["O0", "O1", "O2", "O3"]:
            errors.append(f"Invalid optimization level: {self.optimization_config.optimization_level}")

        if self.optimization_config.quantization_precision not in ["int8", "int16", "float16"]:
            errors.append(f"Invalid quantization precision: {self.optimization_config.quantization_precision}")

        # Validate memory config
        if not self._validate_memory_format(self.memory_config.total_memory):
            errors.append(f"Invalid memory format: {self.memory_config.total_memory}")

        if not self._validate_memory_format(self.memory_config.cache_size):
            errors.append(f"Invalid cache format: {self.memory_config.cache_size}")

        return errors

    def _validate_memory_format(self, memory_str: str) -> bool:
        """Validate memory format string."""
        import re
        pattern = r'^\d+[KMGT]?B$'
        return bool(re.match(pattern, memory_str))

    def get_optimization_flags(self) -> List[str]:
        """Get compilation optimization flags."""
        flags = [f"-O{self.optimization_config.optimization_level}"]

        if self.optimization_config.enable_fusion:
            flags.append("-fuse-operators")

        if self.optimization_config.enable_pruning:
            flags.append("-enable-pruning")

        return flags

    def get_memory_requirements(self) -> Dict[str, str]:
        """Get memory requirements for operations."""
        return {
            "total": self.memory_config.total_memory,
            "cache": self.memory_config.cache_size,
            "buffer": self.memory_config.buffer_size,
            "workspace": self.memory_config.workspace_size,
            "max_model": self.memory_config.max_model_size
        }

    def get_device_constraints(self) -> Dict[str, Any]:
        """Get device-specific constraints."""
        device = self.npu_config.target_device
        device_config = self.device_specific.get(device, {})

        return {
            "max_model_size": self.memory_config.max_model_size,
            "supported_precision": self.optimization_config.quantization_precision,
            "memory_bandwidth": self.npu_config.memory_bandwidth,
            "power_consumption": self.npu_config.power_consumption,
            "thermal_limit": self.npu_config.thermal_design_power,
            "operating_temperature": self.npu_config.operating_temperature_range,
            "interface": self.npu_config.interface,
            "supported_operations": device_config.get("supported_ops", [])
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        result = super().to_dict()

        # Add hardware-specific fields
        result.update({
            "npu": {
                "target_device": self.npu_config.target_device,
                "device_type": self.npu_config.device_type,
                "compute_units": self.npu_config.compute_units,
                "memory_bandwidth": self.npu_config.memory_bandwidth,
                "power_consumption": self.npu_config.power_consumption,
                "thermal_design_power": self.npu_config.thermal_design_power,
                "operating_temperature_range": self.npu_config.operating_temperature_range,
                "interface": self.npu_config.interface
            },
            "optimization": {
                "optimization_level": self.optimization_config.optimization_level,
                "enable_quantization": self.optimization_config.enable_quantization,
                "quantization_precision": self.optimization_config.quantization_precision,
                "enable_fusion": self.optimization_config.enable_fusion,
                "enable_pruning": self.optimization_config.enable_pruning,
                "enable_weight_sharing": self.optimization_config.enable_weight_sharing,
                "enable_dynamic_shapes": self.optimization_config.enable_dynamic_shapes
            },
            "memory": {
                "total_memory": self.memory_config.total_memory,
                "cache_size": self.memory_config.cache_size,
                "buffer_size": self.memory_config.buffer_size,
                "workspace_size": self.memory_config.workspace_size,
                "max_model_size": self.memory_config.max_model_size,
                "enable_memory_optimization": self.memory_config.enable_memory_optimization
            },
            "supported_devices": self.supported_devices,
            "device_specific": self.device_specific
        })

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HardwareConfigModel":
        """Create configuration from dictionary."""
        config = super().from_dict(data)

        # Extract NPU config
        if "npu" in data:
            npu_config = data["npu"]
            config.npu_config = NPUConfig(
                target_device=npu_config.get("target_device", "horizon_x5"),
                device_type=npu_config.get("device_type", "npu"),
                compute_units=npu_config.get("compute_units", 10),
                memory_bandwidth=npu_config.get("memory_bandwidth", "25.6GB/s"),
                power_consumption=npu_config.get("power_consumption", "15W"),
                thermal_design_power=npu_config.get("thermal_design_power", "10W"),
                operating_temperature_range=npu_config.get("operating_temperature_range", "-40°C to 85°C"),
                interface=npu_config.get("interface", "PCIe 4.0 x4")
            )

        # Extract optimization config
        if "optimization" in data:
            opt_config = data["optimization"]
            config.optimization_config = OptimizationConfig(
                optimization_level=opt_config.get("optimization_level", "O2"),
                enable_quantization=opt_config.get("enable_quantization", True),
                quantization_precision=opt_config.get("quantization_precision", "int8"),
                enable_fusion=opt_config.get("enable_fusion", True),
                enable_pruning=opt_config.get("enable_pruning", False),
                enable_weight_sharing=opt_config.get("enable_weight_sharing", False),
                enable_dynamic_shapes=opt_config.get("enable_dynamic_shapes", False)
            )

        # Extract memory config
        if "memory" in data:
            mem_config = data["memory"]
            config.memory_config = MemoryConfig(
                total_memory=mem_config.get("total_memory", "8GB"),
                cache_size=mem_config.get("cache_size", "256MB"),
                buffer_size=mem_config.get("buffer_size", "64MB"),
                workspace_size=mem_config.get("workspace_size", "128MB"),
                max_model_size=mem_config.get("max_model_size", "2GB"),
                enable_memory_optimization=mem_config.get("enable_memory_optimization", True)
            )

        # Extract device-specific configs
        config.device_specific = data.get("device_specific", {})
        config.supported_devices = data.get("supported_devices", ["horizon_x5"])

        return config