"""
Model Validation and Compatibility Checking

This package provides validation capabilities for ONNX models:
- Operator support verification (Story 2.1.2)
- ONNX version compatibility (Story 2.1.2)
- Shape compatibility validation (Story 2.1.2)
- Precision support checking (Story 2.1.2)

Story 2.5 - ONNX Model Validation and Preprocessing:

AC1: Model Structure Validation
- Dynamic shape validation
- Operator dependency analysis
- Structure integrity checking
- Deep compatibility analysis

AC2: Intelligent Preprocessing Optimization
- Intelligent optimization strategies
- Strategy recommendation system

AC3: Five-Dimensional Quality Assurance
- Quality scoring system
- Multi-dimensional assessment

AC4: Intelligent Diagnosis and Repair
- Diagnostic engine
- Knowledge base
- Repair guidance

AC5: Comprehensive Verification Reporting
- Multi-format report generation
- Integrated analysis across AC1-AC4
"""

from .compatibility import (
    CompatibilityChecker,
    CompatibilityResult,
    FullCompatibilityResult,
    CompatibilityLevel
)

# Story 2.5 - AC1: Model Structure Validation
from .dynamic_shape_handler import DynamicShapeHandler
from .structure_validator import StructureValidator
from .compatibility_analyzer import CompatibilityAnalyzer
from .operator_dependency_analyzer import (
    OperatorDependencyAnalyzer,
    DependencyAnalysisResult,
    OperatorNode
)
from .comprehensive_validator import (
    ComprehensiveValidator,
    ComprehensiveValidationReport
)

# Story 2.5 - AC2: Intelligent Preprocessing Optimization
from ..preprocessing.enhanced.intelligent_optimizer import IntelligentOptimizer
from ..preprocessing.enhanced.strategy_recommender import StrategyRecommender

# Story 2.5 - AC3: Five-Dimensional Quality Assurance
from .quality_scorer import QualityScorer

# Story 2.5 - AC4: Intelligent Diagnosis and Repair
from ..diagnostics.diagnostic_engine import DiagnosticEngine
from ..diagnostics.knowledge_base import DiagnosticKnowledgeBase
from ..diagnostics.repair_guide import RepairGuide

# Story 2.5 - AC5: Comprehensive Verification Reporting
from .comprehensive_verification_reporter import (
    ComprehensiveVerificationReporter,
    ComprehensiveVerificationResult,
    AC1Results,
    AC2Results,
    AC3Results,
    AC4Results,
    ReportFormat,
    ReportStatus
)

# Story 2.5 - AC6: Model Quality Grading and Alerting
from .quality_grader import (
    QualityGrader,
    ModelQualityGrade,
    QualityGrade,
    RiskLevel,
    QualityMetrics,
    GradeFactors,
    RiskAssessment,
    PredictiveAnalysis,
    QualityAlert,
    QualityTrend
)

__all__ = [
    "CompatibilityChecker",
    "CompatibilityResult",
    "FullCompatibilityResult",
    "CompatibilityLevel",
    # AC1: Model Structure Validation
    "DynamicShapeHandler",
    "StructureValidator",
    "CompatibilityAnalyzer",
    "OperatorDependencyAnalyzer",
    "DependencyAnalysisResult",
    "OperatorNode",
    "ComprehensiveValidator",
    "ComprehensiveValidationReport",
    # AC2: Intelligent Preprocessing Optimization
    "IntelligentOptimizer",
    "StrategyRecommender",
    # AC3: Five-Dimensional Quality Assurance
    "QualityScorer",
    # AC4: Intelligent Diagnosis and Repair
    "DiagnosticEngine",
    "DiagnosticKnowledgeBase",
    "RepairGuide",
    # AC5: Comprehensive Verification Reporting
    "ComprehensiveVerificationReporter",
    "ComprehensiveVerificationResult",
    "AC1Results",
    "AC2Results",
    "AC3Results",
    "AC4Results",
    "ReportFormat",
    "ReportStatus",
    # AC6: Model Quality Grading and Alerting
    "QualityGrader",
    "ModelQualityGrade",
    "QualityGrade",
    "RiskLevel",
    "QualityMetrics",
    "GradeFactors",
    "RiskAssessment",
    "PredictiveAnalysis",
    "QualityAlert",
    "QualityTrend"
]
