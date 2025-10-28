# XLeRobot配置管理系统 - 示例集合

本目录包含了XLeRobot配置管理系统的详细使用示例，涵盖了从基础配置到高级功能的各种场景。

## 📁 示例目录结构

```
examples/
├── README.md                    # 本文件
├── basic/                       # 基础使用示例
│   ├── simple_config.py         # 简单配置示例
│   ├── model_configs/           # 模型配置示例
│   │   ├── vits_cantonese.yaml  # VITS-Cantonese配置
│   │   ├── sensevoice.yaml      # SenseVoice配置
│   │   └── piper_vits.yaml      # Piper VITS配置
│   └── validation_example.py    # 配置验证示例
├── advanced/                    # 高级功能示例
│   ├── hot_reload_demo.py       # 热加载演示
│   ├── backup_recovery.py       # 备份恢复示例
│   ├── dynamic_config.py        # 动态配置示例
│   └── custom_validation.py     # 自定义验证规则
├── production/                  # 生产环境示例
│   ├── config_service.py        # 配置服务示例
│   ├── monitoring_integration.py # 监控集成示例
│   └── error_handling.py        # 错误处理示例
└── testing/                     # 测试相关示例
    ├── test_configurations.py   # 测试配置生成
    ├── mock_configs.py          # 模拟配置
    └── performance_benchmark.py # 性能基准测试
```

## 🚀 快速开始示例

### 1. 基础配置管理

```python
# examples/basic/simple_config.py
from pathlib import Path
from npu_converter.config import ConfigurationManager

def main():
    # 初始化配置管理器
    config_file = Path("config.yaml")
    manager = ConfigurationManager(config_file)

    # 加载配置
    try:
        config = manager.load_config()
        print("✅ 配置加载成功")
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return

    # 获取基本信息
    model_type = manager.get_config("project.model_type")
    target_device = manager.get_config("hardware.target_device")

    print(f"📋 模型类型: {model_type}")
    print(f"🖥️  目标设备: {target_device}")

    # 动态修改配置
    manager.set_config("hardware.optimization_level", "O3")
    manager.save_config()
    print("✅ 配置已更新并保存")

if __name__ == "__main__":
    main()
```

### 2. 模型配置示例

详见 `basic/model_configs/` 目录中的YAML配置文件：

- **VITS-Cantonese TTS配置**: 粤语语音合成模型配置
- **SenseVoice ASR配置**: 多语言语音识别模型配置
- **Piper VITS TTS配置**: 通用语音合成模型配置

### 3. 热加载演示

```python
# examples/advanced/hot_reload_demo.py
import time
from pathlib import Path
from npu_converter.config import ConfigurationManager

def on_config_change(config_path, changes):
    print(f"🔄 配置文件变更: {config_path}")
    print(f"📝 变更内容: {changes}")

    # 验证新配置
    if manager.validate_config():
        print("✅ 新配置验证通过")
    else:
        print("❌ 新配置验证失败")
        manager.rollback()

def main():
    manager = ConfigurationManager("config.yaml")
    manager.load_config()

    # 启用热加载
    manager.enable_hot_reload()
    manager.add_change_callback(on_config_change)

    print("🔥 热加载已启用，请修改config.yaml文件...")
    print("按Ctrl+C退出")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        manager.disable_hot_reload()
        print("👋 热加载已禁用")

if __name__ == "__main__":
    main()
```

## 📖 示例说明

### 基础示例 (basic/)

- **simple_config.py**: 最基础的配置加载、读取和修改操作
- **validation_example.py**: 配置验证和错误处理示例
- **model_configs/**: 三种支持模型的完整配置模板

### 高级示例 (advanced/)

- **hot_reload_demo.py**: 配置文件热加载功能演示
- **backup_recovery.py**: 配置备份和恢复机制示例
- **dynamic_config.py**: 运行时动态配置修改示例
- **custom_validation.py**: 自定义验证规则示例

### 生产环境示例 (production/)

- **config_service.py**: 生产级配置服务实现
- **monitoring_integration.py**: 与监控系统集成示例
- **error_handling.py**: 完整的错误处理策略

### 测试示例 (testing/)

- **test_configurations.py**: 自动生成测试配置
- **mock_configs.py**: 模拟配置生成工具
- **performance_benchmark.py**: 配置系统性能基准测试

## 🎯 使用建议

1. **初学者**: 从基础示例开始，逐步学习配置管理的基本概念
2. **进阶用户**: 查看高级示例，了解热加载、备份恢复等高级功能
3. **生产用户**: 参考生产环境示例，实现稳定可靠的配置管理服务
4. **开发者**: 使用测试示例进行单元测试和性能测试

## 📚 相关文档

- [配置管理系统使用指南](../configuration-management-guide.md)
- [API参考文档](../api-reference.md)
- [技术架构文档](../architecture-story-1.4.md)

---

**版本**: v1.0.0
**更新时间**: 2025-10-26
**维护者**: XLeRobot开发团队