"""
Unit tests for ParameterOptimizer.

Tests the main parameter optimization functionality including
optimization strategies, model analysis integration, and result processing.

Author: Story 2.6 Implementation
Version: 1.0.0
Date: 2025-10-28
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from npu_converter.optimization import (
    ParameterOptimizer,
    ParameterOptimizationResult,
    OptimizationObjective,
    OptimizationMetrics,
    OptimizationStrategy,
    TradeOffStrategy,
    TradeOffConfig,
    ModelAnalyzer,
    TradeOffCalculator
)


class TestParameterOptimizer(unittest.TestCase):
    """Test cases for ParameterOptimizer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_analyzer = Mock(spec=ModelAnalyzer)
        self.mock_calculator = Mock(spec=TradeOffCalculator)
        self.optimizer = ParameterOptimizer(
            model_analyzer=self.mock_analyzer,
            tradeoff_calculator=self.mock_calculator,
            verbose=True
        )

        # Mock model characteristics
        self.mock_characteristics = Mock()
        self.mock_characteristics.model_type = "asr"
        self.mock_characteristics.model_size = 100_000_000
        self.mock_characteristics.complexity_score = 0.5

        self.mock_analyzer.analyze_model.return_value = self.mock_characteristics

    def test_init(self):
        """Test optimizer initialization."""
        self.assertIsInstance(self.optimizer.model_analyzer, ModelAnalyzer)
        self.assertIsInstance(self.optimizer.tradeoff_calculator, TradeOffCalculator)
        self.assertEqual(len(self.optimizer.optimization_history), 0)

    def test_optimize_basic(self):
        """Test basic optimization functionality."""
        # Define parameter space
        param_space = {
            'quantization_bits': {
                'type': 'choice',
                'values': [8, 16]
            },
            'batch_size': {
                'type': 'choice',
                'values': [16, 32]
            }
        }

        # Mock optimization result
        mock_optimization_result = Mock()
        mock_optimization_result.best_params = {'quantization_bits': 16, 'batch_size': 32}
        mock_optimization_result.best_score = 0.15
        mock_optimization_result.iterations = 50
        mock_optimization_result.strategy = OptimizationStrategy.BAYESIAN
        mock_optimization_result.convergence_achieved = True
        mock_optimization_result.history = []

        # Mock metrics
        mock_metrics = OptimizationMetrics(
            accuracy=0.95,
            latency=100.0,
            throughput=10.0,
            memory=500.0,
            compatibility=1.0,
            success_rate=0.95
        )

        # Patch the optimization strategy creation
        with patch('npu_converter.optimization.parameter_optimizer.create_optimization_strategy') as mock_create:
            mock_strategy = Mock()
            mock_strategy.optimize.return_value = mock_optimization_result
            mock_create.return_value = mock_strategy

            # Mock internal methods
            self.optimizer._evaluate_parameters = Mock(return_value=mock_metrics)
            self.optimizer._get_initial_params = Mock(return_value={'quantization_bits': 16})
            self.optimizer._calculate_improvement = Mock(return_value=5.0)
            self.optimizer._generate_recommendations = Mock(return_value=["Recommendation 1"])

            # Run optimization
            result = self.optimizer.optimize(
                model="mock_model.onnx",
                param_space=param_space,
                strategy=OptimizationStrategy.BAYESIAN
            )

            # Verify results
            self.assertIsInstance(result, ParameterOptimizationResult)
            self.assertEqual(result.best_params, {'quantization_bits': 16, 'batch_size': 32})
            self.assertEqual(result.strategy_used, OptimizationStrategy.BAYESIAN)
            self.assertGreater(result.execution_time, 0)

    def test_optimize_with_tradeoff(self):
        """Test optimization with trade-off configuration."""
        param_space = {
            'quantization_bits': {
                'type': 'choice',
                'values': [8, 16]
            }
        }

        tradeoff_config = TradeOffConfig.from_strategy(TradeOffStrategy.QUALITY_FIRST)

        mock_optimization_result = Mock()
        mock_optimization_result.best_params = {'quantization_bits': 16}
        mock_optimization_result.best_score = 0.10
        mock_optimization_result.iterations = 30
        mock_optimization_result.strategy = OptimizationStrategy.GRID_SEARCH
        mock_optimization_result.convergence_achieved = True
        mock_optimization_result.history = []

        mock_metrics = OptimizationMetrics(accuracy=0.96)

        with patch('npu_converter.optimization.parameter_optimizer.create_optimization_strategy') as mock_create:
            mock_strategy = Mock()
            mock_strategy.optimize.return_value = mock_optimization_result
            mock_create.return_value = mock_strategy

            self.optimizer._evaluate_parameters = Mock(return_value=mock_metrics)
            self.optimizer._get_initial_params = Mock(return_value={'quantization_bits': 16})
            self.optimizer._calculate_improvement = Mock(return_value=3.0)
            self.optimizer._generate_recommendations = Mock(return_value=[])

            result = self.optimizer.optimize(
                model="mock_model.onnx",
                param_space=param_space,
                strategy=OptimizationStrategy.GRID_SEARCH,
                tradeoff_config=tradeoff_config
            )

            self.assertIsInstance(result, ParameterOptimizationResult)

    def test_evaluate_parameters(self):
        """Test parameter evaluation."""
        params = {'quantization_bits': 16, 'batch_size': 32}
        model = "mock_model.onnx"

        # Test evaluation with different model types
        self.mock_characteristics.model_type = "tts"
        metrics = self.optimizer._evaluate_parameters(
            params, model, self.mock_characteristics
        )

        self.assertIsInstance(metrics, OptimizationMetrics)
        self.assertGreater(metrics.accuracy, 0.0)
        self.assertLess(metrics.accuracy, 1.0)
        self.assertGreater(metrics.latency, 0.0)

    def test_calculate_composite_score(self):
        """Test composite score calculation."""
        metrics = OptimizationMetrics(
            accuracy=0.95,
            latency=100.0,
            throughput=10.0,
            memory=500.0,
            compatibility=1.0,
            success_rate=0.95
        )

        tradeoff_config = TradeOffConfig.from_strategy(TradeOffStrategy.BALANCED)

        # Mock the calculator
        self.optimizer.tradeoff_calculator.calculate_score = Mock(return_value=0.85)

        score = self.optimizer._calculate_composite_score(
            metrics,
            OptimizationObjective.BALANCED,
            tradeoff_config
        )

        self.assertIsInstance(score, float)

    def test_get_initial_params(self):
        """Test initial parameter generation."""
        param_space = {
            'quantization_bits': {
                'type': 'choice',
                'values': [8, 16]
            },
            'learning_rate': {
                'type': 'float',
                'bounds': [1e-5, 1e-2]
            }
        }

        # Mock analyzer recommendations
        self.mock_analyzer.recommend_parameters.return_value = {
            'quantization_bits': 16,
            'learning_rate': 1e-3
        }

        initial_params = self.optimizer._get_initial_params(
            param_space, self.mock_characteristics
        )

        self.assertIn('quantization_bits', initial_params)
        self.assertIn('learning_rate', initial_params)

    def test_calculate_improvement(self):
        """Test improvement percentage calculation."""
        params = {'quantization_bits': 16}
        model = "mock_model.onnx"

        # Mock evaluation methods
        self.optimizer._evaluate_parameters = Mock(return_value=Mock(
            accuracy=0.95,
            latency=100.0,
            throughput=10.0,
            memory=500.0,
            compatibility=1.0,
            success_rate=0.95
        ))

        improvement = self.optimizer._calculate_improvement(
            params, model, self.mock_characteristics
        )

        self.assertIsInstance(improvement, float)
        self.assertGreaterEqual(improvement, 0.0)

    def test_generate_recommendations(self):
        """Test recommendation generation."""
        mock_optimization_result = Mock()
        mock_optimization_result.strategy = OptimizationStrategy.BAYESIAN

        metrics = OptimizationMetrics(
            accuracy=0.95,
            latency=100.0,
            compatibility=1.0
        )

        recommendations = self.optimizer._generate_recommendations(
            mock_optimization_result,
            self.mock_characteristics,
            metrics
        )

        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)

    def test_optimization_history(self):
        """Test optimization history tracking."""
        # Create mock result
        mock_result = Mock(spec=ParameterOptimizationResult)
        mock_result.best_params = {'param': 'value'}
        mock_result.execution_time = 1.0

        # Add to history
        self.optimizer.optimization_history.append(mock_result)

        # Get history
        history = self.optimizer.get_optimization_history()
        self.assertEqual(len(history), 1)

        # Clear history
        self.optimizer.clear_history()
        self.assertEqual(len(self.optimizer.optimization_history), 0)

    def test_export_results_json(self):
        """Test result export to JSON."""
        # Create mock result
        mock_result = Mock(spec=ParameterOptimizationResult)
        mock_result.best_params = {'quantization_bits': 16}
        mock_result.best_metrics = Mock(
            accuracy=0.95,
            latency=100.0,
            throughput=10.0,
            memory=500.0,
            compatibility=1.0,
            success_rate=0.95
        )
        mock_result.strategy_used = OptimizationStrategy.BAYESIAN
        mock_result.objective = OptimizationObjective.BALANCED
        mock_result.improvement_percentage = 5.0
        mock_result.execution_time = 1.0
        mock_result.recommendations = ["Test recommendation"]
        mock_result.model_characteristics = Mock(
            model_type="asr",
            model_size=100_000_000,
            complexity_score=0.5
        )

        export_data = self.optimizer.export_results(mock_result, format="json")
        self.assertIsInstance(export_data, str)

    def test_export_results_yaml(self):
        """Test result export to YAML."""
        mock_result = Mock(spec=ParameterOptimizationResult)
        mock_result.best_params = {'quantization_bits': 16}
        mock_result.best_metrics = Mock(
            accuracy=0.95,
            latency=100.0,
            throughput=10.0,
            memory=500.0,
            compatibility=1.0,
            success_rate=0.95
        )
        mock_result.strategy_used = OptimizationStrategy.BAYESIAN
        mock_result.objective = OptimizationObjective.BALANCED
        mock_result.improvement_percentage = 5.0
        mock_result.execution_time = 1.0
        mock_result.recommendations = []
        mock_result.model_characteristics = Mock(
            model_type="asr",
            model_size=100_000_000,
            complexity_score=0.5
        )

        export_data = self.optimizer.export_results(mock_result, format="yaml")
        self.assertIsInstance(export_data, str)

    def test_optimize_with_custom_objective(self):
        """Test optimization with custom objective."""
        param_space = {
            'quantization_bits': {
                'type': 'choice',
                'values': [8, 16]
            }
        }

        mock_optimization_result = Mock()
        mock_optimization_result.best_params = {'quantization_bits': 8}
        mock_optimization_result.best_score = 0.12
        mock_optimization_result.iterations = 40
        mock_optimization_result.strategy = OptimizationStrategy.GENETIC
        mock_optimization_result.convergence_achieved = True
        mock_optimization_result.history = []

        mock_metrics = OptimizationMetrics(
            accuracy=0.94,
            latency=80.0,
            throughput=12.5,
            memory=400.0,
            compatibility=0.95,
            success_rate=0.93
        )

        with patch('npu_converter.optimization.parameter_optimizer.create_optimization_strategy') as mock_create:
            mock_strategy = Mock()
            mock_strategy.optimize.return_value = mock_optimization_result
            mock_create.return_value = mock_strategy

            self.optimizer._evaluate_parameters = Mock(return_value=mock_metrics)
            self.optimizer._get_initial_params = Mock(return_value={'quantization_bits': 16})
            self.optimizer._calculate_improvement = Mock(return_value=7.5)
            self.optimizer._generate_recommendations = Mock(return_value=[])

            result = self.optimizer.optimize(
                model="mock_model.onnx",
                param_space=param_space,
                strategy=OptimizationStrategy.GENETIC,
                objective=OptimizationObjective.MINIMIZE_LATENCY
            )

            self.assertEqual(result.objective, OptimizationObjective.MINIMIZE_LATENCY)


class TestOptimizationMetrics(unittest.TestCase):
    """Test cases for OptimizationMetrics dataclass."""

    def test_metrics_creation(self):
        """Test metrics object creation."""
        metrics = OptimizationMetrics(
            accuracy=0.95,
            latency=100.0,
            throughput=10.0,
            memory=500.0,
            compatibility=1.0,
            success_rate=0.95
        )

        self.assertEqual(metrics.accuracy, 0.95)
        self.assertEqual(metrics.latency, 100.0)
        self.assertEqual(metrics.throughput, 10.0)
        self.assertEqual(metrics.memory_usage, 500.0)
        self.assertEqual(metrics.compatibility, 1.0)
        self.assertEqual(metrics.success_rate, 0.95)

    def test_metrics_defaults(self):
        """Test metrics with default values."""
        metrics = OptimizationMetrics()

        self.assertEqual(metrics.accuracy, 0.0)
        self.assertEqual(metrics.latency, 0.0)
        self.assertEqual(metrics.throughput, 0.0)
        self.assertEqual(metrics.memory_usage, 0.0)
        self.assertEqual(metrics.compatibility, 1.0)
        self.assertEqual(metrics.success_rate, 0.0)


class TestParameterOptimizationResult(unittest.TestCase):
    """Test cases for ParameterOptimizationResult dataclass."""

    def test_result_creation(self):
        """Test result object creation."""
        mock_optimization_result = Mock()
        mock_characteristics = Mock()
        mock_metrics = Mock()

        result = ParameterOptimizationResult(
            best_params={'param': 'value'},
            best_metrics=mock_metrics,
            optimization_result=mock_optimization_result,
            model_characteristics=mock_characteristics,
            improvement_percentage=5.0,
            strategy_used=OptimizationStrategy.BAYESIAN,
            objective=OptimizationObjective.BALANCED,
            execution_time=10.0,
            recommendations=["Rec 1", "Rec 2"]
        )

        self.assertEqual(result.best_params, {'param': 'value'})
        self.assertEqual(result.best_metrics, mock_metrics)
        self.assertEqual(result.improvement_percentage, 5.0)
        self.assertEqual(result.strategy_used, OptimizationStrategy.BAYESIAN)
        self.assertEqual(result.objective, OptimizationObjective.BALANCED)
        self.assertEqual(result.execution_time, 10.0)
        self.assertEqual(len(result.recommendations), 2)


if __name__ == '__main__':
    unittest.main()
