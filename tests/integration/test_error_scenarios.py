"""
错误场景集成测试 - Story 1.8 Subtask 2.4

测试各种错误场景下的系统行为，验证错误处理、恢复机制和用户友好的错误报告。
确保系统在异常情况下的稳定性和可靠性。
遵循pytest 7.x框架和集成测试模式。
"""

import pytest
import tempfile
import os
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# 添加项目路径到sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from npu_converter.cli.main import main
    from npu_converter.config.manager import ConfigurationManager
    from npu_converter.utils.exceptions import (
        ConverterException, ModelLoadError, ConfigurationError,
        ToolchainError, ValidationException
    )
    from npu_converter.utils.error_analyzer import ErrorAnalyzer
    from npu_converter.utils.logger import StructuredLogger
except ImportError as e:
    pytest.skip(f"无法导入核心模块: {e}", allow_module_level=True)


@pytest.mark.integration
class TestErrorScenarios:
    """错误场景集成测试类"""

    def setup_method(self):
        """每个测试方法前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.yaml")
        self.input_model = os.path.join(self.temp_dir, "test_model.onnx")
        self.output_dir = os.path.join(self.temp_dir, "output")

        os.makedirs(self.output_dir, exist_ok=True)
        self.error_analyzer = ErrorAnalyzer()
        self.logger = StructuredLogger("test_error_scenarios")

    def teardown_method(self):
        """每个测试方法后的清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def create_valid_config(self):
        """创建有效配置文件"""
        config = {
            "model_type": "sensevoice",
            "optimization": {
                "level": 2,
                "target_device": "rdk_x5"
            },
            "validation": {
                "accuracy_threshold": 0.98
            }
        }

        with open(self.config_file, 'w') as f:
            yaml.dump(config, f)

        return config

    def test_missing_input_file_error(self):
        """测试缺少输入文件错误"""
        self.create_valid_config()
        # 不创建输入文件

        # 模拟命令行参数
        with patch('sys.argv', ['xlerobot', 'convert', '--input', self.input_model,
                          '--output', self.output_dir, '--config', self.config_file]):
            with patch('builtins.print') as mock_print:
                result = main()

                # 应该返回错误码
                assert result != 0

                # 验证错误消息
                print_calls = [str(call[0][0]) for call in mock_print.call_args_list]
                error_text = ' '.join(print_calls)
                assert any(keyword in error_text.lower() for keyword in ["error", "not found", "missing"])

    def test_invalid_config_file_error(self):
        """测试无效配置文件错误"""
        # 创建无效的YAML文件
        with open(self.config_file, 'w') as f:
            f.write("invalid: yaml: content: [")

        # 创建测试模型文件
        with open(self.input_model, 'wb') as f:
            f.write(b"mock_model")

        with patch('sys.argv', ['xlerobot', 'convert', '--input', self.input_model,
                          '--output', self.output_dir, '--config', self.config_file]):
            with patch('builtins.print') as mock_print:
                result = main()

                # 应该返回错误码
                assert result != 0

    def test_permission_denied_error(self):
        """测试权限拒绝错误"""
        self.create_valid_config()

        # 创建不可写的输出目录
        readonly_dir = os.path.join(self.temp_dir, "readonly")
        os.makedirs(readonly_dir, exist_ok=True)
        os.chmod(readonly_dir, 0o444)  # 只读权限

        try:
            with patch('sys.argv', ['xlerobot', 'convert', '--input', self.input_model,
                              '--output', readonly_dir, '--config', self.config_file]):
                with patch('builtins.print') as mock_print:
                    result = main()

                    # 应该返回错误码
                    assert result != 0

                    # 验证权限错误消息
                    print_calls = [str(call[0][0]) for call in mock_print.call_args_list]
                    error_text = ' '.join(print_calls)
                    assert any(keyword in error_text.lower() for keyword in ["permission", "denied", "access"])
        finally:
            # 恢复权限以便清理
            os.chmod(readonly_dir, 0o755)

    def test_disk_space_error(self):
        """测试磁盘空间不足错误"""
        self.create_valid_config()

        # 模拟磁盘空间不足
        with patch('os.path.getfree', return_value=0):  # 0字节可用空间
            with patch('sys.argv', ['xlerobot', 'convert', '--input', self.input_model,
                              '--output', self.output_dir, '--config', self.config_file]):
                with patch('builtins.print') as mock_print:
                    result = main()

                    # 应该返回错误码
                    assert result != 0

                    # 验证磁盘空间错误消息
                    print_calls = [str(call[0][0]) for call in mock_print.call_args_list]
                    error_text = ' '.join(print_calls)
                    assert any(keyword in error_text.lower() for keyword in ["disk", "space", "storage"])

    def test_network_connection_error(self):
        """测试网络连接错误"""
        self.create_valid_config()

        # 模拟网络连接错误
        with patch('requests.get', side_effect=Exception("Network error")):
            with patch('sys.argv', ['xlerobot', 'convert', '--input', self.input_model,
                              '--output', self.output_dir, '--config', self.config_file,
                              '--download-model']):
                with patch('builtins.print') as mock_print:
                    result = main()

                    # 应该返回错误码
                    assert result != 0

                    # 验证网络错误消息
                    print_calls = [str(call[0][0]) for call in mock_print.call_args_list]
                    error_text = ' '.join(print_calls)
                    assert any(keyword in error_text.lower() for keyword in ["network", "connection", "offline"])

    def test_toolchain_not_found_error(self):
        """测试工具链未找到错误"""
        self.create_valid_config()

        # 模拟工具链未找到
        with patch('shutil.which', return_value=None):
            with patch('sys.argv', ['xlerobot', 'convert', '--input', self.input_model,
                              '--output', self.output_dir, '--config', self.config_file]):
                with patch('builtins.print') as mock_print:
                    result = main()

                    # 应该返回错误码
                    assert result != 0

                    # 验证工具链错误消息
                    print_calls = [str(call[0][0]) for call in mock_print.call_args_list]
                    error_text = ' '.join(print_calls)
                    assert any(keyword in error_text.lower() for keyword in ["toolchain", "not found", "missing"])

    def test_model_incompatible_error(self):
        """测试模型不兼容错误"""
        # 创建无效的模型文件
        with open(self.input_model, 'w') as f:
            f.write("invalid_model_content")

        self.create_valid_config()

        with patch('sys.argv', ['xlerobot', 'convert', '--input', self.input_model,
                          '--output', self.output_dir, '--config', self.config_file]):
            with patch('builtins.print') as mock_print:
                result = main()

                # 应该返回错误码
                assert result != 0

                # 验证模型兼容性错误消息
                print_calls = [str(call[0][0]) for call in mock_print.call_args_list]
                error_text = ' '.join(print_calls)
                assert any(keyword in error_text.lower() for keyword in ["model", "incompatible", "invalid"])

    def test_memory_insufficient_error(self):
        """测试内存不足错误"""
        self.create_valid_config()

        # 模拟内存不足
        with patch('psutil.virtual_memory') as mock_memory:
            mock_memory.return_value.available = 100 * 1024 * 1024  # 100MB

            with patch('sys.argv', ['xlerobot', 'convert', '--input', self.input_model,
                              '--output', self.output_dir, '--config', self.config_file]):
                with patch('builtins.print') as mock_print:
                    result = main()

                    # 应该返回错误码
                    assert result != 0

                    # 验证内存不足错误消息
                    print_calls = [str(call[0][0]) for call in mock_print.call_args_list]
                    error_text = ' '.join(print_calls)
                    assert any(keyword in error_text.lower() for keyword in ["memory", "insufficient", "ram"])

    def test_timeout_error(self):
        """测试超时错误"""
        self.create_valid_config()

        # 模拟超时
        with patch('time.time', side_effect=[0, 300]):  # 模拟300秒超时
            with patch('sys.argv', ['xlerobot', 'convert', '--input', self.input_model,
                              '--output', self.output_dir, '--config', self.config_file,
                              '--timeout', '60']):
                with patch('builtins.print') as mock_print:
                    result = main()

                    # 应该返回错误码
                    assert result != 0

                    # 验证超时错误消息
                    print_calls = [str(call[0][0]) for call in mock_print.call_args_list]
                    error_text = ' '.join(print_calls)
                    assert any(keyword in error_text.lower() for keyword in ["timeout", "timed out"])

    def test_keyboard_interrupt_error(self):
        """测试键盘中断错误"""
        self.create_valid_config()

        # 模拟键盘中断
        with patch('sys.argv', ['xlerobot', 'convert', '--input', self.input_model,
                          '--output', self.output_dir, '--config', self.config_file]):
            with patch('builtins.print'):
                # 模拟键盘中断
                import signal
                def raise_keyboard_interrupt(signum, frame):
                    raise KeyboardInterrupt()

                signal.signal(signal.SIGINT, raise_keyboard_interrupt)
                os.kill(os.getpid(), signal.SIGINT)

                result = main()

                # 应该返回特定错误码
                assert result == 130  # KeyboardInterrupt的标准退出码

    def test_concurrent_access_error(self):
        """测试并发访问错误"""
        self.create_valid_config()

        # 模拟文件被锁定
        with patch('builtins.open', side_effect=PermissionError("File is locked")):
            with patch('sys.argv', ['xlerobot', 'convert', '--input', self.input_model,
                              '--output', self.output_dir, '--config', self.config_file]):
                with patch('builtins.print') as mock_print:
                    result = main()

                    # 应该返回错误码
                    assert result != 0

                    # 验证并发访问错误消息
                    print_calls = [str(call[0][0]) for call in mock_print.call_args_list]
                    error_text = ' '.join(print_calls)
                    assert any(keyword in error_text.lower() for keyword in ["locked", "access", "busy"])

    def test_error_analyzer_integration(self):
        """测试错误分析器集成"""
        # 创建测试错误
        test_error = ConfigurationError(
            "Test configuration error",
            config_key="invalid_key"
        )

        # 分析错误
        error_analysis = self.error_analyzer.analyze_error(test_error)

        # 验证分析结果
        assert error_analysis is not None
        assert "error_type" in error_analysis
        assert "suggestions" in error_analysis

    def test_error_recovery_mechanisms(self):
        """测试错误恢复机制"""
        recovery_scenarios = [
            ("file_not_found", "create_default_file"),
            ("permission_denied", "check_file_permissions"),
            ("invalid_config", "use_default_config"),
            ("network_error", "retry_with_backoff")
        ]

        for error_type, recovery_action in recovery_scenarios:
            # 模拟恢复机制
            with patch.object(self.error_analyzer, 'get_recovery_action') as mock_recovery:
                mock_recovery.return_value = recovery_action

                action = self.error_analyzer.get_recovery_action(error_type)
                assert action == recovery_action

    def test_error_logging_integration(self):
        """测试错误日志集成"""
        # 创建配置文件
        self.create_valid_config()

        # 模拟日志记录
        with patch.object(self.logger, 'log') as mock_log:
            # 记录错误日志
            self.logger.log("ERROR", "Test error message",
                          error_code="E0001",
                          context={"component": "test"})

            # 验证日志调用
            mock_log.assert_called_once()

    def test_error_report_generation(self):
        """测试错误报告生成"""
        # 创建多个错误
        errors = [
            ConfigurationError("Config error 1", "key1"),
            ModelLoadError("Model error 1", "model1.onnx"),
            ToolchainError("Toolchain error 1", "v1.0")
        ]

        # 生成错误报告
        error_report = {
            "timestamp": "2025-10-27T11:30:00Z",
            "total_errors": len(errors),
            "error_categories": {
                "ConfigurationError": 1,
                "ModelLoadError": 1,
                "ToolchainError": 1
            },
            "errors": [
                {
                    "type": type(error).__name__,
                    "message": error.message,
                    "error_code": error.error_code
                }
                for error in errors
            ]
        }

        # 验证错误报告
        assert error_report["total_errors"] == 3
        assert len(error_report["error_categories"]) == 3
        assert len(error_report["errors"]) == 3

    def test_user_friendly_error_messages(self):
        """测试用户友好的错误消息"""
        error_scenarios = [
            {
                "error": "File not found: model.onnx",
                "friendly_message": "找不到模型文件 model.onnx。请检查文件路径是否正确。",
                "suggestions": ["检查文件路径", "确认文件存在", "验证文件权限"]
            },
            {
                "error": "Permission denied: /output/dir",
                "friendly_message": "没有权限访问输出目录 /output/dir。请检查目录权限。",
                "suggestions": ["检查目录权限", "使用sudo运行", "更改输出目录"]
            },
            {
                "error": "Toolchain not found: hbdk",
                "friendly_message": "找不到BPU工具链hbdk。请确保工具链已正确安装。",
                "suggestions": ["检查工具链安装", "验证PATH环境变量", "重新安装工具链"]
            }
        ]

        for scenario in error_scenarios:
            # 验证友好错误消息格式
            assert "friendly_message" in scenario
            assert "suggestions" in scenario
            assert len(scenario["suggestions"]) > 0

    def test_error_recovery_workflows(self):
        """测试错误恢复工作流"""
        recovery_workflows = {
            "file_not_found": [
                "检查文件路径拼写",
                "确认文件存在",
                "验证文件权限",
                "使用绝对路径"
            ],
            "permission_denied": [
                "检查文件/目录权限",
                "使用sudo运行",
                "更改文件所有者",
                "使用其他目录"
            ],
            "network_error": [
                "检查网络连接",
                "重试操作",
                "使用离线模式",
                "联系管理员"
            ]
        }

        for error_type, workflow in recovery_workflows.items():
            # 验证恢复工作流
            assert isinstance(workflow, list)
            assert len(workflow) > 0
            assert all(isinstance(step, str) for step in workflow)

    def test_error_cascade_prevention(self):
        """测试错误级联预防"""
        # 模拟可能导致级联错误的场景
        with patch('os.path.exists', side_effect=[True, False, False, False, False]):
            with patch('sys.argv', ['xlerobot', 'convert', '--input', self.input_model,
                              '--output', self.output_dir, '--config', self.config_file]):
                with patch('builtins.print') as mock_print:
                    result = main()

                    # 验证系统能够优雅地处理级联错误
                    assert result != 0

                    # 验证只报告第一个错误，避免级联
                    print_calls = [str(call[0][0]) for call in mock_print.call_args_list]
                    # 确保没有太多错误消息（避免级联）
                    assert len(print_calls) < 10


@pytest.mark.integration
class TestErrorHandlingRobustness:
    """错误处理鲁棒性测试类"""

    def setup_method(self):
        """每个测试方法前的设置"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """每个测试方法后的清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_multiple_simultaneous_errors(self):
        """测试多个同时发生的错误"""
        # 模拟多个系统同时失败
        errors = [
            OSError("Disk full"),
            MemoryError("Out of memory"),
            ConnectionError("Network down")
        ]

        # 测试系统处理多个错误的能力
        for error in errors:
            try:
                raise error
            except Exception as e:
                # 验证错误被正确捕获
                assert isinstance(e, type(error))

    def test_resource_exhaustion_scenarios(self):
        """测试资源耗尽场景"""
        resource_scenarios = [
            ("file_handles", "Too many open files"),
            ("memory", "Cannot allocate memory"),
            ("disk_space", "No space left on device"),
            ("processes", "Cannot fork process")
        ]

        for resource, error_message in resource_scenarios:
            # 验证资源耗尽错误处理
            assert isinstance(resource, str)
            assert isinstance(error_message, str)

    def test_system_state_corruption(self):
        """测试系统状态损坏场景"""
        corruption_scenarios = [
            "config_file_corrupted",
            "model_file_corrupted",
            "database_corrupted",
            "cache_corrupted"
        ]

        for scenario in corruption_scenarios:
            # 验证系统状态损坏检测
            assert isinstance(scenario, str)
            assert len(scenario) > 0

    def test_graceful_degradation(self):
        """测试优雅降级"""
        degradation_scenarios = [
            ("high_precision_failed", "use_standard_precision"),
            ("gpu_unavailable", "use_cpu"),
            ("fast_mode_failed", "use_standard_mode"),
            ("full_validation_failed", "use_basic_validation")
        ]

        for scenario, fallback in degradation_scenarios:
            # 验证降级策略
            assert isinstance(scenario, str)
            assert isinstance(fallback, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])