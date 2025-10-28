"""
Horizon X5 BPU工具链验证器

负责验证工具链组件的安装和功能。
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ToolchainValidator:
    """BPU工具链验证器"""

    def __init__(self, install_path: str = "/opt/horizon"):
        self.install_path = Path(install_path)
        self.components = {
            "hbdk": "BPU编译器",
            "hb_mapper": "模型转换工具",
            "hb_perf": "性能分析工具",
            "hb_gdb": "调试工具"
        }

    def validate_installation(self) -> Dict[str, Any]:
        """
        验证工具链安装状态

        Returns:
            Dict: 包含验证结果
        """
        logger.info("开始验证工具链安装...")

        result = {
            "success": False,
            "installed_path": str(self.install_path),
            "component_status": {},
            "failed_components": [],
            "error": None
        }

        try:
            # 检查安装目录
            if not self.install_path.exists():
                result["error"] = "工具链安装目录不存在"
                return result

            # 验证每个组件
            for component, description in self.components.items():
                status = self._validate_component(component)
                result["component_status"][component] = status

                if not status["available"]:
                    result["failed_components"].append(component)

            # 判断整体安装状态
            all_available = all(
                status["available"]
                for status in result["component_status"].values()
            )
            result["success"] = all_available

            if all_available:
                logger.info("所有工具链组件验证通过")
            else:
                logger.warning(f"部分组件验证失败: {result['failed_components']}")

        except Exception as e:
            logger.error(f"验证工具链安装失败: {e}")
            result["error"] = str(e)

        return result

    def _validate_component(self, component: str) -> Dict[str, Any]:
        """
        验证单个组件
        """
        status = {
            "component": component,
            "description": self.components[component],
            "available": False,
            "version": "",
            "path": "",
            "test_result": ""
        }

        try:
            component_path = self.install_path / "bin" / component
            if component_path.exists():
                status["path"] = str(component_path)
                status["available"] = True
                status["version"] = self._get_component_version(component)
                status["test_result"] = self._test_component_functionality(component)
                logger.debug(f"组件{component}验证通过: {status['version']}")
            else:
                logger.warning(f"组件{component}不存在: {component_path}")

        except Exception as e:
            logger.error(f"验证组件{component}失败: {e}")

        return status

    def _get_component_version(self, component: str) -> str:
        """获取组件版本"""
        try:
            # 尝试执行版本查询命令
            version_cmd = [str(self.install_path / "bin" / component), "--version"]
            result = subprocess.run(
                version_cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                version = result.stdout.strip()
                logger.debug(f"组件{component}版本: {version}")
                return version
            else:
                logger.warning(f"获取{component}版本失败: {result.stderr}")

        except subprocess.TimeoutExpired:
            logger.error(f"获取{component}版本超时")
        except Exception as e:
            logger.error(f"获取{component}版本异常: {e}")

        return "unknown"

    def _test_component_functionality(self, component: str) -> str:
        """测试组件基本功能"""
        try:
            # 根据不同组件执行不同的测试
            if component == "hbdk":
                return self._test_hbdk_functionality()
            elif component == "hb_mapper":
                return self._test_hb_mapper_functionality()
            elif component == "hb_perf":
                return self._test_hb_perf_functionality()
            elif component == "hb_gdb":
                return self._test_hb_gdb_functionality()
            else:
                return "no test defined"

        except Exception as e:
            logger.error(f"测试{component}功能失败: {e}")
            return f"test failed: {e}"

    def _test_hbdk_functionality(self) -> str:
        """测试BPU编译器基本功能"""
        try:
            # 执行帮助命令测试可用性
            help_cmd = [str(self.install_path / "bin" / "hbdk"), "--help"]
            result = subprocess.run(
                help_cmd,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return "help command works"
            else:
                return "help command failed"

        except subprocess.TimeoutExpired:
            return "test timeout"
        except Exception as e:
            return f"test error: {e}"

    def _test_hb_mapper_functionality(self) -> str:
        """测试模型转换工具基本功能"""
        try:
            # 执行帮助命令测试可用性
            help_cmd = [str(self.install_path / "bin" / "hb_mapper"), "--help"]
            result = subprocess.run(
                help_cmd,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return "help command works"
            else:
                return "help command failed"

        except subprocess.TimeoutExpired:
            return "test timeout"
        except Exception as e:
            return f"test error: {e}"

    def _test_hb_perf_functionality(self) -> str:
        """测试性能分析工具基本功能"""
        try:
            # 执行帮助命令测试可用性
            help_cmd = [str(self.install_path / "bin" / "hb_perf"), "--help"]
            result = subprocess.run(
                help_cmd,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return "help command works"
            else:
                return "help command failed"

        except subprocess.TimeoutExpired:
            return "test timeout"
        except Exception as e:
            return f"test error: {e}"

    def _test_hb_gdb_functionality(self) -> str:
        """测试调试工具基本功能"""
        try:
            # 执行帮助命令测试可用性
            help_cmd = [str(self.install_path / "bin" / "hb_gdb"), "--help"]
            result = subprocess.run(
                help_cmd,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return "help command works"
            else:
                return "help command failed"

        except subprocess.TimeoutExpired:
            return "test timeout"
        except Exception as e:
            return f"test error: {e}"

    def test_environment_configuration(self) -> Dict[str, Any]:
        """测试环境配置"""
        logger.info("测试环境配置...")

        result = {
            "success": False,
            "path_configured": False,
            "library_path_configured": False,
            "environment_variables": {},
            "missing_variables": [],
            "error": None
        }

        try:
            # 检查环境变量
            required_vars = ["HORIZON_TOOLCHAIN_ROOT", "PATH", "LD_LIBRARY_PATH"]
            for var in required_vars:
                value = os.environ.get(var)
                result["environment_variables"][var] = value
                if not value:
                    result["missing_variables"].append(var)

            # 验证PATH是否包含工具链路径
            if "PATH" in os.environ:
                toolchain_bin = str(self.install_path / "bin")
                if toolchain_bin in os.environ["PATH"]:
                    result["path_configured"] = True

            # 验证LD_LIBRARY_PATH是否包含工具链库路径
            if "LD_LIBRARY_PATH" in os.environ:
                toolchain_lib = str(self.install_path / "lib")
                if toolchain_lib in os.environ["LD_LIBRARY_PATH"]:
                    result["library_path_configured"] = True

            # 判断整体配置状态
            result["success"] = (
                len(result["missing_variables"]) == 0 and
                result["path_configured"] and
                result["library_path_configured"]
            )

            if result["success"]:
                logger.info("环境配置验证通过")
            else:
                logger.warning(f"环境配置验证失败: 缺少变量{result['missing_variables']}")

        except Exception as e:
            logger.error(f"环境配置验证失败: {e}")
            result["error"] = str(e)

        return result

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """运行综合测试"""
        logger.info("开始运行综合测试...")

        result = {
            "installation": self.validate_installation(),
            "environment": self.test_environment_configuration(),
            "overall_success": False
        }

        # 判断整体成功状态
        result["overall_success"] = (
            result["installation"]["success"] and
            result["environment"]["success"]
        )

        return result