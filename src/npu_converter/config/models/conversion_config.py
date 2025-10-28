"""
Conversion Configuration Model

Extended configuration model for conversion parameters.
Extends Story 1.3 ConfigModel with conversion-specific capabilities.

Implements the data layer of the configuration architecture as defined
in the architecture document.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from pathlib import Path

from ...core.models.config_model import ConfigModel


@dataclass
class QuantizationConfig:
    """Quantization configuration parameters."""
    enabled: bool = True
    precision: str = "int8"
    calibration_method: str = "minmax"
    calibration_dataset_size: int = 100
    symmetric: bool = False
    per_channel: bool = False


@dataclass
class PerformanceConfig:
    """Performance optimization configuration."""
    batch_size: int = 1
    num_workers: int = 4
    memory_limit: str = "8GB"
    compute_units: int = 10
    cache_size: str = "256MB"
    enable_optimization: bool = True
    optimization_level: str = "O2"


@dataclass
class ModelConfig:
    """Model-specific configuration."""
    model_type: str = "sensevoice"  # "sensevoice" or "piper_vits"
    input_format: str = "onnx"
    output_format: str = "bpu"
    model_path: Optional[Path] = None
    model_version: str = "1.0.0"


@dataclass
class ConversionConfigModel(ConfigModel):
    """
    Extended configuration model for conversion parameters.

    Extends Story 1.3 ConfigModel with conversion-specific functionality
    as defined in the architecture document.
    """

    model_config: ModelConfig = field(default_factory=ModelConfig)
    quantization_config: QuantizationConfig = field(default_factory=QuantizationConfig)
    performance_config: PerformanceConfig = field(default_factory=PerformanceConfig)
    conversion_params: Dict[str, Any] = field(default_factory=dict)
    model_specific: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize conversion config after dataclass creation."""
        super().__post_init__()
        self._setup_conversion_params()

    def _setup_conversion_params(self) -> None:
        """Setup conversion parameters from individual configs."""
        self.conversion_params.update({
            "input_format": self.model_config.input_format,
            "output_format": self.model_config.output_format,
            "precision": self.quantization_config.precision,
            "calibration_method": self.quantization_config.calibration_method,
            "batch_size": self.performance_config.batch_size,
            "num_workers": self.performance_config.num_workers,
        })

    def get_conversion_command_args(self) -> List[str]:
        """Get command line arguments for conversion."""
        args = []

        # Model configuration
        if self.model_config.model_path:
            args.extend(["--model", str(self.model_config.model_path)])

        # Quantization configuration
        if self.quantization_config.enabled:
            args.extend(["--quantize"])
            args.extend(["--precision", self.quantization_config.precision])
            args.extend(["--calibration-method", self.quantization_config.calibration_method])

        # Performance configuration
        args.extend(["--batch-size", str(self.performance_config.batch_size)])
        args.extend(["--workers", str(self.performance_config.num_workers)])

        return args

    def validate_conversion_config(self) -> List[str]:
        """
        Validate conversion configuration.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Validate model configuration
        if self.model_config.model_type not in ["sensevoice", "piper_vits"]:
            errors.append(f"Invalid model type: {self.model_config.model_type}")

        if self.model_config.input_format != "onnx":
            errors.append(f"Unsupported input format: {self.model_config.input_format}")

        if self.model_config.output_format != "bpu":
            errors.append(f"Unsupported output format: {self.model_config.output_format}")

        # Validate quantization configuration
        if self.quantization_config.precision not in ["int8", "int16", "float16"]:
            errors.append(f"Unsupported precision: {self.quantization_config.precision}")

        if self.quantization_config.calibration_method not in ["minmax", "kl_divergence", "entropy"]:
            errors.append(f"Unsupported calibration method: {self.quantization_config.calibration_method}")

        # Validate performance configuration
        if self.performance_config.batch_size < 1:
            errors.append("Batch size must be positive")

        if self.performance_config.num_workers < 1:
            errors.append("Number of workers must be positive")

        return errors

    def get_model_specific_config(self) -> Dict[str, Any]:
        """Get model-specific configuration."""
        return self.model_specific.get(self.model_config.model_type, {})

    def set_model_specific_config(self, config: Dict[str, Any]) -> None:
        """Set model-specific configuration."""
        if self.model_config.model_type not in self.model_specific:
            self.model_specific[self.model_config.model_type] = {}

        self.model_specific[self.model_config.model_type].update(config)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        result = super().to_dict()

        # Add conversion-specific fields
        result.update({
            "project": {
                "name": self.project_name,
                "version": self.version,
                "model_type": self.model_config.model_type
            },
            "model_config": {
                "model_type": self.model_config.model_type,
                "input_format": self.model_config.input_format,
                "output_format": self.model_config.output_format,
                "model_version": self.model_config.model_version
            },
            "quantization": {
                "enabled": self.quantization_config.enabled,
                "precision": self.quantization_config.precision,
                "calibration_method": self.quantization_config.calibration_method,
                "calibration_dataset_size": self.quantization_config.calibration_dataset_size,
                "symmetric": self.quantization_config.symmetric,
                "per_channel": self.quantization_config.per_channel
            },
            "performance": {
                "batch_size": self.performance_config.batch_size,
                "num_workers": self.performance_config.num_workers,
                "memory_limit": self.performance_config.memory_limit,
                "compute_units": self.performance_config.compute_units,
                "cache_size": self.performance_config.cache_size,
                "enable_optimization": self.performance_config.enable_optimization,
                "optimization_level": self.performance_config.optimization_level
            },
            "conversion_params": self.conversion_params,
            "model_specific": self.model_specific
        })

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversionConfigModel":
        """Create configuration from dictionary."""
        config = super().from_dict(data)

        # Extract model config
        if "model_config" in data:
            model_config = data["model_config"]
            config.model_config = ModelConfig(
                model_type=model_config.get("model_type", "sensevoice"),
                input_format=model_config.get("input_format", "onnx"),
                output_format=model_config.get("output_format", "bpu"),
                model_version=model_config.get("model_version", "1.0.0")
            )

        # Extract quantization config
        if "quantization" in data:
            quant_config = data["quantization"]
            config.quantization_config = QuantizationConfig(
                enabled=quant_config.get("enabled", True),
                precision=quant_config.get("precision", "int8"),
                calibration_method=quant_config.get("calibration_method", "minmax"),
                calibration_dataset_size=quant_config.get("calibration_dataset_size", 100),
                symmetric=quant_config.get("symmetric", False),
                per_channel=quant_config.get("per_channel", False)
            )

        # Extract performance config
        if "performance" in data:
            perf_config = data["performance"]
            config.performance_config = PerformanceConfig(
                batch_size=perf_config.get("batch_size", 1),
                num_workers=perf_config.get("num_workers", 4),
                memory_limit=perf_config.get("memory_limit", "8GB"),
                compute_units=perf_config.get("compute_units", 10),
                cache_size=perf_config.get("cache_size", "256MB"),
                enable_optimization=perf_config.get("enable_optimization", True),
                optimization_level=perf_config.get("optimization_level", "O2")
            )

        # Extract conversion params and model specific
        config.conversion_params = data.get("conversion_params", {})
        config.model_specific = data.get("model_specific", {})

        return config