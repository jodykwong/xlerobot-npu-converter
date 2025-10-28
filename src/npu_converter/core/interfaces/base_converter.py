"""
Base Converter Interface

This module defines the abstract base class for all converter implementations.
It provides a common interface for different types of model converters
(PTQ, QAT, custom converters, etc.) ensuring consistency in the conversion
workflow and enabling plugin-based architecture.

Key Features:
- Abstract methods for converter lifecycle
- Standard conversion workflow: validate -> convert -> export
- Progress tracking and status management
- Error handling and validation framework
- Configuration management integration
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Callable
from pathlib import Path
import logging
from datetime import datetime

from ..models.conversion_model import ConversionModel
from ..models.config_model import ConfigModel
from ..models.progress_model import ProgressModel
from ..models.result_model import ResultModel
from ..exceptions.conversion_errors import (
    ConversionError,
    ValidationError,
    ConversionTimeoutError
)
from ..interfaces.validator import ValidationResult

logger = logging.getLogger(__name__)


class BaseConverter(ABC):
    """
    Abstract base class for all model converters.

    This class defines the standard interface and workflow that all converters
    must implement. It provides a consistent API for different conversion types
    while allowing specific implementations to handle their unique requirements.

    Attributes:
        name (str): Human-readable name of the converter
        version (str): Version of the converter implementation
        config (ConfigModel): Configuration for the converter
        progress (ProgressModel): Progress tracking for conversion operations
        status (str): Current status of the converter
    """

    def __init__(
        self,
        name: str,
        version: str,
        config: Optional[ConfigModel] = None
    ) -> None:
        """
        Initialize the base converter.

        Args:
            name: Human-readable name of the converter
            version: Version of the converter implementation
            config: Optional configuration for the converter
        """
        self.name = name
        self.version = version
        self.config = config or ConfigModel(
            hardware_config={},
            system_config={}
        )
        self.progress = ProgressModel(name, f"{name} v{version}")
        self.status = "initialized"
        self._start_time: Optional[datetime] = None
        self._end_time: Optional[datetime] = None

        logger.info(f"Initialized {self.name} v{self.version}")

    @abstractmethod
    def validate_input(
        self,
        model_path: Union[str, Path],
        config: Optional[ConfigModel] = None
    ) -> ValidationResult:
        """
        Validate input model and configuration.

        This method should check if the input model is compatible with this
        converter type and if the configuration is valid for the conversion.

        Args:
            model_path: Path to the input model file
            config: Optional configuration to validate

        Returns:
            ValidationResult: Object containing validation results

        Raises:
            ValidationError: If validation fails
            ModelCompatibilityError: If model is not compatible
        """
        pass

    @abstractmethod
    def prepare_conversion(
        self,
        model_path: Union[str, Path],
        config: Optional[ConfigModel] = None
    ) -> ConversionModel:
        """
        Prepare the conversion process.

        This method should set up the conversion environment, load the model,
        and prepare all necessary resources for the conversion process.

        Args:
            model_path: Path to the input model file
            config: Optional configuration for the conversion

        Returns:
            ConversionModel: Prepared conversion context

        Raises:
            ConversionError: If preparation fails
        """
        pass

    @abstractmethod
    def convert(
        self,
        conversion_model: ConversionModel,
        progress_callback: Optional[Callable[[ProgressModel], None]] = None
    ) -> ResultModel:
        """
        Execute the main conversion process.

        This is the core method that performs the actual model conversion.
        It should handle the conversion logic specific to each converter type.

        Args:
            conversion_model: Prepared conversion context
            progress_callback: Optional callback for progress updates

        Returns:
            ResultModel: Results of the conversion process

        Raises:
            ConversionError: If conversion fails
            ConversionTimeoutError: If conversion times out
        """
        pass

    @abstractmethod
    def export_results(
        self,
        result: ResultModel,
        output_path: Union[str, Path],
        format: str = "default"
    ) -> bool:
        """
        Export conversion results to the specified format and location.

        Args:
            result: Conversion results to export
            output_path: Path where results should be saved
            format: Export format (depends on converter type)

        Returns:
            bool: True if export was successful

        Raises:
            ConversionError: If export fails
        """
        pass

    def run_conversion(
        self,
        model_path: Union[str, Path],
        output_path: Union[str, Path],
        config: Optional[ConfigModel] = None,
        progress_callback: Optional[Callable[[ProgressModel], None]] = None
    ) -> ResultModel:
        """
        Run the complete conversion workflow.

        This method orchestrates the entire conversion process from validation
        through to export, providing a simple interface for users.

        Args:
            model_path: Path to the input model file
            output_path: Path where converted model should be saved
            config: Optional configuration for the conversion
            progress_callback: Optional callback for progress updates

        Returns:
            ResultModel: Complete conversion results

        Raises:
            ConversionError: If any step in the workflow fails
        """
        self._start_time = datetime.now()
        self.status = "running"

        try:
            logger.info(f"Starting conversion with {self.name}")

            # Step 1: Validate input
            logger.info("Validating input model and configuration")
            validation_result = self.validate_input(model_path, config)
            if not validation_result.is_valid:
                raise ValidationError(f"Input validation failed: {validation_result.errors}")

            # Step 2: Prepare conversion
            logger.info("Preparing conversion environment")
            conversion_model = self.prepare_conversion(model_path, config)

            # Step 3: Execute conversion
            logger.info("Executing conversion process")
            result = self.convert(conversion_model, progress_callback)

            # Step 4: Export results
            logger.info(f"Exporting results to {output_path}")
            export_success = self.export_results(result, output_path)
            if not export_success:
                raise ConversionError("Failed to export conversion results")

            self.status = "completed"
            logger.info(f"Conversion completed successfully with {self.name}")

            return result

        except Exception as e:
            self.status = "failed"
            logger.error(f"Conversion failed with {self.name}: {str(e)}")
            raise
        finally:
            self._end_time = datetime.now()

    def get_progress(self) -> ProgressModel:
        """
        Get current conversion progress.

        Returns:
            ProgressModel: Current progress information
        """
        return self.progress

    def get_status(self) -> str:
        """
        Get current converter status.

        Returns:
            str: Current status string
        """
        return self.status

    def get_execution_time(self) -> Optional[float]:
        """
        Get total execution time in seconds.

        Returns:
            Optional[float]: Execution time in seconds, None if not completed
        """
        if self._start_time and self._end_time:
            return (self._end_time - self._start_time).total_seconds()
        return None

    def reset(self) -> None:
        """Reset converter state for new conversion."""
        self.progress = ProgressModel(self.name, f"{self.name} v{self.version}")
        # Reset config to defaults
        self.config = ConfigModel(
            hardware_config={},
            system_config={}
        )
        self.status = "initialized"
        self._start_time = None
        self._end_time = None
        logger.info(f"Reset {self.name} converter state")

    def __str__(self) -> str:
        """String representation of the converter."""
        return f"{self.name} v{self.version} ({self.status})"

    def __repr__(self) -> str:
        """Detailed representation of the converter."""
        return f"{self.__class__.__name__}(name='{self.name}', version='{self.version}', status='{self.status}')"


class ValidationResult:
    """
    Result of input validation.

    This class encapsulates the results of input model and configuration
    validation, providing detailed feedback on any issues found.
    """

    def __init__(self, is_valid: bool = True) -> None:
        """
        Initialize validation result.

        Args:
            is_valid: Whether validation passed
        """
        self.is_valid = is_valid
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.model_info: Dict[str, Any] = {}

    def add_error(self, error: str) -> None:
        """Add an error to the validation result."""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str) -> None:
        """Add a warning to the validation result."""
        self.warnings.append(warning)

    def set_model_info(self, info: Dict[str, Any]) -> None:
        """Set model information from validation."""
        self.model_info = info