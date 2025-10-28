"""
扩展异常处理单元测试 - Story 1.8 Subtask 1.4

测试异常处理系统的异常抛出、错误链和上下文捕获功能。
补充现有的test_exceptions.py，提供更全面的异常测试覆盖。
遵循pytest 7.x框架和AAA测试模式。
"""

import pytest
import traceback
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys
import os

# 添加项目路径到sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from npu_converter.utils.exceptions import (
        ConverterErrorCodes, ErrorContext, ConverterException,
        ModelLoadError, ModelValidationError, ModelConversionError,
        ConfigurationError, ToolchainError, CompilationError,
        FileFormatError, HardwareCompatibilityError
    )
except ImportError as e:
    pytest.skip(f"无法导入异常模块: {e}", allow_module_level=True)


class TestConverterErrorCodes:
    """ConverterErrorCodes测试类"""

    def test_error_codes_constants(self):
        """测试错误代码常量定义"""
        # 通用错误
        assert hasattr(ConverterErrorCodes, 'UNKNOWN_ERROR')
        assert hasattr(ConverterErrorCodes, 'INITIALIZATION_ERROR')
        assert hasattr(ConverterErrorCodes, 'CONFIGURATION_ERROR')
        assert hasattr(ConverterErrorCodes, 'VALIDATION_ERROR')

        # 文件系统错误
        assert hasattr(ConverterErrorCodes, 'FILE_NOT_FOUND')
        assert hasattr(ConverterErrorCodes, 'FILE_PERMISSION_ERROR')
        assert hasattr(ConverterErrorCodes, 'FILE_FORMAT_ERROR')
        assert hasattr(ConverterErrorCodes, 'DISK_SPACE_ERROR')

        # 模型转换错误
        assert hasattr(ConverterErrorCodes, 'MODEL_LOAD_ERROR')
        assert hasattr(ConverterErrorCodes, 'MODEL_VALIDATION_ERROR')
        assert hasattr(ConverterErrorCodes, 'MODEL_CONVERSION_ERROR')
        assert hasattr(ConverterErrorCodes, 'OPTIMIZATION_ERROR')

        # NPU/BPU工具链错误
        assert hasattr(ConverterErrorCodes, 'TOOLCHAIN_ERROR')
        assert hasattr(ConverterErrorCodes, 'COMPILATION_ERROR')
        assert hasattr(ConverterErrorCodes, 'DEPLOYMENT_ERROR')
        assert hasattr(ConverterErrorCodes, 'HARDWARE_COMPATIBILITY_ERROR')

        # 性能错误
        assert hasattr(ConverterErrorCodes, 'MEMORY_ERROR')
        assert hasattr(ConverterErrorCodes, 'TIMEOUT_ERROR')
        assert hasattr(ConverterErrorCodes, 'RESOURCE_LIMIT_ERROR')

    def test_error_codes_values(self):
        """测试错误代码值格式"""
        # 验证错误代码格式为Exxxx
        error_codes = [
            ConverterErrorCodes.UNKNOWN_ERROR,
            ConverterErrorCodes.INITIALIZATION_ERROR,
            ConverterErrorCodes.CONFIGURATION_ERROR,
            ConverterErrorCodes.VALIDATION_ERROR,
            ConverterErrorCodes.FILE_NOT_FOUND,
            ConverterErrorCodes.FILE_PERMISSION_ERROR,
            ConverterErrorCodes.FILE_FORMAT_ERROR,
            ConverterErrorCodes.DISK_SPACE_ERROR,
            ConverterErrorCodes.MODEL_LOAD_ERROR,
            ConverterErrorCodes.MODEL_VALIDATION_ERROR,
            ConverterErrorCodes.MODEL_CONVERSION_ERROR,
            ConverterErrorCodes.OPTIMIZATION_ERROR,
            ConverterErrorCodes.TOOLCHAIN_ERROR,
            ConverterErrorCodes.COMPILATION_ERROR,
            ConverterErrorCodes.DEPLOYMENT_ERROR,
            ConverterErrorCodes.HARDWARE_COMPATIBILITY_ERROR,
            ConverterErrorCodes.MEMORY_ERROR,
            ConverterErrorCodes.TIMEOUT_ERROR,
            ConverterErrorCodes.RESOURCE_LIMIT_ERROR
        ]

        for code in error_codes:
            assert isinstance(code, str)
            assert code.startswith('E')
            assert len(code) == 5
            assert code[1:].isdigit()


class TestErrorContext:
    """ErrorContext测试类"""

    def test_error_context_initialization(self):
        """测试ErrorContext初始化"""
        context = ErrorContext(component="test_component")

        assert context.component == "test_component"
        assert context.operation is None
        assert context.file_path is None
        assert context.line_number is None
        assert context.additional_data is None

    def test_error_context_with_all_fields(self):
        """测试ErrorContext包含所有字段"""
        context = ErrorContext(
            component="test_component",
            operation="test_operation",
            file_path="/path/to/file.py",
            line_number=42,
            additional_data={"key": "value"}
        )

        assert context.component == "test_component"
        assert context.operation == "test_operation"
        assert context.file_path == "/path/to/file.py"
        assert context.line_number == 42
        assert context.additional_data == {"key": "value"}

    def test_error_context_to_dict(self):
        """测试ErrorContext转换为字典"""
        context = ErrorContext(
            component="test_component",
            operation="test_operation",
            file_path="/path/to/file.py",
            line_number=42
        )

        context_dict = context.to_dict()
        assert context_dict["component"] == "test_component"
        assert context_dict["operation"] == "test_operation"
        assert context_dict["file_path"] == "/path/to/file.py"
        assert context_dict["line_number"] == 42

    def test_error_context_str_representation(self):
        """测试ErrorContext字符串表示"""
        context = ErrorContext(
            component="test_component",
            operation="test_operation"
        )

        str_repr = str(context)
        assert "test_component" in str_repr
        assert "test_operation" in str_repr


class TestConverterException:
    """ConverterException基础异常类测试"""

    def test_base_exception_initialization(self):
        """测试基础异常初始化"""
        error = ConverterException(
            message="Test error message",
            error_code=ConverterErrorCodes.UNKNOWN_ERROR
        )

        assert error.message == "Test error message"
        assert error.error_code == ConverterErrorCodes.UNKNOWN_ERROR
        assert error.context == {}

    def test_base_exception_with_context(self):
        """测试带上下文的基础异常"""
        test_context = {"component": "test_component"}
        error = ConverterException(
            message="Test error message",
            error_code=ConverterErrorCodes.CONFIGURATION_ERROR,
            context=test_context
        )

        assert error.context == test_context

    def test_base_exception_str_representation(self):
        """测试基础异常字符串表示"""
        error = ConverterException(
            message="Test error message",
            error_code=ConverterErrorCodes.UNKNOWN_ERROR
        )

        error_str = str(error)
        assert "Test error message" in error_str

    def test_base_exception_with_context_str(self):
        """测试带上下文的基础异常字符串表示"""
        test_context = {"component": "test_component", "operation": "test_operation"}
        error = ConverterException(
            message="Test error message",
            error_code=ConverterErrorCodes.CONFIGURATION_ERROR,
            context=test_context
        )

        error_str = str(error)
        assert "Test error message" in error_str

    def test_base_exception_to_dict(self):
        """测试基础异常转换为字典"""
        test_context = {"component": "test_component"}
        error = ConverterException(
            message="Test error message",
            error_code=ConverterErrorCodes.MODEL_LOAD_ERROR,
            context=test_context
        )

        error_dict = error.to_dict()
        assert error_dict["message"] == "Test error message"
        assert error_dict["error_code"] == ConverterErrorCodes.MODEL_LOAD_ERROR
        assert error_dict["context"]["component"] == "test_component"

    def test_base_exception_with_traceback(self):
        """测试带追踪信息的基础异常"""
        try:
            raise ConverterException(
                message="Test error with traceback",
                error_code=ConverterErrorCodes.VALIDATION_ERROR
            )
        except ConverterException as e:
            assert hasattr(e, '__traceback__')
            assert e.__traceback__ is not None

    def test_with_context_method(self):
        """测试with_context方法"""
        error = ConverterException(
            message="Test error",
            error_code=ConverterErrorCodes.CONFIGURATION_ERROR,
            context={"initial": "value"}
        )

        error.with_context(additional="data")
        assert error.context["initial"] == "value"
        assert error.context["additional"] == "data"

    def test_capture_stack_trace(self):
        """测试capture_stack_trace方法"""
        error = ConverterException(
            message="Test error",
            error_code=ConverterErrorCodes.UNKNOWN_ERROR
        )

        error.capture_stack_trace()
        assert error.stack_trace is not None
        assert isinstance(error.stack_trace, str)


class TestModelLoadError:
    """ModelLoadError测试类"""

    def test_model_load_error(self):
        """测试模型加载错误"""
        error = ModelLoadError(
            message="Failed to load model",
            model_path="/path/to/model.onnx"
        )

        assert error.message == "Failed to load model"
        assert error.error_code == ConverterErrorCodes.MODEL_LOAD_ERROR
        assert error.context["model_path"] == "/path/to/model.onnx"

    def test_model_load_error_str(self):
        """测试模型加载错误字符串表示"""
        error = ModelLoadError(
            message="Model file not found",
            model_path="/missing/model.onnx"
        )

        error_str = str(error)
        assert "Model file not found" in error_str


class TestModelValidationError:
    """ModelValidationError测试类"""

    def test_model_validation_error(self):
        """测试模型验证错误"""
        error = ModelValidationError(
            message="Model validation failed",
            validation_errors=["Invalid architecture", "Missing input shape"]
        )

        assert error.message == "Model validation failed"
        assert error.error_code == ConverterErrorCodes.MODEL_VALIDATION_ERROR
        assert error.context["validation_errors"] == ["Invalid architecture", "Missing input shape"]

    def test_model_validation_error_str(self):
        """测试模型验证错误字符串表示"""
        error = ModelValidationError(
            message="Validation errors found",
            validation_errors=["Error 1", "Error 2"]
        )

        error_str = str(error)
        assert "Validation errors found" in error_str


class TestConfigurationError:
    """ConfigurationError测试类"""

    def test_configuration_error(self):
        """测试配置错误"""
        error = ConfigurationError(
            message="Invalid configuration",
            config_key="optimization.level"
        )

        assert error.message == "Invalid configuration"
        assert error.error_code == ConverterErrorCodes.CONFIGURATION_ERROR
        assert error.context["config_key"] == "optimization.level"

    def test_configuration_error_str(self):
        """测试配置错误字符串表示"""
        error = ConfigurationError(
            message="Configuration validation failed",
            config_key="model.type"
        )

        error_str = str(error)
        assert "Configuration validation failed" in error_str


class TestToolchainError:
    """ToolchainError测试类"""

    def test_toolchain_error(self):
        """测试工具链错误"""
        error = ToolchainError(
            message="Toolchain execution failed",
            toolchain_version="1.2.3"
        )

        assert error.message == "Toolchain execution failed"
        assert error.error_code == ConverterErrorCodes.TOOLCHAIN_ERROR
        assert error.context["toolchain_version"] == "1.2.3"

    def test_toolchain_error_str(self):
        """测试工具链错误字符串表示"""
        error = ToolchainError(
            message="Toolchain command failed",
            toolchain_version="2.0.0"
        )

        error_str = str(error)
        assert "Toolchain command failed" in error_str


class TestCompilationError:
    """CompilationError测试类"""

    def test_compilation_error(self):
        """测试编译错误"""
        error = CompilationError(
            message="Model compilation failed",
            compilation_stage="optimization"
        )

        assert error.message == "Model compilation failed"
        assert error.error_code == ConverterErrorCodes.COMPILATION_ERROR
        assert error.context["compilation_stage"] == "optimization"

    def test_compilation_error_str(self):
        """测试编译错误字符串表示"""
        error = CompilationError(
            message="Compilation stage failed",
            compilation_stage="quantization"
        )

        error_str = str(error)
        assert "Compilation stage failed" in error_str


class TestFileFormatError:
    """FileFormatError测试类"""

    def test_file_format_error(self):
        """测试文件格式错误"""
        error = FileFormatError(
            message="Unsupported file format",
            file_type="model_file"
        )

        assert error.message == "Unsupported file format"
        assert error.error_code == ConverterErrorCodes.FILE_FORMAT_ERROR
        assert error.context["file_type"] == "model_file"

    def test_file_format_error_str(self):
        """测试文件格式错误字符串表示"""
        error = FileFormatError(
            message="Invalid file format",
            file_type="onnx"
        )

        error_str = str(error)
        assert "Invalid file format" in error_str


class TestHardwareCompatibilityError:
    """HardwareCompatibilityError测试类"""

    def test_hardware_compatibility_error(self):
        """测试硬件兼容性错误"""
        hardware_info = {"device": "unsupported_device", "version": "1.0"}
        error = HardwareCompatibilityError(
            message="Hardware not compatible",
            hardware_info=hardware_info
        )

        assert error.message == "Hardware not compatible"
        assert error.error_code == ConverterErrorCodes.HARDWARE_COMPATIBILITY_ERROR
        assert error.context["hardware_info"] == hardware_info

    def test_hardware_compatibility_error_str(self):
        """测试硬件兼容性错误字符串表示"""
        hardware_info = {"device": "test_device"}
        error = HardwareCompatibilityError(
            message="Hardware compatibility issue",
            hardware_info=hardware_info
        )

        error_str = str(error)
        assert "Hardware compatibility issue" in error_str


class TestExceptionChaining:
    """异常链测试类"""

    def test_exception_chaining(self):
        """测试异常链"""
        # 创建原始异常
        original_error = ValueError("Original error message")

        # 创建包装异常
        wrapped_error = ConverterException(
            message="Wrapped error",
            error_code=ConverterErrorCodes.MODEL_CONVERSION_ERROR
        )
        # Python异常链通过 raise from 设置
        try:
            raise original_error
        except Exception:
            raise wrapped_error from original_error

        # 验证异常链
        assert wrapped_error.__cause__ == original_error
        assert isinstance(wrapped_error.__cause__, ValueError)

    def test_exception_chain_with_context(self):
        """测试带上下文的异常链"""
        original_error = ConfigurationError("Original config error", "config_key")

        wrapped_error = ConverterException(
            message="Higher level error",
            error_code=ConverterErrorCodes.CONFIGURATION_ERROR,
            context={"component": "test_component"}
        )

        try:
            raise original_error
        except Exception:
            raise wrapped_error from original_error

        assert wrapped_error.context["component"] == "test_component"
        assert wrapped_error.__cause__ == original_error
        assert isinstance(wrapped_error.__cause__, ConfigurationError)

    def test_exception_chain_traceback(self):
        """测试异常链追踪信息"""
        try:
            try:
                raise ValueError("Root cause")
            except ValueError as e:
                raise ConverterException(
                    message="Wrapped error",
                    error_code=ConverterErrorCodes.MODEL_LOAD_ERROR
                ) from e
        except ConverterException as e:
            # 获取完整的异常链
            tb_list = traceback.format_exception(type(e), e, e.__traceback__)
            tb_text = ''.join(tb_list)

            assert "Wrapped error" in tb_text
            assert "Root cause" in tb_text
            assert "ConverterException" in tb_text
            assert "ValueError" in tb_text


class TestExceptionHandlingPatterns:
    """异常处理模式测试类"""

    def test_raise_and_catch_specific_exception(self):
        """测试抛出和捕获特定异常"""
        with pytest.raises(ConfigurationError) as exc_info:
            raise ConfigurationError(
                message="Test config error",
                config_key="test_key"
            )

        error = exc_info.value
        assert error.message == "Test config error"
        assert error.context["config_key"] == "test_key"
        assert error.error_code == ConverterErrorCodes.CONFIGURATION_ERROR

    def test_catch_base_exception_with_isinstance(self):
        """测试使用isinstance捕获基础异常"""
        specific_error = ModelLoadError(
            message="Model load failed",
            model_path="/test/model.onnx"
        )

        with pytest.raises(ConverterException) as exc_info:
            raise specific_error

        error = exc_info.value
        assert isinstance(error, ConverterException)
        assert isinstance(error, ModelLoadError)
        assert error.context["model_path"] == "/test/model.onnx"

    def test_exception_handling_with_finally(self):
        """测试异常处理的finally块"""
        cleanup_called = False

        try:
            raise ToolchainError(
                message="Toolchain failed",
                toolchain_version="1.0"
            )
        except ConverterException:
            pass
        finally:
            cleanup_called = True

        assert cleanup_called is True

    def test_exception_handling_with_else(self):
        """测试异常处理的else块"""
        result = None

        try:
            # 不抛出异常
            result = "success"
        except ConverterException:
            result = "error"
        else:
            result = "no_exception"

        assert result == "no_exception"