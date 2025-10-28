#!/usr/bin/env python3
"""
Docker配置验证脚本（无Docker环境版本）
用于验证Docker相关配置文件的正确性
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple


class DockerConfigValidator:
    """Docker配置验证器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.test_results = []

    def log(self, message: str, level: str = "INFO"):
        """日志输出"""
        symbols = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
        symbol = symbols.get(level, "ℹ️")
        print(f"{symbol} {message}")

    def validate_file_exists(self, file_path: str, description: str) -> bool:
        """验证文件是否存在"""
        full_path = self.project_root / file_path
        exists = full_path.exists()

        if exists:
            self.log(f"✓ {description}: {file_path}")
        else:
            self.log(f"✗ {description}: {file_path} (缺失)", "ERROR")

        self.test_results.append({
            "test": f"文件存在检查 - {description}",
            "passed": exists,
            "details": file_path
        })

        return exists

    def validate_dockerfile_content(self) -> bool:
        """验证Dockerfile内容"""
        dockerfile_path = self.project_root / "Dockerfile"

        if not dockerfile_path.exists():
            self.log("Dockerfile不存在", "ERROR")
            return False

        content = dockerfile_path.read_text()
        all_checks_passed = True

        checks = [
            ("Ubuntu 20.04基础镜像", "FROM ubuntu:20.04"),
            ("Python 3.10安装", "python3.10"),
            ("多阶段构建", "as base"),
            ("非root用户创建", "groupadd --gid"),
            ("非root用户切换", "USER "),
            ("工作目录设置", "WORKDIR /app"),
            ("环境变量PYTHONUNBUFFERED", "PYTHONUNBUFFERED=1"),
            ("环境变量PYTHONDONTWRITEBYTECODE", "PYTHONDONTWRITEBYTECODE=1"),
            ("包缓存清理", "rm -rf /var/lib/apt/lists/"),
            ("多阶段构建使用", "as application"),
        ]

        self.log("验证Dockerfile内容...")
        for check_name, pattern in checks:
            if pattern in content:
                self.log(f"  ✓ {check_name}")
            else:
                self.log(f"  ✗ {check_name} (缺失)", "ERROR")
                all_checks_passed = False

        self.test_results.append({
            "test": "Dockerfile内容验证",
            "passed": all_checks_passed,
            "details": f"检查了{len(checks)}项内容"
        })

        return all_checks_passed

    def validate_requirements_files(self) -> bool:
        """验证requirements文件"""
        all_passed = True

        # 验证requirements.txt
        req_path = self.project_root / "requirements.txt"
        if req_path.exists():
            content = req_path.read_text()

            expected_packages = [
                "numpy==1.24.3",
                "pyyaml==6.0",
                "click==8.1.7",
                "onnx==1.14.0",
                "onnxruntime==1.15.1"
            ]

            self.log("验证requirements.txt...")
            for package in expected_packages:
                if package in content:
                    self.log(f"  ✓ {package}")
                else:
                    self.log(f"  ✗ {package} (缺失)", "ERROR")
                    all_passed = False
        else:
            self.log("requirements.txt不存在", "ERROR")
            all_passed = False

        # 验证requirements-dev.txt
        dev_req_path = self.project_root / "requirements-dev.txt"
        if dev_req_path.exists():
            content = dev_req_path.read_text()

            expected_dev_packages = [
                "black==23.7.0",
                "ruff==0.0.285",
                "mypy==1.5.1",
                "pre-commit==3.3.3",
                "pytest==7.4.0",
                "pytest-cov==4.1.0"
            ]

            self.log("验证requirements-dev.txt...")
            for package in expected_dev_packages:
                if package in content:
                    self.log(f"  ✓ {package}")
                else:
                    self.log(f"  ✗ {package} (缺失)", "ERROR")
                    all_passed = False
        else:
            self.log("requirements-dev.txt不存在", "ERROR")
            all_passed = False

        self.test_results.append({
            "test": "Requirements文件验证",
            "passed": all_passed,
            "details": "验证生产依赖和开发依赖包"
        })

        return all_passed

    def validate_docker_compose(self) -> bool:
        """验证docker-compose.yml文件"""
        compose_path = self.project_root / "docker-compose.yml"

        if not compose_path.exists():
            self.log("docker-compose.yml不存在", "ERROR")
            return False

        content = compose_path.read_text()
        all_checks_passed = True

        checks = [
            ("版本声明", "version:"),
            ("服务定义", "services:"),
            ("npu-converter服务", "npu-converter:"),
            ("构建上下文", "build:"),
            ("Dockerfile引用", "dockerfile: Dockerfile"),
            ("环境变量", "environment:"),
            ("PYTHONUNBUFFERED设置", "PYTHONUNBUFFERED=1"),
            ("卷挂载", "volumes:"),
            ("源代码挂载", "./src:/app/src"),
            ("非root用户", "user:"),
            ("网络配置", "networks:"),
        ]

        self.log("验证docker-compose.yml内容...")
        for check_name, pattern in checks:
            if pattern in content:
                self.log(f"  ✓ {check_name}")
            else:
                self.log(f"  ✗ {check_name} (缺失)", "ERROR")
                all_checks_passed = False

        self.test_results.append({
            "test": "Docker Compose配置验证",
            "passed": all_checks_passed,
            "details": f"检查了{len(checks)}项配置"
        })

        return all_checks_passed

    def validate_dockerignore(self) -> bool:
        """验证.dockerignore文件"""
        ignore_path = self.project_root / ".dockerignore"

        if not ignore_path.exists():
            self.log(".dockerignore不存在", "ERROR")
            return False

        content = ignore_path.read_text()

        expected_exclusions = [
            ".git",
            "__pycache__",
            "*.pyc",
            ".pytest_cache",
            "docs/",
            "*.log",
        ]

        self.log("验证.dockerignore内容...")
        all_found = True
        for exclusion in expected_exclusions:
            if exclusion in content:
                self.log(f"  ✓ 排除规则: {exclusion}")
            else:
                self.log(f"  ⚠️ 建议排除: {exclusion}", "WARNING")

        self.test_results.append({
            "test": ".dockerignore验证",
            "passed": True,  # 警告不算失败
            "details": "检查排除规则"
        })

        return True

    def validate_script_files(self) -> bool:
        """验证脚本文件"""
        all_passed = True

        scripts = [
            ("scripts/build.sh", "构建脚本"),
            ("scripts/test_docker.py", "Docker测试脚本"),
            ("scripts/validate_docker_complete.py", "完整验证脚本"),
        ]

        self.log("验证脚本文件...")
        for script_path, description in scripts:
            full_path = self.project_root / script_path
            if full_path.exists():
                # 检查是否可执行
                if os.access(full_path, os.X_OK):
                    self.log(f"  ✓ {description} (可执行)")
                else:
                    self.log(f"  ⚠️ {description} (不可执行)", "WARNING")
            else:
                self.log(f"  ✗ {description} (缺失)", "ERROR")
                all_passed = False

        self.test_results.append({
            "test": "脚本文件验证",
            "passed": all_passed,
            "details": f"检查了{len(scripts)}个脚本"
        })

        return all_passed

    def validate_pytest_config(self) -> bool:
        """验证pytest配置"""
        pytest_ini = self.project_root / "pytest.ini"

        if not pytest_ini.exists():
            self.log("pytest.ini不存在", "ERROR")
            return False

        content = pytest_ini.read_text()

        expected_sections = [
            ("测试路径配置", "testpaths = tests"),
            ("测试文件模式", "python_files = test_*.py"),
            ("详细输出", "addopts = --verbose"),
        ]

        self.log("验证pytest配置...")
        all_found = True
        for check_name, pattern in expected_sections:
            if pattern in content:
                self.log(f"  ✓ {check_name}")
            else:
                self.log(f"  ⚠️ {check_name} (缺失)", "WARNING")

        self.test_results.append({
            "test": "Pytest配置验证",
            "passed": True,
            "details": "检查pytest配置文件"
        })

        return True

    def validate_directory_structure(self) -> bool:
        """验证目录结构"""
        required_dirs = [
            "tests",
            "tests/unit",
            "tests/integration",
            "tests/fixtures",
            "scripts",
            "src",  # 预期的未来目录
            "config",  # 预期的未来目录
        ]

        self.log("验证目录结构...")
        all_exist = True
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists() and full_path.is_dir():
                self.log(f"  ✓ 目录: {dir_path}")
            else:
                self.log(f"  ⚠️ 目录: {dir_path} (预期但不存在)", "WARNING")

        self.test_results.append({
            "test": "目录结构验证",
            "passed": True,
            "details": "检查项目目录结构"
        })

        return True

    def generate_validation_report(self) -> Dict:
        """生成验证报告"""
        return {
            "timestamp": subprocess.check_output(["date"], text=True).strip(),
            "project_root": str(self.project_root),
            "validation_type": "Configuration Only (No Docker Runtime)",
            "results": self.test_results,
            "summary": {
                "total_checks": len(self.test_results),
                "passed": sum(1 for r in self.test_results if r["passed"]),
                "failed": sum(1 for r in self.test_results if not r["passed"])
            }
        }

    def run_complete_validation(self) -> bool:
        """运行完整配置验证"""
        self.log("🔍 开始Docker配置验证", "SUCCESS")
        self.log("=" * 60)

        # 验证必要文件
        self.log("\n--- 文件存在性检查 ---")
        file_checks = [
            ("Dockerfile", "Docker镜像定义文件"),
            ("requirements.txt", "生产依赖文件"),
            ("requirements-dev.txt", "开发依赖文件"),
            (".dockerignore", "Docker忽略文件"),
            ("docker-compose.yml", "Docker Compose配置"),
            ("pytest.ini", "pytest配置文件"),
        ]

        files_exist = True
        for file_path, description in file_checks:
            if not self.validate_file_exists(file_path, description):
                files_exist = False

        # 验证配置内容
        content_validations = [
            ("Dockerfile内容", self.validate_dockerfile_content),
            ("Requirements文件", self.validate_requirements_files),
            ("Docker Compose配置", self.validate_docker_compose),
            ("Dockerignore配置", self.validate_dockerignore),
            ("脚本文件", self.validate_script_files),
            ("Pytest配置", self.validate_pytest_config),
            ("目录结构", self.validate_directory_structure),
        ]

        self.log("\n--- 配置内容验证 ---")
        all_content_valid = True
        for validation_name, validation_func in content_validations:
            if not validation_func():
                all_content_valid = False

        # 生成报告
        report = self.generate_validation_report()

        # 显示总结
        self.log("\n" + "=" * 60)
        self.log("📊 配置验证总结", "SUCCESS")
        self.log(f"总检查项: {report['summary']['total_checks']}")
        self.log(f"通过: {report['summary']['passed']}")
        self.log(f"失败: {report['summary']['failed']}")

        # 保存报告
        report_file = self.project_root / "docker_config_validation_report.json"
        import json
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        self.log(f"详细报告已保存到: {report_file}")

        # 给出下一步建议
        self.log("\n📋 下一步建议:", "INFO")
        if files_exist and all_content_valid:
            self.log("✅ 所有配置验证通过！", "SUCCESS")
            self.log("🚀 在有Docker环境中运行: ./scripts/validate_docker_complete.py")
            self.log("🐳 或手动执行: docker build -t xlerobot-npu-converter .")
        else:
            self.log("❌ 部分配置验证失败，请修复后重试", "ERROR")
            self.log("📝 查看详细报告了解具体问题")

        return files_exist and all_content_valid


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent

    print("🐳 XLeRobot NPU Converter - Docker配置验证")
    print("(无Docker运行时环境版本)")
    print("=" * 60)

    validator = DockerConfigValidator(project_root)
    success = validator.run_complete_validation()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())