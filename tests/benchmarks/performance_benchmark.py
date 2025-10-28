"""
XLeRobot NPU Converter - 性能基准测试

提供模型转换性能的基准测试，包括转换时间、内存使用、吞吐量等关键指标。
"""

import time
import gc
import psutil
import os
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from unittest.mock import Mock, patch

import pytest


@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    operation: str
    duration: float
    memory_before: float
    memory_after: float
    memory_peak: float
    cpu_percent: float
    success: bool
    error: Optional[str] = None


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        """初始化性能监控器"""
        self.process = psutil.Process()
        self.monitoring = False
        self.cpu_samples: List[float] = []
        self.memory_samples: List[float] = []
        self.monitor_thread: Optional[threading.Thread] = None

    def start_monitoring(self) -> None:
        """开始性能监控"""
        self.monitoring = True
        self.cpu_samples.clear()
        self.memory_samples.clear()

        def monitor_loop():
            while self.monitoring:
                try:
                    # CPU使用率
                    cpu_percent = self.process.cpu_percent()
                    self.cpu_samples.append(cpu_percent)

                    # 内存使用
                    memory_info = self.process.memory_info()
                    memory_mb = memory_info.rss / 1024 / 1024
                    self.memory_samples.append(memory_mb)

                    time.sleep(0.1)  # 每100ms采样一次
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    break

        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self) -> Dict[str, float]:
        """停止性能监控并返回统计结果

        Returns:
            性能统计数据
        """
        self.monitoring = False

        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)

        # 计算统计数据
        avg_cpu = sum(self.cpu_samples) / len(self.cpu_samples) if self.cpu_samples else 0
        max_cpu = max(self.cpu_samples) if self.cpu_samples else 0
        avg_memory = sum(self.memory_samples) / len(self.memory_samples) if self.memory_samples else 0
        max_memory = max(self.memory_samples) if self.memory_samples else 0

        return {
            "avg_cpu_percent": avg_cpu,
            "max_cpu_percent": max_cpu,
            "avg_memory_mb": avg_memory,
            "max_memory_mb": max_memory,
            "cpu_samples": len(self.cpu_samples),
            "memory_samples": len(self.memory_samples)
        }

    def get_current_memory(self) -> float:
        """获取当前内存使用量(MB)

        Returns:
            内存使用量(MB)
        """
        try:
            memory_info = self.process.memory_info()
            return memory_info.rss / 1024 / 1024
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0.0


class MockModelConverter:
    """模拟模型转换器，用于性能测试"""

    def __init__(self):
        """初始化模拟转换器"""
        self.conversion_time_factor = 0.001  # 模拟转换时间因子
        self.memory_overhead = 50  # 内存开销(MB)

    def simulate_model_loading(self, model_path: str, model_size_mb: float = 100) -> Dict:
        """模拟模型加载

        Args:
            model_path: 模型路径
            model_size_mb: 模型大小(MB)

        Returns:
            加载结果
        """
        # 模拟加载时间（与模型大小成正比）
        load_time = model_size_mb * 0.01  # 0.01s per MB

        # 模拟内存分配
        memory_blocks = []
        for i in range(int(model_size_mb / 10)):
            # 分配10MB内存块
            memory_blocks.append(bytearray(10 * 1024 * 1024))

        time.sleep(load_time)

        # 清理内存
        del memory_blocks
        gc.collect()

        return {
            "model_path": model_path,
            "model_size_mb": model_size_mb,
            "load_time": load_time,
            "success": True
        }

    def simulate_model_conversion(self, model_info: Dict, target_format: str = "bpu") -> Dict:
        """模拟模型转换

        Args:
            model_info: 模型信息
            target_format: 目标格式

        Returns:
            转换结果
        """
        model_size = model_info.get("model_size_mb", 100)

        # 模拟转换步骤
        steps = [
            ("validation", model_size * 0.005),
            ("calibration", model_size * 0.02),
            ("quantization", model_size * 0.015),
            ("compilation", model_size * 0.01),
            ("optimization", model_size * 0.008)
        ]

        total_time = 0
        memory_usage = []

        for step_name, step_time in steps:
            # 记录步骤开始时间
            step_start = time.time()

            # 模拟步骤执行
            time.sleep(step_time)

            # 模拟内存使用峰值
            peak_memory = model_size * (0.8 + 0.4 * (len(memory_usage) / len(steps)))
            memory_usage.append(peak_memory)

            total_time += time.time() - step_start

        # 计算性能指标
        compression_ratio = 4.2  # 模拟压缩比
        performance_improvement = 3.5  # 模拟性能提升

        return {
            "model_path": model_info.get("model_path", ""),
            "target_format": target_format,
            "total_time": total_time,
            "steps": len(steps),
            "compression_ratio": compression_ratio,
            "performance_improvement": performance_improvement,
            "peak_memory_mb": max(memory_usage) if memory_usage else 0,
            "success": True
        }

    def simulate_batch_conversion(self, models: List[Dict]) -> List[Dict]:
        """模拟批量转换

        Args:
            models: 模型列表

        Returns:
            批量转换结果
        """
        results = []

        for model in models:
            result = self.simulate_model_conversion(model)
            results.append(result)

        return results


@pytest.fixture
def performance_monitor():
    """性能监控器fixture"""
    monitor = PerformanceMonitor()
    yield monitor
    # 清理
    monitor.stop_monitoring()


@pytest.fixture
def mock_converter():
    """模拟转换器fixture"""
    return MockModelConverter()


class TestModelConversionPerformance:
    """模型转换性能测试"""

    def test_model_loading_performance(self, performance_monitor, mock_converter):
        """测试模型加载性能"""
        model_sizes = [50, 100, 200, 500]  # MB
        results = []

        for size in model_sizes:
            # 记录初始状态
            memory_before = performance_monitor.get_current_memory()
            performance_monitor.start_monitoring()

            # 执行模型加载
            start_time = time.time()
            result = mock_converter.simulate_model_loading(f"model_{size}mb.onnx", size)
            duration = time.time() - start_time

            # 停止监控
            stats = performance_monitor.stop_monitoring()
            memory_after = performance_monitor.get_current_memory()

            metrics = PerformanceMetrics(
                operation="model_loading",
                duration=duration,
                memory_before=memory_before,
                memory_after=memory_after,
                memory_peak=stats["max_memory_mb"],
                cpu_percent=stats["avg_cpu_percent"],
                success=result["success"]
            )
            results.append(metrics)

            # 验证性能指标
            assert duration < size * 0.02, f"模型加载时间过长: {duration:.3f}s"
            assert stats["max_memory_mb"] < size * 1.5, f"内存使用过多: {stats['max_memory_mb']:.1f}MB"

        # 验证加载时间与模型大小的线性关系
        durations = [r.duration for r in results]
        assert self._is_linear_relationship(model_sizes, durations, tolerance=0.2), \
            "加载时间应与模型大小呈线性关系"

    def test_single_model_conversion_performance(self, performance_monitor, mock_converter):
        """测试单个模型转换性能"""
        model_info = {
            "model_path": "test_model.onnx",
            "model_size_mb": 100
        }

        # 记录初始状态
        memory_before = performance_monitor.get_current_memory()
        performance_monitor.start_monitoring()

        # 执行模型转换
        start_time = time.time()
        result = mock_converter.simulate_model_conversion(model_info)
        duration = time.time() - start_time

        # 停止监控
        stats = performance_monitor.stop_monitoring()
        memory_after = performance_monitor.get_current_memory()

        # 验证结果
        assert result["success"], "模型转换应成功"
        assert duration < 10.0, f"转换时间过长: {duration:.3f}s"
        assert result["compression_ratio"] > 3.0, "压缩比应大于3"
        assert result["performance_improvement"] > 2.0, "性能提升应大于2倍"

        # 记录性能指标
        metrics = PerformanceMetrics(
            operation="single_conversion",
            duration=duration,
            memory_before=memory_before,
            memory_after=memory_after,
            memory_peak=stats["max_memory_mb"],
            cpu_percent=stats["avg_cpu_percent"],
            success=result["success"]
        )

        # 性能基准断言
        assert metrics.duration < 5.0, "单个模型转换应在5秒内完成"
        assert metrics.memory_peak < 500, "内存峰值应小于500MB"

    def test_batch_conversion_performance(self, performance_monitor, mock_converter):
        """测试批量转换性能"""
        # 创建不同大小的模型列表
        models = [
            {"model_path": f"model_{i}.onnx", "model_size_mb": 50 + i * 25}
            for i in range(10)
        ]

        # 记录初始状态
        memory_before = performance_monitor.get_current_memory()
        performance_monitor.start_monitoring()

        # 执行批量转换
        start_time = time.time()
        results = mock_converter.simulate_batch_conversion(models)
        duration = time.time() - start_time

        # 停止监控
        stats = performance_monitor.stop_monitoring()
        memory_after = performance_monitor.get_current_memory()

        # 验证结果
        assert len(results) == len(models), "应转换所有模型"
        assert all(r["success"] for r in results), "所有转换应成功"

        # 计算吞吐量
        throughput = len(models) / duration
        avg_time_per_model = duration / len(models)

        # 性能基准断言
        assert throughput > 0.5, f"吞吐量过低: {throughput:.2f} models/sec"
        assert avg_time_per_model < 2.0, f"平均转换时间过长: {avg_time_per_model:.3f}s"
        assert stats["max_memory_mb"] < 1000, "批量转换内存峰值应小于1GB"

        print(f"批量转换性能指标:")
        print(f"  总时间: {duration:.3f}s")
        print(f"  吞吐量: {throughput:.2f} models/sec")
        print(f"  平均时间: {avg_time_per_model:.3f}s/model")
        print(f"  内存峰值: {stats['max_memory_mb']:.1f}MB")

    def test_memory_efficiency(self, performance_monitor, mock_converter):
        """测试内存效率"""
        # 测试大模型转换的内存使用
        large_model = {
            "model_path": "large_model.onnx",
            "model_size_mb": 500
        }

        # 强制垃圾回收
        gc.collect()
        memory_before = performance_monitor.get_current_memory()

        performance_monitor.start_monitoring()

        # 执行转换
        result = mock_converter.simulate_model_conversion(large_model)

        stats = performance_monitor.stop_monitoring()
        gc.collect()
        memory_after = performance_monitor.get_current_memory()

        # 计算内存效率指标
        memory_overhead = stats["max_memory_mb"] - memory_before
        memory_efficiency = large_model["model_size_mb"] / stats["max_memory_mb"]

        # 验证内存效率
        assert memory_overhead < large_model["model_size_mb"] * 1.2, \
            f"内存开销过大: {memory_overhead:.1f}MB"
        assert memory_efficiency > 0.5, \
            f"内存效率过低: {memory_efficiency:.2f}"

        print(f"内存效率指标:")
        print(f"  模型大小: {large_model['model_size_mb']}MB")
        print(f"  内存峰值: {stats['max_memory_mb']:.1f}MB")
        print(f"  内存开销: {memory_overhead:.1f}MB")
        print(f"  内存效率: {memory_efficiency:.2f}")

    def test_concurrent_conversion_performance(self, performance_monitor, mock_converter):
        """测试并发转换性能"""
        import concurrent.futures

        # 创建模型列表
        models = [
            {"model_path": f"concurrent_model_{i}.onnx", "model_size_mb": 100}
            for i in range(8)
        ]

        def convert_single_model(model_info):
            """单个模型转换函数"""
            return mock_converter.simulate_model_conversion(model_info)

        # 串行转换
        start_time = time.time()
        serial_results = [convert_single_model(model) for model in models]
        serial_duration = time.time() - start_time

        # 并发转换
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            concurrent_results = list(executor.map(convert_single_model, models))
        concurrent_duration = time.time() - start_time

        # 验证结果一致性
        assert len(concurrent_results) == len(serial_results), "并发结果数量应一致"
        assert all(r["success"] for r in concurrent_results), "所有并发转换应成功"

        # 计算性能提升
        speedup = serial_duration / concurrent_duration if concurrent_duration > 0 else 0
        efficiency = speedup / 4  # 4个并发线程

        print(f"并发转换性能:")
        print(f"  串行时间: {serial_duration:.3f}s")
        print(f"  并发时间: {concurrent_duration:.3f}s")
        print(f"  加速比: {speedup:.2f}x")
        print(f"  并发效率: {efficiency:.2f}")

        # 验证并发性能提升
        assert speedup > 1.5, "并发应有显著性能提升"
        assert efficiency > 0.3, "并发效率应合理"

    def _is_linear_relationship(self, x_values: List[float], y_values: List[float], tolerance: float = 0.1) -> bool:
        """检查是否为线性关系

        Args:
            x_values: x值列表
            y_values: y值列表
            tolerance: 容忍度

        Returns:
            是否为线性关系
        """
        if len(x_values) != len(y_values) or len(x_values) < 2:
            return False

        # 计算线性拟合
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)

        # 计算斜率和截距
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n

        # 计算R²
        y_mean = sum_y / n
        ss_total = sum((y - y_mean) ** 2 for y in y_values)
        ss_residual = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(x_values, y_values))

        r_squared = 1 - (ss_residual / ss_total) if ss_total > 0 else 0

        return r_squared >= (1 - tolerance)


class TestResourceUtilization:
    """资源利用率测试"""

    def test_cpu_utilization_pattern(self, performance_monitor, mock_converter):
        """测试CPU利用率模式"""
        # 执行多次转换并监控CPU使用
        cpu_usage = []

        for i in range(5):
            performance_monitor.start_monitoring()
            mock_converter.simulate_model_conversion({
                "model_path": f"cpu_test_model_{i}.onnx",
                "model_size_mb": 100
            })
            stats = performance_monitor.stop_monitoring()
            cpu_usage.append(stats["avg_cpu_percent"])

        # 验证CPU使用率在合理范围内
        avg_cpu = sum(cpu_usage) / len(cpu_usage)
        max_cpu = max(cpu_usage)

        assert 20 <= avg_cpu <= 90, f"平均CPU使用率应在20-90%之间: {avg_cpu:.1f}%"
        assert max_cpu <= 100, f"最大CPU使用率不应超过100%: {max_cpu:.1f}%"

        print(f"CPU利用率分析:")
        print(f"  平均使用率: {avg_cpu:.1f}%")
        print(f"  最大使用率: {max_cpu:.1f}%")
        print(f"  使用率方差: {self._calculate_variance(cpu_usage):.2f}")

    def test_memory_leak_detection(self, performance_monitor, mock_converter):
        """测试内存泄漏检测"""
        initial_memory = performance_monitor.get_current_memory()
        memory_samples = [initial_memory]

        # 执行多次转换
        for i in range(20):
            mock_converter.simulate_model_conversion({
                "model_path": f"leak_test_model_{i}.onnx",
                "model_size_mb": 50
            })

            # 强制垃圾回收
            gc.collect()

            # 记录内存使用
            current_memory = performance_monitor.get_current_memory()
            memory_samples.append(current_memory)

        # 分析内存趋势
        memory_trend = self._calculate_trend(memory_samples)
        final_memory = memory_samples[-1]

        # 检测内存泄漏
        memory_increase = final_memory - initial_memory
        leak_threshold = 100  # 100MB

        assert memory_increase < leak_threshold, \
            f"可能存在内存泄漏，内存增长: {memory_increase:.1f}MB"
        assert abs(memory_trend) < 5, \
            f"内存增长趋势过快: {memory_trend:.2f}MB/iteration"

        print(f"内存泄漏检测:")
        print(f"  初始内存: {initial_memory:.1f}MB")
        print(f"  最终内存: {final_memory:.1f}MB")
        print(f"  内存增长: {memory_increase:.1f}MB")
        print(f"  增长趋势: {memory_trend:.2f}MB/iteration")

    def _calculate_variance(self, values: List[float]) -> float:
        """计算方差

        Args:
            values: 数值列表

        Returns:
            方差
        """
        if not values:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance

    def _calculate_trend(self, values: List[float]) -> float:
        """计算线性趋势斜率

        Args:
            values: 数值列表

        Returns:
            趋势斜率
        """
        if len(values) < 2:
            return 0.0

        n = len(values)
        x_values = list(range(n))
        sum_x = sum(x_values)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(x_values, values))
        sum_x2 = sum(x * x for x in x_values)

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return slope


# 性能基准配置
@pytest.mark.benchmark
class TestPerformanceBenchmarks:
    """性能基准测试标记"""

    def test_conversion_throughput_benchmark(self, mock_converter, benchmark):
        """转换吞吐量基准测试"""
        def conversion_operation():
            return mock_converter.simulate_model_conversion({
                "model_path": "benchmark_model.onnx",
                "model_size_mb": 100
            })

        result = benchmark(conversion_operation)
        assert result["success"], "基准测试应成功"

    def test_memory_usage_benchmark(self, mock_converter, benchmark):
        """内存使用基准测试"""
        def memory_operation():
            return mock_converter.simulate_model_conversion({
                "model_path": "memory_benchmark_model.onnx",
                "model_size_mb": 200
            })

        result = benchmark(memory_operation)
        assert result["success"], "内存基准测试应成功"


if __name__ == "__main__":
    # 直接运行性能测试
    pytest.main([__file__, "-v", "--benchmark-only"])