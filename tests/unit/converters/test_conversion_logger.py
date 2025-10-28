"""
Unit tests for Conversion Logger

This module contains unit tests for the ConversionLogger class,
testing log entry management, file operations, and filtering.
"""

import pytest
import tempfile
import json
import threading
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from npu_converter.converters.conversion_logger import (
    ConversionLogger,
    ConversionLogLevel,
    LogEntry,
    StageMetrics
)


class TestLogEntry:
    """Test cases for LogEntry class."""

    def test_initialization(self):
        """Test LogEntry initialization."""
        timestamp = datetime.now()
        entry = LogEntry(
            timestamp=timestamp,
            level=ConversionLogLevel.INFO,
            operation_id="test_op",
            message="Test message"
        )

        assert entry.timestamp == timestamp
        assert entry.level == ConversionLogLevel.INFO
        assert entry.operation_id == "test_op"
        assert entry.message == "Test message"
        assert entry.stage is None
        assert entry.details == {}
        assert entry.duration_ms is None
        assert entry.error_type is None
        assert entry.error_traceback is None
        assert entry.metadata == {}

    def test_initialization_with_all_fields(self):
        """Test LogEntry initialization with all fields."""
        timestamp = datetime.now()
        entry = LogEntry(
            timestamp=timestamp,
            level=ConversionLogLevel.ERROR,
            operation_id="test_op",
            stage="test_stage",
            message="Error message",
            details={"key": "value"},
            duration_ms=100.5,
            error_type=ValueError,
            error_traceback="Traceback",
            metadata={"meta": "data"}
        )

        assert entry.timestamp == timestamp
        assert entry.level == ConversionLogLevel.ERROR
        assert entry.operation_id == "test_op"
        assert entry.stage == "test_stage"
        assert entry.message == "Error message"
        assert entry.details == {"key": "value"}
        assert entry.duration_ms == 100.5
        assert entry.error_type == ValueError
        assert entry.error_traceback == "Traceback"
        assert entry.metadata == {"meta": "data"}

    def test_to_dict(self):
        """Test converting log entry to dictionary."""
        timestamp = datetime.now()
        entry = LogEntry(
            timestamp=timestamp,
            level=ConversionLogLevel.INFO,
            operation_id="test_op",
            message="Test message",
            details={"key": "value"}
        )

        entry_dict = entry.to_dict()

        assert isinstance(entry_dict, dict)
        assert entry_dict["timestamp"] == timestamp.isoformat()
        assert entry_dict["level"] == "INFO"
        assert entry_dict["operation_id"] == "test_op"
        assert entry_dict["message"] == "Test message"
        assert entry_dict["details"] == {"key": "value"}

    def test_from_dict(self):
        """Test creating log entry from dictionary."""
        timestamp = datetime.now()
        entry_dict = {
            "timestamp": timestamp.isoformat(),
            "level": "INFO",
            "operation_id": "test_op",
            "message": "Test message",
            "stage": "test_stage",
            "details": {"key": "value"},
            "duration_ms": 100.5,
            "error_type": None,
            "error_traceback": None,
            "metadata": {"meta": "data"}
        }

        entry = LogEntry.from_dict(entry_dict)

        assert entry.level == ConversionLogLevel.INFO
        assert entry.operation_id == "test_op"
        assert entry.message == "Test message"
        assert entry.stage == "test_stage"
        assert entry.details == {"key": "value"}
        assert entry.duration_ms == 100.5
        assert entry.metadata == {"meta": "data"}


class TestStageMetrics:
    """Test cases for StageMetrics class."""

    def test_initialization(self):
        """Test StageMetrics initialization."""
        start_time = datetime.now()
        metrics = StageMetrics(
            stage_name="test_stage",
            start_time=start_time
        )

        assert metrics.stage_name == "test_stage"
        assert metrics.start_time == start_time
        assert metrics.end_time is None
        assert metrics.duration_ms is None
        assert metrics.success is False
        assert metrics.error_message is None
        assert metrics.input_size_mb is None
        assert metrics.output_size_mb is None
        assert metrics.memory_usage_mb is None
        assert metrics.cpu_usage_percent is None
        assert metrics.custom_metrics == {}

    def test_complete_successful(self):
        """Test completing a stage successfully."""
        start_time = datetime.now()
        metrics = StageMetrics(
            stage_name="test_stage",
            start_time=start_time
        )

        time.sleep(0.1)  # Small delay
        metrics.complete(success=True)

        assert metrics.success is True
        assert metrics.end_time is not None
        assert metrics.duration_ms is not None
        assert metrics.duration_ms > 0
        assert metrics.error_message is None

    def test_complete_with_failure(self):
        """Test completing a stage with failure."""
        start_time = datetime.now()
        metrics = StageMetrics(
            stage_name="test_stage",
            start_time=start_time
        )

        time.sleep(0.1)  # Small delay
        metrics.complete(success=False, error_message="Test error")

        assert metrics.success is False
        assert metrics.end_time is not None
        assert metrics.duration_ms is not None
        assert metrics.duration_ms > 0
        assert metrics.error_message == "Test error"

    def test_to_dict(self):
        """Test converting stage metrics to dictionary."""
        start_time = datetime.now()
        metrics = StageMetrics(
            stage_name="test_stage",
            start_time=start_time,
            input_size_mb=100.0,
            output_size_mb=50.0,
            memory_usage_mb=512.0,
            cpu_usage_percent=75.0,
            custom_metrics={"custom": "value"}
        )

        metrics.complete(success=True)

        metrics_dict = metrics.to_dict()

        assert isinstance(metrics_dict, dict)
        assert metrics_dict["stage_name"] == "test_stage"
        assert metrics_dict["start_time"] == start_time.isoformat()
        assert metrics_dict["input_size_mb"] == 100.0
        assert metrics_dict["output_size_mb"] == 50.0
        assert metrics_dict["memory_usage_mb"] == 512.0
        assert metrics_dict["cpu_usage_percent"] == 75.0
        assert metrics_dict["custom_metrics"] == {"custom": "value"}


class TestConversionLogger:
    """Test cases for ConversionLogger class."""

    def test_initialization(self):
        """Test ConversionLogger initialization."""
        logger = ConversionLogger("test_op")

        assert logger.operation_id == "test_op"
        assert logger.log_level == ConversionLogLevel.INFO
        assert logger.enable_file_logging is True
        assert logger.enable_console_logging is True
        assert len(logger._log_entries) == 0
        assert len(logger._stage_metrics) == 0

    def test_initialization_with_options(self):
        """Test ConversionLogger initialization with options."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = Path(temp_dir)
            logger = ConversionLogger(
                operation_id="test_op",
                log_level="DEBUG",
                enable_file_logging=False,
                enable_console_logging=True,
                log_directory=log_dir
            )

            assert logger.operation_id == "test_op"
            assert logger.log_level == ConversionLogLevel.DEBUG
            assert logger.enable_file_logging is False
            assert logger.enable_console_logging is True

    def test_log_level_filtering(self):
        """Test that logs below log level are filtered out."""
        logger = ConversionLogger("test_op", log_level="ERROR")

        # These should be filtered out
        logger.trace("Trace message")
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")

        # This should be logged
        logger.error("Error message")

        entries = logger.get_log_entries()
        assert len(entries) == 1
        assert entries[0]["level"] == "ERROR"
        assert entries[0]["message"] == "Error message"

    def test_trace_logging(self):
        """Test trace level logging."""
        logger = ConversionLogger("test_op", log_level="TRACE")

        logger.trace("Trace message", "test_stage", {"key": "value"})

        entries = logger.get_log_entries()
        assert len(entries) == 1
        assert entries[0]["level"] == "TRACE"
        assert entries[0]["message"] == "Trace message"
        assert entries[0]["stage"] == "test_stage"
        assert entries[0]["details"] == {"key": "value"}

    def test_debug_logging(self):
        """Test debug level logging."""
        logger = ConversionLogger("test_op", log_level="DEBUG")

        logger.debug("Debug message", "test_stage")

        entries = logger.get_log_entries()
        assert len(entries) == 1
        assert entries[0]["level"] == "DEBUG"
        assert entries[0]["message"] == "Debug message"

    def test_info_logging(self):
        """Test info level logging."""
        logger = ConversionLogger("test_op")

        logger.info("Info message", "test_stage")

        entries = logger.get_log_entries()
        assert len(entries) == 1
        assert entries[0]["level"] == "INFO"
        assert entries[0]["message"] == "Info message"

    def test_warning_logging(self):
        """Test warning level logging."""
        logger = ConversionLogger("test_op")

        logger.warning("Warning message", "test_stage")

        entries = logger.get_log_entries()
        assert len(entries) == 1
        assert entries[0]["level"] == "WARN"
        assert entries[0]["message"] == "Warning message"

    def test_error_logging(self):
        """Test error level logging."""
        logger = ConversionLogger("test_op")

        error = ValueError("Test error")
        context = {"key": "value"}
        logger.error("Error message", "test_stage", context, error)

        entries = logger.get_log_entries()
        assert len(entries) == 1
        assert entries[0]["level"] == "ERROR"
        assert entries[0]["message"] == "Error message"
        assert entries[0]["error_type"] == "ValueError"
        assert entries[0]["error_traceback"] is not None
        assert entries[0]["details"] == context

    def test_critical_logging(self):
        """Test critical level logging."""
        logger = ConversionLogger("test_op")

        logger.critical("Critical message", "test_stage")

        entries = logger.get_log_entries()
        assert len(entries) == 1
        assert entries[0]["level"] == "CRITICAL"
        assert entries[0]["message"] == "Critical message"

    def test_audit_logging(self):
        """Test audit level logging."""
        logger = ConversionLogger("test_op")

        logger.audit("Audit message", "test_stage")

        entries = logger.get_log_entries()
        assert len(entries) == 1
        assert entries[0]["level"] == "AUDIT"
        assert entries[0]["message"] == "Audit message"

    def test_performance_logging(self):
        """Test performance level logging."""
        logger = ConversionLogger("test_op")

        logger.performance("Performance message", "test_stage", {"key": "value"}, 150.5)

        entries = logger.get_log_entries()
        assert len(entries) == 1
        assert entries[0]["level"] == "PERF"
        assert entries[0]["message"] == "Performance message"
        assert entries[0]["duration_ms"] == 150.5

    def test_log_stage_start(self):
        """Test logging stage start."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = Path(temp_dir)
            logger = ConversionLogger("test_op", log_directory=log_dir)

            metadata = {"key": "value"}
            logger.log_stage_start("test_stage", metadata)

            # Should have audit entry
            audit_entries = logger.get_log_entries(ConversionLogLevel.AUDIT)
            assert len(audit_entries) == 1
            assert "Stage started" in audit_entries[0]["message"]

            # Should have stage metrics
            stage_metrics = logger.get_stage_metrics("test_stage")
            assert stage_metrics is not None
            assert stage_metrics.stage_name == "test_stage"
            assert stage_metrics.start_time is not None

    def test_log_stage_progress(self):
        """Test logging stage progress."""
        logger = ConversionLogger("test_op")

        logger.log_stage_progress("test_stage", 75.0, "Progress details")

        # Should have info entry
        entries = logger.get_log_entries()
        progress_entries = [e for e in entries if e["message"].startswith("Stage progress")]
        assert len(progress_entries) == 1
        assert "75.0%" in progress_entries[0]["message"]
        assert "Progress details" in progress_entries[0]["message"]

    def test_log_stage_completion(self):
        """Test logging stage completion."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = Path(temp_dir)
            logger = ConversionLogger("test_op", log_directory=log_dir)

            result = {"status": "success"}
            logger.log_stage_completion("test_stage", 5.5, result)

            # Should have audit entry
            audit_entries = logger.get_log_entries(ConversionLogLevel.AUDIT)
            assert len(audit_entries) == 1
            assert "Stage completed" in audit_entries[0]["message"]
            assert "5.5s" in audit_entries[0]["message"]

            # Should have updated stage metrics
            stage_metrics = logger.get_stage_metrics("test_stage")
            assert stage_metrics is not None
            assert stage_metrics.success is True

    def test_log_error(self):
        """Test logging error."""
        logger = ConversionLogger("test_op")

        error = ValueError("Test error")
        context = {"stage": "test_stage", "key": "value"}
        logger.log_error("test_stage", error, context)

        # Should have error entry
        error_entries = logger.get_log_entries(ConversionLogLevel.ERROR)
        assert len(error_entries) == 1
        assert error_entries[0]["stage"] == "test_stage"
        assert error_entries[0]["error_type"] == "ValueError"
        assert error_entries[0]["error_message"] == "Test error"

        # Should have updated stage metrics
        stage_metrics = logger.get_stage_metrics("test_stage")
        assert stage_metrics is not None
        assert stage_metrics.success is False
        assert stage_metrics.error_message == "Test error"

    def test_get_log_entries_with_level_filter(self):
        """Test getting log entries with level filter."""
        logger = ConversionLogger("test_op", log_level="TRACE")

        logger.info("Info message")
        logger.error("Error message")
        logger.audit("Audit message")

        # Get only error entries
        error_entries = logger.get_log_entries(level=ConversionLogLevel.ERROR)
        assert len(error_entries) == 1
        assert error_entries[0]["level"] == "ERROR"

        # Get only audit entries
        audit_entries = logger.get_log_entries(level=ConversionLogLevel.AUDIT)
        assert len(audit_entries) == 1
        assert audit_entries[0]["level"] == "AUDIT"

    def test_get_log_entries_with_limit(self):
        """Test getting log entries with limit."""
        logger = ConversionLogger("test_op", log_level="TRACE")

        # Add multiple entries
        for i in range(5):
            logger.info(f"Message {i}")

        # Get with limit
        limited_entries = logger.get_log_entries(limit=3)
        assert len(limited_entries) == 3
        # Should be the last 3 entries
        for i, entry in enumerate(limited_entries):
            assert entry["message"] == f"Message {i+2}"

    def test_export_audit_log(self):
        """Test exporting audit log."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = Path(temp_dir)
            logger = ConversionLogger("test_op", log_directory=log_dir)

            # Add some entries
            logger.audit("Audit message 1")
            logger.audit("Audit message 2")
            logger.log_stage_start("test_stage", {})
            logger.log_stage_completion("test_stage", 1.0, {})

            export_file = Path(temp_dir) / "audit_log.json"
            logger.export_audit_log(export_file)

            assert export_file.exists()
            with open(export_file, 'r') as f:
                audit_data = json.load(f)

            assert audit_data["operation_id"] == "test_op"
            assert audit_data["total_entries"] == 4
            assert len(audit_data["entries"]) == 4
            assert "stage_metrics" in audit_data

    def test_export_structured_log_json(self):
        """Test exporting structured log in JSON format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = Path(temp_dir)
            logger = ConversionLogger("test_op", log_directory=log_dir)

            logger.info("Test message")
            logger.error("Error message")

            export_file = Path(temp_dir) / "structured_log.json"
            logger.export_structured_log(export_file, format="json")

            assert export_file.exists()
            with open(export_file, 'r') as f:
                log_data = json.load(f)

            assert log_data["operation_id"] == "test_op"
            assert len(log_data["log_entries"]) == 2
            assert "stage_metrics" in log_data

    def test_export_structured_log_csv(self):
        """Test exporting structured log in CSV format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = Path(temp_dir)
            logger = ConversionLogger("test_op", log_directory=log_dir)

            logger.info("Test message")
            logger.error("Error message")

            export_file = Path(temp_dir) / "structured_log.csv"
            logger.export_structured_log(export_file, format="csv")

            assert export_file.exists()
            content = export_file.read_text(encoding="utf-8")
            assert "timestamp,level,stage,message" in content

    def test_export_structured_log_text(self):
        """Test exporting structured log in text format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = Path(temp_dir)
            logger = ConversionLogger("test_op", log_directory=log_dir)

            logger.info("Test message")
            logger.error("Error message")

            export_file = Path(temp_dir) / "structured_log.txt"
            logger.export_structured_log(export_file, format="text")

            assert export_file.exists()
            content = export_file.read_text(encoding="utf-8")
            assert "Conversion Log: test_op" in content
            assert "INFO: Test message" in content

    def test_get_summary(self):
        """Test getting logger summary."""
        logger = ConversionLogger("test_op", log_level="TRACE")

        logger.info("Info message")
        logger.error("Error message")
        logger.audit("Audit message")
        logger.log_stage_start("test_stage", {})
        logger.log_stage_completion("test_stage", 1.0, {})

        summary = logger.get_summary()

        assert summary["operation_id"] == "test_op"
        assert summary["total_log_entries"] == 5
        assert summary["log_level_counts"]["INFO"] == 1
        assert summary["log_level_counts"]["ERROR"] == 1
        assert summary["log_level_counts"]["AUDIT"] == 3
        assert summary["total_stages"] == 1
        assert summary["completed_stages"] == 1

    def test_thread_safety(self):
        """Test that logger is thread-safe."""
        logger = ConversionLogger("test_op", log_level="TRACE")

        def log_messages():
            for i in range(10):
                logger.info(f"Message {i}")

        # Run multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=log_messages)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Should have all messages logged
        entries = logger.get_log_entries()
        assert len(entries) == 30  # 3 threads * 10 messages each

    def test_invalid_export_format(self):
        """Test invalid export format."""
        logger = ConversionLogger("test_op")

        with tempfile.TemporaryDirectory() as temp_dir:
            export_file = Path(temp_dir) / "invalid.format"

            with pytest.raises(ValueError, match="Unsupported export format"):
                logger.export_structured_log(export_file, format="invalid")