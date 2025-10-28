"""
算法A/B测试框架

提供算法A/B测试能力，包括实验设计、流量分配、结果分析和统计显著性检验。
"""

import logging
import time
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import statistics


logger = logging.getLogger(__name__)


class TestStatus(Enum):
    """测试状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    STOPPED = "stopped"
    FAILED = "failed"


class MetricType(Enum):
    """指标类型枚举"""
    ACCURACY = "accuracy"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    CUSTOM = "custom"


@dataclass
class ABTestConfig:
    """A/B测试配置"""
    test_name: str
    algorithm_a: str
    algorithm_b: str
    traffic_split: float = 0.5  # A算法流量占比 (0-1)
    duration_seconds: int = 3600  # 测试持续时间
    min_samples: int = 1000  # 最小样本数
    significance_level: float = 0.05  # 显著性水平
    metrics: List[str] = field(default_factory=lambda: ["accuracy", "latency"])
    confidence_interval: float = 0.95  # 置信区间


@dataclass
class TestResult:
    """测试结果"""
    algorithm_id: str
    metric_name: str
    value: float
    timestamp: float
    sample_size: int = 1


@dataclass
class StatisticalResult:
    """统计结果"""
    metric_name: str
    algorithm_a_mean: float
    algorithm_b_mean: float
    algorithm_a_std: float
    algorithm_b_std: float
    p_value: float
    significant: bool
    improvement: float  # B相对A的改善百分比
    confidence_interval: Tuple[float, float]


class AlgorithmABTestingFramework:
    """
    算法A/B测试框架

    提供完整的A/B测试能力，支持多指标测试、统计分析和可视化。
    """

    def __init__(self):
        """初始化A/B测试框架"""
        self._tests: Dict[str, Dict[str, Any]] = {}
        self._results: Dict[str, List[TestResult]] = {}
        self._statistics: Dict[str, Any] = {
            'total_tests': 0,
            'completed_tests': 0,
            'total_samples': 0
        }

        logger.info("算法A/B测试框架已初始化")

    def create_test(self, config: ABTestConfig) -> str:
        """
        创建A/B测试

        Args:
            config: 测试配置

        Returns:
            测试ID

        Raises:
            ValueError: 如果配置无效
        """
        try:
            # 验证配置
            if config.traffic_split < 0 or config.traffic_split > 1:
                raise ValueError("流量分配必须在0-1之间")

            if config.significance_level <= 0 or config.significance_level >= 1:
                raise ValueError("显著性水平必须在0-1之间")

            if not config.metrics:
                raise ValueError("必须指定至少一个测试指标")

            # 生成测试ID
            test_id = f"ab_test_{int(time.time())}_{random.randint(1000, 9999)}"

            # 存储测试信息
            self._tests[test_id] = {
                'config': config,
                'status': TestStatus.PENDING,
                'start_time': None,
                'end_time': None,
                'samples_a': 0,
                'samples_b': 0,
                'current_traffic_split': config.traffic_split
            }

            self._results[test_id] = []

            logger.info(f"A/B测试已创建: {test_id}, 算法: {config.algorithm_a} vs {config.algorithm_b}")
            return test_id

        except Exception as e:
            logger.error(f"创建A/B测试失败: {e}")
            raise

    def start_test(self, test_id: str) -> bool:
        """
        启动A/B测试

        Args:
            test_id: 测试ID

        Returns:
            启动是否成功
        """
        try:
            if test_id not in self._tests:
                logger.error(f"测试 {test_id} 不存在")
                return False

            test_info = self._tests[test_id]
            if test_info['status'] != TestStatus.PENDING:
                logger.warning(f"测试 {test_id} 状态不正确: {test_info['status']}")
                return False

            # 启动测试
            test_info['status'] = TestStatus.RUNNING
            test_info['start_time'] = time.time()

            self._statistics['total_tests'] += 1

            logger.info(f"A/B测试已启动: {test_id}")
            return True

        except Exception as e:
            logger.error(f"启动A/B测试失败: {e}")
            return False

    def record_result(
        self,
        test_id: str,
        algorithm_id: str,
        metric_name: str,
        value: float,
        sample_size: int = 1
    ) -> bool:
        """
        记录测试结果

        Args:
            test_id: 测试ID
            algorithm_id: 算法ID
            metric_name: 指标名
            value: 指标值
            sample_size: 样本大小

        Returns:
            记录是否成功
        """
        try:
            if test_id not in self._tests:
                logger.error(f"测试 {test_id} 不存在")
                return False

            test_info = self._tests[test_id]
            if test_info['status'] != TestStatus.RUNNING:
                logger.warning(f"测试 {test_id} 未运行")
                return False

            # 创建测试结果
            result = TestResult(
                algorithm_id=algorithm_id,
                metric_name=metric_name,
                value=value,
                timestamp=time.time(),
                sample_size=sample_size
            )

            # 存储结果
            self._results[test_id].append(result)

            # 更新样本计数
            if algorithm_id == test_info['config'].algorithm_a:
                test_info['samples_a'] += sample_size
            elif algorithm_id == test_info['config'].algorithm_b:
                test_info['samples_b'] += sample_size

            self._statistics['total_samples'] += sample_size

            return True

        except Exception as e:
            logger.error(f"记录测试结果失败: {e}")
            return False

    def get_algorithm_for_request(self, test_id: str) -> Optional[str]:
        """
        根据流量分配获取要使用的算法

        Args:
            test_id: 测试ID

        Returns:
            算法ID，如果测试不存在或未运行则返回None
        """
        try:
            if test_id not in self._tests:
                return None

            test_info = self._tests[test_id]
            if test_info['status'] != TestStatus.RUNNING:
                return None

            # 根据流量分配随机选择算法
            traffic_split = test_info['current_traffic_split']
            if random.random() < traffic_split:
                return test_info['config'].algorithm_a
            else:
                return test_info['config'].algorithm_b

        except Exception as e:
            logger.error(f"获取算法失败: {e}")
            return None

    def stop_test(self, test_id: str) -> bool:
        """
        停止A/B测试

        Args:
            test_id: 测试ID

        Returns:
            停止是否成功
        """
        try:
            if test_id not in self._tests:
                logger.error(f"测试 {test_id} 不存在")
                return False

            test_info = self._tests[test_id]
            if test_info['status'] != TestStatus.RUNNING:
                logger.warning(f"测试 {test_id} 未在运行")
                return False

            # 停止测试
            test_info['status'] = TestStatus.COMPLETED
            test_info['end_time'] = time.time()

            self._statistics['completed_tests'] += 1

            logger.info(f"A/B测试已停止: {test_id}")
            return True

        except Exception as e:
            logger.error(f"停止A/B测试失败: {e}")
            return False

    def analyze_results(self, test_id: str) -> Dict[str, StatisticalResult]:
        """
        分析测试结果

        Args:
            test_id: 测试ID

        Returns:
            各指标的统计分析结果

        Raises:
            ValueError: 如果测试不存在或未完成
        """
        try:
            if test_id not in self._tests:
                raise ValueError(f"测试 {test_id} 不存在")

            test_info = self._tests[test_id]
            if test_info['status'] != TestStatus.COMPLETED:
                raise ValueError(f"测试 {test_id} 未完成")

            config = test_info['config']
            results = self._results[test_id]

            # 按指标分组
            metric_results = {}
            for metric in config.metrics:
                metric_results[metric] = self._analyze_metric(results, config, metric)

            logger.info(f"A/B测试结果分析完成: {test_id}")
            return metric_results

        except Exception as e:
            logger.error(f"分析测试结果失败: {e}")
            raise

    def _analyze_metric(
        self,
        results: List[TestResult],
        config: ABTestConfig,
        metric_name: str
    ) -> StatisticalResult:
        """
        分析单个指标

        Args:
            results: 测试结果列表
            config: 测试配置
            metric_name: 指标名

        Returns:
            统计结果
        """
        # 分离A和B的结果
        results_a = [r.value for r in results if r.algorithm_id == config.algorithm_a and r.metric_name == metric_name]
        results_b = [r.value for r in results if r.algorithm_id == config.algorithm_b and r.metric_name == metric_name]

        if not results_a or not results_b:
            raise ValueError(f"指标 {metric_name} 缺少数据")

        # 计算统计量
        mean_a = statistics.mean(results_a)
        mean_b = statistics.mean(results_b)
        std_a = statistics.stdev(results_a) if len(results_a) > 1 else 0
        std_b = statistics.stdev(results_b) if len(results_b) > 1 else 0

        # 简化的显著性检验（实际应用中应使用t检验或z检验）
        # 这里使用简化的实现
        p_value = self._calculate_p_value(results_a, results_b)

        # 判断是否显著
        significant = p_value < config.significance_level

        # 计算改善百分比
        if metric_name == 'latency' or metric_name == 'memory_usage' or metric_name == 'cpu_usage':
            # 对于延迟和资源使用，降低是好的
            improvement = (mean_a - mean_b) / mean_a * 100 if mean_a > 0 else 0
        else:
            # 对于准确率和吞吐量，提升是好的
            improvement = (mean_b - mean_a) / mean_a * 100 if mean_a > 0 else 0

        # 计算置信区间（简化实现）
        confidence_interval = self._calculate_confidence_interval(results_a, results_b, config.confidence_interval)

        return StatisticalResult(
            metric_name=metric_name,
            algorithm_a_mean=mean_a,
            algorithm_b_mean=mean_b,
            algorithm_a_std=std_a,
            algorithm_b_std=std_b,
            p_value=p_value,
            significant=significant,
            improvement=improvement,
            confidence_interval=confidence_interval
        )

    def _calculate_p_value(self, results_a: List[float], results_b: List[float]) -> float:
        """
        计算p值（简化实现）

        Args:
            results_a: A组结果
            results_b: B组结果

        Returns:
            p值
        """
        # 简化的实现：使用两组数据的均值差异与标准差的关系
        # 实际应用中应使用t检验

        mean_a = statistics.mean(results_a)
        mean_b = statistics.mean(results_b)

        # 简化的p值计算
        if len(results_a) > 1 and len(results_b) > 1:
            std_a = statistics.stdev(results_a)
            std_b = statistics.stdev(results_b)

            # 简化的z分数
            pooled_std = ((std_a ** 2) + (std_b ** 2)) / 2
            if pooled_std > 0:
                z_score = abs(mean_b - mean_a) / pooled_std
                # 简化的p值转换
                p_value = 2 * (1 - min(0.999, z_score / 10))
                return max(0.001, min(0.999, p_value))

        return 0.5  # 默认值

    def _calculate_confidence_interval(
        self,
        results_a: List[float],
        results_b: List[float],
        confidence_level: float
    ) -> Tuple[float, float]:
        """
        计算置信区间（简化实现）

        Args:
            results_a: A组结果
            results_b: B组结果
            confidence_level: 置信水平

        Returns:
            置信区间
        """
        mean_diff = statistics.mean(results_b) - statistics.mean(results_a)

        # 简化的置信区间
        margin = abs(mean_diff) * (1 - confidence_level)

        return (mean_diff - margin, mean_diff + margin)

    def get_test_status(self, test_id: str) -> Optional[Dict[str, Any]]:
        """
        获取测试状态

        Args:
            test_id: 测试ID

        Returns:
            测试状态信息
        """
        if test_id not in self._tests:
            return None

        test_info = self._tests[test_id]
        config = test_info['config']

        # 计算运行时间
        runtime_seconds = 0
        if test_info['start_time']:
            end_time = test_info['end_time'] or time.time()
            runtime_seconds = end_time - test_info['start_time']

        return {
            'test_id': test_id,
            'status': test_info['status'].value,
            'algorithm_a': config.algorithm_a,
            'algorithm_b': config.algorithm_b,
            'traffic_split': test_info['current_traffic_split'],
            'samples_a': test_info['samples_a'],
            'samples_b': test_info['samples_b'],
            'total_samples': test_info['samples_a'] + test_info['samples_b'],
            'runtime_seconds': runtime_seconds,
            'start_time': test_info['start_time'],
            'end_time': test_info['end_time'],
            'metrics': config.metrics
        }

    def list_tests(self) -> List[str]:
        """
        列出所有测试ID

        Returns:
            测试ID列表
        """
        return list(self._tests.keys())

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取框架统计信息

        Returns:
            统计信息字典
        """
        return {
            'total_tests': self._statistics['total_tests'],
            'completed_tests': self._statistics['completed_tests'],
            'running_tests': self._statistics['total_tests'] - self._statistics['completed_tests'],
            'total_samples': self._statistics['total_samples'],
            'active_tests': sum(
                1 for t in self._tests.values()
                if t['status'] == TestStatus.RUNNING
            )
        }

    def export_results(self, test_id: str, output_path: str) -> bool:
        """
        导出测试结果

        Args:
            test_id: 测试ID
            output_path: 输出路径

        Returns:
            导出是否成功
        """
        try:
            import json
            from pathlib import Path

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # 准备导出数据
            export_data = {
                'test_id': test_id,
                'test_info': self.get_test_status(test_id),
                'results': [
                    {
                        'algorithm_id': r.algorithm_id,
                        'metric_name': r.metric_name,
                        'value': r.value,
                        'timestamp': r.timestamp,
                        'sample_size': r.sample_size
                    }
                    for r in self._results.get(test_id, [])
                ]
            }

            # 添加分析结果（如果测试已完成）
            if test_id in self._tests and self._tests[test_id]['status'] == TestStatus.COMPLETED:
                try:
                    analysis = self.analyze_results(test_id)
                    export_data['analysis'] = {
                        metric: {
                            'algorithm_a_mean': result.algorithm_a_mean,
                            'algorithm_b_mean': result.algorithm_b_mean,
                            'p_value': result.p_value,
                            'significant': result.significant,
                            'improvement': result.improvement
                        }
                        for metric, result in analysis.items()
                    }
                except Exception as e:
                    logger.warning(f"分析结果导出失败: {e}")

            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            logger.info(f"测试结果已导出到: {output_path}")
            return True

        except Exception as e:
            logger.error(f"导出测试结果失败: {e}")
            return False
