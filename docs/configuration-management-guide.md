# XLeRobot NPU转换器 - 配置管理系统使用指南

## 概述

XLeRobot配置管理系统是一个强大而灵活的配置管理解决方案，专为AI模型NPU转换而设计。本系统支持多种模型类型，包括VITS-Cantonese TTS、SenseVoice ASR和Piper VITS TTS，提供完整的配置生命周期管理。

## 🚀 快速开始

### 基础使用示例

```python
from pathlib import Path
from npu_converter.config import ConfigurationManager

# 1. 初始化配置管理器
config_file = Path("config.yaml")
config_manager = ConfigurationManager(config_file)

# 2. 加载配置
config = config_manager.load_config()

# 3. 验证配置
if config_manager.validate_config():
    print("配置验证成功!")
else:
    print("配置验证失败!")

# 4. 获取配置参数
model_type = config_manager.get_config("project.model_type")
target_device = config_manager.get_config("hardware.target_device")

print(f"模型类型: {model_type}")
print(f"目标设备: {target_device}")
```

### 创建不同模型的配置

#### VITS-Cantonese TTS配置 (主要模型)

```python
# 创建VITS-Cantonese配置
vits_config = {
    "project": {
        "name": "cantonese_tts_model",
        "version": "1.0.0",
        "model_type": "vits_cantonese",
        "description": "粤语语音合成模型"
    },
    "hardware": {
        "target_device": "horizon_x5",
        "optimization_level": "O2",
        "memory_limit": "8GB",
        "compute_units": 10
    },
    "conversion_params": {
        "input_format": "onnx",
        "output_format": "bpu",
        "precision": "int8",
        "calibration_method": "minmax",
        "batch_size": 1,
        "num_workers": 4
    },
    "model_specific": {
        "vits_cantonese": {
            # 音频处理参数
            "sampling_rate": 22050,
            "filter_length": 1024,
            "hop_length": 256,
            "win_length": 1024,
            "n_mel_channels": 80,
            "mel_fmin": 0.0,
            "mel_fmax": 8000.0,

            # VITS架构参数
            "inter_channels": 192,
            "hidden_channels": 192,
            "filter_channels": 768,
            "n_heads": 2,
            "n_layers": 4,
            "kernel_size": 3,

            # 粤语特有参数
            "tone_embedding": True,
            "num_tones": 6,
            "use_jyutping": True,
            "cantonese_vocab_size": 5000,
            "phoneme_set": "jyutping_extended",

            # 合成参数
            "noise_scale": 0.667,
            "noise_scale_w": 0.8,
            "length_scale": 1.0
        }
    }
}

# 保存配置
config_manager = ConfigurationManager()
config_manager.config = vits_config
config_manager.save_config("vits_cantonese_config.yaml")
```

#### SenseVoice ASR配置

```python
# 创建SenseVoice配置
sensevoice_config = {
    "project": {
        "name": "multilingual_asr_model",
        "version": "1.0.0",
        "model_type": "sensevoice",
        "description": "多语言语音识别模型"
    },
    "hardware": {
        "target_device": "horizon_x5",
        "optimization_level": "O2",
        "memory_limit": "8GB"
    },
    "conversion_params": {
        "input_format": "onnx",
        "output_format": "bpu",
        "precision": "int8",
        "batch_size": 1
    },
    "model_specific": {
        "sensevoice": {
            # 音频处理参数
            "sample_rate": 16000,
            "n_fft": 400,
            "hop_length": 160,
            "win_length": 400,
            "n_mels": 80,

            # ASR特有参数
            "language_detection": True,
            "supported_languages": ["zh", "en", "yue", "ja"],
            "confidence_threshold": 0.8,
            "segmentation": True,
            "vad_enabled": True,

            # 语音处理参数
            "audio_length": 30,
            "vocab_size": 10000,
            "beam_size": 5
        }
    }
}

config_manager.save_config("sensevoice_config.yaml")
```

#### Piper VITS TTS配置

```python
# 创建Piper VITS配置
piper_config = {
    "project": {
        "name": "general_tts_model",
        "version": "1.0.0",
        "model_type": "piper_vits",
        "description": "通用语音合成模型"
    },
    "hardware": {
        "target_device": "horizon_x5",
        "optimization_level": "O2"
    },
    "conversion_params": {
        "input_format": "onnx",
        "output_format": "bpu",
        "precision": "int8"
    },
    "model_specific": {
        "piper_vits": {
            # 音频处理参数
            "sample_rate": 22050,
            "mel_channels": 80,
            "n_fft": 1024,
            "hop_size": 256,
            "win_size": 1024,
            "f_min": 0.0,
            "f_max": 8000.0,

            # 说话人配置
            "speaker_embedding": True,
            "num_speakers": 1,
            "speaker_id": 0,
            "embedding_dim": 192,

            # VITS架构参数
            "inter_channels": 192,
            "hidden_channels": 192,
            "filter_channels": 768,
            "n_heads": 2,
            "n_layers": 6,
            "kernel_size": 3,

            # 合成参数
            "noise_scale": 0.667,
            "noise_scale_d": 0.8,
            "length_scale": 1.0
        }
    }
}

config_manager.save_config("piper_vits_config.yaml")
```

## 🔧 高级功能

### 动态配置修改

```python
# 运行时修改配置
config_manager = ConfigurationManager("config.yaml")
config_manager.load_config()

# 修改性能参数
config_manager.set_config("performance.target_latency_ms", 150)
config_manager.set_config("hardware.optimization_level", "O3")

# 添加新配置项
config_manager.set_config("debug.enabled", True)
config_manager.set_config("debug.log_level", "INFO")

# 批量修改
performance_updates = {
    "target_latency_ms": 100,
    "max_realtime_factor": 0.8,
    "enable_streaming": True
}
config_manager.update_config("performance", performance_updates)

# 保存修改
config_manager.save_config()
```

### 配置验证和错误处理

```python
# 启用详细验证
config_manager = ConfigurationManager("config.yaml")
config = config_manager.load_config(fast_validation=False)

# 获取验证错误
errors = config_manager.get_validation_errors()
if errors:
    print("配置验证错误:")
    for error in errors:
        print(f"  - {error.field}: {error.message}")
        print(f"    建议: {error.suggestion}")

# 自定义验证规则
from npu_converter.config.validation import ValidationRule, ValidationResult

custom_rule = ValidationRule(
    field_path="hardware.memory_limit",
    validator=lambda value: int(value.rstrip("GB")) >= 4,
    error_message="内存限制不能少于4GB",
    suggestion="请设置memory_limit为4GB或更高"
)

config_manager.add_validation_rule(custom_rule)
```

### 配置热加载

```python
# 启用热加载
config_manager = ConfigurationManager("config.yaml")
config_manager.load_config()

# 启动文件监听
config_manager.enable_hot_reload()

# 配置回调函数
def on_config_change(config_path, changes):
    print(f"配置文件 {config_path} 已更新")
    print("变更内容:", changes)

    # 重新验证配置
    if config_manager.validate_config():
        print("新配置验证成功")
    else:
        print("新配置验证失败，执行回滚")
        config_manager.rollback()

config_manager.add_change_callback(on_config_change)

# 在应用运行期间修改配置文件，系统会自动检测并重新加载
try:
    # 应用主循环
    while True:
        # 使用配置执行任务
        current_config = config_manager.get_config()
        process_with_config(current_config)
        time.sleep(1)
except KeyboardInterrupt:
    config_manager.disable_hot_reload()
```

### 配置备份和恢复

```python
# 创建配置备份
config_manager = ConfigurationManager("config.yaml")
config_manager.load_config()

# 手动创建备份
backup_path = config_manager.create_backup("pre_optimization")
print(f"备份已创建: {backup_path}")

# 列出所有备份
backups = config_manager.list_backups()
for backup in backups:
    print(f"备份: {backup['name']} - {backup['created_at']}")

# 恢复到指定备份
rollback_success = config_manager.rollback_to_backup(backup_path)
if rollback_success:
    print("配置已成功恢复到备份状态")

# 自动备份策略
config_manager.enable_auto_backup(
    backup_interval=3600,  # 每小时备份一次
    max_backups=24        # 保留24个备份
)
```

## 📋 配置模板系统

### 获取默认模板

```python
from npu_converter.config.strategies import VITSCantoneseConfigStrategy

# 获取VITS-Cantonese默认模板
strategy = VITSCantoneseConfigStrategy()
template = strategy.get_default_template()

# 修改模板
template["project"]["name"] = "my_cantonese_tts"
template["hardware"]["memory_limit"] = "16GB"

# 保存为新的配置文件
config_manager = ConfigurationManager()
config_manager.config = template
config_manager.save_config("my_vits_config.yaml")
```

### 模板继承和扩展

```python
# 创建基础模板
base_template = {
    "project": {
        "version": "1.0.0",
        "description": "基于模板的配置"
    },
    "hardware": {
        "target_device": "horizon_x5",
        "optimization_level": "O2"
    },
    "conversion_params": {
        "input_format": "onnx",
        "output_format": "bpu",
        "precision": "int8"
    }
}

# 基于基础模板创建特定配置
vits_config = base_template.copy()
vits_config["project"].update({
    "name": "vits_from_template",
    "model_type": "vits_cantonese"
})
vits_config["model_specific"] = {
    "vits_cantonese": strategy.get_default_template()["model_specific"]["vits_cantonese"]
}
```

## 🔍 配置查询和调试

### 配置路径查询

```python
# 支持点号分隔的配置路径
model_type = config_manager.get_config("project.model_type")
sampling_rate = config_manager.get_config("model_specific.vits_cantonese.sampling_rate")

# 使用列表路径
nested_value = config_manager.get_config(["model_specific", "vits_cantonese", "inter_channels"])

# 检查配置是否存在
if config_manager.has_config("model_specific.vits_cantonese"):
    print("VITS-Cantonese配置已设置")

# 获取所有配置键
all_keys = config_manager.get_all_keys()
print("所有配置键:", all_keys)
```

### 配置调试信息

```python
# 获取配置摘要
summary = config_manager.get_config_summary()
print("配置摘要:")
print(f"  模型类型: {summary['model_type']}")
print(f"  目标设备: {summary['target_device']}")
print(f"  配置大小: {summary['config_size']} bytes")

# 获取策略信息
strategy = config_manager._current_strategy
if strategy:
    print(f"当前策略: {strategy.__class__.__name__}")
    print(f"支持的字段数: {len(strategy.get_model_specific_fields())}")

# 配置性能指标
metrics = config_manager.get_performance_metrics()
print(f"加载时间: {metrics['load_time_ms']}ms")
print(f"验证时间: {metrics['validation_time_ms']}ms")
```

## ⚡ 性能优化建议

### 1. 使用快速验证

```python
# 开发环境使用快速验证
config = config_manager.load_config(fast_validation=True)

# 生产环境使用完整验证
config = config_manager.load_config(fast_validation=False)
```

### 2. 启用懒加载

```python
# 延迟初始化非关键组件
config_manager = ConfigurationManager("config.yaml", lazy_init=True)
```

### 3. 批量配置更新

```python
# 避免多次单点更新，使用批量更新
updates = {
    "hardware.optimization_level": "O3",
    "performance.target_latency_ms": 100,
    "performance.batch_size": 4
}
config_manager.batch_update(updates)
```

## 🚨 错误处理最佳实践

### 配置加载错误

```python
try:
    config = config_manager.load_config()
except ConfigFileNotFoundError:
    print("配置文件未找到，使用默认配置")
    config = config_manager.get_default_config()
except ConfigValidationError as e:
    print(f"配置验证失败: {e}")
    print("错误详情:", e.errors)
    config = None
except Exception as e:
    print(f"配置加载异常: {e}")
    config = None
```

### 热加载错误

```python
def safe_reload_handler(config_path, changes):
    try:
        # 验证新配置
        if config_manager.validate_config():
            print("配置热加载成功")
        else:
            print("新配置无效，执行回滚")
            config_manager.rollback()
    except Exception as e:
        print(f"热加载异常: {e}")
        config_manager.rollback()

config_manager.add_change_callback(safe_reload_handler)
```

## 📚 完整示例

### 生产环境配置管理示例

```python
#!/usr/bin/env python3
"""
XLeRobot配置管理系统生产环境示例
"""

import logging
import time
from pathlib import Path
from npu_converter.config import ConfigurationManager
from npu_converter.config.exceptions import *

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProductionConfigManager:
    def __init__(self, config_file: str):
        self.config_file = Path(config_file)
        self.config_manager = ConfigurationManager(self.config_file)
        self.setup_error_handling()

    def setup_error_handling(self):
        """设置错误处理策略"""
        def on_config_error(error_type, error_details):
            logger.error(f"配置错误 [{error_type}]: {error_details}")

        self.config_manager.set_error_handler(on_config_error)

    def initialize(self) -> bool:
        """初始化配置管理系统"""
        try:
            logger.info(f"正在加载配置文件: {self.config_file}")

            # 启用性能优化选项
            config = self.config_manager.load_config(
                fast_validation=True,
                lazy_init=True
            )

            # 完整验证（如果需要）
            if not self.config_manager.validate_config():
                logger.error("配置验证失败")
                return False

            logger.info("配置加载成功")

            # 启用热加载
            self.config_manager.enable_hot_reload()
            self.config_manager.add_change_callback(self.on_config_change)

            # 启用自动备份
            self.config_manager.enable_auto_backup(
                backup_interval=3600,
                max_backups=24
            )

            # 显示配置摘要
            self.show_config_summary()

            return True

        except Exception as e:
            logger.error(f"配置初始化失败: {e}")
            return False

    def on_config_change(self, config_path, changes):
        """配置变更回调"""
        logger.info(f"检测到配置变更: {config_path}")
        logger.info(f"变更内容: {changes}")

        # 验证新配置
        if self.config_manager.validate_config():
            logger.info("新配置验证成功")
            self.show_config_summary()
        else:
            logger.warning("新配置验证失败，执行回滚")
            self.config_manager.rollback()

    def show_config_summary(self):
        """显示配置摘要"""
        summary = self.config_manager.get_config_summary()
        logger.info("=== 配置摘要 ===")
        logger.info(f"模型类型: {summary.get('model_type', 'Unknown')}")
        logger.info(f"目标设备: {summary.get('target_device', 'Unknown')}")
        logger.info(f"优化级别: {self.config_manager.get_config('hardware.optimization_level')}")
        logger.info(f"内存限制: {self.config_manager.get_config('hardware.memory_limit')}")

    def run(self):
        """运行配置管理服务"""
        if not self.initialize():
            logger.error("配置管理系统初始化失败")
            return

        try:
            logger.info("配置管理系统运行中...")
            while True:
                # 模拟应用主循环
                current_config = self.config_manager.get_config()
                # 这里使用配置执行实际任务
                time.sleep(5)

        except KeyboardInterrupt:
            logger.info("正在关闭配置管理系统...")
            self.config_manager.disable_hot_reload()
            logger.info("配置管理系统已关闭")

if __name__ == "__main__":
    # 使用示例
    config_manager = ProductionConfigManager("production_config.yaml")
    config_manager.run()
```

## 📖 参考资料

- [技术架构文档](architecture-story-1.4.md)
- [API参考文档](api-reference.md)
- [故障排除指南](troubleshooting.md)
- [最佳实践](best-practices.md)

---

**版本**: v1.0.0
**更新时间**: 2025-10-26
**维护者**: XLeRobot开发团队