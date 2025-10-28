"""
Horizon X5 BPU工具链接口

提供统一的工具链调用接口和功能。
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from .installer import ToolchainInstaller
from .version_manager import VersionManager
from .validator import ToolchainValidator

logger = logging.getLogger(__name__)


class HorizonX5Interface:
    """Horizon X5 BPU工具链统一接口"""

    def __init__(self, install_path: str = "/opt/horizon"):
        self.install_path = Path(install_path)
        self.installer = ToolchainInstaller(install_path)
        self.version_manager = VersionManager(install_path)
        self.validator = ToolchainValidator(install_path)

    def get_toolchain_info(self) -> Dict[str, Any]:
        """
        获取工具链信息

        Returns:
            Dict: 包含工具链状态信息
        """
        logger.info("获取工具链信息...")

        info = {
            "install_path": str(self.install_path),
            "is_installed": False,
            "version": "",
            "components": {},
            "installation_status": {},
            "validation_status": {}
        }

        try:
            # 检查安装状态
            install_status = self.installer.install()
            info["installation_status"] = install_status
            info["is_installed"] = install_status.get("success", False)

            # 获取版本信息
            if info["is_installed"]:
                version_info = self.version_manager.check_version()
                info["version"] = version_info.get("current_version", "")
                info["components"] = version_info.get("components_status", {})

            # 获取验证状态
            validation_info = self.validator.validate_installation()
            info["validation_status"] = validation_info

            logger.info(f"工具链信息获取完成: 版本{info['version']}")

        except Exception as e:
            logger.error(f"获取工具链信息失败: {e}")
            info["error"] = str(e)

        return info

    def execute_tool(self, tool_name: str, args: list = None) -> Dict[str, Any]:
        """
        执行工具链命令

        Args:
            tool_name: 工具名称 (hbdk, hb_mapper, hb_perf, hb_gdb)
            args: 命令参数列表

        Returns:
            Dict: 执行结果
        """
        logger.info(f"执行工具链命令: {tool_name}")

        result = {
            "success": False,
            "tool": tool_name,
            "args": args or [],
            "output": "",
            "error": None,
            "exit_code": -1
        }

        try:
            tool_path = self.install_path / "bin" / tool_name
            if not tool_path.exists():
                result["error"] = f"工具不存在: {tool_path}"
                return result

            # 构建命令
            cmd = [str(tool_path)]
            if args:
                cmd.extend(args)

            # 执行命令
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )

            result.update({
                "output": process.stdout,
                "error": process.stderr,
                "exit_code": process.returncode,
                "success": process.returncode == 0
            })

            if result["success"]:
                logger.info(f"工具{tool_name}执行成功")
            else:
                logger.warning(f"工具{tool_name}执行失败: {result.get('error', 'unknown error')}")

        except subprocess.TimeoutExpired:
            logger.error(f"工具{tool_name}执行超时")
            result["error"] = "执行超时"
        except Exception as e:
            logger.error(f"执行工具{tool_name}异常: {e}")
            result["error"] = str(e)

        return result

    def run_hbdk(self, model_path: str, output_path: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        运行BPU编译器

        Args:
            model_path: 输入模型路径
            output_path: 输出路径
            options: 编译选项

        Returns:
            Dict: 编译结果
        """
        logger.info(f"运行BPU编译器: {model_path} -> {output_path}")

        # 构建基本命令参数
        args = ["compile", "--input", model_path, "--output", output_path]

        if options:
            for key, value in options.items():
                args.extend([f"--{key}", str(value)])

        return self.execute_tool("hbdk", args)

    def run_hb_mapper(self, model_path: str, output_path: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        运行模型转换工具

        Args:
            model_path: 输入模型路径
            output_path: 输出路径
            options: 转换选项

        Returns:
            Dict: 转换结果
        """
        logger.info(f"运行模型转换工具: {model_path} -> {output_path}")

        # 构建基本命令参数
        args = ["convert", "--input", model_path, "--output", output_path]

        if options:
            for key, value in options.items():
                args.extend([f"--{key}", str(value)])

        return self.execute_tool("hb_mapper", args)

    def run_hb_perf(self, model_path: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        运行性能分析工具

        Args:
            model_path: 输入模型路径
            options: 性能分析选项

        Returns:
            Dict: 性能分析结果
        """
        logger.info(f"运行性能分析工具: {model_path}")

        # 构建基本命令参数
        args = ["analyze", "--input", model_path]

        if options:
            for key, value in options.items():
                args.extend([f"--{key}", str(value)])

        return self.execute_tool("hb_perf", args)

    def run_hb_gdb(self, executable_path: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        运行调试工具

        Args:
            executable_path: 可执行文件路径
            options: 调试选项

        Returns:
            Dict: 调试结果
        """
        logger.info(f"运行调试工具: {executable_path}")

        # 构建基本命令参数
        args = [executable_path]

        if options:
            for key, value in options.items():
                args.extend([f"--{key}", str(value)])

        return self.execute_tool("hb_gdb", args)