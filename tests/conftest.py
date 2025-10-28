"""
Pytest configuration and fixtures for XLeRobot NPU Converter tests.
"""

import pytest
import os
import tempfile
import subprocess
from pathlib import Path


@pytest.fixture
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def docker_image_name():
    """Return the Docker image name for testing."""
    return "xlerobot-npu-converter:latest"


@pytest.fixture
def test_docker_build():
    """Fixture to test Docker image build."""
    image_name = "xlerobot-test:latest"
    project_root = Path(__file__).parent.parent

    # Build Docker image
    result = subprocess.run(
        ["docker", "build", "-t", image_name, str(project_root)],
        capture_output=True,
        text=True,
        cwd=project_root
    )

    if result.returncode != 0:
        pytest.fail(f"Docker build failed: {result.stderr}")

    yield image_name

    # Cleanup
    subprocess.run(["docker", "rmi", image_name], capture_output=True)


@pytest.fixture
def running_container(test_docker_build):
    """Fixture to run a container for testing."""
    container_id = None
    try:
        # Start container
        result = subprocess.run(
            ["docker", "run", "-d", test_docker_build],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            pytest.fail(f"Failed to start container: {result.stderr}")

        container_id = result.stdout.strip()
        yield container_id

    finally:
        if container_id:
            # Stop and remove container
            subprocess.run(["docker", "stop", container_id], capture_output=True)
            subprocess.run(["docker", "rm", container_id], capture_output=True)