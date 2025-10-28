"""
Configuration Recovery Manager

Provides configuration backup, recovery, and rollback functionality
for the configuration management system.

This component ensures configuration safety and reliability by
maintaining backup snapshots and enabling automatic recovery
from configuration errors.
"""

import os
import shutil
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime

from npu_converter.core.exceptions.config_errors import ConfigError


@dataclass
class ConfigSnapshot:
    """Configuration snapshot metadata."""
    timestamp: float
    datetime_str: str
    config_file_path: str
    backup_path: str
    file_size: int
    checksum: str
    recovery_reason: str = "manual_backup"


class ConfigRecoveryManager:
    """
    Configuration recovery management system.

    Provides backup creation, rollback functionality, and
    recovery statistics to ensure configuration reliability.
    """

    def __init__(self, config_dir: Path, max_backups: int = 10):
        """
        Initialize configuration recovery manager.

        Args:
            config_dir: Directory containing configuration files
            max_backups: Maximum number of backup snapshots to keep
        """
        self.config_dir = Path(config_dir)
        self.backup_dir = self.config_dir / ".config_backups"
        self.backup_dir.mkdir(exist_ok=True)

        self.max_backups = max_backups
        self.snapshots_file = self.backup_dir / "snapshots.json"
        self.recovery_stats_file = self.backup_dir / "recovery_stats.json"

        # Load existing snapshots and statistics
        self._load_snapshots()
        self._load_recovery_stats()

    def create_backup(self, config_file_path: str, reason: str = "manual_backup") -> str:
        """
        Create a backup snapshot of the current configuration.

        Args:
            config_file_path: Path to the configuration file to backup
            reason: Reason for creating this backup

        Returns:
            Backup file path

        Raises:
            ConfigError: If backup creation fails
        """
        try:
            config_path = Path(config_file_path)
            if not config_path.exists():
                raise ConfigError(f"Configuration file not found: {config_file_path}")

            # Generate backup filename with millisecond precision
            timestamp = time.time()
            datetime_str = datetime.fromtimestamp(timestamp).strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
            backup_filename = f"{config_path.stem}_{datetime_str}{config_path.suffix}"
            backup_path = self.backup_dir / backup_filename

            # Copy configuration file
            shutil.copy2(config_path, backup_path)

            # Calculate file checksum
            file_size = backup_path.stat().st_size
            checksum = self._calculate_checksum(backup_path)

            # Create snapshot metadata
            snapshot = ConfigSnapshot(
                timestamp=timestamp,
                datetime_str=datetime_str,
                config_file_path=str(config_path),
                backup_path=str(backup_path),
                file_size=file_size,
                checksum=checksum,
                recovery_reason=reason
            )

            # Add to snapshots registry
            self.snapshots[str(backup_path)] = snapshot

            # Cleanup old backups
            self._cleanup_old_backups()

            # Save snapshots metadata
            self._save_snapshots()

            print(f"✅ Configuration backup created: {backup_path}")
            return str(backup_path)

        except Exception as e:
            raise ConfigError(f"Failed to create configuration backup: {e}")

    def rollback_to_backup(self, backup_path: str) -> bool:
        """
        Rollback configuration to a specified backup.

        Args:
            backup_path: Path to the backup file to rollback to

        Returns:
            True if rollback was successful

        Raises:
            ConfigError: If rollback fails
        """
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                raise ConfigError(f"Backup file not found: {backup_path}")

            # Get snapshot metadata
            if backup_path not in self.snapshots:
                raise ConfigError(f"Backup snapshot metadata not found: {backup_path}")

            snapshot = self.snapshots[backup_path]
            config_path = Path(snapshot.config_file_path)

            # Create backup of current config before rollback
            if config_path.exists():
                current_backup = self.create_backup(
                    str(config_path),
                    "pre_rollback_backup"
                )
                print(f"📁 Created pre-rollback backup: {current_backup}")

            # Restore from backup
            shutil.copy2(backup_file, config_path)

            # Update recovery statistics
            self._update_recovery_stats("rollback_success", snapshot.datetime_str)

            print(f"✅ Configuration rolled back to: {snapshot.datetime_str}")
            return True

        except Exception as e:
            self._update_recovery_stats("rollback_failed", str(e))
            raise ConfigError(f"Failed to rollback configuration: {e}")

    def rollback_to_latest_backup(self) -> bool:
        """
        Rollback to the most recent backup.

        Returns:
            True if rollback was successful

        Raises:
            ConfigError: If no backups are available or rollback fails
        """
        if not self.snapshots:
            raise ConfigError("No backup snapshots available for rollback")

        # Find the most recent backup
        latest_backup_path = max(self.snapshots.keys(),
                               key=lambda k: self.snapshots[k].timestamp)

        return self.rollback_to_backup(latest_backup_path)

    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all available backup snapshots.

        Returns:
            List of backup information dictionaries
        """
        backups = []
        for backup_path, snapshot in self.snapshots.items():
            backups.append({
                "backup_path": backup_path,
                "datetime": snapshot.datetime_str,
                "reason": snapshot.recovery_reason,
                "file_size": snapshot.file_size,
                "config_file": snapshot.config_file_path
            })

        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x["datetime"], reverse=True)
        return backups

    def get_recovery_statistics(self) -> Dict[str, Any]:
        """
        Get recovery and backup statistics.

        Returns:
            Recovery statistics dictionary
        """
        return {
            "total_backups": len(self.snapshots),
            "recovery_attempts": self.recovery_stats.get("total_attempts", 0),
            "successful_recoveries": self.recovery_stats.get("successful_recoveries", 0),
            "failed_recoveries": self.recovery_stats.get("failed_recoveries", 0),
            "success_rate": self._calculate_success_rate(),
            "last_recovery": self.recovery_stats.get("last_recovery"),
            "backup_directory": str(self.backup_dir)
        }

    def validate_backup_integrity(self, backup_path: str) -> bool:
        """
        Validate the integrity of a backup file.

        Args:
            backup_path: Path to the backup file

        Returns:
            True if backup is valid and intact
        """
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                return False

            if backup_path not in self.snapshots:
                return False

            snapshot = self.snapshots[backup_path]

            # Check file size
            current_size = backup_file.stat().st_size
            if current_size != snapshot.file_size:
                return False

            # Check checksum
            current_checksum = self._calculate_checksum(backup_file)
            if current_checksum != snapshot.checksum:
                return False

            return True

        except Exception:
            return False

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate simple checksum for file integrity validation."""
        import hashlib

        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()[:16]
        except Exception:
            return "unknown"

    def _cleanup_old_backups(self) -> None:
        """Remove old backups to maintain maximum backup limit."""
        if len(self.snapshots) <= self.max_backups:
            return

        # Sort backups by timestamp (oldest first)
        sorted_backups = sorted(self.snapshots.items(),
                              key=lambda x: x[1].timestamp)

        # Remove oldest backups
        backups_to_remove = len(self.snapshots) - self.max_backups
        for i in range(backups_to_remove):
            backup_path, snapshot = sorted_backups[i]

            try:
                # Remove backup file
                backup_file = Path(backup_path)
                if backup_file.exists():
                    backup_file.unlink()

                # Remove from snapshots
                del self.snapshots[backup_path]
                print(f"🗑️ Removed old backup: {backup_path}")

            except Exception as e:
                print(f"Warning: Failed to remove old backup {backup_path}: {e}")

    def _load_snapshots(self) -> None:
        """Load existing snapshots metadata."""
        self.snapshots = {}

        if not self.snapshots_file.exists():
            return

        try:
            with open(self.snapshots_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for backup_path, snapshot_data in data.items():
                    self.snapshots[backup_path] = ConfigSnapshot(**snapshot_data)
        except Exception as e:
            print(f"Warning: Failed to load snapshots metadata: {e}")

    def _save_snapshots(self) -> None:
        """Save snapshots metadata to file."""
        try:
            snapshots_data = {}
            for backup_path, snapshot in self.snapshots.items():
                snapshots_data[backup_path] = asdict(snapshot)

            with open(self.snapshots_file, 'w', encoding='utf-8') as f:
                json.dump(snapshots_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"Warning: Failed to save snapshots metadata: {e}")

    def _load_recovery_stats(self) -> None:
        """Load recovery statistics."""
        default_stats = {
            "total_attempts": 0,
            "successful_recoveries": 0,
            "failed_recoveries": 0,
            "last_recovery": None
        }

        if not self.recovery_stats_file.exists():
            self.recovery_stats = default_stats
            return

        try:
            with open(self.recovery_stats_file, 'r', encoding='utf-8') as f:
                self.recovery_stats = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load recovery statistics: {e}")
            self.recovery_stats = default_stats

    def _save_recovery_stats(self) -> None:
        """Save recovery statistics to file."""
        try:
            with open(self.recovery_stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.recovery_stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Failed to save recovery statistics: {e}")

    def _update_recovery_stats(self, result: str, details: str) -> None:
        """Update recovery statistics."""
        self.recovery_stats["total_attempts"] += 1
        self.recovery_stats["last_recovery"] = {
            "timestamp": time.time(),
            "result": result,
            "details": details
        }

        if result == "rollback_success":
            self.recovery_stats["successful_recoveries"] += 1
        else:
            self.recovery_stats["failed_recoveries"] += 1

        self._save_recovery_stats()

    def _calculate_success_rate(self) -> float:
        """Calculate recovery success rate percentage."""
        total = self.recovery_stats.get("total_attempts", 0)
        if total == 0:
            return 0.0

        successful = self.recovery_stats.get("successful_recoveries", 0)
        return (successful / total) * 100