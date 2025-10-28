"""
Diagnostic Engine for Model Validation

Provides intelligent diagnosis of validation failures with repair guidance.
Extends Story 1.7's ErrorHandler with smart diagnosis capabilities.

This module implements AC4's smart diagnosis and repair system.
"""

import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .knowledge_base import DiagnosticKnowledgeBase
from .repair_guide import RepairGuide

logger = logging.getLogger(__name__)


class IssueSeverity(Enum):
    """Severity levels for diagnostic issues"""
    CRITICAL = "critical"  # Blocks conversion
    HIGH = "high"          # Significant impact
    MEDIUM = "medium"      # Moderate impact
    LOW = "low"            # Minor issue
    INFO = "info"          # Informational


class IssueCategory(Enum):
    """Categories of diagnostic issues"""
    STRUCTURE = "structure"
    NUMERICAL = "numerical"
    COMPATIBILITY = "compatibility"
    PERFORMANCE = "performance"
    DYNAMIC_SHAPE = "dynamic_shape"
    OPERATOR = "operator"
    PREPROCESSING = "preprocessing"
    CONVERSION = "conversion"


@dataclass
class DiagnosticFinding:
    """Individual diagnostic finding"""
    issue_id: str
    category: IssueCategory
    severity: IssueSeverity
    description: str
    location: Optional[str] = None
    confidence: float = 1.0
    evidence: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class DiagnosticResult:
    """Complete diagnostic result"""
    model_name: str
    timestamp: float
    overall_health: float  # 0.0 - 1.0
    total_issues: int
    critical_issues: int
    findings: List[DiagnosticFinding]
    root_causes: List[str]
    recommendations: List[str]
    repair_plan: Optional[Dict[str, Any]] = None


class DiagnosticEngine:
    """
    Intelligent diagnostic engine for model validation failures.

    AC4的核心诊断引擎，提供：
    1. 智能问题检测
    2. 根因分析
    3. 解决方案推荐
    4. 修复步骤指导

    Integrates with:
    - DiagnosticKnowledgeBase (问题知识库)
    - RepairGuide (修复向导)
    - Story 1.7 ErrorHandler (错误处理)
    """

    def __init__(self):
        """Initialize the DiagnosticEngine"""
        logger.info("Initializing DiagnosticEngine")
        self.knowledge_base = DiagnosticKnowledgeBase()
        self.repair_guide = RepairGuide()
        self.diagnosis_patterns = self._initialize_diagnosis_patterns()

    def _initialize_diagnosis_patterns(self) -> Dict[str, Any]:
        """Initialize diagnosis patterns for common issues"""
        return {
            "dynamic_shape": {
                "keywords": ["dynamic", "shape", "dimension", "-1", "None"],
                "patterns": [
                    r"unsupported dynamic dimension",
                    r"incompatible shape",
                    r"batch size not supported"
                ],
                "category": IssueCategory.DYNAMIC_SHAPE,
                "severity": IssueSeverity.HIGH,
                "probability": 0.85
            },
            "operator_support": {
                "keywords": ["operator", "not supported", "compatibility"],
                "patterns": [
                    r"operator .+ not supported",
                    r"incompatible operator",
                    r"BPU does not support"
                ],
                "category": IssueCategory.COMPATIBILITY,
                "severity": IssueSeverity.CRITICAL,
                "probability": 0.9
            },
            "structure": {
                "keywords": ["cycle", "orphan", "unused", "connectivity"],
                "patterns": [
                    r"circular dependency",
                    r"orphaned node",
                    r"unused weight"
                ],
                "category": IssueCategory.STRUCTURE,
                "severity": IssueSeverity.MEDIUM,
                "probability": 0.75
            },
            "numerical": {
                "keywords": ["numerical", "instability", "precision", "overflow"],
                "patterns": [
                    r"numerical instability",
                    r"precision mismatch",
                    r"value out of range"
                ],
                "category": IssueCategory.NUMERICAL,
                "severity": IssueSeverity.HIGH,
                "probability": 0.8
            },
            "performance": {
                "keywords": ["slow", "latency", "memory", "throughput"],
                "patterns": [
                    r"high memory usage",
                    r"slow inference",
                    r"performance degradation"
                ],
                "category": IssueCategory.PERFORMANCE,
                "severity": IssueSeverity.MEDIUM,
                "probability": 0.7
            }
        }

    def diagnose_validation_failure(self,
                                   failure_info: Dict[str, Any],
                                   validation_results: Optional[List[Dict[str, Any]]] = None) -> DiagnosticResult:
        """
        Diagnose validation failures and provide repair guidance.

        Args:
            failure_info: Information about the validation failure
            validation_results: Optional list of validation results from AC1-AC3

        Returns:
            DiagnosticResult with detailed diagnosis and repair plan
        """
        logger.info("Starting comprehensive diagnostic analysis")

        start_time = time.time()

        # Step 1: Extract failure information
        model_name = failure_info.get("model_name", "Unknown Model")
        error_message = failure_info.get("error_message", "")
        error_type = failure_info.get("error_type", "Unknown")

        # Step 2: Identify issues using pattern matching
        findings = self._identify_issues(error_message, error_type, validation_results)

        # Step 3: Analyze root causes
        root_causes = self._analyze_root_causes(findings)

        # Step 4: Generate recommendations
        recommendations = self._generate_recommendations(findings, root_causes)

        # Step 5: Create repair plan
        repair_plan = self._create_repair_plan(findings, recommendations)

        # Step 6: Calculate overall health
        overall_health = self._calculate_overall_health(findings)

        # Step 7: Compile results
        result = DiagnosticResult(
            model_name=model_name,
            timestamp=start_time,
            overall_health=overall_health,
            total_issues=len(findings),
            critical_issues=len([f for f in findings if f.severity == IssueSeverity.CRITICAL]),
            findings=findings,
            root_causes=root_causes,
            recommendations=recommendations,
            repair_plan=repair_plan
        )

        elapsed_time = time.time() - start_time
        logger.info(f"Diagnostic analysis completed in {elapsed_time:.2f}s")
        logger.info(f"Found {len(findings)} issues, {result.critical_issues} critical")

        return result

    def _identify_issues(self,
                        error_message: str,
                        error_type: str,
                        validation_results: Optional[List[Dict[str, Any]]]) -> List[DiagnosticFinding]:
        """
        Identify issues using pattern matching and analysis.

        Args:
            error_message: Error message text
            error_type: Type of error
            validation_results: Validation results from AC1-AC3

        Returns:
            List of DiagnosticFinding objects
        """
        findings = []
        error_lower = error_message.lower()

        # Match against known patterns
        for pattern_name, pattern_data in self.diagnosis_patterns.items():
            # Check keywords
            keyword_match = any(keyword in error_lower for keyword in pattern_data["keywords"])

            # Check regex patterns
            import re
            pattern_match = any(re.search(p, error_lower, re.IGNORECASE)
                              for p in pattern_data["patterns"])

            if keyword_match or pattern_match:
                # Create finding
                finding = DiagnosticFinding(
                    issue_id=f"{pattern_name}_{len(findings)}",
                    category=pattern_data["category"],
                    severity=pattern_data["severity"],
                    description=self._generate_issue_description(pattern_name, error_message),
                    confidence=pattern_data["probability"],
                    evidence=[error_message],
                    suggestions=self._generate_issue_suggestions(pattern_name)
                )
                findings.append(finding)

        # Analyze validation results for additional issues
        if validation_results:
            findings.extend(self._analyze_validation_results(validation_results))

        return findings

    def _analyze_root_causes(self, findings: List[DiagnosticFinding]) -> List[str]:
        """
        Analyze findings to determine root causes.

        Args:
            findings: List of diagnostic findings

        Returns:
            List of root causes
        """
        root_causes = []

        # Group findings by category
        category_counts = {}
        for finding in findings:
            category = finding.category.value
            category_counts[category] = category_counts.get(category, 0) + 1

        # Determine primary root cause
        if category_counts:
            primary_category = max(category_counts, key=category_counts.get)
            root_causes.append(f"Primary issue in {primary_category} ({category_counts[primary_category]} findings)")

        # Identify critical patterns
        critical_findings = [f for f in findings if f.severity == IssueSeverity.CRITICAL]
        if critical_findings:
            root_causes.append(f"Critical error blocking conversion: {critical_findings[0].description}")

        # Analyze confidence levels
        low_confidence = [f for f in findings if f.confidence < 0.7]
        if low_confidence:
            root_causes.append(f"Low confidence diagnosis for {len(low_confidence)} issues (unclear root cause)")

        return root_causes

    def _generate_issue_description(self, pattern_name: str, error_message: str) -> str:
        """Generate human-readable issue description"""
        descriptions = {
            "dynamic_shape": "Dynamic shape compatibility issue",
            "operator_support": "Operator not supported by Horizon X5 BPU",
            "structure": "Model structure problem",
            "numerical": "Numerical stability issue",
            "performance": "Performance optimization opportunity"
        }

        base_desc = descriptions.get(pattern_name, "Validation issue detected")

        # Add error context
        if error_message:
            return f"{base_desc}: {error_message[:100]}..."

        return base_desc

    def _generate_issue_suggestions(self, pattern_name: str) -> List[str]:
        """Generate suggestions for specific issue pattern"""
        suggestions_map = {
            "dynamic_shape": [
                "Use fixed shapes instead of dynamic dimensions",
                "Apply Horizon X5 BPU shape constraints",
                "Consider batch size = 1 for first inference"
            ],
            "operator_support": [
                "Replace unsupported operator with Horizon X5 compatible alternative",
                "Use operator fusion to combine operations",
                "Refer to Horizon X5 BPU operator support matrix"
            ],
            "structure": [
                "Remove orphaned nodes from the model",
                "Clean up unused weights and parameters",
                "Fix circular dependencies"
            ],
            "numerical": [
                "Check weight initialization",
                "Validate numerical precision",
                "Review activation function choices"
            ],
            "performance": [
                "Optimize model architecture",
                "Consider quantization",
                "Reduce model complexity"
            ]
        }

        return suggestions_map.get(pattern_name, ["Review validation details"])

    def _analyze_validation_results(self,
                                   validation_results: List[Dict[str, Any]]) -> List[DiagnosticFinding]:
        """
        Analyze validation results from AC1-AC3 for issues.

        Args:
            validation_results: Validation results

        Returns:
            List of additional findings
        """
        findings = []

        for result in validation_results:
            result_type = result.get("type", "unknown")
            result_data = result.get("data", {})

            if result_type == "structure" and not result_data.get("is_valid", True):
                # Structure validation failed
                issues = result_data.get("issues", [])
                for issue in issues:
                    findings.append(DiagnosticFinding(
                        issue_id=f"structure_{len(findings)}",
                        category=IssueCategory.STRUCTURE,
                        severity=IssueSeverity.HIGH,
                        description=f"Structure issue: {issue}",
                        confidence=0.9,
                        suggestions=["Review model topology", "Check node connections"]
                    ))

            elif result_type == "dynamic_shape" and result_data.get("has_unsupported_dynamic_dims"):
                # Dynamic shape issues
                findings.append(DiagnosticFinding(
                    issue_id=f"dynamic_shape_{len(findings)}",
                    category=IssueCategory.DYNAMIC_SHAPE,
                    severity=IssueSeverity.HIGH,
                    description="Unsupported dynamic dimensions detected",
                    confidence=0.95,
                    suggestions=[
                        "Use fixed shapes",
                        "Apply Horizon X5 BPU constraints",
                        "Set batch dimension to 1"
                    ]
                ))

            elif result_type == "compatibility" and not result_data.get("compatible", True):
                # Compatibility issues
                issues = result_data.get("issues", [])
                findings.append(DiagnosticFinding(
                    issue_id=f"compatibility_{len(findings)}",
                    category=IssueCategory.COMPATIBILITY,
                    severity=IssueSeverity.CRITICAL,
                    description=f"Compatibility issues: {len(issues)} problems detected",
                    confidence=0.9,
                    suggestions=[
                        "Replace incompatible operators",
                        "Check Horizon X5 BPU operator support",
                        "Consider operator fusion"
                    ]
                ))

        return findings

    def _generate_recommendations(self,
                                 findings: List[DiagnosticFinding],
                                 root_causes: List[str]) -> List[str]:
        """
        Generate overall recommendations based on findings.

        Args:
            findings: List of diagnostic findings
            root_causes: List of root causes

        Returns:
            List of recommendations
        """
        recommendations = []

        # Prioritize by severity
        critical_findings = [f for f in findings if f.severity == IssueSeverity.CRITICAL]
        high_findings = [f for f in findings if f.severity == IssueSeverity.HIGH]

        if critical_findings:
            recommendations.append(
                f"🚨 CRITICAL: Address {len(critical_findings)} critical issues blocking conversion"
            )

        if high_findings:
            recommendations.append(
                f"⚠️  HIGH: Fix {len(high_findings)} high-priority issues"
            )

        # Add category-specific recommendations
        categories = set(f.category for f in findings)
        if IssueCategory.COMPATIBILITY in categories:
            recommendations.append("📋 Review Horizon X5 BPU operator compatibility matrix")
        if IssueCategory.DYNAMIC_SHAPE in categories:
            recommendations.append("📐 Validate dynamic shapes against Horizon X5 constraints")
        if IssueCategory.STRUCTURE in categories:
            recommendations.append("🔧 Clean up model structure (remove orphans, unused weights)")
        if IssueCategory.NUMERICAL in categories:
            recommendations.append("🔢 Review numerical stability and precision settings")

        # Add general recommendations
        if len(findings) > 5:
            recommendations.append("📊 Consider model simplification to reduce complexity")

        recommendations.append("📚 Consult diagnostic knowledge base for detailed solutions")
        recommendations.append("🛠️  Follow interactive repair guide for step-by-step fixes")

        return recommendations

    def _create_repair_plan(self,
                           findings: List[DiagnosticFinding],
                           recommendations: List[str]) -> Dict[str, Any]:
        """
        Create a structured repair plan.

        Args:
            findings: List of diagnostic findings
            recommendations: List of recommendations

        Returns:
            Repair plan dictionary
        """
        # Group findings by severity
        by_severity = {
            IssueSeverity.CRITICAL: [],
            IssueSeverity.HIGH: [],
            IssueSeverity.MEDIUM: [],
            IssueSeverity.LOW: [],
            IssueSeverity.INFO: []
        }

        for finding in findings:
            by_severity[finding.severity].append(finding)

        # Create repair steps
        repair_steps = []

        # Step 1: Critical issues
        if by_severity[IssueSeverity.CRITICAL]:
            repair_steps.append({
                "step": 1,
                "priority": "CRITICAL",
                "title": "Fix Critical Issues",
                "description": "Address issues that block conversion",
                "findings": [f.issue_id for f in by_severity[IssueSeverity.CRITICAL]],
                "estimated_effort": "High"
            })

        # Step 2: High priority issues
        if by_severity[IssueSeverity.HIGH]:
            repair_steps.append({
                "step": 2,
                "priority": "HIGH",
                "title": "Fix High Priority Issues",
                "description": "Resolve issues with significant impact",
                "findings": [f.issue_id for f in by_severity[IssueSeverity.HIGH]],
                "estimated_effort": "Medium"
            })

        # Step 3: Optimization
        if by_severity[IssueSeverity.MEDIUM]:
            repair_steps.append({
                "step": 3,
                "priority": "MEDIUM",
                "title": "Optimize Model",
                "description": "Address medium priority issues",
                "findings": [f.issue_id for f in by_severity[IssueSeverity.MEDIUM]],
                "estimated_effort": "Low"
            })

        repair_plan = {
            "total_steps": len(repair_steps),
            "estimated_total_effort": self._estimate_total_effort(findings),
            "steps": repair_steps,
            "success_criteria": self._define_success_criteria(findings),
            "resources": [
                "Horizon X5 BPU User Guide",
                "Diagnostic Knowledge Base",
                "Interactive Repair Guide"
            ]
        }

        return repair_plan

    def _estimate_total_effort(self, findings: List[DiagnosticFinding]) -> str:
        """Estimate total repair effort"""
        critical_count = len([f for f in findings if f.severity == IssueSeverity.CRITICAL])
        high_count = len([f for f in findings if f.severity == IssueSeverity.HIGH])
        medium_count = len([f for f in findings if f.severity == IssueSeverity.MEDIUM])

        if critical_count > 0:
            return "2-3 days (Critical issues present)"
        elif high_count > 3:
            return "1-2 days (Multiple high-priority issues)"
        elif high_count > 0:
            return "4-8 hours (Few high-priority issues)"
        elif medium_count > 5:
            return "2-4 hours (Many medium issues)"
        else:
            return "1-2 hours (Minor optimizations)"

    def _define_success_criteria(self, findings: List[DiagnosticFinding]) -> List[str]:
        """Define criteria for successful repair"""
        criteria = [
            "All CRITICAL issues resolved",
            "All HIGH priority issues addressed",
            "Model passes validation",
            "Conversion completes successfully"
        ]

        if not findings:
            criteria = ["No issues found - model is optimal"]

        return criteria

    def _calculate_overall_health(self, findings: List[DiagnosticFinding]) -> float:
        """
        Calculate overall model health score.

        Args:
            findings: List of diagnostic findings

        Returns:
            Health score (0.0 - 1.0, higher is better)
        """
        if not findings:
            return 1.0

        # Weight by severity
        severity_weights = {
            IssueSeverity.CRITICAL: 0.4,
            IssueSeverity.HIGH: 0.25,
            IssueSeverity.MEDIUM: 0.15,
            IssueSeverity.LOW: 0.1,
            IssueSeverity.INFO: 0.05
        }

        total_weight = 0
        weighted_issues = 0

        for finding in findings:
            weight = severity_weights.get(finding.severity, 0.1)
            total_weight += weight
            weighted_issues += weight * (1.0 - finding.confidence)

        # Calculate health score
        if total_weight == 0:
            return 1.0

        issue_penalty = weighted_issues / total_weight
        health_score = max(0.0, min(1.0, 1.0 - issue_penalty))

        return health_score

    def get_repair_guidance(self, finding: DiagnosticFinding) -> Dict[str, Any]:
        """
        Get detailed repair guidance for a specific finding.

        Args:
            finding: Diagnostic finding

        Returns:
            Repair guidance dictionary
        """
        # Get repair steps from repair guide
        steps = self.repair_guide.generate_repair_steps(finding.category.value)

        # Search knowledge base for related issues
        knowledge = self.knowledge_base.search_solutions(finding.category.value)

        return {
            "issue_id": finding.issue_id,
            "category": finding.category.value,
            "severity": finding.severity.value,
            "description": finding.description,
            "repair_steps": steps,
            "knowledge_base_matches": knowledge,
            "suggestions": finding.suggestions,
            "estimated_fix_time": self._estimate_fix_time(finding),
            "difficulty": self._assess_fix_difficulty(finding)
        }

    def _estimate_fix_time(self, finding: DiagnosticFinding) -> str:
        """Estimate time to fix a finding"""
        time_estimates = {
            IssueSeverity.CRITICAL: "2-4 hours",
            IssueSeverity.HIGH: "1-2 hours",
            IssueSeverity.MEDIUM: "30-60 minutes",
            IssueSeverity.LOW: "15-30 minutes",
            IssueSeverity.INFO: "5-15 minutes"
        }

        return time_estimates.get(finding.severity, "30 minutes")

    def _assess_fix_difficulty(self, finding: DiagnosticFinding) -> str:
        """Assess difficulty of fixing a finding"""
        difficulties = {
            IssueCategory.COMPATIBILITY: "Medium",
            IssueCategory.DYNAMIC_SHAPE: "Low",
            IssueCategory.STRUCTURE: "Medium",
            IssueCategory.NUMERICAL: "High",
            IssueCategory.PERFORMANCE: "High"
        }

        base_difficulty = difficulties.get(finding.category, "Medium")

        # Adjust based on confidence
        if finding.confidence < 0.5:
            base_difficulty += " (Low confidence diagnosis)"

        return base_difficulty

    def export_diagnostic_report(self,
                                result: DiagnosticResult,
                                output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Export diagnostic report to structured format.

        Args:
            result: DiagnosticResult
            output_path: Optional path to save report

        Returns:
            Dictionary with diagnostic report
        """
        report = {
            "model_name": result.model_name,
            "timestamp": result.timestamp,
            "overall_health": result.overall_health,
            "total_issues": result.total_issues,
            "critical_issues": result.critical_issues,
            "root_causes": result.root_causes,
            "recommendations": result.recommendations,
            "findings": [
                {
                    "issue_id": f.issue_id,
                    "category": f.category.value,
                    "severity": f.severity.value,
                    "description": f.description,
                    "location": f.location,
                    "confidence": f.confidence,
                    "evidence": f.evidence,
                    "suggestions": f.suggestions
                }
                for f in result.findings
            ],
            "repair_plan": result.repair_plan
        }

        if output_path:
            try:
                import json
                with open(output_path, 'w') as f:
                    json.dump(report, f, indent=2)
                logger.info(f"Diagnostic report exported to: {output_path}")
            except Exception as e:
                logger.error(f"Failed to export diagnostic report: {e}")

        return report

