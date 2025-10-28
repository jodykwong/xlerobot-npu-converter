"""
Horizon X5 BPU工具链接口单元测试 - Story 1.8 Subtask 1.5

测试BPU工具链调用接口的工具链管理、命令执行和错误处理功能。
遵循pytest 7.x框架和AAA测试模式。
"""

import pytest
import subprocess
import tempfile
import os
from unittest.mock import patch, MagicMock, Mock
from pathlib import Path
import sys

# 添加项目路径到sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from npu_converter.bpu_toolchain.horizon_x5 import HorizonX5Interface
    from npu_converter.bpu_toolchain.installer import ToolchainInstaller
    from npu_converter.bpu_toolchain.version_manager import VersionManager
    from npu_converter.bpu_toolchain.validator import ToolchainValidator
except ImportError as e:
    pytest.skip(f"无法导入Horizon X5模块: {e}", allow_module_level=True)


class TestHorizonX5Interface:
    """HorizonX5Interface测试类"""

    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建临时目录用于测试
        self.temp_dir = tempfile.mkdtemp()
        self.install_path = self.temp_dir
        self.interface = HorizonX5Interface(self.install_path)

    def teardown_method(self):
        """每个测试方法后的清理"""
        # 清理临时目录
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_interface_initialization(self):
        """测试接口初始化"""
        interface = HorizonX5Interface("/opt/horizon")

        assert interface.install_path == Path("/opt/horizon")
        assert hasattr(interface, 'installer')
        assert hasattr(interface, 'version_manager')
        assert hasattr(interface, 'validator')
        assert isinstance(interface.installer, ToolchainInstaller)
        assert isinstance(interface.version_manager, VersionManager)
        assert isinstance(interface.validator, ToolchainValidator)

    def test_interface_initialization_default_path(self):
        """测试接口使用默认路径初始化"""
        interface = HorizonX5Interface()

        assert interface.install_path == Path("/opt/horizon")

    @patch('npu_converter.bpu_toolchain.horizon_x5.ToolchainInstaller')
    @patch('npu_converter.bpu_toolchain.horizon_x5.VersionManager')
    @patch('npu_converter.bpu_toolchain.horizon_x5.ToolchainValidator')
    def test_interface_initialization_with_dependencies(self, mock_validator, mock_version_manager, mock_installer):
        """测试接口初始化依赖注入"""
        installer_path = Path("/custom/horizon")
        interface = HorizonX5Interface(str(installer_path))

        mock_installer.assert_called_once_with(installer_path)
        mock_version_manager.assert_called_once_with(installer_path)
        mock_validator.assert_called_once_with(installer_path)

    @patch('npu_converter.bpu_toolchain.horizon_x5.ToolchainInstaller')
    def test_get_toolchain_info_success(self, mock_installer_class):
        """测试获取工具链信息成功"""
        # 模拟installer
        mock_installer = MagicMock()
        mock_installer_class.return_value = mock_installer
        mock_installer.install.return_value = {
            "status": "success",
            "installed": True
        }

        interface = HorizonX5Interface(self.install_path)
        info = interface.get_toolchain_info()

        assert isinstance(info, dict)
        assert "install_path" in info
        assert "is_installed" in info
        assert "version" in info
        assert "components" in info
        assert "installation_status" in info
        assert "validation_status" in info
        assert info["install_path"] == self.install_path

    @patch('npu_converter.bpu_toolchain.horizon_x5.ToolchainInstaller')
    def test_get_toolchain_info_not_installed(self, mock_installer_class):
        """测试获取工具链信息-未安装"""
        mock_installer = MagicMock()
        mock_installer_class.return_value = mock_installer
        mock_installer.install.return_value = {
            "status": "not_installed",
            "installed": False
        }

        interface = HorizonX5Interface(self.install_path)
        info = interface.get_toolchain_info()

        assert info["is_installed"] is False
        assert info["installation_status"]["installed"] is False

    @patch('npu_converter.bpu_toolchain.horizon_x5.ToolchainInstaller')
    def test_get_toolchain_info_installer_exception(self, mock_installer_class):
        """测试获取工具链信息-安装器异常"""
        mock_installer = MagicMock()
        mock_installer_class.return_value = mock_installer
        mock_installer.install.side_effect = Exception("安装器错误")

        interface = HorizonX5Interface(self.install_path)
        info = interface.get_toolchain_info()

        assert info["is_installed"] is False
        assert "installation_status" in info

    @patch('subprocess.run')
    def test_run_hbdk_success(self, mock_subprocess):
        """测试运行hbdk命令成功"""
        # 模拟subprocess成功返回
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "hbdk output"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        interface = HorizonX5Interface(self.install_path)
        result = interface.run_hbdk("model.onnx", "output_dir")

        assert result is True
        mock_subprocess.assert_called_once()
        # 验证调用参数
        call_args = mock_subprocess.call_args[0][0]
        assert "hbdk" in " ".join(call_args)
        assert "model.onnx" in " ".join(call_args)
        assert "output_dir" in " ".join(call_args)

    @patch('subprocess.run')
    def test_run_hbdk_failure(self, mock_subprocess):
        """测试运行hbdk命令失败"""
        # 模拟subprocess失败返回
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "hbdk error"
        mock_subprocess.return_value = mock_result

        interface = HorizonX5Interface(self.install_path)
        result = interface.run_hbdk("model.onnx", "output_dir")

        assert result is False

    @patch('subprocess.run')
    def test_run_hbdk_subprocess_exception(self, mock_subprocess):
        """测试运行hbdk命令subprocess异常"""
        mock_subprocess.side_effect = subprocess.SubprocessError("subprocess error")

        interface = HorizonX5Interface(self.install_path)
        result = interface.run_hbdk("model.onnx", "output_dir")

        assert result is False

    @patch('subprocess.run')
    def test_run_hb_mapper_success(self, mock_subprocess):
        """测试运行hb_mapper命令成功"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "hb_mapper output"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        interface = HorizonX5Interface(self.install_path)
        result = interface.run_hb_mapper("model.onnx", "model.bpu", "config.yaml")

        assert result is True
        call_args = mock_subprocess.call_args[0][0]
        assert "hb_mapper" in " ".join(call_args)
        assert "model.onnx" in " ".join(call_args)
        assert "model.bpu" in " ".join(call_args)
        assert "config.yaml" in " ".join(call_args)

    @patch('subprocess.run')
    def test_run_hb_mapper_with_options(self, mock_subprocess):
        """测试运行hb_mapper命令带选项"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "hb_mapper output"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        interface = HorizonX5Interface(self.install_path)
        result = interface.run_hb_mapper(
            "model.onnx",
            "model.bpu",
            "config.yaml",
            options=["--optimize", "level=2", "--verbose"]
        )

        assert result is True
        call_args = mock_subprocess.call_args[0][0]
        assert "--optimize" in " ".join(call_args)
        assert "level=2" in " ".join(call_args)
        assert "--verbose" in " ".join(call_args)

    @patch('subprocess.run')
    def test_run_hb_perf_success(self, mock_subprocess):
        """测试运行hb_perf命令成功"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Performance metrics..."
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        interface = HorizonX5Interface(self.install_path)
        result = interface.run_hb_perf("model.bpu", "test_data")

        assert result is True
        call_args = mock_subprocess.call_args[0][0]
        assert "hb_perf" in " ".join(call_args)
        assert "model.bpu" in " ".join(call_args)
        assert "test_data" in " ".join(call_args)

    @patch('subprocess.run')
    def test_run_hb_perf_failure(self, mock_subprocess):
        """测试运行hb_perf命令失败"""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Performance analysis failed"
        mock_subprocess.return_value = mock_result

        interface = HorizonX5Interface(self.install_path)
        result = interface.run_hb_perf("model.bpu", "test_data")

        assert result is False

    @patch('subprocess.run')
    def test_run_custom_command_success(self, mock_subprocess):
        """测试运行自定义命令成功"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Custom command output"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        interface = HorizonX5Interface(self.install_path)
        result = interface.run_command("custom_tool", ["--option", "value"])

        assert result is True
        call_args = mock_subprocess.call_args[0][0]
        assert "custom_tool" in call_args
        assert "--option" in call_args
        assert "value" in call_args

    def test_validate_model_file_exists(self):
        """测试验证模型文件存在"""
        # 创建测试文件
        model_file = os.path.join(self.temp_dir, "model.onnx")
        Path(model_file).touch()

        interface = HorizonX5Interface(self.install_path)
        result = interface.validate_model_file(model_file)

        assert result is True

    def test_validate_model_file_not_exists(self):
        """测试验证模型文件不存在"""
        model_file = os.path.join(self.temp_dir, "missing.onnx")

        interface = HorizonX5Interface(self.install_path)
        result = interface.validate_model_file(model_file)

        assert result is False

    def test_validate_model_file_invalid_extension(self):
        """测试验证模型文件无效扩展名"""
        # 创建错误扩展名的文件
        model_file = os.path.join(self.temp_dir, "model.txt")
        Path(model_file).touch()

        interface = HorizonX5Interface(self.install_path)
        result = interface.validate_model_file(model_file)

        assert result is False

    def test_validate_output_directory_exists(self):
        """测试验证输出目录存在"""
        # 创建测试目录
        output_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(output_dir)

        interface = HorizonX5Interface(self.install_path)
        result = interface.validate_output_directory(output_dir)

        assert result is True

    def test_validate_output_directory_not_exists(self):
        """测试验证输出目录不存在"""
        output_dir = os.path.join(self.temp_dir, "missing_output")

        interface = HorizonX5Interface(self.install_path)
        result = interface.validate_output_directory(output_dir)

        assert result is False

    def test_validate_output_directory_create_if_missing(self):
        """测试验证输出目录-缺失时创建"""
        output_dir = os.path.join(self.temp_dir, "new_output")

        interface = HorizonX5Interface(self.install_path)
        result = interface.validate_output_directory(output_dir, create_if_missing=True)

        assert result is True
        assert os.path.exists(output_dir)

    @patch('npu_converter.bpu_toolchain.horizon_x5.ToolchainValidator')
    def test_validate_toolchain_installation(self, mock_validator_class):
        """测试验证工具链安装"""
        mock_validator = MagicMock()
        mock_validator_class.return_value = mock_validator
        mock_validator.validate_installation.return_value = {
            "valid": True,
            "components": {
                "hbdk": "installed",
                "hb_mapper": "installed"
            }
        }

        interface = HorizonX5Interface(self.install_path)
        result = interface.validate_toolchain_installation()

        assert result is True
        mock_validator.validate_installation.assert_called_once()

    @patch('npu_converter.bpu_toolchain.horizon_x5.ToolchainValidator')
    def test_validate_toolchain_installation_failure(self, mock_validator_class):
        """测试验证工具链安装失败"""
        mock_validator = MagicMock()
        mock_validator_class.return_value = mock_validator
        mock_validator.validate_installation.return_value = {
            "valid": False,
            "missing_components": ["hbdk"]
        }

        interface = HorizonX5Interface(self.install_path)
        result = interface.validate_toolchain_installation()

        assert result is False

    def test_get_available_commands(self):
        """测试获取可用命令列表"""
        interface = HorizonX5Interface(self.install_path)
        commands = interface.get_available_commands()

        assert isinstance(commands, list)
        assert "hbdk" in commands
        assert "hb_mapper" in commands
        assert "hb_perf" in commands

    def test_check_command_availability(self):
        """测试检查命令可用性"""
        interface = HorizonX5Interface(self.install_path)

        # 测试存在的命令
        result = interface.check_command_availability("hbdk")
        assert isinstance(result, bool)

        # 测试不存在的命令
        result = interface.check_command_availability("nonexistent_command")
        assert result is False

    @patch('shutil.which')
    def test_check_command_availability_with_which(self, mock_which):
        """测试使用shutil.which检查命令可用性"""
        # 模拟命令存在
        mock_which.return_value = "/usr/bin/hbdk"

        interface = HorizonX5Interface(self.install_path)
        result = interface.check_command_availability("hbdk")

        assert result is True
        mock_which.assert_called_once_with("hbdk")

    def test_get_command_version(self):
        """测试获取命令版本"""
        interface = HorizonX5Interface(self.install_path)

        # 对于不存在的命令，应该返回None或空字符串
        version = interface.get_command_version("nonexistent_command")
        assert version in [None, ""]

    @patch('subprocess.run')
    def test_get_command_version_success(self, mock_subprocess):
        """测试获取命令版本成功"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "hbdk version 1.2.3"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        interface = HorizonX5Interface(self.install_path)
        version = interface.get_command_version("hbdk")

        assert version == "1.2.3"

    def test_format_command_output(self):
        """测试格式化命令输出"""
        interface = HorizonX5Interface(self.install_path)

        # 测试正常输出
        output = "Command executed successfully"
        formatted = interface.format_command_output(output, success=True)
        assert "✅" in formatted
        assert output in formatted

        # 测试错误输出
        error_output = "Command failed with error"
        formatted = interface.format_command_output(error_output, success=False)
        assert "❌" in formatted
        assert error_output in formatted

    def test_cleanup_temporary_files(self):
        """测试清理临时文件"""
        # 创建临时文件
        temp_file = os.path.join(self.temp_dir, "temp_file.txt")
        Path(temp_file).touch()

        interface = HorizonX5Interface(self.install_path)
        interface.cleanup_temporary_files([temp_file])

        assert not os.path.exists(temp_file)

    def test_cleanup_temporary_files_nonexistent(self):
        """测试清理不存在的临时文件"""
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.txt")

        interface = HorizonX5Interface(self.install_path)
        # 不应该抛出异常
        interface.cleanup_temporary_files([nonexistent_file])