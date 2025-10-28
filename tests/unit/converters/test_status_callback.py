"""
Unit tests for Status Callback System

This module contains unit tests for the status callback system,
testing different callback implementations and error handling.
"""

import pytest
import tempfile
import json
import threading
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from npu_converter.converters.status_callback import (
    StatusCallback,
    ConsoleStatusCallback,
    FileStatusCallback,
    MemoryStatusCallback,
    CompositeStatusCallback
)


class MockStatusCallback(StatusCallback):
    """Mock status callback for testing."""

    def __init__(self):
        self.status_updates = []
        self.stage_completions = []
        self.errors = []

    def on_status_update(self, status, message, progress=None):
        """Record status update."""
        self.status_updates.append({
            "status": status,
            "message": message,
            "progress": progress
        })

    def on_stage_completed(self, stage_name, result):
        """Record stage completion."""
        self.stage_completions.append({
            "stage_name": stage_name,
            "result": result
        })

    def on_error(self, error, context):
        """Record error."""
        self.errors.append({
            "error": error,
            "context": context
        })


class TestStatusCallback:
    """Test cases for StatusCallback abstract base class."""

    def test_abstract_methods(self):
        """Test that StatusCallback cannot be instantiated directly."""
        with pytest.raises(TypeError):
            StatusCallback()


class TestConsoleStatusCallback:
    """Test cases for ConsoleStatusCallback."""

    def test_initialization(self):
        """Test ConsoleStatusCallback initialization."""
        callback = ConsoleStatusCallback()

        assert callback.show_progress is True
        assert callback.show_timestamp is True
        assert callback.color_output is True

    def test_initialization_with_options(self):
        """Test ConsoleStatusCallback initialization with options."""
        callback = ConsoleStatusCallback(
            show_progress=False,
            show_timestamp=False,
            color_output=False
        )

        assert callback.show_progress is False
        assert callback.show_timestamp is False
        assert callback.color_output is False

    @patch('builtins.print')
    def test_on_status_update_basic(self, mock_print):
        """Test basic status update without progress."""
        callback = ConsoleStatusCallback(show_progress=False, show_timestamp=False)

        callback.on_status_update("running", "Test message")

        # Should call print
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        assert "[RUNNING]" in call_args
        assert "Test message" in call_args

    @patch('builtins.print')
    def test_on_status_update_with_progress(self, mock_print):
        """Test status update with progress."""
        callback = ConsoleStatusCallback(show_progress=True, show_timestamp=False)

        callback.on_status_update("running", "Test message", progress=75.5)

        # Should call print with progress
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        assert "[RUNNING]" in call_args
        assert "Test message" in call_args
        assert "(75.5%)" in call_args

    @patch('builtins.print')
    def test_on_status_update_with_timestamp(self, mock_print):
        """Test status update with timestamp."""
        callback = ConsoleStatusCallback(show_progress=False, show_timestamp=True)

        with patch('npu_converter.converters.status_callback.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "12:00:00"

            callback.on_status_update("running", "Test message")

            # Should call print with timestamp
            mock_print.assert_called_once()
            call_args = mock_print.call_args[0][0]
            assert "[12:00:00]" in call_args
            assert "[RUNNING]" in call_args
            assert "Test message" in call_args

    @patch('builtins.print')
    def test_on_stage_completed(self, mock_print):
        """Test stage completion notification."""
        callback = ConsoleStatusCallback(show_timestamp=False)

        callback.on_stage_completed("test_stage", {"result": "success"})

        # Should call print with completion message
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        assert "[COMPLETED]" in call_args
        assert "test_stage" in call_args

    @patch('builtins.print')
    def test_on_error(self, mock_print):
        """Test error notification."""
        callback = ConsoleStatusCallback(show_timestamp=False)

        error = ValueError("Test error")
        context = {"stage": "test_stage"}

        callback.on_error(error, context)

        # Should call print with error message
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        assert "[ERROR]" in call_args
        assert "ValueError" in call_args
        assert "Test error" in call_args

    def test_thread_safety(self):
        """Test that callback is thread-safe."""
        callback = ConsoleStatusCallback(show_progress=False, show_timestamp=False)

        def update_status():
            callback.on_status_update("running", "Test message")

        # Run multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=update_status)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Should not raise any exceptions
        assert True  # If we get here, no exceptions occurred


class TestFileStatusCallback:
    """Test cases for FileStatusCallback."""

    def test_initialization(self):
        """Test FileStatusCallback initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            callback = FileStatusCallback(log_file)

            assert callback.log_file_path == log_file
            assert callback.include_json is True
            assert callback.max_file_size is None

    def test_initialization_with_options(self):
        """Test FileStatusCallback initialization with options."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            callback = FileStatusCallback(
                log_file,
                include_json=False,
                max_file_size=1000
            )

            assert callback.include_json is False
            assert callback.max_file_size == 1000

    def test_directory_creation(self):
        """Test that directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "subdir" / "test.log"
            callback = FileStatusCallback(log_file)

            # Directory should be created
            assert log_file.parent.exists()

    def test_on_status_update(self):
        """Test status update logging."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            callback = FileStatusCallback(log_file)

            callback.on_status_update("running", "Test message")

            # Log file should be created and contain the message
            assert log_file.exists()
            content = log_file.read_text(encoding="utf-8")
            assert "status_update:" in content
            assert "Test message" in content
            assert "running" in content

    def test_on_stage_completed(self):
        """Test stage completion logging."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            callback = FileStatusCallback(log_file)

            callback.on_stage_completed("test_stage", {"result": "success"})

            # Log file should contain stage completion
            content = log_file.read_text(encoding="utf-8")
            assert "stage_completed:" in content
            assert "test_stage" in content

    def test_on_error(self):
        """Test error logging."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            callback = FileStatusCallback(log_file)

            error = ValueError("Test error")
            context = {"stage": "test_stage"}

            callback.on_error(error, context)

            # Log file should contain error
            content = log_file.read_text(encoding="utf-8")
            assert "error:" in content
            assert "ValueError" in content
            assert "Test error" in content

    def test_json_inclusion(self):
        """Test JSON data inclusion in logs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            callback = FileStatusCallback(log_file, include_json=True)

            callback.on_status_update("running", "Test message", progress=50.0)

            # Log file should contain JSON
            content = log_file.read_text(encoding="utf-8")
            assert "JSON:" in content
            assert "50.0" in content

    def test_file_rotation(self):
        """Test log file rotation when size limit is reached."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            callback = FileStatusCallback(log_file, max_file_size=100)

            # Write some content to exceed limit
            callback.on_status_update("running", "A" * 50)

            # Should rotate the file
            assert not log_file.exists()
            # Check for backup file
            backup_files = list(Path(temp_dir).glob("test.log.*"))
            assert len(backup_files) > 0


class TestMemoryStatusCallback:
    """Test cases for MemoryStatusCallback."""

    def test_initialization(self):
        """Test MemoryStatusCallback initialization."""
        callback = MemoryStatusCallback()

        assert callback.max_entries == 1000
        assert len(callback._entries) == 0

    def test_initialization_with_limit(self):
        """Test MemoryStatusCallback initialization with limit."""
        callback = MemoryStatusCallback(max_entries=100)

        assert callback.max_entries == 100

    def test_on_status_update(self):
        """Test status update storage."""
        callback = MemoryStatusCallback()

        callback.on_status_update("running", "Test message", progress=75.0)

        # Should have one entry
        entries = callback.get_entries()
        assert len(entries) == 1
        assert entries[0]["type"] == "status_update"
        assert entries[0]["status"] == "running"
        assert entries[0]["message"] == "Test message"
        assert entries[0]["progress"] == 75.0

    def test_on_stage_completed(self):
        """Test stage completion storage."""
        callback = MemoryStatusCallback()

        callback.on_stage_completed("test_stage", {"result": "success"})

        # Should have one entry
        entries = callback.get_entries()
        assert len(entries) == 1
        assert entries[0]["type"] == "stage_completed"
        assert entries[0]["stage_name"] == "test_stage"

    def test_on_error(self):
        """Test error storage."""
        callback = MemoryStatusCallback()

        error = ValueError("Test error")
        context = {"stage": "test_stage"}

        callback.on_error(error, context)

        # Should have one entry
        entries = callback.get_entries()
        assert len(entries) == 1
        assert entries[0]["type"] == "error"
        assert entries[0]["error_type"] == "ValueError"
        assert entries[0]["error_message"] == "Test error"

    def test_get_entries_with_type_filter(self):
        """Test getting entries with type filter."""
        callback = MemoryStatusCallback()

        callback.on_status_update("running", "Test message")
        callback.on_stage_completed("test_stage", {})
        callback.on_error(ValueError("Test"), {})

        # Get only status updates
        status_entries = callback.get_entries(entry_type="status_update")
        assert len(status_entries) == 1
        assert status_entries[0]["type"] == "status_update"

        # Get only stage completions
        stage_entries = callback.get_entries(entry_type="stage_completed")
        assert len(stage_entries) == 1
        assert stage_entries[0]["type"] == "stage_completed"

    def test_get_entries_with_limit(self):
        """Test getting entries with limit."""
        callback = MemoryStatusCallback()

        # Add multiple entries
        for i in range(5):
            callback.on_status_update("running", f"Message {i}")

        # Get with limit
        limited_entries = callback.get_entries(limit=3)
        assert len(limited_entries) == 3
        # Should be the last 3 entries
        for i, entry in enumerate(limited_entries):
            assert entry["message"] == f"Message {i+2}"

    def test_max_entries_enforcement(self):
        """Test that max entries limit is enforced."""
        callback = MemoryStatusCallback(max_entries=3)

        # Add more entries than the limit
        for i in range(5):
            callback.on_status_update("running", f"Message {i}")

        # Should only have the last 3 entries
        entries = callback.get_entries()
        assert len(entries) == 3
        for i, entry in enumerate(entries):
            assert entry["message"] == f"Message {i+2}"

    def test_clear_entries(self):
        """Test clearing all entries."""
        callback = MemoryStatusCallback()

        callback.on_status_update("running", "Test message")
        callback.clear_entries()

        # Should be empty
        entries = callback.get_entries()
        assert len(entries) == 0

    def test_get_latest_status(self):
        """Test getting the latest status."""
        callback = MemoryStatusCallback()

        # Should be None initially
        latest = callback.get_latest_status()
        assert latest is None

        # Add status update
        callback.on_status_update("running", "Test message")
        latest = callback.get_latest_status()
        assert latest is not None
        assert latest["status"] == "running"
        assert latest["message"] == "Test message"


class TestCompositeStatusCallback:
    """Test cases for CompositeStatusCallback."""

    def test_initialization(self):
        """Test CompositeStatusCallback initialization."""
        callback1 = Mock()
        callback2 = Mock()
        callback3 = Mock()

        composite = CompositeStatusCallback([callback1, callback2, callback3])

        assert len(composite.callbacks) == 3
        assert composite.callbacks[0] == callback1
        assert composite.callbacks[1] == callback2
        assert composite.callbacks[2] == callback3

    def test_on_status_update_forwarding(self):
        """Test that status updates are forwarded to all callbacks."""
        callback1 = Mock()
        callback2 = Mock()
        composite = CompositeStatusCallback([callback1, callback2])

        composite.on_status_update("running", "Test message", progress=50.0)

        # Both callbacks should be called
        callback1.on_status_update.assert_called_once_with("running", "Test message", progress=50.0)
        callback2.on_status_update.assert_called_once_with("running", "Test message", progress=50.0)

    def test_on_stage_completed_forwarding(self):
        """Test that stage completions are forwarded to all callbacks."""
        callback1 = Mock()
        callback2 = Mock()
        composite = CompositeStatusCallback([callback1, callback2])

        result = {"result": "success"}
        composite.on_stage_completed("test_stage", result)

        # Both callbacks should be called
        callback1.on_stage_completed.assert_called_once_with("test_stage", result)
        callback2.on_stage_completed.assert_called_once_with("test_stage", result)

    def test_on_error_forwarding(self):
        """Test that errors are forwarded to all callbacks."""
        callback1 = Mock()
        callback2 = Mock()
        composite = CompositeStatusCallback([callback1, callback2])

        error = ValueError("Test error")
        context = {"stage": "test_stage"}
        composite.on_error(error, context)

        # Both callbacks should be called
        callback1.on_error.assert_called_once_with(error, context)
        callback2.on_error.assert_called_once_with(error, context)

    def test_add_callback(self):
        """Test adding callback to composite."""
        callback1 = Mock()
        callback2 = Mock()
        composite = CompositeStatusCallback([callback1])

        composite.add_callback(callback2)

        assert len(composite.callbacks) == 2
        assert composite.callbacks[1] == callback2

    def test_remove_callback(self):
        """Test removing callback from composite."""
        callback1 = Mock()
        callback2 = Mock()
        composite = CompositeStatusCallback([callback1, callback2])

        removed = composite.remove_callback(callback1)

        assert removed is True
        assert len(composite.callbacks) == 1
        assert composite.callbacks[0] == callback2

    def test_remove_nonexistent_callback(self):
        """Test removing non-existent callback."""
        callback1 = Mock()
        callback2 = Mock()
        composite = CompositeStatusCallback([callback1])

        removed = composite.remove_callback(callback2)

        assert removed is False
        assert len(composite.callbacks) == 1

    def test_callback_exception_handling(self):
        """Test that exceptions in callbacks don't stop other callbacks."""
        callback1 = Mock()
        callback1.on_status_update.side_effect = ValueError("Callback error")

        callback2 = Mock()
        callback3 = Mock()

        composite = CompositeStatusCallback([callback1, callback2, callback3])

        # Should not raise exception
        composite.on_status_update("running", "Test message")

        # Callback1 should have been called
        callback1.on_status_update.assert_called_once()

        # Callback2 and Callback3 should still be called
        callback2.on_status_update.assert_called_once()
        callback3.on_status_update.assert_called_once()