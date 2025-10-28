"""
Optimization Strategies

This module defines the optimization strategy interface and implementations
for various parameter optimization algorithms.

Author: Story 2.6 Implementation
Version: 1.0.0
Date: 2025-10-28
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple, Callable
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class OptimizationStrategy(Enum):
    """Optimization strategy types"""
    GRID_SEARCH = "grid_search"
    BAYESIAN = "bayesian"
    GENETIC = "genetic"
    RANDOM = "random"


@dataclass
class OptimizationResult:
    """Result of optimization process"""
    best_params: Dict[str, Any]
    best_score: float
    iterations: int
    strategy: OptimizationStrategy
    convergence_achieved: bool
    history: List[Tuple[Dict[str, Any], float]]  # (params, score) pairs
    execution_time: float  # seconds
    message: str = ""


@dataclass
class OptimizationConfig:
    """Configuration for optimization process"""
    max_iterations: int = 100
    convergence_threshold: float = 0.01
    time_limit: float = 600.0  # seconds (10 minutes)
    early_stopping: bool = True
    patience: int = 10  # iterations to wait for improvement
    random_seed: Optional[int] = None
    verbose: bool = True


class BaseOptimizationStrategy(ABC):
    """
    Abstract base class for optimization strategies.

    Defines the interface that all optimization algorithms must implement.
    """

    def __init__(self, config: OptimizationConfig):
        """
        Initialize optimization strategy.

        Args:
            config: Optimization configuration parameters
        """
        self.config = config
        self.name = self.__class__.__name__
        logger.info(f"Initializing {self.name} optimization strategy")

    @abstractmethod
    def optimize(
        self,
        objective_function: Callable[[Dict[str, Any]], float],
        param_space: Dict[str, Any],
        initial_params: Optional[Dict[str, Any]] = None
    ) -> OptimizationResult:
        """
        Perform optimization.

        Args:
            objective_function: Function to minimize (lower is better)
            param_space: Dictionary defining parameter search space
                         Format: {param_name: {'type': 'float'|'int'|'choice',
                         'bounds': (min, max) or 'values': [list]}
            initial_params: Optional initial parameter values

        Returns:
            OptimizationResult containing best parameters and optimization details
        """
        pass

    @abstractmethod
    def get_strategy_description(self) -> str:
        """
        Get human-readable description of the optimization strategy.

        Returns:
            Description string
        """
        pass


class GridSearchStrategy(BaseOptimizationStrategy):
    """
    Grid Search Optimization Strategy.

    Exhaustively tests all combinations of parameters in a predefined grid.
    Suitable for small parameter spaces where exhaustive search is feasible.
    """

    def __init__(self, config: OptimizationConfig):
        super().__init__(config)
        if config.max_iterations > 1000:
            logger.warning("Grid search with >1000 iterations may be slow")

    def optimize(
        self,
        objective_function: Callable[[Dict[str, Any]], float],
        param_space: Dict[str, Any],
        initial_params: Optional[Dict[str, Any]] = None
    ) -> OptimizationResult:
        """
        Perform grid search optimization.

        Creates a grid of all parameter combinations and tests each one.
        """
        import time
        start_time = time.time()

        logger.info("Starting grid search optimization")
        logger.info(f"Parameter space: {param_space}")

        # Generate parameter grid
        param_combinations = self._generate_grid(param_space)

        if len(param_combinations) > self.config.max_iterations:
            logger.warning(
                f"Grid has {len(param_combinations)} combinations, "
                f"limiting to {self.config.max_iterations} iterations"
            )
            param_combinations = param_combinations[:self.config.max_iterations]

        best_score = float('inf')
        best_params = {}
        history = []
        iteration = 0

        for params in param_combinations:
            if self.config.time_limit and (time.time() - start_time) > self.config.time_limit:
                logger.warning("Time limit reached, stopping optimization")
                break

            iteration += 1

            try:
                score = objective_function(params)
                history.append((params.copy(), score))

                if score < best_score:
                    best_score = score
                    best_params = params.copy()
                    logger.info(f"Iteration {iteration}: New best score = {score:.4f}")

                if self.config.verbose and iteration % 10 == 0:
                    logger.info(f"Grid search iteration {iteration}/{len(param_combinations)}")

            except Exception as e:
                logger.error(f"Error in iteration {iteration}: {e}")
                continue

        execution_time = time.time() - start_time
        convergence_achieved = iteration < len(param_combinations)

        logger.info(
            f"Grid search completed: {iteration} iterations, "
            f"best score = {best_score:.4f}, time = {execution_time:.2f}s"
        )

        return OptimizationResult(
            best_params=best_params,
            best_score=best_score,
            iterations=iteration,
            strategy=OptimizationStrategy.GRID_SEARCH,
            convergence_achieved=convergence_achieved,
            history=history,
            execution_time=execution_time,
            message=f"Grid search evaluated {iteration} parameter combinations"
        )

    def _generate_grid(self, param_space: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate all parameter combinations for grid search."""
        import itertools

        grid_points = []

        # Build grid for each parameter
        param_grids = {}
        for param_name, param_config in param_space.items():
            param_type = param_config.get('type', 'float')
            param_grids[param_name] = self._generate_param_grid(param_name, param_config, param_type)

        # Generate all combinations
        keys = list(param_grids.keys())
        for combination in itertools.product(*[param_grids[k] for k in keys]):
            grid_point = dict(zip(keys, combination))
            grid_points.append(grid_point)

        return grid_points

    def _generate_param_grid(
        self,
        param_name: str,
        param_config: Dict[str, Any],
        param_type: str
    ) -> List[Any]:
        """Generate grid points for a single parameter."""
        if param_type == 'choice':
            return param_config.get('values', [])
        elif param_type == 'int':
            bounds = param_config.get('bounds', (0, 100))
            step = param_config.get('step', 1)
            return list(range(bounds[0], bounds[1] + 1, step))
        elif param_type == 'float':
            bounds = param_config.get('bounds', (0.0, 1.0))
            num_points = param_config.get('num_points', 10)
            return [bounds[0] + (bounds[1] - bounds[0]) * i / (num_points - 1)
                    for i in range(num_points)]
        else:
            raise ValueError(f"Unknown parameter type: {param_type}")

    def get_strategy_description(self) -> str:
        """
        Get description of grid search strategy.

        Returns:
            Description string
        """
        return (
            "Grid Search: Exhaustively tests all parameter combinations in a predefined grid. "
            "Best for small parameter spaces where exhaustive search is feasible. "
            f"Max iterations: {self.config.max_iterations}"
        )


class BayesianOptimizationStrategy(BaseOptimizationStrategy):
    """
    Bayesian Optimization Strategy.

    Uses Gaussian Process regression to model the objective function and
    intelligently selects the next parameter combination to evaluate.
    Suitable for expensive-to-evaluate objective functions.
    """

    def __init__(self, config: OptimizationConfig):
        super().__init__(config)
        logger.info("Bayesian optimization uses acquisition functions to efficiently explore parameter space")

    def optimize(
        self,
        objective_function: Callable[[Dict[str, Any]], float],
        param_space: Dict[str, Any],
        initial_params: Optional[Dict[str, Any]] = None
    ) -> OptimizationResult:
        """
        Perform Bayesian optimization.

        Uses Gaussian Process to model the objective function and
        acquisition functions to select next points.
        """
        import time
        start_time = time.time()

        logger.info("Starting Bayesian optimization")

        # For demonstration, implement a simplified version
        # In production, would use libraries like scikit-optimize
        from .utils.gaussian_process import GaussianProcess
        from .utils.acquisition_functions import ExpectedImprovement

        # Initialize with random samples
        num_initial = min(5, self.config.max_iterations // 10)
        history = []
        iteration = 0

        # Initial random sampling
        logger.info(f"Performing initial random sampling ({num_initial} points)")
        for _ in range(num_initial):
            if self.config.time_limit and (time.time() - start_time) > self.config.time_limit:
                break

            params = self._sample_random_params(param_space)
            score = objective_function(params)
            history.append((params.copy(), score))
            iteration += 1

            logger.debug(f"Initial sample {iteration}: score = {score:.4f}")

        best_score = min(score for _, score in history)
        best_params = history[0][0].copy()

        # Bayesian optimization loop
        logger.info("Starting Bayesian optimization loop")
        while iteration < self.config.max_iterations:
            if self.config.time_limit and (time.time() - start_time) > self.config.time_limit:
                logger.warning("Time limit reached, stopping optimization")
                break

            iteration += 1

            try:
                # Fit Gaussian Process to observed data
                gp = GaussianProcess(param_space)
                gp.fit(history)

                # Use acquisition function to select next point
                acq_func = ExpectedImprovement(gp)
                next_params = acq_func.optimize(param_space)

                # Evaluate objective function
                score = objective_function(next_params)
                history.append((next_params.copy(), score))

                # Update best
                if score < best_score:
                    best_score = score
                    best_params = next_params.copy()
                    logger.info(f"Iteration {iteration}: New best score = {score:.4f}")

                if self.config.verbose and iteration % 5 == 0:
                    logger.info(
                        f"Bayesian optimization iteration {iteration}/{self.config.max_iterations}, "
                        f"best score = {best_score:.4f}"
                    )

            except Exception as e:
                logger.error(f"Error in iteration {iteration}: {e}")
                # Fallback to random sampling
                params = self._sample_random_params(param_space)
                score = objective_function(params)
                history.append((params.copy(), score))
                iteration += 1

        execution_time = time.time() - start_time
        convergence_achieved = iteration >= self.config.max_iterations

        logger.info(
            f"Bayesian optimization completed: {iteration} iterations, "
            f"best score = {best_score:.4f}, time = {execution_time:.2f}s"
        )

        return OptimizationResult(
            best_params=best_params,
            best_score=best_score,
            iterations=iteration,
            strategy=OptimizationStrategy.BAYESIAN,
            convergence_achieved=convergence_achieved,
            history=history,
            execution_time=execution_time,
            message=f"Bayesian optimization with {iteration} evaluations"
        )

    def _sample_random_params(self, param_space: Dict[str, Any]) -> Dict[str, Any]:
        """Sample random parameters from the parameter space."""
        import random
        params = {}

        for param_name, param_config in param_space.items():
            param_type = param_config.get('type', 'float')

            if param_type == 'choice':
                values = param_config.get('values', [0])
                params[param_name] = random.choice(values)
            elif param_type == 'int':
                bounds = param_config.get('bounds', (0, 100))
                params[param_name] = random.randint(bounds[0], bounds[1])
            elif param_type == 'float':
                bounds = param_config.get('bounds', (0.0, 1.0))
                params[param_name] = random.uniform(bounds[0], bounds[1])
            else:
                raise ValueError(f"Unknown parameter type: {param_type}")

        return params

    def get_strategy_description(self) -> str:
        """
        Get description of Bayesian optimization strategy.

        Returns:
            Description string
        """
        return (
            "Bayesian Optimization: Uses Gaussian Process to model the objective function "
            "and acquisition functions to efficiently explore parameter space. "
            "Best for expensive-to-evaluate objective functions. "
            f"Max iterations: {self.config.max_iterations}"
        )


class GeneticAlgorithmStrategy(BaseOptimizationStrategy):
    """
    Genetic Algorithm Optimization Strategy.

    Uses evolutionary algorithms to search for optimal parameters.
    Suitable for complex, non-linear optimization problems.
    """

    def __init__(self, config: OptimizationConfig):
        super().__init__(config)
        self.population_size = config.__dict__.get('population_size', 20)
        self.mutation_rate = config.__dict__.get('mutation_rate', 0.1)
        self.crossover_rate = config.__dict__.get('crossover_rate', 0.7)

        logger.info(
            f"Genetic algorithm: population_size={self.population_size}, "
            f"mutation_rate={self.mutation_rate}, crossover_rate={self.crossover_rate}"
        )

    def optimize(
        self,
        objective_function: Callable[[Dict[str, Any]], float],
        param_space: Dict[str, Any],
        initial_params: Optional[Dict[str, Any]] = None
    ) -> OptimizationResult:
        """
        Perform genetic algorithm optimization.

        Evolves a population of parameter sets over generations.
        """
        import time
        start_time = time.time()

        logger.info("Starting genetic algorithm optimization")

        # Initialize population
        population = self._initialize_population(param_space)
        history = []
        iteration = 0

        # Evaluate initial population
        population_scores = []
        for individual in population:
            score = objective_function(individual)
            population_scores.append(score)
            history.append((individual.copy(), score))

        best_idx = min(range(len(population_scores)), key=lambda i: population_scores[i])
        best_score = population_scores[best_idx]
        best_params = population[best_idx].copy()

        logger.info(
            f"Initial population: best score = {best_score:.4f}, "
            f"avg score = {sum(population_scores)/len(population_scores):.4f}"
        )

        # Evolution loop
        no_improvement_count = 0
        while iteration < self.config.max_iterations:
            if self.config.time_limit and (time.time() - start_time) > self.config.time_limit:
                logger.warning("Time limit reached, stopping optimization")
                break

            iteration += 1

            # Selection
            selected = self._tournament_selection(population, population_scores)

            # Crossover
            offspring = []
            for i in range(0, len(selected), 2):
                if i + 1 < len(selected):
                    child1, child2 = self._crossover(selected[i], selected[i + 1], param_space)
                    offspring.extend([child1, child2])

            # Mutation
            mutated_offspring = []
            for individual in offspring:
                mutated = self._mutate(individual, param_space)
                mutated_offspring.append(mutated)

            # Evaluate offspring
            offspring_scores = []
            for individual in mutated_offspring:
                score = objective_function(individual)
                offspring_scores.append(score)
                history.append((individual.copy(), score))

            # Update best
            min_offspring_score = min(offspring_scores)
            if min_offspring_score < best_score:
                best_idx = offspring_scores.index(min_offspring_score)
                best_score = min_offspring_score
                best_params = mutated_offspring[best_idx].copy()
                no_improvement_count = 0
                logger.info(f"Generation {iteration}: New best score = {best_score:.4f}")
            else:
                no_improvement_count += 1

            # Early stopping
            if self.config.early_stopping and no_improvement_count >= self.config.patience:
                logger.info(f"No improvement for {no_improvement_count} generations, stopping")
                break

            # Next generation
            population = mutated_offspring
            population_scores = offspring_scores

            if self.config.verbose and iteration % 5 == 0:
                avg_score = sum(population_scores) / len(population_scores)
                logger.info(
                    f"Generation {iteration}/{self.config.max_iterations}, "
                    f"best = {best_score:.4f}, avg = {avg_score:.4f}"
                )

        execution_time = time.time() - start_time
        convergence_achieved = no_improvement_count >= self.config.patience

        logger.info(
            f"Genetic algorithm completed: {iteration} generations, "
            f"best score = {best_score:.4f}, time = {execution_time:.2f}s"
        )

        return OptimizationResult(
            best_params=best_params,
            best_score=best_score,
            iterations=iteration,
            strategy=OptimizationStrategy.GENETIC,
            convergence_achieved=convergence_achieved,
            history=history,
            execution_time=execution_time,
            message=f"Genetic algorithm with {iteration} generations"
        )

    def _initialize_population(self, param_space: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Initialize random population."""
        import random
        population = []

        for _ in range(self.population_size):
            individual = {}
            for param_name, param_config in param_space.items():
                param_type = param_config.get('type', 'float')

                if param_type == 'choice':
                    values = param_config.get('values', [0])
                    individual[param_name] = random.choice(values)
                elif param_type == 'int':
                    bounds = param_config.get('bounds', (0, 100))
                    individual[param_name] = random.randint(bounds[0], bounds[1])
                elif param_type == 'float':
                    bounds = param_config.get('bounds', (0.0, 1.0))
                    individual[param_name] = random.uniform(bounds[0], bounds[1])
                else:
                    raise ValueError(f"Unknown parameter type: {param_type}")

            population.append(individual)

        return population

    def _tournament_selection(
        self,
        population: List[Dict[str, Any]],
        scores: List[float],
        tournament_size: int = 3
    ) -> List[Dict[str, Any]]:
        """Select individuals using tournament selection."""
        import random
        selected = []

        for _ in range(len(population)):
            tournament_indices = random.sample(range(len(population)), tournament_size)
            tournament_scores = [scores[i] for i in tournament_indices]
            winner_idx = tournament_indices[tournament_scores.index(min(tournament_scores))]
            selected.append(population[winner_idx].copy())

        return selected

    def _crossover(
        self,
        parent1: Dict[str, Any],
        parent2: Dict[str, Any],
        param_space: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Perform crossover between two parents."""
        import random

        if random.random() > self.crossover_rate:
            return parent1.copy(), parent2.copy()

        child1, child2 = {}, {}

        for param_name in param_space.keys():
            if random.random() < 0.5:
                child1[param_name] = parent1[param_name]
                child2[param_name] = parent2[param_name]
            else:
                child1[param_name] = parent2[param_name]
                child2[param_name] = parent1[param_name]

        return child1, child2

    def _mutate(
        self,
        individual: Dict[str, Any],
        param_space: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Mutate an individual."""
        import random

        mutated = individual.copy()

        for param_name, param_config in param_space.items():
            if random.random() < self.mutation_rate:
                param_type = param_config.get('type', 'float')

                if param_type == 'choice':
                    values = param_config.get('values', [0])
                    current_value = mutated[param_name]
                    # Choose different value
                    choices = [v for v in values if v != current_value]
                    if choices:
                        mutated[param_name] = random.choice(choices)
                elif param_type == 'int':
                    bounds = param_config.get('bounds', (0, 100))
                    mutation_strength = (bounds[1] - bounds[0]) * 0.1
                    mutated_value = int(mutated[param_name] + random.uniform(-mutation_strength, mutation_strength))
                    mutated[param_name] = max(bounds[0], min(bounds[1], mutated_value))
                elif param_type == 'float':
                    bounds = param_config.get('bounds', (0.0, 1.0))
                    mutation_strength = (bounds[1] - bounds[0]) * 0.1
                    mutated_value = mutated[param_name] + random.uniform(-mutation_strength, mutation_strength)
                    mutated[param_name] = max(bounds[0], min(bounds[1], mutated_value))

        return mutated

    def get_strategy_description(self) -> str:
        """
        Get description of genetic algorithm strategy.

        Returns:
            Description string
        """
        return (
            "Genetic Algorithm: Uses evolutionary algorithms to evolve a population of parameter sets. "
            "Suitable for complex, non-linear optimization problems. "
            f"Population size: {self.population_size}, Max iterations: {self.config.max_iterations}"
        )


class RandomSearchStrategy(BaseOptimizationStrategy):
    """
    Random Search Optimization Strategy.

    Randomly samples parameters from the search space.
    Simple and fast baseline for optimization.
    """

    def __init__(self, config: OptimizationConfig):
        super().__init__(config)

    def optimize(
        self,
        objective_function: Callable[[Dict[str, Any]], float],
        param_space: Dict[str, Any],
        initial_params: Optional[Dict[str, Any]] = None
    ) -> OptimizationResult:
        """
        Perform random search optimization.

        Randomly samples parameters and keeps the best result.
        """
        import time
        start_time = time.time()

        logger.info("Starting random search optimization")

        best_score = float('inf')
        best_params = {}
        history = []
        iteration = 0

        while iteration < self.config.max_iterations:
            if self.config.time_limit and (time.time() - start_time) > self.config.time_limit:
                logger.warning("Time limit reached, stopping optimization")
                break

            iteration += 1

            # Sample random parameters
            params = self._sample_random_params(param_space)

            # Evaluate
            try:
                score = objective_function(params)
                history.append((params.copy(), score))

                if score < best_score:
                    best_score = score
                    best_params = params.copy()
                    logger.info(f"Iteration {iteration}: New best score = {score:.4f}")

                if self.config.verbose and iteration % 10 == 0:
                    logger.info(
                        f"Random search iteration {iteration}/{self.config.max_iterations}, "
                        f"best score = {best_score:.4f}"
                    )

            except Exception as e:
                logger.error(f"Error in iteration {iteration}: {e}")
                continue

        execution_time = time.time() - start_time
        convergence_achieved = iteration >= self.config.max_iterations

        logger.info(
            f"Random search completed: {iteration} iterations, "
            f"best score = {best_score:.4f}, time = {execution_time:.2f}s"
        )

        return OptimizationResult(
            best_params=best_params,
            best_score=best_score,
            iterations=iteration,
            strategy=OptimizationStrategy.RANDOM,
            convergence_achieved=convergence_achieved,
            history=history,
            execution_time=execution_time,
            message=f"Random search with {iteration} evaluations"
        )

    def _sample_random_params(self, param_space: Dict[str, Any]) -> Dict[str, Any]:
        """Sample random parameters from the parameter space."""
        import random
        params = {}

        for param_name, param_config in param_space.items():
            param_type = param_config.get('type', 'float')

            if param_type == 'choice':
                values = param_config.get('values', [0])
                params[param_name] = random.choice(values)
            elif param_type == 'int':
                bounds = param_config.get('bounds', (0, 100))
                params[param_name] = random.randint(bounds[0], bounds[1])
            elif param_type == 'float':
                bounds = param_config.get('bounds', (0.0, 1.0))
                params[param_name] = random.uniform(bounds[0], bounds[1])
            else:
                raise ValueError(f"Unknown parameter type: {param_type}")

        return params

    def get_strategy_description(self) -> str:
        """
        Get description of random search strategy.

        Returns:
            Description string
        """
        return (
            "Random Search: Randomly samples parameters from the search space. "
            "Simple and fast baseline for optimization. "
            f"Max iterations: {self.config.max_iterations}"
        )


def create_optimization_strategy(
    strategy_type: OptimizationStrategy,
    config: OptimizationConfig
) -> BaseOptimizationStrategy:
    """
    Factory function to create optimization strategy instances.

    Args:
        strategy_type: Type of optimization strategy
        config: Optimization configuration

    Returns:
        Optimization strategy instance

    Raises:
        ValueError: If strategy type is not recognized
    """
    strategies = {
        OptimizationStrategy.GRID_SEARCH: GridSearchStrategy,
        OptimizationStrategy.BAYESIAN: BayesianOptimizationStrategy,
        OptimizationStrategy.GENETIC: GeneticAlgorithmStrategy,
        OptimizationStrategy.RANDOM: RandomSearchStrategy,
    }

    if strategy_type not in strategies:
        raise ValueError(f"Unknown optimization strategy: {strategy_type}")

    return strategies[strategy_type](config)
