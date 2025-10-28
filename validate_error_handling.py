#!/usr/bin/env python3
"""
Error Handling System Validation Script

Validates that all components of the error handling system work correctly.
Tests AC1-AC5 implementation.
"""

import sys
import os
import tempfile
import shutil
import json
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_logger_implementation():
    """Test AC1: 实现分级日志记录（DEBUG, INFO, WARN, ERROR）"""
    print("🧪 Testing AC1: 分级日志记录...")

    from npu_converter.utils.logger import StructuredLogger, get_logger

    # Test logger initialization
    logger = StructuredLogger("test_validation", "DEBUG")
    assert logger.name == "test_validation"
    print("  ✅ Logger initialization successful")

    # Test all four log levels
    with tempfile.TemporaryDirectory() as temp_dir:
        # Change to temp directory and create logs subdir
        original_cwd = os.getcwd()
        temp_log_dir = Path(temp_dir) / "logs"
        temp_log_dir.mkdir(exist_ok=True)

        os.chdir(temp_dir)

        try:
            # Create a new logger instance in the temp directory
            from npu_converter.utils.logger import StructuredLogger
            temp_logger = StructuredLogger("test_validation", "DEBUG")

            temp_logger.debug("Debug message", component="test", user_id="123")
            temp_logger.info("Info message", component="test", user_id="123")
            temp_logger.warning("Warning message", component="test", user_id="123")
            temp_logger.error("Error message", component="test", user_id="123")

            # Verify log file was created and contains all levels
            log_file = Path(temp_dir) / "logs" / "test_validation.log"
            assert log_file.exists(), "Log file not created"

            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
                assert "Debug message" in log_content
                assert "Info message" in log_content
                assert "Warning message" in log_content
                assert "Error message" in log_content
                assert '"level": "DEBUG"' in log_content
                assert '"level": "INFO"' in log_content
                assert '"level": "WARNING"' in log_content
                assert '"level": "ERROR"' in log_content

            print("  ✅ All four log levels working correctly")

            # Test structured logging with context
            temp_logger.info("Context test",
                            operation="validation",
                            model_type="sensevoice",
                            batch_size=32)

            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Find JSON log entry
                lines = [line.strip() for line in content.split('\n') if line.strip().startswith('{')]
                context_found = False
                for line in lines:
                    try:
                        log_entry = json.loads(line)
                        if log_entry.get('message') == 'Context test':
                            assert 'operation' in log_entry['context']
                            assert log_entry['context']['operation'] == 'validation'
                            assert log_entry['context']['model_type'] == 'sensevoice'
                            assert log_entry['context']['batch_size'] == 32
                            context_found = True
                            break
                    except json.JSONDecodeError:
                        continue

                assert context_found, "Structured context logging failed"
                print("  ✅ Structured logging with context working correctly")

        finally:
            os.chdir(original_cwd)

    # Test global logger
    global_logger = get_logger("global_test")
    assert global_logger.name == "global_test"
    print("  ✅ Global logger working correctly")


def test_exception_system():
    """Test AC2: 提供详细的错误信息和错误代码"""
    print("\n🧪 Testing AC2: 错误信息和错误代码...")

    from npu_converter.utils.exceptions import (
        ConverterException, ConverterErrorCodes,
        ModelLoadError, ModelValidationError,
        ConfigurationError, ToolchainError
    )

    # Test error codes exist
    assert ConverterErrorCodes.FILE_NOT_FOUND == "E1000"
    assert ConverterErrorCodes.MODEL_LOAD_ERROR == "E2000"
    assert ConverterErrorCodes.CONFIGURATION_ERROR == "E0002"
    assert ConverterErrorCodes.TOOLCHAIN_ERROR == "E3000"
    print("  ✅ Error codes defined correctly")

    # Test basic exception
    exc = ConverterException("Test error", ConverterErrorCodes.FILE_NOT_FOUND)
    assert str(exc) == "Test error"
    assert exc.error_code == "E1000"
    assert exc.context == {}
    print("  ✅ Basic exception working correctly")

    # Test exception with context
    context = {"file_path": "/test/model.onnx", "user_id": "123"}
    exc = ConverterException("Test with context", ConverterErrorCodes.UNKNOWN_ERROR, context)
    assert exc.context == context
    print("  ✅ Exception with context working correctly")

    # Test specific exception types
    model_exc = ModelLoadError("Model failed", model_path="/test/model.onnx")
    assert model_exc.error_code == "E2000"
    assert model_exc.context["model_path"] == "/test/model.onnx"
    print("  ✅ ModelLoadError working correctly")

    config_exc = ConfigurationError("Config invalid", config_key="learning_rate")
    assert config_exc.error_code == "E0002"
    assert config_exc.context["config_key"] == "learning_rate"
    print("  ✅ ConfigurationError working correctly")

    # Test to_dict serialization
    exc_dict = model_exc.to_dict()
    assert exc_dict["error_type"] == "ModelLoadError"
    assert exc_dict["message"] == "Model failed"
    assert exc_dict["error_code"] == "E2000"
    assert exc_dict["context"]["model_path"] == "/test/model.onnx"
    print("  ✅ Exception serialization working correctly")


def test_error_analyzer():
    """Test AC4: 实现转换失败的根本原因分析"""
    print("\n🧪 Testing AC4: 根本原因分析...")

    from npu_converter.utils.error_analyzer import ErrorAnalyzer, ErrorCategory, ErrorSeverity
    from npu_converter.utils.exceptions import ConverterException, ConverterErrorCodes

    analyzer = ErrorAnalyzer()

    # Test file not found analysis
    exc = ConverterException("No such file: /test/model.onnx", ConverterErrorCodes.FILE_NOT_FOUND)
    result = analyzer.analyze_exception(exc)

    assert result.exception_type == "ConverterException"
    assert result.error_code == "E1000"
    assert result.category == ErrorCategory.INPUT_DATA
    assert result.severity == ErrorSeverity.HIGH
    assert result.confidence_score > 0.5
    assert "missing or inaccessible" in result.root_cause
    assert len(result.suggested_actions) > 0
    print("  ✅ File not found analysis working correctly")

    # Test model compatibility analysis
    exc = ConverterException("Unsupported operator: CustomLayer", ConverterErrorCodes.MODEL_VALIDATION_ERROR)
    result = analyzer.analyze_exception(exc)

    assert result.category == ErrorCategory.MODEL_COMPATIBILITY
    assert "unsupported operators" in result.root_cause.lower()
    print("  ✅ Model compatibility analysis working correctly")

    # Test solution suggestions
    solutions = analyzer.suggest_solutions(result)
    assert len(solutions) > 0
    assert all(hasattr(sol, 'title') for sol in solutions)
    assert all(hasattr(sol, 'steps') for sol in solutions)
    assert all(hasattr(sol, 'success_probability') for sol in solutions)
    print("  ✅ Solution suggestions working correctly")


def test_knowledge_base():
    """Test AC5: 提供常见错误的自助解决建议"""
    print("\n🧪 Testing AC5: 自助解决建议...")

    from npu_converter.utils.knowledge_base import ErrorKnowledgeBase, SolutionType
    from npu_converter.utils.exceptions import ConverterErrorCodes

    kb = ErrorKnowledgeBase()

    # Test knowledge base lookup
    entry = kb.find_entry(ConverterErrorCodes.FILE_NOT_FOUND)
    assert entry is not None
    assert entry.error_code == ConverterErrorCodes.FILE_NOT_FOUND
    assert entry.title is not None
    assert entry.description is not None
    assert len(entry.symptoms) > 0
    assert len(entry.causes) > 0
    assert len(entry.solutions) > 0
    assert len(entry.prevention) > 0
    print("  ✅ Knowledge base lookup working correctly")

    # Test solutions include different types
    solutions = entry.solutions
    solution_types = [sol.get('type') for sol in solutions]
    assert any(sol_type in solution_types for sol_type in [SolutionType.MANUAL.value, SolutionType.AUTOMATED.value])
    print("  ✅ Multiple solution types available")

    # Test prevention tips
    prevention = kb.get_prevention_tips(ConverterErrorCodes.CONFIGURATION_ERROR)
    if prevention:
        assert len(prevention) > 0
        assert all(isinstance(tip, str) for tip in prevention)
        print("  ✅ Prevention tips available")

    # Test search functionality
    results = kb.search_entries("file")
    assert len(results) > 0
    print("  ✅ Knowledge base search working correctly")


def test_integrated_error_handler():
    """Test integrated error handling system"""
    print("\n🧪 Testing Integrated Error Handler...")

    from npu_converter.utils.error_handler import IntegratedErrorHandler, get_error_handler
    from npu_converter.utils.exceptions import ModelLoadError

    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        temp_log_dir = Path(temp_dir) / "logs"
        temp_log_dir.mkdir(exist_ok=True)
        os.chdir(temp_dir)

        try:
            # Test integrated handler
            handler = IntegratedErrorHandler("integration_test")

            # Test error handling workflow
            try:
                raise ModelLoadError("Test model error", model_path="/test/model.onnx", user_id="123")
            except ModelLoadError as e:
                handled_exception = handler.handle_error(e, context={"operation": "validation"})

                assert handled_exception.error_code == "E2000"
                assert handled_exception.context["model_path"] == "/test/model.onnx"
                assert handled_exception.context["user_id"] == "123"

            print("  ✅ Integrated error handling working correctly")

            # Test error report generation
            try:
                raise ValueError("Test python exception")
            except ValueError as e:
                report = handler.get_error_summary(e)

                assert "error" in report
                assert "analysis" in report
                assert "solutions" in report
                assert "knowledge_base" in report
                assert report["error"]["type"] == "ValueError"
                assert report["error"]["message"] == "Test python exception"

            print("  ✅ Error report generation working correctly")

            # Test global handler
            global_handler = get_error_handler("global_integration_test")
            assert global_handler is not None
            print("  ✅ Global error handler working correctly")

        finally:
            os.chdir(original_cwd)


def test_import_functionality():
    """Test that all imports work correctly"""
    print("\n🧪 Testing Import Functionality...")

    try:
        from npu_converter.utils import (
            StructuredLogger, ConverterException, ErrorAnalyzer,
            ErrorKnowledgeBase, IntegratedErrorHandler,
            get_logger, get_error_handler, error_handler
        )
        print("  ✅ All main imports working correctly")
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        raise


def main():
    """Run all validation tests."""
    print("🚀 开始错误处理系统验证测试")
    print("=" * 50)

    try:
        test_import_functionality()
        test_logger_implementation()
        test_exception_system()
        test_error_analyzer()
        test_knowledge_base()
        test_integrated_error_handler()

        print("\n" + "=" * 50)
        print("✅ 所有测试通过！错误处理系统实现正确")
        print("\n📊 验证结果总结:")
        print("  ✅ AC1: 分级日志记录（DEBUG, INFO, WARN, ERROR）- 完成")
        print("  ✅ AC2: 详细错误信息和错误代码 - 完成")
        print("  ✅ AC4: 根本原因分析 - 完成")
        print("  ✅ AC5: 自助解决建议 - 完成")
        print("  ✅ 集成测试 - 完成")

        return 0

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())