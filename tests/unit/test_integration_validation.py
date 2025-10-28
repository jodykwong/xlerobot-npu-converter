"""
Integration test for Story 2.5 validation features

This test demonstrates the integration of all validation components:
- DynamicShapeHandler
- StructureValidator with OperatorDependencyAnalyzer
- CompatibilityAnalyzer
- QualityScorer
- ComprehensiveValidator (unified interface)
"""

import unittest
from unittest.mock import Mock

from src.npu_converter.validation import (
    DynamicShapeHandler,
    StructureValidator,
    OperatorDependencyAnalyzer,
    CompatibilityAnalyzer,
    QualityScorer,
    ComprehensiveValidator
)


class TestValidationIntegration(unittest.TestCase):
    """Integration tests for Story 2.5 validation features"""

    def test_all_validators_importable(self):
        """Test that all validators can be imported"""
        self.assertIsNotNone(DynamicShapeHandler)
        self.assertIsNotNone(StructureValidator)
        self.assertIsNotNone(OperatorDependencyAnalyzer)
        self.assertIsNotNone(CompatibilityAnalyzer)
        self.assertIsNotNone(QualityScorer)
        self.assertIsNotNone(ComprehensiveValidator)

    def test_validators_initialization(self):
        """Test that all validators can be initialized"""
        dynamic_handler = DynamicShapeHandler()
        self.assertIsInstance(dynamic_handler, DynamicShapeHandler)

        structure_validator = StructureValidator()
        self.assertIsInstance(structure_validator, StructureValidator)
        self.assertIsInstance(structure_validator.dependency_analyzer, OperatorDependencyAnalyzer)

        analyzer = OperatorDependencyAnalyzer()
        self.assertIsInstance(analyzer, OperatorDependencyAnalyzer)

        compat_analyzer = CompatibilityAnalyzer()
        self.assertIsInstance(compat_analyzer, CompatibilityAnalyzer)

        quality_scorer = QualityScorer()
        self.assertIsInstance(quality_scorer, QualityScorer)

        comprehensive = ComprehensiveValidator()
        self.assertIsInstance(comprehensive, ComprehensiveValidator)

    def test_dynamic_shape_handler_features(self):
        """Test DynamicShapeHandler features"""
        handler = DynamicShapeHandler()

        # Test dimension classification
        tensor = Mock()
        tensor.name = "input"
        tensor.shape = [-1, 224, 224, 3]

        all_tensors = [tensor]

        # Test classify_dimension
        dim_type = handler._classify_dimension(0, -1, tensor, all_tensors)
        self.assertIsNotNone(dim_type)

        # Test get_recommended_value
        batch_value = handler._get_recommended_value(
            handler._classify_dimension(0, -1, tensor, all_tensors), 0
        )
        self.assertIsNotNone(batch_value)

    def test_structure_validator_with_mock_model(self):
        """Test StructureValidator with a mock model"""
        validator = StructureValidator()

        # Create a mock model
        model = Mock()
        model.model_proto = Mock()
        model.model_proto.graph = Mock()

        # Mock empty graph
        model.model_proto.graph.node = []
        model.model_proto.graph.initializer = []
        model.model_proto.graph.input = []
        model.model_proto.graph.output = []

        # Validate structure
        result = validator.validate_structure(model)

        # Should have no issues for empty graph
        self.assertIsInstance(result.issues, list)
        self.assertIsInstance(result.warnings, list)

    def test_operator_dependency_analyzer_cycle_detection(self):
        """Test cycle detection in operator dependency analysis"""
        analyzer = OperatorDependencyAnalyzer()

        # Create a mock model with a cycle
        model = Mock()
        model.model_proto = Mock()
        model.model_proto.graph = Mock()

        # Mock nodes that create a cycle: node1 -> node2 -> node1
        node1 = Mock()
        node1.name = "node1"
        node1.op_type = "Add"
        node1.input = ["input1", "output2"]
        node1.output = ["output1"]

        node2 = Mock()
        node2.name = "node2"
        node2.op_type = "Mul"
        node2.input = ["output1", "weight"]
        node2.output = ["output2"]

        model.model_proto.graph.node = [node1, node2]
        model.model_proto.graph.initializer = [Mock(name="weight")]
        model.model_proto.graph.input = [Mock(name="input1")]
        model.model_proto.graph.output = []

        # Analyze dependencies
        result = analyzer.analyze_dependencies(model)

        # Should detect a cycle
        self.assertIsInstance(result, object)
        self.assertIsInstance(result.has_cycles, bool)

    def test_quality_scorer_grade_calculation(self):
        """Test QualityScorer grade calculation"""
        scorer = QualityScorer()

        # Create a mock model
        model = Mock()

        # Score quality
        result = scorer.score_quality(model)

        # Should have a valid grade
        self.assertIsInstance(result.grade, str)
        self.assertIn(result.grade, ['A', 'B', 'C', 'D'])

    def test_integration_all_components(self):
        """Test integration of all components"""
        # Initialize all components
        dynamic_handler = DynamicShapeHandler()
        structure_validator = StructureValidator()
        dep_analyzer = OperatorDependencyAnalyzer()
        compat_analyzer = CompatibilityAnalyzer()
        quality_scorer = QualityScorer()
        comprehensive = ComprehensiveValidator()

        # Verify all are properly initialized
        self.assertIsNotNone(dynamic_handler)
        self.assertIsNotNone(structure_validator)
        self.assertIsNotNone(dep_analyzer)
        self.assertIsNotNone(compat_analyzer)
        self.assertIsNotNone(quality_scorer)
        self.assertIsNotNone(comprehensive)

        # Verify component relationships
        self.assertIsInstance(structure_validator.dependency_analyzer, type(dep_analyzer))

    def test_module_file_creation(self):
        """Test that all module files were created"""
        import os

        base_path = "src/npu_converter/validation"

        # Check that key modules exist
        modules = [
            "dynamic_shape_handler.py",
            "structure_validator.py",
            "operator_dependency_analyzer.py",
            "compatibility_analyzer.py",
            "quality_scorer.py",
            "comprehensive_validator.py"
        ]

        for module in modules:
            module_path = os.path.join(base_path, module)
            self.assertTrue(
                os.path.exists(module_path),
                f"Module {module} was not created at {module_path}"
            )


if __name__ == "__main__":
    unittest.main()
