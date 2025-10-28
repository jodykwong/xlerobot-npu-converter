"""
Unit tests for CompatibilityChecker
"""

import pytest
from unittest.mock import MagicMock, Mock

from npu_converter.validation.compatibility import (
    CompatibilityChecker,
    CompatibilityResult,
    FullCompatibilityResult,
    CompatibilityLevel
)
from npu_converter.models.onnx_model import ONNXModel, ModelMetadata, VersionInfo


class TestCompatibilityChecker:
    """Test cases for CompatibilityChecker."""

    @pytest.fixture
    def checker(self):
        """Create a test compatibility checker."""
        return CompatibilityChecker()

    @pytest.fixture
    def mock_model(self):
        """Create a mock ONNX model for testing."""
        model = MagicMock(spec=ONNXModel)
        model.metadata = MagicMock(spec=ModelMetadata)
        model.version_info = MagicMock(spec=VersionInfo)
        model.input_tensors = []
        model.output_tensors = []
        model.operators = []
        model.operator_count = 0
        return model

    def test_init(self, checker):
        """Test checker initialization."""
        assert isinstance(checker, CompatibilityChecker)
        assert len(checker.supported_operators) > 0
        assert len(checker.supported_data_types) > 0

    def test_check_operator_support_supported_ops(self, checker, mock_model):
        """Test operator support check with supported operators."""
        # Add supported operators
        mock_model.operators = [
            MagicMock(op_type="Conv"),
            MagicMock(op_type="Relu"),
            MagicMock(op_type="Add")
        ]
        mock_model.operator_count = 3

        result = checker.check_operator_support(mock_model)

        assert result.is_compatible is True
        assert result.level == CompatibilityLevel.FULL
        assert len(result.issues) == 0

    def test_check_operator_support_unsupported_ops(self, checker, mock_model):
        """Test operator support check with unsupported operators."""
        # Add unsupported operators
        mock_model.operators = [
            MagicMock(op_type="CustomOp"),
            MagicMock(op_type="UnsupportedOp")
        ]
        mock_model.operator_count = 2

        result = checker.check_operator_support(mock_model)

        assert result.is_compatible is False
        assert result.level == CompatibilityLevel.PARTIAL
        assert len(result.issues) > 0
        assert "Unsupported operator" in result.issues[0]

    def test_check_version_compatibility(self, checker, mock_model):
        """Test version compatibility check."""
        # Set compatible version
        mock_model.version_info.opset_version = 13
        mock_model.version_info.opset_versions = {"ai.onnx": 13}

        result = checker.check_version_compatibility(mock_model)

        assert result.is_compatible is True
        assert result.level == CompatibilityLevel.FULL
        assert len(result.issues) == 0

    def test_check_version_compatibility_old_version(self, checker, mock_model):
        """Test version compatibility check with old version."""
        # Set old version
        mock_model.version_info.opset_version = 5
        mock_model.version_info.opset_versions = {"ai.onnx": 5}

        result = checker.check_version_compatibility(mock_model)

        assert result.is_compatible is False
        assert len(result.issues) > 0

    def test_check_shape_compatibility(self, checker, mock_model):
        """Test shape compatibility check."""
        # Add tensors with valid shapes
        mock_model.input_tensors = [
            MagicMock(shape=[1, 3, 224, 224], name="input1"),
            MagicMock(shape=[-1, 3, 224, 224], name="input2")  # Dynamic shape
        ]
        mock_model.output_tensors = [
            MagicMock(shape=[1, 1000], name="output1")
        ]

        result = checker.check_shape_compatibility(mock_model)

        # Should have warnings for dynamic shapes
        assert len(result.warnings) > 0
        assert "Dynamic shapes detected" in result.warnings[0]

    def test_check_shape_compatibility_invalid_shapes(self, checker, mock_model):
        """Test shape compatibility check with invalid shapes."""
        # Add tensor with invalid shape
        mock_model.input_tensors = [
            MagicMock(shape=[1, 0, 224, 224], name="input1")  # Zero dimension
        ]
        mock_model.output_tensors = []

        result = checker.check_shape_compatibility(mock_model)

        assert len(result.issues) > 0
        assert "Invalid shapes detected" in result.issues[0]

    def test_check_precision_support(self, checker, mock_model):
        """Test precision support check."""
        # Add tensors with supported types
        mock_model.input_tensors = [
            MagicMock(dtype="FLOAT", name="input1"),
            MagicMock(dtype="INT32", name="input2")
        ]
        mock_model.output_tensors = [
            MagicMock(dtype="FLOAT", name="output1")
        ]

        result = checker.check_precision_support(mock_model)

        assert result.is_compatible is True
        assert len(result.issues) == 0

    def test_check_precision_support_unsupported(self, checker, mock_model):
        """Test precision support check with unsupported types."""
        # Add tensor with unsupported type
        mock_model.input_tensors = [
            MagicMock(dtype="STRING", name="input1")
        ]
        mock_model.output_tensors = []

        result = checker.check_precision_support(mock_model)

        assert result.is_compatible is False
        assert len(result.issues) > 0

    def test_check_precision_support_complex(self, checker, mock_model):
        """Test precision support check with complex types."""
        # Add tensor with complex type
        mock_model.input_tensors = [
            MagicMock(dtype="COMPLEX64", name="input1")
        ]
        mock_model.output_tensors = []

        result = checker.check_precision_support(mock_model)

        assert len(result.issues) > 0
        assert "Complex" in result.issues[0]

    def test_full_compatibility_check(self, checker, mock_model):
        """Test full compatibility check."""
        # Configure mock model for full compatibility
        mock_model.operators = [MagicMock(op_type="Conv")]
        mock_model.operator_count = 1
        mock_model.version_info.opset_version = 13
        mock_model.version_info.opset_versions = {"ai.onnx": 13}
        mock_model.input_tensors = [MagicMock(shape=[1, 3, 224, 224], dtype="FLOAT")]
        mock_model.output_tensors = [MagicMock(shape=[1, 1000], dtype="FLOAT")]

        result = checker.full_compatibility_check(mock_model)

        assert isinstance(result, FullCompatibilityResult)
        assert hasattr(result, "operator_check")
        assert hasattr(result, "version_check")
        assert hasattr(result, "shape_check")
        assert hasattr(result, "precision_check")
        assert hasattr(result, "overall")

    def test_get_compatibility_summary(self, checker):
        """Test getting compatibility summary."""
        # Create a mock result
        mock_result = MagicMock(spec=FullCompatibilityResult)
        mock_result.is_fully_compatible = True
        mock_result.overall.level.value = "full"
        mock_result.all_issues = ["issue1", "issue2"]
        mock_result.all_warnings = ["warning1"]
        mock_result.operator_check.is_compatible = True
        mock_result.operator_check.level.value = "full"
        mock_result.operator_check.issues = []
        mock_result.operator_check.warnings = []
        mock_result.version_check.is_compatible = True
        mock_result.version_check.level.value = "full"
        mock_result.version_check.issues = []
        mock_result.version_check.warnings = []
        mock_result.shape_check.is_compatible = True
        mock_result.shape_check.level.value = "full"
        mock_result.shape_check.issues = []
        mock_result.shape_check.warnings = []
        mock_result.precision_check.is_compatible = True
        mock_result.precision_check.level.value = "full"
        mock_result.precision_check.issues = []
        mock_result.precision_check.warnings = []

        summary = checker.get_compatibility_summary(mock_result)

        assert summary["overall_compatible"] is True
        assert summary["overall_level"] == "full"
        assert summary["total_issues"] == 2
        assert summary["total_warnings"] == 1
        assert "checks" in summary
