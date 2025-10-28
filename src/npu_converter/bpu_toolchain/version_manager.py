"""
Horizon X5 BPU工具链版本管理器

负责版本检查、更新和回滚功能。
"""

import os
import logging
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class VersionManager:
    """BPU工具链版本管理器"""

    def __init__(self, install_path: str = "/opt/horizon"):
        self.install_path = Path(install_path)
        self.current_version = ""
        self.available_versions = []
        self.backup_path = self.install_path / "backups"

    def check_version(self) -> Dict[str, Any]:
        """
        检查工具链版本

        Returns:
            Dict: 版本信息和状态
        """
        logger.info("检查工具链版本...")

        result = {
            "current_version": "",
            "is_installed": False,
            "components_status": {},
            "compatibility": ""
        }

        try:
            # 检查主版本文件
            version_file = self.install_path / "version.txt"
            if version_file.exists():
                with open(version_file, 'r') as f:
                    self.current_version = f.read().strip()
                    result["current_version"] = self.current_version

            # 检查组件状态
            components = ["hbdk", "hb_mapper", "hb_perf", "hb_gdb"]
            for component in components:
                component_path = self.install_path / "bin" / component
                if component_path.exists():
                    result["components_status"][component] = "available"
                else:
                    result["components_status"][component] = "missing"

            # 判断是否完整安装
            all_available = all(
                status == "available"
                for status in result["components_status"].values()
            )
            result["is_installed"] = (
                self.current_version != "unknown" and all_available
            )

            # 检查兼容性
            result["compatibility"] = self._check_compatibility()

            logger.info(f"版本检查完成: {self.current_version}")
            return result

        except Exception as e:
            logger.error(f"版本检查失败: {e}")
            result["error"] = str(e)
            return result

    def update_version(self, target_version: str = "latest") -> Dict[str, Any]:
        """
        更新工具链到指定版本

        Args:
            target_version: 目标版本，"latest"表示最新版本

        Returns:
            Dict: 更新结果
        """
        logger.info(f"开始更新工具链到版本: {target_version}")

        result = {
            "success": False,
            "old_version": self.current_version,
            "new_version": target_version,
            "error": None
        }

        try:
            # 1. 创建备份
            self._create_backup()

            # 2. 获取新版本
            if target_version == "latest":
                target_version = self._get_latest_version()

            # 3. 下载新版本
            new_package = self._download_version(target_version)
            if not new_package:
                result["error"] = "下载新版本失败"
                return result

            # 4. 安装新版本
            self._install_version(new_package)

            # 5. 验证更新
            new_version_check = self.check_version()
            if new_version_check["is_installed"]:
                result["success"] = True
                result["new_version"] = target_version
                logger.info(f"工具链更新成功到版本: {target_version}")
            else:
                result["error"] = "更新后验证失败"
                # 回滚到备份版本
                self.rollback()

        except Exception as e:
            logger.error(f"更新版本失败: {e}")
            result["error"] = str(e)
            # 尝试回滚
            try:
                self.rollback()
            except:
                logger.error("回滚也失败")

        return result

    def rollback(self) -> Dict[str, Any]:
        """
        回滚到上一个版本

        Returns:
            Dict: 回滚结果
        """
        logger.info("开始回滚工具链...")

        result = {
            "success": False,
            "from_version": self.current_version,
            "to_version": "",
            "error": None
        }

        try:
            # 找到最新的备份
            backup = self._find_latest_backup()
            if not backup:
                result["error"] = "没有找到可用的备份"
                return result

            # 停止当前版本（如果正在运行）
            self._stop_current_version()

            # 恢复备份
            self._restore_backup(backup)

            # 验证回滚
            version_check = self.check_version()
            if version_check["is_installed"]:
                result["success"] = True
                result["to_version"] = backup["version"]
                logger.info(f"回滚成功到版本: {backup['version']}")

        except Exception as e:
            logger.error(f"回滚失败: {e}")
            result["error"] = str(e)

        return result

    def _create_backup(self) -> None:
        """创建当前版本的备份"""
        logger.info("创建版本备份...")

        try:
            self.backup_path.mkdir(parents=True, exist_ok=True)

            backup_name = f"backup_{self.current_version.replace('.', '_')}_{self._get_timestamp()}"
            backup_dir = self.backup_path / backup_name

            shutil.copytree(self.install_path, backup_dir, ignore=shutil.ignore_patterns('.git'))
            logger.info(f"备份创建成功: {backup_dir}")

        except Exception as e:
            logger.error(f"创建备份失败: {e}")

    def _find_latest_backup(self) -> Optional[Dict]:
        """找到最新的备份"""
        try:
            if not self.backup_path.exists():
                return None

            backup_dirs = [d for d in self.backup_path.iterdir() if d.is_dir()]
            if not backup_dirs:
                return None

            # 按修改时间排序，获取最新的
            latest_backup = max(backup_dirs, key=lambda x: x.stat().st_mtime)

            # 从目录名提取版本信息
            backup_name = latest_backup.name
            version = backup_name.split('_')[1] if '_' in backup_name else "unknown"

            return {
                "path": latest_backup,
                "version": version.replace('_', '.')
            }

        except Exception as e:
            logger.error(f"查找备份失败: {e}")
            return None

    def _restore_backup(self, backup: Dict) -> None:
        """恢复备份版本"""
        logger.info(f"恢复备份版本: {backup['version']}")

        try:
            # 清空当前安装目录
            shutil.rmtree(self.install_path)
            self.install_path.mkdir(parents=True)

            # 复制备份内容
            shutil.copytree(backup["path"], self.install_path)

        except Exception as e:
            logger.error(f"恢复备份失败: {e}")
            raise

    def _check_compatibility(self) -> str:
        """检查版本兼容性"""
        # TODO: 实现具体的兼容性检查逻辑
        if not self.current_version:
            return "unknown"

        # 简单的兼容性检查占位符
        if self.current_version.startswith("1."):
            return "compatible"
        elif self.current_version.startswith("2."):
            return "compatible"
        else:
            return "unknown"

    def _get_latest_version(self) -> str:
        """获取最新版本号"""
        # TODO: 实现获取最新版本的逻辑
        return "1.0.0"

    def _download_version(self, version: str) -> Optional[str]:
        """下载指定版本的工具链"""
        # TODO: 实现下载逻辑
        return str(self.install_path / f"toolchain_{version}.tar.gz")

    def _install_version(self, package_path: str) -> None:
        """安装指定版本的工具链"""
        # TODO: 实现安装逻辑
        pass

    def _stop_current_version(self) -> None:
        """停止当前版本的工具链服务"""
        # TODO: 实现停止逻辑（如果有服务在运行）
        pass

    def _get_timestamp(self) -> str:
        """获取时间戳字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")