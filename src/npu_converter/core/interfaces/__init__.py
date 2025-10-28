"""
Core Interfaces Package

This package contains abstract base classes that define the contracts for all
converter implementations. These interfaces ensure consistency across different
converter types and enable plugin-based architecture.

Key Design Principles:
- All converters must inherit from BaseConverter
- All quantizers must inherit from BaseQuantizer
- Interfaces are abstract - no concrete implementations here
- Type hints and documentation required for all methods
"""

from .base_converter import BaseConverter
from .base_quantizer import BaseQuantizer
from .progress_tracker import (
    BaseProgressTracker,
    ConversionProgressTracker,
    ProgressStage
)
from .validator import (
    BaseValidator,
    ModelValidator,
    ValidationResult,
    ValidationLevel
)
from .quantization_strategy import (
    QuantizationStrategy,
    PTQStrategy,
    QATStrategy,
    QuantizationType,
    Precision
)

__all__ = [
    "BaseConverter",
    "BaseQuantizer",
    "BaseProgressTracker",
    "ConversionProgressTracker",
    "ProgressStage",
    "BaseValidator",
    "ModelValidator",
    "ValidationResult",
    "ValidationLevel",
    "QuantizationStrategy",
    "PTQStrategy",
    "QATStrategy",
    "QuantizationType",
    "Precision",
]