"""
Validation Rules Model

Configuration validation rules and constraints.
Provides type-safe validation rule definitions.

Implements the validation layer of the configuration architecture
as defined in the architecture document.
"""

from dataclasses import dataclass, field
from typing import Any, List, Dict, Union, Optional, Callable
from enum import Enum
from pathlib import Path


class ValidationRuleType(Enum):
    """Types of validation rules."""
    REQUIRED = "required"
    TYPE = "type"
    PATTERN = "pattern"
    RANGE = "range"
    ENUM = "enum"
    CUSTOM = "custom"
    LENGTH = "length"
    CONDITION = "condition"


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationRule:
    """Individual validation rule definition."""
    field_path: str
    rule_type: ValidationRuleType
    rule_params: Dict[str, Any] = field(default_factory=dict)
    error_message: str = ""
    suggestion: str = ""
    severity: ValidationSeverity = ValidationSeverity.ERROR
    custom_validator: Optional[Callable[[Any], bool]] = None

    def validate(self, value: Any, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Validate a value against this rule.

        Args:
            value: Value to validate
            context: Optional context for validation

        Returns:
            True if validation passes
        """
        if self.rule_type == ValidationRuleType.REQUIRED:
            return value is not None and value != ""

        elif self.rule_type == ValidationRuleType.TYPE:
            expected_type = self.rule_params.get("type")
            return isinstance(value, expected_type)

        elif self.rule_type == ValidationRuleType.PATTERN:
            import re
            pattern = self.rule_params.get("pattern")
            if isinstance(value, str) and pattern:
                return bool(re.match(pattern, value))
            return False

        elif self.rule_type == ValidationRuleType.RANGE:
            min_val = self.rule_params.get("min")
            max_val = self.rule_params.get("max")
            if value is None:
                return True
            if min_val is not None and value < min_val:
                return False
            if max_val is not None and value > max_val:
                return False
            return True

        elif self.rule_type == ValidationRuleType.ENUM:
            allowed_values = self.rule_params.get("values", [])
            return value in allowed_values

        elif self.rule_type == ValidationRuleType.LENGTH:
            min_len = self.rule_params.get("min_length")
            max_len = self.rule_params.get("max_length")
            if isinstance(value, (str, list)):
                value_len = len(value)
                if min_len is not None and value_len < min_len:
                    return False
                if max_len is not None and value_len > max_len:
                    return False
            return True

        elif self.rule_type == ValidationRuleType.CONDITION:
            if self.custom_validator:
                return self.custom_validator(value, context)
            return True

        return True

    def get_description(self) -> str:
        """Get human-readable description of the rule."""
        desc_parts = [f"Field '{self.field_path}'"]

        if self.rule_type == ValidationRuleType.REQUIRED:
            desc_parts.append("is required")
        elif self.rule_type == ValidationRuleType.TYPE:
            expected_type = self.rule_params.get("type", "unknown")
            desc_parts.append(f"must be of type {expected_type.__name__}")
        elif self.rule_type == ValidationRuleType.PATTERN:
            pattern = self.rule_params.get("pattern", "")
            desc_parts.append(f"must match pattern: {pattern}")
        elif self.rule_type == ValidationRuleType.RANGE:
            min_val = self.rule_params.get("min")
            max_val = self.rule_params.get("max")
            if min_val is not None and max_val is not None:
                desc_parts.append(f"must be between {min_val} and {max_val}")
            elif min_val is not None:
                desc_parts.append(f"must be >= {min_val}")
            elif max_val is not None:
                desc_parts.append(f"must be <= {max_val}")
        elif self.rule_type == ValidationRuleType.ENUM:
            values = self.rule_params.get("values", [])
            desc_parts.append(f"must be one of: {values}")
        elif self.rule_type == ValidationRuleType.LENGTH:
            min_len = self.rule_params.get("min_length")
            max_len = self.rule_params.get("max_length")
            if min_len is not None and max_len is not None:
                desc_parts.append(f"must have length between {min_len} and {max_len}")
            elif min_len is not None:
                desc_parts.append(f"must have length >= {min_len}")
            elif max_len is not None:
                desc_parts.append(f"must have length <= {max_len}")

        return " ".join(desc_parts)


@dataclass
class ValidationRuleSet:
    """Collection of validation rules for a configuration section."""
    section_name: str
    rules: List[ValidationRule] = field(default_factory=list)
    description: str = ""

    def add_rule(self, rule: ValidationRule) -> None:
        """Add a validation rule to this set."""
        self.rules.append(rule)

    def add_required_field(self, field_path: str, message: Optional[str] = None) -> None:
        """Add a required field validation rule."""
        rule = ValidationRule(
            field_path=field_path,
            rule_type=ValidationRuleType.REQUIRED,
            error_message=message or f"Field '{field_path}' is required",
            suggestion=f"Ensure '{field_path}' is included in configuration"
        )
        self.add_rule(rule)

    def add_type_rule(self, field_path: str, expected_type: type,
                      message: Optional[str] = None) -> None:
        """Add a type validation rule."""
        rule = ValidationRule(
            field_path=field_path,
            rule_type=ValidationRuleType.TYPE,
            rule_params={"type": expected_type},
            error_message=message or f"Field '{field_path}' must be of type {expected_type.__name__}",
            suggestion=f"Change '{field_path}' to a {expected_type.__name__} value"
        )
        self.add_rule(rule)

    def add_enum_rule(self, field_path: str, allowed_values: List[Any],
                      message: Optional[str] = None) -> None:
        """Add an enum validation rule."""
        rule = ValidationRule(
            field_path=field_path,
            rule_type=ValidationRuleType.ENUM,
            rule_params={"values": allowed_values},
            error_message=message or f"Field '{field_path}' must be one of: {allowed_values}",
            suggestion=f"Change '{field_path}' to one of the allowed values"
        )
        self.add_rule(rule)

    def add_range_rule(self, field_path: str, min_val: Optional[Any] = None,
                       max_val: Optional[Any] = None,
                       message: Optional[str] = None) -> None:
        """Add a range validation rule."""
        rule_params = {}
        if min_val is not None:
            rule_params["min"] = min_val
        if max_val is not None:
            rule_params["max"] = max_val

        rule = ValidationRule(
            field_path=field_path,
            rule_type=ValidationRuleType.RANGE,
            rule_params=rule_params,
            error_message=message or f"Field '{field_path}' is out of valid range",
            suggestion=f"Ensure '{field_path}' is within the specified range"
        )
        self.add_rule(rule)

    def add_pattern_rule(self, field_path: str, pattern: str,
                        message: Optional[str] = None) -> None:
        """Add a pattern validation rule."""
        rule = ValidationRule(
            field_path=field_path,
            rule_type=ValidationRule.PATTERN,
            rule_params={"pattern": pattern},
            error_message=message or f"Field '{field_path}' does not match required pattern",
            suggestion=f"Ensure '{field_path}' matches pattern: {pattern}"
        )
        self.add_rule(rule)

    def add_custom_rule(self, field_path: str, validator: Callable[[Any, Optional[Dict[str, Any]]], bool],
                        message: Optional[str] = None,
                        severity: ValidationSeverity = ValidationSeverity.ERROR) -> None:
        """Add a custom validation rule."""
        rule = ValidationRule(
            field_path=field_path,
            rule_type=ValidationRuleType.CUSTOM,
            custom_validator=validator,
            error_message=message or f"Field '{field_path}' failed custom validation",
            suggestion="Check field value and configuration context",
            severity=severity
        )
        self.add_rule(rule)

    def validate(self, config: Dict[str, Any]) -> List[str]:
        """
        Validate configuration against all rules in this set.

        Args:
            config: Configuration section to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        for rule in self.rules:
            # Get nested value using dot notation
            keys = rule.field_path.split('.')
            value = config
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    value = None
                    break

            if not rule.validate(value, config):
                errors.append(rule.error_message)

        return errors

    def get_all_rules(self) -> List[ValidationRule]:
        """Get all validation rules in this set."""
        return self.rules.copy()

    def get_rules_by_severity(self, severity: ValidationSeverity) -> List[ValidationRule]:
        """Get rules filtered by severity level."""
        return [rule for rule in self.rules if rule.severity == severity]

    def count_rules(self) -> int:
        """Count total number of rules."""
        return len(self.rules)

    def count_rules_by_severity(self) -> Dict[ValidationSeverity, int]:
        """Count rules by severity level."""
        counts = {severity: 0 for severity in ValidationSeverity}
        for rule in self.rules:
            counts[rule.severity] += 1
        return counts


class ValidationRules:
    """
    Configuration validation rules manager.

    Manages validation rule sets for different configuration sections
    and provides comprehensive validation capabilities.
    """

    def __init__(self):
        """Initialize validation rules manager."""
        self._rule_sets: Dict[str, ValidationRuleSet] = {}
        self._setup_default_rules()

    def _setup_default_rules(self) -> None:
        """Setup default validation rules for common sections."""
        # Project section rules
        project_rules = ValidationRuleSet(
            section_name="project",
            description="Project configuration validation rules"
        )
        project_rules.add_required_field("name", "Project name is required")
        project_rules.add_type_rule("name", str, "Project name must be a string")
        project_rules.add_pattern_rule("name", r"^[a-zA-Z][a-zA-Z0-9_-]*$", "Project name must contain only letters, numbers, underscores, and hyphens")
        project_rules.add_required_field("version", "Project version is required")
        project_rules.add_pattern_rule("version", r"^\d+\.\d+\.\d+$", "Version must follow semantic versioning (e.g., 1.0.0)")
        project_rules.add_required_field("model_type", "Model type is required")
        project_rules.add_enum_rule("model_type", ["sensevoice", "piper_vits"], "Model type must be 'sensevoice' or 'piper_vits'")
        self._rule_sets["project"] = project_rules

        # Hardware section rules
        hardware_rules = ValidationRuleSet(
            section_name="hardware",
            description="Hardware configuration validation rules"
        )
        hardware_rules.add_required_field("target_device", "Target device is required")
        hardware_rules.add_enum_rule("target_device", ["horizon_x5"], "Target device must be 'horizon_x5'")
        hardware_rules.add_enum_rule("optimization_level", ["O0", "O1", "O2", "O3"], "Optimization level must be one of: O0, O1, O2, O3")
        self._rule_sets["hardware"] = hardware_rules

        # Conversion parameters rules
        conversion_rules = ValidationRuleSet(
            section_name="conversion_params",
            description="Conversion parameters validation rules"
        )
        conversion_rules.add_required_field("input_format", "Input format is required")
        conversion_rules.add_enum_rule("input_format", ["onnx"], "Input format must be 'onnx'")
        conversion_rules.add_required_field("output_format", "Output format is required")
        conversion_rules.add_enum_rule("output_format", ["bpu"], "Output format must be 'bpu'")
        conversion_rules.add_type_rule("batch_size", int, "Batch size must be an integer")
        conversion_rules.add_range_rule("batch_size", 1, 32, "Batch size must be between 1 and 32")
        self._rule_sets["conversion_params"] = conversion_rules

    def add_rule_set(self, rule_set: ValidationRuleSet) -> None:
        """Add a validation rule set."""
        self._rule_sets[rule_set.section_name] = rule_set

    def get_rule_set(self, section_name: str) -> Optional[ValidationRuleSet]:
        """Get a validation rule set by section name."""
        return self._rule_sets.get(section_name)

    def validate_section(self, section_name: str, config: Dict[str, Any]) -> List[str]:
        """
        Validate a specific configuration section.

        Args:
            section_name: Name of the section to validate
            config: Configuration data for the section

        Returns:
            List of validation error messages (empty if valid)
        """
        rule_set = self.get_rule_set(section_name)
        if not rule_set:
            return [f"No validation rules found for section: {section_name}"]

        return rule_set.validate(config)

    def validate_all(self, config: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Validate entire configuration against all rule sets.

        Args:
            config: Complete configuration dictionary

        Returns:
            Dictionary mapping section names to lists of validation errors
        """
        results = {}

        for section_name, rule_set in self._rule_sets.items():
            section_config = config.get(section_name, {})
            errors = rule_set.validate(section_config)
            if errors:
                results[section_name] = errors

        return results

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of all validation rules."""
        summary = {
            "total_sections": len(self._rule_sets),
            "total_rules": 0,
            "rules_by_severity": {severity.value: 0 for severity in ValidationSeverity}
        }

        for rule_set in self._rule_sets.values():
            summary["total_rules"] += rule_set.count_rules()
            severity_counts = rule_set.count_rules_by_severity()
            for severity, count in severity_counts.items():
                summary["rules_by_severity"][severity] += count

        return summary

    def export_rules(self, output_path: Path) -> bool:
        """
        Export validation rules to a file.

        Args:
            output_path: Path to export file

        Returns:
            True if export was successful
        """
        try:
            import yaml

            # Convert to serializable format
            export_data = {}
            for section_name, rule_set in self._rule_sets.items():
                export_data[section_name] = {
                    "description": rule_set.description,
                    "rules": []
                }

                for rule in rule_set.rules:
                    rule_data = {
                        "field_path": rule.field_path,
                        "rule_type": rule.rule_type.value,
                        "rule_params": rule.rule_params,
                        "error_message": rule.error_message,
                        "suggestion": rule.suggestion,
                        "severity": rule.severity.value
                    }

                    # Skip custom validators as they're not serializable
                    if rule.rule_type != ValidationRuleType.CUSTOM:
                        export_data[section_name]["rules"].append(rule_data)

            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(export_data, f, default_flow_style=False, indent=2)

            return True

        except Exception as e:
            print(f"Error exporting validation rules: {e}")
            return False