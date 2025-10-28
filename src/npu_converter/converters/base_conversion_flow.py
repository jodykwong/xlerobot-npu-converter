"""
Base Conversion Flow

This module defines the abstract base class for all conversion flow implementations.
It extends the BaseConverter from Story 1.3 to provide enhanced progress tracking,
status management, and conversion orchestration capabilities for Story 1.5.

Key Features:
- Extended progress tracking with detailed conversion stages
- Real-time status feedback and event notifications
- Comprehensive logging and audit trail capabilities
- Integration with Story 1.4 configuration management system
- Thread-safe operation for concurrent conversions
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Callable
from pathlib import Path
import logging
from datetime import datetime
import threading
from enum import Enum

from ..core.interfaces.base_converter import BaseConverter
from ..core.models.conversion_model import ConversionModel
from ..core.models.config_model import ConfigModel
from ..core.models.progress_model import ProgressModel, ProgressStep
from ..core.models.result_model import ResultModel
from ..core.exceptions.conversion_errors import (
    ConversionError,
    ValidationError,
    ConversionTimeoutError
)
from ..core.interfaces.validator import ValidationResult
from .status_callback import StatusCallback
from .progress_tracker import ProgressTracker
from .conversion_logger import ConversionLogger
from ..config.manager import ConfigurationManager

logger = logging.getLogger(__name__)


class ConversionStage(Enum):
    """Enumeration of conversion stages for progress tracking."""

    INITIALIZATION = "initialization"
    VALIDATION = "validation"
    PREPARATION = "preparation"
    LOADING = "loading"
    PREPROCESSING = "preprocessing"
    QUANTIZATION = "quantization"
    COMPILATION = "compilation"
    OPTIMIZATION = "optimization"
    VALIDATION_POST = "validation_post"
    EXPORT = "export"
    COMPLETED = "completed"
    FAILED = "failed"


class BaseConversionFlow(BaseConverter):
    """
    Abstract base class for all conversion flow implementations.

    This class extends BaseConverter with enhanced progress tracking, status management,
    and conversion orchestration capabilities. It provides the foundation for all
    model-specific conversion flows in Story 1.5.

    Attributes:
        operation_id: Unique identifier for the conversion operation
        conversion_stages: List of conversion stages for this flow
        progress_tracker: Enhanced progress tracking manager
        status_callbacks: List of status callback implementations
        conversion_logger: Comprehensive logging system
        config_manager: Configuration management integration
        thread_lock: Thread safety lock for concurrent operations
    """

    def __init__(
        self,
        name: str,
        version: str,
        config: Optional[ConfigModel] = None,
        operation_id: Optional[str] = None
    ) -> None:
        """
        Initialize the base conversion flow.

        Args:
            name: Human-readable name of the conversion flow
            version: Version of the conversion flow implementation
            config: Optional configuration for the conversion
            operation_id: Optional unique operation identifier
        """
        super().__init__(name, version, config)

        # Generate unique operation ID if not provided
        self.operation_id = operation_id or f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Conversion flow components
        self.conversion_stages: List[ConversionStage] = []
        self.progress_tracker: Optional[ProgressTracker] = None
        self.status_callbacks: List[StatusCallback] = []
        self.conversion_logger: Optional[ConversionLogger] = None
        self.config_manager: Optional[ConfigurationManager] = None

        # Thread safety
        self._thread_lock = threading.Lock()
        self._current_stage: Optional[ConversionStage] = None

        # Enhanced state management
        self._stage_results: Dict[str, Any] = {}
        self._stage_start_times: Dict[str, datetime] = {}
        self._stage_durations: Dict[str, float] = {}

        logger.info(f"Initialized {self.name} conversion flow v{version} with operation_id: {self.operation_id}")

    @abstractmethod
    def create_progress_steps(self) -> List[ProgressStep]:
        """
        Create the progress steps for this conversion flow.

        This method should define the specific steps and stages that this
        conversion flow will go through, including their weights and
        estimated durations.

        Returns:
            List[ProgressStep]: List of progress steps for the conversion
        """
        pass

    @abstractmethod
    def execute_conversion_stage(
        self,
        stage: ConversionStage,
        conversion_model: ConversionModel
    ) -> bool:
        """
        Execute a specific conversion stage.

        This method should implement the logic for each conversion stage.
        It will be called for each stage defined in create_progress_steps().

        Args:
            stage: The conversion stage to execute
            conversion_model: The conversion context and data

        Returns:
            bool: True if the stage executed successfully

        Raises:
            ConversionError: If the stage execution fails
        """
        pass

    @abstractmethod
    def handle_stage_completion(
        self,
        stage: ConversionStage,
        result: Any
    ) -> None:
        """
        Handle the completion of a conversion stage.

        This method is called after each stage completes successfully.
        It can be used to perform post-processing or state updates.

        Args:
            stage: The completed conversion stage
            result: The result of the stage execution
        """
        pass

    def initialize_conversion_components(self) -> None:
        """Initialize conversion flow components."""
        with self._thread_lock:
            if self.progress_tracker is not None:
                return  # Already initialized

            # Initialize progress tracker
            self.progress_tracker = ProgressTracker(
                operation_id=self.operation_id,
                operation_name=self.name
            )

            # Add conversion stages
            progress_steps = self.create_progress_steps()
            for step in progress_steps:
                self.progress_tracker.add_stage(step)

            # Initialize conversion logger
            self.conversion_logger = ConversionLogger(
                operation_id=self.operation_id,
                log_level="INFO"
            )

            # Initialize config manager integration
            if self.config and hasattr(self.config, 'config_file_path'):
                self.config_manager = ConfigurationManager(
                    config_file_path=Path(self.config.config_file_path) if self.config.config_file_path else None
                )

            logger.info(f"Initialized conversion components for {self.operation_id}")

    def add_status_callback(self, callback: StatusCallback) -> None:
        """
        Add a status callback to receive conversion updates.

        Args:
            callback: Status callback implementation
        """
        with self._thread_lock:
            self.status_callbacks.append(callback)
            logger.debug(f"Added status callback {callback.__class__.__name__} to {self.operation_id}")

    def remove_status_callback(self, callback: StatusCallback) -> bool:
        """
        Remove a status callback.

        Args:
            callback: Status callback implementation to remove

        Returns:
            bool: True if callback was found and removed
        """
        with self._thread_lock:
            if callback in self.status_callbacks:
                self.status_callbacks.remove(callback)
                logger.debug(f"Removed status callback {callback.__class__.__name__} from {self.operation_id}")
                return True
            return False

    def _notify_status_update(
        self,
        status: str,
        message: str,
        progress: Optional[float] = None
    ) -> None:
        """Notify all status callbacks of a status update."""
        for callback in self.status_callbacks:
            try:
                callback.on_status_update(status, message, progress)
            except Exception as e:
                logger.warning(f"Status callback {callback.__class__.__name__} failed: {e}")

    def _notify_stage_completed(
        self,
        stage_name: str,
        result: Any
    ) -> None:
        """Notify all status callbacks of stage completion."""
        for callback in self.status_callbacks:
            try:
                callback.on_stage_completed(stage_name, result)
            except Exception as e:
                logger.warning(f"Status callback {callback.__class__.__name__} failed: {e}")

    def _notify_error(
        self,
        error: Exception,
        context: Dict[str, Any]
    ) -> None:
        """Notify all status callbacks of an error."""
        for callback in self.status_callbacks:
            try:
                callback.on_error(error, context)
            except Exception as e:
                logger.warning(f"Status callback {callback.__class__.__name__} failed: {e}")

    def _execute_stage_with_tracking(
        self,
        stage: ConversionStage,
        conversion_model: ConversionModel
    ) -> Any:
        """
        Execute a stage with comprehensive tracking and logging.

        Args:
            stage: The conversion stage to execute
            conversion_model: The conversion context and data

        Returns:
            Any: The result of the stage execution

        Raises:
            ConversionError: If the stage execution fails
        """
        stage_name = stage.value
        start_time = datetime.now()

        with self._thread_lock:
            self._current_stage = stage
            self._stage_start_times[stage_name] = start_time

        try:
            # Log stage start
            if self.conversion_logger:
                self.conversion_logger.log_stage_start(
                    stage_name,
                    {
                        "operation_id": self.operation_id,
                        "conversion_flow": self.name,
                        "stage": stage_name
                    }
                )

            # Start progress tracking
            if self.progress_tracker:
                self.progress_tracker.start_stage(stage_name)

            # Notify status update
            self._notify_status_update(
                "running",
                f"Executing {stage_name} stage",
                None
            )

            # Execute the stage
            logger.info(f"Executing {stage_name} stage for {self.operation_id}")
            result = self.execute_conversion_stage(stage, conversion_model)

            # Calculate duration
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            with self._thread_lock:
                self._stage_durations[stage_name] = duration
                self._stage_results[stage_name] = result

            # Log stage completion
            if self.conversion_logger:
                self.conversion_logger.log_stage_completion(
                    stage_name,
                    duration,
                    result
                )

            # Complete progress tracking
            if self.progress_tracker:
                self.progress_tracker.complete_stage(stage_name, result)

            # Handle stage completion
            self.handle_stage_completion(stage, result)

            # Notify stage completion
            self._notify_stage_completed(stage_name, result)

            logger.info(f"Completed {stage_name} stage for {self.operation_id} in {duration:.2f}s")
            return result

        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Log error
            if self.conversion_logger:
                self.conversion_logger.log_error(
                    stage_name,
                    e,
                    {
                        "operation_id": self.operation_id,
                        "duration": duration,
                        "stage": stage_name
                    }
                )

            # Notify error
            self._notify_error(
                e,
                {
                    "operation_id": self.operation_id,
                    "stage": stage_name,
                    "duration": duration
                }
            )

            logger.error(f"Failed {stage_name} stage for {self.operation_id} after {duration:.2f}s: {e}")
            raise ConversionError(f"Stage {stage_name} failed: {e}") from e

    def convert(
        self,
        conversion_model: ConversionModel,
        progress_callback: Optional[Callable[[ProgressModel], None]] = None
    ) -> ResultModel:
        """
        Execute the complete conversion flow with enhanced tracking.

        This method overrides the base convert method to provide comprehensive
        stage-based execution with progress tracking, status updates, and logging.

        Args:
            conversion_model: Prepared conversion context
            progress_callback: Optional callback for progress updates

        Returns:
            ResultModel: Results of the conversion process

        Raises:
            ConversionError: If conversion fails
            ConversionTimeoutError: If conversion times out
        """
        # Initialize components if not already done
        if self.progress_tracker is None:
            self.initialize_conversion_components()

        self.status = "running"
        conversion_results = {}

        try:
            # Get conversion stages from progress steps
            progress_steps = self.create_progress_steps()
            conversion_stages = [ConversionStage(step.step_id) for step in progress_steps]

            # Execute each stage
            for stage in conversion_stages:
                with self._thread_lock:
                    self._current_stage = stage

                result = self._execute_stage_with_tracking(stage, conversion_model)
                conversion_results[stage.value] = result

                # Call progress callback if provided
                if progress_callback and self.progress_tracker:
                    progress_callback(self.progress_tracker.get_progress_model())

            # Create success result
            result = ResultModel(
                success=True,
                message=f"Conversion completed successfully in {self.name}",
                data=conversion_results,
                metadata={
                    "operation_id": self.operation_id,
                    "conversion_flow": self.name,
                    "stages_completed": list(conversion_results.keys()),
                    "stage_durations": self._stage_durations,
                    "total_duration": sum(self._stage_durations.values())
                }
            )

            self.status = "completed"
            logger.info(f"Conversion flow {self.operation_id} completed successfully")

            return result

        except Exception as e:
            self.status = "failed"
            error_context = {
                "operation_id": self.operation_id,
                "conversion_flow": self.name,
                "current_stage": self._current_stage.value if self._current_stage else None,
                "completed_stages": list(conversion_results.keys())
            }

            logger.error(f"Conversion flow {self.operation_id} failed: {e}")
            raise ConversionError(f"Conversion flow failed: {e}") from e

    def get_detailed_progress(self) -> Dict[str, Any]:
        """
        Get detailed progress information for the conversion flow.

        Returns:
            Dict[str, Any]: Comprehensive progress information
        """
        progress_info = {
            "operation_id": self.operation_id,
            "conversion_flow": self.name,
            "status": self.status,
            "current_stage": self._current_stage.value if self._current_stage else None,
            "stage_results": self._stage_results.copy(),
            "stage_durations": self._stage_durations.copy(),
            "stage_start_times": {k: v.isoformat() for k, v in self._stage_start_times.items()}
        }

        # Add progress tracker information if available
        if self.progress_tracker:
            progress_info["progress_model"] = self.progress_tracker.get_progress_model()

        return progress_info

    def save_progress_state(self, output_path: Union[str, Path]) -> None:
        """
        Save the current progress state to a file.

        Args:
            output_path: Path where progress state should be saved
        """
        if self.progress_tracker:
            self.progress_tracker.save_progress(Path(output_path))
            logger.info(f"Saved progress state for {self.operation_id} to {output_path}")

    def load_progress_state(self, input_path: Union[str, Path]) -> bool:
        """
        Load progress state from a file.

        Args:
            input_path: Path to progress state file

        Returns:
            bool: True if progress state was loaded successfully
        """
        if self.progress_tracker:
            success = self.progress_tracker.load_progress(Path(input_path))
            if success:
                logger.info(f"Loaded progress state for {self.operation_id} from {input_path}")
            return success
        return False

    def get_stage_duration(self, stage_name: str) -> Optional[float]:
        """
        Get the duration of a specific stage.

        Args:
            stage_name: Name of the stage

        Returns:
            Optional[float]: Duration in seconds, None if stage not completed
        """
        return self._stage_durations.get(stage_name)

    def get_stage_result(self, stage_name: str) -> Any:
        """
        Get the result of a specific stage.

        Args:
            stage_name: Name of the stage

        Returns:
            Any: Stage result, None if stage not completed
        """
        return self._stage_results.get(stage_name)

    def __str__(self) -> str:
        """String representation of the conversion flow."""
        return f"{self.name} Conversion Flow v{self.version} ({self.operation_id}) - {self.status}"

    def __repr__(self) -> str:
        """Detailed representation of the conversion flow."""
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"version='{self.version}', "
            f"operation_id='{self.operation_id}', "
            f"status='{self.status}', "
            f"current_stage={self._current_stage})"
        )