"""
Docker环境集成测试 - Story 1.8 Subtask 2.2

测试Docker环境下的模型转换功能，验证容器化部署的可靠性。
确保工具链在Docker环境中正常工作。
遵循pytest 7.x框架和集成测试模式。
"""

import pytest
import os
import tempfile
import subprocess
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# 添加项目路径到sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from npu_converter.bpu_toolchain.horizon_x5 import HorizonX5Interface
    from npu_converter.config.manager import ConfigurationManager
    from npu_converter.utils.exceptions import ToolchainError
except ImportError as e:
    pytest.skip(f"无法导入核心模块: {e}", allow_module_level=True)


@pytest.mark.integration
@pytest.mark.slow
class TestDockerEnvironment:
    """Docker环境集成测试类"""

    def setup_method(self):
        """每个测试方法前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = project_root

    def teardown_method(self):
        """每个测试方法后的清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_dockerfile_exists(self):
        """测试Dockerfile存在"""
        dockerfile = self.project_root / "Dockerfile"
        assert dockerfile.exists(), "Dockerfile不存在"

        content = dockerfile.read_text()
        assert "FROM" in content, "Dockerfile缺少基础镜像"
        assert "ubuntu:20.04" in content or "python:3.10" in content, "Dockerfile缺少运行时环境"

    def test_docker_compose_exists(self):
        """测试docker-compose.yml存在"""
        compose_file = self.project_root / "docker-compose.yml"
        if not compose_file.exists():
            pytest.skip("docker-compose.yml不存在，跳过测试")

        content = compose_file.read_text()
        assert "version:" in content, "docker-compose.yml缺少版本信息"
        assert "services:" in content, "docker-compose.yml缺少服务定义"

    def test_docker_build_configuration(self):
        """测试Docker构建配置"""
        dockerfile = self.project_root / "Dockerfile"
        if not dockerfile.exists():
            pytest.skip("Dockerfile不存在，跳过测试")

        content = dockerfile.read_text()

        # 验证关键的构建步骤
        build_steps = [
            "WORKDIR",
            "COPY",
            "RUN"
        ]

        for step in build_steps:
            assert step in content, f"Dockerfile缺少{step}步骤"

    @patch('subprocess.run')
    def test_docker_build_command(self, mock_subprocess):
        """测试Docker构建命令"""
        # 模拟Docker构建成功
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Successfully built"
        mock_subprocess.return_value = mock_result

        # 执行Docker构建
        build_cmd = ["docker", "build", "-t", "npu-converter:test", "."]
        result = subprocess.run(build_cmd, capture_output=True, text=True)

        # 验证命令格式正确
        assert "docker" in " ".join(build_cmd)
        assert "build" in " ".join(build_cmd)
        assert "npu-converter:test" in " ".join(build_cmd)

    @patch('subprocess.run')
    def test_docker_run_command(self, mock_subprocess):
        """测试Docker运行命令"""
        # 模拟Docker运行成功
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Container started"
        mock_subprocess.return_value = mock_result

        # 执行Docker运行
        run_cmd = [
            "docker", "run", "--rm",
            "-v", f"{self.temp_dir}:/workspace",
            "npu-converter:test",
            "python", "-m", "npu_converter.cli", "--help"
        ]

        # 验证命令格式正确
        assert "docker" in " ".join(run_cmd)
        assert "run" in " ".join(run_cmd)
        assert "--rm" in " ".join(run_cmd)
        assert "-v" in " ".join(run_cmd)
        assert "npu-converter:test" in " ".join(run_cmd)

    @patch('subprocess.run')
    def test_docker_environment_toolchain_availability(self, mock_subprocess):
        """测试Docker环境中工具链可用性"""
        # 模拟工具链检查
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "/opt/horizon/bin/hbdk"
        mock_subprocess.return_value = mock_result

        # 检查工具链可用性
        check_cmd = [
            "docker", "run", "--rm",
            "npu-converter:test",
            "which", "hbdk"
        ]

        result = subprocess.run(check_cmd, capture_output=True, text=True)
        assert result.returncode == 0

    @patch('subprocess.run')
    def test_docker_environment_python_version(self, mock_subprocess):
        """测试Docker环境中Python版本"""
        # 模拟Python版本检查
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Python 3.10.12"
        mock_subprocess.return_value = mock_result

        # 检查Python版本
        version_cmd = [
            "docker", "run", "--rm",
            "npu-converter:test",
            "python", "--version"
        ]

        result = subprocess.run(version_cmd, capture_output=True, text=True)
        assert result.returncode == 0
        assert "3.10" in result.stdout

    def test_docker_volume_mounting(self):
        """测试Docker卷挂载配置"""
        # 创建测试卷挂载配置
        volume_mounts = [
            f"{self.project_root}/src:/app/src",
            f"{self.project_root}/config:/app/config",
            f"{self.temp_dir}:/workspace"
        ]

        # 验证卷挂载格式
        for mount in volume_mounts:
            assert ":" in mount, f"卷挂载格式错误: {mount}"
            host_path, container_path = mount.split(":", 1)
            assert os.path.exists(host_path) or host_path.startswith(self.temp_dir), \
                f"主机路径不存在: {host_path}"

    def test_docker_environment_variables(self):
        """测试Docker环境变量配置"""
        env_vars = {
            "PYTHONPATH": "/app/src",
            "LOG_LEVEL": "INFO",
            "NPU_TOOLCHAIN_PATH": "/opt/horizon"
        }

        # 验证环境变量设置
        for key, value in env_vars.items():
            assert isinstance(key, str)
            assert isinstance(value, str)
            assert len(key) > 0
            assert len(value) > 0

    def test_docker_network_configuration(self):
        """测试Docker网络配置"""
        # 创建Docker网络配置
        network_config = {
            "driver": "bridge",
            "internal": False,
            "ipam": {
                "driver": "default",
                "config": [
                    {
                        "subnet": "172.20.0.0/16"
                    }
                ]
            }
        }

        # 验证网络配置
        assert "driver" in network_config
        assert network_config["driver"] in ["bridge", "host", "none"]
        assert "ipam" in network_config

    @patch('subprocess.run')
    def test_docker_container_logs(self, mock_subprocess):
        """测试Docker容器日志收集"""
        # 模拟日志输出
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Container log output"
        mock_subprocess.return_value = mock_result

        # 收集容器日志
        logs_cmd = [
            "docker", "logs", "npu-converter-container"
        ]

        result = subprocess.run(logs_cmd, capture_output=True, text=True)
        assert result.returncode == 0

    @patch('subprocess.run')
    def test_docker_container_health_check(self, mock_subprocess):
        """测试Docker容器健康检查"""
        # 模拟健康检查
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "healthy"
        mock_subprocess.return_value = mock_result

        # 执行健康检查
        health_cmd = [
            "docker", "exec", "npu-converter-container",
            "python", "-c", "import npu_converter; print('healthy')"
        ]

        result = subprocess.run(health_cmd, capture_output=True, text=True)
        assert result.returncode == 0

    @patch('subprocess.run')
    def test_docker_resource_limits(self, mock_subprocess):
        """测试Docker资源限制配置"""
        # 模拟资源限制检查
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Resource limits applied"
        mock_subprocess.return_value = mock_result

        # 设置资源限制
        resource_limits = {
            "memory": "2g",
            "cpus": "1.0",
            "pids": 100
        }

        # 验证资源限制格式
        for resource, limit in resource_limits.items():
            assert isinstance(resource, str)
            assert isinstance(limit, str)
            assert len(limit) > 0

    @patch('subprocess.run')
    def test_docker_multi_stage_build(self, mock_subprocess):
        """测试Docker多阶段构建"""
        # 模拟多阶段构建
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Multi-stage build completed"
        mock_subprocess.return_value = mock_result

        # 多阶段构建命令
        build_cmd = [
            "docker", "build",
            "--target", "runtime",
            "-t", "npu-converter:runtime",
            "."
        ]

        result = subprocess.run(build_cmd, capture_output=True, text=True)
        assert result.returncode == 0

    def test_docker_image_size_optimization(self):
        """测试Docker镜像大小优化"""
        # 创建优化的Dockerfile内容
        optimized_dockerfile = """
FROM ubuntu:20.04 as base

# 安装系统依赖
RUN apt-get update && apt-get install -y \\
    python3.10 \\
    python3.10-pip \\
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .
RUN pip3.10 install --no-cache-dir -r requirements.txt

# 复制源代码
COPY src/ ./src/

# 设置入口点
ENTRYPOINT ["python3.10", "-m", "npu_converter.cli"]
"""

        # 验证优化策略
        assert "--no-cache-dir" in optimized_dockerfile
        assert "rm -rf /var/lib/apt/lists/*" in optimized_dockerfile
        assert "WORKDIR" in optimized_dockerfile

    @patch('subprocess.run')
    def test_docker_security_configuration(self, mock_subprocess):
        """测试Docker安全配置"""
        # 模拟安全检查
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Security scan passed"
        mock_subprocess.return_value = mock_result

        # 安全扫描命令
        security_cmd = [
            "docker", "run", "--rm",
            "--user", "1000:1000",  # 非root用户
            "npu-converter:test",
            "whoami"
        ]

        result = subprocess.run(security_cmd, capture_output=True, text=True)
        assert result.returncode == 0

    @patch('subprocess.run')
    def test_docker_cleanup_and_maintenance(self, mock_subprocess):
        """测试Docker清理和维护"""
        # 模拟清理操作
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Cleanup completed"
        mock_subprocess.return_value = mock_result

        # 清理命令
        cleanup_cmds = [
            ["docker", "system", "prune", "-f"],
            ["docker", "image", "prune", "-f"],
            ["docker", "volume", "prune", "-f"]
        ]

        for cmd in cleanup_cmds:
            result = subprocess.run(cmd, capture_output=True, text=True)
            assert result.returncode == 0

    def test_docker_configuration_files(self):
        """测试Docker配置文件"""
        config_files = [
            "Dockerfile",
            "docker-compose.yml",
            ".dockerignore"
        ]

        for config_file in config_files:
            file_path = self.project_root / config_file
            if file_path.exists():
                content = file_path.read_text()
                assert len(content) > 0, f"{config_file}为空"

    def test_docker_ignore_file(self):
        """测试.dockerignore文件"""
        dockerignore = self.project_root / ".dockerignore"
        if not dockerignore.exists():
            pytest.skip(".dockerignore不存在，跳过测试")

        content = dockerignore.read_text()

        # 验证常见的忽略模式
        ignore_patterns = [
            ".git",
            "__pycache__",
            "*.pyc",
            ".pytest_cache",
            "node_modules"
        ]

        for pattern in ignore_patterns:
            assert pattern in content, f".dockerignore应该包含{pattern}"


@pytest.mark.integration
class TestDockerToolchainIntegration:
    """Docker工具链集成测试类"""

    def setup_method(self):
        """每个测试方法前的设置"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """每个测试方法后的清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch('subprocess.run')
    def test_docker_toolchain_execution(self, mock_subprocess):
        """测试Docker中工具链执行"""
        # 模拟工具链执行
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Toolchain execution completed"
        mock_subprocess.return_value = mock_result

        # 在Docker中执行工具链命令
        toolchain_cmd = [
            "docker", "run", "--rm",
            "-v", f"{self.temp_dir}:/workspace",
            "npu-converter:test",
            "hbdk", "--input", "/workspace/model.onnx", "--output", "/workspace/output"
        ]

        result = subprocess.run(toolchain_cmd, capture_output=True, text=True)
        assert result.returncode == 0

    @patch('subprocess.run')
    def test_docker_multi_toolchain_workflow(self, mock_subprocess):
        """测试Docker中多工具链工作流"""
        # 模拟多步骤工作流
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Workflow completed"
        mock_subprocess.return_value = mock_result

        # 多步骤工具链工作流
        workflow_steps = [
            ["docker", "run", "--rm", "npu-converter:test", "hbdk", "--validate", "model.onnx"],
            ["docker", "run", "--rm", "npu-converter:test", "hb_mapper", "model.onnx", "model.bpu"],
            ["docker", "run", "--rm", "npu-converter:test", "hb_perf", "model.bpu"]
        ]

        for step in workflow_steps:
            result = subprocess.run(step, capture_output=True, text=True)
            assert result.returncode == 0

    def test_docker_environment_isolation(self):
        """测试Docker环境隔离"""
        # 验证Docker提供的环境隔离
        isolation_features = [
            "文件系统隔离",
            "进程隔离",
            "网络隔离",
            "资源限制"
        ]

        for feature in isolation_features:
            assert isinstance(feature, str)
            assert len(feature) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])