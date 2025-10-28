"""
Unit tests for Progress Tracker

This module contains unit tests for the ProgressTracker class,
testing stage management, progress calculation, and persistence.
"""

import pytest
import tempfile
import json
import time
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from npu_converter.converters.progress_tracker import (
    ProgressTracker,
    StageProgress,
    ConversionStage
)
from npu_converter.core.models.progress_model import ProgressStep


class TestStageProgress:
    """Test cases for StageProgress class."""

    def test_initialization(self):
        """Test StageProgress initialization."""
        stage = StageProgress(
            stage_id="test_stage",
            stage_name="Test Stage",
            status="pending",
            progress=0.0,
            weight=1.0
        )

        assert stage.stage_id == "test_stage"
        assert stage.stage_name == "Test Stage"
        assert stage.status == "pending"
        assert stage.progress == 0.0
        assert stage.weight == 1.0
        assert stage.start_time is None
        assert stage.end_time is None
        assert stage.duration is None

    def test_start(self):
        """Test starting a stage."""
        stage = StageProgress(
            stage_id="test_stage",
            stage_name="Test Stage",
            status="pending",
            progress=0.0,
            weight=1.0
        )

        start_time = datetime.now()
        stage.start()

        assert stage.status == "running"
        assert stage.progress == 0.0
        assert stage.start_time is not None
        assert stage.start_time >= start_time

    def test_update_progress(self):
        """Test updating stage progress."""
        stage = StageProgress(
            stage_id="test_stage",
            stage_name="Test Stage",
            status="running",
            progress=0.0,
            weight=1.0
        )

        stage.update_progress(50.0)

        assert stage.progress == 50.0

        # Test progress bounds
        stage.update_progress(-10.0)
        assert stage.progress == 0.0

        stage.update_progress(150.0)
        assert stage.progress == 100.0

    def test_complete(self):
        """Test completing a stage."""
        stage = StageProgress(
            stage_id="test_stage",
            stage_name="Test Stage",
            status="running",
            progress=50.0,
            weight=1.0
        )

        start_time = datetime.now() - timedelta(seconds=5)
        stage.start_time = start_time

        result = {"status": "success"}
        stage.complete(result)

        assert stage.status == "completed"
        assert stage.progress == 100.0
        assert stage.result == result
        assert stage.end_time is not None
        assert stage.duration is not None
        assert stage.duration > 0

    def test_fail(self):
        """Test failing a stage."""
        stage = StageProgress(
            stage_id="test_stage",
            stage_name="Test Stage",
            status="running",
            progress=50.0,
            weight=1.0
        )

        start_time = datetime.now() - timedelta(seconds=3)
        stage.start_time = start_time

        error_message = "Test error"
        stage.fail(error_message)

        assert stage.status == "failed"
        assert stage.error == error_message
        assert stage.end_time is not None
        assert stage.duration is not None
        assert stage.duration > 0

    def test_weighted_progress(self):
        """Test weighted progress calculation."""
        stage = StageProgress(
            stage_id="test_stage",
            stage_name="Test Stage",
            status="running",
            progress=60.0,
            weight=2.5
        )

        weighted_progress = stage.weighted_progress
        assert weighted_progress == 1.5  # 60% * 2.5 = 1.5

    def test_properties(self):
        """Test stage progress properties."""
        stage = StageProgress(
            stage_id="test_stage",
            stage_name="Test Stage",
            status="running",
            progress=50.0,
            weight=1.0
        )

        assert stage.is_active is True
        assert stage.is_completed is False
        assert stage.is_failed is False
        assert stage.is_pending is False

        # Test completed stage
        stage.status = "completed"
        assert stage.is_active is False
        assert stage.is_completed is True
        assert stage.is_failed is False
        assert stage.is_pending is False

        # Test failed stage
        stage.status = "failed"
        assert stage.is_active is False
        assert stage.is_completed is False
        assert stage.is_failed is True
        assert stage.is_pending is False

        # Test pending stage
        stage.status = "pending"
        assert stage.is_active is False
        assert stage.is_completed is False
        assert stage.is_failed is False
        assert stage.is_pending is True

    def test_to_dict(self):
        """Test converting to dictionary."""
        stage = StageProgress(
            stage_id="test_stage",
            stage_name="Test Stage",
            status="running",
            progress=50.0,
            weight=1.0
        )

        stage_dict = stage.to_dict()

        assert isinstance(stage_dict, dict)
        assert stage_dict["stage_id"] == "test_stage"
        assert stage_dict["stage_name"] == "Test Stage"
        assert stage_dict["status"] == "running"
        assert stage_dict["progress"] == 50.0
        assert stage_dict["weight"] == 1.0

    def test_from_dict(self):
        """Test creating from dictionary."""
        stage_dict = {
            "stage_id": "test_stage",
            "stage_name": "Test Stage",
            "status": "running",
            "progress": 50.0,
            "weight": 1.0,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "duration": None,
            "result": None,
            "error": None,
            "metadata": {}
        }

        stage = StageProgress.from_dict(stage_dict)

        assert stage.stage_id == "test_stage"
        assert stage.stage_name == "Test Stage"
        assert stage.status == "running"
        assert stage.progress == 50.0
        assert stage.weight == 1.0
        assert stage.start_time is not None


class TestProgressTracker:
    """Test cases for ProgressTracker class."""

    def test_initialization(self):
        """Test ProgressTracker initialization."""
        tracker = ProgressTracker("test_op", "Test Operation")

        assert tracker.operation_id == "test_op"
        assert tracker.operation_name == "Test Operation"
        assert tracker._total_weight == 0.0
        assert len(tracker._stages) == 0
        assert tracker._start_time is None
        assert tracker._end_time is None

    def test_add_stage(self):
        """Test adding a stage."""
        tracker = ProgressTracker("test_op", "Test Operation")

        progress_step = ProgressStep(
            step_id="test_stage",
            name="Test Stage",
            weight=1.5
        )

        tracker.add_stage(progress_step)

        assert len(tracker._stages) == 1
        assert "test_stage" in tracker._stages
        assert tracker._total_weight == 1.5

        stage = tracker._stages["test_stage"]
        assert stage.stage_id == "test_stage"
        assert stage.stage_name == "Test Stage"
        assert stage.weight == 1.5

    def test_add_multiple_stages(self):
        """Test adding multiple stages."""
        tracker = ProgressTracker("test_op", "Test Operation")

        steps = [
            ProgressStep(step_id="stage1", name="Stage 1", weight=0.5),
            ProgressStep(step_id="stage2", name="Stage 2", weight=1.0),
            ProgressStep(step_id="stage3", name="Stage 3", weight=1.5)
        ]

        for step in steps:
            tracker.add_stage(step)

        assert len(tracker._stages) == 3
        assert tracker._total_weight == 3.0

    def test_start_stage(self):
        """Test starting a stage."""
        tracker = ProgressTracker("test_op", "Test Operation")

        progress_step = ProgressStep(
            step_id="test_stage",
            name="Test Stage",
            weight=1.0
        )
        tracker.add_stage(progress_step)

        result = tracker.start_stage("test_stage")

        assert result is True
        assert tracker._start_time is not None
        assert tracker._stages["test_stage"].is_active is True

    def test_start_nonexistent_stage(self):
        """Test starting a non-existent stage."""
        tracker = ProgressTracker("test_op", "Test Operation")

        with pytest.raises(ValueError, match="Stage nonexistent not found"):
            tracker.start_stage("nonexistent")

    def test_start_already_running_stage(self):
        """Test starting an already running stage."""
        tracker = ProgressTracker("test_op", "Test Operation")

        progress_step = ProgressStep(
            step_id="test_stage",
            name="Test Stage",
            weight=1.0
        )
        tracker.add_stage(progress_step)
        tracker.start_stage("test_stage")

        # Try to start again
        result = tracker.start_stage("test_stage")

        assert result is False

    def test_update_stage_progress(self):
        """Test updating stage progress."""
        tracker = ProgressTracker("test_op", "Test Operation")

        progress_step = ProgressStep(
            step_id="test_stage",
            name="Test Stage",
            weight=1.0
        )
        tracker.add_stage(progress_step)
        tracker.start_stage("test_stage")

        result = tracker.update_stage_progress("test_stage", 75.0)

        assert result is True
        assert tracker._stages["test_stage"].progress == 75.0

    def test_update_nonexistent_stage_progress(self):
        """Test updating progress for non-existent stage."""
        tracker = ProgressTracker("test_op", "Test Operation")

        with pytest.raises(ValueError, match="Stage nonexistent not found"):
            tracker.update_stage_progress("nonexistent", 50.0)

    def test_complete_stage(self):
        """Test completing a stage."""
        tracker = ProgressTracker("test_op", "Test Operation")

        progress_step = ProgressStep(
            step_id="test_stage",
            name="Test Stage",
            weight=1.0
        )
        tracker.add_stage(progress_step)
        tracker.start_stage("test_stage")

        result = tracker.complete_stage("test_stage", {"status": "success"})

        assert result is True
        assert tracker._stages["test_stage"].is_completed is True
        assert tracker._stages["test_stage"].result == {"status": "success"}

    def test_complete_nonexistent_stage(self):
        """Test completing a non-existent stage."""
        tracker = ProgressTracker("test_op", "Test Operation")

        with pytest.raises(ValueError, match="Stage nonexistent not found"):
            tracker.complete_stage("nonexistent")

    def test_fail_stage(self):
        """Test failing a stage."""
        tracker = ProgressTracker("test_op", "Test Operation")

        progress_step = ProgressStep(
            step_id="test_stage",
            name="Test Stage",
            weight=1.0
        )
        tracker.add_stage(progress_step)
        tracker.start_stage("test_stage")

        result = tracker.fail_stage("test_stage", "Test error")

        assert result is True
        assert tracker._stages["test_stage"].is_failed is True
        assert tracker._stages["test_stage"].error == "Test error"

    def test_get_stage_progress(self):
        """Test getting stage progress."""
        tracker = ProgressTracker("test_op", "Test Operation")

        progress_step = ProgressStep(
            step_id="test_stage",
            name="Test Stage",
            weight=1.0
        )
        tracker.add_stage(progress_step)

        stage_progress = tracker.get_stage_progress("test_stage")

        assert stage_progress is not None
        assert stage_progress.stage_id == "test_stage"
        assert stage_progress.stage_name == "Test Stage"

    def test_get_nonexistent_stage_progress(self):
        """Test getting progress for non-existent stage."""
        tracker = ProgressTracker("test_op", "Test Operation")

        stage_progress = tracker.get_stage_progress("nonexistent")

        assert stage_progress is None

    def test_get_all_stages(self):
        """Test getting all stages."""
        tracker = ProgressTracker("test_op", "Test Operation")

        steps = [
            ProgressStep(step_id="stage1", name="Stage 1", weight=0.5),
            ProgressStep(step_id="stage2", name="Stage 2", weight=1.0)
        ]

        for step in steps:
            tracker.add_stage(step)

        all_stages = tracker.get_all_stages()

        assert len(all_stages) == 2
        assert "stage1" in all_stages
        assert "stage2" in all_stages

    def test_overall_progress_calculation(self):
        """Test overall progress calculation."""
        tracker = ProgressTracker("test_op", "Test Operation")

        # Add stages with different weights
        steps = [
            ProgressStep(step_id="stage1", name="Stage 1", weight=1.0),
            ProgressStep(step_id="stage2", name="Stage 2", weight=2.0),
            ProgressStep(step_id="stage3", name="Stage 3", weight=1.0)
        ]

        for step in steps:
            tracker.add_stage(step)

        # Start first stage and update progress
        tracker.start_stage("stage1")
        tracker.update_stage_progress("stage1", 50.0)

        # Overall progress should be: (50% * 1.0) / 4.0 = 12.5%
        progress_model = tracker.get_progress_model()
        assert abs(progress_model.progress_percentage - 12.5) < 0.1

    def test_save_progress(self):
        """Test saving progress state."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = ProgressTracker("test_op", "Test Operation")

            progress_step = ProgressStep(
                step_id="test_stage",
                name="Test Stage",
                weight=1.0
            )
            tracker.add_stage(progress_step)
            tracker.start_stage("test_stage")

            progress_file = Path(temp_dir) / "progress.json"
            tracker.save_progress(progress_file)

            assert progress_file.exists()
            with open(progress_file, 'r') as f:
                data = json.load(f)
                assert data["operation_id"] == "test_op"
                assert data["operation_name"] == "Test Operation"
                assert "test_stage" in data["stages"]

    def test_load_progress(self):
        """Test loading progress state."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test progress file
            progress_data = {
                "operation_id": "test_op",
                "operation_name": "Test Operation",
                "start_time": datetime.now().isoformat(),
                "total_weight": 1.0,
                "stages": {
                    "test_stage": {
                        "stage_id": "test_stage",
                        "stage_name": "Test Stage",
                        "status": "running",
                        "progress": 50.0,
                        "weight": 1.0,
                        "start_time": datetime.now().isoformat(),
                        "end_time": None,
                        "duration": None,
                        "result": None,
                        "error": None,
                        "metadata": {}
                    }
                }
            }

            progress_file = Path(temp_dir) / "progress.json"
            with open(progress_file, 'w') as f:
                json.dump(progress_data, f)

            # Load progress
            tracker = ProgressTracker("test_op", "Test Operation")
            result = tracker.load_progress(progress_file)

            assert result is True
            assert len(tracker._stages) == 1
            stage = tracker._stages["test_stage"]
            assert stage.stage_id == "test_stage"
            assert stage.progress == 50.0

    def test_load_progress_mismatched_id(self):
        """Test loading progress with mismatched operation ID."""
        with tempfile.TemporaryDirectory() as temp_dir:
            progress_data = {
                "operation_id": "different_op",
                "operation_name": "Different Operation",
                "total_weight": 0.0,
                "stages": {}
            }

            progress_file = Path(temp_dir) / "progress.json"
            with open(progress_file, 'w') as f:
                json.dump(progress_data, f)

            tracker = ProgressTracker("test_op", "Test Operation")
            result = tracker.load_progress(progress_file)

            assert result is False

    def test_get_summary(self):
        """Test getting progress summary."""
        tracker = ProgressTracker("test_op", "Test Operation")

        steps = [
            ProgressStep(step_id="stage1", name="Stage 1", weight=1.0),
            ProgressStep(step_id="stage2", name="Stage 2", weight=1.0),
            ProgressStep(step_id="stage3", name="Stage 3", weight=1.0)
        ]

        for step in steps:
            tracker.add_stage(step)

        # Complete one stage, start another, fail one
        tracker.start_stage("stage1")
        tracker.complete_stage("stage1", {})
        tracker.start_stage("stage2")
        tracker.fail_stage("stage3", "Test error")

        summary = tracker.get_summary()

        assert summary["operation_id"] == "test_op"
        assert summary["operation_name"] == "Test Operation"
        assert summary["total_stages"] == 3
        assert summary["completed_stages"] == 1
        assert summary["running_stages"] == 1
        assert summary["failed_stages"] == 1
        assert summary["pending_stages"] == 0
        assert summary["is_complete"] is False
        assert summary["has_failures"] is True

    def test_reset(self):
        """Test resetting the progress tracker."""
        tracker = ProgressTracker("test_op", "Test Operation")

        progress_step = ProgressStep(
            step_id="test_stage",
            name="Test Stage",
            weight=1.0
        )
        tracker.add_stage(progress_step)
        tracker.start_stage("test_stage")

        tracker.reset()

        assert len(tracker._stages) == 0
        assert tracker._total_weight == 0.0
        assert tracker._start_time is None
        assert tracker._end_time is None

    def test_thread_safety(self):
        """Test that progress tracker is thread-safe."""
        tracker = ProgressTracker("test_op", "Test Operation")

        progress_step = ProgressStep(
            step_id="test_stage",
            name="Test Stage",
            weight=1.0
        )
        tracker.add_stage(progress_step)

        def update_progress():
            tracker.start_stage("test_stage")
            tracker.update_stage_progress("test_stage", 50.0)

        # Run multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=update_progress)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Should not raise any exceptions
        assert True  # If we get here, no exceptions occurred