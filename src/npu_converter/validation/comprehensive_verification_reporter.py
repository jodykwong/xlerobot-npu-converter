"""
Comprehensive Verification Report Generator (AC5)

Generates comprehensive verification reports integrating results from:
- AC1: Model Structure Validation
- AC2: Intelligent Preprocessing Optimization
- AC3: Five-Dimensional Quality Assurance
- AC4: Intelligent Diagnosis and Repair

This module implements AC5's comprehensive verification reporting system.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class ReportFormat(Enum):
    """Supported report formats"""
    JSON = "json"
    HTML = "html"
    MARKDOWN = "markdown"
    PDF = "pdf"


class ReportStatus(Enum):
    """Verification report status"""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"
    PENDING = "pending"


@dataclass
class VerificationMetadata:
    """Metadata for verification report"""
    report_id: str
    model_name: str
    model_path: str
    generation_time: float
    tool_version: str
    report_version: str = "1.0"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AC1Results:
    """AC1: Model Structure Validation Results"""
    overall_valid: bool
    structure_valid: bool
    dynamic_shape_valid: bool
    compatibility_valid: bool
    orphaned_nodes: List[str]
    unused_weights: List[str]
    dynamic_dimensions: Dict[str, Any]
    compatibility_score: float
    issues: List[str]
    warnings: List[str]
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AC2Results:
    """AC2: Intelligent Preprocessing Optimization Results"""
    optimization_applied: bool
    strategy_used: str
    model_type: str
    best_config: Dict[str, Any]
    performance_improvement: float
    before_metrics: Dict[str, float]
    after_metrics: Dict[str, float]
    recommendations: List[str]
    optimization_history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class AC3Results:
    """AC3: Five-Dimensional Quality Assurance Results"""
    overall_score: float
    overall_grade: str
    conversion_readiness: float
    dimension_scores: List[Dict[str, Any]]
    critical_issues: List[str]
    recommendations: List[str]
    optimization_suggestions: List[str]
    dimension_metrics: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class AC4Results:
    """AC4: Intelligent Diagnosis and Repair Results"""
    overall_health: float
    total_issues: int
    critical_issues: int
    findings: List[Dict[str, Any]]
    root_causes: List[str]
    recommendations: List[str]
    repair_plan: Optional[Dict[str, Any]] = None
    diagnostic_report: Optional[Dict[str, Any]] = None


@dataclass
class ComprehensiveVerificationResult:
    """Complete verification result from AC1-AC4"""
    metadata: VerificationMetadata
    ac1_results: AC1Results
    ac2_results: AC2Results
    ac3_results: AC3Results
    ac4_results: AC4Results
    overall_status: ReportStatus
    executive_summary: Dict[str, Any]
    integration_analysis: Dict[str, Any]
    action_items: List[Dict[str, Any]]
    next_steps: List[str]


class ComprehensiveVerificationReporter:
    """
    Comprehensive Verification Report Generator (AC5)

    Integrates all validation results from AC1-AC4 and generates:
    1. Multi-format reports (JSON, HTML, Markdown, PDF)
    2. Executive summaries
    3. Technical analysis
    4. Actionable recommendations
    5. Report history tracking
    6. Comparative analysis
    """

    def __init__(self, output_dir: str = "./verification_reports"):
        """
        Initialize comprehensive verification reporter.

        Args:
            output_dir: Directory for output reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self.report_history = self._load_report_history()

    def generate_comprehensive_report(
        self,
        model_path: str,
        ac1_results: Optional[AC1Results] = None,
        ac2_results: Optional[AC2Results] = None,
        ac3_results: Optional[AC3Results] = None,
        ac4_results: Optional[AC4Results] = None,
        format_type: ReportFormat = ReportFormat.JSON
    ) -> ComprehensiveVerificationResult:
        """
        Generate comprehensive verification report integrating all AC results.

        Args:
            model_path: Path to the model file
            ac1_results: AC1 validation results
            ac2_results: AC2 optimization results
            ac3_results: AC3 quality scoring results
            ac4_results: AC4 diagnostic results
            format_type: Output format

        Returns:
            ComprehensiveVerificationResult with all integrated results
        """
        self.logger.info(f"Generating comprehensive verification report for {model_path}")

        # Generate metadata
        metadata = VerificationMetadata(
            report_id=self._generate_report_id(),
            model_name=Path(model_path).stem,
            model_path=model_path,
            generation_time=datetime.now().timestamp(),
            tool_version="Horizon X5 NPU Converter v2.5.0"
        )

        # Use default/empty results if not provided
        if ac1_results is None:
            ac1_results = self._create_empty_ac1_results()
        if ac2_results is None:
            ac2_results = self._create_empty_ac2_results()
        if ac3_results is None:
            ac3_results = self._create_empty_ac3_results()
        if ac4_results is None:
            ac4_results = self._create_empty_ac4_results()

        # Determine overall status
        overall_status = self._determine_overall_status(
            ac1_results, ac2_results, ac3_results, ac4_results
        )

        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            metadata, ac1_results, ac2_results, ac3_results, ac4_results, overall_status
        )

        # Generate integration analysis
        integration_analysis = self._generate_integration_analysis(
            ac1_results, ac2_results, ac3_results, ac4_results
        )

        # Generate action items
        action_items = self._generate_action_items(
            ac1_results, ac2_results, ac3_results, ac4_results
        )

        # Generate next steps
        next_steps = self._generate_next_steps(
            ac1_results, ac2_results, ac3_results, ac4_results, overall_status
        )

        # Compile comprehensive result
        result = ComprehensiveVerificationResult(
            metadata=metadata,
            ac1_results=ac1_results,
            ac2_results=ac2_results,
            ac3_results=ac3_results,
            ac4_results=ac4_results,
            overall_status=overall_status,
            executive_summary=executive_summary,
            integration_analysis=integration_analysis,
            action_items=action_items,
            next_steps=next_steps
        )

        # Save report in requested format
        self._save_report(result, format_type)

        # Update history
        self._update_report_history(result)

        self.logger.info(f"Comprehensive verification report generated: {metadata.report_id}")
        return result

    def _create_empty_ac1_results(self) -> AC1Results:
        """Create empty AC1 results structure"""
        return AC1Results(
            overall_valid=False,
            structure_valid=False,
            dynamic_shape_valid=False,
            compatibility_valid=False,
            orphaned_nodes=[],
            unused_weights=[],
            dynamic_dimensions={},
            compatibility_score=0.0,
            issues=["AC1 validation not performed"],
            warnings=[],
            details={}
        )

    def _create_empty_ac2_results(self) -> AC2Results:
        """Create empty AC2 results structure"""
        return AC2Results(
            optimization_applied=False,
            strategy_used="none",
            model_type="unknown",
            best_config={},
            performance_improvement=0.0,
            before_metrics={},
            after_metrics={},
            recommendations=[]
        )

    def _create_empty_ac3_results(self) -> AC3Results:
        """Create empty AC3 results structure"""
        return AC3Results(
            overall_score=0.0,
            overall_grade="N/A",
            conversion_readiness=0.0,
            dimension_scores=[],
            critical_issues=["AC3 quality scoring not performed"],
            recommendations=[],
            optimization_suggestions=[]
        )

    def _create_empty_ac4_results(self) -> AC4Results:
        """Create empty AC4 results structure"""
        return AC4Results(
            overall_health=0.0,
            total_issues=0,
            critical_issues=0,
            findings=[],
            root_causes=["AC4 diagnosis not performed"],
            recommendations=[]
        )

    def _determine_overall_status(
        self,
        ac1: AC1Results,
        ac2: AC2Results,
        ac3: AC3Results,
        ac4: AC4Results
    ) -> ReportStatus:
        """Determine overall verification status"""
        if not ac1.overall_valid:
            return ReportStatus.FAILED

        if ac4.critical_issues > 0:
            return ReportStatus.PARTIAL_SUCCESS

        if ac3.overall_score >= 0.8 and ac1.compatibility_score >= 0.8:
            return ReportStatus.SUCCESS

        return ReportStatus.PARTIAL_SUCCESS

    def _generate_executive_summary(
        self,
        metadata: VerificationMetadata,
        ac1: AC1Results,
        ac2: AC2Results,
        ac3: AC3Results,
        ac4: AC4Results,
        status: ReportStatus
    ) -> Dict[str, Any]:
        """Generate executive summary"""
        return {
            "verification_status": status.value,
            "model_name": metadata.model_name,
            "report_id": metadata.report_id,
            "timestamp": metadata.timestamp,
            "key_metrics": {
                "overall_quality_score": ac3.overall_score,
                "conversion_readiness": ac3.conversion_readiness,
                "model_health": ac4.overall_health,
                "structure_validity": 1.0 if ac1.structure_valid else 0.0,
                "optimization_improvement": ac2.performance_improvement,
                "compatibility_score": ac1.compatibility_score
            },
            "critical_findings": {
                "total_issues": ac4.total_issues,
                "critical_issues": ac4.critical_issues,
                "orphaned_nodes": len(ac1.orphaned_nodes),
                "unused_weights": len(ac1.unused_weights),
                "dynamic_dimensions": len(ac1.dynamic_dimensions)
            },
            "readiness_assessment": {
                "ready_for_conversion": status == ReportStatus.SUCCESS,
                "confidence_level": self._calculate_confidence_level(ac1, ac3, ac4),
                "estimated_success_probability": self._estimate_success_probability(ac1, ac3, ac4)
            },
            "top_recommendations": self._get_top_recommendations(ac1, ac2, ac3, ac4)
        }

    def _generate_integration_analysis(
        self,
        ac1: AC1Results,
        ac2: AC2Results,
        ac3: AC3Results,
        ac4: AC4Results
    ) -> Dict[str, Any]:
        """Generate integration analysis across all ACs"""
        return {
            "cross_validation_results": self._analyze_cross_validation(ac1, ac3),
            "optimization_impact": self._analyze_optimization_impact(ac1, ac2, ac3),
            "diagnostic_correlation": self._analyze_diagnostic_correlation(ac1, ac4),
            "quality_consistency": self._check_quality_consistency(ac1, ac3),
            "improvement_opportunities": self._identify_improvement_opportunities(ac1, ac2, ac3, ac4),
            "risk_assessment": self._assess_conversion_risks(ac1, ac3, ac4)
        }

    def _generate_action_items(
        self,
        ac1: AC1Results,
        ac2: AC2Results,
        ac3: AC3Results,
        ac4: AC4Results
    ) -> List[Dict[str, Any]]:
        """Generate prioritized action items"""
        action_items = []

        # Critical issues from AC4
        for finding in ac4.findings:
            if finding.get("severity") == "critical":
                action_items.append({
                    "priority": "CRITICAL",
                    "category": "Diagnosis & Repair",
                    "description": finding.get("description", ""),
                    "source": "AC4",
                    "action": "Immediate fix required",
                    "estimated_effort": "2-4 hours"
                })

        # Structure issues from AC1
        if ac1.orphaned_nodes:
            action_items.append({
                "priority": "HIGH",
                "category": "Structure Validation",
                "description": f"Remove {len(ac1.orphaned_nodes)} orphaned nodes",
                "source": "AC1",
                "action": "Clean up model structure",
                "estimated_effort": "30-60 minutes"
            })

        # Optimization opportunities from AC2
        if not ac2.optimization_applied:
            action_items.append({
                "priority": "MEDIUM",
                "category": "Preprocessing Optimization",
                "description": "Apply intelligent preprocessing optimization",
                "source": "AC2",
                "action": "Run optimization pipeline",
                "estimated_effort": "1-2 hours"
            })

        # Quality improvements from AC3
        low_scores = [d for d in ac3.dimension_scores if d.get("score", 0) < 0.7]
        if low_scores:
            action_items.append({
                "priority": "MEDIUM",
                "category": "Quality Enhancement",
                "description": f"Improve {len(low_scores)} low-scoring dimensions",
                "source": "AC3",
                "action": "Address quality issues",
                "estimated_effort": "2-4 hours"
            })

        return sorted(action_items, key=lambda x: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}[x["priority"]])

    def _generate_next_steps(
        self,
        ac1: AC1Results,
        ac2: AC2Results,
        ac3: AC3Results,
        ac4: AC4Results,
        status: ReportStatus
    ) -> List[str]:
        """Generate recommended next steps"""
        next_steps = []

        if status == ReportStatus.SUCCESS:
            next_steps.append("✅ Model is ready for conversion to Horizon X5 BPU format")
            next_steps.append("Proceed with model conversion pipeline")
            next_steps.append("Set up production monitoring")
        elif status == ReportStatus.PARTIAL_SUCCESS:
            next_steps.append("⚠️  Address identified issues before conversion")
            next_steps.append("Follow action items in priority order")
            next_steps.append("Re-run verification after fixes")
        else:  # FAILED
            next_steps.append("❌ Critical issues must be resolved")
            next_steps.append("Review diagnostic findings from AC4")
            next_steps.append("Consider model architecture review")

        next_steps.extend([
            "Review comprehensive verification report",
            "Consult knowledge base for detailed solutions",
            "Track progress in verification dashboard"
        ])

        return next_steps

    def _analyze_cross_validation(self, ac1: AC1Results, ac3: AC3Results) -> Dict[str, Any]:
        """Analyze cross-validation between AC1 and AC3"""
        return {
            "structure_consistency": ac1.structure_valid == (ac3.overall_score > 0.7),
            "compatibility_alignment": abs(ac1.compatibility_score - ac3.overall_score) < 0.2,
            "validation_harmony": "Good" if abs(ac1.compatibility_score - ac3.overall_score) < 0.1 else "Fair"
        }

    def _analyze_optimization_impact(
        self,
        ac1: AC1Results,
        ac2: AC2Results,
        ac3: AC3Results
    ) -> Dict[str, Any]:
        """Analyze impact of preprocessing optimization"""
        return {
            "optimization_performed": ac2.optimization_applied,
            "performance_gain": ac2.performance_improvement,
            "model_type_detected": ac2.model_type,
            "impact_on_quality": "Positive" if ac2.performance_improvement > 0 else "Neutral",
            "recommendation": "Apply optimization" if not ac2.optimization_applied else "Optimization complete"
        }

    def _analyze_diagnostic_correlation(self, ac1: AC1Results, ac4: AC4Results) -> Dict[str, Any]:
        """Analyze correlation between AC1 issues and AC4 diagnosis"""
        return {
            "issues_detected": ac4.total_issues > 0,
            "critical_correlation": ac4.critical_issues > 0,
            "diagnosis_accuracy": "High" if ac4.overall_health > 0.8 else "Medium",
            "recommended_actions": len(ac4.recommendations)
        }

    def _check_quality_consistency(self, ac1: AC1Results, ac3: AC3Results) -> Dict[str, Any]:
        """Check consistency between AC1 and AC3 quality assessments"""
        return {
            "consistency_score": 1.0 - abs(ac1.compatibility_score - ac3.overall_score),
            "status": "Consistent" if abs(ac1.compatibility_score - ac3.overall_score) < 0.15 else "Inconsistent",
            "variance": (ac1.compatibility_score - ac3.overall_score) ** 2
        }

    def _identify_improvement_opportunities(
        self,
        ac1: AC1Results,
        ac2: AC2Results,
        ac3: AC3Results,
        ac4: AC4Results
    ) -> List[Dict[str, Any]]:
        """Identify opportunities for improvement"""
        opportunities = []

        if ac3.overall_score < 0.8:
            opportunities.append({
                "area": "Overall Quality",
                "potential_gain": 0.8 - ac3.overall_score,
                "effort": "Medium"
            })

        if ac2.performance_improvement < 0.1:
            opportunities.append({
                "area": "Preprocessing Optimization",
                "potential_gain": 0.15,
                "effort": "Low"
            })

        if ac4.overall_health < 0.9:
            opportunities.append({
                "area": "Model Health",
                "potential_gain": 0.9 - ac4.overall_health,
                "effort": "High"
            })

        return opportunities

    def _assess_conversion_risks(
        self,
        ac1: AC1Results,
        ac3: AC3Results,
        ac4: AC4Results
    ) -> Dict[str, Any]:
        """Assess risks for model conversion"""
        risk_score = 0.0
        risk_factors = []

        if ac4.critical_issues > 0:
            risk_score += 0.4
            risk_factors.append("Critical diagnostic issues")

        if ac3.overall_score < 0.7:
            risk_score += 0.3
            risk_factors.append("Low quality score")

        if ac1.compatibility_score < 0.8:
            risk_score += 0.2
            risk_factors.append("Compatibility concerns")

        risk_level = "High" if risk_score > 0.6 else "Medium" if risk_score > 0.3 else "Low"

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "mitigation_strategies": [
                "Address critical issues first",
                "Apply recommended optimizations",
                "Re-validate after changes"
            ]
        }

    def _calculate_confidence_level(
        self,
        ac1: AC1Results,
        ac3: AC3Results,
        ac4: AC4Results
    ) -> str:
        """Calculate confidence level for conversion"""
        if ac4.critical_issues > 0:
            return "Low"
        if ac3.overall_score > 0.85 and ac1.compatibility_score > 0.85:
            return "High"
        if ac3.overall_score > 0.7 and ac1.compatibility_score > 0.7:
            return "Medium"
        return "Low"

    def _estimate_success_probability(
        self,
        ac1: AC1Results,
        ac3: AC3Results,
        ac4: AC4Results
    ) -> float:
        """Estimate probability of successful conversion"""
        base_prob = 0.5

        # Adjust based on scores
        if ac3.overall_score > 0:
            base_prob += (ac3.overall_score - 0.5) * 0.4
        if ac1.compatibility_score > 0:
            base_prob += (ac1.compatibility_score - 0.5) * 0.3

        # Penalize for critical issues
        if ac4.critical_issues > 0:
            base_prob -= min(0.4, ac4.critical_issues * 0.1)

        return max(0.0, min(1.0, base_prob))

    def _get_top_recommendations(
        self,
        ac1: AC1Results,
        ac2: AC2Results,
        ac3: AC3Results,
        ac4: AC4Results
    ) -> List[str]:
        """Get top 3 recommendations"""
        recommendations = []

        # Add from AC4
        recommendations.extend(ac4.recommendations[:2])

        # Add from AC3
        recommendations.extend(ac3.recommendations[:1])

        # Add from AC1
        if ac1.issues:
            recommendations.append(f"Fix {len(ac1.issues)} structural issues")

        return recommendations[:3]

    def _generate_report_id(self) -> str:
        """Generate unique report ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        import random
        import string
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"VER_{timestamp}_{random_suffix}"

    def _save_report(
        self,
        result: ComprehensiveVerificationResult,
        format_type: ReportFormat
    ):
        """Save report in specified format"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_name = result.metadata.model_name
        filename = f"{model_name}_verification_{timestamp}"

        if format_type == ReportFormat.JSON:
            self._save_json_report(result, filename)
        elif format_type == ReportFormat.HTML:
            self._save_html_report(result, filename)
        elif format_type == ReportFormat.MARKDOWN:
            self._save_markdown_report(result, filename)
        elif format_type == ReportFormat.PDF:
            self._save_pdf_report(result, filename)

    def _save_json_report(self, result: ComprehensiveVerificationResult, filename: str):
        """Save report as JSON"""
        output_path = self.output_dir / f"{filename}.json"

        # Convert to dict
        report_dict = {
            "metadata": asdict(result.metadata),
            "ac1_results": asdict(result.ac1_results),
            "ac2_results": asdict(result.ac2_results),
            "ac3_results": asdict(result.ac3_results),
            "ac4_results": asdict(result.ac4_results),
            "overall_status": result.overall_status.value,
            "executive_summary": result.executive_summary,
            "integration_analysis": result.integration_analysis,
            "action_items": result.action_items,
            "next_steps": result.next_steps
        }

        with open(output_path, 'w') as f:
            json.dump(report_dict, f, indent=2, default=str)

        self.logger.info(f"JSON report saved to: {output_path}")

    def _save_html_report(self, result: ComprehensiveVerificationResult, filename: str):
        """Save report as HTML"""
        output_path = self.output_dir / f"{filename}.html"

        html_content = self._generate_html_report(result)

        with open(output_path, 'w') as f:
            f.write(html_content)

        self.logger.info(f"HTML report saved to: {output_path}")

    def _save_markdown_report(self, result: ComprehensiveVerificationResult, filename: str):
        """Save report as Markdown"""
        output_path = self.output_dir / f"{filename}.md"

        md_content = self._generate_markdown_report(result)

        with open(output_path, 'w') as f:
            f.write(md_content)

        self.logger.info(f"Markdown report saved to: {output_path}")

    def _save_pdf_report(self, result: ComprehensiveVerificationResult, filename: str):
        """Save report as PDF (placeholder - would need pdfkit or similar)"""
        output_path = self.output_dir / f"{filename}.pdf"

        # For now, save as HTML with .pdf extension
        # In production, use proper PDF generation library
        html_content = self._generate_html_report(result)
        with open(output_path.with_suffix('.html'), 'w') as f:
            f.write(html_content)

        self.logger.warning(f"PDF generation not fully implemented, saved as HTML: {output_path}")

    def _generate_html_report(self, result: ComprehensiveVerificationResult) -> str:
        """Generate HTML report content"""
        # Status indicator
        status_icon = {
            "success": "✅",
            "partial_success": "⚠️",
            "failed": "❌",
            "pending": "⏳"
        }.get(result.overall_status.value, "📄")

        # Generate CSS
        css = """
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 8px;
                margin-bottom: 30px;
            }
            .header h1 {
                margin: 0;
                font-size: 28px;
            }
            .header p {
                margin: 10px 0 0 0;
                opacity: 0.9;
            }
            .status-badge {
                display: inline-block;
                padding: 5px 15px;
                border-radius: 20px;
                font-weight: bold;
                margin-top: 10px;
            }
            .status-success { background-color: #4CAF50; color: white; }
            .status-partial { background-color: #FF9800; color: white; }
            .status-failed { background-color: #f44336; color: white; }
            .section {
                margin: 30px 0;
                padding: 20px;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
            }
            .section h2 {
                margin-top: 0;
                color: #333;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }
            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }
            .metric-card {
                background-color: #f9f9f9;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #667eea;
            }
            .metric-label {
                font-size: 12px;
                color: #666;
                text-transform: uppercase;
            }
            .metric-value {
                font-size: 24px;
                font-weight: bold;
                color: #333;
                margin: 5px 0;
            }
            .action-item {
                padding: 10px;
                margin: 10px 0;
                border-radius: 5px;
                border-left: 4px solid;
            }
            .action-critical { background-color: #ffebee; border-color: #f44336; }
            .action-high { background-color: #fff3e0; border-color: #FF9800; }
            .action-medium { background-color: #fff9c4; border-color: #FFC107; }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
            }
            th, td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #e0e0e0;
            }
            th {
                background-color: #f5f5f5;
                font-weight: bold;
            }
            .progress-bar {
                width: 100%;
                height: 20px;
                background-color: #e0e0e0;
                border-radius: 10px;
                overflow: hidden;
            }
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                transition: width 0.3s ease;
            }
        </style>
        """

        # Generate HTML body
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Comprehensive Verification Report - {result.metadata.model_name}</title>
            {css}
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Comprehensive Verification Report</h1>
                    <p>Model: <strong>{result.metadata.model_name}</strong></p>
                    <p>Report ID: {result.metadata.report_id}</p>
                    <p>Generated: {result.metadata.timestamp}</p>
                    <span class="status-badge status-{result.overall_status.value}">
                        {status_icon} {result.overall_status.value.upper().replace('_', ' ')}
                    </span>
                </div>

                <div class="section">
                    <h2>📈 Key Metrics</h2>
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-label">Overall Quality</div>
                            <div class="metric-value">{result.ac3_results.overall_score:.1%}</div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {result.ac3_results.overall_score*100}%"></div>
                            </div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Conversion Readiness</div>
                            <div class="metric-value">{result.ac3_results.conversion_readiness:.1%}</div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {result.ac3_results.conversion_readiness*100}%"></div>
                            </div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Model Health</div>
                            <div class="metric-value">{result.ac4_results.overall_health:.1%}</div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {result.ac4_results.overall_health*100}%"></div>
                            </div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Compatibility</div>
                            <div class="metric-value">{result.ac1_results.compatibility_score:.1%}</div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {result.ac1_results.compatibility_score*100}%"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>🔍 Critical Findings</h2>
                    <table>
                        <tr>
                            <th>Metric</th>
                            <th>Value</th>
                            <th>Status</th>
                        </tr>
                        <tr>
                            <td>Total Issues Detected</td>
                            <td>{result.ac4_results.total_issues}</td>
                            <td>{'⚠️' if result.ac4_results.total_issues > 0 else '✅'}</td>
                        </tr>
                        <tr>
                            <td>Critical Issues</td>
                            <td>{result.ac4_results.critical_issues}</td>
                            <td>{'❌' if result.ac4_results.critical_issues > 0 else '✅'}</td>
                        </tr>
                        <tr>
                            <td>Orphaned Nodes</td>
                            <td>{len(result.ac1_results.orphaned_nodes)}</td>
                            <td>{'⚠️' if result.ac1_results.orphaned_nodes else '✅'}</td>
                        </tr>
                        <tr>
                            <td>Unused Weights</td>
                            <td>{len(result.ac1_results.unused_weights)}</td>
                            <td>{'⚠️' if result.ac1_results.unused_weights else '✅'}</td>
                        </tr>
                    </table>
                </div>

                <div class="section">
                    <h2>✅ Action Items</h2>
                    {''.join([f'''
                    <div class="action-item action-{item['priority'].lower()}">
                        <strong>[{item['priority']}] {item['category']}</strong><br>
                        {item['description']}<br>
                        <em>Estimated effort: {item['estimated_effort']}</em>
                    </div>
                    ''' for item in result.action_items[:5]])}

                    {'<p><em>No critical action items</em></p>' if not result.action_items else ''}
                </div>

                <div class="section">
                    <h2>🎯 Next Steps</h2>
                    <ol>
                        {''.join([f'<li>{step}</li>' for step in result.next_steps[:5]])}
                    </ol>
                </div>

                <div class="section">
                    <h2>📋 Detailed Results</h2>
                    <h3>AC1 - Model Structure Validation</h3>
                    <ul>
                        <li>Overall Valid: {'✅' if result.ac1_results.overall_valid else '❌'}</li>
                        <li>Structure Valid: {'✅' if result.ac1_results.structure_valid else '❌'}</li>
                        <li>Dynamic Shape Valid: {'✅' if result.ac1_results.dynamic_shape_valid else '❌'}</li>
                        <li>Compatibility Valid: {'✅' if result.ac1_results.compatibility_valid else '❌'}</li>
                    </ul>

                    <h3>AC2 - Intelligent Preprocessing Optimization</h3>
                    <ul>
                        <li>Optimization Applied: {'✅' if result.ac2_results.optimization_applied else '❌'}</li>
                        <li>Strategy Used: {result.ac2_results.strategy_used}</li>
                        <li>Model Type: {result.ac2_results.model_type}</li>
                        <li>Performance Improvement: {result.ac2_results.performance_improvement:.1%}</li>
                    </ul>

                    <h3>AC3 - Five-Dimensional Quality Assurance</h3>
                    <ul>
                        <li>Overall Grade: {result.ac3_results.overall_grade}</li>
                        <li>Conversion Readiness: {result.ac3_results.conversion_readiness:.1%}</li>
                    </ul>

                    <h3>AC4 - Intelligent Diagnosis and Repair</h3>
                    <ul>
                        <li>Overall Health: {result.ac4_results.overall_health:.1%}</li>
                        <li>Root Causes: {len(result.ac4_results.root_causes)}</li>
                        <li>Recommendations: {len(result.ac4_results.recommendations)}</li>
                    </ul>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def _generate_markdown_report(self, result: ComprehensiveVerificationResult) -> str:
        """Generate Markdown report content"""
        status_icon = {
            "success": "✅",
            "partial_success": "⚠️",
            "failed": "❌",
            "pending": "⏳"
        }.get(result.overall_status.value, "📄")

        md = f"""# 📊 Comprehensive Verification Report

**Model:** {result.metadata.model_name}
**Report ID:** {result.metadata.report_id}
**Generated:** {result.metadata.timestamp}
**Status:** {status_icon} {result.overall_status.value.upper().replace('_', ' ')}

---

## 📈 Key Metrics

| Metric | Value |
|--------|-------|
| Overall Quality Score | {result.ac3_results.overall_score:.1%} |
| Conversion Readiness | {result.ac3_results.conversion_readiness:.1%} |
| Model Health | {result.ac4_results.overall_health:.1%} |
| Compatibility Score | {result.ac1_results.compatibility_score:.1%} |

---

## 🔍 Critical Findings

- **Total Issues Detected:** {result.ac4_results.total_issues}
- **Critical Issues:** {result.ac4_results.critical_issues}
- **Orphaned Nodes:** {len(result.ac1_results.orphaned_nodes)}
- **Unused Weights:** {len(result.ac1_results.unused_weights)}

---

## ✅ Action Items

{chr(10).join([f"- **{item['priority']}** [{item['category']}] {item['description']} _(Effort: {item['estimated_effort']})_" for item in result.action_items[:5]])}

---

## 🎯 Next Steps

{chr(10).join([f"{i+1}. {step}" for i, step in enumerate(result.next_steps[:5])])}

---

## 📋 Detailed Results

### AC1 - Model Structure Validation
- Overall Valid: {'✅' if result.ac1_results.overall_valid else '❌'}
- Structure Valid: {'✅' if result.ac1_results.structure_valid else '❌'}
- Dynamic Shape Valid: {'✅' if result.ac1_results.dynamic_shape_valid else '❌'}
- Compatibility Valid: {'✅' if result.ac1_results.compatibility_valid else '❌'}

### AC2 - Intelligent Preprocessing Optimization
- Optimization Applied: {'✅' if result.ac2_results.optimization_applied else '❌'}
- Strategy Used: {result.ac2_results.strategy_used}
- Model Type: {result.ac2_results.model_type}
- Performance Improvement: {result.ac2_results.performance_improvement:.1%}

### AC3 - Five-Dimensional Quality Assurance
- Overall Grade: {result.ac3_results.overall_grade}
- Conversion Readiness: {result.ac3_results.conversion_readiness:.1%}

### AC4 - Intelligent Diagnosis and Repair
- Overall Health: {result.ac4_results.overall_health:.1%}
- Root Causes: {len(result.ac4_results.root_causes)}
- Recommendations: {len(result.ac4_results.recommendations)}

---

*Report generated by Horizon X5 NPU Converter v{result.metadata.tool_version}*
"""

        return md

    def _load_report_history(self) -> List[Dict[str, Any]]:
        """Load report history from file"""
        history_file = self.output_dir / "report_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load report history: {e}")
        return []

    def _update_report_history(self, result: ComprehensiveVerificationResult):
        """Update report history"""
        history_entry = {
            "report_id": result.metadata.report_id,
            "model_name": result.metadata.model_name,
            "timestamp": result.metadata.timestamp,
            "overall_status": result.overall_status.value,
            "overall_score": result.ac3_results.overall_score,
            "conversion_readiness": result.ac3_results.conversion_readiness
        }

        self.report_history.append(history_entry)

        # Keep only last 100 reports
        self.report_history = self.report_history[-100:]

        # Save to file
        history_file = self.output_dir / "report_history.json"
        try:
            with open(history_file, 'w') as f:
                json.dump(self.report_history, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save report history: {e}")

    def get_report_history(self, model_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get report history, optionally filtered by model name.

        Args:
            model_name: Optional model name filter

        Returns:
            List of historical reports
        """
        if model_name:
            return [r for r in self.report_history if r["model_name"] == model_name]
        return self.report_history

    def compare_reports(
        self,
        report_id_1: str,
        report_id_2: str
    ) -> Dict[str, Any]:
        """
        Compare two verification reports.

        Args:
            report_id_1: First report ID
            report_id_2: Second report ID

        Returns:
            Comparison results
        """
        # This would load reports from history and compare them
        # For now, return a placeholder
        return {
            "report_1": report_id_1,
            "report_2": report_id_2,
            "comparison": "Feature not yet implemented"
        }
