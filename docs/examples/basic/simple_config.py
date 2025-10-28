#!/usr/bin/env python3
"""
XLeRobot配置管理系统 - 基础使用示例

演示最基本的配置管理操作，包括：
- 配置文件加载
- 配置参数读取
- 配置修改和保存
- 基础错误处理
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from npu_converter.config import ConfigurationManager
from npu_converter.config.exceptions import (
    ConfigFileNotFoundError,
    ConfigValidationError,
    ConfigSaveError
)

def demonstrate_basic_config_operations():
    """演示基础配置操作"""
    print("🚀 XLeRobot配置管理系统 - 基础操作演示")
    print("=" * 60)

    # 1. 创建配置管理器
    config_file = Path("basic_config.yaml")
    manager = ConfigurationManager(config_file)

    print(f"📁 配置文件路径: {config_file}")

    # 2. 检查配置文件是否存在
    if not config_file.exists():
        print("⚠️  配置文件不存在，创建默认配置...")
        create_default_config(manager)

    # 3. 加载配置
    try:
        print("\n📖 正在加载配置...")
        config = manager.load_config(fast_validation=True)
        print("✅ 配置加载成功!")

        # 显示配置大小
        config_size = len(str(config))
        print(f"📊 配置大小: {config_size} 字符")

    except ConfigFileNotFoundError:
        print("❌ 配置文件未找到")
        return False
    except ConfigValidationError as e:
        print(f"❌ 配置验证失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 配置加载异常: {e}")
        return False

    # 4. 读取配置参数
    print("\n🔍 读取配置参数...")

    try:
        # 获取项目信息
        project_name = manager.get_config("project.name")
        model_type = manager.get_config("project.model_type")
        version = manager.get_config("project.version")

        print(f"📋 项目名称: {project_name}")
        print(f"🤖 模型类型: {model_type}")
        print(f"🔢 版本: {version}")

        # 获取硬件配置
        target_device = manager.get_config("hardware.target_device")
        optimization_level = manager.get_config("hardware.optimization_level")
        memory_limit = manager.get_config("hardware.memory_limit")

        print(f"🖥️  目标设备: {target_device}")
        print(f"⚡ 优化级别: {optimization_level}")
        print(f"💾 内存限制: {memory_limit}")

        # 获取转换参数
        input_format = manager.get_config("conversion_params.input_format")
        output_format = manager.get_config("conversion_params.output_format")
        precision = manager.get_config("conversion_params.precision")

        print(f"📥 输入格式: {input_format}")
        print(f"📤 输出格式: {output_format}")
        print(f"🎯 精度: {precision}")

    except Exception as e:
        print(f"❌ 配置读取失败: {e}")
        return False

    # 5. 修改配置参数
    print("\n✏️  修改配置参数...")

    try:
        # 修改优化级别
        original_level = manager.get_config("hardware.optimization_level")
        new_level = "O3"
        manager.set_config("hardware.optimization_level", new_level)
        print(f"⚡ 优化级别: {original_level} → {new_level}")

        # 修改批处理大小
        original_batch = manager.get_config("conversion_params.batch_size", 1)
        new_batch = 4
        manager.set_config("conversion_params.batch_size", new_batch)
        print(f"📦 批处理大小: {original_batch} → {new_batch}")

        # 添加新的配置项
        manager.set_config("debug.enabled", True)
        manager.set_config("debug.log_level", "INFO")
        print("🐛 调试配置: 已启用")

    except Exception as e:
        print(f"❌ 配置修改失败: {e}")
        return False

    # 6. 批量更新配置
    print("\n📦 批量更新配置...")

    try:
        performance_updates = {
            "target_latency_ms": 100,
            "max_realtime_factor": 0.8,
            "enable_streaming": True,
            "chunk_size": 1024
        }

        manager.update_config("performance", performance_updates)
        print("✅ 性能配置批量更新完成")

        # 显示更新后的性能配置
        latency = manager.get_config("performance.target_latency_ms")
        rtf = manager.get_config("performance.max_realtime_factor")
        streaming = manager.get_config("performance.enable_streaming")

        print(f"⏱️  目标延迟: {latency}ms")
        print(f"🔄 实时因子: {rtf}")
        print(f"📡 流式处理: {streaming}")

    except Exception as e:
        print(f"❌ 批量更新失败: {e}")
        return False

    # 7. 配置验证
    print("\n🔍 配置验证...")

    try:
        is_valid = manager.validate_config()
        if is_valid:
            print("✅ 配置验证通过")
        else:
            print("❌ 配置验证失败")
            errors = manager.get_validation_errors()
            if errors:
                print("错误详情:")
                for error in errors:
                    print(f"  - {error.field_path}: {error.message}")
            return False

    except Exception as e:
        print(f"❌ 配置验证异常: {e}")
        return False

    # 8. 保存配置
    print("\n💾 保存配置...")

    try:
        manager.save_config()
        print("✅ 配置保存成功")

        # 检查文件是否存在
        if config_file.exists():
            file_size = config_file.stat().st_size
            print(f"📁 文件大小: {file_size} 字节")

    except ConfigSaveError as e:
        print(f"❌ 配置保存失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 保存异常: {e}")
        return False

    # 9. 配置路径操作
    print("\n🛤️  配置路径操作演示...")

    try:
        # 检查配置是否存在
        if manager.has_config("project"):
            print("✅ project 配置节存在")

        if manager.has_config("model_specific.vits_cantonese"):
            print("✅ VITS-Cantonese 配置存在")

        # 获取所有配置键
        all_keys = manager.get_all_keys()
        print(f"🔑 配置键数量: {len(all_keys)}")

        # 显示部分配置键
        sample_keys = all_keys[:5]
        print(f"📋 示例配置键: {sample_keys}")

    except Exception as e:
        print(f"❌ 路径操作失败: {e}")
        return False

    print("\n🎉 基础配置操作演示完成!")
    return True

def create_default_config(manager: ConfigurationManager):
    """创建默认配置"""
    default_config = {
        "project": {
            "name": "xlerobot_basic_example",
            "version": "1.0.0",
            "model_type": "vits_cantonese",
            "description": "XLeRobot基础配置示例"
        },
        "hardware": {
            "target_device": "horizon_x5",
            "optimization_level": "O2",
            "memory_limit": "8GB",
            "compute_units": 10,
            "cache_size": "256MB"
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
        },
        "performance": {
            "target_latency_ms": 200,
            "max_realtime_factor": 0.9,
            "enable_streaming": False
        }
    }

    manager.config = default_config
    manager.save_config()
    print("✅ 默认配置已创建")

def demonstrate_error_handling():
    """演示错误处理"""
    print("\n🚨 错误处理演示")
    print("-" * 30)

    # 1. 不存在的配置文件
    print("1. 测试不存在的配置文件...")
    try:
        nonexistent_manager = ConfigurationManager("nonexistent_config.yaml")
        nonexistent_manager.load_config()
        print("❌ 应该抛出异常但没有")
    except ConfigFileNotFoundError:
        print("✅ 正确捕获了配置文件不存在异常")
    except Exception as e:
        print(f"❌ 捕获了意外异常: {e}")

    # 2. 无效配置值
    print("\n2. 测试无效配置值...")
    try:
        manager = ConfigurationManager("basic_config.yaml")
        if manager.load_config():
            # 尝试设置无效的内存限制
            manager.set_config("hardware.memory_limit", "invalid_memory")
            print("❌ 应该捕获验证错误但没有")
    except (ConfigValidationError, ValueError) as e:
        print(f"✅ 正确捕获了配置验证错误: {e}")
    except Exception as e:
        print(f"❌ 捕获了意外异常: {e}")

def main():
    """主函数"""
    print("🎯 开始演示基础配置管理功能\n")

    # 演示基础操作
    success = demonstrate_basic_config_operations()

    # 演示错误处理
    demonstrate_error_handling()

    if success:
        print("\n✅ 所有演示成功完成!")
        print("\n💡 提示:")
        print("  - 查看生成的 basic_config.yaml 文件")
        print("  - 尝试修改配置文件并重新运行")
        print("  - 查看其他示例了解高级功能")
    else:
        print("\n❌ 演示过程中遇到错误")

    print("\n📚 相关文档:")
    print("  - 配置管理系统使用指南: docs/configuration-management-guide.md")
    print("  - API参考文档: docs/api-reference.md")

if __name__ == "__main__":
    main()