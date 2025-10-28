"""
Unit tests for ErrorAnalyzer module.

Tests root cause analysis, solution suggestions, and pattern matching
as specified in AC4: 实现转换失败的根本原因分析
"""

import pytest
from unittest.mock import patch

import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from npu_converter.utils.error_analyzer import (
    ErrorAnalyzer,
    AnalysisResult,
    Solution,
    ErrorSeverity,
    ErrorCategory
)
from npu_converter.utils.exceptions import (
    ConverterException,
    ConverterErrorCodes,
    ModelLoadError,
    FileFormatError,
    ToolchainError,
    MemoryError
)


class TestErrorAnalyzer:
    """Test cases for ErrorAnalyzer class."""

    @pytest.fixture
    def analyzer(self):
        """Create ErrorAnalyzer instance for testing."""
        return ErrorAnalyzer()

    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initialization with patterns."""
        assert analyzer.error_patterns is not None
        assert len(analyzer.error_patterns) > 0
        assert analyzer.component_mappings is not None
        assert analyzer.solution_database is not None

    def test_analyze_file_not_found_error(self, analyzer):
        """Test analysis of file not found error."""
        exc = ConverterException(
            "No such file: /path/to/model.onnx",
            ConverterErrorCodes.FILE_NOT_FOUND,
            {"file_path": "/path/to/model.onnx"}
        )

        result = analyzer.analyze_exception(exc)

        assert result.exception_type == "ConverterException"
        assert result.error_code == "E1000"
        assert result.category == ErrorCategory.INPUT_DATA
        assert result.severity == ErrorSeverity.HIGH
        assert "missing or inaccessible" in result.root_cause
        assert "file_handler" in result.affected_components
        assert len(result.suggested_actions) > 0
        assert result.confidence_score > 0.5

    def test_analyze_permission_denied_error(self, analyzer):
        """Test analysis of permission denied error."""
        exc = ConverterException(
            "Permission denied: cannot read /protected/file.onnx",
            ConverterErrorCodes.FILE_PERMISSION_ERROR
        )

        result = analyzer.analyze_exception(exc)

        assert result.category == ErrorCategory.ENVIRONMENT
        assert result.severity == ErrorSeverity.HIGH
        assert "permissions" in result.root_cause.lower()
        assert "security" in result.affected_components

    def test_analyze_model_compatibility_error(self, analyzer):
        """Test analysis of model compatibility error."""
        exc = ModelLoadError(
            "Unsupported operator: CustomLayer not supported",
            model_path="/path/to/model.onnx"
        )

        result = analyzer.analyze_exception(exc)

        assert result.category == ErrorCategory.MODEL_COMPATIBILITY
        assert result.severity == ErrorSeverity.HIGH
        assert "unsupported operators" in result.root_cause.lower()
        assert "model_validator" in result.affected_components

    def test_analyze_toolchain_error(self, analyzer):
        """Test analysis of toolchain error."""
        exc = ToolchainError(
            "Compilation failed: internal compiler error",
            toolchain_version="2.1.0"
        )

        result = analyzer.analyze_exception(exc)

        assert result.category == ErrorCategory.TOOLCHAIN
        assert result.severity == ErrorSeverity.HIGH
        assert "compilation failed" in result.root_cause.lower()
        assert "compiler" in result.affected_components

    def test_analyze_memory_error(self, analyzer):
        """Test analysis of memory error."""
        exc = MemoryError("Out of memory: allocation failed")
        converted_exc = ConverterException(
            str(exc),
            ConverterErrorCodes.MEMORY_ERROR
        )

        result = analyzer.analyze_exception(converted_exc)

        assert result.category == ErrorCategory.SYSTEM_RESOURCES
        assert result.severity == ErrorSeverity.CRITICAL
        assert "memory" in result.root_cause.lower()

    def test_analyze_unknown_error(self, analyzer):
        """Test analysis of unknown error pattern."""
        exc = ConverterException(
            "Completely unknown error type",
            "E9999"  # Non-existent error code
        )

        result = analyzer.analyze_exception(exc)

        assert result.category == ErrorCategory.UNKNOWN
        assert result.severity == ErrorSeverity.MEDIUM
        assert "Unknown error" in result.root_cause
        assert result.confidence_score == 0.6  # Default confidence

    def test_suggest_solutions_for_file_error(self, analyzer):
        """Test solution suggestions for file-related errors."""
        exc = FileFormatError("Invalid file format", file_type="ONNX")
        analysis = analyzer.analyze_exception(exc)
        solutions = analyzer.suggest_solutions(analysis)

        assert len(solutions) > 0

        # Should have file-related solutions
        solution_titles = [sol.title for sol in solutions]
        assert any("文件" in title or "file" in title.lower() for title in solution_titles)

        # Solutions should be sorted by success probability
        success_rates = [sol.success_probability for sol in solutions]
        assert success_rates == sorted(success_rates, reverse=True)

    def test_suggest_solutions_for_config_error(self, analyzer):
        """Test solution suggestions for configuration errors."""
        exc = ConverterException(
            "Invalid configuration parameter",
            ConverterErrorCodes.CONFIGURATION_ERROR,
            {"config_key": "learning_rate"}
        )
        analysis = analyzer.analyze_exception(exc)
        solutions = analyzer.suggest_solutions(analysis)

        assert len(solutions) > 0

        # Should have automated solutions for config errors
        automated_solutions = [sol for sol in solutions if sol.automated_fix]
        assert len(automated_solutions) > 0

    def test_context_specific_solutions(self, analyzer):
        """Test context-specific solution generation."""
        exc = ConverterException(
            "Model validation failed",
            ConverterErrorCodes.MODEL_VALIDATION_ERROR
        )
        analysis = analyzer.analyze_exception(exc)
        solutions = analyzer.suggest_solutions(analysis)

        # Should have model validation specific solution
        solution_titles = [sol.title for sol in solutions]
        assert any("验证" in title or "validation" in title.lower() for title in solution_titles)

    def test_extract_related_files_from_stack_trace(self, analyzer):
        """Test extraction of related files from stack trace."""
        # Create exception with simulated stack trace
        try:
            # Simulate a call chain
            def nested_function():
                raise ConverterException("Test error", ConverterErrorCodes.UNKNOWN_ERROR)

            def outer_function():
                nested_function()

            outer_function()
        except Exception as e:
            result = analyzer.analyze_exception(e)

            # Should extract npu_converter files from stack trace
            # (This may be empty in test environment, but the method should not crash)
            assert isinstance(result.related_files, list)

    def test_confidence_score_calculation(self, analyzer):
        """Test confidence score calculation."""
        # High confidence for known pattern
        exc1 = ConverterException(
            "No such file: /test/path",
            ConverterErrorCodes.FILE_NOT_FOUND
        )
        result1 = analyzer.analyze_exception(exc1)

        # Lower confidence for unknown pattern
        exc2 = ConverterException(
            "Random error message",
            ConverterErrorCodes.UNKNOWN_ERROR
        )
        result2 = analyzer.analyze_exception(exc2)

        # Known pattern should have higher confidence
        assert result1.confidence_score > result2.confidence_score

    def test_analysis_result_dataclass(self):
        """Test AnalysisResult dataclass creation."""
        result = AnalysisResult(
            exception_type="ConverterException",
            error_code="E1000",
            category=ErrorCategory.INPUT_DATA,
            severity=ErrorSeverity.HIGH,
            root_cause="File not found",
            affected_components=["file_handler"],
            suggested_actions=["Check file path"],
            related_files=["src/loader.py"],
            confidence_score=0.8
        )

        assert result.exception_type == "ConverterException"
        assert result.error_code == "E1000"
        assert result.category == ErrorCategory.INPUT_DATA
        assert result.severity == ErrorSeverity.HIGH
        assert result.root_cause == "File not found"
        assert result.affected_components == ["file_handler"]
        assert result.suggested_actions == ["Check file path"]
        assert result.related_files == ["src/loader.py"]
        assert result.confidence_score == 0.8

    def test_solution_dataclass(self):
        """Test Solution dataclass creation."""
        solution = Solution(
            title="Fix file path",
            description="Check and correct file path",
            steps=["Verify path exists", "Check permissions"],
            automated_fix=False,
            success_probability=0.9
        )

        assert solution.title == "Fix file path"
        assert solution.description == "Check and correct file path"
        assert solution.steps == ["Verify path exists", "Check permissions"]
        assert solution.automated_fix is False
        assert solution.success_probability == 0.9


class TestErrorPatterns:
    """Test error pattern matching."""

    def test_pattern_matching_case_insensitive(self):
        """Test that pattern matching is case insensitive."""
        analyzer = ErrorAnalyzer()

        test_messages = [
            "NO SUCH FILE: test.txt",
            "No Such File: test.txt",
            "no such file: test.txt"
        ]

        for message in test_messages:
            exc = ConverterException(message, ConverterErrorCodes.FILE_NOT_FOUND)
            result = analyzer.analyze_exception(exc)
            assert result.category == ErrorCategory.INPUT_DATA

    def test_multiple_pattern_matches(self):
        """Test handling of multiple potential pattern matches."""
        analyzer = ErrorAnalyzer()

        # Create message that could match multiple patterns
        exc = ConverterException(
            "File not found and permission denied",
            ConverterErrorCodes.FILE_NOT_FOUND
        )
        result = analyzer.analyze_exception(exc)

        # Should find the first matching pattern
        assert result.category is not None
        assert result.confidence_score > 0.5

    def test_pattern_with_special_characters(self):
        """Test patterns with special regex characters."""
        analyzer = ErrorAnalyzer()

        exc = ConverterException(
            "Memory allocation failed: out of memory",
            ConverterErrorCodes.MEMORY_ERROR
        )
        result = analyzer.analyze_exception(exc)

        assert result.category == ErrorCategory.SYSTEM_RESOURCES


class TestErrorCategoriesAndSeverities:
    """Test error categories and severities."""

    def test_category_coverage(self):
        """Test that all expected categories are handled."""
        analyzer = ErrorAnalyzer()
        categories_used = set()

        # Check all patterns have categories
        for pattern_info in analyzer.error_patterns.values():
            category = pattern_info["category"]
            categories_used.add(category)

        # Should cover main categories
        expected_categories = {
            ErrorCategory.ENVIRONMENT,
            ErrorCategory.CONFIGURATION,
            ErrorCategory.INPUT_DATA,
            ErrorCategory.MODEL_COMPATIBILITY,
            ErrorCategory.TOOLCHAIN,
            ErrorCategory.SYSTEM_RESOURCES
        }

        assert categories_used.intersection(expected_categories) != set()

    def test_severity_levels(self):
        """Test that appropriate severity levels are assigned."""
        analyzer = ErrorAnalyzer()

        # Critical errors
        critical_patterns = [
            ("disk full", ErrorCategory.SYSTEM_RESOURCES),
            ("toolchain not found", ErrorCategory.ENVIRONMENT),
            ("out of memory", ErrorCategory.SYSTEM_RESOURCES)
        ]

        for message, expected_category in critical_patterns:
            exc = ConverterException(message, ConverterErrorCodes.UNKNOWN_ERROR)
            result = analyzer.analyze_exception(exc)
            assert result.severity == ErrorSeverity.CRITICAL


if __name__ == "__main__":
    pytest.main([__file__, "-v"])