"""
报告生成器单元测试

测试ReportGenerator类的所有功能，包括报告生成、
导出等功能。

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

# 添加源码路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'src'))

from npu_converter.performance.report_generator import (
    ReportGenerator,
    ReportConfig,
    SummaryReport,
    DetailedReport
)


class TestReportConfig:
    """测试ReportConfig配置类"""

    def test_default_config(self):
        """测试默认配置"""
        config = ReportConfig()
        assert config.output_dir == "reports/performance"
        assert config.template_dir == "templates/reports"
        assert config.include_charts is True
        assert config.include_recommendations is True
        assert config.include_trends is True
        assert config.include_anomalies is True
        assert config.format == "html"

    def test_custom_config(self):
        """测试自定义配置"""
        config = ReportConfig(
            output_dir="/tmp/test",
            template_dir="/tmp/templates",
            include_charts=False,
            format="json"
        )
        assert config.output_dir == "/tmp/test"
        assert config.include_charts is False
        assert config.format == "json"


class TestSummaryReport:
    """测试SummaryReport汇总报告类"""

    def test_create_summary_report(self):
        """测试创建汇总报告"""
        now = datetime.now()
        report = SummaryReport(
            title="Performance Summary",
            generated_at=now,
            total_tests=10,
            successful_tests=9,
            failed_tests=1,
            success_rate=90.0,
            total_duration=3600.0,
            key_metrics={"throughput": 12.5, "latency": 30.0},
            summary="Overall performance is good"
        )

        assert report.title == "Performance Summary"
        assert report.total_tests == 10
        assert report.success_rate == 90.0

    def test_summary_report_to_dict(self):
        """测试汇总报告转换为字典"""
        now = datetime.now()
        report = SummaryReport(
            title="Performance Summary",
            generated_at=now,
            total_tests=10,
            successful_tests=9,
            failed_tests=1,
            success_rate=90.0,
            total_duration=3600.0,
            key_metrics={"throughput": 12.5},
            summary="Good"
        )

        result = report.to_dict()
        assert result['title'] == "Performance Summary"
        assert result['generated_at'] == now.isoformat()
        assert result['success_rate'] == 90.0


class TestDetailedReport:
    """测试DetailedReport详细报告类"""

    def test_create_detailed_report(self):
        """测试创建详细报告"""
        now = datetime.now()
        report = DetailedReport(
            title="Detailed Performance Report",
            generated_at=now,
            test_results=[{"id": "TC-001", "status": "success"}],
            analysis_results={"anomalies": 2},
            anomalies=[{"metric": "cpu", "value": 95}],
            trends={"cpu": "increasing"},
            recommendations=[{"title": "优化CPU"}]
        )

        assert report.title == "Detailed Performance Report"
        assert len(report.test_results) == 1

    def test_detailed_report_to_dict(self):
        """测试详细报告转换为字典"""
        now = datetime.now()
        report = DetailedReport(
            title="Detailed Report",
            generated_at=now,
            test_results=[],
            analysis_results={},
            anomalies=[],
            trends={},
            recommendations=[]
        )

        result = report.to_dict()
        assert result['title'] == "Detailed Report"
        assert result['generated_at'] == now.isoformat()


class TestReportGenerator:
    """测试ReportGenerator生成器类"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path, ignore_errors=True)

    @pytest.fixture
    def generator(self, temp_dir):
        """创建ReportGenerator实例"""
        config = ReportConfig(output_dir=temp_dir)
        return ReportGenerator(config)

    def test_initialize_generator(self, temp_dir):
        """测试初始化生成器"""
        config = ReportConfig(output_dir=temp_dir)
        generator = ReportGenerator(config)
        assert generator.config.output_dir == temp_dir

    def test_generate_summary_report(self, generator):
        """测试生成汇总报告"""
        result_data = {
            'total_tests': 10,
            'successful_tests': 9,
            'failed_tests': 1,
            'total_duration': 3600,
            'metrics': {
                'throughput': 12.5,
                'latency_p95': 30.0,
                'cpu_utilization': 65.0
            }
        }

        report = generator.generate_summary_report(result_data)

        assert isinstance(report, SummaryReport)
        assert report.total_tests == 10
        assert report.success_rate == 90.0
        assert 'throughput' in report.key_metrics

    def test_generate_summary_report_empty(self, generator):
        """测试生成空数据汇总报告"""
        result_data = {
            'total_tests': 0,
            'successful_tests': 0,
            'failed_tests': 0,
            'total_duration': 0
        }

        report = generator.generate_summary_report(result_data)

        assert report.total_tests == 0
        assert report.success_rate == 0.0

    def test_generate_detailed_report(self, generator):
        """测试生成详细报告"""
        result_data = {
            'test_results': [
                {'id': 'TC-001', 'status': 'success'},
                {'id': 'TC-002', 'status': 'failure'}
            ],
            'analysis_results': {'total_metrics': 4},
            'anomalies': [{'metric': 'cpu', 'value': 95}],
            'trends': {'cpu': 'increasing'},
            'recommendations': [{'title': '优化CPU'}]
        }

        report = generator.generate_detailed_report(result_data)

        assert isinstance(report, DetailedReport)
        assert len(report.test_results) == 2
        assert len(report.anomalies) == 1
        assert len(report.recommendations) == 1

    def test_export_report_json(self, generator):
        """测试导出JSON格式报告"""
        result_data = {
            'total_tests': 5,
            'successful_tests': 5,
            'failed_tests': 0,
            'total_duration': 1800
        }

        report = generator.generate_summary_report(result_data)
        output_file = Path(generator.config.output_dir) / "summary.json"
        generator.export_report(report, "json", str(output_file))

        assert output_file.exists()

    def test_export_report_yaml(self, generator):
        """测试导出YAML格式报告"""
        result_data = {
            'total_tests': 5,
            'successful_tests': 5,
            'failed_tests': 0,
            'total_duration': 1800
        }

        report = generator.generate_summary_report(result_data)
        output_file = Path(generator.config.output_dir) / "summary.yaml"
        generator.export_report(report, "yaml", str(output_file))

        assert output_file.exists()

    def test_export_report_html(self, generator):
        """测试导出HTML格式报告"""
        result_data = {
            'total_tests': 5,
            'successful_tests': 5,
            'failed_tests': 0,
            'total_duration': 1800,
            'metrics': {'throughput': 12.5}
        }

        # 汇总报告
        report = generator.generate_summary_report(result_data)
        output_file = Path(generator.config.output_dir) / "summary.html"
        generator.export_report(report, "html", str(output_file))

        assert output_file.exists()

        # 详细报告
        detailed_data = {
            'test_results': [{'id': 'TC-001', 'status': 'success'}],
            'analysis_results': {},
            'anomalies': [],
            'trends': {},
            'recommendations': []
        }
        detailed_report = generator.generate_detailed_report(detailed_data)
        detailed_file = Path(generator.config.output_dir) / "detailed.html"
        generator.export_report(detailed_report, "html", str(detailed_file))

        assert detailed_file.exists()

    def test_export_report_unsupported_format(self, generator):
        """测试导出不支持的格式"""
        result_data = {'total_tests': 5}
        report = generator.generate_summary_report(result_data)
        output_file = Path(generator.config.output_dir) / "report.unsupported"

        with pytest.raises(ValueError):
            generator.export_report(report, "unsupported", str(output_file))

    def test_create_dashboard(self, generator):
        """测试创建仪表盘"""
        data = {
            'throughput': [12.0, 13.0, 14.0],
            'latency': [30.0, 28.0, 26.0]
        }

        dashboard = generator.create_dashboard(data)

        assert isinstance(dashboard, str)
        assert 'Performance Dashboard' in dashboard
        assert 'plotly' in dashboard.lower()

    def test_generate_summary_text_success(self, generator):
        """测试生成成功汇总文本"""
        text = generator._generate_summary_text(98.0, {})
        assert "successfully" in text.lower()

    def test_generate_summary_text_warning(self, generator):
        """测试生成警告汇总文本"""
        text = generator._generate_summary_text(85.0, {})
        assert "most" in text.lower()

    def test_generate_summary_text_error(self, generator):
        """测试生成错误汇总文本"""
        text = generator._generate_summary_text(70.0, {})
        assert "several" in text.lower() or "failed" in text.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
