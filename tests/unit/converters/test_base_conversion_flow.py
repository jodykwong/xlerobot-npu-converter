"""
Unit tests for BaseConversionFlow

This module contains unit tests for the BaseConversionFlow class,
testing core functionality, stage management, and error handling.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from npu_converter.converters.base_conversion_flow import BaseConversionFlow, ConversionStage
from npu_converter.core.models.conversion_model import ConversionModel
from npu_converter.core.models.config_model import ConfigModel
from npu_converter.core.models.progress_model import ProgressStep
from npu_converter.core.models.result_model import ResultModel
from npu_converter.core.exceptions.conversion_errors import ConversionError


class TestBaseConversionFlow(BaseConversionFlow):
    """Test implementation of BaseConversionFlow for testing."""

    def create_progress_steps(self):
        """Create test progress steps."""
        return [
            ProgressStep(
                step_id="test_step_1",
                name="Test Step 1",
                description="First test step",
                weight=0.5
            ),
            ProgressStep(
                step_id="test_step_2",
                name="Test Step 2",
                description="Second test step",
                weight=0.5
            )
        ]

    def execute_conversion_stage(self, stage, conversion_model):
        """Execute test stage."""
        return True

    def handle_stage_completion(self, stage, result):
        """Handle test stage completion."""
        pass


class TestBaseConversionFlowClass:
    """Test cases for BaseConversionFlow class."""

    def test_initialization(self):
        """Test BaseConversionFlow initialization."""
        flow = TestBaseConversionFlow("Test Flow", "1.0.0")

        assert flow.name == "Test Flow"
        assert flow.version == "1.0.0"
        assert flow.status == "initialized"
        assert flow.operation_id is not None
        assert isinstance(flow.operation_id, str)
        assert flow.progress_tracker is None
        assert flow.status_callbacks == []
        assert flow.conversion_logger is None

    def test_initialization_with_config(self):
        """Test initialization with configuration."""
        config = ConfigModel()
        flow = TestBaseConversionFlow("Test Flow", "1.0.0", config)

        assert flow.config == config

    def test_initialization_with_operation_id(self):
        """Test initialization with custom operation ID."""
        operation_id = "test_operation_123"
        flow = TestBaseConversionFlow("Test Flow", "1.0.0", operation_id=operation_id)

        assert flow.operation_id == operation_id

    def test_initialize_conversion_components(self):
        """Test conversion components initialization."""
        flow = TestBaseConversionFlow("Test Flow", "1.0.0")

        # Components should be None initially
        assert flow.progress_tracker is None
        assert flow.conversion_logger is None

        # Initialize components
        flow.initialize_conversion_components()

        # Components should be initialized
        assert flow.progress_tracker is not None
        assert flow.conversion_logger is not None
        assert flow.progress_tracker.operation_id == flow.operation_id

    def test_add_status_callback(self):
        """Test adding status callbacks."""
        flow = TestBaseConversionFlow("Test Flow", "1.0.0")
        callback = Mock()

        # Add callback
        flow.add_status_callback(callback)

        # Should be in callbacks list
        assert len(flow.status_callbacks) == 1
        assert flow.status_callbacks[0] == callback

    def test_remove_status_callback(self):
        """Test removing status callbacks."""
        flow = TestBaseConversionFlow("Test Flow", "1.0.0")
        callback = Mock()
        flow.add_status_callback(callback)

        # Remove callback
        removed = flow.remove_status_callback(callback)

        assert removed is True
        assert len(flow.status_callbacks) == 0

    def test_remove_nonexistent_callback(self):
        """Test removing non-existent callback."""
        flow = TestBaseConversionFlow("Test Flow", "1.0.0")
        callback = Mock()

        # Try to remove callback that wasn't added
        removed = flow.remove_status_callback(callback)

        assert removed is False

    def test_convert_success(self):
        """Test successful conversion process."""
        flow = TestBaseConversionFlow("Test Flow", "1.0.0")
        flow.initialize_conversion_components()

        # Create mock conversion model
        conversion_model = ConversionModel(
            model_path=Path("test_model.onnx"),
            model_type="test"
        )

        # Execute conversion
        result = flow.convert(conversion_model)

        # Verify result
        assert isinstance(result, ResultModel)
        assert result.success is True
        assert "conversion_flow" in result.metadata
        assert result.metadata["conversion_flow"] == flow.name

    def test_convert_with_callback(self):
        """Test conversion with progress callback."""
        flow = TestBaseConversionFlow("Test Flow", "1.0.0")
        flow.initialize_conversion_components()

        callback = Mock()
        conversion_model = ConversionModel(
            model_path=Path("test_model.onnx"),
            model_type="test"
        )

        # Execute conversion with callback
        result = flow.convert(conversion_model, callback)

        # Callback should have been called
        callback.assert_called()

    def test_get_detailed_progress(self):
        """Test getting detailed progress information."""
        flow = TestBaseConversionFlow("Test Flow", "1.0.0")
        flow.initialize_conversion_components()

        progress_info = flow.get_detailed_progress()

        # Verify structure
        assert "operation_id" in progress_info
        assert "conversion_flow" in progress_info
        assert "status" in progress_info
        assert "stage_results" in progress_info
        assert "stage_durations" in progress_info

        # Verify content
        assert progress_info["operation_id"] == flow.operation_id
        assert progress_info["conversion_flow"] == flow.name
        assert progress_info["status"] == "initialized"

    def test_save_and_load_progress_state(self):
        """Test saving and loading progress state."""
        with tempfile.TemporaryDirectory() as temp_dir:
            flow = TestBaseConversionFlow("Test Flow", "1.0.0")
            flow.initialize_conversion_components()

            # Save progress state
            progress_file = Path(temp_dir) / "progress.json"
            flow.save_progress_state(progress_file)

            # Verify file exists
            assert progress_file.exists()

            # Create new flow and load progress
            new_flow = TestBaseConversionFlow("Test Flow", "1.0.0")
            new_flow.initialize_conversion_components()

            loaded = new_flow.load_progress_state(progress_file)
            assert loaded is True

    def test_load_nonexistent_progress_state(self):
        """Test loading non-existent progress state."""
        flow = TestBaseConversionFlow("Test Flow", "1.0.0")
        flow.initialize_conversion_components()

        # Try to load non-existent file
        non_existent = Path("/tmp/non_existent_progress.json")
        loaded = flow.load_progress_state(non_existent)

        assert loaded is False

    def test_get_stage_duration(self):
        """Test getting stage duration."""
        flow = TestBaseConversionFlow("Test Flow", "1.0.0")

        # Initially should be None
        duration = flow.get_stage_duration("test_step")
        assert duration is None

        # After adding a duration
        flow._stage_durations["test_step"] = 123.45
        duration = flow.get_stage_duration("test_step")
        assert duration == 123.45

    def test_get_stage_result(self):
        """Test getting stage result."""
        flow = TestBaseConversionFlow("Test Flow", "1.0.0")

        # Initially should be None
        result = flow.get_stage_result("test_step")
        assert result is None

        # After adding a result
        test_result = {"status": "success"}
        flow._stage_results["test_step"] = test_result
        result = flow.get_stage_result("test_step")
        assert result == test_result

    def test_string_representation(self):
        """Test string representation of conversion flow."""
        flow = TestBaseConversionFlow("Test Flow", "1.0.0")

        str_repr = str(flow)
        assert "Test Flow Conversion Flow v1.0.0" in str_repr
        assert flow.operation_id in str_repr
        assert "initialized" in str_repr

    def test_detailed_representation(self):
        """Test detailed representation of conversion flow."""
        flow = TestBaseConversionFlow("Test Flow", "1.0.0")

        repr_str = repr(flow)
        assert "TestBaseConversionFlow" in repr_str
        assert "Test Flow" in repr_str
        assert "1.0.0" in repr_str
        assert flow.operation_id in repr_str


class TestConversionStage:
    """Test cases for ConversionStage enum."""

    def test_conversion_stage_values(self):
        """Test conversion stage enum values."""
        stages = [
            "initialization",
            "validation",
            "preparation",
            "loading",
            "preprocessing",
            "quantization",
            "compilation",
            "optimization",
            "validation_post",
            "export",
            "completed",
            "failed"
        ]

        for stage_name in stages:
            stage = ConversionStage(stage_name)
            assert stage.value == stage_name

    def test_conversion_stage_equality(self):
        """Test conversion stage equality comparison."""
        stage1 = ConversionStage.initialization
        stage2 = ConversionStage("initialization")
        stage3 = ConversionStage.validation

        assert stage1 == stage2
        assert stage1 != stage3


class TestErrorHandling:
    """Test cases for error handling in BaseConversionFlow."""

    def test_execute_stage_with_exception(self):
        """Test stage execution when exception occurs."""
        class FailingFlow(TestBaseConversionFlow):
            def execute_conversion_stage(self, stage, conversion_model):
                if stage.value == "test_step_1":
                    raise ValueError("Test error")
                return True

        flow = FailingFlow("Test Flow", "1.0.0")
        flow.initialize_conversion_components()

        conversion_model = ConversionModel(
            model_path=Path("test_model.onnx"),
            model_type="test"
        )

        # Should raise ConversionError due to stage failure
        with pytest.raises(ConversionError, match="Stage execution failed"):
            flow.convert(conversion_model)

    def test_convert_without_initialization(self):
        """Test conversion without component initialization."""
        flow = TestBaseConversionFlow("Test Flow", "1.0.0")

        conversion_model = ConversionModel(
            model_path=Path("test_model.onnx"),
            model_type="test"
        )

        # Should automatically initialize components
        result = flow.convert(conversion_model)
        assert result.success is True
        assert flow.progress_tracker is not None

    def test_progress_tracker_initialization(self):
        """Test progress tracker is properly initialized."""
        flow = TestBaseConversionFlow("Test Flow", "1.0.0")

        # Before initialization, should be None
        assert flow.progress_tracker is None

        # Initialize conversion components
        flow.initialize_conversion_components()

        # After initialization, should be properly set up
        assert flow.progress_tracker is not None
        assert flow.progress_tracker.operation_id == flow.operation_id

    def test_conversion_logger_initialization(self):
        """Test conversion logger is properly initialized."""
        flow = TestBaseConversionFlow("Test Flow", "1.0.0")

        # Before initialization, should be None
        assert flow.conversion_logger is None

        # Initialize conversion components
        flow.initialize_conversion_components()

        # After initialization, should be properly set up
        assert flow.conversion_logger is not None
        assert flow.conversion_logger.operation_id == flow.operation_id