"""
Exception Handling Utilities and Decorators

This module provides utilities, decorators, and context managers for standardized
exception handling throughout the NPU converter system. These tools help ensure
consistent error handling, logging, and error recovery patterns.

Key Features:
- Exception handling decorators
- Context managers for common operations
- Error logging and reporting utilities
- Error recovery and retry mechanisms
- Standardized error response formatting
"""

import logging
import time
import traceback
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, Union
from contextlib import contextmanager
from pathlib import Path

from .conversion_errors import (
    ConversionError,
    ValidationError,
    ConversionTimeoutError,
    ResourceError
)
from .config_errors import (
    ConfigError,
    ConfigLoadError,
    ConfigValidationError
)

logger = logging.getLogger(__name__)


class ErrorContext:
    """Context for error handling operations."""

    def __init__(
        self,
        operation_name: str,
        component: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize error context.

        Args:
            operation_name: Name of the operation
            component: Component name (e.g., converter, quantizer)
            additional_context: Additional context information
        """
        self.operation_name = operation_name
        self.component = component
        self.additional_context = additional_context or {}
        self.start_time = None
        self.error_count = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {
            "operation_name": self.operation_name,
            "component": self.component,
            "additional_context": self.additional_context,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "error_count": self.error_count
        }


def handle_conversion_errors(
    operation_name: Optional[str] = None,
    component: str = "unknown",
    reraise: bool = True,
    default_return: Any = None,
    log_errors: bool = True,
    include_traceback: bool = False
) -> Callable:
    """
    Decorator for handling conversion errors consistently.

    Args:
        operation_name: Name of the operation for error reporting
        component: Component name for error context
        reraise: Whether to reraise exceptions after handling
        default_return: Default return value if exception is suppressed
        log_errors: Whether to log errors
        include_traceback: Whether to include traceback in logs

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            op_name = operation_name or f"{func.__name__}"
            error_context = ErrorContext(op_name, component)
            error_context.start_time = time.time()

            try:
                return func(*args, **kwargs)

            except ConversionError as e:
                error_context.error_count += 1

                # Add operation context to exception
                e.context.update(error_context.to_dict())

                if log_errors:
                    error_msg = f"Conversion error in {op_name}: {e.message}"
                    if include_traceback:
                        error_msg += f"\nTraceback: {traceback.format_exc()}"
                    logger.error(error_msg)

                if reraise:
                    raise
                return default_return

            except Exception as e:
                error_context.error_count += 1

                # Wrap non-conversion errors
                conversion_error = ConversionError(
                    message=f"Unexpected error in {op_name}: {str(e)}",
                    error_code="UNEXPECTED_ERROR",
                    context=error_context.to_dict(),
                    cause=e
                )

                if log_errors:
                    error_msg = f"Unexpected error in {op_name}: {str(e)}"
                    if include_traceback:
                        error_msg += f"\nTraceback: {traceback.format_exc()}"
                    logger.error(error_msg)

                if reraise:
                    raise conversion_error from e
                return default_return

        return wrapper
    return decorator


def handle_config_errors(
    config_path: Optional[Path] = None,
    component: str = "config_loader",
    reraise: bool = True,
    default_return: Any = None
) -> Callable:
    """
    Decorator for handling configuration errors consistently.

    Args:
        config_path: Path to configuration file
        component: Component name for error context
        reraise: Whether to reraise exceptions after handling
        default_return: Default return value if exception is suppressed

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)

            except ConfigError as e:
                # Add config path to context if available
                if config_path:
                    e.context["config_path"] = str(config_path)

                logger.error(f"Configuration error in {component}: {e.message}")

                if reraise:
                    raise
                return default_return

            except FileNotFoundError as e:
                config_error = ConfigLoadError(
                    message=f"Configuration file not found: {str(e)}",
                    config_path=config_path
                )
                logger.error(f"Configuration file not found: {e}")

                if reraise:
                    raise config_error from e
                return default_return

            except Exception as e:
                config_error = ConfigError(
                    message=f"Unexpected configuration error: {str(e)}",
                    config_path=config_path,
                    cause=e
                )
                logger.error(f"Unexpected configuration error: {e}")

                if reraise:
                    raise config_error from e
                return default_return

        return wrapper
    return decorator


def retry_on_error(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    retry_on: Optional[List[Type[Exception]]] = None,
    component: str = "retry_handler"
) -> Callable:
    """
    Decorator for retrying operations on specific errors.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff_factor: Multiplier for delay after each retry
        retry_on: List of exception types to retry on
        component: Component name for logging

    Returns:
        Decorator function
    """
    if retry_on is None:
        retry_on = [ResourceError, ConversionTimeoutError]

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except Exception as e:
                    last_exception = e

                    # Check if this exception type should be retried
                    if not any(isinstance(e, retry_type) for retry_type in retry_on):
                        if attempt == 0:  # Don't log if it's not a retryable error
                            raise
                        break

                    if attempt < max_retries:
                        logger.warning(
                            f"{component}: Attempt {attempt + 1} failed with {type(e).__name__}: {e}. "
                            f"Retrying in {current_delay:.2f}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        logger.error(
                            f"{component}: All {max_retries + 1} attempts failed. "
                            f"Last error: {type(e).__name__}: {e}"
                        )

            # Raise the last exception if all retries failed
            raise last_exception

        return wrapper
    return decorator


def timeout_handler(
    timeout_seconds: float,
    component: str = "timeout_handler"
) -> Callable:
    """
    Decorator for adding timeout protection to functions.

    Args:
        timeout_seconds: Timeout duration in seconds
        component: Component name for error reporting

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            import signal

            def timeout_handler_fn(signum, frame):
                raise ConversionTimeoutError(
                    message=f"Operation {func.__name__} timed out after {timeout_seconds} seconds",
                    timeout_duration=timeout_seconds,
                    operation=func.__name__,
                    component=component
                )

            # Set the signal handler
            original_handler = signal.signal(signal.SIGALRM, timeout_handler_fn)
            signal.alarm(int(timeout_seconds))

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # Restore the original signal handler
                signal.alarm(0)  # Cancel the alarm
                signal.signal(signal.SIGALRM, original_handler)

        return wrapper
    return decorator


@contextmanager
def error_context(
    operation_name: str,
    component: str,
    log_entry: bool = True,
    log_exit: bool = True,
    log_errors: bool = True
) -> Any:
    """
    Context manager for standardized error handling.

    Args:
        operation_name: Name of the operation
        component: Component name
        log_entry: Whether to log operation entry
        log_exit: Whether to log operation exit
        log_errors: Whether to log errors

    Yields:
        ErrorContext instance
    """
    context = ErrorContext(operation_name, component)

    if log_entry:
        logger.info(f"Starting operation '{operation_name}' in component '{component}'")

    try:
        yield context

        if log_exit:
            logger.info(f"Completed operation '{operation_name}' in component '{component}'")

    except ConversionError as e:
        context.error_count += 1
        e.context.update(context.to_dict())

        if log_errors:
            logger.error(f"Conversion error in '{operation_name}': {e.message}")

        raise

    except Exception as e:
        context.error_count += 1
        conversion_error = ConversionError(
            message=f"Unexpected error in '{operation_name}': {str(e)}",
            error_code="UNEXPECTED_ERROR",
            context=context.to_dict(),
            cause=e
        )

        if log_errors:
            logger.error(f"Unexpected error in '{operation_name}': {str(e)}")

        raise conversion_error from e


def validate_parameters(
    validation_rules: Dict[str, Dict[str, Any]],
    component: str = "validator"
) -> Callable:
    """
    Decorator for parameter validation.

    Args:
        validation_rules: Dictionary of parameter validation rules
        component: Component name for error reporting

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Get function signature for parameter mapping
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Validate parameters
            for param_name, rules in validation_rules.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]

                    # Type validation
                    if "type" in rules and not isinstance(value, rules["type"]):
                        raise ValidationError(
                            message=f"Parameter '{param_name}' must be of type {rules['type'].__name__}",
                            validation_field=param_name,
                            validation_value=value,
                            expected_value=rules["type"].__name__
                        )

                    # Range validation for numbers
                    if isinstance(value, (int, float)):
                        if "min_value" in rules and value < rules["min_value"]:
                            raise ValidationError(
                                message=f"Parameter '{param_name}' must be >= {rules['min_value']}",
                                validation_field=param_name,
                                validation_value=value,
                                expected_value=f">= {rules['min_value']}"
                            )
                        if "max_value" in rules and value > rules["max_value"]:
                            raise ValidationError(
                                message=f"Parameter '{param_name}' must be <= {rules['max_value']}",
                                validation_field=param_name,
                                validation_value=value,
                                expected_value=f"<= {rules['max_value']}"
                            )

                    # Choice validation
                    if "choices" in rules and value not in rules["choices"]:
                        raise ValidationError(
                            message=f"Parameter '{param_name}' must be one of {rules['choices']}",
                            validation_field=param_name,
                            validation_value=value,
                            expected_value=rules["choices"]
                        )

                    # Custom validation
                    if "validator" in rules:
                        try:
                            if not rules["validator"](value):
                                raise ValidationError(
                                    message=f"Parameter '{param_name}' failed custom validation",
                                    validation_field=param_name,
                                    validation_value=value
                                )
                        except Exception as e:
                            raise ValidationError(
                                message=f"Custom validation failed for '{param_name}': {str(e)}",
                                validation_field=param_name,
                                validation_value=value
                            ) from e

            return func(*args, **kwargs)

        return wrapper
    return decorator


class ErrorReporter:
    """Utility class for reporting and formatting errors."""

    @staticmethod
    def format_error_for_user(error: Exception, include_suggestions: bool = True) -> str:
        """
        Format an error for user display.

        Args:
            error: Exception to format
            include_suggestions: Whether to include suggestions

        Returns:
            Formatted error message
        """
        if isinstance(error, ConversionError):
            result = f"Error: {error.message}"

            if error.error_code:
                result += f"\nError Code: {error.error_code}"

            if include_suggestions and error.suggestions:
                result += "\n\nSuggested Solutions:"
                for i, suggestion in enumerate(error.suggestions, 1):
                    result += f"\n{i}. {suggestion}"

            return result
        else:
            return f"Error: {str(error)}"

    @staticmethod
    def format_error_for_debug(error: Exception) -> str:
        """
        Format an error for debugging purposes.

        Args:
            error: Exception to format

        Returns:
            Detailed error information
        """
        result = f"Exception Type: {type(error).__name__}\n"
        result += f"Message: {str(error)}\n"
        result += f"Traceback:\n{traceback.format_exc()}"

        if isinstance(error, ConversionError):
            result += f"\nError Code: {error.error_code}"
            result += f"\nContext: {error.context}"
            result += f"\nTimestamp: {error.timestamp}"

        return result

    @staticmethod
    def create_error_report(
        errors: List[Exception],
        operation_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a comprehensive error report.

        Args:
            errors: List of errors to include in the report
            operation_context: Context information about the operation

        Returns:
            Error report dictionary
        """
        report = {
            "error_summary": {
                "total_errors": len(errors),
                "error_types": list(set(type(e).__name__ for e in errors)),
                "timestamp": time.time()
            },
            "operation_context": operation_context or {},
            "errors": []
        }

        for error in errors:
            if isinstance(error, ConversionError):
                error_data = error.to_dict()
            else:
                error_data = {
                    "error_type": type(error).__name__,
                    "message": str(error),
                    "traceback": traceback.format_exc()
                }
            report["errors"].append(error_data)

        return report