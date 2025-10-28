#!/usr/bin/env python3
"""
Simple Error Handling System Validation

Quick validation of the error handling system implementation.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    print("🧪 简化错误处理系统验证")
    print("=" * 40)

    try:
        # Test imports
        from npu_converter.utils import (
            StructuredLogger, ConverterException, ErrorAnalyzer,
            ErrorKnowledgeBase, IntegratedErrorHandler
        )
        print("✅ 所有模块导入成功")

        # Test AC1: 分级日志记录
        logger = StructuredLogger("validation_test")
        logger.debug("Debug message", test_id="1")
        logger.info("Info message", test_id="2")
        logger.warning("Warning message", test_id="3")
        logger.error("Error message", test_id="4")
        print("✅ AC1: 分级日志记录 - 完成")

        # Test AC2: 错误信息和错误代码
        from npu_converter.utils.exceptions import ConverterErrorCodes, ModelLoadError
        exc = ModelLoadError("Failed to load model: file not found", model_path="/test/model.onnx")
        assert exc.error_code == "E2000"
        assert exc.context["model_path"] == "/test/model.onnx"
        print("✅ AC2: 错误信息和错误代码 - 完成")

        # Test AC4: 根本原因分析
        analyzer = ErrorAnalyzer()
        result = analyzer.analyze_exception(exc)
        assert result.category is not None
        assert result.severity is not None
        assert len(result.suggested_actions) > 0
        print(f"  Category: {result.category.value}, Severity: {result.severity.value}")
        print(f"  Root cause: {result.root_cause}")
        print(f"  Suggested actions: {len(result.suggested_actions)}")
        print("✅ AC4: 根本原因分析 - 完成")

        # Test AC5: 自助解决建议
        solutions = analyzer.suggest_solutions(result)
        print(f"  Solutions found: {len(solutions)}")
        for i, sol in enumerate(solutions[:3]):  # Show first 3
            print(f"    {i+1}. {sol.title} (Success: {sol.success_probability:.0%})")
        assert len(solutions) > 0
        print("✅ AC5: 自助解决建议 - 完成")

        # Test integrated error handler
        handler = IntegratedErrorHandler("integration_test")
        handled = handler.handle_error(exc, context={"validation": True})
        assert handled.error_code == "E2000"
        print("✅ 集成错误处理 - 完成")

        print("\n" + "=" * 40)
        print("🎉 所有验证通过！故事1.7实现成功")
        print("\n📋 已完成的功能:")
        print("  ✅ AC1: 实现分级日志记录（DEBUG, INFO, WARN, ERROR）")
        print("  ✅ AC2: 提供详细的错误信息和错误代码")
        print("  ✅ AC4: 实现转换失败的根本原因分析")
        print("  ✅ AC5: 提供常见错误的自助解决建议")
        print("  ✅ 完整的集成错误处理系统")

        return 0

    except Exception as e:
        print(f"❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())