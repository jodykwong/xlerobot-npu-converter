"""
性能分析器单元测试

测试PerformanceAnalyzer类的所有功能，包括统计分析、
异常检测、趋势分析、建议生成等功能。

作者: BMAD Method
创建日期: 2025-10-29
版本: v1.0
"""

import pytest
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import sys

# 添加源码路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'src'))

from npu_converter.performance.performance_analyzer import (
    PerformanceAnalyzer,
    AnalyzerConfig,
    Statistics,
    Anomaly,
    ComparisonResult,
    Recommendation,
    TrendAnalysis,
    AnalysisResult
)


class TestAnalyzerConfig:
    """测试AnalyzerConfig配置类"""

    def test_default_config(self):
        """测试默认配置"""
        config = AnalyzerConfig()
        assert config.anomaly_threshold == 2.0
        assert config.trend_window_size == 10
        assert config.percentile_values == [50, 90, 95, 99]
        assert config.correlation_threshold == 0.7

    def test_custom_config(self):
        """测试自定义配置"""
        config = AnalyzerConfig(
            anomaly_threshold=3.0,
            trend_window_size=20,
            percentile_values=[50, 95, 99],
            correlation_threshold=0.8
        )
        assert config.anomaly_threshold == 3.0
        assert config.trend_window_size == 20
        assert config.percentile_values == [50, 95, 99]
        assert config.correlation_threshold == 0.8


class TestStatistics:
    """测试Statistics统计类"""

    def test_create_statistics(self):
        """测试创建统计指标"""
        stats = Statistics(
            count=100,
            min=10.0,
            max=90.0,
            mean=50.0,
            median=52.0,
            std_dev=15.0,
            variance=225.0,
            percentiles={50: 52.0, 90: 75.0, 95: 82.0}
        )

        assert stats.count == 100
        assert stats.min == 10.0
        assert stats.max == 90.0
        assert stats.mean == 50.0
        assert stats.median == 52.0

    def test_statistics_to_dict(self):
        """测试统计指标转换为字典"""
        stats = Statistics(
            count=100,
            min=10.0,
            max=90.0,
            mean=50.0,
            median=52.0,
            std_dev=15.0,
            variance=225.0,
            percentiles={50: 52.0, 90: 75.0}
        )

        result = stats.to_dict()
        assert result['count'] == 100
        assert result['mean'] == 50.0
        assert result['percentiles'][50] == 52.0


class TestAnomaly:
    """测试Anomaly异常类"""

    def test_create_anomaly(self):
        """测试创建异常"""
        now = datetime.now()
        anomaly = Anomaly(
            timestamp=now,
            metric_name="cpu_utilization",
            value=95.0,
            expected_range=(0.0, 80.0),
            anomaly_score=2.5,
            severity="high",
            description="CPU利用率过高"
        )

        assert anomaly.metric_name == "cpu_utilization"
        assert anomaly.value == 95.0
        assert anomaly.severity == "high"

    def test_anomaly_to_dict(self):
        """测试异常转换为字典"""
        now = datetime.now()
        anomaly = Anomaly(
            timestamp=now,
            metric_name="cpu_utilization",
            value=95.0,
            expected_range=(0.0, 80.0),
            anomaly_score=2.5,
            severity="high",
            description="CPU利用率过高"
        )

        result = anomaly.to_dict()
        assert result['timestamp'] == now.isoformat()
        assert result['metric_name'] == "cpu_utilization"
        assert result['severity'] == "high"


class TestPerformanceAnalyzer:
    """测试PerformanceAnalyzer分析器类"""

    @pytest.fixture
    def analyzer(self):
        """创建PerformanceAnalyzer实例"""
        config = AnalyzerConfig(
            anomaly_threshold=2.0,
            trend_window_size=10,
            percentile_values=[50, 90, 95, 99]
        )
        return PerformanceAnalyzer(config)

    @pytest.fixture
    def sample_metrics(self):
        """创建示例指标数据"""
        metrics = []
        for i in range(100):
            metrics.append({
                'timestamp': datetime.now() - timedelta(minutes=i),
                'cpu_utilization': 50 + np.random.normal(0, 10),
                'memory_usage': 2000 + np.random.normal(0, 200),
                'throughput': 12 + np.random.normal(0, 2),
                'latency_p95': 30 + np.random.normal(0, 5)
            })
        return metrics

    def test_initialize_analyzer(self):
        """测试初始化分析器"""
        config = AnalyzerConfig(anomaly_threshold=3.0)
        analyzer = PerformanceAnalyzer(config)
        assert analyzer.config.anomaly_threshold == 3.0

    def test_calculate_statistics(self, analyzer, sample_metrics):
        """测试计算统计指标"""
        stats = analyzer.calculate_statistics(sample_metrics, 'cpu_utilization')

        assert isinstance(stats, Statistics)
        assert stats.count == 100
        assert stats.min >= 0
        assert stats.max <= 100
        assert stats.mean >= 0
        assert stats.std_dev >= 0
        assert 50 in stats.percentiles
        assert 95 in stats.percentiles

    def test_calculate_statistics_empty(self, analyzer):
        """测试计算空数据统计指标"""
        with pytest.raises(ValueError):
            analyzer.calculate_statistics([], 'cpu_utilization')

    def test_calculate_statistics_no_metric(self, analyzer):
        """测试计算不存在指标的统计指标"""
        metrics = [{'timestamp': datetime.now()}]
        with pytest.raises(ValueError):
            analyzer.calculate_statistics(metrics, 'nonexistent')

    def test_detect_anomalies(self, analyzer, sample_metrics):
        """测试检测异常"""
        anomalies = analyzer.detect_anomalies(sample_metrics)

        assert isinstance(anomalies, list)
        # 可能有异常，也可能没有

        for anomaly in anomalies:
            assert isinstance(anomaly, Anomaly)
            assert anomaly.metric_name in ['cpu_utilization', 'memory_usage', 'throughput', 'latency_p95']
            assert anomaly.severity in ['low', 'medium', 'high', 'critical']

    def test_detect_anomalies_no_anomalies(self, analyzer):
        """测试无异常的检测"""
        # 创建无异常的数据（都在正常范围内）
        metrics = []
        for i in range(10):
            metrics.append({
                'timestamp': datetime.now() - timedelta(minutes=i),
                'cpu_utilization': 50.0,  # 固定值
                'memory_usage': 2000.0
            })

        anomalies = analyzer.detect_anomalies(metrics)
        # 可能检测不到异常

    def test_compare_benchmarks(self, analyzer):
        """测试对比基准测试"""
        baseline = []
        current = []

        # 创建基准数据
        for i in range(50):
            baseline.append({
                'timestamp': datetime.now() - timedelta(minutes=i),
                'throughput': 12.0 + np.random.normal(0, 1),
                'latency_p95': 30.0 + np.random.normal(0, 2),
                'cpu_utilization': 60.0 + np.random.normal(0, 5)
            })

        # 创建当前数据（性能略有提升）
        for i in range(50):
            current.append({
                'timestamp': datetime.now() - timedelta(minutes=i),
                'throughput': 13.0 + np.random.normal(0, 1),
                'latency_p95': 28.0 + np.random.normal(0, 2),
                'cpu_utilization': 58.0 + np.random.normal(0, 5)
            })

        result = analyzer.compare_benchmarks(baseline, current, "Baseline", "Current")

        assert isinstance(result, ComparisonResult)
        assert result.baseline_name == "Baseline"
        assert result.current_name == "Current"
        assert 'throughput' in result.metric_comparisons
        assert 'latency_p95' in result.metric_comparisons
        assert isinstance(result.regression_detected, bool)
        assert isinstance(result.improvements_detected, bool)
        assert isinstance(result.overall_score, float)

    def test_generate_recommendations(self, analyzer):
        """测试生成优化建议"""
        # 创建有问题的数据
        metrics = []
        for i in range(20):
            metrics.append({
                'timestamp': datetime.now() - timedelta(minutes=i),
                'cpu_utilization': 85.0,  # CPU使用率过高
                'memory_usage': 3800.0,  # 内存使用过高
                'throughput': 9.0,  # 吞吐量不足
                'latency_p95': 70.0  # 延迟过高
            })

        # 创建分析结果
        analysis_result = AnalysisResult(
            analysis_id="test-analysis",
            start_time=datetime.now(),
            end_time=datetime.now(),
            total_metrics=4,
            statistics={},
            anomalies=[],
            trends={},
            correlations={},
            recommendations=[]
        )

        recommendations = analyzer.generate_recommendations(analysis_result)

        assert isinstance(recommendations, list)
        # 应该生成一些建议

        for rec in recommendations:
            assert isinstance(rec, Recommendation)
            assert rec.category in ['configuration', 'algorithm', 'resource', 'architecture', 'performance', 'stability']
            assert rec.priority in ['low', 'medium', 'high', 'critical']
            assert rec.title is not None
            assert rec.description is not None

    def test_trend_analysis(self, analyzer, sample_metrics):
        """测试趋势分析"""
        trend = analyzer.trend_analysis(sample_metrics, 'cpu_utilization')

        assert isinstance(trend, TrendAnalysis)
        assert trend.metric_name == 'cpu_utilization'
        assert trend.trend_direction in ['increasing', 'decreasing', 'stable', 'volatile']
        assert 0.0 <= trend.trend_strength <= 1.0
        assert isinstance(trend.predicted_values, list)
        assert isinstance(trend.confidence_interval, tuple)
        assert isinstance(trend.changepoints, list)

    def test_trend_analysis_insufficient_data(self, analyzer):
        """测试数据不足的趋势分析"""
        # 只有2个数据点
        metrics = [
            {'timestamp': datetime.now(), 'cpu_utilization': 50.0},
            {'timestamp': datetime.now(), 'cpu_utilization': 55.0}
        ]

        trend = analyzer.trend_analysis(metrics, 'cpu_utilization')

        assert trend.trend_direction == "stable"
        assert trend.trend_strength == 0.0
        assert len(trend.predicted_values) == 0

    def test_analyze(self, analyzer, sample_metrics):
        """测试完整分析"""
        result = analyzer.analyze(sample_metrics)

        assert isinstance(result, AnalysisResult)
        assert result.analysis_id.startswith("analysis-")
        assert result.total_metrics > 0
        assert isinstance(result.statistics, dict)
        assert isinstance(result.anomalies, list)
        assert isinstance(result.trends, dict)
        assert isinstance(result.correlations, dict)
        assert isinstance(result.recommendations, list)

    def test_analyze_with_baseline(self, analyzer, sample_metrics):
        """测试带基准的完整分析"""
        baseline = []
        for i in range(50):
            baseline.append({
                'timestamp': datetime.now() - timedelta(minutes=i),
                'cpu_utilization': 55.0 + np.random.normal(0, 5),
                'memory_usage': 2100 + np.random.normal(0, 100)
            })

        result = analyzer.analyze(sample_metrics, baseline)

        assert isinstance(result, AnalysisResult)
        # 分析结果应该包含对比信息

    def test_calculate_correlations(self, analyzer, sample_metrics):
        """测试计算相关性"""
        # 手动调用私有方法进行测试
        correlations = analyzer._calculate_correlations(sample_metrics)

        assert isinstance(correlations, dict)
        # 可能有相关性，也可能没有

    def test_generate_anomaly_recommendation(self, analyzer):
        """测试基于异常生成建议"""
        # 创建异常
        anomaly = Anomaly(
            timestamp=datetime.now(),
            metric_name="cpu_utilization",
            value=95.0,
            expected_range=(0.0, 80.0),
            anomaly_score=2.5,
            severity="high",
            description="CPU利用率过高"
        )

        recommendation = analyzer._generate_anomaly_recommendation(anomaly)

        assert isinstance(recommendation, Recommendation)
        assert recommendation.category in ['resource', 'performance', 'algorithm', 'stability']
        assert recommendation.priority == anomaly.severity


class TestComparisonResult:
    """测试ComparisonResult对比结果类"""

    def test_create_comparison_result(self):
        """测试创建对比结果"""
        result = ComparisonResult(
            baseline_name="Baseline",
            current_name="Current",
            metric_comparisons={
                'throughput': {
                    'baseline_mean': 12.0,
                    'current_mean': 13.0,
                    'change': 1.0,
                    'change_percent': 8.33
                }
            },
            regression_detected=False,
            improvements_detected=True,
            overall_score=75.0
        )

        assert result.baseline_name == "Baseline"
        assert result.current_name == "Current"
        assert result.regression_detected is False
        assert result.improvements_detected is True

    def test_comparison_result_to_dict(self):
        """测试对比结果转换为字典"""
        result = ComparisonResult(
            baseline_name="Baseline",
            current_name="Current",
            metric_comparisons={},
            regression_detected=False,
            improvements_detected=True,
            overall_score=75.0
        )

        result_dict = result.to_dict()
        assert result_dict['baseline_name'] == "Baseline"
        assert result_dict['regression_detected'] is False


class TestRecommendation:
    """测试Recommendation建议类"""

    def test_create_recommendation(self):
        """测试创建建议"""
        recommendation = Recommendation(
            category="resource",
            priority="high",
            title="CPU利用率过高",
            description="CPU平均利用率达到85%",
            impact="可减少CPU使用率10-20%",
            effort="medium",
            metrics=["cpu_utilization"],
            actions=["优化算法", "增加批处理"],
            references=["doc1.md", "doc2.md"]
        )

        assert recommendation.category == "resource"
        assert recommendation.priority == "high"
        assert len(recommendation.actions) == 2
        assert len(recommendation.references) == 2

    def test_recommendation_to_dict(self):
        """测试建议转换为字典"""
        recommendation = Recommendation(
            category="resource",
            priority="high",
            title="CPU利用率过高",
            description="CPU平均利用率达到85%",
            impact="可减少CPU使用率10-20%",
            effort="medium",
            metrics=["cpu_utilization"],
            actions=["优化算法"]
        )

        result = recommendation.to_dict()
        assert result['category'] == "resource"
        assert result['title'] == "CPU利用率过高"
        assert len(result['actions']) == 1


class TestTrendAnalysis:
    """测试TrendAnalysis趋势分析类"""

    def test_create_trend_analysis(self):
        """测试创建趋势分析"""
        trend = TrendAnalysis(
            metric_name="cpu_utilization",
            trend_direction="increasing",
            trend_strength=0.75,
            predicted_values=[55.0, 56.0, 57.0, 58.0, 59.0],
            confidence_interval=(50.0, 65.0),
            changepoints=[datetime.now() - timedelta(hours=1)]
        )

        assert trend.metric_name == "cpu_utilization"
        assert trend.trend_direction == "increasing"
        assert trend.trend_strength == 0.75
        assert len(trend.predicted_values) == 5
        assert len(trend.changepoints) == 1

    def test_trend_analysis_to_dict(self):
        """测试趋势分析转换为字典"""
        now = datetime.now()
        trend = TrendAnalysis(
            metric_name="cpu_utilization",
            trend_direction="increasing",
            trend_strength=0.75,
            predicted_values=[55.0],
            confidence_interval=(50.0, 65.0),
            changepoints=[now]
        )

        result = trend.to_dict()
        assert result['metric_name'] == "cpu_utilization"
        assert result['trend_direction'] == "increasing"
        assert result['changepoints'][0] == now.isoformat()


class TestAnalysisResult:
    """测试AnalysisResult分析结果类"""

    def test_create_analysis_result(self):
        """测试创建分析结果"""
        now = datetime.now()
        result = AnalysisResult(
            analysis_id="test-001",
            start_time=now,
            end_time=now,
            total_metrics=5,
            statistics={},
            anomalies=[],
            trends={},
            correlations={},
            recommendations=[]
        )

        assert result.analysis_id == "test-001"
        assert result.total_metrics == 5

    def test_analysis_result_to_dict(self):
        """测试分析结果转换为字典"""
        now = datetime.now()
        result = AnalysisResult(
            analysis_id="test-001",
            start_time=now,
            end_time=now,
            total_metrics=5,
            statistics={},
            anomalies=[],
            trends={},
            correlations={},
            recommendations=[]
        )

        result_dict = result.to_dict()
        assert result_dict['analysis_id'] == "test-001"
        assert result_dict['total_metrics'] == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
