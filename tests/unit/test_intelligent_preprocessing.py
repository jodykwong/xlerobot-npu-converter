"""
Unit tests for AC2: Intelligent Preprocessing Optimization System

Tests:
- IntelligentOptimizer
- StrategyRecommender
- Model type detection
- Strategy recommendation
- Optimization strategies
"""

import unittest
from unittest.mock import Mock, patch

# Import using importlib to avoid onnx dependency issues
import importlib.util
import sys

def load_module(module_path, module_name):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Load the modules
intelligent_optimizer = load_module(
    "src/npu_converter/preprocessing/enhanced/intelligent_optimizer.py",
    "intelligent_optimizer"
)

strategy_recommender = load_module(
    "src/npu_converter/preprocessing/enhanced/strategy_recommender.py",
    "strategy_recommender"
)

IntelligentOptimizer = intelligent_optimizer.IntelligentOptimizer
OptimizationStrategy = intelligent_optimizer.OptimizationStrategy
ModelType = intelligent_optimizer.ModelType
OptimizationResult = intelligent_optimizer.OptimizationResult

StrategyRecommender = strategy_recommender.StrategyRecommender
PreprocessingStrategy = strategy_recommender.PreprocessingStrategy
StrategyRecommendation = strategy_recommender.StrategyRecommendation
StrategyAnalysisResult = strategy_recommender.StrategyAnalysisResult


class TestIntelligentOptimizer(unittest.TestCase):
    """Test cases for IntelligentOptimizer"""

    def setUp(self):
        """Set up test fixtures"""
        self.optimizer = IntelligentOptimizer()

    def test_init(self):
        """Test IntelligentOptimizer initialization"""
        self.assertIsInstance(self.optimizer, IntelligentOptimizer)
        self.assertIsNotNone(self.optimizer.optimization_strategies)
        self.assertIsNotNone(self.optimizer.model_patterns)

    def test_model_type_classification(self):
        """Test model type classification"""
        # Mock model with vision operators
        model = Mock()
        model.model_proto = Mock()
        model.model_proto.graph = Mock()

        node1 = Mock()
        node1.op_type = "Conv"
        node2 = Mock()
        node2.op_type = "Relu"
        node3 = Mock()
        node3.op_type = "Pool"

        model.model_proto.graph.node = [node1, node2, node3]
        model.model_proto.graph.input = [Mock(name="image")]
        model.model_proto.graph.output = []

        model_type = self.optimizer._classify_model_type(model)

        self.assertEqual(model_type, ModelType.VISION)

    def test_extract_model_info(self):
        """Test model info extraction"""
        model = Mock()
        model.model_proto = Mock()
        model.model_proto.graph = Mock()

        node1 = Mock()
        node1.op_type = "Conv"
        node1.output = ["output1"]

        model.model_proto.graph.node = [node1]
        model.model_proto.graph.input = [Mock(name="input1")]
        model.model_proto.graph.output = [Mock(name="output1")]

        model_info = self.optimizer._extract_model_info(model)

        self.assertIn("operators", model_info)
        self.assertIn("tensor_names", model_info)
        self.assertEqual(model_info["operators"][0], "Conv")

    def test_generate_parameter_space_vision(self):
        """Test parameter space generation for vision models"""
        parameter_space = self.optimizer._generate_parameter_space(ModelType.VISION)

        self.assertIn("resize", parameter_space)
        self.assertIn("mean", parameter_space)
        self.assertGreater(len(parameter_space["resize"]), 0)

    def test_generate_parameter_space_nlp(self):
        """Test parameter space generation for NLP models"""
        parameter_space = self.optimizer._generate_parameter_space(ModelType.NLP)

        self.assertIn("normalize", parameter_space)
        self.assertIn("data_type", parameter_space)

    def test_optimize_preprocessing(self):
        """Test preprocessing optimization"""
        # Mock model
        model = Mock()

        # Mock base config
        base_config = Mock()
        base_config.normalize = False
        base_config.resize = None

        # Run optimization
        result = self.optimizer.optimize_preprocessing(
            model=model,
            current_config=base_config,
            strategy=OptimizationStrategy.RANDOM,
            max_iterations=10
        )

        self.assertIsInstance(result, OptimizationResult)
        self.assertGreater(result.iterations, 0)
        self.assertIsInstance(result.strategy, OptimizationStrategy)
        self.assertGreater(result.improvement_percentage, 0)

    def test_compare_strategies(self):
        """Test strategy comparison"""
        model = Mock()
        base_config = Mock()

        strategies = [
            OptimizationStrategy.BAYESIAN,
            OptimizationStrategy.GENETIC,
            OptimizationStrategy.RANDOM
        ]

        results = self.optimizer.compare_strategies(model, base_config, strategies)

        self.assertEqual(len(results), 3)
        for strategy_name in [s.value for s in strategies]:
            self.assertIn(strategy_name, results)
            self.assertIsInstance(results[strategy_name], OptimizationResult)


class TestStrategyRecommender(unittest.TestCase):
    """Test cases for StrategyRecommender"""

    def setUp(self):
        """Set up test fixtures"""
        self.recommender = StrategyRecommender()

    def test_init(self):
        """Test StrategyRecommender initialization"""
        self.assertIsInstance(self.recommender, StrategyRecommender)
        self.assertIsNotNone(self.recommender.strategy_database)

    def test_detect_model_type_vision(self):
        """Test vision model detection"""
        model = Mock()
        model.model_proto = Mock()
        model.model_proto.graph = Mock()

        node1 = Mock()
        node1.op_type = "Conv"

        model.model_proto.graph.node = [node1]
        model.model_proto.graph.input = [Mock(name="image_input")]
        model.model_proto.graph.output = []

        detected_type = self.recommender._detect_model_type(model)

        self.assertEqual(detected_type, "vision")

    def test_detect_model_type_nlp(self):
        """Test NLP model detection"""
        model = Mock()
        model.model_proto = Mock()
        model.model_proto.graph = Mock()

        node1 = Mock()
        node1.op_type = "Embedding"

        model.model_proto.graph.node = [node1]
        model.model_proto.graph.input = [Mock(name="token_ids")]
        model.model_proto.graph.output = []

        detected_type = self.recommender._detect_model_type(model)

        self.assertEqual(detected_type, "nlp")

    def test_recommend_strategy_vision(self):
        """Test strategy recommendation for vision models"""
        model = Mock()
        model.model_proto = Mock()
        model.model_proto.graph = Mock()

        model.model_proto.graph.node = []
        model.model_proto.graph.input = []
        model.model_proto.graph.output = []

        result = self.recommender.recommend_strategy(
            model=model,
            model_type="vision",
            target_metric="accuracy"
        )

        self.assertIsInstance(result, StrategyAnalysisResult)
        self.assertEqual(result.model_type, "vision")
        self.assertGreater(result.total_recommendations, 0)
        self.assertGreater(len(result.best_config), 0)

    def test_strategy_filtering(self):
        """Test strategy filtering by target metric"""
        strategies = {
            "default_strategies": [
                {
                    "strategy": PreprocessingStrategy.RESIZE,
                    "priority": 9,
                    "description": "Resize strategy"
                },
                {
                    "strategy": PreprocessingStrategy.NORMALIZE,
                    "priority": 10,
                    "description": "Normalize strategy"
                }
            ]
        }

        # Test accuracy target
        filtered = self.recommender._filter_strategies(strategies, "accuracy")
        self.assertEqual(len(filtered), 2)

        # Test latency target
        filtered = self.recommender._filter_strategies(strategies, "latency")
        self.assertLess(filtered[0]["priority"], 9)  # Should be reduced

    def test_create_recommendations(self):
        """Test recommendation creation"""
        strategies = [
            {
                "strategy": PreprocessingStrategy.NORMALIZE,
                "priority": 10,
                "description": "Normalize using ImageNet",
                "parameters": {"mean": [0.5, 0.5, 0.5]},
                "reasoning": "Standard for vision models"
            }
        ]

        recommendations = self.recommender._create_recommendations(strategies, "accuracy", Mock())

        self.assertEqual(len(recommendations), 1)
        self.assertIsInstance(recommendations[0], StrategyRecommendation)
        self.assertEqual(recommendations[0].strategy, PreprocessingStrategy.NORMALIZE)
        self.assertGreater(recommendations[0].expected_improvement, 0)

    def test_generate_best_config(self):
        """Test best configuration generation"""
        recommendations = [
            StrategyRecommendation(
                strategy=PreprocessingStrategy.NORMALIZE,
                priority=10,
                confidence=0.9,
                description="Normalize",
                parameters={"mean": [0.485, 0.456, 0.406]},
                expected_improvement=5.0,
                reasoning="Standard for vision"
            ),
            StrategyRecommendation(
                strategy=PreprocessingStrategy.RESIZE,
                priority=8,
                confidence=0.8,
                description="Resize",
                parameters={"size": (224, 224)},
                expected_improvement=3.0,
                reasoning="Required for input"
            )
        ]

        best_config = self.recommender._generate_best_config(recommendations)

        self.assertIn("normalize", best_config)
        self.assertIn("resize", best_config)

    def test_export_recommendations(self):
        """Test recommendations export"""
        result = StrategyAnalysisResult(
            model_type="vision",
            total_recommendations=2,
            recommendations=[
                StrategyRecommendation(
                    strategy=PreprocessingStrategy.NORMALIZE,
                    priority=10,
                    confidence=0.9,
                    description="Normalize",
                    parameters={},
                    expected_improvement=5.0,
                    reasoning="Test"
                )
            ],
            best_config={"normalize": True},
            warnings=[],
            notes=[]
        )

        export_data = self.recommender.export_recommendations(result)

        self.assertIn("model_type", export_data)
        self.assertIn("recommendations", export_data)
        self.assertIn("best_config", export_data)
        self.assertEqual(export_data["model_type"], "vision")


if __name__ == "__main__":
    unittest.main()
