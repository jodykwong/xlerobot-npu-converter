"""
性能测试基类
为Story 3.1 Phase 3验证和测试提供基础框架
"""

import unittest
import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PerformanceTestBase(unittest.TestCase):
    """性能测试基类"""

    # 测试配置
    MAX_CONVERSION_TIME = 300  # 5分钟
    MIN_THROUGHPUT = 10  # 10模型/分钟
    MEMORY_OPTIMIZATION_THRESHOLD = 30  # 30%优化
    STABILITY_TEST_DURATION = 72 * 3600  # 72小时

    # 资源监控阈值
    CPU_THRESHOLD = 80.0
    MEMORY_THRESHOLD = 85.0
    NPU_THRESHOLD = 90.0

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        logger.info(f"🚀 开始执行 {cls.__name__}")
        cls.start_time = datetime.now()
        cls.test_results = {
            'test_name': cls.__name__,
            'start_time': cls.start_time.isoformat(),
            'metrics': {},
            'pass': True,
            'errors': []
        }

    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        cls.end_time = datetime.now()
        duration = (cls.end_time - cls.start_time).total_seconds()
        cls.test_results['end_time'] = cls.end_time.isoformat()
        cls.test_results['duration_seconds'] = duration
        logger.info(f"✅ {cls.__name__} 完成，耗时: {duration:.2f}秒")

    def setUp(self):
        """测试初始化"""
        self.start_time = datetime.now()
        self.metrics = {
            'conversion_time': [],
            'throughput': [],
            'cpu_usage': [],
            'memory_usage': [],
            'npu_usage': []
        }
        self.monitoring = False
        self.monitor_thread = None

    def tearDown(self):
        """测试清理"""
        self.stop_monitoring()

    def start_monitoring(self, interval=1.0):
        """开始资源监控"""
        if self.monitoring:
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_resources,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("🔍 开始资源监控")

    def stop_monitoring(self):
        """停止资源监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("⏹️ 停止资源监控")

    def _monitor_resources(self, interval):
        """资源监控后台任务"""
        while self.monitoring:
            try:
                # CPU使用率
                cpu_percent = psutil.cpu_percent(interval=None)

                # 内存使用率
                memory = psutil.virtual_memory()
                memory_percent = memory.percent

                # 记录指标
                self.metrics['cpu_usage'].append(cpu_percent)
                self.metrics['memory_usage'].append(memory_percent)

                # 检查阈值
                if cpu_percent > self.CPU_THRESHOLD:
                    logger.warning(f"⚠️ CPU使用率过高: {cpu_percent:.1f}%")

                if memory_percent > self.MEMORY_THRESHOLD:
                    logger.warning(f"⚠️ 内存使用率过高: {memory_percent:.1f}%")

                time.sleep(interval)
            except Exception as e:
                logger.error(f"监控出错: {e}")

    def measure_conversion_time(self, conversion_func, *args, **kwargs):
        """测量转换时间"""
        start = time.time()
        result = conversion_func(*args, **kwargs)
        end = time.time()

        conversion_time = end - start
        self.metrics['conversion_time'].append(conversion_time)

        # 检查是否超过阈值
        self.assertLess(
            conversion_time,
            self.MAX_CONVERSION_TIME,
            f"转换时间超过阈值 {self.MAX_CONVERSION_TIME}秒: {conversion_time:.2f}秒"
        )

        logger.info(f"⏱️ 转换时间: {conversion_time:.2f}秒")
        return result

    def measure_throughput(self, conversion_func, num_models, duration_seconds=60):
        """测量吞吐量"""
        start = time.time()
        completed = 0

        # 并发执行转换
        threads = []
        for _ in range(num_models):
            thread = threading.Thread(
                target=lambda: self._run_conversion(conversion_func, lambda: completed.__add__(1))
            )
            threads.append(thread)
            thread.start()

        # 等待指定时间
        time.sleep(duration_seconds)

        # 计算吞吐量
        elapsed = time.time() - start
        throughput = completed / (elapsed / 60)  # 模型/分钟

        self.metrics['throughput'].append(throughput)

        # 检查是否达到阈值
        self.assertGreater(
            throughput,
            self.MIN_THROUGHPUT,
            f"吞吐量低于阈值 {self.MIN_THROUGHPUT} 模型/分钟: {throughput:.2f}"
        )

        logger.info(f"🚀 吞吐量: {throughput:.2f} 模型/分钟")
        return throughput

    def _run_conversion(self, conversion_func, increment_func):
        """执行转换并计数"""
        try:
            conversion_func()
            increment_func()
        except Exception as e:
            logger.error(f"转换失败: {e}")

    def check_resource_optimization(self, baseline_metrics, optimized_metrics):
        """检查资源优化"""
        cpu_optimization = (
            (baseline_metrics['cpu_avg'] - optimized_metrics['cpu_avg']) /
            baseline_metrics['cpu_avg'] * 100
        )
        memory_optimization = (
            (baseline_metrics['memory_avg'] - optimized_metrics['memory_avg']) /
            baseline_metrics['memory_avg'] * 100
        )

        logger.info(f"💾 CPU优化: {cpu_optimization:.1f}%")
        logger.info(f"💾 内存优化: {memory_optimization:.1f}%")

        # 检查是否达到优化阈值
        self.assertGreater(
            memory_optimization,
            self.MEMORY_OPTIMIZATION_THRESHOLD,
            f"内存优化未达到阈值 {self.MEMORY_OPTIMIZATION_THRESHOLD}%"
        )

    def stability_test(self, duration_hours=72):
        """稳定性测试"""
        logger.info(f"🧪 开始 {duration_hours} 小时稳定性测试")

        start_time = datetime.now()
        end_time = start_time + timedelta(hours=duration_hours)
        iteration = 0
        errors = []

        while datetime.now() < end_time:
            iteration += 1
            try:
                # 执行转换
                self._run_stability_conversion()

                # 检查资源使用
                current_cpu = psutil.cpu_percent(interval=1)
                current_memory = psutil.virtual_memory().percent

                # 记录指标
                self.metrics['cpu_usage'].append(current_cpu)
                self.metrics['memory_usage'].append(current_memory)

                logger.info(f"🔄 稳定性测试迭代 {iteration}: CPU={current_cpu:.1f}%, MEM={current_memory:.1f}%")

                # 检查是否有异常
                if current_cpu > 95 or current_memory > 95:
                    errors.append(f"Iteration {iteration}: Resource usage too high")

                time.sleep(60)  # 每分钟执行一次
            except Exception as e:
                error_msg = f"Iteration {iteration}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ 稳定性测试完成，耗时 {duration/3600:.2f} 小时，迭代 {iteration} 次")

        # 检查错误数量
        self.assertEqual(len(errors), 0, f"稳定性测试中发现 {len(errors)} 个错误")

    def _run_stability_conversion(self):
        """执行稳定性测试转换"""
        # 模拟转换过程
        time.sleep(2)
        # 这里应该调用实际的转换函数

    def generate_test_report(self, output_path: str):
        """生成测试报告"""
        report = {
            'test_name': self.__class__.__name__,
            'timestamp': datetime.now().isoformat(),
            'metrics': self.metrics,
            'summary': {
                'total_tests': len(self.metrics.get('conversion_time', [])),
                'avg_conversion_time': self._calculate_average(self.metrics.get('conversion_time', [])),
                'max_conversion_time': self._calculate_max(self.metrics.get('conversion_time', [])),
                'avg_cpu_usage': self._calculate_average(self.metrics.get('cpu_usage', [])),
                'avg_memory_usage': self._calculate_average(self.metrics.get('memory_usage', [])),
                'avg_throughput': self._calculate_average(self.metrics.get('throughput', []))
            }
        }

        # 保存报告
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"📊 测试报告已保存: {output_path}")
        return report

    def _calculate_average(self, values: List[float]) -> float:
        """计算平均值"""
        return sum(values) / len(values) if values else 0

    def _calculate_max(self, values: List[float]) -> float:
        """计算最大值"""
        return max(values) if values else 0


class MockConversionFunc:
    """模拟转换函数"""
    def __init__(self, duration=30):
        self.duration = duration
        self.result = {"status": "success", "model_size_mb": 500}

    def __call__(self):
        """执行模拟转换"""
        time.sleep(self.duration / 1000)  # 转换为秒
        return self.result
