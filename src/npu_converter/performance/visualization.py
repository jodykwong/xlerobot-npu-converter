"""
可视化引擎 (Visualization Engine)

生成性能图表，提供交互式可视化，
支持多种图表类型，自定义图表样式。

作者: BMAD Method
创建日期: 2025-10-29
版本: v1.0
"""

import json
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
class VisualizationConfig:
    """可视化配置"""
    output_dir: str = "reports/performance/charts"
    width: int = 800
    height: int = 600
    theme: str = "plotly"  # plotly, seaborn, matplotlib
    color_scheme: str = "default"
    interactive: bool = True


@dataclass
class Chart:
    """图表"""
    title: str
    chart_type: str
    data: Dict[str, Any]
    layout: Dict[str, Any]
    config: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'title': self.title,
            'chart_type': self.chart_type,
            'data': self.data,
            'layout': self.layout,
            'config': self.config
        }


@dataclass
class Dashboard:
    """仪表盘"""
    title: str
    charts: List[Chart]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'title': self.title,
            'charts': [c.to_dict() for c in self.charts],
            'metadata': self.metadata
        }


class VisualizationEngine:
    """
    可视化引擎

    生成性能图表，提供交互式可视化，
    支持多种图表类型。
    """

    CHART_TYPES = {
        'line': 'Line Chart',
        'bar': 'Bar Chart',
        'histogram': 'Histogram',
        'heatmap': 'Heatmap',
        'scatter': 'Scatter Plot',
        'gauge': 'Gauge Chart',
        'time_series': 'Time Series'
    }

    def __init__(self, config: VisualizationConfig):
        """
        初始化可视化引擎

        Args:
            config: 可视化配置
        """
        self.config = config
        Path(config.output_dir).mkdir(parents=True, exist_ok=True)

        logger.info(f"Visualization Engine initialized with config: {asdict(config)}")

    def create_time_series_chart(self, data: Dict[str, Any]) -> Chart:
        """创建时间序列图表"""
        chart = Chart(
            title=data.get('title', 'Time Series Chart'),
            chart_type='line',
            data={
                'x': data.get('timestamps', []),
                'y': data.get('values', []),
                'name': data.get('series_name', 'Series')
            },
            layout={
                'title': data.get('title', 'Time Series Chart'),
                'xaxis': {'title': 'Time'},
                'yaxis': {'title': data.get('yaxis_title', 'Value')}
            },
            config={'responsive': True}
        )
        return chart

    def create_comparison_chart(self, data: Dict[str, Any]) -> Chart:
        """创建对比图表"""
        chart = Chart(
            title=data.get('title', 'Comparison Chart'),
            chart_type='bar',
            data={
                'x': data.get('categories', []),
                'y': data.get('values', []),
                'name': data.get('series_name', 'Series')
            },
            layout={
                'title': data.get('title', 'Comparison Chart'),
                'barmode': 'group'
            },
            config={'responsive': True}
        )
        return chart

    def create_distribution_chart(self, data: Dict[str, Any]) -> Chart:
        """创建分布图表"""
        chart = Chart(
            title=data.get('title', 'Distribution Chart'),
            chart_type='histogram',
            data={
                'x': data.get('values', []),
                'name': data.get('series_name', 'Series')
            },
            layout={
                'title': data.get('title', 'Distribution Chart'),
                'xaxis': {'title': 'Value'},
                'yaxis': {'title': 'Frequency'}
            },
            config={'responsive': True}
        )
        return chart

    def create_dashboard(self, charts: List[Chart], title: str = "Performance Dashboard") -> Dashboard:
        """创建仪表盘"""
        dashboard = Dashboard(
            title=title,
            charts=charts,
            metadata={
                'created_at': datetime.now().isoformat(),
                'chart_count': len(charts)
            }
        )
        logger.info(f"Created dashboard with {len(charts)} charts")
        return dashboard

    def export_chart(self, chart: Chart, format: str, output_path: str):
        """导出图表"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format.lower() == "json":
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(chart.to_dict(), f, indent=2, ensure_ascii=False)
        elif format.lower() == "html":
            html_content = self._generate_chart_html(chart)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

        logger.info(f"Exported chart to {output_path}")

    def _generate_chart_html(self, chart: Chart) -> str:
        """生成图表HTML"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>{chart.title}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
    </style>
</head>
<body>
    <div id="chart" style="width:100%; height:600px;"></div>
    <script>
        var data = {json.dumps([chart.data])};
        var layout = {json.dumps(chart.layout)};
        var config = {json.dumps(chart.config)};
        Plotly.newPlot('chart', data, layout, config);
    </script>
</body>
</html>
        """


if __name__ == "__main__":
    # 示例使用
    config = VisualizationConfig(
        output_dir="reports/performance/charts",
        interactive=True
    )

    engine = VisualizationEngine(config)

    # 创建时间序列图表
    ts_data = {
        'title': 'CPU Utilization Over Time',
        'timestamps': ['2025-10-29 10:00', '2025-10-29 10:01', '2025-10-29 10:02'],
        'values': [50, 55, 60],
        'series_name': 'CPU %'
    }
    ts_chart = engine.create_time_series_chart(ts_data)
    engine.export_chart(ts_chart, 'html', 'reports/performance/charts/cpu_usage.html')

    # 创建对比图表
    comp_data = {
        'title': 'Model Performance Comparison',
        'categories': ['SenseVoice', 'VITS-Cantonese', 'Piper-VITS'],
        'values': [12.5, 10.2, 11.8],
        'series_name': 'Throughput'
    }
    comp_chart = engine.create_comparison_chart(comp_data)
    engine.export_chart(comp_chart, 'html', 'reports/performance/charts/model_comparison.html')

    print("Charts generated successfully!")
