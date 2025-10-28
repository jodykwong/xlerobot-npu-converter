"""
报告生成器 (Report Generator)

生成性能测试报告，支持多种输出格式，
提供报告模板，自动化报告生成。

作者: BMAD Method
创建日期: 2025-10-29
版本: v1.0
"""

import json
import yaml
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ReportConfig:
    """报告配置"""
    output_dir: str = "reports/performance"
    template_dir: str = "templates/reports"
    include_charts: bool = True
    include_recommendations: bool = True
    include_trends: bool = True
    include_anomalies: bool = True
    format: str = "html"  # html, pdf, json, csv


@dataclass
class SummaryReport:
    """汇总报告"""
    title: str
    generated_at: datetime
    total_tests: int
    successful_tests: int
    failed_tests: int
    success_rate: float
    total_duration: float
    key_metrics: Dict[str, Any]
    summary: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            'title': self.title,
            'generated_at': self.generated_at.isoformat(),
            'total_tests': self.total_tests,
            'successful_tests': self.successful_tests,
            'failed_tests': self.failed_tests,
            'success_rate': self.success_rate,
            'total_duration': self.total_duration,
            'key_metrics': self.key_metrics,
            'summary': self.summary
        }


@dataclass
class DetailedReport:
    """详细报告"""
    title: str
    generated_at: datetime
    test_results: List[Dict[str, Any]]
    analysis_results: Dict[str, Any]
    anomalies: List[Dict[str, Any]]
    trends: Dict[str, Any]
    recommendations: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'title': self.title,
            'generated_at': self.generated_at.isoformat(),
            'test_results': self.test_results,
            'analysis_results': self.analysis_results,
            'anomalies': self.anomalies,
            'trends': self.trends,
            'recommendations': self.recommendations
        }


class ReportGenerator:
    """
    报告生成器

    生成性能测试报告，支持多种输出格式，
    提供报告模板，自动化报告生成。
    """

    def __init__(self, config: ReportConfig):
        """
        初始化报告生成器

        Args:
            config: 报告配置
        """
        self.config = config
        Path(config.output_dir).mkdir(parents=True, exist_ok=True)

        logger.info(f"Report Generator initialized with config: {asdict(config)}")

    def generate_summary_report(self, result_data: Dict[str, Any]) -> SummaryReport:
        """
        生成汇总报告

        Args:
            result_data: 测试结果数据

        Returns:
            SummaryReport: 汇总报告
        """
        total_tests = result_data.get('total_tests', 0)
        successful_tests = result_data.get('successful_tests', 0)
        failed_tests = result_data.get('failed_tests', 0)

        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0

        key_metrics = result_data.get('metrics', {})
        summary = self._generate_summary_text(success_rate, key_metrics)

        report = SummaryReport(
            title="Performance Benchmark Summary Report",
            generated_at=datetime.now(),
            total_tests=total_tests,
            successful_tests=successful_tests,
            failed_tests=failed_tests,
            success_rate=success_rate,
            total_duration=result_data.get('total_duration', 0),
            key_metrics=key_metrics,
            summary=summary
        )

        logger.info(f"Generated summary report: {report.title}")
        return report

    def generate_detailed_report(self, result_data: Dict[str, Any]) -> DetailedReport:
        """
        生成详细报告

        Args:
            result_data: 测试结果数据

        Returns:
            DetailedReport: 详细报告
        """
        report = DetailedReport(
            title="Performance Benchmark Detailed Report",
            generated_at=datetime.now(),
            test_results=result_data.get('test_results', []),
            analysis_results=result_data.get('analysis_results', {}),
            anomalies=result_data.get('anomalies', []),
            trends=result_data.get('trends', {}),
            recommendations=result_data.get('recommendations', [])
        )

        logger.info(f"Generated detailed report: {report.title}")
        return report

    def export_report(self, report: Any, format: str, output_path: str):
        """
        导出报告

        Args:
            report: 报告对象
            format: 输出格式
            output_path: 输出文件路径
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format.lower() == "json":
            self._export_json(report, output_path)
        elif format.lower() == "yaml":
            self._export_yaml(report, output_path)
        elif format.lower() == "html":
            self._export_html(report, output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")

        logger.info(f"Exported report to {output_path}")

    def _export_json(self, report: Any, output_path: Path):
        """导出JSON格式"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)

    def _export_yaml(self, report: Any, output_path: Path):
        """导出YAML格式"""
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(report.to_dict(), f, default_flow_style=False, allow_unicode=True)

    def _export_html(self, report: Any, output_path: Path):
        """导出HTML格式"""
        html_content = self._generate_html_template(report)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def _generate_html_template(self, report: Any) -> str:
        """生成HTML模板"""
        if isinstance(report, SummaryReport):
            return self._generate_summary_html(report)
        elif isinstance(report, DetailedReport):
            return self._generate_detailed_html(report)
        else:
            return "<html><body>Unsupported report type</body></html>"

    def _generate_summary_html(self, report: SummaryReport) -> str:
        """生成汇总报告HTML"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>{report.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #2c3e50; }}
        .metric {{ background: #ecf0f1; padding: 10px; margin: 10px 0; }}
        .success {{ color: #27ae60; }}
        .error {{ color: #e74c3c; }}
    </style>
</head>
<body>
    <h1>{report.title}</h1>
    <p>Generated at: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}</p>

    <h2>Summary</h2>
    <p>{report.summary}</p>

    <h2>Test Results</h2>
    <div class="metric">
        <strong>Total Tests:</strong> {report.total_tests}<br>
        <strong class="success">Successful:</strong> {report.successful_tests}<br>
        <strong class="error">Failed:</strong> {report.failed_tests}<br>
        <strong>Success Rate:</strong> {report.success_rate:.2f}%<br>
        <strong>Total Duration:</strong> {report.total_duration:.2f}s
    </div>

    <h2>Key Metrics</h2>
    <div class="metric">
        {json.dumps(report.key_metrics, indent=2)}
    </div>
</body>
</html>
        """

    def _generate_detailed_html(self, report: DetailedReport) -> str:
        """生成详细报告HTML"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>{report.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; }}
        .metric {{ background: #ecf0f1; padding: 10px; margin: 10px 0; }}
        .anomaly {{ background: #ffe6e6; padding: 10px; margin: 10px 0; }}
        .recommendation {{ background: #e6f7ff; padding: 10px; margin: 10px 0; }}
    </style>
</head>
<body>
    <h1>{report.title}</h1>
    <p>Generated at: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}</p>

    <h2>Test Results</h2>
    <div class="metric">
        {len(report.test_results)} test cases executed
    </div>

    <h2>Anomalies</h2>
    {''.join([f'<div class="anomaly">{a}</div>' for a in report.anomalies])}

    <h2>Recommendations</h2>
    {''.join([f'<div class="recommendation">{r}</div>' for r in report.recommendations])}
</body>
</html>
        """

    def _generate_summary_text(self, success_rate: float, key_metrics: Dict[str, Any]) -> str:
        """生成汇总文本"""
        if success_rate >= 95:
            return "All performance benchmarks passed successfully. The system is performing within expected parameters."
        elif success_rate >= 80:
            return "Most performance benchmarks passed. Some areas may need attention."
        else:
            return "Several performance benchmarks failed. Immediate action recommended."

    def create_dashboard(self, data: Dict[str, Any]) -> str:
        """
        创建仪表盘

        Args:
            data: 数据

        Returns:
            str: 仪表盘HTML内容
        """
        dashboard_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Performance Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .dashboard-container {{ display: flex; flex-wrap: wrap; }}
        .chart {{ width: 45%; margin: 10px; }}
    </style>
</head>
<body>
    <h1>Performance Dashboard</h1>
    <div class="dashboard-container">
        <div id="throughput-chart" class="chart"></div>
        <div id="latency-chart" class="chart"></div>
        <div id="resource-chart" class="chart"></div>
        <div id="trend-chart" class="chart"></div>
    </div>
</body>
</html>
        """
        return dashboard_html


if __name__ == "__main__":
    # 示例使用
    config = ReportConfig(
        output_dir="reports/performance",
        format="html"
    )

    generator = ReportGenerator(config)

    # 示例数据
    result_data = {
        'total_tests': 10,
        'successful_tests': 9,
        'failed_tests': 1,
        'total_duration': 3600,
        'metrics': {
            'throughput': 12.5,
            'latency_p95': 28.5,
            'cpu_utilization': 65.5
        }
    }

    # 生成汇总报告
    summary_report = generator.generate_summary_report(result_data)
    generator.export_report(summary_report, "html", "reports/performance/summary_report.html")

    # 生成详细报告
    detailed_report = generator.generate_detailed_report(result_data)
    generator.export_report(detailed_report, "html", "reports/performance/detailed_report.html")

    print("Reports generated successfully!")
