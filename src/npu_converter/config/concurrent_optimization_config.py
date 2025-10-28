"""
并发优化配置策略模块

为Story 3.3: 并行处理能力提供完整的配置管理策略，
支持多种并发优化模式和配置预设。

作者: Claude Code / Story 3.3
版本: 1.0
日期: 2025-10-28
"""

from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel, Field, validator
import yaml


class ConcurrencyLevel(Enum):
    """并发级别枚举"""
    MINIMAL = "minimal"  # 最小并发，仅1-2个并发任务
    MODERATE = "moderate"  # 适度并发，5-10个并发任务
    HIGH = "high"  # 高并发，10-20个并发任务
    MAXIMUM = "maximum"  # 最大并发，20+个并发任务


class ProcessingMode(Enum):
    """处理模式"""
    THROUGHPUT = "throughput"  # 高吞吐量模式
    LATENCY = "latency"  # 低延迟模式
    BALANCED = "balanced"  # 平衡模式
    RESOURCE_EFFICIENT = "resource_efficient"  # 资源高效模式


class BatchStrategy(Enum):
    """批处理策略"""
    FIXED_SIZE = "fixed_size"  # 固定大小
    DYNAMIC = "dynamic"  # 动态大小
    ADAPTIVE = "adaptive"  # 自适应
    TIME_BASED = "time_based"  # 时间基础


class ConcurrentOptimizationConfig(BaseModel):
    """并发优化配置模型"""

    # === 基础配置 ===
    concurrency_level: ConcurrencyLevel = Field(
        default=ConcurrencyLevel.MODERATE,
        description="并发级别"
    )

    processing_mode: ProcessingMode = Field(
        default=ProcessingMode.BALANCED,
        description="处理模式"
    )

    # === 并发控制配置 ===
    max_concurrent_tasks: int = Field(
        default=10,
        ge=1,
        le=100,
        description="最大并发任务数"
    )

    max_queue_size: int = Field(
        default=1000,
        ge=10,
        description="最大队列大小"
    )

    task_timeout: float = Field(
        default=300.0,
        ge=1.0,
        description="任务超时时间（秒）"
    )

    task_retry_count: int = Field(
        default=3,
        ge=0,
        le=10,
        description="任务重试次数"
    )

    # === 批处理配置 ===
    batch_processing_enabled: bool = Field(
        default=True,
        description="启用批处理"
    )

    batch_strategy: BatchStrategy = Field(
        default=BatchStrategy.DYNAMIC,
        description="批处理策略"
    )

    batch_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="批大小"
    )

    batch_timeout: float = Field(
        default=1.0,
        ge=0.1,
        le=60.0,
        description="批处理超时（秒）"
    )

    max_batch_wait_time: float = Field(
        default=5.0,
        ge=0.1,
        description="最大批等待时间（秒）"
    )

    # === 负载均衡配置 ===
    load_balancing_enabled: bool = Field(
        default=True,
        description="启用负载均衡"
    )

    load_balancer_type: str = Field(
        default="round_robin",
        description="负载均衡类型"
    )

    worker_health_check_interval: float = Field(
        default=10.0,
        ge=1.0,
        description="工作节点健康检查间隔（秒）"
    )

    # === 资源管理配置 ===
    resource_monitoring_enabled: bool = Field(
        default=True,
        description="启用资源监控"
    )

    cpu_threshold: float = Field(
        default=0.80,
        ge=0.0,
        le=1.0,
        description="CPU使用率阈值"
    )

    memory_threshold: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description="内存使用率阈值"
    )

    auto_scaling_enabled: bool = Field(
        default=False,
        description="启用自动扩缩容"
    )

    scale_up_threshold: float = Field(
        default=0.75,
        ge=0.0,
        le=1.0,
        description="扩容阈值"
    )

    scale_down_threshold: float = Field(
        default=0.30,
        ge=0.0,
        le=1.0,
        description="缩容阈值"
    )

    # === 任务调度配置 ===
    scheduling_strategy: str = Field(
        default="priority",
        description="调度策略"
    )

    priority_levels: int = Field(
        default=4,
        ge=1,
        le=10,
        description="优先级级别数"
    )

    fairness_enabled: bool = Field(
        default=True,
        description="启用公平调度"
    )

    starvation_prevention: bool = Field(
        default=True,
        description="启用饥饿预防"
    )

    # === 内存优化配置 ===
    memory_optimization_enabled: bool = Field(
        default=True,
        description="启用内存优化"
    )

    memory_pool_size: int = Field(
        default=100 * 1024 * 1024,  # 100MB
        ge=1024 * 1024,
        description="内存池大小（字节）"
    )

    gc_optimization_enabled: bool = Field(
        default=True,
        description="启用GC优化"
    )

    # === 性能优化配置 ===
    performance_monitoring_enabled: bool = Field(
        default=True,
        description="启用性能监控"
    )

    metrics_collection_interval: float = Field(
        default=1.0,
        ge=0.1,
        description="指标收集间隔（秒）"
    )

    performance_history_size: int = Field(
        default=1000,
        ge=100,
        description="性能历史记录大小"
    )

    optimization_enabled: bool = Field(
        default=True,
        description="启用自动优化"
    )

    optimization_interval: float = Field(
        default=60.0,
        ge=10.0,
        description="优化间隔（秒）"
    )

    # === 错误处理配置 ===
    error_handling_enabled: bool = Field(
        default=True,
        description="启用错误处理"
    )

    circuit_breaker_enabled: bool = Field(
        default=True,
        description="启用断路器"
    )

    circuit_breaker_threshold: int = Field(
        default=5,
        ge=1,
        description="断路器阈值"
    )

    circuit_breaker_timeout: float = Field(
        default=30.0,
        ge=1.0,
        description="断路器超时（秒）"
    )

    # === 报告配置 ===
    reporting_enabled: bool = Field(
        default=True,
        description="启用报告生成"
    )

    report_formats: List[str] = Field(
        default=["json", "html"],
        description="报告格式列表"
    )

    auto_report_generation: bool = Field(
        default=True,
        description="自动报告生成"
    )

    report_interval: float = Field(
        default=300.0,
        ge=60.0,
        description="报告生成间隔（秒）"
    )

    @validator('report_formats')
    def validate_report_formats(cls, v):
        valid_formats = {"json", "html", "pdf"}
        for fmt in v:
            if fmt not in valid_formats:
                raise ValueError(f"无效的报告格式: {fmt}")
        return v

    def get_concurrent_strategy(self) -> Dict[str, Any]:
        """获取当前配置的并发策略"""
        return {
            "level": self.concurrency_level.value,
            "mode": self.processing_mode.value,
            "strategies": {
                "batch_processing": self.batch_processing_enabled,
                "load_balancing": self.load_balancing_enabled,
                "resource_monitoring": self.resource_monitoring_enabled,
                "memory_optimization": self.memory_optimization_enabled,
                "performance_monitoring": self.performance_monitoring_enabled,
                "auto_optimization": self.optimization_enabled,
            },
            "thresholds": {
                "max_concurrent": self.max_concurrent_tasks,
                "cpu": self.cpu_threshold,
                "memory": self.memory_threshold,
                "scale_up": self.scale_up_threshold,
                "scale_down": self.scale_down_threshold,
            },
            "batch": {
                "strategy": self.batch_strategy.value,
                "size": self.batch_size,
                "timeout": self.batch_timeout,
            }
        }

    def is_optimization_enabled(self, feature: str) -> bool:
        """检查特定优化功能是否启用"""
        feature_map = {
            "batch_processing": self.batch_processing_enabled,
            "load_balancing": self.load_balancing_enabled,
            "resource_monitoring": self.resource_monitoring_enabled,
            "memory_optimization": self.memory_optimization_enabled,
            "performance_monitoring": self.performance_monitoring_enabled,
            "auto_optimization": self.optimization_enabled,
            "gc_optimization": self.gc_optimization_enabled,
            "error_handling": self.error_handling_enabled,
            "circuit_breaker": self.circuit_breaker_enabled,
            "reporting": self.reporting_enabled,
            "auto_scaling": self.auto_scaling_enabled,
        }
        return feature_map.get(feature, False)

    def get_resource_limits(self) -> Dict[str, Any]:
        """获取资源限制"""
        return {
            "max_concurrent": self.max_concurrent_tasks,
            "max_queue_size": self.max_queue_size,
            "task_timeout": self.task_timeout,
            "cpu_threshold": self.cpu_threshold,
            "memory_threshold": self.memory_threshold,
            "memory_pool_size": self.memory_pool_size,
        }

    class Config:
        """Pydantic配置"""
        use_enum_values = False
        validate_assignment = True
        str_strip_whitespace = True


class ConcurrentOptimizationPresets:
    """并发优化预设配置"""

    @staticmethod
    def get_high_throughput_mode() -> ConcurrentOptimizationConfig:
        """高吞吐量模式预设，适用于大量小任务处理"""
        return ConcurrentOptimizationConfig(
            concurrency_level=ConcurrencyLevel.MAXIMUM,
            processing_mode=ProcessingMode.THROUGHPUT,
            max_concurrent_tasks=20,
            batch_processing_enabled=True,
            batch_strategy=BatchStrategy.DYNAMIC,
            batch_size=20,
            batch_timeout=2.0,
            load_balancing_enabled=True,
            resource_monitoring_enabled=True,
            cpu_threshold=0.90,
            memory_threshold=0.85,
            auto_scaling_enabled=True,
            performance_monitoring_enabled=True,
            optimization_enabled=True,
            reporting_enabled=True,
        )

    @staticmethod
    def get_low_latency_mode() -> ConcurrentOptimizationConfig:
        """低延迟模式预设，适用于实时转换场景"""
        return ConcurrentOptimizationConfig(
            concurrency_level=ConcurrencyLevel.MODERATE,
            processing_mode=ProcessingMode.LATENCY,
            max_concurrent_tasks=5,
            batch_processing_enabled=False,
            load_balancing_enabled=True,
            resource_monitoring_enabled=True,
            cpu_threshold=0.70,
            memory_threshold=0.75,
            task_timeout=30.0,
            performance_monitoring_enabled=True,
            optimization_enabled=True,
            circuit_breaker_enabled=True,
            reporting_enabled=True,
        )

    @staticmethod
    def get_balanced_mode() -> ConcurrentOptimizationConfig:
        """平衡模式预设，适用于大多数转换场景"""
        return ConcurrentOptimizationConfig(
            concurrency_level=ConcurrencyLevel.MODERATE,
            processing_mode=ProcessingMode.BALANCED,
            max_concurrent_tasks=10,
            batch_processing_enabled=True,
            batch_strategy=BatchStrategy.DYNAMIC,
            batch_size=10,
            batch_timeout=1.0,
            load_balancing_enabled=True,
            resource_monitoring_enabled=True,
            cpu_threshold=0.80,
            memory_threshold=0.85,
            performance_monitoring_enabled=True,
            optimization_enabled=True,
            error_handling_enabled=True,
            reporting_enabled=True,
        )

    @staticmethod
    def get_resource_efficient_mode() -> ConcurrentOptimizationConfig:
        """资源高效模式预设，适用于资源受限环境"""
        return ConcurrentOptimizationConfig(
            concurrency_level=ConcurrencyLevel.MINIMAL,
            processing_mode=ProcessingMode.RESOURCE_EFFICIENT,
            max_concurrent_tasks=2,
            batch_processing_enabled=True,
            batch_strategy=BatchStrategy.FIXED_SIZE,
            batch_size=5,
            batch_timeout=3.0,
            load_balancing_enabled=False,
            resource_monitoring_enabled=True,
            cpu_threshold=0.60,
            memory_threshold=0.70,
            memory_optimization_enabled=True,
            gc_optimization_enabled=True,
            performance_monitoring_enabled=False,
            auto_scaling_enabled=False,
            reporting_enabled=False,
        )

    @staticmethod
    def get_preset(preset_name: str) -> Optional[ConcurrentOptimizationConfig]:
        """获取指定名称的预设配置"""
        presets = {
            "high_throughput": ConcurrentOptimizationPresets.get_high_throughput_mode(),
            "low_latency": ConcurrentOptimizationPresets.get_low_latency_mode(),
            "balanced": ConcurrentOptimizationPresets.get_balanced_mode(),
            "resource_efficient": ConcurrentOptimizationPresets.get_resource_efficient_mode(),
        }
        return presets.get(preset_name)

    @classmethod
    def list_presets(cls) -> List[str]:
        """列出所有可用的预设配置"""
        return ["high_throughput", "low_latency", "balanced", "resource_efficient"]


def load_config_from_yaml(config_path: str) -> ConcurrentOptimizationConfig:
    """从YAML文件加载配置"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        return ConcurrentOptimizationConfig(**config_dict)
    except Exception as e:
        raise ValueError(f"加载配置文件失败: {e}")


def save_config_to_yaml(config: ConcurrentOptimizationConfig, config_path: str) -> None:
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
) -> ConcurrentOptimizationConfig:
    """
    创建并发优化配置的工厂函数

    Args:
        level: 并发级别 ("minimal", "moderate", "high", "maximum")
        mode: 处理模式 ("throughput", "latency", "balanced", "resource_efficient")
        preset: 预设配置名称 ("high_throughput", "low_latency", "balanced", "resource_efficient")
        custom_params: 自定义参数字典

    Returns:
        ConcurrentOptimizationConfig: 配置实例

    Raises:
        ValueError: 参数无效时抛出异常
    """
    # 1. 首先尝试从预设加载
    if preset:
        config = ConcurrentOptimizationPresets.get_preset(preset)
        if not config:
            raise ValueError(f"无效的预设配置: {preset}")
    else:
        # 2. 使用默认配置
        config = ConcurrentOptimizationConfig()

    # 3. 应用指定的并发级别
    if level:
        try:
            config.concurrency_level = ConcurrencyLevel(level)
        except ValueError:
            raise ValueError(f"无效的并发级别: {level}")

    # 4. 应用指定的处理模式
    if mode:
        try:
            config.processing_mode = ProcessingMode(mode)
        except ValueError:
            raise ValueError(f"无效的处理模式: {mode}")

    # 5. 应用自定义参数
    if custom_params:
        for key, value in custom_params.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                raise ValueError(f"未知的配置参数: {key}")

    return config
