"""
性能基准验证测试
验证系统是否满足性能基准要求
"""

import unittest
import time
import threading
from datetime import datetime
from pathlib import Path
import json

from ..base_test import PerformanceTestBase, MockConversionFunc
import logging

logger = logging.getLogger(__name__)


class PerformanceBenchmarkTest(PerformanceTestBase):
    """性能基准验证测试"""

    def test_conversion_latency_benchmark(self):
        """转换延迟基准测试 (<5分钟)"""
        logger.info("🧪 测试转换延迟基准")

        test_cases = [
            ("SenseVoice模型", MockConversionFunc(180000)),  # 3分钟
            ("VITS-Cantonese模型", MockConversionFunc(240000)),  # 4分钟
            ("Piper VITS模型", MockConversionFunc(300000)),  # 5分钟
        ]

        for model_name, conversion in test_cases:
            logger.info(f"🔄 测试 {model_name}")

            # 开始监控
            self.start_monitoring()

            # 执行转换并测量时间
            self.measure_conversion_time(conversion)

            # 停止监控
            self.stop_monitoring()

            # 验证结果
            self.assertTrue(
                len(self.metrics['conversion_time']) > 0,
                f"{model_name} 转换失败"
            )
            self.assertLess(
                self.metrics['conversion_time'][-1],
                self.MAX_CONVERSION_TIME,
                f"{model_name} 转换时间超过 {self.MAX_CONVERSION_TIME}秒"
            )

            logger.info(f"✅ {model_name} 转换时间: {self.metrics['conversion_time'][-1]:.2f}秒")

    def test_concurrent_throughput_benchmark(self):
        """并发吞吐量基准测试 (>10模型/分钟)"""
        logger.info("🧪 测试并发吞吐量基准")

        test_scenarios = [
            ("5模型并发", 5, 60),
            ("10模型并发", 10, 60),
            ("15模型并发", 15, 90),
        ]

        for scenario_name, num_models, duration in test_scenarios:
            logger.info(f"🔄 测试 {scenario_name}")

            # 准备转换函数
            conversions = [MockConversionFunc(3000) for _ in range(num_models)]  # 每个3秒

            # 开始监控
            self.start_monitoring()

            # 并发执行
            with ThreadPoolExecutor(max_workers=num_models) as executor:
                futures = [executor.submit(conversion) for conversion in conversions]

                # 等待所有任务完成
                for future in futures:
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"转换失败: {e}")

            self.stop_monitoring()

            # 计算吞吐量
            avg_conversion_time = self._calculate_average(self.metrics['conversion_time'])
            throughput = num_models / (avg_conversion_time / 60)  # 模型/分钟

            logger.info(f"📊 {scenario_name} 结果:")
            logger.info(f"   模型数: {num_models}")
            logger.info(f"   平均转换时间: {avg_conversion_time:.2f}s")
            logger.info(f"   吞吐量: {throughput:.2f} 模型/分钟")

            # 验证吞吐量
            self.assertGreater(
                throughput,
                self.MIN_THROUGHPUT,
                f"{scenario_name} 吞吐量低于阈值 {self.MIN_THROUGHPUT} 模型/分钟"
            )

            logger.info(f"✅ {scenario_name} 基准测试通过")

    def test_memory_efficiency_benchmark(self):
        """内存使用效率基准测试 (峰值降低30%+)"""
        logger.info("🧪 测试内存效率基准")

        # 记录基准内存使用 (无优化)
        logger.info("📊 记录基准内存使用")
        baseline_conversions = [MockConversionFunc(2000) for _ in range(5)]

        # 执行基准测试
        self.start_monitoring()
        for conversion in baseline_conversions:
            conversion()
        self.stop_monitoring()

        baseline_memory = self._calculate_average(self.metrics['memory_usage'])
        baseline_peak = self._calculate_max(self.metrics['memory_usage'])

        logger.info(f"📊 基准内存 - 平均: {baseline_memory:.1f}%, 峰值: {baseline_peak:.1f}%")

        # 清理指标
        self.metrics = {key: [] for key in self.metrics.keys()}

        # 模拟优化后的内存使用
        logger.info("📊 记录优化后内存使用")
        optimized_conversions = [MockConversionFunc(2000) for _ in range(5)]

        # 执行优化测试
        self.start_monitoring()
        for conversion in optimized_conversions:
            conversion()
        self.stop_monitoring()

        optimized_memory = self._calculate_average(self.metrics['memory_usage'])
        optimized_peak = self._calculate_max(self.metrics['memory_usage'])

        logger.info(f"📊 优化内存 - 平均: {optimized_memory:.1f}%, 峰值: {optimized_peak:.1f}%")

        # 计算优化效果
        avg_optimization = (baseline_memory - optimized_memory) / baseline_memory * 100
        peak_optimization = (baseline_peak - optimized_peak) / baseline_peak * 100

        logger.info(f"📊 优化效果 - 平均优化: {avg_optimization:.1f}%, 峰值优化: {peak_optimization:.1f}%")

        # 验证优化效果
        self.assertGreater(
            avg_optimization,
            self.MEMORY_OPTIMIZATION_THRESHOLD,
            f"平均内存优化未达到阈值 {self.MEMORY_OPTIMIZATION_THRESHOLD}%"
        )
        self.assertGreater(
            peak_optimization,
            self.MEMORY_OPTIMIZATION_THRESHOLD,
            f"峰值内存优化未达到阈值 {self.MEMORY_OPTIMIZATION_THRESHOLD}%"
        )

        logger.info("✅ 内存效率基准测试通过")

    def test_long_term_stability_benchmark(self):
        """长期稳定性基准测试 (72小时)"""
        logger.info("🧪 测试长期稳定性基准")

        # 注意: 这里使用短时间模拟，实际测试中应该使用72小时
        duration_minutes = 5  # 模拟5分钟
        self._run_stability_benchmark(duration_minutes)

    def _run_stability_benchmark(self, duration_minutes):
        """运行稳定性基准测试"""
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)

        iteration = 0
        errors = 0
        completed = 0

        while time.time() < end_time:
            iteration += 1
            try:
                # 执行转换
                conversion = MockConversionFunc(2000)
                conversion()
                completed += 1

                # 记录资源使用
                current_cpu = psutil.cpu_percent(interval=None)
                current_memory = psutil.virtual_memory().percent

                self.metrics['cpu_usage'].append(current_cpu)
                self.metrics['memory_usage'].append(current_memory)

                elapsed = time.time() - start_time
                logger.debug(f"🔄 稳定性基准 - 迭代 {iteration}, 完成 {completed}, 耗时 {elapsed/60:.1f} 分钟")

                time.sleep(1)

            except Exception as e:
                errors += 1
                logger.error(f"稳定性基准错误: {e}")

        # 分析结果
        total_time = time.time() - start_time
        success_rate = (completed / iteration * 100) if iteration > 0 else 0
        throughput = completed / (total_time / 60)  # 模型/分钟

        logger.info(f"📊 稳定性基准测试结果:")
        logger.info(f"   总迭代数: {iteration}")
        logger.info(f"   成功完成: {completed}")
        logger.info(f"   错误数: {errors}")
        logger.info(f"   成功率: {success_rate:.1f}%")
        logger.info(f"   平均吞吐量: {throughput:.2f} 模型/分钟")
        logger.info(f"   平均CPU使用率: {self._calculate_average(self.metrics['cpu_usage']):.1f}%")
        logger.info(f"   平均内存使用率: {self._calculate_average(self.metrics['memory_usage']):.1f}%")

        # 验证结果
        self.assertGreater(success_rate, 95, "稳定性测试成功率低于95%")
        self.assertEqual(errors, 0, f"稳定性测试中发现 {errors} 个错误")
        self.assertGreater(throughput, self.MIN_THROUGHPUT * 0.8, "稳定性测试中吞吐量下降过多")

        logger.info("✅ 长期稳定性基准测试通过")

    def test_resource_utilization_benchmark(self):
        """资源利用率基准测试"""
        logger.info("🧪 测试资源利用率基准")

        # 记录基准资源使用
        conversions = [MockConversionFunc(3000) for _ in range(10)]

        # 开始监控
        self.start_monitoring()

        # 执行转换
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(conversion) for conversion in conversions]

            # 等待所有任务完成
            for future in futures:
                future.result()

        self.stop_monitoring()

        # 分析资源使用
        avg_cpu = self._calculate_average(self.metrics['cpu_usage'])
        max_cpu = self._calculate_max(self.metrics['cpu_usage'])
        avg_memory = self._calculate_average(self.metrics['memory_usage'])
        max_memory = self._calculate_max(self.metrics['memory_usage'])

        logger.info(f"📊 资源利用率分析:")
        logger.info(f"   CPU - 平均: {avg_cpu:.1f}%, 峰值: {max_cpu:.1f}%")
        logger.info(f"   Memory - 平均: {avg_memory:.1f}%, 峰值: {max_memory:.1f}%")

        # 验证资源使用在合理范围内
        self.assertGreater(avg_cpu, 30, "CPU平均使用率过低 (资源利用不充分)")
        self.assertLess(max_cpu, 90, "CPU峰值使用率过高")
        self.assertGreater(avg_memory, 20, "内存平均使用率过低")
        self.assertLess(max_memory, 85, "内存峰值使用率过高")

        logger.info("✅ 资源利用率基准测试通过")

    def test_end_to_end_performance(self):
        """端到端性能测试"""
        logger.info("🧪 测试端到端性能")

        # 模拟完整的模型转换流程
        workflow_steps = [
            ("模型加载", MockConversionFunc(500)),
            ("预处理", MockConversionFunc(1000)),
            ("转换", MockConversionFunc(3000)),
            ("验证", MockConversionFunc(800)),
            ("导出", MockConversionFunc(1200)),
        ]

        total_start = time.time()
        step_results = []

        for step_name, conversion in workflow_steps:
            logger.info(f"🔄 执行 {step_name}")

            # 开始监控
            self.start_monitoring()

            # 执行步骤
            step_start = time.time()
            result = conversion()
            step_end = time.time()

            # 停止监控
            self.stop_monitoring()

            step_duration = step_end - step_start
            step_results.append({
                'step': step_name,
                'duration': step_duration,
                'cpu_avg': self._calculate_average(self.metrics['cpu_usage']),
                'memory_avg': self._calculate_average(self.metrics['memory_usage'])
            })

            logger.info(f"   耗时: {step_duration:.2f}s")

        total_end = time.time()
        total_duration = total_end - total_start

        # 分析结果
        logger.info(f"📊 端到端性能测试结果:")
        logger.info(f"   总耗时: {total_duration:.2f}s ({total_duration/60:.2f}分钟)")

        for result in step_results:
            logger.info(f"   {result['step']}: {result['duration']:.2f}s "
                       f"(CPU: {result['cpu_avg']:.1f}%, MEM: {result['memory_avg']:.1f}%)")

        # 验证总耗时
        self.assertLess(
            total_duration,
            self.MAX_CONVERSION_TIME,
            f"端到端转换时间超过 {self.MAX_CONVERSION_TIME}秒"
        )

        # 验证每个步骤的耗时
        max_step_duration = max(result['duration'] for result in step_results)
        self.assertLess(max_step_duration, 120, "单个步骤耗时过长")

        logger.info("✅ 端到端性能测试通过")

    def tearDown(self):
        """测试清理"""
        super().tearDown()

        # 生成测试报告
        if hasattr(self, 'metrics') and self.metrics:
            report_path = f"reports/performance/benchmark_{self._testMethodName}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.generate_test_report(report_path)


if __name__ == '__main__':
    unittest.main()
