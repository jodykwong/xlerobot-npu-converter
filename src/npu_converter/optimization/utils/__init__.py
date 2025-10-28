"""
Optimization Utilities

Utility modules for optimization algorithms.

Author: Story 2.6 Implementation
Version: 1.0.0
Date: 2025-10-28
"""

from .gaussian_process import GaussianProcess
from .acquisition_functions import ExpectedImprovement, UpperConfidenceBound

__all__ = [
    'GaussianProcess',
    'ExpectedImprovement',
    'UpperConfidenceBound',
]
