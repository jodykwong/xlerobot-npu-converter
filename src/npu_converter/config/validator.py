"""
Configuration Validator

Validates configuration files according to defined rules and schema.
Provides detailed error messages and suggestions for fixing issues.

Implements the validation layer of the configuration architecture
as defined in the architecture document.
"""

import re
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass

from npu_converter.core.exceptions.config_errors import ConfigError


@dataclass
class ValidationError:
    """Configuration validation error details."""
    field_path: str
    error_type: str
    message: str
    suggestion: str
    severity: str  # "error", "warning", "info"


@dataclass
class ValidationResult:
    """Configuration validation result."""
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    info: List[ValidationError]

    @property
    def has_errors(self) -> bool:
        """Check if validation found errors."""
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        """Check if validation found warnings."""
        return len(self.warnings) > 0

    def get_summary(self) -> str:
        """Get validation result summary."""
        error_count = len(self.errors)
        warning_count = len(self.warnings)
        info_count = len(self.info)

        if self.is_valid:
            status = "✅ Valid"
        else:
            status = f"❌ Invalid ({error_count} errors)"

        summary = f"{status}"
        if warning_count > 0:
            summary += f", {warning_count} warnings"
        if info_count > 0:
            summary += f", {info_count} info messages"

        return summary


class ConfigValidator:
    """
    Configuration validation system.

    Validates configuration files against defined rules and provides
    detailed error messages and suggestions for fixing issues.
    """

    def __init__(self):
        """Initialize the configuration validator."""
        self._validation_rules: Dict[str, List[Dict[str, Any]]] = {}
        self._setup_validation_rules()

    def _setup_validation_rules(self) -> None:
        """Setup validation rules for different configuration sections."""
        self._validation_rules.update({
            "project": [
                {
                    "field": "name",
                    "required": True,
                    "type": str,
                    "pattern": r"^[a-zA-Z][a-zA-Z0-9_-]*$",
                    "message": "Project name must contain only letters, numbers, underscores, and hyphens"
                },
                {
                    "field": "version",
                    "required": True,
                    "type": str,
                    "pattern": r"^\d+\.\d+\.\d+$",
                    "message": "Version must follow semantic versioning (e.g., 1.0.0)"
                },
                {
                    "field": "model_type",
                    "required": True,
                    "type": str,
                    "enum": ["sensevoice", "piper_vits", "vits_cantonese"],
                    "message": "Model type must be 'sensevoice', 'piper_vits', or 'vits_cantonese'"
                }
            ],
            "hardware": [
                {
                    "field": "target_device",
                    "required": True,
                    "type": str,
                    "enum": ["horizon_x5"],
                    "message": "Target device must be 'horizon_x5'"
                },
                {
                    "field": "optimization_level",
                    "type": str,
                    "enum": ["O0", "O1", "O2", "O3"],
                    "default": "O2",
                    "message": "Optimization level must be one of: O0, O1, O2, O3"
                },
                {
                    "field": "memory_limit",
                    "type": str,
                    "pattern": r"^\d+[KMGT]?B$",
                    "message": "Memory limit must be in format like '8GB', '512MB', etc."
                }
            ],
            "conversion_params": [
                {
                    "field": "input_format",
                    "required": True,
                    "type": str,
                    "enum": ["onnx"],
                    "message": "Input format must be 'onnx'"
                },
                {
                    "field": "output_format",
                    "required": True,
                    "type": str,
                    "enum": ["bpu"],
                    "message": "Output format must be 'bpu'"
                },
                {
                    "field": "precision",
                    "type": str,
                    "enum": ["int8", "int16", "float16"],
                    "default": "int8",
                    "message": "Precision must be one of: int8, int16, float16"
                },
                {
                    "field": "batch_size",
                    "type": int,
                    "min": 1,
                    "max": 32,
                    "default": 1,
                    "message": "Batch size must be between 1 and 32"
                }
            ]
        })

    def validate(self, config: Dict[str, Any]) -> bool:
        """
        Validate configuration dictionary.

        Args:
            config: Configuration dictionary to validate

        Returns:
            True if configuration is valid

        Raises:
            ConfigError: If validation fails
        """
        result = self.validate_detailed(config)

        if not result.is_valid:
            # Format error messages for exception
            error_messages = []
            for error in result.errors:
                error_messages.append(f"{error.field_path}: {error.message}")

            if result.warnings:
                warning_messages = []
                for warning in result.warnings:
                    warning_messages.append(f"{warning.field_path}: {warning.message}")

                error_messages.append(f"Warnings: {'; '.join(warning_messages)}")

            raise ConfigError(f"Configuration validation failed: {'; '.join(error_messages)}")

        return True

    def validate_detailed(self, config: Dict[str, Any]) -> ValidationResult:
        """
        Validate configuration with detailed results.

        Args:
            config: Configuration dictionary to validate

        Returns:
            Detailed validation result
        """
        errors = []
        warnings = []
        info = []

        # Validate top-level structure
        self._validate_structure(config, errors, warnings, info)

        # Validate each section
        for section_name, section_rules in self._validation_rules.items():
            section_config = config.get(section_name, {})
            self._validate_section(section_name, section_config, section_rules, errors, warnings, info)

        # Validate model-specific configuration
        self._validate_model_specific(config, errors, warnings, info)

        # Check for required files and paths
        self._validate_paths(config, errors, warnings, info)

        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings, info)

    def _validate_structure(self, config: Dict[str, Any],
                          errors: List[ValidationError],
                          warnings: List[ValidationError],
                          info: List[ValidationError]) -> None:
        """Validate overall configuration structure."""
        if not isinstance(config, dict):
            errors.append(ValidationError(
                field_path="root",
                error_type="structure",
                message="Configuration must be a dictionary",
                suggestion="Ensure configuration file contains valid YAML dictionary",
                severity="error"
            ))
            return

        required_sections = ["project", "hardware", "conversion_params"]
        for section in required_sections:
            if section not in config:
                errors.append(ValidationError(
                    field_path=section,
                    error_type="missing_section",
                    message=f"Required section '{section}' is missing",
                    suggestion=f"Add the '{section}' section to your configuration file",
                    severity="error"
                ))

    def _validate_section(self, section_name: str,
                         section_config: Dict[str, Any],
                         section_rules: List[Dict[str, Any]],
                         errors: List[ValidationError],
                         warnings: List[ValidationError],
                         info: List[ValidationError]) -> None:
        """Validate a specific configuration section."""
        for rule in section_rules:
            field_path = f"{section_name}.{rule['field']}"
            field_value = section_config.get(rule['field'])

            # Check required fields
            if rule.get('required', False) and field_value is None:
                errors.append(ValidationError(
                    field_path=field_path,
                    error_type="required_field",
                    message=f"Required field '{rule['field']}' is missing",
                    suggestion=f"Add '{rule['field']}' to the {section_name} section",
                    severity="error"
                ))
                continue

            # Skip validation if field is missing but not required
            if field_value is None:
                if 'default' in rule:
                    info.append(ValidationError(
                        field_path=field_path,
                        error_type="default_value",
                        message=f"Using default value for '{rule['field']}': {rule['default']}",
                        suggestion=f"Consider explicitly setting '{rule['field']}' in configuration",
                        severity="info"
                    ))
                continue

            # Validate field type
            if 'type' in rule and not isinstance(field_value, rule['type']):
                errors.append(ValidationError(
                    field_path=field_path,
                    error_type="type_mismatch",
                    message=f"Field '{rule['field']}' must be of type {rule['type'].__name__}, got {type(field_value).__name__}",
                    suggestion=f"Change '{rule['field']}' to a {rule['type'].__name__} value",
                    severity="error"
                ))

            # Validate enum values
            if 'enum' in rule and field_value not in rule['enum']:
                errors.append(ValidationError(
                    field_path=field_path,
                    error_type="invalid_enum",
                    message=f"Invalid value for '{rule['field']}': {field_value}. Must be one of: {rule['enum']}",
                    suggestion=f"Change '{rule['field']}' to one of the allowed values",
                    severity="error"
                ))

            # Validate pattern
            if 'pattern' in rule and isinstance(field_value, str):
                if not re.match(rule['pattern'], field_value):
                    errors.append(ValidationError(
                        field_path=field_path,
                        error_type="pattern_mismatch",
                        message=f"Field '{rule['field']}' does not match required pattern",
                        suggestion=rule['message'],
                        severity="error"
                    ))

            # Validate range
            if 'min' in rule and field_value < rule['min']:
                errors.append(ValidationError(
                    field_path=field_path,
                    error_type="range_violation",
                    message=f"Field '{rule['field']}' value {field_value} is below minimum {rule['min']}",
                    suggestion=f"Set '{rule['field']}' to a value >= {rule['min']}",
                    severity="error"
                ))

            if 'max' in rule and field_value > rule['max']:
                errors.append(ValidationError(
                    field_path=field_path,
                    error_type="range_violation",
                    message=f"Field '{rule['field']}' value {field_value} is above maximum {rule['max']}",
                    suggestion=f"Set '{rule['field']}' to a value <= {rule['max']}",
                    severity="error"
                ))

            # Validate custom validator
            if 'custom_validator' in rule:
                try:
                    custom_validator = rule['custom_validator']
                    if not custom_validator(field_value, section_config):
                        errors.append(ValidationError(
                            field_path=field_path,
                            error_type="custom_validation_failed",
                            message=rule.get('message', f"Field '{rule['field']}' failed custom validation"),
                            suggestion=rule.get('suggestion', "Check field value against custom requirements"),
                            severity="error"
                        ))
                except Exception as e:
                    errors.append(ValidationError(
                        field_path=field_path,
                        error_type="custom_validator_error",
                        message=f"Custom validator error for '{rule['field']}': {str(e)}",
                        suggestion="Check custom validator implementation",
                        severity="error"
                    ))

    def _validate_model_specific(self, config: Dict[str, Any],
                               errors: List[ValidationError],
                               warnings: List[ValidationError],
                               info: List[ValidationError]) -> None:
        """Validate model-specific configuration."""
        model_type = config.get("project", {}).get("model_type")
        if not model_type:
            return

        model_specific = config.get("model_specific", {}).get(model_type, {})
        if not model_specific:
            warnings.append(ValidationError(
                field_path="model_specific",
                error_type="missing_model_config",
                message=f"No model-specific configuration found for {model_type}",
                suggestion=f"Add a '{model_type}' section under 'model_specific'",
                severity="warning"
            ))
            return

        # Model-specific validation rules
        if model_type == "sensevoice":
            self._validate_sensevoice_config(model_specific, errors, warnings, info)
        elif model_type == "piper_vits":
            self._validate_piper_vits_config(model_specific, errors, warnings, info)
        elif model_type == "vits_cantonese":
            self._validate_vits_cantonese_config(model_specific, errors, warnings, info)

    def _validate_sensevoice_config(self, config: Dict[str, Any],
                                   errors: List[ValidationError],
                                   warnings: List[ValidationError],
                                   info: List[ValidationError]) -> None:
        """Validate SenseVoice-specific configuration."""
        # Check for required SenseVoice fields
        required_fields = ["sample_rate", "audio_length", "vocab_size"]
        for field in required_fields:
            if field not in config:
                errors.append(ValidationError(
                    field_path=f"model_specific.sensevoice.{field}",
                    error_type="required_field",
                    message=f"Required SenseVoice field '{field}' is missing",
                    suggestion=f"Add '{field}' to the sensevoice configuration",
                    severity="error"
                ))

        # Validate sample rate
        if "sample_rate" in config:
            valid_rates = [8000, 16000, 22050, 44100]
            if config["sample_rate"] not in valid_rates:
                errors.append(ValidationError(
                    field_path="model_specific.sensevoice.sample_rate",
                    error_type="invalid_value",
                    message=f"Invalid sample rate: {config['sample_rate']}",
                    suggestion=f"Use one of: {valid_rates}",
                    severity="error"
                ))

    def _validate_piper_vits_config(self, config: Dict[str, Any],
                                   errors: List[ValidationError],
                                   warnings: List[ValidationError],
                                   info: List[ValidationError]) -> None:
        """Validate Piper VITS-specific configuration."""
        # Check for required Piper VITS fields
        required_fields = ["sample_rate", "mel_channels", "speaker_embedding"]
        for field in required_fields:
            if field not in config:
                errors.append(ValidationError(
                    field_path=f"model_specific.piper_vits.{field}",
                    error_type="required_field",
                    message=f"Required Piper VITS field '{field}' is missing",
                    suggestion=f"Add '{field}' to the piper_vits configuration",
                    severity="error"
                ))

        # Validate sample rate
        if "sample_rate" in config:
            valid_rates = [16000, 22050, 44100]
            if config["sample_rate"] not in valid_rates:
                errors.append(ValidationError(
                    field_path="model_specific.piper_vits.sample_rate",
                    error_type="invalid_value",
                    message=f"Invalid sample rate: {config['sample_rate']}",
                    suggestion=f"Use one of: {valid_rates}",
                    severity="error"
                ))

    def _validate_vits_cantonese_config(self, config: Dict[str, Any],
                                      errors: List[ValidationError],
                                      warnings: List[ValidationError],
                                      info: List[ValidationError]) -> None:
        """Validate VITS-Cantonese-specific configuration based on technical specifications."""
        # Check for required VITS-Cantonese fields
        required_vits_fields = [
            "inter_channels", "hidden_channels", "filter_channels",
            "n_heads", "n_layers", "kernel_size"
        ]

        required_cantonese_fields = [
            "sampling_rate", "filter_length", "hop_length", "win_length",
            "n_mel_channels", "cantonese_vocab_size", "phoneme_set",
            "tone_embedding", "num_tones", "use_jyutping"
        ]

        for field in required_vits_fields + required_cantonese_fields:
            if field not in config:
                errors.append(ValidationError(
                    field_path=f"model_specific.vits_cantonese.{field}",
                    error_type="required_field",
                    message=f"Required VITS-Cantonese field '{field}' is missing",
                    suggestion=f"Add '{field}' to the vits_cantonese configuration",
                    severity="error"
                ))

        # Validate VITS architecture parameters (strict validation)
        if "inter_channels" in config and config["inter_channels"] != 192:
            errors.append(ValidationError(
                field_path="model_specific.vits_cantonese.inter_channels",
                error_type="invalid_value",
                message=f"VITS inter_channels must be 192, got {config['inter_channels']}",
                suggestion="Use VITS standard configuration: inter_channels=192",
                severity="error"
            ))

        if "n_heads" in config and config["n_heads"] != 2:
            errors.append(ValidationError(
                field_path="model_specific.vits_cantonese.n_heads",
                error_type="invalid_value",
                message=f"VITS n_heads must be 2, got {config['n_heads']}",
                suggestion="Use VITS standard configuration: n_heads=2",
                severity="error"
            ))

        if "n_layers" in config and config["n_layers"] != 4:
            errors.append(ValidationError(
                field_path="model_specific.vits_cantonese.n_layers",
                error_type="invalid_value",
                message=f"VITS n_layers must be 4, got {config['n_layers']}",
                suggestion="Use VITS standard configuration: n_layers=4",
                severity="error"
            ))

        # Validate Cantonese-specific parameters
        if "sampling_rate" in config and config["sampling_rate"] != 22050:
            errors.append(ValidationError(
                field_path="model_specific.vits_cantonese.sampling_rate",
                error_type="invalid_value",
                message=f"VITS-Cantonese sampling rate must be 22050 Hz, got {config['sampling_rate']}",
                suggestion="Use standard sampling rate for Cantonese TTS: 22050",
                severity="error"
            ))

        if "num_tones" in config and config["num_tones"] != 6:
            errors.append(ValidationError(
                field_path="model_specific.vits_cantonese.num_tones",
                error_type="invalid_value",
                message=f"Cantonese has 6 tones, got {config['num_tones']}",
                suggestion="Use correct Cantonese tone system: num_tones=6",
                severity="error"
            ))

        if "phoneme_set" in config and config["phoneme_set"] != "jyutping_extended":
            errors.append(ValidationError(
                field_path="model_specific.vits_cantonese.phoneme_set",
                error_type="invalid_value",
                message=f"Phoneme set must be 'jyutping_extended', got {config['phoneme_set']}",
                suggestion="Use standard Cantonese phoneme set: jyutping_extended",
                severity="error"
            ))

        # Validate vocabulary size
        if "cantonese_vocab_size" in config:
            vocab_size = config["cantonese_vocab_size"]
            if not (1000 <= vocab_size <= 10000):
                errors.append(ValidationError(
                    field_path="model_specific.vits_cantonese.cantonese_vocab_size",
                    error_type="range_violation",
                    message=f"Cantonese vocabulary size {vocab_size} is out of range [1000, 10000]",
                    suggestion="Use vocabulary size between 1000 and 10000 for Cantonese",
                    severity="error"
                ))

        # Validate synthesis parameters
        synthesis_fields = ["noise_scale", "noise_scale_w", "length_scale", "inference_noise_scale"]
        for field in synthesis_fields:
            if field in config:
                value = config[field]
                if field == "noise_scale" and not (0.1 <= value <= 2.0):
                    errors.append(ValidationError(
                        field_path=f"model_specific.vits_cantonese.{field}",
                        error_type="range_violation",
                        message=f"{field} {value} is out of range [0.1, 2.0]",
                        suggestion="Use synthesis parameter between 0.1 and 2.0",
                        severity="error"
                    ))
                elif field == "length_scale" and not (0.5 <= value <= 2.0):
                    errors.append(ValidationError(
                        field_path=f"model_specific.vits_cantonese.{field}",
                        error_type="range_violation",
                        message=f"{field} {value} is out of range [0.5, 2.0]",
                        suggestion="Use length scale between 0.5 and 2.0",
                        severity="error"
                    ))

    def _validate_paths(self, config: Dict[str, Any],
                       errors: List[ValidationError],
                       warnings: List[ValidationError],
                       info: List[ValidationError]) -> None:
        """Validate file paths and directories."""
        # Check for model file paths
        model_config = config.get("model_config", {})
        if "model_path" in model_config and model_config["model_path"] is not None:
            model_path = Path(model_config["model_path"])
            if not model_path.exists():
                warnings.append(ValidationError(
                    field_path="model_config.model_path",
                    error_type="file_not_found",
                    message=f"Model file not found: {model_path}",
                    suggestion="Ensure the model file exists at the specified path",
                    severity="warning"
                ))

    def get_validation_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all validation rules."""
        return self._validation_rules.copy()

    def add_validation_rule(self, section: str, rule: Dict[str, Any]) -> None:
        """Add a new validation rule."""
        if section not in self._validation_rules:
            self._validation_rules[section] = []
        self._validation_rules[section].append(rule)