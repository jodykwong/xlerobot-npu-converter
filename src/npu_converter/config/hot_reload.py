"""
Hot Reload Manager

Monitors configuration file changes and automatically reloads configuration.
Implements atomic updates and rollback mechanisms.

Implements the hot reload functionality as defined in the architecture
document with performance requirements: <500ms reload time.
"""

import time
import threading
from pathlib import Path
from typing import Callable, Optional, Dict, Any
from dataclasses import dataclass
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import FileModifiedEvent

from npu_converter.core.exceptions.config_errors import ConfigError


@dataclass
class HotReloadMetrics:
    """Hot reload performance metrics."""
    reload_count: int = 0
    successful_reloads: int = 0
    failed_reloads: int = 0
    total_reload_time_ms: float = 0.0
    average_reload_time_ms: float = 0.0
    last_reload_time_ms: float = 0.0
    last_reload_timestamp: Optional[float] = None


class ConfigFileHandler(FileSystemEventHandler):
    """File system event handler for configuration files."""

    def __init__(self, config_file_path: Path, reload_callback: Callable[[], None]):
        """
        Initialize file handler.

        Args:
            config_file_path: Path to configuration file to monitor
            reload_callback: Callback function to execute on file changes
        """
        self.config_file_path = config_file_path
        self.reload_callback = reload_callback
        self._last_reload_time = 0.0
        self._reload_cooldown = 0.1  # 100ms cooldown between reloads

    def on_modified(self, event):
        """Handle file modification events."""
        if isinstance(event, FileModifiedEvent):
            if event.src_path == str(self.config_file_path):
                current_time = time.time()

                # Prevent rapid successive reloads
                if current_time - self._last_reload_time < self._reload_cooldown:
                    return

                self._last_reload_time = current_time
                try:
                    self.reload_callback()
                except Exception as e:
                    print(f"Error during hot reload callback: {e}")


class HotReloadManager:
    """
    Hot reload management system.

    Monitors configuration file changes and automatically reloads configuration
    with atomic updates and rollback mechanisms.
    """

    def __init__(self, config_file_path: Path, reload_callback: Callable[[], None]):
        """
        Initialize hot reload manager.

        Args:
            config_file_path: Path to configuration file to monitor
            reload_callback: Callback function to execute on reload
        """
        self.config_file_path = Path(config_file_path)
        self.reload_callback = reload_callback
        self._observer: Optional[Observer] = None
        self._file_handler: Optional[ConfigFileHandler] = None
        self._is_monitoring = False
        self._metrics = HotReloadMetrics()
        self._lock = threading.Lock()

        # Performance requirements from architecture
        self._reload_time_threshold_ms = 500.0

    def start_monitoring(self) -> None:
        """Start monitoring configuration file changes."""
        if self._is_monitoring:
            return

        if not self.config_file_path.exists():
            raise ConfigError(f"Configuration file not found: {self.config_file_path}")

        try:
            self._observer = Observer()
            self._file_handler = ConfigFileHandler(self.config_file_path, self.reload_callback)

            # Monitor the directory containing the config file
            self._observer.schedule(self._file_handler, str(self.config_file_path.parent), recursive=False)
            self._observer.start()
            self._is_monitoring = True

            print(f"Hot reload monitoring started for: {self.config_file_path}")

        except Exception as e:
            raise ConfigError(f"Failed to start hot reload monitoring: {e}")

    def stop_monitoring(self) -> None:
        """Stop monitoring configuration file changes."""
        if not self._is_monitoring:
            return

        try:
            if self._observer:
                self._observer.stop()
                self._observer.join(timeout=1.0)  # Wait up to 1 second for thread to stop
                self._observer = None

            self._file_handler = None
            self._is_monitoring = False

            print("Hot reload monitoring stopped")

        except Exception as e:
            print(f"Error stopping hot reload monitoring: {e}")

    def is_monitoring(self) -> bool:
        """Check if hot reload monitoring is active."""
        return self._is_monitoring

    def get_metrics(self) -> HotReloadMetrics:
        """Get hot reload performance metrics."""
        with self._lock:
            return self._metrics

    def _update_metrics(self, reload_time_ms: float, success: bool) -> None:
        """Update hot reload performance metrics."""
        with self._lock:
            self._metrics.reload_count += 1
            self._metrics.last_reload_time_ms = reload_time_ms
            self._metrics.last_reload_timestamp = time.time()
            self._metrics.total_reload_time_ms += reload_time_ms

            if success:
                self._metrics.successful_reloads += 1
            else:
                self._metrics.failed_reloads += 1

            # Calculate average reload time
            if self._metrics.reload_count > 0:
                self._metrics.average_reload_time_ms = (
                    self._metrics.total_reload_time_ms / self._metrics.reload_count
                )

            # Check performance threshold
            if reload_time_ms > self._reload_time_threshold_ms:
                print(f"Warning: Reload time {reload_time_ms:.2f}ms exceeds threshold {self._reload_time_threshold_ms}ms")

    def force_reload(self) -> bool:
        """
        Force a configuration reload.

        Returns:
            True if reload was successful
        """
        if not self.config_file_path.exists():
            print(f"Configuration file not found: {self.config_file_path}")
            return False

        start_time = time.time()
        success = False

        try:
            self.reload_callback()
            success = True
        except Exception as e:
            print(f"Force reload failed: {e}")
            success = False
        finally:
            reload_time = (time.time() - start_time) * 1000
            self._update_metrics(reload_time, success)

        return success

    def __enter__(self):
        """Context manager entry."""
        self.start_monitoring()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_monitoring()

    def get_status_summary(self) -> Dict[str, Any]:
        """Get hot reload status summary."""
        with self._lock:
            return {
                "monitoring": self._is_monitoring,
                "config_file": str(self.config_file_path),
                "reload_count": self._metrics.reload_count,
                "successful_reloads": self._metrics.successful_reloads,
                "failed_reloads": self._metrics.failed_reloads,
                "average_reload_time_ms": round(self._metrics.average_reload_time_ms, 2),
                "last_reload_time_ms": round(self._metrics.last_reload_time_ms, 2),
                "last_reload_timestamp": self._metrics.last_reload_timestamp
            }


class AtomicConfigUpdater:
    """
    Provides atomic configuration update operations.

    Ensures configuration updates are atomic and can be rolled back
    if validation fails.
    """

    def __init__(self, config_file_path: Path):
        """
        Initialize atomic config updater.

        Args:
            config_file_path: Path to configuration file
        """
        self.config_file_path = config_file_path
        self._backup_path = config_file_path.with_suffix('.yaml.backup')
        self._temp_path = config_file_path.with_suffix('.yaml.tmp')

    def update_config(self, new_config: Dict[str, Any], validator: Optional[Callable[[Dict[str, Any]], bool]] = None) -> bool:
        """
        Atomically update configuration file.

        Args:
            new_config: New configuration dictionary
            validator: Optional validation function

        Returns:
            True if update was successful
        """
        import yaml

        try:
            # Create backup
            if self.config_file_path.exists():
                import shutil
                shutil.copy2(self.config_file_path, self._backup_path)

            # Write new config to temporary file
            with open(self._temp_path, 'w', encoding='utf-8') as f:
                yaml.dump(new_config, f, default_flow_style=False, indent=2)

            # Validate new config if validator provided
            if validator and not validator(new_config):
                raise ValueError("Configuration validation failed")

            # Atomic move: replace original with new
            import os
            os.replace(self._temp_path, self.config_file_path)

            # Clean up backup after successful update
            if self._backup_path.exists():
                os.remove(self._backup_path)

            return True

        except Exception as e:
            # Rollback on failure
            if self._backup_path.exists():
                import os
                os.replace(self._backup_path, self.config_file_path)

            # Clean up temporary file
            if self._temp_path.exists():
                import os
                os.remove(self._temp_path)

            print(f"Configuration update failed, rolled back: {e}")
            return False

    def rollback(self) -> bool:
        """
        Rollback to last backup if available.

        Returns:
            True if rollback was successful
        """
        if not self._backup_path.exists():
            print("No backup available for rollback")
            return False

        try:
            import os
            os.replace(self._backup_path, self.config_file_path)
            return True
        except Exception as e:
            print(f"Rollback failed: {e}")
            return False

    def has_backup(self) -> bool:
        """Check if backup is available."""
        return self._backup_path.exists()