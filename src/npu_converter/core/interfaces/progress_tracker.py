"""
Progress Tracker Interface

This module defines the interface for progress tracking throughout the NPU converter system.
It provides a standardized way to monitor and report progress during long-running operations
like model conversion, quantization, and optimization.

Key Features:
- Standardized progress reporting interface
- Hierarchical progress tracking (main operation -> subtasks)
- Cancellable operation support
- Detailed progress metadata and metrics
- Real-time progress callback system
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Union
from datetime import datetime
import logging
from enum import Enum

from ..models.progress_model import ProgressModel
from ..models.config_model import ConfigModel

logger = logging.getLogger(__name__)


class ProgressStage(Enum):
    """Enumeration of standard progress stages."""

    INITIALIZING = "initializing"
    VALIDATING = "validating"
    PREPARING = "preparing"
    PROCESSING = "processing"
    OPTIMIZING = "optimizing"
    EXPORTING = "exporting"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    FAILED = "failed"


class BaseProgressTracker(ABC):
    """
    Abstract base class for all progress trackers.

    This class defines the standard interface for progress tracking throughout
    the NPU converter system. It provides consistent progress reporting and
    operation management capabilities.

    Attributes:
        operation_name (str): Name of the operation being tracked
        total_stages (int): Total number of stages in the operation
        current_stage (int): Current stage index
        progress (ProgressModel): Current progress state
        is_cancellable (bool): Whether the operation can be cancelled
    """

    def __init__(
        self,
        operation_name: str,
        total_stages: int,
        config: Optional[ConfigModel] = None,
        is_cancellable: bool = True
    ) -> None:
        """
        Initialize the progress tracker.

        Args:
            operation_name: Name of the operation being tracked
            total_stages: Total number of stages in the operation
            config: Optional configuration for progress tracking
            is_cancellable: Whether the operation can be cancelled
        """
        self.operation_name = operation_name
        self.total_stages = total_stages
        self.current_stage = 0
        self.is_cancellable = is_cancellable
        self.config = config or ConfigModel()

        self.progress = ProgressModel()
        self.progress.operation_name = operation_name
        self.progress.total_stages = total_stages
        self.progress.start_time = datetime.now()

        self._callbacks: List[Callable[[ProgressModel], None]] = []
        self._stage_descriptions: List[str] = [""] * total_stages
        self._stage_weights: List[float] = [1.0] * total_stages
        self._is_cancelled = False
        self._is_paused = False

        logger.info(f"Initialized progress tracker for '{operation_name}' with {total_stages} stages")

    @abstractmethod
    def start_stage(
        self,
        stage_name: str,
        description: Optional[str] = None,
        weight: Optional[float] = None
    ) -> None:
        """
        Start a new progress stage.

        Args:
            stage_name: Name of the stage
            description: Optional description of the stage
            weight: Optional weight for the stage (affects overall progress calculation)
        """
        pass

    @abstractmethod
    def update_progress(
        self,
        stage_progress: float,
        message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update progress within the current stage.

        Args:
            stage_progress: Progress within the current stage (0.0 to 1.0)
            message: Optional progress message
            metadata: Optional progress metadata
        """
        pass

    @abstractmethod
    def complete_stage(
        self,
        result: Optional[Dict[str, Any]] = None,
        warnings: Optional[List[str]] = None
    ) -> None:
        """
        Complete the current stage.

        Args:
            result: Optional stage result data
            warnings: Optional list of warnings
        """
        pass

    @abstractmethod
    def set_stage_description(self, description: str) -> None:
        """
        Set description for the current stage.

        Args:
            description: Description of the current stage
        """
        pass

    def add_progress_callback(self, callback: Callable[[ProgressModel], None]) -> None:
        """
        Add a progress callback function.

        Args:
            callback: Function to call when progress updates
        """
        self._callbacks.append(callback)
        logger.debug(f"Added progress callback for '{self.operation_name}'")

    def remove_progress_callback(self, callback: Callable[[ProgressModel], None]) -> None:
        """
        Remove a progress callback function.

        Args:
            callback: Function to remove from callbacks
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)
            logger.debug(f"Removed progress callback for '{self.operation_name}'")

    def notify_callbacks(self) -> None:
        """Notify all registered callbacks of progress updates."""
        for callback in self._callbacks:
            try:
                callback(self.progress)
            except Exception as e:
                logger.warning(f"Progress callback failed: {str(e)}")

    def cancel(self, reason: Optional[str] = None) -> bool:
        """
        Cancel the operation if cancellable.

        Args:
            reason: Optional reason for cancellation

        Returns:
            bool: True if cancellation was successful
        """
        if not self.is_cancellable:
            logger.warning(f"Operation '{self.operation_name}' is not cancellable")
            return False

        if self._is_cancelled:
            logger.warning(f"Operation '{self.operation_name}' is already cancelled")
            return True

        self._is_cancelled = True
        self.progress.status = "cancelled"
        self.progress.end_time = datetime.now()

        if reason:
            self.progress.error_message = f"Cancelled: {reason}"

        logger.info(f"Operation '{self.operation_name}' cancelled: {reason or 'No reason provided'}")
        self.notify_callbacks()
        return True

    def pause(self) -> bool:
        """
        Pause the operation if supported.

        Returns:
            bool: True if pause was successful
        """
        if self._is_paused:
            logger.warning(f"Operation '{self.operation_name}' is already paused")
            return True

        self._is_paused = True
        self.progress.status = "paused"
        logger.info(f"Operation '{self.operation_name}' paused")
        self.notify_callbacks()
        return True

    def resume(self) -> bool:
        """
        Resume the operation if paused.

        Returns:
            bool: True if resume was successful
        """
        if not self._is_paused:
            logger.warning(f"Operation '{self.operation_name}' is not paused")
            return False

        self._is_paused = False
        self.progress.status = "running"
        logger.info(f"Operation '{self.operation_name}' resumed")
        self.notify_callbacks()
        return True

    def complete(self, result: Optional[Dict[str, Any]] = None) -> None:
        """
        Complete the operation successfully.

        Args:
            result: Optional final result data
        """
        self.progress.status = "completed"
        self.progress.end_time = datetime.now()
        self.progress.overall_progress = 1.0

        if result:
            self.progress.result_data = result

        logger.info(f"Operation '{self.operation_name}' completed successfully")
        self.notify_callbacks()

    def fail(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Mark the operation as failed.

        Args:
            error: Exception that caused the failure
            context: Optional error context information
        """
        self.progress.status = "failed"
        self.progress.end_time = datetime.now()
        self.progress.error_message = str(error)

        if context:
            self.progress.error_context = context

        logger.error(f"Operation '{self.operation_name}' failed: {str(error)}")
        self.notify_callbacks()

    def get_progress(self) -> ProgressModel:
        """
        Get current progress state.

        Returns:
            ProgressModel: Current progress state
        """
        return self.progress

    def is_cancelled(self) -> bool:
        """
        Check if the operation has been cancelled.

        Returns:
            bool: True if cancelled
        """
        return self._is_cancelled

    def is_paused(self) -> bool:
        """
        Check if the operation is paused.

        Returns:
            bool: True if paused
        """
        return self._is_paused

    def get_elapsed_time(self) -> Optional[float]:
        """
        Get elapsed time in seconds.

        Returns:
            Optional[float]: Elapsed time in seconds, None if not started
        """
        if self.progress.start_time:
            end_time = self.progress.end_time or datetime.now()
            return (end_time - self.progress.start_time).total_seconds()
        return None

    def get_estimated_remaining_time(self) -> Optional[float]:
        """
        Get estimated remaining time in seconds.

        Returns:
            Optional[float]: Estimated remaining time in seconds, None if not estimable
        """
        if self.progress.overall_progress > 0 and self.get_elapsed_time():
            elapsed = self.get_elapsed_time()
            remaining = elapsed * (1.0 - self.progress.overall_progress) / self.progress.overall_progress
            return max(0, remaining)
        return None

    def __str__(self) -> str:
        """String representation of the progress tracker."""
        progress_pct = self.progress.overall_progress * 100
        return f"{self.operation_name}: {progress_pct:.1f}% ({self.progress.status})"

    def __repr__(self) -> str:
        """Detailed representation of the progress tracker."""
        return (f"{self.__class__.__name__}(operation_name='{self.operation_name}', "
                f"progress={self.progress.overall_progress:.1%}, status='{self.progress.status}')")


class ConversionProgressTracker(BaseProgressTracker):
    """
    Progress tracker specialized for model conversion operations.

    This tracker provides predefined stages and metrics for model conversion
    workflows, including validation, preparation, conversion, and export phases.
    """

    def __init__(
        self,
        model_path: str,
        output_path: str,
        config: Optional[ConfigModel] = None
    ) -> None:
        """
        Initialize conversion progress tracker.

        Args:
            model_path: Path to input model
            output_path: Path for output model
            config: Optional configuration
        """
        super().__init__(
            operation_name=f"Convert {Path(model_path).name}",
            total_stages=4,
            config=config
        )

        self.model_path = model_path
        self.output_path = output_path
        self.model_size_original = 0
        self.model_size_converted = 0

        # Define standard conversion stages
        self._stage_descriptions = [
            "Validating input model and configuration",
            "Preparing conversion environment and loading model",
            "Executing model conversion",
            "Exporting converted model and generating reports"
        ]

        # Define stage weights for more accurate progress calculation
        self._stage_weights = [0.1, 0.2, 0.6, 0.1]

    def start_validation(self) -> None:
        """Start the validation stage."""
        self.start_stage("validation", self._stage_descriptions[0], weight=0.1)

    def start_preparation(self) -> None:
        """Start the preparation stage."""
        self.start_stage("preparation", self._stage_descriptions[1], weight=0.2)

    def start_conversion(self) -> None:
        """Start the conversion stage."""
        self.start_stage("conversion", self._stage_descriptions[2], weight=0.6)

    def start_export(self) -> None:
        """Start the export stage."""
        self.start_stage("export", self._stage_descriptions[3], weight=0.1)

    def set_model_metrics(
        self,
        original_size: Optional[int] = None,
        converted_size: Optional[int] = None,
        compression_ratio: Optional[float] = None
    ) -> None:
        """
        Set model size metrics.

        Args:
            original_size: Original model size in bytes
            converted_size: Converted model size in bytes
            compression_ratio: Compression ratio
        """
        if original_size is not None:
            self.model_size_original = original_size
        if converted_size is not None:
            self.model_size_converted = converted_size

        # Update progress metadata
        self.progress.metadata.update({
            "model_size_original": original_size,
            "model_size_converted": converted_size,
            "compression_ratio": compression_ratio or (original_size / converted_size if converted_size else None)
        })

    # Implement abstract methods
    def start_stage(
        self,
        stage_name: str,
        description: Optional[str] = None,
        weight: Optional[float] = None
    ) -> None:
        """Start a new progress stage."""
        if self.current_stage >= self.total_stages:
            logger.warning(f"Cannot start stage '{stage_name}': all stages completed")
            return

        self.progress.current_stage = self.current_stage
        self.progress.stage_name = stage_name

        if description:
            self.set_stage_description(description)

        if weight:
            self._stage_weights[self.current_stage] = weight

        self.progress.stage_start_time = datetime.now()
        logger.info(f"Starting stage {self.current_stage + 1}/{self.total_stages}: {stage_name}")

    def update_progress(
        self,
        stage_progress: float,
        message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update progress within the current stage."""
        if not 0.0 <= stage_progress <= 1.0:
            logger.warning(f"Invalid stage progress: {stage_progress}. Must be between 0.0 and 1.0")
            stage_progress = max(0.0, min(1.0, stage_progress))

        # Calculate overall progress based on completed stages and current stage progress
        completed_weight = sum(self._stage_weights[:self.current_stage])
        current_stage_weight = self._stage_weights[self.current_stage] if self.current_stage < self.total_stages else 0
        total_weight = sum(self._stage_weights)

        self.progress.overall_progress = (completed_weight + current_stage_weight * stage_progress) / total_weight
        self.progress.stage_progress = stage_progress

        if message:
            self.progress.message = message

        if metadata:
            self.progress.metadata.update(metadata)

        self.notify_callbacks()

    def complete_stage(
        self,
        result: Optional[Dict[str, Any]] = None,
        warnings: Optional[List[str]] = None
    ) -> None:
        """Complete the current stage."""
        self.progress.stage_progress = 1.0
        self.progress.stage_end_time = datetime.now()

        if result:
            self.progress.metadata.update(result)

        if warnings:
            self.progress.warnings.extend(warnings)

        self.current_stage += 1
        logger.info(f"Completed stage {self.current_stage}/{self.total_stages}")

        # Update overall progress
        if self.current_stage < self.total_stages:
            completed_weight = sum(self._stage_weights[:self.current_stage])
            total_weight = sum(self._stage_weights)
            self.progress.overall_progress = completed_weight / total_weight

    def set_stage_description(self, description: str) -> None:
        """Set description for the current stage."""
        self.progress.stage_description = description


# Import Path for type hints
from pathlib import Path