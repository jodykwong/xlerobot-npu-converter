"""
Status Callback Interface

This module defines the callback interface for receiving real-time status updates
during the conversion process. It provides a flexible way to implement different
types of status feedback mechanisms.

Key Features:
- Abstract base class for status callbacks
- Support for multiple callback implementations
- Real-time status updates and event notifications
- Error handling and context information
- Thread-safe callback execution
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List, Union, Callable
from pathlib import Path
import logging
import json
from datetime import datetime
import threading

logger = logging.getLogger(__name__)


class StatusCallback(ABC):
    """
    Abstract base class for status callback implementations.

    This class defines the interface that all status callbacks must implement.
    Callbacks are used to provide real-time feedback during the conversion process.
    """

    @abstractmethod
    def on_status_update(
        self,
        status: str,
        message: str,
        progress: Optional[float] = None
    ) -> None:
        """
        Called when the conversion status updates.

        Args:
            status: Current status string (e.g., "running", "completed", "failed")
            message: Descriptive message about the status update
            progress: Optional progress percentage (0.0 to 100.0)
        """
        pass

    @abstractmethod
    def on_stage_completed(
        self,
        stage_name: str,
        result: Any
    ) -> None:
        """
        Called when a conversion stage completes.

        Args:
            stage_name: Name of the completed stage
            result: Result of the stage execution
        """
        pass

    @abstractmethod
    def on_error(
        self,
        error: Exception,
        context: Dict[str, Any]
    ) -> None:
        """
        Called when an error occurs during conversion.

        Args:
            error: The exception that occurred
            context: Additional context information about the error
        """
        pass


class ConsoleStatusCallback(StatusCallback):
    """Console-based status callback that prints updates to the terminal."""

    def __init__(
        self,
        show_progress: bool = True,
        show_timestamp: bool = True,
        color_output: bool = True
    ) -> None:
        """
        Initialize console status callback.

        Args:
            show_progress: Whether to show progress percentage
            show_timestamp: Whether to show timestamps
            color_output: Whether to use colored output (if supported)
        """
        self.show_progress = show_progress
        self.show_timestamp = show_timestamp
        self.color_output = color_output
        self._lock = threading.Lock()

    def on_status_update(
        self,
        status: str,
        message: str,
        progress: Optional[float] = None
    ) -> None:
        """Print status update to console."""
        with self._lock:
            output_parts = []

            if self.show_timestamp:
                timestamp = datetime.now().strftime("%H:%M:%S")
                output_parts.append(f"[{timestamp}]")

            status_part = f"[{status.upper()}]"
            if self.color_output:
                # Simple color mapping (could be enhanced with proper terminal colors)
                color_map = {
                    "running": "\033[93m",  # Yellow
                    "completed": "\033[92m",  # Green
                    "failed": "\033[91m",  # Red
                    "ready": "\033[94m",  # Blue
                }
                reset_color = "\033[0m"
                status_part = f"{color_map.get(status, '')}{status_part}{reset_color}"

            output_parts.append(status_part)
            output_parts.append(message)

            if self.show_progress and progress is not None:
                output_parts.append(f"({progress:.1f}%)")

            print(" ".join(output_parts))

    def on_stage_completed(
        self,
        stage_name: str,
        result: Any
    ) -> None:
        """Print stage completion to console."""
        with self._lock:
            timestamp = datetime.now().strftime("%H:%M:%S")
            status_part = "\033[92m[COMPLETED]\033[0m" if self.color_output else "[COMPLETED]"
            print(f"[{timestamp}] {status_part} Stage '{stage_name}' completed successfully")

    def on_error(
        self,
        error: Exception,
        context: Dict[str, Any]
    ) -> None:
        """Print error to console."""
        with self._lock:
            timestamp = datetime.now().strftime("%H:%M:%S")
            status_part = "\033[91m[ERROR]\033[0m" if self.color_output else "[ERROR]"
            print(f"[{timestamp}] {status_part} {type(error).__name__}: {error}")

            if context.get("stage"):
                print(f"  Stage: {context['stage']}")
            if context.get("operation_id"):
                print(f"  Operation ID: {context['operation_id']}")


class FileStatusCallback(StatusCallback):
    """File-based status callback that writes updates to a log file."""

    def __init__(
        self,
        log_file_path: Union[str, Path],
        include_json: bool = True,
        max_file_size: Optional[int] = None
    ) -> None:
        """
        Initialize file status callback.

        Args:
            log_file_path: Path to the log file
            include_json: Whether to include structured JSON data
            max_file_size: Maximum file size in bytes before rotation (None for unlimited)
        """
        self.log_file_path = Path(log_file_path)
        self.include_json = include_json
        self.max_file_size = max_file_size
        self._lock = threading.Lock()

        # Create parent directory if it doesn't exist
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)

    def _write_log_entry(self, entry_type: str, data: Dict[str, Any]) -> None:
        """Write a log entry to the file."""
        with self._lock:
            # Check file size and rotate if necessary
            if self.max_file_size and self.log_file_path.exists():
                if self.log_file_path.stat().st_size >= self.max_file_size:
                    self._rotate_log_file()

            with open(self.log_file_path, "a", encoding="utf-8") as f:
                timestamp = datetime.now().isoformat()

                # Write human-readable line
                f.write(f"[{timestamp}] {entry_type.upper()}: {data.get('message', '')}\n")

                # Write JSON data if requested
                if self.include_json:
                    json_data = {
                        "timestamp": timestamp,
                        "type": entry_type,
                        **data
                    }
                    f.write(f"  JSON: {json.dumps(json_data, indent=2, default=str)}\n")

                f.write("\n")  # Add separator

    def _rotate_log_file(self) -> None:
        """Rotate the log file by appending timestamp to current file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.log_file_path.with_suffix(f".{timestamp}{self.log_file_path.suffix}")
        self.log_file_path.rename(backup_path)
        logger.info(f"Rotated log file to {backup_path}")

    def on_status_update(
        self,
        status: str,
        message: str,
        progress: Optional[float] = None
    ) -> None:
        """Write status update to file."""
        data = {
            "status": status,
            "message": message
        }
        if progress is not None:
            data["progress"] = progress

        self._write_log_entry("status_update", data)

    def on_stage_completed(
        self,
        stage_name: str,
        result: Any
    ) -> None:
        """Write stage completion to file."""
        data = {
            "stage_name": stage_name,
            "result_type": type(result).__name__
        }

        # Try to include result summary if it's serializable
        try:
            if hasattr(result, 'success'):
                data["result_success"] = result.success
            if hasattr(result, 'message'):
                data["result_message"] = result.message
        except Exception:
            pass  # Ignore serialization errors

        self._write_log_entry("stage_completed", data)

    def on_error(
        self,
        error: Exception,
        context: Dict[str, Any]
    ) -> None:
        """Write error to file."""
        data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        }

        self._write_log_entry("error", data)


class MemoryStatusCallback(StatusCallback):
    """Memory-based status callback that stores updates in memory for later retrieval."""

    def __init__(self, max_entries: int = 1000) -> None:
        """
        Initialize memory status callback.

        Args:
            max_entries: Maximum number of entries to keep in memory
        """
        self.max_entries = max_entries
        self._entries: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

    def _add_entry(self, entry_type: str, data: Dict[str, Any]) -> None:
        """Add an entry to the memory buffer."""
        with self._lock:
            entry = {
                "timestamp": datetime.now().isoformat(),
                "type": entry_type,
                **data
            }

            self._entries.append(entry)

            # Remove oldest entries if exceeding max_entries
            if len(self._entries) > self.max_entries:
                self._entries = self._entries[-self.max_entries:]

    def on_status_update(
        self,
        status: str,
        message: str,
        progress: Optional[float] = None
    ) -> None:
        """Store status update in memory."""
        data = {
            "status": status,
            "message": message
        }
        if progress is not None:
            data["progress"] = progress

        self._add_entry("status_update", data)

    def on_stage_completed(
        self,
        stage_name: str,
        result: Any
    ) -> None:
        """Store stage completion in memory."""
        data = {
            "stage_name": stage_name,
            "result_type": type(result).__name__
        }

        # Try to include result summary
        try:
            if hasattr(result, 'success'):
                data["result_success"] = result.success
            if hasattr(result, 'message'):
                data["result_message"] = result.message
        except Exception:
            pass

        self._add_entry("stage_completed", data)

    def on_error(
        self,
        error: Exception,
        context: Dict[str, Any]
    ) -> None:
        """Store error in memory."""
        data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        }

        self._add_entry("error", data)

    def get_entries(
        self,
        entry_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get stored entries.

        Args:
            entry_type: Filter by entry type (None for all)
            limit: Maximum number of entries to return

        Returns:
            List[Dict[str, Any]]: List of matching entries
        """
        with self._lock:
            entries = self._entries

            if entry_type:
                entries = [e for e in entries if e["type"] == entry_type]

            if limit:
                entries = entries[-limit:]

            return entries.copy()

    def clear_entries(self) -> None:
        """Clear all stored entries."""
        with self._lock:
            self._entries.clear()

    def get_latest_status(self) -> Optional[Dict[str, Any]]:
        """Get the latest status update."""
        status_entries = self.get_entries("status_update", limit=1)
        return status_entries[0] if status_entries else None


class CompositeStatusCallback(StatusCallback):
    """Composite callback that forwards events to multiple other callbacks."""

    def __init__(self, callbacks: List[StatusCallback]) -> None:
        """
        Initialize composite callback.

        Args:
            callbacks: List of callbacks to forward events to
        """
        self.callbacks = callbacks

    def on_status_update(
        self,
        status: str,
        message: str,
        progress: Optional[float] = None
    ) -> None:
        """Forward status update to all callbacks."""
        for callback in self.callbacks:
            try:
                callback.on_status_update(status, message, progress)
            except Exception as e:
                logger.warning(f"Callback {callback.__class__.__name__} failed on_status_update: {e}")

    def on_stage_completed(
        self,
        stage_name: str,
        result: Any
    ) -> None:
        """Forward stage completion to all callbacks."""
        for callback in self.callbacks:
            try:
                callback.on_stage_completed(stage_name, result)
            except Exception as e:
                logger.warning(f"Callback {callback.__class__.__name__} failed on_stage_completed: {e}")

    def on_error(
        self,
        error: Exception,
        context: Dict[str, Any]
    ) -> None:
        """Forward error to all callbacks."""
        for callback in self.callbacks:
            try:
                callback.on_error(error, context)
            except Exception as e:
                logger.warning(f"Callback {callback.__class__.__name__} failed on_error: {e}")

    def add_callback(self, callback: StatusCallback) -> None:
        """Add a callback to the composite."""
        self.callbacks.append(callback)

    def remove_callback(self, callback: StatusCallback) -> bool:
        """Remove a callback from the composite."""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
            return True
        return False