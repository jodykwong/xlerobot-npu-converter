"""
NPU Converter Utilities

This package contains utility modules for error handling, logging, and analysis.
"""

from .logger import StructuredLogger, get_logger, setup_logging
from .exceptions import (
    ConverterException,
    ConverterErrorCodes,
    ModelLoadError,
    ModelValidationError,
    ModelConversionError,
    ConfigurationError,
    ToolchainError,
    CompilationError,
    FileFormatError,
    HardwareCompatibilityError,
    create_error_context,
    handle_exception
)
from .error_analyzer import ErrorAnalyzer, AnalysisResult, Solution, ErrorSeverity, ErrorCategory
from .knowledge_base import ErrorKnowledgeBase, ErrorEntry, SolutionType
from .error_handler import (
    IntegratedErrorHandler,
    get_error_handler,
    error_handler,
    safe_execute,
    log_function_call,
    create_error_report,
    log_error,
    log_warning,
    log_info,
    log_debug
)

__all__ = [
    # Logger
    "StructuredLogger",
    "get_logger",
    "setup_logging",

    # Exceptions
    "ConverterException",
    "ConverterErrorCodes",
    "ModelLoadError",
    "ModelValidationError",
    "ModelConversionError",
    "ConfigurationError",
    "ToolchainError",
    "CompilationError",
    "FileFormatError",
    "HardwareCompatibilityError",
    "create_error_context",
    "handle_exception",

    # Error Analysis
    "ErrorAnalyzer",
    "AnalysisResult",
    "Solution",
    "ErrorSeverity",
    "ErrorCategory",

    # Knowledge Base
    "ErrorKnowledgeBase",
    "ErrorEntry",
    "SolutionType",

    # Error Handler
    "IntegratedErrorHandler",
    "get_error_handler",
    "error_handler",
    "safe_execute",
    "log_function_call",
    "create_error_report",
    "log_error",
    "log_warning",
    "log_info",
    "log_debug",
]