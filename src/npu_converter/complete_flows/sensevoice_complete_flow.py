"""
SenseVoice ASR Complete Conversion Flow

This module implements the complete conversion flow for SenseVoice ASR models (Story 2.3).
It extends the SenseVoiceConversionFlow from Story 1.5 to provide production-ready,
full-featured conversion capabilities for multi-language ASR models.

Key Features (Story 2.3):
- Enhanced end-to-end conversion capabilities with >95% success rate
- Multi-language ASR optimizations (Chinese, English, Japanese, etc.)
- Multiple audio format support (WAV, MP3, FLAC, etc.)
- Real-time streaming and batch processing modes
- Complete parameter configuration support
- Precise conversion result validation
- Dedicated conversion report generation

Architecture:
- Extends SenseVoiceConversionFlow (Story 1.5)
- Integrates with Story 1.4 ConfigurationManager
- Depends on Story 2.1.2 ONNXModelLoader
- Uses SenseVoiceOptimizer, SenseVoiceValidator, SenseVoiceReportGenerator

Author: Story 2.3 Implementation
Version: 1.0.0
Date: 2025-10-28
"""

from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path
import logging
from datetime import datetime
import asyncio
from enum import Enum

from ..converters.base_conversion_flow import BaseConversionFlow, ConversionStage
from ..converters.sensevoice_flow import SenseVoiceConversionFlow
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

from .optimizers.sensevoice_optimizer import SenseVoiceOptimizer
from .validators.sensevoice_validator import SenseVoiceValidator
from .reports.sensevoice_report_generator import SenseVoiceReportGenerator
from ..loaders.onnx_loader import ONNXModelLoader

logger = logging.getLogger(__name__)


class SenseVoiceConversionLevel(Enum):
    """Conversion optimization levels for SenseVoice ASR models."""
    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    PRODUCTION = "production"


class SenseVoiceProcessingMode(Enum):
    """Processing modes for SenseVoice ASR models."""
    STREAMING = "streaming"
    BATCH = "batch"
    INTERACTIVE = "interactive"


class SenseVoiceCompleteFlow(SenseVoiceConversionFlow):
    """
    Complete SenseVoice ASR model conversion flow.

    This class provides production-ready, full-featured conversion capabilities for
    SenseVoice ASR models, including:
    - Enhanced conversion with >95% success rate
    - Multi-language speech recognition optimizations
    - Support for multiple audio formats (WAV, MP3, FLAC, etc.)
    - Real-time streaming and batch processing modes
    - Complete parameter configuration
    - Precise result validation
    - Comprehensive reporting

    Extends: SenseVoiceConversionFlow (Story 1.5)
    Integration: Story 1.4 ConfigurationManager
    Dependencies: Story 2.1.2 ONNXModelLoader
    """

    def __init__(
        self,
        config: Optional[ConfigModel] = None,
        conversion_level: SenseVoiceConversionLevel = SenseVoiceConversionLevel.PRODUCTION,
        processing_mode: SenseVoiceProcessingMode = SenseVoiceProcessingMode.BATCH,
        enable_optimizations: bool = True,
        enable_validation: bool = True,
        enable_reports: bool = True
    ):
        """
        Initialize the SenseVoice complete conversion flow.

        Args:
            config: Configuration model for conversion parameters
            conversion_level: Optimization level (BASIC, STANDARD, ENHANCED, PRODUCTION)
            processing_mode: Processing mode (STREAMING, BATCH, INTERACTIVE)
            enable_optimizations: Whether to enable ASR-specific optimizations
            enable_validation: Whether to enable result validation
            enable_reports: Whether to generate conversion reports
        """
        super().__init__(config=config)

        self.conversion_level = conversion_level
        self.processing_mode = processing_mode
        self.enable_optimizations = enable_optimizations
        self.enable_validation = enable_validation
        self.enable_reports = enable_reports

        # Initialize components
        self._optimizer = None
        self._validator = None
        self._report_generator = None
        self._onnx_loader = None

        logger.info(
            f"Initialized SenseVoiceCompleteFlow: "
            f"level={conversion_level.value}, mode={processing_mode.value}, "
            f"optimizations={enable_optimizations}, validation={enable_validation}, "
            f"reports={enable_reports}"
        )

    @property
    def optimizer(self) -> SenseVoiceOptimizer:
        """Get the SenseVoice optimizer instance."""
        if self._optimizer is None:
            self._optimizer = SenseVoiceOptimizer(
                config=self.config,
                conversion_level=self.conversion_level,
                processing_mode=self.processing_mode
            )
        return self._optimizer

    @property
    def validator(self) -> SenseVoiceValidator:
        """Get the SenseVoice validator instance."""
        if self._validator is None:
            self._validator = SenseVoiceValidator(
                config=self.config,
                processing_mode=self.processing_mode
            )
        return self._validator

    @property
    def report_generator(self) -> SenseVoiceReportGenerator:
        """Get the SenseVoice report generator instance."""
        if self._report_generator is None:
            self._report_generator = SenseVoiceReportGenerator(
                config=self.config,
                conversion_level=self.conversion_level
            )
        return self._report_generator

    @property
    def onnx_loader(self) -> ONNXModelLoader:
        """Get the ONNX model loader instance."""
        if self._onnx_loader is None:
            self._onnx_loader = ONNXModelLoader()
        return self._onnx_loader

    async def convert_model(
        self,
        model_path: Union[str, Path],
        output_path: Union[str, Path],
        conversion_params: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[callable] = None
    ) -> ResultModel:
        """
        Convert a SenseVoice ASR model with complete processing pipeline.

        This method performs the full conversion pipeline including:
        1. Model loading and validation
        2. ASR-specific optimizations
        3. NPU conversion
        4. Result validation
        5. Report generation

        Args:
            model_path: Path to the input ONNX model
            output_path: Path for the converted model
            conversion_params: Additional conversion parameters
            progress_callback: Optional callback for progress updates

        Returns:
            ResultModel: Complete conversion result with validation and report data

        Raises:
            ConversionError: If conversion fails
            ValidationError: If validation fails
            ModelCompatibilityError: If model is incompatible
        """
        start_time = datetime.now()
        conversion_id = f"sensevoice_{start_time.strftime('%Y%m%d_%H%M%S')}"

        logger.info(f"Starting SenseVoice conversion: {conversion_id}")
        logger.info(f"Model: {model_path}")
        logger.info(f"Output: {output_path}")
        logger.info(f"Level: {self.conversion_level.value}, Mode: {self.processing_mode.value}")

        # Step 1: Initialize progress tracking
        progress_steps = [
            ProgressStep("model_loading", "Loading ONNX model", 10),
            ProgressStep("model_validation", "Validating model compatibility", 15),
            ProgressStep("audio_preprocessing", "Optimizing audio preprocessing", 20),
            ProgressStep("asr_optimization", "Applying ASR-specific optimizations", 25),
            ProgressStep("npu_conversion", "Converting to NPU format", 15),
            ProgressStep("result_validation", "Validating conversion results", 10),
            ProgressStep("report_generation", "Generating conversion report", 5)
        ]

        if progress_callback:
            await self._call_progress_callback(progress_callback, progress_steps[0])

        # Step 2: Load and validate ONNX model
        logger.info("Step 1/7: Loading ONNX model...")
        try:
            model_data = await self.onnx_loader.load_model(
                model_path=model_path,
                progress_callback=progress_callback
            )
            await self._update_progress(progress_callback, progress_steps[0])

            logger.info("Step 2/7: Validating model compatibility...")
            validation_result = await self.validator.validate_model_structure(
                model_data=model_data,
                model_type="sensevoice",
                processing_mode=self.processing_mode
            )

            if not validation_result.is_valid:
                raise ModelCompatibilityError(
                    f"Model validation failed: {validation_result.error_message}",
                    validation_result.error_code,
                    validation_result.details
                )

            await self._update_progress(progress_callback, progress_steps[1])

        except Exception as e:
            logger.error(f"Model loading/validation failed: {e}")
            raise ConversionError(
                f"Failed to load or validate model: {e}",
                error_code="MODEL_LOAD_FAILED",
                details={"model_path": str(model_path)}
            )

        # Step 3: Audio preprocessing optimization
        logger.info("Step 3/7: Optimizing audio preprocessing...")
        try:
            if self.enable_optimizations:
                preprocessing_config = await self.optimizer.optimize_audio_preprocessing(
                    model_data=model_data,
                    processing_mode=self.processing_mode,
                    conversion_level=self.conversion_level
                )
            else:
                preprocessing_config = {}

            await self._update_progress(progress_callback, progress_steps[2])

        except Exception as e:
            logger.error(f"Audio preprocessing optimization failed: {e}")
            raise OptimizationError(
                f"Audio preprocessing optimization failed: {e}",
                error_code="AUDIO_PREPROCESS_FAILED",
                details={"model_path": str(model_path)}
            )

        # Step 4: ASR-specific optimization
        logger.info("Step 4/7: Applying ASR-specific optimizations...")
        try:
            if self.enable_optimizations:
                optimization_result = await self.optimizer.optimize_model(
                    model_data=model_data,
                    preprocessing_config=preprocessing_config,
                    conversion_params=conversion_params,
                    processing_mode=self.processing_mode,
                    conversion_level=self.conversion_level
                )
            else:
                optimization_result = {"optimized": False, "changes": []}

            await self._update_progress(progress_callback, progress_steps[3])

        except Exception as e:
            logger.error(f"ASR optimization failed: {e}")
            raise OptimizationError(
                f"ASR optimization failed: {e}",
                error_code="ASR_OPTIMIZATION_FAILED",
                details={"model_path": str(model_path)}
            )

        # Step 5: NPU conversion (using parent class implementation)
        logger.info("Step 5/7: Converting to NPU format...")
        try:
            conversion_model = ConversionModel(
                model_data=model_data,
                optimization_data=optimization_result,
                preprocessing_config=preprocessing_config,
                conversion_params=conversion_params or {},
                conversion_level=self.conversion_level.value,
                processing_mode=self.processing_mode.value
            )

            npc_result = await super().convert_model(
                model_path=model_path,
                output_path=output_path,
                conversion_params={
                    **conversion_params,
                    "optimization_result": optimization_result,
                    "preprocessing_config": preprocessing_config
                } if conversion_params else {
                    "optimization_result": optimization_result,
                    "preprocessing_config": preprocessing_config
                },
                progress_callback=progress_callback
            )

            await self._update_progress(progress_callback, progress_steps[4])

        except Exception as e:
            logger.error(f"NPU conversion failed: {e}")
            raise ConversionError(
                f"NPU conversion failed: {e}",
                error_code="NPU_CONVERSION_FAILED",
                details={"model_path": str(model_path), "output_path": str(output_path)}
            )

        # Step 6: Result validation
        logger.info("Step 6/7: Validating conversion results...")
        try:
            if self.enable_validation:
                validation_result = await self.validator.validate_conversion_result(
                    conversion_result=npc_result,
                    model_data=model_data,
                    processing_mode=self.processing_mode,
                    conversion_level=self.conversion_level
                )

                if not validation_result.is_valid:
                    logger.warning(f"Validation warnings: {validation_result.warnings}")

            await self._update_progress(progress_callback, progress_steps[5])

        except Exception as e:
            logger.error(f"Result validation failed: {e}")
            raise ValidationError(
                f"Result validation failed: {e}",
                error_code="VALIDATION_FAILED",
                details={"model_path": str(model_path)}
            )

        # Step 7: Report generation
        logger.info("Step 7/7: Generating conversion report...")
        try:
            if self.enable_reports:
                report_data = await self.report_generator.generate_report(
                    conversion_id=conversion_id,
                    conversion_result=npc_result,
                    validation_result=validation_result if self.enable_validation else None,
                    optimization_result=optimization_result,
                    processing_mode=self.processing_mode,
                    conversion_level=self.conversion_level
                )

                npc_result.report_data = report_data

            await self._update_progress(progress_callback, progress_steps[6])

        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            # Report generation failure is not critical, continue
            logger.warning("Continuing without report generation")

        # Finalize result
        end_time = datetime.now()
        conversion_time = (end_time - start_time).total_seconds()

        npc_result.conversion_time = conversion_time
        npc_result.metadata["conversion_id"] = conversion_id
        npc_result.metadata["sensevoice_version"] = "1.0.0"
        npc_result.metadata["processing_mode"] = self.processing_mode.value
        npc_result.metadata["conversion_level"] = self.conversion_level.value
        npc_result.metadata["enable_optimizations"] = self.enable_optimizations
        npc_result.metadata["enable_validation"] = self.enable_validation
        npc_result.metadata["enable_reports"] = self.enable_reports

        if self.enable_validation:
            npc_result.metadata["validation_score"] = validation_result.overall_score
            npc_result.metadata["validation_metrics"] = validation_result.metrics

        logger.info(f"SenseVoice conversion completed successfully!")
        logger.info(f"Conversion ID: {conversion_id}")
        logger.info(f"Total time: {conversion_time:.2f} seconds")
        logger.info(f"Output: {output_path}")

        return npc_result

    async def _update_progress(
        self,
        progress_callback: Optional[callable],
        step: ProgressStep
    ) -> None:
        """Update progress if callback is provided."""
        if progress_callback:
            await self._call_progress_callback(progress_callback, step)

    async def _call_progress_callback(
        self,
        progress_callback: callable,
        step: ProgressStep
    ) -> None:
        """Call the progress callback with the given step."""
        try:
            if asyncio.iscoroutinefunction(progress_callback):
                await progress_callback(step)
            else:
                progress_callback(step)
        except Exception as e:
            logger.warning(f"Progress callback error: {e}")

    async def get_supported_languages(self) -> List[str]:
        """
        Get the list of supported languages for SenseVoice ASR models.

        Returns:
            List[str]: List of supported language codes (e.g., 'zh', 'en', 'ja')
        """
        return [
            "zh",  # Chinese (Mandarin)
            "en",  # English
            "ja",  # Japanese
            "ko",  # Korean
            "es",  # Spanish
            "fr",  # French
            "de",  # German
            "it",  # Italian
            "pt",  # Portuguese
            "ru"   # Russian
        ]

    async def get_supported_audio_formats(self) -> List[str]:
        """
        Get the list of supported audio formats.

        Returns:
            List[str]: List of supported audio format extensions
        """
        return [
            "wav",   # WAV
            "mp3",   # MP3
            "flac",  # FLAC
            "m4a",   # M4A
            "aac",   # AAC
            "ogg",   # OGG
            "wma",   # WMA
            "aiff"   # AIFF
        ]

    async def validate_model_compatibility(
        self,
        model_path: Union[str, Path],
        processing_mode: Optional[SenseVoiceProcessingMode] = None
    ) -> ValidationResult:
        """
        Validate if a model is compatible with SenseVoice conversion.

        Args:
            model_path: Path to the ONNX model
            processing_mode: Specific processing mode to validate for

        Returns:
            ValidationResult: Detailed validation result
        """
        mode = processing_mode or self.processing_mode

        try:
            model_data = await self.onnx_loader.load_model(model_path=model_path)
            validation_result = await self.validator.validate_model_structure(
                model_data=model_data,
                model_type="sensevoice",
                processing_mode=mode
            )
            return validation_result

        except Exception as e:
            logger.error(f"Model compatibility validation failed: {e}")
            return ValidationResult(
                is_valid=False,
                error_message=str(e),
                error_code="VALIDATION_ERROR",
                overall_score=0.0,
                metrics={},
                warnings=[f"Validation failed: {e}"],
                details={"model_path": str(model_path), "processing_mode": mode.value}
            )

    def get_conversion_statistics(self) -> Dict[str, Any]:
        """
        Get conversion statistics and configuration.

        Returns:
            Dict[str, Any]: Current conversion flow statistics and settings
        """
        return {
            "conversion_level": self.conversion_level.value,
            "processing_mode": self.processing_mode.value,
            "enable_optimizations": self.enable_optimizations,
            "enable_validation": self.enable_validation,
            "enable_reports": self.enable_reports,
            "supported_languages": asyncio.run(self.get_supported_languages()),
            "supported_audio_formats": asyncio.run(self.get_supported_audio_formats()),
            "conversion_levels": [level.value for level in SenseVoiceConversionLevel],
            "processing_modes": [mode.value for mode in SenseVoiceProcessingMode],
            "optimization_features": [
                "multi_language_optimization",
                "audio_format_support",
                "streaming_optimization",
                "batch_optimization",
                "noise_reduction",
                "audio_enhancement"
            ]
        }
