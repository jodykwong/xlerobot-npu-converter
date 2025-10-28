"""
Result Data Models

This module defines data structures for representing conversion results,
performance metrics, and analysis reports. These models provide standardized
ways to store, analyze, and communicate conversion outcomes.

Key Features:
- Comprehensive result representation
- Performance metrics and analysis
- Quality assessment and validation
- Exportable report generation
- Comparison and benchmarking support
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from datetime import datetime
from enum import Enum
import json

from ..exceptions.conversion_errors import ValidationError


class ResultStatus(Enum):
    """Result status values."""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class QualityLevel(Enum):
    """Quality assessment levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"


@dataclass
class PerformanceMetrics:
    """
    Performance metrics for conversion operations.

    Contains comprehensive performance data including timing,
    resource usage, and efficiency measurements.
    """

    # Timing Metrics
    total_time: float  # in seconds
    preprocessing_time: Optional[float] = None
    conversion_time: Optional[float] = None
    postprocessing_time: Optional[float] = None
    validation_time: Optional[float] = None

    # Memory Metrics
    peak_memory_usage: Optional[float] = None  # in MB
    average_memory_usage: Optional[float] = None  # in MB
    memory_efficiency: Optional[float] = None  # 0.0 to 1.0

    # CPU/GPU Metrics
    cpu_utilization: Optional[float] = None  # 0.0 to 1.0
    gpu_utilization: Optional[float] = None  # 0.0 to 1.0
    compute_efficiency: Optional[float] = None  # 0.0 to 1.0

    # I/O Metrics
    input_read_time: Optional[float] = None  # in seconds
    output_write_time: Optional[float] = None  # in seconds
    io_throughput: Optional[float] = None  # in MB/s

    # Quality Metrics
    accuracy_preservation: Optional[float] = None  # 0.0 to 1.0
    compression_ratio: Optional[float] = None  # output_size / input_size
    inference_speedup: Optional[float] = None  # speedup factor

    # Custom Metrics
    custom_metrics: Dict[str, float] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate performance metrics."""
        if self.total_time <= 0:
            raise ValidationError("Total time must be positive")

        # Validate percentage values
        for field_name, value in [
            ("memory_efficiency", self.memory_efficiency),
            ("cpu_utilization", self.cpu_utilization),
            ("gpu_utilization", self.gpu_utilization),
            ("compute_efficiency", self.compute_efficiency),
            ("accuracy_preservation", self.accuracy_preservation),
        ]:
            if value is not None and (value < 0.0 or value > 1.0):
                raise ValidationError(f"{field_name} must be between 0.0 and 1.0")

        if self.compression_ratio is not None and self.compression_ratio <= 0:
            raise ValidationError("Compression ratio must be positive")

        if self.inference_speedup is not None and self.inference_speedup <= 0:
            raise ValidationError("Inference speedup must be positive")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "total_time": self.total_time,
            "preprocessing_time": self.preprocessing_time,
            "conversion_time": self.conversion_time,
            "postprocessing_time": self.postprocessing_time,
            "validation_time": self.validation_time,
            "peak_memory_usage": self.peak_memory_usage,
            "average_memory_usage": self.average_memory_usage,
            "memory_efficiency": self.memory_efficiency,
            "cpu_utilization": self.cpu_utilization,
            "gpu_utilization": self.gpu_utilization,
            "compute_efficiency": self.compute_efficiency,
            "input_read_time": self.input_read_time,
            "output_write_time": self.output_write_time,
            "io_throughput": self.io_throughput,
            "accuracy_preservation": self.accuracy_preservation,
            "compression_ratio": self.compression_ratio,
            "inference_speedup": self.inference_speedup,
            "custom_metrics": self.custom_metrics,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerformanceMetrics":
        """Create from dictionary representation."""
        return cls(**data)


@dataclass
class QualityAssessment:
    """
    Quality assessment for conversion results.

    Provides comprehensive quality evaluation including accuracy,
    performance, and compliance metrics.
    """

    # Overall Assessment
    overall_quality: QualityLevel
    quality_score: float  # 0.0 to 1.0

    # Accuracy Assessment
    accuracy_score: Optional[float] = None  # 0.0 to 1.0
    accuracy_degradation: Optional[float] = None  # 0.0 to 1.0
    top1_accuracy: Optional[float] = None  # 0.0 to 1.0
    top5_accuracy: Optional[float] = None  # 0.0 to 1.0

    # Performance Assessment
    performance_score: Optional[float] = None  # 0.0 to 1.0
    latency_improvement: Optional[float] = None  # percentage improvement
    throughput_improvement: Optional[float] = None  # percentage improvement
    energy_efficiency: Optional[float] = None  # 0.0 to 1.0

    # Model Characteristics
    model_size_reduction: Optional[float] = None  # percentage reduction
    parameter_count_reduction: Optional[float] = None  # percentage reduction
    complexity_reduction: Optional[float] = None  # 0.0 to 1.0

    # Compliance Assessment
    standard_compliance: Optional[float] = None  # 0.0 to 1.0
    hardware_compatibility: Optional[float] = None  # 0.0 to 1.0
    format_compliance: Optional[float] = None  # 0.0 to 1.0

    # Issues and Recommendations
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    # Assessment Details
    assessment_details: Dict[str, Any] = field(default_factory=dict)
    comparison_baseline: Optional[str] = None  # baseline model name

    def validate(self) -> None:
        """Validate quality assessment."""
        if not 0.0 <= self.quality_score <= 1.0:
            raise ValidationError("Quality score must be between 0.0 and 1.0")

        # Validate score values
        for field_name, value in [
            ("accuracy_score", self.accuracy_score),
            ("performance_score", self.performance_score),
            ("top1_accuracy", self.top1_accuracy),
            ("top5_accuracy", self.top5_accuracy),
            ("energy_efficiency", self.energy_efficiency),
            ("complexity_reduction", self.complexity_reduction),
            ("standard_compliance", self.standard_compliance),
            ("hardware_compatibility", self.hardware_compatibility),
            ("format_compliance", self.format_compliance),
        ]:
            if value is not None and (value < 0.0 or value > 1.0):
                raise ValidationError(f"{field_name} must be between 0.0 and 1.0")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "overall_quality": self.overall_quality.value,
            "quality_score": self.quality_score,
            "accuracy_score": self.accuracy_score,
            "accuracy_degradation": self.accuracy_degradation,
            "top1_accuracy": self.top1_accuracy,
            "top5_accuracy": self.top5_accuracy,
            "performance_score": self.performance_score,
            "latency_improvement": self.latency_improvement,
            "throughput_improvement": self.throughput_improvement,
            "energy_efficiency": self.energy_efficiency,
            "model_size_reduction": self.model_size_reduction,
            "parameter_count_reduction": self.parameter_count_reduction,
            "complexity_reduction": self.complexity_reduction,
            "standard_compliance": self.standard_compliance,
            "hardware_compatibility": self.hardware_compatibility,
            "format_compliance": self.format_compliance,
            "issues": self.issues,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
            "assessment_details": self.assessment_details,
            "comparison_baseline": self.comparison_baseline,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QualityAssessment":
        """Create from dictionary representation."""
        if "overall_quality" in data and isinstance(data["overall_quality"], str):
            data["overall_quality"] = QualityLevel(data["overall_quality"])

        return cls(**data)


@dataclass
class ConversionSummary:
    """
    Summary of conversion operation.

    Provides high-level summary information about the conversion
    operation including key metrics and outcomes.
    """

    # Basic Information
    conversion_id: str
    model_name: str
    conversion_type: str
    target_format: str
    status: ResultStatus

    # Timing Information
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None  # in seconds

    # Size Information
    input_model_size: Optional[int] = None  # in bytes
    output_model_size: Optional[int] = None  # in bytes
    size_reduction: Optional[float] = None  # percentage

    # Quality Information
    success_rate: Optional[float] = None  # 0.0 to 1.0
    quality_score: Optional[float] = None  # 0.0 to 1.0
    accuracy_preservation: Optional[float] = None  # 0.0 to 1.0

    # Performance Information
    speed_improvement: Optional[float] = None  # percentage
    memory_improvement: Optional[float] = None  # percentage

    # Output Information
    output_files: List[Path] = field(default_factory=list)
    report_files: List[Path] = field(default_factory=list)

    # Additional Information
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate conversion summary."""
        if not self.conversion_id:
            raise ValidationError("Conversion ID is required")

        if not self.model_name:
            raise ValidationError("Model name is required")

        if not self.conversion_type:
            raise ValidationError("Conversion type is required")

        if not self.target_format:
            raise ValidationError("Target format is required")

        # Validate percentage values
        for field_name, value in [
            ("success_rate", self.success_rate),
            ("quality_score", self.quality_score),
            ("accuracy_preservation", self.accuracy_preservation),
        ]:
            if value is not None and (value < 0.0 or value > 1.0):
                raise ValidationError(f"{field_name} must be between 0.0 and 1.0")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "conversion_id": self.conversion_id,
            "model_name": self.model_name,
            "conversion_type": self.conversion_type,
            "target_format": self.target_format,
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "input_model_size": self.input_model_size,
            "output_model_size": self.output_model_size,
            "size_reduction": self.size_reduction,
            "success_rate": self.success_rate,
            "quality_score": self.quality_score,
            "accuracy_preservation": self.accuracy_preservation,
            "speed_improvement": self.speed_improvement,
            "memory_improvement": self.memory_improvement,
            "output_files": [str(p) for p in self.output_files],
            "report_files": [str(p) for p in self.report_files],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversionSummary":
        """Create from dictionary representation."""
        if "status" in data and isinstance(data["status"], str):
            data["status"] = ResultStatus(data["status"])

        # Handle datetime conversions
        for dt_field in ["start_time", "end_time"]:
            if dt_field in data and data[dt_field] is not None:
                data[dt_field] = datetime.fromisoformat(data[dt_field])

        # Handle path conversions
        for path_field in ["output_files", "report_files"]:
            if path_field in data:
                data[path_field] = [Path(p) for p in data[path_field]]

        return cls(**data)


@dataclass
class ResultModel:
    """
    Comprehensive result model for conversion operations.

    This class provides a complete representation of conversion results,
    including performance metrics, quality assessment, and detailed reports.
    """

    # Basic Information
    conversion_id: str
    model_name: str
    conversion_type: str
    status: ResultStatus

    # Results Data
    summary: ConversionSummary
    performance_metrics: PerformanceMetrics
    quality_assessment: Optional[QualityAssessment] = None

    # Detailed Results
    detailed_metrics: Dict[str, Any] = field(default_factory=dict)
    layer_analysis: Optional[Dict[str, Any]] = None
    optimization_details: Optional[Dict[str, Any]] = None

    # Output Information
    output_models: List[Path] = field(default_factory=list)
    output_reports: List[Path] = field(default_factory=list)
    intermediate_files: List[Path] = field(default_factory=list)

    # Operation Information
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    configuration: Optional[Dict[str, Any]] = None

    # Error and Warning Information
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    debug_info: Dict[str, Any] = field(default_factory=dict)

    # Comparison Information
    baseline_comparison: Optional[Dict[str, Any]] = None
    benchmark_results: Optional[Dict[str, Any]] = None

    def validate(self) -> None:
        """Validate the result model."""
        if not self.conversion_id:
            raise ValidationError("Conversion ID is required")

        if not self.model_name:
            raise ValidationError("Model name is required")

        if not self.conversion_type:
            raise ValidationError("Conversion type is required")

        # Validate nested models
        self.summary.validate()
        self.performance_metrics.validate()

        if self.quality_assessment:
            self.quality_assessment.validate()

    def is_successful(self) -> bool:
        """Check if the conversion was successful."""
        return self.status in [ResultStatus.SUCCESS, ResultStatus.PARTIAL_SUCCESS]

    def get_success_rate(self) -> float:
        """Get the success rate as a percentage."""
        if self.quality_assessment and self.quality_assessment.quality_score is not None:
            return self.quality_assessment.quality_score * 100
        elif self.summary.success_rate is not None:
            return self.summary.success_rate * 100
        return 100.0 if self.is_successful() else 0.0

    def get_duration(self) -> Optional[float]:
        """Get the total duration in seconds."""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        return self.performance_metrics.total_time

    def get_size_reduction(self) -> Optional[float]:
        """Get the size reduction percentage."""
        if self.summary.size_reduction is not None:
            return self.summary.size_reduction
        elif (self.summary.input_model_size and self.summary.output_model_size and
              self.summary.input_model_size > 0):
            return ((self.summary.input_model_size - self.summary.output_model_size) /
                   self.summary.input_model_size * 100)
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "conversion_id": self.conversion_id,
            "model_name": self.model_name,
            "conversion_type": self.conversion_type,
            "status": self.status.value,
            "summary": self.summary.to_dict(),
            "performance_metrics": self.performance_metrics.to_dict(),
            "quality_assessment": self.quality_assessment.to_dict() if self.quality_assessment else None,
            "detailed_metrics": self.detailed_metrics,
            "layer_analysis": self.layer_analysis,
            "optimization_details": self.optimization_details,
            "output_models": [str(p) for p in self.output_models],
            "output_reports": [str(p) for p in self.output_reports],
            "intermediate_files": [str(p) for p in self.intermediate_files],
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "configuration": self.configuration,
            "errors": self.errors,
            "warnings": self.warnings,
            "debug_info": self.debug_info,
            "baseline_comparison": self.baseline_comparison,
            "benchmark_results": self.benchmark_results,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResultModel":
        """Create from dictionary representation."""
        if "status" in data and isinstance(data["status"], str):
            data["status"] = ResultStatus(data["status"])

        # Handle datetime conversions
        for dt_field in ["start_time", "end_time"]:
            if dt_field in data and data[dt_field] is not None:
                data[dt_field] = datetime.fromisoformat(data[dt_field])

        # Handle nested model conversions
        if "summary" in data:
            data["summary"] = ConversionSummary.from_dict(data["summary"])

        if "performance_metrics" in data:
            data["performance_metrics"] = PerformanceMetrics.from_dict(data["performance_metrics"])

        if "quality_assessment" in data and data["quality_assessment"] is not None:
            data["quality_assessment"] = QualityAssessment.from_dict(data["quality_assessment"])

        # Handle path conversions
        for path_field in ["output_models", "output_reports", "intermediate_files"]:
            if path_field in data:
                data[path_field] = [Path(p) for p in data[path_field]]

        return cls(**data)

    def save_to_file(self, file_path: Path) -> None:
        """Save result model to JSON file."""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(self.to_dict(), f, indent=2, default=str)
        except Exception as e:
            raise ValidationError(f"Failed to save result to {file_path}: {str(e)}")

    @classmethod
    def load_from_file(cls, file_path: Path) -> "ResultModel":
        """Load result model from JSON file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            raise ValidationError(f"Failed to load result from {file_path}: {str(e)}")