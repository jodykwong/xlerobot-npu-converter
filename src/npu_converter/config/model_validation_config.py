#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型精度验证系统 - 配置管理
=====================================

这是Story 2.7: 模型精度验证系统的配置策略组件。

功能特性:
- 验证参数配置
- 阈值预设
- 配置验证
- 配置加载和保存

作者: Claude Code / BMM Method
创建: 2025-10-28
版本: 1.0.0

BMM v6 Phase 1: 架构扩展
"""

import yaml
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict

from npu_converter.logging.logger import ConversionLogger


logger = ConversionLogger(__name__)


@dataclass
class ValidationThresholds:
    """验证阈值配置"""
    # 精度阈值
    accuracy: float = 0.98  # PRD标准: >98%精度
    precision: float = 0.98
    recall: float = 0.98
    f1_score: float = 0.98

    # 性能阈值
    max_inference_time: float = 30.0  # 秒
    min_throughput: float = 1.0  # samples/sec
    max_memory_usage: float = 2048.0  # MB

    # 兼容性阈值
    min_npu_compatibility: float = 0.95
    min_operator_support: float = 0.90
    min_format_compliance: float = 0.98

    # 量化阈值
    max_quantization_loss: float = 0.02  # 2%损失


@dataclass
class ValidationFeatures:
    """验证功能开关"""
    # 验证维度开关
    enable_structure_validation: bool = True
    enable_functionality_validation: bool = True
    enable_performance_validation: bool = True
    enable_compatibility_validation: bool = True
    enable_quantization_validation: bool = True

    # 高级功能
    enable_realtime_monitoring: bool = True
    enable_batch_validation: bool = True
    enable_benchmark_system: bool = True
    enable_trend_analysis: bool = True


@dataclass
class ReportConfig:
    """报告配置"""
    # 输出格式
    output_formats: List[str] = field(default_factory=lambda: ['json', 'html', 'pdf'])

    # 输出目录
    output_dir: str = 'validation_reports'

    # 报告选项
    include_metrics_history: bool = True
    include_trend_analysis: bool = True
    include_error_details: bool = True
    include_recommendations: bool = True


@dataclass
class BenchmarkConfig:
    """基准测试配置"""
    # 数据集路径
    default_dataset_path: Optional[str] = None

    # 参考模型路径
    reference_model_path: Optional[str] = None

    # 基准测试选项
    auto_compare: bool = True
    benchmark_iterations: int = 10
    warmup_iterations: int = 3

    # 数据集配置
    dataset_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class ModelValidationConfig:
    """模型验证配置主类"""
    # 验证阈值
    thresholds: ValidationThresholds = field(default_factory=ValidationThresholds)

    # 验证功能
    features: ValidationFeatures = field(default_factory=ValidationFeatures)

    # 报告配置
    report: ReportConfig = field(default_factory=ReportConfig)

    # 基准测试配置
    benchmark: BenchmarkConfig = field(default_factory=BenchmarkConfig)

    # 全局选项
    max_concurrent_validations: int = 4
    cache_results: bool = True
    cache_ttl: int = 3600  # seconds
    log_level: str = 'INFO'

    # 模型类型特定配置
    model_type_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self):
        """初始化后处理"""
        self._setup_model_type_configs()

    def _setup_model_type_configs(self):
        """设置模型类型特定配置"""
        # VITS-Cantonese 配置
        self.model_type_configs['vits_cantonese'] = {
            'accuracy_threshold': 0.98,
            'max_inference_time': 30.0,
            'dataset': 'vits_cantonese_test',
            'validation_dimensions': ['structure', 'functionality', 'performance', 'compatibility', 'quantization']
        }

        # SenseVoice 配置
        self.model_type_configs['sensevoice'] = {
            'accuracy_threshold': 0.97,
            'max_inference_time': 25.0,
            'dataset': 'sensevoice_test',
            'validation_dimensions': ['structure', 'functionality', 'performance', 'compatibility', 'quantization']
        }

        # Piper VITS 配置
        self.model_type_configs['piper_vits'] = {
            'accuracy_threshold': 0.98,
            'max_inference_time': 30.0,
            'dataset': 'piper_vits_test',
            'validation_dimensions': ['structure', 'functionality', 'performance', 'compatibility', 'quantization']
        }

    def get_model_config(self, model_type: str) -> Dict[str, Any]:
        """获取特定模型类型的配置"""
        return self.model_type_configs.get(model_type, {})

    def validate_config(self) -> List[str]:
        """验证配置有效性"""
        errors = []

        # 验证阈值
        if not 0.0 <= self.thresholds.accuracy <= 1.0:
            errors.append(f"精度阈值必须在0-1之间: {self.thresholds.accuracy}")

        if self.thresholds.max_inference_time <= 0:
            errors.append(f"最大推理时间必须大于0: {self.thresholds.max_inference_time}")

        if self.thresholds.max_memory_usage <= 0:
            errors.append(f"最大内存使用必须大于0: {self.thresholds.max_memory_usage}")

        # 验证输出目录
        try:
            Path(self.report.output_dir).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"无法创建输出目录: {e}")

        # 验证并发数
        if self.max_concurrent_validations <= 0:
            errors.append(f"最大并发验证数必须大于0: {self.max_concurrent_validations}")

        # 验证缓存TTL
        if self.cache_ttl <= 0:
            errors.append(f"缓存TTL必须大于0: {self.cache_ttl}")

        return errors

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ModelValidationConfig':
        """从字典创建配置"""
        # 转换嵌套字典为对象
        if 'thresholds' in config_dict:
            config_dict['thresholds'] = ValidationThresholds(**config_dict['thresholds'])

        if 'features' in config_dict:
            config_dict['features'] = ValidationFeatures(**config_dict['features'])

        if 'report' in config_dict:
            config_dict['report'] = ReportConfig(**config_dict['report'])

        if 'benchmark' in config_dict:
            config_dict['benchmark'] = BenchmarkConfig(**config_dict['benchmark'])

        return cls(**config_dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def load_from_file(cls, config_path: str) -> 'ModelValidationConfig':
        """从文件加载配置"""
        config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_dict = yaml.safe_load(f)

            config = cls.from_dict(config_dict)

            # 验证配置
            errors = config.validate_config()
            if errors:
                raise ValueError(f"配置验证失败: {errors}")

            logger.info(f"配置已加载: {config_path}")
            return config

        except Exception as e:
            logger.error(f"加载配置失败: {config_path}", error=e)
            raise

    def save_to_file(self, config_path: str):
        """保存配置到文件"""
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            config_dict = self.to_dict()

            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)

            logger.info(f"配置已保存: {config_path}")

        except Exception as e:
            logger.error(f"保存配置失败: {config_path}", error=e)
            raise

    @classmethod
    def create_default(cls, preset: str = 'default') -> 'ModelValidationConfig':
        """创建默认配置"""
        if preset == 'strict':
            # 严格模式
            return cls(
                thresholds=ValidationThresholds(
                    accuracy=0.99,
                    precision=0.99,
                    recall=0.99,
                    f1_score=0.99,
                    max_inference_time=20.0,
                    max_quantization_loss=0.01
                ),
                features=ValidationFeatures(
                    enable_structure_validation=True,
                    enable_functionality_validation=True,
                    enable_performance_validation=True,
                    enable_compatibility_validation=True,
                    enable_quantization_validation=True
                ),
                max_concurrent_validations=2
            )

        elif preset == 'fast':
            # 快速模式
            return cls(
                thresholds=ValidationThresholds(
                    accuracy=0.95,
                    max_inference_time=60.0
                ),
                features=ValidationFeatures(
                    enable_performance_validation=False,
                    enable_quantization_validation=False,
                    enable_benchmark_system=False
                ),
                max_concurrent_validations=8
            )

        else:  # default
            # 默认模式
            return cls()


def load_config(config_path: Optional[str] = None) -> ModelValidationConfig:
    """
    加载配置

    Args:
        config_path: 配置文件路径，如果为None则使用默认配置

    Returns:
        ModelValidationConfig: 配置对象
    """
    if config_path:
        return ModelValidationConfig.load_from_file(config_path)
    else:
        # 尝试从默认路径加载
        default_path = Path("config/model_validation.yaml")
        if default_path.exists():
            return ModelValidationConfig.load_from_file(str(default_path))
        else:
            # 创建默认配置
            logger.info("使用默认配置")
            return ModelValidationConfig.create_default()


def save_default_config(output_path: str = "config/model_validation.yaml"):
    """
    保存默认配置文件

    Args:
        output_path: 输出路径
    """
    config = ModelValidationConfig.create_default()
    config.save_to_file(output_path)
    print(f"默认配置已保存到: {output_path}")


if __name__ == "__main__":
    # 示例：创建和保存默认配置
    print("创建默认配置...")
    config = ModelValidationConfig.create_default()

    # 验证配置
    errors = config.validate_config()
    if errors:
        print(f"配置验证失败: {errors}")
    else:
        print("配置验证通过")

    # 保存配置
    save_default_config()

    # 加载配置
    print("\n加载配置...")
    loaded_config = load_config("config/model_validation.yaml")
    print(f"已加载配置: {loaded_config.thresholds.accuracy_threshold}")
