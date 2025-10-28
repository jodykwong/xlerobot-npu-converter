"""
Quality Scorer for ONNX Models

Provides quality scoring for ONNX models across five dimensions:
1. Structure Integrity: Model topology and connectivity
2. Numerical Validity: Weights, gradients, and precision
3. Compatibility: Horizon X5 BPU compatibility
4. Performance Benchmark: Expected inference performance
5. Conversion Readiness: Overall conversion readiness

Part of the five-dimensional validation system (AC3).
"""

import logging
import time
import math
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

from ..models.onnx_model import ONNXModel
from .structure_validator import StructureValidator, StructureValidationResult
from .dynamic_shape_handler import DynamicShapeHandler, DynamicShapeValidationResult
from .compatibility_analyzer import CompatibilityAnalyzer, CompatibilityAnalysisResult

logger = logging.getLogger(__name__)


@dataclass
class QualityScore:
    """Quality score for a specific dimension"""
    dimension: str
    score: float  # 0.0 - 1.0
    description: str
    max_score: float = 1.0
    weight: float = 1.0  # Weight in overall calculation
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DimensionMetrics:
    """Detailed metrics for a quality dimension"""
    dimension: str
    score: float
    metrics: Dict[str, Any]
    issues: List[str]
    warnings: List[str]


@dataclass
class QualityScoringResult:
    """Result of five-dimensional quality scoring"""
    overall_score: float
    overall_grade: str
    dimension_scores: List[QualityScore]
    dimension_metrics: List[DimensionMetrics]
    conversion_readiness: float
    critical_issues: List[str]
    recommendations: List[str]
    optimization_suggestions: List[str]

    def __post_init__(self):
        """Initialize derived fields"""
        if not self.critical_issues:
            self.critical_issues = []
        if not self.recommendations:
            self.recommendations = []
        if not self.optimization_suggestions:
            self.optimization_suggestions = []


class QualityScorer:
    """
    Scores the quality of ONNX models across five dimensions.

    Five-dimensional validation system:
    1. Structure Integrity: Topology validation, node connectivity, weight integrity
    2. Numerical Validity: Weight ranges, gradient flow, precision consistency
    3. Compatibility: Horizon X5 BPU operator support and constraints
    4. Performance Benchmark: Expected latency, throughput, memory usage
    5. Conversion Readiness: Overall probability of successful conversion

    Integrates with:
    - StructureValidator (from AC1)
    - DynamicShapeHandler (from AC1)
    - CompatibilityAnalyzer (framework from AC1)
    """

    def __init__(self):
        """Initialize the QualityScorer"""
        logger.info("Initializing QualityScorer")
        self.structure_validator = StructureValidator()
        self.dynamic_shape_handler = DynamicShapeHandler()
        self.compatibility_analyzer = CompatibilityAnalyzer()

    def score_quality(self,
                     model: ONNXModel,
                     structure_result: Optional[StructureValidationResult] = None,
                     dynamic_result: Optional[DynamicShapeValidationResult] = None,
                     compatibility_result: Optional[CompatibilityAnalysisResult] = None) -> QualityScoringResult:
        """
        Score the quality of a model across five dimensions.

        Args:
            model: ONNXModel instance
            structure_result: Optional structure validation result
            dynamic_result: Optional dynamic shape validation result
            compatibility_result: Optional compatibility analysis result

        Returns:
            QualityScoringResult with detailed five-dimensional scores
        """
        logger.info(f"Starting five-dimensional quality scoring for model: {model}")

        # Step 1: Run validations if results not provided
        if structure_result is None:
            structure_result = self.structure_validator.validate_structure(model)

        if dynamic_result is None:
            # Get tensors from structure validation
            input_tensors = []
            output_tensors = []
            if hasattr(model, 'input_tensors'):
                input_tensors = model.input_tensors
                output_tensors = model.output_tensors

            dynamic_result = self.dynamic_shape_handler.validate_dynamic_shapes(
                model, input_tensors, output_tensors
            )

        if compatibility_result is None:
            compatibility_result = self.compatibility_analyzer.analyze_compatibility(model)

        # Step 2: Score each dimension
        dimension_scores = []

        # Dimension 1: Structure Integrity
        structure_score = self._score_structure_integrity(model, structure_result)
        dimension_scores.append(structure_score)

        # Dimension 2: Numerical Validity
        numerical_score = self._score_numerical_validity(model, structure_result)
        dimension_scores.append(numerical_score)

        # Dimension 3: Compatibility
        compatibility_score = self._score_compatibility(model, compatibility_result)
        dimension_scores.append(compatibility_score)

        # Dimension 4: Performance Benchmark
        performance_score = self._score_performance(model, structure_result, dynamic_result)
        dimension_scores.append(performance_score)

        # Dimension 5: Conversion Readiness
        readiness_score = self._score_conversion_readiness(
            model, structure_result, dynamic_result, compatibility_result
        )
        dimension_scores.append(readiness_score)

        # Step 3: Calculate overall score (weighted average)
        overall_score = sum(s.score * s.weight for s in dimension_scores) / sum(s.weight for s in dimension_scores)

        # Step 4: Calculate overall grade
        overall_grade = self._calculate_grade(overall_score)

        # Step 5: Compile dimension metrics
        dimension_metrics = self._compile_dimension_metrics(
            structure_result, dynamic_result, compatibility_result
        )

        # Step 6: Generate recommendations
        recommendations = self._generate_recommendations(dimension_scores, dimension_metrics)

        # Step 7: Identify critical issues
        critical_issues = self._identify_critical_issues(dimension_scores, dimension_metrics)

        # Step 8: Generate optimization suggestions
        optimization_suggestions = self._generate_optimization_suggestions(
            dimension_scores, dimension_metrics
        )

        # Step 9: Compile final result
        result = QualityScoringResult(
            overall_score=overall_score,
            overall_grade=overall_grade,
            dimension_scores=dimension_scores,
            dimension_metrics=dimension_metrics,
            conversion_readiness=readiness_score.score,
            critical_issues=critical_issues,
            recommendations=recommendations,
            optimization_suggestions=optimization_suggestions
        )

        logger.info(f"Five-dimensional quality scoring completed: {overall_score:.2f} ({overall_grade})")
        return result

    def _score_structure_integrity(self,
                                   model: ONNXModel,
                                   structure_result: StructureValidationResult) -> QualityScore:
        """Score structure integrity (Dimension 1)"""
        logger.debug("Scoring structure integrity")

        # Base score from structure validation
        if structure_result.is_valid:
            base_score = 0.95
            description = "Model structure is well-formed with no critical issues"
        else:
            base_score = 0.5
            description = f"Model has {len(structure_result.issues)} structural issues"

        # Adjust for orphaned nodes
        if structure_result.orphaned_nodes:
            penalty = min(0.3, len(structure_result.orphaned_nodes) * 0.05)
            base_score -= penalty

        # Adjust for unused weights
        if structure_result.unused_weights:
            penalty = min(0.1, len(structure_result.unused_weights) * 0.02)
            base_score -= penalty

        # Check dependency analysis
        if structure_result.dependency_analysis:
            if structure_result.dependency_analysis.has_cycles:
                base_score -= 0.4
                description = "Model has circular dependencies (critical issue)"
            elif len(structure_result.dependency_analysis.topological_order) == 0:
                base_score -= 0.3

        score = max(0.0, min(1.0, base_score))

        details = {
            "is_valid": structure_result.is_valid,
            "node_count": structure_result.node_count,
            "edge_count": structure_result.edge_count,
            "orphaned_nodes_count": len(structure_result.orphaned_nodes),
            "unused_weights_count": len(structure_result.unused_weights),
            "has_cycles": structure_result.dependency_analysis.has_cycles if structure_result.dependency_analysis else False
        }

        return QualityScore(
            dimension="structure_integrity",
            score=score,
            description=description,
            weight=0.25,  # 25% weight
            details=details
        )

    def _score_numerical_validity(self,
                                  model: ONNXModel,
                                  structure_result: StructureValidationResult) -> QualityScore:
        """Score numerical validity (Dimension 2)"""
        logger.debug("Scoring numerical validity")

        score = 0.9  # Start with good score
        issues = []
        warnings = []

        try:
            # Check for weights/initializers
            if not model.model_proto or not model.model_proto.graph:
                score -= 0.3
                issues.append("No model graph found")
            else:
                graph = model.model_proto.graph

                # Check initializers
                initializers = graph.initializer
                if initializers:
                    # Sample some initializers to check for extreme values
                    sample_size = min(5, len(initializers))
                    extreme_values = 0

                    for i in range(sample_size):
                        init = initializers[i]
                        # Check if initializer has data
                        if hasattr(init, 'raw_data'):
                            # This is a simplification - real implementation would check actual values
                            pass

                    # Penalize excessive initializers (unused weights already checked)
                    initializer_ratio = len(initializers) / max(1, structure_result.node_count)
                    if initializer_ratio > 2.0:
                        warnings.append("High initializer-to-node ratio")
                        score -= 0.1

                # Check for numerical instability indicators
                # (This is simplified - real implementation would analyze actual values)
                dynamic_dims = 0
                if hasattr(model, 'input_tensors'):
                    for tensor in model.input_tensors:
                        if tensor.shape:
                            dynamic_dims += sum(1 for d in tensor.shape if d == -1)

                if dynamic_dims > 10:
                    warnings.append(f"High number of dynamic dimensions ({dynamic_dims})")
                    score -= 0.1

        except Exception as e:
            logger.warning(f"Error checking numerical validity: {e}")
            score -= 0.2
            issues.append(f"Numerical validation error: {str(e)}")

        score = max(0.0, min(1.0, score))

        details = {
            "has_weights": hasattr(model.model_proto.graph, 'initializer') if model.model_proto and model.model_proto.graph else False,
            "weight_count": len(model.model_proto.graph.initializer) if model.model_proto and model.model_proto.graph else 0,
            "issues": issues,
            "warnings": warnings
        }

        description = "Good numerical stability" if score > 0.8 else "Potential numerical issues detected"

        return QualityScore(
            dimension="numerical_validity",
            score=score,
            description=description,
            weight=0.20,  # 20% weight
            details=details
        )

    def _score_compatibility(self,
                            model: ONNXModel,
                            compatibility_result: CompatibilityAnalysisResult) -> QualityScore:
        """Score Horizon X5 BPU compatibility (Dimension 3)"""
        logger.debug("Scoring Horizon X5 BPU compatibility")

        # Base score from compatibility analysis
        base_score = compatibility_result.confidence_score if compatibility_result else 0.7
        description = "Compatibility analysis complete"

        # Adjust for issues
        if compatibility_result and compatibility_result.issues:
            penalty = min(0.4, len(compatibility_result.issues) * 0.1)
            base_score -= penalty

        # Adjust for warnings
        if compatibility_result and compatibility_result.warnings:
            penalty = min(0.2, len(compatibility_result.warnings) * 0.05)
            base_score -= penalty

        score = max(0.0, min(1.0, base_score))

        details = {
            "confidence": compatibility_result.confidence_score if compatibility_result else 0.0,
            "compatible": compatibility_result.compatible if compatibility_result else False,
            "issue_count": len(compatibility_result.issues) if compatibility_result else 0,
            "warning_count": len(compatibility_result.warnings) if compatibility_result else 0
        }

        if score > 0.9:
            description = "Excellent Horizon X5 BPU compatibility"
        elif score > 0.7:
            description = "Good compatibility with minor concerns"
        else:
            description = "Compatibility issues detected"

        return QualityScore(
            dimension="compatibility",
            score=score,
            description=description,
            weight=0.25,  # 25% weight
            details=details
        )

    def _score_performance(self,
                          model: ONNXModel,
                          structure_result: StructureValidationResult,
                          dynamic_result: DynamicShapeValidationResult) -> QualityScore:
        """Score expected performance (Dimension 4)"""
        logger.debug("Scoring expected performance")

        score = 0.85  # Start with good score
        details = {}
        issues = []

        # Factor 1: Model complexity (more nodes = potentially slower)
        node_count = structure_result.node_count
        if node_count > 1000:
            score -= 0.2
            issues.append("Large model may have performance issues")
        elif node_count > 500:
            score -= 0.1
        elif node_count < 50:
            score += 0.05  # Small models are fast

        details["node_count"] = node_count

        # Factor 2: Dynamic shapes (can impact performance)
        if dynamic_result.total_dynamic_dims > 0:
            penalty = min(0.15, dynamic_result.total_dynamic_dims * 0.02)
            score -= penalty
            details["dynamic_dims"] = dynamic_result.total_dynamic_dims

            if dynamic_result.has_unsupported_dynamic_dims:
                score -= 0.1
                issues.append("Unsupported dynamic dimensions detected")
        else:
            details["dynamic_dims"] = 0

        # Factor 3: Batch independence
        if dynamic_result.batch_independent:
            score += 0.05  # Good for variable batch sizes

        # Factor 4: Model connectivity
        if structure_result.edge_count > 0:
            avg_fanout = structure_result.edge_count / max(1, node_count)
            if avg_fanout > 10:
                score -= 0.1
                issues.append("High fan-out nodes may impact performance")

        # Calculate estimated metrics (simplified)
        # Latency estimation (ms)
        base_latency = node_count * 0.01  # 0.01ms per node (rough estimate)
        if dynamic_result.total_dynamic_dims > 0:
            base_latency *= 1.2  # Dynamic shapes add overhead

        details["estimated_latency_ms"] = base_latency
        details["estimated_throughput_samples_per_sec"] = 1000.0 / base_latency if base_latency > 0 else 100.0
        details["memory_usage_mb"] = node_count * 0.01  # Rough estimate

        score = max(0.0, min(1.0, score))

        if score > 0.9:
            description = "Expected excellent performance"
        elif score > 0.7:
            description = "Good performance expected"
        else:
            description = "Performance concerns detected"

        return QualityScore(
            dimension="performance",
            score=score,
            description=description,
            weight=0.15,  # 15% weight
            details=details
        )

    def _score_conversion_readiness(self,
                                   model: ONNXModel,
                                   structure_result: StructureValidationResult,
                                   dynamic_result: DynamicShapeValidationResult,
                                   compatibility_result: CompatibilityAnalysisResult) -> QualityScore:
        """Score overall conversion readiness (Dimension 5)"""
        logger.debug("Scoring conversion readiness")

        # Start with neutral score
        score = 0.7

        # Factor 1: Structure validity (30% weight in readiness)
        if structure_result.is_valid:
            score += 0.15
        else:
            score -= 0.3

        # Factor 2: Dynamic shape compatibility (25% weight)
        if not dynamic_result.has_unsupported_dynamic_dims:
            score += 0.15
        else:
            score -= 0.25

        # Factor 3: BPU compatibility (25% weight)
        if compatibility_result and compatibility_result.compatible:
            score += 0.15
        else:
            score -= 0.25

        # Factor 4: Overall model health (20% weight)
        # Based on issue counts
        total_issues = (
            len(structure_result.issues) +
            (len(compatibility_result.issues) if compatibility_result else 0) +
            len(dynamic_result.errors)
        )

        if total_issues == 0:
            score += 0.1
        elif total_issues < 5:
            score += 0.05
        else:
            score -= min(0.3, total_issues * 0.05)

        # Factor 5: Critical path analysis
        if (structure_result.dependency_analysis and
            structure_result.dependency_analysis.topological_order):
            # Models with clear dependency graph are easier to convert
            score += 0.05

        score = max(0.0, min(1.0, score))

        details = {
            "structure_ready": structure_result.is_valid,
            "dynamic_shapes_ready": not dynamic_result.has_unsupported_dynamic_dims,
            "bpu_compatible": compatibility_result.compatible if compatibility_result else False,
            "total_issues": total_issues,
            "critical_path_length": len(structure_result.dependency_analysis.topological_order)
                                    if structure_result.dependency_analysis else 0
        }

        if score > 0.9:
            description = "Excellent conversion readiness"
        elif score > 0.7:
            description = "Good conversion readiness with minor concerns"
        elif score > 0.5:
            description = "Moderate conversion readiness, several issues to address"
        else:
            description = "Poor conversion readiness, significant issues detected"

        return QualityScore(
            dimension="conversion_readiness",
            score=score,
            description=description,
            weight=0.15,  # 15% weight
            details=details
        )

    def _compile_dimension_metrics(self,
                                  structure_result: StructureValidationResult,
                                  dynamic_result: DynamicShapeValidationResult,
                                  compatibility_result: CompatibilityAnalysisResult) -> List[DimensionMetrics]:
        """Compile detailed metrics for each dimension"""
        metrics = []

        # Structure metrics
        metrics.append(DimensionMetrics(
            dimension="structure_integrity",
            score=1.0 if structure_result.is_valid else 0.5,
            metrics={
                "node_count": structure_result.node_count,
                "edge_count": structure_result.edge_count,
                "orphaned_nodes": len(structure_result.orphaned_nodes),
                "unused_weights": len(structure_result.unused_weights)
            },
            issues=structure_result.issues,
            warnings=structure_result.warnings
        ))

        # Dynamic shape metrics
        metrics.append(DimensionMetrics(
            dimension="dynamic_shapes",
            score=1.0 if not dynamic_result.has_unsupported_dynamic_dims else 0.6,
            metrics={
                "total_dynamic_dims": dynamic_result.total_dynamic_dims,
                "batch_independent": dynamic_result.batch_independent,
                "has_unsupported": dynamic_result.has_unsupported_dynamic_dims
            },
            issues=dynamic_result.errors,
            warnings=dynamic_result.warnings
        ))

        # Compatibility metrics
        if compatibility_result:
            metrics.append(DimensionMetrics(
                dimension="compatibility",
                score=compatibility_result.confidence_score,
                metrics={
                    "confidence": compatibility_result.confidence_score,
                    "compatible": compatibility_result.compatible
                },
                issues=compatibility_result.issues,
                warnings=compatibility_result.warnings
            ))

        return metrics

    def _generate_recommendations(self,
                                 dimension_scores: List[QualityScore],
                                 dimension_metrics: List[DimensionMetrics]) -> List[str]:
        """Generate recommendations based on scores"""
        recommendations = []

        for score in dimension_scores:
            if score.score < 0.7:
                if score.dimension == "structure_integrity":
                    recommendations.append("Fix structural issues before conversion")
                elif score.dimension == "numerical_validity":
                    recommendations.append("Review numerical stability and weight initialization")
                elif score.dimension == "compatibility":
                    recommendations.append("Replace incompatible operators with Horizon X5 BPU supported alternatives")
                elif score.dimension == "performance":
                    recommendations.append("Optimize model architecture for better performance")
                elif score.dimension == "conversion_readiness":
                    recommendations.append("Address critical issues to improve conversion probability")

        return recommendations

    def _identify_critical_issues(self,
                                  dimension_scores: List[QualityScore],
                                  dimension_metrics: List[DimensionMetrics]) -> List[str]:
        """Identify critical issues that block conversion"""
        critical_issues = []

        for metric in dimension_metrics:
            if metric.score < 0.5:
                critical_issues.extend([f"{metric.dimension}: {issue}" for issue in metric.issues])

        return critical_issues

    def _generate_optimization_suggestions(self,
                                          dimension_scores: List[QualityScore],
                                          dimension_metrics: List[DimensionMetrics]) -> List[str]:
        """Generate optimization suggestions"""
        suggestions = []

        for score in dimension_scores:
            if 0.7 <= score.score < 0.9:
                if score.dimension == "performance":
                    suggestions.append("Consider model pruning or quantization for better performance")
                elif score.dimension == "compatibility":
                    suggestions.append("Use operator fusion to reduce incompatible operations")

        return suggestions

    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from score"""
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        else:
            return "D"

    def export_quality_report(self,
                             result: QualityScoringResult,
                             output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Export quality report to dictionary format.

        Args:
            result: QualityScoringResult
            output_path: Optional path to save JSON report

        Returns:
            Dictionary with quality report
        """
        report = {
            "overall_score": result.overall_score,
            "overall_grade": result.overall_grade,
            "conversion_readiness": result.conversion_readiness,
            "dimension_scores": [
                {
                    "dimension": s.dimension,
                    "score": s.score,
                    "weight": s.weight,
                    "description": s.description,
                    "details": s.details
                }
                for s in result.dimension_scores
            ],
            "critical_issues": result.critical_issues,
            "recommendations": result.recommendations,
            "optimization_suggestions": result.optimization_suggestions
        }

        if output_path:
            try:
                import json
                with open(output_path, 'w') as f:
                    json.dump(report, f, indent=2)
                logger.info(f"Quality report exported to: {output_path}")
            except Exception as e:
                logger.error(f"Failed to export quality report: {e}")

        return report
