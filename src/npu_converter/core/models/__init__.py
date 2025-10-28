"""
Core Data Models Package

This package contains data structures that are used throughout the NPU converter
system. These models provide type-safe containers for conversion data,
configuration, progress tracking, and results.

Key Features:
- Type safety with dataclasses and type hints
- JSON serialization support
- Validation and error handling
- Immutable where appropriate
- Standardized interfaces across the system
"""

from .conversion_model import (
    ConversionModel,
    ModelInfo,
    ConversionConfig,
    ModelFormat,
    ConversionType
)
from .config_model import (
    ConfigModel,
    HardwareConfig,
    SystemConfig,
    LogLevel,
    HardwareType
)
from .progress_model import (
    ProgressModel,
    ProgressStep,
    ProgressStatus
)
from .result_model import (
    ResultModel,
    PerformanceMetrics,
    QualityAssessment,
    ConversionSummary,
    ResultStatus,
    QualityLevel
)

__all__ = [
    # Conversion Models
    "ConversionModel",
    "ModelInfo",
    "ConversionConfig",
    "ModelFormat",
    "ConversionType",

    # Configuration Models
    "ConfigModel",
    "HardwareConfig",
    "SystemConfig",
    "LogLevel",
    "HardwareType",

    # Progress Models
    "ProgressModel",
    "ProgressStep",
    "ProgressStatus",

    # Result Models
    "ResultModel",
    "PerformanceMetrics",
    "QualityAssessment",
    "ConversionSummary",
    "ResultStatus",
    "QualityLevel",
]