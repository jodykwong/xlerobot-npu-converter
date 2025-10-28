"""
Conversion-related Exception Classes

This module defines the hierarchy of exceptions for conversion operations.
These exceptions provide detailed error information and context for debugging
and error handling throughout the conversion pipeline.

Key Features:
- Hierarchical exception structure
- Error context and metadata
- User-friendly error messages
- Debug information support
- Error recovery suggestions
"""

from typing import Any, Dict, List, Optional
from datetime import datetime


class ConversionError(Exception):
    """
    Base exception for all conversion-related errors.

    This class serves as the foundation for all conversion-related exceptions
    and provides common functionality for error context, metadata, and
    user-friendly messaging.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
        cause: Optional[Exception] = None
    ) -> None:
        """
        Initialize conversion error.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            context: Additional context information
            suggestions: List of suggested solutions
            cause: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.suggestions = suggestions or []
        self.cause = cause
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary representation."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
            "suggestions": self.suggestions,
            "timestamp": self.timestamp.isoformat(),
            "cause": str(self.cause) if self.cause else None,
        }

    def __str__(self) -> str:
        """String representation with suggestions."""
        result = f"[{self.error_code}] {self.message}"

        if self.suggestions:
            result += "\n\nSuggested solutions:"
            for i, suggestion in enumerate(self.suggestions, 1):
                result += f"\n{i}. {suggestion}"

        return result


class ValidationError(ConversionError):
    """
    Exception raised when validation fails.

    This exception is used when input validation, configuration validation,
    or other validation steps fail during the conversion process.
    """

    def __init__(
        self,
        message: str,
        validation_field: Optional[str] = None,
        validation_value: Optional[Any] = None,
        expected_value: Optional[Any] = None,
        **kwargs
    ) -> None:
        """
        Initialize validation error.

        Args:
            message: Human-readable error message
            validation_field: Field that failed validation
            validation_value: Value that failed validation
            expected_value: Expected value or range
            **kwargs: Additional arguments passed to base class
        """
        super().__init__(message, **kwargs)

        # Add validation-specific context
        if validation_field:
            self.context["validation_field"] = validation_field
        if validation_value is not None:
            self.context["validation_value"] = validation_value
        if expected_value is not None:
            self.context["expected_value"] = expected_value

        # Add default suggestions if not provided
        if not self.suggestions:
            self.suggestions = [
                "Check input parameters and try again",
                "Refer to the documentation for valid parameter ranges",
                "Validate the input model before conversion"
            ]


class ModelCompatibilityError(ConversionError):
    """
    Exception raised when model compatibility issues are detected.

    This exception is used when the input model is not compatible with the
    target conversion type, hardware platform, or other requirements.
    """

    def __init__(
        self,
        message: str,
        model_format: Optional[str] = None,
        target_format: Optional[str] = None,
        incompatible_layers: Optional[List[str]] = None,
        **kwargs
    ) -> None:
        """
        Initialize model compatibility error.

        Args:
            message: Human-readable error message
            model_format: Format of the input model
            target_format: Target conversion format
            incompatible_layers: List of incompatible layer names
            **kwargs: Additional arguments passed to base class
        """
        super().__init__(message, **kwargs)

        # Add compatibility-specific context
        if model_format:
            self.context["model_format"] = model_format
        if target_format:
            self.context["target_format"] = target_format
        if incompatible_layers:
            self.context["incompatible_layers"] = incompatible_layers

        # Add default suggestions if not provided
        if not self.suggestions:
            self.suggestions = [
                "Check if the model format is supported",
                "Consider converting to an intermediate format first",
                "Verify all layers are supported by the target platform",
                "Use model compatibility checker before conversion"
            ]


class ConversionTimeoutError(ConversionError):
    """
    Exception raised when conversion operations exceed time limits.

    This exception is used when conversion operations take longer than
    the configured timeout period.
    """

    def __init__(
        self,
        message: str,
        timeout_duration: Optional[float] = None,
        elapsed_time: Optional[float] = None,
        operation: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Initialize timeout error.

        Args:
            message: Human-readable error message
            timeout_duration: Configured timeout duration in seconds
            elapsed_time: Actual elapsed time in seconds
            operation: Operation that timed out
            **kwargs: Additional arguments passed to base class
        """
        super().__init__(message, **kwargs)

        # Add timeout-specific context
        if timeout_duration is not None:
            self.context["timeout_duration"] = timeout_duration
        if elapsed_time is not None:
            self.context["elapsed_time"] = elapsed_time
        if operation:
            self.context["operation"] = operation

        # Add default suggestions if not provided
        if not self.suggestions:
            self.suggestions = [
                "Increase the timeout duration",
                "Check system resources and performance",
                "Consider reducing model complexity",
                "Use more powerful hardware if available"
            ]


class QuantizationError(ConversionError):
    """
    Exception raised during quantization operations.

    This exception is used for errors that occur specifically during
    model quantization processes.
    """

    def __init__(
        self,
        message: str,
        quantization_type: Optional[str] = None,
        target_precision: Optional[str] = None,
        problematic_layers: Optional[List[str]] = None,
        **kwargs
    ) -> None:
        """
        Initialize quantization error.

        Args:
            message: Human-readable error message
            quantization_type: Type of quantization (PTQ, QAT, etc.)
            target_precision: Target precision (int8, fp16, etc.)
            problematic_layers: List of problematic layer names
            **kwargs: Additional arguments passed to base class
        """
        super().__init__(message, **kwargs)

        # Add quantization-specific context
        if quantization_type:
            self.context["quantization_type"] = quantization_type
        if target_precision:
            self.context["target_precision"] = target_precision
        if problematic_layers:
            self.context["problematic_layers"] = problematic_layers

        # Add default suggestions if not provided
        if not self.suggestions:
            self.suggestions = [
                "Check if the target precision is supported",
                "Verify calibration data quality and quantity",
                "Consider per-channel quantization",
                "Try different quantization algorithms"
            ]


class OptimizationError(ConversionError):
    """
    Exception raised during model optimization operations.

    This exception is used for errors that occur during model optimization
    processes such as pruning, fusion, or other optimization techniques.
    """

    def __init__(
        self,
        message: str,
        optimization_type: Optional[str] = None,
        optimization_level: Optional[int] = None,
        failed_operations: Optional[List[str]] = None,
        **kwargs
    ) -> None:
        """
        Initialize optimization error.

        Args:
            message: Human-readable error message
            optimization_type: Type of optimization (pruning, fusion, etc.)
            optimization_level: Optimization level that failed
            failed_operations: List of failed optimization operations
            **kwargs: Additional arguments passed to base class
        """
        super().__init__(message, **kwargs)

        # Add optimization-specific context
        if optimization_type:
            self.context["optimization_type"] = optimization_type
        if optimization_level is not None:
            self.context["optimization_level"] = optimization_level
        if failed_operations:
            self.context["failed_operations"] = failed_operations

        # Add default suggestions if not provided
        if not self.suggestions:
            self.suggestions = [
                "Reduce optimization level",
                "Check model compatibility with optimizations",
                "Try different optimization parameters",
                "Skip problematic optimization operations"
            ]


class ExportError(ConversionError):
    """
    Exception raised during model export operations.

    This exception is used for errors that occur when exporting converted
    models to various formats or destinations.
    """

    def __init__(
        self,
        message: str,
        export_format: Optional[str] = None,
        output_path: Optional[str] = None,
        export_step: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Initialize export error.

        Args:
            message: Human-readable error message
            export_format: Target export format
            output_path: Output path that failed
            export_step: Export step that failed
            **kwargs: Additional arguments passed to base class
        """
        super().__init__(message, **kwargs)

        # Add export-specific context
        if export_format:
            self.context["export_format"] = export_format
        if output_path:
            self.context["output_path"] = output_path
        if export_step:
            self.context["export_step"] = export_step

        # Add default suggestions if not provided
        if not self.suggestions:
            self.suggestions = [
                "Check output path permissions and disk space",
                "Verify export format is supported",
                "Check model compatibility with export format",
                "Try different export parameters"
            ]


class ResourceError(ConversionError):
    """
    Exception raised when system resources are insufficient.

    This exception is used when there are insufficient system resources
    (memory, disk space, etc.) to complete conversion operations.
    """

    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        required_amount: Optional[float] = None,
        available_amount: Optional[float] = None,
        **kwargs
    ) -> None:
        """
        Initialize resource error.

        Args:
            message: Human-readable error message
            resource_type: Type of resource (memory, disk, etc.)
            required_amount: Required amount of resource
            available_amount: Available amount of resource
            **kwargs: Additional arguments passed to base class
        """
        super().__init__(message, **kwargs)

        # Add resource-specific context
        if resource_type:
            self.context["resource_type"] = resource_type
        if required_amount is not None:
            self.context["required_amount"] = required_amount
        if available_amount is not None:
            self.context["available_amount"] = available_amount

        # Add default suggestions if not provided
        if not self.suggestions:
            suggestions = [
                "Free up system resources",
                "Close other applications",
                "Use more powerful hardware"
            ]

            if resource_type == "memory":
                suggestions.extend([
                    "Reduce batch size",
                    "Use model streaming",
                    "Increase system memory or swap space"
                ])
            elif resource_type == "disk":
                suggestions.extend([
                    "Clean up temporary files",
                    "Free up disk space",
                    "Use different output location"
                ])

            self.suggestions = suggestions