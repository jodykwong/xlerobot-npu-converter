# XLeRobot 高级配置示例和最佳实践

## 🔧 高级配置模式

### 1. 配置继承和覆盖

```python
from pathlib import Path
from npu_converter.config import ConfigurationManager, ConfigTemplateManager

# 使用模板管理器创建基础配置
template_manager = ConfigTemplateManager()
base_template = template_manager.get_template("sensevoice_default")

# 应用环境特定的覆盖
production_overrides = {
    "hardware": {
        "optimization_level": "O3",  # 生产环境使用更高优化级别
        "memory_limit": "16GB"
    },
    "performance": {
        "target_latency_ms": 50,     # 生产环境要求更低延迟
        "enable_streaming": True
    },
    "conversion_params": {
        "batch_size": 4               # 生产环境使用更大批次
    }
}

# 合并配置
config_manager = ConfigurationManager()
final_config = template_manager.apply_template_overrides(base_template, production_overrides)

# 保存生产配置
config_manager.config = final_config
config_manager.save_config("production_sensevoice.yaml")
```

### 2. 动态配置更新

```python
# 运行时动态调整配置参数
from npu_converter.config import DynamicConfigManager

config_manager = ConfigurationManager("config.yaml")
config_manager.load_config()

# 启用动态配置管理
dynamic_manager = DynamicConfigManager(config_manager, validation_enabled=True)

# 在运行时调整性能参数
dynamic_manager.update_config("performance.batch_size", 8)
dynamic_manager.update_config("performance.target_latency_ms", 80)

# 动态更新会触发验证
print(f"配置更新后验证结果: {dynamic_manager.validate_current_config()}")
```

### 3. 配置热加载

```python
import time
from pathlib import Path
from npu_converter.config import ConfigurationManager

def on_config_change():
    """配置文件变更回调函数"""
    print("🔄 配置文件已更新，重新加载...")
    # 可以在这里添加应用逻辑，如重启服务、通知其他组件等

# 初始化配置管理器并启用热加载
config_manager = ConfigurationManager("config.yaml")
config_manager.load_config()

# 启用热加载监控
config_manager.enable_hot_reload(callback=on_config_change)

# 应用继续运行，配置文件变更时会自动触发回调
try:
    while True:
        time.sleep(1)
        # 应用主逻辑
        current_config = config_manager.get_config("project.model_type")
        print(f"当前模型类型: {current_config}")
except KeyboardInterrupt:
    config_manager.disable_hot_reload()
    print("热加载已停止")
```

### 4. 配置备份和恢复

```python
from datetime import datetime
from npu_converter.config import ConfigurationManager

config_manager = ConfigurationManager("production_config.yaml")
config_manager.load_config()

# 创建带时间戳的备份
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = config_manager.create_backup(f"pre_update_{timestamp}")

print(f"配置已备份至: {backup_path}")

# 执行配置更改
config_manager.set_config("performance.target_latency_ms", 60)
config_manager.set_config("hardware.optimization_level", "O3")

# 验证更改
if config_manager.validate_config():
    print("配置更改验证通过")
    config_manager.save_config()
    print("配置已保存")
else:
    print("配置验证失败，回滚到备份")
    config_manager.rollback_to_backup(backup_path)
    print("已回滚到之前版本")
```

## 🏗️ 多模型配置管理

### 1. 批量模型配置

```python
from pathlib import Path
from npu_converter.config import ConfigurationManager
import yaml

# 定义多个模型的配置
models_config = {
    "sensevoice_asr": {
        "model_type": "sensevoice",
        "config_file": "sensevoice_config.yaml",
        "priority": "high",
        "description": "中文语音识别模型"
    },
    "vits_cantonese": {
        "model_type": "vits_cantonese",
        "config_file": "vits_cantonese_config.yaml",
        "priority": "high",
        "description": "粤语语音合成模型"
    },
    "piper_vits": {
        "model_type": "piper_vits",
        "config_file": "piper_vits_config.yaml",
        "priority": "medium",
        "description": "多语言语音合成模型"
    }
}

# 批量创建和验证配置
for model_name, model_info in models_config.items():
    print(f"处理模型: {model_name}")

    # 使用相应的策略创建配置
    config_manager = ConfigurationManager()

    if model_info["model_type"] == "sensevoice":
        from npu_converter.config.strategies import SenseVoiceConfigStrategy
        strategy = SenseVoiceConfigStrategy({})
        config = strategy.get_default_template()
    elif model_info["model_type"] == "vits_cantonese":
        from npu_converter.config.strategies import VITSCantoneseConfigStrategy
        strategy = VITSCantoneseConfigStrategy({})
        config = strategy.get_default_template()
    elif model_info["model_type"] == "piper_vits":
        from npu_converter.config.strategies import PiperVITSConfigStrategy
        strategy = PiperVITSConfigStrategy({})
        config = strategy.get_default_template()

    # 保存配置文件
    config_file = Path(model_info["config_file"])
    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)

    # 验证配置
    test_manager = ConfigurationManager(config_file)
    if test_manager.load_config() and test_manager.validate_config():
        print(f"✅ {model_name} 配置创建并验证成功")
    else:
        print(f"❌ {model_name} 配置验证失败")
```

### 2. 配置对比和迁移

```python
import yaml
from pathlib import Path
from npu_converter.config import ConfigurationManager

def compare_configs(config1_path, config2_path):
    """对比两个配置文件的差异"""
    with open(config1_path, 'r') as f:
        config1 = yaml.safe_load(f)

    with open(config2_path, 'r') as f:
        config2 = yaml.safe_load(f)

    differences = []

    def compare_dict(d1, d2, path=""):
        for key in set(d1.keys()) | set(d2.keys()):
            current_path = f"{path}.{key}" if path else key

            if key not in d1:
                differences.append(f"仅在配置2中存在: {current_path} = {d2[key]}")
            elif key not in d2:
                differences.append(f"仅在配置1中存在: {current_path} = {d1[key]}")
            elif d1[key] != d2[key]:
                if isinstance(d1[key], dict) and isinstance(d2[key], dict):
                    compare_dict(d1[key], d2[key], current_path)
                else:
                    differences.append(f"值不同: {current_path} = {d1[key]} vs {d2[key]}")

    compare_dict(config1, config2)
    return differences

# 使用示例
config_v1 = Path("config_v1.yaml")
config_v2 = Path("config_v2.yaml")

differences = compare_configs(config_v1, config_v2)
if differences:
    print("配置差异:")
    for diff in differences:
        print(f"  - {diff}")
else:
    print("配置文件相同")
```

## 📊 性能优化配置

### 1. 高性能配置模板

```python
# 针对不同场景的性能优化配置
performance_configs = {
    "low_latency": {
        "description": "低延迟优先配置",
        "hardware": {
            "optimization_level": "O3",
            "memory_limit": "4GB",
            "compute_units": 16
        },
        "conversion_params": {
            "batch_size": 1,
            "num_workers": 1,
            "precision": "int8"
        },
        "performance": {
            "target_latency_ms": 20,
            "enable_streaming": True,
            "memory_optimization": True
        }
    },

    "high_throughput": {
        "description": "高吞吐量优先配置",
        "hardware": {
            "optimization_level": "O2",
            "memory_limit": "16GB",
            "compute_units": 10
        },
        "conversion_params": {
            "batch_size": 16,
            "num_workers": 8,
            "precision": "int8"
        },
        "performance": {
            "target_latency_ms": 200,
            "enable_streaming": False,
            "memory_optimization": False
        }
    },

    "balanced": {
        "description": "平衡配置",
        "hardware": {
            "optimization_level": "O2",
            "memory_limit": "8GB",
            "compute_units": 10
        },
        "conversion_params": {
            "batch_size": 4,
            "num_workers": 4,
            "precision": "int8"
        },
        "performance": {
            "target_latency_ms": 100,
            "enable_streaming": False,
            "memory_optimization": True
        }
    }
}

def create_performance_config(model_type, performance_profile):
    """创建特定性能配置的配置文件"""
    from npu_converter.config.strategies import (
        SenseVoiceConfigStrategy, VITSCantoneseConfigStrategy, PiperVITSConfigStrategy
    )

    # 获取模型的基础配置
    strategies = {
        "sensevoice": SenseVoiceConfigStrategy,
        "vits_cantonese": VITSCantoneseConfigStrategy,
        "piper_vits": PiperVITSConfigStrategy
    }

    strategy_class = strategies.get(model_type)
    if not strategy_class:
        raise ValueError(f"不支持的模型类型: {model_type}")

    strategy = strategy_class({})
    base_config = strategy.get_default_template()

    # 应用性能配置覆盖
    perf_config = performance_configs.get(performance_profile)
    if not perf_config:
        raise ValueError(f"不支持的性能配置: {performance_profile}")

    # 深度合并配置
    def deep_merge(base, override):
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                deep_merge(base[key], value)
            else:
                base[key] = value

    deep_merge(base_config, perf_config)

    # 保存配置
    config_filename = f"{model_type}_{performance_profile}_config.yaml"
    config_manager = ConfigurationManager()
    config_manager.config = base_config
    config_manager.save_config(config_filename)

    return config_filename

# 创建不同性能配置的配置文件
configs = []
for model_type in ["sensevoice", "vits_cantonese", "piper_vits"]:
    for perf_profile in ["low_latency", "high_throughput", "balanced"]:
        config_file = create_performance_config(model_type, perf_profile)
        configs.append(config_file)
        print(f"✅ 创建配置: {config_file}")
```

## 🛠️ 故障排除和调试

### 1. 配置验证和错误诊断

```python
from npu_converter.config import ConfigurationManager
from npu_converter.core.exceptions.config_errors import ConfigError, ConfigValidationError

def diagnose_config(config_path):
    """诊断配置文件问题"""
    print(f"🔍 诊断配置文件: {config_path}")

    try:
        config_manager = ConfigurationManager(config_path)

        # 尝试加载配置
        config = config_manager.load_config()
        print("✅ 配置文件加载成功")

        # 获取加载指标
        metrics = config_manager.get_metrics()
        print(f"📊 加载时间: {metrics.load_time_ms:.2f}ms")

        # 验证配置
        is_valid = config_manager.validate_config()
        if is_valid:
            print("✅ 配置验证通过")
        else:
            print("❌ 配置验证失败")

            # 获取详细的验证信息
            validator = config_manager._validator
            detailed_result = validator.validate_detailed(config)

            print("错误详情:")
            for error in detailed_result.errors:
                print(f"  ❌ {error.field_path}: {error.message}")
                print(f"     建议: {error.suggestion}")

            print("警告:")
            for warning in detailed_result.warnings:
                print(f"  ⚠️ {warning.field_path}: {warning.message}")

        # 检查策略初始化
        strategy = config_manager.get_strategy()
        if strategy:
            print(f"✅ 策略初始化成功: {strategy.get_model_type()}")
        else:
            print("❌ 策略初始化失败")

        # 检查关键配置项
        model_type = config_manager.get_config("project.model_type")
        target_device = config_manager.get_config("hardware.target_device")

        print(f"📋 模型类型: {model_type}")
        print(f"📋 目标设备: {target_device}")

    except ConfigError as e:
        print(f"❌ 配置错误: {e}")
        print("💡 建议解决方案:")
        print("  1. 检查配置文件格式是否正确")
        print("  2. 确认所有必需字段都已提供")
        print("  3. 验证模型类型是否受支持")

    except Exception as e:
        print(f"❌ 未知错误: {e}")
        print("💡 建议检查:")
        print("  1. 文件路径是否正确")
        print("  2. 文件权限是否足够")
        print("  3. 系统资源是否充足")

# 使用示例
diagnose_config("test_config.yaml")
```

### 2. 配置性能基准测试

```python
import time
import statistics
from pathlib import Path
from npu_converter.config import ConfigurationManager

def benchmark_config_performance(config_path, iterations=10):
    """对配置管理器进行性能基准测试"""
    print(f"🏃 配置性能基准测试: {config_path}")
    print(f"📊 测试迭代次数: {iterations}")

    load_times = []
    validation_times = []

    for i in range(iterations):
        # 测试加载性能
        start_time = time.time()
        config_manager = ConfigurationManager(config_path)
        config_manager.load_config()
        load_time = (time.time() - start_time) * 1000
        load_times.append(load_time)

        # 测试验证性能
        start_time = time.time()
        config_manager.validate_config()
        validation_time = (time.time() - start_time) * 1000
        validation_times.append(validation_time)

    # 计算统计数据
    load_stats = {
        "mean": statistics.mean(load_times),
        "median": statistics.median(load_times),
        "min": min(load_times),
        "max": max(load_times),
        "std": statistics.stdev(load_times) if len(load_times) > 1 else 0
    }

    validation_stats = {
        "mean": statistics.mean(validation_times),
        "median": statistics.median(validation_times),
        "min": min(validation_times),
        "max": max(validation_times),
        "std": statistics.stdev(validation_times) if len(validation_times) > 1 else 0
    }

    print("📈 加载性能统计:")
    print(f"  平均: {load_stats['mean']:.2f}ms")
    print(f"  中位数: {load_stats['median']:.2f}ms")
    print(f"  最小: {load_stats['min']:.2f}ms")
    print(f"  最大: {load_stats['max']:.2f}ms")
    print(f"  标准差: {load_stats['std']:.2f}ms")

    print("📈 验证性能统计:")
    print(f"  平均: {validation_stats['mean']:.2f}ms")
    print(f"  中位数: {validation_stats['median']:.2f}ms")
    print(f"  最小: {validation_stats['min']:.2f}ms")
    print(f"  最大: {validation_stats['max']:.2f}ms")
    print(f"  标准差: {validation_stats['std']:.2f}ms")

    # 性能评估
    load_target = 100  # 100ms
    validation_target = 50  # 50ms

    print("🎯 性能评估:")
    if load_stats['mean'] < load_target:
        print(f"✅ 加载性能达标 (平均 {load_stats['mean']:.2f}ms < {load_target}ms)")
    else:
        print(f"❌ 加载性能不达标 (平均 {load_stats['mean']:.2f}ms > {load_target}ms)")

    if validation_stats['mean'] < validation_target:
        print(f"✅ 验证性能达标 (平均 {validation_stats['mean']:.2f}ms < {validation_target}ms)")
    else:
        print(f"❌ 验证性能不达标 (平均 {validation_stats['mean']:.2f}ms > {validation_target}ms)")

    return load_stats, validation_stats

# 使用示例
benchmark_config_performance("test_config.yaml")
```

## 📚 最佳实践建议

### 1. 配置文件组织
- 使用版本控制管理配置文件
- 为不同环境创建独立的配置文件
- 使用配置模板避免重复
- 定期备份关键配置

### 2. 性能优化
- 启用配置缓存以提高加载速度
- 使用适当的批次大小平衡内存和性能
- 根据硬件资源调整配置参数
- 定期进行性能基准测试

### 3. 错误处理
- 始终验证配置文件格式
- 提供详细的错误信息和建议
- 实现配置回滚机制
- 记录配置变更历史

### 4. 监控和维护
- 监控配置加载性能
- 定期检查配置一致性
- 验证模型特定配置的正确性
- 保持配置文档的更新