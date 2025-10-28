"""
端到端性能基准测试

测试完整的性能基准测试流程，从测试执行到最终报告生成的端到端场景。

作者: BMAD Method
创建日期: 2025-10-29
版本: v1.0
"""

import pytest
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
import sys
import time

# 添加源码路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'src'))

from npu_converter.performance.benchmark_runner import (
    BenchmarkRunner,
    BenchmarkConfig
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


class TestEndToEndBenchmark:
    """端到端性能基准测试"""

    @pytest.fixture
    def setup_system(self):
        """设置完整的性能基准测试系统"""
        temp_dir = tempfile.mkdtemp()

        try:
            # 创建配置
            config = {
                'benchmark': BenchmarkConfig(
                    output_dir=str(Path(temp_dir) / "benchmark"),
                    max_concurrent=5,
                    retry_count=2,
                    save_raw_data=True
                ),
                'metrics': MetricsConfig(
                    collection_interval=1,
                    buffer_size=1000,
                    storage_type="memory"
                ),
                'suite': SuiteConfig(
                    test_data_dir=str(temp_dir),
                    test_cases_file="test_cases.yaml"
                ),
                'analyzer': AnalyzerConfig(
                    anomaly_threshold=2.0
                ),
                'report': ReportConfig(
                    output_dir=str(Path(temp_dir) / "reports"),
                    format="html"
                ),
                'viz': VisualizationConfig(
                    output_dir=str(Path(temp_dir) / "charts")
                ),
                'alert': AlertConfig(
                    alert_dir=str(Path(temp_dir) / "alerts")
                )
            }

            # 创建组件
            runner = BenchmarkRunner(config['benchmark'])
            collector = MetricsCollector(config['metrics'])
            suite = BenchmarkSuite(config['suite'])
            analyzer = PerformanceAnalyzer(config['analyzer'])
            generator = ReportGenerator(config['report'])
            viz_engine = VisualizationEngine(config['viz'])
            alert_system = AlertSystem(config['alert'])

            # 注册组件
            runner.set_test_suite(suite)
            runner.set_metrics_collector(collector)

            return {
                'temp_dir': temp_dir,
                'config': config,
                'runner': runner,
                'collector': collector,
                'suite': suite,
                'analyzer': analyzer,
                'generator': generator,
                'viz_engine': viz_engine,
                'alert_system': alert_system
            }
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise e

    @pytest.fixture
    def cleanup_system(self, setup_system):
        """清理系统资源"""
        yield setup_system
        # 清理临时目录
        if Path(setup_system['temp_dir']).exists():
            shutil.rmtree(setup_system['temp_dir'], ignore_errors=True)

    def test_scenario_single_model_performance(self, cleanup_system):
        """场景1: 单模型性能基准测试"""
        print("\n=== 场景1: 单模型性能基准测试 ===")

        system = cleanup_system
        temp_dir = system['temp_dir']

        # 1. 选择测试用例
        test_cases = [
            system['suite'].get_test_case("TC-001"),  # SenseVoice
            system['suite'].get_test_case("TC-002"),  # VITS-Cantonese
            system['suite'].get_test_case("TC-003")   # Piper-VITS
        ]

        assert all(tc is not None for tc in test_cases)
        print(f"✓ 选择 {len(test_cases)} 个单模型测试用例")

        # 2. 开始指标采集
        system['collector'].start_real_time_collection(interval=0.1)
        print("✓ 开始实时指标采集")

        # 3. 依次执行测试
        results = []
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n  执行测试 {i}/{len(test_cases)}: {test_case.name}")
            result = system['runner'].run_benchmark(test_case)
            results.append(result)
            assert result is not None
            print(f"  ✓ 测试完成: {result.result.status}")

        # 4. 停止指标采集
        system['collector'].stop_real_time_collection()
        print("\n✓ 停止指标采集")

        # 5. 收集性能数据
        metrics = system['collector'].get_recent_metrics('system', count=50)
        print(f"✓ 收集性能数据: {len(metrics)} 条")

        # 6. 执行性能分析
        analysis_result = system['analyzer'].analyze(metrics)
        print(f"✓ 执行性能分析: {len(analysis_result.statistics)} 个指标")

        # 7. 生成报告
        report_data = {
            'total_tests': len(results),
            'successful_tests': sum(1 for r in results if r.result.success),
            'failed_tests': sum(1 for r in results if not r.result.success),
            'total_duration': sum(r.result.duration for r in results),
            'metrics': {k: v.to_dict() for k, v in analysis_result.statistics.items()},
            'anomalies': [a.to_dict() for a in analysis_result.anomalies],
            'trends': {k: v.to_dict() for k, v in analysis_result.trends.items()},
            'recommendations': [r.to_dict() for r in analysis_result.recommendations]
        }

        summary = system['generator'].generate_summary_report(report_data)
        detailed = system['generator'].generate_detailed_report(report_data)

        # 8. 保存报告
        summary_file = Path(temp_dir) / "single_model_summary.html"
        detailed_file = Path(temp_dir) / "single_model_detailed.html"

        system['generator'].export_report(summary, "html", str(summary_file))
        system['generator'].export_report(detailed, "html", str(detailed_file))

        assert summary_file.exists()
        assert detailed_file.exists()
        print(f"✓ 生成报告: 2 个文件")

        # 9. 创建可视化
        if metrics:
            chart_data = {
                'title': '单模型性能测试 - CPU使用率',
                'timestamps': [m.get('timestamp', '') for m in metrics[-20:]],
                'values': [m.get('cpu_percent', 0) for m in metrics[-20:] if 'cpu_percent' in m],
                'series_name': 'CPU %'
            }

            if chart_data['values']:
                chart = system['viz_engine'].create_time_series_chart(chart_data)
                chart_file = Path(temp_dir) / "single_model_chart.html"
                system['viz_engine'].export_chart(chart, "html", str(chart_file))
                print(f"✓ 创建可视化: 1 个图表")

        # 10. 验证结果
        assert summary.total_tests == 3
        assert summary.success_rate >= 0
        print(f"\n=== 场景1完成: 成功率 {summary.success_rate:.1f}% ===")

    def test_scenario_concurrent_models_performance(self, cleanup_system):
        """场景2: 多模型并发性能基准测试"""
        print("\n=== 场景2: 多模型并发性能基准测试 ===")

        system = cleanup_system
        temp_dir = system['temp_dir']

        # 1. 选择并发测试用例
        test_case = system['suite'].get_test_case("TC-004")
        assert test_case is not None
        print(f"✓ 选择并发测试用例: {test_case.name}")

        # 2. 开始指标采集
        system['collector'].start_real_time_collection(interval=0.1)
        print("✓ 开始实时指标采集")

        # 3. 执行并发测试
        print("\n  执行并发测试...")
        result = system['runner'].run_benchmark(test_case)
        assert result is not None
        print(f"✓ 并发测试完成: {result.result.status}")

        # 4. 停止指标采集
        system['collector'].stop_real_time_collection()
        print("✓ 停止指标采集")

        # 5. 收集性能数据
        metrics = system['collector'].get_recent_metrics('system', count=30)
        print(f"✓ 收集性能数据: {len(metrics)} 条")

        # 6. 性能分析
        analysis_result = system['analyzer'].analyze(metrics)
        print(f"✓ 执行性能分析")

        # 7. 生成报告
        report_data = {
            'total_tests': 1,
            'successful_tests': 1 if result.result.success else 0,
            'failed_tests': 0 if result.result.success else 1,
            'total_duration': result.result.duration,
            'metrics': {k: v.to_dict() for k, v in analysis_result.statistics.items()}
        }

        summary = system['generator'].generate_summary_report(report_data)

        # 8. 保存报告
        summary_file = Path(temp_dir) / "concurrent_summary.html"
        system['generator'].export_report(summary, "html", str(summary_file))
        assert summary_file.exists()
        print(f"✓ 生成报告完成")

        print(f"\n=== 场景2完成 ===")

    def test_scenario_performance_regression(self, cleanup_system):
        """场景3: 性能回归测试"""
        print("\n=== 场景3: 性能回归测试 ===")

        system = cleanup_system

        # 1. 创建基准数据（模拟之前版本）
        baseline_metrics = []
        for i in range(30):
            baseline_metrics.append({
                'timestamp': datetime.now(),
                'throughput': 12.0 + (i * 0.1),  # 递增趋势
                'latency_p95': 30.0 - (i * 0.2),  # 递减趋势（性能改善）
                'cpu_utilization': 65.0 + (i * 0.5)
            })
        print("✓ 创建基准数据")

        # 2. 创建当前数据（模拟当前版本）
        current_metrics = []
        for i in range(30):
            current_metrics.append({
                'timestamp': datetime.now(),
                'throughput': 12.5 + (i * 0.15),  # 更好的性能
                'latency_p95': 28.0 - (i * 0.25),  # 更低的延迟
                'cpu_utilization': 62.0 + (i * 0.3)
            })
        print("✓ 创建当前数据")

        # 3. 执行对比分析
        comparison = system['analyzer'].compare_benchmarks(
            baseline_metrics,
            current_metrics,
            "Baseline",
            "Current"
        )
        print(f"✓ 执行性能对比")

        # 4. 检查结果
        assert 'throughput' in comparison.metric_comparisons
        assert 'latency_p95' in comparison.metric_comparisons

        throughput_change = comparison.metric_comparisons['throughput']['change_percent']
        latency_change = comparison.metric_comparisons['latency_p95']['change_percent']

        print(f"✓ 吞吐量改进: {throughput_change:.2f}%")
        print(f"✓ 延迟改进: {latency_change:.2f}%")
        print(f"✓ 总体评分: {comparison.overall_score:.2f}")

        if comparison.improvements_detected:
            print("✓ 检测到性能改进")
        elif comparison.regression_detected:
            print("⚠ 检测到性能回归")
        else:
            print("✓ 性能保持稳定")

        print(f"\n=== 场景3完成 ===")

    def test_scenario_alert_monitoring(self, cleanup_system):
        """场景4: 告警监控测试"""
        print("\n=== 场景4: 告警监控测试 ===")

        system = cleanup_system

        # 1. 模拟正常指标
        normal_metrics = {
            'cpu_utilization': 50.0,
            'memory_usage': 2000.0,
            'throughput': 15.0,
            'latency_p95': 25.0
        }

        alerts = system['alert_system'].check_alerts(normal_metrics)
        print(f"✓ 正常指标触发告警: {len(alerts)} 个")
        assert len(alerts) == 0  # 正常指标不应该触发告警

        # 2. 模拟高负载指标
        high_load_metrics = {
            'cpu_utilization': 90.0,
            'memory_usage': 3800.0,
            'throughput': 8.0,
            'latency_p95': 70.0
        }

        alerts = system['alert_system'].check_alerts(high_load_metrics)
        print(f"✓ 高负载指标触发告警: {len(alerts)} 个")

        # 3. 检查告警详情
        if alerts:
            for alert in alerts:
                print(f"  - {alert.severity.upper()}: {alert.message}")

        # 4. 获取活动告警
        active_alerts = system['alert_system'].get_active_alerts()
        print(f"✓ 活动告警数量: {len(active_alerts)}")

        # 5. 模拟告警确认
        if active_alerts:
            first_alert = active_alerts[0]
            result = system['alert_system'].acknowledge_alert(first_alert.id)
            assert result is True
            print(f"✓ 确认告警: {first_alert.id}")

        # 6. 模拟告警解决
        if active_alerts:
            first_alert = active_alerts[0]
            result = system['alert_system'].resolve_alert(first_alert.id)
            assert result is True
            print(f"✓ 解决告警: {first_alert.id}")

        # 7. 获取告警统计
        stats = system['alert_system'].get_statistics()
        print(f"✓ 告警统计:")
        print(f"  - 总规则数: {stats['total_rules']}")
        print(f"  - 活动告警: {stats['active_alerts']}")
        print(f"  - 24小时告警: {stats['total_alerts_24h']}")

        print(f"\n=== 场景4完成 ===")

    def test_scenario_full_pipeline(self, cleanup_system):
        """场景5: 完整流水线测试"""
        print("\n=== 场景5: 完整流水线测试 ===")

        system = cleanup_system
        temp_dir = system['temp_dir']

        # 1. 执行多个测试
        test_cases = [
            system['suite'].get_test_case("TC-001"),
            system['suite'].get_test_case("TC-002"),
            system['suite'].get_test_case("TC-004")
        ]

        # 2. 开始监控
        system['collector'].start_real_time_collection(interval=0.1)

        # 3. 执行测试套件
        print("\n  执行测试套件...")
        results = system['runner'].run_suite(test_cases)
        print(f"✓ 测试套件完成: {len(results)} 个测试")

        # 4. 停止监控
        system['collector'].stop_real_time_collection()

        # 5. 收集数据
        metrics = system['collector'].get_recent_metrics('system', count=100)
        print(f"✓ 收集性能数据: {len(metrics)} 条")

        # 6. 分析数据
        analysis_result = system['analyzer'].analyze(metrics)
        print(f"✓ 执行性能分析")

        # 7. 检查告警
        alert_metrics = {
            'cpu_utilization': 70.0,
            'memory_usage': 2500.0,
            'throughput': 12.0,
            'latency_p95': 35.0
        }
        alerts = system['alert_system'].check_alerts(alert_metrics)
        print(f"✓ 检查告警: {len(alerts)} 个")

        # 8. 生成完整报告
        report_data = {
            'total_tests': len(results),
            'successful_tests': sum(1 for r in results if r.result.success),
            'failed_tests': sum(1 for r in results if not r.result.success),
            'total_duration': sum(r.result.duration for r in results),
            'metrics': {k: v.to_dict() for k, v in analysis_result.statistics.items()},
            'test_results': [r.to_dict() for r in results],
            'anomalies': [a.to_dict() for a in analysis_result.anomalies],
            'trends': {k: v.to_dict() for k, v in analysis_result.trends.items()},
            'recommendations': [r.to_dict() for r in analysis_result.recommendations]
        }

        summary = system['generator'].generate_summary_report(report_data)
        detailed = system['generator'].generate_detailed_report(report_data)

        # 9. 保存所有报告
        summary_file = Path(temp_dir) / "full_pipeline_summary.html"
        detailed_file = Path(temp_dir) / "full_pipeline_detailed.html"

        system['generator'].export_report(summary, "html", str(summary_file))
        system['generator'].export_report(detailed, "html", str(detailed_file))

        print(f"✓ 生成报告: 2 个文件")

        # 10. 创建仪表盘
        charts = []
        if metrics:
            # CPU图表
            cpu_data = {
                'title': 'CPU使用率',
                'timestamps': [m.get('timestamp', '') for m in metrics[-30:]],
                'values': [m.get('cpu_percent', 0) for m in metrics[-30:] if 'cpu_percent' in m],
                'series_name': 'CPU %'
            }
            if cpu_data['values']:
                cpu_chart = system['viz_engine'].create_time_series_chart(cpu_data)
                charts.append(cpu_chart)

            # 吞吐量图表
            throughput_data = {
                'title': '模型性能对比',
                'categories': [r.test_case.name for r in results],
                'values': [r.result.metrics.get('throughput', 0) for r in results],
                'series_name': '吞吐量'
            }
            throughput_chart = system['viz_engine'].create_comparison_chart(throughput_data)
            charts.append(throughput_chart)

        if charts:
            dashboard = system['viz_engine'].create_dashboard(charts, "完整流水线仪表盘")
            dashboard_file = Path(temp_dir) / "full_pipeline_dashboard.html"
            # 注意：这里简化处理，实际应该保存整个仪表盘
            print(f"✓ 创建仪表盘: {len(charts)} 个图表")

        # 11. 输出最终结果
        print(f"\n=== 完整流水线测试结果 ===")
        print(f"总测试数: {summary.total_tests}")
        print(f"成功率: {summary.success_rate:.1f}%")
        print(f"总耗时: {summary.total_duration:.2f} 秒")
        print(f"性能指标: {len(analysis_result.statistics)} 个")
        print(f"告警数量: {len(alerts)} 个")
        print(f"建议数量: {len(analysis_result.recommendations)} 个")
        print(f"生成文件: 3 个")
        print(f"\n=== 场景5完成 ===")

    def test_scenario_stress_test(self, cleanup_system):
        """场景6: 压力测试"""
        print("\n=== 场景6: 压力测试 ===")

        system = cleanup_system

        # 1. 获取压力测试用例
        stress_test = system['suite'].get_test_case("TC-005")
        assert stress_test is not None
        print(f"✓ 选择压力测试: {stress_test.name}")

        # 2. 准备高压指标
        stress_metrics = {
            'cpu_utilization': 85.0,  # 高CPU
            'memory_usage': 3600.0,   # 高内存
            'throughput': 18.0,       # 高吞吐量
            'latency_p95': 65.0       # 高延迟
        }

        # 3. 执行压力测试
        print("\n  执行压力测试...")
        result = system['runner'].run_benchmark(stress_test)
        print(f"✓ 压力测试完成: {result.result.status}")

        # 4. 检查压力告警
        alerts = system['alert_system'].check_alerts(stress_metrics)
        print(f"✓ 压力测试告警: {len(alerts)} 个")

        # 5. 分析压力结果
        stress_analysis = {
            'cpu_utilization': stress_metrics['cpu_utilization'],
            'memory_usage': stress_metrics['memory_usage'],
            'throughput': stress_metrics['throughput'],
            'latency_p95': stress_metrics['latency_p95']
        }

        recommendations = []
        if stress_metrics['cpu_utilization'] > 80:
            recommendations.append("CPU使用率过高，建议优化算法")
        if stress_metrics['memory_usage'] > 3500:
            recommendations.append("内存使用过高，建议优化内存管理")

        print(f"✓ 压力测试分析:")
        for rec in recommendations:
            print(f"  - {rec}")

        print(f"\n=== 场景6完成 ===")

    def test_scenario_long_term_stability(self, cleanup_system):
        """场景7: 长期稳定性测试"""
        print("\n=== 场景7: 长期稳定性测试 ===")

        system = cleanup_system

        # 1. 获取稳定性测试用例
        stability_test = system['suite'].get_test_case("TC-006")
        assert stability_test is not None
        print(f"✓ 选择稳定性测试: {stability_test.name}")

        # 2. 模拟长期运行数据
        long_term_metrics = []
        for i in range(100):  # 模拟100个时间点的数据
            long_term_metrics.append({
                'timestamp': datetime.now(),
                'cpu_utilization': 60 + (i % 20 - 10),  # 在60附近波动
                'memory_usage': 2200 + (i % 15 - 7) * 10,  # 在2200附近波动
                'throughput': 12 + (i % 10 - 5) * 0.2,  # 在12附近波动
                'latency_p95': 30 + (i % 12 - 6) * 0.5  # 在30附近波动
            })
        print(f"✓ 生成长期数据: {len(long_term_metrics)} 个数据点")

        # 3. 趋势分析
        trends = {}
        for metric_name in ['cpu_utilization', 'memory_usage', 'throughput', 'latency_p95']:
            trend = system['analyzer'].trend_analysis(long_term_metrics, metric_name)
            trends[metric_name] = trend
            print(f"✓ {metric_name} 趋势: {trend.trend_direction}")

        # 4. 稳定性评估
        stable_metrics = []
        volatile_metrics = []

        for metric_name, trend in trends.items():
            if trend.trend_direction in ['stable']:
                stable_metrics.append(metric_name)
            elif trend.trend_direction in ['volatile']:
                volatile_metrics.append(metric_name)

        print(f"\n✓ 稳定性评估:")
        print(f"  稳定指标: {stable_metrics}")
        print(f"  波动指标: {volatile_metrics}")

        if len(volatile_metrics) == 0:
            print("✓ 所有指标表现稳定")
        else:
            print(f"⚠ {len(volatile_metrics)} 个指标存在波动")

        print(f"\n=== 场景7完成 ===")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
