"""
Comprehensive Model Validator

Integrates all validation capabilities from Story 2.5 including:
- Dynamic shape validation (Story 2.1.2 integration)
- Structure validation with dependency analysis
- Five-dimensional quality assurance
- Intelligent preprocessing optimization

This validator provides a unified interface for all validation operations.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from ..models.onnx_model import ONNXModel, TensorInfo
from .dynamic_shape_handler import (
    DynamicShapeHandler,
    DynamicShapeValidationResult
)
from .structure_validator import (
    StructureValidator,
    StructureValidationResult
)
from .compatibility_analyzer import (
    CompatibilityAnalyzer,
    CompatibilityAnalysisResult
)
from .quality_scorer import (
    QualityScorer,
    QualityScoringResult
)

logger = logging.getLogger(__name__)


@dataclass
class ComprehensiveValidationReport:
    """
    Comprehensive validation report combining all validation dimensions.

    This represents the five-dimensional validation system:
    1. Structure Integrity
    2. Numerical Validity
    3. Compatibility (Horizon X5 BPU)
    4. Performance Benchmark
    5. Conversion Readiness
    """
    model_name: str
    is_valid: bool
    overall_confidence: float  # 0.0 - 1.0

    # Five-dimensional results
    structure_validation: Optional[StructureValidationResult] = None
    dynamic_shape_validation: Optional[DynamicShapeValidationResult] = None
    compatibility_analysis: Optional[CompatibilityAnalysisResult] = None
    quality_scoring: Optional[QualityScoringResult] = None
    conversion_readiness: Optional[Dict[str, Any]] = None

    # Metadata integration
    metadata_extracted: Optional[Dict[str, Any]] = None

    # AC2: Intelligent Preprocessing Optimization
    intelligent_optimization: Optional[Dict[str, Any]] = None
    preprocessing_recommendations: Optional[List[Dict[str, Any]]] = None
    optimization_results: Optional[List[Dict[str, Any]]] = None

    # Summary
    total_issues: int = 0
    total_warnings: int = 0
    critical_issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Initialize derived fields"""
        self.total_issues = len(self.critical_issues)
        self.total_warnings = len(self.warnings)
        if self.preprocessing_recommendations is None:
            self.preprocessing_recommendations = []
        if self.optimization_results is None:
            self.optimization_results = []

    def get_summary(self) -> str:
        """Get a human-readable summary of the validation report"""
        summary_lines = [
            f"Comprehensive Validation Report for: {self.model_name}",
            f"  Overall Status: {'✅ VALID' if self.is_valid else '❌ INVALID'}",
            f"  Confidence: {self.overall_confidence:.1%}",
            f"  Issues: {self.total_issues}, Warnings: {self.total_warnings}",
            ""
        ]

        # Add dimensional scores if available
        if self.quality_scoring:
            summary_lines.append("Quality Scores:")
            for score in self.quality_scoring.scores:
                summary_lines.append(f"  - {score.dimension}: {score.score:.1%} ({score.description})")
            summary_lines.append(f"  Overall Grade: {self.quality_scoring.grade}")

        if self.critical_issues:
            summary_lines.append("\nCritical Issues:")
            for issue in self.critical_issues[:5]:  # Show first 5
                summary_lines.append(f"  - {issue}")

        if self.recommendations:
            summary_lines.append("\nRecommendations:")
            for rec in self.recommendations[:5]:  # Show first 5
                summary_lines.append(f"  - {rec}")

        return "\n".join(summary_lines)


class ComprehensiveValidator:
    """
    Comprehensive validator integrating all validation capabilities.

    This is the main entry point for Story 2.5's five-dimensional validation system.
    It integrates:
    - Story 2.1.2's ModelMetadataExtractor for metadata extraction
    - DynamicShapeHandler for dynamic shape validation
    - StructureValidator for structure and dependency analysis
    - CompatibilityAnalyzer for Horizon X5 BPU compatibility
    - QualityScorer for multi-dimensional quality scoring

    The validator performs:
    1. Deep metadata extraction and analysis
    2. Dynamic shape validation and optimization
    3. Structure validation with dependency analysis
    4. Comprehensive compatibility analysis
    5. Quality scoring across multiple dimensions
    6. Conversion readiness assessment
    """

    def __init__(self):
        """Initialize the ComprehensiveValidator with all sub-validators"""
        logger.info("Initializing ComprehensiveValidator")

        # Initialize all sub-validators
        # Note: metadata_extractor is lazily loaded in _extract_deep_metadata
        self.metadata_extractor = None  # Lazy loaded
        self.dynamic_shape_handler = DynamicShapeHandler()
        self.structure_validator = StructureValidator()
        self.compatibility_analyzer = CompatibilityAnalyzer()
        self.quality_scorer = QualityScorer()

        # AC2: Intelligent Preprocessing Optimization
        from ..preprocessing.enhanced.intelligent_optimizer import IntelligentOptimizer
        from ..preprocessing.enhanced.strategy_recommender import StrategyRecommender
        self.intelligent_optimizer = IntelligentOptimizer()
        self.strategy_recommender = StrategyRecommender()

        logger.info("All validators initialized")
        logger.info("AC2 Intelligent Preprocessing Optimization initialized")

    def validate_model(self,
                      model: ONNXModel,
                      deep_analysis: bool = True) -> ComprehensiveValidationReport:
        """
        Perform comprehensive validation of an ONNX model.

        This method integrates all validation capabilities and provides
        a unified validation report.

        Args:
            model: ONNXModel instance to validate
            deep_analysis: If True, performs deep analysis across all dimensions

        Returns:
            ComprehensiveValidationReport with detailed validation results
        """
        logger.info(f"Starting comprehensive validation for model: {model}")

        # Step 1: Deep metadata extraction (Story 2.1.2 integration)
        logger.info("Step 1: Extracting and analyzing metadata...")
        metadata = self._extract_deep_metadata(model)

        # Step 2: Dynamic shape validation
        logger.info("Step 2: Validating dynamic shapes...")
        dynamic_result = self._validate_dynamic_shapes(model, metadata)

        # Step 3: Structure validation
        logger.info("Step 3: Validating structure and dependencies...")
        structure_result = self.structure_validator.validate_structure(model)

        # Step 4: Compatibility analysis
        logger.info("Step 4: Analyzing Horizon X5 BPU compatibility...")
        compatibility_result = self.compatibility_analyzer.analyze_compatibility(model)

        # Step 5: Quality scoring
        logger.info("Step 5: Scoring quality across dimensions...")
        quality_result = self.quality_scorer.score_quality(model)

        # Step 6: Conversion readiness assessment
        logger.info("Step 6: Assessing conversion readiness...")
        readiness_result = self._assess_conversion_readiness(
            dynamic_result, structure_result, compatibility_result, quality_result
        )

        # Step 6.5: AC2 - Intelligent Preprocessing Optimization
        logger.info("Step 6.5: Running AC2 intelligent preprocessing optimization...")
        optimization_result = self._run_intelligent_optimization(model)
        readiness_result['ac2_optimization'] = optimization_result

        # Step 7: Compile comprehensive report
        report = self._compile_comprehensive_report(
            model=model,
            metadata=metadata,
            dynamic_result=dynamic_result,
            structure_result=structure_result,
            compatibility_result=compatibility_result,
            quality_result=quality_result,
            readiness_result=readiness_result
        )

        logger.info(f"Comprehensive validation completed: {report.is_valid} "
                   f"(Confidence: {report.overall_confidence:.1%})")
        return report

    def _extract_deep_metadata(self, model: ONNXModel) -> Dict[str, Any]:
        """
        Extract deep metadata using Story 2.1.2's ModelMetadataExtractor.

        Args:
            model: ONNXModel instance

        Returns:
            Dictionary containing extracted metadata
        """
        metadata = {}

        # Lazy import to avoid module loading issues
        try:
            from ..loaders.metadata_extractor import ModelMetadataExtractor
            self.metadata_extractor = ModelMetadataExtractor()
        except ImportError as e:
            logger.warning(f"Could not import ModelMetadataExtractor: {e}")
            metadata["error"] = "ModelMetadataExtractor not available"
            return metadata

        try:
            # Extract input tensors
            input_tensors = self.metadata_extractor.extract_input_tensors(model)
            metadata["input_tensors"] = [
                {
                    "name": t.name,
                    "shape": t.shape,
                    "dtype": t.dtype,
                    "has_dynamic": any(dim == -1 or dim == 0 for dim in t.shape)
                }
                for t in input_tensors
            ]

            # Extract output tensors
            output_tensors = self.metadata_extractor.extract_output_tensors(model)
            metadata["output_tensors"] = [
                {
                    "name": t.name,
                    "shape": t.shape,
                    "dtype": t.dtype,
                    "has_dynamic": any(dim == -1 or dim == 0 for dim in t.shape)
                }
                for t in output_tensors
            ]

            # Extract operators
            operators = self.metadata_extractor.extract_operators(model)
            metadata["operators"] = [
                {
                    "op_type": op.op_type,
                    "domain": op.domain,
                    "input_count": len(op.inputs),
                    "output_count": len(op.outputs)
                }
                for op in operators
            ]

            # Extract version info
            version_info = self.metadata_extractor.extract_version_info(model)
            metadata["version_info"] = {
                "onnx_version": version_info.onnx_version,
                "opset_version": version_info.opset_version,
                "producer_name": version_info.producer_name
            }

            # Calculate statistics
            metadata["statistics"] = {
                "total_input_tensors": len(input_tensors),
                "total_output_tensors": len(output_tensors),
                "total_operators": len(operators),
                "dynamic_input_count": sum(1 for t in input_tensors if any(dim == -1 or dim == 0 for dim in t.shape)),
                "dynamic_output_count": sum(1 for t in output_tensors if any(dim == -1 or dim == 0 for dim in t.shape)),
                "unique_operator_types": len(set(op.op_type for op in operators))
            }

            logger.info(f"Deep metadata extracted: {len(operators)} operators, "
                       f"{len(input_tensors)} inputs, {len(output_tensors)} outputs")

        except Exception as e:
            logger.error(f"Failed to extract deep metadata: {e}")
            metadata["error"] = str(e)

        return metadata

    def _validate_dynamic_shapes(self,
                                model: ONNXModel,
                                metadata: Dict[str, Any]) -> DynamicShapeValidationResult:
        """
        Validate dynamic shapes using metadata from Story 2.1.2.

        Args:
            model: ONNXModel instance
            metadata: Extracted metadata

        Returns:
            DynamicShapeValidationResult
        """
        # Convert metadata back to TensorInfo objects
        input_tensors = []
        if "input_tensors" in metadata:
            for t_data in metadata["input_tensors"]:
                tensor_info = TensorInfo(
                    name=t_data["name"],
                    shape=t_data["shape"],
                    dtype=t_data["dtype"]
                )
                input_tensors.append(tensor_info)

        # Use dynamic shape handler
        return self.dynamic_shape_handler.validate_dynamic_shapes(
            model=model,
            input_tensors=input_tensors
        )

    def _assess_conversion_readiness(self,
                                    dynamic_result: DynamicShapeValidationResult,
                                    structure_result: StructureValidationResult,
                                    compatibility_result: CompatibilityAnalysisResult,
                                    quality_result: QualityScoringResult) -> Dict[str, Any]:
        """
        Assess overall conversion readiness based on all validation results.

        Args:
            dynamic_result: Dynamic shape validation result
            structure_result: Structure validation result
            compatibility_result: Compatibility analysis result
            quality_result: Quality scoring result

        Returns:
            Dictionary with conversion readiness assessment
        """
        readiness = {
            "ready": True,
            "confidence": 0.0,
            "risk_level": "low",  # low, medium, high
            "blocking_issues": [],
            "concerns": [],
            "recommendations": []
        }

        # Check for blocking issues
        if not structure_result.is_valid:
            readiness["ready"] = False
            readiness["blocking_issues"].extend(structure_result.issues)

        if dynamic_result.has_unsupported_dynamic_dims:
            readiness["ready"] = False
            readiness["blocking_issues"].append("Unsupported dynamic dimensions detected")

        if not compatibility_result.compatible:
            readiness["ready"] = False
            readiness["blocking_issues"].extend(compatibility_result.issues)

        # Calculate confidence score
        scores = []
        if quality_result:
            scores.append(quality_result.overall_score)

        if structure_result:
            structure_score = max(0.0, 1.0 - len(structure_result.issues) * 0.1)
            scores.append(structure_score)

        if dynamic_result:
            dynamic_score = 1.0 if dynamic_result.is_valid else 0.5
            scores.append(dynamic_score)

        if compatibility_result:
            scores.append(compatibility_result.confidence_score)

        readiness["confidence"] = sum(scores) / len(scores) if scores else 0.0

        # Determine risk level
        if len(readiness["blocking_issues"]) > 0:
            readiness["risk_level"] = "high"
        elif readiness["confidence"] < 0.7:
            readiness["risk_level"] = "medium"
        else:
            readiness["risk_level"] = "low"

        # Add recommendations
        if dynamic_result.warnings:
            readiness["recommendations"].extend(dynamic_result.warnings[:3])

        if quality_result and quality_result.recommendations:
            readiness["recommendations"].extend(quality_result.recommendations[:3])

        logger.info(f"Conversion readiness: {readiness['ready']} "
                   f"(confidence: {readiness['confidence']:.1%}, risk: {readiness['risk_level']})")

        return readiness

    def _compile_comprehensive_report(self,
                                     model: ONNXModel,
                                     metadata: Dict[str, Any],
                                     dynamic_result: DynamicShapeValidationResult,
                                     structure_result: StructureValidationResult,
                                     compatibility_result: CompatibilityAnalysisResult,
                                     quality_result: QualityScoringResult,
                                     readiness_result: Dict[str, Any]) -> ComprehensiveValidationReport:
        """
        Compile all validation results into a comprehensive report.

        Args:
            model: ONNXModel instance
            metadata: Extracted metadata
            dynamic_result: Dynamic shape validation result
            structure_result: Structure validation result
            compatibility_result: Compatibility analysis result
            quality_result: Quality scoring result
            readiness_result: Conversion readiness assessment

        Returns:
            ComprehensiveValidationReport
        """
        # Collect all issues and warnings
        all_issues = []
        all_warnings = []

        if structure_result:
            all_issues.extend(structure_result.issues)
            all_warnings.extend(structure_result.warnings)

        if dynamic_result.errors:
            all_issues.extend(dynamic_result.errors)
        if dynamic_result.warnings:
            all_warnings.extend(dynamic_result.warnings)

        if compatibility_result and compatibility_result.issues:
            all_issues.extend(compatibility_result.issues)
        if compatibility_result and compatibility_result.warnings:
            all_warnings.extend(compatibility_result.warnings)

        # Determine overall validity
        is_valid = (
            readiness_result.get("ready", False) and
            len(all_issues) == 0
        )

        # Calculate overall confidence
        overall_confidence = readiness_result.get("confidence", 0.0)

        # Model name
        model_name = model.model_path.name if model.model_path else "Unknown Model"

        report = ComprehensiveValidationReport(
            model_name=model_name,
            is_valid=is_valid,
            overall_confidence=overall_confidence,
            structure_validation=structure_result,
            dynamic_shape_validation=dynamic_result,
            compatibility_analysis=compatibility_result,
            quality_scoring=quality_result,
            conversion_readiness=readiness_result,
            metadata_extracted=metadata,
            critical_issues=all_issues,
            warnings=all_warnings,
            recommendations=readiness_result.get("recommendations", [])
        )

        return report

    def validate_and_export_report(self,
                                   model: ONNXModel,
                                   output_path: Optional[str] = None) -> ComprehensiveValidationReport:
        """
        Validate model and optionally export report to file.

        Args:
            model: ONNXModel instance to validate
            output_path: Optional path to save the report

        Returns:
            ComprehensiveValidationReport
        """
        # Perform validation
        report = self.validate_model(model)

        # Export to file if requested
        if output_path:
            try:
                import json
                report_dict = {
                    "model_name": report.model_name,
                    "is_valid": report.is_valid,
                    "overall_confidence": report.overall_confidence,
                    "total_issues": report.total_issues,
                    "total_warnings": report.total_warnings,
                    "critical_issues": report.critical_issues,
                    "warnings": report.warnings,
                    "recommendations": report.recommendations
                }

                with open(output_path, 'w') as f:
                    json.dump(report_dict, f, indent=2)

                logger.info(f"Validation report exported to: {output_path}")

            except Exception as e:
                logger.error(f"Failed to export report: {e}")

        return report

    def _run_intelligent_optimization(self, model: ONNXModel) -> Dict[str, Any]:
        """
        Run AC2 intelligent preprocessing optimization.

        This method:
        1. Analyzes model characteristics and recommends preprocessing strategies
        2. Performs intelligent parameter optimization
        3. Returns optimization results and recommendations

        Args:
            model: ONNXModel instance

        Returns:
            Dictionary containing optimization results, recommendations, and metrics
        """
        logger.info("Starting AC2 intelligent preprocessing optimization")

        try:
            # Step 1: Get strategy recommendations
            logger.info("Analyzing model and recommending preprocessing strategies...")
            strategy_result = self.strategy_recommender.recommend_strategy(model)
            preprocessing_recommendations = []

            if strategy_result and strategy_result.recommendations:
                for rec in strategy_result.recommendations:
                    preprocessing_recommendations.append({
                        "strategy": rec.strategy.value,
                        "priority": rec.priority,
                        "confidence": rec.confidence,
                        "description": rec.description,
                        "parameters": rec.parameters,
                        "expected_improvement": rec.expected_improvement,
                        "reasoning": rec.reasoning
                    })

            # Step 2: Perform optimization if recommendations exist
            optimization_results = []
            best_improvement = 0.0

            if preprocessing_recommendations:
                logger.info(f"Found {len(preprocessing_recommendations)} preprocessing recommendations")

                # Try to optimize with Bayesian optimization
                try:
                    from ..preprocessing.pipeline import PreprocessingConfig
                    from ..preprocessing.enhanced.intelligent_optimizer import OptimizationStrategy

                    # Create a base configuration
                    best_config = PreprocessingConfig()

                    # Perform optimization
                    optimization_result = self.intelligent_optimizer.optimize_preprocessing(
                        model=model,
                        current_config=best_config,
                        strategy=OptimizationStrategy.BAYESIAN,
                        max_iterations=50
                    )

                    optimization_results.append({
                        "strategy": optimization_result.strategy.value,
                        "best_score": optimization_result.best_score,
                        "improvement_percentage": optimization_result.improvement_percentage,
                        "iterations": optimization_result.iterations,
                        "model_type": optimization_result.model_type.value
                    })

                    best_improvement = optimization_result.improvement_percentage

                    logger.info(f"Optimization completed: {best_improvement:.2f}% improvement")

                except Exception as opt_e:
                    logger.warning(f"Optimization failed: {opt_e}")
                    optimization_results.append({
                        "error": str(opt_e),
                        "optimization_applied": False
                    })
            else:
                logger.info("No preprocessing recommendations available")

            # Compile results
            optimization_summary = {
                "model_type": getattr(strategy_result, 'model_type', 'generic') if strategy_result else 'unknown',
                "total_recommendations": len(preprocessing_recommendations),
                "optimization_applied": len(optimization_results) > 0,
                "best_improvement": best_improvement,
                "recommendations": preprocessing_recommendations,
                "results": optimization_results,
                "success": True
            }

            logger.info(f"AC2 optimization completed: {len(preprocessing_recommendations)} recommendations, "
                       f"{best_improvement:.2f}% best improvement")

            return optimization_summary

        except Exception as e:
            logger.error(f"AC2 intelligent optimization failed: {e}")
            return {
                "error": str(e),
                "success": False,
                "optimization_applied": False,
                "total_recommendations": 0,
                "best_improvement": 0.0
            }

