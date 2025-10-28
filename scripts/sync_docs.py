#!/usr/bin/env python3
"""
文档同步脚本

自动同步README.md与BMM工作流状态，确保文档与项目状态一致。
功能包括:
- 提取BMM工作流状态
- 更新README中的项目状态
- 更新覆盖率信息
- 验证文档一致性

使用方式:
    python scripts/sync_docs.py --check-only  # 仅检查不同步
    python scripts/sync_docs.py --sync        # 自动同步
    python scripts/sync_docs.py --report      # 生成报告
"""

import re
import sys
import yaml
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
README_PATH = PROJECT_ROOT / "README.md"
BMM_STATUS_PATH = PROJECT_ROOT / "docs" / "bmm-workflow-status.md"
SPRINT_STATUS_PATH = PROJECT_ROOT / "docs" / "sprint-status.yaml"

class DocSyncer:
    """文档同步器"""

    def __init__(self):
        self.changes = []

    def extract_bmm_status(self) -> Dict:
        """从BMM工作流状态文档提取信息"""
        status_info = {
            "last_updated": "",
            "epic_progress": {},
            "code_quality": "",
            "test_coverage": "",
            "completed_stories": [],
            "current_focus": ""
        }

        try:
            with open(BMM_STATUS_PATH, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取最后更新时间
            match = re.search(r'\*\*最后更新\*\*:\s*([^\n]+)', content)
            if match:
                status_info["last_updated"] = match.group(1).strip()

            # 提取Epic进度
            epic_match = re.search(r'current_focus:\s*\'([^\']+)\'', content)
            if epic_match:
                status_info["current_focus"] = epic_match.group(1)

            # 提取整体进度
            progress_match = re.search(r'status:\s*STORY\s+([^\s]+)\s+-\s+EPIC\s+(\d+)\s+PROGRESS\s+(\d+)%', content)
            if progress_match:
                status_info["current_story"] = progress_match.group(1)
                status_info["current_epic"] = progress_match.group(2)
                status_info["epic_progress"] = {
                    "epic_1": "100%",
                    f"epic_{progress_match.group(2)}": f"{progress_match.group(3)}%"
                }

            # 提取代码质量
            quality_match = re.search(r'code_quality:\s*(\d+)/100', content)
            if quality_match:
                status_info["code_quality"] = quality_match.group(1)

            # 提取测试覆盖率
            coverage_match = re.search(r'test_coverage:\s*(\d+)/100', content)
            if coverage_match:
                status_info["test_coverage"] = coverage_match.group(1)

        except Exception as e:
            print(f"警告: 无法读取BMM状态文档: {e}")

        return status_info

    def extract_sprint_status(self) -> Dict:
        """从Sprint状态YAML提取信息"""
        sprint_info = {
            "development_status": {}
        }

        try:
            with open(SPRINT_STATUS_PATH, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if 'development_status' in data:
                sprint_info["development_status"] = data['development_status']

        except Exception as e:
            print(f"警告: 无法读取Sprint状态文档: {e}")

        return sprint_info

    def update_readme_status(self, status_info: Dict, dry_run: bool = False) -> bool:
        """更新README中的项目状态"""
        changes_made = False

        try:
            with open(README_PATH, 'r', encoding='utf-8') as f:
                readme_content = f.read()

            original_content = readme_content

            # 更新项目状态部分
            if "epic_progress" in status_info:
                # 构建新的状态字符串
                epic_lines = []
                for epic, progress in status_info["epic_progress"].items():
                    if epic == "epic_1":
                        epic_lines.append(f"- **🔧 Epic 1**: ✅ 核心基础设施 {progress} 完成 (8/8故事)")
                    elif epic == "epic_2":
                        epic_lines.append(f"- **⚡ Epic 2**: ⚡ 模型转换与验证 {progress} 完成 (2/6故事)")

                if epic_lines:
                    # 查找并替换项目状态部分
                    status_pattern = r'## 📋 项目状态\n\n### ✅ 架构重构已完成.*?(?=###)'
                    new_status = f"""## 📋 项目状态

### ✅ 架构重构已完成 (2025-10-27)
**当前阶段**: Epic 1完成，Epic 2开发进行中

- **📊 整体进度**: {epic_lines[0].split()[-3]} {epic_lines[0].split()[-2]} {epic_lines[0].split()[-1]}
{chr(10).join(epic_lines)}
- **⏸️ Epic 3**: 性能优化与扩展 0%未开始 (等待Epic 2完成)"""

                    readme_content = re.sub(status_pattern, new_status, readme_content, flags=re.DOTALL)
                    if readme_content != original_content:
                        self.changes.append("更新项目状态进度")
                        changes_made = True
                        original_content = readme_content

            # 更新代码质量
            if "code_quality" in status_info:
                quality = status_info["code_quality"]
                quality_pattern = r'- \*\*📏 代码质量\*\*: ✅ 企业级标准 \((\d+)/100\)'
                readme_content = re.sub(
                    quality_pattern,
                    f'- **📏 代码质量**: ✅ 企业级标准 ({quality}/100)',
                    readme_content
                )
                if readme_content != original_content:
                    self.changes.append(f"更新代码质量到{quality}/100")
                    changes_made = True
                    original_content = readme_content

            # 更新测试覆盖率
            if "test_coverage" in status_info:
                coverage = status_info["test_coverage"]
                coverage_pattern = r'- \*\*🧪 测试覆盖\*\*: (\d+)%代码覆盖率'
                readme_content = re.sub(
                    coverage_pattern,
                    f'- **🧪 测试覆盖**: {coverage}%代码覆盖率',
                    readme_content
                )
                if readme_content != original_content:
                    self.changes.append(f"更新测试覆盖率到{coverage}%")
                    changes_made = True
                    original_content = readme_content

            # 更新时间戳
            current_date = datetime.now().strftime("%Y-%m-%d")
            timestamp_pattern = r'\*最后更新:\s*\d{4}-\d{2}-\d{2}\*'
            new_timestamp = f"*最后更新: {current_date}*"

            if re.search(timestamp_pattern, readme_content):
                readme_content = re.sub(timestamp_pattern, new_timestamp, readme_content)
            else:
                # 如果没有找到时间戳，在文档末尾添加
                readme_content = readme_content.rstrip() + f"\n\n{new_timestamp}\n"

            if readme_content != original_content:
                self.changes.append("更新时间戳")
                changes_made = True

            # 写入文件
            if changes_made and not dry_run:
                with open(README_PATH, 'w', encoding='utf-8') as f:
                    f.write(readme_content)

        except Exception as e:
            print(f"错误: 无法更新README: {e}")
            return False

        return changes_made

    def check_consistency(self) -> List[str]:
        """检查文档一致性"""
        issues = []

        # 检查README与BMM状态是否一致
        try:
            with open(README_PATH, 'r', encoding='utf-8') as f:
                readme = f.read()

            with open(BMM_STATUS_PATH, 'r', encoding='utf-8') as f:
                bmm = f.read()

            # 检查Epic状态
            readme_epic1 = "Epic 1: ✅" in readme
            bmm_epic1_done = "Epic 1: 100%" in bmm

            if readme_epic1 != bmm_epic1_done:
                issues.append("README中的Epic 1状态与BMM工作流状态不一致")

            # 检查更新时间
            readme_date_match = re.search(r'\*最后更新:\s*(\d{4}-\d{2}-\d{2})\*', readme)
            if readme_date_match:
                readme_date = datetime.strptime(readme_date_match.group(1), '%Y-%m-%d')
                file_mtime = datetime.fromtimestamp(README_PATH.stat().st_mtime)
                if (file_mtime - readme_date).days > 1:
                    issues.append("README更新时间戳可能过时")

        except Exception as e:
            issues.append(f"无法检查文档一致性: {e}")

        return issues

    def generate_report(self) -> str:
        """生成同步报告"""
        status_info = self.extract_bmm_status()
        issues = self.check_consistency()

        report = f"""
# 文档同步报告

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 当前状态

### BMM工作流状态
- 最后更新: {status_info.get('last_updated', '未知')}
- 当前焦点: {status_info.get('current_focus', '未知')}
- 代码质量: {status_info.get('code_quality', '未知')}/100
- 测试覆盖率: {status_info.get('test_coverage', '未知')}/100

### Epic进度
{chr(10).join([f'- {k}: {v}' for k, v in status_info.get('epic_progress', {}).items()])}

## 检查结果

### 发现的问题
{chr(10).join([f'❌ {issue}' for issue in issues]) if issues else '✅ 未发现一致性问题'}

### 建议的操作
{chr(10).join([f'- {change}' for change in self.changes]) if self.changes else '- 无需同步操作'}

## 建议

1. 定期运行此脚本检查文档一致性
2. 在代码审查时同步更新相关文档
3. 设置CI检查自动验证文档状态

---
*此报告由 scripts/sync_docs.py 自动生成*
"""

        return report


def main():
    parser = argparse.ArgumentParser(description='同步项目文档状态')
    parser.add_argument('--check-only', action='store_true', help='仅检查不进行同步')
    parser.add_argument('--sync', action='store_true', help='执行同步操作')
    parser.add_argument('--report', action='store_true', help='生成同步报告')
    parser.add_argument('--dry-run', action='store_true', help='预览模式，不实际修改文件')

    args = parser.parse_args()

    if not any([args.check_only, args.sync, args.report]):
        args.check_only = True

    syncer = DocSyncer()

    if args.check_only or args.report:
        issues = syncer.check_consistency()
        if issues:
            print("⚠️ 发现文档一致性问题:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ 文档状态一致")

    if args.report:
        report = syncer.generate_report()
        print(report)

        # 保存报告到文件
        report_path = PROJECT_ROOT / "docs" / "doc_sync_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n📄 报告已保存到: {report_path}")

    if args.sync:
        print("🔄 开始同步文档...")
        status_info = syncer.extract_bmm_status()

        if args.dry_run:
            print("🔍 预览模式 - 将要进行的更改:")
            syncer.update_readme_status(status_info, dry_run=True)
            for change in syncer.changes:
                print(f"  - {change}")
        else:
            changes = syncer.update_readme_status(status_info)
            if changes:
                print("✅ 文档同步完成")
                for change in syncer.changes:
                    print(f"  - {change}")
            else:
                print("ℹ️ 无需同步")

    return 0


if __name__ == "__main__":
    sys.exit(main())
