"""
算法性能分析器

提供性能分析、瓶颈识别和优化建议功能。
"""

import logging
import time
import psutil
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import statistics


logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """性能指标"""
    name: str
    value: float
    unit: str
    timestamp: float
    algorithm_id: str


@dataclass
class PerformanceSnapshot:
    """性能快照"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    execution_time: float
    throughput: float
    accuracy: Optional[float] = None
    custom_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class PerformanceReport:
    """性能报告"""
    algorithm_id: str
    start_time: float
    end_time: float
    total_requests: int
    success_rate: float
    average_latency: float
    p95_latency: float
    p99_latency: float
    throughput_rps: float
    cpu_usage: float
    memory_usage: float
    bottlenecks: List[str]
    recommendations: List[str]


class AlgorithmPerformanceAnalyzer:
    """
    算法性能分析器

    提供完整的性能监控、分析和优化建议功能。
    """

    def __init__(self, max_history: int = 10000):
        """
        初始化性能分析器

        Args:
            max_history: 最大历史记录数
        """
        self._max_history = max_history
        self._metrics_history: Dict[str, deque] = {}
        self._snapshots: deque = deque(maxlen=max_history)
        self._monitoring_active = False
        self._monitored_algorithms: set = set()
        self._statistics = {
            'total_metrics_collected': 0,
            'total_snapshots': 0,
            'analysis_count': 0
        }

        logger.info("算法性能分析器已初始化")

    def start_monitoring(self, algorithm_ids: List[str]) -> None:
        """
        开始监控

        Args:
            algorithm_ids: 要监控的算法ID列表
        """
        self._monitoring_active = True
        self._monitored_algorithms.update(algorithm_ids)

        # 为每个算法初始化历史记录
        for algorithm_id in algorithm_ids:
            if algorithm_id not in self._metrics_history:
                self._metrics_history[algorithm_id] = deque(maxlen=self._max_history)

        logger.info(f"开始监控算法: {algorithm_ids}")

    def stop_monitoring(self, algorithm_ids: Optional[List[str]] = None) -> None:
        """
        停止监控

        Args:
            algorithm_ids: 要停止监控的算法ID列表，如果为None则停止所有监控
        """
        if algorithm_ids is None:
            self._monitoring_active = False
            self._monitored_algorithms.clear()
            logger.info("停止所有算法监控")
        else:
            for algorithm_id in algorithm_ids:
                self._monitored_algorithms.discard(algorithm_id)
            logger.info(f"停止监控算法: {algorithm_ids}")

    def record_metric(
        self,
        algorithm_id: str,
        metric_name: str,
        value: float,
        unit: str = ""
    ) -> None:
        """
        记录性能指标

        Args:
            algorithm_id: 算法ID
            metric_name: 指标名
            value: 指标值
            unit: 单位
        """
        if algorithm_id not in self._metrics_history:
            self._metrics_history[algorithm_id] = deque(maxlen=self._max_history)

        metric = PerformanceMetric(
            name=metric_name,
            value=value,
            unit=unit,
            timestamp=time.time(),
            algorithm_id=algorithm_id
        )

        self._metrics_history[algorithm_id].append(metric)
        self._statistics['total_metrics_collected'] += 1

        logger.debug(f"记录指标: {algorithm_id}.{metric_name} = {value}{unit}")

    def take_snapshot(self, algorithm_id: str, execution_time: float, **kwargs) -> None:
        """
        拍摄性能快照

        Args:
            algorithm_id: 算法ID
            execution_time: 执行时间（秒）
            **kwargs: 其他指标
        """
        # 获取系统资源使用情况
        cpu_percent = psutil.cpu_percent(interval=None)
        memory_info = psutil.virtual_memory()
        memory_percent = memory_info.percent
        memory_used_mb = memory_info.used / (1024 * 1024)

        # 计算吞吐量（简化实现）
        throughput = 1.0 / execution_time if execution_time > 0 else 0

        snapshot = PerformanceSnapshot(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used_mb=memory_used_mb,
            execution_time=execution_time,
            throughput=throughput,
            accuracy=kwargs.get('accuracy'),
            custom_metrics={k: v for k, v in kwargs.items() if k not in ['accuracy']}
        )

        self._snapshots.append(snapshot)
        self._statistics['total_snapshots'] += 1

        logger.debug(f"性能快照已记录: 算法={algorithm_id}, 执行时间={execution_time:.3f}s")

    def analyze_performance(
        self,
        algorithm_id: str,
        time_window_seconds: int = 3600
    ) -> PerformanceReport:
        """
        分析性能

        Args:
            algorithm_id: 算法ID
            time_window_seconds: 时间窗口（秒）

        Returns:
            性能报告
        """
        try:
            current_time = time.time()
            start_time = current_time - time_window_seconds

            # 获取时间窗口内的数据
            metrics = [
                m for m in self._metrics_history.get(algorithm_id, [])
                if start_time <= m.timestamp <= current_time
            ]

            snapshots = [
                s for s in self._snapshots
                if start_time <= s.timestamp <= current_time
            ]

            if not metrics and not snapshots:
                logger.warning(f"算法 {algorithm_id} 在时间窗口内没有数据")

            # 分析延迟
            execution_times = [s.execution_time for s in snapshots]
            if not execution_times:
                execution_times = [
                    m.value for m in metrics if m.name == 'execution_time'
                ]

            avg_latency = statistics.mean(execution_times) if execution_times else 0
            p95_latency = self._percentile(execution_times, 95) if execution_times else 0
            p99_latency = self._percentile(execution_times, 99) if execution_times else 0

            # 分析吞吐量
            throughputs = [s.throughput for s in snapshots]
            avg_throughput = statistics.mean(throughputs) if throughputs else 0

            # 分析资源使用
            cpu_usage = statistics.mean([s.cpu_percent for s in snapshots]) if snapshots else 0
            memory_usage = statistics.mean([s.memory_percent for s in snapshots]) if snapshots else 0

            # 识别瓶颈
            bottlenecks = self._identify_bottlenecks(
                avg_latency, avg_throughput, cpu_usage, memory_usage
            )

            # 生成优化建议
            recommendations = self._generate_recommendations(
                algorithm_id, bottlenecks, avg_latency, cpu_usage, memory_usage
            )

            # 计算成功率（简化实现）
            total_requests = len(execution_times)
            success_rate = 100.0  # 假设所有请求都成功

            report = PerformanceReport(
                algorithm_id=algorithm_id,
                start_time=start_time,
                end_time=current_time,
                total_requests=total_requests,
                success_rate=success_rate,
                average_latency=avg_latency,
                p95_latency=p95_latency,
                p99_latency=p99_latency,
                throughput_rps=avg_throughput,
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                bottlenecks=bottlenecks,
                recommendations=recommendations
            )

            self._statistics['analysis_count'] += 1
            logger.info(f"性能分析完成: 算法={algorithm_id}, 请求数={total_requests}")

            return report

        except Exception as e:
            logger.error(f"性能分析失败: {e}")
            raise

    def _identify_bottlenecks(
        self,
        avg_latency: float,
        throughput: float,
        cpu_usage: float,
        memory_usage: float
    ) -> List[str]:
        """
        识别性能瓶颈

        Args:
            avg_latency: 平均延迟
            throughput: 吞吐量
            cpu_usage: CPU使用率
            memory_usage: 内存使用率

        Returns:
            瓶颈列表
        """
        bottlenecks = []

        # 检查延迟
        if avg_latency > 1.0:  # 1秒
            bottlenecks.append("高延迟 (>1s)")
        elif avg_latency > 0.5:  # 500ms
            bottlenecks.append("中等延迟 (500ms-1s)")

        # 检查吞吐量
        if throughput < 1.0:  # 1 RPS
            bottlenecks.append("低吞吐量 (<1 RPS)")
        elif throughput < 5.0:  # 5 RPS
            bottlenecks.append("中等吞吐量 (1-5 RPS)")

        # 检查CPU使用率
        if cpu_usage > 90:
            bottlenecks.append("CPU使用率过高 (>90%)")
        elif cpu_usage > 70:
            bottlenecks.append("CPU使用率偏高 (70-90%)")

        # 检查内存使用率
        if memory_usage > 90:
            bottlenecks.append("内存使用率过高 (>90%)")
        elif memory_usage > 70:
            bottlenecks.append("内存使用率偏高 (70-90%)")

        return bottlenecks

    def _generate_recommendations(
        self,
        algorithm_id: str,
        bottlenecks: List[str],
        avg_latency: float,
        cpu_usage: float,
        memory_usage: float
    ) -> List[str]:
        """
        生成优化建议

        Args:
            algorithm_id: 算法ID
            bottlenecks: 瓶颈列表
            avg_latency: 平均延迟
            cpu_usage: CPU使用率
            memory_usage: 内存使用率

        Returns:
            优化建议列表
        """
        recommendations = []

        # 基于瓶颈的建议
        if "高延迟" in str(bottlenecks):
            recommendations.append("考虑优化算法复杂度或使用更高效的数据结构")
            recommendations.append("实现缓存机制减少重复计算")
            recommendations.append("使用并行处理提升性能")

        if "低吞吐量" in str(bottlenecks):
            recommendations.append("增加并发处理能力")
            recommendations.append("优化I/O操作")
            recommendations.append("考虑使用异步处理")

        if "CPU使用率过高" in str(bottlenecks):
            recommendations.append("优化CPU密集型操作")
            recommendations.append("使用更高效的算法")
            recommendations.append("考虑使用GPU加速")

        if "内存使用率过高" in str(bottlenecks):
            recommendations.append("优化内存使用，释放不必要的对象")
            recommendations.append("使用内存池减少分配开销")
            recommendations.append("考虑流式处理减少内存占用")

        # 通用建议
        if avg_latency > 0.1:  # 100ms
            recommendations.append("启用性能分析工具定位具体瓶颈")
            recommendations.append("考虑算法重构或使用更高效的实现")

        if cpu_usage > 50 or memory_usage > 50:
            recommendations.append("监控系统资源使用情况")
            recommendations.append("设置资源使用告警")

        if not recommendations:
            recommendations.append("性能表现良好，无需优化")

        return recommendations

    def _percentile(self, data: List[float], percentile: int) -> float:
        """
        计算百分位数

        Args:
            data: 数据列表
            percentile: 百分位数 (0-100)

        Returns:
            百分位数值
        """
        if not data:
            return 0

        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)

        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))

    def get_performance_trends(
        self,
        algorithm_id: str,
        metric_name: str,
        time_window_seconds: int = 3600
    ) -> Optional[List[Tuple[float, float]]]:
        """
        获取性能趋势

        Args:
            algorithm_id: 算法ID
            metric_name: 指标名
            time_window_seconds: 时间窗口（秒）

        Returns:
            时间序列数据 [(timestamp, value), ...]
        """
        current_time = time.time()
        start_time = current_time - time_window_seconds

        metrics = [
            m for m in self._metrics_history.get(algorithm_id, [])
            if m.name == metric_name and start_time <= m.timestamp <= current_time
        ]

        return [(m.timestamp, m.value) for m in metrics]

    def compare_performance(
        self,
        algorithm_ids: List[str],
        time_window_seconds: int = 3600
    ) -> Dict[str, Dict[str, float]]:
        """
        比较多个算法的性能

        Args:
            algorithm_ids: 算法ID列表
            time_window_seconds: 时间窗口（秒）

        Returns:
            比较结果字典
        """
        comparison = {}

        for algorithm_id in algorithm_ids:
            report = self.analyze_performance(algorithm_id, time_window_seconds)
            comparison[algorithm_id] = {
                'average_latency': report.average_latency,
                'throughput': report.throughput_rps,
                'cpu_usage': report.cpu_usage,
                'memory_usage': report.memory_usage,
                'success_rate': report.success_rate
            }

        return comparison

    def export_performance_data(
        self,
        algorithm_id: str,
        output_path: str,
        time_window_seconds: int = 3600
    ) -> bool:
        """
        导出性能数据

        Args:
            algorithm_id: 算法ID
            output_path: 输出路径
            time_window_seconds: 时间窗口（秒）

        Returns:
            导出是否成功
        """
        try:
            import json
            from pathlib import Path

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # 收集数据
            current_time = time.time()
            start_time = current_time - time_window_seconds

            metrics = [
                {
                    'name': m.name,
                    'value': m.value,
                    'unit': m.unit,
                    'timestamp': m.timestamp
                }
                for m in self._metrics_history.get(algorithm_id, [])
                if start_time <= m.timestamp <= current_time
            ]

            snapshots = [
                {
                    'timestamp': s.timestamp,
                    'cpu_percent': s.cpu_percent,
                    'memory_percent': s.memory_percent,
                    'execution_time': s.execution_time,
                    'throughput': s.throughput,
                    'accuracy': s.accuracy,
                    'custom_metrics': s.custom_metrics
                }
                for s in self._snapshots
                if start_time <= s.timestamp <= current_time
            ]

            # 性能报告
            report = self.analyze_performance(algorithm_id, time_window_seconds)

            # 导出数据
            export_data = {
                'algorithm_id': algorithm_id,
                'time_window': time_window_seconds,
                'metrics': metrics,
                'snapshots': snapshots,
                'performance_report': {
                    'total_requests': report.total_requests,
                    'success_rate': report.success_rate,
                    'average_latency': report.average_latency,
                    'p95_latency': report.p95_latency,
                    'p99_latency': report.p99_latency,
                    'throughput_rps': report.throughput_rps,
                    'cpu_usage': report.cpu_usage,
                    'memory_usage': report.memory_usage,
                    'bottlenecks': report.bottlenecks,
                    'recommendations': report.recommendations
                }
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            logger.info(f"性能数据已导出到: {output_path}")
            return True

        except Exception as e:
            logger.error(f"导出性能数据失败: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取分析器统计信息

        Returns:
            统计信息字典
        """
        return {
            'monitoring_active': self._monitoring_active,
            'monitored_algorithms': list(self._monitored_algorithms),
            'total_metrics_collected': self._statistics['total_metrics_collected'],
            'total_snapshots': self._statistics['total_snapshots'],
            'analysis_count': self._statistics['analysis_count'],
            'max_history': self._max_history
        }
