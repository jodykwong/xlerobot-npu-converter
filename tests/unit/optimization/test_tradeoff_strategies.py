"""
Unit tests for Trade-off Strategies.

Tests quality-performance trade-off strategies and configurations.

Author: Story 2.6 Implementation
Version: 1.0.0
Date: 2025-10-28
"""

import unittest
from unittest.mock import Mock
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from npu_converter.optimization.tradeoff_strategies import (
    TradeOffStrategy,
    TradeOffWeights,
    TradeOffConfig,
    TradeOffCalculator,
    get_predefined_strategies,
    create_custom_config
)


class TestTradeOffWeights(unittest.TestCase):
    """Test cases for TradeOffWeights dataclass."""

    def test_weights_creation(self):
        """Test weights object creation."""
        weights = TradeOffWeights(
            accuracy=0.7,
            latency=0.2,
            throughput=0.05,
            memory=0.03,
            compatibility=0.01,
            success_rate=0.01
        )

        self.assertEqual(weights.accuracy, 0.7)
        self.assertEqual(weights.latency, 0.2)
        self.assertEqual(weights.throughput, 0.05)
        self.assertEqual(weights.memory, 0.03)
        self.assertEqual(weights.compatibility, 0.01)
        self.assertEqual(weights.success_rate, 0.01)

    def test_validate_positive_weights(self):
        """Test validation with positive weights."""
        weights = TradeOffWeights(
            accuracy=0.5,
            latency=0.3,
            throughput=0.1,
            memory=0.05,
            compatibility=0.03,
            success_rate=0.02
        )

        self.assertTrue(weights.validate())

    def test_validate_zero_weights(self):
        """Test validation with zero weights."""
        weights = TradeOffWeights(
            accuracy=0.0,
            latency=0.0,
            throughput=0.0,
            memory=0.0,
            compatibility=0.0,
            success_rate=1.0
        )

        self.assertTrue(weights.validate())

    def test_validate_negative_weights(self):
        """Test validation with negative weights (should fail)."""
        weights = TradeOffWeights(
            accuracy=-0.1,
            latency=0.5,
            throughput=0.3,
            memory=0.1,
            compatibility=0.05,
            success_rate=0.05
        )

        self.assertFalse(weights.validate())

    def test_normalize_equal_weights(self):
        """Test normalization with equal weights."""
        weights = TradeOffWeights(
            accuracy=1.0,
            latency=1.0,
            throughput=1.0,
            memory=1.0,
            compatibility=1.0,
            success_rate=1.0
        )

        normalized = weights.normalize()

        # All weights should sum to 1.0
        total = (normalized.accuracy + normalized.latency +
                normalized.throughput + normalized.memory +
                normalized.compatibility + normalized.success_rate)

        self.assertAlmostEqual(total, 1.0, places=5)
        self.assertAlmostEqual(normalized.accuracy, 1/6, places=5)

    def test_normalize_unequal_weights(self):
        """Test normalization with unequal weights."""
        weights = TradeOffWeights(
            accuracy=0.7,
            latency=0.2,
            throughput=0.1,
            memory=0.0,
            compatibility=0.0,
            success_rate=0.0
        )

        normalized = weights.normalize()

        total = (normalized.accuracy + normalized.latency +
                normalized.throughput + normalized.memory +
                normalized.compatibility + normalized.success_rate)

        self.assertAlmostEqual(total, 1.0, places=5)
        # Accuracy should be 0.7 / (0.7 + 0.2 + 0.1) = 0.7
        self.assertAlmostEqual(normalized.accuracy, 0.7, places=5)

    def test_normalize_all_zero(self):
        """Test normalization with all zero weights."""
        weights = TradeOffWeights(
            accuracy=0.0,
            latency=0.0,
            throughput=0.0,
            memory=0.0,
            compatibility=0.0,
            success_rate=0.0
        )

        normalized = weights.normalize()

        # Should default to equal distribution
        self.assertAlmostEqual(normalized.accuracy, 1/6, places=5)


class TestTradeOffConfig(unittest.TestCase):
    """Test cases for TradeOffConfig dataclass."""

    def test_from_strategy_quality_first(self):
        """Test creating config from quality-first strategy."""
        config = TradeOffConfig.from_strategy(TradeOffStrategy.QUALITY_FIRST)

        self.assertEqual(config.strategy, TradeOffStrategy.QUALITY_FIRST)
        self.assertIsInstance(config.weights, TradeOffWeights)
        self.assertEqual(config.custom_weights, None)

        # Quality first should prioritize accuracy
        self.assertGreater(config.weights.accuracy, 0.5)

    def test_from_strategy_performance_first(self):
        """Test creating config from performance-first strategy."""
        config = TradeOffConfig.from_strategy(TradeOffStrategy.PERFORMANCE_FIRST)

        self.assertEqual(config.strategy, TradeOffStrategy.PERFORMANCE_FIRST)
        self.assertIsInstance(config.weights, TradeOffWeights)

        # Performance first should prioritize latency and throughput
        self.assertGreater(config.weights.latency, 0.3)
        self.assertGreater(config.weights.throughput, 0.1)

    def test_from_strategy_balanced(self):
        """Test creating config from balanced strategy."""
        config = TradeOffConfig.from_strategy(TradeOffStrategy.BALANCED)

        self.assertEqual(config.strategy, TradeOffStrategy.BALANCED)
        self.assertIsInstance(config.weights, TradeOffWeights)

        # Balanced should have roughly equal weights
        weights = [config.weights.accuracy, config.weights.latency,
                  config.weights.throughput, config.weights.memory,
                  config.weights.compatibility, config.weights.success_rate]

        # All should be between 0.1 and 0.3
        for w in weights:
            self.assertGreaterEqual(w, 0.1)
            self.assertLessEqual(w, 0.3)

    def test_from_strategy_resource_saving(self):
        """Test creating config from resource-saving strategy."""
        config = TradeOffConfig.from_strategy(TradeOffStrategy.RESOURCE_SAVING)

        self.assertEqual(config.strategy, TradeOffStrategy.RESOURCE_SAVING)
        self.assertIsInstance(config.weights, TradeOffWeights)

        # Resource saving should prioritize memory
        self.assertGreater(config.weights.memory, 0.3)

    def test_from_custom_weights(self):
        """Test creating config from custom weights."""
        weights = TradeOffWeights(
            accuracy=0.6,
            latency=0.3,
            throughput=0.05,
            memory=0.03,
            compatibility=0.015,
            success_rate=0.005
        )

        config = TradeOffConfig.from_custom_weights(weights)

        self.assertEqual(config.strategy, TradeOffStrategy.CUSTOM)
        self.assertEqual(config.custom_weights, weights)
        self.assertIsNotNone(config.weights)

    def test_from_custom_weights_invalid(self):
        """Test creating config with invalid weights (negative)."""
        weights = TradeOffWeights(
            accuracy=-0.1,
            latency=0.5,
            throughput=0.3,
            memory=0.2,
            compatibility=0.05,
            success_rate=0.0
        )

        with self.assertRaises(ValueError):
            TradeOffConfig.from_custom_weights(weights)

    def test_default(self):
        """Test getting default configuration."""
        config = TradeOffConfig.default()

        self.assertEqual(config.strategy, TradeOffStrategy.BALANCED)

    def test_get_weights_custom(self):
        """Test getting weights with custom configuration."""
        custom_weights = TradeOffWeights(
            accuracy=0.8,
            latency=0.1,
            throughput=0.05,
            memory=0.025,
            compatibility=0.015,
            success_rate=0.01
        )

        config = TradeOffConfig.from_custom_weights(custom_weights)
        retrieved_weights = config.get_weights()

        # Should return normalized custom weights
        self.assertIsInstance(retrieved_weights, TradeOffWeights)

    def test_get_weights_predefined(self):
        """Test getting weights from predefined strategy."""
        config = TradeOffConfig.from_strategy(TradeOffStrategy.QUALITY_FIRST)
        weights = config.get_weights()

        self.assertEqual(weights, config.weights)

    def test_get_description_quality_first(self):
        """Test getting description for quality-first strategy."""
        config = TradeOffConfig.from_strategy(TradeOffStrategy.QUALITY_FIRST)
        description = config.get_description()

        self.assertIsInstance(description, str)
        self.assertIn("Quality", description)
        self.assertIn("accuracy", description.lower())

    def test_get_description_performance_first(self):
        """Test getting description for performance-first strategy."""
        config = TradeOffConfig.from_strategy(TradeOffStrategy.PERFORMANCE_FIRST)
        description = config.get_description()

        self.assertIsInstance(description, str)
        self.assertIn("Performance", description)
        self.assertIn("latency", description.lower())

    def test_get_description_balanced(self):
        """Test getting description for balanced strategy."""
        config = TradeOffConfig.from_strategy(TradeOffStrategy.BALANCED)
        description = config.get_description()

        self.assertIsInstance(description, str)
        self.assertIn("Balanced", description)

    def test_get_description_resource_saving(self):
        """Test getting description for resource-saving strategy."""
        config = TradeOffConfig.from_strategy(TradeOffStrategy.RESOURCE_SAVING)
        description = config.get_description()

        self.assertIsInstance(description, str)
        self.assertIn("Resource", description)
        self.assertIn("memory", description.lower())


class TestTradeOffCalculator(unittest.TestCase):
    """Test cases for TradeOffCalculator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.calculator = TradeOffCalculator()

    def test_init(self):
        """Test calculator initialization."""
        self.assertIsInstance(self.calculator, TradeOffCalculator)

    def test_calculate_score(self):
        """Test score calculation."""
        metrics = {
            'accuracy': 0.95,
            'latency': 100.0,
            'throughput': 10.0,
            'memory': 500.0,
            'compatibility': 1.0,
            'success_rate': 0.95
        }

        config = TradeOffConfig.from_strategy(TradeOffStrategy.BALANCED)

        score = self.calculator.calculate_score(metrics, config)

        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_normalize_metrics(self):
        """Test metric normalization."""
        metrics = {
            'accuracy': 0.95,
            'latency': 100.0,
            'throughput': 10.0,
            'memory': 500.0,
            'compatibility': 1.0,
            'success_rate': 0.95
        }

        normalized = self.calculator._normalize_metrics(metrics)

        self.assertIsInstance(normalized, dict)
        self.assertIn('accuracy', normalized)
        self.assertIn('latency', normalized)
        self.assertIn('throughput', normalized)
        self.assertIn('memory', normalized)
        self.assertIn('compatibility', normalized)
        self.assertIn('success_rate', normalized)

        # All normalized values should be between 0 and 1
        for value in normalized.values():
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_estimate_outcome_asr(self):
        """Test outcome estimation for ASR model."""
        outcome = self.calculator.estimate_outcome(
            model_type="asr",
            config=TradeOffConfig.from_strategy(TradeOffStrategy.BALANCED),
            model_complexity=0.5
        )

        self.assertIsInstance(outcome, dict)
        self.assertIn('accuracy', outcome)
        self.assertIn('latency', outcome)
        self.assertIn('throughput', outcome)
        self.assertIn('memory', outcome)
        self.assertIn('compatibility', outcome)
        self.assertIn('success_rate', outcome)

        # ASR models should have high accuracy
        self.assertGreaterEqual(outcome['accuracy'], 0.9)

    def test_estimate_outcome_tts(self):
        """Test outcome estimation for TTS model."""
        outcome = self.calculator.estimate_outcome(
            model_type="tts",
            config=TradeOffConfig.from_strategy(TradeOffStrategy.QUALITY_FIRST),
            model_complexity=0.6
        )

        self.assertIsInstance(outcome, dict)
        self.assertGreaterEqual(outcome['accuracy'], 0.9)

    def test_estimate_outcome_with_constraints(self):
        """Test outcome estimation with trade-off adjustments."""
        config = TradeOffConfig.from_strategy(TradeOffStrategy.PERFORMANCE_FIRST)

        outcome = self.calculator.estimate_outcome(
            model_type="asr",
            config=config,
            model_complexity=0.5
        )

        # Performance strategy should improve latency
        self.assertLess(outcome['latency'], 150.0)

    def test_compare_strategies(self):
        """Test strategy comparison."""
        strategies = [
            TradeOffStrategy.QUALITY_FIRST,
            TradeOffStrategy.PERFORMANCE_FIRST,
            TradeOffStrategy.BALANCED
        ]

        comparison = self.calculator.compare_strategies(
            model_type="asr",
            strategies=strategies,
            model_complexity=0.5
        )

        self.assertIsInstance(comparison, dict)
        self.assertEqual(len(comparison), 3)

        for strategy_name in comparison.keys():
            self.assertIn('metrics', comparison[strategy_name])
            self.assertIn('description', comparison[strategy_name])

    def test_get_strategy_recommendation_realtime(self):
        """Test strategy recommendation for real-time use case."""
        recommendation = self.calculator.get_strategy_recommendation(
            use_case="real-time speech recognition system",
            constraints=None
        )

        self.assertEqual(recommendation, TradeOffStrategy.PERFORMANCE_FIRST)

    def test_get_strategy_recommendation_quality(self):
        """Test strategy recommendation for quality-focused use case."""
        recommendation = self.calculator.get_strategy_recommendation(
            use_case="high-quality audio generation for production",
            constraints=None
        )

        self.assertEqual(recommendation, TradeOffStrategy.QUALITY_FIRST)

    def test_get_strategy_recommendation_edge(self):
        """Test strategy recommendation for edge device."""
        recommendation = self.calculator.get_strategy_recommendation(
            use_case="model for edge device with limited memory",
            constraints=None
        )

        self.assertEqual(recommendation, TradeOffStrategy.RESOURCE_SAVING)

    def test_get_strategy_recommendation_general(self):
        """Test strategy recommendation for general use case."""
        recommendation = self.calculator.get_strategy_recommendation(
            use_case="general purpose model optimization",
            constraints=None
        )

        self.assertEqual(recommendation, TradeOffStrategy.BALANCED)

    def test_get_strategy_recommendation_with_constraints(self):
        """Test strategy recommendation with constraints."""
        constraints = {'latency_max': 50}

        recommendation = self.calculator.get_strategy_recommendation(
            use_case="any use case",
            constraints=constraints
        )

        # Should recommend performance first due to latency constraint
        self.assertEqual(recommendation, TradeOffStrategy.PERFORMANCE_FIRST)


class TestGetPredefinedStrategies(unittest.TestCase):
    """Test cases for get_predefined_strategies function."""

    def test_get_predefined_strategies(self):
        """Test getting predefined strategies."""
        strategies = get_predefined_strategies()

        self.assertIsInstance(strategies, list)
        self.assertEqual(len(strategies), 4)

        expected_strategies = [
            TradeOffStrategy.QUALITY_FIRST,
            TradeOffStrategy.PERFORMANCE_FIRST,
            TradeOffStrategy.BALANCED,
            TradeOffStrategy.RESOURCE_SAVING
        ]

        for strategy in expected_strategies:
            self.assertIn(strategy, strategies)


class TestCreateCustomConfig(unittest.TestCase):
    """Test cases for create_custom_config convenience function."""

    def test_create_custom_config_default(self):
        """Test creating custom config with default weights."""
        config = create_custom_config()

        self.assertEqual(config.strategy, TradeOffStrategy.CUSTOM)
        self.assertIsInstance(config.weights, TradeOffWeights)

    def test_create_custom_config_custom_weights(self):
        """Test creating custom config with specific weights."""
        config = create_custom_config(
            accuracy=0.6,
            latency=0.3,
            throughput=0.05,
            memory=0.025,
            compatibility=0.015,
            success_rate=0.01
        )

        self.assertEqual(config.strategy, TradeOffStrategy.CUSTOM)
        self.assertEqual(config.weights.accuracy, 0.6)
        self.assertEqual(config.weights.latency, 0.3)

    def test_create_custom_config_validation(self):
        """Test that custom config validates weights."""
        # Negative weight should fail during normalization check
        config = create_custom_config(accuracy=-0.1)

        # Should still create config (normalization happens in get_weights)
        self.assertEqual(config.strategy, TradeOffStrategy.CUSTOM)

    def test_get_predefined_strategies_result(self):
        """Test that all predefined strategies are in the result."""
        strategies = get_predefined_strategies()

        self.assertIn(TradeOffStrategy.QUALITY_FIRST, strategies)
        self.assertIn(TradeOffStrategy.PERFORMANCE_FIRST, strategies)
        self.assertIn(TradeOffStrategy.BALANCED, strategies)
        self.assertIn(TradeOffStrategy.RESOURCE_SAVING, strategies)
        self.assertNotIn(TradeOffStrategy.CUSTOM, strategies)


if __name__ == '__main__':
    unittest.main()
