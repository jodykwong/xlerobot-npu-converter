"""
内存使用优化配置策略模块

为Story 3.2: 内存使用优化提供完整的配置管理策略，
支持多种内存优化模式和配置预设。

作者: Claude Code / BMM v6
版本: 1.0
日期: 2025-10-28
"""

from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel, Field, validator
import yaml


class OptimizationLevel(Enum):
    """内存优化级别枚举"""
    MINIMAL = "minimal"  # 最小优化，仅基础监控
    BALANCED = "balanced"  # 平衡模式，优化与性能平衡
    AGGRESSIVE = "aggressive"  # 激进模式，最大化内存效率
    CUSTOM = "custom"  # 自定义模式


class MemoryMode(Enum):
    """内存使用模式"""
    LOW_MEMORY = "low_memory"  # 低内存模式，适用于内存受限环境
    STANDARD = "standard"  # 标准模式，适用于大多数场景
    HIGH_PERFORMANCE = "high_performance"  # 高性能模式，适用于大模型转换
    BATCH_PROCESSING = "batch_processing"  # 批处理模式，适用于批量转换


class MemoryOptimizationConfig(BaseModel):
    """内存优化配置模型"""

    # === 基础配置 ===
    optimization_level: OptimizationLevel = Field(
        default=OptimizationLevel.BALANCED,
        description="内存优化级别"
    )

    memory_mode: MemoryMode = Field(
        default=MemoryMode.STANDARD,
        description="内存使用模式"
    )

    # === 内存监控配置 ===
    monitoring_enabled: bool = Field(
        default=True,
        description="启用内存监控"
    )

    monitoring_interval: float = Field(
        default=0.1,
        ge=0.01,
        le=10.0,
        description="监控间隔（秒）"
    )

    peak_memory_threshold: float = Field(
        default=0.85,
        ge=0.5,
        le=1.0,
        description="内存峰值预警阈值（相对于总内存）"
    )

    # === 内存分配优化配置 ===
    memory_pool_enabled: bool = Field(
        default=True,
        description="启用内存池"
    )

    memory_pool_size: int = Field(
        default=100 * 1024 * 1024,  # 100MB
        ge=1024 * 1024,  # 最小1MB
        description="内存池大小（字节）"
    )

    object_reuse_enabled: bool = Field(
        default=True,
        description="启用对象复用"
    )

    object_reuse_threshold: int = Field(
        default=100,
        ge=10,
        description="对象复用阈值（使用次数）"
    )

    # === 算子级优化配置 ===
    operator_optimization_enabled: bool = Field(
        default=True,
        description="启用算子级优化"
    )

    intermediate_result_reuse: bool = Field(
        default=True,
        description="中间结果复用"
    )

    memory_compression_enabled: bool = Field(
        default=False,
        description="启用内存压缩（性能开销较大）"
    )

    compute_memory_tradeoff: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="计算换内存权衡系数（1.0=最大化内存节省）"
    )

    # === 批处理配置 ===
    batch_processing_enabled: bool = Field(
        default=False,
        description="启用批处理"
    )

    batch_size: int = Field(
        default=4,
        ge=1,
        le=32,
        description="批处理大小"
    )

    dynamic_batch_adjustment: bool = Field(
        default=True,
        description="动态批大小调整"
    )

    batch_memory_limit: int = Field(
        default=2 * 1024 * 1024 * 1024,  # 2GB
        ge=256 * 1024 * 1024,  # 最小256MB
        description="批处理内存限制（字节）"
    )

    # === GC优化配置 ===
    gc_optimization_enabled: bool = Field(
        default=True,
        description="启用GC优化"
    )

    gc_threshold_adjustment: bool = Field(
        default=True,
        description="调整GC阈值"
    )

    reference_counting_optimization: bool = Field(
        default=True,
        description="引用计数优化"
    )

    cycle_detection_enabled: bool = Field(
        default=True,
        description="循环检测"
    )

    gc_aggressiveness: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="GC激进程度"
    )

    # === 大模型分片配置 ===
    model_sharding_enabled: bool = Field(
        default=False,
        description="启用模型分片"
    )

    shard_size_threshold: int = Field(
        default=500 * 1024 * 1024,  # 500MB
        ge=100 * 1024 * 1024,  # 最小100MB
        description="模型分片大小阈值（字节）"
    )

    max_shards: int = Field(
        default=4,
        ge=2,
        le=16,
        description="最大分片数"
    )

    # === 泄漏检测配置 ===
    leak_detection_enabled: bool = Field(
        default=True,
        description="启用泄漏检测"
    )

    leak_detection_interval: float = Field(
        default=1.0,
        ge=0.1,
        le=60.0,
        description="泄漏检测间隔（秒）"
    )

    leak_threshold: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        ge=1024 * 1024,  # 最小1MB
        description="泄漏检测阈值（字节）"
    )

    out_of_bounds_detection: bool = Field(
        default=True,
        description="启用越界检测"
    )

    # === 报告配置 ===
    reporting_enabled: bool = Field(
        default=True,
        description="启用报告生成"
    )

    report_format: List[str] = Field(
        default=["json", "html"],
        description="报告格式列表"
    )

    auto_report_generation: bool = Field(
        default=True,
        description="自动报告生成"
    )

    @validator('report_format')
    def validate_report_format(cls, v):
        valid_formats = {"json", "html", "pdf"}
        for fmt in v:
            if fmt not in valid_formats:
                raise ValueError(f"无效的报告格式: {fmt}")
        return v

    def get_optimization_strategy(self) -> Dict[str, Any]:
        """获取当前配置的优化策略"""
        return {
            "level": self.optimization_level.value,
            "mode": self.memory_mode.value,
            "strategies": {
                "memory_pool": self.memory_pool_enabled,
                "object_reuse": self.object_reuse_enabled,
                "operator_optimization": self.operator_optimization_enabled,
                "gc_optimization": self.gc_optimization_enabled,
                "leak_detection": self.leak_detection_enabled,
            },
            "thresholds": {
                "peak_memory": self.peak_memory_threshold,
                "leak_detection": self.leak_threshold,
                "sharding": self.shard_size_threshold,
            }
        }

    def is_optimization_enabled(self, feature: str) -> bool:
        """检查特定优化功能是否启用"""
        feature_map = {
            "monitoring": self.monitoring_enabled,
            "memory_pool": self.memory_pool_enabled,
            "object_reuse": self.object_reuse_enabled,
            "operator_optimization": self.operator_optimization_enabled,
            "batch_processing": self.batch_processing_enabled,
            "gc_optimization": self.gc_optimization_enabled,
            "model_sharding": self.model_sharding_enabled,
            "leak_detection": self.leak_detection_enabled,
            "reporting": self.reporting_enabled,
        }
        return feature_map.get(feature, False)

    class Config:
        """Pydantic配置"""
        use_enum_values = False
        validate_assignment = True
        str_strip_whitespace = True


class MemoryOptimizationPresets:
    """内存优化预设配置"""

    @staticmethod
    def get_low_memory_mode() -> MemoryOptimizationConfig:
        """低内存模式预设，适用于内存受限环境"""
        return MemoryOptimizationConfig(
            optimization_level=OptimizationLevel.AGGRESSIVE,
            memory_mode=MemoryMode.LOW_MEMORY,
            monitoring_interval=0.05,
            peak_memory_threshold=0.70,
            memory_pool_size=50 * 1024 * 1024,  # 50MB
            memory_pool_enabled=True,
            object_reuse_enabled=True,
            operator_optimization_enabled=True,
            memory_compression_enabled=True,
            compute_memory_tradeoff=0.9,  # 更注重内存节省
            batch_processing_enabled=False,
            gc_optimization_enabled=True,
            gc_aggressiveness=1.0,  # 最激进的GC
            model_sharding_enabled=True,
            leak_detection_enabled=True,
            reporting_enabled=False,  # 减少报告开销
        )

    @staticmethod
    def get_standard_mode() -> MemoryOptimizationConfig:
        """标准模式预设，适用于大多数转换场景"""
        return MemoryOptimizationConfig(
            optimization_level=OptimizationLevel.BALANCED,
            memory_mode=MemoryMode.STANDARD,
            monitoring_interval=0.1,
            peak_memory_threshold=0.85,
            memory_pool_size=100 * 1024 * 1024,  # 100MB
            memory_pool_enabled=True,
            object_reuse_enabled=True,
            operator_optimization_enabled=True,
            memory_compression_enabled=False,
            compute_memory_tradeoff=0.7,
            batch_processing_enabled=True,
            batch_size=4,
            gc_optimization_enabled=True,
            gc_aggressiveness=0.8,
            model_sharding_enabled=False,
            leak_detection_enabled=True,
            reporting_enabled=True,
            auto_report_generation=True,
        )

    @staticmethod
    def get_high_performance_mode() -> MemoryOptimizationConfig:
        """高性能模式预设，适用于大模型转换"""
        return MemoryOptimizationConfig(
            optimization_level=OptimizationLevel.AGGRESSIVE,
            memory_mode=MemoryMode.HIGH_PERFORMANCE,
            monitoring_interval=0.2,
            peak_memory_threshold=0.90,
            memory_pool_size=500 * 1024 * 1024,  # 500MB
            memory_pool_enabled=True,
            object_reuse_enabled=True,
            operator_optimization_enabled=True,
            memory_compression_enabled=True,
            compute_memory_tradeoff=0.6,  # 平衡内存和性能
            batch_processing_enabled=True,
            batch_size=8,
            gc_optimization_enabled=True,
            gc_aggressiveness=0.7,
            model_sharding_enabled=True,
            leak_detection_enabled=True,
            reporting_enabled=True,
            auto_report_generation=True,
        )

    @staticmethod
    def get_batch_processing_mode() -> MemoryOptimizationConfig:
        """批处理模式预设，适用于批量转换场景"""
        return MemoryOptimizationConfig(
            optimization_level=OptimizationLevel.BALANCED,
            memory_mode=MemoryMode.BATCH_PROCESSING,
            monitoring_interval=0.5,
            peak_memory_threshold=0.75,
            memory_pool_size=200 * 1024 * 1024,  # 200MB
            memory_pool_enabled=True,
            object_reuse_enabled=True,
            operator_optimization_enabled=True,
            memory_compression_enabled=False,
            compute_memory_tradeoff=0.5,
            batch_processing_enabled=True,
            batch_size=16,
            dynamic_batch_adjustment=True,
            batch_memory_limit=4 * 1024 * 1024 * 1024,  # 4GB
            gc_optimization_enabled=True,
            gc_aggressiveness=0.9,
            model_sharding_enabled=True,
            leak_detection_enabled=True,
            reporting_enabled=True,
            auto_report_generation=True,
        )

    @classmethod
    def get_preset(cls, preset_name: str) -> Optional[MemoryOptimizationConfig]:
        """获取指定名称的预设配置"""
        presets = {
            "low_memory": cls.get_low_memory_mode(),
            "standard": cls.get_standard_mode(),
            "high_performance": cls.get_high_performance_mode(),
            "batch_processing": cls.get_batch_processing_mode(),
        }
        return presets.get(preset_name)

    @classmethod
    def list_presets(cls) -> List[str]:
        """列出所有可用的预设配置"""
        return ["low_memory", "standard", "high_performance", "batch_processing"]


def load_config_from_yaml(config_path: str) -> MemoryOptimizationConfig:
    """从YAML文件加载配置"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        return MemoryOptimizationConfig(**config_dict)
    except Exception as e:
        raise ValueError(f"加载配置文件失败: {e}")


def save_config_to_yaml(config: MemoryOptimizationConfig, config_path: str) -> None:
    """将配置保存到YAML文件"""
    try:
        config_dict = config.dict()
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
    except Exception as e:
        raise ValueError(f"保存配置文件失败: {e}")


# === 配置工厂函数 ===

def create_config(
    level: Optional[str] = None,
    mode: Optional[str] = None,
    preset: Optional[str] = None,
    custom_params: Optional[Dict[str, Any]] = None
) -> MemoryOptimizationConfig:
    """
    创建内存优化配置的工厂函数

    Args:
        level: 优化级别 ("minimal", "balanced", "aggressive", "custom")
        mode: 内存模式 ("low_memory", "standard", "high_performance", "batch_processing")
        preset: 预设配置名称 ("low_memory", "standard", "high_performance", "batch_processing")
        custom_params: 自定义参数字典

    Returns:
        MemoryOptimizationConfig: 配置实例

    Raises:
        ValueError: 参数无效时抛出异常
    """
    # 1. 首先尝试从预设加载
    if preset:
        config = MemoryOptimizationPresets.get_preset(preset)
        if not config:
            raise ValueError(f"无效的预设配置: {preset}")
    else:
        # 2. 使用默认配置
        config = MemoryOptimizationConfig()

    # 3. 应用指定的优化级别
    if level:
        try:
            config.optimization_level = OptimizationLevel(level)
        except ValueError:
            raise ValueError(f"无效的优化级别: {level}")

    # 4. 应用指定的内存模式
    if mode:
        try:
            config.memory_mode = MemoryMode(mode)
        except ValueError:
            raise ValueError(f"无效的内存模式: {mode}")

    # 5. 应用自定义参数
    if custom_params:
        for key, value in custom_params.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                raise ValueError(f"未知的配置参数: {key}")

    return config
