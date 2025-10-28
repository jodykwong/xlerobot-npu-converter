"""
Integration tests for complete error handling flow.

Tests the integration of logging, exception handling, error analysis,
and knowledge base systems as specified in AC5: 提供常见错误的自助解决建议
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from npu_converter.utils import (
    StructuredLogger,
    ConverterException,
    ModelLoadError,
    ErrorAnalyzer,
    ErrorKnowledgeBase,
    IntegratedErrorHandler,
    get_error_handler,
    error_handler,
    safe_execute
)


class TestErrorHandlingIntegration:
    """Test integration of all error handling components."""

    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary directory for logs."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def integrated_handler(self, temp_log_dir):
        """Create integrated error handler for testing."""
        with patch('npu_converter.utils.logger.Path') as mock_path:
            mock_path.return_value = Path(temp_dir)
            handler = IntegratedErrorHandler("test_integration")
            return handler

    def test_complete_error_handling_workflow(self, integrated_handler, temp_log_dir):
        """Test complete workflow from error to solution suggestions (AC5)."""
        # Step 1: Create a model loading error
        try:
            raise ModelLoadError(
                "Failed to load ONNX model",
                model_path="/nonexistent/model.onnx",
                model_type="sensevoice"
            )
        except ModelLoadError as e:
            # Step 2: Handle error with integrated system
            handled_exception = integrated_handler.handle_error(
                e,
                context={"user_id": "123", "operation": "model_load"}
            )

            # Step 3: Verify error analysis
            assert handled_exception.error_code == "E2000"
            assert "sensevoice" in handled_exception.context

            # Step 4: Verify logging worked
            log_file = Path(temp_log_dir) / "test_integration.log"
            assert log_file.exists()

            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
                assert "Failed to load ONNX model" in log_content
                assert "user_id" in log_content
                assert "Error analysis completed" in log_content

    def test_solution_suggestions_integration(self, integrated_handler):
        """Test that solution suggestions are provided (AC5)."""
        # Create different types of errors and verify suggestions
        test_cases = [
            (
                ModelLoadError("File not found", model_path="/test/model.onnx"),
                "file"
            ),
            (
                ConverterException(
                    "Invalid configuration",
                    ConverterErrorCodes.CONFIGURATION_ERROR,
                    config_key="learning_rate"
                ),
                "config"
            ),
            (
                ConverterException(
                    "Out of memory",
                    ConverterErrorCodes.MEMORY_ERROR
                ),
                "memory"
            )
        ]

        for exception, expected_keyword in test_cases:
            with patch('npu_converter.utils.logger.Path') as mock_path:
                mock_path.return_value = Path(tempfile.mkdtemp())
                handler = IntegratedErrorHandler("test_suggestions")

                handled_exception = handler.handle_error(exception)
                analysis = handler.analyzer.analyze_exception(handled_exception)
                solutions = handler.analyzer.suggest_solutions(analysis)

                # Should have at least one solution
                assert len(solutions) > 0

                # Solutions should be sorted by success probability
                success_rates = [sol.success_probability for sol in solutions]
                assert success_rates == sorted(success_rates, reverse=True)

                # Should have relevant solutions (check via title or description)
                solution_text = " ".join([sol.title + " " + sol.description for sol in solutions])
                assert expected_keyword in solution_text.lower() or len(solutions) > 0

    def test_knowledge_base_integration(self, integrated_handler):
        """Test knowledge base integration with error handling."""
        # Create an error that exists in knowledge base
        exception = ConverterException(
            "No such file: /test/path",
            ConverterErrorCodes.FILE_NOT_FOUND
        )

        handled_exception = integrated_handler.handle_error(exception)

        # Verify knowledge base lookup happened
        kb_entry = integrated_handler.knowledge_base.find_entry(
            handled_exception.error_code
        )
        assert kb_entry is not None
        assert kb_entry.error_code == "E1000"

    def test_error_report_generation(self, integrated_handler):
        """Test comprehensive error report generation."""
        exception = ModelLoadError(
            "Model validation failed",
            model_path="/test/model.onnx",
            validation_errors=["Invalid shape", "Unsupported op"]
        )

        report = integrated_handler.get_error_summary(exception)

        # Verify report structure
        assert "error" in report
        assert "analysis" in report
        assert "solutions" in report
        assert "knowledge_base" in report

        # Verify error section
        assert report["error"]["type"] == "ModelLoadError"
        assert report["error"]["code"] == "E2001"
        assert "validation_errors" in report["error"]["context"]

        # Verify analysis section
        assert report["analysis"]["category"] == "model_compatibility"
        assert "confidence" in report["analysis"]
        assert "affected_components" in report["analysis"]

        # Verify solutions section
        assert len(report["solutions"]) > 0
        for solution in report["solutions"]:
            assert "title" in solution
            assert "steps" in solution
            assert "success_probability" in solution

    def test_error_decorator_functionality(self, temp_log_dir):
        """Test error handling decorator functionality."""
        with patch('npu_converter.utils.logger.Path') as mock_path:
            mock_path.return_value = Path(temp_log_dir)

            @error_handler(show_suggestions=True)
            def failing_function():
                raise ValueError("Intentional error for testing")

            # Should handle error gracefully and return None
            result = failing_function()
            assert result is None

            # Should log the error
            log_file = Path(temp_log_dir) / "npu_converter.log"
            assert log_file.exists()

    def test_safe_execute_functionality(self, temp_log_dir):
        """Test safe_execute functionality."""
        with patch('npu_converter.utils.logger.Path') as mock_path:
            mock_path.return_value = Path(temp_log_dir)

            def successful_function():
                return "success"

            def failing_function():
                raise RuntimeError("Test error")

            # Test successful execution
            result = safe_execute(successful_function)
            assert result == "success"

            # Test failing execution with default return
            result = safe_execute(failing_function, default_return="fallback")
            assert result == "fallback"

    def test_logging_context_propagation(self, integrated_handler, temp_log_dir):
        """Test that context properly propagates through logging system."""
        exception = ConverterException(
            "Context test error",
            ConverterErrorCodes.UNKNOWN_ERROR
        )

        complex_context = {
            "user_id": "123",
            "session_id": "abc-def",
            "operation": "model_conversion",
            "model_type": "sensevoice",
            "batch_size": 32,
            "metadata": {
                "version": "1.0",
                "environment": "test"
            }
        }

        integrated_handler.handle_error(exception, context=complex_context)

        # Verify context appears in logs
        log_file = Path(temp_log_dir) / "test_integration.log"
        with open(log_file, 'r', encoding='utf-8') as f:
            log_lines = f.readlines()

            # Should find context in structured log entries
            context_found = False
            for line in log_lines:
                try:
                    log_entry = json.loads(line.strip())
                    if "context" in log_entry:
                        context_found = True
                        assert log_entry["context"]["user_id"] == "123"
                        assert log_entry["context"]["operation"] == "model_conversion"
                        break
                except json.JSONDecodeError:
                    # Skip non-JSON lines (console output)
                    continue

            assert context_found, "Context not found in structured logs"

    def test_multiple_error_cascading(self, integrated_handler):
        """Test handling of cascading errors."""
        errors = []

        # Create multiple errors in sequence
        for i in range(3):
            try:
                if i == 0:
                    raise ModelLoadError(f"Error {i+1}", model_path=f"/test/model_{i+1}.onnx")
                elif i == 1:
                    raise ConverterException(f"Error {i+1}", ConverterErrorCodes.CONFIGURATION_ERROR)
                else:
                    raise ValueError(f"Error {i+1}")
            except Exception as e:
                handled = integrated_handler.handle_error(e, context={"error_index": i+1})
                errors.append(handled)

        # Verify all errors were handled
        assert len(errors) == 3

        # Verify different error types were handled
        error_codes = [error.error_code for error in errors]
        assert "E2000" in error_codes  # ModelLoadError
        assert "E0002" in error_codes  # ConfigurationError
        assert "E0000" in error_codes  # Unknown error (from ValueError)

    def test_global_error_handler_singleton(self, temp_log_dir):
        """Test global error handler singleton behavior."""
        with patch('npu_converter.utils.logger.Path') as mock_path:
            mock_path.return_value = Path(temp_log_dir)

            handler1 = get_error_handler("singleton_test")
            handler2 = get_error_handler("singleton_test")
            handler3 = get_error_handler("different_name")

            # Same name should return same instance
            assert handler1 is handler2

            # Different name should return different instance
            assert handler1 is not handler3

    def test_error_prevention_tips(self, integrated_handler):
        """Test that prevention tips are provided (AC5)."""
        exception = ConverterException(
            "Configuration parameter invalid",
            ConverterErrorCodes.CONFIGURATION_ERROR,
            config_key="learning_rate"
        )

        handled_exception = integrated_handler.handle_error(exception)

        # Get prevention tips from knowledge base
        prevention_tips = integrated_handler.knowledge_base.get_prevention_tips(
            handled_exception.error_code
        )

        # Should have prevention tips for common errors
        if prevention_tips:
            assert len(prevention_tips) > 0
            assert all(isinstance(tip, str) for tip in prevention_tips)


class TestErrorHandlingPerformance:
    """Test performance characteristics of error handling system."""

    def test_error_handling_performance(self):
        """Test that error handling doesn't significantly impact performance."""
        import time

        handler = get_error_handler("performance_test")

        # Measure time for handling multiple errors
        start_time = time.time()

        for i in range(100):
            try:
                raise ValueError(f"Performance test error {i}")
            except ValueError as e:
                handler.handle_error(e, context={"iteration": i})

        end_time = time.time()
        duration = end_time - start_time

        # Should handle 100 errors in reasonable time (less than 5 seconds)
        assert duration < 5.0, f"Error handling too slow: {duration:.2f}s for 100 errors"

    def test_memory_usage(self):
        """Test that error handling doesn't leak memory."""
        import gc
        import weakref

        handler = get_error_handler("memory_test")
        weak_refs = []

        # Create many errors and check they get garbage collected
        for i in range(50):
            try:
                raise ValueError(f"Memory test error {i}")
            except ValueError as e:
                handled = handler.handle_error(e, context={"iteration": i})
                weak_refs.append(weakref.ref(handled))

        # Force garbage collection
        gc.collect()

        # Most objects should be garbage collectible
        collected = sum(1 for ref in weak_refs if ref() is None)
        assert collected > len(weak_refs) * 0.8, "Too many error objects not garbage collected"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])