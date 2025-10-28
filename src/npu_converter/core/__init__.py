"""
NPU Converter Core Framework

This package provides the core architecture and interfaces for the NPU converter system.
It contains abstract base classes, data models, exceptions, and utilities that are
shared across all converter implementations.

Architecture Layers:
- Interfaces: Abstract base classes defining converter contracts
- Models: Data structures for conversion, configuration, and results
- Exceptions: Hierarchy of error types for consistent error handling
- Utils: Common utilities for validation, serialization, etc.

Dependencies:
- Converters depend on Core interfaces
- Core depends on external libraries (ONNX, YAML, etc.)
- No circular dependencies allowed
"""

from .interfaces import (
    BaseConverter,
    BaseQuantizer,
    BaseProgressTracker,
    ConversionProgressTracker,
    ProgressStage,
    BaseValidator,
    ModelValidator,
    ValidationResult,
    ValidationLevel,
    QuantizationStrategy,
    PTQStrategy,
    QATStrategy,
    QuantizationType,
    Precision
)
from .models.conversion_model import ConversionModel
from .models.config_model import ConfigModel
from .models.progress_model import ProgressModel
from .models.result_model import ResultModel
from .exceptions import (
    ConversionError,
    ValidationError,
    ConversionTimeoutError,
    ModelCompatibilityError,
    QuantizationError,
    OptimizationError,
    ExportError,
    ResourceError,
    ConfigError,
    ConfigValidationError,
    ConfigNotFoundError,
    ConfigLoadError,
    ConfigMergeError,
    ConfigSchemaError,
    ErrorContext,
    handle_conversion_errors,
    handle_config_errors,
    retry_on_error,
    timeout_handler,
    error_context,
    validate_parameters,
    ErrorReporter
)

__version__ = "1.0.0"
__author__ = "NPU Converter Team"

__all__ = [
    # Base Interfaces
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

    # Data Models
    "ConversionModel",
    "ConfigModel",
    "ProgressModel",
    "ResultModel",

    # Exception Classes
    "ConversionError",
    "ValidationError",
    "ConversionTimeoutError",
    "ModelCompatibilityError",
    "QuantizationError",
    "OptimizationError",
    "ExportError",
    "ResourceError",
    "ConfigError",
    "ConfigValidationError",
    "ConfigNotFoundError",
    "ConfigLoadError",
    "ConfigMergeError",
    "ConfigSchemaError",

    # Exception Handlers and Utilities
    "ErrorContext",
    "handle_conversion_errors",
    "handle_config_errors",
    "retry_on_error",
    "timeout_handler",
    "error_context",
    "validate_parameters",
    "ErrorReporter",
]