"""
Conversion Data Models

This module defines data structures for managing model conversion operations.
These models provide type-safe containers for conversion contexts, model
information, and conversion-specific configuration.

Key Features:
- Type-safe data structures with validation
- JSON serialization for persistence and communication
- Immutable model information where appropriate
- Comprehensive metadata tracking
- Support for multiple model formats
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import json
from datetime import datetime
from enum import Enum

from ..exceptions.conversion_errors import ValidationError


class ModelFormat(Enum):
    """Supported model formats."""
    ONNX = "onnx"
    TENSORFLOW = "tensorflow"
    PYTORCH = "pytorch"
    CAFFE = "caffe"
    CUSTOM = "custom"


class ConversionType(Enum):
    """Supported conversion types."""
    PTQ = "ptq"  # Post-Training Quantization
    QAT = "qat"  # Quantization-Aware Training
    PRUNING = "pruning"
    OPTIMIZATION = "optimization"
    CUSTOM = "custom"


@dataclass
class ModelInfo:
    """
    Comprehensive information about a model.

    This class captures all relevant metadata about a model including
    format, size, architecture details, and operational parameters.
    """

    # Basic Information
    name: str
    format: ModelFormat
    version: str
    description: Optional[str] = None

    # File Information
    file_path: Optional[Path] = None
    file_size: Optional[int] = None  # in bytes
    checksum: Optional[str] = None

    # Architecture Information
    input_shape: Optional[List[Any]] = None
    output_shape: Optional[List[Any]] = None
    num_parameters: Optional[int] = None
    num_layers: Optional[int] = None
    layer_types: Optional[List[str]] = None

    # Operational Information
    input_dtype: Optional[str] = None
    output_dtype: Optional[str] = None
    precision: Optional[str] = None  # e.g., "fp32", "fp16", "int8"

    # Hardware Requirements
    memory_requirement: Optional[int] = None  # in MB
    compute_requirement: Optional[str] = None  # e.g., "CPU", "GPU", "NPU"

    # Metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def validate(self) -> None:
        """Validate model information for consistency."""
        if not self.name:
            raise ValidationError("Model name is required")

        if not self.format:
            raise ValidationError("Model format is required")

        if self.version is None or self.version == "":
            raise ValidationError("Model version is required")

        if self.file_path is not None and not self.file_path.exists():
            raise ValidationError(f"Model file does not exist: {self.file_path}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "format": self.format.value,
            "version": self.version,
            "description": self.description,
            "file_path": str(self.file_path) if self.file_path else None,
            "file_size": self.file_size,
            "checksum": self.checksum,
            "input_shape": self.input_shape,
            "output_shape": self.output_shape,
            "num_parameters": self.num_parameters,
            "num_layers": self.num_layers,
            "layer_types": self.layer_types,
            "input_dtype": self.input_dtype,
            "output_dtype": self.output_dtype,
            "precision": self.precision,
            "memory_requirement": self.memory_requirement,
            "compute_requirement": self.compute_requirement,
            "tags": self.tags,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelInfo":
        """Create from dictionary representation."""
        # Handle enum conversion
        if "format" in data and isinstance(data["format"], str):
            data["format"] = ModelFormat(data["format"])

        # Handle path conversion
        if "file_path" in data and data["file_path"] is not None:
            data["file_path"] = Path(data["file_path"])

        # Handle datetime conversion
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])

        return cls(**data)


@dataclass
class ConversionConfig:
    """
    Configuration for a specific conversion operation.

    This class contains all parameters and settings required for a conversion
    operation, including target format, optimization settings, and output options.
    """

    # Conversion Parameters
    conversion_type: ConversionType
    target_format: ModelFormat
    target_precision: Optional[str] = None  # e.g., "int8", "fp16"

    # Optimization Settings
    optimize_for_size: bool = True
    optimize_for_performance: bool = True
    optimization_level: int = 1  # 0-3, higher means more aggressive

    # Quantization Settings (for PTQ/QAT)
    calibration_data_path: Optional[Path] = None
    quantization_algorithm: Optional[str] = None  # e.g., "minmax", "kl", "entropy"
    per_channel_quantization: bool = False
    symmetric_quantization: bool = True

    # Output Settings
    output_path: Optional[Path] = None
    output_format: Optional[str] = None  # e.g., "onnx", "h5", "pb"
    include_metadata: bool = True
    include_debug_info: bool = False

    # Advanced Settings
    custom_parameters: Dict[str, Any] = field(default_factory=dict)
    hardware_target: Optional[str] = None  # e.g., "horizon_x5", "nvidia_gpu"
    memory_limit: Optional[int] = None  # in MB

    def validate(self) -> None:
        """Validate conversion configuration."""
        if not self.conversion_type:
            raise ValidationError("Conversion type is required")

        if not self.target_format:
            raise ValidationError("Target format is required")

        if self.optimization_level < 0 or self.optimization_level > 3:
            raise ValidationError("Optimization level must be between 0 and 3")

        # Validate conversion-specific requirements
        if self.conversion_type == ConversionType.PTQ:
            if not self.calibration_data_path:
                raise ValidationError("Calibration data path is required for PTQ")

        if self.calibration_data_path is not None and not self.calibration_data_path.exists():
            raise ValidationError(f"Calibration data file does not exist: {self.calibration_data_path}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "conversion_type": self.conversion_type.value,
            "target_format": self.target_format.value,
            "target_precision": self.target_precision,
            "optimize_for_size": self.optimize_for_size,
            "optimize_for_performance": self.optimize_for_performance,
            "optimization_level": self.optimization_level,
            "calibration_data_path": str(self.calibration_data_path) if self.calibration_data_path else None,
            "quantization_algorithm": self.quantization_algorithm,
            "per_channel_quantization": self.per_channel_quantization,
            "symmetric_quantization": self.symmetric_quantization,
            "output_path": str(self.output_path) if self.output_path else None,
            "output_format": self.output_format,
            "include_metadata": self.include_metadata,
            "include_debug_info": self.include_debug_info,
            "custom_parameters": self.custom_parameters,
            "hardware_target": self.hardware_target,
            "memory_limit": self.memory_limit,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversionConfig":
        """Create from dictionary representation."""
        # Handle enum conversions
        if "conversion_type" in data and isinstance(data["conversion_type"], str):
            data["conversion_type"] = ConversionType(data["conversion_type"])

        if "target_format" in data and isinstance(data["target_format"], str):
            data["target_format"] = ModelFormat(data["target_format"])

        # Handle path conversions
        for path_field in ["calibration_data_path", "output_path"]:
            if path_field in data and data[path_field] is not None:
                data[path_field] = Path(data[path_field])

        return cls(**data)


@dataclass
class ConversionModel:
    """
    Complete context for a model conversion operation.

    This class combines model information, conversion configuration, and
    runtime state into a single comprehensive context that can be passed
    through the conversion pipeline.
    """

    # Core Information
    model_info: ModelInfo
    conversion_config: ConversionConfig

    # Runtime State
    conversion_id: str
    status: str = "initialized"  # initialized, running, completed, failed
    progress_percentage: float = 0.0
    current_step: str = "initialized"

    # Timing Information
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Execution Context
    working_directory: Optional[Path] = None
    temporary_files: List[Path] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)

    # Intermediate Results
    intermediate_results: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate the conversion model."""
        self.model_info.validate()
        self.conversion_config.validate()

        if not self.conversion_id:
            raise ValidationError("Conversion ID is required")

    def start_conversion(self) -> None:
        """Mark conversion as started."""
        self.status = "running"
        self.started_at = datetime.now()
        self.current_step = "conversion_started"

    def complete_conversion(self) -> None:
        """Mark conversion as completed."""
        self.status = "completed"
        self.completed_at = datetime.now()
        self.progress_percentage = 100.0
        self.current_step = "conversion_completed"

    def fail_conversion(self, error_message: str) -> None:
        """Mark conversion as failed."""
        self.status = "failed"
        self.completed_at = datetime.now()
        self.current_step = "conversion_failed"
        self.logs.append(f"Conversion failed: {error_message}")

    def update_progress(self, percentage: float, step: str) -> None:
        """Update conversion progress."""
        self.progress_percentage = max(0.0, min(100.0, percentage))
        self.current_step = step

    def add_log(self, message: str) -> None:
        """Add a log message."""
        timestamp = datetime.now().isoformat()
        self.logs.append(f"[{timestamp}] {message}")

    def add_temporary_file(self, file_path: Path) -> None:
        """Add a temporary file to track."""
        self.temporary_files.append(file_path)

    def set_metric(self, name: str, value: float) -> None:
        """Set a performance metric."""
        self.metrics[name] = value

    def get_execution_time(self) -> Optional[float]:
        """Get total execution time in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "model_info": self.model_info.to_dict(),
            "conversion_config": self.conversion_config.to_dict(),
            "conversion_id": self.conversion_id,
            "status": self.status,
            "progress_percentage": self.progress_percentage,
            "current_step": self.current_step,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "working_directory": str(self.working_directory) if self.working_directory else None,
            "temporary_files": [str(p) for p in self.temporary_files],
            "logs": self.logs,
            "intermediate_results": self.intermediate_results,
            "metrics": self.metrics,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversionModel":
        """Create from dictionary representation."""
        # Handle datetime conversions
        for dt_field in ["created_at", "started_at", "completed_at"]:
            if dt_field in data and data[dt_field] is not None:
                data[dt_field] = datetime.fromisoformat(data[dt_field])

        # Handle nested model conversions
        if "model_info" in data:
            data["model_info"] = ModelInfo.from_dict(data["model_info"])

        if "conversion_config" in data:
            data["conversion_config"] = ConversionConfig.from_dict(data["conversion_config"])

        # Handle path conversions
        if "working_directory" in data and data["working_directory"] is not None:
            data["working_directory"] = Path(data["working_directory"])

        if "temporary_files" in data:
            data["temporary_files"] = [Path(p) for p in data["temporary_files"]]

        return cls(**data)