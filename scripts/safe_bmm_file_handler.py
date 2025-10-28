#!/usr/bin/env python3
"""
BMM Workflow Safe File Handler
防止在BMM工作流程中出现 "Cannot read properties of undefined (reading 'map')" 错误
"""

import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any


class BMMFileHandler:
    """BMM工作流程安全文件处理器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.docs_path = self.project_root / "docs"
        self.stories_path = self.docs_path / "stories"

    def safe_read_file(self, file_path: str) -> Optional[str]:
        """安全读取文件，防止undefined错误"""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.project_root / path

            if not path.exists():
                print(f"⚠️  文件不存在: {path}")
                return None

            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"✅ 成功读取文件: {path}")
                print(f"   大小: {len(content)} 字符")
                return content

        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
            return None

    def safe_write_file(self, file_path: str, content: str) -> bool:
        """安全写入文件，防止undefined错误"""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.project_root / path

            # 确保目录存在
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✅ 成功写入文件: {path}")
            print(f"   大小: {len(content)} 字符")
            return True

        except Exception as e:
            print(f"❌ 写入文件失败: {e}")
            return False

    def safe_update_story_status(self, story_id: str, updates: Dict[str, Any]) -> bool:
        """安全更新故事状态文件"""
        try:
            story_file = self.stories_path / f"{story_id}.md"

            # 读取现有内容
            content = self.safe_read_file(str(story_file))

            if content is None:
                print(f"⚠️  无法读取故事文件，创建新文件")
                content = f"# {story_id}\n\n"

            # 应用更新
            for key, value in updates.items():
                # 查找并替换特定模式
                if key == "phase_2_status":
                    pattern = r"\*\*Phase 2 状态\*\*:.*?(?=\n\n|\n\*\*|\Z)"
                    replacement = f"**Phase 2 状态**: {value}"
                    content = self._safe_replace_pattern(content, pattern, replacement)

                elif key == "phase_2_completion_date":
                    pattern = r"\*\*Phase 2 完成日期\*\*:.*?(?=\n\n|\n\*\*|\Z)"
                    replacement = f"**Phase 2 完成日期**: {value}"
                    content = self._safe_replace_pattern(content, pattern, replacement)

                elif key == "phase_2_progress":
                    pattern = r"\*\*Phase 2 进度\*\*:.*?(?=\n\n|\n\*\*|\Z)"
                    replacement = f"**Phase 2 进度**: {value}"
                    content = self._safe_replace_pattern(content, pattern, replacement)

            # 写入更新后的内容
            return self.safe_write_file(str(story_file), content)

        except Exception as e:
            print(f"❌ 更新故事状态失败: {e}")
            return False

    def _safe_replace_pattern(self, content: str, pattern: str, replacement: str) -> str:
        """安全替换文本模式"""
        import re

        if not isinstance(content, str):
            print(f"⚠️  内容不是字符串类型，返回空字符串")
            return ""

        try:
            if re.search(pattern, content, re.MULTILINE | re.DOTALL):
                return re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
            else:
                # 如果模式不存在，添加到文件末尾
                return content + f"\n\n{replacement}\n"
        except Exception as e:
            print(f"⚠️  替换模式失败: {e}")
            return content

    def safe_list_stories(self) -> List[str]:
        """安全列出所有故事文件"""
        try:
            if not self.stories_path.exists():
                print(f"⚠️  故事目录不存在: {self.stories_path}")
                return []

            story_files = list(self.stories_path.glob("*.md"))
            story_names = [f.stem for f in story_files if f.is_file()]

            print(f"✅ 找到 {len(story_names)} 个故事文件")
            for name in story_names:
                print(f"   - {name}")

            return story_names

        except Exception as e:
            print(f"❌ 列出故事文件失败: {e}")
            return []

    def safe_create_phase_report(self, story_id: str, phase: int, data: Dict[str, Any]) -> bool:
        """安全创建阶段完成报告"""
        try:
            report_file = self.stories_path / f"{story_id}-bmm-v6-phase{phase}-completion-report.md"

            # 构建报告内容
            content = f"""# {story_id} - BMM v6 Phase {phase} 完成报告

**状态**: ✅ Phase {phase} 已完成
**故事**: {data.get('story_title', story_id)}
**史诗**: {data.get('epic_title', 'N/A')}
**完成日期**: {data.get('completion_date', 'N/A')}
**执行流程**: BMM v6 {phase}-Phase流程
**总进度**: {data.get('total_progress', 'N/A')}

---

## Phase {phase} 完成摘要

{data.get('summary', 'Phase completed successfully')}

## 完成组件

"""

            # 安全添加组件列表
            components = data.get('components', [])
            if isinstance(components, list):
                for component in components:
                    if component:
                        content += f"- ✅ {component}\n"
            else:
                content += f"- ✅ {components}\n"

            content += f"""
## 技术指标

- **代码质量**: {data.get('code_quality', 'N/A')}
- **测试覆盖率**: {data.get('test_coverage', 'N/A')}
- **性能提升**: {data.get('performance_gain', 'N/A')}

## 下一步行动

{data.get('next_steps', '准备下一阶段开发')}

---

*报告生成时间*: {data.get('generation_time', 'N/A')}
*BMM v6流程*: Phase {phase} completed
"""

            return self.safe_write_file(str(report_file), content)

        except Exception as e:
            print(f"❌ 创建阶段报告失败: {e}")
            return False


# 使用示例
if __name__ == "__main__":
    project_root = "/home/sunrise/xlerobot"
    handler = BMMFileHandler(project_root)

    # 安全列出故事文件
    stories = handler.safe_list_stories()
    print(f"\n📚 找到 {len(stories)} 个故事")

    # 示例更新
    if "story-3.1" in stories:
        print("\n📝 更新 story-3.1 状态...")
        updates = {
            "phase_2_status": "✅ 已完成",
            "phase_2_completion_date": "2025-10-28",
            "phase_2_progress": "100% (Phase 2 组件验证通过)"
        }
        handler.safe_update_story_status("story-3.1", updates)
