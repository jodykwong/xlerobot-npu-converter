"""
Configuration Data Models

This module defines data structures for managing configuration throughout the
NPU converter system. These models provide type-safe containers for
hardware configurations, conversion settings, and system-wide parameters.

Key Features:
- Hierarchical configuration management
- Environment-specific configurations
- Validation and type checking
- Configuration merging and inheritance
- JSON/YAML serialization support
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import yaml
from enum import Enum

from ..exceptions.conversion_errors import ValidationError
from ..exceptions.config_errors import ConfigError


class LogLevel(Enum):
    """Supported log levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class HardwareType(Enum):
    """Supported hardware types."""
    CPU = "cpu"
    GPU = "gpu"
    NPU = "npu"
    FPGA = "fpga"
    ASIC = "asic"


@dataclass
class HardwareConfig:
    """
    Configuration for target hardware platform.

    This class contains all hardware-specific parameters needed for
    optimization and compatibility checks.
    """

    # Basic Hardware Information
    hardware_type: HardwareType
    vendor: str
    model: str
    architecture: Optional[str] = None

    # Memory Configuration
    total_memory: Optional[int] = None  # in MB
    available_memory: Optional[int] = None  # in MB
    memory_bandwidth: Optional[float] = None  # in GB/s

    # Compute Configuration
    compute_units: Optional[int] = None
    max_frequency: Optional[float] = None  # in GHz
    tensor_cores: bool = False
    support_int8: bool = False
    support_fp16: bool = False
    support_bf16: bool = False

    # Platform-Specific Settings
    instruction_set: Optional[str] = None  # e.g., "avx2", "neon"
    cache_sizes: Optional[Dict[str, int]] = None  # in KB
    thermal_limits: Optional[Dict[str, float]] = None  # in Celsius

    # Optimization Parameters
    optimal_batch_size: Optional[int] = None
    memory_optimization_level: int = 1  # 0-3
    parallelization_limit: Optional[int] = None

    # Custom Parameters
    custom_parameters: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate hardware configuration."""
        if not self.hardware_type:
            raise ValidationError("Hardware type is required")

        if not self.vendor:
            raise ValidationError("Hardware vendor is required")

        if not self.model:
            raise ValidationError("Hardware model is required")

        if self.memory_optimization_level < 0 or self.memory_optimization_level > 3:
            raise ValidationError("Memory optimization level must be between 0 and 3")

        if self.total_memory is not None and self.total_memory <= 0:
            raise ValidationError("Total memory must be positive")

        if self.available_memory is not None and self.available_memory <= 0:
            raise ValidationError("Available memory must be positive")

        if self.total_memory and self.available_memory:
            if self.available_memory > self.total_memory:
                raise ValidationError("Available memory cannot exceed total memory")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "hardware_type": self.hardware_type.value,
            "vendor": self.vendor,
            "model": self.model,
            "architecture": self.architecture,
            "total_memory": self.total_memory,
            "available_memory": self.available_memory,
            "memory_bandwidth": self.memory_bandwidth,
            "compute_units": self.compute_units,
            "max_frequency": self.max_frequency,
            "tensor_cores": self.tensor_cores,
            "support_int8": self.support_int8,
            "support_fp16": self.support_fp16,
            "support_bf16": self.support_bf16,
            "instruction_set": self.instruction_set,
            "cache_sizes": self.cache_sizes,
            "thermal_limits": self.thermal_limits,
            "optimal_batch_size": self.optimal_batch_size,
            "memory_optimization_level": self.memory_optimization_level,
            "parallelization_limit": self.parallelization_limit,
            "custom_parameters": self.custom_parameters,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HardwareConfig":
        """Create from dictionary representation."""
        if "hardware_type" in data and isinstance(data["hardware_type"], str):
            data["hardware_type"] = HardwareType(data["hardware_type"])

        return cls(**data)

    @classmethod
    def from_yaml(cls, yaml_path: Path) -> "HardwareConfig":
        """Load configuration from YAML file."""
        try:
            with open(yaml_path, 'r') as f:
                data = yaml.safe_load(f)
            return cls.from_dict(data)
        except Exception as e:
            raise ConfigError(f"Failed to load hardware config from {yaml_path}: {str(e)}")


@dataclass
class SystemConfig:
    """
    System-wide configuration settings.

    This class contains global system parameters that affect all
    conversion operations.
    """

    # Logging Configuration
    log_level: LogLevel = LogLevel.INFO
    log_file: Optional[Path] = None
    log_to_console: bool = True
    max_log_size: Optional[int] = None  # in MB
    log_backup_count: int = 5

    # Performance Configuration
    max_concurrent_conversions: int = 1
    timeout_seconds: int = 3600  # 1 hour default
    memory_limit_mb: Optional[int] = None
    cpu_limit: Optional[float] = None  # percentage of CPU

    # File System Configuration
    temp_directory: Optional[Path] = None
    output_directory: Optional[Path] = None
    cleanup_temp_files: bool = True
    max_disk_usage_mb: Optional[int] = None

    # Security Configuration
    validate_inputs: bool = True
    sanitize_outputs: bool = True
    allowed_model_formats: List[str] = field(default_factory=lambda: ["onnx", "pb", "h5"])
    max_model_size_mb: Optional[int] = None

    # Network Configuration
    allow_network_access: bool = False
    proxy_config: Optional[Dict[str, str]] = None
    timeout_network_requests: int = 30

    # Debug Configuration
    debug_mode: bool = False
    save_intermediate_results: bool = False
    profile_performance: bool = False
    generate_debug_reports: bool = False

    # Custom Parameters
    custom_parameters: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate system configuration."""
        if self.max_concurrent_conversions < 1:
            raise ValidationError("Max concurrent conversions must be at least 1")

        if self.timeout_seconds <= 0:
            raise ValidationError("Timeout must be positive")

        if self.cpu_limit is not None and (self.cpu_limit <= 0 or self.cpu_limit > 100):
            raise ValidationError("CPU limit must be between 0 and 100")

        if self.log_backup_count < 1:
            raise ValidationError("Log backup count must be at least 1")

        if self.max_log_size is not None and self.max_log_size <= 0:
            raise ValidationError("Max log size must be positive")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "log_level": self.log_level.value,
            "log_file": str(self.log_file) if self.log_file else None,
            "log_to_console": self.log_to_console,
            "max_log_size": self.max_log_size,
            "log_backup_count": self.log_backup_count,
            "max_concurrent_conversions": self.max_concurrent_conversions,
            "timeout_seconds": self.timeout_seconds,
            "memory_limit_mb": self.memory_limit_mb,
            "cpu_limit": self.cpu_limit,
            "temp_directory": str(self.temp_directory) if self.temp_directory else None,
            "output_directory": str(self.output_directory) if self.output_directory else None,
            "cleanup_temp_files": self.cleanup_temp_files,
            "max_disk_usage_mb": self.max_disk_usage_mb,
            "validate_inputs": self.validate_inputs,
            "sanitize_outputs": self.sanitize_outputs,
            "allowed_model_formats": self.allowed_model_formats,
            "max_model_size_mb": self.max_model_size_mb,
            "allow_network_access": self.allow_network_access,
            "proxy_config": self.proxy_config,
            "timeout_network_requests": self.timeout_network_requests,
            "debug_mode": self.debug_mode,
            "save_intermediate_results": self.save_intermediate_results,
            "profile_performance": self.profile_performance,
            "generate_debug_reports": self.generate_debug_reports,
            "custom_parameters": self.custom_parameters,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SystemConfig":
        """Create from dictionary representation."""
        if "log_level" in data and isinstance(data["log_level"], str):
            data["log_level"] = LogLevel(data["log_level"])

        # Handle path conversions
        for path_field in ["log_file", "temp_directory", "output_directory"]:
            if path_field in data and data[path_field] is not None:
                data[path_field] = Path(data[path_field])

        return cls(**data)


@dataclass
class ConfigModel:
    """
    Complete configuration model for the NPU converter system.

    This class combines all configuration aspects into a single
    comprehensive model that can be loaded from files and used throughout
    the system.
    """

    # Core Configuration
    hardware_config: HardwareConfig
    system_config: SystemConfig

    # Configuration Metadata
    config_version: str = "1.0.0"
    environment: str = "production"  # development, testing, staging, production
    description: Optional[str] = None

    # Conversion Defaults
    default_conversion_type: str = "ptq"
    default_precision: str = "int8"
    default_optimization_level: int = 1

    # Paths and Directories
    base_directory: Optional[Path] = None
    models_directory: Optional[Path] = None
    calibrations_directory: Optional[Path] = None
    reports_directory: Optional[Path] = None

    def validate(self) -> None:
        """Validate the complete configuration."""
        self.hardware_config.validate()
        self.system_config.validate()

        if not self.config_version:
            raise ValidationError("Configuration version is required")

        if self.environment not in ["development", "testing", "staging", "production"]:
            raise ValidationError("Invalid environment specified")

        if self.default_optimization_level < 0 or self.default_optimization_level > 3:
            raise ValidationError("Default optimization level must be between 0 and 3")

    def merge_with(self, other: "ConfigModel") -> "ConfigModel":
        """Merge this configuration with another, with other taking precedence."""
        # Merge hardware configs (other takes precedence)
        merged_hardware = self.hardware_config
        if other.hardware_config:
            hardware_dict = self.hardware_config.to_dict()
            other_hardware_dict = other.hardware_config.to_dict()
            hardware_dict.update(other_hardware_dict)
            merged_hardware = HardwareConfig.from_dict(hardware_dict)

        # Merge system configs (other takes precedence)
        merged_system = self.system_config
        if other.system_config:
            system_dict = self.system_config.to_dict()
            other_system_dict = other.system_config.to_dict()
            system_dict.update(other_system_dict)
            merged_system = SystemConfig.from_dict(system_dict)

        # Create merged config
        return ConfigModel(
            hardware_config=merged_hardware,
            system_config=merged_system,
            config_version=other.config_version or self.config_version,
            environment=other.environment or self.environment,
            description=other.description or self.description,
            default_conversion_type=other.default_conversion_type or self.default_conversion_type,
            default_precision=other.default_precision or self.default_precision,
            default_optimization_level=other.default_optimization_level or self.default_optimization_level,
            base_directory=other.base_directory or self.base_directory,
            models_directory=other.models_directory or self.models_directory,
            calibrations_directory=other.calibrations_directory or self.calibrations_directory,
            reports_directory=other.reports_directory or self.reports_directory,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "hardware_config": self.hardware_config.to_dict(),
            "system_config": self.system_config.to_dict(),
            "config_version": self.config_version,
            "environment": self.environment,
            "description": self.description,
            "default_conversion_type": self.default_conversion_type,
            "default_precision": self.default_precision,
            "default_optimization_level": self.default_optimization_level,
            "base_directory": str(self.base_directory) if self.base_directory else None,
            "models_directory": str(self.models_directory) if self.models_directory else None,
            "calibrations_directory": str(self.calibrations_directory) if self.calibrations_directory else None,
            "reports_directory": str(self.reports_directory) if self.reports_directory else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConfigModel":
        """Create from dictionary representation."""
        if "hardware_config" in data:
            data["hardware_config"] = HardwareConfig.from_dict(data["hardware_config"])

        if "system_config" in data:
            data["system_config"] = SystemConfig.from_dict(data["system_config"])

        # Handle path conversions
        for path_field in ["base_directory", "models_directory", "calibrations_directory", "reports_directory"]:
            if path_field in data and data[path_field] is not None:
                data[path_field] = Path(data[path_field])

        return cls(**data)

    @classmethod
    def from_yaml(cls, yaml_path: Path) -> "ConfigModel":
        """Load complete configuration from YAML file."""
        try:
            with open(yaml_path, 'r') as f:
                data = yaml.safe_load(f)
            return cls.from_dict(data)
        except Exception as e:
            raise ConfigError(f"Failed to load config from {yaml_path}: {str(e)}")

    def save_to_yaml(self, yaml_path: Path) -> None:
        """Save configuration to YAML file."""
        try:
            yaml_path.parent.mkdir(parents=True, exist_ok=True)
            with open(yaml_path, 'w') as f:
                yaml.dump(self.to_dict(), f, default_flow_style=False, indent=2)
        except Exception as e:
            raise ConfigError(f"Failed to save config to {yaml_path}: {str(e)}")