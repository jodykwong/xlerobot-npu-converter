"""
XLeRobot NPU模型转换工具 - 转换失败诊断系统
===============================================

该模块提供完整的转换失败诊断功能，包括多维度失败分析、
智能错误诊断、修复建议和失败预防系统。

作者: XLeRobot 开发团队
日期: 2025-10-28
版本: 1.0.0
"""

import json
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
import logging

from ..core.interfaces.base_converter import BaseConverter
from ..core.models.result_model import ResultStatus
from ..config.manager import ConfigurationManager


logger = logging.getLogger(__name__)


@dataclass
class FailureDiagnostic:
    """转换失败诊断数据模型"""

    model_name: str
    failure_stage: str
    failure_type: str
    failure_message: str
    root_cause: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    diagnosis_time: str
    suggestions: List[str]
    fix_steps: List[str]
    prevention_measures: List[str]
    error_code: str
    stack_trace: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


@dataclass
class DiagnosticSummary:
    """诊断摘要"""

    total_failures: int
    critical_failures: int
    high_failures: int
    medium_failures: int
    low_failures: int
    most_common_failure_type: str
    top_root_causes: List[str]
    recommended_actions: List[str]


class FailureDiagnosticSystem:
    """转换失败诊断系统核心类

    提供多维度失败诊断、智能错误分析、修复建议和失败预防功能。
    """

    def __init__(
        self,
        config_manager: Optional[ConfigurationManager] = None,
        report_generator: Optional[Any] = None
    ):
        """初始化失败诊断系统

        Args:
            config_manager: 配置管理器实例
            report_generator: 报告生成器实例
        """
        self.config_manager = config_manager or ConfigurationManager()
        self.report_generator = report_generator

        # 加载失败诊断配置
        self.diagnostic_config = self.config_manager.get_config(
            'failure_diagnostic',
            default_config_path='default_failure_diagnostic.yaml'
        )

        # 初始化知识库
        self.knowledge_base = self._load_failure_knowledge_base()

        # 诊断历史记录
        self.diagnostic_history: List[FailureDiagnostic] = []

        logger.info("失败诊断系统初始化完成")

    def _load_failure_knowledge_base(self) -> Dict[str, Any]:
        """加载失败知识库

        Returns:
            知识库字典
        """
        knowledge_base = {
            # 模型加载失败
            'model_load_error': {
                'root_causes': [
                    '模型文件不存在',
                    '模型文件损坏',
                    'ONNX格式不支持',
                    '模型版本不兼容',
                    '缺少依赖库'
                ],
                'fix_steps': [
                    '检查模型文件路径',
                    '验证模型文件完整性',
                    '确认ONNX版本',
                    '更新相关依赖库',
                    '使用模型转换工具重新生成'
                ],
                'prevention_measures': [
                    '定期备份模型文件',
                    '使用版本控制管理模型',
                    '建立模型验证流程',
                    '使用容器化环境'
                ]
            },
            # 量化失败
            'quantization_error': {
                'root_causes': [
                    '校准数据不足',
                    '量化参数设置错误',
                    '不支持的算子',
                    '数值范围超出限制',
                    '内存不足'
                ],
                'fix_steps': [
                    '增加校准数据量',
                    '调整量化参数',
                    '替换不支持的算子',
                    '检查数值范围',
                    '优化内存使用'
                ],
                'prevention_measures': [
                    '准备充足的校准数据',
                    '使用推荐参数配置',
                    '预先检查算子兼容性',
                    '进行小规模测试'
                ]
            },
            # 优化失败
            'optimization_error': {
                'root_causes': [
                    '优化策略不匹配',
                    '模型结构不支持',
                    '硬件限制',
                    '参数冲突',
                    '性能退化过大'
                ],
                'fix_steps': [
                    '更换优化策略',
                    '调整模型结构',
                    '检查硬件要求',
                    '验证参数设置',
                    '权衡性能与精度'
                ],
                'prevention_measures': [
                    '选择合适的优化策略',
                    '遵循模型设计规范',
                    '了解硬件限制',
                    '进行性能基准测试'
                ]
            },
            # 导出失败
            'export_error': {
                'root_causes': [
                    '导出路径不存在',
                    '权限不足',
                    '磁盘空间不足',
                    '导出格式不支持',
                    '模型过大'
                ],
                'fix_steps': [
                    '创建导出目录',
                    '检查文件权限',
                    '清理磁盘空间',
                    '更换导出格式',
                    '压缩模型大小'
                ],
                'prevention_measures': [
                    '预先检查环境',
                    '设置合适的权限',
                    '监控磁盘使用',
                    '选择兼容格式',
                    '优化模型大小'
                ]
            },
            # 环境错误
            'environment_error': {
                'root_causes': [
                    '依赖库版本不匹配',
                    '环境变量未设置',
                    '硬件驱动问题',
                    '权限配置错误',
                    '系统资源不足'
                ],
                'fix_steps': [
                    '更新依赖库',
                    '配置环境变量',
                    '更新硬件驱动',
                    '调整权限设置',
                    '释放系统资源'
                ],
                'prevention_measures': [
                    '使用固定版本',
                    '自动化环境配置',
                    '定期更新驱动',
                    '建立权限规范',
                    '监控系统资源'
                ]
            },
            # 配置错误
            'configuration_error': {
                'root_causes': [
                    '参数值无效',
                    '配置格式错误',
                    '必填参数缺失',
                    '参数冲突',
                    '配置不完整'
                ],
                'fix_steps': [
                    '修正参数值',
                    '修复配置格式',
                    '添加必填参数',
                    '解决参数冲突',
                    '完善配置信息'
                ],
                'prevention_measures': [
                    '使用配置验证',
                    '建立配置模板',
                    '文档化参数说明',
                    '实施配置审查'
                ]
            }
        }

        return knowledge_base

    def diagnose_failure(
        self,
        error: Exception,
        model_name: str,
        conversion_result: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> FailureDiagnostic:
        """诊断转换失败

        Args:
            error: 转换错误
            model_name: 模型名称
            conversion_result: 转换结果（可选）
            context: 错误上下文（可选）

        Returns:
            FailureDiagnostic: 失败诊断结果
        """
        logger.info(f"开始诊断模型 {model_name} 的转换失败")

        # 1. 错误分类
        failure_type = self._classify_error(error)

        # 2. 确定失败阶段
        failure_stage = self._determine_failure_stage(error, conversion_result)

        # 3. 错误代码生成
        error_code = self._generate_error_code(failure_type, failure_stage)

        # 4. 根因分析
        root_cause = self._analyze_root_cause(error, failure_type)

        # 5. 严重程度评估
        severity = self._assess_severity(error, failure_type)

        # 6. 修复建议生成
        suggestions = self._generate_suggestions(failure_type, error)

        # 7. 修复步骤生成
        fix_steps = self._generate_fix_steps(failure_type, error)

        # 8. 预防措施生成
        prevention_measures = self._generate_prevention_measures(failure_type)

        # 9. 创建诊断结果
        diagnostic = FailureDiagnostic(
            model_name=model_name,
            failure_stage=failure_stage,
            failure_type=failure_type,
            failure_message=str(error),
            root_cause=root_cause,
            severity=severity,
            diagnosis_time=datetime.now().isoformat(),
            suggestions=suggestions,
            fix_steps=fix_steps,
            prevention_measures=prevention_measures,
            error_code=error_code,
            stack_trace=traceback.format_exc() if self.diagnostic_config.get('include_stack_trace', True) else None,
            context=context
        )

        # 10. 添加到历史记录
        self.diagnostic_history.append(diagnostic)

        logger.info(f"失败诊断完成: {error_code}")
        return diagnostic

    def _classify_error(self, error: Exception) -> str:
        """错误分类

        Args:
            error: 错误对象

        Returns:
            错误类型字符串
        """
        # 根据错误消息进行分类
        error_msg = str(error).lower()

        if 'file' in error_msg or 'model' in error_msg or 'load' in error_msg:
            return 'model_load_error'
        elif 'quant' in error_msg or 'calibr' in error_msg:
            return 'quantization_error'
        elif 'optim' in error_msg or 'strategy' in error_msg:
            return 'optimization_error'
        elif 'export' in error_msg or 'save' in error_msg or 'write' in error_msg:
            return 'export_error'
        elif 'environment' in error_msg or 'dependency' in error_msg:
            return 'environment_error'
        elif 'config' in error_msg or 'parameter' in error_msg or 'setting' in error_msg:
            return 'configuration_error'
        else:
            return 'unknown_error'

    def _determine_failure_stage(
        self,
        error: Exception,
        conversion_result: Optional[Dict[str, Any]] = None
    ) -> str:
        """确定失败阶段

        Args:
            error: 错误对象
            conversion_result: 转换结果

        Returns:
            失败阶段字符串
        """
        if conversion_result:
            # 根据转换结果确定失败阶段
            if 'current_stage' in conversion_result:
                return conversion_result['current_stage']

        # 根据错误消息推断失败阶段
        error_msg = str(error).lower()

        if 'file' in error_msg or 'model' in error_msg or 'load' in error_msg:
            return 'model_loading'
        elif 'quant' in error_msg or 'calibr' in error_msg:
            return 'quantization'
        elif 'optim' in error_msg or 'strategy' in error_msg:
            return 'optimization'
        elif 'export' in error_msg or 'save' in error_msg:
            return 'model_export'
        else:
            return 'unknown_stage'

    def _generate_error_code(self, failure_type: str, failure_stage: str) -> str:
        """生成错误代码

        Args:
            failure_type: 失败类型
            failure_stage: 失败阶段

        Returns:
            错误代码
        """
        # 错误代码格式: [TYPE]-[STAGE]-[TIMESTAMP]
        type_code = failure_type[:3].upper()
        stage_code = failure_stage[:3].upper()
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

        return f"{type_code}-{stage_code}-{timestamp}"

    def _analyze_root_cause(self, error: Exception, failure_type: str) -> str:
        """根因分析

        Args:
            error: 错误对象
            failure_type: 失败类型

        Returns:
            根因描述
        """
        # 从知识库获取可能根因
        if failure_type in self.knowledge_base:
            root_causes = self.knowledge_base[failure_type]['root_causes']

            # 根据错误消息匹配最可能的根因
            error_msg = str(error).lower()
            for cause in root_causes:
                if any(keyword in error_msg for keyword in cause.lower().split()):
                    return cause

            # 返回最常见的根因
            return root_causes[0] if root_causes else "未知根因"

        return "需要进一步分析"

    def _assess_severity(self, error: Exception, failure_type: str) -> str:
        """严重程度评估

        Args:
            error: 错误对象
            failure_type: 失败类型

        Returns:
            严重程度: CRITICAL, HIGH, MEDIUM, LOW
        """
        # 基于错误类型评估严重程度
        critical_errors = ['model_load_error', 'environment_error']
        high_errors = ['quantization_error', 'optimization_error']
        medium_errors = ['export_error', 'configuration_error']

        if failure_type in critical_errors:
            return 'CRITICAL'
        elif failure_type in high_errors:
            return 'HIGH'
        elif failure_type in medium_errors:
            return 'MEDIUM'
        else:
            return 'LOW'

    def _generate_suggestions(self, failure_type: str, error: Exception) -> List[str]:
        """生成修复建议

        Args:
            failure_type: 失败类型
            error: 错误对象

        Returns:
            修复建议列表
        """
        suggestions = []

        # 从知识库获取建议
        if failure_type in self.knowledge_base:
            base_suggestions = self.knowledge_base[failure_type]['fix_steps']
            suggestions.extend(base_suggestions)

        # 基于错误消息添加特定建议
        error_msg = str(error).lower()
        if 'memory' in error_msg:
            suggestions.append("考虑减少批处理大小或使用更强大的硬件")
        if 'timeout' in error_msg:
            suggestions.append("增加超时时间或优化模型结构")
        if 'version' in error_msg:
            suggestions.append("检查并更新相关库的版本")

        # 如果没有建议，生成通用建议
        if not suggestions:
            suggestions = [
                "检查错误消息详情",
                "查看相关文档和示例",
                "在社区论坛搜索类似问题",
                "联系技术支持团队",
                "检查系统日志获取更多信息"
            ]

        return suggestions[:self.diagnostic_config.get('max_suggestions', 5)]  # 限制建议数量

    def _generate_fix_steps(self, failure_type: str, error: Exception) -> List[str]:
        """生成修复步骤

        Args:
            failure_type: 失败类型
            error: 错误对象

        Returns:
            修复步骤列表
        """
        if failure_type in self.knowledge_base:
            return self.knowledge_base[failure_type]['fix_steps']

        return [
            "检查错误消息详情",
            "查阅相关文档",
            "在社区论坛搜索类似问题",
            "联系技术支持团队"
        ]

    def _generate_prevention_measures(self, failure_type: str) -> List[str]:
        """生成预防措施

        Args:
            failure_type: 失败类型

        Returns:
            预防措施列表
        """
        if failure_type in self.knowledge_base:
            return self.knowledge_base[failure_type]['prevention_measures']

        return [
            "遵循最佳实践指南",
            "进行充分的测试",
            "保持环境和依赖更新",
            "建立监控和告警机制"
        ]

    def generate_diagnostic_report(
        self,
        diagnostic: FailureDiagnostic,
        output_format: str = 'json'
    ) -> str:
        """生成诊断报告

        Args:
            diagnostic: 诊断结果
            output_format: 输出格式 (json, html)

        Returns:
            报告内容
        """
        logger.info(f"生成{output_format}格式的诊断报告")

        if output_format.lower() == 'json':
            return json.dumps(asdict(diagnostic), ensure_ascii=False, indent=2)
        elif output_format.lower() == 'html':
            return self._generate_html_report(diagnostic)
        else:
            raise ValueError(f"不支持的报告格式: {output_format}")

    def _generate_html_report(self, diagnostic: FailureDiagnostic) -> str:
        """生成HTML格式诊断报告

        Args:
            diagnostic: 诊断结果

        Returns:
            HTML报告内容
        """
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>转换失败诊断报告</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .severity {{ padding: 5px 10px; border-radius: 3px; color: white; }}
                .severity-critical {{ background-color: #dc3545; }}
                .severity-high {{ background-color: #fd7e14; }}
                .severity-medium {{ background-color: #ffc107; color: black; }}
                .severity-low {{ background-color: #28a745; }}
                pre {{ background: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>转换失败诊断报告</h1>
                <p><strong>模型名称:</strong> {diagnostic.model_name}</p>
                <p><strong>诊断时间:</strong> {diagnostic.diagnosis_time}</p>
                <p><strong>错误代码:</strong> {diagnostic.error_code}</p>
            </div>

            <div class="section">
                <h2>失败信息</h2>
                <p><strong>失败阶段:</strong> {diagnostic.failure_stage}</p>
                <p><strong>失败类型:</strong> {diagnostic.failure_type}</p>
                <p><strong>严重程度:</strong> <span class="severity severity-{diagnostic.severity.lower()}">{diagnostic.severity}</span></p>
                <p><strong>错误消息:</strong> {diagnostic.failure_message}</p>
            </div>

            <div class="section">
                <h2>根因分析</h2>
                <p>{diagnostic.root_cause}</p>
            </div>

            <div class="section">
                <h2>修复建议</h2>
                <ul>
                    {"".join(f"<li>{s}</li>" for s in diagnostic.suggestions)}
                </ul>
            </div>

            <div class="section">
                <h2>修复步骤</h2>
                <ol>
                    {"".join(f"<li>{s}</li>" for s in diagnostic.fix_steps)}
                </ol>
            </div>

            <div class="section">
                <h2>预防措施</h2>
                <ul>
                    {"".join(f"<li>{s}</li>" for s in diagnostic.prevention_measures)}
                </ul>
            </div>

            {"".join(f'<div class="section"><h2>堆栈跟踪</h2><pre>{diagnostic.stack_trace}</pre></div>' if diagnostic.stack_trace else '')}
        </body>
        </html>
        """

        return html

    def analyze_diagnostic_history(self) -> DiagnosticSummary:
        """分析诊断历史记录

        Returns:
            DiagnosticSummary: 诊断摘要
        """
        if not self.diagnostic_history:
            return DiagnosticSummary(
                total_failures=0,
                critical_failures=0,
                high_failures=0,
                medium_failures=0,
                low_failures=0,
                most_common_failure_type="",
                top_root_causes=[],
                recommended_actions=[]
            )

        # 统计严重程度
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for diag in self.diagnostic_history:
            severity_counts[diag.severity] += 1

        # 统计失败类型
        failure_type_counts = {}
        for diag in self.diagnostic_history:
            failure_type_counts[diag.failure_type] = failure_type_counts.get(diag.failure_type, 0) + 1

        most_common_failure_type = max(failure_type_counts, key=failure_type_counts.get) if failure_type_counts else ""

        # 统计根因
        root_cause_counts = {}
        for diag in self.diagnostic_history:
            root_cause_counts[diag.root_cause] = root_cause_counts.get(diag.root_cause, 0) + 1

        top_root_causes = sorted(root_cause_counts, key=root_cause_counts.get, reverse=True)[:3]

        # 生成推荐行动
        recommended_actions = self._generate_recommended_actions(failure_type_counts)

        return DiagnosticSummary(
            total_failures=len(self.diagnostic_history),
            critical_failures=severity_counts['CRITICAL'],
            high_failures=severity_counts['HIGH'],
            medium_failures=severity_counts['MEDIUM'],
            low_failures=severity_counts['LOW'],
            most_common_failure_type=most_common_failure_type,
            top_root_causes=top_root_causes,
            recommended_actions=recommended_actions
        )

    def _generate_recommended_actions(self, failure_type_counts: Dict[str, int]) -> List[str]:
        """生成推荐行动

        Args:
            failure_type_counts: 失败类型统计

        Returns:
            推荐行动列表
        """
        actions = []

        if not failure_type_counts:
            return ["暂无推荐行动"]

        # 基于失败类型统计生成推荐
        total_failures = sum(failure_type_counts.values())

        for failure_type, count in failure_type_counts.items():
            percentage = (count / total_failures) * 100

            if percentage > 50:
                actions.append(f"严重关注: {failure_type} 占失败总数的 {percentage:.1f}%")
            elif percentage > 30:
                actions.append(f"重点改进: {failure_type} 占失败总数的 {percentage:.1f}%")

        # 添加通用建议
        actions.extend([
            "建立失败监控机制",
            "定期审查失败原因",
            "持续改进转换流程",
            "加强团队培训"
        ])

        return actions

    def save_diagnostic_report(
        self,
        diagnostic: FailureDiagnostic,
        output_path: Path,
        output_format: str = 'json'
    ) -> None:
        """保存诊断报告

        Args:
            diagnostic: 诊断结果
            output_path: 输出路径
            output_format: 输出格式
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        report_content = self.generate_diagnostic_report(diagnostic, output_format)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        logger.info(f"诊断报告已保存到: {output_path}")

    def batch_diagnose(
        self,
        errors: List[Tuple[Exception, str]],
        context_data: Optional[Dict[str, Any]] = None
    ) -> List[FailureDiagnostic]:
        """批量诊断失败

        Args:
            errors: 错误列表，每个元素为(error, model_name)元组
            context_data: 上下文数据（可选）

        Returns:
            诊断结果列表
        """
        logger.info(f"开始批量诊断 {len(errors)} 个失败案例")

        diagnostics = []
        for error, model_name in errors:
            diagnostic = self.diagnose_failure(error, model_name, context=context_data)
            diagnostics.append(diagnostic)

        logger.info(f"批量诊断完成，共生成 {len(diagnostics)} 个诊断结果")
        return diagnostics

    def export_diagnostic_history(self, output_path: Path) -> None:
        """导出诊断历史记录

        Args:
            output_path: 输出路径
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        history_data = [asdict(diagnostic) for diagnostic in self.diagnostic_history]

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)

        logger.info(f"诊断历史记录已导出到: {output_path}")