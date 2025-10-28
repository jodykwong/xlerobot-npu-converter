"""
算法扩展系统测试
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))

from npu_converter.extensions import (
    AlgorithmExtensionSystem,
    AlgorithmRegistry,
    AlgorithmConfigManager,
    AlgorithmLifecycle,
    BaseAlgorithmAdapter
)


class DummyAlgorithmAdapter(BaseAlgorithmAdapter):
    """测试用算法适配器"""

    def initialize(self, **kwargs) -> bool:
        self.set_initialized(True)
        return True

    def execute(self, input_data, **kwargs):
        if not self.is_initialized():
            raise Exception("算法未初始化")
        return f"Processed: {input_data}"

    def validate_input(self, input_data) -> bool:
        return input_data is not None

    def validate_output(self, output_data) -> bool:
        return output_data is not None


class TestAlgorithmExtensionSystem:
    """算法扩展系统测试"""

    def setup_method(self):
        """测试前准备"""
        self.system = AlgorithmExtensionSystem()

    def test_initialization(self):
        """测试系统初始化"""
        assert not self.system._initialized

        self.system.initialize()
        assert self.system._initialized

    def test_register_algorithm(self):
        """测试算法注册"""
        self.system.initialize()

        success = self.system.register_algorithm(
            "dummy",
            DummyAlgorithmAdapter,
            {"description": "测试算法"}
        )

        assert success
        assert "dummy" in self.system.list_algorithms()

    def test_unregister_algorithm(self):
        """测试算法注销"""
        self.system.initialize()
        self.system.register_algorithm("dummy", DummyAlgorithmAdapter)

        success = self.system.unregister_algorithm("dummy")

        assert success
        assert "dummy" not in self.system.list_algorithms()

    def test_get_algorithm(self):
        """测试获取算法实例"""
        self.system.initialize()
        self.system.register_algorithm("dummy", DummyAlgorithmAdapter)

        algorithm = self.system.get_algorithm("dummy")
        assert algorithm is not None
        assert isinstance(algorithm, DummyAlgorithmAdapter)

    def test_execute_algorithm(self):
        """测试算法执行"""
        self.system.initialize()
        self.system.register_algorithm("dummy", DummyAlgorithmAdapter)

        result = self.system.execute_algorithm("dummy", "test_input")

        assert result == "Processed: test_input"

    def test_configure_algorithm(self):
        """测试算法配置"""
        self.system.initialize()
        self.system.register_algorithm("dummy", DummyAlgorithmAdapter)

        config = {"batch_size": 10, "timeout": 30.0}
        success = self.system.configure_algorithm("dummy", config)

        assert success

    def test_lifecycle_listeners(self):
        """测试生命周期监听器"""
        self.system.initialize()

        events = []
        def listener(context):
            events.append(context)

        self.system.add_lifecycle_listener("before_initialize", listener)
        self.system.emit_event("before_initialize", {"test": "data"})

        assert len(events) == 1
        assert events[0]["test"] == "data"

    def test_statistics(self):
        """测试统计信息"""
        self.system.initialize()

        stats = self.system.get_statistics()
        assert "initialized" in stats
        assert "registered_algorithms" in stats
        assert stats["initialized"] is True
