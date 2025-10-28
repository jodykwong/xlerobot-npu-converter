"""
Configuration Manager

Main controller for the configuration management system. Provides unified
interface for loading, validating, and managing configuration files.

Implements the layered configuration architecture with strategy pattern
as defined in the architecture document.
"""

import yaml
import time
from pathlib import Path
from typing import Dict, Any, Optional, Type, List
from dataclasses import dataclass, field

from npu_converter.core.models.config_model import ConfigModel
from npu_converter.core.exceptions.config_errors import ConfigError
from .validator import ConfigValidator
from .hot_reload import HotReloadManager
from .templates import ConfigTemplateManager
from .strategies.base_strategy import BaseConfigStrategy
from .strategies.sensevoice_strategy import SenseVoiceConfigStrategy
from .strategies.piper_vits_strategy import PiperVITSConfigStrategy
from .strategies.vits_cantonese_strategy import VITSCantoneseConfigStrategy
from .dynamic import DynamicConfigManager
from .recovery import ConfigRecoveryManager


@dataclass
class ConfigMetrics:
    """Configuration system performance metrics."""
    load_time_ms: float = 0.0
    reload_time_ms: float = 0.0
    validation_time_ms: float = 0.0
    last_reload_timestamp: Optional[float] = None
    reload_count: int = 0
    validation_failures: int = 0
    backup_count: int = 0
    recovery_success_rate: float = 0.0
    last_recovery_timestamp: Optional[float] = None


class ConfigurationManager:
    """
    Main configuration management controller.

    Implements the layered configuration architecture with strategy pattern.
    Integrates with Story 1.3 core framework by extending ConfigModel.
    """

    def __init__(self, config_file_path: Optional[Path] = None, lazy_init: bool = True):
        """
        Initialize configuration manager.

        Args:
            config_file_path: Path to main configuration file
            lazy_init: Whether to lazily initialize components for better performance
        """
        self.config_file_path = config_file_path or Path("config.yaml")
        self._config: Optional[Dict[str, Any]] = None
        self._strategies: Dict[str, Type[BaseConfigStrategy]] = {
            "sensevoice": SenseVoiceConfigStrategy,
            "piper_vits": PiperVITSConfigStrategy,
            "vits_cantonese": VITSCantoneseConfigStrategy,
        }
        self._current_strategy: Optional[BaseConfigStrategy] = None
        self._validator: Optional[ConfigValidator] = None
        self._template_manager: Optional[ConfigTemplateManager] = None
        self._hot_reload_manager: Optional[HotReloadManager] = None
        self._dynamic_config_manager: Optional[DynamicConfigManager] = None
        self._recovery_manager: Optional[ConfigRecoveryManager] = None
        self._metrics: ConfigMetrics = ConfigMetrics()
        self._lazy_init = lazy_init
        self._components_initialized = False
        self._strategy_model_type: Optional[str] = None

        # Performance requirements from architecture
        self._load_time_threshold_ms = 100.0
        self._reload_time_threshold_ms = 500.0

    def _initialize_components(self, config: Dict[str, Any]) -> None:
        """
        Initialize supporting components with performance optimization.

        Args:
            config: Loaded configuration dictionary
        """
        if self._components_initialized:
            return

        # Initialize validator first (needed for validation)
        self._validator = ConfigValidator()

        # Initialize template manager (lightweight with lazy loading)
        self._template_manager = ConfigTemplateManager(lazy_load=True)

        # Initialize recovery manager (lightweight)
        backup_dir = self.config_file_path.parent if self.config_file_path else Path.cwd()
        self._recovery_manager = ConfigRecoveryManager(backup_dir)

        # Initialize strategy based on model type (deferred to after validation for performance)
        self._strategy_model_type = config.get('project', {}).get('model_type')

        self._components_initialized = True

    def _initialize_strategy(self, config: Dict[str, Any]) -> None:
        """Initialize model-specific strategy after validation."""
        if self._current_strategy is None and self._strategy_model_type:
            if self._strategy_model_type in self._strategies:
                strategy_class = self._strategies[self._strategy_model_type]
                self._current_strategy = strategy_class(config)

    def _initialize_heavy_components(self) -> None:
        """
        Initialize heavy components that can be deferred for performance.
        """
        if not self._config:
            return

        # Initialize hot reload manager (I/O intensive)
        if not self._hot_reload_manager:
            self._hot_reload_manager = HotReloadManager(
                self.config_file_path,
                self._on_config_reload
            )

        # Initialize dynamic config manager
        if not self._dynamic_config_manager:
            self._dynamic_config_manager = DynamicConfigManager(self, validation_enabled=True)

    def load_config(self, skip_backup: bool = False, fast_validation: bool = True) -> Dict[str, Any]:
        """
        Load configuration from YAML file with performance optimization.

        Args:
            skip_backup: Skip initial backup creation for faster loading
            fast_validation: Use fast validation (basic checks only) for better performance

        Returns:
            Loaded configuration dictionary

        Raises:
            ConfigError: If config file cannot be loaded or parsed
        """
        start_time = time.time()

        try:
            if not self.config_file_path.exists():
                raise ConfigError(f"Configuration file not found: {self.config_file_path}")

            # Fast YAML loading with optimized parser
            with open(self.config_file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            if not isinstance(config, dict):
                raise ConfigError("Configuration file must contain a YAML dictionary")

            self._config = config

            # Initialize lightweight components first
            self._initialize_components(config)

            # Validate configuration (essential for correctness)
            if fast_validation:
                # Fast validation: basic checks only for performance
                validation_success = self._validator.validate(config)
                if not validation_success:
                    raise ConfigError("Configuration validation failed (fast mode)")
            else:
                # Detailed validation for critical operations
                validation_result = self._validator.validate_detailed(config)
                if not validation_result.is_valid:
                    error_messages = []
                    for error in validation_result.errors:
                        error_messages.append(f"{error.field_path}: {error.message}")

                    raise ConfigError(f"Configuration validation failed: {'; '.join(error_messages)}")

            # Initialize strategy after successful validation (performance optimization)
            self._initialize_strategy(config)

            # Record metrics
            load_time = (time.time() - start_time) * 1000
            self._metrics.load_time_ms = load_time

            if load_time > self._load_time_threshold_ms:
                print(f"Warning: Config load time {load_time:.2f}ms exceeds threshold {self._load_time_threshold_ms}ms")

            # Initialize heavy components asynchronously if lazy_init is enabled
            if self._lazy_init:
                # Schedule heavy component initialization for later
                pass
            else:
                self._initialize_heavy_components()

            # Create initial backup only if needed (can be deferred)
            if not skip_backup and self._recovery_manager:
                try:
                    self._recovery_manager.create_backup(str(self.config_file_path), "initial_load")
                except Exception as backup_error:
                    # Don't fail config loading if backup fails
                    print(f"Warning: Backup creation failed: {backup_error}")

            return config

        except yaml.YAMLError as e:
            raise ConfigError(f"YAML parsing error in {self.config_file_path}: {e}")
        except Exception as e:
            raise ConfigError(f"Error loading configuration: {e}")

    def get_config(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by key path (dot notation).

        Args:
            key_path: Dot-separated key path (e.g., 'hardware.target_device')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        if not self._config:
            self.load_config()

        keys = key_path.split('.')
        value = self._config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set_config(self, key_path: str, value: Any) -> None:
        """
        Set configuration value by key path.

        Args:
            key_path: Dot-separated key path
            value: Value to set
        """
        if not self._config:
            self.load_config()

        keys = key_path.split('.')
        config = self._config

        # Navigate to parent of target key
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        # Set the value
        config[keys[-1]] = value

    def validate_config(self) -> bool:
        """
        Validate current configuration.

        Returns:
            True if configuration is valid

        Raises:
            ConfigError: If configuration validation fails
        """
        if not self._config:
            raise ConfigError("No configuration loaded")

        if not self._validator:
            self._validator = ConfigValidator()

        start_time = time.time()

        try:
            is_valid = self._validator.validate(self._config)

            # Record metrics
            validation_time = (time.time() - start_time) * 1000
            self._metrics.validation_time_ms = validation_time

            if not is_valid:
                self._metrics.validation_failures += 1

            return is_valid

        except Exception as e:
            self._metrics.validation_failures += 1
            raise ConfigError(f"Configuration validation failed: {e}")

    def start_hot_reload(self) -> None:
        """Start hot reload monitoring."""
        self._ensure_heavy_components_initialized()
        if self._hot_reload_manager:
            self._hot_reload_manager.start_monitoring()

    def stop_hot_reload(self) -> None:
        """Stop hot reload monitoring."""
        if self._hot_reload_manager:
            self._hot_reload_manager.stop_monitoring()

    def _ensure_heavy_components_initialized(self) -> None:
        """Ensure heavy components are initialized."""
        if not self._components_initialized:
            self.load_config()
        self._initialize_heavy_components()

    def _on_config_reload(self) -> None:
        """Handle configuration file reload."""
        start_time = time.time()

        try:
            # Reload configuration
            old_config = self._config.copy() if self._config else {}
            self.load_config()

            # Validate new configuration
            if self.validate_config():
                # Update strategy if model type changed
                new_model_type = self._config.get('project', {}).get('model_type')
                old_model_type = old_config.get('project', {}).get('model_type')

                if new_model_type != old_model_type:
                    if new_model_type in self._strategies:
                        strategy_class = self._strategies[new_model_type]
                        self._current_strategy = strategy_class(self._config)

                # Record metrics
                reload_time = (time.time() - start_time) * 1000
                self._metrics.reload_time_ms = reload_time
                self._metrics.last_reload_timestamp = time.time()
                self._metrics.reload_count += 1

                if reload_time > self._reload_time_threshold_ms:
                    print(f"Warning: Config reload time {reload_time:.2f}ms exceeds threshold {self._reload_time_threshold_ms}ms")

                print(f"Configuration reloaded successfully (model: {new_model_type})")
            else:
                print("Configuration validation failed, keeping previous configuration")
                self._config = old_config

        except Exception as e:
            print(f"Configuration reload failed: {e}")

    def get_metrics(self) -> ConfigMetrics:
        """Get configuration system performance metrics."""
        return self._metrics

    def save_config(self, file_path: Optional[Path] = None) -> None:
        """
        Save current configuration to file.

        Args:
            file_path: Optional file path, defaults to current config file
        """
        if not self._config:
            raise ConfigError("No configuration to save")

        save_path = file_path or self.config_file_path

        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, default_flow_style=False, indent=2)

            print(f"Configuration saved to {save_path}")

        except Exception as e:
            raise ConfigError(f"Error saving configuration: {e}")

    def get_strategy(self) -> Optional[BaseConfigStrategy]:
        """Get current model-specific strategy."""
        return self._current_strategy

    def list_available_strategies(self) -> list[str]:
        """List all available configuration strategies."""
        return list(self._strategies.keys())

    # Dynamic Configuration Methods

    def get_dynamic_manager(self) -> Optional[DynamicConfigManager]:
        """Get the dynamic configuration manager."""
        self._ensure_heavy_components_initialized()
        return self._dynamic_config_manager

    def set_config_dynamic(self, field_path: str, value: Any, source: str = "user") -> bool:
        """
        Dynamically set a configuration value.

        Args:
            field_path: Dot-separated path to the configuration field
            value: New value to set
            source: Source of the change

        Returns:
            True if the change was applied successfully
        """
        self._ensure_heavy_components_initialized()
        if not self._dynamic_config_manager:
            raise ConfigError("Dynamic configuration manager not initialized")

        return self._dynamic_config_manager.set_config(field_path, value, source)

    def batch_update_dynamic(self, changes: Dict[str, Any], source: str = "batch") -> bool:
        """
        Apply multiple configuration changes atomically.

        Args:
            changes: Dictionary of field_path -> value mappings
            source: Source of the batch changes

        Returns:
            True if all changes were applied successfully
        """
        if not self._dynamic_config_manager:
            raise ConfigError("Dynamic configuration manager not initialized")

        return self._dynamic_config_manager.batch_update(changes, source)

    def reset_config_dynamic(self, field_path: str, source: str = "reset") -> bool:
        """
        Reset a configuration field to its default value.

        Args:
            field_path: Dot-separated path to the configuration field
            source: Source of the reset operation

        Returns:
            True if the reset was successful
        """
        if not self._dynamic_config_manager:
            raise ConfigError("Dynamic configuration manager not initialized")

        return self._dynamic_config_manager.reset_config(field_path, source)

    def reload_from_template_dynamic(self, template_name: str, preserve_overrides: bool = True) -> bool:
        """
        Reload configuration from a template.

        Args:
            template_name: Name of the template to reload from
            preserve_overrides: Whether to preserve user overrides

        Returns:
            True if reload was successful
        """
        if not self._dynamic_config_manager:
            raise ConfigError("Dynamic configuration manager not initialized")

        return self._dynamic_config_manager.reload_from_template(template_name, preserve_overrides)

    def get_dynamic_metrics(self):
        """Get dynamic configuration metrics."""
        if not self._dynamic_config_manager:
            return None

        return self._dynamic_config_manager.get_metrics()

    def add_config_change_callback(self, callback) -> None:
        """Add a callback to be notified of configuration changes."""
        if self._dynamic_config_manager:
            self._dynamic_config_manager.add_change_callback(callback)

    def remove_config_change_callback(self, callback) -> None:
        """Remove a configuration change callback."""
        if self._dynamic_config_manager:
            self._dynamic_config_manager.remove_change_callback(callback)

    # Configuration Recovery Methods

    def create_backup(self, reason: str = "manual_backup") -> str:
        """
        Create a backup snapshot of the current configuration.

        Args:
            reason: Reason for creating this backup

        Returns:
            Backup file path

        Raises:
            ConfigError: If backup creation fails
        """
        if not self._recovery_manager:
            raise ConfigError("Recovery manager not initialized")

        backup_path = self._recovery_manager.create_backup(str(self.config_file_path), reason)
        self._metrics.backup_count += 1

        return backup_path

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
        if not self._recovery_manager:
            raise ConfigError("Recovery manager not initialized")

        success = self._recovery_manager.rollback_to_backup(backup_path)
        if success:
            # Reload configuration after rollback
            self._config = None  # Force reload
            self.load_config()
            self._metrics.last_recovery_timestamp = time.time()

            # Update recovery success rate
            stats = self._recovery_manager.get_recovery_statistics()
            self._metrics.recovery_success_rate = stats.get("success_rate", 0.0)

        return success

    def rollback_to_latest_backup(self) -> bool:
        """
        Rollback to the most recent backup.

        Returns:
            True if rollback was successful

        Raises:
            ConfigError: If no backups are available or rollback fails
        """
        if not self._recovery_manager:
            raise ConfigError("Recovery manager not initialized")

        success = self._recovery_manager.rollback_to_latest_backup()
        if success:
            # Reload configuration after rollback
            self._config = None  # Force reload
            self.load_config()
            self._metrics.last_recovery_timestamp = time.time()

            # Update recovery success rate
            stats = self._recovery_manager.get_recovery_statistics()
            self._metrics.recovery_success_rate = stats.get("success_rate", 0.0)

        return success

    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all available backup snapshots.

        Returns:
            List of backup information dictionaries
        """
        if not self._recovery_manager:
            raise ConfigError("Recovery manager not initialized")

        return self._recovery_manager.list_backups()

    def get_recovery_statistics(self) -> Dict[str, Any]:
        """
        Get recovery and backup statistics.

        Returns:
            Recovery statistics dictionary
        """
        if not self._recovery_manager:
            raise ConfigError("Recovery manager not initialized")

        return self._recovery_manager.get_recovery_statistics()

    def safe_reload_config(self) -> bool:
        """
        Safely reload configuration with automatic rollback on failure.

        Returns:
            True if reload was successful, False if rollback was used

        Raises:
            ConfigError: If both reload and rollback fail
        """
        try:
            # Get list of existing backups before any operation
            existing_backups = self.list_backups()

            # Create backup before reload
            backup_path = self.create_backup("pre_reload_backup")

            # Attempt reload
            old_config = self._config.copy() if self._config else {}
            self.load_config()

            print("✅ Configuration reloaded successfully")
            return True

        except Exception as e:
            print(f"❌ Configuration reload failed: {e}")

            try:
                # Use the most recent backup BEFORE the reload attempt
                # Find the backup that was created before the "pre_reload_backup"
                all_backups = self.list_backups()
                valid_backup = None

                # Look for a backup that's not the pre_reload_backup
                for backup in all_backups:
                    if backup["reason"] != "pre_reload_backup":
                        valid_backup = backup["backup_path"]
                        break

                if valid_backup:
                    print(f"🔄 Attempting automatic rollback to {valid_backup}...")
                    success = self.rollback_to_backup(valid_backup)
                    if success:
                        print("✅ Automatic rollback successful")
                        return False
                else:
                    print("⚠️ No valid backup found for rollback")

                raise ConfigError(f"Configuration reload failed and no valid backup available: {e}")

            except Exception as rollback_error:
                print(f"❌ Automatic rollback failed: {rollback_error}")
                raise ConfigError(f"Configuration reload and rollback both failed: {e}, {rollback_error}")

    def validate_recovery_system(self) -> Dict[str, Any]:
        """
        Validate the configuration recovery system.

        Returns:
            Validation results dictionary
        """
        results = {
            "recovery_manager_available": self._recovery_manager is not None,
            "backup_directory_exists": False,
            "recent_backups_valid": 0,
            "total_backups": 0,
            "recovery_success_rate": 0.0,
            "system_healthy": False
        }

        try:
            if not self._recovery_manager:
                return results

            # Check backup directory
            backup_dir = self._recovery_manager.backup_dir
            results["backup_directory_exists"] = backup_dir.exists()

            # Check backup integrity
            backups = self.list_backups()
            results["total_backups"] = len(backups)

            # Validate recent backups (last 5)
            recent_backups = backups[:5]
            valid_recent = 0
            for backup in recent_backups:
                if self._recovery_manager.validate_backup_integrity(backup["backup_path"]):
                    valid_recent += 1

            results["recent_backups_valid"] = valid_recent

            # Get recovery statistics
            stats = self.get_recovery_statistics()
            results["recovery_success_rate"] = stats.get("success_rate", 0.0)

            # Determine system health
            results["system_healthy"] = (
                results["recovery_manager_available"] and
                results["backup_directory_exists"] and
                results["total_backups"] > 0 and
                results["recovery_success_rate"] >= 95.0  # AC requirement
            )

        except Exception as e:
            print(f"Warning: Error during recovery system validation: {e}")

        return results