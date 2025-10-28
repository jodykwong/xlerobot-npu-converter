#!/usr/bin/env python3
"""
XLeRobot NPU Converter - 覆盖率监控脚本

提供代码覆盖率分析、报告生成和趋势监控功能。
支持CI/CD集成和本地开发使用。
"""

import os
import sys
import json
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class CoverageMonitor:
    """覆盖率监控器"""

    def __init__(self, project_root: str = None):
        """初始化覆盖率监控器

        Args:
            project_root: 项目根目录，默认为当前目录
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.coverage_dir = self.project_root / "htmlcov"
        self.coverage_file = self.project_root / "coverage.xml"
        self.report_file = self.project_root / "coverage_report.json"
        self.history_file = self.project_root / "coverage_history.json"

        # 覆盖率目标
        self.coverage_targets = {
            "overall": 85.0,
            "src/cli": 90.0,
            "src/converter": 85.0,
            "src/config": 90.0,
            "src/utils": 85.0
        }

    def run_coverage(self, test_path: str = None, extra_args: List[str] = None) -> int:
        """运行测试并生成覆盖率报告

        Args:
            test_path: 测试路径，默认为tests/
            extra_args: 额外的pytest参数

        Returns:
            退出码，0表示成功
        """
        cmd = [
            sys.executable, "-m", "pytest",
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-report=xml:coverage.xml",
            "--cov-report=json:coverage.json",
            "--cov-branch",
            "--cov-fail-under=85"
        ]

        if test_path:
            cmd.append(test_path)
        else:
            cmd.append("tests/")

        if extra_args:
            cmd.extend(extra_args)

        print(f"🧪 运行覆盖率分析: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, cwd=self.project_root)
            return result.returncode
        except FileNotFoundError:
            print("❌ pytest未找到，请安装pytest和pytest-cov")
            print("pip install pytest pytest-cov")
            return 1

    def parse_coverage_json(self) -> Dict:
        """解析覆盖率JSON报告

        Returns:
            覆盖率数据字典
        """
        coverage_json_file = self.project_root / "coverage.json"

        if not coverage_json_file.exists():
            return {}

        try:
            with open(coverage_json_file, 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"❌ 解析覆盖率报告失败: {e}")
            return {}

    def generate_coverage_report(self) -> Dict:
        """生成覆盖率报告

        Returns:
            覆盖率报告字典
        """
        coverage_data = self.parse_coverage_json()

        if not coverage_data:
            return {"error": "无法获取覆盖率数据"}

        report = {
            "timestamp": datetime.now().isoformat(),
            "overall": self._calculate_overall_coverage(coverage_data),
            "files": self._get_file_coverage(coverage_data),
            "directories": self._get_directory_coverage(coverage_data),
            "targets_status": self._check_coverage_targets(coverage_data),
            "summary": self._generate_summary(coverage_data)
        }

        return report

    def _calculate_overall_coverage(self, coverage_data: Dict) -> Dict:
        """计算总体覆盖率

        Args:
            coverage_data: 覆盖率数据

        Returns:
            总体覆盖率信息
        """
        totals = coverage_data.get("totals", {})

        return {
            "line_coverage": totals.get("covered_lines", 0),
            "line_total": totals.get("num_statements", 0),
            "line_percent": totals.get("percent_covered", 0),
            "branch_coverage": totals.get("covered_branches", 0),
            "branch_total": totals.get("num_branches", 0),
            "branch_percent": totals.get("percent_covered_display", 0)
        }

    def _get_file_coverage(self, coverage_data: Dict) -> List[Dict]:
        """获取文件覆盖率信息

        Args:
            coverage_data: 覆盖率数据

        Returns:
            文件覆盖率列表
        """
        files = coverage_data.get("files", {})
        file_list = []

        for file_path, file_data in files.items():
            if file_path.startswith("src/"):
                summary = file_data.get("summary", {})

                file_info = {
                    "file": file_path,
                    "line_coverage": summary.get("covered_lines", 0),
                    "line_total": summary.get("num_statements", 0),
                    "line_percent": summary.get("percent_covered", 0),
                    "missing_lines": summary.get("missing_lines", []),
                    "excluded_lines": summary.get("excluded_lines", [])
                }

                file_list.append(file_info)

        return sorted(file_list, key=lambda x: x["file"])

    def _get_directory_coverage(self, coverage_data: Dict) -> Dict:
        """获取目录覆盖率信息

        Args:
            coverage_data: 覆盖率数据

        Returns:
            目录覆盖率字典
        """
        directories = {}
        files = coverage_data.get("files", {})

        for file_path, file_data in files.items():
            if file_path.startswith("src/"):
                # 提取目录路径
                parts = file_path.split("/")
                if len(parts) >= 3:
                    dir_path = "/".join(parts[:3])

                    if dir_path not in directories:
                        directories[dir_path] = {
                            "line_coverage": 0,
                            "line_total": 0,
                            "files": []
                        }

                    summary = file_data.get("summary", {})
                    directories[dir_path]["line_coverage"] += summary.get("covered_lines", 0)
                    directories[dir_path]["line_total"] += summary.get("num_statements", 0)
                    directories[dir_path]["files"].append(file_path)

        # 计算目录覆盖率百分比
        for dir_path, dir_data in directories.items():
            if dir_data["line_total"] > 0:
                dir_data["line_percent"] = (dir_data["line_coverage"] / dir_data["line_total"]) * 100
            else:
                dir_data["line_percent"] = 0

        return directories

    def _check_coverage_targets(self, coverage_data: Dict) -> Dict:
        """检查覆盖率目标达成情况

        Args:
            coverage_data: 覆盖率数据

        Returns:
            目标检查结果
        """
        directories = self._get_directory_coverage(coverage_data)
        targets_status = {}

        # 检查总体覆盖率
        overall_percent = coverage_data.get("totals", {}).get("percent_covered", 0)
        targets_status["overall"] = {
            "target": self.coverage_targets["overall"],
            "actual": overall_percent,
            "passed": overall_percent >= self.coverage_targets["overall"]
        }

        # 检查各目录覆盖率
        for target_dir, target_percent in self.coverage_targets.items():
            if target_dir != "overall" and target_dir in directories:
                actual_percent = directories[target_dir]["line_percent"]
                targets_status[target_dir] = {
                    "target": target_percent,
                    "actual": actual_percent,
                    "passed": actual_percent >= target_percent
                }

        return targets_status

    def _generate_summary(self, coverage_data: Dict) -> Dict:
        """生成覆盖率摘要

        Args:
            coverage_data: 覆盖率数据

        Returns:
            覆盖率摘要
        """
        totals = coverage_data.get("totals", {})
        directories = self._get_directory_coverage(coverage_data)
        targets_status = self._check_coverage_targets(coverage_data)

        # 统计通过的覆盖率目标
        passed_targets = sum(1 for status in targets_status.values() if status.get("passed", False))
        total_targets = len(targets_status)

        return {
            "total_files": len([f for f in coverage_data.get("files", {}).keys() if f.startswith("src/")]),
            "total_lines": totals.get("num_statements", 0),
            "covered_lines": totals.get("covered_lines", 0),
            "coverage_percent": totals.get("percent_covered", 0),
            "targets_passed": passed_targets,
            "targets_total": total_targets,
            "targets_met_ratio": passed_targets / total_targets if total_targets > 0 else 0
        }

    def save_report(self, report: Dict) -> None:
        """保存覆盖率报告

        Args:
            report: 覆盖率报告
        """
        try:
            with open(self.report_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"✅ 覆盖率报告已保存: {self.report_file}")
        except Exception as e:
            print(f"❌ 保存覆盖率报告失败: {e}")

    def update_history(self, report: Dict) -> None:
        """更新覆盖率历史记录

        Args:
            report: 当前覆盖率报告
        """
        history = []

        # 读取现有历史记录
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
            except Exception:
                history = []

        # 添加当前记录
        history_entry = {
            "timestamp": report["timestamp"],
            "overall_percent": report["overall"]["line_percent"],
            "targets_passed": report["summary"]["targets_passed"],
            "targets_total": report["summary"]["targets_total"]
        }

        history.append(history_entry)

        # 只保留最近30条记录
        history = history[-30:]

        try:
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
            print(f"✅ 覆盖率历史已更新: {self.history_file}")
        except Exception as e:
            print(f"❌ 更新覆盖率历史失败: {e}")

    def print_report(self, report: Dict) -> None:
        """打印覆盖率报告

        Args:
            report: 覆盖率报告
        """
        print("\n" + "="*60)
        print("📊 XLeRobot NPU Converter - 覆盖率报告")
        print("="*60)

        # 总体覆盖率
        overall = report.get("overall", {})
        print(f"\n🎯 总体覆盖率:")
        print(f"   行覆盖率: {overall.get('line_percent', 0):.1f}% "
              f"({overall.get('line_coverage', 0)}/{overall.get('line_total', 0)})")
        if overall.get('branch_total', 0) > 0:
            print(f"   分支覆盖率: {overall.get('branch_percent', 0):.1f}% "
                  f"({overall.get('branch_coverage', 0)}/{overall.get('branch_total', 0)})")

        # 覆盖率目标
        targets_status = report.get("targets_status", {})
        print(f"\n🎯 覆盖率目标:")
        for target, status in targets_status.items():
            status_icon = "✅" if status.get("passed", False) else "❌"
            print(f"   {status_icon} {target}: {status.get('actual', 0):.1f}% "
                  f"(目标: {status.get('target', 0)}%)")

        # 目录覆盖率
        directories = report.get("directories", {})
        if directories:
            print(f"\n📁 目录覆盖率:")
            for dir_path, dir_data in directories.items():
                print(f"   {dir_path}: {dir_data.get('line_percent', 0):.1f}% "
                      f"({dir_data.get('files', 0)} 个文件)")

        # 摘要
        summary = report.get("summary", {})
        print(f"\n📈 摘要:")
        print(f"   文件总数: {summary.get('total_files', 0)}")
        print(f"   代码行数: {summary.get('total_lines', 0)}")
        print(f"   覆盖行数: {summary.get('covered_lines', 0)}")
        print(f"   目标达成: {summary.get('targets_passed', 0)}/{summary.get('targets_total', 0)} "
              f"({summary.get('targets_met_ratio', 0)*100:.1f}%)")

        print(f"\n📋 详细报告:")
        print(f"   HTML报告: {self.cover_dir}/index.html")
        print(f"   JSON数据: {self.report_file}")
        print(f"   历史记录: {self.history_file}")

        print("="*60)

    def check_thresholds(self, report: Dict) -> bool:
        """检查覆盖率是否达到阈值

        Args:
            report: 覆盖率报告

        Returns:
            是否达到所有阈值
        """
        targets_status = report.get("targets_status", {})

        # 检查所有目标是否通过
        failed_targets = []
        for target, status in targets_status.items():
            if not status.get("passed", False):
                failed_targets.append(target)

        if failed_targets:
            print(f"\n❌ 覆盖率未达标的模块: {', '.join(failed_targets)}")
            return False
        else:
            print(f"\n✅ 所有覆盖率目标都已达成!")
            return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="XLeRobot NPU Converter 覆盖率监控")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 运行覆盖率测试
    run_parser = subparsers.add_parser("run", help="运行覆盖率测试")
    run_parser.add_argument("--test-path", default="tests/", help="测试路径")
    run_parser.add_argument("--extra-args", nargs="*", help="额外的pytest参数")

    # 生成报告
    report_parser = subparsers.add_parser("report", help="生成覆盖率报告")
    report_parser.add_argument("--format", choices=["text", "json"], default="text", help="报告格式")

    # 检查阈值
    check_parser = subparsers.add_parser("check", help="检查覆盖率阈值")

    # 完整流程
    full_parser = subparsers.add_parser("full", help="完整流程：运行测试并生成报告")
    full_parser.add_argument("--test-path", default="tests/", help="测试路径")
    full_parser.add_argument("--extra-args", nargs="*", help="额外的pytest参数")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    monitor = CoverageMonitor()

    if args.command == "run":
        return monitor.run_coverage(args.test_path, args.extra_args)

    elif args.command == "report":
        report = monitor.generate_coverage_report()

        if args.format == "json":
            print(json.dumps(report, indent=2))
        else:
            monitor.print_report(report)

        monitor.save_report(report)
        monitor.update_history(report)
        return 0

    elif args.command == "check":
        report = monitor.generate_coverage_report()
        monitor.print_report(report)
        return 0 if monitor.check_thresholds(report) else 1

    elif args.command == "full":
        # 运行测试
        exit_code = monitor.run_coverage(args.test_path, args.extra_args)

        if exit_code == 0:
            # 生成报告
            report = monitor.generate_coverage_report()
            monitor.print_report(report)
            monitor.save_report(report)
            monitor.update_history(report)

            # 检查阈值
            if not monitor.check_thresholds(report):
                return 1

        return exit_code

    return 0


if __name__ == "__main__":
    sys.exit(main())