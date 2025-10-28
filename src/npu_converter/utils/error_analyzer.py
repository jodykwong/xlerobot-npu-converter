"""
Error Analysis Engine for NPU Converter

Provides intelligent error analysis, root cause identification, and solution suggestions.
Implements analysis algorithms for conversion failures and error classification.
"""

import re
import traceback
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

from .exceptions import ConverterException, ConverterErrorCodes


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification."""
    ENVIRONMENT = "environment"
    CONFIGURATION = "configuration"
    INPUT_DATA = "input_data"
    MODEL_COMPATIBILITY = "model_compatibility"
    TOOLCHAIN = "toolchain"
    SYSTEM_RESOURCES = "system_resources"
    UNKNOWN = "unknown"


@dataclass
class AnalysisResult:
    """Result of error analysis."""
    exception_type: str
    error_code: str
    category: ErrorCategory
    severity: ErrorSeverity
    root_cause: str
    affected_components: List[str]
    suggested_actions: List[str]
    related_files: List[str]
    confidence_score: float  # 0.0 to 1.0


@dataclass
class Solution:
    """Solution suggestion for an error."""
    title: str
    description: str
    steps: List[str]
    automated_fix: bool
    success_probability: float  # 0.0 to 1.0


class ErrorAnalyzer:
    """
    Error analysis engine for NPU converter.

    Implements interface specified in story-context-1.7.xml:
    - def analyze_exception(self, exception: Exception) -> AnalysisResult
    - def suggest_solutions(self, analysis: AnalysisResult) -> List[Solution]
    """

    def __init__(self):
        """Initialize error analyzer with pattern rules."""
        self.error_patterns = self._initialize_error_patterns()
        self.component_mappings = self._initialize_component_mappings()
        self.solution_database = self._initialize_solution_database()

    def _initialize_error_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize error pattern recognition rules."""
        return {
            # File system errors
            r"no such file|file not found|cannot open": {
                "category": ErrorCategory.INPUT_DATA,
                "severity": ErrorSeverity.HIGH,
                "components": ["file_handler", "model_loader"],
                "root_cause_template": "Required file or resource is missing or inaccessible"
            },
            r"permission denied|access denied|read.*denied": {
                "category": ErrorCategory.ENVIRONMENT,
                "severity": ErrorSeverity.HIGH,
                "components": ["file_handler", "security"],
                "root_cause_template": "Insufficient permissions to access required resources"
            },
            r"disk full|no space left|storage.*full": {
                "category": ErrorCategory.SYSTEM_RESOURCES,
                "severity": ErrorSeverity.CRITICAL,
                "components": ["file_handler", "storage"],
                "root_cause_template": "Insufficient disk space for operation"
            },

            # Configuration errors
            r"invalid.*config|configuration.*error|missing.*config": {
                "category": ErrorCategory.CONFIGURATION,
                "severity": ErrorSeverity.MEDIUM,
                "components": ["config_manager", "validator"],
                "root_cause_template": "Invalid or missing configuration parameters"
            },

            # Model compatibility errors
            r"unsupported.*op|unsupported.*layer|operator.*not.*supported": {
                "category": ErrorCategory.MODEL_COMPATIBILITY,
                "severity": ErrorSeverity.HIGH,
                "components": ["model_validator", "converter"],
                "root_cause_template": "Model contains unsupported operators or layers"
            },
            r"shape.*mismatch|dimension.*mismatch|tensor.*shape": {
                "category": ErrorCategory.MODEL_COMPATIBILITY,
                "severity": ErrorSeverity.MEDIUM,
                "components": ["model_validator", "converter"],
                "root_cause_template": "Tensor shape or dimension compatibility issue"
            },

            # Toolchain errors
            r"compilation.*failed|compiler.*error|link.*error": {
                "category": ErrorCategory.TOOLCHAIN,
                "severity": ErrorSeverity.HIGH,
                "components": ["compiler", "toolchain"],
                "root_cause_template": "Model compilation failed during NPU conversion"
            },
            r"toolchain.*not.*found|horizon.*not.*found|bpu.*not.*found": {
                "category": ErrorCategory.ENVIRONMENT,
                "severity": ErrorSeverity.CRITICAL,
                "components": ["toolchain", "environment"],
                "root_cause_template": "NPU/BPU toolchain not properly installed or accessible"
            },

            # Memory/resource errors
            r"out.*of.*memory|memory.*error|allocation.*failed": {
                "category": ErrorCategory.SYSTEM_RESOURCES,
                "severity": ErrorSeverity.CRITICAL,
                "components": ["memory_manager", "converter"],
                "root_cause_template": "Insufficient memory for model processing"
            },
            r"timeout|time.*out|operation.*timed": {
                "category": ErrorCategory.SYSTEM_RESOURCES,
                "severity": ErrorSeverity.MEDIUM,
                "components": ["converter", "process_manager"],
                "root_cause_template": "Operation exceeded time limit"
            }
        }

    def _initialize_component_mappings(self) -> Dict[str, List[str]]:
        """Initialize component-to-file mappings."""
        return {
            "model_loader": ["src/npu_converter/core/loader.py"],
            "model_validator": ["src/npu_converter/core/validator.py"],
            "converter": ["src/npu_converter/core/converter.py"],
            "config_manager": ["src/npu_converter/utils/config.py"],
            "file_handler": ["src/npu_converter/utils/file_utils.py"],
            "compiler": ["src/npu_converter/bpu_toolchain/compiler.py"],
            "toolchain": ["src/npu_converter/bpu_toolchain/horizon_x5.py"],
            "memory_manager": ["src/npu_converter/core/memory.py"],
            "storage": ["src/npu_converter/utils/storage.py"]
        }

    def _initialize_solution_database(self) -> Dict[ErrorCategory, List[Dict[str, Any]]]:
        """Initialize solution database for different error categories."""
        return {
            ErrorCategory.ENVIRONMENT: [
                {
                    "title": "检查工具链安装",
                    "description": "验证Horizon X5 BPU工具链是否正确安装",
                    "steps": [
                        "运行 hrt_model_exec --version 检查工具链版本",
                        "验证环境变量设置",
                        "检查工具链路径是否在PATH中"
                    ],
                    "automated_fix": False,
                    "success_probability": 0.8
                }
            ],
            ErrorCategory.CONFIGURATION: [
                {
                    "title": "验证配置文件",
                    "description": "检查配置文件格式和必需参数",
                    "steps": [
                        "使用配置验证工具检查YAML格式",
                        "对照模板检查必需参数",
                        "验证参数值的有效性"
                    ],
                    "automated_fix": True,
                    "success_probability": 0.9
                }
            ],
            ErrorCategory.INPUT_DATA: [
                {
                    "title": "检查输入文件",
                    "description": "验证模型文件和输入数据",
                    "steps": [
                        "确认文件路径正确",
                        "检查文件权限",
                        "验证文件格式和完整性"
                    ],
                    "automated_fix": False,
                    "success_probability": 0.7
                }
            ],
            ErrorCategory.MODEL_COMPATIBILITY: [
                {
                    "title": "模型兼容性处理",
                    "description": "处理模型兼容性问题",
                    "steps": [
                        "检查模型算子支持情况",
                        "尝试模型简化或重构",
                        "使用替代算子"
                    ],
                    "automated_fix": True,
                    "success_probability": 0.6
                }
            ],
            ErrorCategory.TOOLCHAIN: [
                {
                    "title": "工具链问题排查",
                    "description": "诊断和解决工具链问题",
                    "steps": [
                        "检查工具链版本兼容性",
                        "重新安装或更新工具链",
                        "验证硬件兼容性"
                    ],
                    "automated_fix": False,
                    "success_probability": 0.5
                }
            ],
            ErrorCategory.SYSTEM_RESOURCES: [
                {
                    "title": "系统资源优化",
                    "description": "优化系统资源使用",
                    "steps": [
                        "清理临时文件释放空间",
                        "调整内存限制",
                        "优化处理批大小"
                    ],
                    "automated_fix": True,
                    "success_probability": 0.8
                }
            ]
        }

    def analyze_exception(self, exception: Exception) -> AnalysisResult:
        """
        Analyze exception and provide detailed analysis.

        Args:
            exception: Exception to analyze

        Returns:
            AnalysisResult with detailed error information
        """
        error_message = str(exception)
        error_code = getattr(exception, 'error_code', ConverterErrorCodes.UNKNOWN_ERROR)
        exception_type = exception.__class__.__name__

        # Find matching pattern
        matched_pattern = None
        confidence_score = 0.5  # Default confidence

        for pattern, pattern_info in self.error_patterns.items():
            if re.search(pattern, error_message, re.IGNORECASE):
                matched_pattern = pattern_info
                confidence_score = 0.8
                break

        # Determine category and severity
        if matched_pattern:
            category = matched_pattern["category"]
            severity = matched_pattern["severity"]
            components = matched_pattern["components"]
            root_cause = matched_pattern["root_cause_template"]
        else:
            category = ErrorCategory.UNKNOWN
            severity = ErrorSeverity.MEDIUM
            components = ["unknown"]
            root_cause = f"Unknown error: {error_message}"

        # Extract affected files from stack trace
        related_files = self._extract_related_files(exception)

        # Generate suggested actions
        suggested_actions = self._generate_suggested_actions(category, error_message, components)

        # Improve confidence based on error code
        if error_code != ConverterErrorCodes.UNKNOWN_ERROR:
            confidence_score += 0.1

        return AnalysisResult(
            exception_type=exception_type,
            error_code=error_code,
            category=category,
            severity=severity,
            root_cause=root_cause,
            affected_components=components,
            suggested_actions=suggested_actions,
            related_files=related_files,
            confidence_score=min(confidence_score, 1.0)
        )

    def suggest_solutions(self, analysis: AnalysisResult) -> List[Solution]:
        """
        Suggest solutions based on error analysis.

        Args:
            analysis: Error analysis result

        Returns:
            List of Solution objects
        """
        solutions = []

        # Get solutions from database
        category_solutions = self.solution_database.get(analysis.category, [])

        for solution_data in category_solutions:
            solution = Solution(
                title=solution_data["title"],
                description=solution_data["description"],
                steps=solution_data["steps"].copy(),
                automated_fix=solution_data["automated_fix"],
                success_probability=solution_data["success_probability"]
            )
            solutions.append(solution)

        # Add context-specific solutions
        context_solutions = self._generate_context_solutions(analysis)
        solutions.extend(context_solutions)

        # Sort by success probability
        solutions.sort(key=lambda s: s.success_probability, reverse=True)

        return solutions

    def _extract_related_files(self, exception: Exception) -> List[str]:
        """Extract related file paths from exception stack trace."""
        files = []

        if hasattr(exception, '__traceback__') and exception.__traceback__:
            for frame_summary in traceback.extract_tb(exception.__traceback__):
                file_path = frame_summary.filename
                if 'src/npu_converter' in file_path:
                    # Convert to project-relative path
                    relative_path = file_path[file_path.find('src/npu_converter'):]
                    files.append(relative_path)

        return list(set(files))  # Remove duplicates

    def _generate_suggested_actions(self, category: ErrorCategory, error_message: str, components: List[str]) -> List[str]:
        """Generate suggested actions based on error category and context."""
        actions = []

        if category == ErrorCategory.ENVIRONMENT:
            actions = [
                "检查环境配置和依赖项",
                "验证工具链安装状态",
                "检查系统权限设置"
            ]
        elif category == ErrorCategory.CONFIGURATION:
            actions = [
                "验证配置文件格式",
                "检查必需参数设置",
                "对照文档确认配置正确性"
            ]
        elif category == ErrorCategory.INPUT_DATA:
            actions = [
                "确认输入文件存在且可访问",
                "验证文件格式正确性",
                "检查文件权限"
            ]
        elif category == ErrorCategory.MODEL_COMPATIBILITY:
            actions = [
                "检查模型算子支持情况",
                "验证模型架构兼容性",
                "考虑模型简化或替代方案"
            ]
        elif category == ErrorCategory.TOOLCHAIN:
            actions = [
                "检查工具链版本兼容性",
                "验证硬件支持状态",
                "重新安装或更新工具链"
            ]
        elif category == ErrorCategory.SYSTEM_RESOURCES:
            actions = [
                "检查可用内存和磁盘空间",
                "优化处理参数",
                "考虑分批处理"
            ]
        else:
            actions = [
                "收集详细错误信息",
                "检查日志文件",
                "联系技术支持"
            ]

        return actions

    def _generate_context_solutions(self, analysis: AnalysisResult) -> List[Solution]:
        """Generate context-specific solutions based on analysis."""
        solutions = []

        # Add specific solutions based on error code
        if analysis.error_code == ConverterErrorCodes.MODEL_VALIDATION_ERROR:
            solutions.append(Solution(
                title="模型验证修复",
                description="修复模型验证错误",
                steps=[
                    "检查模型结构完整性",
                    "验证输入张量形状",
                    "修复模型配置参数"
                ],
                automated_fix=True,
                success_probability=0.7
            ))
        elif analysis.error_code == ConverterErrorCodes.FILE_NOT_FOUND:
            solutions.append(Solution(
                title="文件路径修复",
                description="修复文件路径问题",
                steps=[
                    "确认文件路径正确",
                    "检查文件权限",
                    "验证文件存在性"
                ],
                automated_fix=True,
                success_probability=0.9
            ))

        return solutions