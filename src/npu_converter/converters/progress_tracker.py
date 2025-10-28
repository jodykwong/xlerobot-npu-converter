"""
Progress Tracker

This module defines the enhanced progress tracking system for conversion flows.
It extends Story 1.3's ProgressModel to provide detailed stage-level tracking,
persistence, and recovery capabilities.

Key Features:
- Enhanced stage-level progress tracking
- Progress persistence and recovery
- ETA calculation and performance metrics
- Thread-safe progress management
- Integration with conversion flow orchestration
"""

from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import logging
import json
import threading
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import copy

from ..core.models.progress_model import ProgressModel, ProgressStep
from ..core.models.conversion_model import ConversionModel

logger = logging.getLogger(__name__)


@dataclass
class StageProgress:
    """Progress information for a specific stage."""

    stage_id: str
    stage_name: str
    status: str  # "pending", "running", "completed", "failed"
    progress: float  # 0.0 to 100.0
    weight: float  # Weight in overall progress calculation
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}

    @property
    def is_active(self) -> bool:
        """Check if stage is currently active."""
        return self.status == "running"

    @property
    def is_completed(self) -> bool:
        """Check if stage has completed successfully."""
        return self.status == "completed"

    @property
    def is_failed(self) -> bool:
        """Check if stage has failed."""
        return self.status == "failed"

    @property
    def is_pending(self) -> bool:
        """Check if stage is pending to start."""
        return self.status == "pending"

    @property
    def weighted_progress(self) -> float:
        """Calculate weighted progress contribution."""
        return (self.progress / 100.0) * self.weight

    def start(self) -> None:
        """Mark stage as started."""
        self.status = "running"
        self.start_time = datetime.now()
        self.progress = 0.0
        self.error = None

    def update_progress(self, progress: float) -> None:
        """Update stage progress."""
        self.progress = max(0.0, min(100.0, progress))

    def complete(self, result: Optional[Any] = None) -> None:
        """Mark stage as completed."""
        self.status = "completed"
        self.end_time = datetime.now()
        self.progress = 100.0
        self.result = result
        if self.start_time:
            self.duration = (self.end_time - self.start_time).total_seconds()

    def fail(self, error: str) -> None:
        """Mark stage as failed."""
        self.status = "failed"
        self.end_time = datetime.now()
        self.error = error
        if self.start_time:
            self.duration = (self.end_time - self.start_time).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        # Convert datetime objects to strings
        if data["start_time"]:
            data["start_time"] = data["start_time"].isoformat()
        if data["end_time"]:
            data["end_time"] = data["end_time"].isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StageProgress":
        """Create from dictionary."""
        # Convert string datetimes back to datetime objects
        if data.get("start_time"):
            data["start_time"] = datetime.fromisoformat(data["start_time"])
        if data.get("end_time"):
            data["end_time"] = datetime.fromisoformat(data["end_time"])
        return cls(**data)


class ProgressTracker:
    """
    Enhanced progress tracking system for conversion flows.

    This class extends Story 1.3's progress tracking capabilities by providing
    detailed stage-level tracking, persistence, and recovery features.
    """

    def __init__(
        self,
        operation_id: str,
        operation_name: str,
        auto_save_interval: Optional[float] = 30.0
    ) -> None:
        """
        Initialize progress tracker.

        Args:
            operation_id: Unique identifier for the operation
            operation_name: Human-readable name of the operation
            auto_save_interval: Auto-save interval in seconds (None to disable)
        """
        self.operation_id = operation_id
        self.operation_name = operation_name
        self.auto_save_interval = auto_save_interval

        # Progress tracking data
        self._stages: Dict[str, StageProgress] = {}
        self._overall_progress: ProgressModel(operation_id, operation_name)
        self._start_time: Optional[datetime] = None
        self._end_time: Optional[datetime] = None
        self._total_weight: float = 0.0

        # Thread safety
        self._lock = threading.Lock()

        # Auto-save state
        self._last_save_time: Optional[datetime] = None
        self._auto_save_file_path: Optional[Path] = None

        logger.info(f"Initialized ProgressTracker for {operation_name} (ID: {operation_id})")

    def add_stage(self, progress_step: ProgressStep) -> None:
        """
        Add a progress stage to track.

        Args:
            progress_step: Progress step to add
        """
        with self._lock:
            stage_progress = StageProgress(
                stage_id=progress_step.step_id,
                stage_name=progress_step.name,
                status="pending",
                progress=0.0,
                weight=progress_step.weight,
                metadata={
                    "description": progress_step.description
                }
            )

            self._stages[progress_step.step_id] = stage_progress
            self._total_weight += progress_step.weight

            logger.debug(f"Added stage {progress_step.step_id} to tracker")

    def start_stage(self, stage_id: str) -> bool:
        """
        Start tracking a stage.

        Args:
            stage_id: ID of the stage to start

        Returns:
            bool: True if stage was started successfully

        Raises:
            ValueError: If stage ID is not found
        """
        with self._lock:
            if stage_id not in self._stages:
                raise ValueError(f"Stage {stage_id} not found in progress tracker")

            stage = self._stages[stage_id]

            if stage.status == "running":
                logger.warning(f"Stage {stage_id} is already running")
                return False

            # Set overall start time if this is the first stage
            if not self._start_time:
                self._start_time = datetime.now()
                logger.info(f"Started overall operation tracking for {self.operation_id}")

            stage.start()
            self._update_overall_progress()

            logger.info(f"Started stage {stage_id} for {self.operation_id}")
            return True

    def update_stage_progress(self, stage_id: str, progress: float) -> bool:
        """
        Update progress for a stage.

        Args:
            stage_id: ID of the stage to update
            progress: Progress percentage (0.0 to 100.0)

        Returns:
            bool: True if progress was updated successfully

        Raises:
            ValueError: If stage ID is not found
        """
        with self._lock:
            if stage_id not in self._stages:
                raise ValueError(f"Stage {stage_id} not found in progress tracker")

            stage = self._stages[stage_id]

            if stage.status != "running":
                logger.warning(f"Cannot update progress for stage {stage_id} with status {stage.status}")
                return False

            stage.update_progress(progress)
            self._update_overall_progress()

            # Auto-save if configured
            self._maybe_auto_save()

            logger.debug(f"Updated stage {stage_id} progress to {progress:.1f}%")
            return True

    def complete_stage(self, stage_id: str, result: Optional[Any] = None) -> bool:
        """
        Complete a stage.

        Args:
            stage_id: ID of the stage to complete
            result: Optional result from the stage

        Returns:
            bool: True if stage was completed successfully

        Raises:
            ValueError: If stage ID is not found
        """
        with self._lock:
            if stage_id not in self._stages:
                raise ValueError(f"Stage {stage_id} not found in progress tracker")

            stage = self._stages[stage_id]

            if stage.status == "completed":
                logger.warning(f"Stage {stage_id} is already completed")
                return False

            stage.complete(result)
            self._update_overall_progress()

            # Check if all stages are completed
            if all(s.is_completed for s in self._stages.values()):
                self._end_time = datetime.now()
                logger.info(f"All stages completed for {self.operation_id}")

            # Auto-save if configured
            self._maybe_auto_save()

            logger.info(f"Completed stage {stage_id} for {self.operation_id}")
            return True

    def fail_stage(self, stage_id: str, error: str) -> bool:
        """
        Mark a stage as failed.

        Args:
            stage_id: ID of the stage that failed
            error: Error message describing the failure

        Returns:
            bool: True if stage was marked as failed

        Raises:
            ValueError: If stage ID is not found
        """
        with self._lock:
            if stage_id not in self._stages:
                raise ValueError(f"Stage {stage_id} not found in progress tracker")

            stage = self._stages[stage_id]
            stage.fail(error)
            self._update_overall_progress()

            # Auto-save if configured
            self._maybe_auto_save()

            logger.error(f"Stage {stage_id} failed for {self.operation_id}: {error}")
            return True

    def _update_overall_progress(self) -> None:
        """Update the overall progress model."""
        total_weighted_progress = 0.0
        total_completed_weight = 0.0
        active_stages = []
        failed_stages = []
        completed_stages = []

        for stage in self._stages.values():
            if stage.is_completed:
                total_weighted_progress += stage.weighted_progress
                total_completed_weight += stage.weight
                completed_stages.append(stage)
            elif stage.is_active:
                total_weighted_progress += stage.weighted_progress
                active_stages.append(stage)
            elif stage.is_failed:
                failed_stages.append(stage)

        # Calculate overall progress percentage
        if self._total_weight > 0:
            overall_progress = (total_weighted_progress / self._total_weight) * 100.0
        else:
            overall_progress = 0.0

        # Update the overall progress model
        self._overall_progress.current_step = len(completed_stages) + 1
        self._overall_progress.total_steps = len(self._stages)
        self._overall_progress.progress_percentage = overall_progress
        self._overall_progress.completed_steps = completed_stages
        self._overall_progress.failed_steps = failed_stages

        # Update ETA if there are active stages
        if active_stages and self._start_time:
            elapsed_time = (datetime.now() - self._start_time).total_seconds()
            if overall_progress > 0:
                estimated_total_time = (elapsed_time / overall_progress) * 100.0
                remaining_time = estimated_total_time - elapsed_time
                self._overall_progress.estimated_time_remaining = remaining_time

    def get_stage_progress(self, stage_id: str) -> Optional[StageProgress]:
        """
        Get progress information for a specific stage.

        Args:
            stage_id: ID of the stage

        Returns:
            Optional[StageProgress]: Stage progress information, None if not found
        """
        with self._lock:
            return copy.deepcopy(self._stages.get(stage_id))

    def get_all_stages(self) -> Dict[str, StageProgress]:
        """
        Get progress information for all stages.

        Returns:
            Dict[str, StageProgress]: All stage progress information
        """
        with self._lock:
            return copy.deepcopy(self._stages)

    def get_progress_model(self) -> ProgressModel:
        """
        Get the overall progress model.

        Returns:
            ProgressModel: Overall progress information
        """
        with self._lock:
            # Update current step info for the progress model
            if self._stages:
                current_step_info = None
                for stage in self._stages.values():
                    if stage.is_running:
                        current_step_info = f"Running: {stage.stage_name}"
                        break
                    elif stage.is_pending:
                        current_step_info = f"Pending: {stage.stage_name}"
                        break

                if current_step_info:
                    self._overall_progress.current_step_info = current_step_info

            return copy.deepcopy(self._overall_progress)

    def save_progress(self, file_path: Path) -> None:
        """
        Save progress state to a file.

        Args:
            file_path: Path where progress state should be saved
        """
        with self._lock:
            progress_data = {
                "operation_id": self.operation_id,
                "operation_name": self.operation_name,
                "start_time": self._start_time.isoformat() if self._start_time else None,
                "end_time": self._end_time.isoformat() if self._end_time else None,
                "total_weight": self._total_weight,
                "stages": {stage_id: stage.to_dict() for stage_id, stage in self._stages.items()},
                "overall_progress": {
                    "current_step": self._overall_progress.current_step,
                    "total_steps": self._overall_progress.total_steps,
                    "progress_percentage": self._overall_progress.progress_percentage,
                    "estimated_time_remaining": self._overall_progress.estimated_time_remaining,
                    "current_step_info": self._overall_progress.current_step_info
                }
            }

            # Create parent directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(progress_data, f, indent=2, default=str)

            self._last_save_time = datetime.now()
            logger.info(f"Saved progress state to {file_path}")

    def load_progress(self, file_path: Path) -> bool:
        """
        Load progress state from a file.

        Args:
            file_path: Path to progress state file

        Returns:
            bool: True if progress was loaded successfully
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                progress_data = json.load(f)

            with self._lock:
                # Validate operation ID matches
                if progress_data.get("operation_id") != self.operation_id:
                    logger.warning(f"Operation ID mismatch: expected {self.operation_id}, got {progress_data.get('operation_id')}")
                    return False

                # Load basic properties
                self.operation_name = progress_data.get("operation_name", self.operation_name)
                self._total_weight = progress_data.get("total_weight", 0.0)

                if progress_data.get("start_time"):
                    self._start_time = datetime.fromisoformat(progress_data["start_time"])
                if progress_data.get("end_time"):
                    self._end_time = datetime.fromisoformat(progress_data["end_time"])

                # Load stages
                self._stages = {}
                for stage_id, stage_data in progress_data.get("stages", {}).items():
                    self._stages[stage_id] = StageProgress.from_dict(stage_data)

                # Load overall progress
                overall_data = progress_data.get("overall_progress", {})
                self._overall_progress.current_step = overall_data.get("current_step", 0)
                self._overall_progress.total_steps = overall_data.get("total_steps", 0)
                self._overall_progress.progress_percentage = overall_data.get("progress_percentage", 0.0)
                self._overall_progress.estimated_time_remaining = overall_data.get("estimated_time_remaining", None)
                self._overall_progress.current_step_info = overall_data.get("current_step_info", "")

                logger.info(f"Loaded progress state from {file_path}")
                return True

        except Exception as e:
            logger.error(f"Failed to load progress state from {file_path}: {e}")
            return False

    def _maybe_auto_save(self) -> None:
        """Auto-save progress if configured and enough time has passed."""
        if not self.auto_save_interval or not self._auto_save_file_path:
            return

        if self._last_save_time:
            time_since_save = (datetime.now() - self._last_save_time).total_seconds()
            if time_since_save < self.auto_save_interval:
                return

        # Auto-save to configured file
        try:
            self.save_progress(self._auto_save_file_path)
        except Exception as e:
            logger.warning(f"Auto-save failed: {e}")

    def set_auto_save_file(self, file_path: Path) -> None:
        """
        Set the auto-save file path.

        Args:
            file_path: Path for auto-saving progress state
        """
        self._auto_save_file_path = file_path

    def reset(self) -> None:
        """Reset the progress tracker."""
        with self._lock:
            self._stages.clear()
            self._overall_progress = ProgressModel()
            self._start_time = None
            self._end_time = None
            self._total_weight = 0.0
            self._last_save_time = None

            logger.info(f"Reset progress tracker for {self.operation_id}")

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current progress state.

        Returns:
            Dict[str, Any]: Progress summary
        """
        with self._lock:
            completed_count = sum(1 for s in self._stages.values() if s.is_completed)
            running_count = sum(1 for s in self._stages.values() if s.is_running)
            failed_count = sum(1 for s in self._stages.values() if s.is_failed)
            pending_count = sum(1 for s in self._stages.values() if s.is_pending)

            duration = None
            if self._start_time:
                if self._end_time:
                    duration = (self._end_time - self._start_time).total_seconds()
                else:
                    duration = (datetime.now() - self._start_time).total_seconds()

            return {
                "operation_id": self.operation_id,
                "operation_name": self.operation_name,
                "overall_progress": self._overall_progress.progress_percentage,
                "total_stages": len(self._stages),
                "completed_stages": completed_count,
                "running_stages": running_count,
                "failed_stages": failed_count,
                "pending_stages": pending_count,
                "duration_seconds": duration,
                "estimated_time_remaining": self._overall_progress.estimated_time_remaining,
                "is_complete": completed_count == len(self._stages),
                "has_failures": failed_count > 0
            }