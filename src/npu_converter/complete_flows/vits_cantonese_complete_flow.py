"""
VITS-Cantonese TTS Complete Conversion Flow

This module implements the complete conversion flow for VITS-Cantonese TTS models (Story 2.2).
It extends the VITSCantoneseConversionFlow from Story 1.5 to provide production-ready,
full-featured conversion capabilities for Cantonese TTS models.

Key Features (Story 2.2):
- Enhanced end-to-end conversion capabilities with >95% success rate
- Cantonese-specific voice synthesis optimizations (tones, prosody, multi-voice)
- Complete parameter configuration support
- Precise conversion result validation
- Dedicated conversion report generation

Architecture:
- Extends VITSCantoneseConversionFlow (Story 1.5)
- Integrates with Story 1.4 ConfigurationManager
- Depends on Story 2.1.2 ONNXModelLoader
- Uses CantoneseOptimizer, CantoneseValidator, CantoneseReportGenerator

Author: Story 2.2 Implementation
Version: 1.0.0
Date: 2025-10-27
"""

from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path
import logging
from datetime import datetime
import asyncio
from enum import Enum

from ..converters.base_conversion_flow import BaseConversionFlow, ConversionStage
from ..converters.vits_cantonese_flow import VITSCantoneseConversionFlow
from ..core.models.conversion_model import ConversionModel
from ..core.models.config_model import ConfigModel
from ..core.models.progress_model import ProgressStep
from ..core.models.result_model import ResultModel
from ..core.interfaces.validator import ValidationResult
from ..core.exceptions.conversion_errors import (
    ConversionError,
    ValidationError,
    ModelCompatibilityError,
    OptimizationError
)

from .optimizers.cantonese_optimizer import CantoneseOptimizer
from .validators.cantonese_validator import CantoneseValidator
from .reports.cantonese_report_generator import CantoneseReportGenerator
from ..loaders.onnx_loader import ONNXModelLoader

logger = logging.getLogger(__name__)


class CantoneseConversionLevel(Enum):
    """Conversion optimization levels for VITS-Cantonese models."""
    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    PRODUCTION = "production"


class VITSCantoneseCompleteFlow(VITSCantoneseConversionFlow):
    """
    Complete VITS-Cantonese TTS model conversion flow.

    This class provides production-ready, full-featured conversion capabilities for
    VITS-Cantonese TTS models, including:
    - Enhanced conversion with >95% success rate
    - Cantonese language optimizations (九声六调)
    - Multi-voice support (male, female, children)
    - Complete parameter configuration
    - Precise result validation
    - Comprehensive reporting

    Extends: VITSCantoneseConversionFlow (Story 1.5)
    Integration: Story 1.4 ConfigurationManager
    Dependencies: Story 2.1.2 ONNXModelLoader
    """

    def __init__(
        self,
        config: Optional[ConfigModel] = None,
        operation_id: Optional[str] = None,
        conversion_level: CantoneseConversionLevel = CantoneseConversionLevel.PRODUCTION
    ) -> None:
        """
        Initialize complete VITS-Cantonese conversion flow.

        Args:
            config: Configuration model for the conversion
            operation_id: Optional unique operation identifier
            conversion_level: Optimization level (default: PRODUCTION)

        Raises:
            ConversionError: If initialization fails
        """
        super().__init__(config=config, operation_id=operation_id)

        # Story 2.2 specific attributes
        self.conversion_level = conversion_level
        self.cantonese_optimizer = None
        self.cantonese_validator = None
        self.report_generator = None
        self.onnx_loader = None

        # Track optimization and validation state
        self.optimization_applied = False
        self.validation_results = []
        self.conversion_metrics = {}

        logger.info(
            f"Initialized VITSCantoneseCompleteFlow v1.0.0 (Story 2.2) - "
            f"Level: {conversion_level.value}, Operation: {self.operation_id}"
        )

    def create_progress_steps(self) -> List[ProgressStep]:
        """
        Create enhanced progress steps for complete VITS-Cantonese conversion.

        Extends the base progress steps with Story 2.2 specific stages:
        - Cantonese optimization
        - Parameter configuration validation
        - Precision validation
        - Report generation

        Returns:
            List[ProgressStep]: Enhanced progress steps for complete conversion
        """
        steps = super().create_progress_steps()

        # Add Story 2.2 specific steps
        story_2_2_steps = [
            ProgressStep(
                step_id="cantonese_optimization",
                name="Cantonese Optimization",
                description="Apply Cantonese-specific optimizations (tones, prosody, multi-voice)",
                weight=15.0,
                metadata={
                    "stage_type": "optimization",
                    "language": "cantonese",
                    "conversion_level": self.conversion_level.value,
                    "story": "2.2"
                }
            ),
            ProgressStep(
                step_id="parameter_validation",
                name="Parameter Configuration Validation",
                description="Validate complete parameter configuration for production use",
                weight=8.0,
                metadata={
                    "stage_type": "validation",
                    "component": "configuration",
                    "story": "2.2"
                }
            ),
            ProgressStep(
                step_id="precision_validation",
                name="Precision Validation",
                description="Validate conversion precision and Cantonese speech quality",
                weight=10.0,
                metadata={
                    "stage_type": "validation",
                    "component": "precision",
                    "target_accuracy": ">98%",
                    "story": "2.2"
                }
            ),
            ProgressStep(
                step_id="report_generation",
                name="Conversion Report Generation",
                description="Generate comprehensive conversion report",
                weight=5.0,
                metadata={
                    "stage_type": "reporting",
                    "formats": ["json", "html", "pdf"],
                    "story": "2.2"
                }
            )
        ]

        # Insert after base steps
        steps.extend(story_2_2_steps)

        return steps

    def initialize_components(self) -> None:
        """
        Initialize Story 2.2 specific components.

        Creates and configures:
        - CantoneseOptimizer
        - CantoneseValidator
        - CantoneseReportGenerator
        - ONNXModelLoader

        Raises:
            ConversionError: If component initialization fails
        """
        try:
            logger.info("Initializing Story 2.2 components...")

            # Initialize Cantonese Optimizer
            self.cantonese_optimizer = CantoneseOptimizer(
                conversion_level=self.conversion_level,
                language="cantonese",
                config=self.config
            )
            logger.info(f"CantoneseOptimizer initialized (level: {self.conversion_level.value})")

            # Initialize Cantonese Validator
            self.cantonese_validator = CantoneseValidator(
                language="cantonese",
                validation_level="strict",
                config=self.config
            )
            logger.info("CantoneseValidator initialized (strict validation)")

            # Initialize Report Generator
            self.report_generator = CantoneseReportGenerator(
                output_formats=["json", "html", "pdf"],
                config=self.config
            )
            logger.info("CantoneseReportGenerator initialized (multi-format)")

            # Initialize ONNX Model Loader (Story 2.1.2)
            self.onnx_loader = ONNXModelLoader()
            logger.info("ONNXModelLoader initialized (Story 2.1.2)")

            logger.info("All Story 2.2 components initialized successfully")

        except Exception as e:
            error_msg = f"Failed to initialize Story 2.2 components: {str(e)}"
            logger.error(error_msg)
            raise ConversionError(error_msg) from e

    async def execute_cantonese_optimization(self, model: ConversionModel) -> ConversionModel:
        """
        Execute Cantonese-specific optimizations.

        AC2: Implement Cantonese speech synthesis optimizations

        Args:
            model: Conversion model to optimize

        Returns:
            ConversionModel: Optimized conversion model

        Raises:
            OptimizationError: If optimization fails
        """
        try:
            self.update_progress("cantonese_optimization", 0.0)

            if not self.cantonese_optimizer:
                raise OptimizationError("CantoneseOptimizer not initialized")

            logger.info("Starting Cantonese optimization...")

            # Apply Cantonese tone modeling
            self.update_progress("cantonese_optimization", 25.0, "Applying Cantonese tone modeling")
            model = await self.cantonese_optimizer.apply_tone_modeling(model)

            # Apply prosody optimization
            self.update_progress("cantonese_optimization", 50.0, "Optimizing prosody and rhythm")
            model = await self.cantonese_optimizer.optimize_prosody(model)

            # Apply multi-voice support (if configured)
            if self.config and hasattr(self.config, 'voice_type'):
                self.update_progress("cantonese_optimization", 75.0, f"Applying {self.config.voice_type} voice optimization")
                model = await self.cantonese_optimizer.apply_voice_optimization(model, self.config.voice_type)

            # Final optimization pass
            self.update_progress("cantonese_optimization", 100.0, "Cantonese optimization complete")
            self.optimization_applied = True

            logger.info("Cantonese optimization completed successfully")
            return model

        except Exception as e:
            error_msg = f"Cantonese optimization failed: {str(e)}"
            logger.error(error_msg)
            raise OptimizationError(error_msg) from e

    async def validate_parameter_configuration(self, model: ConversionModel) -> ValidationResult:
        """
        Validate complete parameter configuration.

        AC3: Support complete parameter configuration

        Args:
            model: Conversion model to validate

        Returns:
            ValidationResult: Validation result with detailed checks

        Raises:
            ValidationError: If validation fails
        """
        try:
            self.update_progress("parameter_validation", 0.0)

            logger.info("Validating parameter configuration...")

            if not self.cantonese_validator:
                raise ValidationError("CantoneseValidator not initialized")

            # Validate configuration completeness
            self.update_progress("parameter_validation", 30.0, "Checking configuration completeness")
            config_result = await self.cantonese_validator.validate_configuration(self.config)

            # Validate model parameters
            self.update_progress("parameter_validation", 60.0, "Validating model parameters")
            model_result = await self.cantonese_validator.validate_model_parameters(model)

            # Validate optimization parameters
            if self.optimization_applied:
                self.update_progress("parameter_validation", 90.0, "Validating optimization parameters")
                opt_result = await self.cantonese_validator.validate_optimization_parameters(
                    self.cantonese_optimizer.get_parameters()
                )

                # Combine results
                combined_result = ValidationResult(
                    is_valid=config_result.is_valid and model_result.is_valid and opt_result.is_valid,
                    message="Parameter configuration validation complete",
                    details={
                        "configuration": config_result.details,
                        "model": model_result.details,
                        "optimization": opt_result.details
                    },
                    warnings=config_result.warnings + model_result.warnings + opt_result.warnings,
                    errors=config_result.errors + model_result.errors + opt_result.errors
                )
            else:
                combined_result = ValidationResult(
                    is_valid=config_result.is_valid and model_result.is_valid,
                    message="Parameter configuration validation complete",
                    details={
                        "configuration": config_result.details,
                        "model": model_result.details
                    },
                    warnings=config_result.warnings + model_result.warnings,
                    errors=config_result.errors + model_result.errors
                )

            self.update_progress("parameter_validation", 100.0)

            if not combined_result.is_valid:
                error_msg = f"Parameter validation failed: {combined_result.errors}"
                logger.error(error_msg)
                raise ValidationError(error_msg)

            logger.info("Parameter configuration validation passed")
            return combined_result

        except Exception as e:
            error_msg = f"Parameter validation failed: {str(e)}"
            logger.error(error_msg)
            raise ValidationError(error_msg) from e

    async def validate_conversion_precision(self, original_model: ConversionModel, converted_model: ConversionModel) -> ValidationResult:
        """
        Validate conversion precision and Cantonese speech quality.

        AC4: Implement precise validation of conversion results

        Args:
            original_model: Original ONNX model
            converted_model: Converted BPU model

        Returns:
            ValidationResult: Precision validation results

        Raises:
            ValidationError: If precision validation fails
        """
        try:
            self.update_progress("precision_validation", 0.0)

            if not self.cantonese_validator:
                raise ValidationError("CantoneseValidator not initialized")

            logger.info("Starting precision validation...")

            # Validate audio format and quality
            self.update_progress("precision_validation", 25.0, "Validating audio format and quality")
            audio_result = await self.cantonese_validator.validate_audio_quality(converted_model)

            # Validate Cantonese semantic accuracy
            self.update_progress("precision_validation", 50.0, "Validating Cantonese semantic accuracy")
            semantic_result = await self.cantonese_validator.validate_semantic_accuracy(
                original_model, converted_model
            )

            # Validate pronunciation accuracy (tone modeling)
            self.update_progress("precision_validation", 75.0, "Validating pronunciation and tone accuracy")
            pronunciation_result = await self.cantonese_validator.validate_pronunciation_accuracy(
                converted_model
            )

            # Calculate overall precision score
            precision_scores = [
                audio_result.details.get("quality_score", 0.0),
                semantic_result.details.get("accuracy_score", 0.0),
                pronunciation_result.details.get("tone_accuracy_score", 0.0)
            ]
            overall_precision = sum(precision_scores) / len(precision_scores)

            # Check against PRD requirement (>98%)
            precision_passed = overall_precision >= 0.98

            combined_result = ValidationResult(
                is_valid=precision_passed,
                message=f"Precision validation complete (score: {overall_precision:.2%})",
                details={
                    "overall_precision": overall_precision,
                    "audio_quality": audio_result.details,
                    "semantic_accuracy": semantic_result.details,
                    "pronunciation_accuracy": pronunciation_result.details,
                    "prd_requirement": ">98%",
                    "meets_requirement": precision_passed
                },
                warnings=audio_result.warnings + semantic_result.warnings + pronunciation_result.warnings,
                errors=audio_result.errors + semantic_result.errors + pronunciation_result.errors
            )

            self.update_progress("precision_validation", 100.0)

            if not combined_result.is_valid:
                error_msg = f"Precision validation failed: {overall_precision:.2%} < 98%"
                logger.error(error_msg)
                raise ValidationError(error_msg)

            # Store precision metrics
            self.conversion_metrics['precision_score'] = overall_precision

            logger.info(f"Precision validation passed: {overall_precision:.2%}")
            return combined_result

        except Exception as e:
            error_msg = f"Precision validation failed: {str(e)}"
            logger.error(error_msg)
            raise ValidationError(error_msg) from e

    async def generate_conversion_report(self, conversion_result: ResultModel) -> Path:
        """
        Generate comprehensive conversion report.

        AC5: Provide dedicated VITS-Cantonese conversion report

        Args:
            conversion_result: Result model from conversion

        Returns:
            Path: Path to generated report file

        Raises:
            ConversionError: If report generation fails
        """
        try:
            self.update_progress("report_generation", 0.0)

            if not self.report_generator:
                raise ConversionError("CantoneseReportGenerator not initialized")

            logger.info("Generating comprehensive conversion report...")

            # Collect report data
            report_data = {
                "story": "2.2",
                "story_name": "VITS-Cantonese TTS Complete Conversion Implementation",
                "model_type": "VITS-Cantonese TTS",
                "language": "Cantonese",
                "conversion_level": self.conversion_level.value,
                "operation_id": self.operation_id,
                "timestamp": datetime.now().isoformat(),
                "conversion_result": conversion_result.to_dict(),
                "optimization_applied": self.optimization_applied,
                "precision_metrics": self.conversion_metrics,
                "validation_results": [vr.to_dict() for vr in self.validation_results]
            }

            # Generate report in multiple formats
            self.update_progress("report_generation", 50.0, "Generating JSON report")
            json_path = await self.report_generator.generate_json_report(report_data)

            self.update_progress("report_generation", 75.0, "Generating HTML report")
            html_path = await self.report_generator.generate_html_report(report_data)

            self.update_progress("report_generation", 100.0, "Report generation complete")
            pdf_path = await self.report_generator.generate_pdf_report(report_data)

            logger.info(f"Conversion report generated: JSON={json_path}, HTML={html_path}, PDF={pdf_path}")

            # Return primary report path (JSON)
            return json_path

        except Exception as e:
            error_msg = f"Report generation failed: {str(e)}"
            logger.error(error_msg)
            raise ConversionError(error_msg) from e

    async def convert_model(
        self,
        model_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        **kwargs
    ) -> Tuple[ResultModel, Path]:
        """
        Execute complete VITS-Cantonese model conversion.

        Enhanced conversion method for Story 2.2 that includes:
        1. Base conversion (from Story 1.5)
        2. Cantonese optimization (AC2)
        3. Parameter validation (AC3)
        4. Precision validation (AC4)
        5. Report generation (AC5)

        Args:
            model_path: Path to input ONNX model
            output_path: Optional output path for converted model
            **kwargs: Additional conversion parameters

        Returns:
            Tuple[ResultModel, Path]: Conversion result and report path

        Raises:
            ConversionError: If conversion fails
        """
        try:
            logger.info(f"Starting complete VITS-Cantonese conversion (Story 2.2): {model_path}")

            # Track overall conversion success
            conversion_start_time = datetime.now()

            # Initialize components
            self.initialize_components()

            # Step 1: Load ONNX model (Story 2.1.2)
            self.update_progress("loading", 0.0)
            onnx_model = await self.onnx_loader.load_model(model_path)
            conversion_model = ConversionModel.from_onnx_model(onnx_model)

            # Step 2: Validate model compatibility
            self.update_progress("validation", 0.0)
            validation_result = await self.validate_model(compression_model)
            if not validation_result.is_valid:
                raise ModelCompatibilityError(f"Model validation failed: {validation_result.errors}")

            # Step 3: Execute base conversion
            self.update_progress("conversion", 0.0)
            base_result = await super().convert_model(model_path, output_path, **kwargs)

            # Step 4: Apply Cantonese optimization (AC2)
            optimized_model = await self.execute_cantonese_optimization(conversion_model)

            # Step 5: Validate parameter configuration (AC3)
            param_validation = await self.validate_parameter_configuration(optimized_model)
            self.validation_results.append(param_validation)

            # Step 6: Validate conversion precision (AC4)
            precision_validation = await self.validate_conversion_precision(
                conversion_model,
                ConversionModel.from_result(base_result)
            )
            self.validation_results.append(precision_validation)

            # Step 7: Generate conversion report (AC5)
            report_path = await self.generate_conversion_report(base_result)

            # Calculate success metrics
            conversion_time = (datetime.now() - conversion_start_time).total_seconds()
            success_rate = 1.0 if all(vr.is_valid for vr in self.validation_results) else 0.0

            # Store conversion metrics
            self.conversion_metrics.update({
                'conversion_time_seconds': conversion_time,
                'success_rate': success_rate,
                'precision_score': self.conversion_metrics.get('precision_score', 0.0),
                'validation_count': len(self.validation_results)
            })

            # Check PRD requirements
            prd_requirements_met = (
                success_rate >= 0.95 and  # >95% success rate
                self.conversion_metrics.get('precision_score', 0.0) >= 0.98 and  # >98% precision
                conversion_time < 300  # <5 minutes
            )

            if not prd_requirements_met:
                logger.warning("PRD requirements not fully met - see metrics for details")

            logger.info(
                f"Complete VITS-Cantonese conversion finished - "
                f"Success: {success_rate:.2%}, Precision: {self.conversion_metrics.get('precision_score', 0):.2%}, "
                f"Time: {conversion_time:.1f}s"
            )

            return base_result, report_path

        except Exception as e:
            error_msg = f"Complete VITS-Cantonese conversion failed: {str(e)}"
            logger.error(error_msg)
            raise ConversionError(error_msg) from e

    def get_conversion_metrics(self) -> Dict[str, Any]:
        """
        Get conversion metrics and performance data.

        Returns:
            Dict[str, Any]: Conversion metrics dictionary
        """
        return {
            'story': '2.2',
            'conversion_level': self.conversion_level.value,
            'optimization_applied': self.optimization_applied,
            'validation_results_count': len(self.validation_results),
            'metrics': self.conversion_metrics.copy(),
            'prd_requirements': {
                'success_rate_target': '>95%',
                'precision_target': '>98%',
                'performance_target': '2-5x improvement'
            }
        }

    def __repr__(self) -> str:
        """String representation of VITSCantoneseCompleteFlow."""
        return (
            f"VITSCantoneseCompleteFlow("
            f"version='1.0.0', "
            f"level={self.conversion_level.value}, "
            f"operation_id='{self.operation_id}', "
            f"optimization={self.optimization_applied}"
            f")"
        )
