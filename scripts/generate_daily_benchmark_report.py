#!/usr/bin/env python3
"""
每日性能基准测试报告生成器
Daily Performance Benchmark Report Generator

Usage:
    python scripts/generate_daily_benchmark_report.py --input reports/nightly.json --output daily_report.html
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from npu_converter.performance import ReportGenerator, ReportConfig


def generate_daily_report(input_file, output_file, config=None):
    """生成每日性能报告"""

    # 加载测试数据
    with open(input_file, 'r') as f:
        test_data = json.load(f)

    # 创建报告配置
    if config is None:
        config = ReportConfig(
            output_dir=str(Path(output_file).parent),
            include_charts=True,
            include_recommendations=True,
            include_trends=True
        )

    # 创建报告生成器
    generator = ReportGenerator(config)

    # 生成HTML报告
    generator.generate_html_report(test_data, output_file)

    print(f"✅ Daily benchmark report generated: {output_file}")

    # 统计信息
    print("\n📊 Report Statistics:")
    print(f"  - Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"  - Total Tests: {test_data.get('total_tests', 'N/A')}")
    print(f"  - Pass Rate: {test_data.get('pass_rate', 'N/A')}")
    print(f"  - Average Duration: {test_data.get('avg_duration', 'N/A')}")


def main():
    parser = argparse.ArgumentParser(description="Generate daily benchmark report")
    parser.add_argument("--input", required=True, help="Input JSON file with benchmark results")
    parser.add_argument("--output", required=True, help="Output HTML file")
    parser.add_argument("--config", help="Path to report config file")
    args = parser.parse_args()

    # 验证输入文件
    if not Path(args.input).exists():
        print(f"❌ Error: Input file not found: {args.input}")
        sys.exit(1)

    # 生成报告
    generate_daily_report(args.input, args.output)


if __name__ == "__main__":
    main()
