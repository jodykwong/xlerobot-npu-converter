"""
Integration tests for Docker build and runtime environment.
"""

import subprocess
import pytest
import time


class TestDockerBuild:
    """Test Docker image build process."""

    def test_docker_build_succeeds(self, project_root, docker_image_name):
        """Test that Docker image builds successfully."""
        result = subprocess.run(
            ["docker", "build", "-t", docker_image_name, str(project_root)],
            capture_output=True,
            text=True,
            cwd=project_root
        )

        assert result.returncode == 0, f"Docker build failed: {result.stderr}"
        assert "Successfully built" in result.stdout, "Build should report success"

    def test_docker_image_size(self, docker_image_name):
        """Test that Docker image size is under 5GB limit."""
        result = subprocess.run(
            ["docker", "images", docker_image_name, "--format", "{{.Size}}"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, "Failed to get image size"

        size_str = result.stdout.strip()
        # Parse size (format could be like "1.23GB" or "123MB")
        if "GB" in size_str:
            size_gb = float(size_str.replace("GB", ""))
            assert size_gb < 5.0, f"Image size {size_gb}GB exceeds 5GB limit"
        elif "MB" in size_str:
            size_mb = float(size_str.replace("MB", ""))
            assert size_mb < 5120, f"Image size {size_mb}MB exceeds 5GB limit"

    def test_docker_image_layers(self, docker_image_name):
        """Test that Docker image has reasonable number of layers."""
        result = subprocess.run(
            ["docker", "history", docker_image_name],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, "Failed to get image history"

        layers = result.stdout.strip().split('\n')
        # Remove header line
        layer_count = len([l for l in layers if not l.startswith("IMAGE")])

        # Should have reasonable number of layers (not too many, not too few)
        assert 10 <= layer_count <= 30, f"Image has {layer_count} layers, expected 10-30"


class TestDockerRuntime:
    """Test Docker container runtime environment."""

    def test_python_version(self, running_container):
        """Test that Python 3.10 is available in container."""
        result = subprocess.run(
            ["docker", "exec", running_container, "python", "--version"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, "Failed to get Python version"
        assert "Python 3.10" in result.stdout, "Should have Python 3.10"

    def test_pip_version(self, running_container):
        """Test that pip is available and working."""
        result = subprocess.run(
            ["docker", "exec", running_container, "pip", "--version"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, "Failed to get pip version"
        assert "pip" in result.stdout.lower(), "Should have pip available"

    def test_required_packages_installed(self, running_container):
        """Test that required packages are installed."""
        required_packages = [
            "numpy",
            "pyyaml",
            "click",
            "onnx",
            "onnxruntime"
        ]

        for package in required_packages:
            result = subprocess.run(
                ["docker", "exec", running_container, "python", "-c", f"import {package}"],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Package {package} should be importable"

    def test_dev_packages_installed(self, running_container):
        """Test that development packages are installed."""
        dev_packages = [
            "black",
            "ruff",
            "mypy",
            "pytest"
        ]

        for package in dev_packages:
            result = subprocess.run(
                ["docker", "exec", running_container, package, "--version"],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Dev package {package} should be available"

    def test_working_directory(self, running_container):
        """Test that working directory is set to /app."""
        result = subprocess.run(
            ["docker", "exec", running_container, "pwd"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, "Failed to get working directory"
        assert result.stdout.strip() == "/app", "Working directory should be /app"

    def test_user_permissions(self, running_container):
        """Test that container runs as non-root user."""
        # Check current user
        result = subprocess.run(
            ["docker", "exec", running_container, "whoami"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, "Failed to get current user"
        assert result.stdout.strip() != "root", "Should not run as root user"

        # Check user ID
        result = subprocess.run(
            ["docker", "exec", running_container, "id", "-u"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, "Failed to get user ID"
        user_id = int(result.stdout.strip())
        assert user_id != 0, "User ID should not be 0 (root)"

    def test_environment_variables(self, running_container):
        """Test that required environment variables are set."""
        env_vars = [
            "PYTHONUNBUFFERED=1",
            "PYTHONDONTWRITEBYTECODE=1"
        ]

        for env_var in env_vars:
            var_name, expected_value = env_var.split("=")
            result = subprocess.run(
                ["docker", "exec", running_container, "printenv", var_name],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, f"Failed to get {var_name}"
            assert result.stdout.strip() == expected_value, f"{var_name} should be {expected_value}"