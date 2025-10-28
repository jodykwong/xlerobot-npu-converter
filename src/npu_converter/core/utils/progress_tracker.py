"""
PTQ Conversion Progress Tracker

This module provides real-time progress tracking for the PTQ conversion process
as defined in Acceptance Criteria 4: Provide detailed progress feedback.
"""

import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class StepStatus(Enum):
    """Status of conversion steps."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StepInfo:
    """Information about a conversion step."""
    name: str
    step_number: int
    total_steps: int
    status: StepStatus = StepStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None
    progress_percentage: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)

    def start(self):
        """Start the step."""
        self.status = StepStatus.IN_PROGRESS
        self.start_time = datetime.now()
        self.progress_percentage = 0.0

    def complete(self, details: Optional[Dict[str, Any]] = None):
        """Complete the step."""
        self.status = StepStatus.COMPLETED
        self.end_time = datetime.now()
        if self.start_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()
        self.progress_percentage = 100.0
        if details:
            self.details.update(details)

    def fail(self, error_message: str):
        """Mark the step as failed."""
        self.status = StepStatus.FAILED
        self.end_time = datetime.now()
        if self.start_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()
        self.error_message = error_message

    def update_progress(self, percentage: float, details: Optional[Dict[str, Any]] = None):
        """Update progress percentage."""
        self.progress_percentage = min(100.0, max(0.0, percentage))
        if details:
            self.details.update(details)

    def get_duration_string(self) -> str:
        """Get formatted duration string."""
        if self.duration_seconds is None:
            return "N/A"
        if self.duration_seconds < 60:
            return f"{self.duration_seconds:.1f}s"
        else:
            minutes = int(self.duration_seconds // 60)
            seconds = self.duration_seconds % 60
            return f"{minutes}m {seconds:.1f}s"


class ProgressTracker:
    """
    Tracks progress of PTQ conversion process with real-time feedback.
    """

    def __init__(self, enable_console_output: bool = True):
        """
        Initialize progress tracker.

        Args:
            enable_console_output: Whether to output progress to console
        """
        self.enable_console_output = enable_console_output
        self.logger = logging.getLogger(__name__)

        self.steps: List[StepInfo] = []
        self.current_step: Optional[StepInfo] = None
        self.conversion_start_time: Optional[datetime] = None
        self.conversion_end_time: Optional[datetime] = None

        # Progress callback functions
        self.progress_callbacks: List[callable] = []

    def add_progress_callback(self, callback: callable):
        """Add a callback function to receive progress updates."""
        self.progress_callbacks.append(callback)

    def _notify_callbacks(self, step_info: StepInfo):
        """Notify all registered callbacks of progress update."""
        for callback in self.progress_callbacks:
            try:
                callback(step_info, self.get_overall_progress())
            except Exception as e:
                self.logger.warning(f"Progress callback failed: {str(e)}")

    def start_step(self, step_name: str, step_number: int, total_steps: int):
        """Start a new conversion step."""
        # Complete previous step if still in progress
        if self.current_step and self.current_step.status == StepStatus.IN_PROGRESS:
            self.complete_current_step()

        # Start conversion if this is the first step
        if not self.conversion_start_time:
            self.conversion_start_time = datetime.now()

        # Create and start new step
        step_info = StepInfo(
            name=step_name,
            step_number=step_number,
            total_steps=total_steps
        )
        step_info.start()

        self.steps.append(step_info)
        self.current_step = step_info

        if self.enable_console_output:
            self._print_step_start(step_info)

        self._notify_callbacks(step_info)

    def complete_step(self, step_name: str, details: Optional[Dict[str, Any]] = None):
        """Complete a step by name."""
        step_info = self._find_step_by_name(step_name)
        if step_info:
            step_info.complete(details)
            if self.enable_console_output:
                self._print_step_complete(step_info)
            self._notify_callbacks(step_info)

    def complete_current_step(self, details: Optional[Dict[str, Any]] = None):
        """Complete the current step."""
        if self.current_step:
            self.current_step.complete(details)
            if self.enable_console_output:
                self._print_step_complete(self.current_step)
            self._notify_callbacks(self.current_step)

    def fail_step(self, step_name: str, error_message: str):
        """Mark a step as failed."""
        step_info = self._find_step_by_name(step_name)
        if step_info:
            step_info.fail(error_message)
            if self.enable_console_output:
                self._print_step_failed(step_info)
            self._notify_callbacks(step_info)

    def update_step_progress(self, percentage: float, details: Optional[Dict[str, Any]] = None):
        """Update progress of current step."""
        if self.current_step:
            self.current_step.update_progress(percentage, details)
            if self.enable_console_output:
                self._print_progress_update(self.current_step)
            self._notify_callbacks(self.current_step)

    def _find_step_by_name(self, step_name: str) -> Optional[StepInfo]:
        """Find step by name."""
        for step in self.steps:
            if step.name == step_name:
                return step
        return None

    def get_overall_progress(self) -> Dict[str, Any]:
        """Get overall progress information."""
        total_steps = len(self.steps)
        completed_steps = len([s for s in self.steps if s.status == StepStatus.COMPLETED])
        failed_steps = len([s for s in self.steps if s.status == StepStatus.FAILED])

        overall_percentage = (completed_steps / total_steps * 100) if total_steps > 0 else 0.0

        # Calculate total time
        total_time = None
        if self.conversion_start_time:
            end_time = self.conversion_end_time or datetime.now()
            total_time = (end_time - self.conversion_start_time).total_seconds()

        return {
            'total_steps': total_steps,
            'completed_steps': completed_steps,
            'failed_steps': failed_steps,
            'current_step': self.current_step.name if self.current_step else None,
            'overall_percentage': overall_percentage,
            'total_time_seconds': total_time,
            'steps': [
                {
                    'name': step.name,
                    'step_number': step.step_number,
                    'status': step.status.value,
                    'progress_percentage': step.progress_percentage,
                    'duration_seconds': step.duration_seconds,
                    'error_message': step.error_message
                }
                for step in self.steps
            ]
        }

    def get_total_time(self) -> Optional[float]:
        """Get total conversion time in seconds."""
        if self.conversion_start_time and self.conversion_end_time:
            return (self.conversion_end_time - self.conversion_start_time).total_seconds()
        elif self.conversion_start_time:
            return (datetime.now() - self.conversion_start_time).total_seconds()
        return None

    def finish_conversion(self):
        """Mark the entire conversion as finished."""
        self.conversion_end_time = datetime.now()
        if self.current_step and self.current_step.status == StepStatus.IN_PROGRESS:
            self.complete_current_step()

        if self.enable_console_output:
            self._print_conversion_summary()

    def _print_step_start(self, step_info: StepInfo):
        """Print step start message."""
        progress_bar = self._create_progress_bar(0, step_info.step_number, step_info.total_steps)
        print(f"\n🚀 Starting Step {step_info.step_number}/{step_info.total_steps}: {step_info.name}")
        print(f"   {progress_bar}")

    def _print_step_complete(self, step_info: StepInfo):
        """Print step completion message."""
        progress_bar = self._create_progress_bar(100, step_info.step_number, step_info.total_steps)
        print(f"✅ Step {step_info.step_number}/{step_info.total_steps} Complete: {step_info.name} ({step_info.get_duration_string()})")
        print(f"   {progress_bar}")

        # Print step details if available
        if step_info.details:
            print("   Details:")
            for key, value in step_info.details.items():
                print(f"     • {key}: {value}")

    def _print_step_failed(self, step_info: StepInfo):
        """Print step failure message."""
        progress_bar = self._create_progress_bar(0, step_info.step_number, step_info.total_steps)
        print(f"❌ Step {step_info.step_number}/{step_info.total_steps} Failed: {step_info.name} ({step_info.get_duration_string()})")
        print(f"   {progress_bar}")
        print(f"   Error: {step_info.error_message}")

    def _print_progress_update(self, step_info: StepInfo):
        """Print progress update."""
        if step_info.progress_percentage > 0:
            progress_bar = self._create_progress_bar(step_info.progress_percentage, step_info.step_number, step_info.total_steps)
            print(f"   {progress_bar} {step_info.progress_percentage:.1f}%")

    def _print_conversion_summary(self):
        """Print conversion summary."""
        overall_progress = self.get_overall_progress()
        total_time = self.get_total_time()

        print(f"\n{'='*60}")
        print(f"🎉 PTQ Conversion Summary")
        print(f"{'='*60}")
        print(f"Total Steps: {overall_progress['total_steps']}")
        print(f"Completed: {overall_progress['completed_steps']}")
        print(f"Failed: {overall_progress['failed_steps']}")
        print(f"Overall Progress: {overall_progress['overall_percentage']:.1f}%")

        if total_time:
            print(f"Total Time: {self._format_duration(total_time)}")

        print(f"\nStep Details:")
        for step in self.steps:
            status_emoji = "✅" if step.status == StepStatus.COMPLETED else "❌" if step.status == StepStatus.FAILED else "⏳"
            print(f"  {status_emoji} {step.name} ({step.get_duration_string()})")

    def _create_progress_bar(self, percentage: float, current_step: int, total_steps: int) -> str:
        """Create a progress bar string."""
        bar_width = 30
        filled_width = int(bar_width * percentage / 100)
        bar = "█" * filled_width + "░" * (bar_width - filled_width)
        return f"[{bar}]"

    def _format_duration(self, seconds: float) -> str:
        """Format duration in seconds to human readable string."""
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds:.1f}s"
        else:
            hours = int(seconds // 3600)
            remaining_minutes = int((seconds % 3600) // 60)
            return f"{hours}h {remaining_minutes}m"

    def get_status_message(self) -> str:
        """Get current status message for display."""
        if not self.current_step:
            return "Ready to start PTQ conversion"

        if self.current_step.status == StepStatus.IN_PROGRESS:
            return f"Executing: {self.current_step.name} ({self.current_step.progress_percentage:.1f}%)"
        elif self.current_step.status == StepStatus.COMPLETED:
            return f"Completed: {self.current_step.name}"
        elif self.current_step.status == StepStatus.FAILED:
            return f"Failed: {self.current_step.name} - {self.current_step.error_message}"
        else:
            return f"Status: {self.current_step.status.value}"

    def export_progress_report(self) -> Dict[str, Any]:
        """Export detailed progress report."""
        overall_progress = self.get_overall_progress()

        report = {
            'conversion_info': {
                'start_time': self.conversion_start_time.isoformat() if self.conversion_start_time else None,
                'end_time': self.conversion_end_time.isoformat() if self.conversion_end_time else None,
                'total_duration_seconds': self.get_total_time(),
                'status': 'completed' if self.conversion_end_time else 'in_progress'
            },
            'overall_progress': overall_progress,
            'step_details': []
        }

        for step in self.steps:
            step_detail = {
                'name': step.name,
                'step_number': step.step_number,
                'total_steps': step.total_steps,
                'status': step.status.value,
                'start_time': step.start_time.isoformat() if step.start_time else None,
                'end_time': step.end_time.isoformat() if step.end_time else None,
                'duration_seconds': step.duration_seconds,
                'progress_percentage': step.progress_percentage,
                'error_message': step.error_message,
                'details': step.details
            }
            report['step_details'].append(step_detail)

        return report