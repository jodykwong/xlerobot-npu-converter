"""
Dynamic Configuration Manager

Provides runtime configuration adjustment capabilities.
Allows configuration changes without system restart.

Implements the dynamic configuration layer as defined in the
architecture document with thread-safe operations.
"""

import threading
import time
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field
from pathlib import Path

from npu_converter.core.exceptions.config_errors import ConfigError


@dataclass
class ConfigChange:
    """Represents a configuration change operation."""
    field_path: str
    old_value: Any
    new_value: Any
    timestamp: float
    source: str = "dynamic_update"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DynamicConfigMetrics:
    """Dynamic configuration performance metrics."""
    total_changes: int = 0
    successful_changes: int = 0
    failed_changes: int = 0
    last_change_timestamp: Optional[float] = None
    average_change_time_ms: float = 0.0
    change_history: List[ConfigChange] = field(default_factory=list)


class DynamicConfigManager:
    """
    Dynamic configuration management system.

    Provides thread-safe runtime configuration adjustment capabilities
    with validation, change tracking, and rollback functionality.
    """

    def __init__(self, config_manager, validation_enabled: bool = True):
        """
        Initialize dynamic configuration manager.

        Args:
            config_manager: Main configuration manager instance
            validation_enabled: Whether to validate changes before applying
        """
        self._config_manager = config_manager
        self._validation_enabled = validation_enabled
        self._lock = threading.RLock()
        self._change_callbacks: List[Callable[[ConfigChange], None]] = []
        self._metrics = DynamicConfigMetrics()
        self._change_history_limit = 100

    def set_config(self, field_path: str, value: Any, source: str = "user") -> bool:
        """
        Dynamically set a configuration value.

        Args:
            field_path: Dot-separated path to the configuration field
            value: New value to set
            source: Source of the change (for tracking)

        Returns:
            True if the change was applied successfully

        Raises:
            ConfigError: If the change cannot be applied
        """
        start_time = time.time()

        with self._lock:
            try:
                # Get current value
                old_value = self._config_manager.get_config(field_path)

                # Validate the change if validation is enabled
                if self._validation_enabled:
                    self._validate_change(field_path, old_value, value)

                # Apply the change
                self._config_manager.set_config(field_path, value)

                # Record the change
                change = ConfigChange(
                    field_path=field_path,
                    old_value=old_value,
                    new_value=value,
                    timestamp=time.time(),
                    source=source,
                    metadata={"validation_enabled": self._validation_enabled}
                )

                self._record_change(change)
                self._notify_callbacks(change)

                # Update metrics
                change_time = (time.time() - start_time) * 1000
                self._update_metrics(change_time, True)

                return True

            except Exception as e:
                # Update metrics for failed change
                change_time = (time.time() - start_time) * 1000
                self._update_metrics(change_time, False)

                if isinstance(e, ConfigError):
                    raise
                else:
                    raise ConfigError(f"Failed to set configuration '{field_path}': {e}")

    def get_config(self, field_path: str) -> Any:
        """
        Get a configuration value.

        Args:
            field_path: Dot-separated path to the configuration field

        Returns:
            Current configuration value
        """
        with self._lock:
            return self._config_manager.get_config(field_path)

    def batch_update(self, changes: Dict[str, Any], source: str = "batch") -> bool:
        """
        Apply multiple configuration changes atomically.

        Args:
            changes: Dictionary of field_path -> value mappings
            source: Source of the batch changes

        Returns:
            True if all changes were applied successfully

        Raises:
            ConfigError: If any change cannot be applied
        """
        start_time = time.time()
        applied_changes = []

        with self._lock:
            try:
                # Validate all changes first and collect old values
                old_values = {}
                if self._validation_enabled:
                    for field_path, new_value in changes.items():
                        old_value = self._config_manager.get_config(field_path)
                        old_values[field_path] = old_value
                        self._validate_change(field_path, old_value, new_value)

                # Apply all changes
                for field_path, new_value in changes.items():
                    old_value = old_values.get(field_path)
                    self._config_manager.set_config(field_path, new_value)

                    change = ConfigChange(
                        field_path=field_path,
                        old_value=old_value,
                        new_value=new_value,
                        timestamp=time.time(),
                        source=source,
                        metadata={"batch_update": True}
                    )

                    applied_changes.append(change)

                # Record all changes
                for change in applied_changes:
                    self._record_change(change)
                    self._notify_callbacks(change)

                # Update metrics
                change_time = (time.time() - start_time) * 1000
                self._metrics.total_changes += len(changes)
                self._metrics.successful_changes += len(changes)
                self._metrics.last_change_timestamp = time.time()
                self._update_average_change_time(change_time)

                return True

            except Exception as e:
                # Rollback applied changes if batch fails
                for change in reversed(applied_changes):
                    try:
                        self._config_manager.set_config(change.field_path, change.old_value)
                    except Exception as rollback_error:
                        print(f"Warning: Failed to rollback change '{change.field_path}': {rollback_error}")

                if isinstance(e, ConfigError):
                    raise
                else:
                    raise ConfigError(f"Batch update failed: {e}")

    def reset_config(self, field_path: str, source: str = "reset") -> bool:
        """
        Reset a configuration field to its default value.

        Args:
            field_path: Dot-separated path to the configuration field
            source: Source of the reset operation

        Returns:
            True if the reset was successful

        Raises:
            ConfigError: If the field cannot be reset
        """
        try:
            # Get default value from template or validation rules
            default_value = self._get_default_value(field_path)

            if default_value is not None:
                return self.set_config(field_path, default_value, source)
            else:
                raise ConfigError(f"No default value available for field: {field_path}")

        except Exception as e:
            if isinstance(e, ConfigError):
                raise
            else:
                raise ConfigError(f"Failed to reset configuration '{field_path}': {e}")

    def reload_from_template(self, template_name: str, preserve_overrides: bool = True) -> bool:
        """
        Reload configuration from a template.

        Args:
            template_name: Name of the template to reload from
            preserve_overrides: Whether to preserve user overrides

        Returns:
            True if reload was successful

        Raises:
            ConfigError: If reload fails
        """
        try:
            with self._lock:
                # Get current configuration
                current_config = self._config_manager._config.copy()

                # Load template configuration
                template_config = self._config_manager._template_manager.apply_template(template_name)

                if not template_config:
                    raise ConfigError(f"Template not found: {template_name}")

                # Determine changes to apply
                changes_to_apply = {}

                if preserve_overrides:
                    # Only apply differences from template
                    changes_to_apply = self._get_template_changes(current_config, template_config)
                else:
                    # Apply entire template
                    changes_to_apply = template_config

                # Apply changes as batch
                success = self.batch_update(changes_to_apply, source=f"template_reload:{template_name}")

                if success:
                    print(f"Successfully reloaded configuration from template: {template_name}")

                return success

        except Exception as e:
            if isinstance(e, ConfigError):
                raise
            else:
                raise ConfigError(f"Failed to reload from template '{template_name}': {e}")

    def add_change_callback(self, callback: Callable[[ConfigChange], None]) -> None:
        """
        Add a callback to be notified of configuration changes.

        Args:
            callback: Function to call when configuration changes
        """
        with self._lock:
            self._change_callbacks.append(callback)

    def remove_change_callback(self, callback: Callable[[ConfigChange], None]) -> None:
        """
        Remove a configuration change callback.

        Args:
            callback: Function to remove from callbacks
        """
        with self._lock:
            if callback in self._change_callbacks:
                self._change_callbacks.remove(callback)

    def get_change_history(self, limit: Optional[int] = None) -> List[ConfigChange]:
        """
        Get the history of configuration changes.

        Args:
            limit: Maximum number of changes to return

        Returns:
            List of configuration changes
        """
        with self._lock:
            history = self._metrics.change_history.copy()
            if limit:
                return history[-limit:]
            return history

    def get_metrics(self) -> DynamicConfigMetrics:
        """
        Get dynamic configuration metrics.

        Returns:
            Current metrics
        """
        with self._lock:
            return DynamicConfigMetrics(
                total_changes=self._metrics.total_changes,
                successful_changes=self._metrics.successful_changes,
                failed_changes=self._metrics.failed_changes,
                last_change_timestamp=self._metrics.last_change_timestamp,
                average_change_time_ms=self._metrics.average_change_time_ms,
                change_history=self._metrics.change_history.copy()
            )

    def _validate_change(self, field_path: str, old_value: Any, new_value: Any) -> None:
        """Validate a configuration change."""
        # Type validation
        if old_value is not None and type(old_value) != type(new_value):
            raise ConfigError(f"Type mismatch for '{field_path}': expected {type(old_value).__name__}, got {type(new_value).__name__}")

        # Range validation for numeric values
        if isinstance(new_value, (int, float)):
            self._validate_numeric_range(field_path, new_value)

        # Enum validation
        self._validate_enum_values(field_path, new_value)

        # Model-specific validation
        self._validate_model_specific(field_path, new_value)

    def _validate_numeric_range(self, field_path: str, value: Union[int, float]) -> None:
        """Validate numeric value ranges."""
        # Define validation rules for common numeric fields
        range_rules = {
            "performance.target_latency_ms": (1, 10000),
            "conversion_params.batch_size": (1, 32),
            "hardware.compute_units": (1, 64),
            "model_specific.sensevoice.sample_rate": (8000, 48000),
            "model_specific.piper_vits.sample_rate": (16000, 48000),
        }

        if field_path in range_rules:
            min_val, max_val = range_rules[field_path]
            if not (min_val <= value <= max_val):
                raise ConfigError(f"Value {value} for '{field_path}' is out of range [{min_val}, {max_val}]")

    def _validate_enum_values(self, field_path: str, value: Any) -> None:
        """Validate enum values."""
        enum_rules = {
            "project.model_type": ["sensevoice", "piper_vits"],
            "hardware.target_device": ["horizon_x5"],
            "hardware.optimization_level": ["O0", "O1", "O2", "O3"],
            "conversion_params.input_format": ["onnx"],
            "conversion_params.output_format": ["bpu"],
            "conversion_params.precision": ["int8", "int16", "float16"],
        }

        if field_path in enum_rules and value not in enum_rules[field_path]:
            raise ConfigError(f"Invalid value '{value}' for '{field_path}'. Must be one of: {enum_rules[field_path]}")

    def _validate_model_specific(self, field_path: str, value: Any) -> None:
        """Validate model-specific configuration changes."""
        # Add model-specific validation logic here
        if field_path.startswith("model_specific."):
            # Validate based on current model type
            model_type = self._config_manager.get_config("project.model_type")
            if model_type == "sensevoice":
                self._validate_sensevoice_specific(field_path, value)
            elif model_type == "piper_vits":
                self._validate_piper_vits_specific(field_path, value)

    def _validate_sensevoice_specific(self, field_path: str, value: Any) -> None:
        """Validate SenseVoice-specific configuration."""
        sensevoice_rules = {
            "model_specific.sensevoice.vocab_size": (1000, 50000),
            "model_specific.sensevoice.mel_bins": (40, 128),
        }

        if field_path in sensevoice_rules and isinstance(value, (int, float)):
            min_val, max_val = sensevoice_rules[field_path]
            if not (min_val <= value <= max_val):
                raise ConfigError(f"SenseVoice value {value} for '{field_path}' is out of range [{min_val}, {max_val}]")

    def _validate_piper_vits_specific(self, field_path: str, value: Any) -> None:
        """Validate Piper VITS-specific configuration."""
        piper_rules = {
            "model_specific.piper_vits.mel_channels": (40, 128),
            "model_specific.piper_vits.num_speakers": (1, 1000),
        }

        if field_path in piper_rules and isinstance(value, (int, float)):
            min_val, max_val = piper_rules[field_path]
            if not (min_val <= value <= max_val):
                raise ConfigError(f"Piper VITS value {value} for '{field_path}' is out of range [{min_val}, {max_val}]")

    def _record_change(self, change: ConfigChange) -> None:
        """Record a configuration change in history."""
        self._metrics.change_history.append(change)

        # Limit history size
        if len(self._metrics.change_history) > self._change_history_limit:
            self._metrics.change_history.pop(0)

    def _notify_callbacks(self, change: ConfigChange) -> None:
        """Notify all registered callbacks of a change."""
        for callback in self._change_callbacks:
            try:
                callback(change)
            except Exception as e:
                print(f"Warning: Configuration change callback failed: {e}")

    def _update_metrics(self, change_time: float, success: bool) -> None:
        """Update performance metrics."""
        self._metrics.total_changes += 1
        self._metrics.last_change_timestamp = time.time()

        if success:
            self._metrics.successful_changes += 1
        else:
            self._metrics.failed_changes += 1

        self._update_average_change_time(change_time)

    def _update_average_change_time(self, change_time: float) -> None:
        """Update average change time metric."""
        if self._metrics.total_changes == 1:
            self._metrics.average_change_time_ms = change_time
        else:
            # Exponential moving average
            alpha = 0.1
            self._metrics.average_change_time_ms = (
                alpha * change_time +
                (1 - alpha) * self._metrics.average_change_time_ms
            )

    def _get_default_value(self, field_path: str) -> Any:
        """Get default value for a configuration field."""
        # Try to get from validation rules
        validator = self._config_manager._validator
        if validator:
            rules = validator.get_validation_rules()

            # Parse field path to get section and field
            parts = field_path.split('.')
            if len(parts) >= 2:
                section = parts[0]
                field = parts[1]

                if section in rules:
                    for rule in rules[section]:
                        if rule.get('field') == field and 'default' in rule:
                            return rule['default']

        return None

    def _get_template_changes(self, current_config: Dict[str, Any], template_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get changes between current config and template config."""
        changes = {}

        def find_changes(current: Dict[str, Any], template: Dict[str, Any], prefix: str = ""):
            for key, template_value in template.items():
                current_path = f"{prefix}.{key}" if prefix else key

                if key not in current:
                    # Field doesn't exist in current config, add it
                    changes[current_path] = template_value
                elif isinstance(template_value, dict) and isinstance(current.get(key), dict):
                    # Recursively compare nested dictionaries
                    find_changes(current[key], template_value, current_path)
                elif current[key] != template_value:
                    # Value differs, update it
                    changes[current_path] = template_value

        find_changes(current_config, template_config)
        return changes