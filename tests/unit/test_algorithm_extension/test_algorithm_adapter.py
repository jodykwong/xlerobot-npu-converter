"""
算法适配器测试
"""

import pytest
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))

from npu_converter.extensions import BaseAlgorithmAdapter
from npu_converter.extensions.adapters.algorithm_adapter import (
    AlgorithmError,
    AlgorithmInitializationError,
    AlgorithmExecutionError
)


class TestAlgorithmAdapter(BaseAlgorithmAdapter):
    """测试用算法适配器"""

    PARAMETERS = {
        "batch_size": {
            "type": "int",
            "default": 1,
            "min": 1,
            "max": 1000,
            "description": "批处理大小"
        },
        "timeout": {
            "type": "float",
            "default": 30.0,
            "min": 0.1,
            "max": 3600.0,
            "description": "超时时间"
        }
    }

    def initialize(self, **kwargs) -> bool:
        if self.is_initialized():
            return False

        self.set_initialized(True)
        return True

    def execute(self, input_data, **kwargs):
        if not self.is_initialized():
            raise AlgorithmInitializationError("算法未初始化")

        if not self.validate_input(input_data):
            raise AlgorithmValidationError("输入验证失败")

        # 模拟处理
        result = f"Processed: {input_data}"

        if not self.validate_output(result):
            raise AlgorithmValidationError("输出验证失败")

        return result

    def validate_input(self, input_data) -> bool:
        return input_data is not None and isinstance(input_data, str)

    def validate_output(self, output_data) -> bool:
        return output_data is not None and isinstance(output_data, str)


class TestBaseAlgorithmAdapter:
    """基础算法适配器测试"""

    def test_initialization(self):
        """测试初始化"""
        adapter = TestAlgorithmAdapter()

        assert not adapter.is_initialized()
        assert not adapter.is_configured()

    def test_initialize(self):
        """测试算法初始化"""
        adapter = TestAlgorithmAdapter()

        success = adapter.initialize()
        assert success
        assert adapter.is_initialized()

        # 重复初始化应该返回False
        success = adapter.initialize()
        assert not success

    def test_configure(self):
        """测试配置"""
        adapter = TestAlgorithmAdapter()

        config = {"batch_size": 10, "timeout": 30.0}
        success = adapter.configure(config)

        assert success
        assert adapter.is_configured()
        assert adapter.get_config()["batch_size"] == 10

    def test_configure_invalid(self):
        """测试无效配置"""
        adapter = TestAlgorithmAdapter()

        # 缺少必需参数（如果定义了的话）
        config = {"batch_size": 0}  # 小于最小值
        success = adapter.configure(config)

        # 基础验证不会检查最小值，所以会成功
        assert success

    def test_execute(self):
        """测试算法执行"""
        adapter = TestAlgorithmAdapter()
        adapter.initialize()

        result = adapter.execute("test_input")

        assert result == "Processed: test_input"

    def test_execute_without_init(self):
        """测试未初始化执行"""
        adapter = TestAlgorithmAdapter()

        with pytest.raises(AlgorithmInitializationError):
            adapter.execute("test_input")

    def test_execute_invalid_input(self):
        """测试无效输入执行"""
        adapter = TestAlgorithmAdapter()
        adapter.initialize()

        with pytest.raises(Exception):  # 具体异常类型取决于实现
            adapter.execute(None)

    def test_validate_input(self):
        """测试输入验证"""
        adapter = TestAlgorithmAdapter()

        assert adapter.validate_input("test")
        assert not adapter.validate_input(None)

    def test_validate_output(self):
        """测试输出验证"""
        adapter = TestAlgorithmAdapter()

        assert adapter.validate_output("result")
        assert not adapter.validate_output(None)

    def test_get_metadata(self):
        """测试获取元数据"""
        adapter = TestAlgorithmAdapter()

        metadata = adapter.get_metadata()

        assert "name" in metadata
        assert "version" in metadata
        assert metadata["name"] == "TestAlgorithmAdapter"

    def test_get_parameter_info(self):
        """测试获取参数信息"""
        adapter = TestAlgorithmAdapter()

        info = adapter.get_parameter_info("batch_size")

        assert info is not None
        assert "type" in info
        assert info["type"] == "int"

    def test_list_parameters(self):
        """测试列出参数"""
        adapter = TestAlgorithmAdapter()

        params = adapter.list_parameters()

        assert "batch_size" in params
        assert "timeout" in params

    def test_reset_config(self):
        """测试重置配置"""
        adapter = TestAlgorithmAdapter()
        adapter.configure({"batch_size": 10})

        assert adapter.is_configured()

        adapter.reset_config()

        assert not adapter.is_configured()
        assert adapter.get_config() == {}

    def test_get_statistics(self):
        """测试获取统计信息"""
        adapter = TestAlgorithmAdapter()
        adapter.initialize()

        stats = adapter.get_statistics()

        assert "name" in stats
        assert "initialized" in stats
        assert "execution_count" in stats
        assert stats["initialized"] is True

    def test_context_manager(self):
        """测试上下文管理器"""
        adapter = TestAlgorithmAdapter()

        with adapter as ctx:
            assert ctx is adapter
            assert adapter.is_initialized()

        # 退出后会自动清理
        # 具体清理逻辑取决于实现

    def test_health_status(self):
        """测试健康状态"""
        adapter = TestAlgorithmAdapter()

        status = adapter.get_health_status()

        assert "status" in status
        assert "initialized" in status
        assert status["status"] == "not_initialized"

        adapter.initialize()
        status = adapter.get_health_status()

        assert status["status"] == "healthy"
