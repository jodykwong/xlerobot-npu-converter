"""
Trade-off Strategies

Provides different quality-performance trade-off strategies for optimization.
Supports predefined strategies and custom weight configurations.

Author: Story 2.6 Implementation
Version: 1.0.0
Date: 2025-10-28
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class TradeOffStrategy(Enum):
    """Predefined trade-off strategies"""
    QUALITY_FIRST = "quality_first"
    PERFORMANCE_FIRST = "performance_first"
    BALANCED = "balanced"
    RESOURCE_SAVING = "resource_saving"
    CUSTOM = "custom"


@dataclass
class TradeOffWeights:
    """Weight configuration for trade-off objectives"""
    accuracy: float
    latency: float
    throughput: float
    memory: float
    compatibility: float
    success_rate: float

    def validate(self) -> bool:
        """Validate that weights are non-negative."""
        weights = [self.accuracy, self.latency, self.throughput, self.memory,
                   self.compatibility, self.success_rate]
        return all(w >= 0 for w in weights)

    def normalize(self) -> 'TradeOffWeights':
        """Normalize weights to sum to 1.0."""
        total = self.accuracy + self.latency + self.throughput + self.memory + \
                self.compatibility + self.success_rate

        if total == 0:
            return TradeOffWeights(1/6, 1/6, 1/6, 1/6, 1/6, 1/6)

        return TradeOffWeights(
            self.accuracy / total,
            self.latency / total,
            self.throughput / total,
            self.memory / total,
            self.compatibility / total,
            self.success_rate / total
        )


@dataclass
class TradeOffConfig:
    """Configuration for trade-off strategy"""
    strategy: TradeOffStrategy
    weights: TradeOffWeights
    custom_weights: Optional[TradeOffWeights] = None

    @classmethod
    def from_strategy(cls, strategy: TradeOffStrategy) -> 'TradeOffConfig':
        """
        Create configuration from predefined strategy.

        Args:
            strategy: Trade-off strategy

        Returns:
            TradeOffConfig instance
        """
        if strategy == TradeOffStrategy.QUALITY_FIRST:
            # Prioritize accuracy and quality, moderate performance
            weights = TradeOffWeights(
                accuracy=0.7,
                latency=0.2,
                throughput=0.05,
                memory=0.03,
                compatibility=0.01,
                success_rate=0.01
            )
        elif strategy == TradeOffStrategy.PERFORMANCE_FIRST:
            # Prioritize speed and throughput
            weights = TradeOffWeights(
                accuracy=0.3,
                latency=0.4,
                throughput=0.2,
                memory=0.05,
                compatibility=0.03,
                success_rate=0.02
            )
        elif strategy == TradeOffStrategy.BALANCED:
            # Balance all objectives
            weights = TradeOffWeights(
                accuracy=0.25,
                latency=0.25,
                throughput=0.15,
                memory=0.15,
                compatibility=0.1,
                success_rate=0.1
            )
        elif strategy == TradeOffStrategy.RESOURCE_SAVING:
            # Minimize resource usage
            weights = TradeOffWeights(
                accuracy=0.2,
                latency=0.15,
                throughput=0.1,
                memory=0.35,
                compatibility=0.1,
                success_rate=0.1
            )
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        return cls(strategy=strategy, weights=weights)

    @classmethod
    def from_custom_weights(cls, weights: TradeOffWeights) -> 'TradeOffConfig':
        """
        Create configuration from custom weights.

        Args:
            weights: Custom weight configuration

        Returns:
            TradeOffConfig instance
        """
        if not weights.validate():
            raise ValueError("All weights must be non-negative")

        normalized_weights = weights.normalize()

        return cls(
            strategy=TradeOffStrategy.CUSTOM,
            weights=normalized_weights,
            custom_weights=weights
        )

    @classmethod
    def default(cls) -> 'TradeOffConfig':
        """
        Get default trade-off configuration (balanced).

        Returns:
            Default TradeOffConfig
        """
        return cls.from_strategy(TradeOffStrategy.BALANCED)

    def get_weights(self) -> TradeOffWeights:
        """
        Get effective weights (custom weights if available, else predefined).

        Returns:
            TradeOffWeights instance
        """
        if self.custom_weights is not None:
            return self.custom_weights.normalize()
        return self.weights

    def get_description(self) -> str:
        """
        Get human-readable description of the strategy.

        Returns:
            Description string
        """
        if self.strategy == TradeOffStrategy.QUALITY_FIRST:
            return (
                "Quality First: Maximize accuracy and model quality, "
                "with moderate emphasis on latency. Best for production "
                "systems where output quality is critical."
            )
        elif self.strategy == TradeOffStrategy.PERFORMANCE_FIRST:
            return (
                "Performance First: Prioritize speed and throughput. "
                "Best for real-time applications where low latency "
                "is essential."
            )
        elif self.strategy == TradeOffStrategy.BALANCED:
            return (
                "Balanced: Balance all objectives evenly. "
                "Good default choice for general-purpose optimization."
            )
        elif self.strategy == TradeOffStrategy.RESOURCE_SAVING:
            return (
                "Resource Saving: Minimize memory and resource usage. "
                "Best for edge devices or constrained environments."
            )
        elif self.strategy == TradeOffStrategy.CUSTOM:
            return (
                "Custom: User-defined weights for specific optimization goals. "
                "Flexible configuration for specialized requirements."
            )
        else:
            return "Unknown strategy"


class TradeOffCalculator:
    """
    Calculates trade-off scores and estimates optimization outcomes.

    Provides utilities to predict optimization outcomes and compare strategies.
    """

    def __init__(self):
        """Initialize trade-off calculator."""
        logger.info("Initialized TradeOffCalculator")

    def calculate_score(
        self,
        metrics: Dict[str, float],
        config: TradeOffConfig
    ) -> float:
        """
        Calculate composite score based on metrics and trade-off config.

        Args:
            metrics: Dictionary of metric values
                     Expected keys: accuracy, latency, throughput, memory,
                                    compatibility, success_rate
            config: Trade-off configuration

        Returns:
            Composite score (0.0 - 1.0, higher is better)
        """
        weights = config.get_weights()

        # Normalize metrics (convert to 0-1 range, higher is better)
        norm_metrics = self._normalize_metrics(metrics)

        # Calculate weighted score
        score = (
            weights.accuracy * norm_metrics.get('accuracy', 0) +
            weights.latency * norm_metrics.get('latency', 0) +
            weights.throughput * norm_metrics.get('throughput', 0) +
            weights.memory * norm_metrics.get('memory', 0) +
            weights.compatibility * norm_metrics.get('compatibility', 0) +
            weights.success_rate * norm_metrics.get('success_rate', 0)
        )

        return score

    def estimate_outcome(
        self,
        model_type: str,
        config: TradeOffConfig,
        model_complexity: float = 0.5
    ) -> Dict[str, Any]:
        """
        Estimate optimization outcome for a model type and strategy.

        Args:
            model_type: Type of model (ASR, TTS, VISION, etc.)
            config: Trade-off configuration
            model_complexity: Model complexity (0.0 - 1.0)

        Returns:
            Dictionary with estimated metrics
        """
        # Base expectations by model type
        base_metrics = {
            'ASR': {'accuracy': 0.97, 'latency': 100, 'throughput': 10},
            'TTS': {'accuracy': 0.96, 'latency': 120, 'throughput': 8},
            'VISION': {'accuracy': 0.94, 'latency': 50, 'throughput': 20},
            'NLP': {'accuracy': 0.95, 'latency': 80, 'throughput': 12}
        }.get(model_type.upper(), {
            'accuracy': 0.95,
            'latency': 100,
            'throughput': 10
        })

        # Adjust based on trade-off strategy
        weights = config.get_weights()

        # Quality strategy improves accuracy
        if weights.accuracy > 0.4:
            base_metrics['accuracy'] = min(0.99, base_metrics['accuracy'] * 1.02)

        # Performance strategy reduces latency
        if weights.latency > 0.3:
            base_metrics['latency'] = max(30, base_metrics['latency'] * 0.85)
            base_metrics['throughput'] *= 1.2

        # Resource saving reduces memory
        base_metrics['memory'] = 500 * (1.0 - weights.memory * 0.5)

        # Calculate dependent metrics
        base_metrics['throughput'] = max(1, base_metrics['throughput'])
        base_metrics['compatibility'] = 0.95
        base_metrics['success_rate'] = 0.95

        # Complexity adjustment
        base_metrics['latency'] *= (1 + model_complexity * 0.5)
        base_metrics['memory'] *= (1 + model_complexity)

        return base_metrics

    def compare_strategies(
        self,
        model_type: str,
        strategies: list[TradeOffStrategy],
        model_complexity: float = 0.5
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compare multiple trade-off strategies.

        Args:
            model_type: Type of model
            strategies: List of strategies to compare
            model_complexity: Model complexity (0.0 - 1.0)

        Returns:
            Dictionary mapping strategy name to estimated metrics
        """
        comparison = {}

        for strategy in strategies:
            config = TradeOffConfig.from_strategy(strategy)
            outcome = self.estimate_outcome(model_type, config, model_complexity)

            comparison[strategy.value] = {
                'metrics': outcome,
                'description': config.get_description()
            }

        return comparison

    def _normalize_metrics(self, metrics: Dict[str, float]) -> Dict[str, float]:
        """
        Normalize metrics to 0-1 range.

        Args:
            metrics: Raw metric values

        Returns:
            Normalized metrics (all 0.0 - 1.0, higher is better)
        """
        normalized = {}

        # Accuracy: already 0-1
        normalized['accuracy'] = metrics.get('accuracy', 0.0)

        # Latency: inverse relationship, 0-1 (lower latency is better)
        latency = metrics.get('latency', 100.0)
        normalized['latency'] = 1.0 / (1.0 + latency / 1000.0)

        # Throughput: normalize to 0-1 (assume max 100 samples/sec)
        throughput = metrics.get('throughput', 0.0)
        normalized['throughput'] = min(1.0, throughput / 100.0)

        # Memory: inverse relationship (lower memory is better)
        memory = metrics.get('memory', 1000.0)
        normalized['memory'] = 1.0 / (1.0 + memory / 1000.0)

        # Compatibility: already 0-1
        normalized['compatibility'] = metrics.get('compatibility', 0.0)

        # Success rate: already 0-1
        normalized['success_rate'] = metrics.get('success_rate', 0.0)

        return normalized

    def get_strategy_recommendation(
        self,
        use_case: str,
        constraints: Optional[Dict[str, float]] = None
    ) -> TradeOffStrategy:
        """
        Recommend trade-off strategy based on use case.

        Args:
            use_case: Description of use case
            constraints: Optional constraints (e.g., {'latency_max': 50})

        Returns:
            Recommended TradeOffStrategy
        """
        use_case_lower = use_case.lower()

        # Check constraints first
        if constraints:
            if constraints.get('latency_max', float('inf')) < 60:
                return TradeOffStrategy.PERFORMANCE_FIRST
            if constraints.get('memory_max', float('inf')) < 500:
                return TradeOffStrategy.RESOURCE_SAVING
            if constraints.get('accuracy_min', 0) > 0.97:
                return TradeOffStrategy.QUALITY_FIRST

        # Use case based recommendations
        if any(keyword in use_case_lower for keyword in
               ['real-time', 'realtime', 'streaming', 'live']):
            return TradeOffStrategy.PERFORMANCE_FIRST

        if any(keyword in use_case_lower for keyword in
               ['quality', 'production', 'accuracy', 'precision']):
            return TradeOffStrategy.QUALITY_FIRST

        if any(keyword in use_case_lower for keyword in
               ['edge', 'mobile', 'embedded', 'constrained']):
            return TradeOffStrategy.RESOURCE_SAVING

        if any(keyword in use_case_lower for keyword in
               ['general', 'balanced', 'default', 'standard']):
            return TradeOffStrategy.BALANCED

        # Default recommendation
        return TradeOffStrategy.BALANCED


# Convenience functions
def get_predefined_strategies() -> list[TradeOffStrategy]:
    """Get list of all predefined trade-off strategies."""
    return [
        TradeOffStrategy.QUALITY_FIRST,
        TradeOffStrategy.PERFORMANCE_FIRST,
        TradeOffStrategy.BALANCED,
        TradeOffStrategy.RESOURCE_SAVING
    ]


def create_custom_config(
    accuracy: float = 0.25,
    latency: float = 0.25,
    throughput: float = 0.15,
    memory: float = 0.15,
    compatibility: float = 0.1,
    success_rate: float = 0.1
) -> TradeOffConfig:
    """
    Create custom trade-off configuration.

    Args:
        accuracy: Weight for accuracy objective
        latency: Weight for latency objective
        throughput: Weight for throughput objective
        memory: Weight for memory objective
        compatibility: Weight for compatibility objective
        success_rate: Weight for success rate objective

    Returns:
        Custom TradeOffConfig
    """
    weights = TradeOffWeights(
        accuracy=accuracy,
        latency=latency,
        throughput=throughput,
        memory=memory,
        compatibility=compatibility,
        success_rate=success_rate
    )

    return TradeOffConfig.from_custom_weights(weights)
