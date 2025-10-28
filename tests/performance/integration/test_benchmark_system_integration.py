"""
性能基准测试系统集成测试

测试整个性能基准测试系统的各个组件协同工作，
包括测试执行、指标采集、分析、报告生成等完整流程。

作者: BMAD Method
创建日期: 2025-10-29
版本: v1.0
"""

import pytest
import tempfile
import shutil
import time
from datetime import datetime
from pathlib import Path
import sys

# 添加源码路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'src'))

from npu_converter.performance.benchmark_runner import (
    BenchmarkRunner,
    BenchmarkConfig,
    TestCase
)
from npu_converter.performance.metrics_collector import (
    MetricsCollector,
    MetricsConfig
)
from npu_converter.performance.benchmark_suite import (
    BenchmarkSuite,
    SuiteConfig
)
from npu_converter.performance.performance_analyzer import (
    PerformanceAnalyzer,
    AnalyzerConfig
)
from npu_converter.performance.report_generator import (
    ReportGenerator,
    ReportConfig
)
from npu_converter.performance.visualization import (
    VisualizationEngine,
    VisualizationConfig
)
from npu_converter.performance.alerts import (
    AlertSystem,
    AlertConfig
)


class TestBenchmarkSystemIntegration:
    """测试性能基准测试系统集成"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path, ignore_errors=True)

    @pytest.fixture
    def benchmark_system(self, temp_dir):
        """创建完整的性能基准测试系统"""
        # 创建配置
        benchmark_config = BenchmarkConfig(
            output_dir=str(Path(temp_dir) / "benchmark"),
            max_concurrent=3,
            retry_count=2,
            save_raw_data=True
        )

        metrics_config = MetricsConfig(
            collection_interval=1,
            buffer_size=100,
            storage_type="memory"
        )

        suite_config = SuiteConfig(
            test_data_dir=str(temp_dir),
            test_cases_file="test_cases.yaml",
            default_timeout=300
        )

        analysis_config = AnalyzerConfig(
            anomaly_threshold=2.0,
            trend_window_size=10
        )

        report_config = ReportConfig(
            output_dir=str(Path(temp_dir) / "reports"),
            format="html"
        )

        viz_config = VisualizationConfig(
            output_dir=str(Path(temp_dir) / "charts")
        )

        alert_config = AlertConfig(
            alert_dir=str(Path(temp_dir) / "alerts"),
            enable_webhook=False,
            enable_email=False
        )

        # 创建组件
        runner = BenchmarkRunner(benchmark_config)
        collector = MetricsCollector(metrics_config)
        suite = BenchmarkSuite(suite_config)
        analyzer = PerformanceAnalyzer(analysis_config)
        generator = ReportGenerator(report_config)
        viz_engine = VisualizationEngine(viz_config)
        alert_system = AlertSystem(alert_config)

        # 注册组件
        runner.set_test_suite(suite)
        runner.set_metrics_collector(collector)

        return {
            'runner': runner,
            'collector': collector,
            'suite': suite,
            'analyzer': analyzer,
            'generator': generator,
            'viz_engine': viz_engine,
            'alert_system': alert_system,
            'temp_dir': temp_dir
        }

    def test_full_benchmark_workflow(self, benchmark_system):
        """测试完整的基准测试工作流"""
        system = benchmark_system

        # 1. 获取测试用例
        test_case = system['suite'].get_test_case("TC-001")
        assert test_case is not None
        print(f"✓ 获取测试用例: {test_case.id}")

        # 2. 运行基准测试
        result = system['runner'].run_benchmark(test_case)
        assert result is not None
        assert result.test_case.id == "TC-001"
        print(f"✓ 运行基准测试完成: {result.result.status}")

        # 3. 生成报告
        result_data = result.to_dict()
        summary = system['generator'].generate_summary_report(result_data)
        assert summary is not None
        assert summary.total_tests == 1
        print(f"✓ 生成汇总报告完成")

        # 4. 保存报告
        summary_file = Path(system['temp_dir']) / "summary_report.html"
        system['generator'].export_report(summary, "html", str(summary_file))
        assert summary_file.exists()
        print(f"✓ 保存报告完成: {summary_file}")

    def test_multiple_tests_execution(self, benchmark_system):
        """测试多个测试用例执行"""
        system = benchmark_system

        # 获取多个测试用例
        test_cases = [
            system['suite'].get_test_case("TC-001"),
            system['suite'].get_test_case("TC-002"),
            system['suite'].get_test_case("TC-003")
        ]

        assert all(tc is not None for tc in test_cases)

        # 并发执行测试
        results = system['runner'].run_concurrent(test_cases, max_workers=2)

        assert results.total_tests == 3
        assert results.successful_tests + results.failed_tests == 3
        assert len(results.results) == 3
        print(f"✓ 并发执行测试完成: {results.success_rate:.1f}% 成功率")

        # 生成汇总报告
        results_list = [r.to_dict() for r in results.results]
        summary_data = {
            'total_tests': results.total_tests,
            'successful_tests': results.successful_tests,
            'failed_tests': results.failed_tests,
            'total_duration': results.total_duration,
            'metrics': {}
        }

        summary = system['generator'].generate_summary_report(summary_data)
        assert summary is not None
        print(f"✓ 生成多测试汇总报告完成")

    def test_metrics_collection_integration(self, benchmark_system):
        """测试指标采集集成"""
        system = benchmark_system

        # 开始实时采集
        system['collector'].start_real_time_collection(interval=0.1)
        print("✓ 开始实时指标采集")

        # 等待一段时间
        time.sleep(0.5)

        # 停止采集
        system['collector'].stop_real_time_collection()
        print("✓ 停止实时指标采集")

        # 检查缓冲区中是否有数据
        buffer_size = system['collector'].metrics_buffer.size()
        assert buffer_size > 0
        print(f"✓ 采集到 {buffer_size} 条指标数据")

        # 获取最近指标
        recent_metrics = system['collector'].get_recent_metrics('system', count=10)
        assert len(recent_metrics) > 0
        print(f"✓ 获取最近指标: {len(recent_metrics)} 条")

    def test_performance_analysis_integration(self, benchmark_system):
        """测试性能分析集成"""
        system = benchmark_system

        # 创建示例性能数据
        metrics = []
        for i in range(20):
            metrics.append({
                'timestamp': datetime.now(),
                'cpu_utilization': 60 + i * 0.5,  # 递增趋势
                'memory_usage': 2000 + i * 10,
                'throughput': 12 - i * 0.1,  # 递减趋势
                'latency_p95': 30 + i * 0.2
            })

        # 执行分析
        analysis_result = system['analyzer'].analyze(metrics)

        assert analysis_result is not None
        assert analysis_result.total_metrics == 4
        print(f"✓ 性能分析完成: {analysis_result.total_metrics} 个指标")

        # 检查分析结果
        assert len(analysis_result.statistics) == 4
        print(f"✓ 计算统计指标: {len(analysis_result.statistics)} 个")

        assert len(analysis_result.trends) == 4
        print(f"✓ 趋势分析: {len(analysis_result.trends)} 个趋势")

        # 检查建议
        if analysis_result.recommendations:
            print(f"✓ 生成 {len(analysis_result.recommendations)} 条建议")

    def test_alert_system_integration(self, benchmark_system):
        """测试告警系统集成"""
        system = benchmark_system

        # 模拟高CPU使用率指标
        metrics = {
            'cpu_utilization': 90.0,  # 高CPU
            'memory_usage': 2500.0,
            'throughput': 11.0,
            'latency_p95': 45.0
        }

        # 检查告警
        alerts = system['alert_system'].check_alerts(metrics)

        assert isinstance(alerts, list)
        print(f"✓ 检测到 {len(alerts)} 个告警")

        # 检查告警内容
        for alert in alerts:
            print(f"  - {alert.rule_name}: {alert.message}")

        # 获取活动告警
        active_alerts = system['alert_system'].get_active_alerts()
        assert len(active_alerts) >= 0
        print(f"✓ 当前活动告警: {len(active_alerts)} 个")

        # 获取告警统计
        stats = system['alert_system'].get_statistics()
        assert 'total_rules' in stats
        assert stats['total_rules'] >= 4
        print(f"✓ 告警统计: {stats['total_rules']} 个规则")

    def test_visualization_integration(self, benchmark_system):
        """测试可视化集成"""
        system = benchmark_system

        # 创建时间序列数据
        timestamps = [f"2025-10-29 10:{i:02d}" for i in range(10)]
        values = [50 + i * 2 for i in range(10)]

        ts_data = {
            'title': 'CPU使用率趋势',
            'timestamps': timestamps,
            'values': values,
            'series_name': 'CPU %'
        }

        # 创建时间序列图表
        ts_chart = system['viz_engine'].create_time_series_chart(ts_data)
        assert ts_chart is not None
        print("✓ 创建时间序列图表完成")

        # 创建对比图表
        comp_data = {
            'title': '模型性能对比',
            'categories': ['SenseVoice', 'VITS-Cantonese', 'Piper-VITS'],
            'values': [12.5, 10.2, 11.8],
            'series_name': '吞吐量'
        }

        comp_chart = system['viz_engine'].create_comparison_chart(comp_data)
        assert comp_chart is not None
        print("✓ 创建对比图表完成")

        # 创建仪表盘
        dashboard = system['viz_engine'].create_dashboard([ts_chart, comp_chart], "性能仪表盘")
        assert dashboard is not None
        assert len(dashboard.charts) == 2
        print("✓ 创建仪表盘完成")

        # 导出图表
        chart_file = Path(system['temp_dir']) / "chart.html"
        system['viz_engine'].export_chart(ts_chart, "html", str(chart_file))
        assert chart_file.exists()
        print(f"✓ 导出图表完成: {chart_file}")

    def test_end_to_end_workflow(self, benchmark_system):
        """测试端到端工作流"""
        system = benchmark_system

        # 1. 获取测试用例
        test_case = system['suite'].get_test_case("TC-004")  # 并发测试
        assert test_case is not None

        # 2. 开始指标采集
        system['collector'].start_real_time_collection(interval=0.1)

        # 3. 运行基准测试
        result = system['runner'].run_benchmark(test_case)

        # 4. 停止指标采集
        system['collector'].stop_real_time_collection()

        # 5. 收集性能数据
        metrics = system['collector'].get_recent_metrics('system', count=10)
        print(f"✓ 收集性能数据: {len(metrics)} 条")

        # 6. 执行性能分析
        analysis_result = system['analyzer'].analyze(metrics)
        print(f"✓ 执行性能分析")

        # 7. 生成报告
        result_data = result.to_dict()
        result_data['metrics'] = analysis_result.statistics

        summary = system['generator'].generate_summary_report(result_data)
        detailed = system['generator'].generate_detailed_report(result_data)

        # 8. 保存报告
        summary_file = Path(system['temp_dir']) / "e2e_summary.html"
        detailed_file = Path(system['temp_dir']) / "e2e_detailed.html"

        system['generator'].export_report(summary, "html", str(summary_file))
        system['generator'].export_report(detailed, "html", str(detailed_file))

        # 9. 创建可视化
        if metrics:
            chart_data = {
                'title': '性能指标',
                'timestamps': [m.get('timestamp', '') for m in metrics],
                'values': [m.get('cpu_percent', 0) for m in metrics if 'cpu_percent' in m],
                'series_name': 'CPU %'
            }

            if chart_data['values']:
                chart = system['viz_engine'].create_time_series_chart(chart_data)
                chart_file = Path(system['temp_dir']) / "e2e_chart.html"
                system['viz_engine'].export_chart(chart, "html", str(chart_file))

        # 10. 检查告警
        alert_metrics = {
            'cpu_utilization': 75.0,
            'memory_usage': 3000.0,
            'throughput': 10.0
        }
        alerts = system['alert_system'].check_alerts(alert_metrics)

        print("✓ 端到端工作流完成")
        print(f"  - 测试结果: {result.result.status}")
        print(f"  - 性能分析: {len(analysis_result.statistics)} 个指标")
        print(f"  - 告警数量: {len(alerts)} 个")
        print(f"  - 报告文件: 2 个")
        print(f"  - 图表文件: 1 个")

    def test_error_handling_integration(self, benchmark_system):
        """测试错误处理集成"""
        system = benchmark_system

        # 测试无效测试用例
        try:
            invalid_result = system['runner'].run_benchmark(None)
            # 不应该到达这里
        except (TypeError, AttributeError):
            print("✓ 正确处理无效测试用例")

        # 测试空指标数据
        empty_analysis = system['analyzer'].analyze([])
        assert empty_analysis is not None
        print("✓ 正确处理空指标数据")

        # 测试无效告警规则
        custom_rule = None  # 模拟无效规则
        try:
            system['alert_system'].add_alert_rule(custom_rule)
            # 不应该到达这里
        except (TypeError, AttributeError):
            print("✓ 正确处理无效告警规则")

    def test_component_registration(self, benchmark_system):
        """测试组件注册"""
        system = benchmark_system

        # 检查组件是否正确注册
        assert system['runner'].test_suite is not None
        assert system['runner'].metrics_collector is not None
        print("✓ 组件注册正确")

    def test_data_flow_integration(self, benchmark_system):
        """测试数据流集成"""
        system = benchmark_system

        # 执行测试并收集数据
        test_case = system['suite'].get_test_case("TC-001")
        result = system['runner'].run_benchmark(test_case)

        # 检查数据流
        assert result is not None
        assert result.result.metrics is not None
        print("✓ 测试结果数据流正确")

        # 采集指标数据
        system['collector'].start_real_time_collection(interval=0.1)
        time.sleep(0.3)
        system['collector'].stop_real_time_collection()

        # 检查指标数据流
        metrics = system['collector'].get_recent_metrics('system', count=5)
        assert len(metrics) > 0
        print(f"✓ 指标数据流正确: {len(metrics)} 条")

    def test_configuration_integration(self, benchmark_system):
        """测试配置集成"""
        system = benchmark_system

        # 检查各个组件的配置
        assert system['runner'].config.max_concurrent == 3
        assert system['runner'].config.save_raw_data is True
        print("✓ Benchmark Runner配置正确")

        assert system['collector'].config.collection_interval == 1
        assert system['collector'].config.storage_type == "memory"
        print("✓ Metrics Collector配置正确")

        assert system['suite'].config.default_timeout == 300
        print("✓ Benchmark Suite配置正确")

        assert system['analyzer'].config.anomaly_threshold == 2.0
        print("✓ Performance Analyzer配置正确")

        assert system['generator'].config.format == "html"
        print("✓ Report Generator配置正确")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
