"""
Conversion Logger

This module defines the comprehensive logging system for conversion flows.
It extends Story 1.3's logging framework to provide conversion-specific
logging capabilities, audit trails, and structured output.

Key Features:
- Enhanced logging with conversion-specific log levels
- Complete audit trail for conversion processes
- Structured logging output and filtering
- Integration with Story 1.3 logging framework
- Performance metrics and timing information
"""

from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import logging
import json
import copy
import threading
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import traceback

logger = logging.getLogger(__name__)


class ConversionLogLevel(Enum):
    """Conversion-specific log levels."""

    TRACE = "TRACE"       # Detailed execution tracing
    DEBUG = "DEBUG"       # Debug information
    INFO = "INFO"         # General information
    WARN = "WARN"         # Warning messages
    ERROR = "ERROR"       # Error messages
    CRITICAL = "CRITICAL" # Critical errors
    AUDIT = "AUDIT"       # Audit trail entries
    PERFORMANCE = "PERF"  # Performance metrics


@dataclass
class LogEntry:
    """Structured log entry for conversion logging."""

    timestamp: datetime
    level: ConversionLogLevel
    operation_id: str
    stage: Optional[str] = None
    message: str = ""
    details: Dict[str, Any] = None
    duration_ms: Optional[float] = None
    error_type: Optional[str] = None
    error_traceback: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.details is None:
            self.details = {}
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary for serialization."""
        data = asdict(self)
        data["timestamp"] = data["timestamp"].isoformat()
        data["level"] = data["level"].value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LogEntry":
        """Create log entry from dictionary."""
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        data["level"] = ConversionLogLevel(data["level"])
        return cls(**data)


@dataclass
class StageMetrics:
    """Metrics for a conversion stage."""

    stage_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    success: bool = False
    error_message: Optional[str] = None
    input_size_mb: Optional[float] = None
    output_size_mb: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    custom_metrics: Dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.custom_metrics is None:
            self.custom_metrics = {}

    @property
    def is_completed(self) -> bool:
        """Check if stage has completed."""
        return self.end_time is not None

    def complete(self, success: bool = True, error_message: Optional[str] = None) -> None:
        """Mark stage as completed."""
        self.end_time = datetime.now()
        self.duration_ms = (self.end_time - self.start_time).total_seconds() * 1000.0
        self.success = success
        if error_message:
            self.error_message = error_message

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        data = asdict(self)
        data["start_time"] = data["start_time"].isoformat()
        if data["end_time"]:
            data["end_time"] = data["end_time"].isoformat()
        return data


class ConversionLogger:
    """
    Comprehensive logging system for conversion flows.

    This class provides enhanced logging capabilities specifically designed for
    model conversion processes, including audit trails, performance metrics,
    and structured output.
    """

    def __init__(
        self,
        operation_id: str,
        log_level: str = "INFO",
        enable_file_logging: bool = True,
        enable_console_logging: bool = True,
        log_directory: Optional[Path] = None
    ) -> None:
        """
        Initialize conversion logger.

        Args:
            operation_id: Unique identifier for the conversion operation
            log_level: Minimum log level to record
            enable_file_logging: Whether to enable file-based logging
            enable_console_logging: Whether to enable console logging
            log_directory: Directory for log files (defaults to "logs/conversions")
        """
        self.operation_id = operation_id
        self.log_level = ConversionLogLevel(log_level.upper())
        self.enable_file_logging = enable_file_logging
        self.enable_console_logging = enable_console_logging

        # Set default log directory
        if log_directory:
            self.log_directory = log_directory
        else:
            self.log_directory = Path("logs") / "conversions" / operation_id

        # Logging state
        self._log_entries: List[LogEntry] = []
        self._stage_metrics: Dict[str, StageMetrics] = {}
        self._lock = threading.Lock()

        # Standard logger for compatibility
        self._logger = logging.getLogger(f"conversion.{operation_id}")

        # Initialize logging infrastructure
        self._setup_logging()

        logger.info(f"Initialized ConversionLogger for {operation_id}")

    def _setup_logging(self) -> None:
        """Set up logging infrastructure."""
        # Create log directory if needed
        if self.enable_file_logging:
            self.log_directory.mkdir(parents=True, exist_ok=True)

            # Configure file handler for this operation
            log_file = self.log_directory / f"{self.operation_id}.log"
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)

            # Create formatter
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(formatter)

            self._logger.addHandler(file_handler)

        # Configure console logging if enabled
        if self.enable_console_logging:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(getattr(logging, self.log_level.value))
            console_handler.setFormatter(formatter)
            self._logger.addHandler(console_handler)

        # Set logger level
        self._logger.setLevel(getattr(logging, self.log_level.value))

    def _should_log(self, level: ConversionLogLevel) -> bool:
        """Check if a log level should be recorded."""
        level_priorities = {
            ConversionLogLevel.TRACE: 0,
            ConversionLogLevel.DEBUG: 10,
            ConversionLogLevel.INFO: 20,
            ConversionLogLevel.WARN: 30,
            ConversionLogLevel.ERROR: 40,
            ConversionLogLevel.CRITICAL: 50,
            ConversionLogLevel.AUDIT: 25,
            ConversionLogLevel.PERFORMANCE: 15,
        }

        return level_priorities.get(level, 0) >= level_priorities.get(self.log_level, 0)

    def _add_log_entry(
        self,
        level: ConversionLogLevel,
        message: str,
        stage: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[float] = None,
        error: Optional[Exception] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a log entry to the logger."""
        if not self._should_log(level):
            return

        entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            operation_id=self.operation_id,
            stage=stage,
            message=message,
            details=details or {},
            duration_ms=duration_ms,
            error_type=type(error).__name__ if error else None,
            error_traceback=traceback.format_exc() if error else None,
            metadata=metadata or {}
        )

        with self._lock:
            self._log_entries.append(entry)

        # Log to standard logger
        log_message = f"[{stage}] {message}" if stage else message
        if details:
            log_message += f" | Details: {json.dumps(details, default=str)}"
        if duration_ms is not None:
            log_message += f" | Duration: {duration_ms:.2f}ms"

        if level == ConversionLogLevel.TRACE:
            self._logger.debug(f"TRACE: {log_message}")
        elif level == ConversionLogLevel.DEBUG:
            self._logger.debug(log_message)
        elif level == ConversionLogLevel.INFO:
            self._logger.info(log_message)
        elif level == ConversionLogLevel.WARN:
            self._logger.warning(log_message)
        elif level == ConversionLogLevel.ERROR:
            self._logger.error(log_message)
        elif level == ConversionLogLevel.CRITICAL:
            self._logger.critical(log_message)
        elif level == ConversionLogLevel.AUDIT:
            self._logger.info(f"AUDIT: {log_message}")
        elif level == ConversionLogLevel.PERFORMANCE:
            self._logger.info(f"PERF: {log_message}")

    def trace(
        self,
        message: str,
        stage: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log a trace message."""
        self._add_log_entry(ConversionLogLevel.TRACE, message, stage, details)

    def debug(
        self,
        message: str,
        stage: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log a debug message."""
        self._add_log_entry(ConversionLogLevel.DEBUG, message, stage, details)

    def info(
        self,
        message: str,
        stage: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log an info message."""
        self._add_log_entry(ConversionLogLevel.INFO, message, stage, details)

    def warning(
        self,
        message: str,
        stage: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log a warning message."""
        self._add_log_entry(ConversionLogLevel.WARN, message, stage, details)

    def error(
        self,
        message: str,
        stage: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None
    ) -> None:
        """Log an error message."""
        self._add_log_entry(ConversionLogLevel.ERROR, message, stage, details, error=error)

    def critical(
        self,
        message: str,
        stage: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None
    ) -> None:
        """Log a critical message."""
        self._add_log_entry(ConversionLogLevel.CRITICAL, message, stage, details, error=error)

    def audit(
        self,
        message: str,
        stage: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log an audit trail entry."""
        self._add_log_entry(ConversionLogLevel.AUDIT, message, stage, details)

    def performance(
        self,
        message: str,
        stage: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[float] = None
    ) -> None:
        """Log a performance metric."""
        self._add_log_entry(ConversionLogLevel.PERFORMANCE, message, stage, details, duration_ms)

    def log_stage_start(self, stage_name: str, metadata: Dict[str, Any]) -> None:
        """Log the start of a conversion stage."""
        self.audit(f"Stage started: {stage_name}", stage_name, metadata)

        # Initialize stage metrics
        with self._lock:
            self._stage_metrics[stage_name] = StageMetrics(
                stage_name=stage_name,
                start_time=datetime.now()
            )

    def log_stage_progress(
        self,
        stage_name: str,
        progress: float,
        details: str
    ) -> None:
        """Log progress for a conversion stage."""
        self.info(f"Stage progress: {progress:.1f}% - {details}", stage_name, {"progress": progress})

    def log_stage_completion(
        self,
        stage_name: str,
        duration: float,
        result: Any
    ) -> None:
        """Log the completion of a conversion stage."""
        self.audit(
            f"Stage completed: {stage_name} in {duration:.2f}s",
            stage_name,
            {
                "duration_seconds": duration,
                "result_type": type(result).__name__
            }
        )

        # Update stage metrics
        with self._lock:
            if stage_name in self._stage_metrics:
                self._stage_metrics[stage_name].complete(success=True)

    def log_error(self, stage: str, error: Exception, context: Dict[str, Any]) -> None:
        """Log an error that occurred during a stage."""
        self.error(
            f"Error in stage {stage}: {str(error)}",
            stage,
            context,
            error
        )

        # Update stage metrics
        with self._lock:
            if stage in self._stage_metrics:
                self._stage_metrics[stage].complete(success=False, error_message=str(error))

    def get_log_entries(
        self,
        level: Optional[ConversionLogLevel] = None,
        stage: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[LogEntry]:
        """
        Get log entries with optional filtering.

        Args:
            level: Filter by log level (None for all)
            stage: Filter by stage name (None for all)
            limit: Maximum number of entries to return

        Returns:
            List[LogEntry]: Filtered log entries
        """
        with self._lock:
            entries = self._log_entries

            # Apply filters
            if level:
                entries = [e for e in entries if e.level == level]
            if stage:
                entries = [e for e in entries if e.stage == stage]

            # Apply limit
            if limit:
                entries = entries[-limit:]

            return entries.copy()

    def get_stage_metrics(self, stage_name: Optional[str] = None) -> Union[StageMetrics, Dict[str, StageMetrics]]:
        """
        Get metrics for stages.

        Args:
            stage_name: Specific stage name (None for all stages)

        Returns:
            Union[StageMetrics, Dict[str, StageMetrics]]: Stage metrics
        """
        with self._lock:
            if stage_name:
                return copy.deepcopy(self._stage_metrics.get(stage_name))
            else:
                return copy.deepcopy(self._stage_metrics)

    def export_audit_log(self, output_path: Path) -> None:
        """
        Export the complete audit log to a file.

        Args:
            output_path: Path where audit log should be saved
        """
        audit_entries = self.get_log_entries(level=ConversionLogLevel.AUDIT)

        audit_data = {
            "operation_id": self.operation_id,
            "export_timestamp": datetime.now().isoformat(),
            "total_entries": len(audit_entries),
            "entries": [entry.to_dict() for entry in audit_entries],
            "stage_metrics": {name: metrics.to_dict() for name, metrics in self._stage_metrics.items()}
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(audit_data, f, indent=2, default=str)

        self.info(f"Exported audit log with {len(audit_entries)} entries to {output_path}")

    def export_structured_log(
        self,
        output_path: Path,
        format: str = "json",
        include_performance: bool = True
    ) -> None:
        """
        Export structured log data in various formats.

        Args:
            output_path: Path where log data should be saved
            format: Export format ("json", "csv", "txt")
            include_performance: Whether to include performance data
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format.lower() == "json":
            self._export_json_log(output_path, include_performance)
        elif format.lower() == "csv":
            self._export_csv_log(output_path)
        elif format.lower() == "txt":
            self._export_text_log(output_path)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _export_json_log(self, output_path: Path, include_performance: bool) -> None:
        """Export log in JSON format."""
        log_data = {
            "operation_id": self.operation_id,
            "export_timestamp": datetime.now().isoformat(),
            "log_entries": [entry.to_dict() for entry in self._log_entries]
        }

        if include_performance:
            log_data["stage_metrics"] = {name: metrics.to_dict() for name, metrics in self._stage_metrics.items()}

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2, default=str)

    def _export_csv_log(self, output_path: Path) -> None:
        """Export log in CSV format."""
        import csv

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "level", "stage", "message", "duration_ms",
                "error_type", "details_json"
            ])

            for entry in self._log_entries:
                writer.writerow([
                    entry.timestamp.isoformat(),
                    entry.level.value,
                    entry.stage or "",
                    entry.message,
                    entry.duration_ms or "",
                    entry.error_type or "",
                    json.dumps(entry.details) if entry.details else ""
                ])

    def _export_text_log(self, output_path: Path) -> None:
        """Export log in human-readable text format."""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"Conversion Log: {self.operation_id}\n")
            f.write(f"Exported: {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n\n")

            for entry in self._log_entries:
                f.write(f"[{entry.timestamp.isoformat()}] {entry.level.value}")
                if entry.stage:
                    f.write(f" [{entry.stage}]")
                f.write(f": {entry.message}\n")

                if entry.details:
                    f.write(f"  Details: {json.dumps(entry.details, indent=2)}\n")

                if entry.duration_ms is not None:
                    f.write(f"  Duration: {entry.duration_ms:.2f}ms\n")

                if entry.error_traceback:
                    f.write(f"  Error Traceback:\n{entry.error_traceback}\n")

                f.write("\n")

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the logging session.

        Returns:
            Dict[str, Any]: Logging summary
        """
        with self._lock:
            level_counts = {}
            for entry in self._log_entries:
                level = entry.level.value
                level_counts[level] = level_counts.get(level, 0) + 1

            completed_stages = sum(1 for m in self._stage_metrics.values() if m.is_completed and m.success)
            failed_stages = sum(1 for m in self._stage_metrics.values() if m.is_completed and not m.success)
            total_stages = len(self._stage_metrics)

            return {
                "operation_id": self.operation_id,
                "total_log_entries": len(self._log_entries),
                "log_level_counts": level_counts,
                "total_stages": total_stages,
                "completed_stages": completed_stages,
                "failed_stages": failed_stages,
                "log_directory": str(self.log_directory),
                "file_logging_enabled": self.enable_file_logging,
                "console_logging_enabled": self.enable_console_logging
            }