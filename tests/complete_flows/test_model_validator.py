#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型精度验证系统 - 测试套件
=====================================

这是Story 2.7: 模型精度验证系统的测试组件。

测试覆盖:
- 单元测试
- 集成测试
- 性能测试
- 端到端测试

作者: Claude Code / BMM Method
创建: 2025-10-28
版本: 1.0.0

BMM v6 Phase 3: 验证和测试
"""

import unittest
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from npu_converter.complete_flows.model_validator import (
    ModelValidator,
    ValidationConfig,
    ValidationMetrics,
    ValidationResult
)
from npu_converter.complete_flows.benchmark_system import (
    BenchmarkSystem,
    BenchmarkDataset,
    BenchmarkResult
)
from npu_converter.complete_flows.realtime_monitor import (
    RealtimeMonitor,
    RealtimeMetrics,
    MetricAlert
)
from npu_converter.complete_flows.batch_validator import (
    BatchValidator,
    BatchValidationTask,
    BatchValidationResult
)
from npu_converter.config.model_validation_config import (
    ModelValidationConfig,
    ValidationThresholds
)


class TestModelValidator(unittest.TestCase):
    """模型验证器测试"""

    def setUp(self):
        """测试初始化"""
        self.config = ValidationConfig(
            accuracy_threshold=0.98,
            max_inference_time=30.0
        )
        self.validator = ModelValidator(self.config)
        self.test_model_path = "tests/fixtures/model.onnx"

    def test_config_validation(self):
        """测试配置验证"""
        config = ValidationConfig(
            accuracy_threshold=0.95,
            max_inference_time=25.0
        )
        self.assertEqual(config.accuracy_threshold, 0.95)
        self.assertEqual(config.max_inference_time, 25.0)

    def test_validation_metrics(self):
        """测试验证指标"""
        metrics = ValidationMetrics(
            accuracy=0.99,
            precision=0.98,
            recall=0.97,
            inference_time=0.5
        )

        self.assertEqual(metrics.accuracy, 0.99)
        self.assertEqual(metrics.inference_time, 0.5)

    @patch('npu_converter.complete_flows.model_validator.logger')
    async def test_validate_model(self, mock_logger):
        """测试模型验证"""
        # 创建模拟进度回调
        progress_updates = []
        progress_callback = lambda p: progress_updates.append(p)

        validator = ModelValidator(self.config, progress_callback)

        # 执行验证
        result = await validator.validate_model(
            self.test_model_path,
            "test_model"
        )

        # 断言结果
        self.assertIsInstance(result, ValidationResult)
        self.assertEqual(result.model_path, self.test_model_path)
        self.assertIsNotNone(result.metrics)
        self.assertGreater(result.metrics.accuracy, 0)

        # 验证进度更新
        self.assertGreater(len(progress_updates), 0)

    @patch('npu_converter.complete_flows.model_validator.logger')
    async def test_validate_batch(self, mock_logger):
        """测试批量验证"""
        validator = ModelValidator(self.config)

        model_paths = [
            "tests/fixtures/model1.onnx",
            "tests/fixtures/model2.onnx",
            "tests/fixtures/model3.onnx"
        ]

        results = await validator.validate_batch(model_paths, "test_type")

        self.assertEqual(len(results), 3)
        for result in results:
            self.assertIsInstance(result, ValidationResult)

    def test_determine_validation_status(self):
        """测试验证状态判定"""
        metrics = ValidationMetrics(
            accuracy=0.99,
            quantization_loss=0.01,
            inference_time=0.5
        )

        status = self.validator._determine_validation_status(metrics)

        self.assertEqual(status.value, 'passed')

    def test_get_validation_history(self):
        """测试获取验证历史"""
        history = self.validator.get_validation_history()

        self.assertIsInstance(history, list)


class TestBenchmarkSystem(unittest.TestCase):
    """基准测试系统测试"""

    def setUp(self):
        """测试初始化"""
        self.benchmark_system = BenchmarkSystem()

    def test_init(self):
        """测试初始化"""
        self.assertIsInstance(self.benchmark_system, BenchmarkSystem)
        self.assertGreater(len(self.benchmark_system.datasets), 0)

    def test_load_default_datasets(self):
        """测试默认数据集加载"""
        datasets = self.benchmark_system.datasets

        # 检查VITS-Cantonese数据集
        self.assertIn('vits_cantonese_test', datasets)
        self.assertEqual(datasets['vits_cantonese_test'].data_type, 'audio')

        # 检查SenseVoice数据集
        self.assertIn('sensevoice_test', datasets)
        self.assertEqual(datasets['sensevoice_test'].data_type, 'audio')

        # 检查Piper VITS数据集
        self.assertIn('piper_vits_test', datasets)
        self.assertEqual(datasets['piper_vits_test'].data_type, 'audio')

    async def test_add_dataset(self):
        """测试添加数据集"""
        dataset = BenchmarkDataset(
            name='custom_test',
            path='datasets/custom',
            description='自定义测试数据集',
            data_type='audio',
            size=50,
            format='wav'
        )

        await self.benchmark_system.add_dataset(dataset)

        self.assertIn('custom_test', self.benchmark_system.datasets)
        self.assertEqual(self.benchmark_system.datasets['custom_test'].size, 50)

    async def test_get_dataset(self):
        """测试获取数据集"""
        dataset = await self.benchmark_system.get_dataset('vits_cantonese_test')

        self.assertIsNotNone(dataset)
        self.assertEqual(dataset.name, 'vits_cantonese_test')

    async def test_benchmark_model(self):
        """测试模型基准测试"""
        result = await self.benchmark_system.benchmark_model(
            model_path="models/test.onnx",
            model_name="test_model",
            dataset_name="vits_cantonese_test"
        )

        self.assertIsInstance(result, BenchmarkResult)
        self.assertEqual(result.model_name, "test_model")
        self.assertGreaterEqual(result.accuracy, 0.0)
        self.assertLessEqual(result.accuracy, 1.0)

    async def test_batch_benchmark(self):
        """测试批量基准测试"""
        model_configs = [
            {'name': 'model1', 'path': 'models/model1.onnx'},
            {'name': 'model2', 'path': 'models/model2.onnx'}
        ]

        results = await self.benchmark_system.batch_benchmark(
            model_configs,
            'vits_cantonese_test'
        )

        self.assertEqual(len(results), 2)
        for result in results:
            self.assertIsInstance(result, BenchmarkResult)

    async def test_compare_models(self):
        """测试模型对比"""
        results = [
            BenchmarkResult(
                model_name='model1',
                model_path='models/model1.onnx',
                dataset_name='test',
                timestamp=datetime.now(),
                accuracy=0.99,
                precision=0.98,
                recall=0.97,
                f1_score=0.98,
                inference_time=0.5,
                throughput=10.0,
                memory_usage=1024.0,
                status='passed'
            ),
            BenchmarkResult(
                model_name='model2',
                model_path='models/model2.onnx',
                dataset_name='test',
                timestamp=datetime.now(),
                accuracy=0.97,
                precision=0.96,
                recall=0.95,
                f1_score=0.96,
                inference_time=0.6,
                throughput=9.0,
                memory_usage=1100.0,
                status='passed'
            )
        ]

        comparison = await self.benchmark_system.compare_models(results)

        self.assertIn('best_accuracy', comparison)
        self.assertIn('statistics', comparison)
        self.assertEqual(comparison['statistics']['passed_count'], 2)


class TestRealtimeMonitor(unittest.TestCase):
    """实时监控系统测试"""

    def setUp(self):
        """测试初始化"""
        self.monitor = RealtimeMonitor(
            accuracy_threshold=0.98,
            max_inference_time=30.0
        )

    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.monitor.accuracy_threshold, 0.98)
        self.assertEqual(self.monitor.max_inference_time, 30.0)
        self.assertFalse(self.monitor.is_monitoring)

    def test_add_alert_callback(self):
        """测试添加告警回调"""
        callback = Mock()
        self.monitor.add_alert_callback(callback)

        self.assertEqual(len(self.monitor.alert_callbacks), 1)

    async def test_start_stop_monitoring(self):
        """测试开始和停止监控"""
        await self.monitor.start_monitoring("test_model")
        self.assertTrue(self.monitor.is_monitoring)

        await self.monitor.stop_monitoring()
        self.assertFalse(self.monitor.is_monitoring)

    async def test_update_metrics(self):
        """测试更新指标"""
        await self.monitor.start_monitoring("test_model")

        metrics = RealtimeMetrics(
            accuracy=0.99,
            inference_time=0.5
        )

        await self.monitor.update_metrics(metrics, "test_model")

        self.assertEqual(self.monitor.current_metrics, metrics)
        self.assertEqual(len(self.monitor.metrics_history), 1)

    async def test_alert_trigger(self):
        """测试告警触发"""
        alerts = []

        def capture_alert(alert):
            alerts.append(alert)

        self.monitor.add_alert_callback(capture_alert)
        await self.monitor.start_monitoring("test_model")

        # 触发精度告警
        metrics = RealtimeMetrics(accuracy=0.95)  # 低于阈值0.98
        await self.monitor.update_metrics(metrics, "test_model")

        # 等待告警处理
        await asyncio.sleep(0.1)

        # 应该有一个告警
        self.assertGreater(len(alerts), 0)
        self.assertEqual(alerts[0].metric_name, 'accuracy')

    def test_get_trend_analysis(self):
        """测试趋势分析"""
        # 添加一些测试数据
        for i in range(10):
            metrics = RealtimeMetrics(
                accuracy=0.98 + i * 0.001,
                inference_time=0.5 + i * 0.01
            )
            self.monitor.metrics_history.append(metrics)

        trend = self.monitor.get_trend_analysis()

        self.assertIn('accuracy_trend', trend)
        self.assertIn('performance_trend', trend)
        self.assertIn('current_accuracy', trend)
        self.assertIn('accuracy_stability', trend)


class TestBatchValidator(unittest.TestCase):
    """批量验证器测试"""

    def setUp(self):
        """测试初始化"""
        self.config = ValidationConfig()
        self.batch_validator = BatchValidator(self.config)

    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.batch_validator.max_workers, 4)
        self.assertEqual(len(self.batch_validator.batch_history), 0)

    async def test_create_task(self):
        """测试创建验证任务"""
        task = BatchValidationTask(
            model_path="models/test.onnx",
            model_name="test",
            model_type="test_type",
            priority=1
        )

        self.assertEqual(task.model_name, "test")
        self.assertEqual(task.priority, 1)

    @patch('npu_converter.complete_flows.batch_validator.logger')
    async def test_validate_batch(self, mock_logger):
        """测试批量验证"""
        tasks = [
            BatchValidationTask(
                model_path="models/model1.onnx",
                model_name="model1",
                model_type="test_type"
            ),
            BatchValidationTask(
                model_path="models/model2.onnx",
                model_name="model2",
                model_type="test_type"
            )
        ]

        result = await self.batch_validator.validate_batch(tasks, "test_batch")

        self.assertIsInstance(result, BatchValidationResult)
        self.assertEqual(result.batch_id, "test_batch")
        self.assertEqual(result.total_models, 2)

    def test_get_batch_history(self):
        """测试获取批量历史"""
        history = self.batch_validator.get_batch_history()
        self.assertIsInstance(history, list)

    def test_get_active_batches(self):
        """测试获取活动批次"""
        batches = self.batch_validator.get_active_batches()
        self.assertIsInstance(batches, list)


class TestModelValidationConfig(unittest.TestCase):
    """模型验证配置测试"""

    def test_create_default(self):
        """测试创建默认配置"""
        config = ModelValidationConfig.create_default()

        self.assertIsInstance(config, ModelValidationConfig)
        self.assertEqual(config.thresholds.accuracy, 0.98)

    def test_create_strict_preset(self):
        """测试创建严格模式配置"""
        config = ModelValidationConfig.create_default('strict')

        self.assertEqual(config.thresholds.accuracy, 0.99)

    def test_create_fast_preset(self):
        """测试创建快速模式配置"""
        config = ModelValidationConfig.create_default('fast')

        self.assertEqual(config.features.enable_performance_validation, False)

    def test_validate_config(self):
        """测试配置验证"""
        config = ModelValidationConfig.create_default()

        errors = config.validate_config()
        self.assertIsInstance(errors, list)

    def test_model_type_configs(self):
        """测试模型类型配置"""
        config = ModelValidationConfig.create_default()

        # 检查VITS-Cantonese配置
        vits_config = config.get_model_config('vits_cantonese')
        self.assertIn('accuracy_threshold', vits_config)

        # 检查SenseVoice配置
        sensevoice_config = config.get_model_config('sensevoice')
        self.assertIn('accuracy_threshold', sensevoice_config)

        # 检查Piper VITS配置
        piper_config = config.get_model_config('piper_vits')
        self.assertIn('accuracy_threshold', piper_config)

    def test_from_dict_to_dict(self):
        """测试字典转换"""
        config = ModelValidationConfig.create_default()

        # 转换为字典
        config_dict = config.to_dict()

        # 从字典创建
        new_config = ModelValidationConfig.from_dict(config_dict)

        # 验证相等
        self.assertEqual(new_config.thresholds.accuracy, config.thresholds.accuracy)

    async def test_save_and_load_config(self):
        """测试保存和加载配置"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = f.name

        try:
            # 保存配置
            config = ModelValidationConfig.create_default()
            config.save_to_file(temp_path)

            # 加载配置
            loaded_config = ModelValidationConfig.load_from_file(temp_path)

            # 验证相等
            self.assertEqual(
                loaded_config.thresholds.accuracy,
                config.thresholds.accuracy
            )

        finally:
            # 清理临时文件
            Path(temp_path).unlink(missing_ok=True)


# 集成测试
class TestIntegration(unittest.TestCase):
    """集成测试"""

    async def test_end_to_end_validation(self):
        """端到端验证测试"""
        # 创建配置
        config = ValidationConfig(accuracy_threshold=0.98)

        # 创建验证器
        validator = ModelValidator(config)

        # 验证模型
        result = await validator.validate_model(
            "tests/fixtures/model.onnx",
            "test_model"
        )

        # 验证结果
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.metrics)

        # 创建基准测试
        benchmark = BenchmarkSystem()

        # 执行基准测试
        benchmark_result = await benchmark.benchmark_model(
            "tests/fixtures/model.onnx",
            "test_model",
            "vits_cantonese_test"
        )

        self.assertIsNotNone(benchmark_result)


async def run_async_tests():
    """运行异步测试"""
    # 创建测试套件
    test_loader = unittest.TestLoader()
    test_suite = test_loader.loadTestsFromModule(__import__(__name__))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    print("运行模型精度验证系统测试套件...")
    print("=" * 70)

    success = asyncio.run(run_async_tests())

    print("=" * 70)
    if success:
        print("✅ 所有测试通过")
    else:
        print("❌ 测试失败")
        exit(1)
