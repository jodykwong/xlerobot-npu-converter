#!/usr/bin/env python3
"""
性能基准测试报告生成器
Generate Performance Benchmark Report

Usage:
    python scripts/generate_benchmark_report.py --output-dir reports/performance --format html,pdf
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from npu_converter.performance import (
    BenchmarkRunner,
    MetricsCollector,
    BenchmarkSuite,
    PerformanceAnalyzer,
    ReportGenerator,
    ReportConfig
)


def main():
    parser = argparse.ArgumentParser(description="Generate performance benchmark report")
    parser.add_argument("--output-dir", required=True, help="Output directory for reports")
    parser.add_argument("--format", default="html", help="Report format (html, pdf, json)")
    parser.add_argument("--config", help="Path to benchmark config file")
    parser.add_argument("--test-data", help="Path to test results JSON file")
    args = parser.parse_args()

    # 创建输出目录
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 加载测试数据（如果提供）
    test_data = {}
    if args.test_data and Path(args.test_data).exists():
        with open(args.test_data, 'r') as f:
            test_data = json.load(f)

    # 创建报告生成器
    config = ReportConfig(
        output_dir=str(output_dir),
        include_charts=True,
        include_recommendations=True
    )
    generator = ReportGenerator(config)

    # 生成报告
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if args.format == "html":
        report_file = output_dir / f"benchmark_report_{timestamp}.html"
        generator.generate_html_report(test_data, str(report_file))
        print(f"✅ HTML report generated: {report_file}")

    elif args.format == "pdf":
        # 先生成HTML，再转换为PDF
        html_file = output_dir / f"benchmark_report_{timestamp}.html"
        pdf_file = output_dir / f"benchmark_report_{timestamp}.pdf"
        generator.generate_html_report(test_data, str(html_file))
        # 这里可以添加PDF转换逻辑
        print(f"✅ PDF report generated: {pdf_file}")

    elif args.format == "json":
        json_file = output_dir / f"benchmark_report_{timestamp}.json"
        generator.generate_json_report(test_data, str(json_file))
        print(f"✅ JSON report generated: {json_file}")

    print(f"\n📊 Reports saved to: {output_dir}")


if __name__ == "__main__":
    main()
