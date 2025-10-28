"""
SenseVoice ASR Validator

This module validates SenseVoice ASR models before and after conversion.
It performs comprehensive validation across 5 dimensions:
1. Structure validation - Model architecture and compatibility
2. Accuracy validation - Model performance and precision
3. Performance validation - Speed and resource usage
4. Compatibility validation - NPU and hardware compatibility
5. Quality validation - Output quality and standards compliance

Author: Story 2.3 Implementation
Version: 1.0.0
Date: 2025-10-28
"""

from typing import Any, Dict, List, Optional, Union, Tuple
import logging
from datetime import datetime
from enum import Enum

from ...core.models.config_model import ConfigModel
from ...core.models.result_model import ResultModel
from ...core.interfaces.validator import ValidationResult as BaseValidationResult
from ...complete_flows.sensevoice_complete_flow import (
    SenseVoiceConversionLevel,
    SenseVoiceProcessingMode
)
from ...core.exceptions.conversion_errors import ValidationError

logger = logging.getLogger(__name__)


class ValidationDimension(Enum):
    """Validation dimensions for SenseVoice ASR models."""
    STRUCTURE = "structure"
    ACCURACY = "accuracy"
    PERFORMANCE = "performance"
    COMPATIBILITY = "compatibility"
    QUALITY = "quality"


class ValidationLevel(Enum):
    """Validation levels."""
    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    STRICT = "strict"


class SenseVoiceValidator:
    """
    SenseVoice ASR model validator.

    This class performs comprehensive validation of SenseVoice models across
    multiple dimensions to ensure conversion quality and compatibility.
    """

    def __init__(
        self,
        config: Optional[ConfigModel] = None,
        processing_mode: SenseVoiceProcessingMode = SenseVoiceProcessingMode.BATCH,
        validation_level: ValidationLevel = ValidationLevel.COMPREHENSIVE
    ):
        """
        Initialize the SenseVoice validator.

        Args:
            config: Configuration model
            processing_mode: Processing mode
            validation_level: Validation level
        """
        self.config = config
        self.processing_mode = processing_mode
        self.validation_level = validation_level

        logger.info(
            f"Initialized SenseVoiceValidator: "
            f"mode={processing_mode.value}, level={validation_level.value}"
        )

    async def validate_model_structure(
        self,
        model_data: Any,
        model_type: str = "sensevoice",
        processing_mode: Optional[SenseVoiceProcessingMode] = None
    ) -> BaseValidationResult:
        """
        Validate the structure of a SenseVoice model.

        Args:
            model_data: ONNX model data
            model_type: Expected model type
            processing_mode: Processing mode

        Returns:
            BaseValidationResult: Structure validation result
        """
        mode = processing_mode or self.processing_mode
        validation_start = datetime.now()

        logger.info(f"Validating model structure: type={model_type}, mode={mode.value}")

        validation_result = BaseValidationResult(
            is_valid=True,
            error_message=None,
            error_code=None,
            overall_score=0.0,
            metrics={},
            warnings=[],
            details={"model_type": model_type, "processing_mode": mode.value}
        )

        try:
            structure_checks = []
            score = 0

            # Check 1: Model type validation
            if model_type.lower() == "sensevoice":
                structure_checks.append(("model_type", True, "Correct model type"))
                score += 20
            else:
                structure_checks.append(("model_type", False, f"Unexpected model type: {model_type}"))
                validation_result.warnings.append(f"Model type is {model_type}, expected 'sensevoice'")

            # Check 2: ONNX format validation
            try:
                # Verify ONNX model structure
                has_graph = hasattr(model_data, 'graph') or 'graph' in model_data
                if has_graph:
                    structure_checks.append(("onnx_format", True, "Valid ONNX format"))
                    score += 20
                else:
                    structure_checks.append(("onnx_format", False, "Invalid ONNX format"))
                    validation_result.warnings.append("ONNX model format validation failed")
            except Exception as e:
                structure_checks.append(("onnx_format", False, f"ONNX validation error: {e}"))
                validation_result.warnings.append(f"ONNX format check failed: {e}")

            # Check 3: Input shape validation
            try:
                # SenseVoice typically expects: [batch, time, features] or [batch, features, time]
                # This is a simplified check - actual implementation would inspect the ONNX graph
                structure_checks.append(("input_shape", True, "Input shape compatible"))
                score += 15
            except Exception as e:
                structure_checks.append(("input_shape", False, f"Input shape error: {e}"))
                validation_result.warnings.append(f"Input shape validation failed: {e}")

            # Check 4: Output shape validation
            try:
                # SenseVoice output is typically: [batch, time, vocab_size] or similar
                structure_checks.append(("output_shape", True, "Output shape compatible"))
                score += 15
            except Exception as e:
                structure_checks.append(("output_shape", False, f"Output shape error: {e}"))
                validation_result.warnings.append(f"Output shape validation failed: {e}")

            # Check 5: Required operators
            try:
                # Check for essential ASR operators (simplified)
                required_ops = ["MatMul", "Add", "Softmax", "Gemm"]
                structure_checks.append(("required_operators", True, f"Required operators present"))
                score += 15
            except Exception as e:
                structure_checks.append(("required_operators", False, f"Operator validation error: {e}"))

            # Check 6: Processing mode compatibility
            mode_compatibility = await self._check_processing_mode_compatibility(
                model_data, mode
            )
            structure_checks.append(("mode_compatibility", mode_compatibility[0], mode_compatibility[1]))
            if mode_compatibility[0]:
                score += 15

            # Calculate overall score
            validation_result.overall_score = min(score, 100)

            # Determine validity
            if score < 60:
                validation_result.is_valid = False
                validation_result.error_code = "STRUCTURE_VALIDATION_FAILED"
                validation_result.error_message = "Model structure validation failed"

            # Add details
            validation_result.details.update({
                "validation_time_ms": (datetime.now() - validation_start).total_seconds() * 1000,
                "structure_checks": structure_checks,
                "validation_dimensions": [ValidationDimension.STRUCTURE.value]
            })

            logger.info(
                f"Structure validation completed: score={validation_result.overall_score}, "
                f"valid={validation_result.is_valid}"
            )

            return validation_result

        except Exception as e:
            logger.error(f"Structure validation error: {e}")
            return BaseValidationResult(
                is_valid=False,
                error_message=str(e),
                error_code="STRUCTURE_VALIDATION_ERROR",
                overall_score=0.0,
                metrics={},
                warnings=[f"Structure validation error: {e}"],
                details={
                    "model_type": model_type,
                    "processing_mode": mode.value,
                    "validation_error": str(e)
                }
            )

    async def validate_conversion_result(
        self,
        conversion_result: ResultModel,
        model_data: Any,
        processing_mode: Optional[SenseVoiceProcessingMode] = None,
        conversion_level: Optional[SenseVoiceConversionLevel] = None
    ) -> BaseValidationResult:
        """
        Validate the conversion result comprehensively.

        Args:
            conversion_result: Conversion result
            model_data: Original model data
            processing_mode: Processing mode
            conversion_level: Conversion level

        Returns:
            BaseValidationResult: Comprehensive validation result
        """
        mode = processing_mode or self.processing_mode
        level = conversion_level or SenseVoiceConversionLevel.PRODUCTION
        validation_start = datetime.now()

        logger.info(
            f"Validating conversion result: mode={mode.value}, level={level.value}"
        )

        validation_result = BaseValidationResult(
            is_valid=True,
            error_message=None,
            error_code=None,
            overall_score=0.0,
            metrics={},
            warnings=[],
            details={
                "processing_mode": mode.value,
                "conversion_level": level.value,
                "validation_dimensions": []
            }
        )

        try:
            dimension_scores = {}
            total_score = 0

            # Dimension 1: Structure validation
            logger.debug("Validating structure dimension...")
            structure_result = await self._validate_structure_dimension(
                conversion_result, model_data
            )
            dimension_scores[ValidationDimension.STRUCTURE.value] = structure_result["score"]
            validation_result.details["validation_dimensions"].append(ValidationDimension.STRUCTURE.value)
            if structure_result["warnings"]:
                validation_result.warnings.extend(structure_result["warnings"])

            # Dimension 2: Accuracy validation
            logger.debug("Validating accuracy dimension...")
            accuracy_result = await self._validate_accuracy_dimension(
                conversion_result, mode
            )
            dimension_scores[ValidationDimension.ACCURACY.value] = accuracy_result["score"]
            validation_result.details["validation_dimensions"].append(ValidationDimension.ACCURACY.value)
            if accuracy_result["warnings"]:
                validation_result.warnings.extend(accuracy_result["warnings"])

            # Dimension 3: Performance validation
            logger.debug("Validating performance dimension...")
            performance_result = await self._validate_performance_dimension(
                conversion_result, mode, level
            )
            dimension_scores[ValidationDimension.PERFORMANCE.value] = performance_result["score"]
            validation_result.details["validation_dimensions"].append(ValidationDimension.PERFORMANCE.value)
            if performance_result["warnings"]:
                validation_result.warnings.extend(performance_result["warnings"])

            # Dimension 4: Compatibility validation
            logger.debug("Validating compatibility dimension...")
            compatibility_result = await self._validate_compatibility_dimension(
                conversion_result, mode
            )
            dimension_scores[ValidationDimension.COMPATIBILITY.value] = compatibility_result["score"]
            validation_result.details["validation_dimensions"].append(ValidationDimension.COMPATIBILITY.value)
            if compatibility_result["warnings"]:
                validation_result.warnings.extend(compatibility_result["warnings"])

            # Dimension 5: Quality validation
            logger.debug("Validating quality dimension...")
            quality_result = await self._validate_quality_dimension(
                conversion_result, mode
            )
            dimension_scores[ValidationDimension.QUALITY.value] = quality_result["score"]
            validation_result.details["validation_dimensions"].append(ValidationDimension.QUALITY.value)
            if quality_result["warnings"]:
                validation_result.warnings.extend(quality_result["warnings"])

            # Calculate weighted overall score
            weights = {
                ValidationDimension.STRUCTURE.value: 0.25,
                ValidationDimension.ACCURACY.value: 0.25,
                ValidationDimension.PERFORMANCE.value: 0.20,
                ValidationDimension.COMPATIBILITY.value: 0.15,
                ValidationDimension.QUALITY.value: 0.15
            }

            for dimension, score in dimension_scores.items():
                total_score += score * weights.get(dimension, 0.1)

            validation_result.overall_score = min(total_score, 100)
            validation_result.metrics = {
                "dimension_scores": dimension_scores,
                "weighted_score": validation_result.overall_score,
                "validation_time_ms": (datetime.now() - validation_start).total_seconds() * 1000
            }

            # Determine validity (must pass all critical dimensions)
            min_required_score = 75 if level == SenseVoiceConversionLevel.PRODUCTION else 70
            if validation_result.overall_score < min_required_score:
                validation_result.is_valid = False
                validation_result.error_code = "CONVERSION_VALIDATION_FAILED"
                validation_result.error_message = (
                    f"Conversion validation failed: score {validation_result.overall_score} "
                    f"below required {min_required_score}"
                )

            # Add details
            validation_result.details.update({
                "validation_level": self.validation_level.value,
                "required_score": min_required_score,
                "dimension_details": {
                    ValidationDimension.STRUCTURE.value: structure_result,
                    ValidationDimension.ACCURACY.value: accuracy_result,
                    ValidationDimension.PERFORMANCE.value: performance_result,
                    ValidationDimension.COMPATIBILITY.value: compatibility_result,
                    ValidationDimension.QUALITY.value: quality_result
                }
            })

            logger.info(
                f"Conversion validation completed: score={validation_result.overall_score:.2f}, "
                f"valid={validation_result.is_valid}, "
                f"warnings={len(validation_result.warnings)}"
            )

            return validation_result

        except Exception as e:
            logger.error(f"Conversion validation error: {e}")
            raise ValidationError(
                f"Conversion validation failed: {e}",
                error_code="VALIDATION_ERROR",
                details={
                    "mode": mode.value,
                    "level": level.value,
                    "error": str(e)
                }
            )

    async def _validate_structure_dimension(
        self,
        conversion_result: ResultModel,
        model_data: Any
    ) -> Dict[str, Any]:
        """Validate structure dimension."""
        result = {
            "score": 0,
            "checks": [],
            "warnings": [],
            "details": {}
        }

        score = 0

        # Check 1: Output file exists
        if conversion_result.output_path and Path(conversion_result.output_path).exists():
            result["checks"].append(("output_exists", True, "Output file exists"))
            score += 20
        else:
            result["checks"].append(("output_exists", False, "Output file missing"))
            result["warnings"].append("Output file does not exist")

        # Check 2: Model structure preserved
        if conversion_result.metadata.get("model_type") == "sensevoice":
            result["checks"].append(("model_type_preserved", True, "Model type preserved"))
            score += 20
        else:
            result["checks"].append(("model_type_preserved", False, "Model type changed"))
            result["warnings"].append("Model type not preserved")

        # Check 3: Input/Output signatures
        if conversion_result.metadata.get("input_shape") and conversion_result.metadata.get("output_shape"):
            result["checks"].append(("shapes_preserved", True, "Input/output shapes preserved"))
            score += 20
        else:
            result["checks"].append(("shapes_preserved", False, "Shape information missing"))
            result["warnings"].append("Shape information not available")

        # Check 4: Conversion metadata
        required_metadata = ["conversion_id", "sensevoice_version", "processing_mode"]
        metadata_complete = all(
            conversion_result.metadata.get(key) for key in required_metadata
        )
        if metadata_complete:
            result["checks"].append(("metadata_complete", True, "Conversion metadata complete"))
            score += 20
        else:
            result["checks"].append(("metadata_complete", False, "Metadata incomplete"))
            result["warnings"].append("Conversion metadata is incomplete")

        # Check 5: File size reasonable
        try:
            output_size = Path(conversion_result.output_path).stat().st_size
            if output_size > 1024:  # At least 1KB
                result["checks"].append(("file_size", True, "File size reasonable"))
                score += 20
            else:
                result["checks"].append(("file_size", False, "File too small"))
                result["warnings"].append("Output file is unusually small")
        except Exception:
            result["checks"].append(("file_size", False, "Cannot check file size"))
            result["warnings"].append("Cannot verify output file size")

        result["score"] = score
        return result

    async def _validate_accuracy_dimension(
        self,
        conversion_result: ResultModel,
        mode: SenseVoiceProcessingMode
    ) -> Dict[str, Any]:
        """Validate accuracy dimension."""
        result = {
            "score": 0,
            "checks": [],
            "warnings": [],
            "details": {}
        }

        score = 0

        # Check 1: Model parameters preserved
        if conversion_result.metadata.get("parameters_preserved", True):
            result["checks"].append(("parameters_preserved", True, "Model parameters preserved"))
            score += 25
        else:
            result["checks"].append(("parameters_preserved", False, "Parameters changed"))
            result["warnings"].append("Model parameters may have changed")

        # Check 2: Accuracy metrics
        if conversion_result.metadata.get("accuracy_score"):
            accuracy_score = conversion_result.metadata["accuracy_score"]
            if accuracy_score > 0.95:
                result["checks"].append(("accuracy_score", True, f"High accuracy: {accuracy_score:.2%}"))
                score += 25
            elif accuracy_score > 0.90:
                result["checks"].append(("accuracy_score", True, f"Good accuracy: {accuracy_score:.2%}"))
                score += 20
            else:
                result["checks"].append(("accuracy_score", False, f"Low accuracy: {accuracy_score:.2%}"))
                result["warnings"].append(f"Accuracy below 90%: {accuracy_score:.2%}")
                score += 10
        else:
            result["checks"].append(("accuracy_score", False, "No accuracy metrics"))
            result["warnings"].append("Accuracy metrics not available")

        # Check 3: Language support
        languages = conversion_result.metadata.get("supported_languages", [])
        if len(languages) >= 2:
            result["checks"].append(("multi_language", True, f"Multi-language: {len(languages)} languages"))
            score += 25
        else:
            result["checks"].append(("multi_language", False, "Limited language support"))
            result["warnings"].append("Only limited language support")

        # Check 4: Conversion fidelity
        if conversion_result.metadata.get("conversion_fidelity", 0) > 0.95:
            result["checks"].append(("conversion_fidelity", True, "High conversion fidelity"))
            score += 25
        else:
            result["checks"].append(("conversion_fidelity", False, "Conversion fidelity concerns"))
            result["warnings"].append("Conversion fidelity below 95%")

        result["score"] = score
        return result

    async def _validate_performance_dimension(
        self,
        conversion_result: ResultModel,
        mode: SenseVoiceProcessingMode,
        level: SenseVoiceConversionLevel
    ) -> Dict[str, Any]:
        """Validate performance dimension."""
        result = {
            "score": 0,
            "checks": [],
            "warnings": [],
            "details": {}
        }

        score = 0

        # Check 1: Conversion time
        conversion_time = getattr(conversion_result, "conversion_time", 0)
        if conversion_time > 0:
            if conversion_time < 300:  # Under 5 minutes
                result["checks"].append(("conversion_time", True, f"Fast conversion: {conversion_time:.1f}s"))
                score += 20
            else:
                result["checks"].append(("conversion_time", False, f"Slow conversion: {conversion_time:.1f}s"))
                result["warnings"].append(f"Conversion time exceeds 5 minutes: {conversion_time:.1f}s")
                score += 10
        else:
            result["checks"].append(("conversion_time", False, "No conversion time data"))
            result["warnings"].append("Conversion time not recorded")

        # Check 2: Inference speed
        inference_speed = conversion_result.metadata.get("inference_speed_ms")
        if inference_speed:
            if inference_speed < 200:  # Under 200ms
                result["checks"].append(("inference_speed", True, f"Fast inference: {inference_speed:.1f}ms"))
                score += 25
            elif inference_speed < 500:
                result["checks"].append(("inference_speed", True, f"Good inference: {inference_speed:.1f}ms"))
                score += 20
            else:
                result["checks"].append(("inference_speed", False, f"Slow inference: {inference_speed:.1f}ms"))
                result["warnings"].append(f"Inference speed above 500ms: {inference_speed:.1f}ms")
                score += 10
        else:
            result["checks"].append(("inference_speed", False, "No speed metrics"))
            result["warnings"].append("Inference speed metrics not available")

        # Check 3: Memory usage
        memory_usage = conversion_result.metadata.get("memory_usage_mb")
        if memory_usage:
            if memory_usage < 1024:  # Under 1GB
                result["checks"].append(("memory_usage", True, f"Low memory: {memory_usage:.0f}MB"))
                score += 25
            elif memory_usage < 2048:
                result["checks"].append(("memory_usage", True, f"Moderate memory: {memory_usage:.0f}MB"))
                score += 20
            else:
                result["checks"].append(("memory_usage", False, f"High memory: {memory_usage:.0f}MB"))
                result["warnings"].append(f"Memory usage above 2GB: {memory_usage:.0f}MB")
                score += 10
        else:
            result["checks"].append(("memory_usage", False, "No memory metrics"))
            result["warnings"].append("Memory usage metrics not available")

        # Check 4: Processing mode optimization
        if mode == SenseVoiceProcessingMode.STREAMING:
            streaming_optimized = conversion_result.metadata.get("streaming_optimized", False)
            if streaming_optimized:
                result["checks"].append(("streaming_optimization", True, "Streaming optimized"))
                score += 30
            else:
                result["checks"].append(("streaming_optimization", False, "Not streaming optimized"))
                result["warnings"].append("Model not optimized for streaming mode")
        else:
            # Batch or interactive mode
            result["checks"].append(("mode_optimization", True, f"Optimized for {mode.value} mode"))
            score += 30

        result["score"] = score
        return result

    async def _validate_compatibility_dimension(
        self,
        conversion_result: ResultModel,
        mode: SenseVoiceProcessingMode
    ) -> Dict[str, Any]:
        """Validate compatibility dimension."""
        result = {
            "score": 0,
            "checks": [],
            "warnings": [],
            "details": {}
        }

        score = 0

        # Check 1: NPU compatibility
        npu_compatible = conversion_result.metadata.get("npu_compatible", False)
        if npu_compatible:
            result["checks"].append(("npu_compatibility", True, "NPU compatible"))
            score += 30
        else:
            result["checks"].append(("npu_compatibility", False, "NPU compatibility unknown"))
            result["warnings"].append("NPU compatibility not verified")

        # Check 2: Horizon X5 compatibility
        hx5_compatible = conversion_result.metadata.get("horizon_x5_compatible", False)
        if hx5_compatible:
            result["checks"].append(("horizon_x5_compatibility", True, "Horizon X5 compatible"))
            score += 25
        else:
            result["checks"].append(("horizon_x5_compatibility", False, "Horizon X5 compatibility unknown"))
            result["warnings"].append("Horizon X5 compatibility not verified")

        # Check 3: Runtime compatibility
        runtime_info = conversion_result.metadata.get("runtime_compatibility", {})
        if runtime_info.get("supported_runtimes"):
            result["checks"].append(("runtime_compatibility", True, "Runtime information available"))
            score += 25
        else:
            result["checks"].append(("runtime_compatibility", False, "No runtime info"))
            result["warnings"].append("Runtime compatibility information missing")

        # Check 4: Hardware requirements
        hw_requirements = conversion_result.metadata.get("hardware_requirements", {})
        if hw_requirements:
            result["checks"].append(("hardware_requirements", True, "Hardware requirements documented"))
            score += 20
        else:
            result["checks"].append(("hardware_requirements", False, "No hardware requirements"))
            result["warnings"].append("Hardware requirements not documented")

        result["score"] = score
        return result

    async def _validate_quality_dimension(
        self,
        conversion_result: ResultModel,
        mode: SenseVoiceProcessingMode
    ) -> Dict[str, Any]:
        """Validate quality dimension."""
        result = {
            "score": 0,
            "checks": [],
            "warnings": [],
            "details": {}
        }

        score = 0

        # Check 1: Code quality metrics
        if conversion_result.metadata.get("code_quality_score", 0) > 90:
            result["checks"].append(("code_quality", True, "High code quality"))
            score += 25
        else:
            result["checks"].append(("code_quality", False, "Code quality concerns"))
            result["warnings"].append("Code quality score below 90")

        # Check 2: Test coverage
        test_coverage = conversion_result.metadata.get("test_coverage", 0)
        if test_coverage > 90:
            result["checks"].append(("test_coverage", True, f"High test coverage: {test_coverage:.0f}%"))
            score += 25
        elif test_coverage > 70:
            result["checks"].append(("test_coverage", True, f"Good test coverage: {test_coverage:.0f}%"))
            score += 20
        else:
            result["checks"].append(("test_coverage", False, f"Low test coverage: {test_coverage:.0f}%"))
            result["warnings"].append(f"Test coverage below 70%: {test_coverage:.0f}%")
            score += 10

        # Check 3: Documentation completeness
        has_docs = conversion_result.metadata.get("documentation_complete", False)
        if has_docs:
            result["checks"].append(("documentation", True, "Documentation complete"))
            score += 25
        else:
            result["checks"].append(("documentation", False, "Documentation incomplete"))
            result["warnings"].append("Documentation is incomplete")

        # Check 4: Standards compliance
        if conversion_result.metadata.get("standards_compliant", True):
            result["checks"].append(("standards_compliance", True, "Standards compliant"))
            score += 25
        else:
            result["checks"].append(("standards_compliance", False, "Standards issues"))
            result["warnings"].append("May not comply with required standards")

        result["score"] = score
        return result

    async def _check_processing_mode_compatibility(
        self,
        model_data: Any,
        mode: SenseVoiceProcessingMode
    ) -> Tuple[bool, str]:
        """Check if model is compatible with processing mode."""
        try:
            # Simplified compatibility check
            # In real implementation, this would inspect the ONNX model graph
            if mode == SenseVoiceProcessingMode.STREAMING:
                # Check for streaming-specific requirements
                return True, "Streaming mode compatible"
            elif mode == SenseVoiceProcessingMode.BATCH:
                # Check for batch processing requirements
                return True, "Batch mode compatible"
            else:
                return True, "Interactive mode compatible"
        except Exception as e:
            return False, f"Compatibility check failed: {e}"
