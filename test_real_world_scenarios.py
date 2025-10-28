#!/usr/bin/env python3
"""
实际场景测试 - 模拟真实使用环境下的配置管理系统测试
"""

import sys
import tempfile
import yaml
import json
import time
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from npu_converter.config import ConfigurationManager, ConfigTemplateManager
from npu_converter.config.strategies import (
    SenseVoiceConfigStrategy, VITSCantoneseConfigStrategy, PiperVITSConfigStrategy
)

def test_production_deployment_scenario():
    """测试生产部署场景"""
    print("🏭 测试生产部署场景...")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # 场景: 生产环境需要高可靠性和性能
            # 1. 创建生产级配置
            production_configs = []
            for model_type in ["sensevoice", "vits_cantonese", "piper_vits"]:
                config_file = temp_path / f"production_{model_type}.yaml"

                if model_type == "sensevoice":
                    manager = ConfigurationManager()
                    strategy = SenseVoiceConfigStrategy({})
                    config = strategy.get_default_template()

                    # 生产环境优化配置
                    config["hardware"]["optimization_level"] = "O3"
                    config["hardware"]["memory_limit"] = "16GB"
                    config["performance"]["target_latency_ms"] = 30
                    config["performance"]["enable_streaming"] = True

                elif model_type == "vits_cantonese":
                    manager = ConfigurationManager()
                    strategy = VITSCantoneseConfigStrategy({})
                    config = strategy.get_default_template()

                    config["hardware"]["optimization_level"] = "O3"
                    config["performance"]["target_latency_ms"] = 80
                    config["model_specific"]["vits_cantonese"]["use_fast_synthesis"] = True

                else:  # piper_vits
                    manager = ConfigurationManager()
                    strategy = PiperVITSConfigStrategy({})
                    config = strategy.get_default_template()

                    config["hardware"]["optimization_level"] = "O2"
                    config["performance"]["target_latency_ms"] = 100

                # 保存配置
                with open(config_file, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False, indent=2)

                # 验证配置
                test_manager = ConfigurationManager(config_file)
                if test_manager.load_config() and test_manager.validate_config():
                    production_configs.append(config_file)
                    print(f"✅ 生产配置创建成功: {model_type}")
                else:
                    print(f"❌ 生产配置验证失败: {model_type}")
                    return False

            # 2. 测试配置加载性能
            load_times = []
            for config_file in production_configs:
                start_time = time.time()
                manager = ConfigurationManager(config_file)
                manager.load_config()
                load_time = (time.time() - start_time) * 1000
                load_times.append(load_time)

                if load_time > 50:  # 生产环境要求更快加载
                    print(f"⚠️ 配置加载时间过长: {config_file.name} - {load_time:.2f}ms")

            avg_load_time = sum(load_times) / len(load_times)
            if avg_load_time < 30:
                print(f"✅ 生产环境加载性能达标: {avg_load_time:.2f}ms")
            else:
                print(f"⚠️ 生产环境加载性能需要优化: {avg_load_time:.2f}ms")

            # 3. 测试并发访问
            def concurrent_load_test(config_file):
                try:
                    manager = ConfigurationManager(config_file)
                    manager.load_config()
                    return True
                except Exception as e:
                    print(f"并发加载失败: {config_file.name} - {e}")
                    return False

            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                for _ in range(20):  # 20个并发请求
                    for config_file in production_configs:
                        futures.append(executor.submit(concurrent_load_test, config_file))

                success_count = sum(1 for future in as_completed(futures) if future.result())
                total_requests = len(futures)

                if success_count / total_requests > 0.95:  # 95%成功率
                    print(f"✅ 并发访问测试通过: {success_count}/{total_requests}")
                else:
                    print(f"❌ 并发访问测试失败: {success_count}/{total_requests}")
                    return False

            print("✅ 生产部署场景测试通过")
            return True

    except Exception as e:
        print(f"❌ 生产部署场景测试失败: {e}")
        return False

def test_development_workflow_scenario():
    """测试开发工作流场景"""
    print("👨‍💻 测试开发工作流场景...")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # 场景: 开发者需要频繁修改和测试配置
            # 1. 创建开发配置
            dev_config_file = temp_path / "development_sensevoice.yaml"

            manager = ConfigurationManager()
            strategy = SenseVoiceConfigStrategy({})
            config = strategy.get_default_template()

            # 开发环境配置
            config["hardware"]["optimization_level"] = "O1"  # 更快编译
            config["performance"]["target_latency_ms"] = 200  # 宽松要求
            config["model_specific"]["sensevoice"]["beam_size"] = 1  # 更快推理

            with open(dev_config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)

            # 2. 测试配置迭代开发
            dev_manager = ConfigurationManager(dev_config_file)
            dev_manager.load_config()

            # 模拟开发过程中的配置修改
            modifications = [
                ("performance.batch_size", 2),
                ("performance.num_workers", 2),
                ("model_specific.sensevoice.confidence_threshold", 0.7),
                ("hardware.memory_limit", "4GB"),
            ]

            for key, value in modifications:
                dev_manager.set_config(key, value)

                # 每次修改后验证
                if not dev_manager.validate_config():
                    print(f"❌ 配置修改导致验证失败: {key} = {value}")
                    return False

                # 测试热重载
                dev_manager.save_config()
                time.sleep(0.1)  # 模拟文件系统延迟

                reload_manager = ConfigurationManager(dev_config_file)
                if reload_manager.load_config():
                    reloaded_value = reload_manager.get_config(key)
                    if reloaded_value != value:
                        print(f"❌ 热重载失败: {key} 期望 {value}, 得到 {reloaded_value}")
                        return False
                else:
                    print(f"❌ 热重载加载失败: {dev_config_file}")
                    return False

            # 3. 测试配置版本管理
            backup_count = 0
            for i in range(5):
                backup_path = dev_manager.create_backup(f"dev_backup_{i}")
                if backup_path and Path(backup_path).exists():
                    backup_count += 1

            if backup_count == 5:
                print("✅ 配置备份功能正常")
            else:
                print(f"❌ 配置备份功能异常: {backup_count}/5")
                return False

            # 4. 测试配置回滚
            # 修改配置到错误状态
            dev_manager.set_config("hardware.target_device", "invalid_device")
            dev_manager.save_config()

            # 验证失败状态
            reload_manager = ConfigurationManager(dev_config_file)
            try:
                if reload_manager.load_config():
                    if not reload_manager.validate_config():
                        print("✅ 错误配置验证正常工作")
                    else:
                        print("❌ 错误配置应该验证失败")
                        return False
                else:
                    print("✅ 错误配置加载失败（预期行为）")
            except Exception:
                print("✅ 错误配置异常处理正常")

            # 回滚到正常状态
            backups = dev_manager.list_backups()
            if backups:
                latest_backup = backups[-1]
                if dev_manager.rollback_to_backup(latest_backup):
                    print("✅ 配置回滚功能正常")
                else:
                    print("❌ 配置回滚失败")
                    return False
            else:
                print("❌ 没有可用的备份")
                return False

            print("✅ 开发工作流场景测试通过")
            return True

    except Exception as e:
        print(f"❌ 开发工作流场景测试失败: {e}")
        return False

def test_multi_tenant_scenario():
    """测试多租户场景"""
    print("🏢 测试多租户场景...")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # 场景: 多个用户/团队使用不同的配置
            # 1. 为不同租户创建配置
            tenants = {
                "tenant_a": {
                    "model_type": "sensevoice",
                    "hardware": {"target_device": "horizon_x5", "memory_limit": "8GB"},
                    "performance": {"target_latency_ms": 50}
                },
                "tenant_b": {
                    "model_type": "vits_cantonese",
                    "hardware": {"target_device": "horizon_x5", "memory_limit": "4GB"},
                    "performance": {"target_latency_ms": 100}
                },
                "tenant_c": {
                    "model_type": "piper_vits",
                    "hardware": {"target_device": "horizon_x5", "memory_limit": "2GB"},
                    "performance": {"target_latency_ms": 200}
                }
            }

            tenant_configs = {}
            for tenant_name, tenant_config in tenants.items():
                config_file = temp_path / f"{tenant_name}_config.yaml"

                if tenant_config["model_type"] == "sensevoice":
                    strategy = SenseVoiceConfigStrategy({})
                elif tenant_config["model_type"] == "vits_cantonese":
                    strategy = VITSCantoneseConfigStrategy({})
                else:
                    strategy = PiperVITSConfigStrategy({})

                base_config = strategy.get_default_template()

                # 应用租户特定配置
                for section, values in tenant_config.items():
                    if section != "model_type":
                        if section not in base_config:
                            base_config[section] = {}
                        base_config[section].update(values)

                # 添加租户标识
                base_config["project"]["name"] = f"{tenant_name}_model"
                base_config["project"]["tenant"] = tenant_name

                with open(config_file, 'w') as f:
                    yaml.dump(base_config, f, default_flow_style=False, indent=2)

                tenant_configs[tenant_name] = config_file
                print(f"✅ 租户配置创建: {tenant_name}")

            # 2. 测试租户隔离
            def tenant_config_test(tenant_name, config_file):
                try:
                    manager = ConfigurationManager(config_file)
                    manager.load_config()

                    # 验证租户标识
                    tenant_id = manager.get_config("project.tenant")
                    if tenant_id != tenant_name:
                        print(f"❌ 租户标识错误: 期望 {tenant_name}, 得到 {tenant_id}")
                        return False

                    # 验证租户特定配置
                    model_type = manager.get_config("project.model_type")
                    expected_model = tenants[tenant_name]["model_type"]
                    if model_type != expected_model:
                        print(f"❌ 模型类型错误: 期望 {expected_model}, 得到 {model_type}")
                        return False

                    return True

                except Exception as e:
                    print(f"❌ 租户配置测试失败 {tenant_name}: {e}")
                    return False

            # 并发测试所有租户配置
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {
                    executor.submit(tenant_config_test, tenant_name, config_file): tenant_name
                    for tenant_name, config_file in tenant_configs.items()
                }

                success_count = 0
                for future in as_completed(futures):
                    tenant_name = futures[future]
                    if future.result():
                        success_count += 1
                        print(f"✅ 租户测试通过: {tenant_name}")
                    else:
                        print(f"❌ 租户测试失败: {tenant_name}")

            if success_count == len(tenants):
                print("✅ 所有租户隔离测试通过")
            else:
                print(f"❌ 租户隔离测试失败: {success_count}/{len(tenants)}")
                return False

            # 3. 测试租户配置更新
            for tenant_name, config_file in tenant_configs.items():
                manager = ConfigurationManager(config_file)
                manager.load_config()

                # 租户特定的配置更新
                if tenant_name == "tenant_a":
                    manager.set_config("performance.target_latency_ms", 30)  # 更严格的要求
                elif tenant_name == "tenant_b":
                    manager.set_config("model_specific.vits_cantonese.use_fast_synthesis", True)
                elif tenant_name == "tenant_c":
                    manager.set_config("hardware.optimization_level", "O1")  # 资源受限

                if manager.validate_config():
                    manager.save_config()
                    print(f"✅ 租户配置更新成功: {tenant_name}")
                else:
                    print(f"❌ 租户配置更新失败: {tenant_name}")
                    return False

            print("✅ 多租户场景测试通过")
            return True

    except Exception as e:
        print(f"❌ 多租户场景测试失败: {e}")
        return False

def test_disaster_recovery_scenario():
    """测试灾难恢复场景"""
    print("🆘 测试灾难恢复场景...")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # 场景: 配置文件损坏或丢失时的恢复
            # 1. 创建正常配置并备份
            config_file = temp_path / "critical_config.yaml"
            backup_dir = temp_path / "backups"
            backup_dir.mkdir(exist_ok=True)

            manager = ConfigurationManager(config_file)
            strategy = SenseVoiceConfigStrategy({})
            config = strategy.get_default_template()

            # 设置重要配置
            config["project"]["name"] = "critical_production_model"
            config["hardware"]["target_device"] = "horizon_x5"
            config["performance"]["target_latency_ms"] = 25

            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)

            # 加载并创建多个备份
            manager.load_config()
            backups = []
            for i in range(3):
                backup_path = manager.create_backup(f"critical_backup_{i}")
                backups.append(backup_path)
                time.sleep(0.1)  # 确保时间戳不同

            print(f"✅ 创建了 {len(backups)} 个备份")

            # 2. 模拟配置文件损坏
            with open(config_file, 'w') as f:
                f.write("invalid: yaml: content: [")

            # 3. 测试损坏检测
            damaged_manager = ConfigurationManager(config_file)
            try:
                damaged_manager.load_config()
                print("❌ 损坏的配置文件应该加载失败")
                return False
            except Exception:
                print("✅ 损坏配置文件检测正常")

            # 4. 测试从备份恢复
            recovery_success = False
            for backup_path in backups:
                try:
                    if manager.rollback_to_backup(backup_path):
                        # 验证恢复的配置
                        recovery_manager = ConfigurationManager(config_file)
                        recovery_manager.load_config()

                        if recovery_manager.validate_config():
                            project_name = recovery_manager.get_config("project.name")
                            if project_name == "critical_production_model":
                                recovery_success = True
                                print(f"✅ 从备份恢复成功: {Path(backup_path).name}")
                                break
                except Exception as e:
                    print(f"恢复失败 {backup_path}: {e}")
                    continue

            if not recovery_success:
                print("❌ 灾难恢复失败")
                return False

            # 5. 测试配置完整性验证
            final_manager = ConfigurationManager(config_file)
            final_manager.load_config()

            # 验证关键配置项
            critical_checks = [
                ("project.name", "critical_production_model"),
                ("hardware.target_device", "horizon_x5"),
                ("performance.target_latency_ms", 25),
                ("project.model_type", "sensevoice")
            ]

            for key, expected_value in critical_checks:
                actual_value = final_manager.get_config(key)
                if actual_value != expected_value:
                    print(f"❌ 配置完整性检查失败: {key} 期望 {expected_value}, 得到 {actual_value}")
                    return False

            print("✅ 配置完整性验证通过")

            # 6. 测试恢复后功能正常
            if final_manager.validate_config():
                print("✅ 恢复后配置验证正常")
            else:
                print("❌ 恢复后配置验证失败")
                return False

            print("✅ 灾难恢复场景测试通过")
            return True

    except Exception as e:
        print(f"❌ 灾难恢复场景测试失败: {e}")
        return False

def test_configuration_migration_scenario():
    """测试配置迁移场景"""
    print("🔄 测试配置迁移场景...")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # 场景: 从旧版本配置迁移到新版本
            # 1. 创建旧版本配置 (模拟v1.0)
            old_config_file = temp_path / "old_version_config.yaml"

            old_config = {
                "project": {
                    "name": "legacy_model",
                    "model_type": "sensevoice",
                    "version": "1.0.0"
                },
                "hardware": {
                    "target_device": "horizon_x5"
                    # 缺少新版本的字段
                },
                "conversion_params": {
                    "input_format": "onnx",
                    "output_format": "bpu"
                    # 缺少新版本的字段
                },
                # 缺少model_specific、performance等新版本字段
            }

            with open(old_config_file, 'w') as f:
                yaml.dump(old_config, f, default_flow_style=False, indent=2)

            # 2. 测试旧配置加载（应该向后兼容）
            old_manager = ConfigurationManager(old_config_file)
            if old_manager.load_config():
                print("✅ 旧版本配置加载成功（向后兼容）")
            else:
                print("❌ 旧版本配置加载失败")
                return False

            # 3. 创建新版本配置模板
            new_config_file = temp_path / "new_version_config.yaml"
            new_manager = ConfigurationManager()
            strategy = SenseVoiceConfigStrategy({})
            new_config = strategy.get_default_template()

            # 保留旧配置的关键设置
            new_config["project"]["name"] = old_config["project"]["name"]
            new_config["hardware"]["target_device"] = old_config["hardware"]["target_device"]
            new_config["conversion_params"]["input_format"] = old_config["conversion_params"]["input_format"]
            new_config["conversion_params"]["output_format"] = old_config["conversion_params"]["output_format"]

            with open(new_config_file, 'w') as f:
                yaml.dump(new_config, f, default_flow_style=False, indent=2)

            # 4. 验证新配置
            new_manager = ConfigurationManager(new_config_file)
            if new_manager.load_config() and new_manager.validate_config():
                print("✅ 新版本配置创建和验证成功")
            else:
                print("❌ 新版本配置验证失败")
                return False

            # 5. 测试配置对比
            def compare_config_features(old_config, new_config):
                """对比配置功能差异"""
                old_features = set()
                new_features = set()

                def extract_features(config, prefix=""):
                    for key, value in config.items():
                        feature_key = f"{prefix}.{key}" if prefix else key
                        if isinstance(value, dict):
                            extract_features(value, feature_key)
                        else:
                            if prefix == "":
                                old_features.add(feature_key) if prefix == "" else new_features.add(feature_key)

                extract_features(old_config)
                extract_features(new_config)

                return old_features, new_features

            old_features, new_features = compare_config_features(old_config, new_config)

            # 新版本应该有更多功能
            if len(new_features) > len(old_features):
                print(f"✅ 新版本功能增加: {len(new_features) - len(old_features)} 个新功能")
            else:
                print("⚠️ 新版本功能没有明显增加")

            # 6. 测试迁移脚本逻辑
            def migrate_config(old_config_path, new_config_path):
                """模拟配置迁移逻辑"""
                # 加载旧配置
                with open(old_config_path, 'r') as f:
                    old_config = yaml.safe_load(f)

                # 创建新配置模板
                strategy = SenseVoiceConfigStrategy({})
                new_config = strategy.get_default_template()

                # 迁移兼容字段
                migration_map = {
                    "project.name": "project.name",
                    "project.model_type": "project.model_type",
                    "hardware.target_device": "hardware.target_device",
                    "conversion_params.input_format": "conversion_params.input_format",
                    "conversion_params.output_format": "conversion_params.output_format"
                }

                for old_path, new_path in migration_map.items():
                    old_parts = old_path.split('.')
                    new_parts = new_path.split('.')

                    # 获取旧配置值
                    value = old_config
                    for part in old_parts:
                        if part in value:
                            value = value[part]
                        else:
                            value = None
                            break

                    if value is not None:
                        # 设置到新配置
                        target = new_config
                        for part in new_parts[:-1]:
                            if part not in target:
                                target[part] = {}
                            target = target[part]
                        target[new_parts[-1]] = value

                # 保存新配置
                with open(new_config_path, 'w') as f:
                    yaml.dump(new_config, f, default_flow_style=False, indent=2)

                return True

            # 测试迁移功能
            migrated_config_file = temp_path / "migrated_config.yaml"
            if migrate_config(old_config_file, migrated_config_file):
                print("✅ 配置迁移功能正常")
            else:
                print("❌ 配置迁移功能失败")
                return False

            # 验证迁移结果
            migrated_manager = ConfigurationManager(migrated_config_file)
            if migrated_manager.load_config() and migrated_manager.validate_config():
                print("✅ 迁移后配置验证成功")
            else:
                print("❌ 迁移后配置验证失败")
                return False

            print("✅ 配置迁移场景测试通过")
            return True

    except Exception as e:
        print(f"❌ 配置迁移场景测试失败: {e}")
        return False

def test_edge_cases_and_error_handling():
    """测试边界情况和错误处理"""
    print("⚠️ 测试边界情况和错误处理...")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # 测试1: 空配置文件
            empty_config_file = temp_path / "empty.yaml"
            empty_config_file.write_text("")

            empty_manager = ConfigurationManager(empty_config_file)
            try:
                empty_manager.load_config()
                print("❌ 空配置文件应该加载失败")
                return False
            except Exception:
                print("✅ 空配置文件错误处理正常")

            # 测试2: 格式错误的YAML
            malformed_yaml_file = temp_path / "malformed.yaml"
            malformed_yaml_file.write_text("invalid: yaml: content: [")

            malformed_manager = ConfigurationManager(malformed_yaml_file)
            try:
                malformed_manager.load_config()
                print("❌ 格式错误的YAML应该加载失败")
                return False
            except Exception:
                print("✅ 格式错误YAML错误处理正常")

            # 测试3: 不存在的配置文件
            non_existent_file = temp_path / "non_existent.yaml"
            non_existent_manager = ConfigurationManager(non_existent_file)

            try:
                non_existent_manager.load_config()
                print("❌ 不存在的文件应该加载失败")
                return False
            except Exception:
                print("✅ 不存在文件错误处理正常")

            # 测试4: 缺少必需字段的配置
            incomplete_config_file = temp_path / "incomplete.yaml"
            incomplete_config = {
                "project": {
                    "name": "incomplete_model"
                    # 缺少model_type
                }
                # 缺少其他必需字段
            }

            with open(incomplete_config_file, 'w') as f:
                yaml.dump(incomplete_config, f)

            incomplete_manager = ConfigurationManager(incomplete_config_file)
            try:
                if incomplete_manager.load_config():
                    if not incomplete_manager.validate_config():
                        print("✅ 不完整配置验证正常失败")
                    else:
                        print("❌ 不完整配置应该验证失败")
                        return False
                else:
                    print("❌ 不完整配置加载失败")
                    return False
            except Exception:
                print("✅ 不完整配置异常处理正常")

            # 测试5: 极大配置文件
            large_config_file = temp_path / "large.yaml"
            strategy = SenseVoiceConfigStrategy({})
            large_config = strategy.get_default_template()

            # 添加大量数据
            large_config["large_data"] = {f"item_{i}": f"value_{i}" for i in range(1000)}

            with open(large_config_file, 'w') as f:
                yaml.dump(large_config, f)

            start_time = time.time()
            large_manager = ConfigurationManager(large_config_file)
            if large_manager.load_config():
                load_time = (time.time() - start_time) * 1000
                if load_time < 1000:  # 应该在1秒内加载
                    print(f"✅ 大配置文件加载正常: {load_time:.2f}ms")
                else:
                    print(f"⚠️ 大配置文件加载较慢: {load_time:.2f}ms")
            else:
                print("❌ 大配置文件加载失败")
                return False

            # 测试6: 特殊字符和Unicode
            unicode_config_file = temp_path / "unicode.yaml"
            unicode_config = {
                "project": {
                    "name": "unicode_模型_测试",
                    "description": "测试中文、日本語、한국어、العربية",
                    "tags": ["标签1", "标签2", "🎯", "🚀", "⭐"]
                },
                "hardware": {
                    "target_device": "horizon_x5"
                },
                "conversion_params": {
                    "input_format": "onnx",
                    "output_format": "bpu"
                },
                "model_specific": {
                    "sensevoice": {
                        "sample_rate": 16000,
                        "audio_length": 30,
                        "vocab_size": 10000
                    }
                }
            }

            with open(unicode_config_file, 'w', encoding='utf-8') as f:
                yaml.dump(unicode_config, f, default_flow_style=False, indent=2, allow_unicode=True)

            unicode_manager = ConfigurationManager(unicode_config_file)
            if unicode_manager.load_config() and unicode_manager.validate_config():
                retrieved_name = unicode_manager.get_config("project.name")
                if retrieved_name == "unicode_模型_测试":
                    print("✅ Unicode配置处理正常")
                else:
                    print(f"❌ Unicode配置处理失败: {retrieved_name}")
                    return False
            else:
                print("❌ Unicode配置验证失败")
                return False

            print("✅ 边界情况和错误处理测试通过")
            return True

    except Exception as e:
        print(f"❌ 边界情况和错误处理测试失败: {e}")
        return False

def run_all_real_world_tests():
    """运行所有实际场景测试"""
    print("🌍 运行实际场景测试套件")
    print("=" * 80)

    tests = [
        ("生产部署场景", test_production_deployment_scenario),
        ("开发工作流场景", test_development_workflow_scenario),
        ("多租户场景", test_multi_tenant_scenario),
        ("灾难恢复场景", test_disaster_recovery_scenario),
        ("配置迁移场景", test_configuration_migration_scenario),
        ("边界情况和错误处理", test_edge_cases_and_error_handling)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{'='*20}")
        print(f"测试: {test_name}")
        print(f"{'='*20}")

        start_time = time.time()
        try:
            if test_func():
                passed += 1
                test_time = time.time() - start_time
                print(f"✅ {test_name}: PASSED ({test_time:.2f}s)")
            else:
                test_time = time.time() - start_time
                print(f"❌ {test_name}: FAILED ({test_time:.2f}s)")
        except Exception as e:
            test_time = time.time() - start_time
            print(f"❌ {test_name}: ERROR ({test_time:.2f}s) - {e}")

    print(f"\n{'='*80}")
    print(f"实际场景测试结果: {passed}/{total} 测试通过")

    if passed == total:
        print("🎉 所有实际场景测试通过！配置管理系统在真实环境中表现稳定。")
        return True
    else:
        print(f"⚠️ {total - passed} 个测试失败。需要进一步优化。")
        return False

if __name__ == "__main__":
    success = run_all_real_world_tests()
    sys.exit(0 if success else 1)