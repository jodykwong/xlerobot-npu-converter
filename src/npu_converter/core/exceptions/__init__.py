"""
Core Exception Classes Package

This package contains the exception hierarchy for the NPU converter system.
These exceptions provide standardized error handling and detailed error
information throughout the conversion pipeline.

Key Features:
- Hierarchical exception structure
- Detailed error context and metadata
- User-friendly error messages
- Debug information support
"""

from .conversion_errors import (
    ConversionError,
    ValidationError,
    ModelCompatibilityError,
    ConversionTimeoutError,
    QuantizationError,
    OptimizationError,
    ExportError,
    ResourceError
)

from .config_errors import (
    ConfigError,
    ConfigValidationError,
    ConfigNotFoundError,
    ConfigLoadError,
    ConfigMergeError,
    ConfigSchemaError
)

from .exception_handlers import (
    ErrorContext,
    handle_conversion_errors,
    handle_config_errors,
    retry_on_error,
    timeout_handler,
    error_context,
    validate_parameters,
    ErrorReporter
)

__all__ = [
    # Conversion Errors
    "ConversionError",
    "ValidationError",
    "ModelCompatibilityError",
    "ConversionTimeoutError",
    "QuantizationError",
    "OptimizationError",
    "ExportError",
    "ResourceError",

    # Config Errors
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