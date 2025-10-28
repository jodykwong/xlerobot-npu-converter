"""
Unit tests for AC3: Five-Dimensional Quality Assurance System

Tests the five-dimensional quality scoring system:
1. Structure Integrity
2. Numerical Validity
3. Compatibility
4. Performance Benchmark
5. Conversion Readiness
"""

import unittest
from unittest.mock import Mock

# Import using importlib to avoid onnx dependency issues
import importlib.util
import sys

def load_module(module_path, module_name):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Load the quality_scorer module
quality_scorer = load_module(
    "src/npu_converter/validation/quality_scorer.py",
    "quality_scorer"
)

QualityScorer = quality_scorer.QualityScorer
QualityScore = quality_scorer.QualityScore
QualityScoringResult = quality_scorer.QualityScoringResult
DimensionMetrics = quality_scorer.DimensionMetrics


class TestAC3QualityScorer(unittest.TestCase):
    """Test cases for AC3 Five-Dimensional Quality Scoring"""

    def setUp(self):
        """Set up test fixtures"""
        self.scorer = QualityScorer()

    def test_init(self):
        """Test QualityScorer initialization"""
        self.assertIsInstance(self.scorer, QualityScorer)
        self.assertIsNotNone(self.scorer.structure_validator)
        self.assertIsNotNone(self.scorer.dynamic_shape_handler)
        self.assertIsNotNone(self.scorer.compatibility_analyzer)

    def test_quality_score_dataclass(self):
        """Test QualityScore dataclass"""
        score = QualityScore(
            dimension="test",
            score=0.85,
            description="Test score",
            weight=0.2
        )
        self.assertEqual(score.dimension, "test")
        self.assertEqual(score.score, 0.85)
        self.assertEqual(score.weight, 0.2)

    def test_dimension_metrics_dataclass(self):
        """Test DimensionMetrics dataclass"""
        metrics = DimensionMetrics(
            dimension="structure",
            score=0.9,
            metrics={"node_count": 100},
            issues=[],
            warnings=[]
        )
        self.assertEqual(metrics.dimension, "structure")
        self.assertEqual(metrics.score, 0.9)
        self.assertIn("node_count", metrics.metrics)

    def test_calculate_grade(self):
        """Test grade calculation"""
        grade_a = self.scorer._calculate_grade(0.95)
        self.assertEqual(grade_a, "A")

        grade_b = self.scorer._calculate_grade(0.85)
        self.assertEqual(grade_b, "B")

        grade_c = self.scorer._calculate_grade(0.75)
        self.assertEqual(grade_c, "C")

        grade_d = self.scorer._calculate_grade(0.65)
        self.assertEqual(grade_d, "D")

    def test_score_structure_integrity(self):
        """Test structure integrity scoring"""
        # Mock model and structure result
        model = Mock()
        structure_result = Mock()
        structure_result.is_valid = True
        structure_result.orphaned_nodes = []
        structure_result.unused_weights = []
        structure_result.dependency_analysis = None

        score = self.scorer._score_structure_integrity(model, structure_result)

        self.assertIsInstance(score, QualityScore)
        self.assertEqual(score.dimension, "structure_integrity")
        self.assertGreater(score.score, 0.0)
        self.assertLessEqual(score.score, 1.0)
        self.assertEqual(score.weight, 0.25)

    def test_score_numerical_validity(self):
        """Test numerical validity scoring"""
        model = Mock()
        model.model_proto = Mock()
        model.model_proto.graph = Mock()
        model.model_proto.graph.initializer = []

        structure_result = Mock()
        structure_result.node_count = 100

        score = self.scorer._score_numerical_validity(model, structure_result)

        self.assertIsInstance(score, QualityScore)
        self.assertEqual(score.dimension, "numerical_validity")
        self.assertGreater(score.score, 0.0)
        self.assertLessEqual(score.score, 1.0)

    def test_score_compatibility(self):
        """Test compatibility scoring"""
        model = Mock()
        compatibility_result = Mock()
        compatibility_result.confidence_score = 0.9
        compatibility_result.compatible = True
        compatibility_result.issues = []
        compatibility_result.warnings = []

        score = self.scorer._score_compatibility(model, compatibility_result)

        self.assertIsInstance(score, QualityScore)
        self.assertEqual(score.dimension, "compatibility")
        self.assertGreater(score.score, 0.0)
        self.assertLessEqual(score.score, 1.0)

    def test_score_performance(self):
        """Test performance scoring"""
        model = Mock()

        structure_result = Mock()
        structure_result.node_count = 100
        structure_result.edge_count = 200

        dynamic_result = Mock()
        dynamic_result.total_dynamic_dims = 2
        dynamic_result.batch_independent = True
        dynamic_result.has_unsupported_dynamic_dims = False

        score = self.scorer._score_performance(model, structure_result, dynamic_result)

        self.assertIsInstance(score, QualityScore)
        self.assertEqual(score.dimension, "performance")
        self.assertIn("node_count", score.details)
        self.assertIn("dynamic_dims", score.details)

    def test_score_conversion_readiness(self):
        """Test conversion readiness scoring"""
        model = Mock()

        structure_result = Mock()
        structure_result.is_valid = True
        structure_result.issues = []
        structure_result.dependency_analysis = Mock()
        structure_result.dependency_analysis.topological_order = [1, 2, 3]

        dynamic_result = Mock()
        dynamic_result.has_unsupported_dynamic_dims = False
        dynamic_result.errors = []

        compatibility_result = Mock()
        compatibility_result.compatible = True
        compatibility_result.issues = []

        score = self.scorer._score_conversion_readiness(
            model, structure_result, dynamic_result, compatibility_result
        )

        self.assertIsInstance(score, QualityScore)
        self.assertEqual(score.dimension, "conversion_readiness")
        self.assertIn("structure_ready", score.details)

    def test_compile_dimension_metrics(self):
        """Test dimension metrics compilation"""
        structure_result = Mock()
        structure_result.is_valid = True
        structure_result.node_count = 100
        structure_result.edge_count = 200
        structure_result.orphaned_nodes = []
        structure_result.unused_weights = []
        structure_result.issues = []
        structure_result.warnings = []

        dynamic_result = Mock()
        dynamic_result.total_dynamic_dims = 1
        dynamic_result.batch_independent = True
        dynamic_result.has_unsupported_dynamic_dims = False
        dynamic_result.errors = []
        dynamic_result.warnings = []

        compatibility_result = Mock()
        compatibility_result.confidence_score = 0.9
        compatibility_result.compatible = True
        compatibility_result.issues = []
        compatibility_result.warnings = []

        metrics = self.scorer._compile_dimension_metrics(
            structure_result, dynamic_result, compatibility_result
        )

        self.assertIsInstance(metrics, list)
        self.assertGreater(len(metrics), 0)
        for metric in metrics:
            self.assertIsInstance(metric, DimensionMetrics)

    def test_generate_recommendations(self):
        """Test recommendation generation"""
        # Create low-scoring dimension
        low_score = QualityScore(
            dimension="structure_integrity",
            score=0.6,  # Below threshold
            description="Poor structure",
            weight=0.25
        )

        high_score = QualityScore(
            dimension="compatibility",
            score=0.9,  # Above threshold
            description="Good compatibility",
            weight=0.25
        )

        dimension_scores = [low_score, high_score]
        dimension_metrics = []

        recommendations = self.scorer._generate_recommendations(dimension_scores, dimension_metrics)

        self.assertIsInstance(recommendations, list)
        # Should have recommendations for low-scoring dimension
        self.assertGreater(len(recommendations), 0)

    def test_identify_critical_issues(self):
        """Test critical issue identification"""
        # Create metric with low score (critical)
        critical_metric = DimensionMetrics(
            dimension="structure",
            score=0.4,  # Critical threshold
            metrics={},
            issues=["Circular dependency detected"],
            warnings=[]
        )

        normal_metric = DimensionMetrics(
            dimension="compatibility",
            score=0.8,  # Normal
            metrics={},
            issues=[],
            warnings=[]
        )

        dimension_metrics = [critical_metric, normal_metric]

        critical_issues = self.scorer._identify_critical_issues([], dimension_metrics)

        self.assertIsInstance(critical_issues, list)
        self.assertGreater(len(critical_issues), 0)
        self.assertIn("Circular dependency detected", str(critical_issues))

    def test_generate_optimization_suggestions(self):
        """Test optimization suggestion generation"""
        # Create medium-scoring dimension (needs optimization)
        medium_score = QualityScore(
            dimension="performance",
            score=0.8,  # Medium range
            description="Good performance",
            weight=0.15
        )

        high_score = QualityScore(
            dimension="compatibility",
            score=0.95,
            description="Excellent",
            weight=0.25
        )

        dimension_scores = [medium_score, high_score]
        dimension_metrics = []

        suggestions = self.scorer._generate_optimization_suggestions(dimension_scores, dimension_metrics)

        self.assertIsInstance(suggestions, list)
        # Should have suggestions for medium-scoring dimension
        self.assertGreater(len(suggestions), 0)

    def test_export_quality_report(self):
        """Test quality report export"""
        # Create mock result
        result = Mock()
        result.overall_score = 0.85
        result.overall_grade = "B"
        result.conversion_readiness = 0.8
        result.dimension_scores = []
        result.critical_issues = []
        result.recommendations = []
        result.optimization_suggestions = []

        report = self.scorer.export_quality_report(result)

        self.assertIsInstance(report, dict)
        self.assertIn("overall_score", report)
        self.assertIn("overall_grade", report)
        self.assertIn("conversion_readiness", report)
        self.assertEqual(report["overall_score"], 0.85)
        self.assertEqual(report["overall_grade"], "B")


if __name__ == "__main__":
    unittest.main()
