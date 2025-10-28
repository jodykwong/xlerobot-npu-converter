"""
Custom Exception System for NPU Converter

Provides hierarchical exception classes with error codes and contextual information.
Supports exception chaining and detailed error reporting.
"""

from typing import Any, Dict, Optional, List
from dataclasses import dataclass, asdict
import traceback


class ConverterErrorCodes:
    """Centralized error code definitions for the NPU converter."""

    # General errors (E0000-E0999)
    UNKNOWN_ERROR = "E0000"
    INITIALIZATION_ERROR = "E0001"
    CONFIGURATION_ERROR = "E0002"
    VALIDATION_ERROR = "E0003"

    # File system errors (E1000-E1999)
    FILE_NOT_FOUND = "E1000"
    FILE_PERMISSION_ERROR = "E1001"
    FILE_FORMAT_ERROR = "E1002"
    DISK_SPACE_ERROR = "E1003"

    # Model conversion errors (E2000-E2999)
    MODEL_LOAD_ERROR = "E2000"
    MODEL_VALIDATION_ERROR = "E2001"
    MODEL_CONVERSION_ERROR = "E2002"
    OPTIMIZATION_ERROR = "E2003"

    # NPU/BPU toolchain errors (E3000-E3999)
    TOOLCHAIN_ERROR = "E3000"
    COMPILATION_ERROR = "E3001"
    DEPLOYMENT_ERROR = "E3002"
    HARDWARE_COMPATIBILITY_ERROR = "E3003"

    # Performance errors (E4000-E4999)
    MEMORY_ERROR = "E4000"
    TIMEOUT_ERROR = "E4001"
    RESOURCE_LIMIT_ERROR = "E4002"


@dataclass
class ErrorContext:
    """Context information for error reporting."""
    component: str
    operation: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    additional_data: Optional[Dict[str, Any]] = None


class ConverterException(Exception):
    """
    Base exception class for NPU converter errors.

    Implements interface specified in story-context-1.7.xml:
    - def __init__(self, message: str, error_code: str, context: Dict[str, Any] = None)
    - def to_dict(self) -> Dict[str, Any]
    """

    def __init__(
        self,
        message: str,
        error_code: str = ConverterErrorCodes.UNKNOWN_ERROR,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize converter exception.

        Args:
            message: Error message
            error_code: Error code from ConverterErrorCodes
            context: Additional context information
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.timestamp = None
        self.stack_trace = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for serialization."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "context": self.context,
            "timestamp": self.timestamp,
            "stack_trace": self.stack_trace
        }

    def with_context(self, **kwargs) -> 'ConverterException':
        """Add additional context to the exception."""
        self.context.update(kwargs)
        return self

    def capture_stack_trace(self):
        """Capture current stack trace."""
        self.stack_trace = traceback.format_exc()


class ModelLoadError(ConverterException):
    """Exception raised when model loading fails."""

    def __init__(self, message: str, model_path: Optional[str] = None, **context):
        context_with_path = {"model_path": model_path, **context}
        super().__init__(
            message,
            ConverterErrorCodes.MODEL_LOAD_ERROR,
            context_with_path
        )


class ModelValidationError(ConverterException):
    """Exception raised when model validation fails."""

    def __init__(self, message: str, validation_errors: Optional[List[str]] = None, **context):
        context_with_errors = {"validation_errors": validation_errors or [], **context}
        super().__init__(
            message,
            ConverterErrorCodes.MODEL_VALIDATION_ERROR,
            context_with_errors
        )


class ModelConversionError(ConverterException):
    """Exception raised when model conversion fails."""

    def __init__(self, message: str, stage: Optional[str] = None, **context):
        context_with_stage = {"conversion_stage": stage, **context}
        super().__init__(
            message,
            ConverterErrorCodes.MODEL_CONVERSION_ERROR,
            context_with_stage
        )


class ConfigurationError(ConverterException):
    """Exception raised when configuration is invalid."""

    def __init__(self, message: str, config_key: Optional[str] = None, **context):
        context_with_key = {"config_key": config_key, **context}
        super().__init__(
            message,
            ConverterErrorCodes.CONFIGURATION_ERROR,
            context_with_key
        )


class ToolchainError(ConverterException):
    """Exception raised when NPU/BPU toolchain operations fail."""

    def __init__(self, message: str, toolchain_version: Optional[str] = None, **context):
        context_with_version = {"toolchain_version": toolchain_version, **context}
        super().__init__(
            message,
            ConverterErrorCodes.TOOLCHAIN_ERROR,
            context_with_version
        )


class CompilationError(ConverterException):
    """Exception raised during model compilation."""

    def __init__(self, message: str, compilation_stage: Optional[str] = None, **context):
        context_with_stage = {"compilation_stage": compilation_stage, **context}
        super().__init__(
            message,
            ConverterErrorCodes.COMPILATION_ERROR,
            context_with_stage
        )


class FileFormatError(ConverterException):
    """Exception raised when file format is invalid or unsupported."""

    def __init__(self, message: str, file_type: Optional[str] = None, **context):
        context_with_type = {"file_type": file_type, **context}
        super().__init__(
            message,
            ConverterErrorCodes.FILE_FORMAT_ERROR,
            context_with_type
        )


class HardwareCompatibilityError(ConverterException):
    """Exception raised when hardware compatibility issues occur."""

    def __init__(self, message: str, hardware_info: Optional[Dict[str, Any]] = None, **context):
        context_with_info = {"hardware_info": hardware_info or {}, **context}
        super().__init__(
            message,
            ConverterErrorCodes.HARDWARE_COMPATIBILITY_ERROR,
            context_with_info
        )


def create_error_context(
    component: str,
    operation: Optional[str] = None,
    file_path: Optional[str] = None,
    line_number: Optional[int] = None,
    **additional_data
) -> ErrorContext:
    """Create error context object."""
    return ErrorContext(
        component=component,
        operation=operation,
        file_path=file_path,
        line_number=line_number,
        additional_data=additional_data if additional_data else None
    )


def handle_exception(
    exception: Exception,
    default_error_code: str = ConverterErrorCodes.UNKNOWN_ERROR,
    context: Optional[Dict[str, Any]] = None
) -> ConverterException:
    """
    Convert any exception to ConverterException with proper context.

    Args:
        exception: Original exception
        default_error_code: Default error code if not a ConverterException
        context: Additional context to add

    Returns:
        ConverterException with captured information
    """
    if isinstance(exception, ConverterException):
        converter_exception = exception
    else:
        converter_exception = ConverterException(
            str(exception),
            default_error_code,
            original_type=exception.__class__.__name__,
            context=context or {}
        )

    converter_exception.capture_stack_trace()
    if context:
        converter_exception.with_context(**context)

    return converter_exception