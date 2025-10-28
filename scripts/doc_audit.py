#!/usr/bin/env python3
"""
定期文档质量审计脚本

自动执行文档质量检查，生成审计报告，支持以下检查:
- 文档完整性检查
- 链接有效性验证
- 内容质量评估
- 一致性检查
- 格式规范检查
- 指标统计和趋势分析

使用方法:
    python scripts/doc_audit.py --full          # 完整审计
    python scripts/doc_audit.py --quick         # 快速检查
    python scripts/doc_audit.py --report        # 生成报告
    python scripts/doc_audit.py --schedule      # 设置定时任务
"""

import re
import os
import sys
import json
import yaml
import argparse
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
README_PATH = PROJECT_ROOT / "README.md"

# 必要文档列表
REQUIRED_DOCS = [
    "README.md",
    "docs/PRD.md",
    "docs/architecture.md",
    "docs/bmm-workflow-status.md",
    "docs/sprint-status.yaml",
    "docs/production-deployment-guide.md",
    "docs/cli-usage-guide.md",
    "docs/cli-usage-examples.md",
    "docs/doc-review-checklist.md",
]

# 文档质量阈值
QUALITY_THRESHOLDS = {
    "coverage": 0.95,  # 95%
    "consistency": 0.98,  # 98%
    "link_validity": 0.98,  # 98%
    "format_compliance": 0.99,  # 99%
    "user_satisfaction": 4.0,  # 4.0/5.0
}

@dataclass
class AuditResult:
    """审计结果数据类"""
    timestamp: str
    doc_type: str
    status: str
    score: float
    issues: List[str]
    metrics: Dict
    recommendations: List[str]

class DocAuditor:
    """文档审计器"""

    def __init__(self):
        self.results: List[AuditResult] = []
        self.issues_list: List[str] = []
        self.metrics: Dict = {}

    def check_doc_completeness(self) -> AuditResult:
        """检查文档完整性"""
        issues = []
        missing_docs = []

        for doc in REQUIRED_DOCS:
            doc_path = PROJECT_ROOT / doc
            if not doc_path.exists():
                missing_docs.append(doc)

        if missing_docs:
            issues.append(f"缺少必要文档: {', '.join(missing_docs)}")

        # 检查文档大小
        for doc in REQUIRED_DOCS:
            doc_path = PROJECT_ROOT / doc
            if doc_path.exists():
                size = doc_path.stat().st_size
                if size > 1048576:  # 1MB
                    issues.append(f"文档过大: {doc} ({(size/1048576):.1f}MB)")

        coverage = 1.0 - (len(missing_docs) / len(REQUIRED_DOCS))

        return AuditResult(
            timestamp=datetime.now().isoformat(),
            doc_type="Completeness",
            status="PASS" if coverage >= QUALITY_THRESHOLDS["coverage"] else "FAIL",
            score=coverage,
            issues=issues,
            metrics={"total_required": len(REQUIRED_DOCS), "missing": len(missing_docs)},
            recommendations=["补充缺少的文档", "优化过大文档"] if issues else []
        )

    def check_link_validity(self) -> AuditResult:
        """检查链接有效性"""
        issues = []
        total_links = 0
        broken_links = 0

        # 检查README中的链接
        if README_PATH.exists():
            with open(README_PATH, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取链接
            links = re.findall(r'\[.*?\]\((.*?)\)', content)
            total_links += len(links)

            for link in links:
                # 跳过外部链接和锚点
                if link.startswith(('http://', 'https://', '#', 'mailto:')):
                    continue

                link_path = PROJECT_ROOT / link
                if not link_path.exists():
                    issues.append(f"断链: {link}")
                    broken_links += 1

        # 检查docs目录中的链接
        for doc_path in DOCS_DIR.rglob("*.md"):
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()

            links = re.findall(r'\[.*?\]\((.*?)\)', content)
            for link in links:
                if link.startswith(('http://', 'https://', '#', 'mailto:')):
                    continue

                link_path = PROJECT_ROOT / link
                if not link_path.exists():
                    issues.append(f"断链 {doc_path.relative_to(PROJECT_ROOT)}: {link}")
                    broken_links += 1

            total_links += len(links)

        validity = 1.0 - (broken_links / total_links) if total_links > 0 else 1.0

        return AuditResult(
            timestamp=datetime.now().isoformat(),
            doc_type="Link Validity",
            status="PASS" if validity >= QUALITY_THRESHOLDS["link_validity"] else "FAIL",
            score=validity,
            issues=issues,
            metrics={"total_links": total_links, "broken_links": broken_links},
            recommendations=["修复断链", "添加链接检查到CI"] if issues else []
        )

    def check_consistency(self) -> AuditResult:
        """检查文档一致性"""
        issues = []

        # 检查README与BMM状态的一致性
        try:
            with open(README_PATH, 'r', encoding='utf-8') as f:
                readme = f.read()

            bmm_path = DOCS_DIR / "bmm-workflow-status.md"
            if bmm_path.exists():
                with open(bmm_path, 'r', encoding='utf-8') as f:
                    bmm = f.read()

                # 检查Epic状态
                readme_epic1 = "Epic 1: ✅" in readme or "Epic 1 100%" in readme
                bmm_epic1_done = "Epic 1: 100%" in bmm or "Epic 1 Complete" in bmm

                if readme_epic1 != bmm_epic1_done:
                    issues.append("README中的Epic 1状态与BMM工作流状态不一致")

                # 检查更新时间
                readme_date_match = re.search(r'\*最后更新:\s*(\d{4}-\d{2}-\d{2})\*', readme)
                if readme_date_match:
                    readme_date = datetime.strptime(readme_date_match.group(1), '%Y-%m-%d')
                    file_mtime = datetime.fromtimestamp(README_PATH.stat().st_mtime)
                    if (file_mtime - readme_date).days > 7:
                        issues.append("README更新时间戳可能过时")

        except Exception as e:
            issues.append(f"一致性检查失败: {e}")

        consistency = 1.0 - (len(issues) / 10)  # 假设最多10个一致性问题

        return AuditResult(
            timestamp=datetime.now().isoformat(),
            doc_type="Consistency",
            status="PASS" if consistency >= QUALITY_THRESHOLDS["consistency"] else "FAIL",
            score=consistency,
            issues=issues,
            metrics={"issues_count": len(issues)},
            recommendations=["同步文档状态", "使用自动同步脚本"] if issues else []
        )

    def check_format_compliance(self) -> AuditResult:
        """检查格式规范"""
        issues = []
        total_docs = 0
        compliant_docs = 0

        # 检查所有Markdown文档
        for doc_path in list(PROJECT_ROOT.glob("**/*.md")):
            total_docs += 1

            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 检查编码
                if not doc_path.name.startswith('.'):
                    # 检查标题格式
                    if not re.search(r'^# ', content, re.MULTILINE):
                        issues.append(f"缺少主标题: {doc_path.relative_to(PROJECT_ROOT)}")

                    # 检查代码块格式
                    code_blocks = re.findall(r'```(\w+)?', content)
                    if code_blocks:
                        # 检查是否有语言标识
                        for block in code_blocks:
                            if not block:
                                issues.append(f"代码块缺少语言标识: {doc_path.relative_to(PROJECT_ROOT)}")
                                break

                    # 检查表格格式
                    tables = re.findall(r'\|.*\|', content)
                    if tables:
                        # 简单检查表格对齐
                        for table in tables:
                            if not re.match(r'^\|[\s\-\:|]+\|$', table.strip()):
                                issues.append(f"表格格式可能有问题: {doc_path.relative_to(PROJECT_ROOT)}")
                                break

                compliant_docs += 1

            except Exception as e:
                issues.append(f"格式检查失败 {doc_path.relative_to(PROJECT_ROOT)}: {e}")

        compliance = compliant_docs / total_docs if total_docs > 0 else 1.0

        return AuditResult(
            timestamp=datetime.now().isoformat(),
            doc_type="Format Compliance",
            status="PASS" if compliance >= QUALITY_THRESHOLDS["format_compliance"] else "FAIL",
            score=compliance,
            issues=issues[:20],  # 限制显示前20个问题
            metrics={"total_docs": total_docs, "compliant_docs": compliant_docs},
            recommendations=["修正格式问题", "添加格式检查到pre-commit"] if issues else []
        )

    def check_code_examples(self) -> AuditResult:
        """检查代码示例"""
        issues = []
        total_examples = 0
        valid_examples = 0

        for doc_path in list(PROJECT_ROOT.glob("**/*.md")):
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取代码块
            bash_examples = re.findall(r'```bash\n(.*?)\n```', content, re.DOTALL)
            python_examples = re.findall(r'```python\n(.*?)\n```', content, re.DOTALL)

            total_examples += len(bash_examples) + len(python_examples)

            # 验证bash示例（简单语法检查）
            for example in bash_examples:
                if example.strip():
                    # 检查基本bash语法
                    if not re.search(r'^[\s$\w\-./]+', example.strip()):
                        issues.append(f"Bash示例可能有问题: {doc_path.relative_to(PROJECT_ROOT)}")
                    else:
                        valid_examples += 1

            # 验证python示例（简单语法检查）
            for example in python_examples:
                if example.strip():
                    # 检查基本python语法
                    if not re.search(r'^[\s\w#=+\-*\/()[\]{}.,":<>!]+', example.strip()):
                        issues.append(f"Python示例可能有问题: {doc_path.relative_to(PROJECT_ROOT)}")
                    else:
                        valid_examples += 1

        validity = valid_examples / total_examples if total_examples > 0 else 1.0

        return AuditResult(
            timestamp=datetime.now().isoformat(),
            doc_type="Code Examples",
            status="PASS" if validity >= 0.95 else "FAIL",
            score=validity,
            issues=issues,
            metrics={"total_examples": total_examples, "valid_examples": valid_examples},
            recommendations=["修正无效代码示例", "添加示例测试"] if issues else []
        )

    def collect_metrics(self) -> Dict:
        """收集文档指标"""
        metrics = {
            "total_docs": 0,
            "total_size": 0,
            "recent_updates": 0,
            "last_audit": None,
            "coverage": 0,
            "quality_score": 0,
        }

        # 统计文档数量和大小
        for doc_path in list(PROJECT_ROOT.glob("**/*.md")):
            metrics["total_docs"] += 1
            metrics["total_size"] += doc_path.stat().st_size

            # 检查最近更新 (7天内)
            if doc_path.stat().st_mtime > (datetime.now() - timedelta(days=7)).timestamp():
                metrics["recent_updates"] += 1

        # 转换大小单位
        metrics["total_size_mb"] = metrics["total_size"] / 1048576

        return metrics

    def run_full_audit(self) -> List[AuditResult]:
        """运行完整审计"""
        print("🔍 开始文档质量审计...")

        checks = [
            ("完整性", self.check_doc_completeness),
            ("链接有效性", self.check_link_validity),
            ("一致性", self.check_consistency),
            ("格式规范", self.check_format_compliance),
            ("代码示例", self.check_code_examples),
        ]

        results = []
        for name, check_func in checks:
            print(f"  检查 {name}...")
            try:
                result = check_func()
                results.append(result)
                status_icon = "✅" if result.status == "PASS" else "❌"
                print(f"    {status_icon} {result.status} (得分: {result.score:.2%})")
            except Exception as e:
                print(f"    ❌ 检查失败: {e}")
                results.append(AuditResult(
                    timestamp=datetime.now().isoformat(),
                    doc_type=name,
                    status="ERROR",
                    score=0.0,
                    issues=[str(e)],
                    metrics={},
                    recommendations=["修复检查错误"]
                ))

        # 收集指标
        print("  收集指标...")
        self.metrics = self.collect_metrics()

        self.results = results
        return results

    def run_quick_audit(self) -> List[AuditResult]:
        """运行快速检查"""
        print("⚡ 运行快速文档检查...")

        # 仅运行关键检查
        results = [
            self.check_doc_completeness(),
            self.check_link_validity(),
        ]

        self.results = results

        # 收集指标
        print("  收集指标...")
        self.metrics = self.collect_metrics()

        return results

    def generate_report(self, output_format: str = "markdown") -> str:
        """生成审计报告"""
        if not self.results:
            print("❌ 没有审计结果，请先运行审计")
            return ""

        # 计算总体分数
        total_score = sum(r.score for r in self.results) / len(self.results)
        overall_status = "PASS" if total_score >= 0.9 else "FAIL"

        if output_format == "json":
            return json.dumps({
                "timestamp": datetime.now().isoformat(),
                "overall_status": overall_status,
                "overall_score": total_score,
                "results": [asdict(r) for r in self.results],
                "metrics": self.metrics,
            }, indent=2, ensure_ascii=False)

        # Markdown格式报告
        report = f"""# 文档质量审计报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**审计范围**: 完整文档库
**总体状态**: {'✅ PASS' if overall_status == 'PASS' else '❌ FAIL'}
**总体得分**: {total_score:.2%}

---

## 📊 审计结果概览

| 检查项目 | 状态 | 得分 | 问题数 |
|----------|------|------|--------|
"""

        for result in self.results:
            status_icon = "✅" if result.status == "PASS" else "❌"
            report += f"| {result.doc_type} | {status_icon} {result.status} | {result.score:.2%} | {len(result.issues)} |\n"

        report += f"""
---

## 📈 指标统计

- **文档总数**: {self.metrics['total_docs']}
- **文档总大小**: {self.metrics['total_size_mb']:.2f} MB
- **最近更新**: {self.metrics['recent_updates']} 文档 (7天内)
- **平均文档大小**: {self.metrics['total_size_mb'] / self.metrics['total_docs']:.2f} KB

---

## ❌ 发现的问题

"""

        # 汇总所有问题
        all_issues = []
        for result in self.results:
            if result.issues:
                all_issues.append(f"**{result.doc_type}** ({len(result.issues)} 个问题)")
                for issue in result.issues[:10]:  # 限制显示数量
                    all_issues.append(f"- {issue}")
                all_issues.append("")

        if all_issues:
            report += "\n".join(all_issues)
        else:
            report += "✅ 未发现严重问题"

        report += "\n\n## 💡 改进建议\n\n"

        # 汇总建议
        all_recommendations = []
        for result in self.results:
            if result.recommendations:
                for rec in result.recommendations:
                    if rec not in all_recommendations:
                        all_recommendations.append(f"- {rec}")

        if all_recommendations:
            report += "\n".join(all_recommendations)
        else:
            report += "文档质量良好，继续保持！"

        report += f"""

---

## 📋 详细结果

"""

        for result in self.results:
            report += f"""### {result.doc_type}

**状态**: {result.status}
**得分**: {result.score:.2%}

**指标**:
"""
            for key, value in result.metrics.items():
                report += f"- {key}: {value}\n"

            if result.issues:
                report += "\n**问题**:\n"
                for issue in result.issues:
                    report += f"- {issue}\n"

            report += "\n"

        report += f"""---

## 🔍 建议行动

### 立即行动 (今天)
"""
        urgent_actions = []
        for result in self.results:
            if result.status == "FAIL":
                urgent_actions.append(f"- [{result.doc_type}] 修复 {len(result.issues)} 个问题")

        if urgent_actions:
            report += "\n".join(urgent_actions)
        else:
            report += "- 文档质量良好，无需紧急修复"

        report += """

### 短期行动 (本周)
- 运行文档同步脚本
- 修复发现的链接问题
- 更新过时文档
- 添加自动化检查

### 长期行动 (本月)
- 建立文档维护流程
- 培训团队文档规范
- 优化文档结构
- 提升文档覆盖率

---

*此报告由 scripts/doc_audit.py 自动生成*
"""

        return report

    def save_report(self, report: str, filename: str = None):
        """保存报告到文件"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"doc_audit_report_{timestamp}.md"

        report_path = DOCS_DIR / filename

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n📄 报告已保存到: {report_path}")
        return report_path


def setup_cron_job():
    """设置定时任务 (Linux)"""
    script_path = PROJECT_ROOT / "scripts" / "doc_audit.py"
    cron_command = f"0 9 * * 1 {sys.executable} {script_path} --report >> {PROJECT_ROOT}/logs/doc_audit.log 2>&1"

    print("💡 定时任务设置建议:")
    print(f"添加以下行到crontab (crontab -e):")
    print(cron_command)
    print("\n或者使用其他定时任务工具 (如systemd timer, GitHub Actions等)")


def main():
    parser = argparse.ArgumentParser(description='文档质量审计工具')
    parser.add_argument('--full', action='store_true', help='完整审计')
    parser.add_argument('--quick', action='store_true', help='快速检查')
    parser.add_argument('--report', action='store_true', help='生成报告')
    parser.add_argument('--output', type=str, help='报告输出文件名')
    parser.add_argument('--format', type=str, choices=['markdown', 'json'], default='markdown', help='报告格式')
    parser.add_argument('--schedule', action='store_true', help='显示定时任务设置')
    parser.add_argument('--save', type=str, help='保存报告到文件')

    args = parser.parse_args()

    if not any([args.full, args.quick, args.report, args.schedule]):
        args.quick = True

    auditor = DocAuditor()

    if args.schedule:
        setup_cron_job()
        return 0

    if args.full or args.quick:
        if args.full:
            auditor.run_full_audit()
        else:
            auditor.run_quick_audit()

    if args.report or args.save:
        report = auditor.generate_report(output_format=args.format)

        if args.save:
            auditor.save_report(report, args.save)
        else:
            print(report)

    # 输出总结
    if auditor.results:
        print("\n" + "="*60)
        print("📊 审计总结")
        print("="*60)

        total_score = sum(r.score for r in auditor.results) / len(auditor.results)
        status = "✅ 通过" if total_score >= 0.9 else "❌ 未通过"

        print(f"总体状态: {status}")
        print(f"总体得分: {total_score:.2%}")
        print(f"检查项目: {len(auditor.results)}")
        print(f"发现问题: {sum(len(r.issues) for r in auditor.results)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
