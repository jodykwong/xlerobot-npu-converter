"""
Unit tests for StructuredLogger module.

Tests all logging levels, output formats, and functionality
as specified in AC1: 实现分级日志记录（DEBUG, INFO, WARN, ERROR）
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from npu_converter.utils.logger import StructuredLogger, LogEntry, StructuredFormatter, get_logger


class TestStructuredLogger:
    """Test cases for StructuredLogger class."""

    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary directory for log files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def logger(self, temp_log_dir):
        """Create logger instance for testing."""
        with patch('npu_converter.utils.logger.Path') as mock_path:
            mock_path.return_value = Path(temp_dir)
            logger = StructuredLogger("test_logger")
            return logger

    def test_logger_initialization(self, logger):
        """Test logger initialization with different levels."""
        assert logger.name == "test_logger"
        assert logger.logger.level == 20  # INFO level
        assert len(logger.logger.handlers) == 2  # Console and file handlers

    def test_logger_levels(self, temp_log_dir):
        """Test all four logging levels (AC1)."""
        with patch('npu_converter.utils.logger.Path') as mock_path:
            mock_path.return_value = Path(temp_dir)
            logger = StructuredLogger("test_logger", "DEBUG")

            # Test all four levels
            logger.debug("Debug message", component="test")
            logger.info("Info message", component="test")
            logger.warning("Warning message", component="test")
            logger.error("Error message", component="test")

            # Verify log file was created
            log_file = Path(temp_dir) / "test_logger.log"
            assert log_file.exists()

            # Verify log content
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
                assert "Debug message" in log_content
                assert "Info message" in log_content
                assert "Warning message" in log_content
                assert "Error message" in log_content

    def test_structured_logging_with_context(self, temp_log_dir):
        """Test structured logging with contextual information."""
        with patch('npu_converter.utils.logger.Path') as mock_path:
            mock_path.return_value = Path(temp_dir)
            logger = StructuredLogger("test_logger")

            logger.info("Test message",
                       user_id="123",
                       operation="conversion",
                       model_type="sensevoice")

            log_file = Path(temp_dir) / "test_logger.log"
            with open(log_file, 'r', encoding='utf-8') as f:
                log_entry = json.loads(f.readline().strip())

                assert log_entry["message"] == "Test message"
                assert log_entry["level"] == "INFO"
                assert log_entry["context"]["user_id"] == "123"
                assert log_entry["context"]["operation"] == "conversion"
                assert log_entry["context"]["model_type"] == "sensevoice"

    def test_exception_logging(self, temp_log_dir):
        """Test exception logging with stack trace."""
        with patch('npu_converter.utils.logger.Path') as mock_path:
            mock_path.return_value = Path(temp_dir)
            logger = StructuredLogger("test_logger")

            try:
                raise ValueError("Test exception")
            except ValueError as e:
                logger.error("Error occurred", exception=e, context={"operation": "test"})

            log_file = Path(temp_dir) / "test_logger.log"
            with open(log_file, 'r', encoding='utf-8') as f:
                log_entry = json.loads(f.readline().strip())

                assert log_entry["message"] == "Error occurred"
                assert log_entry["level"] == "ERROR"
                assert log_entry["exception"] is not None
                assert "ValueError" in log_entry["exception"]
                assert "Test exception" in log_entry["exception"]

    def test_console_output_format(self, logger):
        """Test console output is human-readable."""
        with patch('sys.stdout') as mock_stdout:
            mock_stdout.write = MagicMock()

            logger.info("Console test message", user_id="123")

            # Console output should be human-readable, not JSON
            calls = mock_stdout.write.call_args_list
            output_text = ''.join(str(call) for call in calls)
            assert "Console test message" in output_text
            assert "INFO" in output_text

    def test_log_level_filtering(self, temp_log_dir):
        """Test log level filtering works correctly."""
        with patch('npu_converter.utils.logger.Path') as mock_path:
            mock_path.return_value = Path(temp_dir)
            logger = StructuredLogger("test_logger", "WARN")

            logger.debug("Debug message")  # Should not appear
            logger.info("Info message")    # Should not appear
            logger.warning("Warning message")  # Should appear
            logger.error("Error message")      # Should appear

            log_file = Path(temp_dir) / "test_logger.log"
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
                assert "Debug message" not in log_content
                assert "Info message" not in log_content
                assert "Warning message" in log_content
                assert "Error message" in log_content

    def test_dynamic_level_change(self, logger):
        """Test changing log level dynamically."""
        original_level = logger.logger.level
        logger.set_level("ERROR")
        assert logger.logger.level == 40  # ERROR level
        assert logger.logger.level != original_level

    def test_additional_file_handler(self, temp_log_dir):
        """Test adding additional file handler."""
        with patch('npu_converter.utils.logger.Path') as mock_path:
            mock_path.return_value = Path(temp_dir)
            logger = StructuredLogger("test_logger")

            # Add additional file handler
            extra_log_file = Path(temp_dir) / "extra.log"
            logger.add_file_handler(extra_log_file, "DEBUG")

            logger.info("Test message for multiple handlers")

            # Verify both log files have content
            main_log_file = Path(temp_dir) / "test_logger.log"
            assert main_log_file.exists()
            assert extra_log_file.exists()

            with open(main_log_file, 'r', encoding='utf-8') as f:
                assert "Test message for multiple handlers" in f.read()

            with open(extra_log_file, 'r', encoding='utf-8') as f:
                assert "Test message for multiple handlers" in f.read()

    def test_get_logger_singleton(self):
        """Test get_logger returns same instance for same name."""
        logger1 = get_logger("singleton_test")
        logger2 = get_logger("singleton_test")
        assert logger1 is logger2

    def test_get_logger_different_names(self):
        """Test get_logger returns different instances for different names."""
        logger1 = get_logger("test1")
        logger2 = get_logger("test2")
        assert logger1 is not logger2
        assert logger1.name == "test1"
        assert logger2.name == "test2"


class TestStructuredFormatter:
    """Test cases for StructuredFormatter class."""

    def test_structured_formatter_with_context(self):
        """Test structured formatter includes context."""
        formatter = StructuredFormatter(include_context=True)

        # Create mock log record
        import logging
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.context = {"user_id": "123", "operation": "test"}

        formatted = formatter.format(record)
        log_entry = json.loads(formatted)

        assert log_entry["message"] == "Test message"
        assert log_entry["context"]["user_id"] == "123"
        assert log_entry["context"]["operation"] == "test"

    def test_structured_formatter_without_context(self):
        """Test structured formatter without context is human-readable."""
        formatter = StructuredFormatter(include_context=False)

        import logging
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.context = {"user_id": "123"}

        formatted = formatter.format(record)

        # Should be human-readable, not JSON
        assert "Test message" in formatted
        assert "INFO" in formatted
        assert "test:" in formatted
        assert "{" not in formatted  # Not JSON

    def test_exception_formatting(self):
        """Test exception information is properly formatted."""
        formatter = StructuredFormatter(include_context=True)

        import logging
        try:
            raise ValueError("Test exception")
        except ValueError:
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="test.py",
                lineno=1,
                msg="Error occurred",
                args=(),
                exc_info=sys.exc_info()
            )
            record.context = {}

            formatted = formatter.format(record)
            log_entry = json.loads(formatted)

            assert log_entry["exception"] is not None
            assert "ValueError" in log_entry["exception"]
            assert "Test exception" in log_entry["exception"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])