"""
大规模模型转换性能测试
测试系统处理大规模模型的能力
"""

import unittest
import time
import threading
import psutil
from datetime import datetime
from pathlib import Path
import json

from ..base_test import PerformanceTestBase, MockConversionFunc
import logging

logger = logging.getLogger(__name__)


class LargeScaleModelTest(PerformanceTestBase):
    """大规模模型转换性能测试"""

    def test_single_large_model(self):
        """单模型大文件测试"""
        logger.info("🧪 测试单模型大文件转换")

        # 模拟大文件模型 (500MB+)
        mock_conversion = MockConversionFunc(duration=30000)  # 30秒模拟时间

        # 开始监控
        self.start_monitoring()

        # 执行转换
        result = self.measure_conversion_time(mock_conversion)

        # 停止监控
        self.stop_monitoring()

        # 验证结果
        self.assertIsNotNone(result)
        logger.info("✅ 单模型大文件测试通过")

    def test_multiple_models_batch(self):
        """多模型批量测试"""
        logger.info("🧪 测试多模型批量转换")

        num_models = 10
        conversions = [MockConversionFunc(2000) for _ in range(num_models)]  # 每个2秒

        # 开始监控
        self.start_monitoring()

        # 并发执行
        threads = []
        for conversion in conversions:
            thread = threading.Thread(target=conversion)
            threads.append(thread)
            thread.start()

        # 等待所有转换完成
        for thread in threads:
            thread.join()

        # 停止监控
        self.stop_monitoring()

        # 验证结果
        avg_time = self._calculate_average(self.metrics['conversion_time'])
        self.assertLess(avg_time, 5)  # 平均转换时间 < 5秒
        logger.info(f"✅ 多模型批量测试通过，平均时间: {avg_time:.2f}秒")

    def test_mixed_model_types(self):
        """混合模型类型测试 (ASR + TTS)"""
        logger.info("🧪 测试混合模型类型转换")

        # 模拟ASR模型 (SenseVoice)
        asr_models = [MockConversionFunc(2500) for _ in range(5)]

        # 模拟TTS模型 (VITS-Cantonese)
        tts_models = [MockConversionFunc(3000) for _ in range(5)]

        all_models = asr_models + tts_models

        # 开始监控
        self.start_monitoring()

        # 并发执行
        threads = []
        for model in all_models:
            thread = threading.Thread(target=model)
            threads.append(thread)
            thread.start()

        # 等待所有转换完成
        for thread in threads:
            thread.join()

        # 停止监控
        self.stop_monitoring()

        # 验证结果
        asr_avg = self._calculate_average(self.metrics['conversion_time'][:5])
        tts_avg = self._calculate_average(self.metrics['conversion_time'][5:])

        self.assertLess(asr_avg, 5)
        self.assertLess(tts_avg, 5)
        logger.info(f"✅ 混合模型类型测试通过 - ASR: {asr_avg:.2f}s, TTS: {tts_avg:.2f}s")

    def test_continuous_conversion(self):
        """连续转换测试"""
        logger.info("🧪 测试连续转换 (24小时)")

        # 注意: 这里使用短时间模拟，实际测试中应该使用24小时
        duration_minutes = 5  # 模拟5分钟
        iterations = duration_minutes

        start_time = time.time()
        for i in range(iterations):
            logger.info(f"🔄 连续转换进度: {i+1}/{iterations}")

            # 执行转换
            mock_conversion = MockConversionFunc(2000)  # 2秒
            self.start_monitoring()
            mock_conversion()
            self.stop_monitoring()

        elapsed = time.time() - start_time
        logger.info(f"✅ 连续转换测试完成，耗时: {elapsed/60:.2f}分钟")

    def test_memory_efficiency_large_models(self):
        """大模型内存效率测试"""
        logger.info("🧪 测试大模型内存效率")

        # 记录基准内存使用
        baseline_memory = psutil.virtual_memory().percent
        logger.info(f"📊 基准内存使用率: {baseline_memory:.1f}%")

        # 执行大模型转换
        mock_conversion = MockConversionFunc(duration=5000)  # 5秒
        self.start_monitoring()
        mock_conversion()
        self.stop_monitoring()

        # 计算内存使用统计
        max_memory = self._calculate_max(self.metrics['memory_usage'])
        avg_memory = self._calculate_average(self.metrics['memory_usage'])

        logger.info(f"📊 峰值内存使用率: {max_memory:.1f}%")
        logger.info(f"📊 平均内存使用率: {avg_memory:.1f}%")

        # 验证内存使用在合理范围内
        self.assertLess(max_memory, 90)  # 峰值 < 90%
        self.assertLess(avg_memory, 80)  # 平均 < 80%

        logger.info("✅ 大模型内存效率测试通过")

    def test_concurrent_large_models(self):
        """并发大模型测试"""
        logger.info("🧪 测试并发大模型转换")

        num_concurrent = 8  # 8个并发模型
        conversions = [MockConversionFunc(10000) for _ in range(num_concurrent)]  # 每个10秒

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
        throughput = num_concurrent / (elapsed / 60)  # 模型/分钟

        logger.info(f"📊 并发大模型测试 - 并发数: {num_concurrent}, 耗时: {elapsed:.2f}s, 吞吐量: {throughput:.2f} 模型/分钟")

        # 验证吞吐量
        self.assertGreater(throughput, self.MIN_THROUGHPUT)
        logger.info("✅ 并发大模型测试通过")

    def test_resource_peak_handling(self):
        """资源峰值处理测试"""
        logger.info("🧪 测试资源峰值处理")

        # 创建多个高负载转换
        num_high_load = 5
        conversions = [MockConversionFunc(15000) for _ in range(num_high_load)]  # 每个15秒

        # 开始监控
        self.start_monitoring()

        # 并发执行
        threads = []
        for conversion in conversions:
            thread = threading.Thread(target=conversion)
            threads.append(thread)
            thread.start()

        # 等待所有转换完成
        for thread in threads:
            thread.join()

        self.stop_monitoring()

        # 分析资源峰值
        max_cpu = self._calculate_max(self.metrics['cpu_usage'])
        max_memory = self._calculate_max(self.metrics['memory_usage'])

        logger.info(f"📊 峰值CPU使用率: {max_cpu:.1f}%")
        logger.info(f"📊 峰值内存使用率: {max_memory:.1f}%")

        # 验证系统在峰值时仍然稳定
        self.assertLess(max_cpu, 95)  # CPU峰值 < 95%
        self.assertLess(max_memory, 95)  # 内存峰值 < 95%

        logger.info("✅ 资源峰值处理测试通过")

    def tearDown(self):
        """测试清理"""
        super().tearDown()

        # 生成测试报告
        if hasattr(self, 'metrics') and self.metrics:
            report_path = f"reports/performance/large_scale_{self._testMethodName}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.generate_test_report(report_path)


if __name__ == '__main__':
    unittest.main()
