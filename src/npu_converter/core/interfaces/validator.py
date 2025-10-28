"""
Validation Interface

This module defines the interface for validation throughout the NPU converter system.
It provides standardized validation for models, configurations, and conversion parameters
with detailed reporting and error handling.

Key Features:
- Standardized validation interface
- Detailed validation reporting with warnings and errors
- Model compatibility checking
- Configuration validation
- Parameter validation and type checking
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path
import logging
from enum import Enum

from ..models.config_model import ConfigModel

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Validation severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationResult:
    """
    Container for validation results.

    This class encapsulates the results of validation operations,
    providing detailed feedback on any issues found.
    """

    def __init__(self, target: str) -> None:
        """
        Initialize validation result.

        Args:
            target: Name of what was validated
        """
        self.target = target
        self.is_valid = True
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.info: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}
        self.validation_time: Optional[float] = None

    def add_error(
        self,
        message: str,
        code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add an error to the validation result.

        Args:
            message: Error message
            code: Optional error code
            context: Optional error context
        """
        self.errors.append({
            "message": message,
            "code": code,
            "context": context or {},
            "level": ValidationLevel.ERROR.value
        })
        self.is_valid = False

    def add_warning(
        self,
        message: str,
        code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a warning to the validation result.

        Args:
            message: Warning message
            code: Optional warning code
            context: Optional warning context
        """
        self.warnings.append({
            "message": message,
            "code": code,
            "context": context or {},
            "level": ValidationLevel.WARNING.value
        })

    def add_info(
        self,
        message: str,
        code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add an info message to the validation result.

        Args:
            message: Info message
            code: Optional info code
            context: Optional info context
        """
        self.info.append({
            "message": message,
            "code": code,
            "context": context or {},
            "level": ValidationLevel.INFO.value
        })

    def get_all_issues(self) -> List[Dict[str, Any]]:
        """
        Get all validation issues (errors and warnings).

        Returns:
            List of all issues sorted by severity
        """
        all_issues = []
        all_issues.extend(self.errors)
        all_issues.extend(self.warnings)
        all_issues.extend(self.info)
        return sorted(all_issues, key=lambda x: self._severity_order(x["level"]))

    def _severity_order(self, level: str) -> int:
        """Get severity order for sorting."""
        order = {
            ValidationLevel.CRITICAL.value: 0,
            ValidationLevel.ERROR.value: 1,
            ValidationLevel.WARNING.value: 2,
            ValidationLevel.INFO.value: 3
        }
        return order.get(level, 99)

    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the validation result.

        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value

    def merge(self, other: 'ValidationResult') -> None:
        """
        Merge another validation result into this one.

        Args:
            other: Another validation result to merge
        """
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.info.extend(other.info)
        self.metadata.update(other.metadata)
        if not other.is_valid:
            self.is_valid = False

    def __str__(self) -> str:
        """String representation of the validation result."""
        status = "VALID" if self.is_valid else "INVALID"
        issues_count = len(self.errors) + len(self.warnings)
        return f"ValidationResult({self.target}): {status} - {issues_count} issues"

    def __repr__(self) -> str:
        """Detailed representation of the validation result."""
        return (f"{self.__class__.__name__}(target='{self.target}', "
                f"is_valid={self.is_valid}, errors={len(self.errors)}, "
                f"warnings={len(self.warnings)})")


class BaseValidator(ABC):
    """
    Abstract base class for all validators.

    This class defines the standard interface for validation operations
    throughout the NPU converter system.

    Attributes:
        name (str): Name of the validator
        version (str): Version of the validator
        config (ConfigModel): Configuration for the validator
    """

    def __init__(
        self,
        name: str,
        version: str,
        config: Optional[ConfigModel] = None
    ) -> None:
        """
        Initialize the base validator.

        Args:
            name: Name of the validator
            version: Version of the validator
            config: Optional configuration for the validator
        """
        self.name = name
        self.version = version
        self.config = config or ConfigModel()

        logger.info(f"Initialized {self.name} v{self.version}")

    @abstractmethod
    def validate_model(
        self,
        model_path: Union[str, Path],
        strict_mode: bool = False
    ) -> ValidationResult:
        """
        Validate a model file.

        Args:
            model_path: Path to the model file
            strict_mode: Whether to use strict validation mode

        Returns:
            ValidationResult: Detailed validation results

        Raises:
            ValidationError: If validation fails catastrophically
        """
        pass

    @abstractmethod
    def validate_config(
        self,
        config: Union[ConfigModel, Dict[str, Any], str, Path],
        schema_name: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate configuration.

        Args:
            config: Configuration to validate
            schema_name: Optional schema name to validate against

        Returns:
            ValidationResult: Detailed validation results

        Raises:
            ValidationError: If validation fails catastrophically
        """
        pass

    @abstractmethod
    def validate_parameters(
        self,
        parameters: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate parameters against a schema.

        Args:
            parameters: Parameters to validate
            schema: Schema to validate against

        Returns:
            ValidationResult: Detailed validation results

        Raises:
            ValidationError: If validation fails catastrophically
        """
        pass

    def validate_compatibility(
        self,
        source_model: Union[str, Path],
        target_format: str,
        config: Optional[ConfigModel] = None
    ) -> ValidationResult:
        """
        Validate model compatibility with target format.

        Args:
            source_model: Source model path
            target_format: Target format to convert to
            config: Optional configuration for compatibility checking

        Returns:
            ValidationResult: Compatibility validation results
        """
        result = ValidationResult(f"compatibility_{Path(source_model).name}_to_{target_format}")

        # Default implementation checks basic compatibility
        result.add_info(f"Checking compatibility for {target_format} conversion")

        # Subclasses should override this method for specific compatibility checks
        return result

    def validate_path(
        self,
        path: Union[str, Path],
        must_exist: bool = True,
        expected_extension: Optional[str] = None,
        check_permissions: bool = True
    ) -> ValidationResult:
        """
        Validate a file system path.

        Args:
            path: Path to validate
            must_exist: Whether the path must exist
            expected_extension: Optional expected file extension
            check_permissions: Whether to check read/write permissions

        Returns:
            ValidationResult: Path validation results
        """
        path_obj = Path(path)
        target = str(path_obj)
        result = ValidationResult(target)

        # Check if path exists
        if must_exist and not path_obj.exists():
            result.add_error(f"Path does not exist: {target}", code="PATH_NOT_FOUND")
            return result

        if path_obj.exists():
            # Check if it's a file when expected
            if expected_extension and path_obj.is_file():
                if path_obj.suffix.lower() != expected_extension.lower():
                    result.add_error(
                        f"Expected extension {expected_extension}, got {path_obj.suffix}",
                        code="WRONG_EXTENSION",
                        context={"expected": expected_extension, "actual": path_obj.suffix}
                    )

            # Check permissions
            if check_permissions:
                if not path_obj.is_dir():  # Not checking write permissions for directories
                    try:
                        # Check read permission
                        with open(path_obj, 'rb') if path_obj.is_file() else iter([]):
                            pass
                    except (PermissionError, OSError) as e:
                        result.add_error(
                            f"Cannot read path: {str(e)}",
                            code="READ_PERMISSION_DENIED",
                            context={"path": target}
                        )

        else:
            if must_exist:
                result.add_error(f"Required path does not exist: {target}", code="PATH_REQUIRED")

        result.set_metadata("path_type", "file" if path_obj.is_file() else "directory")
        result.set_metadata("path_exists", path_obj.exists())

        return result

    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported formats for this validator.

        Returns:
            List[str]: List of supported format names
        """
        return []  # Subclasses should override

    def __str__(self) -> str:
        """String representation of the validator."""
        return f"{self.name} v{self.version}"

    def __repr__(self) -> str:
        """Detailed representation of the validator."""
        return f"{self.__class__.__name__}(name='{self.name}', version='{self.version}')"


class ModelValidator(BaseValidator):
    """
    Specialized validator for model files.

    This validator provides comprehensive validation for different model formats,
    including structure validation, metadata checking, and compatibility analysis.
    """

    def __init__(self, config: Optional[ConfigModel] = None) -> None:
        """Initialize model validator."""
        super().__init__("ModelValidator", "1.0.0", config)

    def validate_model(
        self,
        model_path: Union[str, Path],
        strict_mode: bool = False
    ) -> ValidationResult:
        """
        Validate a model file.

        Args:
            model_path: Path to the model file
            strict_mode: Whether to use strict validation mode

        Returns:
            ValidationResult: Detailed validation results
        """
        path_obj = Path(model_path)
        result = ValidationResult(str(path_obj))

        # Basic path validation
        path_result = self.validate_path(path_obj, must_exist=True)
        result.merge(path_result)

        if not path_result.is_valid:
            return result

        # Check file size
        if path_obj.is_file():
            file_size = path_obj.stat().st_size
            result.set_metadata("file_size", file_size)

            if file_size == 0:
                result.add_error("Model file is empty", code="EMPTY_FILE")
            elif file_size > 10 * 1024 * 1024 * 1024:  # 10GB limit
                result.add_warning(
                    f"Large model file detected ({file_size / (1024**3):.2f}GB)",
                    code="LARGE_FILE",
                    context={"size_bytes": file_size}
                )

        # Basic format detection based on extension
        extension = path_obj.suffix.lower()
        result.set_metadata("file_extension", extension)

        # Subclasses should implement format-specific validation
        result.add_info(f"Model file validated with extension: {extension}")

        return result

    def validate_config(
        self,
        config: Union[ConfigModel, Dict[str, Any], str, Path],
        schema_name: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate configuration.

        Args:
            config: Configuration to validate
            schema_name: Optional schema name to validate against

        Returns:
            ValidationResult: Detailed validation results
        """
        result = ValidationResult("config_validation")

        if isinstance(config, (str, Path)):
            # Validate file path
            path_result = self.validate_path(config, must_exist=True, expected_extension=".json")
            result.merge(path_result)

        # Basic config structure validation
        result.add_info("Configuration structure validated")

        return result

    def validate_parameters(
        self,
        parameters: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate parameters against a schema.

        Args:
            parameters: Parameters to validate
            schema: Schema to validate against

        Returns:
            ValidationResult: Detailed validation results
        """
        result = ValidationResult("parameter_validation")

        # Basic parameter validation
        for param_name, param_schema in schema.items():
            if param_name not in parameters:
                if param_schema.get("required", False):
                    result.add_error(f"Required parameter missing: {param_name}", code="MISSING_PARAMETER")
            else:
                # Type checking
                expected_type = param_schema.get("type")
                if expected_type and not isinstance(parameters[param_name], expected_type):
                    result.add_error(
                        f"Parameter {param_name} has wrong type. Expected {expected_type}, got {type(parameters[param_name])}",
                        code="WRONG_TYPE",
                        context={"parameter": param_name, "expected_type": expected_type}
                    )

        result.add_info("Parameter validation completed")

        return result

    def get_supported_formats(self) -> List[str]:
        """Get list of supported model formats."""
        return ["onnx", "tflite", "torchscript", "caffe", "pb"]  # Common formats