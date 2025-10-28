"""
性能分析器 (Performance Analyzer)

分析性能数据，计算性能指标，生成性能报告，提供性能优化建议。

作者: BMAD Method
创建日期: 2025-10-29
版本: v1.0
"""

import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import statistics

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class AnalyzerConfig:
    """性能分析器配置"""
    anomaly_threshold: float = 2.0  # 异常检测阈值（标准差倍数）
    trend_window_size: int = 10  # 趋势分析窗口大小
    percentile_values: List[float] = None  # 百分位数
    correlation_threshold: float = 0.7  # 相关性阈值

    def __post_init__(self):
        if self.percentile_values is None:
            self.percentile_values = [50, 90, 95, 99]


@dataclass
class Statistics:
    """统计指标"""
    count: int
    min: float
    max: float
    mean: float
    median: float
    std_dev: float
    variance: float
    percentiles: Dict[float, float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'count': self.count,
            'min': self.min,
            'max': self.max,
            'mean': self.mean,
            'median': self.median,
            'std_dev': self.std_dev,
            'variance': self.variance,
            'percentiles': self.percentiles
        }


@dataclass
class Anomaly:
    """性能异常"""
    timestamp: datetime
    metric_name: str
    value: float
    expected_range: Tuple[float, float]
    anomaly_score: float
    severity: str  # low, medium, high, critical
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'metric_name': self.metric_name,
            'value': self.value,
            'expected_range': self.expected_range,
            'anomaly_score': self.anomaly_score,
            'severity': self.severity,
            'description': self.description
        }


@dataclass
class ComparisonResult:
    """对比结果"""
    baseline_name: str
    current_name: str
    metric_comparisons: Dict[str, Dict[str, float]]  # metric -> {change, change_percent}
    regression_detected: bool
    improvements_detected: bool
    overall_score: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            'baseline_name': self.baseline_name,
            'current_name': self.current_name,
            'metric_comparisons': self.metric_comparisons,
            'regression_detected': self.regression_detected,
            'improvements_detected': self.improvements_detected,
            'overall_score': self.overall_score
        }


@dataclass
class Recommendation:
    """优化建议"""
    category: str  # configuration, algorithm, resource, architecture
    priority: str  # low, medium, high, critical
    title: str
    description: str
    impact: str  # 预期影响
    effort: str  # 实施难度
    metrics: List[str]  # 相关指标
    actions: List[str]  # 具体行动
    references: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'category': self.category,
            'priority': self.priority,
            'title': self.title,
            'description': self.description,
            'impact': self.impact,
            'effort': self.effort,
            'metrics': self.metrics,
            'actions': self.actions,
            'references': self.references or []
        }


@dataclass
class TrendAnalysis:
    """趋势分析"""
    metric_name: str
    trend_direction: str  # increasing, decreasing, stable, volatile
    trend_strength: float  # 0-1
    predicted_values: List[float]  # 预测值
    confidence_interval: Tuple[float, float]  # 置信区间
    changepoints: List[datetime]  # 变化点

    def to_dict(self) -> Dict[str, Any]:
        return {
            'metric_name': self.metric_name,
            'trend_direction': self.trend_direction,
            'trend_strength': self.trend_strength,
            'predicted_values': self.predicted_values,
            'confidence_interval': self.confidence_interval,
            'changepoints': [cp.isoformat() for cp in self.changepoints]
        }


@dataclass
class AnalysisResult:
    """分析结果"""
    analysis_id: str
    start_time: datetime
    end_time: datetime
    total_metrics: int
    statistics: Dict[str, Statistics]
    anomalies: List[Anomaly]
    trends: Dict[str, TrendAnalysis]
    correlations: Dict[str, float]  # metric_pairs -> correlation
    recommendations: List[Recommendation]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'analysis_id': self.analysis_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'total_metrics': self.total_metrics,
            'statistics': {k: v.to_dict() for k, v in self.statistics.items()},
            'anomalies': [a.to_dict() for a in self.anomalies],
            'trends': {k: v.to_dict() for v in self.trends.items()},
            'correlations': self.correlations,
            'recommendations': [r.to_dict() for r in self.recommendations]
        }


class PerformanceAnalyzer:
    """
    性能分析器

    分析性能数据，计算性能指标，检测异常，分析趋势，
    提供性能优化建议。
    """

    def __init__(self, config: AnalyzerConfig):
        """
        初始化性能分析器

        Args:
            config: 分析器配置
        """
        self.config = config
        logger.info(f"Performance Analyzer initialized with config: {asdict(config)}")

    def calculate_statistics(self, metrics: List[Dict[str, Any]],
                           metric_name: str) -> Statistics:
        """
        计算统计指标

        Args:
            metrics: 指标数据列表
            metric_name: 指标名称

        Returns:
            Statistics: 统计指标
        """
        if not metrics:
            raise ValueError("No metrics data provided")

        # 提取数值
        values = []
        for m in metrics:
            if metric_name in m:
                value = m[metric_name]
                if isinstance(value, (int, float)):
                    values.append(value)

        if not values:
            raise ValueError(f"No valid values found for metric: {metric_name}")

        # 计算统计指标
        count = len(values)
        min_val = min(values)
        max_val = max(values)
        mean_val = statistics.mean(values)
        median_val = statistics.median(values)

        # 标准差和方差
        if count > 1:
            std_dev = statistics.stdev(values)
            variance = statistics.variance(values)
        else:
            std_dev = 0.0
            variance = 0.0

        # 百分位数
        percentiles = {}
        for p in self.config.percentile_values:
            percentiles[p] = np.percentile(values, p)

        return Statistics(
            count=count,
            min=min_val,
            max=max_val,
            mean=mean_val,
            median=median_val,
            std_dev=std_dev,
            variance=variance,
            percentiles=percentiles
        )

    def detect_anomalies(self, metrics: List[Dict[str, Any]]) -> List[Anomaly]:
        """
        检测性能异常

        Args:
            metrics: 指标数据列表

        Returns:
            List[Anomaly]: 异常列表
        """
        anomalies = []

        # 按指标分组
        metric_groups = defaultdict(list)
        for m in metrics:
            for key, value in m.items():
                if isinstance(value, (int, float)) and key not in ['timestamp']:
                    metric_groups[key].append((m.get('timestamp', datetime.now()), value))

        # 对每个指标检测异常
        for metric_name, values in metric_groups.items():
            if len(values) < 3:  # 需要至少3个数据点
                continue

            # 提取数值
            numeric_values = [v[1] for v in values]
            mean_val = statistics.mean(numeric_values)
            std_dev = statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0

            if std_dev == 0:
                continue

            # 检测异常
            for timestamp, value in values:
                z_score = abs((value - mean_val) / std_dev)

                if z_score > self.config.anomaly_threshold:
                    expected_range = (
                        mean_val - self.config.anomaly_threshold * std_dev,
                        mean_val + self.config.anomaly_threshold * std_dev
                    )

                    # 确定严重程度
                    if z_score > 4.0:
                        severity = "critical"
                    elif z_score > 3.0:
                        severity = "high"
                    elif z_score > 2.5:
                        severity = "medium"
                    else:
                        severity = "low"

                    anomaly = Anomaly(
                        timestamp=timestamp,
                        metric_name=metric_name,
                        value=value,
                        expected_range=expected_range,
                        anomaly_score=z_score,
                        severity=severity,
                        description=f"Detected {severity} anomaly for {metric_name}: {value:.2f} (z-score: {z_score:.2f})"
                    )

                    anomalies.append(anomaly)

        logger.info(f"Detected {len(anomalies)} anomalies")
        return anomalies

    def compare_benchmarks(self, baseline: List[Dict[str, Any]],
                          current: List[Dict[str, Any]],
                          baseline_name: str = "Baseline",
                          current_name: str = "Current") -> ComparisonResult:
        """
        对比基准测试结果

        Args:
            baseline: 基准测试数据
            current: 当前测试数据
            baseline_name: 基准名称
            current_name: 当前名称

        Returns:
            ComparisonResult: 对比结果
        """
        metric_comparisons = {}
        regression_count = 0
        improvement_count = 0

        # 收集所有指标
        baseline_metrics = set()
        current_metrics = set()

        for m in baseline:
            baseline_metrics.update(m.keys())

        for m in current:
            current_metrics.update(m.keys())

        common_metrics = baseline_metrics & current_metrics
        common_metrics.discard('timestamp')

        # 对比每个指标
        for metric_name in common_metrics:
            baseline_values = [m[metric_name] for m in baseline if metric_name in m and isinstance(m[metric_name], (int, float))]
            current_values = [m[metric_name] for m in current if metric_name in m and isinstance(m[metric_name], (int, float))]

            if not baseline_values or not current_values:
                continue

            baseline_mean = statistics.mean(baseline_values)
            current_mean = statistics.mean(current_values)

            change = current_mean - baseline_mean
            change_percent = (change / baseline_mean * 100) if baseline_mean != 0 else 0

            metric_comparisons[metric_name] = {
                'baseline_mean': baseline_mean,
                'current_mean': current_mean,
                'change': change,
                'change_percent': change_percent
            }

            # 判断是否为回归或改进
            # 注意：对于某些指标（如延迟），值越小越好
            is_positive_metric = metric_name in ['throughput', 'success_rate']
            is_negative_metric = metric_name in ['latency', 'cpu_utilization', 'memory_usage']

            if is_positive_metric and change < 0:
                regression_count += 1
            elif is_negative_metric and change > 0:
                regression_count += 1
            elif is_positive_metric and change > 0:
                improvement_count += 1
            elif is_negative_metric and change < 0:
                improvement_count += 1

        # 计算总体评分
        total_changes = len(metric_comparisons)
        if total_changes > 0:
            overall_score = (improvement_count - regression_count) / total_changes * 100
        else:
            overall_score = 0

        regression_detected = regression_count > 0
        improvements_detected = improvement_count > 0

        return ComparisonResult(
            baseline_name=baseline_name,
            current_name=current_name,
            metric_comparisons=metric_comparisons,
            regression_detected=regression_detected,
            improvements_detected=improvements_detected,
            overall_score=overall_score
        )

    def generate_recommendations(self, analysis_result: AnalysisResult) -> List[Recommendation]:
        """
        生成优化建议

        Args:
            analysis_result: 分析结果

        Returns:
            List[Recommendation]: 优化建议列表
        """
        recommendations = []

        # 基于异常生成建议
        for anomaly in analysis_result.anomalies:
            if anomaly.severity in ['high', 'critical']:
                recommendation = self._generate_anomaly_recommendation(anomaly)
                recommendations.append(recommendation)

        # 基于统计指标生成建议
        for metric_name, stats in analysis_result.statistics.items():
            # CPU利用率建议
            if metric_name == 'cpu_utilization':
                if stats.mean > 80:
                    recommendations.append(Recommendation(
                        category="resource",
                        priority="high",
                        title="CPU利用率过高",
                        description=f"CPU平均利用率达到{stats.mean:.1f}%，建议优化",
                        impact="可减少CPU使用率10-20%",
                        effort="medium",
                        metrics=[metric_name],
                        actions=[
                            "优化算法实现",
                            "增加批处理大小",
                            "使用多线程并行处理",
                            "减少不必要的计算"
                        ]
                    ))
                elif stats.mean < 30:
                    recommendations.append(Recommendation(
                        category="resource",
                        priority="low",
                        title="CPU利用率偏低",
                        description=f"CPU平均利用率仅为{stats.mean:.1}%，资源利用不足",
                        impact="可提高系统吞吐量",
                        effort="low",
                        metrics=[metric_name],
                        actions=[
                            "增加并发度",
                            "优化负载均衡",
                            "调整批处理策略"
                        ]
                    ))

            # 内存使用建议
            if metric_name == 'memory_usage':
                if stats.mean > 3500:  # MB
                    recommendations.append(Recommendation(
                        category="resource",
                        priority="high",
                        title="内存使用过高",
                        description=f"内存平均使用{stats.mean:.0f}MB，可能导致OOM",
                        impact="可减少内存使用500MB-1GB",
                        effort="medium",
                        metrics=[metric_name],
                        actions=[
                            "优化内存管理",
                            "减少批处理大小",
                            "及时释放不需要的内存",
                            "使用内存映射技术"
                        ]
                    ))

            # 延迟建议
            if metric_name == 'latency_p95':
                if stats.mean > 60:
                    recommendations.append(Recommendation(
                        category="algorithm",
                        priority="high",
                        title="延迟过高",
                        description=f"P95延迟达到{stats.mean:.1f}秒，影响用户体验",
                        impact="可降低延迟30-50%",
                        effort="high",
                        metrics=[metric_name],
                        actions=[
                            "优化模型结构",
                            "使用更高效的算子",
                            "启用模型量化",
                            "优化数据加载策略"
                        ]
                    ))

            # 吞吐量建议
            if metric_name == 'throughput':
                if stats.mean < 10:
                    recommendations.append(Recommendation(
                        category="performance",
                        priority="high",
                        title="吞吐量不足",
                        description=f"吞吐量仅为{stats.mean:.1f}模型/分钟，未达目标",
                        impact="可提高吞吐量50-100%",
                        effort="high",
                        metrics=[metric_name],
                        actions=[
                            "优化模型转换流程",
                            "增加并发处理",
                            "使用流水线并行",
                            "启用硬件加速"
                        ]
                    ))

        # 基于趋势生成建议
        for metric_name, trend in analysis_result.trends.items():
            if trend.trend_direction == "increasing" and metric_name in ['cpu_utilization', 'memory_usage']:
                recommendations.append(Recommendation(
                    category="stability",
                    priority="medium",
                    title=f"{metric_name}呈上升趋势",
                    description=f"{metric_name}持续上升，可能存在资源泄漏",
                    impact="防止系统资源耗尽",
                    effort="medium",
                    metrics=[metric_name],
                    actions=[
                        "检查资源泄漏",
                        "优化内存管理",
                        "定期重启服务",
                        "监控资源使用趋势"
                    ]
                ))

        # 去重
        unique_recommendations = []
        seen_titles = set()
        for rec in recommendations:
            if rec.title not in seen_titles:
                unique_recommendations.append(rec)
                seen_titles.add(rec.title)

        logger.info(f"Generated {len(unique_recommendations)} recommendations")
        return unique_recommendations

    def _generate_anomaly_recommendation(self, anomaly: Anomaly) -> Recommendation:
        """基于异常生成建议"""
        category_map = {
            'cpu_utilization': 'resource',
            'memory_usage': 'resource',
            'gpu_utilization': 'resource',
            'throughput': 'performance',
            'latency': 'algorithm',
            'error_rate': 'stability'
        }

        category = category_map.get(anomaly.metric_name, 'performance')
        priority = anomaly.severity

        return Recommendation(
            category=category,
            priority=priority,
            title=f"检测到{anomaly.metric_name}异常",
            description=anomaly.description,
            impact="需立即处理以防止系统性能下降",
            effort="high" if priority == "critical" else "medium",
            metrics=[anomaly.metric_name],
            actions=[
                f"分析{anomaly.metric_name}异常原因",
                "检查相关日志和指标",
                "调整系统配置",
                "重启相关服务（如必要）"
            ]
        )

    def trend_analysis(self, historical_data: List[Dict[str, Any]],
                      metric_name: str) -> TrendAnalysis:
        """
        趋势分析

        Args:
            historical_data: 历史数据
            metric_name: 指标名称

        Returns:
            TrendAnalysis: 趋势分析结果
        """
        # 提取时间序列数据
        time_series = []
        for m in historical_data:
            if metric_name in m and 'timestamp' in m:
                try:
                    timestamp = datetime.fromisoformat(m['timestamp']) if isinstance(m['timestamp'], str) else m['timestamp']
                    value = m[metric_name]
                    if isinstance(value, (int, float)):
                        time_series.append((timestamp, value))
                except Exception:
                    continue

        if len(time_series) < 3:
            return TrendAnalysis(
                metric_name=metric_name,
                trend_direction="stable",
                trend_strength=0.0,
                predicted_values=[],
                confidence_interval=(0, 0),
                changepoints=[]
            )

        # 按时间排序
        time_series.sort(key=lambda x: x[0])
        values = [v[1] for v in time_series]

        # 计算趋势
        n = len(values)
        x = list(range(n))
        slope = np.polyfit(x, values, 1)[0]

        # 确定趋势方向
        if abs(slope) < 0.01:
            trend_direction = "stable"
            trend_strength = 0.0
        elif slope > 0:
            trend_direction = "increasing"
            trend_strength = min(abs(slope) / max(values) * n, 1.0)
        else:
            trend_direction = "decreasing"
            trend_strength = min(abs(slope) / max(values) * n, 1.0)

        # 检查波动性
        if len(values) > 10:
            rolling_std = []
            window = 5
            for i in range(window, len(values)):
                window_data = values[i-window:i]
                rolling_std.append(statistics.stdev(window_data))

            avg_std = statistics.mean(rolling_std)
            if avg_std / statistics.mean(values) > 0.2:
                trend_direction = "volatile"

        # 简单预测（线性回归）
        predicted_values = []
        for i in range(5):  # 预测未来5个点
            pred_x = n + i
            pred_y = np.polyval(np.polyfit(x, values, 1), pred_x)
            predicted_values.append(pred_y)

        # 置信区间
        residuals = [values[i] - np.polyval(np.polyfit(x, values, 1), i) for i in range(n)]
        std_error = statistics.stdev(residuals) if len(residuals) > 1 else 0
        confidence_interval = (predicted_values[-1] - 2 * std_error, predicted_values[-1] + 2 * std_error)

        # 变化点检测（简化版）
        changepoints = []
        if len(values) > 10:
            for i in range(5, len(values) - 5):
                before = statistics.mean(values[i-5:i])
                after = statistics.mean(values[i:i+5])
                change_percent = abs(after - before) / before * 100
                if change_percent > 20:  # 变化超过20%
                    changepoints.append(time_series[i][0])

        return TrendAnalysis(
            metric_name=metric_name,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            predicted_values=predicted_values,
            confidence_interval=confidence_interval,
            changepoints=changepoints
        )

    def analyze(self, metrics: List[Dict[str, Any]],
               baseline_metrics: Optional[List[Dict[str, Any]]] = None) -> AnalysisResult:
        """
        执行完整分析

        Args:
            metrics: 当前指标数据
            baseline_metrics: 基准指标数据（可选）

        Returns:
            AnalysisResult: 分析结果
        """
        logger.info(f"Starting analysis with {len(metrics)} data points")

        analysis_id = f"analysis-{int(datetime.now().timestamp())}"
        start_time = datetime.now()

        # 计算统计指标
        all_metric_names = set()
        for m in metrics:
            all_metric_names.update(m.keys())
        all_metric_names.discard('timestamp')

        statistics_dict = {}
        for metric_name in all_metric_names:
            try:
                stats = self.calculate_statistics(metrics, metric_name)
                statistics_dict[metric_name] = stats
            except Exception as e:
                logger.warning(f"Failed to calculate statistics for {metric_name}: {e}")

        # 检测异常
        anomalies = self.detect_anomalies(metrics)

        # 趋势分析
        trends_dict = {}
        for metric_name in all_metric_names:
            try:
                trend = self.trend_analysis(metrics, metric_name)
                trends_dict[metric_name] = trend
            except Exception as e:
                logger.warning(f"Failed to perform trend analysis for {metric_name}: {e}")

        # 相关性分析
        correlations = self._calculate_correlations(metrics)

        # 生成建议
        analysis_result = AnalysisResult(
            analysis_id=analysis_id,
            start_time=start_time,
            end_time=datetime.now(),
            total_metrics=len(all_metric_names),
            statistics=statistics_dict,
            anomalies=anomalies,
            trends=trends_dict,
            correlations=correlations,
            recommendations=[]
        )

        # 生成建议
        analysis_result.recommendations = self.generate_recommendations(analysis_result)

        logger.info(f"Analysis completed: {analysis_id}")
        return analysis_result

    def _calculate_correlations(self, metrics: List[Dict[str, Any]]) -> Dict[str, float]:
        """计算指标相关性"""
        # 收集所有数值指标
        metric_data = defaultdict(list)
        for m in metrics:
            for key, value in m.items():
                if isinstance(value, (int, float)) and key not in ['timestamp']:
                    metric_data[key].append(value)

        # 计算相关性
        correlations = {}
        metric_names = list(metric_data.keys())

        for i in range(len(metric_names)):
            for j in range(i + 1, len(metric_names)):
                name1 = metric_names[i]
                name2 = metric_names[j]

                if len(metric_data[name1]) == len(metric_data[name2]) and len(metric_data[name1]) > 3:
                    try:
                        corr = np.corrcoef(metric_data[name1], metric_data[name2])[0, 1]
                        if not np.isnan(corr) and abs(corr) > self.config.correlation_threshold:
                            correlations[f"{name1}-{name2}"] = corr
                    except Exception:
                        pass

        return correlations


if __name__ == "__main__":
    # 示例使用
    config = AnalyzerConfig(
        anomaly_threshold=2.0,
        trend_window_size=10,
        percentile_values=[50, 90, 95, 99]
    )

    analyzer = PerformanceAnalyzer(config)

    # 生成示例数据
    metrics = []
    for i in range(100):
        metrics.append({
            'timestamp': datetime.now() - timedelta(minutes=i),
            'cpu_utilization': 50 + np.random.normal(0, 10),
            'memory_usage': 2000 + np.random.normal(0, 200),
            'throughput': 12 + np.random.normal(0, 2),
            'latency_p95': 30 + np.random.normal(0, 5)
        })

    # 执行分析
    result = analyzer.analyze(metrics)

    print(f"Analysis ID: {result.analysis_id}")
    print(f"Total metrics: {result.total_metrics}")
    print(f"Anomalies detected: {len(result.anomalies)}")
    print(f"Recommendations: {len(result.recommendations)}")

    # 输出建议
    for rec in result.recommendations:
        print(f"\n{rec.priority.upper()}: {rec.title}")
        print(f"  {rec.description}")
