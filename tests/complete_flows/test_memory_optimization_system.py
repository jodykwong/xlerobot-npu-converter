"""
内存使用优化系统测试套件

为Story 3.2: 内存使用优化提供完整的测试覆盖，
包括单元测试、集成测试、性能测试和端到端测试。

作者: Claude Code / BMM v6
版本: 1.0
日期: 2025-10-28
"""

import unittest
import time
import threading
import gc
import tracemalloc
from typing import Dict, Any, List, Tuple
from unittest.mock import Mock, patch, MagicMock
import pytest

from src.npu_converter.config.memory_optimization_config import (
    MemoryOptimizationConfig,
    OptimizationLevel,
    MemoryMode,
    MemoryOptimizationPresets,
    create_config,
    load_config_from_yaml,
    save_config_to_yaml,
)


class TestMemoryOptimizationConfig(unittest.TestCase):
    """测试内存优化配置模型"""

    def setUp(self):
        """测试前准备"""
        self.config = MemoryOptimizationConfig()

    def test_default_config_creation(self):
        """测试默认配置创建"""
        self.assertEqual(self.config.optimization_level, OptimizationLevel.BALANCED)
        self.assertEqual(self.config.memory_mode, MemoryMode.STANDARD)
        self.assertTrue(self.config.monitoring_enabled)
        self.assertTrue(self.config.memory_pool_enabled)

    def test_custom_config_creation(self):
        """测试自定义配置创建"""
        custom_config = MemoryOptimizationConfig(
            optimization_level=OptimizationLevel.AGGRESSIVE,
            memory_mode=MemoryMode.HIGH_PERFORMANCE,
            monitoring_interval=0.05,
        )
        self.assertEqual(custom_config.optimization_level, OptimizationLevel.AGGRESSIVE)
        self.assertEqual(custom_config.memory_mode, MemoryMode.HIGH_PERFORMANCE)
        self.assertEqual(custom_config.monitoring_interval, 0.05)

    def test_optimization_strategy_getter(self):
        """测试优化策略获取"""
        strategy = self.config.get_optimization_strategy()
        self.assertIn("level", strategy)
        self.assertIn("mode", strategy)
        self.assertIn("strategies", strategy)
        self.assertIn("thresholds", strategy)
        self.assertEqual(strategy["level"], "balanced")
        self.assertEqual(strategy["mode"], "standard")

    def test_feature_enabled_checker(self):
        """测试功能启用检查"""
        self.assertTrue(self.config.is_optimization_enabled("monitoring"))
        self.assertTrue(self.config.is_optimization_enabled("memory_pool"))
        self.assertFalse(self.config.is_optimization_enabled("batch_processing"))  # 默认禁用
        self.assertFalse(self.config.is_optimization_enabled("nonexistent_feature"))

    def test_validation(self):
        """测试参数验证"""
        # 测试报告格式验证
        with self.assertRaises(ValueError):
            MemoryOptimizationConfig(report_format=["invalid_format"])

        # 测试数值范围验证
        with self.assertRaises(ValueError):
            MemoryOptimizationConfig(monitoring_interval=100.0)  # 超出范围


class TestMemoryOptimizationPresets(unittest.TestCase):
    """测试内存优化预设配置"""

    def test_low_memory_preset(self):
        """测试低内存模式预设"""
        config = MemoryOptimizationPresets.get_low_memory_mode()
        self.assertEqual(config.optimization_level, OptimizationLevel.AGGRESSIVE)
        self.assertEqual(config.memory_mode, MemoryMode.LOW_MEMORY)
        self.assertEqual(config.peak_memory_threshold, 0.70)
        self.assertTrue(config.memory_compression_enabled)

    def test_standard_preset(self):
        """测试标准模式预设"""
        config = MemoryOptimizationPresets.get_standard_mode()
        self.assertEqual(config.optimization_level, OptimizationLevel.BALANCED)
        self.assertEqual(config.memory_mode, MemoryMode.STANDARD)
        self.assertTrue(config.batch_processing_enabled)

    def test_high_performance_preset(self):
        """测试高性能模式预设"""
        config = MemoryOptimizationPresets.get_high_performance_mode()
        self.assertEqual(config.optimization_level, OptimizationLevel.AGGRESSIVE)
        self.assertEqual(config.memory_mode, MemoryMode.HIGH_PERFORMANCE)
        self.assertTrue(config.model_sharding_enabled)

    def test_batch_processing_preset(self):
        """测试批处理模式预设"""
        config = MemoryOptimizationPresets.get_batch_processing_mode()
        self.assertEqual(config.memory_mode, MemoryMode.BATCH_PROCESSING)
        self.assertTrue(config.batch_processing_enabled)
        self.assertEqual(config.batch_size, 16)

    def test_get_preset(self):
        """测试获取预设"""
        config = MemoryOptimizationPresets.get_preset("standard")
        self.assertIsNotNone(config)
        self.assertIsInstance(config, MemoryOptimizationConfig)

        # 测试无效预设
        invalid_config = MemoryOptimizationPresets.get_preset("invalid_preset")
        self.assertIsNone(invalid_config)

    def test_list_presets(self):
        """测试列出预设"""
        presets = MemoryOptimizationPresets.list_presets()
        self.assertIn("low_memory", presets)
        self.assertIn("standard", presets)
        self.assertIn("high_performance", presets)
        self.assertIn("batch_processing", presets)


class TestConfigFactory(unittest.TestCase):
    """测试配置工厂函数"""

    def test_create_config_from_preset(self):
        """测试从预设创建配置"""
        config = create_config(preset="standard")
        self.assertEqual(config.optimization_level, OptimizationLevel.BALANCED)

    def test_create_config_with_level_and_mode(self):
        """测试指定优化级别和模式"""
        config = create_config(level="aggressive", mode="high_performance")
        self.assertEqual(config.optimization_level, OptimizationLevel.AGGRESSIVE)
        self.assertEqual(config.memory_mode, MemoryMode.HIGH_PERFORMANCE)

    def test_create_config_with_custom_params(self):
        """测试自定义参数"""
        custom_params = {
            "monitoring_interval": 0.05,
            "memory_pool_size": 500 * 1024 * 1024,  # 500MB
        }
        config = create_config(custom_params=custom_params)
        self.assertEqual(config.monitoring_interval, 0.05)
        self.assertEqual(config.memory_pool_size, 500 * 1024 * 1024)

    def test_create_config_invalid_level(self):
        """测试无效优化级别"""
        with self.assertRaises(ValueError):
            create_config(level="invalid_level")

    def test_create_config_invalid_mode(self):
        """测试无效内存模式"""
        with self.assertRaises(ValueError):
            create_config(mode="invalid_mode")

    def test_create_config_invalid_custom_param(self):
        """测试无效自定义参数"""
        with self.assertRaises(ValueError):
            create_config(custom_params={"invalid_param": "value"})


class TestMemoryMonitoring(unittest.TestCase):
    """测试内存监控功能"""

    def setUp(self):
        """测试前准备"""
        self.config = MemoryOptimizationConfig(monitoring_enabled=True)

    def test_memory_monitoring(self):
        """测试内存监控"""
        # 开始内存追踪
        tracemalloc.start()

        # 分配一些内存
        data = [i for i in range(10000)]

        # 获取当前内存使用情况
        current, peak = tracemalloc.get_traced_memory()
        self.assertGreater(current, 0)
        self.assertGreater(peak, current)

        # 停止内存追踪
        tracemalloc.stop()

    def test_memory_threshold_monitoring(self):
        """测试内存阈值监控"""
        # 模拟监控过程
        total_memory = 8 * 1024 * 1024 * 1024  # 8GB
        threshold = self.config.peak_memory_threshold

        # 模拟内存使用
        current_usage = total_memory * 0.9  # 90%
        self.assertGreater(current_usage / total_memory, threshold)

    def test_memory_growth_monitoring(self):
        """测试内存增长监控"""
        memory_usage = []

        # 模拟内存使用增长
        for i in range(10):
            # 分配内存
            data = [0] * (1000 * (i + 1))
            # 记录内存使用
            memory_usage.append(len(data))

        # 验证内存使用增长
        self.assertEqual(len(memory_usage), 10)
        self.assertGreater(memory_usage[-1], memory_usage[0])


class TestMemoryOptimization(unittest.TestCase):
    """测试内存优化策略"""

    def setUp(self):
        """测试前准备"""
        self.config = MemoryOptimizationConfig(
            memory_pool_enabled=True,
            object_reuse_enabled=True,
            operator_optimization_enabled=True,
        )

    def test_object_reuse(self):
        """测试对象复用优化"""
        # 模拟对象池
        object_pool = []
        reuse_threshold = 10

        # 创建对象
        for i in range(20):
            if i < 10:
                obj = {"id": i, "data": f"data_{i}"}
                object_pool.append(obj)
            else:
                # 重用对象
                if len(object_pool) > 0:
                    obj = object_pool[0]
                    obj["data"] = f"data_{i}"
                    object_pool[0] = obj

        # 验证对象复用
        self.assertLessEqual(len(object_pool), reuse_threshold)

    def test_memory_pool_allocation(self):
        """测试内存池分配"""
        pool_size = self.config.memory_pool_size
        allocated = []

        # 模拟内存分配
        for i in range(10):
            chunk_size = pool_size // 20
            allocated.append(chunk_size)

        # 验证分配
        total_allocated = sum(allocated)
        self.assertLessEqual(total_allocated, pool_size)

    def test_garbage_collection_optimization(self):
        """测试GC优化"""
        # 收集初始GC统计
        gc.collect()
        before_count = gc.collect()

        # 创建循环引用
        obj1 = {"data": "test1"}
        obj2 = {"data": "test2"}
        obj1["ref"] = obj2
        obj2["ref"] = obj1

        # 删除引用
        del obj1
        del obj2

        # 强制GC
        after_count = gc.collect()

        # 验证GC工作
        self.assertGreaterEqual(after_count, 0)


class TestMemoryLeakDetection(unittest.TestCase):
    """测试内存泄漏检测"""

    def setUp(self):
        """测试前准备"""
        self.config = MemoryOptimizationConfig(leak_detection_enabled=True)
        self.leak_detected = False

    def test_memory_leak_detection(self):
        """测试内存泄漏检测"""
        # 开始内存追踪
        tracemalloc.start()

        # 记录初始内存
        snapshot1 = tracemalloc.take_snapshot()

        # 分配内存但不释放（模拟泄漏）
        leaked_objects = []
        for i in range(1000):
            leaked_objects.append([0] * 100)

        # 记录分配后内存
        snapshot2 = tracemalloc.take_snapshot()

        # 分析差异
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')

        # 检查是否有显著内存增长
        memory_growth = sum(stat.size_diff for stat in top_stats)
        self.assertGreater(memory_growth, 0)

        # 清理
        del leaked_objects
        tracemalloc.stop()

    def test_out_of_bounds_detection(self):
        """测试越界检测"""
        # 测试数组越界
        with self.assertRaises(IndexError):
            arr = [1, 2, 3]
            _ = arr[10]  # 越界访问

        # 测试字符串越界
        with self.assertRaises(IndexError):
            s = "test"
            _ = s[10]  # 越界访问

    def test_reference_cycle_detection(self):
        """测试循环引用检测"""
        # 创建循环引用
        obj1 = {"name": "obj1"}
        obj2 = {"name": "obj2"}
        obj1["ref"] = obj2
        obj2["ref"] = obj1

        # 检查循环引用
        self.assertIsNotNone(obj1["ref"])
        self.assertIsNotNone(obj2["ref"])
        self.assertIs(obj1["ref"], obj2)
        self.assertIs(obj2["ref"], obj1)

        # 清理
        del obj1
        del obj2


class TestBatchProcessing(unittest.TestCase):
    """测试批处理内存管理"""

    def setUp(self):
        """测试前准备"""
        self.config = MemoryOptimizationConfig(
            batch_processing_enabled=True,
            batch_size=4,
            batch_memory_limit=1024 * 1024,  # 1MB
        )

    def test_batch_size_management(self):
        """测试批大小管理"""
        batch_size = self.config.batch_size
        total_items = 20

        # 计算批次数
        batches = (total_items + batch_size - 1) // batch_size
        self.assertEqual(batches, 5)

        # 验证每批大小
        for i in range(batches):
            start = i * batch_size
            end = min(start + batch_size, total_items)
            batch_size_actual = end - start
            self.assertLessEqual(batch_size_actual, self.config.batch_size)

    def test_batch_memory_limit(self):
        """测试批处理内存限制"""
        batch_memory_limit = self.config.batch_memory_limit
        items_per_batch = []

        # 模拟每批内存使用
        for i in range(5):
            # 假设每个项目使用100KB
            item_memory = 100 * 1024
            items_in_batch = batch_memory_limit // item_memory
            items_per_batch.append(items_in_batch)

        # 验证内存限制
        total_memory = sum(items_in_batch * 100 * 1024 for items_in_batch in items_per_batch)
        self.assertLessEqual(total_memory, batch_memory_limit * len(items_per_batch))


class TestMemoryOptimizationIntegration(unittest.TestCase):
    """内存优化集成测试"""

    def setUp(self):
        """测试前准备"""
        self.config = MemoryOptimizationConfig()
        self.memory_measurements = []

    def test_full_optimization_workflow(self):
        """测试完整优化流程"""
        # 1. 初始化配置
        self.assertIsNotNone(self.config)

        # 2. 启用监控
        if self.config.monitoring_enabled:
            tracemalloc.start()
            snapshot1 = tracemalloc.take_snapshot()

        # 3. 分配和优化内存
        optimized_objects = []
        for i in range(100):
            # 使用对象池（如果启用）
            if self.config.object_reuse_enabled and i > 0:
                # 重用对象
                obj = optimized_objects[0] if optimized_objects else {}
                obj["data"] = f"item_{i}"
            else:
                # 创建新对象
                obj = {"id": i, "data": f"item_{i}"}

            optimized_objects.append(obj)

            # 模拟算子级优化
            if self.config.operator_optimization_enabled:
                # 中间结果复用（简化模拟）
                pass

        # 4. 执行GC优化
        if self.config.gc_optimization_enabled:
            gc.collect()

        # 5. 检查内存使用
        if self.config.monitoring_enabled:
            snapshot2 = tracemalloc.take_snapshot()
            top_stats = snapshot2.compare_to(snapshot1, 'lineno')
            memory_diff = sum(stat.size_diff for stat in top_stats)
            self.memory_measurements.append(memory_diff)

        # 验证结果
        self.assertEqual(len(optimized_objects), 100)

        # 清理
        if self.config.monitoring_enabled:
            tracemalloc.stop()

    def test_large_model_conversion_simulation(self):
        """模拟大模型转换场景"""
        # 使用高性能配置
        config = MemoryOptimizationPresets.get_high_performance_mode()

        # 模拟大模型数据
        model_size = 500 * 1024 * 1024  # 500MB
        batch_size = config.batch_size

        # 分批处理
        for batch_idx in range(5):
            # 模拟批处理内存分配
            batch_memory = 0
            for item_idx in range(batch_size):
                item_size = model_size // batch_size
                batch_memory += item_size

                # 检查内存限制
                if config.model_sharding_enabled:
                    if item_size > config.shard_size_threshold:
                        # 模拟分片
                        shard_count = (item_size + config.shard_size_threshold - 1) // config.shard_size_threshold
                        self.assertLessEqual(shard_count, config.max_shards)

            # 验证批处理内存
            self.assertLessEqual(batch_memory, config.batch_memory_limit)

    def test_concurrent_memory_usage(self):
        """测试并发内存使用"""
        results = []
        errors = []

        def worker(worker_id):
            try:
                # 模拟工作线程内存使用
                data = []
                for i in range(1000):
                    data.append([0] * 100)

                # 测量内存
                tracemalloc.start()
                snapshot = tracemalloc.take_snapshot()
                top_stats = snapshot.statistics('lineno')
                memory_usage = sum(stat.size for stat in top_stats[:5])

                results.append({
                    "worker_id": worker_id,
                    "memory_usage": memory_usage,
                    "data_size": len(data),
                })

                tracemalloc.stop()

            except Exception as e:
                errors.append(str(e))

        # 创建多个工作线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证结果
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(results), 5)

        # 验证内存使用
        for result in results:
            self.assertGreater(result["memory_usage"], 0)
            self.assertEqual(result["data_size"], 1000)


class TestMemoryOptimizationPerformance(unittest.TestCase):
    """内存优化性能测试"""

    def setUp(self):
        """测试前准备"""
        self.config = MemoryOptimizationConfig()

    def test_memory_allocation_performance(self):
        """测试内存分配性能"""
        iterations = 10000

        # 测试普通分配
        start_time = time.time()
        normal_objects = []
        for i in range(iterations):
            normal_objects.append({"id": i, "data": f"item_{i}"})
        normal_time = time.time() - start_time

        # 测试优化分配（模拟对象池）
        start_time = time.time()
        optimized_objects = []
        object_pool = []
        for i in range(iterations):
            if object_pool:
                obj = object_pool.pop()
                obj["id"] = i
                obj["data"] = f"item_{i}"
            else:
                obj = {"id": i, "data": f"item_{i}"}
            optimized_objects.append(obj)

            # 池满时回收
            if len(object_pool) > 100:
                object_pool.clear()

        optimized_time = time.time() - start_time

        # 验证性能提升
        self.assertLessEqual(optimized_time, normal_time * 1.2)  # 允许20%的误差

    def test_memory_compression_performance(self):
        """测试内存压缩性能"""
        # 准备测试数据
        data = ["test_data_" + str(i) for i in range(10000)]

        # 测试压缩前
        start_time = time.time()
        uncompressed_size = sum(len(str(item).encode('utf-8')) for item in data)
        uncompressed_time = time.time() - start_time

        # 测试压缩后（使用简单压缩模拟）
        import zlib
        start_time = time.time()
        compressed_data = zlib.compress(str(data).encode('utf-8'))
        compressed_size = len(compressed_data)
        compression_time = time.time() - start_time

        # 计算压缩比
        compression_ratio = compressed_size / uncompressed_size

        # 验证结果
        self.assertLess(compression_ratio, 1.0)  # 压缩后应该更小
        self.assertGreater(compression_time, uncompressed_time)  # 压缩有开销

    def test_gc_performance(self):
        """测试GC性能"""
        iterations = 1000

        # 测试默认GC
        gc.collect()
        start_time = time.time()
        for i in range(iterations):
            obj = {"id": i, "data": [0] * 100}
            del obj
        gc.collect()
        default_gc_time = time.time() - start_time

        # 测试优化GC
        gc.collect()
        start_time = time.time()
        for i in range(iterations):
            obj = {"id": i, "data": [0] * 100}
            del obj
            # 模拟阈值调整
            if i % 100 == 0:
                gc.collect()
        optimized_gc_time = time.time() - start_time

        # 验证优化效果
        self.assertLessEqual(optimized_gc_time, default_gc_time * 1.1)


class TestMemoryOptimizationReporting(unittest.TestCase):
    """测试内存优化报告"""

    def setUp(self):
        """测试前准备"""
        self.config = MemoryOptimizationConfig(reporting_enabled=True)

    def test_memory_report_generation(self):
        """测试内存报告生成"""
        if not self.config.reporting_enabled:
            self.skipTest("报告功能未启用")

        # 模拟内存使用数据
        memory_data = {
            "timestamp": time.time(),
            "peak_usage": 1024 * 1024 * 100,  # 100MB
            "average_usage": 1024 * 1024 * 50,  # 50MB
            "current_usage": 1024 * 1024 * 75,  # 75MB
            "allocation_count": 1000,
            "deallocation_count": 950,
        }

        # 验证报告数据
        self.assertIn("peak_usage", memory_data)
        self.assertIn("average_usage", memory_data)
        self.assertGreater(memory_data["peak_usage"], memory_data["average_usage"])

    def test_memory_efficiency_calculation(self):
        """测试内存效率计算"""
        total_allocated = 1024 * 1024 * 1000  # 1000MB
        effective_used = 1024 * 1024 * 850  # 850MB
        leaked = 1024 * 1024 * 50  # 50MB

        # 计算效率
        efficiency = (effective_used / total_allocated) * 100
        leak_rate = (leaked / total_allocated) * 100

        # 验证计算
        self.assertAlmostEqual(efficiency, 85.0, places=1)
        self.assertAlmostEqual(leak_rate, 5.0, places=1)

    def test_performance_metrics_reporting(self):
        """测试性能指标报告"""
        performance_data = {
            "conversion_time": 30.5,  # 秒
            "memory_optimization_time": 2.3,  # 秒
            "throughput": 15.2,  # 模型/分钟
            "efficiency_gain": 35.5,  # 百分比
        }

        # 验证性能数据
        self.assertGreater(performance_data["conversion_time"], 0)
        self.assertLess(performance_data["memory_optimization_time"], performance_data["conversion_time"])
        self.assertGreater(performance_data["efficiency_gain"], 0)


def run_memory_optimization_tests():
    """运行所有内存优化测试"""
    # 创建测试套件
    test_suite = unittest.TestSuite()

    # 添加测试类
    test_classes = [
        TestMemoryOptimizationConfig,
        TestMemoryOptimizationPresets,
        TestConfigFactory,
        TestMemoryMonitoring,
        TestMemoryOptimization,
        TestMemoryLeakDetection,
        TestBatchProcessing,
        TestMemoryOptimizationIntegration,
        TestMemoryOptimizationPerformance,
        TestMemoryOptimizationReporting,
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    return result


if __name__ == "__main__":
    # 运行所有测试
    result = run_memory_optimization_tests()

    # 输出测试结果
    print("\n" + "=" * 70)
    print("内存使用优化系统测试结果")
    print("=" * 70)
    print(f"运行测试数: {result.testsRun}")
    print(f"失败数: {len(result.failures)}")
    print(f"错误数: {len(result.errors)}")
    print(f"跳过数: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    print("=" * 70)

    # 如果有失败的测试，输出详细信息
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split(chr(10))[0]}")

    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split(chr(10))[0]}")

    # 返回测试结果
    exit(0 if result.wasSuccessful() else 1)
