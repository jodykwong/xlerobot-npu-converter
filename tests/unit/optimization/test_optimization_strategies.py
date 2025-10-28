"""
Unit tests for Optimization Strategies.

Tests the various optimization algorithms including grid search,
Bayesian optimization, genetic algorithm, and random search.

Author: Story 2.6 Implementation
Version: 1.0.0
Date: 2025-10-28
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from npu_converter.optimization.optimization_strategies import (
    OptimizationStrategy,
    OptimizationConfig,
    OptimizationResult,
    BaseOptimizationStrategy,
    GridSearchStrategy,
    BayesianOptimizationStrategy,
    GeneticAlgorithmStrategy,
    RandomSearchStrategy,
    create_optimization_strategy
)


class TestOptimizationConfig(unittest.TestCase):
    """Test cases for OptimizationConfig dataclass."""

    def test_config_creation(self):
        """Test config object creation."""
        config = OptimizationConfig(
            max_iterations=100,
            convergence_threshold=0.01,
            time_limit=600.0,
            early_stopping=True,
            patience=10,
            random_seed=42,
            verbose=True
        )

        self.assertEqual(config.max_iterations, 100)
        self.assertEqual(config.convergence_threshold, 0.01)
        self.assertEqual(config.time_limit, 600.0)
        self.assertTrue(config.early_stopping)
        self.assertEqual(config.patience, 10)
        self.assertEqual(config.random_seed, 42)
        self.assertTrue(config.verbose)

    def test_config_defaults(self):
        """Test config with default values."""
        config = OptimizationConfig()

        self.assertEqual(config.max_iterations, 100)
        self.assertEqual(config.convergence_threshold, 0.01)
        self.assertEqual(config.time_limit, 600.0)
        self.assertTrue(config.early_stopping)
        self.assertEqual(config.patience, 10)
        self.assertIsNone(config.random_seed)
        self.assertTrue(config.verbose)


class TestGridSearchStrategy(unittest.TestCase):
    """Test cases for GridSearchStrategy class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = OptimizationConfig(max_iterations=10, verbose=False)
        self.strategy = GridSearchStrategy(self.config)

    def test_init(self):
        """Test strategy initialization."""
        self.assertIsInstance(self.strategy, BaseOptimizationStrategy)
        self.assertEqual(self.strategy.config.max_iterations, 10)

    def test_optimize_simple(self):
        """Test basic grid search optimization."""
        param_space = {
            'x': {
                'type': 'float',
                'bounds': [0.0, 1.0],
                'num_points': 3
            },
            'y': {
                'type': 'choice',
                'values': [1, 2, 3]
            }
        }

        # Simple objective function
        def objective(params):
            return (params['x'] - 0.5) ** 2 + params['y']

        result = self.strategy.optimize(objective, param_space)

        self.assertIsInstance(result, OptimizationResult)
        self.assertEqual(result.strategy, OptimizationStrategy.GRID_SEARCH)
        self.assertGreater(result.iterations, 0)
        self.assertIsInstance(result.best_params, dict)
        self.assertIn('x', result.best_params)
        self.assertIn('y', result.best_params)

    def test_optimize_with_time_limit(self):
        """Test optimization with time limit."""
        param_space = {
            'x': {
                'type': 'float',
                'bounds': [0.0, 1.0],
                'num_points': 10
            }
        }

        # Slow objective function
        def slow_objective(params):
            import time
            time.sleep(0.1)  # Simulate slow evaluation
            return params['x'] ** 2

        # Set short time limit
        self.config.time_limit = 0.5
        result = self.strategy.optimize(slow_objective, param_space)

        # Should stop early due to time limit
        self.assertLessEqual(result.execution_time, 1.0)

    def test_generate_grid(self):
        """Test grid generation."""
        param_space = {
            'x': {
                'type': 'float',
                'bounds': [0.0, 1.0],
                'num_points': 3
            },
            'y': {
                'type': 'choice',
                'values': [1, 2]
            }
        }

        grid = self.strategy._generate_grid(param_space)

        self.assertIsInstance(grid, list)
        self.assertEqual(len(grid), 6)  # 3 x 2 = 6 combinations

        # Check grid points
        for point in grid:
            self.assertIn('x', point)
            self.assertIn('y', point)
            self.assertIsInstance(point['x'], float)
            self.assertIsInstance(point['y'], int)

    def test_generate_param_grid_choice(self):
        """Test parameter grid for choice type."""
        param_config = {
            'type': 'choice',
            'values': [1, 2, 3]
        }

        grid = self.strategy._generate_param_grid('param', param_config, 'choice')

        self.assertEqual(grid, [1, 2, 3])

    def test_generate_param_grid_int(self):
        """Test parameter grid for int type."""
        param_config = {
            'type': 'int',
            'bounds': [0, 10],
            'step': 2
        }

        grid = self.strategy._generate_param_grid('param', param_config, 'int')

        self.assertEqual(grid, [0, 2, 4, 6, 8, 10])

    def test_generate_param_grid_float(self):
        """Test parameter grid for float type."""
        param_config = {
            'type': 'float',
            'bounds': [0.0, 1.0],
            'num_points': 5
        }

        grid = self.strategy._generate_param_grid('param', param_config, 'float')

        self.assertEqual(len(grid), 5)
        self.assertAlmostEqual(grid[0], 0.0, places=5)
        self.assertAlmostEqual(grid[-1], 1.0, places=5)

    def test_get_strategy_description(self):
        """Test strategy description."""
        description = self.strategy.get_strategy_description()

        self.assertIsInstance(description, str)
        self.assertIn("Grid Search", description)
        self.assertIn("exhaustive", description.lower())


class TestBayesianOptimizationStrategy(unittest.TestCase):
    """Test cases for BayesianOptimizationStrategy class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = OptimizationConfig(max_iterations=10, verbose=False)
        self.strategy = BayesianOptimizationStrategy(self.config)

    def test_init(self):
        """Test strategy initialization."""
        self.assertIsInstance(self.strategy, BaseOptimizationStrategy)
        self.assertEqual(self.strategy.config.max_iterations, 10)

    def test_optimize(self):
        """Test Bayesian optimization."""
        param_space = {
            'x': {
                'type': 'float',
                'bounds': [0.0, 1.0]
            },
            'y': {
                'type': 'int',
                'bounds': [0, 10]
            }
        }

        # Simple objective function
        def objective(params):
            return (params['x'] - 0.3) ** 2 + (params['y'] - 5) ** 2

        result = self.strategy.optimize(objective, param_space)

        self.assertIsInstance(result, OptimizationResult)
        self.assertEqual(result.strategy, OptimizationStrategy.BAYESIAN)
        self.assertGreater(result.iterations, 0)

    def test_sample_random_params(self):
        """Test random parameter sampling."""
        param_space = {
            'x': {
                'type': 'float',
                'bounds': [0.0, 1.0]
            },
            'y': {
                'type': 'choice',
                'values': [1, 2, 3]
            },
            'z': {
                'type': 'int',
                'bounds': [0, 10]
            }
        }

        params = self.strategy._sample_random_params(param_space)

        self.assertIsInstance(params, dict)
        self.assertIn('x', params)
        self.assertIn('y', params)
        self.assertIn('z', params)
        self.assertIsInstance(params['x'], float)
        self.assertIsInstance(params['y'], int)
        self.assertIsInstance(params['z'], int)
        self.assertGreaterEqual(params['x'], 0.0)
        self.assertLessEqual(params['x'], 1.0)
        self.assertIn(params['y'], [1, 2, 3])
        self.assertGreaterEqual(params['z'], 0)
        self.assertLessEqual(params['z'], 10)

    def test_get_strategy_description(self):
        """Test strategy description."""
        description = self.strategy.get_strategy_description()

        self.assertIsInstance(description, str)
        self.assertIn("Bayesian", description)


class TestGeneticAlgorithmStrategy(unittest.TestCase):
    """Test cases for GeneticAlgorithmStrategy class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = OptimizationConfig(max_iterations=10, verbose=False)
        self.config.population_size = 20
        self.config.mutation_rate = 0.1
        self.config.crossover_rate = 0.7
        self.strategy = GeneticAlgorithmStrategy(self.config)

    def test_init(self):
        """Test strategy initialization."""
        self.assertIsInstance(self.strategy, BaseOptimizationStrategy)
        self.assertEqual(self.strategy.population_size, 20)
        self.assertEqual(self.strategy.mutation_rate, 0.1)
        self.assertEqual(self.strategy.crossover_rate, 0.7)

    def test_optimize(self):
        """Test genetic algorithm optimization."""
        param_space = {
            'x': {
                'type': 'float',
                'bounds': [0.0, 1.0]
            },
            'y': {
                'type': 'int',
                'bounds': [0, 10]
            }
        }

        # Simple objective function
        def objective(params):
            return (params['x'] - 0.5) ** 2 + params['y']

        result = self.strategy.optimize(objective, param_space)

        self.assertIsInstance(result, OptimizationResult)
        self.assertEqual(result.strategy, OptimizationStrategy.GENETIC)
        self.assertGreater(result.iterations, 0)

    def test_initialize_population(self):
        """Test population initialization."""
        param_space = {
            'x': {
                'type': 'float',
                'bounds': [0.0, 1.0]
            },
            'y': {
                'type': 'choice',
                'values': [1, 2, 3]
            }
        }

        population = self.strategy._initialize_population(param_space)

        self.assertEqual(len(population), self.strategy.population_size)
        for individual in population:
            self.assertIsInstance(individual, dict)
            self.assertIn('x', individual)
            self.assertIn('y', individual)

    def test_tournament_selection(self):
        """Test tournament selection."""
        population = [
            {'x': 0.1, 'y': 1},
            {'x': 0.5, 'y': 2},
            {'x': 0.9, 'y': 3}
        ]
        scores = [0.8, 0.3, 0.6]  # Lower is better

        selected = self.strategy._tournament_selection(population, scores)

        self.assertEqual(len(selected), len(population))
        # Should select individuals with lower scores

    def test_crossover(self):
        """Test crossover operation."""
        param_space = {
            'x': {
                'type': 'float',
                'bounds': [0.0, 1.0]
            },
            'y': {
                'type': 'int',
                'bounds': [0, 10]
            }
        }

        parent1 = {'x': 0.3, 'y': 5}
        parent2 = {'x': 0.7, 'y': 3}

        # Disable crossover for deterministic test
        self.strategy.crossover_rate = 0.0
        child1, child2 = self.strategy._crossover(parent1, parent2, param_space)

        # Without crossover, children should be identical to parents
        self.assertEqual(child1, parent1)
        self.assertEqual(child2, parent2)

        # Enable crossover
        self.strategy.crossover_rate = 1.0
        child1, child2 = self.strategy._crossover(parent1, parent2, param_space)

        # With crossover, children should be combinations
        self.assertIsInstance(child1, dict)
        self.assertIsInstance(child2, dict)

    def test_mutate(self):
        """Test mutation operation."""
        param_space = {
            'x': {
                'type': 'float',
                'bounds': [0.0, 1.0]
            },
            'y': {
                'type': 'choice',
                'values': [1, 2, 3]
            }
        }

        individual = {'x': 0.5, 'y': 2}

        # Disable mutation for deterministic test
        self.strategy.mutation_rate = 0.0
        mutated = self.strategy._mutate(individual, param_space)

        # Without mutation, individual should be unchanged
        self.assertEqual(mutated, individual)

        # Enable mutation
        self.strategy.mutation_rate = 1.0
        mutated = self.strategy._mutate(individual, param_space)

        # With mutation, individual should be modified (bounds check)
        self.assertIsInstance(mutated, dict)

    def test_get_strategy_description(self):
        """Test strategy description."""
        description = self.strategy.get_strategy_description()

        self.assertIsInstance(description, str)
        self.assertIn("Genetic", description)


class TestRandomSearchStrategy(unittest.TestCase):
    """Test cases for RandomSearchStrategy class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = OptimizationConfig(max_iterations=10, verbose=False)
        self.strategy = RandomSearchStrategy(self.config)

    def test_init(self):
        """Test strategy initialization."""
        self.assertIsInstance(self.strategy, BaseOptimizationStrategy)
        self.assertEqual(self.strategy.config.max_iterations, 10)

    def test_optimize(self):
        """Test random search optimization."""
        param_space = {
            'x': {
                'type': 'float',
                'bounds': [0.0, 1.0]
            },
            'y': {
                'type': 'choice',
                'values': [1, 2, 3]
            }
        }

        # Simple objective function
        def objective(params):
            return (params['x'] - 0.5) ** 2 + params['y']

        result = self.strategy.optimize(objective, param_space)

        self.assertIsInstance(result, OptimizationResult)
        self.assertEqual(result.strategy, OptimizationStrategy.RANDOM)
        self.assertGreater(result.iterations, 0)

    def test_sample_random_params(self):
        """Test random parameter sampling."""
        param_space = {
            'x': {
                'type': 'float',
                'bounds': [0.0, 1.0]
            },
            'y': {
                'type': 'choice',
                'values': [1, 2, 3]
            }
        }

        params = self.strategy._sample_random_params(param_space)

        self.assertIsInstance(params, dict)
        self.assertIn('x', params)
        self.assertIn('y', params)

    def test_get_strategy_description(self):
        """Test strategy description."""
        description = self.strategy.get_strategy_description()

        self.assertIsInstance(description, str)
        self.assertIn("Random", description)


class TestOptimizationResult(unittest.TestCase):
    """Test cases for OptimizationResult dataclass."""

    def test_result_creation(self):
        """Test result object creation."""
        result = OptimizationResult(
            best_params={'x': 0.5, 'y': 2},
            best_score=0.25,
            iterations=50,
            strategy=OptimizationStrategy.BAYESIAN,
            convergence_achieved=True,
            history=[({'x': 0.1, 'y': 1}, 0.9)],
            execution_time=10.5,
            message="Optimization completed successfully"
        )

        self.assertEqual(result.best_params, {'x': 0.5, 'y': 2})
        self.assertEqual(result.best_score, 0.25)
        self.assertEqual(result.iterations, 50)
        self.assertEqual(result.strategy, OptimizationStrategy.BAYESIAN)
        self.assertTrue(result.convergence_achieved)
        self.assertEqual(len(result.history), 1)
        self.assertEqual(result.execution_time, 10.5)
        self.assertEqual(result.message, "Optimization completed successfully")


class TestCreateOptimizationStrategy(unittest.TestCase):
    """Test cases for create_optimization_strategy factory function."""

    def test_create_grid_search(self):
        """Test creating grid search strategy."""
        config = OptimizationConfig()
        strategy = create_optimization_strategy(
            OptimizationStrategy.GRID_SEARCH,
            config
        )

        self.assertIsInstance(strategy, GridSearchStrategy)

    def test_create_bayesian(self):
        """Test creating Bayesian optimization strategy."""
        config = OptimizationConfig()
        strategy = create_optimization_strategy(
            OptimizationStrategy.BAYESIAN,
            config
        )

        self.assertIsInstance(strategy, BayesianOptimizationStrategy)

    def test_create_genetic(self):
        """Test creating genetic algorithm strategy."""
        config = OptimizationConfig()
        strategy = create_optimization_strategy(
            OptimizationStrategy.GENETIC,
            config
        )

        self.assertIsInstance(strategy, GeneticAlgorithmStrategy)

    def test_create_random(self):
        """Test creating random search strategy."""
        config = OptimizationConfig()
        strategy = create_optimization_strategy(
            OptimizationStrategy.RANDOM,
            config
        )

        self.assertIsInstance(strategy, RandomSearchStrategy)

    def test_create_unknown_strategy(self):
        """Test creating unknown strategy (should raise error)."""
        config = OptimizationConfig()

        with self.assertRaises(ValueError):
            create_optimization_strategy("unknown_strategy", config)


class TestBaseOptimizationStrategy(unittest.TestCase):
    """Test cases for BaseOptimizationStrategy abstract class."""

    def test_abstract_class(self):
        """Test that BaseOptimizationStrategy is abstract."""
        # Cannot instantiate abstract class directly
        with self.assertRaises(TypeError):
            BaseOptimizationStrategy(OptimizationConfig())


if __name__ == '__main__':
    unittest.main()
