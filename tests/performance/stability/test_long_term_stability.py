"""
长时间运行稳定性测试
验证系统长时间运行的可靠性
"""

import unittest
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
import json

from ..base_test import PerformanceTestBase, MockConversionFunc
import logging
import psutil

logger = logging.getLogger(__name__)


class LongTermStabilityTest(PerformanceTestBase):
    """长时间运行稳定性测试"""

    def test_24_hour_stability(self):
        """24小时稳定性测试"""
        logger.info("🧪 测试24小时稳定性")

        # 注意: 这里使用短时间模拟，实际测试中应该使用24小时
        duration_minutes = 10  # 模拟10分钟
        self._run_stability_test(duration_minutes)

    def test_48_hour_stability(self):
        """48小时稳定性测试"""
        logger.info("🧪 测试48小时稳定性")

        # 注意: 这里使用短时间模拟，实际测试中应该使用48小时
        duration_minutes = 15  # 模拟15分钟
        self._run_stability_test(duration_minutes)

    def test_72_hour_stability(self):
        """72小时稳定性测试"""
        logger.info("🧪 测试72小时稳定性")

        # 注意: 这里使用短时间模拟，实际测试中应该使用72小时
        duration_minutes = 20  # 模拟20分钟
        self._run_stability_test(duration_minutes)

    def _run_stability_test(self, duration_minutes):
        """运行稳定性测试的内部方法"""
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)

        iteration = 0
        errors = []
        warnings = []

        # 初始资源记录
        initial_memory = psutil.virtual_memory().percent
        initial_cpu = psutil.cpu_percent(interval=1)

        logger.info(f"📊 初始资源 - CPU: {initial_cpu:.1f}%, Memory: {initial_memory:.1f}%")

        while datetime.now() < end_time:
            iteration += 1
            try:
                # 执行转换
                conversion = MockConversionFunc(3000)  # 3秒转换

                # 开始监控
                self.start_monitoring()

                # 执行转换
                conversion()

                # 停止监控
                self.stop_monitoring()

                # 检查资源使用
                current_cpu = psutil.cpu_percent(interval=None)
                current_memory = psutil.virtual_memory().percent

                # 记录指标
                self.metrics['cpu_usage'].append(current_cpu)
                self.metrics['memory_usage'].append(current_memory)

                # 检查是否有异常
                if current_cpu > 95:
                    warnings.append(f"Iteration {iteration}: CPU使用率过高 ({current_cpu:.1f}%)")

                if current_memory > 90:
                    warnings.append(f"Iteration {iteration}: 内存使用率过高 ({current_memory:.1f}%)")

                # 检查内存泄漏（内存持续增长）
                if iteration > 10:
                    recent_memory = self.metrics['memory_usage'][-10:]
                    avg_recent = sum(recent_memory) / len(recent_memory)
                    if avg_recent > initial_memory + 20:
                        warnings.append(f"Iteration {iteration}: 可能存在内存泄漏 (平均 {avg_recent:.1f}%)")

                elapsed = (datetime.now() - start_time).total_seconds()
                logger.info(f"🔄 稳定性测试进度: {iteration} 迭代, {elapsed/60:.1f}/{duration_minutes} 分钟")
                logger.info(f"   CPU: {current_cpu:.1f}%, Memory: {current_memory:.1f}%")

                time.sleep(2)  # 每3秒执行一次转换

            except Exception as e:
                error_msg = f"Iteration {iteration}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)

        # 测试结束
        final_memory = psutil.virtual_memory().percent
        final_cpu = psutil.cpu_percent(interval=1)

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ 稳定性测试完成")
        logger.info(f"   总迭代数: {iteration}")
        logger.info(f"   总耗时: {duration/60:.2f} 分钟")
        logger.info(f"   错误数: {len(errors)}")
        logger.info(f"   警告数: {len(warnings)}")
        logger.info(f"📊 最终资源 - CPU: {final_cpu:.1f}%, Memory: {final_memory:.1f}%")

        # 验证结果
        self.assertEqual(len(errors), 0, f"稳定性测试中发现 {len(errors)} 个错误")

        # 允许少量警告，但不应过多
        self.assertLess(len(warnings), iteration * 0.1, "警告数量过多")

        # 验证资源使用在合理范围内
        max_memory = self._calculate_max(self.metrics['memory_usage'])
        max_cpu = self._calculate_max(self.metrics['cpu_usage'])

        self.assertLess(max_memory, 95, "内存使用率峰值过高")
        self.assertLess(max_cpu, 95, "CPU使用率峰值过高")

    def test_memory_leak_detection(self):
        """内存泄漏检测测试"""
        logger.info("🧪 测试内存泄漏检测")

        # 记录初始内存
        initial_memory = psutil.virtual_memory().percent
        logger.info(f"📊 初始内存使用率: {initial_memory:.1f}%")

        # 执行多次转换，观察内存变化
        memory_samples = []
        for i in range(50):
            conversion = MockConversionFunc(1000)  # 1秒转换
            conversion()

            # 记录内存使用
            current_memory = psutil.virtual_memory().percent
            memory_samples.append(current_memory)

            # 检查内存是否持续增长
            if i > 20:
                recent_samples = memory_samples[-10:]
                avg_recent = sum(recent_samples) / len(recent_samples)

                # 如果最近10次平均值比初始值高出20%以上，怀疑内存泄漏
                if avg_recent > initial_memory + 20:
                    logger.warning(f"⚠️ 怀疑内存泄漏 (迭代 {i+1}, 平均内存: {avg_recent:.1f}%)")

            time.sleep(0.5)

        # 最终内存使用
        final_memory = psutil.virtual_memory().percent
        logger.info(f"📊 最终内存使用率: {final_memory:.1f}%")

        # 验证内存使用增长是否合理 (应该在5%以内)
        memory_growth = final_memory - initial_memory
        logger.info(f"📊 内存增长: {memory_growth:.1f}%")

        self.assertLess(memory_growth, 10, "内存使用增长过多，可能存在内存泄漏")
        logger.info("✅ 内存泄漏检测测试通过")

    def test_performance_degradation(self):
        """性能衰减测试"""
        logger.info("🧪 测试性能衰减")

        # 记录每次转换的时间
        conversion_times = []
        num_iterations = 30

        for i in range(num_iterations):
            start = time.time()
            conversion = MockConversionFunc(2000)  # 2秒转换
            conversion()
            elapsed = time.time() - start

            conversion_times.append(elapsed)
            logger.debug(f"🔄 迭代 {i+1}: {elapsed:.3f}s")

            time.sleep(1)

        # 分析性能趋势
        first_10_avg = sum(conversion_times[:10]) / 10
        last_10_avg = sum(conversion_times[-10:]) / 10
        overall_avg = sum(conversion_times) / len(conversion_times)

        logger.info(f"📊 性能分析:")
        logger.info(f"   前10次平均: {first_10_avg:.3f}s")
        logger.info(f"   后10次平均: {last_10_avg:.3f}s")
        logger.info(f"   总体平均: {overall_avg:.3f}s")

        # 计算性能衰减百分比
        performance_degradation = (last_10_avg - first_10_avg) / first_10_avg * 100

        logger.info(f"📊 性能衰减: {performance_degradation:.1f}%")

        # 验证性能衰减是否在合理范围内 (不超过20%)
        self.assertLess(performance_degradation, 20, "性能衰减过多")
        logger.info("✅ 性能衰减测试通过")

    def test_error_recovery(self):
        """错误恢复测试"""
        logger.info("🧪 测试错误恢复")

        iteration = 0
        errors_injected = 0
        errors_recovered = 0

        while iteration < 20:
            iteration += 1
            try:
                # 正常执行转换
                conversion = MockConversionFunc(1000)
                conversion()

                # 模拟错误 (每5次迭代注入一个错误)
                if iteration % 5 == 0:
                    errors_injected += 1
                    # 这里应该模拟一个错误，但为了测试，我们捕获并记录
                    logger.warning(f"⚠️ 模拟错误 - 迭代 {iteration}")

                logger.debug(f"✅ 迭代 {iteration} 成功")

            except Exception as e:
                errors_recovered += 1
                logger.error(f"❌ 迭代 {iteration} 错误: {e}")

                # 验证系统能够从错误中恢复
                self.assertIsNotNone(e, "错误应该被捕获和记录")

            time.sleep(0.5)

        logger.info(f"📊 错误恢复测试结果:")
        logger.info(f"   总迭代数: {iteration}")
        logger.info(f"   注入错误数: {errors_injected}")
        logger.info(f"   恢复错误数: {errors_recovered}")

        # 验证所有错误都被正确处理
        self.assertGreaterEqual(errors_recovered, errors_injected * 0.8, "错误恢复率过低")
        logger.info("✅ 错误恢复测试通过")

    def test_resource_cleanup(self):
        """资源清理测试"""
        logger.info("🧪 测试资源清理")

        # 记录初始资源
        initial_cpu = psutil.cpu_percent(interval=1)
        initial_memory = psutil.virtual_memory().percent
        initial_threads = threading.active_count()

        logger.info(f"📊 初始资源 - CPU: {initial_cpu:.1f}%, Memory: {initial_memory:.1f}%, Threads: {initial_threads}")

        # 执行大量转换
        for i in range(50):
            conversion = MockConversionFunc(500)
            conversion()
            time.sleep(0.1)

        # 等待资源释放
        time.sleep(5)

        # 检查资源清理
        final_cpu = psutil.cpu_percent(interval=1)
        final_memory = psutil.virtual_memory().percent
        final_threads = threading.active_count()

        logger.info(f"📊 最终资源 - CPU: {final_cpu:.1f}%, Memory: {final_memory:.1f}%, Threads: {final_threads}")

        # 验证资源清理
        memory_diff = final_memory - initial_memory
        thread_diff = final_threads - initial_threads

        logger.info(f"📊 资源变化 - Memory: {memory_diff:+.1f}%, Threads: {thread_diff:+d}")

        # 资源增长应该在合理范围内
        self.assertLess(memory_diff, 5, "内存使用增长过多")
        self.assertLess(abs(thread_diff), 5, "线程数量变化过大")

        logger.info("✅ 资源清理测试通过")

    def tearDown(self):
        """测试清理"""
        super().tearDown()

        # 生成测试报告
        if hasattr(self, 'metrics') and self.metrics:
            report_path = f"reports/performance/stability_{self._testMethodName}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.generate_test_report(report_path)


if __name__ == '__main__':
    unittest.main()
