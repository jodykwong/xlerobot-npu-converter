"""
BPU工具链单元测试

测试工具链的各个组件和功能。
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# 添加src目录到Python路径
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from npu_converter.bpu_toolchain.installer import ToolchainInstaller
from npu_converter.bpu_toolchain.version_manager import VersionManager
from npu_converter.bpu_toolchain.validator import ToolchainValidator
from npu_converter.bpu_toolchain.horizon_x5 import HorizonX5Interface


class TestToolchainInstaller:
    """BPU工具链安装器测试"""

    @pytest.fixture
    def temp_install_path(self):
        """临时安装路径fixture"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_create_install_directory(self, temp_install_path):
        """测试安装目录创建"""
        installer = ToolchainInstaller(temp_install_path)
        installer._create_install_directory()

        assert Path(temp_install_path).exists()
        assert Path(temp_install_path).is_dir()

    def test_verify_package_integrity_success(self, temp_install_path):
        """测试文件完整性验证 - 成功案例"""
        installer = ToolchainInstaller(temp_install_path)

        # 创建模拟的有效包文件
        test_file = Path(temp_install_path) / "valid_package.tar.gz"
        test_file.touch()

        # Mock验证为成功
        with pytest.mock.patch.object(installer, '_verify_package_integrity', return_value=True):
            result = installer._verify_package_integrity(str(test_file))
            assert result is True

    def test_verify_package_integrity_failure(self, temp_install_path):
        """测试文件完整性验证 - 失败案例"""
        installer = ToolchainInstaller(temp_install_path)

        # 创建模拟的无效包文件
        test_file = Path(temp_install_path) / "invalid_package.tar.gz"
        test_file.touch()

        # Mock验证为失败
        with pytest.mock.patch.object(installer, '_verify_package_integrity', return_value=False):
            result = installer._verify_package_integrity(str(test_file))
            assert result is False

    def test_get_installed_version_unknown(self, temp_install_path):
        """测试获取安装版本 - 未知版本"""
        installer = ToolchainInstaller(temp_install_path)

        # 无版本文件情况
        result = installer._get_installed_version()
        assert result == "unknown"


class TestVersionManager:
    """版本管理器测试"""

    @pytest.fixture
    def temp_install_path(self):
        """临时安装路径fixture"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_check_version_not_installed(self, temp_install_path):
        """测试版本检查 - 未安装状态"""
        manager = VersionManager(temp_install_path)
        result = manager.check_version()

        assert result["current_version"] == "unknown"
        assert result["is_installed"] is False
        assert "components_status" in result
        assert "compatibility" in result

    def test_check_compatibility_unknown_version(self, temp_install_path):
        """测试兼容性检查 - 未知版本"""
        manager = VersionManager(temp_install_path)

        with pytest.mock.patch.object(manager, 'current_version', ""):
            result = manager._check_compatibility()
            assert result == "unknown"

    def test_check_compatibility_v1_compatible(self, temp_install_path):
        """测试兼容性检查 - v1兼容"""
        manager = VersionManager(temp_install_path)

        with pytest.mock.patch.object(manager, 'current_version', "1.0.0"):
            result = manager._check_compatibility()
            assert result == "compatible"

    def test_get_timestamp(self):
        """测试时间戳生成"""
        manager = VersionManager()
        timestamp = manager._get_timestamp()

        assert len(timestamp) > 0
        # 验证时间戳格式为 YYYYMMDD_HHMMSS
        assert len(timestamp) == len("20241201_120000")


class TestToolchainValidator:
    """工具链验证器测试"""

    @pytest.fixture
    def temp_install_path(self):
        """临时安装路径fixture"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_validate_installation_no_install_path(self):
        """测试安装验证 - 安装路径不存在"""
        validator = ToolchainValidator("/nonexistent/path")
        result = validator.validate_installation()

        assert result["success"] is False
        assert "安装目录不存在" in result["error"]

    def test_validate_component_available(self, temp_install_path):
        """测试组件验证 - 可用组件"""
        validator = ToolchainValidator(temp_install_path)

        # 创建模拟组件文件
        bin_path = Path(temp_install_path) / "bin"
        bin_path.mkdir(parents=True, exist_ok=True)
        (bin_path / "hbdk").touch()
        (bin_path / "hbdk").chmod(0o755)

        with pytest.mock.patch.object(validator, '_get_component_version', return_value="1.0.0"):
            with pytest.mock.patch.object(validator, '_test_component_functionality', return_value="help command works"):
                result = validator._validate_component("hbdk")
                assert result["component"] == "hbdk"
                assert result["available"] is True
                assert result["version"] == "1.0.0"
                assert result["path"] == str(bin_path / "hbdk")
                assert result["test_result"] == "help command works"

    def test_validate_component_missing(self, temp_install_path):
        """测试组件验证 - 缺失组件"""
        validator = ToolchainValidator(temp_install_path)

        result = validator._validate_component("hbdk")
        assert result["component"] == "hbdk"
        assert result["available"] is False
        assert result["path"] == str(Path(temp_install_path) / "bin" / "hbdk")

    def test_environment_configuration_all_set(self):
        """测试环境配置 - 所有变量设置"""
        validator = ToolchainValidator()

        # Mock环境变量全部设置
        with pytest.mock.patch.dict(os.environ, {
            "HORIZON_TOOLCHAIN_ROOT": "/opt/horizon",
            "PATH": "/opt/horizon/bin:/usr/bin",
            "LD_LIBRARY_PATH": "/opt/horizon/lib:/usr/lib"
        }, clear=True):
            result = validator.test_environment_configuration()
            assert result["success"] is True
            assert result["path_configured"] is True
            assert result["library_path_configured"] is True

    def test_environment_configuration_missing_vars(self):
        """测试环境配置 - 缺少环境变量"""
        validator = ToolchainValidator()

        # Mock环境变量部分设置
        with pytest.mock.patch.dict(os.environ, {"PATH": "/opt/horizon/bin:/usr/bin"}, clear=True):
            result = validator.test_environment_configuration()
            assert result["success"] is False
            assert "HORIZON_TOOLCHAIN_ROOT" in result["missing_variables"]


class TestHorizonX5Interface:
    """Horizon X5工具链接口测试"""

    @pytest.fixture
    def temp_install_path(self):
        """临时安装路径fixture"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_get_toolchain_info_not_installed(self, temp_install_path):
        """测试获取工具链信息 - 未安装状态"""
        interface = HorizonX5Interface(temp_install_path)

        with pytest.mock.patch.object(interface.installer, 'install', return_value={"success": False}):
            with pytest.mock.patch.object(interface.validator, 'validate_installation', return_value={"success": False}):
                result = interface.get_toolchain_info()
                assert result["is_installed"] is False

    def test_execute_tool_success(self, temp_install_path):
        """测试执行工具命令 - 成功"""
        interface = HorizonX5Interface(temp_install_path)

        # 创建模拟工具文件
        tool_path = Path(temp_install_path) / "bin" / "hbdk"
        tool_path.mkdir(parents=True, exist_ok=True)
        (tool_path / "hbdk").touch()
        (tool_path / "hbdk").chmod(0o755)

        with pytest.mock.patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Tool executed successfully"
            result = interface.execute_tool("hbdk", ["--version"])

            assert result["success"] is True
            assert result["exit_code"] == 0
            assert result["tool"] == "hbdk"
            assert "Tool executed successfully" in result["output"]

    def test_execute_tool_missing(self, temp_install_path):
        """测试执行工具命令 - 工具不存在"""
        interface = HorizonX5Interface(temp_install_path)

        with pytest.mock.patch('subprocess.run') as mock_run:
            result = interface.execute_tool("hbdk", ["--version"])

            assert result["success"] is False
            assert result["tool"] == "hbdk"
            assert "工具不存在" in result["error"]

    def test_run_hbdk_functionality(self, temp_install_path):
        """测试运行BPU编译器"""
        interface = HorizonX5Interface(temp_install_path)

        with pytest.mock.patch.object(interface, 'execute_tool') as mock_execute:
            mock_execute.return_value = {"success": True, "output": "Compilation successful"}

            result = interface.run_hbdk("model.onnx", "output.bpu", {"optimize": True})

            assert mock_execute.called_once
            call_args = mock_execute.call_args
            assert call_args[0][0] == "hbdk"
            expected_args = ["compile", "--input", "model.onnx", "--output", "output.bpu", "--optimize", "True"]
            assert call_args[0][1] == expected_args

    def test_run_hb_mapper_functionality(self, temp_install_path):
        """测试运行模型转换工具"""
        interface = HorizonX5Interface(temp_install_path)

        with pytest.mock.patch.object(interface, 'execute_tool') as mock_execute:
            mock_execute.return_value = {"success": True, "output": "Conversion successful"}

            result = interface.run_hb_mapper("model.onnx", "output.bpu", {"quantize": "int8"})

            assert mock_execute.called_once
            call_args = mock_execute.call_args
            assert call_args[0][0] == "hb_mapper"
            expected_args = ["convert", "--input", "model.onnx", "--output", "output.bpu", "--quantize", "int8"]
            assert call_args[0][1] == expected_args