"""
算法注册表测试
"""

import pytest
from unittest.mock import Mock
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))

from npu_converter.extensions import BaseAlgorithmAdapter
from npu_converter.extensions.algorithm_registry import AlgorithmRegistry


class DummyAlgorithmAdapter(BaseAlgorithmAdapter):
    """测试用算法适配器"""

    def initialize(self, **kwargs) -> bool:
        return True

    def execute(self, input_data, **kwargs):
        return f"Processed: {input_data}"

    def validate_input(self, input_data) -> bool:
        return input_data is not None

    def validate_output(self, output_data) -> bool:
        return output_data is not None


class TestAlgorithmRegistry:
    """算法注册表测试"""

    def setup_method(self):
        """测试前准备"""
        self.registry = AlgorithmRegistry()

    def test_initialization(self):
        """测试初始化"""
        assert self.registry.get_algorithm_count() == 0

    def test_register_algorithm(self):
        """测试算法注册"""
        success = self.registry.register(
            "dummy",
            DummyAlgorithmAdapter,
            {"description": "测试算法"}
        )

        assert success
        assert self.registry.get_algorithm_count() == 1
        assert "dummy" in self.registry.list_algorithms()

    def test_register_duplicate(self):
        """测试重复注册"""
        self.registry.register("dummy", DummyAlgorithmAdapter)

        # 重复注册应该成功但会覆盖
        success = self.registry.register(
            "dummy",
            DummyAlgorithmAdapter,
            {"description": "新描述"}
        )

        assert success

    def test_unregister_algorithm(self):
        """测试算法注销"""
        self.registry.register("dummy", DummyAlgorithmAdapter)

        success = self.registry.unregister("dummy")

        assert success
        assert self.registry.get_algorithm_count() == 0
        assert "dummy" not in self.registry.list_algorithms()

    def test_get_algorithm(self):
        """测试获取算法实例"""
        self.registry.register("dummy", DummyAlgorithmAdapter)

        algorithm = self.registry.get_algorithm("dummy")
        assert algorithm is not None
        assert isinstance(algorithm, DummyAlgorithmAdapter)

    def test_get_algorithm_info(self):
        """测试获取算法信息"""
        metadata = {"description": "测试算法"}
        self.registry.register("dummy", DummyAlgorithmAdapter, metadata)

        info = self.registry.get_algorithm_info("dummy")
        assert info is not None
        assert "description" in info

    def test_search_algorithms(self):
        """测试算法搜索"""
        self.registry.register("transformer", DummyAlgorithmAdapter, {"description": "变换算法"})
        self.registry.register("optimizer", DummyAlgorithmAdapter, {"description": "优化算法"})

        results = self.registry.search_algorithms("变换")
        assert "transformer" in results

        results = self.registry.search_algorithms("优化")
        assert "optimizer" in results

    def test_validate_algorithm(self):
        """测试算法验证"""
        self.registry.register("dummy", DummyAlgorithmAdapter, {"description": "测试算法"})

        result = self.registry.validate_algorithm("dummy")

        assert "valid" in result
        assert "errors" in result
        assert "warnings" in result

    def test_get_registry_status(self):
        """测试获取注册表状态"""
        self.registry.register("dummy", DummyAlgorithmAdapter)

        status = self.registry.get_registry_status()

        assert "total_algorithms" in status
        assert "algorithms" in status
        assert status["total_algorithms"] == 1

    def test_clear(self):
        """测试清空注册表"""
        self.registry.register("dummy1", DummyAlgorithmAdapter)
        self.registry.register("dummy2", DummyAlgorithmAdapter)

        assert self.registry.get_algorithm_count() == 2

        self.registry.clear()

        assert self.registry.get_algorithm_count() == 0
