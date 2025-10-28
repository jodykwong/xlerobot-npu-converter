#!/usr/bin/env python3
"""
Docker环境快速验证脚本
提供简化的验证检查
"""

import sys
import subprocess
from pathlib import Path


def quick_validate():
    """快速验证Docker配置"""
    project_root = Path(__file__).parent.parent

    print("🔍 XLeRobot Docker环境快速验证")
    print("=" * 40)

    # 检查关键文件
    key_files = [
        "Dockerfile",
        "requirements.txt",
        "requirements-dev.txt",
        "docker-compose.yml",
        "scripts/build.sh"
    ]

    files_ok = True
    print("\n📁 关键文件检查:")
    for file_name in key_files:
        if (project_root / file_name).exists():
            print(f"  ✅ {file_name}")
        else:
            print(f"  ❌ {file_name}")
            files_ok = False

    # 检查依赖包
    req_path = project_root / "requirements.txt"
    if req_path.exists():
        content = req_path.read_text()
        required_packages = ["numpy==1.24.3", "pyyaml==6.0", "click==8.1.7"]

        print("\n📦 核心依赖包检查:")
        packages_ok = True
        for package in required_packages:
            if package in content:
                print(f"  ✅ {package}")
            else:
                print(f"  ❌ {package}")
                packages_ok = False

    # 检查Dockerfile关键配置
    dockerfile_path = project_root / "Dockerfile"
    if dockerfile_path.exists():
        content = dockerfile_path.read_text()

        print("\n🐳 Dockerfile配置检查:")
        docker_checks = [
            ("Ubuntu 20.04", "FROM ubuntu:20.04" in content),
            ("Python 3.10", "python3.10" in content),
            ("非root用户", "USER " in content),
            ("工作目录", "WORKDIR /app" in content),
        ]

        docker_ok = True
        for check_name, passed in docker_checks:
            if passed:
                print(f"  ✅ {check_name}")
            else:
                print(f"  ❌ {check_name}")
                docker_ok = False

    # 检查脚本可执行性
    script_path = project_root / "scripts/build.sh"
    scripts_ok = True
    if script_path.exists():
        import os
        if os.access(script_path, os.X_OK):
            print("\n🔧 脚本可执行性: ✅ build.sh")
        else:
            print("\n🔧 脚本可执行性: ❌ build.sh (不可执行)")
            scripts_ok = False

    # 总结
    print("\n" + "=" * 40)
    all_ok = files_ok and packages_ok and docker_ok and scripts_ok

    if all_ok:
        print("🎉 快速验证通过！")
        print("\n📋 下一步:")
        print("1. 在有Docker的环境中运行: ./scripts/validate_docker_complete.py")
        print("2. 或手动构建: docker build -t xlerobot-npu-converter .")
    else:
        print("❌ 快速验证发现问题，请检查上述失败项")

    return all_ok


if __name__ == "__main__":
    success = quick_validate()
    sys.exit(0 if success else 1)