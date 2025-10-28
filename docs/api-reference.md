# XLeRobot配置管理系统 - API参考文档

## 概述

本文档提供XLeRobot配置管理系统的完整API参考，包括所有公共类、方法和接口的详细说明。

## 核心模块

### ConfigurationManager

配置管理系统的主控制器，提供配置加载、验证、修改和持久化功能。

#### 构造函数

```python
def __init__(
    config_file: Optional[Union[str, Path]] = None,
    lazy_init: bool = False,
    enable_backup: bool = True
):
    """
    初始化配置管理器

    Args:
        config_file: 配置文件路径，如果为None则创建内存配置
        lazy_init: 是否启用懒加载模式
        enable_backup: 是否启用自动备份功能
    """
```

#### 主要方法

##### load_config()

```python
def load_config(
    fast_validation: bool = True,
    force_reload: bool = False
) -> Dict[str, Any]:
    """
    加载配置文件

    Args:
        fast_validation: 是否使用快速验证模式
        force_reload: 是否强制重新加载

    Returns:
        配置字典

    Raises:
        ConfigFileNotFoundError: 配置文件不存在
        ConfigValidationError: 配置验证失败
    """
```

##### validate_config()

```python
def validate_config(config: Optional[Dict] = None) -> bool:
    """
    验证配置

    Args:
        config: 要验证的配置，如果为None则验证当前配置

    Returns:
        验证是否通过

    Raises:
        ConfigValidationError: 配置验证失败
    """
```

##### get_config()

```python
def get_config(
    key: Optional[Union[str, List[str]]] = None,
    default: Any = None
) -> Any:
    """
    获取配置值

    Args:
        key: 配置键，支持点号分隔的路径或列表路径
        default: 默认值

    Returns:
        配置值

    Examples:
        # 获取完整配置
        config = manager.get_config()

        # 获取嵌套配置
        model_type = manager.get_config("project.model_type")

        # 使用列表路径
        value = manager.get_config(["model_specific", "vits_cantonese", "sampling_rate"])
    """
```

##### set_config()

```python
def set_config(
    key: Union[str, List[str]],
    value: Any,
    validate: bool = True
) -> None:
    """
    设置配置值

    Args:
        key: 配置键，支持点号分隔的路径或列表路径
        value: 配置值
        validate: 是否验证新值

    Raises:
        ConfigValidationError: 配置验证失败

    Examples:
        manager.set_config("hardware.optimization_level", "O3")
        manager.set_config(["performance", "target_latency_ms"], 100)
    """
```

##### update_config()

```python
def update_config(
    section: str,
    updates: Dict[str, Any],
    validate: bool = True
) -> None:
    """
    批量更新配置节

    Args:
        section: 配置节名称
        updates: 更新的配置字典
        validate: 是否验证更新

    Examples:
        updates = {
            "target_latency_ms": 100,
            "batch_size": 4
        }
        manager.update_config("performance", updates)
    """
```

##### save_config()

```python
def save_config(
    config_file: Optional[Union[str, Path]] = None,
    backup: bool = True
) -> None:
    """
    保存配置到文件

    Args:
        config_file: 保存路径，如果为None则保存到原文件
        backup: 是否在保存前创建备份

    Raises:
        ConfigSaveError: 配置保存失败
    """
```

##### create_backup()

```python
def create_backup(name: Optional[str] = None) -> str:
    """
    创建配置备份

    Args:
        name: 备份名称，如果为None则使用时间戳

    Returns:
        备份文件路径

    Examples:
        backup_path = manager.create_backup("pre_optimization")
    """
```

##### rollback_to_backup()

```python
def rollback_to_backup(backup_path: str) -> bool:
    """
    回滚到指定备份

    Args:
        backup_path: 备份文件路径

    Returns:
        回滚是否成功
    """
```

##### enable_hot_reload()

```python
def enable_hot_reload() -> None:
    """
    启用配置热加载功能

    启动文件监听，自动检测配置文件变更并重新加载
    """
```

##### disable_hot_reload()

```python
def disable_hot_reload() -> None:
    """
    禁用配置热加载功能
    """
```

##### add_change_callback()

```python
def add_change_callback(callback: Callable[[str, Dict], None]) -> None:
    """
    添加配置变更回调函数

    Args:
        callback: 回调函数，接收(config_path, changes)参数

    Examples:
        def on_change(config_path, changes):
            print(f"配置已变更: {config_path}")

        manager.add_change_callback(on_change)
    """
```

## 配置策略接口

### BaseConfigStrategy

所有配置策略的基类，定义了配置管理的通用接口。

#### 抽象方法

##### get_model_type()

```python
def get_model_type() -> str:
    """
    获取模型类型

    Returns:
        模型类型标识符
    """
```

##### validate_model_specific_config()

```python
def validate_model_specific_config(config: Dict) -> bool:
    """
    验证模型特定配置

    Args:
        config: 配置字典

    Returns:
        验证是否通过
    """
```

##### get_default_template()

```python
def get_default_template() -> Dict[str, Any]:
    """
    获取默认配置模板

    Returns:
        默认配置字典
    """
```

##### get_validation_rules()

```python
def get_validation_rules() -> List[ValidationRule]:
    """
    获取验证规则列表

    Returns:
        验证规则列表
    """
```

## VITSCantoneseConfigStrategy

VITS-Cantonese TTS模型的配置策略实现。

### 特有方法

##### get_audio_processing_config()

```python
def get_audio_processing_config() -> Dict[str, Any]:
    """
    获取音频处理配置

    Returns:
        音频处理参数字典，包含采样率、滤波器长度等
    """
```

##### get_vits_architecture_config()

```python
def get_vits_architecture_config() -> Dict[str, Any]:
    """
    获取VITS架构配置

    Returns:
        VITS模型架构参数字典
    """
```

##### get_cantonese_specific_config()

```python
def get_cantonese_specific_config() -> Dict[str, Any]:
    """
    获取粤语特定配置

    Returns:
        粤语语音合成特定参数字典
    """
```

## SenseVoiceConfigStrategy

SenseVoice ASR模型的配置策略实现。

### 特有方法

##### get_asr_config()

```python
def get_asr_config() -> Dict[str, Any]:
    """
    获取ASR配置

    Returns:
        ASR模型配置参数字典
    """
```

##### get_language_config()

```python
def get_language_config() -> Dict[str, Any]:
    """
    获取多语言配置

    Returns:
        语言识别和配置参数字典
    """
```

## PiperVITSConfigStrategy

Piper VITS TTS模型的配置策略实现。

### 特有方法

##### get_speaker_config()

```python
def get_speaker_config() -> Dict[str, Any]:
    """
    获取说话人配置

    Returns:
        说话人相关配置参数字典
    """
```

## 配置验证系统

### ValidationRule

配置验证规则类。

#### 构造函数

```python
def __init__(
    field_path: str,
    validator: Callable[[Any], bool],
    error_message: str,
    suggestion: Optional[str] = None,
    severity: str = "error"
):
    """
    初始化验证规则

    Args:
        field_path: 配置字段路径
        validator: 验证函数
        error_message: 错误信息
        suggestion: 建议修复方案
        severity: 严重级别 (error, warning, info)
    """
```

#### 方法

##### validate()

```python
def validate(value: Any) -> ValidationResult:
    """
    验证配置值

    Args:
        value: 要验证的值

    Returns:
        验证结果对象
    """
```

### ValidationResult

验证结果类。

#### 属性

- `is_valid: bool` - 验证是否通过
- `error_message: Optional[str]` - 错误信息
- `suggestion: Optional[str]` - 建议修复方案
- `field_path: str` - 字段路径
- `severity: str` - 严重级别

## 配置模板系统

### ConfigTemplateManager

配置模板管理器。

#### 方法

##### get_template()

```python
def get_template(model_type: str) -> Dict[str, Any]:
    """
    获取指定模型类型的配置模板

    Args:
        model_type: 模型类型

    Returns:
        配置模板字典

    Raises:
        TemplateNotFoundError: 模板不存在
    """
```

##### register_template()

```python
def register_template(
    model_type: str,
    template: Dict[str, Any],
    overwrite: bool = False
) -> None:
    """
    注册配置模板

    Args:
        model_type: 模板类型
        template: 模板字典
        overwrite: 是否覆盖已存在的模板
    """
```

## 热加载系统

### HotReloadManager

配置热加载管理器。

#### 方法

##### start_monitoring()

```python
def start_monitoring(config_file: Path) -> None:
    """
    开始监听配置文件变更

    Args:
        config_file: 要监听的配置文件路径
    """
```

##### stop_monitoring()

```python
def stop_monitoring() -> None:
    """
    停止监听配置文件变更
    """
```

##### add_observer()

```python
def add_observer(observer: Callable[[Path], None]) -> None:
    """
    添加文件变更观察者

    Args:
        observer: 观察者回调函数
    """
```

## 异常类

### ConfigError

配置系统基础异常类。

```python
class ConfigError(Exception):
    """配置系统基础异常"""
    pass
```

### ConfigFileNotFoundError

配置文件不存在异常。

```python
class ConfigFileNotFoundError(ConfigError):
    """配置文件不存在异常"""
    pass
```

### ConfigValidationError

配置验证失败异常。

```python
class ConfigValidationError(ConfigError):
    """配置验证失败异常"""

    def __init__(self, message: str, errors: List[ValidationResult] = None):
        super().__init__(message)
        self.errors = errors or []
```

### ConfigSaveError

配置保存失败异常。

```python
class ConfigSaveError(ConfigError):
    """配置保存失败异常"""
    pass
```

## 工具函数

### config_merge()

```python
def config_merge(base: Dict, override: Dict) -> Dict:
    """
    深度合并配置字典

    Args:
        base: 基础配置
        override: 覆盖配置

    Returns:
        合并后的配置字典
    """
```

### validate_file_path()

```python
def validate_file_path(file_path: Union[str, Path]) -> Path:
    """
    验证文件路径安全性

    Args:
        file_path: 文件路径

    Returns:
        验证后的Path对象

    Raises:
        SecurityError: 路径不安全
    """
```

### parse_config_path()

```python
def parse_config_path(path: Union[str, List[str]]) -> List[str]:
    """
    解析配置路径

    Args:
        path: 配置路径，支持点号分隔字符串或列表

    Returns:
        解析后的路径列表
    """
```

## 常量定义

### 模型类型常量

```python
class ModelType:
    VITS_CANTONESE = "vits_cantonese"
    SENSEVOICE = "sensevoice"
    PIPER_VITS = "piper_vits"
```

### 硬件类型常量

```python
class HardwareType:
    HORIZON_X5 = "horizon_x5"
    NVIDIA_GPU = "nvidia_gpu"
    CPU = "cpu"
```

### 优化级别常量

```python
class OptimizationLevel:
    O0 = "O0"  # 无优化
    O1 = "O1"  # 基础优化
    O2 = "O2"  # 标准优化
    O3 = "O3"  # 激进优化
```

## 使用示例

### 基础使用

```python
from npu_converter.config import ConfigurationManager

# 初始化
manager = ConfigurationManager("config.yaml")

# 加载配置
config = manager.load_config()

# 获取配置
model_type = manager.get_config("project.model_type")

# 设置配置
manager.set_config("hardware.optimization_level", "O3")

# 保存配置
manager.save_config()
```

### 高级使用

```python
# 启用热加载
manager.enable_hot_reload()

def on_change(config_path, changes):
    print(f"配置已变更: {changes}")
    if not manager.validate_config():
        manager.rollback()

manager.add_change_callback(on_change)

# 创建备份
backup_path = manager.create_backup("before_changes")

# 回滚
if some_error_condition:
    manager.rollback_to_backup(backup_path)
```

### 策略使用

```python
from npu_converter.config.strategies import VITSCantoneseConfigStrategy

# 直接使用策略
strategy = VITSCantoneseConfigStrategy()
template = strategy.get_default_template()

# 获取特定配置
audio_config = strategy.get_audio_processing_config()
vits_config = strategy.get_vits_architecture_config()
```

---

**版本**: v1.0.0
**更新时间**: 2025-10-26
**维护者**: XLeRobot开发团队