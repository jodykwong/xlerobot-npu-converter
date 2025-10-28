"""
性能分析器单元测试

测试AlgorithmPerformanceAnalyzer的所有功能。
"""

import pytest
import sys
import os
import time
from datetime import datetime, timedelta

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../src'))

from npu_converter.extensions.analysis.algorithm_performance_analyzer import (
    AlgorithmPerformanceAnalyzer,
    PerformanceMetric,
    PerformanceSnapshot,
    PerformanceReport
)


class TestPerformanceMetric:
    """性能指标测试"""

    def test_metric_creation(self):
        """测试指标创建"""
        metric = PerformanceMetric(
            name="latency",
            value=0.05,
            unit="s",
            timestamp=time.time()
        )

        assert metric.name == "latency"
        assert metric.value == 0.05
        assert metric.unit == "s"
        assert metric.timestamp is not None

    def test_metric_aggregation_min(self):
        """测试最小值聚合"""
        metric = PerformanceMetric(
            name="latency",
            value=0.05,
            unit="s"
        )

        aggregation = MetricAggregation.MIN
        assert aggregation == MetricAggregation.MIN

    def test_metric_aggregation_max(self):
        """测试最大值聚合"""
        aggregation = MetricAggregation.MAX
        assert aggregation == MetricAggregation.MAX

    def test_metric_aggregation_avg(self):
        """测试平均值聚合"""
        aggregation = MetricAggregation.AVG
        assert aggregation == MetricAggregation.AVG

    def test_metric_aggregation_sum(self):
        """测试求和聚合"""
        aggregation = MetricAggregation.SUM
        assert aggregation == MetricAggregation.SUM


class TestMetricSnapshot:
    """指标快照测试"""

    def test_snapshot_creation(self):
        """测试快照创建"""
        snapshot = MetricSnapshot(
            algorithm_id="test_algo",
            execution_time=0.05,
            timestamp=time.time(),
            custom_metrics={
                "accuracy": 0.92,
                "memory_usage": 100
            }
        )

        assert snapshot.algorithm_id == "test_algo"
        assert snapshot.execution_time == 0.05
        assert "accuracy" in snapshot.custom_metrics
        assert "memory_usage" in snapshot.custom_metrics

    def test_snapshot_default_timestamp(self):
        """测试快照默认时间戳"""
        snapshot = MetricSnapshot(
            algorithm_id="test_algo",
            execution_time=0.05
        )

        assert snapshot.timestamp is not None


class TestPerformanceReport:
    """性能报告测试"""

    def test_report_creation(self):
        """测试报告创建"""
        report = PerformanceReport(
            algorithm_id="test_algo",
            start_time=time.time() - 100,
            end_time=time.time()
        )

        assert report.algorithm_id == "test_algo"
        assert report.total_requests > 0
        assert report.successful_requests > 0
        assert report.failed_requests == 0

    def test_report_with_metrics(self):
        """测试带指标的报告"""
        report = PerformanceReport(
            algorithm_id="test_algo",
            start_time=time.time() - 100,
            end_time=time.time(),
            metrics={
                "latency": {"min": 0.01, "max": 0.1, "avg": 0.05, "count": 100}
            }
        )

        assert "latency" in report.metrics


class TestPerformanceTrend:
    """性能趋势测试"""

    def test_trend_creation(self):
        """测试趋势创建"""
        trend = PerformanceTrend(
            algorithm_id="test_algo",
            metric_name="latency",
            time_points=[time.time() - 10, time.time() - 5, time.time()],
            values=[0.06, 0.055, 0.05],
            unit="s"
        )

        assert trend.algorithm_id == "test_algo"
        assert trend.metric_name == "latency"
        assert len(trend.time_points) == 3
        assert len(trend.values) == 3

    def test_trend_calculation(self):
        """测试趋势计算"""
        trend = PerformanceTrend(
            algorithm_id="test_algo",
            metric_name="accuracy",
            time_points=[time.time() - 10, time.time()],
            values=[0.90, 0.92],
            unit="%"
        )

        # 验证趋势方向（上升）
        assert trend.values[-1] > trend.values[0]


class TestAlgorithmPerformanceAnalyzer:
    """性能分析器测试"""

    def test_initialization(self):
        """测试初始化"""
        analyzer = AlgorithmPerformanceAnalyzer()
        assert analyzer._monitoring_targets == {}
        assert len(algorithm_performance_analyzer._metrics) == 0
        assert len(analyzer._snapshots) == 0
        assert len(analyzer._performance_history) == 0

    def test_start_monitoring_single_algorithm(self):
        """测试监控单个算法"""
        analyzer = AlgorithmPerformanceAnalyzer()

        success = analyzer.start_monitoring(["algo_1"])

        assert success
        assert "algo_1" in analyzer._monitoring_targets

    def test_start_monitoring_multiple_algorithms(self):
        """测试监控多个算法"""
        analyzer = AlgorithmPerformanceAnalyzer()

        success = analyzer.start_monitoring(["algo_1", "algo_2", "algo_3"])

        assert success
        assert len(analyzer._monitoring_targets) == 3
        assert "algo_1" in analyzer._monitoring_targets
        assert "algo_2" in analyzer._monitoring_targets
        assert "algo_3" in analyzer._monitoring_targets

    def test_start_monitoring_duplicate_algorithms(self):
        """测试监控重复算法"""
        analyzer = AlgorithmPerformanceAnalyzer()

        success1 = analyzer.start_monitoring(["algo_1"])
        success2 = analyzer.start_monitoring(["algo_1"])

        # 重复监控应该允许但不会重复添加
        assert success1
        assert success2
        assert len(analyzer._monitoring_targets) == 1

    def test_stop_monitoring(self):
        """测试停止监控"""
        analyzer = AlgorithmPerformanceAnalyzer()

        analyzer.start_monitoring(["algo_1"])
        success = analyzer.stop_monitoring("algo_1")

        assert success
        assert "algo_1" not in analyzer._monitoring_targets

    def test_stop_nonexistent_monitoring(self):
        """测试停止不存在的监控"""
        analyzer = AlgorithmPerformanceAnalyzer()

        success = analyzer.stop_monitoring("nonexistent_algo")

        assert not success

    def test_record_metric(self):
        """测试记录指标"""
        analyzer = AlgorithmPerformanceAnalyzer()

        analyzer.start_monitoring(["algo_1"])
        success = analyzer.record_metric(
            "algo_1",
            "latency",
            0.05,
            "s"
        )

        assert success
        assert "algo_1" in analyzer._metrics
        assert "latency" in analyzer._metrics["algo_1"]
        assert len(analyzer._metrics["algo_1"]["latency"]) == 1

    def test_record_multiple_metrics(self):
        """测试记录多个指标"""
        analyzer = AlgorithmPerformanceAnalyzer()

        analyzer.start_monitoring(["algo_1"])

        analyzer.record_metric("algo_1", "latency", 0.05, "s")
        analyzer.record_metric("algo_1", "accuracy", 0.92, "%")
        analyzer.record_metric("algo_1", "memory", 100, "MB")

        assert len(analyzer._metrics["algo_1"]) == 3
        assert "latency" in analyzer._metrics["algo_1"]
        assert "accuracy" in analyzer._metrics["algo_1"]
        assert "memory" in analyzer._metrics["algo_1"]

    def test_record_metric_not_monitoring(self):
        """测试记录未监控算法的指标"""
        analyzer = AlgorithmPerformanceAnalyzer()

        # 不启动监控直接记录
        success = analyzer.record_metric(
            "algo_not_monitored",
            "latency",
            0.05,
            "s"
        )

        assert success  # 允许记录但不会启动监控
        assert "algo_not_monitored" not in analyzer._monitoring_targets

    def test_take_snapshot(self):
        """测试拍摄快照"""
        analyzer = AlgorithmPerformanceAnalyzer()

        analyzer.start_monitoring(["algo_1"])
        snapshot = analyzer.take_snapshot(
            "algo_1",
            0.05,
            accuracy=0.92,
            memory=100
        )

        assert isinstance(snapshot, MetricSnapshot)
        assert snapshot.algorithm_id == "algo_1"
        assert snapshot.execution_time == 0.05
        assert snapshot.custom_metrics["accuracy"] == 0.92
        assert snapshot.custom_metrics["memory"] == 100

    def test_take_snapshot_not_monitoring(self):
        """测试为未监控算法拍摄快照"""
        analyzer = AlgorithmPerformanceAnalyzer()

        snapshot = analyzer.take_snapshot(
            "algo_not_monitored",
            0.05,
            accuracy=0.92
        )

        # 允许拍摄快照但不会自动监控
        assert isinstance(snapshot, MetricSnapshot)
        assert "algo_not_monitored" not in analyzer._monitoring_targets

    def test_take_multiple_snapshots(self):
        """测试拍摄多个快照"""
        analyzer = AlgorithmPerformanceAnalyzer()

        analyzer.start_monitoring(["algo_1"])

        for i in range(10):
            analyzer.take_snapshot(
                "algo_1",
                0.05 + i * 0.001,
                accuracy=0.90 + i * 0.001
            )

        assert "algo_1" in analyzer._snapshots
        assert len(analyzer._snapshots["algo_1"]) == 10

    def test_analyze_performance(self):
        """测试性能分析"""
        analyzer = AlgorithmPerformanceAnalyzer()

        analyzer.start_monitoring(["algo_1"])

        # 记录多个指标
        for i in range(10):
            analyzer.record_metric("algo_1", "latency", 0.05 + i * 0.001, "s")
            analyzer.record_metric("algo_1", "accuracy", 0.92 + i * 0.001, "%")

        report = analyzer.analyze_performance("algo_1")

        assert isinstance(report, PerformanceReport)
        assert report.algorithm_id == "algo_1"
        assert report.total_requests >= 10
        assert "latency" in report.metrics
        assert "accuracy" in report.metrics

    def test_analyze_performance_with_time_window(self):
        """测试带时间窗口的性能分析"""
        analyzer = AlgorithmPerformanceAnalyzer()

        analyzer.start_monitoring(["algo_1"])

        # 记录时间戳较早的指标
        old_time = time.time() - 100
        analyzer.record_metric("algo_1", "latency", 0.10, "s", timestamp=old_time)

        # 记录时间戳较晚的指标
        recent_time = time.time() - 10
        analyzer.record_metric("algo_1", "latency", 0.05, "s", timestamp=recent_time)

        # 分析最近60秒的数据
        report = analyzer.analyze_performance("algo_1", time_window_seconds=60)

        assert isinstance(report, PerformanceReport)

    def test_analyze_nonexistent_algorithm(self):
        """测试分析不存在的算法"""
        analyzer = AlgorithmPerformanceAnalyzer()

        report = analyzer.analyze_performance("nonexistent_algo")

        assert report is None

    def test_get_performance_trends(self):
        """测试获取性能趋势"""
        analyzer = AlgorithmPerformanceAnalyzer()

        analyzer.start_monitoring(["algo_1"])

        # 记录时间序列数据
        base_time = time.time() - 100
        for i in range(10):
            timestamp = base_time + i * 10
            analyzer.record_metric(
                "algo_1",
                "latency",
                0.05 + i * 0.001,
                "s",
                timestamp=timestamp
            )

        trend = analyzer.get_performance_trends("algo_1", "latency")

        assert isinstance(trend, PerformanceTrend)
        assert trend.algorithm_id == "algo_1"
        assert trend.metric_name == "latency"
        assert len(trend.values) == 10

    def test_get_performance_trends_nonexistent_algorithm(self):
        """测试获取不存在算法的性能趋势"""
        analyzer = AlgorithmPerformanceAnalyzer()

        trend = analyzer.get_performance_trends("nonexistent_algo", "latency")

        assert trend is None

    def test_get_performance_trends_nonexistent_metric(self):
        """测试获取不存在的指标趋势"""
        analyzer = AlgorithmPerformanceAnalyzer()

        analyzer.start_monitoring(["algo_1"])
        # 不记录任何指标

        trend = analyzer.get_performance_trends("algo_1", "nonexistent_metric")

        assert trend is None

    def test_identify_bottlenecks(self):
        """测试识别瓶颈"""
        analyzer = AlgorithmPerformanceAnalyzer()

        analyzer.start_monitoring(["algo_1"])

        # 记录高性能数据
        for i in range(10):
            analyzer.record_metric("algo_1", "latency", 0.05 + i * 0.001, "s")

        report = analyzer.analyze_performance("algo_1")
        bottlenecks = analyzer.identify_bottlenecks("algo_1")

        assert isinstance(bottlenecks, list)

    def test_identify_bottlenecks_with_high_latency(self):
        """测试识别高延迟瓶颈"""
        analyzer = AlgorithmPerformanceAnalyzer()

        analyzer.start_monitoring(["algo_1"])

        # 记录高延迟数据
        for i in range(10):
            analyzer.record_metric("algo_1", "latency", 0.5 + i * 0.1, "s")

        report = analyzer.analyze_performance("algo_1")
        bottlenecks = analyzer.identify_bottlenecks("algo_1")

        assert isinstance(bottlenecks, list)
        # 如果延迟过高，应该识别出瓶颈
        if report.metrics.get("latency", {}).get("avg", 0) > 0.2:
            assert len(bottlenecks) > 0

    def test_generate_performance_report(self):
        """测试生成性能报告"""
        analyzer = AlgorithmPerformanceAnalyzer()

        analyzer.start_monitoring(["algo_1"])

        for i in range(5):
            analyzer.record_metric("algo_1", "latency", 0.05 + i * 0.001, "s")
            analyzer.take_snapshot("algo_1", 0.05 + i * 0.001)

        report_data = analyzer.generate_performance_report("algo_1")

        assert isinstance(report_data, dict)
        assert "report" in report_data
        assert "trends" in report_data
        assert "bottlenecks" in report_data
        assert "recommendations" in report_data

    def test_export_performance_data(self):
        """测试导出性能数据"""
        analyzer = AlgorithmPerformanceAnalyzer()

        analyzer.start_monitoring(["algo_1"])

        analyzer.record_metric("algo_1", "latency", 0.05, "s")
        analyzer.take_snapshot("algo_1", 0.05)

        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            output_path = f.name

        try:
            success = analyzer.export_performance_data("algo_1", output_path)

            assert success

            # 验证文件存在
            import os
            assert os.path.exists(output_path)

            # 验证文件内容
            import json
            with open(output_path, 'r') as f:
                data = json.load(f)

            assert 'metrics' in data
            assert 'snapshots' in data
            assert 'reports' in data

        finally:
            import os
            if os.path.exists(output_path):
                os.remove(output_path)

    def test_clear_algorithm_data(self):
        """测试清除算法数据"""
        analyzer = AlgorithmPerformanceAnalyzer()

        analyzer.start_monitoring(["algo_1"])

        analyzer.record_metric("algo_1", "latency", 0.05, "s")
        analyzer.take_snapshot("algo_1", 0.05)

        success = analyzer.clear_algorithm_data("algo_1")

        assert success
        assert "algo_1" not in analyzer._metrics
        assert "algo_1" not in analyzer._snapshots

    def test_clear_all_data(self):
        """测试清除所有数据"""
        analyzer = AlgorithmPerformanceAnalyzer()

        analyzer.start_monitoring(["algo_1", "algo_2"])

        analyzer.record_metric("algo_1", "latency", 0.05, "s")
        analyzer.record_metric("algo_2", "latency", 0.06, "s")

        analyzer.clear_all_data()

        assert len(analyzer._metrics) == 0
        assert len(analyzer._snapshots) == 0

    def test_get_statistics(self):
        """测试获取统计信息"""
        analyzer = AlgorithmPerformanceAnalyzer()

        analyzer.start_monitoring(["algo_1"])

        analyzer.record_metric("algo_1", "latency", 0.05, "s")
        analyzer.take_snapshot("algo_1", 0.05)

        stats = analyzer.get_statistics()

        assert isinstance(stats, dict)
        assert 'monitored_algorithms' in stats
        assert 'total_metrics_recorded' in stats
        assert 'total_snapshots' in stats
        assert stats['monitored_algorithms'] >= 1


class TestAlgorithmPerformanceAnalyzerEdgeCases:
    """性能分析器边界情况测试"""

    def test_record_metric_negative_value(self):
        """测试记录负值指标"""
        analyzer = AlgorithmPerformanceAnalyzer()

        analyzer.start_monitoring(["algo_1"])

        # 允许负值指标
        success = analyzer.record_metric(
            "algo_1",
            "score",
            -0.1,
            ""
        )

        assert success

    def test_record_metric_zero_value(self):
        """测试记录零值指标"""
        analyzer = AlgorithmPerformanceAnalyzer()

        analyzer.start_monitoring(["algo_1"])

        success = analyzer.record_metric(
            "algo_1",
            "score",
            0.0,
            ""
        )

        assert success

    def test_record_metric_very_large_value(self):
        """测试记录极大值指标"""
        analyzer = AlgorithmPerformanceAnalyzer()

        analyzer.start_monitoring(["algo_1"])

        success = analyzer.record_metric(
            "algo_1",
            "large_metric",
            1e10,
            ""
        )

        assert success

    def test_take_snapshot_with_many_custom_metrics(self):
        """测试拍摄包含大量自定义指标的快照"""
        analyzer = AlgorithmPerformanceAnalyzer()

        analyzer.start_monitoring(["algo_1"])

        custom_metrics = {f"metric_{i}": i * 0.1 for i in range(100)}

        snapshot = analyzer.take_snapshot(
            "algo_1",
            0.05,
            **custom_metrics
        )

        assert isinstance(snapshot, MetricSnapshot)
        assert len(snapshot.custom_metrics) == 100

    def test_analyze_performance_with_no_data(self):
        """测试分析无数据的算法"""
        analyzer = AlgorithmPerformanceAnalyzer()

        analyzer.start_monitoring(["algo_1"])
        # 不记录任何指标

        report = analyzer.analyze_performance("algo_1")

        assert isinstance(report, PerformanceReport)
        assert report.total_requests == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
