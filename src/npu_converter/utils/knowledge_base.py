"""
Error Knowledge Base for NPU Converter

Provides intelligent error resolution suggestions and diagnostic information.
Contains a database of common errors, their solutions, and preventive measures.
"""

import json
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum

from .exceptions import ConverterErrorCodes
from .error_analyzer import ErrorCategory, ErrorSeverity


class SolutionType(Enum):
    """Types of solutions."""
    MANUAL = "manual"
    AUTOMATED = "automated"
    SEMI_AUTOMATED = "semi_automated"


@dataclass
class ErrorEntry:
    """Knowledge base entry for an error."""
    error_code: str
    error_pattern: str
    title: str
    description: str
    category: ErrorCategory
    severity: ErrorSeverity
    symptoms: List[str]
    causes: List[str]
    solutions: List[Dict[str, Any]]
    prevention: List[str]
    related_errors: List[str]


class ErrorKnowledgeBase:
    """
    Error knowledge base for intelligent error resolution.

    Provides comprehensive error information and solution suggestions.
    """

    def __init__(self, knowledge_file: Optional[str] = None):
        """
        Initialize knowledge base.

        Args:
            knowledge_file: Optional path to knowledge base file
        """
        self.knowledge_file = knowledge_file
        self.entries: Dict[str, ErrorEntry] = {}
        self._initialize_default_knowledge()
        if knowledge_file:
            self._load_knowledge_file()

    def _initialize_default_knowledge(self):
        """Initialize default knowledge base entries."""
        default_entries = [
            # File system errors
            ErrorEntry(
                error_code=ConverterErrorCodes.FILE_NOT_FOUND,
                error_pattern=r"no such file|file not found|cannot open",
                title="文件未找到",
                description="所需的文件或资源不存在或无法访问",
                category=ErrorCategory.INPUT_DATA,
                severity=ErrorSeverity.HIGH,
                symptoms=[
                    "程序报告文件不存在",
                    "模型加载失败",
                    "配置文件读取错误"
                ],
                causes=[
                    "文件路径错误",
                    "文件被删除或移动",
                    "权限不足",
                    "文件名拼写错误"
                ],
                solutions=[
                    {
                        "type": SolutionType.MANUAL.value,
                        "title": "检查文件路径",
                        "steps": [
                            "确认文件路径拼写正确",
                            "检查文件是否存在",
                            "验证相对路径和绝对路径",
                            "检查工作目录"
                        ],
                        "success_rate": 0.9
                    },
                    {
                        "type": SolutionType.AUTOMATED.value,
                        "title": "自动路径修复",
                        "steps": [
                            "使用文件系统搜索功能",
                            "自动更正常见路径错误",
                            "验证文件格式兼容性"
                        ],
                        "success_rate": 0.7
                    }
                ],
                prevention=[
                    "使用配置文件管理路径",
                    "实现路径验证机制",
                    "提供文件选择对话框",
                    "使用相对路径"
                ],
                related_errors=[ConverterErrorCodes.FILE_PERMISSION_ERROR]
            ),
            ErrorEntry(
                error_code=ConverterErrorCodes.FILE_PERMISSION_ERROR,
                error_pattern=r"permission denied|access denied|read.*denied",
                title="文件权限错误",
                description="没有足够的权限访问文件或目录",
                category=ErrorCategory.ENVIRONMENT,
                severity=ErrorSeverity.HIGH,
                symptoms=[
                    "权限被拒绝错误",
                    "无法读取或写入文件",
                    "目录访问失败"
                ],
                causes=[
                    "文件权限设置不当",
                    "用户权限不足",
                    "文件被其他进程锁定",
                    "安全软件阻止访问"
                ],
                solutions=[
                    {
                        "type": SolutionType.MANUAL.value,
                        "title": "修复文件权限",
                        "steps": [
                            "检查文件所有者和权限",
                            "使用chmod修改权限",
                            "确认用户访问权限",
                            "检查文件锁定状态"
                        ],
                        "success_rate": 0.8
                    }
                ],
                prevention=[
                    "检查文件权限设置",
                    "使用适当的用户权限运行",
                    "实现权限检查机制"
                ],
                related_errors=[ConverterErrorCodes.FILE_NOT_FOUND]
            ),

            # Model compatibility errors
            ErrorEntry(
                error_code=ConverterErrorCodes.MODEL_VALIDATION_ERROR,
                error_pattern=r"validation.*error|invalid.*model|model.*invalid",
                title="模型验证错误",
                description="模型结构或参数不符合要求",
                category=ErrorCategory.MODEL_COMPATIBILITY,
                severity=ErrorSeverity.HIGH,
                symptoms=[
                    "模型验证失败",
                    "参数格式错误",
                    "结构不兼容"
                ],
                causes=[
                    "模型版本不兼容",
                    "算子不支持",
                    "张量形状不匹配",
                    "参数超出范围"
                ],
                solutions=[
                    {
                        "type": SolutionType.AUTOMATED.value,
                        "title": "模型自动修复",
                        "steps": [
                            "自动检测并修复常见问题",
                            "调整参数范围",
                            "替换不支持的算子"
                        ],
                        "success_rate": 0.6
                    },
                    {
                        "type": SolutionType.MANUAL.value,
                        "title": "手动模型调整",
                        "steps": [
                            "检查模型文档",
                            "使用模型转换工具",
                            "联系模型提供方"
                        ],
                        "success_rate": 0.8
                    }
                ],
                prevention=[
                    "使用模型验证工具",
                    "检查版本兼容性",
                    "提供模型转换指南"
                ],
                related_errors=[ConverterErrorCodes.MODEL_CONVERSION_ERROR]
            ),
            ErrorEntry(
                error_code=ConverterErrorCodes.MODEL_CONVERSION_ERROR,
                error_pattern=r"conversion.*failed|convert.*error",
                title="模型转换错误",
                description="模型转换过程中发生错误",
                category=ErrorCategory.MODEL_COMPATIBILITY,
                severity=ErrorSeverity.CRITICAL,
                symptoms=[
                    "转换过程失败",
                    "输出文件损坏",
                    "转换结果异常"
                ],
                causes=[
                    "模型过于复杂",
                    "内存不足",
                    "工具链版本不兼容",
                    "硬件限制"
                ],
                solutions=[
                    {
                        "type": SolutionType.MANUAL.value,
                        "title": "转换参数优化",
                        "steps": [
                            "调整转换精度设置",
                            "分步骤转换",
                            "降低模型复杂度"
                        ],
                        "success_rate": 0.7
                    },
                    {
                        "type": SolutionType.AUTOMATED.value,
                        "title": "智能转换重试",
                        "steps": [
                            "自动调整参数",
                            "分批处理",
                            "优化内存使用"
                        ],
                        "success_rate": 0.5
                    }
                ],
                prevention=[
                    "预先验证模型",
                    "使用适当的转换参数",
                    "监控系统资源使用"
                ],
                related_errors=[ConverterErrorCodes.MODEL_VALIDATION_ERROR]
            ),

            # Toolchain errors
            ErrorEntry(
                error_code=ConverterErrorCodes.TOOLCHAIN_ERROR,
                error_pattern=r"toolchain.*error|bpu.*error|horizon.*error",
                title="工具链错误",
                description="NPU/BPU工具链操作失败",
                category=ErrorCategory.TOOLCHAIN,
                severity=ErrorSeverity.CRITICAL,
                symptoms=[
                    "工具链命令失败",
                    "编译错误",
                    "部署失败"
                ],
                causes=[
                    "工具链未安装",
                    "版本不兼容",
                    "环境变量错误",
                    "硬件不支持"
                ],
                solutions=[
                    {
                        "type": SolutionType.MANUAL.value,
                        "title": "工具链重装",
                        "steps": [
                            "卸载现有工具链",
                            "下载正确版本",
                            "重新安装配置",
                            "验证安装"
                        ],
                        "success_rate": 0.9
                    },
                    {
                        "type": SolutionType.AUTOMATED.value,
                        "title": "环境修复",
                        "steps": [
                            "自动检测环境问题",
                            "修复环境变量",
                            "验证工具链状态"
                        ],
                        "success_rate": 0.7
                    }
                ],
                prevention=[
                    "定期检查工具链状态",
                    "使用版本管理",
                    "维护环境配置"
                ],
                related_errors=[ConverterErrorCodes.COMPILATION_ERROR]
            ),

            # System resource errors
            ErrorEntry(
                error_code=ConverterErrorCodes.MEMORY_ERROR,
                error_pattern=r"out.*of.*memory|memory.*error|allocation.*failed",
                title="内存不足错误",
                description="系统内存不足无法完成操作",
                category=ErrorCategory.SYSTEM_RESOURCES,
                severity=ErrorSeverity.CRITICAL,
                symptoms=[
                    "内存分配失败",
                    "程序崩溃",
                    "系统响应缓慢"
                ],
                causes=[
                    "模型过大",
                    "内存泄漏",
                    "并发处理过多",
                    "系统内存不足"
                ],
                solutions=[
                    {
                        "type": SolutionType.AUTOMATED.value,
                        "title": "内存优化",
                        "steps": [
                            "自动释放未使用内存",
                            "调整批处理大小",
                            "启用内存映射"
                        ],
                        "success_rate": 0.8
                    },
                    {
                        "type": SolutionType.MANUAL.value,
                        "title": "系统优化",
                        "steps": [
                            "关闭其他程序",
                            "增加虚拟内存",
                            "升级硬件"
                        ],
                        "success_rate": 0.9
                    }
                ],
                prevention=[
                    "监控内存使用",
                    "优化算法",
                    "分批处理大数据"
                ],
                related_errors=[ConverterErrorCodes.RESOURCE_LIMIT_ERROR]
            )
        ]

        for entry in default_entries:
            self.entries[entry.error_code] = entry

    def _load_knowledge_file(self):
        """Load knowledge base from file."""
        try:
            if Path(self.knowledge_file).exists():
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                for entry_data in data:
                    entry = ErrorEntry(**entry_data)
                    self.entries[entry.error_code] = entry
        except Exception:
            # If loading fails, use default knowledge
            pass

    def save_knowledge_file(self):
        """Save knowledge base to file."""
        if self.knowledge_file:
            data = []
            for entry in self.entries.values():
                # Convert enums to strings for JSON serialization
                entry_dict = asdict(entry)
                entry_dict['category'] = entry.category.value
                entry_dict['severity'] = entry.severity.value
                data.append(entry_dict)

            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    def find_entry(self, error_code: str) -> Optional[ErrorEntry]:
        """Find knowledge base entry by error code."""
        return self.entries.get(error_code)

    def search_entries(self, query: str) -> List[ErrorEntry]:
        """Search knowledge base entries by query string."""
        query = query.lower()
        results = []

        for entry in self.entries.values():
            if (query in entry.title.lower() or
                query in entry.description.lower() or
                query in entry.error_pattern.lower() or
                any(query in symptom.lower() for symptom in entry.symptoms)):
                results.append(entry)

        return results

    def get_related_errors(self, error_code: str) -> List[ErrorEntry]:
        """Get related error entries."""
        entry = self.find_entry(error_code)
        if not entry:
            return []

        related = []
        for related_code in entry.related_errors:
            related_entry = self.find_entry(related_code)
            if related_entry:
                related.append(related_entry)

        return related

    def add_entry(self, entry: ErrorEntry):
        """Add new entry to knowledge base."""
        self.entries[entry.error_code] = entry

    def get_solution_by_type(self, error_code: str, solution_type: SolutionType) -> List[Dict[str, Any]]:
        """Get solutions of specific type for an error."""
        entry = self.find_entry(error_code)
        if not entry:
            return []

        return [
            solution for solution in entry.solutions
            if solution.get('type') == solution_type.value
        ]

    def get_prevention_tips(self, error_code: str) -> List[str]:
        """Get prevention tips for an error."""
        entry = self.find_entry(error_code)
        return entry.prevention if entry else []

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get statistics about knowledge base."""
        categories = {}
        severities = {}

        for entry in self.entries.values():
            # Count by category
            cat = entry.category.value
            categories[cat] = categories.get(cat, 0) + 1

            # Count by severity
            sev = entry.severity.value
            severities[sev] = severities.get(sev, 0) + 1

        return {
            "total_entries": len(self.entries),
            "categories": categories,
            "severities": severities
        }