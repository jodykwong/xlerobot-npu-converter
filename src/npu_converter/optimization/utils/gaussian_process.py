"""
Gaussian Process for Bayesian Optimization

Simplified implementation of Gaussian Process for parameter optimization.
In production, would use libraries like scikit-learn or GPy.

Author: Story 2.6 Implementation
Version: 1.0.0
Date: 2025-10-28
"""

import numpy as np
from typing import List, Dict, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class GaussianProcess:
    """
    Simplified Gaussian Process implementation for Bayesian optimization.

    Models the objective function as a Gaussian Process and provides
    predictions and uncertainty estimates.
    """

    def __init__(
        self,
        param_space: Dict[str, Any],
        length_scale: float = 1.0,
        variance: float = 1.0,
        noise_level: float = 1e-6
    ):
        """
        Initialize Gaussian Process.

        Args:
            param_space: Parameter space definition
            length_scale: RBF kernel length scale
            variance: RBF kernel variance
            noise_level: Noise level for observations
        """
        self.param_space = param_space
        self.length_scale = length_scale
        self.variance = variance
        self.noise_level = noise_level

        self.X_train = None  # Training inputs
        self.y_train = None  # Training outputs
        self.is_fitted = False

        logger.debug(f"Initialized Gaussian Process with length_scale={length_scale}, variance={variance}")

    def fit(self, observations: List[Tuple[Dict[str, Any], float]]) -> None:
        """
        Fit the Gaussian Process to observed data.

        Args:
            observations: List of (params, score) pairs
        """
        if len(observations) < 2:
            logger.warning("Need at least 2 observations to fit GP")
            return

        # Convert observations to arrays
        self.X_train = np.array([self._params_to_array(obs[0]) for obs in observations])
        self.y_train = np.array([obs[1] for obs in observations])

        self.is_fitted = True

        logger.debug(f"Fitted GP with {len(observations)} observations")

    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict mean and variance at given points.

        Args:
            X: Input points (n_samples, n_features)

        Returns:
            Tuple of (mean, variance) arrays
        """
        if not self.is_fitted:
            raise ValueError("GP must be fitted before prediction")

        # Simplified kernel function
        X_train = self.X_train
        n_train = X_train.shape[0]

        # Compute kernel matrices
        K = self._rbf_kernel(X_train, X_train)
        K += self.noise_level * np.eye(n_train)  # Add noise
        K_inv = np.linalg.inv(K)

        K_s = self._rbf_kernel(X_train, X)  # (n_train, n_test)
        K_ss = self._rbf_kernel(X, X) + self.variance * np.eye(X.shape[0])

        # Predictive mean
        mu = K_s.T @ K_inv @ self.y_train

        # Predictive variance
        var = np.diag(K_ss - K_s.T @ K_inv @ K_s)

        # Ensure variance is positive
        var = np.maximum(var, self.noise_level)

        return mu, var

    def _rbf_kernel(self, X1: np.ndarray, X2: np.ndarray) -> np.ndarray:
        """
        Compute RBF (Gaussian) kernel between two sets of points.

        Args:
            X1: First set of points (n1, d)
            X2: Second set of points (n2, d)

        Returns:
            Kernel matrix (n1, n2)
        """
        # Euclidean distance matrix
        dists = self._euclidean_distances(X1, X2)

        # RBF kernel
        K = self.variance * np.exp(-0.5 * (dists / self.length_scale) ** 2)

        return K

    def _euclidean_distances(self, X1: np.ndarray, X2: np.ndarray) -> np.ndarray:
        """
        Compute Euclidean distances between two sets of points.

        Args:
            X1: First set of points (n1, d)
            X2: Second set of points (n2, d)

        Returns:
            Distance matrix (n1, n2)
        """
        # Squared distances
        sq_dists = np.sum(X1**2, axis=1, keepdims=True) + np.sum(X2**2, axis=1) - 2 * X1 @ X2.T

        # Ensure non-negative (numerical errors)
        sq_dists = np.maximum(sq_dists, 0)

        # Square root
        return np.sqrt(sq_dists)

    def _params_to_array(self, params: Dict[str, Any]) -> np.ndarray:
        """
        Convert parameter dictionary to numpy array.

        Args:
            params: Parameter dictionary

        Returns:
            Parameter array
        """
        values = []
        for param_name in sorted(self.param_space.keys()):
            param_config = self.param_space[param_name]
            param_type = param_config.get('type', 'float')
            value = params[param_name]

            if param_type == 'choice':
                # Map categorical to numeric
                values.append(float(value))
            else:
                values.append(float(value))

        return np.array(values)
