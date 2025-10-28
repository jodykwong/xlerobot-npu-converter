"""
可视化引擎单元测试

测试VisualizationEngine类的所有功能，包括图表创建、
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

from npu_converter.performance.visualization import (
    VisualizationEngine,
    VisualizationConfig,
    Chart,
    Dashboard
)


class TestVisualizationConfig:
    """测试VisualizationConfig配置类"""

    def test_default_config(self):
        """测试默认配置"""
        config = VisualizationConfig()
        assert config.output_dir == "reports/performance/charts"
        assert config.width == 800
        assert config.height == 600
        assert config.theme == "plotly"
        assert config.color_scheme == "default"
        assert config.interactive is True

    def test_custom_config(self):
        """测试自定义配置"""
        config = VisualizationConfig(
            output_dir="/tmp/charts",
            width=1024,
            height=768,
            theme="seaborn",
            interactive=False
        )
        assert config.output_dir == "/tmp/charts"
        assert config.width == 1024
        assert config.height == 768
        assert config.theme == "seaborn"
        assert config.interactive is False


class TestChart:
    """测试Chart图表类"""

    def test_create_chart(self):
        """测试创建图表"""
        chart = Chart(
            title="CPU Usage",
            chart_type="line",
            data={"x": [1, 2, 3], "y": [10, 20, 30]},
            layout={"title": "CPU Usage"},
            config={"responsive": True}
        )

        assert chart.title == "CPU Usage"
        assert chart.chart_type == "line"
        assert "x" in chart.data
        assert "y" in chart.data

    def test_chart_to_dict(self):
        """测试图表转换为字典"""
        chart = Chart(
            title="CPU Usage",
            chart_type="line",
            data={"x": [1, 2], "y": [10, 20]},
            layout={"title": "CPU"},
            config={}
        )

        result = chart.to_dict()
        assert result['title'] == "CPU Usage"
        assert result['chart_type'] == "line"


class TestDashboard:
    """测试Dashboard仪表盘类"""

    def test_create_dashboard(self):
        """测试创建仪表盘"""
        chart = Chart(
            title="Chart1",
            chart_type="line",
            data={"x": [1], "y": [10]},
            layout={},
            config={}
        )

        dashboard = Dashboard(
            title="Performance Dashboard",
            charts=[chart],
            metadata={"created": "2025-10-29"}
        )

        assert dashboard.title == "Performance Dashboard"
        assert len(dashboard.charts) == 1
        assert dashboard.metadata["created"] == "2025-10-29"

    def test_dashboard_to_dict(self):
        """测试仪表盘转换为字典"""
        chart = Chart(
            title="Chart1",
            chart_type="line",
            data={"x": [1], "y": [10]},
            layout={},
            config={}
        )

        dashboard = Dashboard(
            title="Dashboard",
            charts=[chart],
            metadata={}
        )

        result = dashboard.to_dict()
        assert result['title'] == "Dashboard"
        assert len(result['charts']) == 1


class TestVisualizationEngine:
    """测试VisualizationEngine可视化引擎类"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path, ignore_errors=True)

    @pytest.fixture
    def engine(self, temp_dir):
        """创建VisualizationEngine实例"""
        config = VisualizationConfig(output_dir=temp_dir)
        return VisualizationEngine(config)

    def test_initialize_engine(self, temp_dir):
        """测试初始化引擎"""
        config = VisualizationConfig(output_dir=temp_dir)
        engine = VisualizationEngine(config)
        assert engine.config.output_dir == temp_dir

    def test_create_time_series_chart(self, engine):
        """测试创建时间序列图表"""
        data = {
            'title': 'CPU Utilization Over Time',
            'timestamps': ['2025-10-29 10:00', '2025-10-29 10:01'],
            'values': [50, 55],
            'series_name': 'CPU %',
            'yaxis_title': 'CPU %'
        }

        chart = engine.create_time_series_chart(data)

        assert isinstance(chart, Chart)
        assert chart.title == 'CPU Utilization Over Time'
        assert chart.chart_type == 'line'
        assert 'x' in chart.data
        assert 'y' in chart.data
        assert chart.data['name'] == 'CPU %'

    def test_create_comparison_chart(self, engine):
        """测试创建对比图表"""
        data = {
            'title': 'Model Performance Comparison',
            'categories': ['Model A', 'Model B', 'Model C'],
            'values': [12.5, 10.0, 11.8],
            'series_name': 'Throughput'
        }

        chart = engine.create_comparison_chart(data)

        assert isinstance(chart, Chart)
        assert chart.title == 'Model Performance Comparison'
        assert chart.chart_type == 'bar'
        assert 'x' in chart.data
        assert 'y' in chart.data
        assert chart.data['name'] == 'Throughput'

    def test_create_distribution_chart(self, engine):
        """测试创建分布图表"""
        data = {
            'title': 'CPU Distribution',
            'values': [50, 55, 60, 65, 70],
            'series_name': 'CPU %'
        }

        chart = engine.create_distribution_chart(data)

        assert isinstance(chart, Chart)
        assert chart.title == 'CPU Distribution'
        assert chart.chart_type == 'histogram'
        assert 'x' in chart.data
        assert chart.data['name'] == 'CPU %'

    def test_create_dashboard(self, engine):
        """测试创建仪表盘"""
        # 创建多个图表
        ts_data = {
            'title': 'Time Series',
            'timestamps': ['2025-10-29 10:00'],
            'values': [50],
            'series_name': 'Series'
        }
        ts_chart = engine.create_time_series_chart(ts_data)

        comp_data = {
            'title': 'Comparison',
            'categories': ['A', 'B'],
            'values': [10, 20],
            'series_name': 'Value'
        }
        comp_chart = engine.create_comparison_chart(comp_data)

        dashboard = engine.create_dashboard([ts_chart, comp_chart], "Test Dashboard")

        assert isinstance(dashboard, Dashboard)
        assert dashboard.title == "Test Dashboard"
        assert len(dashboard.charts) == 2
        assert dashboard.metadata['chart_count'] == 2

    def test_export_chart_json(self, engine):
        """测试导出JSON格式图表"""
        data = {
            'title': 'Test Chart',
            'timestamps': ['2025-10-29'],
            'values': [50],
            'series_name': 'Series'
        }
        chart = engine.create_time_series_chart(data)

        output_file = Path(engine.config.output_dir) / "chart.json"
        engine.export_chart(chart, "json", str(output_file))

        assert output_file.exists()

    def test_export_chart_html(self, engine):
        """测试导出HTML格式图表"""
        data = {
            'title': 'Test Chart',
            'timestamps': ['2025-10-29'],
            'values': [50],
            'series_name': 'Series'
        }
        chart = engine.create_time_series_chart(data)

        output_file = Path(engine.config.output_dir) / "chart.html"
        engine.export_chart(chart, "html", str(output_file))

        assert output_file.exists()

        # 检查HTML内容
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'Test Chart' in content
            assert 'plotly' in content.lower()

    def test_chart_types(self, engine):
        """测试图表类型常量"""
        assert 'line' in engine.CHART_TYPES
        assert 'bar' in engine.CHART_TYPES
        assert 'histogram' in engine.CHART_TYPES
        assert 'scatter' in engine.CHART_TYPES
        assert 'time_series' in engine.CHART_TYPES

    def test_create_chart_with_empty_data(self, engine):
        """测试创建空数据图表"""
        data = {
            'title': 'Empty Chart',
            'timestamps': [],
            'values': [],
            'series_name': 'Series'
        }
        chart = engine.create_time_series_chart(data)

        assert chart.title == 'Empty Chart'
        assert len(chart.data['x']) == 0
        assert len(chart.data['y']) == 0

    def test_create_multiple_charts(self, engine):
        """测试创建多个图表"""
        # 时间序列图表
        ts_chart = engine.create_time_series_chart({
            'title': 'Time Series',
            'timestamps': ['2025-10-29'],
            'values': [50],
            'series_name': 'Series'
        })

        # 对比图表
        comp_chart = engine.create_comparison_chart({
            'title': 'Comparison',
            'categories': ['A', 'B'],
            'values': [10, 20],
            'series_name': 'Value'
        })

        # 分布图表
        dist_chart = engine.create_distribution_chart({
            'title': 'Distribution',
            'values': [10, 20, 30],
            'series_name': 'Values'
        })

        assert isinstance(ts_chart, Chart)
        assert isinstance(comp_chart, Chart)
        assert isinstance(dist_chart, Chart)

    def test_dashboard_with_multiple_charts(self, engine):
        """测试多图表仪表盘"""
        charts = []
        for i in range(3):
            chart = engine.create_time_series_chart({
                'title': f'Chart {i}',
                'timestamps': ['2025-10-29'],
                'values': [i * 10],
                'series_name': f'Series {i}'
            })
            charts.append(chart)

        dashboard = engine.create_dashboard(charts, "Multi-Chart Dashboard")

        assert dashboard.title == "Multi-Chart Dashboard"
        assert len(dashboard.charts) == 3
        assert dashboard.metadata['chart_count'] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
