"""
Configuration-related Exception Classes

This module defines the hierarchy of exceptions for configuration-related
errors. These exceptions provide detailed error information for configuration
loading, validation, and management operations.

Key Features:
- Configuration-specific error handling
- Detailed error context with file paths
- Validation error details
- Configuration loading error information
"""

from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime

from .conversion_errors import ConversionError


class ConfigError(ConversionError):
    """
    Base exception for all configuration-related errors.

    This class serves as the foundation for configuration-specific exceptions
    and provides common functionality for configuration error handling.
    """

    def __init__(
        self,
        message: str,
        config_path: Optional[Path] = None,
        config_section: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Initialize configuration error.

        Args:
            message: Human-readable error message
            config_path: Path to configuration file
            config_section: Configuration section that caused the error
            **kwargs: Additional arguments passed to base class
        """
        super().__init__(message, **kwargs)

        # Add config-specific context
        if config_path:
            self.context["config_path"] = str(config_path)
        if config_section:
            self.context["config_section"] = config_section

        # Add default suggestions if not provided
        if not self.suggestions:
            self.suggestions = [
                "Check configuration file format and syntax",
                "Verify all required fields are present",
                "Consult configuration documentation",
                "Use configuration validation tools"
            ]


class ConfigValidationError(ConfigError):
    """
    Exception raised when configuration validation fails.

    This exception is used when configuration data fails validation
    checks, such as type validation, range validation, or dependency
    validation.
    """

    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        validation_rule: Optional[str] = None,
        valid_values: Optional[List[Any]] = None,
        **kwargs
    ) -> None:
        """
        Initialize configuration validation error.

        Args:
            message: Human-readable error message
            field_name: Name of the field that failed validation
            field_value: Value that failed validation
            validation_rule: Description of the validation rule that failed
            valid_values: List of valid values (if applicable)
            **kwargs: Additional arguments passed to base class
        """
        super().__init__(message, **kwargs)

        # Add validation-specific context
        if field_name:
            self.context["field_name"] = field_name
        if field_value is not None:
            self.context["field_value"] = field_value
        if validation_rule:
            self.context["validation_rule"] = validation_rule
        if valid_values:
            self.context["valid_values"] = valid_values

        # Add default suggestions if not provided
        if not self.suggestions:
            suggestions = [
                "Check field value against validation requirements",
                "Update configuration with valid values"
            ]

            if field_name:
                suggestions.append(f"Verify the '{field_name}' field in configuration")

            if valid_values:
                suggestions.append(f"Use one of the valid values: {valid_values}")

            self.suggestions = suggestions


class ConfigNotFoundError(ConfigError):
    """
    Exception raised when configuration file is not found.

    This exception is used when the system cannot locate a required
    configuration file.
    """

    def __init__(
        self,
        message: str,
        search_paths: Optional[List[Path]] = None,
        config_name: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Initialize configuration not found error.

        Args:
            message: Human-readable error message
            search_paths: List of paths that were searched
            config_name: Name of the configuration file that was not found
            **kwargs: Additional arguments passed to base class
        """
        super().__init__(message, **kwargs)

        # Add not-found-specific context
        if search_paths:
            self.context["search_paths"] = [str(p) for p in search_paths]
        if config_name:
            self.context["config_name"] = config_name

        # Add default suggestions if not provided
        if not self.suggestions:
            suggestions = [
                "Verify configuration file exists",
                "Check file path and permissions",
                "Create configuration file if missing"
            ]

            if config_name:
                suggestions.append(f"Create '{config_name}' configuration file")

            if search_paths:
                suggestions.append("Place configuration file in one of the search locations")

            self.suggestions = suggestions


class ConfigLoadError(ConfigError):
    """
    Exception raised when configuration file cannot be loaded.

    This exception is used when there are errors reading or parsing
    configuration files, such as format errors or permission issues.
    """

    def __init__(
        self,
        message: str,
        config_path: Optional[Path] = None,
        load_error: Optional[str] = None,
        file_format: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Initialize configuration load error.

        Args:
            message: Human-readable error message
            config_path: Path to configuration file that failed to load
            load_error: Specific error that occurred during loading
            file_format: Expected file format (YAML, JSON, etc.)
            **kwargs: Additional arguments passed to base class
        """
        super().__init__(message, config_path=config_path, **kwargs)

        # Add load-error-specific context
        if load_error:
            self.context["load_error"] = load_error
        if file_format:
            self.context["file_format"] = file_format

        # Add default suggestions if not provided
        if not self.suggestions:
            suggestions = [
                "Check file format and syntax",
                "Verify file permissions",
                "Ensure file is not corrupted"
            ]

            if file_format:
                suggestions.append(f"Validate {file_format.upper()} file syntax")

            if config_path:
                suggestions.append(f"Check '{config_path}' file integrity")

            self.suggestions = suggestions


class ConfigMergeError(ConfigError):
    """
    Exception raised when configuration merging fails.

    This exception is used when there are errors merging multiple
    configuration sources, such as conflicts or incompatible structures.
    """

    def __init__(
        self,
        message: str,
        source_configs: Optional[List[str]] = None,
        conflict_fields: Optional[List[str]] = None,
        merge_strategy: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Initialize configuration merge error.

        Args:
            message: Human-readable error message
            source_configs: List of configuration source identifiers
            conflict_fields: List of fields that caused conflicts
            merge_strategy: Merge strategy that was being used
            **kwargs: Additional arguments passed to base class
        """
        super().__init__(message, **kwargs)

        # Add merge-error-specific context
        if source_configs:
            self.context["source_configs"] = source_configs
        if conflict_fields:
            self.context["conflict_fields"] = conflict_fields
        if merge_strategy:
            self.context["merge_strategy"] = merge_strategy

        # Add default suggestions if not provided
        if not self.suggestions:
            suggestions = [
                "Review configuration conflicts",
                "Use different merge strategy",
                "Manually resolve conflicts in configuration"
            ]

            if conflict_fields:
                suggestions.append(f"Resolve conflicts in fields: {conflict_fields}")

            self.suggestions = suggestions


class ConfigSchemaError(ConfigError):
    """
    Exception raised when configuration schema validation fails.

    This exception is used when configuration data does not conform to
    the expected schema or structure.
    """

    def __init__(
        self,
        message: str,
        schema_path: Optional[str] = None,
        expected_structure: Optional[Dict[str, Any]] = None,
        actual_structure: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        """
        Initialize configuration schema error.

        Args:
            message: Human-readable error message
            schema_path: Path within the schema where validation failed
            expected_structure: Expected structure at the failed path
            actual_structure: Actual structure that was found
            **kwargs: Additional arguments passed to base class
        """
        super().__init__(message, **kwargs)

        # Add schema-error-specific context
        if schema_path:
            self.context["schema_path"] = schema_path
        if expected_structure:
            self.context["expected_structure"] = expected_structure
        if actual_structure:
            self.context["actual_structure"] = actual_structure

        # Add default suggestions if not provided
        if not self.suggestions:
            suggestions = [
                "Update configuration to match expected schema",
                "Refer to configuration schema documentation",
                "Use configuration schema validation tools"
            ]

            if schema_path:
                suggestions.append(f"Fix configuration structure at '{schema_path}'")

            self.suggestions = suggestions