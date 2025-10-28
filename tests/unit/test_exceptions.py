"""
Unit tests for Exceptions module.

Tests error code system, context handling, and exception chaining
as specified in AC2: 提供详细的错误信息和错误代码
"""

import pytest
import json
from unittest.mock import patch

import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from npu_converter.utils.exceptions import (
    ConverterException,
    ConverterErrorCodes,
    ModelLoadError,
    ModelValidationError,
    ModelConversionError,
    ConfigurationError,
    ToolchainError,
    CompilationError,
    FileFormatError,
    HardwareCompatibilityError,
    ErrorContext,
    create_error_context,
    handle_exception
)


class TestConverterErrorCodes:
    """Test error code definitions."""

    def test_error_codes_exist(self):
        """Test all expected error codes are defined."""
        # General errors
        assert hasattr(ConverterErrorCodes, 'UNKNOWN_ERROR')
        assert hasattr(ConverterErrorCodes, 'INITIALIZATION_ERROR')
        assert hasattr(ConverterErrorCodes, 'CONFIGURATION_ERROR')
        assert hasattr(ConverterErrorCodes, 'VALIDATION_ERROR')

        # File system errors
        assert hasattr(ConverterErrorCodes, 'FILE_NOT_FOUND')
        assert hasattr(ConverterErrorCodes, 'FILE_PERMISSION_ERROR')
        assert hasattr(ConverterErrorCodes, 'FILE_FORMAT_ERROR')
        assert hasattr(ConverterErrorCodes, 'DISK_SPACE_ERROR')

        # Model conversion errors
        assert hasattr(ConverterErrorCodes, 'MODEL_LOAD_ERROR')
        assert hasattr(ConverterErrorCodes, 'MODEL_VALIDATION_ERROR')
        assert hasattr(ConverterErrorCodes, 'MODEL_CONVERSION_ERROR')
        assert hasattr(ConverterErrorCodes, 'OPTIMIZATION_ERROR')

        # Toolchain errors
        assert hasattr(ConverterErrorCodes, 'TOOLCHAIN_ERROR')
        assert hasattr(ConverterErrorCodes, 'COMPILATION_ERROR')
        assert hasattr(ConverterErrorCodes, 'DEPLOYMENT_ERROR')
        assert hasattr(ConverterErrorCodes, 'HARDWARE_COMPATIBILITY_ERROR')

        # Performance errors
        assert hasattr(ConverterErrorCodes, 'MEMORY_ERROR')
        assert hasattr(ConverterErrorCodes, 'TIMEOUT_ERROR')
        assert hasattr(ConverterErrorCodes, 'RESOURCE_LIMIT_ERROR')

    def test_error_code_format(self):
        """Test error codes follow expected format."""
        # Should start with E and be 4 characters
        assert ConverterErrorCodes.UNKNOWN_ERROR == "E0000"
        assert ConverterErrorCodes.FILE_NOT_FOUND == "E1000"
        assert ConverterErrorCodes.MODEL_LOAD_ERROR == "E2000"
        assert ConverterErrorCodes.TOOLCHAIN_ERROR == "E3000"
        assert ConverterErrorCodes.MEMORY_ERROR == "E4000"


class TestConverterException:
    """Test base ConverterException class."""

    def test_basic_initialization(self):
        """Test basic exception initialization."""
        exc = ConverterException("Test message", ConverterErrorCodes.FILE_NOT_FOUND)

        assert str(exc) == "Test message"
        assert exc.message == "Test message"
        assert exc.error_code == "E1000"
        assert exc.context == {}

    def test_initialization_with_context(self):
        """Test exception initialization with context."""
        context = {"file_path": "/test/path", "operation": "load"}
        exc = ConverterException(
            "Test message",
            ConverterErrorCodes.MODEL_LOAD_ERROR,
            context
        )

        assert exc.error_code == "E2000"
        assert exc.context == context

    def test_to_dict_method(self):
        """Test to_dict method serialization."""
        context = {"user_id": "123", "operation": "convert"}
        exc = ConverterException(
            "Test error",
            ConverterErrorCodes.CONFIGURATION_ERROR,
            context
        )

        result = exc.to_dict()

        assert result["error_type"] == "ConverterException"
        assert result["message"] == "Test error"
        assert result["error_code"] == "E0002"
        assert result["context"] == context

    def test_with_context_method(self):
        """Test adding context to exception."""
        exc = ConverterException(
            "Test message",
            ConverterErrorCodes.UNKNOWN_ERROR,
            {"initial_context": "value"}
        )

        exc.with_context(additional_context="new_value")

        assert exc.context == {
            "initial_context": "value",
            "additional_context": "new_value"
        }

    def test_capture_stack_trace(self):
        """Test stack trace capture."""
        exc = ConverterException("Test error")

        # Before capture
        assert exc.stack_trace is None

        # Capture stack trace
        exc.capture_stack_trace()

        # After capture
        assert exc.stack_trace is not None
        assert "ConverterException" in exc.stack_trace
        assert "Test error" in exc.stack_trace


class TestSpecificExceptionTypes:
    """Test specific exception types."""

    def test_model_load_error(self):
        """Test ModelLoadError includes model path."""
        exc = ModelLoadError("Failed to load model", "/path/to/model.onnx", user_id="123")

        assert exc.error_code == ConverterErrorCodes.MODEL_LOAD_ERROR
        assert exc.context["model_path"] == "/path/to/model.onnx"
        assert exc.context["user_id"] == "123"

    def test_model_validation_error(self):
        """Test ModelValidationError includes validation errors."""
        errors = ["Invalid operator", "Wrong tensor shape"]
        exc = ModelValidationError("Validation failed", errors, model_type="sensevoice")

        assert exc.error_code == ConverterErrorCodes.MODEL_VALIDATION_ERROR
        assert exc.context["validation_errors"] == errors
        assert exc.context["model_type"] == "sensevoice"

    def test_model_conversion_error(self):
        """Test ModelConversionError includes conversion stage."""
        exc = ModelConversionError("Conversion failed", stage="optimization", batch_size=32)

        assert exc.error_code == ConverterErrorCodes.MODEL_CONVERSION_ERROR
        assert exc.context["conversion_stage"] == "optimization"
        assert exc.context["batch_size"] == 32

    def test_configuration_error(self):
        """Test ConfigurationError includes config key."""
        exc = ConfigurationError("Invalid config", config_key="learning_rate", config_value=0.001)

        assert exc.error_code == ConverterErrorCodes.CONFIGURATION_ERROR
        assert exc.context["config_key"] == "learning_rate"
        assert exc.context["config_value"] == 0.001

    def test_toolchain_error(self):
        """Test ToolchainError includes toolchain version."""
        exc = ToolchainError("Toolchain error", toolchain_version="2.1.0", hardware="rdk_x5")

        assert exc.error_code == ConverterErrorCodes.TOOLCHAIN_ERROR
        assert exc.context["toolchain_version"] == "2.1.0"
        assert exc.context["hardware"] == "rdk_x5"

    def test_compilation_error(self):
        """Test CompilationError includes compilation stage."""
        exc = CompilationError("Compilation failed", compilation_stage="code_generation", optimization_level=3)

        assert exc.error_code == ConverterErrorCodes.COMPILATION_ERROR
        assert exc.context["compilation_stage"] == "code_generation"
        assert exc.context["optimization_level"] == 3

    def test_file_format_error(self):
        """Test FileFormatError includes file type."""
        exc = FileFormatError("Invalid format", file_type="ONNX", expected_version="1.4")

        assert exc.error_code == ConverterErrorCodes.FILE_FORMAT_ERROR
        assert exc.context["file_type"] == "ONNX"
        assert exc.context["expected_version"] == "1.4"

    def test_hardware_compatibility_error(self):
        """Test HardwareCompatibilityError includes hardware info."""
        hardware_info = {"device": "NPU", "memory": "4GB", "version": "1.0"}
        exc = HardwareCompatibilityError("Not compatible", hardware_info, model_size="2GB")

        assert exc.error_code == ConverterErrorCodes.HARDWARE_COMPATIBILITY_ERROR
        assert exc.context["hardware_info"] == hardware_info
        assert exc.context["model_size"] == "2GB"


class TestErrorContext:
    """Test ErrorContext dataclass."""

    def test_error_context_creation(self):
        """Test ErrorContext creation."""
        context = ErrorContext(
            component="model_loader",
            operation="load_onnx",
            file_path="/test/model.onnx",
            line_number=42
        )

        assert context.component == "model_loader"
        assert context.operation == "load_onnx"
        assert context.file_path == "/test/model.onnx"
        assert context.line_number == 42
        assert context.additional_data is None

    def test_error_context_with_additional_data(self):
        """Test ErrorContext with additional data."""
        additional_data = {"user_id": "123", "timestamp": "2023-01-01"}
        context = ErrorContext(
            component="converter",
            additional_data=additional_data
        )

        assert context.additional_data == additional_data

    def test_create_error_context_function(self):
        """Test create_error_context function."""
        context = create_error_context(
            component="validator",
            operation="check_model",
            file_path="/test/model.onnx",
            line_number=100,
            severity="high"
        )

        assert isinstance(context, ErrorContext)
        assert context.component == "validator"
        assert context.operation == "check_model"
        assert context.additional_data["severity"] == "high"


class TestHandleException:
    """Test handle_exception function."""

    def test_handle_converter_exception(self):
        """Test handling ConverterException."""
        original_exc = ConverterException(
            "Original error",
            ConverterErrorCodes.MODEL_LOAD_ERROR,
            {"file_path": "/test/model.onnx"}
        )

        result = handle_exception(original_exc)

        assert result is original_exc  # Should return the same exception
        assert result.error_code == "E2000"
        assert result.context["file_path"] == "/test/model.onnx"

    def test_handle_regular_exception(self):
        """Test handling regular Python exception."""
        try:
            raise ValueError("Python exception")
        except ValueError as e:
            result = handle_exception(e, "E1000", {"operation": "test"})

            assert isinstance(result, ConverterException)
            assert result.error_code == "E1000"
            assert result.message == "Python exception"
            assert result.context["original_type"] == "ValueError"
            assert result.context["operation"] == "test"
            assert result.stack_trace is not None

    def test_handle_exception_with_default_code(self):
        """Test handling exception with default error code."""
        try:
            raise RuntimeError("Runtime error")
        except RuntimeError as e:
            result = handle_exception(e)

            assert result.error_code == ConverterErrorCodes.UNKNOWN_ERROR
            assert result.context["original_type"] == "RuntimeError"

    def test_handle_exception_adds_context(self):
        """Test that additional context is added to ConverterException."""
        original_exc = ConverterException(
            "Original error",
            ConverterErrorCodes.CONFIGURATION_ERROR,
            {"config_key": "learning_rate"}
        )

        additional_context = {"user_id": "123", "operation": "config_validate"}
        result = handle_exception(original_exc, context=additional_context)

        assert result.context["config_key"] == "learning_rate"
        assert result.context["user_id"] == "123"
        assert result.context["operation"] == "config_validate"


class TestExceptionSerialization:
    """Test exception serialization and deserialization."""

    def test_json_serialization(self):
        """Test JSON serialization of exception data."""
        exc = ModelValidationError(
            "Invalid model",
            ["Wrong shape", "Unsupported op"],
            model_type="sensevoice",
            user_id="123"
        )

        # Convert to dictionary and then to JSON
        exc_dict = exc.to_dict()
        json_str = json.dumps(exc_dict, ensure_ascii=False)
        restored_dict = json.loads(json_str)

        # Verify all fields are preserved
        assert restored_dict["error_type"] == "ModelValidationError"
        assert restored_dict["message"] == "Invalid model"
        assert restored_dict["error_code"] == "E2001"
        assert restored_dict["context"]["validation_errors"] == ["Wrong shape", "Unsupported op"]
        assert restored_dict["context"]["model_type"] == "sensevoice"
        assert restored_dict["context"]["user_id"] == "123"

    def test_exception_inheritance_chain(self):
        """Test that specific exceptions inherit from ConverterException."""
        exc = ModelLoadError("Test error")
        assert isinstance(exc, ConverterException)
        assert isinstance(exc, Exception)

        exc2 = ConfigurationError("Config error")
        assert isinstance(exc2, ConverterException)
        assert isinstance(exc2, Exception)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])