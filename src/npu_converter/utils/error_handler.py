"""
Integrated Error Handler for NPU Converter

Provides unified error handling, logging, analysis, and suggestion system.
Integrates StructuredLogger, ErrorAnalyzer, and ErrorKnowledgeBase.
"""

import sys
import traceback
from typing import Any, Dict, List, Optional, Callable
from functools import wraps

from .logger import StructuredLogger, get_logger
from .exceptions import ConverterException, handle_exception
from .error_analyzer import ErrorAnalyzer, AnalysisResult, Solution
from .knowledge_base import ErrorKnowledgeBase, SolutionType


class IntegratedErrorHandler:
    """
    Integrated error handling system that combines logging, analysis, and suggestions.

    Provides comprehensive error management for the NPU converter tool.
    """

    def __init__(self, logger_name: str = "npu_converter"):
        """
        Initialize integrated error handler.

        Args:
            logger_name: Name for the structured logger
        """
        self.logger = get_logger(logger_name)
        self.analyzer = ErrorAnalyzer()
        self.knowledge_base = ErrorKnowledgeBase()
        self.error_handlers: Dict[str, Callable] = {}

    def handle_error(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
        show_suggestions: bool = True
    ) -> ConverterException:
        """
        Handle exception with comprehensive analysis and logging.

        Args:
            exception: Exception to handle
            context: Additional context information
            show_suggestions: Whether to show solution suggestions

        Returns:
            ConverterException with full analysis
        """
        # Convert to ConverterException
        converter_exception = handle_exception(exception, context=context)

        # Log the error
        self.logger.error(
            f"Error occurred: {converter_exception.message}",
            exception=exception,
            error_code=converter_exception.error_code,
            context=converter_exception.context,
            **(context or {})
        )

        # Analyze the error
        analysis = self.analyzer.analyze_exception(converter_exception)

        # Log analysis results
        self.logger.info(
            f"Error analysis completed: {analysis.category.value} - {analysis.severity.value}",
            confidence_score=analysis.confidence_score,
            affected_components=analysis.affected_components,
            root_cause=analysis.root_cause
        )

        # Get and show suggestions
        if show_suggestions:
            solutions = self.analyzer.suggest_solutions(analysis)
            self._log_solutions(solutions)

            # Check knowledge base for additional information
            kb_entry = self.knowledge_base.find_entry(converter_exception.error_code)
            if kb_entry:
                self._log_knowledge_base_info(kb_entry)

        return converter_exception

    def _log_solutions(self, solutions: List[Solution]):
        """Log solution suggestions."""
        self.logger.info(f"Found {len(solutions)} solution(s):")
        for i, solution in enumerate(solutions, 1):
            self.logger.info(
                f"Solution {i}: {solution.title} (Success: {solution.success_probability:.0%})"
            )
            for j, step in enumerate(solution.steps, 1):
                self.logger.info(f"  {j}. {step}")

    def _log_knowledge_base_info(self, kb_entry):
        """Log knowledge base information."""
        self.logger.info("Knowledge base information:")
        self.logger.info(f"  Category: {kb_entry.category.value}")
        self.logger.info(f"  Prevention tips: {len(kb_entry.prevention)}")
        for tip in kb_entry.prevention:
            self.logger.info(f"    - {tip}")

    def register_error_handler(self, error_code: str, handler: Callable):
        """Register custom error handler for specific error code."""
        self.error_handlers[error_code] = handler

    def get_error_summary(self, exception: Exception) -> Dict[str, Any]:
        """Get comprehensive error summary."""
        converter_exception = handle_exception(exception)
        analysis = self.analyzer.analyze_exception(converter_exception)
        solutions = self.analyzer.suggest_solutions(analysis)
        kb_entry = self.knowledge_base.find_entry(converter_exception.error_code)

        return {
            "error": {
                "type": converter_exception.__class__.__name__,
                "message": converter_exception.message,
                "code": converter_exception.error_code,
                "context": converter_exception.context
            },
            "analysis": {
                "category": analysis.category.value,
                "severity": analysis.severity.value,
                "root_cause": analysis.root_cause,
                "confidence": analysis.confidence_score,
                "affected_components": analysis.affected_components,
                "related_files": analysis.related_files
            },
            "solutions": [
                {
                    "title": sol.title,
                    "description": sol.description,
                    "automated": sol.automated_fix,
                    "success_probability": sol.success_probability,
                    "steps": sol.steps
                }
                for sol in solutions
            ],
            "knowledge_base": {
                "symptoms": kb_entry.symptoms if kb_entry else [],
                "prevention": kb_entry.prevention if kb_entry else []
            }
        }


# Global error handler instance
_default_error_handler: Optional[IntegratedErrorHandler] = None


def get_error_handler(logger_name: str = "npu_converter") -> IntegratedErrorHandler:
    """Get or create global error handler instance."""
    global _default_error_handler
    if _default_error_handler is None:
        _default_error_handler = IntegratedErrorHandler(logger_name)
    return _default_error_handler


def error_handler(
    error_code: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    show_suggestions: bool = True,
    reraise: bool = False
):
    """
    Decorator for automatic error handling.

    Args:
        error_code: Default error code for exceptions
        context: Additional context to add to errors
        show_suggestions: Whether to show solution suggestions
        reraise: Whether to reraise the exception after handling
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handler = get_error_handler()

                # Add context information
                func_context = {
                    "function": func.__name__,
                    "module": func.__module__,
                    **(context or {})
                }

                # Handle the error
                converter_exception = handler.handle_error(
                    e,
                    context=func_context,
                    show_suggestions=show_suggestions
                )

                if reraise:
                    raise converter_exception

                return None
        return wrapper
    return decorator


def safe_execute(
    func: Callable,
    args: tuple = (),
    kwargs: Optional[Dict[str, Any]] = None,
    default_return: Any = None,
    error_context: Optional[Dict[str, Any]] = None
) -> Any:
    """
    Safely execute a function with error handling.

    Args:
        func: Function to execute
        args: Positional arguments
        kwargs: Keyword arguments
        default_return: Default return value on error
        error_context: Additional context for error handling

    Returns:
        Function result or default_return on error
    """
    try:
        return func(*args, **(kwargs or {}))
    except Exception as e:
        handler = get_error_handler()
        handler.handle_error(e, context=error_context)
        return default_return


def log_function_call(level: str = "DEBUG"):
    """
    Decorator to log function calls.

    Args:
        level: Logging level for the call
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger()
            log_message = f"Calling {func.__name__}"
            if args or kwargs:
                log_message += f" with args={args}, kwargs={kwargs}"

            getattr(logger, level.lower())(log_message)

            try:
                result = func(*args, **kwargs)
                getattr(logger, level.lower())(f"Completed {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"Failed {func.__name__}: {str(e)}")
                raise
        return wrapper
    return decorator


def create_error_report(exception: Exception, output_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Create comprehensive error report.

    Args:
        exception: Exception to analyze
        output_file: Optional file to save report

    Returns:
        Error report dictionary
    """
    handler = get_error_handler()
    report = handler.get_error_summary(exception)

    if output_file:
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

    return report


# Convenience functions for common operations
def log_error(message: str, exception: Optional[Exception] = None, **context):
    """Log error with optional exception."""
    get_logger().error(message, exception=exception, **context)


def log_warning(message: str, **context):
    """Log warning message."""
    get_logger().warning(message, **context)


def log_info(message: str, **context):
    """Log info message."""
    get_logger().info(message, **context)


def log_debug(message: str, **context):
    """Log debug message."""
    get_logger().debug(message, **context)