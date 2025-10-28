#!/usr/bin/env python3
"""
Story 2.10 验收测试脚本 (简化版)
===============================

验证转换失败诊断系统的5个验收标准：
1. AC1: 多维度失败诊断框架
2. AC2: 智能错误分析系统
3. AC3: 智能修复建议系统
4. AC4: 失败诊断报告系统
5. AC5: 失败预防建议系统

作者: XLeRobot 开发团队
日期: 2025-10-28
版本: 1.0.0
"""

import sys
import os
import json
from pathlib import Path
from unittest.mock import Mock

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))


def print_header(title):
    """打印测试标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_test_result(test_name, passed, message=""):
    """打印测试结果"""
    status = "✅ 通过" if passed else "❌ 失败"
    print(f"\n[{status}] {test_name}")
    if message:
        print(f"     {message}")


def test_core_classes_import():
    """测试核心类导入"""
    print_header("核心类导入测试")

    passed = True

    try:
        from src.npu_converter.complete_flows.failure_diagnostic_system import (
            FailureDiagnosticSystem,
            FailureDiagnostic
        )
        print("     ✅ FailureDiagnosticSystem 导入成功")
        print("     ✅ FailureDiagnostic 导入成功")
    except Exception as e:
        print(f"     ❌ 导入失败: {str(e)}")
        passed = False

    try:
        from src.npu_converter.config.failure_diagnostic_config import (
            FailureDiagnosticConfig,
            FailureDiagnosticConfigStrategy
        )
        print("     ✅ FailureDiagnosticConfig 导入成功")
        print("     ✅ FailureDiagnosticConfigStrategy 导入成功")
    except Exception as e:
        print(f"     ❌ 配置类导入失败: {str(e)}")
        passed = False

    print_test_result("核心类导入测试", passed)
    return passed


def test_failure_diagnostic_system_basic():
    """测试失败诊断系统基本功能"""
    print_header("AC1: 多维度失败诊断框架")

    passed = True

    try:
        from src.npu_converter.complete_flows.failure_diagnostic_system import (
            FailureDiagnosticSystem
        )

        # 创建模拟配置管理器
        config_manager = Mock()
        config_manager.get_config.return_value = {
            'include_stack_trace': True,
            'max_suggestions': 5
        }

        # 创建诊断系统
        diagnostic_system = FailureDiagnosticSystem(config_manager=config_manager)
        print("     ✅ 诊断系统创建成功")

        # 测试基本诊断功能
        test_error = ValueError("测试错误")
        diagnostic = diagnostic_system.diagnose_failure(
            error=test_error,
            model_name="test_model"
        )

        # 验证诊断结果
        if not diagnostic.model_name == "test_model":
            print(f"     ❌ 模型名称不匹配: {diagnostic.model_name}")
            passed = False

        if not diagnostic.failure_type:
            print("     ❌ 缺少失败类型")
            passed = False

        if not diagnostic.error_code:
            print("     ❌ 缺少错误代码")
            passed = False

        print(f"     ✅ 诊断结果: {diagnostic.failure_type} - {diagnostic.error_code}")

    except Exception as e:
        print(f"     ❌ 诊断测试失败: {str(e)}")
        passed = False

    print_test_result("AC1: 多维度失败诊断框架", passed)
    return passed


def test_error_analysis():
    """测试错误分析功能"""
    print_header("AC2: 智能错误分析系统")

    passed = True

    try:
        from src.npu_converter.complete_flows.failure_diagnostic_system import (
            FailureDiagnosticSystem
        )

        config_manager = Mock()
        config_manager.get_config.return_value = {'include_stack_trace': True}
        diagnostic_system = FailureDiagnosticSystem(config_manager=config_manager)

        # 测试不同类型的错误
        test_errors = [
            (FileNotFoundError("文件不存在"), "文件加载错误"),
            (ValueError("参数值无效"), "配置错误"),
            (RuntimeError("运行时错误"), "运行时错误")
        ]

        for error, error_desc in test_errors:
            diagnostic = diagnostic_system.diagnose_failure(
                error=error,
                model_name="test_model"
            )

            print(f"     {error_desc}:")
            print(f"       类型: {diagnostic.failure_type}")
            print(f"       严重程度: {diagnostic.severity}")

            if not diagnostic.failure_type:
                print(f"       ❌ 缺少失败类型")
                passed = False

    except Exception as e:
        print(f"     ❌ 错误分析测试失败: {str(e)}")
        passed = False

    print_test_result("AC2: 智能错误分析系统", passed)
    return passed


def test_fix_suggestions():
    """测试修复建议功能"""
    print_header("AC3: 智能修复建议系统")

    passed = True

    try:
        from src.npu_converter.complete_flows.failure_diagnostic_system import (
            FailureDiagnosticSystem
        )

        config_manager = Mock()
        config_manager.get_config.return_value = {'include_stack_trace': True}
        diagnostic_system = FailureDiagnosticSystem(config_manager=config_manager)

        # 测试修复建议
        error = FileNotFoundError("模型文件不存在")
        diagnostic = diagnostic_system.diagnose_failure(
            error=error,
            model_name="test_model"
        )

        # 验证修复建议
        if not diagnostic.suggestions or len(diagnostic.suggestions) == 0:
            print("     ❌ 缺少修复建议")
            passed = False
        else:
            print(f"     ✅ 生成了 {len(diagnostic.suggestions)} 条修复建议")
            for i, suggestion in enumerate(diagnostic.suggestions[:3], 1):
                print(f"       {i}. {suggestion}")

        # 验证修复步骤
        if not diagnostic.fix_steps or len(diagnostic.fix_steps) == 0:
            print("     ❌ 缺少修复步骤")
            passed = False
        else:
            print(f"     ✅ 生成了 {len(diagnostic.fix_steps)} 个修复步骤")

    except Exception as e:
        print(f"     ❌ 修复建议测试失败: {str(e)}")
        passed = False

    print_test_result("AC3: 智能修复建议系统", passed)
    return passed


def test_diagnostic_report():
    """测试诊断报告功能"""
    print_header("AC4: 失败诊断报告系统")

    passed = True

    try:
        from src.npu_converter.complete_flows.failure_diagnostic_system import (
            FailureDiagnosticSystem
        )

        config_manager = Mock()
        config_manager.get_config.return_value = {'include_stack_trace': True}
        diagnostic_system = FailureDiagnosticSystem(config_manager=config_manager)

        # 生成诊断
        error = ValueError("配置参数无效")
        diagnostic = diagnostic_system.diagnose_failure(
            error=error,
            model_name="test_model"
        )

        # 测试 JSON 报告
        try:
            json_report = diagnostic_system.generate_diagnostic_report(
                diagnostic=diagnostic,
                output_format='json'
            )
            json_data = json.loads(json_report)
            print(f"     ✅ JSON 报告生成成功, 包含 {len(json_data)} 个字段")
        except Exception as e:
            print(f"     ❌ JSON 报告生成失败: {str(e)}")
            passed = False

        # 测试 HTML 报告
        try:
            html_report = diagnostic_system.generate_diagnostic_report(
                diagnostic=diagnostic,
                output_format='html'
            )
            if '<!DOCTYPE html>' in html_report:
                print(f"     ✅ HTML 报告生成成功, 长度: {len(html_report)} 字符")
            else:
                print("     ❌ HTML 报告格式不正确")
                passed = False
        except Exception as e:
            print(f"     ❌ HTML 报告生成失败: {str(e)}")
            passed = False

    except Exception as e:
        print(f"     ❌ 诊断报告测试失败: {str(e)}")
        passed = False

    print_test_result("AC4: 失败诊断报告系统", passed)
    return passed


def test_prevention_measures():
    """测试预防措施功能"""
    print_header("AC5: 失败预防建议系统")

    passed = True

    try:
        from src.npu_converter.complete_flows.failure_diagnostic_system import (
            FailureDiagnosticSystem
        )

        config_manager = Mock()
        config_manager.get_config.return_value = {'include_stack_trace': True}
        diagnostic_system = FailureDiagnosticSystem(config_manager=config_manager)

        # 生成多个诊断
        test_errors = [
            FileNotFoundError("文件不存在"),
            ValueError("参数值无效"),
            RuntimeError("运行时错误")
        ]

        for error in test_errors:
            diagnostic = diagnostic_system.diagnose_failure(
                error=error,
                model_name="test_model"
            )

            # 验证预防措施
            if not diagnostic.prevention_measures or len(diagnostic.prevention_measures) == 0:
                print(f"     ❌ {diagnostic.failure_type} - 缺少预防措施")
                passed = False
            else:
                print(f"     ✅ {diagnostic.failure_type} - 生成了 {len(diagnostic.prevention_measures)} 个预防措施")

        # 测试诊断历史分析
        if len(diagnostic_system.diagnostic_history) > 0:
            summary = diagnostic_system.analyze_diagnostic_history()
            print(f"     ✅ 诊断历史分析成功: 总计 {summary.total_failures} 个失败")
            print(f"     ✅ 推荐行动: {len(summary.recommended_actions)} 条")

    except Exception as e:
        print(f"     ❌ 预防措施测试失败: {str(e)}")
        passed = False

    print_test_result("AC5: 失败预防建议系统", passed)
    return passed


def test_configuration_system():
    """测试配置系统"""
    print_header("配置系统测试")

    passed = True

    try:
        from src.npu_converter.config.failure_diagnostic_config import (
            FailureDiagnosticConfig,
            FailureDiagnosticConfigStrategy
        )

        # 测试默认配置
        config = FailureDiagnosticConfig()
        config.validate()
        print("     ✅ 默认配置验证通过")

        # 测试预设配置
        config_manager = Mock()
        config_strategy = FailureDiagnosticConfigStrategy(config_manager)

        preset_names = config_strategy.get_preset_config_names()
        print(f"     ✅ 可用预设配置: {', '.join(preset_names)}")

        for preset_name in ['basic', 'detailed', 'production']:
            if preset_name in preset_names:
                config = config_strategy.load_config(preset_name=preset_name)
                print(f"     ✅ 预设配置 '{preset_name}' 加载成功")

    except Exception as e:
        print(f"     ❌ 配置系统测试失败: {str(e)}")
        passed = False

    print_test_result("配置系统测试", passed)
    return passed


def main():
    """主测试函数"""
    print("\n" + "=" * 70)
    print("  XLeRobot NPU模型转换工具")
    print("  Story 2.10 转换失败诊断系统 - 验收测试")
    print("  测试日期: 2025-10-28")
    print("=" * 70)

    test_results = []

    # 执行验收标准测试
    test_results.append(("核心类导入测试", test_core_classes_import()))
    test_results.append(("AC1: 多维度失败诊断框架", test_failure_diagnostic_system_basic()))
    test_results.append(("AC2: 智能错误分析系统", test_error_analysis()))
    test_results.append(("AC3: 智能修复建议系统", test_fix_suggestions()))
    test_results.append(("AC4: 失败诊断报告系统", test_diagnostic_report()))
    test_results.append(("AC5: 失败预防建议系统", test_prevention_measures()))
    test_results.append(("配置系统测试", test_configuration_system()))

    # 打印测试总结
    print_header("测试总结")

    total_tests = len(test_results)
    passed_tests = sum(1 for _, passed in test_results if passed)
    failed_tests = total_tests - passed_tests

    print(f"\n总测试数: {total_tests}")
    print(f"通过数: {passed_tests}")
    print(f"失败数: {failed_tests}")
    print(f"成功率: {(passed_tests / total_tests * 100):.1f}%")

    # 打印详细结果
    print("\n详细结果:")
    for test_name, passed in test_results:
        status = "✅" if passed else "❌"
        print(f"  {status} {test_name}")

    # 返回测试结果
    if failed_tests == 0:
        print("\n🎉 所有测试通过! Story 2.10 验收测试成功!")
        return 0
    else:
        print(f"\n⚠️  有 {failed_tests} 个测试失败，请检查日志")
        return 1


if __name__ == '__main__':
    sys.exit(main())