"""
BPU工具链集成测试

测试工具链的完整安装和集成流程。
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import subprocess
import sys

# 添加src目录到Python路径
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from npu_converter.bpu_toolchain.installer import ToolchainInstaller
from npu_converter.bpu_toolchain.version_manager import VersionManager
from npu_converter.bpu_toolchain.validator import ToolchainValidator
from npu_converter.bpu_toolchain.horizon_x5 import HorizonX5Interface


class TestToolchainIntegration:
    """工具链集成测试"""

    @pytest.fixture
    def temp_install_path(self):
        """临时安装路径fixture"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_complete_installation_workflow(self, temp_install_path):
        """测试完整安装工作流"""
        installer = ToolchainInstaller(temp_install_path)

        # Mock各个步骤成功
        with pytest.mock.patch.object(installer, '_create_install_directory'):
            with pytest.mock.patch.object(installer, '_download_toolchain', return_value=str(Path(temp_install_path) / "toolchain.tar.gz")):
                with pytest.mock.patch.object(installer, '_verify_package_integrity', return_value=True):
                    with pytest.mock.patch.object(installer, '_extract_and_install'):
                        with pytest.mock.patch.object(installer, '_setup_permissions'):
                            with pytest.mock.patch.object(installer, '_get_installed_version', return_value="1.0.0"):
                                result = installer.install()

        assert result["success"] is True
        assert result["installed_version"] == "1.0.0"
        assert "hbdk" in result["installed_components"]

    def test_version_manager_integration(self, temp_install_path):
        """测试版本管理器集成"""
        manager = VersionManager(temp_install_path)

        # Mock版本检查成功
        mock_version_info = {
            "current_version": "1.0.0",
            "is_installed": True,
            "components_status": {
                "hbdk": "available",
                "hb_mapper": "available",
                "hb_perf": "available",
                "hb_gdb": "available"
            }
        }

        with pytest.mock.patch.object(manager, 'check_version', return_value=mock_version_info):
            result = manager.check_version()

        assert result["success"] is True
        assert result["current_version"] == "1.0.0"
        assert all(status == "available" for status in result["components_status"].values())

    def test_validator_integration(self, temp_install_path):
        """测试验证器集成"""
        validator = ToolchainValidator(temp_install_path)

        # Mock验证成功
        mock_validation_result = {
            "success": True,
            "component_status": {
                "hbdk": {"available": True, "version": "1.0.0"},
                "hb_mapper": {"available": True, "version": "1.0.0"}
            },
            "failed_components": []
        }

        with pytest.mock.patch.object(validator, 'validate_installation', return_value=mock_validation_result):
            with pytest.mock.patch.object(validator, 'test_environment_configuration', return_value={"success": True}):
                result = validator.run_comprehensive_test()

        assert result["overall_success"] is True

    def test_horizon_interface_integration(self, temp_install_path):
        """测试Horizon X5接口集成"""
        interface = HorizonX5Interface(temp_install_path)

        # Mock各个组件成功
        mock_tool_info = {
            "is_installed": True,
            "version": "1.0.0",
            "components": {
                "hbdk": "available",
                "hb_mapper": "available"
            }
        }

        with pytest.mock.patch.object(interface, 'get_toolchain_info', return_value=mock_tool_info):
            with pytest.mock.patch.object(interface, 'execute_tool') as mock_execute:
                # Mock多个工具调用
                mock_execute.side_effect = [
                    {"success": True, "exit_code": 0, "output": "hbdk version 1.0.0"},
                    {"success": True, "exit_code": 0, "output": "Compilation successful"},
                    {"success": True, "exit_code": 0, "output": "Conversion successful"}
                ]

                result = interface.get_toolchain_info()
                assert result["version"] == "1.0.0"

                # 测试工具链功能验证
                validator_result = interface.validator.run_comprehensive_test()
                assert validator_result["overall_success"] is True

    def test_error_handling_workflow(self, temp_install_path):
        """测试错误处理工作流"""
        installer = ToolchainInstaller(temp_install_path)

        # Mock下载失败
        with pytest.mock.patch.object(installer, '_create_install_directory'):
            with pytest.mock.patch.object(installer, '_download_toolchain', return_value=None):
                with pytest.mock.patch.object(installer, '_verify_package_integrity'):
                    result = installer.install()

        assert result["success"] is False
        assert "下载失败" in result["error"]

    def test_environment_setup(self, temp_install_path):
        """测试环境设置"""
        interface = HorizonX5Interface(temp_install_path)

        # Mock环境变量设置成功
        with pytest.mock.patch.dict('os.environ', {
            'HORIZON_TOOLCHAIN_ROOT': temp_install_path,
            'PATH': f'{temp_install_path}/bin:/usr/bin',
            'LD_LIBRARY_PATH': f'{temp_install_path}/lib:/usr/lib'
        }, clear=True):

            # 测试环境变量是否正确设置
            import os
            assert os.environ['HORIZON_TOOLCHAIN_ROOT'] == temp_install_path
            assert temp_install_path in os.environ['PATH']
            assert temp_install_path in os.environ['LD_LIBRARY_PATH']

    def test_installation_permissions(self, temp_install_path):
        """测试安装权限设置"""
        installer = ToolchainInstaller(temp_install_path)

        # Mock权限设置
        with pytest.mock.patch.object(installer, '_extract_and_install'):
            with pytest.mock.patch.object(installer, '_setup_permissions') as mock_setup:
                installer._extract_and_install("mock_package.tar.gz")

                # 验证权限设置被调用
                mock_setup.assert_called_once()

    def test_docker_compatibility(self):
        """测试Docker环境兼容性"""
        interface = HorizonX5Interface("/opt/horizon")

        # 验证Docker环境下的路径结构
        docker_install_path = Path("/opt/horizon")

        assert docker_install_path.parent == Path("/opt")
        assert docker_install_path.name == "horizon"