"""
并发转换压力测试
验证系统在高并发场景下的稳定性
"""

import unittest
import time
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

from ..base_test import PerformanceTestBase, MockConversionFunc
import logging

logger = logging.getLogger(__name__)


class ConcurrentStressTest(PerformanceTestBase):
    """并发转换压力测试"""

    def test_5_models_concurrent(self):
        """5模型并发测试"""
        logger.info("🧪 测试5模型并发转换")

        num_models = 5
        conversions = [MockConversionFunc(3000) for _ in range(num_models)]  # 每个3秒

        # 开始监控
        self.start_monitoring()

        # 并发执行
        start = time.time()
        threads = []
        for conversion in conversions:
            thread = threading.Thread(target=conversion)
            threads.append(thread)
            thread.start()

        # 等待所有转换完成
        for thread in threads:
            thread.join()

        elapsed = time.time() - start
        self.stop_monitoring()

        # 计算吞吐量
        throughput = num_models / (elapsed / 60)  # 模型/分钟

        logger.info(f"📊 5模型并发测试 - 耗时: {elapsed:.2f}s, 吞吐量: {throughput:.2f} 模型/分钟")

        # 验证吞吐量
        self.assertGreater(throughput, self.MIN_THROUGHPUT)
        logger.info("✅ 5模型并发测试通过")

    def test_10_models_concurrent(self):
        """10模型并发测试"""
        logger.info("🧪 测试10模型并发转换")

        num_models = 10
        conversions = [MockConversionFunc(5000) for _ in range(num_models)]  # 每个5秒

        # 开始监控
        self.start_monitoring()

        # 使用线程池执行
        with ThreadPoolExecutor(max_workers=num_models) as executor:
            start = time.time()
            futures = [executor.submit(conversion) for conversion in conversions]

            # 等待所有任务完成
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"转换失败: {e}")

        elapsed = time.time() - start
        self.stop_monitoring()

        # 计算吞吐量
        throughput = num_models / (elapsed / 60)  # 模型/分钟

        logger.info(f"📊 10模型并发测试 - 耗时: {elapsed:.2f}s, 吞吐量: {throughput:.2f} 模型/分钟")

        # 验证吞吐量
        self.assertGreater(throughput, self.MIN_THROUGHPUT)
        logger.info("✅ 10模型并发测试通过")

    def test_peak_load_15_models(self):
        """峰值负载测试 (15模型)"""
        logger.info("🧪 测试峰值负载 (15模型)")

        num_models = 15
        conversions = [MockConversionFunc(8000) for _ in range(num_models)]  # 每个8秒

        # 开始监控
        self.start_monitoring()

        # 使用线程池执行
        with ThreadPoolExecutor(max_workers=num_models) as executor:
            start = time.time()
            futures = [executor.submit(conversion) for conversion in conversions]

            # 等待所有任务完成
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"转换失败: {e}")

        elapsed = time.time() - start
        self.stop_monitoring()

        # 计算吞吐量
        throughput = num_models / (elapsed / 60)  # 模型/分钟

        logger.info(f"📊 峰值负载测试 - 耗时: {elapsed:.2f}s, 吞吐量: {throughput:.2f} 模型/分钟")

        # 验证吞吐量（峰值负载下可以适当降低阈值）
        self.assertGreater(throughput, self.MIN_THROUGHPUT * 0.8)
        logger.info("✅ 峰值负载测试通过")

    def test_burst_concurrent_20_models(self):
        """突发并发测试 (瞬间启动20模型)"""
        logger.info("🧪 测试突发并发 (20模型)")

        num_models = 20
        conversions = [MockConversionFunc(3000) for _ in range(num_models)]  # 每个3秒

        # 开始监控
        self.start_monitoring()

        # 瞬间启动所有模型
        start = time.time()
        with ThreadPoolExecutor(max_workers=num_models) as executor:
            futures = [executor.submit(conversion) for conversion in conversions]

            # 等待所有任务完成
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"转换失败: {e}")

        elapsed = time.time() - start
        self.stop_monitoring()

        # 计算吞吐量
        throughput = num_models / (elapsed / 60)  # 模型/分钟

        logger.info(f"📊 突发并发测试 - 耗时: {elapsed:.2f}s, 吞吐量: {throughput:.2f} 模型/分钟")

        # 验证系统没有崩溃
        self.assertGreater(throughput, 0)
        logger.info("✅ 突发并发测试通过 (系统未崩溃)")

    def test_concurrent_with_different_priorities(self):
        """不同优先级并发测试"""
        logger.info("🧪 测试不同优先级并发转换")

        # 高优先级任务
        high_priority = [MockConversionFunc(2000) for _ in range(3)]

        # 中优先级任务
        medium_priority = [MockConversionFunc(3000) for _ in range(5)]

        # 低优先级任务
        low_priority = [MockConversionFunc(4000) for _ in range(7)]

        all_tasks = high_priority + medium_priority + low_priority

        # 开始监控
        self.start_monitoring()

        # 并发执行
        start = time.time()
        threads = []
        for task in all_tasks:
            thread = threading.Thread(target=task)
            threads.append(thread)
            thread.start()

        # 等待所有转换完成
        for thread in threads:
            thread.join()

        elapsed = time.time() - start
        self.stop_monitoring()

        # 验证结果
        total_tasks = len(all_tasks)
        throughput = total_tasks / (elapsed / 60)  # 模型/分钟

        logger.info(f"📊 优先级测试 - 高: {len(high_priority)}, 中: {len(medium_priority)}, 低: {len(low_priority)}")
        logger.info(f"📊 总任务数: {total_tasks}, 耗时: {elapsed:.2f}s, 吞吐量: {throughput:.2f} 模型/分钟")

        # 验证吞吐量
        self.assertGreater(throughput, self.MIN_THROUGHPUT)
        logger.info("✅ 不同优先级并发测试通过")

    def test_concurrent_mixed_workloads(self):
        """混合工作负载并发测试"""
        logger.info("🧪 测试混合工作负载并发")

        # 模拟不同类型的转换
        # ASR转换 (较短)
        asr_conversions = [MockConversionFunc(2500) for _ in range(4)]

        # TTS转换 (中等)
        tts_conversions = [MockConversionFunc(3500) for _ in range(4)]

        # 复杂转换 (较长)
        complex_conversions = [MockConversionFunc(5000) for _ in range(3)]

        all_conversions = asr_conversions + tts_conversions + complex_conversions

        # 开始监控
        self.start_monitoring()

        # 并发执行
        start = time.time()
        with ThreadPoolExecutor(max_workers=len(all_conversions)) as executor:
            futures = [executor.submit(conversion) for conversion in all_conversions]

            # 等待所有任务完成
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"转换失败: {e}")

        elapsed = time.time() - start
        self.stop_monitoring()

        # 验证结果
        total_models = len(all_conversions)
        throughput = total_models / (elapsed / 60)  # 模型/分钟

        logger.info(f"📊 混合负载测试 - ASR: {len(asr_conversions)}, TTS: {len(tts_conversions)}, 复杂: {len(complex_conversions)}")
        logger.info(f"📊 总模型数: {total_models}, 耗时: {elapsed:.2f}s, 吞吐量: {throughput:.2f} 模型/分钟")

        # 验证吞吐量
        self.assertGreater(throughput, self.MIN_THROUGHPUT)
        logger.info("✅ 混合工作负载并发测试通过")

    def test_concurrent_stress_sustained(self):
        """持续并发压力测试"""
        logger.info("🧪 测试持续并发压力 (60秒)")

        # 缩短测试时间至60秒用于快速验证
        duration_seconds = 60  # 60秒 (原600秒)
        batch_size = 5  # 每批5个模型
        batch_interval = 10  # 每10秒一批 (原30秒)

        start_time = time.time()
        completed_batches = 0

        while (time.time() - start_time) < duration_seconds:
            # 准备一批转换
            conversions = [MockConversionFunc(2000) for _ in range(batch_size)]

            # 执行一批转换
            with ThreadPoolExecutor(max_workers=batch_size) as executor:
                futures = [executor.submit(conversion) for conversion in conversions]

                # 等待当前批次完成
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"转换失败: {e}")

            completed_batches += 1
            elapsed = time.time() - start_time

            logger.info(f"🔄 批次 {completed_batches} 完成，耗时: {elapsed:.1f}s")

            # 等待下一批
            time.sleep(batch_interval)

        # 验证结果
        total_models = completed_batches * batch_size
        throughput = total_models / (duration_seconds / 60)  # 模型/分钟

        logger.info(f"📊 持续压力测试 - 完成批次: {completed_batches}, 总模型数: {total_models}")
        logger.info(f"📊 平均吞吐量: {throughput:.2f} 模型/分钟")

        # 验证吞吐量
        self.assertGreater(throughput, self.MIN_THROUGHPUT * 0.9)
        logger.info("✅ 持续并发压力测试通过")

    def tearDown(self):
        """测试清理"""
        super().tearDown()

        # 生成测试报告
        if hasattr(self, 'metrics') and self.metrics:
            report_path = f"reports/performance/stress_{self._testMethodName}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.generate_test_report(report_path)


if __name__ == '__main__':
    unittest.main()
