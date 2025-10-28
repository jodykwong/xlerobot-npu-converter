"""
Story 3.3 并发转换系统测试套件

此模块包含完整的测试用例，用于验证并发转换系统
在不同场景下的功能正确性和性能表现。

测试场景:
1. 基本并发功能测试
2. 任务调度测试
3. 批处理测试
4. 负载均衡测试
5. 性能压力测试

作者: Claude Code / Story 3.3
版本: 1.0
日期: 2025-10-28
"""

import sys
sys.path.insert(0, '/home/sunrise/xlerobot/src')

import unittest
import time
import threading
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor

from npu_converter.performance.concurrent_conversion_system import (
    ConcurrentConversionSystem,
    TaskScheduler,
    TaskPriority,
    TaskStatus,
    create_concurrent_converter,
)
from npu_converter.config.concurrent_optimization_config import (
    ConcurrentOptimizationPresets,
    create_config,
)


class TestTaskScheduler(unittest.TestCase):
    """任务调度器测试"""

    def setUp(self):
        self.scheduler = TaskScheduler(max_concurrent=5)

    def tearDown(self):
        self.scheduler.shutdown()

    def test_submit_task(self):
        """测试任务提交"""
        task_id = self.scheduler.submit_task(
            model_data=[1, 2, 3],
            conversion_params={'model_type': 'test'},
            priority=TaskPriority.NORMAL,
        )

        self.assertIsNotNone(task_id)
        self.assertTrue(task_id.startswith('task_'))

        task = self.scheduler.get_task(task_id)
        self.assertIsNotNone(task)
        self.assertEqual(task.status, TaskStatus.PENDING)

    def test_priority_scheduling(self):
        """测试优先级调度"""
        # 提交低优先级任务
        low_id = self.scheduler.submit_task(
            model_data=[1],
            conversion_params={},
            priority=TaskPriority.LOW,
        )

        # 提交高优先级任务
        high_id = self.scheduler.submit_task(
            model_data=[2],
            conversion_params={},
            priority=TaskPriority.HIGH,
        )

        # 高优先级任务应该先执行
        task = self.scheduler.get_next_task()
        self.assertIsNotNone(task)
        self.assertEqual(task.task_id, high_id)

    def test_task_completion(self):
        """测试任务完成"""
        task_id = self.scheduler.submit_task(
            model_data=[1, 2, 3],
            conversion_params={},
        )

        # 模拟任务执行
        task = self.scheduler.get_next_task()
        self.assertIsNotNone(task)

        # 开始任务
        self.scheduler.start_task(task)

        # 完成任务
        result = {'status': 'success'}
        self.scheduler.complete_task(task_id, result)

        # 验证任务状态
        completed_task = self.scheduler.get_task(task_id)
        self.assertEqual(completed_task.status, TaskStatus.COMPLETED)
        self.assertEqual(completed_task.result, result)

    def test_task_cancellation(self):
        """测试任务取消"""
        task_id = self.scheduler.submit_task(
            model_data=[1, 2, 3],
            conversion_params={},
        )

        # 取消任务
        cancelled = self.scheduler.cancel_task(task_id)
        self.assertTrue(cancelled)

        # 验证任务状态
        task = self.scheduler.get_task(task_id)
        self.assertEqual(task.status, TaskStatus.CANCELLED)

    def test_max_concurrent_limit(self):
        """测试最大并发数限制"""
        scheduler = TaskScheduler(max_concurrent=2)

        # 提交3个任务
        task_ids = []
        for i in range(3):
            task_id = scheduler.submit_task(
                model_data=[i],
                conversion_params={},
            )
            task_ids.append(task_id)

        # 只允许2个任务同时运行
        self.assertEqual(len(scheduler.running_tasks), 2)

        scheduler.shutdown()


class TestConcurrentConversionSystem(unittest.TestCase):
    """并发转换系统测试"""

    def test_create_converter(self):
        """测试创建转换器"""
        converter = create_concurrent_converter(
            max_concurrent=5,
            max_batch_size=5,
            preset='balanced',
        )

        self.assertIsNotNone(converter)
        self.assertEqual(converter.max_concurrent, 5)

    def test_submit_single_task(self):
        """测试提交单个任务"""
        converter = ConcurrentConversionSystem(
            max_concurrent=5,
            max_batch_size=5,
            enable_memory_optimization=False,
        )

        task_id = converter.submit_conversion(
            model_data=[1, 2, 3],
            conversion_params={'model_type': 'test'},
        )

        self.assertIsNotNone(task_id)

        # 验证任务存在
        task = converter.scheduler.get_task(task_id)
        self.assertIsNotNone(task)

        converter.shutdown()

    def test_submit_multiple_tasks(self):
        """测试提交多个任务"""
        converter = ConcurrentConversionSystem(
            max_concurrent=3,
            max_batch_size=3,
            enable_memory_optimization=False,
        )

        # 提交多个任务
        task_ids = []
        for i in range(10):
            task_id = converter.submit_conversion(
                model_data=list(range(100)),
                conversion_params={'model_type': 'test', 'iteration': i},
            )
            task_ids.append(task_id)

        self.assertEqual(len(task_ids), 10)

        # 验证所有任务都已提交
        for task_id in task_ids:
            task = converter.scheduler.get_task(task_id)
            self.assertIsNotNone(task)

        converter.shutdown()

    def test_wait_for_completion(self):
        """测试等待任务完成"""
        converter = ConcurrentConversionSystem(
            max_concurrent=2,
            max_batch_size=2,
            enable_memory_optimization=False,
        )

        # 提交任务并等待完成
        result = converter.submit_conversion(
            model_data=[1, 2, 3],
            conversion_params={'model_type': 'test'},
            wait_for_completion=True,
            timeout=5.0,
        )

        self.assertIsNotNone(result)
        self.assertEqual(result['status'], 'success')

        converter.shutdown()

    def test_priority_tasks(self):
        """测试优先级任务"""
        converter = ConcurrentConversionSystem(
            max_concurrent=2,
            max_batch_size=2,
            enable_memory_optimization=False,
        )

        # 提交不同优先级的任务
        low_id = converter.submit_conversion(
            model_data=[1],
            conversion_params={},
            priority=TaskPriority.LOW,
        )

        high_id = converter.submit_conversion(
            model_data=[2],
            conversion_params={},
            priority=TaskPriority.HIGH,
        )

        critical_id = converter.submit_conversion(
            model_data=[3],
            conversion_params={},
            priority=TaskPriority.CRITICAL,
        )

        # 获取指标
        metrics = converter.get_metrics()
        self.assertGreaterEqual(metrics.pending_tasks, 3)

        converter.shutdown()

    def test_batch_processing(self):
        """测试批处理"""
        converter = ConcurrentConversionSystem(
            max_concurrent=5,
            max_batch_size=5,
            enable_memory_optimization=False,
        )

        # 提交多个任务
        task_ids = []
        for i in range(15):
            task_id = converter.submit_conversion(
                model_data=list(range(100)),
                conversion_params={'model_type': 'test'},
                batch_mode=True,
            )
            task_ids.append(task_id)

        # 验证批处理
        self.assertGreater(len(task_ids), 0)

        converter.shutdown()

    def test_metrics_collection(self):
        """测试指标收集"""
        converter = ConcurrentConversionSystem(
            max_concurrent=3,
            max_batch_size=3,
            enable_memory_optimization=False,
        )

        # 提交任务
        converter.submit_conversion(
            model_data=[1, 2, 3],
            conversion_params={},
        )

        # 获取指标
        metrics = converter.get_metrics()
        self.assertIsNotNone(metrics.timestamp)
        self.assertGreaterEqual(metrics.active_tasks, 0)

        # 获取历史指标
        history = converter.get_metrics_history(count=10)
        self.assertLessEqual(len(history), 10)

        converter.shutdown()

    def test_stats(self):
        """测试统计信息"""
        converter = ConcurrentConversionSystem(
            max_concurrent=3,
            max_batch_size=3,
            enable_memory_optimization=False,
        )

        # 提交任务
        converter.submit_conversion(
            model_data=[1, 2, 3],
            conversion_params={},
        )

        # 获取统计信息
        stats = converter.get_stats()
        self.assertIn('tasks_submitted', stats)
        self.assertGreaterEqual(stats['tasks_submitted'], 1)

        converter.shutdown()

    def test_concurrent_context(self):
        """测试并发上下文管理器"""
        converter = ConcurrentConversionSystem(
            max_concurrent=3,
            max_batch_size=3,
            enable_memory_optimization=True,
        )

        # 使用上下文管理器
        with converter.concurrent_context():
            task_id = converter.submit_conversion(
                model_data=[1, 2, 3],
                conversion_params={},
            )
            self.assertIsNotNone(task_id)

        # 上下文管理器已自动关闭系统


class TestConcurrentConfig(unittest.TestCase):
    """并发配置测试"""

    def test_create_config_from_preset(self):
        """测试从预设创建配置"""
        config = ConcurrentOptimizationPresets.get_preset('balanced')
        self.assertIsNotNone(config)
        self.assertEqual(config.processing_mode.value, 'balanced')

    def test_list_presets(self):
        """测试列出预设"""
        presets = ConcurrentOptimizationPresets.list_presets()
        self.assertIn('balanced', presets)
        self.assertIn('high_throughput', presets)
        self.assertIn('low_latency', presets)

    def test_factory_create_config(self):
        """测试工厂函数创建配置"""
        config = create_config(
            level='high',
            mode='throughput',
            custom_params={'max_concurrent_tasks': 20},
        )

        self.assertIsNotNone(config)
        self.assertEqual(config.max_concurrent_tasks, 20)

    def test_get_concurrent_strategy(self):
        """测试获取并发策略"""
        config = ConcurrentOptimizationPresets.get_balanced_mode()
        strategy = config.get_concurrent_strategy()

        self.assertIn('level', strategy)
        self.assertIn('mode', strategy)
        self.assertIn('strategies', strategy)
        self.assertIn('thresholds', strategy)

    def test_is_optimization_enabled(self):
        """测试检查优化功能是否启用"""
        config = ConcurrentOptimizationPresets.get_balanced_mode()

        self.assertTrue(config.is_optimization_enabled('batch_processing'))
        self.assertTrue(config.is_optimization_enabled('memory_optimization'))
        self.assertFalse(config.is_optimization_enabled('invalid_feature'))


class TestConcurrentPerformance(unittest.TestCase):
    """并发性能测试"""

    def test_throughput_performance(self):
        """测试吞吐量性能"""
        converter = ConcurrentConversionSystem(
            max_concurrent=10,
            max_batch_size=10,
            enable_memory_optimization=False,
        )

        start_time = time.time()

        # 提交多个任务
        num_tasks = 20
        task_ids = []
        for i in range(num_tasks):
            task_id = converter.submit_conversion(
                model_data=list(range(1000)),
                conversion_params={'model_type': 'test'},
            )
            task_ids.append(task_id)

        # 运行系统2秒
        run_thread = threading.Thread(
            target=converter.run,
            kwargs={'duration': 2.0}
        )
        run_thread.start()
        run_thread.join()

        elapsed_time = time.time() - start_time
        throughput = len(task_ids) / elapsed_time if elapsed_time > 0 else 0

        print(f"\n吞吐量测试结果:")
        print(f"  任务数: {num_tasks}")
        print(f"  耗时: {elapsed_time:.2f}秒")
        print(f"  吞吐量: {throughput:.2f} 任务/秒")

        converter.shutdown()

    def test_concurrent_limit_performance(self):
        """测试并发限制性能"""
        converter = ConcurrentConversionSystem(
            max_concurrent=5,
            max_batch_size=5,
            enable_memory_optimization=False,
        )

        # 提交大量任务
        num_tasks = 50
        for i in range(num_tasks):
            converter.submit_conversion(
                model_data=list(range(100)),
                conversion_params={'model_type': 'test'},
            )

        # 获取指标
        metrics = converter.get_metrics()
        self.assertLessEqual(metrics.active_tasks, 5)

        converter.shutdown()

    def test_batch_vs_individual_performance(self):
        """测试批处理与单个任务性能比较"""

        # 批处理模式
        converter_batch = ConcurrentConversionSystem(
            max_concurrent=5,
            max_batch_size=10,
            enable_memory_optimization=False,
        )

        start_time = time.time()
        for i in range(20):
            converter_batch.submit_conversion(
                model_data=list(range(100)),
                conversion_params={'model_type': 'test'},
                batch_mode=True,
            )
        converter_batch.run(duration=2.0)
        batch_time = time.time() - start_time

        converter_batch.shutdown()

        # 单个任务模式
        converter_individual = ConcurrentConversionSystem(
            max_concurrent=5,
            max_batch_size=1,
            enable_memory_optimization=False,
        )

        start_time = time.time()
        for i in range(20):
            converter_individual.submit_conversion(
                model_data=list(range(100)),
                conversion_params={'model_type': 'test'},
                batch_mode=False,
            )
        converter_individual.run(duration=2.0)
        individual_time = time.time() - start_time

        converter_individual.shutdown()

        print(f"\n批处理性能对比:")
        print(f"  批处理模式耗时: {batch_time:.2f}秒")
        print(f"  单任务模式耗时: {individual_time:.2f}秒")


def run_benchmark_tests():
    """运行基准测试"""
    print("\n" + "=" * 70)
    print("Story 3.3 并发转换系统基准测试")
    print("=" * 70)

    # 创建测试套件
    suite = unittest.TestSuite()

    # 添加测试用例
    suite.addTest(TestTaskScheduler('test_submit_task'))
    suite.addTest(TestTaskScheduler('test_task_completion'))
    suite.addTest(TestTaskScheduler('test_max_concurrent_limit'))

    suite.addTest(TestConcurrentConversionSystem('test_submit_multiple_tasks'))
    suite.addTest(TestConcurrentConversionSystem('test_metrics_collection'))
    suite.addTest(TestConcurrentConversionSystem('test_stats'))

    suite.addTest(TestConcurrentConfig('test_create_config_from_preset'))
    suite.addTest(TestConcurrentConfig('test_factory_create_config'))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    print(f"基准测试完成!")
    print(f"  运行测试: {result.testsRun}")
    print(f"  失败: {len(result.failures)}")
    print(f"  错误: {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == '__main__':
    # 运行基准测试
    success = run_benchmark_tests()

    # 运行性能测试
    print("\n运行性能测试...")
    performance_suite = unittest.TestSuite()
    performance_suite.addTest(TestConcurrentPerformance('test_throughput_performance'))
    performance_suite.addTest(TestConcurrentPerformance('test_concurrent_limit_performance'))

    runner = unittest.TextTestRunner(verbosity=2)
    performance_result = runner.run(performance_suite)

    if success and performance_result.wasSuccessful():
        print("\n✅ 所有测试通过!")
    else:
        print("\n❌ 部分测试失败")
        sys.exit(1)
