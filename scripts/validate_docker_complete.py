#!/usr/bin/env python3
"""
完整的Docker环境验证脚本
用于在有Docker环境中进行全面验证测试
"""

import subprocess
import sys
import time
import json
import tempfile
from pathlib import Path
from typing import List, Dict, Tuple


class DockerValidator:
    """Docker环境验证器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.image_name = "xlerobot-npu-converter"
        self.container_name = "xlerobot-validator"
        self.test_results = []

    def log(self, message: str, level: str = "INFO"):
        """日志输出"""
        symbols = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
        symbol = symbols.get(level, "ℹ️")
        print(f"{symbol} {message}")

    def run_command(self, cmd: str, check: bool = True, timeout: int = 60) -> subprocess.CompletedProcess:
        """运行命令"""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                check=check, timeout=timeout, cwd=self.project_root
            )
            return result
        except subprocess.TimeoutExpired:
            self.log(f"命令超时: {cmd}", "ERROR")
            raise
        except subprocess.CalledProcessError as e:
            self.log(f"命令失败: {cmd} (退出码: {e.returncode})", "ERROR")
            self.log(f"错误输出: {e.stderr}")
            raise

    def validate_docker_environment(self) -> bool:
        """验证Docker环境"""
        self.log("验证Docker环境...")

        try:
            # 检查Docker版本
            result = self.run_command("docker --version")
            self.log(f"Docker版本: {result.stdout.strip()}")

            # 检查Docker服务状态
            result = self.run_command("docker info")
            self.log("Docker服务运行正常")

            # 检查docker-compose
            try:
                result = self.run_command("docker-compose --version")
                self.log(f"Docker Compose版本: {result.stdout.strip()}")
            except:
                self.log("Docker Compose不可用，将使用docker compose", "WARNING")
                result = self.run_command("docker compose version")
                self.log(f"Docker Compose (V2)版本: {result.stdout.strip()}")

            return True

        except Exception as e:
            self.log(f"Docker环境验证失败: {e}", "ERROR")
            return False

    def build_image(self) -> bool:
        """构建Docker镜像"""
        self.log("构建Docker镜像...")

        try:
            # 清理旧镜像
            self.run_command(f"docker rmi {self.image_name} 2>/dev/null || true", check=False)

            # 构建新镜像
            result = self.run_command(
                f"docker build --no-cache -t {self.image_name} .",
                timeout=300  # 5分钟超时
            )

            self.log("Docker镜像构建成功")
            return True

        except Exception as e:
            self.log(f"镜像构建失败: {e}", "ERROR")
            return False

    def validate_image_size(self) -> Tuple[bool, str]:
        """验证镜像大小"""
        self.log("检查镜像大小...")

        try:
            result = self.run_command(f"docker images {self.image_name} --format '{{{{.Size}}}}'")
            size_str = result.stdout.strip()
            self.log(f"镜像大小: {size_str}")

            # 解析大小
            if "GB" in size_str:
                size_gb = float(size_str.replace("GB", "").replace('"', ""))
                if size_gb < 5.0:
                    self.log(f"镜像大小 {size_gb}GB 符合 <5GB 要求", "SUCCESS")
                    return True, size_str
                else:
                    self.log(f"镜像大小 {size_gb}GB 超过 5GB 限制", "ERROR")
                    return False, size_str
            elif "MB" in size_str:
                size_mb = float(size_str.replace("MB", "").replace('"', ""))
                if size_mb < 5120:
                    self.log(f"镜像大小 {size_mb}MB 符合 <5GB 要求", "SUCCESS")
                    return True, size_str
                else:
                    self.log(f"镜像大小 {size_mb}MB 超过 5GB 限制", "ERROR")
                    return False, size_str
            else:
                self.log(f"无法解析镜像大小格式: {size_str}", "WARNING")
                return True, size_str

        except Exception as e:
            self.log(f"镜像大小检查失败: {e}", "ERROR")
            return False, "Unknown"

    def start_container(self) -> str:
        """启动容器"""
        self.log("启动验证容器...")

        try:
            # 清理旧容器
            self.run_command(f"docker stop {self.container_name} 2>/dev/null || true", check=False)
            self.run_command(f"docker rm {self.container_name} 2>/dev/null || true", check=False)

            # 启动新容器
            result = self.run_command(
                f"docker run -d --name {self.container_name} {self.image_name} tail -f /dev/null"
            )

            container_id = result.stdout.strip()
            self.log(f"容器启动成功: {container_id[:12]}")

            # 等待容器启动
            time.sleep(3)

            return container_id

        except Exception as e:
            self.log(f"容器启动失败: {e}", "ERROR")
            raise

    def validate_python_environment(self, container_id: str) -> bool:
        """验证Python环境"""
        self.log("验证Python环境...")

        tests = [
            ("Python版本", "python --version", "Python 3.10"),
            ("pip版本", "pip --version", "pip"),
            ("Python路径", "which python", "/usr/bin/python"),
        ]

        all_passed = True
        for test_name, cmd, expected in tests:
            try:
                result = self.run_command(f"docker exec {container_id} {cmd}", check=False)
                if result.returncode == 0 and expected in result.stdout:
                    self.log(f"✓ {test_name}: {result.stdout.strip()}")
                else:
                    self.log(f"✗ {test_name}: 检查失败", "ERROR")
                    all_passed = False
            except Exception as e:
                self.log(f"✗ {test_name}: {e}", "ERROR")
                all_passed = False

        return all_passed

    def validate_packages(self, container_id: str) -> bool:
        """验证Python包"""
        self.log("验证Python包...")

        # 生产依赖
        production_packages = [
            "numpy", "pyyaml", "click", "onnx", "onnxruntime"
        ]

        # 开发依赖
        dev_packages = [
            "black", "ruff", "mypy", "pytest", "pytest_cov"
        ]

        all_passed = True

        self.log("检查生产依赖包...")
        for package in production_packages:
            try:
                result = self.run_command(
                    f"docker exec {container_id} python -c 'import {package}'",
                    check=False
                )
                if result.returncode == 0:
                    self.log(f"✓ {package} 导入成功")
                else:
                    self.log(f"✗ {package} 导入失败", "ERROR")
                    all_passed = False
            except Exception as e:
                self.log(f"✗ {package} 检查失败: {e}", "ERROR")
                all_passed = False

        self.log("检查开发依赖包...")
        for package in dev_packages:
            try:
                # pytest_cov在代码中是pytest_cov，但包名是pytest-cov
                import_name = "pytest_cov" if package == "pytest_cov" else package
                cmd_name = package.replace("_", "-")

                result = self.run_command(
                    f"docker exec {container_id} {cmd_name} --version",
                    check=False
                )
                if result.returncode == 0:
                    self.log(f"✓ {package} 可用")
                else:
                    self.log(f"✗ {package} 不可用", "ERROR")
                    all_passed = False
            except Exception as e:
                self.log(f"✗ {package} 检查失败: {e}", "ERROR")
                all_passed = False

        return all_passed

    def validate_filesystem(self, container_id: str) -> bool:
        """验证文件系统"""
        self.log("验证文件系统...")

        tests = [
            ("工作目录", "pwd", "/app"),
            ("用户权限", "whoami", "npuuser"),
            ("用户ID", "id -u", "1000"),
            ("组ID", "id -g", "1000"),
        ]

        all_passed = True
        for test_name, cmd, expected in tests:
            try:
                result = self.run_command(f"docker exec {container_id} {cmd}")
                actual = result.stdout.strip()
                if actual == expected:
                    self.log(f"✓ {test_name}: {actual}")
                else:
                    self.log(f"✗ {test_name}: 期望 '{expected}', 实际 '{actual}'", "ERROR")
                    all_passed = False
            except Exception as e:
                self.log(f"✗ {test_name}: {e}", "ERROR")
                all_passed = False

        return all_passed

    def validate_environment_variables(self, container_id: str) -> bool:
        """验证环境变量"""
        self.log("验证环境变量...")

        expected_env_vars = {
            "PYTHONUNBUFFERED": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "DEBIAN_FRONTEND": "noninteractive"
        }

        all_passed = True
        for var_name, expected_value in expected_env_vars.items():
            try:
                result = self.run_command(
                    f"docker exec {container_id} printenv {var_name}",
                    check=False
                )
                if result.returncode == 0 and result.stdout.strip() == expected_value:
                    self.log(f"✓ {var_name}={expected_value}")
                else:
                    self.log(f"✗ {var_name}: 设置不正确", "ERROR")
                    all_passed = False
            except Exception as e:
                self.log(f"✗ {var_name}: 检查失败: {e}", "ERROR")
                all_passed = False

        return all_passed

    def run_tests(self, container_id: str) -> bool:
        """运行测试套件"""
        self.log("运行测试套件...")

        try:
            # 运行单元测试
            self.log("运行单元测试...")
            result = self.run_command(
                f"docker exec {container_id} python -m pytest tests/unit/ -v --tb=short",
                check=False
            )

            if result.returncode == 0:
                self.log("✓ 单元测试通过", "SUCCESS")
                unit_tests_passed = True
            else:
                self.log("✗ 单元测试失败", "ERROR")
                self.log(f"测试输出: {result.stdout}")
                self.log(f"错误输出: {result.stderr}")
                unit_tests_passed = False

            # 如果有集成测试，也运行
            if Path(self.project_root / "tests/integration").exists():
                self.log("运行集成测试...")
                result = self.run_command(
                    f"docker exec {container_id} python -m pytest tests/integration/ -v --tb=short",
                    check=False
                )

                if result.returncode == 0:
                    self.log("✓ 集成测试通过", "SUCCESS")
                    integration_tests_passed = True
                else:
                    self.log("✗ 集成测试失败", "ERROR")
                    integration_tests_passed = False
            else:
                integration_tests_passed = True

            return unit_tests_passed and integration_tests_passed

        except Exception as e:
            self.log(f"测试运行失败: {e}", "ERROR")
            return False

    def validate_docker_compose(self) -> bool:
        """验证Docker Compose配置"""
        self.log("验证Docker Compose配置...")

        try:
            # 检查docker-compose.yml语法
            self.run_command("docker-compose config", check=False)

            # 尝试构建compose服务
            self.run_command("docker-compose build", timeout=300)

            self.log("✓ Docker Compose配置验证通过", "SUCCESS")
            return True

        except Exception as e:
            self.log(f"Docker Compose验证失败: {e}", "ERROR")
            return False

    def cleanup(self, container_id: str):
        """清理资源"""
        self.log("清理验证资源...")

        try:
            self.run_command(f"docker stop {container_id}", check=False)
            self.run_command(f"docker rm {container_id}", check=False)
            self.log("清理完成")
        except:
            pass

    def generate_report(self) -> Dict:
        """生成验证报告"""
        return {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "image_name": self.image_name,
            "results": self.test_results,
            "summary": {
                "total_tests": len(self.test_results),
                "passed": sum(1 for r in self.test_results if r["passed"]),
                "failed": sum(1 for r in self.test_results if not r["passed"])
            }
        }

    def run_complete_validation(self) -> bool:
        """运行完整验证"""
        self.log("🚀 开始完整Docker环境验证", "SUCCESS")
        self.log("=" * 60)

        all_passed = True
        container_id = None

        try:
            # 验证Docker环境
            if not self.validate_docker_environment():
                return False

            # 构建镜像
            if not self.build_image():
                return False

            # 验证镜像大小
            size_ok, size_str = self.validate_image_size()
            self.test_results.append({
                "test": "镜像大小检查",
                "passed": size_ok,
                "details": f"大小: {size_str}"
            })
            if not size_ok:
                all_passed = False

            # 启动容器
            container_id = self.start_container()

            # 运行各项验证
            validations = [
                ("Python环境验证", self.validate_python_environment),
                ("Python包验证", self.validate_packages),
                ("文件系统验证", self.validate_filesystem),
                ("环境变量验证", self.validate_environment_variables),
                ("测试套件运行", self.run_tests),
                ("Docker Compose验证", self.validate_docker_compose),
            ]

            for test_name, test_func in validations:
                self.log(f"\n--- {test_name} ---")
                try:
                    passed = test_func(container_id) if container_id else test_func()
                    self.test_results.append({
                        "test": test_name,
                        "passed": passed,
                        "details": "验证通过" if passed else "验证失败"
                    })
                    if not passed:
                        all_passed = False
                except Exception as e:
                    self.log(f"{test_name} 执行失败: {e}", "ERROR")
                    self.test_results.append({
                        "test": test_name,
                        "passed": False,
                        "details": f"执行失败: {str(e)}"
                    })
                    all_passed = False

        except Exception as e:
            self.log(f"验证过程中发生错误: {e}", "ERROR")
            all_passed = False

        finally:
            # 清理资源
            if container_id:
                self.cleanup(container_id)

        # 生成报告
        report = self.generate_report()

        # 显示总结
        self.log("\n" + "=" * 60)
        self.log("📊 验证总结", "SUCCESS")
        self.log(f"总测试数: {report['summary']['total_tests']}")
        self.log(f"通过: {report['summary']['passed']}")
        self.log(f"失败: {report['summary']['failed']}")

        if all_passed:
            self.log("🎉 所有验证测试通过！", "SUCCESS")
        else:
            self.log("💥 部分验证测试失败！", "ERROR")

        # 保存报告
        report_file = self.project_root / "docker_validation_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        self.log(f"详细报告已保存到: {report_file}")

        return all_passed


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent

    print("🐳 XLeRobot NPU Converter - Docker环境完整验证")
    print("=" * 60)

    validator = DockerValidator(project_root)
    success = validator.run_complete_validation()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())