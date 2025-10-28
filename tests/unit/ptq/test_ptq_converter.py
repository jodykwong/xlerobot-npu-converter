"""
Unit tests for PTQ Converter

Tests the complete 6-step PTQ conversion process as defined in AC 1.
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from npu_converter.ptq.converter import PTQConverter
from npu_converter.models.calibration import (
    CalibrationConfig, ModelInfo, ValidationResult,
    QuantizedModel, CompiledModel, PerformanceResult, AccuracyResult
)


class TestPTQConverter:
    """Test suite for PTQConverter class."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def sample_model_path(self):
        """Create a sample ONNX model file."""
        with tempfile.NamedTemporaryFile(suffix='.onnx', delete=False) as tmp_file:
            # Write some mock ONNX model data
            tmp_file.write(b'mock_onnx_model_data')
            return tmp_file.name

    @pytest.fixture
    def ptq_converter(self, temp_output_dir):
        """Create PTQConverter instance."""
        return PTQConverter(output_dir=temp_output_dir, debug_mode=False)

    @pytest.fixture
    def calibration_config(self):
        """Create sample calibration configuration."""
        return CalibrationConfig(
            data_path="/tmp/mock_calib_data",
            batch_size=32,
            num_samples=100,
            input_shape=(1, 224, 224, 3)
        )

    def test_converter_initialization(self, temp_output_dir):
        """Test PTQConverter initialization."""
        converter = PTQConverter(output_dir=temp_output_dir)

        assert converter.output_dir == Path(temp_output_dir)
        assert converter.debug_mode is False
        assert converter.model_info is None
        assert converter.validation_result is None
        assert converter.calibration_data is None
        assert converter.quantized_model is None
        assert converter.compiled_model is None
        assert converter.performance_result is None
        assert converter.accuracy_result is None

    @patch('npu_converter.ptq.converter.onnx.load')
    def test_prepare_model_success(self, mock_onnx_load, ptq_converter, sample_model_path):
        """Test successful model preparation."""
        # Mock ONNX model
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

        # Mock file size
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value.st_size = 1024 * 1024 * 100  # 100MB

            result = ptq_converter.prepare_model(sample_model_path)

        assert isinstance(result, ModelInfo)
        assert result.model_path == sample_model_path
        assert result.input_shape == (1, 224, 224, 3)
        assert result.output_shape == (1, 1000)
        assert result.model_size_mb == 100.0
        assert result.model_format == "onnx"
        assert result.opset_version == 13
        assert len(result.supported_ops) > 0

    def test_prepare_model_file_not_found(self, ptq_converter):
        """Test model preparation with non-existent file."""
        with pytest.raises(FileNotFoundError):
            ptq_converter.prepare_model("/nonexistent/model.onnx")

    def test_validate_model_success(self, ptq_converter):
        """Test successful model validation."""
        model_info = ModelInfo(
            model_path="/tmp/model.onnx",
            input_shape=(1, 224, 224, 3),
            output_shape=(1, 1000),
            model_size_mb=100.0,
            num_parameters=1000000,
            model_format="onnx",
            supported_ops=["Conv", "Relu"],
            unsupported_ops=[]
        )

        result = ptq_converter.validate_model(model_info)

        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert result.compatibility_score == 1.0
        assert len(result.errors) == 0

    def test_validate_model_with_unsupported_ops(self, ptq_converter):
        """Test model validation with unsupported operators."""
        model_info = ModelInfo(
            model_path="/tmp/model.onnx",
            input_shape=(1, 224, 224, 3),
            output_shape=(1, 1000),
            model_size_mb=100.0,
            num_parameters=1000000,
            model_format="onnx",
            supported_ops=["Conv", "Relu"],
            unsupported_ops=["UnsupportedOp"]
        )

        result = ptq_converter.validate_model(model_info)

        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
        assert result.compatibility_score < 1.0
        assert len(result.errors) > 0
        assert "Unsupported operators" in str(result.errors)

    def test_validate_model_with_dynamic_dimensions(self, ptq_converter):
        """Test model validation with dynamic dimensions."""
        model_info = ModelInfo(
            model_path="/tmp/model.onnx",
            input_shape=(-1, 224, 224, 3),  # Dynamic batch dimension
            output_shape=(1, 1000),
            model_size_mb=100.0,
            num_parameters=1000000,
            model_format="onnx",
            supported_ops=["Conv", "Relu"],
            unsupported_ops=[]
        )

        result = ptq_converter.validate_model(model_info)

        assert isinstance(result, ValidationResult)
        assert result.is_valid is True  # Dynamic dimensions are warnings, not errors
        assert len(result.warnings) > 0
        assert any("dynamic dimensions" in warning for warning in result.warnings)

    def test_prepare_calibration_data_success(self, ptq_converter, calibration_config):
        """Test successful calibration data preparation."""
        # Mock calibration data directory
        with patch('pathlib.Path.exists', return_value=True):
            result = ptq_converter.prepare_calibration_data(calibration_config)

        assert isinstance(result, calibration_config.__class__)
        assert result.config == calibration_config
        assert result.preprocessing_applied is False
        assert result.statistics is not None
        assert result.validation_results is not None
        assert result.data is not None

    def test_prepare_calibration_data_invalid_config(self, ptq_converter):
        """Test calibration data preparation with invalid config."""
        invalid_config = CalibrationConfig(
            data_path="/nonexistent/data",
            batch_size=-1,  # Invalid
            num_samples=100,
            input_shape=(1, 224, 224, 3)
        )

        with pytest.raises(ValueError, match="batch_size must be positive"):
            ptq_converter.prepare_calibration_data(invalid_config)

    @patch('numpy.random.randn')
    def test_quantize_model_success(self, mock_random, ptq_converter, calibration_config):
        """Test successful model quantization."""
        # Setup mock data
        mock_random.return_value = Mock()
        mock_random.return_value.shape = (100, 224, 224, 3)

        model_info = ModelInfo(
            model_path="/tmp/model.onnx",
            input_shape=(1, 224, 224, 3),
            output_shape=(1, 1000),
            model_size_mb=100.0,
            num_parameters=1000000
        )

        # Create calibration data
        with patch('pathlib.Path.exists', return_value=True):
            calib_data = ptq_converter.prepare_calibration_data(calibration_config)

        result = ptq_converter.quantize_model(model_info, calib_data)

        assert isinstance(result, QuantizedModel)
        assert result.model_info == model_info
        assert result.calibration_info == calib_data
        assert "quantization_config" in result.quantization_statistics
        assert result.quantization_statistics["compression_ratio"] == 4.0

    def test_quantize_model_invalid_calibration_data(self, ptq_converter):
        """Test model quantization with invalid calibration data."""
        model_info = ModelInfo(
            model_path="/tmp/model.onnx",
            input_shape=(1, 224, 224, 3),
            output_shape=(1, 1000),
            model_size_mb=100.0,
            num_parameters=1000000
        )

        # Create invalid calibration data
        invalid_calib_data = Mock()
        invalid_calib_data.validate.return_value = False

        with pytest.raises(ValueError, match="Invalid calibration data"):
            ptq_converter.quantize_model(model_info, invalid_calib_data)

    def test_compile_model_success(self, ptq_converter):
        """Test successful model compilation."""
        quantized_model = Mock()
        quantized_model.model_path = "/tmp/quantized_model.onnx"
        quantized_model.quantization_config = {"method": "min_max"}
        quantized_model.model_info = Mock()
        quantized_model.calibration_info = Mock()

        result = ptq_converter.compile_model(quantized_model)

        assert isinstance(result, CompiledModel)
        assert result.success is True
        assert result.target_device == "horizon_x5"
        assert result.compilation_log is not None
        assert "performance_metrics" in result.__dict__

    def test_analyze_performance_success(self, ptq_converter):
        """Test successful performance analysis."""
        compiled_model = Mock()
        compiled_model.performance_metrics = {
            "expected_inference_time_ms": 15.5,
            "expected_throughput_fps": 64.5,
            "expected_memory_usage_mb": 128.0
        }

        result = ptq_converter.analyze_performance(compiled_model)

        assert isinstance(result, PerformanceResult)
        assert result.inference_time_ms == 15.5
        assert result.throughput_fps == 64.5
        assert result.memory_usage_mb == 128.0
        assert result.benchmark_score == 215.0  # 64.5 / 30.0 * 100
        assert result.meets_performance_target(30.0) is True
        assert "comparison_with_baseline" in result.__dict__

    def test_analyze_performance_below_target(self, ptq_converter):
        """Test performance analysis with below-target performance."""
        compiled_model = Mock()
        compiled_model.performance_metrics = {
            "expected_inference_time_ms": 50.0,
            "expected_throughput_fps": 20.0,  # Below 30 FPS target
            "expected_memory_usage_mb": 128.0
        }

        result = ptq_converter.analyze_performance(compiled_model)

        assert isinstance(result, PerformanceResult)
        assert result.throughput_fps == 20.0
        assert result.meets_performance_target(30.0) is False

    def test_analyze_accuracy_success(self, ptq_converter):
        """Test successful accuracy analysis."""
        compiled_model = Mock()

        result = ptq_converter.analyze_accuracy(compiled_model)

        assert isinstance(result, AccuracyResult)
        assert result.accuracy_before_quantization == 99.5
        assert result.accuracy_after_quantization == 98.8
        assert result.accuracy_drop_percentage == 0.7
        assert result.meets_accuracy_target(98.0) is True
        assert result.is_acceptable_drop(2.0) is True
        assert "per_class_accuracy" in result.__dict__
        assert "metrics" in result.__dict__

    def test_analyze_accuracy_below_target(self, ptq_converter):
        """Test accuracy analysis with below-target accuracy."""
        # This would require modifying the method to accept different values
        # For now, we test the existing implementation
        compiled_model = Mock()

        result = ptq_converter.analyze_accuracy(compiled_model)

        # Test with different targets
        assert result.meets_accuracy_target(99.0) is False  # 98.8 < 99.0
        assert result.is_acceptable_drop(0.5) is False     # 0.7 > 0.5

    def test_generate_report_complete_conversion(self, ptq_converter, calibration_config):
        """Test report generation with complete conversion data."""
        # Setup all required conversion data
        with patch('pathlib.Path.exists', return_value=True):
            with patch('numpy.random.randn'):
                model_info = ModelInfo(
                    model_path="/tmp/model.onnx",
                    input_shape=(1, 224, 224, 3),
                    output_shape=(1, 1000),
                    model_size_mb=100.0,
                    num_parameters=1000000
                )

                ptq_converter.model_info = model_info
                ptq_converter.validation_result = ValidationResult(
                    is_valid=True, errors=[], warnings=[],
                    compatibility_score=1.0, recommendations=[]
                )
                ptq_converter.calibration_data = ptq_converter.prepare_calibration_data(calibration_config)
                ptq_converter.quantized_model = ptq_converter.quantize_model(model_info, ptq_converter.calibration_data)
                ptq_converter.compiled_model = ptq_converter.compile_model(ptq_converter.quantized_model)
                ptq_converter.performance_result = ptq_converter.analyze_performance(ptq_converter.compiled_model)
                ptq_converter.accuracy_result = ptq_converter.analyze_accuracy(ptq_converter.compiled_model)

                report = ptq_converter.generate_report()

                assert isinstance(report, dict)
                assert "conversion_summary" in report
                assert "model_information" in report
                assert "validation_results" in report
                assert "quantization_results" in report
                assert "performance_results" in report
                assert "accuracy_results" in report
                assert "calibration_data_info" in report

                # Check specific values
                assert report["conversion_summary"]["conversion_status"] == "SUCCESS"
                assert report["validation_results"]["is_valid"] is True
                assert report["quantization_results"]["compression_ratio"] == 4.0
                assert report["performance_results"]["throughput_fps"] == 64.5
                assert report["accuracy_results"]["meets_accuracy_target"] is True

    def test_generate_report_incomplete_conversion(self, ptq_converter):
        """Test report generation with incomplete conversion data."""
        # Only set model info, leave others as None
        ptq_converter.model_info = Mock()

        with pytest.raises(ValueError, match="All conversion steps must be completed"):
            ptq_converter.generate_report()

    def test_save_report(self, ptq_converter, temp_output_dir):
        """Test saving report to file."""
        report_path = Path(temp_output_dir) / "test_report.json"

        # Mock the generate_report method
        mock_report = {"test": "data"}
        ptq_converter.generate_report = Mock(return_value=mock_report)

        ptq_converter.save_report(str(report_path))

        assert report_path.exists()
        with open(report_path, 'r') as f:
            saved_report = json.load(f)
        assert saved_report == mock_report

    def test_get_supported_operators(self, ptq_converter):
        """Test getting supported operators list."""
        operators = ptq_converter._get_supported_operators()

        assert isinstance(operators, list)
        assert len(operators) > 0
        assert "Conv" in operators
        assert "Relu" in operators

    def test_apply_preprocessing(self, ptq_converter):
        """Test preprocessing application."""
        import numpy as np

        # Create test data
        data = np.random.randn(10, 224, 224, 3)

        # Test normalization
        config = {
            "normalize": {"mean": 0.5, "std": 0.25},
            "scale": {"factor": 2.0},
            "clip": {"min": -1.0, "max": 1.0}
        }

        result = ptq_converter._apply_preprocessing(data, config)

        assert result.shape == data.shape
        assert np.all(result >= -1.0)  # Check clipping
        assert np.all(result <= 1.0)   # Check clipping

    def test_apply_preprocessing_no_config(self, ptq_converter):
        """Test preprocessing with no configuration."""
        import numpy as np

        data = np.random.randn(10, 224, 224, 3)
        result = ptq_converter._apply_preprocessing(data, {})

        # Should return unchanged data
        assert np.array_equal(result, data)