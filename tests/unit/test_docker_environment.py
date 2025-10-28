"""
Unit tests for Docker environment configuration and setup.
"""

import subprocess
import pytest
from pathlib import Path


class TestDockerfile:
    """Test Dockerfile configuration and structure."""

    def test_dockerfile_exists(self, project_root):
        """Test that Dockerfile exists in project root."""
        dockerfile_path = project_root / "Dockerfile"
        assert dockerfile_path.exists(), "Dockerfile should exist in project root"

    def test_dockerfile_content_valid(self, project_root):
        """Test that Dockerfile contains required elements."""
        dockerfile_path = project_root / "Dockerfile"
        content = dockerfile_path.read_text()

        # Check for Ubuntu 20.04 base image
        assert "FROM ubuntu:20.04" in content, "Should use Ubuntu 20.04 base image"

        # Check for Python 3.10 installation
        assert "python3.10" in content, "Should install Python 3.10"

        # Check for non-root user creation
        assert "useradd" in content or "adduser" in content, "Should create non-root user"

        # Check for working directory setup
        assert "WORKDIR /app" in content, "Should set /app as working directory"

    def test_dockerfile_security_practices(self, project_root):
        """Test that Dockerfile follows security best practices."""
        dockerfile_path = project_root / "Dockerfile"
        content = dockerfile_path.read_text()

        # Check for non-root user usage
        assert "USER " in content, "Should switch to non-root user"

        # Check for proper environment variables
        assert "PYTHONUNBUFFERED=1" in content, "Should set PYTHONUNBUFFERED"

        # Check for cleanup of package caches
        assert "rm -rf /var/lib/apt/lists/" in content, "Should clean apt caches"


class TestRequirements:
    """Test requirements files."""

    def test_requirements_txt_exists(self, project_root):
        """Test that requirements.txt exists."""
        requirements_path = project_root / "requirements.txt"
        assert requirements_path.exists(), "requirements.txt should exist"

    def test_requirements_dev_txt_exists(self, project_root):
        """Test that requirements-dev.txt exists."""
        requirements_dev_path = project_root / "requirements-dev.txt"
        assert requirements_dev_path.exists(), "requirements-dev.txt should exist"

    def test_requirements_content(self, project_root):
        """Test that requirements.txt contains expected packages."""
        requirements_path = project_root / "requirements.txt"
        content = requirements_path.read_text()

        expected_packages = [
            "numpy==1.24.3",
            "pyyaml==6.0",
            "click==8.1.7",
            "onnx==1.14.0",
            "onnxruntime==1.15.1"
        ]

        for package in expected_packages:
            assert package in content, f"Should include {package}"

    def test_requirements_dev_content(self, project_root):
        """Test that requirements-dev.txt contains development packages."""
        requirements_dev_path = project_root / "requirements-dev.txt"
        content = requirements_dev_path.read_text()

        expected_dev_packages = [
            "black==23.7.0",
            "ruff==0.0.285",
            "mypy==1.5.1",
            "pre-commit==3.3.3",
            "pytest==7.4.0",
            "pytest-cov==4.1.0"
        ]

        for package in expected_dev_packages:
            assert package in content, f"Should include {package}"


class TestDockerIgnore:
    """Test .dockerignore file."""

    def test_dockerignore_exists(self, project_root):
        """Test that .dockerignore exists."""
        dockerignore_path = project_root / ".dockerignore"
        assert dockerignore_path.exists(), ".dockerignore should exist"

    def test_dockerignore_content(self, project_root):
        """Test that .dockerignore excludes appropriate files."""
        dockerignore_path = project_root / ".dockerignore"
        content = dockerignore_path.read_text()

        # Check for common exclusions
        exclusions = [
            ".git",
            "__pycache__",
            "*.pyc",
            ".pytest_cache",
            "docs/"
        ]

        for exclusion in exclusions:
            assert exclusion in content, f"Should exclude {exclusion}"