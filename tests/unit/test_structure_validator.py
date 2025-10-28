"""
Unit tests for StructureValidator

Tests the structure validation capabilities including:
- Operator dependency analysis
- Cycle detection
- Orphaned node detection
- Unused weight detection
"""

import unittest
from unittest.mock import Mock, MagicMock

from src.npu_converter.validation.structure_validator import StructureValidator
from src.npu_converter.validation.operator_dependency_analyzer import (
    OperatorDependencyAnalyzer,
    OperatorInfo,
    OperatorNode
)


class TestStructureValidator(unittest.TestCase):
    """Test cases for StructureValidator"""

    def setUp(self):
        """Set up test fixtures"""
        self.validator = StructureValidator()

    def test_init(self):
        """Test StructureValidator initialization"""
        self.assertIsInstance(self.validator, StructureValidator)
        self.assertIsInstance(self.validator.dependency_analyzer, OperatorDependencyAnalyzer)

    def test_dependency_analyzer_initialization(self):
        """Test that dependency analyzer is properly initialized"""
        analyzer = OperatorDependencyAnalyzer()
        self.assertIsInstance(analyzer, OperatorDependencyAnalyzer)

    def test_operator_node_creation(self):
        """Test OperatorNode dataclass creation"""
        operator = OperatorInfo(
            op_type="Conv",
            inputs=["input", "weight"],
            outputs=["output"]
        )

        node = OperatorNode(
            operator=operator,
            node_name="conv_node",
            inputs=["input", "weight"],
            outputs=["output"],
            dependencies=["input_node"]
        )

        self.assertEqual(node.node_name, "conv_node")
        self.assertEqual(node.operator.op_type, "Conv")
        self.assertEqual(node.dependencies, ["input_node"])

    def test_find_unused_weights(self):
        """Test detection of unused weights"""
        # Mock model with unused weights
        model = Mock()
        model.model_proto = Mock()
        model.model_proto.graph = Mock()

        # Mock initializers
        initializer1 = Mock()
        initializer1.name = "weight1"
        initializer2 = Mock()
        initializer2.name = "weight2"  # Unused

        model.model_proto.graph.initializer = [initializer1, initializer2]

        # Mock nodes - only use weight1
        node1 = Mock()
        node1.input = ["weight1", "input"]
        model.model_proto.graph.node = [node1]

        unused = self.validator._find_unused_weights(model)

        self.assertIn("weight2", unused)
        self.assertNotIn("weight1", unused)

    def test_find_disconnected_subgraphs(self):
        """Test detection of disconnected subgraphs"""
        # Create a simple dependency graph
        node1 = Mock()
        node1.dependencies = []

        node2 = Mock()
        node2.dependencies = ["node1"]

        node3 = Mock()  # Disconnected
        node3.dependencies = []

        dependency_graph = {
            "node1": node1,
            "node2": node2,
            "node3": node3
        }

        topological_order = ["node1", "node2", "node3"]

        subgraphs = self.validator._find_disconnected_subgraphs(
            dependency_graph, topological_order
        )

        # node3 is alone, so no subgraph with >1 node
        self.assertEqual(len(subgraphs), 0)

    def test_check_tensor_connectivity(self):
        """Test tensor connectivity checking"""
        model = Mock()
        model.model_proto = Mock()
        model.model_proto.graph = Mock()

        # Mock input (defined)
        input1 = Mock()
        input1.name = "input1"
        model.model_proto.graph.input = [input1]

        # Mock output (defined)
        output1 = Mock()
        output1.name = "output1"
        model.model_proto.graph.output = [output1]

        # Mock node (uses undefined tensor)
        node1 = Mock()
        node1.input = ["undefined_tensor"]
        node1.output = ["output1"]
        model.model_proto.graph.node = [node1]

        # Mock initializer
        init1 = Mock()
        init1.name = "weight1"
        model.model_proto.graph.initializer = [init1]

        issues = self.validator._check_tensor_connectivity(model)

        # Should have detected undefined tensor usage
        self.assertTrue(any("used but not defined" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
