#!/usr/bin/env python3
"""
覆盖率徽章生成脚本

生成基于当前覆盖率的徽章SVG文件，可用于README或文档显示。
"""

import json
import sys
from pathlib import Path
from typing import Dict, Tuple


class CoverageBadgeGenerator:
    """覆盖率徽章生成器"""

    def __init__(self, project_root: str = None):
        """初始化徽章生成器

        Args:
            project_root: 项目根目录
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.coverage_file = self.project_root / "coverage.json"
        self.badge_file = self.project_root / "docs" / "coverage_badge.svg"

    def get_coverage_percent(self) -> float:
        """获取覆盖率百分比

        Returns:
            覆盖率百分比，如果获取失败返回0
        """
        if not self.coverage_file.exists():
            print(f"❌ 覆盖率文件不存在: {self.coverage_file}")
            return 0.0

        try:
            with open(self.coverage_file, 'r') as f:
                data = json.load(f)

            totals = data.get("totals", {})
            return totals.get("percent_covered", 0.0)
        except Exception as e:
            print(f"❌ 读取覆盖率数据失败: {e}")
            return 0.0

    def get_coverage_color(self, coverage: float) -> str:
        """根据覆盖率获取颜色

        Args:
            coverage: 覆盖率百分比

        Returns:
            十六进制颜色值
        """
        if coverage >= 90:
            return "#28a745"  # 绿色
        elif coverage >= 80:
            return "#a3c663"  # 浅绿色
        elif coverage >= 70:
            return "#ffc107"  # 黄色
        elif coverage >= 60:
            return "#fd7e14"  # 橙色
        else:
            return "#dc3545"  # 红色

    def calculate_badge_dimensions(self, text: str) -> Tuple[int, int, int, int]:
        """计算徽章尺寸

        Args:
            text: 徽章文本

        Returns:
            (总宽度, 左部分宽度, 右部分宽度, 高度)
        """
        # 估算文本宽度 (每个字符约8像素)
        left_text = "coverage"
        right_text = f"{text}%"

        left_width = len(left_text) * 8 + 20
        right_width = len(right_text) * 8 + 20
        total_width = left_width + right_width
        height = 28

        return total_width, left_width, right_width, height

    def generate_svg(self, coverage: float) -> str:
        """生成徽章SVG

        Args:
            coverage: 覆盖率百分比

        Returns:
            SVG字符串
        """
        coverage_text = f"{coverage:.1f}"
        color = self.get_coverage_color(coverage)
        total_width, left_width, right_width, height = self.calculate_badge_dimensions(coverage_text)

        svg_template = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="{height}">
  <defs>
    <clipPath id="clip-left">
      <rect width="{left_width}" height="{height}" rx="3"/>
    </clipPath>
    <clipPath id="clip-right">
      <rect x="{left_width}" width="{right_width}" height="{height}" rx="3"/>
    </clipPath>
  </defs>

  <!-- 左侧背景 -->
  <rect width="{left_width}" height="{height}" fill="#555" clip-path="url(#clip-left)"/>

  <!-- 右侧背景 -->
  <rect x="{left_width}" width="{right_width}" height="{height}" fill="{color}" clip-path="url(#clip-right)"/>

  <!-- 左侧文本 -->
  <text x="{left_width//2}" y="{height//2 + 5}"
        font-family="Verdana, Arial, sans-serif"
        font-size="11"
        fill="white"
        text-anchor="middle">
    coverage
  </text>

  <!-- 右侧文本 -->
  <text x="{left_width + right_width//2}" y="{height//2 + 5}"
        font-family="Verdana, Arial, sans-serif"
        font-size="11"
        fill="white"
        text-anchor="middle">
    {coverage_text}%
  </text>
</svg>'''

        return svg_template

    def save_badge(self, svg_content: str) -> None:
        """保存徽章文件

        Args:
            svg_content: SVG内容
        """
        # 确保docs目录存在
        self.badge_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.badge_file, 'w') as f:
                f.write(svg_content)
            print(f"✅ 覆盖率徽章已保存: {self.badge_file}")
        except Exception as e:
            print(f"❌ 保存徽章失败: {e}")

    def generate_and_save(self) -> None:
        """生成并保存覆盖率徽章"""
        coverage = self.get_coverage_percent()
        svg_content = self.generate_svg(coverage)
        self.save_badge(svg_content)

        print(f"📊 覆盖率: {coverage:.1f}%")
        print(f"🎨 颜色: {self.get_coverage_color(coverage)}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="生成覆盖率徽章")
    parser.add_argument("--project-root", default=".", help="项目根目录")
    parser.add_argument("--output", help="输出文件路径")

    args = parser.parse_args()

    generator = CoverageBadgeGenerator(args.project_root)

    if args.output:
        generator.badge_file = Path(args.output)

    generator.generate_and_save()


if __name__ == "__main__":
    main()