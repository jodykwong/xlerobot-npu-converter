"""
XLeRobot NPU模型转换工具 - 转换失败诊断配置策略
=================================================

该模块提供转换失败诊断系统的配置管理功能，包括配置策略、
验证、加载和预设配置管理。

作者: XLeRobot 开发团队
日期: 2025-10-28
版本: 1.0.0
"""

import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field

from .manager import ConfigurationManager


@dataclass
class FailureDiagnosticConfig:
    """转换失败诊断配置数据模型"""

    # 诊断设置
    include_stack_trace: bool = True
    max_suggestions: int = 5
    max_fix_steps: int = 10
    max_prevention_measures: int = 5

    # 报告设置
    report_format: str = 'json'  # json, html, pdf
    report_output_dir: Path = field(default_factory=lambda: Path('reports/failure_diagnostics'))
    auto_save_reports: bool = True
    report_template: str = 'default'

    # 知识库设置
    knowledge_base_update: bool = False
    knowledge_base_path: Optional[Path] = None
    custom_knowledge_base: Dict[str, Any] = field(default_factory=dict)

    # 严重程度阈值
    severity_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'critical': 0.8,
        'high': 0.6,
        'medium': 0.4,
        'low': 0.2
    })

    # 错误分类设置
    error_classification_rules: Dict[str, List[str]] = field(default_factory=lambda: {
        'model_load_error': ['模型文件不存在', '模型文件损坏', 'ONNX格式不支持'],
        'quantization_error': ['校准数据不足', '量化参数设置错误', '不支持的算子'],
        'optimization_error': ['优化策略不匹配', '模型结构不支持', '硬件限制'],
        'export_error': ['导出路径不存在', '权限不足', '磁盘空间不足'],
        'environment_error': ['依赖库版本不匹配', '环境变量未设置', '硬件驱动问题'],
        'configuration_error': ['参数值无效', '配置格式错误', '必填参数缺失']
    })

    # 智能建议设置
    enable_smart_suggestions: bool = True
    suggestion_confidence_threshold: float = 0.7
    context_aware_suggestions: bool = True

    # 预防措施设置
    enable_failure_prediction: bool = True
    prediction_model_path: Optional[Path] = None
    historical_data_threshold: int = 10

    # 集成设置
    integrate_with_report_generator: bool = True
    integrate_with_error_handler: bool = True
    integrate_with_monitoring: bool = True

    def validate(self) -> None:
        """验证配置有效性

        Raises:
            ValueError: 配置无效时抛出
        """
        if not isinstance(self.max_suggestions, int) or self.max_suggestions <= 0:
            raise ValueError("max_suggestions 必须为正整数")

        if not isinstance(self.max_fix_steps, int) or self.max_fix_steps <= 0:
            raise ValueError("max_fix_steps 必须为正整数")

        if self.report_format not in ['json', 'html', 'pdf']:
            raise ValueError("report_format 必须是 json、html 或 pdf")

        if not isinstance(self.suggestion_confidence_threshold, float):
            raise ValueError("suggestion_confidence_threshold 必须为浮点数")

        if not 0 <= self.suggestion_confidence_threshold <= 1:
            raise ValueError("suggestion_confidence_threshold 必须在 0 到 1 之间")

        for severity, threshold in self.severity_thresholds.items():
            if not isinstance(threshold, (int, float)) or not 0 <= threshold <= 1:
                raise ValueError(f"severity_thresholds.{severity} 必须在 0 到 1 之间")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典

        Returns:
            配置字典
        """
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, Path):
                result[key] = str(value)
            elif isinstance(value, dict):
                result[key] = value.copy()
            else:
                result[key] = value
        return result

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'FailureDiagnosticConfig':
        """从字典创建配置

        Args:
            config_dict: 配置字典

        Returns:
            配置实例
        """
        # 处理Path类型字段
        if 'report_output_dir' in config_dict:
            config_dict['report_output_dir'] = Path(config_dict['report_output_dir'])

        if 'knowledge_base_path' in config_dict and config_dict['knowledge_base_path']:
            config_dict['knowledge_base_path'] = Path(config_dict['knowledge_base_path'])

        if 'prediction_model_path' in config_dict and config_dict['prediction_model_path']:
            config_dict['prediction_model_path'] = Path(config_dict['prediction_model_path'])

        return cls(**config_dict)


class FailureDiagnosticConfigStrategy:
    """转换失败诊断配置策略类

    负责管理失败诊断系统的配置策略，包括加载、验证、保存等操作。
    """

    def __init__(self, config_manager: ConfigurationManager):
        """初始化配置策略

        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.config: Optional[FailureDiagnosticConfig] = None

        # 预设配置
        self.preset_configs = {
            'basic': self._get_basic_config(),
            'detailed': self._get_detailed_config(),
            'production': self._get_production_config(),
            'quick': self._get_quick_config(),
            'development': self._get_development_config()
        }

    def load_config(
        self,
        config_path: Optional[Path] = None,
        preset_name: Optional[str] = None
    ) -> FailureDiagnosticConfig:
        """加载配置

        Args:
            config_path: 配置文件路径
            preset_name: 预设配置名称

        Returns:
            配置实例
        """
        # 如果提供了预设配置，使用预设配置
        if preset_name and preset_name in self.preset_configs:
            self.config = self.preset_configs[preset_name]
            logger.info(f"加载预设配置: {preset_name}")
        elif config_path and config_path.exists():
            # 从文件加载配置
            self.config = self._load_from_file(config_path)
            logger.info(f"从文件加载配置: {config_path}")
        else:
            # 使用默认配置
            self.config = self._get_default_config()
            logger.info("使用默认配置")

        # 验证配置
        self.config.validate()

        return self.config

    def _load_from_file(self, config_path: Path) -> FailureDiagnosticConfig:
        """从文件加载配置

        Args:
            config_path: 配置文件路径

        Returns:
            配置实例
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)

        return FailureDiagnosticConfig.from_dict(config_dict)

    def save_config(self, config: FailureDiagnosticConfig, output_path: Path) -> None:
        """保存配置

        Args:
            config: 配置实例
            output_path: 输出路径
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        config_dict = config.to_dict()

        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)

        logger.info(f"配置已保存到: {output_path}")

    def _get_default_config(self) -> FailureDiagnosticConfig:
        """获取默认配置

        Returns:
            默认配置实例
        """
        return FailureDiagnosticConfig()

    def _get_basic_config(self) -> FailureDiagnosticConfig:
        """获取基础配置

        Returns:
            基础配置实例
        """
        return FailureDiagnosticConfig(
            include_stack_trace=False,
            max_suggestions=3,
            max_fix_steps=5,
            max_prevention_measures=3,
            report_format='json',
            auto_save_reports=False,
            enable_smart_suggestions=False,
            enable_failure_prediction=False
        )

    def _get_detailed_config(self) -> FailureDiagnosticConfig:
        """获取详细配置

        Returns:
            详细配置实例
        """
        return FailureDiagnosticConfig(
            include_stack_trace=True,
            max_suggestions=10,
            max_fix_steps=15,
            max_prevention_measures=10,
            report_format='html',
            auto_save_reports=True,
            report_output_dir=Path('reports/failure_diagnostics_detailed'),
            enable_smart_suggestions=True,
            enable_failure_prediction=True,
            context_aware_suggestions=True
        )

    def _get_production_config(self) -> FailureDiagnosticConfig:
        """获取生产配置

        Returns:
            生产配置实例
        """
        return FailureDiagnosticConfig(
            include_stack_trace=True,
            max_suggestions=7,
            max_fix_steps=10,
            max_prevention_measures=7,
            report_format='pdf',
            auto_save_reports=True,
            report_output_dir=Path('reports/production/failure_diagnostics'),
            enable_smart_suggestions=True,
            enable_failure_prediction=True,
            integrate_with_monitoring=True,
            historical_data_threshold=50
        )

    def _get_quick_config(self) -> FailureDiagnosticConfig:
        """获取快速配置

        Returns:
            快速配置实例
        """
        return FailureDiagnosticConfig(
            include_stack_trace=False,
            max_suggestions=2,
            max_fix_steps=3,
            max_prevention_measures=2,
            report_format='json',
            auto_save_reports=False,
            enable_smart_suggestions=False,
            enable_failure_prediction=False
        )

    def _get_development_config(self) -> FailureDiagnosticConfig:
        """获取开发配置

        Returns:
            开发配置实例
        """
        return FailureDiagnosticConfig(
            include_stack_trace=True,
            max_suggestions=10,
            max_fix_steps=20,
            max_prevention_measures=10,
            report_format='html',
            auto_save_reports=True,
            report_output_dir=Path('reports/dev/failure_diagnostics'),
            enable_smart_suggestions=True,
            enable_failure_prediction=True,
            context_aware_suggestions=True,
            knowledge_base_update=True
        )

    def get_preset_config_names(self) -> List[str]:
        """获取所有预设配置名称

        Returns:
            预设配置名称列表
        """
        return list(self.preset_configs.keys())

    def get_current_config(self) -> Optional[FailureDiagnosticConfig]:
        """获取当前配置

        Returns:
            当前配置实例
        """
        return self.config

    def update_config(
        self,
        config_updates: Dict[str, Any]
    ) -> FailureDiagnosticConfig:
        """更新配置

        Args:
            config_updates: 配置更新字典

        Returns:
            更新后的配置实例
        """
        if self.config is None:
            self.config = self._get_default_config()

        # 更新配置
        for key, value in config_updates.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                logger.warning(f"未知的配置项: {key}")

        # 验证更新后的配置
        self.config.validate()

        return self.config

    def merge_with_preset(
        self,
        preset_name: str,
        custom_updates: Optional[Dict[str, Any]] = None
    ) -> FailureDiagnosticConfig:
        """合并预设配置和自定义更新

        Args:
            preset_name: 预设配置名称
            custom_updates: 自定义更新字典

        Returns:
            合并后的配置实例
        """
        if preset_name not in self.preset_configs:
            raise ValueError(f"未知的预设配置: {preset_name}")

        # 获取预设配置
        merged_config = self.preset_configs[preset_name]

        # 应用自定义更新
        if custom_updates:
            for key, value in custom_updates.items():
                if hasattr(merged_config, key):
                    setattr(merged_config, key, value)
                else:
                    logger.warning(f"未知的配置项: {key}")

        # 验证合并后的配置
        merged_config.validate()

        return merged_config

    def validate_config_file(self, config_path: Path) -> bool:
        """验证配置文件

        Args:
            config_path: 配置文件路径

        Returns:
            验证是否通过
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_dict = yaml.safe_load(f)

            config = FailureDiagnosticConfig.from_dict(config_dict)
            config.validate()

            logger.info(f"配置文件验证通过: {config_path}")
            return True

        except Exception as e:
            logger.error(f"配置文件验证失败: {config_path}, 错误: {str(e)}")
            return False


import logging

logger = logging.getLogger(__name__)