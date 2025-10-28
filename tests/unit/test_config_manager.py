"""
Configuration Manager单元测试 - Story 1.8 Subtask 1.3

测试配置管理器的配置加载、验证和管理功能。
遵循pytest 7.x框架和AAA测试模式。
"""

import pytest
import yaml
import tempfile
import os
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import time

# 添加项目路径到sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from npu_converter.config.manager import ConfigurationManager, ConfigMetrics
    from npu_converter.core.models.config_model import ConfigModel
    from npu_converter.core.exceptions.config_errors import ConfigError
    from npu_converter.config.strategies.base_strategy import BaseConfigStrategy
    from npu_converter.config.strategies.sensevoice_strategy import SenseVoiceConfigStrategy
    from npu_converter.config.strategies.piper_vits_strategy import PiperVITSConfigStrategy
    from npu_converter.config.strategies.vits_cantonese_strategy import VITSCantoneseConfigStrategy
except ImportError as e:
    pytest.skip(f"无法导入ConfigurationManager: {e}", allow_module_level=True)


class TestConfigMetrics:
    """ConfigMetrics测试类"""

    def test_config_metrics_initialization(self):
        """测试ConfigMetrics初始化"""
        metrics = ConfigMetrics()

        assert metrics.load_time_ms == 0.0
        assert metrics.reload_time_ms == 0.0
        assert metrics.validation_time_ms == 0.0
        assert metrics.last_reload_timestamp is None
        assert metrics.reload_count == 0
        assert metrics.validation_failures == 0
        assert metrics.backup_count == 0
        assert metrics.recovery_success_rate == 0.0
        assert metrics.last_recovery_timestamp is None

    def test_config_metrics_with_values(self):
        """测试ConfigMetrics带值初始化"""
        current_time = time.time()
        metrics = ConfigMetrics(
            load_time_ms=100.5,
            reload_time_ms=50.2,
            validation_time_ms=25.8,
            last_reload_timestamp=current_time,
            reload_count=3,
            validation_failures=1,
            backup_count=5,
            recovery_success_rate=0.95,
            last_recovery_timestamp=current_time + 10
        )

        assert metrics.load_time_ms == 100.5
        assert metrics.reload_time_ms == 50.2
        assert metrics.validation_time_ms == 25.8
        assert metrics.last_reload_timestamp == current_time
        assert metrics.reload_count == 3
        assert metrics.validation_failures == 1
        assert metrics.backup_count == 5
        assert metrics.recovery_success_rate == 0.95
        assert metrics.last_recovery_timestamp == current_time + 10


class TestConfigurationManager:
    """ConfigurationManager测试类"""

    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建临时目录用于测试
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, 'test_config.yaml')
        self.config_manager = ConfigurationManager()

    def teardown_method(self):
        """每个测试方法后的清理"""
        # 清理临时目录
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_configuration_manager_initialization(self):
        """测试ConfigurationManager初始化"""
        manager = ConfigurationManager()

        assert hasattr(manager, 'strategies')
        assert hasattr(manager, 'metrics')
        assert hasattr(manager, 'validator')
        assert isinstance(manager.metrics, ConfigMetrics)

    def test_load_config_success(self):
        """测试配置加载成功"""
        # 创建测试配置文件
        test_config = {
            'model_type': 'sensevoice',
            'optimization': {
                'level': 2,
                'target_device': 'rdk_x5'
            },
            'validation': {
                'accuracy_threshold': 0.98
            }
        }

        with open(self.config_file, 'w') as f:
            yaml.dump(test_config, f)

        # 加载配置
        result = self.config_manager.load_config(self.config_file)

        assert result is not None
        assert isinstance(result, dict)
        assert result['model_type'] == 'sensevoice'
        assert result['optimization']['level'] == 2

    def test_load_config_file_not_found(self):
        """测试配置文件不存在"""
        non_existent_file = os.path.join(self.temp_dir, 'non_existent.yaml')

        with pytest.raises(ConfigError):
            self.config_manager.load_config(non_existent_file)

    def test_load_config_invalid_yaml(self):
        """测试无效YAML文件"""
        # 创建无效YAML文件
        with open(self.config_file, 'w') as f:
            f.write("invalid: yaml: content:\n  - unclosed: [")

        with pytest.raises(ConfigError):
            self.config_manager.load_config(self.config_file)

    def test_load_config_empty_file(self):
        """测试空配置文件"""
        # 创建空文件
        with open(self.config_file, 'w') as f:
            f.write("")

        with pytest.raises(ConfigError):
            self.config_manager.load_config(self.config_file)

    def test_validate_config_success(self):
        """测试配置验证成功"""
        # 创建有效配置
        valid_config = {
            'model_type': 'sensevoice',
            'optimization': {
                'level': 2,
                'target_device': 'rdk_x5'
            },
            'validation': {
                'accuracy_threshold': 0.98
            }
        }

        result = self.config_manager.validate_config(valid_config)
        assert result is True

    def test_validate_config_missing_required_fields(self):
        """测试配置缺少必需字段"""
        invalid_config = {
            'optimization': {
                'level': 2
            }
            # 缺少model_type字段
        }

        result = self.config_manager.validate_config(invalid_config)
        assert result is False

    def test_validate_config_invalid_values(self):
        """测试配置包含无效值"""
        invalid_config = {
            'model_type': 'invalid_model',
            'optimization': {
                'level': 10,  # 无效的优化级别
                'target_device': 'rdk_x5'
            }
        }

        result = self.config_manager.validate_config(invalid_config)
        assert result is False

    def test_get_strategy_for_sensevoice(self):
        """测试获取SenseVoice策略"""
        strategy = self.config_manager.get_strategy('sensevoice')
        assert isinstance(strategy, SenseVoiceConfigStrategy)

    def test_get_strategy_for_piper_vits(self):
        """测试获取Piper VITS策略"""
        strategy = self.config_manager.get_strategy('piper_vits')
        assert isinstance(strategy, PiperVITSConfigStrategy)

    def test_get_strategy_for_vits_cantonese(self):
        """测试获取VITS Cantonese策略"""
        strategy = self.config_manager.get_strategy('vits_cantonese')
        assert isinstance(strategy, VITSCantoneseConfigStrategy)

    def test_get_strategy_for_unknown_model(self):
        """测试获取未知模型策略"""
        strategy = self.config_manager.get_strategy('unknown_model')
        assert strategy is None

    def test_get_strategy_default(self):
        """测试获取默认策略"""
        strategy = self.config_manager.get_strategy()
        # 应该返回默认策略（可能是SenseVoice或其他）
        assert isinstance(strategy, BaseConfigStrategy)

    @patch('npu_converter.config.manager.yaml.dump')
    @patch('npu_converter.config.manager.yaml.load')
    def test_save_config_success(self, mock_yaml_load, mock_yaml_dump):
        """测试保存配置成功"""
        test_config = {
            'model_type': 'sensevoice',
            'optimization': {'level': 2}
        }

        # 模拟yaml.load返回
        mock_yaml_load.return_value = test_config

        result = self.config_manager.save_config(test_config, self.config_file)

        assert result is True
        mock_yaml_dump.assert_called_once()

    def test_save_config_invalid_path(self):
        """测试保存到无效路径"""
        invalid_path = '/invalid/path/config.yaml'
        test_config = {'model_type': 'sensevoice'}

        result = self.config_manager.save_config(test_config, invalid_path)
        assert result is False

    def test_reload_config_success(self):
        """测试重新加载配置成功"""
        # 创建初始配置
        initial_config = {
            'model_type': 'sensevoice',
            'optimization': {'level': 1}
        }

        with open(self.config_file, 'w') as f:
            yaml.dump(initial_config, f)

        # 加载初始配置
        self.config_manager.load_config(self.config_file)

        # 更新配置文件
        updated_config = {
            'model_type': 'sensevoice',
            'optimization': {'level': 3}
        }

        with open(self.config_file, 'w') as f:
            yaml.dump(updated_config, f)

        # 重新加载配置
        result = self.config_manager.reload_config()
        assert result is True
        assert self.config_manager.metrics.reload_count > 0

    def test_reload_config_no_file_loaded(self):
        """测试重新加载配置时没有已加载的文件"""
        result = self.config_manager.reload_config()
        assert result is False

    def test_get_metrics(self):
        """测试获取指标"""
        metrics = self.config_manager.get_metrics()
        assert isinstance(metrics, ConfigMetrics)

    def test_reset_metrics(self):
        """测试重置指标"""
        # 设置一些指标值
        self.config_manager.metrics.load_time_ms = 100.0
        self.config_manager.metrics.reload_count = 5

        # 重置指标
        self.config_manager.reset_metrics()

        # 验证指标已重置
        assert self.config_manager.metrics.load_time_ms == 0.0
        assert self.config_manager.metrics.reload_count == 0

    @patch('time.time')
    def test_update_metrics_load_time(self, mock_time):
        """测试更新加载时间指标"""
        mock_time.return_value = 1000.0

        start_time = 999.0
        self.config_manager._update_load_time_metrics(start_time)

        assert self.config_manager.metrics.load_time_ms == 1000.0  # (1000.0 - 999.0) * 1000

    @patch('time.time')
    def test_update_metrics_reload_time(self, mock_time):
        """测试更新重新加载时间指标"""
        mock_time.return_value = 2000.0
        self.config_manager.metrics.reload_count = 1

        start_time = 1999.0
        self.config_manager._update_reload_time_metrics(start_time)

        assert self.config_manager.metrics.reload_time_ms == 1000.0  # (2000.0 - 1999.0) * 1000
        assert self.config_manager.metrics.last_reload_timestamp == 2000.0

    def test_get_available_strategies(self):
        """测试获取可用策略列表"""
        strategies = self.config_manager.get_available_strategies()
        assert isinstance(strategies, list)
        assert len(strategies) > 0
        assert 'sensevoice' in strategies
        assert 'piper_vits' in strategies
        assert 'vits_cantonese' in strategies

    def test_register_custom_strategy(self):
        """测试注册自定义策略"""
        # 创建自定义策略
        class CustomStrategy(BaseConfigStrategy):
            def get_config_template(self):
                return {}

            def validate_config(self, config):
                return True

        custom_strategy = CustomStrategy()
        self.config_manager.register_strategy('custom_model', custom_strategy)

        # 验证策略已注册
        strategy = self.config_manager.get_strategy('custom_model')
        assert strategy is custom_strategy

    def test_merge_configs(self):
        """测试配置合并"""
        base_config = {
            'model_type': 'sensevoice',
            'optimization': {
                'level': 1,
                'target_device': 'rdk_x5'
            }
        }

        override_config = {
            'optimization': {
                'level': 3  # 只覆盖level
            },
            'validation': {  # 新增字段
                'accuracy_threshold': 0.98
            }
        }

        merged = self.config_manager.merge_configs(base_config, override_config)

        assert merged['model_type'] == 'sensevoice'  # 保持原值
        assert merged['optimization']['level'] == 3  # 被覆盖
        assert merged['optimization']['target_device'] == 'rdk_x5'  # 保持原值
        assert merged['validation']['accuracy_threshold'] == 0.98  # 新增字段

    def test_get_config_summary(self):
        """测试获取配置摘要"""
        config = {
            'model_type': 'sensevoice',
            'optimization': {'level': 2},
            'validation': {'accuracy_threshold': 0.98}
        }

        summary = self.config_manager.get_config_summary(config)
        assert isinstance(summary, str)
        assert 'sensevoice' in summary
        assert 'level: 2' in summary
        assert '0.98' in summary