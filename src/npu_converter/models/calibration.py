"""
PTQ Calibration Configuration Data Models

This module contains data classes for PTQ calibration data configuration
as defined in the Story Context XML. Now uses core PTQ configuration models
for better architectural alignment.
"""

from dataclasses import dataclass
from typing import Tuple, Optional, Any
from pathlib import Path

# Import from core models for architectural alignment
from ..core.models.ptq_config import CalibrationConfig as CoreCalibrationConfig

# Re-export for backward compatibility
CalibrationConfig = CoreCalibrationConfig


@dataclass
class CalibrationData:
    """Processed calibration data ready for PTQ."""
    data: Any
    config: CalibrationConfig
    preprocessing_applied: bool = False
    statistics: Optional[dict] = None
    validation_results: Optional[dict] = None

    def validate(self) -> bool:
        """Validate calibration data quality."""
        if self.data is None:
            return False
        if not self.preprocessing_applied:
            return False
        if self.validation_results is None:
            return False
        return True


@dataclass
class ModelInfo:
    """Model information extracted during PTQ preparation."""
    model_path: str
    input_shape: Tuple[int, ...]
    output_shape: Tuple[int, ...]
    model_size_mb: float
    num_parameters: int
    model_format: str = "onnx"
    opset_version: Optional[int] = None
    supported_ops: Optional[list] = None
    unsupported_ops: Optional[list] = None

    def is_compatible(self) -> bool:
        """Check if model is compatible with PTQ."""
        if self.unsupported_ops and len(self.unsupported_ops) > 0:
            return False
        return True


@dataclass
class ValidationResult:
    """Model validation results."""
    is_valid: bool
    errors: list
    warnings: list
    compatibility_score: float
    recommendations: list

    def has_critical_errors(self) -> bool:
        """Check if there are critical validation errors."""
        return any("critical" in error.lower() for error in self.errors)


@dataclass
class QuantizedModel:
    """Quantized model after PTQ processing."""
    model_path: str
    quantization_config: dict
    calibration_info: CalibrationData
    model_info: ModelInfo
    quantization_statistics: dict

    def get_compression_ratio(self) -> float:
        """Calculate model compression ratio."""
        return self.model_info.model_size_mb / self.quantization_statistics.get('quantized_size_mb', 1.0)


@dataclass
class CompiledModel:
    """Compiled model ready for BPU deployment."""
    model_path: str
    compilation_config: dict
    target_device: str
    compilation_log: str
    success: bool
    performance_metrics: dict

    def is_deployment_ready(self) -> bool:
        """Check if model is ready for deployment."""
        return self.success and self.compilation_log is not None


@dataclass
class PerformanceResult:
    """Performance analysis results."""
    inference_time_ms: float
    throughput_fps: float
    memory_usage_mb: float
    power_consumption_w: Optional[float] = None
    benchmark_score: Optional[float] = None
    comparison_with_baseline: Optional[dict] = None

    def meets_performance_target(self, target_fps: float = 30.0) -> bool:
        """Check if performance meets target requirements."""
        return self.throughput_fps >= target_fps


@dataclass
class AccuracyResult:
    """Accuracy analysis results."""
    accuracy_before_quantization: float
    accuracy_after_quantization: float
    accuracy_drop_percentage: float
    per_class_accuracy: Optional[dict] = None
    metrics: Optional[dict] = None

    def meets_accuracy_target(self, target_accuracy: float = 98.0) -> bool:
        """Check if accuracy meets target requirements."""
        return self.accuracy_after_quantization >= target_accuracy

    def is_acceptable_drop(self, max_drop: float = 2.0) -> bool:
        """Check if accuracy drop is acceptable."""
        return self.accuracy_drop_percentage <= max_drop


@dataclass
class ModelAnalysis:
    """Model analysis results from debug tools."""
    model_info: ModelInfo
    op_analysis: dict
    memory_analysis: dict
    compatibility_report: dict
    optimization_suggestions: list