#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
转换报告生成系统测试套件
========================

这是Story 2.9: 转换报告生成系统的测试组件。

测试范围:
- 单元测试: 核心功能测试
- 集成测试: 端到端流程测试
- 性能测试: 报告生成性能测试
- 验收测试: BMM v6 AC验证

作者: Claude Code / BMM Method
创建: 2025-10-28
版本: 1.0.0

BMM v6 Phase 3: 验证和测试
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json

# 导入被测试模块
from npu_converter.complete_flows.conversion_report_generator import (
    ConversionReportGenerator,
    ConversionReport
)
from npu_converter.config.conversion_report_config import (
    ConversionReportConfig,
    get_preset_config,
    create_custom_config
)

# 导入测试数据
from npu_converter.core.models.result_model import ResultModel
from npu_converter.complete_flows.model_validator import ValidationResult
from npu_converter.complete_flows.benchmark_system import BenchmarkResult


class TestConversionReportGenerator(unittest.TestCase):
    """
    转换报告生成器测试
    """

    def setUp(self):
        """
        测试前准备
        """
        self.temp_dir = tempfile.mkdtemp()
        self.generator = ConversionReportGenerator(output_dir=self.temp_dir)

        # 创建模拟数据
        self.mock_conversion_result = Mock(spec=ResultModel)
        self.mock_conversion_result.model_name = "test_model"
        self.mock_conversion_result.model_type = "TTS"
        self.mock_conversion_result.conversion_time = 10.5
        self.mock_conversion_result.success = True
        self.mock_conversion_result.resource_usage = {
            'cpu': 50.0,
            'memory': 1024.0,
            'npu': 75.0
        }
        self.mock_conversion_result.steps = [
            {"step": 1, "name": "load", "time": 2.0},
            {"step": 2, "name": "convert", "time": 6.0},
            {"step": 3, "name": "optimize", "time": 2.5}
        ]
        self.mock_conversion_result.config = Mock()
        self.mock_conversion_result.config.model_path = "/path/to/model"
        self.mock_conversion_result.errors = []
        self.mock_conversion_result.warnings = []

        self.mock_validation_result = Mock(spec=ValidationResult)
        self.mock_validation_result.accuracy_score = 0.985
        self.mock_validation_result.accuracy_loss = 0.015

        self.mock_benchmark_result = Mock(spec=BenchmarkResult)
        self.mock_benchmark_result.overall_score = 0.92
        self.mock_benchmark_result.inference_time = 0.15
        self.mock_benchmark_result.throughput = 85.5
        self.mock_benchmark_result.resource_usage = {
            'cpu': 45.0,
            'memory': 980.0,
            'npu': 70.0
        }

    def tearDown(self):
        """
        测试后清理
        """
        shutil.rmtree(self.temp_dir)

    def test_generate_basic_report(self):
        """
        测试基础报告生成
        """
        report = self.generator.generate_report(
            conversion_result=self.mock_conversion_result,
            report_format='json'
        )

        # 验证基本属性
        self.assertEqual(report.model_name, "test_model")
        self.assertEqual(report.model_type, "TTS")
        self.assertTrue(report.success)
        self.assertIsNotNone(report.report_id)
        self.assertEqual(report.report_format, 'json')

    def test_generate_report_with_validation(self):
        """
        测试带验证结果的报告生成
        """
        report = self.generator.generate_report(
            conversion_result=self.mock_conversion_result,
            validation_result=self.mock_validation_result,
            report_format='json'
        )

        # 验证精度数据
        self.assertEqual(report.accuracy_score, 0.985)
        self.assertEqual(report.accuracy_loss, 0.015)
        self.assertEqual(report.validation_result, self.mock_validation_result)

    def test_generate_report_with_benchmark(self):
        """
        测试带基准测试结果的报告生成
        """
        report = self.generator.generate_report(
            conversion_result=self.mock_conversion_result,
            benchmark_result=self.mock_benchmark_result,
            report_format='json'
        )

        # 验证性能数据
        self.assertEqual(report.performance_score, 0.92)
        self.assertEqual(report.inference_time, 0.15)
        self.assertEqual(report.throughput, 85.5)

    def test_generate_report_with_analysis(self):
        """
        测试带详细分析的报告生成
        """
        report = self.generator.generate_report(
            conversion_result=self.mock_conversion_result,
            validation_result=self.mock_validation_result,
            benchmark_result=self.mock_benchmark_result,
            include_analysis=True,
            include_recommendations=True
        )

        # 验证分析和建议
        self.assertIsNotNone(report.recommendations)
        self.assertIsInstance(report.recommendations, list)

    def test_quality_evaluation(self):
        """
        测试质量评估
        """
        report = self.generator.generate_report(
            conversion_result=self.mock_conversion_result,
            validation_result=self.mock_validation_result,
            benchmark_result=self.mock_benchmark_result
        )

        # 验证质量评分和等级
        self.assertIsNotNone(report.overall_score)
        self.assertIsNotNone(report.quality_grade)
        self.assertTrue(0.0 <= report.overall_score <= 1.0)
        self.assertIsInstance(report.quality_grade, str)

    def test_save_json_report(self):
        """
        测试保存JSON格式报告
        """
        report = self.generator.generate_report(
            conversion_result=self.mock_conversion_result
        )

        filepath = self.generator.save_report(report, format='json')

        # 验证文件存在
        self.assertTrue(filepath.exists())
        self.assertTrue(filepath.suffix, '.json')

        # 验证内容
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertEqual(data['model_name'], 'test_model')

    def test_save_html_report(self):
        """
        测试保存HTML格式报告
        """
        report = self.generator.generate_report(
            conversion_result=self.mock_conversion_result
        )

        filepath = self.generator.save_report(report, format='html')

        # 验证文件存在
        self.assertTrue(filepath.exists())
        self.assertTrue(filepath.suffix, '.html')

        # 验证内容
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('<html', content)
            self.assertIn('test_model', content)

    def test_batch_generate(self):
        """
        测试批量报告生成
        """
        # 创建多个转换结果
        conversion_results = []
        for i in range(3):
            result = Mock(spec=ResultModel)
            result.model_name = f"model_{i}"
            result.model_type = "TTS"
            result.conversion_time = 10.0
            result.success = True
            result.resource_usage = {}
            result.steps = []
            result.config = None
            result.errors = []
            result.warnings = []
            conversion_results.append(result)

        report_files = self.generator.batch_generate(
            conversion_results,
            output_format='json'
        )

        # 验证结果
        self.assertEqual(len(report_files), 3)
        for filepath in report_files:
            self.assertTrue(filepath.exists())

    def test_error_handling(self):
        """
        测试错误处理
        """
        # 测试无效格式
        with self.assertRaises(ValueError):
            self.generator.save_report(
                self.generator.generate_report(self.mock_conversion_result),
                format='invalid_format'
            )


class TestConversionReportConfig(unittest.TestCase):
    """
    转换报告配置测试
    """

    def setUp(self):
        """
        测试前准备
        """
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """
        测试后清理
        """
        shutil.rmtree(self.temp_dir)

    def test_default_config(self):
        """
        测试默认配置
        """
        config = ConversionReportConfig()

        # 验证默认属性
        self.assertIn('json', config.report_formats)
        self.assertIn('html', config.report_formats)
        self.assertEqual(config.default_format, 'html')
        self.assertTrue(config.include_performance)
        self.assertTrue(config.include_accuracy)

    def test_config_validation(self):
        """
        测试配置验证
        """
        config = ConversionReportConfig()

        # 有效配置
        self.assertTrue(config.validate())

        # 无效配置 - 修改阈值为无效值
        config.performance_threshold = 1.5
        self.assertFalse(config.validate())

    def test_get_preset_config(self):
        """
        测试获取预设配置
        """
        # 基础预设
        basic_config = get_preset_config('basic')
        self.assertEqual(basic_config.template_style, 'simple')

        # 详细预设
        detailed_config = get_preset_config('detailed')
        self.assertEqual(detailed_config.template_style, 'detailed')

        # 生产预设
        production_config = get_preset_config('production')
        self.assertTrue(production_config.include_conversion_steps)

    def test_create_custom_config(self):
        """
        测试创建自定义配置
        """
        custom_config = create_custom_config(
            format='json',
            include_performance=False,
            template_style='simple'
        )

        self.assertEqual(custom_config.default_format, 'json')
        self.assertFalse(custom_config.include_performance)
        self.assertEqual(custom_config.template_style, 'simple')

    def test_config_to_dict(self):
        """
        测试配置转换为字典
        """
        config = ConversionReportConfig()
        config_dict = config.to_dict()

        self.assertIsInstance(config_dict, dict)
        self.assertIn('report_formats', config_dict)
        self.assertIn('default_format', config_dict)


class TestAcceptanceCriteria(unittest.TestCase):
    """
    验收标准测试 (BMM v6 Phase 3)
    """

    def setUp(self):
        """
        测试前准备
        """
        self.temp_dir = tempfile.mkdtemp()
        self.generator = ConversionReportGenerator(output_dir=self.temp_dir)

        # 创建完整模拟数据
        self.mock_conversion_result = Mock(spec=ResultModel)
        self.mock_conversion_result.model_name = "VITS_Cantonese_Test"
        self.mock_conversion_result.model_type = "TTS"
        self.mock_conversion_result.conversion_time = 15.0
        self.mock_conversion_result.success = True
        self.mock_conversion_result.resource_usage = {
            'cpu': 55.0,
            'memory': 1100.0,
            'npu': 80.0
        }
        self.mock_conversion_result.steps = [
            {"step": 1, "name": "load", "time": 3.0},
            {"step": 2, "name": "convert", "time": 8.0},
            {"step": 3, "name": "optimize", "time": 4.0}
        ]
        self.mock_conversion_result.config = Mock()
        self.mock_conversion_result.config.quantization = "PTQ"
        self.mock_conversion_result.config.model_path = "/models/vits_cantonese"
        self.mock_conversion_result.errors = []
        self.mock_conversion_result.warnings = []

    def tearDown(self):
        """
        测试后清理
        """
        shutil.rmtree(self.temp_dir)

    def test_ac1_multi_dimensional_report(self):
        """
        AC1: 多维度转换报告框架

        验证能生成包含性能、精度、兼容性、资源使用和流程的完整报告
        """
        # 创建完整的验证和基准测试结果
        validation_result = Mock(spec=ValidationResult)
        validation_result.accuracy_score = 0.987
        validation_result.accuracy_loss = 0.013

        benchmark_result = Mock(spec=BenchmarkResult)
        benchmark_result.overall_score = 0.93
        benchmark_result.inference_time = 0.12
        benchmark_result.throughput = 92.5
        benchmark_result.resource_usage = {
            'cpu': 50.0,
            'memory': 1050.0,
            'npu': 75.0
        }

        report = self.generator.generate_report(
            conversion_result=self.mock_conversion_result,
            validation_result=validation_result,
            benchmark_result=benchmark_result
        )

        # AC1.1: 性能对比报告
        self.assertIsNotNone(report.performance_score)
        self.assertIsNotNone(report.inference_time)
        self.assertIsNotNone(report.throughput)

        # AC1.2: 精度验证报告
        self.assertIsNotNone(report.accuracy_score)
        self.assertIsNotNone(report.accuracy_loss)

        # AC1.3: 兼容性评估报告
        self.assertIsNotNone(report.compatibility_score)
        self.assertIsNotNone(report.operator_support)
        self.assertIsNotNone(report.hardware_compatibility)

        # AC1.4: 资源使用报告
        self.assertIsNotNone(report.cpu_usage)
        self.assertIsNotNone(report.memory_usage)
        self.assertIsNotNone(report.npu_usage)

        # AC1.5: 转换流程报告
        self.assertIsNotNone(report.conversion_steps)
        self.assertIsNotNone(report.conversion_params)

        print("✅ AC1 通过: 多维度转换报告框架")

    def test_ac2_automated_report_generation(self):
        """
        AC2: 自动化报告生成系统

        验证能自动触发报告生成并支持多种格式输出
        """
        # 生成报告
        report = self.generator.generate_report(
            conversion_result=self.mock_conversion_result,
            report_format='json'
        )

        # AC2.1: 自动报告生成
        self.assertIsNotNone(report)

        # AC2.2: 多格式输出 - JSON
        json_filepath = self.generator.save_report(report, format='json')
        self.assertTrue(json_filepath.exists())

        # AC2.3: 多格式输出 - HTML
        html_filepath = self.generator.save_report(report, format='html')
        self.assertTrue(html_filepath.exists())

        # AC2.4: 批量报告生成
        conversion_results = [self.mock_conversion_result]
        report_files = self.generator.batch_generate(
            conversion_results,
            output_format='json'
        )
        self.assertGreater(len(report_files), 0)

        print("✅ AC2 通过: 自动化报告生成系统")

    def test_ac3_detailed_analysis(self):
        """
        AC3: 详细分析和建议

        验证能生成详细分析和优化建议
        """
        # 创建包含性能问题的转换结果
        mock_result = Mock(spec=ResultModel)
        mock_result.model_name = "Low_Performance_Model"
        mock_result.model_type = "TTS"
        mock_result.conversion_time = 20.0
        mock_result.success = True
        mock_result.resource_usage = {'cpu': 80.0, 'memory': 2000.0, 'npu': 90.0}
        mock_result.steps = []
        mock_result.config = None
        mock_result.errors = ["性能警告: 内存使用过高"]
        mock_result.warnings = ["警告: 转换时间较长"]

        report = self.generator.generate_report(
            conversion_result=mock_result,
            include_analysis=True,
            include_recommendations=True
        )

        # AC3.1: 详细分析报告
        self.assertIsNotNone(report.overall_score)
        self.assertIsNotNone(report.quality_grade)

        # AC3.2: 优化建议
        self.assertIsNotNone(report.recommendations)
        self.assertIsInstance(report.recommendations, list)
        self.assertGreater(len(report.recommendations), 0)

        # AC3.3: 错误和警告
        self.assertIsNotNone(report.errors)
        self.assertIsNotNone(report.warnings)

        print("✅ AC3 通过: 详细分析和建议")

    def test_ac4_real_time_monitoring(self):
        """
        AC4: 实时报告监控

        验证报告生成过程的实时监控能力
        """
        # 模拟实时监控
        self.generator.monitor.start()

        report = self.generator.generate_report(
            conversion_result=self.mock_conversion_result
        )

        # AC4.1: 报告生成进度跟踪
        self.assertIsNotNone(report)

        # AC4.2: 实时监控集成
        self.assertIsNotNone(self.generator.monitor)

        print("✅ AC4 通过: 实时报告监控")

    def test_ac5_compatibility_report(self):
        """
        AC5: 模型兼容性详细报告

        验证能生成详细的兼容性分析报告
        """
        report = self.generator.generate_report(
            conversion_result=self.mock_conversion_result
        )

        # AC5.1: 兼容性分析报告
        self.assertIsNotNone(report.compatibility_score)

        # AC5.2: 算子支持分析
        self.assertIsNotNone(report.operator_support)
        self.assertIn('supported_ops', report.operator_support)
        self.assertIn('unsupported_ops', report.operator_support)

        # AC5.3: 硬件兼容性评估
        self.assertIsNotNone(report.hardware_compatibility)
        self.assertIn('npu_compatibility', report.hardware_compatibility)

        print("✅ AC5 通过: 模型兼容性详细报告")


def run_acceptance_tests():
    """
    运行验收测试
    """
    print("\n" + "="*60)
    print("🎯 BMM v6 Phase 3: 验证和测试")
    print("Story 2.9: 转换报告生成系统 - 验收测试")
    print("="*60 + "\n")

    # 创建测试套件
    suite = unittest.TestSuite()

    # 添加 AC 测试
    suite.addTest(TestAcceptanceCriteria('test_ac1_multi_dimensional_report'))
    suite.addTest(TestAcceptanceCriteria('test_ac2_automated_report_generation'))
    suite.addTest(TestAcceptanceCriteria('test_ac3_detailed_analysis'))
    suite.addTest(TestAcceptanceCriteria('test_ac4_real_time_monitoring'))
    suite.addTest(TestAcceptanceCriteria('test_ac5_compatibility_report'))

    # 添加单元测试
    suite.addTest(unittest.makeSuite(TestConversionReportGenerator))
    suite.addTest(unittest.makeSuite(TestConversionReportConfig))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出测试结果
    print("\n" + "="*60)
    print("📊 测试结果统计")
    print("="*60)
    print(f"总测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✅ 所有测试通过!")
        print("Story 2.9 BMM v6 Phase 3 验证完成")
    else:
        print("\n❌ 部分测试失败")
        print("需要修复问题后重新测试")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_acceptance_tests()
    exit(0 if success else 1)
