"""
Acquisition Functions for Bayesian Optimization

Functions to determine the next point to evaluate.

Author: Story 2.6 Implementation
Version: 1.0.0
Date: 2025-10-28
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple
import numpy as np
import logging

logger = logging.getLogger(__name__)


class AcquisitionFunction(ABC):
    """
    Abstract base class for acquisition functions.

    Acquisition functions balance exploration and exploitation
    to select the next point to evaluate.
    """

    def __init__(self, gp, xi: float = 0.01):
        """
        Initialize acquisition function.

        Args:
            gp: Fitted Gaussian Process
            xi: Exploration-exploitation tradeoff parameter
        """
        self.gp = gp
        self.xi = xi
        self.best_observed_value = None

    def set_best_value(self, best_value: float) -> None:
        """Set the best observed value so far."""
        self.best_observed_value = best_value

    @abstractmethod
    def evaluate(self, X: np.ndarray) -> np.ndarray:
        """
        Evaluate acquisition function at given points.

        Args:
            X: Points to evaluate (n_points, n_features)

        Returns:
            Acquisition values
        """
        pass

    @abstractmethod
    def optimize(self, param_space: Dict[str, Any]) -> Dict[str, Any]:
        """
        Find the point that maximizes the acquisition function.

        Args:
            param_space: Parameter space definition

        Returns:
            Best parameters
        """
        pass


class ExpectedImprovement(AcquisitionFunction):
    """
    Expected Improvement (EI) acquisition function.

    Computes the expected improvement over the current best point.
    Balances exploration and exploitation naturally.
    """

    def evaluate(self, X: np.ndarray) -> np.ndarray:
        """
        Evaluate Expected Improvement at given points.

        Args:
            X: Points to evaluate (n_points, n_features)

        Returns:
            EI values
        """
        if self.best_observed_value is None:
            raise ValueError("Must set best_observed_value before evaluation")

        # Get GP predictions
        mu, var = self.gp.predict(X)
        std = np.sqrt(var)

        # Ensure std is not zero
        std = np.maximum(std, 1e-9)

        # Compute improvement
        z = (self.best_observed_value - mu - self.xi) / std

        # Normal distribution CDF and PDF
        Phi = 0.5 * (1 + np.erf(z / np.sqrt(2)))
        phi = np.exp(-0.5 * z ** 2) / np.sqrt(2 * np.pi)

        # Expected improvement
        ei = (self.best_observed_value - mu - self.xi) * Phi + std * phi

        return ei

    def optimize(self, param_space: Dict[str, Any]) -> Dict[str, Any]:
        """
        Find point that maximizes Expected Improvement.

        Args:
            param_space: Parameter space definition

        Returns:
            Best parameters
        """
        # Generate candidate points
        candidates = self._generate_candidates(param_space, n_candidates=100)

        # Evaluate EI
        ei_values = self.evaluate(candidates)

        # Find best
        best_idx = np.argmax(ei_values)
        best_candidate = candidates[best_idx]

        # Convert back to parameter dictionary
        params = self._array_to_params(best_candidate, param_space)

        logger.debug(f"EI optimization found best params: {params}, EI = {ei_values[best_idx]:.4f}")

        return params

    def _generate_candidates(
        self,
        param_space: Dict[str, Any],
        n_candidates: int = 100
    ) -> np.ndarray:
        """
        Generate candidate points for optimization.

        Args:
            param_space: Parameter space definition
            n_candidates: Number of candidates to generate

        Returns:
            Candidate points array
        """
        import random

        candidates = []
        for _ in range(n_candidates):
            candidate = []
            for param_name in sorted(param_space.keys()):
                param_config = param_space[param_name]
                param_type = param_config.get('type', 'float')

                if param_type == 'choice':
                    values = param_config.get('values', [0])
                    candidate.append(random.choice(values))
                elif param_type == 'int':
                    bounds = param_config.get('bounds', (0, 100))
                    candidate.append(random.randint(bounds[0], bounds[1]))
                elif param_type == 'float':
                    bounds = param_config.get('bounds', (0.0, 1.0))
                    candidate.append(random.uniform(bounds[0], bounds[1]))
                else:
                    raise ValueError(f"Unknown parameter type: {param_type}")

            candidates.append(candidate)

        return np.array(candidates)

    def _array_to_params(
        self,
        array: np.ndarray,
        param_space: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Convert numpy array to parameter dictionary.

        Args:
            array: Parameter array
            param_space: Parameter space definition

        Returns:
            Parameter dictionary
        """
        params = {}
        param_names = sorted(param_space.keys())

        for i, param_name in enumerate(param_names):
            param_config = param_space[param_name]
            param_type = param_config.get('type', 'float')
            value = array[i]

            if param_type == 'choice':
                # Round to nearest valid choice
                values = param_config.get('values', [0])
                params[param_name] = min(values, key=lambda x: abs(x - value))
            elif param_type == 'int':
                params[param_name] = int(round(value))
            elif param_type == 'float':
                params[param_name] = float(value)

        return params


class UpperConfidenceBound(AcquisitionFunction):
    """
    Upper Confidence Bound (UCB) acquisition function.

    Computes a confidence bound on the objective function.
    Provides explicit control over exploration.
    """

    def __init__(self, gp, beta: float = 2.0):
        """
        Initialize UCB acquisition function.

        Args:
            gp: Fitted Gaussian Process
            beta: Exploration parameter (higher = more exploration)
        """
        super().__init__(gp)
        self.beta = beta

    def evaluate(self, X: np.ndarray) -> np.ndarray:
        """
        Evaluate UCB at given points.

        Args:
            X: Points to evaluate (n_points, n_features)

        Returns:
            UCB values
        """
        # Get GP predictions
        mu, var = self.gp.predict(X)
        std = np.sqrt(var)

        # UCB = mu + beta * std
        ucb = mu + self.beta * std

        return ucb

    def optimize(self, param_space: Dict[str, Any]) -> Dict[str, Any]:
        """
        Find point that maximizes UCB.

        Args:
            param_space: Parameter space definition

        Returns:
            Best parameters
        """
        # Generate candidate points
        candidates = self._generate_candidates(param_space, n_candidates=100)

        # Evaluate UCB
        ucb_values = self.evaluate(candidates)

        # Find best
        best_idx = np.argmax(ucb_values)
        best_candidate = candidates[best_idx]

        # Convert back to parameter dictionary
        params = self._array_to_params(best_candidate, param_space)

        logger.debug(f"UCB optimization found best params: {params}, UCB = {ucb_values[best_idx]:.4f}")

        return params

    def _generate_candidates(
        self,
        param_space: Dict[str, Any],
        n_candidates: int = 100
    ) -> np.ndarray:
        """Generate candidate points (same as ExpectedImprovement)."""
        import random

        candidates = []
        for _ in range(n_candidates):
            candidate = []
            for param_name in sorted(param_space.keys()):
                param_config = param_space[param_name]
                param_type = param_config.get('type', 'float')

                if param_type == 'choice':
                    values = param_config.get('values', [0])
                    candidate.append(random.choice(values))
                elif param_type == 'int':
                    bounds = param_config.get('bounds', (0, 100))
                    candidate.append(random.randint(bounds[0], bounds[1]))
                elif param_type == 'float':
                    bounds = param_config.get('bounds', (0.0, 1.0))
                    candidate.append(random.uniform(bounds[0], bounds[1]))
                else:
                    raise ValueError(f"Unknown parameter type: {param_type}")

            candidates.append(candidate)

        return np.array(candidates)

    def _array_to_params(
        self,
        array: np.ndarray,
        param_space: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert numpy array to parameter dictionary (same as ExpectedImprovement)."""
        params = {}
        param_names = sorted(param_space.keys())

        for i, param_name in enumerate(param_names):
            param_config = param_space[param_name]
            param_type = param_config.get('type', 'float')
            value = array[i]

            if param_type == 'choice':
                values = param_config.get('values', [0])
                params[param_name] = min(values, key=lambda x: abs(x - value))
            elif param_type == 'int':
                params[param_name] = int(round(value))
            elif param_type == 'float':
                params[param_name] = float(value)

        return params
