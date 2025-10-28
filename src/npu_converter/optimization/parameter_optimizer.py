"""
Parameter Optimizer

Main parameter optimization module that orchestrates the optimization process.
Integrates multiple optimization strategies and provides unified interface.

Author: Story 2.6 Implementation
Version: 1.0.0
Date: 2025-10-28
"""

import time
import logging
from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass
from enum import Enum

from .optimization_strategies import (
    OptimizationStrategy,
    OptimizationConfig,
    OptimizationResult,
    create_optimization_strategy
)
from .model_analyzer import ModelAnalyzer, ModelCharacteristics
from .tradeoff_strategies import (
    TradeOffStrategy,
    TradeOffConfig,
    TradeOffWeights,
    TradeOffCalculator
)

logger = logging.getLogger(__name__)


class OptimizationObjective(Enum):
    """Optimization objective types"""
    MAXIMIZE_ACCURACY = "maximize_accuracy"
    MINIMIZE_LATENCY = "minimize_latency"
    MAXIMIZE_THROUGHPUT = "maximize_throughput"
    MINIMIZE_MEMORY = "minimize_memory"
    MAXIMIZE_COMPATIBILITY = "maximize_compatibility"
    BALANCED = "balanced"


@dataclass
class OptimizationMetrics:
    """Metrics tracked during optimization"""
    accuracy: float = 0.0
    latency: float = 0.0  # milliseconds
    throughput: float = 0.0  # samples per second
    memory_usage: float = 0.0  # MB
    compatibility: float = 1.0  # 0.0 - 1.0 (Horizon X5 BPU compatibility)
    success_rate: float = 0.0  # conversion success rate


@dataclass
class ParameterOptimizationResult:
    """Result of parameter optimization"""
    best_params: Dict[str, Any]
    best_metrics: OptimizationMetrics
    optimization_result: OptimizationResult
    model_characteristics: ModelCharacteristics
    improvement_percentage: float
    strategy_used: OptimizationStrategy
    objective: OptimizationObjective
    execution_time: float
    recommendations: List[str]


class ParameterOptimizer:
    """
    Main parameter optimizer for NPU model conversion.

    Provides intelligent parameter optimization using multiple strategies,
    model analysis, and optimization metrics tracking.
    """

    def __init__(
        self,
        model_analyzer: Optional[ModelAnalyzer] = None,
        tradeoff_calculator: Optional[TradeOffCalculator] = None,
        verbose: bool = True
    ):
        """
        Initialize parameter optimizer.

        Args:
            model_analyzer: Optional ModelAnalyzer instance
            tradeoff_calculator: Optional TradeOffCalculator instance
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.model_analyzer = model_analyzer or ModelAnalyzer()
        self.tradeoff_calculator = tradeoff_calculator or TradeOffCalculator()

        # Track optimization history
        self.optimization_history: List[ParameterOptimizationResult] = []

        logger.info("Initialized ParameterOptimizer")

    def optimize(
        self,
        model: Any,  # ONNX model or path
        param_space: Dict[str, Any],
        objective: OptimizationObjective = OptimizationObjective.BALANCED,
        strategy: OptimizationStrategy = OptimizationStrategy.BAYESIAN,
        config: Optional[OptimizationConfig] = None,
        tradeoff_config: Optional[TradeOffConfig] = None,
        max_iterations: Optional[int] = None,
        initial_params: Optional[Dict[str, Any]] = None
    ) -> ParameterOptimizationResult:
        """
        Optimize parameters for a model.

        Args:
            model: ONNX model or model path
            param_space: Dictionary defining parameter search space
                        Format: {param_name: {'type': 'float'|'int'|'choice',
                        'bounds': (min, max) or 'values': [list]}}
            objective: Optimization objective
            strategy: Optimization strategy
            config: Optimization configuration
            tradeoff_config: Trade-off configuration
            max_iterations: Override max iterations from config
            initial_params: Initial parameter values

        Returns:
            ParameterOptimizationResult with optimized parameters and metrics
        """
        start_time = time.time()

        logger.info(f"Starting parameter optimization using {strategy.value} strategy")
        logger.info(f"Optimization objective: {objective.value}")

        # Step 1: Analyze model characteristics
        logger.info("Analyzing model characteristics...")
        model_characteristics = self.model_analyzer.analyze_model(model)

        # Step 2: Initialize configurations
        if config is None:
            config = OptimizationConfig(
                max_iterations=max_iterations or 100,
                verbose=self.verbose
            )

        if tradeoff_config is None:
            # Create default tradeoff config based on objective
            if objective == OptimizationObjective.MINIMIZE_LATENCY:
                tradeoff_config = TradeOffConfig.from_strategy(TradeOffStrategy.PERFORMANCE_FIRST)
            elif objective == OptimizationObjective.MAXIMIZE_ACCURACY:
                tradeoff_config = TradeOffConfig.from_strategy(TradeOffStrategy.QUALITY_FIRST)
            elif objective == OptimizationObjective.MINIMIZE_MEMORY:
                tradeoff_config = TradeOffConfig.from_strategy(TradeOffStrategy.RESOURCE_SAVING)
            else:
                tradeoff_config = TradeOffConfig.from_strategy(TradeOffStrategy.BALANCED)

        # Step 3: Create objective function
        objective_func = self._create_objective_function(
            model,
            model_characteristics,
            objective,
            tradeoff_config
        )

        # Step 4: Get initial parameters if not provided
        if initial_params is None:
            initial_params = self._get_initial_params(param_space, model_characteristics)

        # Step 5: Run optimization
        strategy_instance = create_optimization_strategy(strategy, config)

        logger.info(f"Running optimization with {len(param_space)} parameters")
        optimization_result = strategy_instance.optimize(
            objective_function=objective_func,
            param_space=param_space,
            initial_params=initial_params
        )

        # Step 6: Evaluate best parameters
        logger.info("Evaluating optimized parameters...")
        best_metrics = self._evaluate_parameters(
            optimization_result.best_params,
            model,
            model_characteristics
        )

        # Step 7: Calculate improvement
        improvement = self._calculate_improvement(
            optimization_result.best_params,
            model,
            model_characteristics
        )

        # Step 8: Generate recommendations
        recommendations = self._generate_recommendations(
            optimization_result,
            model_characteristics,
            best_metrics
        )

        # Step 9: Create result
        result = ParameterOptimizationResult(
            best_params=optimization_result.best_params,
            best_metrics=best_metrics,
            optimization_result=optimization_result,
            model_characteristics=model_characteristics,
            improvement_percentage=improvement,
            strategy_used=strategy,
            objective=objective,
            execution_time=time.time() - start_time,
            recommendations=recommendations
        )

        # Step 10: Store in history
        self.optimization_history.append(result)

        logger.info(
            f"Optimization completed in {result.execution_time:.2f}s. "
            f"Best score: {optimization_result.best_score:.4f}, "
            f"Improvement: {improvement:.1f}%"
        )

        return result

    def _create_objective_function(
        self,
        model: Any,
        model_characteristics: ModelCharacteristics,
        objective: OptimizationObjective,
        tradeoff_config: TradeOffConfig
    ) -> Callable[[Dict[str, Any]], float]:
        """
        Create objective function for optimization.

        Args:
            model: ONNX model
            model_characteristics: Model characteristics
            objective: Optimization objective
            tradeoff_config: Trade-off configuration

        Returns:
            Objective function (lower is better)
        """
        def objective_func(params: Dict[str, Any]) -> float:
            """
            Objective function to minimize.

            Args:
                params: Parameter dictionary

            Returns:
                Objective score (lower is better)
            """
            # Evaluate parameters
            metrics = self._evaluate_parameters(params, model, model_characteristics)

            # Calculate composite score based on objective and trade-off
            score = self._calculate_composite_score(metrics, objective, tradeoff_config)

            return score

        return objective_func

    def _evaluate_parameters(
        self,
        params: Dict[str, Any],
        model: Any,
        model_characteristics: ModelCharacteristics
    ) -> OptimizationMetrics:
        """
        Evaluate parameters and return metrics.

        Args:
            params: Parameter dictionary
            model: ONNX model
            model_characteristics: Model characteristics

        Returns:
            OptimizationMetrics
        """
        # Simulated evaluation (in production, would run actual conversion)
        # This is a placeholder for the actual evaluation logic

        # Calculate metrics based on parameters and model characteristics
        base_accuracy = 0.95  # Base accuracy

        # Model type affects metrics
        if model_characteristics.model_type == "ASR":
            base_accuracy = 0.97
        elif model_characteristics.model_type == "TTS":
            base_accuracy = 0.96
        elif model_characteristics.model_type == "VISION":
            base_accuracy = 0.94

        # Parameter effects (simplified)
        quantization = params.get('quantization_bits', 16)
        if quantization == 8:
            accuracy_loss = 0.02
            latency_improvement = 0.3
        elif quantization == 16:
            accuracy_loss = 0.005
            latency_improvement = 0.15
        else:
            accuracy_loss = 0.0
            latency_improvement = 0.0

        # Calculate metrics
        accuracy = base_accuracy - accuracy_loss
        latency = 100.0 * (1 - latency_improvement)  # milliseconds
        throughput = 1000.0 / latency if latency > 0 else 0  # samples/sec
        memory_usage = 500.0 * (quantization / 16.0)  # MB
        compatibility = 1.0 if quantization in [8, 16] else 0.5
        success_rate = 0.95 if accuracy > 0.93 else 0.85

        return OptimizationMetrics(
            accuracy=accuracy,
            latency=latency,
            throughput=throughput,
            memory_usage=memory_usage,
            compatibility=compatibility,
            success_rate=success_rate
        )

    def _calculate_composite_score(
        self,
        metrics: OptimizationMetrics,
        objective: OptimizationObjective,
        tradeoff_config: TradeOffConfig
    ) -> float:
        """
        Calculate composite score for multi-objective optimization.

        Args:
            metrics: Optimization metrics
            objective: Optimization objective
            tradeoff_config: Trade-off configuration

        Returns:
            Composite score (lower is better)
        """
        # Convert metrics to dictionary
        metrics_dict = {
            'accuracy': metrics.accuracy,
            'latency': metrics.latency,
            'throughput': metrics.throughput,
            'memory': metrics.memory_usage,
            'compatibility': metrics.compatibility,
            'success_rate': metrics.success_rate
        }

        # Use TradeOffCalculator to compute score
        score = self.tradeoff_calculator.calculate_score(metrics_dict, tradeoff_config)

        # Invert to make lower better
        return 1.0 - score

    def _get_initial_params(
        self,
        param_space: Dict[str, Any],
        model_characteristics: ModelCharacteristics
    ) -> Dict[str, Any]:
        """
        Get initial parameter values.

        Args:
            param_space: Parameter space definition
            model_characteristics: Model characteristics

        Returns:
            Initial parameter values
        """
        initial_params = {}

        # Use model analyzer to get recommended parameters
        recommendations = self.model_analyzer.recommend_parameters(
            param_space,
            model_characteristics
        )

        # Build initial parameters from recommendations
        for param_name, param_config in param_space.items():
            param_type = param_config.get('type', 'float')

            if param_name in recommendations:
                initial_params[param_name] = recommendations[param_name]
            elif param_type == 'choice':
                values = param_config.get('values', [0])
                initial_params[param_name] = values[0]
            elif param_type == 'int':
                bounds = param_config.get('bounds', (0, 100))
                initial_params[param_name] = (bounds[0] + bounds[1]) // 2
            elif param_type == 'float':
                bounds = param_config.get('bounds', (0.0, 1.0))
                initial_params[param_name] = (bounds[0] + bounds[1]) / 2.0
            else:
                raise ValueError(f"Unknown parameter type: {param_type}")

        return initial_params

    def _calculate_improvement(
        self,
        params: Dict[str, Any],
        model: Any,
        model_characteristics: ModelCharacteristics
    ) -> float:
        """
        Calculate percentage improvement over baseline.

        Args:
            params: Optimized parameters
            model: ONNX model
            model_characteristics: Model characteristics

        Returns:
            Improvement percentage
        """
        # Calculate baseline score
        baseline_params = self._get_initial_params(
            {},  # Empty param space for baseline
            model_characteristics
        )
        baseline_metrics = self._evaluate_parameters(baseline_params, model, model_characteristics)
        baseline_score = self._calculate_composite_score(
            baseline_metrics,
            OptimizationObjective.BALANCED,
            TradeOffConfig.default()
        )

        # Calculate optimized score
        optimized_metrics = self._evaluate_parameters(params, model, model_characteristics)
        optimized_score = self._calculate_composite_score(
            optimized_metrics,
            OptimizationObjective.BALANCED,
            TradeOffConfig.default()
        )

        # Calculate improvement
        if baseline_score > 0:
            improvement = ((baseline_score - optimized_score) / baseline_score) * 100.0
        else:
            improvement = 0.0

        return max(0.0, improvement)

    def _generate_recommendations(
        self,
        optimization_result: OptimizationResult,
        model_characteristics: ModelCharacteristics,
        metrics: OptimizationMetrics
    ) -> List[str]:
        """
        Generate optimization recommendations.

        Args:
            optimization_result: Optimization result
            model_characteristics: Model characteristics
            metrics: Final metrics

        Returns:
            List of recommendations
        """
        recommendations = []

        # Strategy recommendation
        if optimization_result.strategy == OptimizationStrategy.BAYESIAN:
            recommendations.append(
                "Bayesian optimization is efficient for expensive evaluations. "
                "Consider using grid search for smaller parameter spaces."
            )
        elif optimization_result.strategy == OptimizationStrategy.GRID_SEARCH:
            recommendations.append(
                "Grid search provides exhaustive exploration. "
                "Consider Bayesian optimization for faster convergence."
            )

        # Accuracy recommendation
        if metrics.accuracy < 0.93:
            recommendations.append(
                f"Accuracy ({metrics.accuracy:.2%}) is below target. "
                "Consider using 16-bit quantization or adjusting other parameters."
            )

        # Latency recommendation
        if metrics.latency > 150.0:
            recommendations.append(
                f"Latency ({metrics.latency:.0f}ms) is high. "
                "Consider using 8-bit quantization or model compression."
            )

        # Compatibility recommendation
        if metrics.compatibility < 0.9:
            recommendations.append(
                f"Compatibility ({metrics.compatibility:.2%}) may cause issues. "
                "Ensure all parameters are within Horizon X5 BPU supported ranges."
            )

        # Model type specific recommendations
        if model_characteristics.model_type == "ASR":
            recommendations.append(
                "For ASR models, prioritize latency for real-time processing."
            )
        elif model_characteristics.model_type == "TTS":
            recommendations.append(
                "For TTS models, balance quality and latency for optimal user experience."
            )

        # General recommendation
        if not recommendations:
            recommendations.append(
                "Optimization completed successfully. Parameters look optimal for the given model."
            )

        return recommendations

    def get_optimization_history(self) -> List[ParameterOptimizationResult]:
        """
        Get optimization history.

        Returns:
            List of past optimization results
        """
        return self.optimization_history.copy()

    def clear_history(self) -> None:
        """Clear optimization history."""
        self.optimization_history.clear()
        logger.info("Cleared optimization history")

    def export_results(
        self,
        result: ParameterOptimizationResult,
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        Export optimization results.

        Args:
            result: Optimization result
            format: Export format (json, yaml)

        Returns:
            Exported data dictionary
        """
        export_data = {
            "best_params": result.best_params,
            "best_metrics": {
                "accuracy": result.best_metrics.accuracy,
                "latency": result.best_metrics.latency,
                "throughput": result.best_metrics.throughput,
                "memory_usage": result.best_metrics.memory_usage,
                "compatibility": result.best_metrics.compatibility,
                "success_rate": result.best_metrics.success_rate
            },
            "strategy_used": result.strategy_used.value,
            "objective": result.objective.value,
            "improvement_percentage": result.improvement_percentage,
            "execution_time": result.execution_time,
            "recommendations": result.recommendations,
            "model_characteristics": {
                "model_type": result.model_characteristics.model_type,
                "model_size": result.model_characteristics.model_size,
                "complexity_score": result.model_characteristics.complexity_score
            }
        }

        if format.lower() == "yaml":
            import yaml
            return yaml.dump(export_data, default_flow_style=False)
        else:
            import json
            return json.dumps(export_data, indent=2)
