"""
Structured Logging System

Provides hierarchical logging with structured output for the NPU converter tool.
Supports DEBUG, INFO, WARN, ERROR levels with contextual information.
"""

import logging
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, asdict


@dataclass
class LogEntry:
    """Structured log entry with context information."""
    timestamp: str
    level: str
    message: str
    logger_name: str
    context: Dict[str, Any]
    exception: Optional[str] = None


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured log output."""

    def __init__(self, include_context: bool = True):
        super().__init__()
        self.include_context = include_context

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON or human-readable text."""
        log_entry = LogEntry(
            timestamp=datetime.fromtimestamp(record.created).isoformat(),
            level=record.levelname,
            message=record.getMessage(),
            logger_name=record.name,
            context=getattr(record, 'context', {}),
            exception=self._format_exception(record) if record.exc_info else None
        )

        if self.include_context and log_entry.context:
            return json.dumps(asdict(log_entry), ensure_ascii=False, indent=None)
        else:
            # Human-readable format for console output
            return f"{log_entry.timestamp} [{log_entry.level}] {log_entry.logger_name}: {log_entry.message}"

    def _format_exception(self, record: logging.LogRecord) -> Optional[str]:
        """Format exception information."""
        if record.exc_info:
            return logging.Formatter().formatException(record.exc_info)
        return None


class StructuredLogger:
    """
    Structured logger with support for multiple output modes and contextual information.

    Implements interface specified in story-context-1.7.xml:
    - def __init__(self, name: str, level: str = "INFO")
    - def debug(self, message: str, **context)
    - def info(self, message: str, **context)
    - def warning(self, message: str, **context)
    - def error(self, message: str, exception: Exception = None, **context)
    """

    def __init__(self, name: str, level: str = "INFO"):
        """
        Initialize structured logger.

        Args:
            name: Logger name
            level: Logging level (DEBUG, INFO, WARN, ERROR)
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))

        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()

    def _setup_handlers(self):
        """Setup console and file handlers with appropriate formatters."""
        # Console handler with human-readable format
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_formatter = StructuredFormatter(include_context=False)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File handler with structured JSON format
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        log_file_path = log_dir / f"{self.name}.log"

        file_handler = logging.FileHandler(
            log_file_path,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = StructuredFormatter(include_context=True)
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

    def _log_with_context(self, level: int, message: str, exception: Optional[Exception] = None, **context):
        """Log message with contextual information."""
        extra = {'context': context}
        if exception:
            self.logger.log(level, message, exc_info=(type(exception), exception, exception.__traceback__), extra=extra)
        else:
            self.logger.log(level, message, extra=extra)

    def debug(self, message: str, **context):
        """Log debug message with context."""
        self._log_with_context(logging.DEBUG, message, **context)

    def info(self, message: str, **context):
        """Log info message with context."""
        self._log_with_context(logging.INFO, message, **context)

    def warning(self, message: str, **context):
        """Log warning message with context."""
        self._log_with_context(logging.WARNING, message, **context)

    def error(self, message: str, exception: Optional[Exception] = None, **context):
        """Log error message with optional exception and context."""
        self._log_with_context(logging.ERROR, message, exception, **context)

    def set_level(self, level: str):
        """Change logging level."""
        self.logger.setLevel(getattr(logging, level.upper()))

    def add_file_handler(self, file_path: Union[str, Path], level: str = "DEBUG"):
        """Add additional file handler."""
        file_handler = logging.FileHandler(file_path, encoding='utf-8')
        file_handler.setLevel(getattr(logging, level.upper()))
        file_formatter = StructuredFormatter(include_context=True)
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)


# Global logger instance for the NPU converter
_default_logger: Optional[StructuredLogger] = None


def get_logger(name: str = "npu_converter") -> StructuredLogger:
    """Get or create a structured logger instance."""
    global _default_logger
    if _default_logger is None or _default_logger.name != name:
        _default_logger = StructuredLogger(name)
    return _default_logger


def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """Setup global logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            *([logging.FileHandler(log_file, encoding='utf-8')] if log_file else [])
        ]
    )