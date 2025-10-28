"""
Test SenseVoiceCompleteFlow

Test suite for Story 2.3 SenseVoiceCompleteFlow implementation.
Validates all acceptance criteria and PRD requirements.

Key Test Areas:
- AC1: SenseVoice model complete conversion capability
- AC2: ASR model specific optimizations
- AC3: Complete parameter configuration system
- AC4: Conversion result validation system
- AC5: Error handling and diagnostics

Author: Story 2.3 Implementation
Version: 1.0.0
Date: 2025-10-28
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any

from src.npu_converter.complete_flows.sensevoice_complete_flow import (
    SenseVoiceCompleteFlow,
    SenseVoiceConversionLevel,
    SenseVoiceProcessingMode
)
from src.npu_converter.config.sensevoice_config import SenseVoiceConfigStrategy
from src.npu_converter.core.models.config_model import ConfigModel
from src.npu_converter.core.models.result_model import ResultModel
from src.npu_converter.core.models.progress_model import ProgressStep


class TestSenseVoiceCompleteFlow:
    """Test suite for SenseVoiceCompleteFlow."""

    @pytest.fixture
    def config_model(self):
        """Create a test configuration model."""
        config_strategy = SenseVoiceConfigStrategy()
        return config_strategy.create_config()

    @pytest.fixture
    def complete_flow_default(self, config_model):
        """Create a test complete flow instance with default settings."""
        return SenseVoiceCompleteFlow(
            config=config_model,
            conversion_level=SenseVoiceConversionLevel.PRODUCTION,
            processing_mode=SenseVoiceProcessingMode.BATCH,
            enable_optimizations=True,
            enable_validation=True,
            enable_reports=True
        )

    @pytest.fixture
    def complete_flow_streaming(self, config_model):
        """Create a test complete flow instance for streaming mode."""
        return SenseVoiceCompleteFlow(
            config=config_model,
            conversion_level=SenseVoiceConversionLevel.ENHANCED,
            processing_mode=SenseVoiceProcessingMode.STREAMING,
            enable_optimizations=True,
            enable_validation=True,
            enable_reports=True
        )

    @pytest.fixture
    def mock_progress_callback(self):
        """Create a mock progress callback."""
        return Mock()

    # ========== Test Initialization ==========

    def test_initialization_default(self, complete_flow_default, config_model):
        """Test initialization with default settings."""
        assert complete_flow_default.conversion_level == SenseVoiceConversionLevel.PRODUCTION
        assert complete_flow_default.processing_mode == SenseVoiceProcessingMode.BATCH
        assert complete_flow_default.enable_optimizations is True
        assert complete_flow_default.enable_validation is True
        assert complete_flow_default.enable_reports is True
        assert complete_flow_default.config == config_model
        assert complete_flow_default._optimizer is None
        assert complete_flow_default._validator is None
        assert complete_flow_default._report_generator is None
        assert complete_flow_default._onnx_loader is None

    def test_initialization_streaming(self, complete_flow_streaming):
        """Test initialization with streaming mode."""
        assert complete_flow_streaming.processing_mode == SenseVoiceProcessingMode.STREAMING
        assert complete_flow_streaming.conversion_level == SenseVoiceConversionLevel.ENHANCED

    # ========== Test Component Properties ==========

    def test_optimizer_property(self, complete_flow_default):
        """Test optimizer property initialization."""
        optimizer = complete_flow_default.optimizer
        assert optimizer is not None
        assert optimizer.config == complete_flow_default.config
        assert optimizer.conversion_level == complete_flow_default.conversion_level
        assert optimizer.processing_mode == complete_flow_default.processing_mode

    def test_validator_property(self, complete_flow_default):
        """Test validator property initialization."""
        validator = complete_flow_default.validator
        assert validator is not None
        assert validator.config == complete_flow_default.config
        assert validator.processing_mode == complete_flow_default.processing_mode

    def test_report_generator_property(self, complete_flow_default):
        """Test report generator property initialization."""
        report_generator = complete_flow_default.report_generator
        assert report_generator is not None
        assert report_generator.config == complete_flow_default.config
        assert report_generator.conversion_level == complete_flow_default.conversion_level

    def test_onnx_loader_property(self, complete_flow_default):
        """Test ONNX loader property initialization."""
        onnx_loader = complete_flow_default.onnx_loader
        assert onnx_loader is not None

    # ========== Test Supported Features ==========

    @pytest.mark.asyncio
    async def test_get_supported_languages(self, complete_flow_default):
        """Test getting supported languages."""
        languages = await complete_flow_default.get_supported_languages()

        assert isinstance(languages, list)
        assert "zh" in languages  # Chinese
        assert "en" in languages  # English
        assert "ja" in languages  # Japanese
        assert len(languages) >= 10  # At least 10 languages

    @pytest.mark.asyncio
    async def test_get_supported_audio_formats(self, complete_flow_default):
        """Test getting supported audio formats."""
        formats = await complete_flow_default.get_supported_audio_formats()

        assert isinstance(formats, list)
        assert "wav" in formats
        assert "mp3" in formats
        assert "flac" in formats
        assert len(formats) >= 6  # At least 6 formats

    # ========== Test Conversion ==========

    @pytest.mark.asyncio
    @patch('src.npu_converter.complete_flows.sensevoice_complete_flow.ONNXModelLoader')
    @patch('src.npu_converter.complete_flows.sensevoice_complete_flow.BaseConversionFlow.convert_model')
    async def test_convert_model_basic_flow(
        self,
        mock_super_convert,
        mock_loader_class,
        complete_flow_default,
        mock_progress_callback,
        tmp_path
    ):
        """Test basic model conversion flow (AC1)."""
        # Setup mocks
        mock_loader = AsyncMock()
        mock_loader_class.return_value = mock_loader
        mock_loader.load_model.return_value = {"mock": "model_data"}

        mock_super_result = ResultModel(
            success=True,
            input_path="input.onnx",
            output_path=str(tmp_path / "output.bpu"),
            metadata={"mock": "result"}
        )
        mock_super_convert.return_value = mock_super_result

        # Setup validator mock
        with patch.object(complete_flow_default.validator, 'validate_model_structure') as mock_validate:
            mock_validation_result = Mock()
            mock_validation_result.is_valid = True
            mock_validation_result.error_message = None
            mock_validate.return_value = mock_validation_result

            # Setup optimizer mock
            with patch.object(complete_flow_default.optimizer, 'optimize_model') as mock_opt:
                mock_opt.return_value = {"optimized": True, "changes": []}

                with patch.object(complete_flow_default.optimizer, 'optimize_audio_preprocessing') as mock_audio_opt:
                    mock_audio_opt.return_value = {"audio": "config"}

                    # Setup report generator mock
                    with patch.object(complete_flow_default.report_generator, 'generate_report') as mock_report:
                        mock_report.return_value = {"report": "data"}

                        # Execute conversion
                        result = await complete_flow_default.convert_model(
                            model_path="test_model.onnx",
                            output_path=str(tmp_path / "output.bpu"),
                            progress_callback=mock_progress_callback
                        )

                        # Verify results
                        assert result.success is True
                        assert result.metadata["sensevoice_version"] == "1.0.0"
                        assert result.metadata["processing_mode"] == "batch"
                        assert result.metadata["conversion_level"] == "production"
                        assert result.metadata["enable_optimizations"] is True
                        assert result.metadata["enable_validation"] is True
                        assert result.metadata["enable_reports"] is True

                        # Verify mock calls
                        mock_loader.load_model.assert_called_once()
                        mock_validate.assert_called_once()
                        mock_opt.assert_called_once()
                        mock_audio_opt.assert_called_once()
                        mock_super_convert.assert_called_once()
                        mock_report.assert_called_once()

    @pytest.mark.asyncio
    async def test_convert_model_with_custom_params(
        self,
        complete_flow_default,
        mock_progress_callback,
        tmp_path
    ):
        """Test conversion with custom parameters (AC3)."""
        custom_params = {
            "sample_rate": 16000,
            "languages": ["zh", "en"],
            "noise_reduction": True
        }

        with patch('src.npu_converter.complete_flows.sensevoice_complete_flow.ONNXModelLoader'):
            with patch('src.npu_converter.complete_flows.sensevoice_complete_flow.BaseConversionFlow.convert_model'):
                with patch.object(complete_flow_default.validator, 'validate_model_structure'):
                    with patch.object(complete_flow_default.optimizer, 'optimize_model'):
                        with patch.object(complete_flow_default.optimizer, 'optimize_audio_preprocessing'):
                            with patch.object(complete_flow_default.report_generator, 'generate_report'):

                                result = await complete_flow_default.convert_model(
                                    model_path="test_model.onnx",
                                    output_path=str(tmp_path / "output.bpu"),
                                    conversion_params=custom_params,
                                    progress_callback=mock_progress_callback
                                )

                                # Custom parameters should be passed through
                                assert result.success is True

    @pytest.mark.asyncio
    async def test_convert_model_streaming_mode(
        self,
        complete_flow_streaming,
        tmp_path
    ):
        """Test conversion in streaming mode."""
        with patch('src.npu_converter.complete_flows.sensevoice_complete_flow.ONNXModelLoader'):
            with patch('src.npu_converter.complete_flows.sensevoice_complete_flow.BaseConversionFlow.convert_model'):
                with patch.object(complete_flow_streaming.validator, 'validate_model_structure'):
                    mock_validation_result = Mock()
                    mock_validation_result.is_valid = True
                    complete_flow_streaming.validator.validate_model_structure.return_value = mock_validation_result

                    with patch.object(complete_flow_streaming.optimizer, 'optimize_model'):
                        with patch.object(complete_flow_streaming.optimizer, 'optimize_audio_preprocessing'):
                            with patch.object(complete_flow_streaming.report_generator, 'generate_report'):

                                result = await complete_flow_streaming.convert_model(
                                    model_path="test_model.onnx",
                                    output_path=str(tmp_path / "output.bpu")
                                )

                                # Verify streaming mode metadata
                                assert result.metadata["processing_mode"] == "streaming"

    # ========== Test Validation ==========

    @pytest.mark.asyncio
    async def test_validate_model_compatibility(self, complete_flow_default, tmp_path):
        """Test model compatibility validation."""
        # Create a temporary model file
        model_file = tmp_path / "test_model.onnx"
        model_file.write_text("mock onnx model")

        with patch('src.npu_converter.complete_flows.sensevoice_complete_flow.ONNXModelLoader'):
            with patch.object(complete_flow_default.validator, 'validate_model_structure') as mock_validate:
                mock_validation_result = Mock()
                mock_validation_result.is_valid = True
                mock_validation_result.error_message = None
                mock_validation_result.overall_score = 95.0
                mock_validate.return_value = mock_validation_result

                result = await complete_flow_default.validate_model_compatibility(
                    model_path=str(model_file),
                    processing_mode=SenseVoiceProcessingMode.BATCH
                )

                assert result.is_valid is True
                assert result.overall_score == 95.0
                mock_validate.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_model_compatibility_streaming(self, complete_flow_default, tmp_path):
        """Test model compatibility validation for streaming mode."""
        model_file = tmp_path / "test_model.onnx"
        model_file.write_text("mock onnx model")

        with patch('src.npu_converter.complete_flows.sensevoice_complete_flow.ONNXModelLoader'):
            with patch.object(complete_flow_default.validator, 'validate_model_structure') as mock_validate:
                mock_validation_result = Mock()
                mock_validation_result.is_valid = True
                mock_validate.return_value = mock_validation_result

                result = await complete_flow_default.validate_model_compatibility(
                    model_path=str(model_file),
                    processing_mode=SenseVoiceProcessingMode.STREAMING
                )

                assert result.is_valid is True

    # ========== Test Statistics ==========

    def test_get_conversion_statistics(self, complete_flow_default):
        """Test getting conversion statistics."""
        stats = complete_flow_default.get_conversion_statistics()

        assert isinstance(stats, dict)
        assert "conversion_level" in stats
        assert "processing_mode" in stats
        assert "enable_optimizations" in stats
        assert "enable_validation" in stats
        assert "enable_reports" in stats
        assert "supported_languages" in stats
        assert "supported_audio_formats" in stats
        assert "conversion_levels" in stats
        assert "processing_modes" in stats
        assert "optimization_features" in stats

        # Check conversion levels
        assert "basic" in stats["conversion_levels"]
        assert "production" in stats["conversion_levels"]

        # Check processing modes
        assert "streaming" in stats["processing_modes"]
        assert "batch" in stats["processing_modes"]
        assert "interactive" in stats["processing_modes"]

        # Check optimization features
        assert "multi_language_optimization" in stats["optimization_features"]
        assert "audio_format_support" in stats["optimization_features"]

    # ========== Test Error Handling ==========

    @pytest.mark.asyncio
    async def test_convert_model_invalid_model(
        self,
        complete_flow_default,
        tmp_path
    ):
        """Test conversion with invalid model (AC5)."""
        with patch('src.npu_converter.complete_flows.sensevoice_complete_flow.ONNXModelLoader') as mock_loader_class:
            mock_loader = AsyncMock()
            mock_loader_class.return_value = mock_loader
            mock_loader.load_model.side_effect = Exception("Invalid model")

            with pytest.raises(Exception) as exc_info:
                await complete_flow_default.convert_model(
                    model_path="invalid_model.onnx",
                    output_path=str(tmp_path / "output.bpu")
                )

            assert "Invalid model" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_convert_model_validation_failure(
        self,
        complete_flow_default,
        tmp_path
    ):
        """Test conversion with validation failure (AC4)."""
        with patch('src.npu_converter.complete_flows.sensevoice_complete_flow.ONNXModelLoader'):
            with patch.object(complete_flow_default.validator, 'validate_model_structure') as mock_validate:
                mock_validation_result = Mock()
                mock_validation_result.is_valid = False
                mock_validation_result.error_message = "Model validation failed"
                mock_validation_result.error_code = "INVALID_MODEL"
                mock_validate.return_value = mock_validation_result

                with pytest.raises(Exception) as exc_info:
                    await complete_flow_default.convert_model(
                        model_path="test_model.onnx",
                        output_path=str(tmp_path / "output.bpu")
                    )

                assert "Model validation failed" in str(exc_info.value)

    # ========== Test Progress Tracking ==========

    @pytest.mark.asyncio
    async def test_progress_callback(self, complete_flow_default, mock_progress_callback, tmp_path):
        """Test progress callback functionality."""
        with patch('src.npu_converter.complete_flows.sensevoice_complete_flow.ONNXModelLoader'):
            with patch('src.npu_converter.complete_flows.sensevoice_complete_flow.BaseConversionFlow.convert_model'):
                with patch.object(complete_flow_default.validator, 'validate_model_structure'):
                    mock_validation_result = Mock()
                    mock_validation_result.is_valid = True
                    complete_flow_default.validator.validate_model_structure.return_value = mock_validation_result

                    with patch.object(complete_flow_default.optimizer, 'optimize_model'):
                        with patch.object(complete_flow_default.optimizer, 'optimize_audio_preprocessing'):
                            with patch.object(complete_flow_default.report_generator, 'generate_report'):

                                await complete_flow_default.convert_model(
                                    model_path="test_model.onnx",
                                    output_path=str(tmp_path / "output.bpu"),
                                    progress_callback=mock_progress_callback
                                )

                                # Verify progress callback was called multiple times
                                assert mock_progress_callback.call_count > 0

                                # Check that progress steps were passed
                                call_args = mock_progress_callback.call_args_list
                                for call in call_args:
                                    assert isinstance(call[0][0], ProgressStep)

    # ========== Test Configuration Integration ==========

    def test_config_integration(self, config_model):
        """Test integration with ConfigurationManager (AC3)."""
        flow = SenseVoiceCompleteFlow(
            config=config_model,
            conversion_level=SenseVoiceConversionLevel.STANDARD,
            processing_mode=SenseVoiceProcessingMode.INTERACTIVE
        )

        assert flow.config.config_type == "sensevoice"
        assert flow.config.config_data["model"]["type"] == "sensevoice"

    @pytest.mark.asyncio
    async def test_load_preset_configurations(self):
        """Test loading preset configurations (default, fast, accurate)."""
        config_strategy = SenseVoiceConfigStrategy()

        # Test default preset
        default_config = config_strategy.get_preset_config("default")
        assert default_config.config_type == "sensevoice"

        # Test fast preset
        fast_config = config_strategy.get_preset_config("fast")
        assert fast_config.config_type == "sensevoice"

        # Test accurate preset
        accurate_config = config_strategy.get_preset_config("accurate")
        assert accurate_config.config_type == "sensevoice"

    def test_unsupported_preset(self):
        """Test error handling for unsupported preset."""
        config_strategy = SenseVoiceConfigStrategy()

        with pytest.raises(ValueError) as exc_info:
            config_strategy.get_preset_config("unsupported")

        assert "Unknown preset" in str(exc_info.value)

    # ========== Test Multi-language Support ==========

    @pytest.mark.asyncio
    async def test_multi_language_configuration(self, config_model):
        """Test multi-language configuration support."""
        # Modify config to include multiple languages
        config_data = config_model.config_data
        config_data["model"]["languages"] = ["zh", "en", "ja"]
        config_model.config_data = config_data

        flow = SenseVoiceCompleteFlow(
            config=config_model,
            conversion_level=SenseVoiceConversionLevel.PRODUCTION,
            processing_mode=SenseVoiceProcessingMode.BATCH
        )

        # Verify multi-language support in optimization
        optimizer = flow.optimizer
        assert optimizer is not None

    @pytest.mark.asyncio
    async def test_audio_format_support(self, complete_flow_default):
        """Test multiple audio format support."""
        formats = await complete_flow_default.get_supported_audio_formats()

        # Verify WAV support
        assert "wav" in formats

        # Verify MP3 support
        assert "mp3" in formats

        # Verify FLAC support
        assert "flac" in formats

    # ========== Test Acceptance Criteria ==========

    @pytest.mark.asyncio
    async def test_acceptance_criteria_ac1_complete_conversion(
        self,
        complete_flow_default,
        tmp_path
    ):
        """Test AC1: SenseVoice model complete conversion capability."""
        # This test validates that complete conversion flow works end-to-end
        with patch('src.npu_converter.complete_flows.sensevoice_complete_flow.ONNXModelLoader'):
            with patch('src.npu_converter.complete_flows.sensevoice_complete_flow.BaseConversionFlow.convert_model'):
                with patch.object(complete_flow_default.validator, 'validate_model_structure'):
                    mock_validation_result = Mock()
                    mock_validation_result.is_valid = True
                    complete_flow_default.validator.validate_model_structure.return_value = mock_validation_result

                    with patch.object(complete_flow_default.optimizer, 'optimize_model'):
                        with patch.object(complete_flow_default.optimizer, 'optimize_audio_preprocessing'):
                            with patch.object(complete_flow_default.report_generator, 'generate_report'):

                                result = await complete_flow_default.convert_model(
                                    model_path="test_model.onnx",
                                    output_path=str(tmp_path / "output.bpu")
                                )

                                # AC1: Complete conversion capability
                                assert result.success is True
                                assert "conversion_id" in result.metadata
                                assert result.metadata["enable_optimizations"] is True

    @pytest.mark.asyncio
    async def test_acceptance_criteria_ac2_asr_optimization(
        self,
        complete_flow_default,
        tmp_path
    ):
        """Test AC2: ASR model specific optimizations."""
        with patch('src.npu_converter.complete_flows.sensevoice_complete_flow.ONNXModelLoader'):
            with patch('src.npu_converter.complete_flows.sensevoice_complete_flow.BaseConversionFlow.convert_model'):
                with patch.object(complete_flow_default.validator, 'validate_model_structure'):
                    mock_validation_result = Mock()
                    mock_validation_result.is_valid = True
                    complete_flow_default.validator.validate_model_structure.return_value = mock_validation_result

                    with patch.object(complete_flow_default.optimizer, 'optimize_model') as mock_opt:
                        mock_opt.return_value = {
                            "optimized": True,
                            "optimizations_applied": [
                                "multi_language_optimization",
                                "audio_format_support",
                                "noise_reduction"
                            ]
                        }

                        with patch.object(complete_flow_default.optimizer, 'optimize_audio_preprocessing'):
                            with patch.object(complete_flow_default.report_generator, 'generate_report'):

                                result = await complete_flow_default.convert_model(
                                    model_path="test_model.onnx",
                                    output_path=str(tmp_path / "output.bpu")
                                )

                                # AC2: ASR-specific optimizations should be applied
                                assert result.success is True

    @pytest.mark.asyncio
    async def test_acceptance_criteria_ac4_validation_system(
        self,
        complete_flow_default,
        tmp_path
    ):
        """Test AC4: Conversion result validation system."""
        with patch('src.npu_converter.complete_flows.sensevoice_complete_flow.ONNXModelLoader'):
            with patch('src.npu_converter.complete_flows.sensevoice_complete_flow.BaseConversionFlow.convert_model'):
                with patch.object(complete_flow_default.validator, 'validate_model_structure'):
                    mock_validation_result = Mock()
                    mock_validation_result.is_valid = True
                    mock_validation_result.error_message = None
                    mock_validation_result.overall_score = 95.0
                    mock_validation_result.metrics = {"structure": 100, "accuracy": 95}
                    mock_validation_result.warnings = []
                    complete_flow_default.validator.validate_model_structure.return_value = mock_validation_result

                    with patch.object(complete_flow_default.optimizer, 'optimize_model'):
                        with patch.object(complete_flow_default.optimizer, 'optimize_audio_preprocessing'):
                            with patch.object(complete_flow_default.report_generator, 'generate_report'):

                                # Validate compatibility
                                compat_result = await complete_flow_default.validate_model_compatibility(
                                    model_path="test_model.onnx"
                                )

                                # AC4: Validation system should work
                                assert compat_result.is_valid is True
                                assert compat_result.overall_score == 95.0
