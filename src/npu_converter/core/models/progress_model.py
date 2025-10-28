"""
Progress Tracking Data Models

This module defines data structures for tracking progress throughout the
NPU converter system. These models provide standardized ways to monitor
conversion operations, quantization processes, and other long-running tasks.

Key Features:
- Hierarchical progress tracking
- Real-time progress updates
- ETA calculation
- Error and warning tracking
- Progress persistence and recovery
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import json
import time

from ..exceptions.conversion_errors import ValidationError


class ProgressStatus(Enum):
    """Progress status values."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ProgressStep:
    """
    Individual step within a progress track.

    Represents a single discrete step in a larger operation with its own
    progress tracking, status, and metadata.
    """

    # Basic Information
    step_id: str
    name: str
    description: Optional[str] = None

    # Progress Information
    current_progress: float = 0.0  # 0.0 to 1.0
    weight: float = 1.0  # Relative weight in overall progress

    # Status Information
    status: ProgressStatus = ProgressStatus.NOT_STARTED
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Additional Information
    metadata: Dict[str, Any] = field(default_factory=dict)
    sub_steps: List["ProgressStep"] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def start(self) -> None:
        """Mark the step as started."""
        self.status = ProgressStatus.IN_PROGRESS
        self.started_at = datetime.now()

    def complete(self) -> None:
        """Mark the step as completed."""
        self.status = ProgressStatus.COMPLETED
        self.completed_at = datetime.now()
        self.current_progress = 1.0

    def fail(self, error_message: str) -> None:
        """Mark the step as failed."""
        self.status = ProgressStatus.FAILED
        self.completed_at = datetime.now()
        self.errors.append(error_message)

    def pause(self) -> None:
        """Mark the step as paused."""
        if self.status == ProgressStatus.IN_PROGRESS:
            self.status = ProgressStatus.PAUSED

    def resume(self) -> None:
        """Resume a paused step."""
        if self.status == ProgressStatus.PAUSED:
            self.status = ProgressStatus.IN_PROGRESS

    def update_progress(self, progress: float) -> None:
        """Update progress value."""
        self.current_progress = max(0.0, min(1.0, progress))

    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)

    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)

    def get_duration(self) -> Optional[timedelta]:
        """Get the duration of the step."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        elif self.started_at:
            return datetime.now() - self.started_at
        return None

    def get_weighted_progress(self) -> float:
        """Get weighted progress contribution."""
        return self.current_progress * self.weight

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "step_id": self.step_id,
            "name": self.name,
            "description": self.description,
            "current_progress": self.current_progress,
            "weight": self.weight,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata,
            "sub_steps": [step.to_dict() for step in self.sub_steps],
            "errors": self.errors,
            "warnings": self.warnings,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProgressStep":
        """Create from dictionary representation."""
        # Handle enum conversion
        if "status" in data and isinstance(data["status"], str):
            data["status"] = ProgressStatus(data["status"])

        # Handle datetime conversions
        for dt_field in ["started_at", "completed_at"]:
            if dt_field in data and data[dt_field] is not None:
                data[dt_field] = datetime.fromisoformat(data[dt_field])

        # Handle sub-steps
        if "sub_steps" in data:
            data["sub_steps"] = [cls.from_dict(step_data) for step_data in data["sub_steps"]]

        return cls(**data)


@dataclass
class ProgressModel:
    """
    Comprehensive progress tracking model.

    This class provides complete progress tracking capabilities for
    long-running operations, including hierarchical steps, ETA calculation,
    and real-time updates.
    """

    # Basic Information
    operation_id: str
    operation_name: str
    description: Optional[str] = None

    # Overall Progress
    total_progress: float = 0.0  # 0.0 to 1.0
    status: ProgressStatus = ProgressStatus.NOT_STARTED

    # Timing Information
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None

    # Steps and Structure
    steps: List[ProgressStep] = field(default_factory=list)
    current_step_index: int = 0

    # Progress Tracking
    progress_history: List[Dict[str, Any]] = field(default_factory=list)
    update_callbacks: List[Callable[[Dict[str, Any]], None]] = field(default_factory=list)

    # Additional Information
    metadata: Dict[str, Any] = field(default_factory=dict)
    custom_metrics: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Post-initialization setup."""
        self._last_update_time = time.time()
        self._progress_samples: List[tuple] = []  # (timestamp, progress)

    def start(self) -> None:
        """Start the operation."""
        self.status = ProgressStatus.IN_PROGRESS
        self.started_at = datetime.now()
        self._record_progress_update()

    def complete(self) -> None:
        """Complete the operation."""
        self.status = ProgressStatus.COMPLETED
        self.completed_at = datetime.now()
        self.total_progress = 1.0
        self._record_progress_update()

    def fail(self, error_message: str) -> None:
        """Fail the operation."""
        self.status = ProgressStatus.FAILED
        self.completed_at = datetime.now()
        self._record_progress_update()

        # Add error to current step if available
        if self.current_step_index < len(self.steps):
            self.steps[self.current_step_index].add_error(error_message)

    def pause(self) -> None:
        """Pause the operation."""
        if self.status == ProgressStatus.IN_PROGRESS:
            self.status = ProgressStatus.PAUSED
            self._record_progress_update()

    def resume(self) -> None:
        """Resume a paused operation."""
        if self.status == ProgressStatus.PAUSED:
            self.status = ProgressStatus.IN_PROGRESS
            self._record_progress_update()

    def add_step(self, step: ProgressStep) -> None:
        """Add a new step to the operation."""
        self.steps.append(step)
        self._update_overall_progress()

    def start_step(self, step_id: str) -> bool:
        """Start a specific step."""
        for i, step in enumerate(self.steps):
            if step.step_id == step_id:
                step.start()
                self.current_step_index = i
                self._update_overall_progress()
                return True
        return False

    def complete_step(self, step_id: str) -> bool:
        """Complete a specific step."""
        for step in self.steps:
            if step.step_id == step_id:
                step.complete()
                self._update_overall_progress()
                return True
        return False

    def update_step_progress(self, step_id: str, progress: float) -> bool:
        """Update progress for a specific step."""
        for step in self.steps:
            if step.step_id == step_id:
                step.update_progress(progress)
                self._update_overall_progress()
                return True
        return False

    def set_custom_metric(self, name: str, value: float) -> None:
        """Set a custom progress metric."""
        self.custom_metrics[name] = value
        self._record_progress_update()

    def add_progress_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Add a callback for progress updates."""
        self.update_callbacks.append(callback)

    def _update_overall_progress(self) -> None:
        """Update the overall progress based on step progress."""
        if not self.steps:
            self.total_progress = 0.0
            return

        total_weight = sum(step.weight for step in self.steps)
        if total_weight == 0:
            self.total_progress = 0.0
            return

        weighted_progress = sum(step.get_weighted_progress() for step in self.steps)
        self.total_progress = weighted_progress / total_weight

        # Update ETA
        self._update_eta()

        # Record progress update
        self._record_progress_update()

    def _update_eta(self) -> None:
        """Update estimated time of completion."""
        if not self.started_at or self.total_progress <= 0:
            return

        # Calculate progress rate
        elapsed_time = (datetime.now() - self.started_at).total_seconds()
        if elapsed_time <= 0:
            return

        progress_rate = self.total_progress / elapsed_time
        if progress_rate <= 0:
            return

        # Calculate remaining time
        remaining_progress = 1.0 - self.total_progress
        remaining_time = remaining_progress / progress_rate

        self.estimated_completion = datetime.now() + timedelta(seconds=remaining_time)

    def _record_progress_update(self) -> None:
        """Record a progress update in history."""
        current_time = time.time()

        # Limit update frequency to avoid too many records
        if current_time - self._last_update_time < 0.1:  # 100ms minimum interval
            return

        self._last_update_time = current_time
        self._progress_samples.append((current_time, self.total_progress))

        # Keep only recent samples (last 1000)
        if len(self._progress_samples) > 1000:
            self._progress_samples = self._progress_samples[-1000:]

        # Create progress update
        update_data = {
            "timestamp": datetime.now().isoformat(),
            "total_progress": self.total_progress,
            "status": self.status.value,
            "current_step": self.steps[self.current_step_index].name if self.current_step_index < len(self.steps) else None,
            "estimated_completion": self.estimated_completion.isoformat() if self.estimated_completion else None,
            "custom_metrics": self.custom_metrics.copy(),
        }

        self.progress_history.append(update_data)

        # Notify callbacks
        for callback in self.update_callbacks:
            try:
                callback(update_data)
            except Exception:
                # Don't let callback errors break progress tracking
                pass

    def get_current_step(self) -> Optional[ProgressStep]:
        """Get the current step."""
        if self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None

    def get_step_by_id(self, step_id: str) -> Optional[ProgressStep]:
        """Get a step by its ID."""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None

    def get_progress_rate(self) -> Optional[float]:
        """Get the current progress rate (progress per second)."""
        if len(self._progress_samples) < 2:
            return None

        # Use last 10 samples for rate calculation
        recent_samples = self._progress_samples[-10:]
        if len(recent_samples) < 2:
            return None

        time_diff = recent_samples[-1][0] - recent_samples[0][0]
        progress_diff = recent_samples[-1][1] - recent_samples[0][1]

        if time_diff <= 0:
            return None

        return progress_diff / time_diff

    def get_elapsed_time(self) -> Optional[timedelta]:
        """Get elapsed time since start."""
        if self.started_at:
            return datetime.now() - self.started_at
        return None

    def get_remaining_time_estimate(self) -> Optional[timedelta]:
        """Get estimated remaining time."""
        if self.estimated_completion:
            return self.estimated_completion - datetime.now()
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "operation_id": self.operation_id,
            "operation_name": self.operation_name,
            "description": self.description,
            "total_progress": self.total_progress,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "estimated_completion": self.estimated_completion.isoformat() if self.estimated_completion else None,
            "steps": [step.to_dict() for step in self.steps],
            "current_step_index": self.current_step_index,
            "metadata": self.metadata,
            "custom_metrics": self.custom_metrics,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProgressModel":
        """Create from dictionary representation."""
        # Handle enum conversion
        if "status" in data and isinstance(data["status"], str):
            data["status"] = ProgressStatus(data["status"])

        # Handle datetime conversions
        for dt_field in ["created_at", "started_at", "completed_at", "estimated_completion"]:
            if dt_field in data and data[dt_field] is not None:
                data[dt_field] = datetime.fromisoformat(data[dt_field])

        # Handle steps
        if "steps" in data:
            data["steps"] = [ProgressStep.from_dict(step_data) for step_data in data["steps"]]

        # Create instance without calling __post_init__
        instance = cls.__new__(cls)
        instance.__dict__.update(data)
        instance._last_update_time = time.time()
        instance._progress_samples = []

        return instance