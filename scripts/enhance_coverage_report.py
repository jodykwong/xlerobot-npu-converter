#!/usr/bin/env python3
"""
覆盖率报告增强脚本

增强默认的HTML覆盖率报告，添加更多有用的信息和可视化。
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class CoverageReportEnhancer:
    """覆盖率报告增强器"""

    def __init__(self, project_root: str = None):
        """初始化增强器

        Args:
            project_root: 项目根目录
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.coverage_dir = self.project_root / "htmlcov"
        self.enhanced_file = self.coverage_dir / "enhanced_index.html"

    def load_coverage_data(self) -> Dict:
        """加载覆盖率数据

        Returns:
            覆盖率数据字典
        """
        coverage_file = self.project_root / "coverage.json"

        if not coverage_file.exists():
            return {}

        try:
            with open(coverage_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 加载覆盖率数据失败: {e}")
            return {}

    def load_history(self) -> List[Dict]:
        """加载历史覆盖率数据

        Returns:
            历史数据列表
        """
        history_file = self.project_root / "coverage_history.json"

        if not history_file.exists():
            return []

        try:
            with open(history_file, 'r') as f:
                return json.load(f)
        except Exception:
            return []

    def generate_trend_chart(self, history: List[Dict]) -> str:
        """生成趋势图表HTML

        Args:
            history: 历史数据

        Returns:
            趋势图表HTML
        """
        if not history:
            return "<p>暂无历史数据</p>"

        # 提取数据点
        dates = [entry["timestamp"][:10] for entry in history[-10:]]  # 最近10条
        coverage = [entry["overall_percent"] for entry in history[-10:]]

        # 生成简单的条形图
        max_coverage = max(coverage) if coverage else 100

        chart_html = '''
        <div class="trend-chart">
            <h3>覆盖率趋势 (最近10次)</h3>
            <div class="chart-container">
        '''

        for date, cov in zip(dates, coverage):
            height_percent = (cov / max_coverage) * 100 if max_coverage > 0 else 0
            color = self._get_coverage_color(cov)

            chart_html += f'''
                <div class="chart-bar" style="height: {height_percent}%; background-color: {color};"
                     title="{date}: {cov:.1f}%">
                    <span class="bar-label">{cov:.0f}%</span>
                </div>
            '''

        chart_html += '''
            </div>
            <div class="chart-labels">
        '''

        for date in dates:
            chart_html += f'<span class="date-label">{date}</span>'

        chart_html += '''
            </div>
        </div>
        '''

        return chart_html

    def _get_coverage_color(self, coverage: float) -> str:
        """获取覆盖率对应的颜色

        Args:
            coverage: 覆盖率百分比

        Returns:
            颜色值
        """
        if coverage >= 90:
            return "#28a745"
        elif coverage >= 80:
            return "#6c757d"
        elif coverage >= 70:
            return "#ffc107"
        else:
            return "#dc3545"

    def generate_file_analysis(self, coverage_data: Dict) -> str:
        """生成文件分析HTML

        Args:
            coverage_data: 覆盖率数据

        Returns:
            文件分析HTML
        """
        files = coverage_data.get("files", {})
        src_files = [(path, data) for path, data in files.items() if path.startswith("src/")]

        if not src_files:
            return "<p>没有找到源码文件</p>"

        # 按覆盖率排序
        src_files.sort(key=lambda x: x[1].get("summary", {}).get("percent_covered", 0))

        analysis_html = '''
        <div class="file-analysis">
            <h3>文件覆盖率分析</h3>
            <table class="file-table">
                <thead>
                    <tr>
                        <th>文件</th>
                        <th>覆盖率</th>
                        <th>状态</th>
                        <th>详情</th>
                    </tr>
                </thead>
                <tbody>
        '''

        for file_path, file_data in src_files:
            summary = file_data.get("summary", {})
            coverage = summary.get("percent_covered", 0)
            covered = summary.get("covered_lines", 0)
            total = summary.get("num_statements", 0)
            missing = summary.get("missing_lines", [])

            status = self._get_file_status(coverage)
            status_color = self._get_coverage_color(coverage)

            analysis_html += f'''
                <tr>
                    <td class="file-path">{file_path}</td>
                    <td class="coverage-percent" style="color: {status_color};">{coverage:.1f}%</td>
                    <td class="status">{status}</td>
                    <td class="details">
                        {covered}/{total} 行
                        {f"({len(missing)} 缺失)" if missing else ""}
                    </td>
                </tr>
            '''

        analysis_html += '''
                </tbody>
            </table>
        </div>
        '''

        return analysis_html

    def _get_file_status(self, coverage: float) -> str:
        """获取文件状态

        Args:
            coverage: 覆盖率百分比

        Returns:
            状态字符串
        """
        if coverage >= 90:
            return "优秀"
        elif coverage >= 80:
            return "良好"
        elif coverage >= 70:
            return "一般"
        elif coverage >= 50:
            return "需改进"
        else:
            return "严重"

    def generate_directory_summary(self, coverage_data: Dict) -> str:
        """生成目录摘要HTML

        Args:
            coverage_data: 覆盖率数据

        Returns:
            目录摘要HTML
        """
        directories = {}
        files = coverage_data.get("files", {})

        # 按目录分组
        for file_path, file_data in files.items():
            if file_path.startswith("src/"):
                parts = file_path.split("/")
                if len(parts) >= 3:
                    dir_path = "/".join(parts[:3])

                    if dir_path not in directories:
                        directories[dir_path] = {
                            "files": [],
                            "total_lines": 0,
                            "covered_lines": 0
                        }

                    summary = file_data.get("summary", {})
                    directories[dir_path]["files"].append(file_path)
                    directories[dir_path]["total_lines"] += summary.get("num_statements", 0)
                    directories[dir_path]["covered_lines"] += summary.get("covered_lines", 0)

        # 计算覆盖率
        for dir_path, dir_data in directories.items():
            if dir_data["total_lines"] > 0:
                dir_data["coverage"] = (dir_data["covered_lines"] / dir_data["total_lines"]) * 100
            else:
                dir_data["coverage"] = 0

        summary_html = '''
        <div class="directory-summary">
            <h3>目录覆盖率摘要</h3>
            <div class="directory-grid">
        '''

        for dir_path, dir_data in directories.items():
            coverage = dir_data["coverage"]
            color = self._get_coverage_color(coverage)

            summary_html += f'''
                <div class="directory-card" style="border-left: 4px solid {color};">
                    <h4>{dir_path}</h4>
                    <div class="coverage-display">{coverage:.1f}%</div>
                    <div class="directory-stats">
                        <div>文件数: {len(dir_data["files"])}</div>
                        <div>代码行: {dir_data["total_lines"]}</div>
                        <div>覆盖行: {dir_data["covered_lines"]}</div>
                    </div>
                </div>
            '''

        summary_html += '''
            </div>
        </div>
        '''

        return summary_html

    def generate_enhanced_html(self, coverage_data: Dict, history: List[Dict]) -> str:
        """生成增强的HTML报告

        Args:
            coverage_data: 覆盖率数据
            history: 历史数据

        Returns:
            增强的HTML内容
        """
        totals = coverage_data.get("totals", {})
        overall_coverage = totals.get("percent_covered", 0)

        html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XLeRobot NPU Converter - 增强覆盖率报告</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}

        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}

        .header .subtitle {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}

        .overall-metric {{
            background: #f8f9fa;
            margin: 30px;
            padding: 30px;
            border-radius: 8px;
            text-align: center;
            border-left: 5px solid {self._get_coverage_color(overall_coverage)};
        }}

        .overall-metric .coverage-number {{
            font-size: 4em;
            font-weight: bold;
            color: {self._get_coverage_color(overall_coverage)};
            margin: 0;
        }}

        .overall-metric .coverage-label {{
            font-size: 1.2em;
            color: #6c757d;
            margin-top: 10px;
        }}

        .content {{
            padding: 0 30px 30px;
        }}

        .section {{
            margin-bottom: 40px;
        }}

        .section h3 {{
            color: #495057;
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}

        .file-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}

        .file-table th, .file-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }}

        .file-table th {{
            background-color: #f8f9fa;
            font-weight: 600;
        }}

        .file-table tr:hover {{
            background-color: #f8f9fa;
        }}

        .file-path {{
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.9em;
        }}

        .coverage-percent {{
            font-weight: bold;
        }}

        .directory-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}

        .directory-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e9ecef;
        }}

        .directory-card h4 {{
            margin: 0 0 15px 0;
            color: #495057;
        }}

        .coverage-display {{
            font-size: 2em;
            font-weight: bold;
            margin: 15px 0;
        }}

        .directory-stats div {{
            margin: 5px 0;
            font-size: 0.9em;
            color: #6c757d;
        }}

        .chart-container {{
            display: flex;
            align-items: end;
            height: 200px;
            gap: 10px;
            margin: 20px 0;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
        }}

        .chart-bar {{
            flex: 1;
            min-width: 30px;
            background: #6c757d;
            border-radius: 4px 4px 0 0;
            position: relative;
            display: flex;
            align-items: end;
            justify-content: center;
            padding-bottom: 5px;
        }}

        .bar-label {{
            color: white;
            font-size: 0.8em;
            font-weight: bold;
        }}

        .chart-labels {{
            display: flex;
            gap: 10px;
            margin-top: 10px;
            overflow-x: auto;
        }}

        .date-label {{
            flex: 1;
            min-width: 30px;
            text-align: center;
            font-size: 0.8em;
            color: #6c757d;
        }}

        .status {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
        }}

        .status.优秀 {{
            background: #d4edda;
            color: #155724;
        }}

        .status.良好 {{
            background: #cce5ff;
            color: #004085;
        }}

        .status.一般 {{
            background: #fff3cd;
            color: #856404;
        }}

        .status.需改进 {{
            background: #f8d7da;
            color: #721c24;
        }}

        .status.严重 {{
            background: #f5c6cb;
            color: #491217;
        }}

        .footer {{
            background: #343a40;
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: 40px;
        }}

        @media (max-width: 768px) {{
            .directory-grid {{
                grid-template-columns: 1fr;
            }}

            .chart-container {{
                gap: 5px;
            }}

            .file-table {{
                font-size: 0.8em;
            }}

            .file-table th, .file-table td {{
                padding: 8px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>XLeRobot NPU Converter</h1>
            <div class="subtitle">增强覆盖率报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>

        <div class="overall-metric">
            <div class="coverage-number">{overall_coverage:.1f}%</div>
            <div class="coverage-label">总体覆盖率</div>
        </div>

        <div class="content">
            <div class="section">
                {self.generate_trend_chart(history)}
            </div>

            <div class="section">
                {self.generate_directory_summary(coverage_data)}
            </div>

            <div class="section">
                {self.generate_file_analysis(coverage_data)}
            </div>
        </div>

        <div class="footer">
            <p>报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>由 XLeRobot NPU Converter Coverage Monitor 生成</p>
        </div>
    </div>
</body>
</html>'''

        return html_template

    def generate_enhanced_report(self) -> None:
        """生成增强的覆盖率报告"""
        print("🔄 正在生成增强覆盖率报告...")

        # 加载数据
        coverage_data = self.load_coverage_data()
        history = self.load_history()

        if not coverage_data:
            print("❌ 无法加载覆盖率数据")
            return

        # 生成HTML
        html_content = self.generate_enhanced_html(coverage_data, history)

        # 确保目录存在
        self.coverage_dir.mkdir(parents=True, exist_ok=True)

        # 保存文件
        try:
            with open(self.enhanced_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"✅ 增强覆盖率报告已保存: {self.enhanced_file}")
            print(f"📂 原始报告: {self.coverage_dir}/index.html")
            print(f"📂 增强报告: {self.enhanced_file}")
        except Exception as e:
            print(f"❌ 保存增强报告失败: {e}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="生成增强覆盖率报告")
    parser.add_argument("--project-root", default=".", help="项目根目录")

    args = parser.parse_args()

    enhancer = CoverageReportEnhancer(args.project_root)
    enhancer.generate_enhanced_report()


if __name__ == "__main__":
    main()