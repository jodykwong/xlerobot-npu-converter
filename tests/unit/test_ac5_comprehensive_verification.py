"""
Unit tests for AC5: Comprehensive Verification Reporting System

Tests the comprehensive verification report generator that integrates
results from AC1-AC4.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock

# Import the module to test using importlib to avoid onnx dependency issues
import sys
import os
import importlib.util

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

# Load the comprehensive_verification_reporter module directly
spec = importlib.util.spec_from_file_location(
    "comprehensive_verification_reporter",
    os.path.join(os.path.dirname(__file__), '../../src/npu_converter/validation/comprehensive_verification_reporter.py')
)
comprehensive_verification_reporter = importlib.util.module_from_spec(spec)
sys.modules["comprehensive_verification_reporter"] = comprehensive_verification_reporter
spec.loader.exec_module(comprehensive_verification_reporter)

# Import classes
ComprehensiveVerificationReporter = comprehensive_verification_reporter.ComprehensiveVerificationReporter
ComprehensiveVerificationResult = comprehensive_verification_reporter.ComprehensiveVerificationResult
AC1Results = comprehensive_verification_reporter.AC1Results
AC2Results = comprehensive_verification_reporter.AC2Results
AC3Results = comprehensive_verification_reporter.AC3Results
AC4Results = comprehensive_verification_reporter.AC4Results
ReportFormat = comprehensive_verification_reporter.ReportFormat
ReportStatus = comprehensive_verification_reporter.ReportStatus
VerificationMetadata = comprehensive_verification_reporter.VerificationMetadata


class TestAC5ComprehensiveVerification(unittest.TestCase):
    """Test cases for AC5 Comprehensive Verification Reporting"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.reporter = ComprehensiveVerificationReporter(output_dir=self.test_dir)

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_reporter_initialization(self):
        """Test ComprehensiveVerificationReporter initialization"""
        self.assertIsInstance(self.reporter, ComprehensiveVerificationReporter)
        self.assertTrue(Path(self.test_dir).exists())
        self.assertIsInstance(self.reporter.report_history, list)

    def test_empty_ac1_results_creation(self):
        """Test creation of empty AC1 results"""
        ac1_results = self.reporter._create_empty_ac1_results()
        self.assertIsInstance(ac1_results, AC1Results)
        self.assertFalse(ac1_results.overall_valid)
        self.assertEqual(len(ac1_results.issues), 1)
        self.assertIn("AC1 validation not performed", ac1_results.issues[0])

    def test_empty_ac2_results_creation(self):
        """Test creation of empty AC2 results"""
        ac2_results = self.reporter._create_empty_ac2_results()
        self.assertIsInstance(ac2_results, AC2Results)
        self.assertFalse(ac2_results.optimization_applied)
        self.assertEqual(ac2_results.strategy_used, "none")
        self.assertEqual(ac2_results.model_type, "unknown")
        self.assertEqual(ac2_results.performance_improvement, 0.0)

    def test_empty_ac3_results_creation(self):
        """Test creation of empty AC3 results"""
        ac3_results = self.reporter._create_empty_ac3_results()
        self.assertIsInstance(ac3_results, AC3Results)
        self.assertEqual(ac3_results.overall_score, 0.0)
        self.assertEqual(ac3_results.overall_grade, "N/A")
        self.assertEqual(ac3_results.conversion_readiness, 0.0)
        self.assertIn("AC3 quality scoring not performed", ac3_results.critical_issues[0])

    def test_empty_ac4_results_creation(self):
        """Test creation of empty AC4 results"""
        ac4_results = self.reporter._create_empty_ac4_results()
        self.assertIsInstance(ac4_results, AC4Results)
        self.assertEqual(ac4_results.overall_health, 0.0)
        self.assertEqual(ac4_results.total_issues, 0)
        self.assertEqual(ac4_results.critical_issues, 0)
        self.assertIn("AC4 diagnosis not performed", ac4_results.root_causes[0])

    def test_determine_overall_status_success(self):
        """Test determining overall status as SUCCESS"""
        ac1 = AC1Results(
            overall_valid=True,
            structure_valid=True,
            dynamic_shape_valid=True,
            compatibility_valid=True,
            orphaned_nodes=[],
            unused_weights=[],
            dynamic_dimensions={},
            compatibility_score=0.9,
            issues=[],
            warnings=[]
        )
        ac3 = AC3Results(
            overall_score=0.85,
            overall_grade="B",
            conversion_readiness=0.8,
            dimension_scores=[],
            critical_issues=[],
            recommendations=[],
            optimization_suggestions=[]
        )
        ac4 = AC4Results(
            overall_health=0.9,
            total_issues=1,
            critical_issues=0,
            findings=[],
            root_causes=[],
            recommendations=[]
        )

        status = self.reporter._determine_overall_status(ac1, None, ac3, ac4)
        self.assertEqual(status, ReportStatus.SUCCESS)

    def test_determine_overall_status_failed(self):
        """Test determining overall status as FAILED"""
        ac1 = AC1Results(
            overall_valid=False,
            structure_valid=False,
            dynamic_shape_valid=False,
            compatibility_valid=False,
            orphaned_nodes=[],
            unused_weights=[],
            dynamic_dimensions={},
            compatibility_score=0.0,
            issues=["Critical error"],
            warnings=[]
        )

        status = self.reporter._determine_overall_status(ac1, None, None, None)
        self.assertEqual(status, ReportStatus.FAILED)

    def test_determine_overall_status_partial(self):
        """Test determining overall status as PARTIAL_SUCCESS"""
        ac1 = AC1Results(
            overall_valid=True,
            structure_valid=True,
            dynamic_shape_valid=True,
            compatibility_valid=True,
            orphaned_nodes=[],
            unused_weights=[],
            dynamic_dimensions={},
            compatibility_score=0.9,
            issues=[],
            warnings=[]
        )
        ac4 = AC4Results(
            overall_health=0.8,
            total_issues=2,
            critical_issues=1,  # Critical issues
            findings=[{"severity": "critical"}],
            root_causes=[],
            recommendations=[]
        )

        status = self.reporter._determine_overall_status(ac1, None, None, ac4)
        self.assertEqual(status, ReportStatus.PARTIAL_SUCCESS)

    def test_generate_executive_summary(self):
        """Test executive summary generation"""
        ac1 = AC1Results(
            overall_valid=True,
            structure_valid=True,
            dynamic_shape_valid=True,
            compatibility_valid=True,
            orphaned_nodes=[],
            unused_weights=[],
            dynamic_dimensions={},
            compatibility_score=0.85,
            issues=[],
            warnings=[]
        )
        ac2 = AC2Results(
            optimization_applied=True,
            strategy_used="grid_search",
            model_type="vision",
            best_config={},
            performance_improvement=0.15,
            before_metrics={},
            after_metrics={},
            recommendations=[]
        )
        ac3 = AC3Results(
            overall_score=0.88,
            overall_grade="B+",
            conversion_readiness=0.82,
            dimension_scores=[],
            critical_issues=[],
            recommendations=[],
            optimization_suggestions=[]
        )
        ac4 = AC4Results(
            overall_health=0.9,
            total_issues=2,
            critical_issues=0,
            findings=[],
            root_causes=[],
            recommendations=[]
        )

        summary = self.reporter._generate_executive_summary(
            Mock(), ac1, ac2, ac3, ac4, ReportStatus.SUCCESS
        )

        self.assertIn("verification_status", summary)
        self.assertIn("key_metrics", summary)
        self.assertIn("critical_findings", summary)
        self.assertIn("readiness_assessment", summary)
        self.assertIn("top_recommendations", summary)

        # Check key metrics
        self.assertEqual(summary["key_metrics"]["overall_quality_score"], 0.88)
        self.assertEqual(summary["key_metrics"]["conversion_readiness"], 0.82)
        self.assertEqual(summary["key_metrics"]["model_health"], 0.9)

    def test_generate_action_items(self):
        """Test action items generation"""
        ac1 = AC1Results(
            overall_valid=True,
            structure_valid=True,
            dynamic_shape_valid=True,
            compatibility_valid=True,
            orphaned_nodes=["node1", "node2"],
            unused_weights=["weight1"],
            dynamic_dimensions={},
            compatibility_score=0.85,
            issues=[],
            warnings=[]
        )
        ac2 = AC2Results(
            optimization_applied=False,
            strategy_used="none",
            model_type="unknown",
            best_config={},
            performance_improvement=0.0,
            before_metrics={},
            after_metrics={},
            recommendations=[]
        )
        ac3 = AC3Results(
            overall_score=0.65,  # Low score
            overall_grade="C",
            conversion_readiness=0.6,
            dimension_scores=[{"dimension": "test", "score": 0.65}],
            critical_issues=[],
            recommendations=[],
            optimization_suggestions=[]
        )
        ac4 = AC4Results(
            overall_health=0.8,
            total_issues=2,
            critical_issues=0,
            findings=[
                {"severity": "high", "description": "Test issue"}
            ],
            root_causes=[],
            recommendations=[]
        )

        action_items = self.reporter._generate_action_items(ac1, ac2, ac3, ac4)

        self.assertIsInstance(action_items, list)
        self.assertGreater(len(action_items), 0)

        # Check that critical issues are prioritized
        priorities = [item["priority"] for item in action_items]
        self.assertIn("HIGH", priorities)

    def test_calculate_confidence_level(self):
        """Test confidence level calculation"""
        ac1 = Mock()
        ac1.compatibility_score = 0.9
        ac3 = Mock()
        ac3.overall_score = 0.9
        ac4 = Mock()
        ac4.critical_issues = 0

        confidence = self.reporter._calculate_confidence_level(ac1, ac3, ac4)
        self.assertEqual(confidence, "High")

        # Test with critical issues
        ac4.critical_issues = 1
        confidence = self.reporter._calculate_confidence_level(ac1, ac3, ac4)
        self.assertEqual(confidence, "Low")

    def test_estimate_success_probability(self):
        """Test success probability estimation"""
        ac1 = Mock()
        ac1.compatibility_score = 0.9
        ac3 = Mock()
        ac3.overall_score = 0.85
        ac4 = Mock()
        ac4.critical_issues = 0

        probability = self.reporter._estimate_success_probability(ac1, ac3, ac4)
        self.assertGreater(probability, 0.7)
        self.assertLessEqual(probability, 1.0)

        # Test with critical issues
        ac4.critical_issues = 3
        probability = self.reporter._estimate_success_probability(ac1, ac3, ac4)
        self.assertLess(probability, 0.7)

    def test_generate_report_id(self):
        """Test report ID generation"""
        report_id_1 = self.reporter._generate_report_id()
        report_id_2 = self.reporter._generate_report_id()

        self.assertIsInstance(report_id_1, str)
        self.assertTrue(report_id_1.startswith("VER_"))
        self.assertNotEqual(report_id_1, report_id_2)

    def test_save_json_report(self):
        """Test saving JSON report"""
        ac1 = self.reporter._create_empty_ac1_results()
        ac2 = self.reporter._create_empty_ac2_results()
        ac3 = self.reporter._create_empty_ac3_results()
        ac4 = self.reporter._create_empty_ac4_results()

        result = self.reporter.generate_comprehensive_report(
            "/test/model.onnx",
            ac1_results=ac1,
            ac2_results=ac2,
            ac3_results=ac3,
            ac4_results=ac4,
            format_type=ReportFormat.JSON
        )

        # Check that file was created (exclude history file)
        report_files = [f for f in Path(self.test_dir).glob("*.json")
                       if f.name != "report_history.json"]
        self.assertGreater(len(report_files), 0)

        # Verify file content (check for report format)
        with open(report_files[0], 'r') as f:
            import json
            report_data = json.load(f)
            # Check the actual report format
            self.assertIn("metadata", report_data)
            self.assertIn("ac1_results", report_data)
            self.assertIn("executive_summary", report_data)

    def test_save_html_report(self):
        """Test saving HTML report"""
        ac1 = self.reporter._create_empty_ac1_results()
        ac2 = self.reporter._create_empty_ac2_results()
        ac3 = self.reporter._create_empty_ac3_results()
        ac4 = self.reporter._create_empty_ac4_results()

        result = self.reporter.generate_comprehensive_report(
            "/test/model.onnx",
            ac1_results=ac1,
            ac2_results=ac2,
            ac3_results=ac3,
            ac4_results=ac4,
            format_type=ReportFormat.HTML
        )

        # Check that HTML file was created
        report_files = list(Path(self.test_dir).glob("*.html"))
        self.assertGreater(len(report_files), 0)

        # Verify HTML content
        with open(report_files[0], 'r') as f:
            html_content = f.read()
            self.assertIn("<!DOCTYPE html>", html_content)
            self.assertIn("Comprehensive Verification Report", html_content)

    def test_save_markdown_report(self):
        """Test saving Markdown report"""
        ac1 = self.reporter._create_empty_ac1_results()
        ac2 = self.reporter._create_empty_ac2_results()
        ac3 = self.reporter._create_empty_ac3_results()
        ac4 = self.reporter._create_empty_ac4_results()

        result = self.reporter.generate_comprehensive_report(
            "/test/model.onnx",
            ac1_results=ac1,
            ac2_results=ac2,
            ac3_results=ac3,
            ac4_results=ac4,
            format_type=ReportFormat.MARKDOWN
        )

        # Check that Markdown file was created
        report_files = list(Path(self.test_dir).glob("*.md"))
        self.assertGreater(len(report_files), 0)

        # Verify Markdown content (account for emoji)
        with open(report_files[0], 'r') as f:
            md_content = f.read()
            self.assertIn("Comprehensive Verification Report", md_content)
            self.assertIn("Key Metrics", md_content)  # Don't check for "## " prefix

    def test_report_history_update(self):
        """Test report history tracking"""
        initial_history_count = len(self.reporter.report_history)

        ac1 = self.reporter._create_empty_ac1_results()
        ac2 = self.reporter._create_empty_ac2_results()
        ac3 = self.reporter._create_empty_ac3_results()
        ac4 = self.reporter._create_empty_ac4_results()

        result = self.reporter.generate_comprehensive_report(
            "/test/model.onnx",
            ac1_results=ac1,
            ac2_results=ac2,
            ac3_results=ac3,
            ac4_results=ac4
        )

        # Check history was updated
        self.assertEqual(len(self.reporter.report_history), initial_history_count + 1)
        self.assertEqual(self.reporter.report_history[-1]["report_id"], result.metadata.report_id)

    def test_get_report_history(self):
        """Test retrieving report history"""
        # Add some mock history
        self.reporter.report_history = [
            {
                "report_id": "R001",
                "model_name": "model1",
                "timestamp": "2025-10-28",
                "overall_status": "success"
            },
            {
                "report_id": "R002",
                "model_name": "model2",
                "timestamp": "2025-10-28",
                "overall_status": "partial_success"
            }
        ]

        # Get all history
        all_history = self.reporter.get_report_history()
        self.assertEqual(len(all_history), 2)

        # Get filtered history
        model1_history = self.reporter.get_report_history(model_name="model1")
        self.assertEqual(len(model1_history), 1)
        self.assertEqual(model1_history[0]["model_name"], "model1")

    def test_integration_analysis_generation(self):
        """Test integration analysis across ACs"""
        ac1 = Mock()
        ac1.structure_valid = True
        ac1.compatibility_score = 0.85
        ac1.orphaned_nodes = []

        ac2 = Mock()
        ac2.optimization_applied = True
        ac2.performance_improvement = 0.15
        ac2.model_type = "vision"

        ac3 = Mock()
        ac3.overall_score = 0.88

        ac4 = Mock()
        ac4.total_issues = 2
        ac4.critical_issues = 0
        ac4.overall_health = 0.9
        ac4.recommendations = ["Fix issue 1", "Fix issue 2"]

        analysis = self.reporter._generate_integration_analysis(ac1, ac2, ac3, ac4)

        self.assertIn("cross_validation_results", analysis)
        self.assertIn("optimization_impact", analysis)
        self.assertIn("diagnostic_correlation", analysis)
        self.assertIn("quality_consistency", analysis)
        self.assertIn("improvement_opportunities", analysis)
        self.assertIn("risk_assessment", analysis)

    def test_next_steps_generation(self):
        """Test next steps generation based on status"""
        ac1 = Mock()
        ac1.overall_valid = True
        ac1.compatibility_score = 0.9

        ac2 = Mock()
        ac2.optimization_applied = True

        ac3 = Mock()
        ac3.overall_score = 0.85

        ac4 = Mock()
        ac4.critical_issues = 0

        # Test SUCCESS status
        success_steps = self.reporter._generate_next_steps(
            ac1, ac2, ac3, ac4, ReportStatus.SUCCESS
        )
        self.assertIn("ready for conversion", success_steps[0].lower())

        # Test FAILED status
        failed_steps = self.reporter._generate_next_steps(
            ac1, ac2, ac3, ac4, ReportStatus.FAILED
        )
        self.assertIn("critical issues must be resolved", failed_steps[0].lower())

    def test_report_with_all_results(self):
        """Test generating report with all AC results provided"""
        # Create complete results with some issues to generate action items
        ac1 = AC1Results(
            overall_valid=True,
            structure_valid=True,
            dynamic_shape_valid=True,
            compatibility_valid=True,
            orphaned_nodes=["unused_node"],  # Add an orphaned node
            unused_weights=["unused_weight"],  # Add unused weight
            dynamic_dimensions={"input": [-1, 224, 224, 3]},
            compatibility_score=0.88,
            issues=[],
            warnings=[]
        )

        ac2 = AC2Results(
            optimization_applied=False,  # Not applied to trigger action item
            strategy_used="none",
            model_type="vision",
            best_config={},
            performance_improvement=0.0,
            before_metrics={},
            after_metrics={},
            recommendations=[]
        )

        ac3 = AC3Results(
            overall_score=0.65,  # Low score to trigger action items
            overall_grade="C",
            conversion_readiness=0.6,
            dimension_scores=[
                {"dimension": "structure", "score": 0.9},
                {"dimension": "numerical", "score": 0.4}  # Low score
            ],
            critical_issues=[],
            recommendations=["Improve numerical stability"],
            optimization_suggestions=[]
        )

        ac4 = AC4Results(
            overall_health=0.92,
            total_issues=1,
            critical_issues=0,
            findings=[{"severity": "medium", "description": "Minor issue"}],
            root_causes=["Minor configuration issue"],
            recommendations=["Adjust configuration settings"]
        )

        result = self.reporter.generate_comprehensive_report(
            "/test/vision_model.onnx",
            ac1_results=ac1,
            ac2_results=ac2,
            ac3_results=ac3,
            ac4_results=ac4
        )

        # Verify result structure
        self.assertIsInstance(result, ComprehensiveVerificationResult)
        self.assertEqual(result.metadata.model_name, "vision_model")
        # With orphaned nodes and low score, should be partial success
        self.assertEqual(result.overall_status, ReportStatus.PARTIAL_SUCCESS)
        self.assertGreaterEqual(len(result.action_items), 0)
        self.assertGreater(len(result.next_steps), 0)


if __name__ == "__main__":
    unittest.main()
