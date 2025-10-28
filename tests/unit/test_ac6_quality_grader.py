"""
Unit tests for AC6: Model Quality Grading and Alerting System

Tests the quality grading system that provides:
- Model quality grading (A+ to F)
- Conversion risk assessment
- Predictive success rate analysis
- Quality trend analysis
- Alert generation
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock

# Import using importlib to avoid onnx dependency issues
import sys
import os
import importlib.util

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

# Load quality_grader module directly
spec = importlib.util.spec_from_file_location(
    "quality_grader",
    os.path.join(os.path.dirname(__file__), '../../src/npu_converter/validation/quality_grader.py')
)
quality_grader_module = importlib.util.module_from_spec(spec)
sys.modules["quality_grader"] = quality_grader_module
spec.loader.exec_module(quality_grader_module)

# Import classes
QualityGrader = quality_grader_module.QualityGrader
ModelQualityGrade = quality_grader_module.ModelQualityGrade
QualityGrade = quality_grader_module.QualityGrade
RiskLevel = quality_grader_module.RiskLevel
QualityMetrics = quality_grader_module.QualityMetrics
RiskAssessment = quality_grader_module.RiskAssessment
AlertSeverity = quality_grader_module.AlertSeverity

# Load comprehensive_verification_reporter
spec2 = importlib.util.spec_from_file_location(
    "comprehensive_verification_reporter",
    os.path.join(os.path.dirname(__file__), '../../src/npu_converter/validation/comprehensive_verification_reporter.py')
)
cvreporter_module = importlib.util.module_from_spec(spec2)
sys.modules["comprehensive_verification_reporter"] = cvreporter_module
spec2.loader.exec_module(cvreporter_module)

ComprehensiveVerificationResult = cvreporter_module.ComprehensiveVerificationResult
AC1Results = cvreporter_module.AC1Results
AC2Results = cvreporter_module.AC2Results
AC3Results = cvreporter_module.AC3Results
AC4Results = cvreporter_module.AC4Results
ReportStatus = cvreporter_module.ReportStatus


class TestAC6QualityGrader(unittest.TestCase):
    """Test cases for AC6 Model Quality Grading and Alerting"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.grader = QualityGrader(historical_data_dir=self.test_dir)

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_grader_initialization(self):
        """Test QualityGrader initialization"""
        self.assertIsInstance(self.grader, QualityGrader)
        self.assertIsNotNone(self.grader.historical_records)
        self.assertGreater(len(self.grader.historical_records), 0)

    def test_quality_metrics_extraction(self):
        """Test quality metrics extraction"""
        # Create mock verification result
        result = self._create_mock_verification_result()

        metrics = self.grader._extract_quality_metrics(result)

        self.assertIsInstance(metrics, QualityMetrics)
        self.assertGreaterEqual(metrics.overall_score, 0.0)
        self.assertLessEqual(metrics.overall_score, 1.0)
        self.assertGreaterEqual(metrics.structure_score, 0.0)
        self.assertLessEqual(metrics.structure_score, 1.0)

    def test_quality_grade_determination(self):
        """Test quality grade determination"""
        # Test A+ grade
        metrics = QualityMetrics(
            overall_score=0.97,
            structure_score=0.95,
            compatibility_score=0.98,
            optimization_score=0.90,
            health_score=0.95
        )
        grade = self.grader._determine_quality_grade(metrics)
        self.assertEqual(grade, QualityGrade.A_PLUS)

        # Test A grade
        metrics.overall_score = 0.92
        grade = self.grader._determine_quality_grade(metrics)
        self.assertEqual(grade, QualityGrade.A)

        # Test B grade
        metrics.overall_score = 0.82
        grade = self.grader._determine_quality_grade(metrics)
        self.assertEqual(grade, QualityGrade.B)

        # Test C grade
        metrics.overall_score = 0.72
        grade = self.grader._determine_quality_grade(metrics)
        self.assertEqual(grade, QualityGrade.C)

        # Test D grade
        metrics.overall_score = 0.65
        grade = self.grader._determine_quality_grade(metrics)
        self.assertEqual(grade, QualityGrade.D)

        # Test F grade
        metrics.overall_score = 0.55
        grade = self.grader._determine_quality_grade(metrics)
        self.assertEqual(grade, QualityGrade.F)

    def test_grade_factors_analysis(self):
        """Test grade factors analysis"""
        # Create mock results with good metrics
        result = self._create_mock_verification_result(good_metrics=True)
        metrics = QualityMetrics(
            overall_score=0.92,
            structure_score=0.95,
            compatibility_score=0.90,
            optimization_score=0.85,
            health_score=0.95
        )

        grade_factors = self.grader._analyze_grade_factors(result, metrics, QualityGrade.A)

        self.assertIsInstance(grade_factors.strengths, list)
        self.assertIsInstance(grade_factors.weaknesses, list)
        self.assertIsInstance(grade_factors.improvement_areas, list)
        self.assertEqual(grade_factors.confidence_level, "High")

    def test_conversion_risk_assessment(self):
        """Test conversion risk assessment"""
        # Create high-quality model (low risk)
        result = self._create_mock_verification_result(good_metrics=True)
        metrics = QualityMetrics(
            overall_score=0.92,
            structure_score=0.95,
            compatibility_score=0.90,
            optimization_score=0.85,
            health_score=0.95
        )

        risk = self.grader._assess_conversion_risk(result, metrics)

        self.assertIsInstance(risk, RiskAssessment)
        self.assertIn(risk.risk_level, [RiskLevel.LOW, RiskLevel.MEDIUM])
        self.assertGreaterEqual(risk.estimated_success_probability, 0.7)

        # Create low-quality model (high risk)
        result = self._create_mock_verification_result(poor_metrics=True)
        metrics.overall_score = 0.55

        risk = self.grader._assess_conversion_risk(result, metrics)

        self.assertIn(risk.risk_level, [RiskLevel.HIGH, RiskLevel.CRITICAL])
        self.assertLess(risk.estimated_success_probability, 0.6)

    def test_predictive_analysis(self):
        """Test predictive analysis generation"""
        result = self._create_mock_verification_result()
        metrics = QualityMetrics(
            overall_score=0.85,
            structure_score=0.80,
            compatibility_score=0.90,
            optimization_score=0.75,
            health_score=0.85
        )

        prediction = self.grader._generate_predictive_analysis(result, metrics)

        self.assertGreaterEqual(prediction.predicted_success_rate, 0.0)
        self.assertLessEqual(prediction.predicted_success_rate, 1.0)
        self.assertIsInstance(prediction.expected_conversion_time, str)
        self.assertGreaterEqual(prediction.recommendation_confidence, 0.0)
        self.assertLessEqual(prediction.recommendation_confidence, 1.0)

    def test_alert_generation(self):
        """Test quality alert generation"""
        # Test with high-risk model
        result = self._create_mock_verification_result(poor_metrics=True)
        metrics = QualityMetrics(
            overall_score=0.55,
            structure_score=0.50,
            compatibility_score=0.60,
            optimization_score=0.40,
            health_score=0.50
        )
        risk = RiskAssessment(
            risk_level=RiskLevel.CRITICAL,
            risk_score=0.8,
            risk_factors=["Critical issues"],
            mitigation_strategies=["Fix issues"],
            estimated_success_probability=0.3
        )

        alerts = self.grader._generate_alerts(result, metrics, risk)

        self.assertIsInstance(alerts, list)
        self.assertGreater(len(alerts), 0)

        # Should have critical alert
        critical_alerts = [a for a in alerts if a.severity == AlertSeverity.CRITICAL]
        self.assertGreater(len(critical_alerts), 0)

    def test_historical_success_rate_calculation(self):
        """Test historical success rate calculation"""
        success_rate = self.grader._calculate_historical_success_rate()
        self.assertGreaterEqual(success_rate, 0.0)
        self.assertLessEqual(success_rate, 1.0)

    def test_full_model_grading(self):
        """Test complete model grading workflow"""
        result = self._create_mock_verification_result(good_metrics=True)

        grade_result = self.grader.grade_model(result)

        self.assertIsInstance(grade_result, ModelQualityGrade)
        self.assertEqual(grade_result.model_name, "test_model")
        self.assertIn(grade_result.grade, list(QualityGrade))
        self.assertIsInstance(grade_result.quality_metrics, QualityMetrics)
        self.assertIsInstance(grade_result.risk_assessment, RiskAssessment)
        self.assertIsInstance(grade_result.predictive_analysis, object)
        self.assertIsInstance(grade_result.alerts, list)

    def test_risk_summary_multiple_models(self):
        """Test risk summary for multiple models"""
        # Create multiple grade results
        results = []
        for i in range(5):
            result = self._create_mock_verification_result(model_suffix=f"model_{i}")
            grade_result = self.grader.grade_model(result)
            results.append(grade_result)

        summary = self.grader.get_risk_summary(results)

        self.assertIn("total_models", summary)
        self.assertIn("risk_distribution", summary)
        self.assertIn("grade_distribution", summary)
        self.assertEqual(summary["total_models"], 5)
        self.assertIsInstance(summary["risk_distribution"], dict)

    def test_grade_save_and_historical_update(self):
        """Test saving grade result and updating historical records"""
        result = self._create_mock_verification_result()
        grade_result = self.grader.grade_model(result)

        # Save grade result
        self.grader.save_grade_result(grade_result, self.test_dir)

        # Check file was created
        output_files = list(Path(self.test_dir).glob("*.json"))
        # Filter out history file
        grade_files = [f for f in output_files if f.name != "quality_history.json"]
        self.assertGreater(len(grade_files), 0)

        # Check historical records were updated
        self.assertGreater(len(self.grader.historical_records), 0)
        # Should have the new record
        new_record = self.grader.historical_records[-1]
        self.assertEqual(new_record["model_name"], "test_model")

    def test_quality_trend_analysis(self):
        """Test quality trend analysis"""
        # Add some historical data for the same model
        for i in range(3):
            self.grader.historical_records.append({
                "model_name": "test_model",
                "quality_score": 0.7 + i * 0.05,
                "grade": "B",
                "conversion_success": True,
                "timestamp": f"2025-10-{20+i}"
            })

        trend = self.grader._analyze_quality_trend("test_model")

        self.assertIsNotNone(trend)
        self.assertIn(trend.trend_direction, ["improving", "stable", "declining"])
        self.assertGreaterEqual(trend.trend_strength, 0.0)
        self.assertLessEqual(trend.trend_strength, 1.0)
        self.assertIsInstance(trend.predictions, dict)

    def test_historical_context(self):
        """Test historical context retrieval"""
        # First evaluation
        context = self.grader._get_historical_context("new_model")
        self.assertEqual(context["status"], "first_evaluation")

        # Add historical data
        self.grader.historical_records.append({
            "model_name": "existing_model",
            "quality_score": 0.85,
            "grade": "B+",
            "conversion_success": True,
            "timestamp": "2025-10-20"
        })

        context = self.grader._get_historical_context("existing_model")
        self.assertEqual(context["previous_evaluations"], 1)
        self.assertIn("best_score", context)
        self.assertIn("average_score", context)

    def test_edge_case_very_low_score(self):
        """Test edge case with very low quality score"""
        result = self._create_mock_verification_result(very_poor_metrics=True)
        metrics = QualityMetrics(
            overall_score=0.30,
            structure_score=0.20,
            compatibility_score=0.25,
            optimization_score=0.15,
            health_score=0.20
        )

        grade = self.grader._determine_quality_grade(metrics)
        risk = self.grader._assess_conversion_risk(result, metrics)

        self.assertEqual(grade, QualityGrade.F)
        self.assertIn(risk.risk_level, [RiskLevel.HIGH, RiskLevel.CRITICAL])

    def test_edge_case_perfect_score(self):
        """Test edge case with perfect quality score"""
        metrics = QualityMetrics(
            overall_score=1.0,
            structure_score=1.0,
            compatibility_score=1.0,
            optimization_score=1.0,
            health_score=1.0
        )

        grade = self.grader._determine_quality_grade(metrics)
        self.assertEqual(grade, QualityGrade.A_PLUS)

    def _create_mock_verification_result(
        self,
        good_metrics: bool = False,
        poor_metrics: bool = False,
        very_poor_metrics: bool = False,
        model_suffix: str = ""
    ) -> ComprehensiveVerificationResult:
        """Helper to create mock verification result"""

        if good_metrics:
            ac1_results = AC1Results(
                overall_valid=True,
                structure_valid=True,
                dynamic_shape_valid=True,
                compatibility_valid=True,
                orphaned_nodes=[],
                unused_weights=[],
                dynamic_dimensions={},
                compatibility_score=0.90,
                issues=[],
                warnings=[]
            )
            ac2_results = AC2Results(
                optimization_applied=True,
                strategy_used="bayesian",
                model_type="vision",
                best_config={},
                performance_improvement=0.15,
                before_metrics={},
                after_metrics={},
                recommendations=[]
            )
            ac3_results = AC3Results(
                overall_score=0.88,
                overall_grade="B+",
                conversion_readiness=0.85,
                dimension_scores=[{"dimension": "structure", "score": 0.9}],
                critical_issues=[],
                recommendations=[],
                optimization_suggestions=[]
            )
            ac4_results = AC4Results(
                overall_health=0.92,
                total_issues=1,
                critical_issues=0,
                findings=[],
                root_causes=[],
                recommendations=[]
            )
        elif poor_metrics or very_poor_metrics:
            score = 0.55 if very_poor_metrics else 0.65
            ac1_results = AC1Results(
                overall_valid=True,
                structure_valid=True,
                dynamic_shape_valid=True,
                compatibility_valid=True,
                orphaned_nodes=["node1", "node2"],
                unused_weights=["weight1"],
                dynamic_dimensions={},
                compatibility_score=0.60,
                issues=["Some issues"],
                warnings=["Warnings"]
            )
            ac2_results = AC2Results(
                optimization_applied=False,
                strategy_used="none",
                model_type="unknown",
                best_config={},
                performance_improvement=0.0,
                before_metrics={},
                after_metrics={},
                recommendations=[]
            )
            ac3_results = AC3Results(
                overall_score=score,
                overall_grade="C",
                conversion_readiness=score,
                dimension_scores=[{"dimension": "structure", "score": 0.6}],
                critical_issues=[],
                recommendations=[],
                optimization_suggestions=[]
            )
            ac4_results = AC4Results(
                overall_health=0.60,
                total_issues=3,
                critical_issues=1,
                findings=[{"severity": "critical", "description": "Critical issue"}],
                root_causes=["Root cause"],
                recommendations=[]
            )
        else:
            ac1_results = AC1Results(
                overall_valid=False,
                structure_valid=False,
                dynamic_shape_valid=False,
                compatibility_valid=False,
                orphaned_nodes=[],
                unused_weights=[],
                dynamic_dimensions={},
                compatibility_score=0.5,
                issues=["AC1 validation not performed"],
                warnings=[]
            )
            ac2_results = AC2Results(
                optimization_applied=False,
                strategy_used="none",
                model_type="unknown",
                best_config={},
                performance_improvement=0.0,
                before_metrics={},
                after_metrics={},
                recommendations=[]
            )
            ac3_results = AC3Results(
                overall_score=0.5,
                overall_grade="N/A",
                conversion_readiness=0.5,
                dimension_scores=[],
                critical_issues=["AC3 quality scoring not performed"],
                recommendations=[],
                optimization_suggestions=[]
            )
            ac4_results = AC4Results(
                overall_health=0.5,
                total_issues=0,
                critical_issues=0,
                findings=[],
                root_causes=["AC4 diagnosis not performed"],
                recommendations=[]
            )

        # Create metadata
        metadata = Mock()
        metadata.model_name = f"test_model{model_suffix}"
        metadata.model_path = f"/test/test_model{model_suffix}.onnx"
        metadata.timestamp = "2025-10-28"

        return ComprehensiveVerificationResult(
            metadata=metadata,
            ac1_results=ac1_results,
            ac2_results=ac2_results,
            ac3_results=ac3_results,
            ac4_results=ac4_results,
            overall_status=ReportStatus.SUCCESS,
            executive_summary={},
            integration_analysis={},
            action_items=[],
            next_steps=[]
        )


if __name__ == "__main__":
    unittest.main()
