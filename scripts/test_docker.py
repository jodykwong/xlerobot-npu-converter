#!/usr/bin/env python3
"""
Docker environment validation script for XLeRobot NPU Converter.
This script validates that the Docker environment meets all requirements.
"""

import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd, capture_output=True, text=True, check=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(cmd, capture_output=capture_output, text=text, check=check, shell=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {cmd}")
        print(f"Error: {e}")
        return None


def test_docker_build():
    """Test that Docker image can be built successfully."""
    print("🔨 Testing Docker build...")

    cmd = "docker build -t xlerobot-test ."
    result = run_command(cmd)

    if result and result.returncode == 0:
        print("✅ Docker build successful")
        return True
    else:
        print("❌ Docker build failed")
        if result:
            print(f"Error: {result.stderr}")
        return False


def test_docker_image_size():
    """Test that Docker image size is under 5GB."""
    print("📏 Testing Docker image size...")

    cmd = "docker images xlerobot-test --format '{{.Size}}'"
    result = run_command(cmd)

    if result and result.returncode == 0:
        size_str = result.stdout.strip()
        print(f"Image size: {size_str}")

        # Parse size
        if "GB" in size_str:
            size_gb = float(size_str.replace("GB", "").replace('"', ""))
            if size_gb < 5.0:
                print(f"✅ Image size {size_gb}GB is under 5GB limit")
                return True
            else:
                print(f"❌ Image size {size_gb}GB exceeds 5GB limit")
                return False
        elif "MB" in size_str:
            size_mb = float(size_str.replace("MB", "").replace('"', ""))
            if size_mb < 5120:
                print(f"✅ Image size {size_mb}MB is under 5GB limit")
                return True
            else:
                print(f"❌ Image size {size_mb}MB exceeds 5GB limit")
                return False

    print("❌ Failed to get image size")
    return False


def test_docker_container():
    """Test that Docker container runs correctly."""
    print("🐳 Testing Docker container...")

    # Start container
    container_id = None
    try:
        cmd = "docker run -d xlerobot-test sleep 30"
        result = run_command(cmd)

        if not result or result.returncode != 0:
            print("❌ Failed to start container")
            return False

        container_id = result.stdout.strip()
        print(f"Started container: {container_id[:12]}")

        # Wait for container to start
        time.sleep(2)

        # Test Python version
        cmd = f"docker exec {container_id} python --version"
        result = run_command(cmd)

        if result and result.returncode == 0 and "Python 3.10" in result.stdout:
            print("✅ Python 3.10 is available")
        else:
            print("❌ Python 3.10 not available")
            return False

        # Test working directory
        cmd = f"docker exec {container_id} pwd"
        result = run_command(cmd)

        if result and result.returncode == 0 and result.stdout.strip() == "/app":
            print("✅ Working directory is /app")
        else:
            print("❌ Working directory not set correctly")
            return False

        # Test user permissions
        cmd = f"docker exec {container_id} whoami"
        result = run_command(cmd)

        if result and result.returncode == 0 and result.stdout.strip() != "root":
            print(f"✅ Running as non-root user: {result.stdout.strip()}")
        else:
            print("❌ Container is running as root user")
            return False

        # Test package imports
        packages = ["numpy", "pyyaml", "click", "onnx", "onnxruntime"]
        for package in packages:
            cmd = f"docker exec {container_id} python -c 'import {package}'"
            result = run_command(cmd)

            if result and result.returncode == 0:
                print(f"✅ Package {package} is importable")
            else:
                print(f"❌ Package {package} is not importable")
                return False

        return True

    finally:
        # Cleanup container
        if container_id:
            run_command(f"docker stop {container_id}", check=False)
            run_command(f"docker rm {container_id}", check=False)


def main():
    """Main validation function."""
    print("🚀 XLeRobot NPU Converter - Docker Environment Validation")
    print("=" * 60)

    # Change to project root
    project_root = Path(__file__).parent.parent
    import os
    os.chdir(project_root)

    tests = [
        ("Docker Build", test_docker_build),
        ("Image Size", test_docker_image_size),
        ("Container Runtime", test_docker_container),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        result = test_func()
        results.append((test_name, result))

    # Cleanup test image
    print("\n🧹 Cleaning up test image...")
    run_command("docker rmi xlerobot-test", check=False)

    # Summary
    print("\n" + "=" * 60)
    print("📊 Validation Summary:")

    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("🎉 All Docker environment validations passed!")
        return 0
    else:
        print("💥 Some validations failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())