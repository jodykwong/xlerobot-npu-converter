"""
Parameter Optimization Module

This module provides intelligent parameter optimization capabilities for NPU model conversion.
Supports multiple optimization algorithms, model analysis, optimization history management,
and comprehensive reporting.

Author: Story 2.6 Implementation
Version: 1.0.0
Date: 2025-10-28
"""

# Core components
from .parameter_optimizer import (
    ParameterOptimizer,
    ParameterOptimizationResult,
    OptimizationObjective,
    OptimizationMetrics
)
from .model_analyzer import (
    ModelAnalyzer,
    ModelCharacteristics,
    ModelType,
    ParameterRecommendation
)
from .history_manager import (
    OptimizationHistory,
    OptimizationEntry,
    VersionComparison,
    HistoryStorageFormat,
    VersionTag
)
from .tradeoff_strategies import (
    TradeOffStrategy,
    TradeOffConfig,
    TradeOffWeights,
    TradeOffCalculator
)
from .report_generator import OptimizationReportGenerator
from .optimization_strategies import (
    OptimizationStrategy,
    OptimizationConfig,
    OptimizationResult,
    create_optimization_strategy
)
from .preprocessing_integration import (
    PreprocessingOptimizer,
    PreprocessingOptimizationConfig
)

__all__ = [
    # Core classes
    'ParameterOptimizer',
    'ParameterOptimizationResult',
    'OptimizationObjective',
    'OptimizationMetrics',

    # Model analysis
    'ModelAnalyzer',
    'ModelCharacteristics',
    'ModelType',
    'ParameterRecommendation',

    # History management
    'OptimizationHistory',
    'OptimizationEntry',
    'VersionComparison',
    'HistoryStorageFormat',
    'VersionTag',

    # Trade-off strategies
    'TradeOffStrategy',
    'TradeOffConfig',
    'TradeOffWeights',
    'TradeOffCalculator',

    # Optimization strategies
    'OptimizationStrategy',
    'OptimizationConfig',
    'OptimizationResult',
    'create_optimization_strategy',

    # Reporting
    'OptimizationReportGenerator',

    # Preprocessing integration
    'PreprocessingOptimizer',
    'PreprocessingOptimizationConfig',
]

