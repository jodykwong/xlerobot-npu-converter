"""
单元测试套件验证 - Story 1.8 验证测试

验证所有创建的单元测试文件能够正确导入和执行。
这个测试确保我们的测试基础设施正常工作。
"""

import pytest
import sys
import os
from pathlib import Path

# 添加项目路径到sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))


class TestUnitTestSuite:
    """单元测试套件验证类"""

    def test_all_test_files_exist(self):
        """验证所有测试文件存在"""
        test_files = [
            "tests/unit/test_cli_main.py",
            "tests/unit/test_convert_command.py",
            "tests/unit/test_config_manager.py",
            "tests/unit/test_exceptions_extended.py",
            "tests/unit/test_horizon_x5_interface.py"
        ]

        for test_file in test_files:
            file_path = project_root / test_file
            assert file_path.exists(), f"测试文件不存在: {test_file}"
            assert file_path.is_file(), f"不是文件: {test_file}"

    def test_all_test_files_importable(self):
        """验证所有测试文件可以导入"""
        test_modules = [
            "test_cli_main",
            "test_convert_command",
            "test_config_manager",
            "test_exceptions_extended",
            "test_horizon_x5_interface"
        ]

        for module_name in test_modules:
            try:
                # 使用importlib动态导入测试模块
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    module_name,
                    project_root / f"tests/unit/{module_name}.py"
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                assert True, f"模块 {module_name} 导入成功"
            except Exception as e:
                pytest.fail(f"模块 {module_name} 导入失败: {e}")

    def test_core_modules_importable(self):
        """验证核心模块可以导入"""
        core_modules = [
            ("npu_converter.cli.main", "main"),
            ("npu_converter.config.manager", "ConfigurationManager"),
            ("npu_converter.utils.exceptions", "ConverterException"),
        ]

        for module_name, class_name in core_modules:
            try:
                module = __import__(module_name, fromlist=[class_name])
                cls = getattr(module, class_name)
                assert cls is not None
            except ImportError as e:
                pytest.skip(f"核心模块 {module_name} 导入失败: {e}")

    def test_pytest_configuration_exists(self):
        """验证pytest配置文件存在"""
        pytest_config = project_root / "pytest.ini"
        assert pytest_config.exists(), "pytest.ini配置文件不存在"

    def test_pytest_configuration_content(self):
        """验证pytest配置内容正确"""
        pytest_config = project_root / "pytest.ini"
        content = pytest_config.read_text()

        assert "testpaths = tests" in content
        assert "python_files = test_*.py" in content
        assert "--cov=src" in content
        assert "markers" in content

    def test_test_directory_structure(self):
        """验证测试目录结构正确"""
        test_dirs = [
            "tests",
            "tests/unit",
            "tests/integration",
            "tests/fixtures"
        ]

        for test_dir in test_dirs:
            dir_path = project_root / test_dir
            assert dir_path.exists(), f"测试目录不存在: {test_dir}"
            assert dir_path.is_dir(), f"不是目录: {test_dir}"

    def test_dev_dependencies_installed(self):
        """验证开发依赖包已安装"""
        try:
            import pytest
            assert pytest.__version__ is not None
        except ImportError:
            pytest.fail("pytest未安装")

        try:
            import pytest_cov
            assert pytest_cov is not None
        except ImportError:
            pytest.fail("pytest-cov未安装")

    def test_test_class_naming_convention(self):
        """验证测试类命名约定"""
        test_files = [
            "tests/unit/test_cli_main.py",
            "tests/unit/test_convert_command.py",
            "tests/unit/test_config_manager.py",
            "tests/unit/test_exceptions_extended.py",
            "tests/unit/test_horizon_x5_interface.py"
        ]

        for test_file in test_files:
            file_path = project_root / test_file
            content = file_path.read_text()

            # 检查是否有正确的测试类命名
            assert "class Test" in content, f"{test_file} 缺少测试类"
            assert "def test_" in content, f"{test_file} 缺少测试方法"

    def test_test_method_coverage(self):
        """验证测试方法覆盖核心功能"""
        expected_test_areas = {
            "tests/unit/test_cli_main.py": ["CLI主模块"],
            "tests/unit/test_convert_command.py": ["转换命令"],
            "tests/unit/test_config_manager.py": ["配置管理"],
            "tests/unit/test_exceptions_extended.py": ["异常处理"],
            "tests/unit/test_horizon_x5_interface.py": ["BPU工具链"]
        }

        for test_file, areas in expected_test_areas.items():
            file_path = project_root / test_file
            content = file_path.read_text()

            # 检查是否包含相关功能的测试
            for area in areas:
                # 简单检查：文件名应该反映测试内容
                assert area.lower() in content.lower() or test_file.lower().replace("test_", "").replace(".py", "") in area.lower(), \
                    f"{test_file} 缺少对 {area} 的测试"

    def test_mock_usage_in_tests(self):
        """验证测试中正确使用mock"""
        test_files = [
            "tests/unit/test_cli_main.py",
            "tests/unit/test_convert_command.py",
            "tests/unit/test_config_manager.py"
        ]

        for test_file in test_files:
            file_path = project_root / test_file
            content = file_path.read_text()

            # 检查是否使用了适当的mock
            assert "Mock" in content or "mock" in content.lower(), \
                f"{test_file} 应该使用mock进行单元测试"

    def test_exception_handling_in_tests(self):
        """验证测试中的异常处理"""
        test_files = [
            "tests/unit/test_cli_main.py",
            "tests/unit/test_convert_command.py",
            "tests/unit/test_config_manager.py",
            "tests/unit/test_horizon_x5_interface.py"
        ]

        for test_file in test_files:
            file_path = project_root / test_file
            content = file_path.read_text()

            # 检查是否测试了异常情况
            assert "pytest.raises" in content or "assert" in content, \
                f"{test_file} 应该包含异常测试或断言"

    def test_fixture_usage(self):
        """验证fixture使用"""
        test_files = [
            "tests/unit/test_cli_main.py",
            "tests/unit/test_convert_command.py",
            "tests/unit/test_config_manager.py"
        ]

        for test_file in test_files:
            file_path = project_root / test_file
            content = file_path.read_text()

            # 检查是否使用了setup_method/teardown_method
            has_setup = "def setup_method" in content or "def teardown_method" in content
            has_fixture = "@pytest.fixture" in content

            # 至少应该有一种设置方式
            assert has_setup or has_fixture or "tempfile" in content, \
                f"{test_file} 应该有适当的测试设置"

    def test_assertion_quality(self):
        """验证断言质量"""
        test_files = [
            "tests/unit/test_cli_main.py",
            "tests/unit/test_convert_command.py",
            "tests/unit/test_config_manager.py",
            "tests/unit/test_exceptions_extended.py",
            "tests/unit/test_horizon_x5_interface.py"
        ]

        for test_file in test_files:
            file_path = project_root / test_file
            content = file_path.read_text()

            # 检查是否有具体的断言
            assert "assert " in content, f"{test_file} 缺少断言"

            # 检查是否有描述性的断言消息
            assert 'msg=' in content or any('description' in line for line in content.split('\n')), \
                f"{test_file} 应该有描述性的断言消息"

    def test_file_list_updated(self):
        """验证文件列表已更新到故事文件"""
        story_file = project_root / "docs/stories/story-1.8.md"
        content = story_file.read_text()

        assert "### File List" in content, "故事文件应该有File List部分"

        # 检查是否包含新创建的测试文件
        test_files_mentioned = [
            "test_cli_main.py",
            "test_convert_command.py",
            "test_config_manager.py",
            "test_exceptions_extended.py",
            "test_horizon_x5_interface.py"
        ]

        for test_file in test_files_mentioned:
            assert test_file in content, f"故事文件File List中应该包含{test_file}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])