"""
Base Configuration Strategy

Abstract base class for model-specific configuration strategies.
Implements the strategy pattern as defined in the architecture document.

Each model type (SenseVoice, Piper VITS) extends this base class to provide
model-specific configuration handling and validation.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class ConfigValidationRule:
    """Configuration validation rule definition."""
    field_path: str
    rule_type: str  # 'required', 'type', 'range', 'enum'
    rule_params: Dict[str, Any]
    error_message: str


class BaseConfigStrategy(ABC):
    """
    Abstract base class for configuration strategies.

    Each model type extends this class to provide model-specific
    configuration handling and validation logic.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize strategy with configuration.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.validation_rules: List[ConfigValidationRule] = []
        self._setup_validation_rules()

    @abstractmethod
    def get_model_type(self) -> str:
        """Get the model type this strategy handles."""
        pass

    @abstractmethod
    def get_default_template(self) -> Dict[str, Any]:
        """Get the default configuration template for this model type."""
        pass

    @abstractmethod
    def validate_model_specific_config(self) -> bool:
        """Validate model-specific configuration parameters."""
        pass

    @abstractmethod
    def get_model_specific_fields(self) -> List[str]:
        """Get list of model-specific configuration field paths."""
        pass

    def _setup_validation_rules(self) -> None:
        """Setup validation rules for this strategy."""
        # Common validation rules that apply to all strategies
        self.validation_rules.extend([
            ConfigValidationRule(
                field_path="project.model_type",
                rule_type="required",
                rule_params={},
                error_message="Model type is required"
            ),
            ConfigValidationRule(
                field_path="project.model_type",
                rule_type="enum",
                rule_params={"values": [self.get_model_type()]},
                error_message=f"Model type must be '{self.get_model_type()}'"
            ),
            ConfigValidationRule(
                field_path="conversion_params.input_format",
                rule_type="required",
                rule_params={},
                error_message="Input format is required"
            ),
            ConfigValidationRule(
                field_path="conversion_params.input_format",
                rule_type="enum",
                rule_params={"values": ["onnx"]},
                error_message="Input format must be 'onnx'"
            ),
            ConfigValidationRule(
                field_path="conversion_params.output_format",
                rule_type="required",
                rule_params={},
                error_message="Output format is required"
            ),
            ConfigValidationRule(
                field_path="conversion_params.output_format",
                rule_type="enum",
                rule_params={"values": ["bpu"]},
                error_message="Output format must be 'bpu'"
            ),
        ])

    def validate(self) -> bool:
        """
        Validate configuration using strategy-specific rules.

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If validation fails with detailed error message
        """
        for rule in self.validation_rules:
            if not self._validate_rule(rule):
                raise ValueError(rule.error_message)

        # Validate model-specific configuration
        return self.validate_model_specific_config()

    def _validate_rule(self, rule: ConfigValidationRule) -> bool:
        """Validate a single configuration rule."""
        value = self._get_nested_value(rule.field_path)

        if rule.rule_type == "required":
            return value is not None and value != ""

        elif rule.rule_type == "type":
            expected_type = rule.rule_params.get("type")
            return isinstance(value, expected_type)

        elif rule.rule_type == "range":
            if value is None:
                return True
            min_val = rule.rule_params.get("min")
            max_val = rule.rule_params.get("max")
            if min_val is not None and value < min_val:
                return False
            if max_val is not None and value > max_val:
                return False
            return True

        elif rule.rule_type == "enum":
            if value is None:
                return True
            allowed_values = rule.rule_params.get("values", [])
            return value in allowed_values

        return True

    def _get_nested_value(self, field_path: str) -> Any:
        """Get nested value from configuration using dot notation."""
        keys = field_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None

        return value

    def set_nested_value(self, field_path: str, value: Any) -> None:
        """Set nested value in configuration using dot notation."""
        keys = field_path.split('.')
        config = self.config

        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        config[keys[-1]] = value

    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration."""
        return {
            "model_type": self.get_model_type(),
            "input_format": self._get_nested_value("conversion_params.input_format"),
            "output_format": self._get_nested_value("conversion_params.output_format"),
            "hardware_target": self._get_nested_value("hardware.target_device"),
            "model_specific_fields": self.get_model_specific_fields()
        }