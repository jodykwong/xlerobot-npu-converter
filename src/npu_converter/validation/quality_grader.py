"""
Model Quality Grading and Alerting System (AC6)

Provides comprehensive model quality grading, conversion risk assessment,
and predictive analytics based on historical data.

This module implements AC6's model quality grading and alerting system.
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import statistics

# Note: ComprehensiveVerificationResult and related classes are expected to be passed in
# or can be imported at runtime when needed to avoid circular dependencies

logger = logging.getLogger(__name__)


class QualityGrade(Enum):
    """Model quality grades"""
    A_PLUS = "A+"  # 95-100: Excellent
    A = "A"        # 90-95: Very Good
    B_PLUS = "B+"  # 85-90: Good
    B = "B"        # 80-85: Above Average
    C_PLUS = "C+"  # 75-80: Average
    C = "C"        # 70-75: Below Average
    D = "D"        # 60-70: Poor
    F = "F"        # <60: Not Recommended


class RiskLevel(Enum):
    """Conversion risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class QualityMetrics:
    """Quality metrics for grading"""
    overall_score: float
    structure_score: float
    compatibility_score: float
    optimization_score: float
    health_score: float
    dimension_scores: Dict[str, float] = field(default_factory=dict)


@dataclass
class GradeFactors:
    """Factors contributing to quality grade"""
    strengths: List[str]
    weaknesses: List[str]
    critical_issues: List[str]
    improvement_areas: List[str]
    confidence_level: str


@dataclass
class RiskAssessment:
    """Risk assessment for model conversion"""
    risk_level: RiskLevel
    risk_score: float  # 0.0 - 1.0
    risk_factors: List[str]
    mitigation_strategies: List[str]
    estimated_success_probability: float
    failure_modes: List[str] = field(default_factory=list)


@dataclass
class PredictiveAnalysis:
    """Predictive analysis based on historical data"""
    predicted_success_rate: float
    expected_conversion_time: str
    expected_issues: List[str]
    recommendation_confidence: float
    historical_comparisons: List[Dict[str, Any]] = field(default_factory=list)
    trend_analysis: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityAlert:
    """Quality alert for model issues"""
    severity: AlertSeverity
    title: str
    description: str
    impact: str
    recommendation: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    resolved: bool = False


@dataclass
class QualityTrend:
    """Quality trend analysis"""
    trend_direction: str  # "improving", "declining", "stable"
    trend_strength: float
    period_analyzed: str
    key_changes: List[str]
    predictions: Dict[str, float]


@dataclass
class ModelQualityGrade:
    """Complete model quality grade result"""
    model_name: str
    grade: QualityGrade
    quality_metrics: QualityMetrics
    grade_factors: GradeFactors
    risk_assessment: RiskAssessment
    predictive_analysis: PredictiveAnalysis
    alerts: List[QualityAlert]
    quality_trend: Optional[QualityTrend] = None
    historical_context: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class QualityGrader:
    """
    Model Quality Grading and Alerting System (AC6)

    Provides:
    1. Model quality grading (A+ to F)
    2. Conversion risk assessment
    3. Predictive success rate analysis
    4. Quality trend analysis
    5. Alert generation
    """

    def __init__(self, historical_data_dir: Optional[str] = None):
        """
        Initialize quality grader.

        Args:
            historical_data_dir: Directory for historical quality data
        """
        self.historical_data_dir = Path(historical_data_dir) if historical_data_dir else None
        self.logger = logging.getLogger(__name__)
        self._load_historical_data()

    def _load_historical_data(self):
        """Load historical quality data"""
        self.historical_records = []

        if self.historical_data_dir and self.historical_data_dir.exists():
            try:
                history_file = self.historical_data_dir / "quality_history.json"
                if history_file.exists():
                    with open(history_file, 'r') as f:
                        self.historical_records = json.load(f)
                    self.logger.info(f"Loaded {len(self.historical_records)} historical records")
            except Exception as e:
                self.logger.warning(f"Failed to load historical data: {e}")

        if not self.historical_records:
            self._initialize_default_historical_data()

    def _initialize_default_historical_data(self):
        """Initialize with default historical data"""
        self.historical_records = [
            {
                "model_name": "resnet50_v1",
                "quality_score": 0.92,
                "conversion_success": True,
                "grade": "A",
                "timestamp": "2025-10-01",
                "issues": []
            },
            {
                "model_name": "mobilenet_v2",
                "quality_score": 0.88,
                "conversion_success": True,
                "grade": "B+",
                "timestamp": "2025-10-05",
                "issues": []
            },
            {
                "model_name": "bert_base",
                "quality_score": 0.85,
                "conversion_success": True,
                "grade": "B+",
                "timestamp": "2025-10-10",
                "issues": ["dynamic_shape"]
            }
        ]
        self.logger.info("Initialized with default historical data")

    def grade_model(
        self,
        verification_result,  # Using Any to avoid circular import
        include_trend: bool = True
    ) -> ModelQualityGrade:
        """
        Grade model quality based on verification results.

        Args:
            verification_result: Comprehensive verification results from AC1-AC5
            include_trend: Whether to include trend analysis

        Returns:
            ModelQualityGrade with complete assessment
        """
        self.logger.info(f"Grading model: {verification_result.metadata.model_name}")

        # Extract quality metrics
        metrics = self._extract_quality_metrics(verification_result)

        # Determine grade
        grade = self._determine_quality_grade(metrics)

        # Analyze grade factors
        grade_factors = self._analyze_grade_factors(verification_result, metrics, grade)

        # Assess conversion risk
        risk_assessment = self._assess_conversion_risk(verification_result, metrics)

        # Predictive analysis
        predictive_analysis = self._generate_predictive_analysis(
            verification_result, metrics
        )

        # Generate alerts
        alerts = self._generate_alerts(verification_result, metrics, risk_assessment)

        # Trend analysis
        quality_trend = None
        if include_trend:
            quality_trend = self._analyze_quality_trend(verification_result.metadata.model_name)

        # Compile result
        result = ModelQualityGrade(
            model_name=verification_result.metadata.model_name,
            grade=grade,
            quality_metrics=metrics,
            grade_factors=grade_factors,
            risk_assessment=risk_assessment,
            predictive_analysis=predictive_analysis,
            alerts=alerts,
            quality_trend=quality_trend,
            historical_context=self._get_historical_context(verification_result.metadata.model_name)
        )

        self.logger.info(f"Graded {verification_result.metadata.model_name}: {grade.value} "
                        f"(Risk: {risk_assessment.risk_level.value})")

        return result

    def _extract_quality_metrics(self, result) -> QualityMetrics:
        """Extract quality metrics from verification results"""
        # Extract AC scores
        structure_score = self._extract_structure_score(result.ac1_results)
        compatibility_score = result.ac1_results.compatibility_score
        optimization_score = result.ac2_results.performance_improvement if result.ac2_results.optimization_applied else 0.0
        health_score = result.ac4_results.overall_health

        # Calculate overall score (weighted)
        overall_score = (
            structure_score * 0.25 +
            compatibility_score * 0.25 +
            result.ac3_results.overall_score * 0.25 +
            health_score * 0.15 +
            optimization_score * 0.10
        )

        # Extract dimension scores
        dimension_scores = {}
        for dim_score in result.ac3_results.dimension_scores:
            dimension_scores[dim_score.get("dimension", "unknown")] = dim_score.get("score", 0.0)

        return QualityMetrics(
            overall_score=overall_score,
            structure_score=structure_score,
            compatibility_score=compatibility_score,
            optimization_score=optimization_score,
            health_score=health_score,
            dimension_scores=dimension_scores
        )

    def _extract_structure_score(self, ac1_results) -> float:
        """Extract structure score from AC1 results"""
        score = 1.0

        # Penalize for issues
        score -= len(ac1_results.issues) * 0.1
        score -= len(ac1_results.warnings) * 0.05

        # Penalize for orphaned nodes and unused weights
        score -= len(ac1_results.orphaned_nodes) * 0.05
        score -= len(ac1_results.unused_weights) * 0.03

        # Bonus for validation passed
        if ac1_results.overall_valid:
            score += 0.1

        return max(0.0, min(1.0, score))

    def _determine_quality_grade(self, metrics: QualityMetrics) -> QualityGrade:
        """Determine quality grade from metrics"""
        score = metrics.overall_score

        if score >= 0.95:
            return QualityGrade.A_PLUS
        elif score >= 0.90:
            return QualityGrade.A
        elif score >= 0.85:
            return QualityGrade.B_PLUS
        elif score >= 0.80:
            return QualityGrade.B
        elif score >= 0.75:
            return QualityGrade.C_PLUS
        elif score >= 0.70:
            return QualityGrade.C
        elif score >= 0.60:
            return QualityGrade.D
        else:
            return QualityGrade.F

    def _analyze_grade_factors(
        self,
        result,
        metrics: QualityMetrics,
        grade: QualityGrade
    ) -> GradeFactors:
        """Analyze factors contributing to grade"""
        strengths = []
        weaknesses = []
        critical_issues = []
        improvement_areas = []

        # Analyze strengths
        if metrics.structure_score >= 0.9:
            strengths.append("Excellent model structure")
        if metrics.compatibility_score >= 0.9:
            strengths.append("High compatibility with Horizon X5 BPU")
        if metrics.health_score >= 0.9:
            strengths.append("Model health is excellent")
        if result.ac2_results.optimization_applied:
            strengths.append("Preprocessing optimization applied")

        # Analyze weaknesses
        if metrics.structure_score < 0.7:
            weaknesses.append("Model structure needs improvement")
            improvement_areas.append("Clean up orphaned nodes and unused weights")
        if metrics.compatibility_score < 0.7:
            weaknesses.append("Compatibility issues detected")
            improvement_areas.append("Review operator compatibility")
        if metrics.health_score < 0.7:
            weaknesses.append("Model health concerns")
            improvement_areas.append("Address diagnostic findings")

        # Critical issues from AC4
        if result.ac4_results.critical_issues > 0:
            critical_issues.append(f"{result.ac4_results.critical_issues} critical issues detected")
            improvement_areas.append("Resolve critical issues before conversion")

        # Determine confidence level
        if metrics.overall_score >= 0.85:
            confidence = "High"
        elif metrics.overall_score >= 0.70:
            confidence = "Medium"
        else:
            confidence = "Low"

        return GradeFactors(
            strengths=strengths,
            weaknesses=weaknesses,
            critical_issues=critical_issues,
            improvement_areas=improvement_areas,
            confidence_level=confidence
        )

    def _assess_conversion_risk(
        self,
        result,
        metrics: QualityMetrics
    ) -> RiskAssessment:
        """Assess conversion risk level"""
        risk_score = 0.0
        risk_factors = []
        mitigation_strategies = []
        failure_modes = []

        # Risk from quality score
        if metrics.overall_score < 0.6:
            risk_score += 0.4
            risk_factors.append("Very low quality score")
            mitigation_strategies.append("Major model refactoring required")
        elif metrics.overall_score < 0.8:
            risk_score += 0.2
            risk_factors.append("Below-average quality score")
            mitigation_strategies.append("Address identified issues")

        # Risk from critical issues
        if result.ac4_results.critical_issues > 0:
            risk_score += min(0.3, result.ac4_results.critical_issues * 0.1)
            risk_factors.append(f"{result.ac4_results.critical_issues} critical issues")
            mitigation_strategies.append("Resolve critical issues immediately")
            failure_modes.append("Conversion will fail with critical issues")

        # Risk from compatibility
        if metrics.compatibility_score < 0.7:
            risk_score += 0.25
            risk_factors.append("Low compatibility score")
            mitigation_strategies.append("Review and update incompatible operators")

        # Risk from structure
        if result.ac1_results.orphaned_nodes:
            risk_score += 0.15
            risk_factors.append(f"{len(result.ac1_results.orphaned_nodes)} orphaned nodes")
            mitigation_strategies.append("Remove orphaned nodes")

        # Determine risk level
        risk_score = min(1.0, risk_score)
        if risk_score >= 0.7:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 0.5:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 0.3:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        # Calculate success probability
        success_probability = 1.0 - risk_score

        # Additional failure modes
        if risk_score > 0.5:
            failure_modes.append("May require multiple conversion attempts")

        if not mitigation_strategies:
            mitigation_strategies.append("Model appears ready for conversion")

        return RiskAssessment(
            risk_level=risk_level,
            risk_score=risk_score,
            risk_factors=risk_factors,
            mitigation_strategies=mitigation_strategies,
            estimated_success_probability=success_probability,
            failure_modes=failure_modes
        )

    def _generate_predictive_analysis(
        self,
        result,
        metrics: QualityMetrics
    ) -> PredictiveAnalysis:
        """Generate predictive analysis based on historical data"""
        # Calculate predicted success rate
        historical_success_rate = self._calculate_historical_success_rate()

        # Adjust based on current metrics
        predicted_success = historical_success_rate * metrics.overall_score

        # Estimate conversion time
        if metrics.overall_score >= 0.9:
            conversion_time = "15-30 minutes"
        elif metrics.overall_score >= 0.8:
            conversion_time = "30-60 minutes"
        elif metrics.overall_score >= 0.7:
            conversion_time = "1-2 hours"
        else:
            conversion_time = "2-4 hours"

        # Expected issues based on analysis
        expected_issues = []
        if result.ac4_results.total_issues > 0:
            expected_issues.append(f"{result.ac4_results.total_issues} issues to resolve")
        if result.ac1_results.orphaned_nodes:
            expected_issues.append("Clean up orphaned nodes")
        if metrics.compatibility_score < 0.8:
            expected_issues.append("Address compatibility issues")

        # Recommendation confidence
        if metrics.overall_score >= 0.8:
            confidence = 0.9
        elif metrics.overall_score >= 0.6:
            confidence = 0.7
        else:
            confidence = 0.5

        return PredictiveAnalysis(
            predicted_success_rate=predicted_success,
            expected_conversion_time=conversion_time,
            expected_issues=expected_issues,
            recommendation_confidence=confidence,
            historical_comparisons=self._get_historical_comparisons(result.metadata.model_name),
            trend_analysis=self._get_trend_analysis()
        )

    def _calculate_historical_success_rate(self) -> float:
        """Calculate historical success rate from records"""
        if not self.historical_records:
            return 0.85  # Default

        successful = sum(1 for record in self.historical_records if record.get("conversion_success", False))
        return successful / len(self.historical_records)

    def _get_historical_comparisons(self, model_name: str) -> List[Dict[str, Any]]:
        """Get historical comparisons for model"""
        # Find similar models
        comparisons = []
        for record in self.historical_records[-5:]:  # Last 5 records
            comparisons.append({
                "model": record["model_name"],
                "score": record["quality_score"],
                "grade": record["grade"],
                "success": record["conversion_success"]
            })
        return comparisons

    def _get_trend_analysis(self) -> Dict[str, Any]:
        """Get overall trend analysis"""
        if len(self.historical_records) < 2:
            return {"trend": "insufficient_data"}

        scores = [record["quality_score"] for record in self.historical_records[-10:]]
        recent_avg = statistics.mean(scores[-3:]) if len(scores) >= 3 else scores[-1]
        older_avg = statistics.mean(scores[:3]) if len(scores) >= 6 else scores[0]

        if recent_avg > older_avg + 0.05:
            trend = "improving"
        elif recent_avg < older_avg - 0.05:
            trend = "declining"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "recent_average": recent_avg,
            "overall_average": statistics.mean(scores),
            "samples_analyzed": len(scores)
        }

    def _generate_alerts(
        self,
        result,
        metrics: QualityMetrics,
        risk_assessment: RiskAssessment
    ) -> List[QualityAlert]:
        """Generate quality alerts"""
        alerts = []

        # Critical alerts
        if risk_assessment.risk_level == RiskLevel.CRITICAL:
            alerts.append(QualityAlert(
                severity=AlertSeverity.CRITICAL,
                title="Critical Conversion Risk",
                description="Model has critical issues that must be resolved",
                impact="Conversion will likely fail",
                recommendation="Address all critical issues before proceeding"
            ))

        # High risk alert
        if risk_assessment.risk_level == RiskLevel.HIGH:
            alerts.append(QualityAlert(
                severity=AlertSeverity.ERROR,
                title="High Conversion Risk",
                description="Significant issues detected",
                impact="Conversion may encounter problems",
                recommendation="Review and address identified issues"
            ))

        # Quality alerts
        if metrics.overall_score < 0.6:
            alerts.append(QualityAlert(
                severity=AlertSeverity.ERROR,
                title="Low Quality Score",
                description="Model quality is below recommended threshold",
                impact="May not convert successfully",
                recommendation="Consider model optimization or refactoring"
            ))

        # Compatibility alert
        if metrics.compatibility_score < 0.7:
            alerts.append(QualityAlert(
                severity=AlertSeverity.WARNING,
                title="Compatibility Issues",
                description="Some operators may not be supported",
                impact="May require operator substitution",
                recommendation="Check operator compatibility matrix"
            ))

        # Optimization alerts
        if not result.ac2_results.optimization_applied:
            alerts.append(QualityAlert(
                severity=AlertSeverity.INFO,
                title="Optimization Opportunity",
                description="Preprocessing optimization not applied",
                impact="May miss performance improvements",
                recommendation="Consider applying intelligent preprocessing optimization"
            ))

        return alerts

    def _analyze_quality_trend(self, model_name: str) -> Optional[QualityTrend]:
        """Analyze quality trend for model"""
        # Find historical records for this model
        model_records = [r for r in self.historical_records if r["model_name"] == model_name]

        if len(model_records) < 2:
            return None

        # Analyze trend
        scores = [r["quality_score"] for r in model_records]
        recent_scores = scores[-3:]
        older_scores = scores[:-3] if len(scores) > 3 else scores[:1]

        if len(recent_scores) > 0 and len(older_scores) > 0:
            recent_avg = statistics.mean(recent_scores)
            older_avg = statistics.mean(older_scores)

            if recent_avg > older_avg + 0.03:
                direction = "improving"
                strength = min(1.0, (recent_avg - older_avg) / 0.1)
            elif recent_avg < older_avg - 0.03:
                direction = "declining"
                strength = min(1.0, (older_avg - recent_avg) / 0.1)
            else:
                direction = "stable"
                strength = 0.5

            key_changes = []
            if direction == "improving":
                key_changes.append("Quality scores trending upward")
            elif direction == "declining":
                key_changes.append("Quality scores trending downward")

            predictions = {
                "next_score": recent_avg + (0.02 if direction == "improving" else -0.02 if direction == "declining" else 0),
                "trend_continuation_probability": strength
            }

            return QualityTrend(
                trend_direction=direction,
                trend_strength=strength,
                period_analyzed=f"{len(model_records)} evaluations",
                key_changes=key_changes,
                predictions=predictions
            )

        return None

    def _get_historical_context(self, model_name: str) -> Dict[str, Any]:
        """Get historical context for model"""
        model_records = [r for r in self.historical_records if r["model_name"] == model_name]

        if not model_records:
            return {"status": "first_evaluation"}

        return {
            "previous_evaluations": len(model_records),
            "best_score": max(r["quality_score"] for r in model_records),
            "average_score": statistics.mean(r["quality_score"] for r in model_records),
            "last_evaluation": model_records[-1]["timestamp"],
            "conversion_history": {
                "attempted": any("conversion_success" in r for r in model_records),
                "successful": any(r.get("conversion_success", False) for r in model_records)
            }
        }

    def save_grade_result(self, grade_result: ModelQualityGrade, output_dir: str):
        """
        Save grade result to file.

        Args:
            grade_result: Grade result to save
            output_dir: Output directory
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        filename = f"{grade_result.model_name}_quality_grade_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = output_path / filename

        # Convert to dict
        result_dict = {
            "model_name": grade_result.model_name,
            "grade": grade_result.grade.value,
            "quality_metrics": asdict(grade_result.quality_metrics),
            "grade_factors": asdict(grade_result.grade_factors),
            "risk_assessment": {
                **asdict(grade_result.risk_assessment),
                "risk_level": grade_result.risk_assessment.risk_level.value
            },
            "predictive_analysis": asdict(grade_result.predictive_analysis),
            "alerts": [asdict(alert) for alert in grade_result.alerts],
            "quality_trend": asdict(grade_result.quality_trend) if grade_result.quality_trend else None,
            "historical_context": grade_result.historical_context,
            "timestamp": grade_result.timestamp
        }

        # Save to file
        with open(filepath, 'w') as f:
            json.dump(result_dict, f, indent=2, default=str)

        self.logger.info(f"Quality grade saved to: {filepath}")

        # Update historical records
        self._update_historical_records(grade_result)

    def _update_historical_records(self, grade_result: ModelQualityGrade):
        """Update historical records with new grade"""
        record = {
            "model_name": grade_result.model_name,
            "quality_score": grade_result.quality_metrics.overall_score,
            "grade": grade_result.grade.value,
            "conversion_success": None,  # Will be updated after conversion
            "timestamp": grade_result.timestamp,
            "issues": [issue.description for issue in grade_result.alerts]
        }

        self.historical_records.append(record)

        # Keep only last 100 records
        self.historical_records = self.historical_records[-100:]

        # Save to file
        if self.historical_data_dir:
            try:
                history_file = self.historical_data_dir / "quality_history.json"
                with open(history_file, 'w') as f:
                    json.dump(self.historical_records, f, indent=2)
            except Exception as e:
                self.logger.error(f"Failed to save historical records: {e}")

    def get_risk_summary(self, grade_results: List[ModelQualityGrade]) -> Dict[str, Any]:
        """
        Get risk summary across multiple models.

        Args:
            grade_results: List of grade results

        Returns:
            Risk summary dictionary
        """
        if not grade_results:
            return {"error": "No grade results provided"}

        risk_distribution = {
            RiskLevel.CRITICAL: 0,
            RiskLevel.HIGH: 0,
            RiskLevel.MEDIUM: 0,
            RiskLevel.LOW: 0
        }

        grade_distribution = {}
        total_alerts = 0
        critical_alerts = 0

        for result in grade_results:
            # Count risk levels
            risk_distribution[result.risk_assessment.risk_level] += 1

            # Count grades
            grade = result.grade.value
            grade_distribution[grade] = grade_distribution.get(grade, 0) + 1

            # Count alerts
            total_alerts += len(result.alerts)
            critical_alerts += sum(1 for alert in result.alerts if alert.severity == AlertSeverity.CRITICAL)

        # Calculate averages
        avg_quality = statistics.mean(r.quality_metrics.overall_score for r in grade_results)
        avg_risk = statistics.mean(r.risk_assessment.risk_score for r in grade_results)

        return {
            "total_models": len(grade_results),
            "risk_distribution": {k.value: v for k, v in risk_distribution.items()},
            "grade_distribution": grade_distribution,
            "average_quality_score": avg_quality,
            "average_risk_score": avg_risk,
            "total_alerts": total_alerts,
            "critical_alerts": critical_alerts,
            "high_risk_models": len([r for r in grade_results if r.risk_assessment.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]),
            "recommendation": "Review high and critical risk models before conversion" if risk_distribution[RiskLevel.HIGH] + risk_distribution[RiskLevel.CRITICAL] > 0 else "All models ready for conversion"
        }
