#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
转换报告配置系统
================

这是Story 2.9: 转换报告生成系统的配置组件。

提供转换报告生成的各种配置选项和预设方案。

作者: Claude Code / BMM Method
创建: 2025-10-28
版本: 1.0.0

BMM v6 Phase 2: 核心功能实现
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import yaml

from npu_converter.core.models.config_model import BaseConfig


class ConversionReportConfig(BaseConfig):
    """
    转换报告配置类

    管理转换报告生成的所有配置参数。
    """

    DEFAULT_CONFIG_PATH = "conversion_report_default.yaml"

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置

        Args:
            config_path: 配置文件路径
        """
        super().__init__()

        # 默认配置
        self.report_formats = ['json', 'html', 'pdf']
        self.default_format = 'html'

        # 报告内容配置
        self.include_performance = True
        self.include_accuracy = True
        self.include_compatibility = True
        self.include_resource_usage = True
        self.include_conversion_steps = True

        # 质量阈值配置
        self.performance_threshold = 0.90
        self.accuracy_threshold = 0.95
        self.compatibility_threshold = 0.90

        # 输出配置
        self.output_dir = 'conversion_reports'
        self.auto_generate = True
        self.include_recommendations = True
        self.include_analysis = True

        # 批量处理配置
        self.batch_size = 10
        self.concurrent_reports = 5

        # 报告模板配置
        self.template_style = 'detailed'
        self.include_charts = True
        self.include_trends = False

        # 加载配置文件
        if config_path:
            self.load_from_file(config_path)
        else:
            self.load_default_config()

    def load_default_config(self):
        """
        加载默认配置文件
        """
        default_path = Path(__file__).parent / "conversion_report_default.yaml"

        if default_path.exists():
            self.load_from_file(str(default_path))
        else:
            self.logger.info("使用内置默认配置")

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典

        Returns:
            配置字典
        """
        return {
            'report_formats': self.report_formats,
            'default_format': self.default_format,
            'include_performance': self.include_performance,
            'include_accuracy': self.include_accuracy,
            'include_compatibility': self.include_compatibility,
            'include_resource_usage': self.include_resource_usage,
            'include_conversion_steps': self.include_conversion_steps,
            'performance_threshold': self.performance_threshold,
            'accuracy_threshold': self.accuracy_threshold,
            'compatibility_threshold': self.compatibility_threshold,
            'output_dir': self.output_dir,
            'auto_generate': self.auto_generate,
            'include_recommendations': self.include_recommendations,
            'include_analysis': self.include_analysis,
            'batch_size': self.batch_size,
            'concurrent_reports': self.concurrent_reports,
            'template_style': self.template_style,
            'include_charts': self.include_charts,
            'include_trends': self.include_trends
        }

    def validate(self) -> bool:
        """
        验证配置有效性

        Returns:
            验证结果
        """
        try:
            # 验证格式
            if not isinstance(self.report_formats, list) or not self.report_formats:
                raise ValueError("报告格式必须是非空列表")

            # 验证阈值
            if not (0.0 <= self.performance_threshold <= 1.0):
                raise ValueError("性能阈值必须在0-1之间")

            if not (0.0 <= self.accuracy_threshold <= 1.0):
                raise ValueError("精度阈值必须在0-1之间")

            if not (0.0 <= self.compatibility_threshold <= 1.0):
                raise ValueError("兼容性阈值必须在0-1之间")

            # 验证批量大小
            if self.batch_size <= 0:
                raise ValueError("批量大小必须大于0")

            if self.concurrent_reports <= 0:
                raise ValueError("并发报告数必须大于0")

            return True

        except Exception as e:
            self.logger.error(f"配置验证失败: {str(e)}")
            return False


# 预设配置方案
REPORT_PRESETS = {
    'basic': {
        'name': '基础报告',
        'description': '包含基本转换信息',
        'include_performance': False,
        'include_accuracy': True,
        'include_compatibility': False,
        'include_resource_usage': False,
        'template_style': 'simple',
        'include_charts': False
    },
    'detailed': {
        'name': '详细报告',
        'description': '包含所有维度的完整分析',
        'include_performance': True,
        'include_accuracy': True,
        'include_compatibility': True,
        'include_resource_usage': True,
        'template_style': 'detailed',
        'include_charts': True,
        'include_trends': True
    },
    'production': {
        'name': '生产报告',
        'description': '适合生产环境的完整报告',
        'include_performance': True,
        'include_accuracy': True,
        'include_compatibility': True,
        'include_resource_usage': True,
        'include_conversion_steps': True,
        'template_style': 'production',
        'include_charts': True,
        'include_trends': True,
        'include_recommendations': True,
        'include_analysis': True
    },
    'quick': {
        'name': '快速报告',
        'description': '快速生成的简要报告',
        'include_performance': True,
        'include_accuracy': False,
        'include_compatibility': True,
        'template_style': 'simple',
        'include_charts': False,
        'include_recommendations': False,
        'include_analysis': False
    }
}


def get_preset_config(preset_name: str) -> ConversionReportConfig:
    """
    获取预设配置

    Args:
        preset_name: 预设名称

    Returns:
        配置实例
    """
    if preset_name not in REPORT_PRESETS:
        raise ValueError(f"未知的预设配置: {preset_name}")

    preset = REPORT_PRESETS[preset_name]
    config = ConversionReportConfig()

    # 应用预设配置
    for key, value in preset.items():
        if hasattr(config, key):
            setattr(config, key, value)

    return config


def create_custom_config(
    format: str = 'html',
    include_performance: bool = True,
    include_accuracy: bool = True,
    include_compatibility: bool = True,
    include_resource_usage: bool = True,
    template_style: str = 'detailed',
    output_dir: str = 'conversion_reports'
) -> ConversionReportConfig:
    """
    创建自定义配置

    Args:
        format: 默认格式
        include_performance: 是否包含性能
        include_accuracy: 是否包含精度
        include_compatibility: 是否包含兼容性
        include_resource_usage: 是否包含资源使用
        template_style: 模板样式
        output_dir: 输出目录

    Returns:
        配置实例
    """
    config = ConversionReportConfig()
    config.default_format = format
    config.include_performance = include_performance
    config.include_accuracy = include_accuracy
    config.include_compatibility = include_compatibility
    config.include_resource_usage = include_resource_usage
    config.template_style = template_style
    config.output_dir = output_dir

    return config
