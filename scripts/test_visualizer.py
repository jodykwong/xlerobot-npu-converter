#!/usr/bin/env python3
"""
XLeRobot NPU Converter - 测试结果可视化器

提供测试结果的多维度可视化，包括图表、趋势分析和交互式仪表板。
"""

import json
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import base64

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import seaborn as sns
    import pandas as pd
    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False
    print("⚠️ matplotlib/seaborn/pandas未安装，可视化功能受限")


class TestResultVisualizer:
    """测试结果可视化器"""

    def __init__(self, project_root: str = None):
        """初始化可视化器

        Args:
            project_root: 项目根目录
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.reports_dir = self.project_root / "reports"
        self.visualization_dir = self.reports_dir / "visualizations"
        self.dashboard_file = self.visualization_dir / "dashboard.html"

        # 确保目录存在
        self.visualization_dir.mkdir(parents=True, exist_ok=True)

        # 设置图表样式
        if HAS_PLOTTING:
            plt.style.use('seaborn-v0_8' if hasattr(plt.style, 'seaborn-v0_8') else 'default')
            sns.set_palette("husl")

    def generate_test_success_chart(self, test_report: Dict) -> str:
        """生成测试成功率图表

        Args:
            test_report: 测试报告数据

        Returns:
            Base64编码的图片数据
        """
        if not HAS_PLOTTING:
            return ""

        test_suites = test_report.get("test_suites", [])
        if not test_suites:
            return ""

        # 提取数据
        names = [suite.get("name", "").replace("_tests", "").title() for suite in test_suites]
        passed = [suite.get("passed", 0) for suite in test_suites]
        failed = [suite.get("failed", 0) for suite in test_suites]
        skipped = [suite.get("skipped", 0) for suite in test_suites]

        # 创建图表
        fig, ax = plt.subplots(figsize=(10, 6))
        x = range(len(names))

        # 堆叠条形图
        bars_passed = ax.bar(x, passed, label='通过', color='#28a745', alpha=0.8)
        bars_failed = ax.bar(x, failed, bottom=passed, label='失败', color='#dc3545', alpha=0.8)
        bars_skipped = ax.bar(x, skipped, bottom=[p + f for p, f in zip(passed, failed)],
                             label='跳过', color='#ffc107', alpha=0.8)

        # 设置图表属性
        ax.set_xlabel('测试套件')
        ax.set_ylabel('测试数量')
        ax.set_title('测试套件执行结果分布')
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 添加数值标签
        for i, (p, f, s) in enumerate(zip(passed, failed, skipped)):
            if p > 0:
                ax.text(i, p/2, str(p), ha='center', va='center', fontweight='bold')
            if f > 0:
                ax.text(i, p + f/2, str(f), ha='center', va='center', fontweight='bold')
            if s > 0:
                ax.text(i, p + f + s/2, str(s), ha='center', va='center', fontweight='bold')

        plt.tight_layout()

        # 保存为Base64
        chart_file = self.visualization_dir / "test_success_chart.png"
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()

        return self._encode_image_to_base64(chart_file)

    def generate_performance_chart(self, test_report: Dict) -> str:
        """生成性能测试图表

        Args:
            test_report: 测试报告数据

        Returns:
            Base64编码的图片数据
        """
        if not HAS_PLOTTING:
            return ""

        performance_metrics = test_report.get("performance_metrics", [])
        if not performance_metrics:
            return ""

        # 提取数据
        names = [metric.get("name", "").replace("_", " ").title() for metric in performance_metrics]
        values = [metric.get("value", 0) for metric in performance_metrics]
        units = [metric.get("unit", "") for metric in performance_metrics]

        # 创建图表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # 柱状图
        bars = ax1.bar(range(len(names)), values, alpha=0.8, color='#007bff')
        ax1.set_xlabel('性能指标')
        ax1.set_ylabel('数值')
        ax1.set_title('性能指标对比')
        ax1.set_xticks(range(len(names)))
        ax1.set_xticklabels(names, rotation=45, ha='right')
        ax1.grid(True, alpha=0.3)

        # 添加数值标签和单位
        for i, (bar, value, unit) in enumerate(zip(bars, values, units)):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{value:.2f} {unit}', ha='center', va='bottom', fontweight='bold')

        # 改进对比图（如果有基线数据）
        improvements = []
        labels = []
        for i, metric in enumerate(performance_metrics):
            if metric.get("baseline") is not None:
                improvements.append(metric.get("improvement", 0))
                labels.append(names[i])

        if improvements:
            colors = ['#28a745' if imp > 0 else '#dc3545' for imp in improvements]
            bars2 = ax2.bar(range(len(labels)), improvements, color=colors, alpha=0.8)
            ax2.set_xlabel('性能指标')
            ax2.set_ylabel('改进百分比 (%)')
            ax2.set_title('性能改进对比')
            ax2.set_xticks(range(len(labels)))
            ax2.set_xticklabels(labels, rotation=45, ha='right')
            ax2.grid(True, alpha=0.3)
            ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)

            # 添加数值标签
            for bar, imp in zip(bars2, improvements):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + (1 if height > 0 else -3),
                        f'{imp:+.1f}%', ha='center', va='bottom' if height > 0 else 'top',
                        fontweight='bold')
        else:
            ax2.text(0.5, 0.5, '无基线数据', ha='center', va='center',
                    transform=ax2.transAxes, fontsize=16, alpha=0.5)
            ax2.set_title('性能改进对比')

        plt.tight_layout()

        # 保存为Base64
        chart_file = self.visualization_dir / "performance_chart.png"
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()

        return self._encode_image_to_base64(chart_file)

    def generate_coverage_chart(self, test_report: Dict) -> str:
        """生成覆盖率图表

        Args:
            test_report: 测试报告数据

        Returns:
            Base64编码的图片数据
        """
        if not HAS_PLOTTING:
            return ""

        coverage = test_report.get("coverage")
        if not coverage:
            return ""

        # 创建图表
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))

        # 总体覆盖率饼图
        overall_percent = coverage.get("overall_percent", 0)
        uncovered = 100 - overall_percent

        ax1.pie([overall_percent, uncovered],
                labels=[f'覆盖率 ({overall_percent:.1f}%)', f'未覆盖 ({uncovered:.1f}%)'],
                colors=['#28a745', '#dc3545'],
                autopct='%1.1f%%',
                startangle=90)
        ax1.set_title('总体覆盖率分布')

        # 行覆盖率vs分支覆盖率
        line_coverage = coverage.get("line_coverage", 0)
        line_total = coverage.get("line_total", 0)
        branch_coverage = coverage.get("branch_coverage", 0)
        branch_total = coverage.get("branch_total", 0)

        line_percent = (line_coverage / line_total * 100) if line_total > 0 else 0
        branch_percent = (branch_coverage / branch_total * 100) if branch_total > 0 else 0

        bars = ax2.bar(['行覆盖率', '分支覆盖率'], [line_percent, branch_percent],
                      color=['#007bff', '#17a2b8'], alpha=0.8)
        ax2.set_ylabel('覆盖率 (%)')
        ax2.set_title('行覆盖率 vs 分支覆盖率')
        ax2.set_ylim(0, 100)
        ax2.grid(True, alpha=0.3)

        # 添加数值标签
        for bar, value in zip(bars, [line_percent, branch_percent]):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')

        # 目录覆盖率（如果有）
        directories = coverage.get("directories", {})
        if directories:
            dir_names = list(directories.keys())
            dir_coverage = [d.get("line_percent", 0) for d in directories.values()]

            bars3 = ax3.bar(range(len(dir_names)), dir_coverage, alpha=0.8, color='#6f42c1')
            ax3.set_xlabel('目录')
            ax3.set_ylabel('覆盖率 (%)')
            ax3.set_title('目录覆盖率分布')
            ax3.set_xticks(range(len(dir_names)))
            ax3.set_xticklabels([name.replace("src/", "") for name in dir_names],
                               rotation=45, ha='right')
            ax3.grid(True, alpha=0.3)

            # 添加数值标签
            for bar, value in zip(bars3, dir_coverage):
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
        else:
            ax3.text(0.5, 0.5, '无目录数据', ha='center', va='center',
                    transform=ax3.transAxes, fontsize=16, alpha=0.5)
            ax3.set_title('目录覆盖率分布')

        # 覆盖率目标对比
        targets = {
            "总体": 85,
            "CLI": 90,
            "转换器": 85,
            "配置": 90,
            "工具链": 85
        }

        actual_values = [overall_percent]
        target_values = [targets["总体"]]
        labels = ["总体"]

        # 从目录数据中提取实际值
        for dir_name, target_name in [("src/cli", "CLI"), ("src/converter", "转换器"),
                                     ("src/config", "配置"), ("src/utils", "工具链")]:
            if dir_name in directories:
                actual_values.append(directories[dir_name].get("line_percent", 0))
                target_values.append(targets[target_name])
                labels.append(target_name)

        x = range(len(labels))
        width = 0.35

        bars4 = ax4.bar([i - width/2 for i in x], actual_values, width,
                       label='实际覆盖率', color='#28a745', alpha=0.8)
        bars5 = ax4.bar([i + width/2 for i in x], target_values, width,
                       label='目标覆盖率', color='#ffc107', alpha=0.8)

        ax4.set_xlabel('模块')
        ax4.set_ylabel('覆盖率 (%)')
        ax4.set_title('覆盖率目标达成情况')
        ax4.set_xticks(x)
        ax4.set_xticklabels(labels, rotation=45, ha='right')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.set_ylim(0, 100)

        # 添加数值标签
        for bar, value in zip(bars4, actual_values):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{value:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=8)

        for bar, value in zip(bars5, target_values):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{value:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=8)

        plt.tight_layout()

        # 保存为Base64
        chart_file = self.visualization_dir / "coverage_chart.png"
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()

        return self._encode_image_to_base64(chart_file)

    def generate_trend_analysis(self, history_data: List[Dict]) -> str:
        """生成趋势分析图表

        Args:
            history_data: 历史数据列表

        Returns:
            Base64编码的图片数据
        """
        if not HAS_PLOTTING or not history_data:
            return ""

        # 转换数据格式
        timestamps = []
        coverage_data = []
        test_success_data = []

        for record in history_data:
            try:
                timestamp = datetime.fromisoformat(record["timestamp"].replace('Z', '+00:00'))
                timestamps.append(timestamp)
                coverage_data.append(record.get("overall_percent", 0))
                test_success_data.append(record.get("success_rate", 0))
            except (ValueError, KeyError):
                continue

        if not timestamps:
            return ""

        # 创建图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))

        # 覆盖率趋势
        ax1.plot(timestamps, coverage_data, marker='o', linewidth=2, markersize=6,
                color='#28a745', label='覆盖率')
        ax1.set_xlabel('时间')
        ax1.set_ylabel('覆盖率 (%)')
        ax1.set_title('覆盖率变化趋势')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # 添加目标线
        ax1.axhline(y=85, color='red', linestyle='--', alpha=0.7, label='目标线 (85%)')

        # 格式化x轴
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        ax1.xaxis.set_major_locator(mdates.HourLocator(interval=12))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

        # 测试成功率趋势
        if test_success_data:
            ax2.plot(timestamps, test_success_data, marker='s', linewidth=2, markersize=6,
                    color='#007bff', label='测试成功率')
            ax2.set_xlabel('时间')
            ax2.set_ylabel('成功率 (%)')
            ax2.set_title('测试成功率变化趋势')
            ax2.grid(True, alpha=0.3)
            ax2.legend()

            # 添加目标线
            ax2.axhline(y=95, color='red', linestyle='--', alpha=0.7, label='目标线 (95%)')

            # 格式化x轴
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
            ax2.xaxis.set_major_locator(mdates.HourLocator(interval=12))
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

        plt.tight_layout()

        # 保存为Base64
        chart_file = self.visualization_dir / "trend_analysis.png"
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()

        return self._encode_image_to_base64(chart_file)

    def _encode_image_to_base64(self, image_path: Path) -> str:
        """将图片编码为Base64

        Args:
            image_path: 图片文件路径

        Returns:
            Base64编码的图片数据
        """
        try:
            with open(image_path, "rb") as image_file:
                encoded = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/png;base64,{encoded}"
        except Exception as e:
            print(f"❌ 编码图片失败: {e}")
            return ""

    def load_test_report(self) -> Optional[Dict]:
        """加载测试报告

        Returns:
            测试报告数据，如果加载失败返回None
        """
        report_file = self.reports_dir / "test_report.json"

        if not report_file.exists():
            print(f"❌ 测试报告文件不存在: {report_file}")
            return None

        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 加载测试报告失败: {e}")
            return None

    def load_coverage_history(self) -> List[Dict]:
        """加载覆盖率历史数据

        Returns:
            历史数据列表
        """
        history_file = self.project_root / "coverage_history.json"

        if not history_file.exists():
            return []

        try:
            with open(history_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ 加载历史数据失败: {e}")
            return []

    def generate_dashboard(self) -> str:
        """生成交互式仪表板

        Returns:
            HTML仪表板内容
        """
        print("🎨 生成测试可视化仪表板...")

        # 加载数据
        test_report = self.load_test_report()
        coverage_history = self.load_coverage_history()

        if not test_report:
            print("❌ 无法生成仪表板：缺少测试报告数据")
            return ""

        # 生成图表
        test_success_chart = self.generate_test_success_chart(test_report)
        performance_chart = self.generate_performance_chart(test_report)
        coverage_chart = self.generate_coverage_chart(test_report)
        trend_chart = self.generate_trend_analysis(coverage_history)

        # 提取关键指标
        summary = test_report.get("summary", {})
        metadata = test_report.get("metadata", {})
        recommendations = test_report.get("recommendations", [])

        # 生成HTML
        dashboard_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XLeRobot NPU Converter - 测试仪表板</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .dashboard-container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .header {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}

        .header h1 {{
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }}

        .header .timestamp {{
            color: #666;
            font-size: 1.1em;
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .metric-card {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}

        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        }}

        .metric-value {{
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .metric-label {{
            color: #666;
            font-size: 1.1em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .chart-container {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}

        .chart-container h2 {{
            color: #333;
            margin-bottom: 20px;
            font-weight: 400;
        }}

        .chart-image {{
            width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }}

        .recommendations {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}

        .recommendations h2 {{
            color: #333;
            margin-bottom: 20px;
            font-weight: 400;
        }}

        .recommendation-list {{
            list-style: none;
        }}

        .recommendation-item {{
            background: linear-gradient(135deg, #ffeaa7, #fdcb6e);
            border-radius: 10px;
            padding: 15px 20px;
            margin-bottom: 15px;
            border-left: 4px solid #fdcb6e;
            color: #2d3436;
            font-weight: 500;
        }}

        .footer {{
            text-align: center;
            margin-top: 40px;
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9em;
        }}

        .status-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }}

        .status-success {{
            background: #28a745;
            box-shadow: 0 0 10px rgba(40, 167, 69, 0.5);
        }}

        .status-warning {{
            background: #ffc107;
            box-shadow: 0 0 10px rgba(255, 193, 7, 0.5);
        }}

        .status-error {{
            background: #dc3545;
            box-shadow: 0 0 10px rgba(220, 53, 69, 0.5);
        }}

        @media (max-width: 768px) {{
            .dashboard-container {{
                padding: 10px;
            }}

            .header {{
                padding: 20px;
            }}

            .header h1 {{
                font-size: 2em;
            }}

            .metrics-grid {{
                grid-template-columns: 1fr;
            }}

            .chart-container {{
                padding: 20px;
            }}
        }}

        .loading {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 200px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="header">
            <h1>🧪 XLeRobot NPU Converter</h1>
            <div class="timestamp">
                <span class="status-indicator status-success"></span>
                测试仪表板 - {metadata.get('generated_at', '')[:19].replace('T', ' ')}
            </div>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{summary.get('total_tests', 0)}</div>
                <div class="metric-label">总测试数</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{summary.get('success_rate', 0):.1f}%</div>
                <div class="metric-label">成功率</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{summary.get('total_duration', 0):.1f}s</div>
                <div class="metric-label">执行时间</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{test_report.get('coverage', {}).get('overall_percent', 0):.1f}%</div>
                <div class="metric-label">代码覆盖率</div>
            </div>
        </div>

        <div class="chart-container">
            <h2>📊 测试结果分布</h2>
            {f'<img src="{test_success_chart}" class="chart-image" alt="测试结果分布">' if test_success_chart else '<div class="loading">图表生成中...</div>'}
        </div>

        <div class="chart-container">
            <h2>⚡ 性能指标分析</h2>
            {f'<img src="{performance_chart}" class="chart-image" alt="性能指标分析">' if performance_chart else '<div class="loading">图表生成中...</div>'}
        </div>

        <div class="chart-container">
            <h2>📈 代码覆盖率分析</h2>
            {f'<img src="{coverage_chart}" class="chart-image" alt="代码覆盖率分析">' if coverage_chart else '<div class="loading">图表生成中...</div>'}
        </div>

        {f'''
        <div class="chart-container">
            <h2>📊 趋势分析</h2>
            <img src="{trend_chart}" class="chart-image" alt="趋势分析">
        </div>
        ''' if trend_chart else ''}

        {f'''
        <div class="recommendations">
            <h2>💡 改进建议</h2>
            <ul class="recommendation-list">
                {"".join([f'<li class="recommendation-item">{rec}</li>' for rec in recommendations])}
            </ul>
        </div>
        ''' if recommendations else ''}

        <div class="footer">
            <p>🤖 由 XLeRobot NPU Converter Test Visualizer 自动生成</p>
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>

    <script>
        // 添加一些交互性
        document.addEventListener('DOMContentLoaded', function() {{
            // 为指标卡片添加点击效果
            const metricCards = document.querySelectorAll('.metric-card');
            metricCards.forEach(card => {{
                card.addEventListener('click', function() {{
                    this.style.transform = 'scale(1.05)';
                    setTimeout(() => {{
                        this.style.transform = '';
                    }}, 200);
                }});
            }});

            // 图表容器hover效果
            const chartContainers = document.querySelectorAll('.chart-container');
            chartContainers.forEach(container => {{
                container.addEventListener('mouseenter', function() {{
                    this.style.transform = 'translateY(-2px)';
                }});
                container.addEventListener('mouseleave', function() {{
                    this.style.transform = '';
                }});
            }});
        }});
    </script>
</body>
</html>'''

        return dashboard_html

    def save_dashboard(self, dashboard_html: str) -> None:
        """保存仪表板

        Args:
            dashboard_html: 仪表板HTML内容
        """
        try:
            with open(self.dashboard_file, 'w', encoding='utf-8') as f:
                f.write(dashboard_html)
            print(f"✅ 测试仪表板已保存: {self.dashboard_file}")
        except Exception as e:
            print(f"❌ 保存仪表板失败: {e}")

    def generate_and_save(self) -> None:
        """生成并保存可视化仪表板"""
        dashboard_html = self.generate_dashboard()
        if dashboard_html:
            self.save_dashboard(dashboard_html)
            print(f"🎨 可视化仪表板生成完成!")
            print(f"📊 仪表板地址: {self.dashboard_file}")
            print(f"🌐 在浏览器中打开查看: file://{self.dashboard_file.absolute()}")
        else:
            print("❌ 仪表板生成失败")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="生成测试结果可视化仪表板")
    parser.add_argument("--project-root", default=".", help="项目根目录")
    parser.add_argument("--output", help="输出目录")

    args = parser.parse_args()

    visualizer = TestResultVisualizer(args.project_root)

    if args.output:
        visualizer.visualization_dir = Path(args.output)
        visualizer.dashboard_file = visualizer.visualization_dir / "dashboard.html"

    visualizer.generate_and_save()


if __name__ == "__main__":
    main()