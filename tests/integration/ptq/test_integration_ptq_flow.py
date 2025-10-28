"""
Integration tests for complete PTQ conversion flow

Tests the end-to-end PTQ conversion process as defined in AC 1.
"""

import pytest
import tempfile
import json
import time
from pathlib import Path
from unittest.mock import patch, Mock

from npu_converter.ptq.converter import PTQConverter
from npu_converter.models.calibration import CalibrationConfig
from npu_converter.core.utils.progress_tracker import ProgressTracker


class TestPTQIntegrationFlow:
    """Integration tests for complete PTQ conversion workflow."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def mock_model_path(self):
        """Create a mock model file."""
        with tempfile.NamedTemporaryFile(suffix='.onnx', delete=False) as tmp_file:
            tmp_file.write(b'mock_onnx_model_data_for_testing')
            return tmp_file.name

    @pytest.fixture
    def calibration_config(self):
        """Create sample calibration configuration."""
        return CalibrationConfig(
            data_path="/tmp/mock_calib_data",
            batch_size=16,
            num_samples=50,
            input_shape=(1, 224, 224, 3)
        )

    @patch('npu_converter.ptq.converter.onnx.load')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    def test_complete_ptq_conversion_flow(self, mock_stat, mock_exists, mock_onnx_load,
                                        temp_output_dir, mock_model_path, calibration_config):
        """Test complete 6-step PTQ conversion flow."""
        # Setup mocks
        mock_exists.return_value = True
        mock_stat.return_value.st_size = 1024 * 1024 * 50  # 50MB

        # Mock ONNX model structure
        mock_model = Mock()
        mock_model.graph = Mock()
        mock_model.graph.input = [Mock()]
        mock_model.graph.input[0].type.tensor_type.shape.dim = [
            Mock(dim_value=1),
            Mock(dim_value=224),
            Mock(dim_value=224),
            Mock(dim_value=3)
        ]
        mock_model.graph.output = [Mock()]
        mock_model.graph.output[0].type.tensor_type.shape.dim = [
            Mock(dim_value=1),
            Mock(dim_value=1000)
        ]
        mock_model.graph.node = [Mock(type='Conv') for _ in range(15)]
        mock_model.graph.initializer = []
        mock_model.opset_import = [Mock(version=13)]
        mock_onnx_load.return_value = mock_model

        # Initialize converter with progress tracking
        converter = PTQConverter(output_dir=temp_output_dir, debug_mode=True)
        progress_tracker = ProgressTracker(enable_console_output=False)

        # Track conversion progress
        steps_completed = []
        def progress_callback(step_info, overall_progress):
            steps_completed.append(step_info.name)

        progress_tracker.add_progress_callback(progress_callback)

        # Step 1: Model Preparation
        model_info = converter.prepare_model(mock_model_path)
        assert model_info is not None
        assert model_info.model_format == "onnx"
        assert model_info.input_shape == (1, 224, 224, 3)

        # Step 2: Model Validation
        validation_result = converter.validate_model(model_info)
        assert validation_result is not None
        assert validation_result.is_valid is True

        # Step 3: Calibration Data Preparation
        calib_data = converter.prepare_calibration_data(calibration_config)
        assert calib_data is not None
        assert calib_data.validate() is True

        # Step 4: Model Quantization
        quantized_model = converter.quantize_model(model_info, calib_data)
        assert quantized_model is not None
        assert quantized_model.get_compression_ratio() > 1.0

        # Step 5: Model Compilation
        compiled_model = converter.compile_model(quantized_model)
        assert compiled_model is not None
        assert compiled_model.success is True

        # Step 6: Performance Analysis
        performance_result = converter.analyze_performance(compiled_model)
        assert performance_result is not None
        assert performance_result.throughput_fps > 0

        # Step 7: Accuracy Analysis
        accuracy_result = converter.analyze_accuracy(compiled_model)
        assert accuracy_result is not None
        assert accuracy_result.accuracy_after_quantization > 0

        # Verify all steps completed
        expected_steps = [
            "Model Preparation",
            "Model Validation",
            "Calibration Data Preparation",
            "Model Quantization",
            "Model Compilation",
            "Performance Analysis"
        ]

        for expected_step in expected_steps:
            assert expected_step in steps_completed

    @patch('npu_converter.ptq.converter.onnx.load')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    def test_ptq_conversion_with_errors(self, mock_stat, mock_exists, mock_onnx_load,
                                      temp_output_dir, mock_model_path):
        """Test PTQ conversion error handling."""
        # Setup mocks for model with unsupported operators
        mock_exists.return_value = True
        mock_stat.return_value.st_size = 1024 * 1024 * 50

        mock_model = Mock()
        mock_model.graph = Mock()
        mock_model.graph.input = [Mock()]
        mock_model.graph.input[0].type.tensor_type.shape.dim = [
            Mock(dim_value=1),
            Mock(dim_value=224),
            Mock(dim_value=224),
            Mock(dim_value=3)
        ]
        mock_model.graph.output = [Mock()]
        mock_model.graph.output[0].type.tensor_type.shape.dim = [
            Mock(dim_value=1),
            Mock(dim_value=1000)
        ]
        mock_model.graph.node = [Mock(type='UnsupportedOp') for _ in range(5)]
        mock_model.graph.initializer = []
        mock_model.opset_import = [Mock(version=13)]
        mock_onnx_load.return_value = mock_model

        converter = PTQConverter(output_dir=temp_output_dir)

        # Step 1: Model Preparation
        model_info = converter.prepare_model(mock_model_path)
        assert model_info is not None

        # Step 2: Model Validation - should fail due to unsupported operators
        validation_result = converter.validate_model(model_info)
        assert validation_result is not None
        assert validation_result.is_valid is False
        assert len(validation_result.errors) > 0
        assert "Unsupported operators" in str(validation_result.errors)

    @patch('npu_converter.ptq.converter.onnx.load')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    def test_progress_tracking_integration(self, mock_stat, mock_exists, mock_onnx_load,
                                         temp_output_dir, mock_model_path):
        """Test progress tracking integration."""
        # Setup mocks
        mock_exists.return_value = True
        mock_stat.return_value.st_size = 1024 * 1024 * 50

        mock_model = Mock()
        mock_model.graph = Mock()
        mock_model.graph.input = [Mock()]
        mock_model.graph.input[0].type.tensor_type.shape.dim = [
            Mock(dim_value=1),
            Mock(dim_value=224),
            Mock(dim_value=224),
            Mock(dim_value=3)
        ]
        mock_model.graph.output = [Mock()]
        mock_model.graph.output[0].type.tensor_type.shape.dim = [
            Mock(dim_value=1),
            Mock(dim_value=1000)
        ]
        mock_model.graph.node = [Mock(type='Conv') for _ in range(10)]
        mock_model.graph.initializer = []
        mock_model.opset_import = [Mock(version=13)]
        mock_onnx_load.return_value = mock_model

        converter = PTQConverter(output_dir=temp_output_dir)
        progress_tracker = ProgressTracker(enable_console_output=False)

        # Track detailed progress
        progress_events = []
        def detailed_callback(step_info, overall_progress):
            progress_events.append({
                'step_name': step_info.name,
                'step_status': step_info.status.value,
                'step_progress': step_info.progress_percentage,
                'overall_progress': overall_progress['overall_percentage']
            })

        progress_tracker.add_progress_callback(detailed_callback)

        # Execute conversion steps
        calibration_config = CalibrationConfig(
            data_path="/tmp/mock_calib_data",
            batch_size=16,
            num_samples=50,
            input_shape=(1, 224, 224, 3)
        )

        # Execute all steps
        model_info = converter.prepare_model(mock_model_path)
        validation_result = converter.validate_model(model_info)

        with patch('pathlib.Path.exists', return_value=True):
            calib_data = converter.prepare_calibration_data(calibration_config)

        quantized_model = converter.quantize_model(model_info, calib_data)
        compiled_model = converter.compile_model(quantized_model)
        performance_result = converter.analyze_performance(compiled_model)
        accuracy_result = converter.analyze_accuracy(compiled_model)

        # Verify progress tracking
        assert len(progress_events) == 6  # 6 steps tracked

        # Check final progress state
        final_progress = progress_tracker.get_overall_progress()
        assert final_progress['completed_steps'] == 6
        assert final_progress['overall_percentage'] == 100.0
        assert final_progress['failed_steps'] == 0

    @patch('npu_converter.ptq.converter.onnx.load')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    def test_report_generation_integration(self, mock_stat, mock_exists, mock_onnx_load,
                                          temp_output_dir, mock_model_path):
        """Test report generation integration."""
        # Setup mocks
        mock_exists.return_value = True
        mock_stat.return_value.st_size = 1024 * 1024 * 50

        mock_model = Mock()
        mock_model.graph = Mock()
        mock_model.graph.input = [Mock()]
        mock_model.graph.input[0].type.tensor_type.shape.dim = [
            Mock(dim_value=1),
            Mock(dim_value=224),
            Mock(dim_value=224),
            Mock(dim_value=3)
        ]
        mock_model.graph.output = [Mock()]
        mock_model.graph.output[0].type.tensor_type.shape.dim = [
            Mock(dim_value=1),
            Mock(dim_value=1000)
        ]
        mock_model.graph.node = [Mock(type='Conv') for _ in range(10)]
        mock_model.graph.initializer = []
        mock_model.opset_import = [Mock(version=13)]
        mock_onnx_load.return_value = mock_model

        converter = PTQConverter(output_dir=temp_output_dir)

        # Execute complete conversion
        calibration_config = CalibrationConfig(
            data_path="/tmp/mock_calib_data",
            batch_size=16,
            num_samples=50,
            input_shape=(1, 224, 224, 3)
        )

        model_info = converter.prepare_model(mock_model_path)
        validation_result = converter.validate_model(model_info)

        with patch('pathlib.Path.exists', return_value=True):
            calib_data = converter.prepare_calibration_data(calibration_config)

        quantized_model = converter.quantize_model(model_info, calib_data)
        compiled_model = converter.compile_model(quantized_model)
        performance_result = converter.analyze_performance(compiled_model)
        accuracy_result = converter.analyze_accuracy(compiled_model)

        # Generate and save report
        report = converter.generate_report()
        converter.save_report()

        # Verify report structure
        assert isinstance(report, dict)
        assert "conversion_summary" in report
        assert "model_information" in report
        assert "validation_results" in report
        assert "quantization_results" in report
        assert "performance_results" in report
        assert "accuracy_results" in report

        # Verify report was saved
        report_file = Path(temp_output_dir) / "ptq_conversion_report.json"
        assert report_file.exists()

        # Verify saved report content
        with open(report_file, 'r') as f:
            saved_report = json.load(f)
        assert saved_report == report

        # Verify key metrics
        assert report["performance_results"]["throughput_fps"] == 64.5
        assert report["accuracy_results"]["meets_accuracy_target"] is True
        assert report["quantization_results"]["compression_ratio"] == 4.0

    def test_converter_with_debug_mode(self, temp_output_dir, mock_model_path):
        """Test converter with debug mode enabled."""
        converter = PTQConverter(output_dir=temp_output_dir, debug_mode=True)

        # Verify debug mode is enabled
        assert converter.debug_mode is True
        assert converter.debug_tools is not None
        assert converter.progress_tracker is not None

        # Verify debug logging is set up
        import logging
        logger = logging.getLogger('npu_converter.ptq.converter')
        assert logger.level == logging.DEBUG

    @patch('npu_converter.ptq.converter.onnx.load')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    def test_conversion_performance_targets(self, mock_stat, mock_exists, mock_onnx_load,
                                            temp_output_dir, mock_model_path):
        """Test that conversion meets performance targets."""
        # Setup mocks
        mock_exists.return_value = True
        mock_stat.return_value.st_size = 1024 * 1024 * 50

        mock_model = Mock()
        mock_model.graph = Mock()
        mock_model.graph.input = [Mock()]
        mock_model.graph.input[0].type.tensor_type.shape.dim = [
            Mock(dim_value=1),
            Mock(dim_value=224),
            Mock(dim_value=224),
            Mock(dim_value=3)
        ]
        mock_model.graph.output = [Mock()]
        mock_model.graph.output[0].type.tensor_type.shape.dim = [
            Mock(dim_value=1),
            Mock(dim_value=1000)
        ]
        mock_model.graph.node = [Mock(type='Conv') for _ in range(10)]
        mock_model.graph.initializer = []
        mock_model.opset_import = [Mock(version=13)]
        mock_onnx_load.return_value = mock_model

        converter = PTQConverter(output_dir=temp_output_dir)

        # Execute conversion
        calibration_config = CalibrationConfig(
            data_path="/tmp/mock_calib_data",
            batch_size=16,
            num_samples=50,
            input_shape=(1, 224, 224, 3)
        )

        model_info = converter.prepare_model(mock_model_path)
        validation_result = converter.validate_model(model_info)

        with patch('pathlib.Path.exists', return_value=True):
            calib_data = converter.prepare_calibration_data(calibration_config)

        quantized_model = converter.quantize_model(model_info, calib_data)
        compiled_model = converter.compile_model(quantized_model)
        performance_result = converter.analyze_performance(compiled_model)
        accuracy_result = converter.analyze_accuracy(compiled_model)

        # Verify targets are met
        # Performance target: >30 FPS
        assert performance_result.meets_performance_target(30.0) is True
        assert performance_result.throughput_fps >= 30.0

        # Accuracy target: >98%
        assert accuracy_result.meets_accuracy_target(98.0) is True
        assert accuracy_result.accuracy_after_quantization >= 98.0

        # Compression target: >2x
        assert quantized_model.get_compression_ratio() >= 2.0

        # Speedup target: >2x
        assert performance_result.comparison_with_baseline['speedup_ratio'] >= 2.0