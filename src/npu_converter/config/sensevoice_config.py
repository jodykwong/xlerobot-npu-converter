"""
SenseVoice ASR Configuration Module

This module provides configuration templates and strategies for SenseVoice ASR models.
Integrates with Story 1.4 ConfigurationManager and Story 2.3 complete flow.

Key Features:
- Multi-language ASR parameter configuration
- Audio format support configuration
- Processing mode configuration (streaming, batch, interactive)
- Performance optimization settings
- Accuracy vs speed trade-offs

Author: Story 2.3 Implementation
Version: 1.0.0
Date: 2025-10-28
"""

from typing import Any, Dict, List, Optional
from pathlib import Path
import yaml

from ..manager import ConfigurationManager
from ...core.models.config_model import ConfigModel


class SenseVoiceConfigStrategy:
    """
    Configuration strategy for SenseVoice ASR models.

    Provides complete parameter configuration support for AC3.
    Integrates with ConfigurationManager from Story 1.4.
    """

    def __init__(self):
        """Initialize SenseVoice configuration strategy."""
        self.model_type = "sensevoice"
        self.config_template = self._load_default_template()

    def _load_default_template(self) -> Dict[str, Any]:
        """Load default configuration template for SenseVoice."""
        return {
            "model": {
                "type": "sensevoice",
                "version": "1.0.0",
                "languages": ["zh", "en"],  # Default supported languages
                "voice_activity_detection": True,
                "noise_reduction": True
            },
            "conversion": {
                "level": "production",  # basic, standard, enhanced, production
                "input_format": "onnx",
                "output_format": "bpu",
                "target_hardware": "horizon_x5",
                "processing_mode": "batch",  # streaming, batch, interactive
                "optimization": {
                    "multi_language_optimization": True,
                    "audio_format_support": True,
                    "streaming_optimization": False,
                    "batch_optimization": True,
                    "noise_reduction": True,
                    "audio_enhancement": True
                }
            },
            "audio_parameters": {
                "sample_rate": 16000,
                "bit_depth": 16,
                "channels": 1,  # mono
                "format": "wav",  # wav, mp3, flac
                "frame_length": 25,  # ms
                "hop_length": 10,  # ms
                "n_mels": 80,
                "fmax": 8000,
                "normalize": True,
                "pre_emphasis": 0.97
            },
            "asr_parameters": {
                "confidence_threshold": 0.7,
                "language_detection": True,
                "endpoint_detection": True,
                "max_segment_duration": 30,  # seconds
                "min_segment_duration": 0.5,  # seconds
                "silence_duration": 0.5,  # seconds
                "vad_threshold": 0.5,
                "vad_min_duration": 100  # ms
            },
            "processing": {
                "batch_size": 32,
                "num_workers": 4,
                "buffer_size": 1024,
                "chunk_size": 512,
                "overlap": 0.5,
                "streaming": {
                    "buffer_size": 1024,
                    "chunk_size": 512,
                    "overlap_ms": 10,
                    "real_time_factor": 1.0,
                    "max_delay_ms": 100
                },
                "interactive": {
                    "response_time_ms": 200,
                    "confidence_threshold": 0.7,
                    "enable_correction": True
                }
            },
            "quality": {
                "accuracy_target": 0.95,
                "speed_target_ms": 200,
                "precision_threshold": 0.98,
                "success_rate_threshold": 0.95,
                "validation_level": "comprehensive"
            },
            "output": {
                "formats": ["json", "html", "pdf"],
                "include_metrics": True,
                "include_optimization_details": True,
                "include_audio_analysis": True
            },
            "validation": {
                "strict_mode": True,
                "enable_validation": True,
                "validation_dimensions": ["structure", "accuracy", "performance", "compatibility", "quality"],
                "precision_threshold": 0.98,
                "success_rate_threshold": 0.95,
                "validation_level": "comprehensive"
            }
        }

    def create_config(self, custom_params: Optional[Dict[str, Any]] = None) -> ConfigModel:
        """
        Create a ConfigModel with SenseVoice configuration.

        Args:
            custom_params: Custom parameters to override defaults

        Returns:
            ConfigModel: Configured model for SenseVoice conversion
        """
        config_dict = self.config_template.copy()

        # Apply custom parameters if provided
        if custom_params:
            config_dict = self._merge_config(config_dict, custom_params)

        # Validate configuration
        self._validate_config(config_dict)

        # Create ConfigModel
        config_model = ConfigModel(
            config_type="sensevoice",
            config_data=config_dict,
            version="1.0.0",
            metadata={
                "model_type": "sensevoice",
                "created_by": "SenseVoiceConfigStrategy",
                "description": "Configuration for SenseVoice ASR model conversion"
            }
        )

        return config_model

    def load_from_file(self, config_file: Union[str, Path]) -> ConfigModel:
        """
        Load configuration from YAML file.

        Args:
            config_file: Path to configuration file

        Returns:
            ConfigModel: Loaded configuration model
        """
        config_path = Path(config_file)

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)

        # Validate loaded configuration
        self._validate_config(config_data)

        # Create ConfigModel
        config_model = ConfigModel(
            config_type="sensevoice",
            config_data=config_data,
            version="1.0.0",
            metadata={
                "model_type": "sensevoice",
                "loaded_from": str(config_path),
                "created_by": "SenseVoiceConfigStrategy"
            }
        )

        return config_model

    def save_to_file(
        self,
        config_model: ConfigModel,
        output_file: Union[str, Path],
        overwrite: bool = False
    ) -> None:
        """
        Save configuration to YAML file.

        Args:
            config_model: Configuration model to save
            output_file: Output file path
            overwrite: Whether to overwrite existing file
        """
        output_path = Path(output_file)

        if output_path.exists() and not overwrite:
            raise FileExistsError(f"Configuration file already exists: {output_path}")

        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(
                config_model.config_data,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False
            )

        logger.info(f"Configuration saved to: {output_path}")

    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Merge configuration dictionaries recursively."""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value

        return result

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration parameters."""
        # Check required sections
        required_sections = ["model", "conversion", "audio_parameters", "asr_parameters"]
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing required configuration section: {section}")

        # Validate conversion level
        valid_levels = ["basic", "standard", "enhanced", "production"]
        if config["conversion"]["level"] not in valid_levels:
            raise ValueError(f"Invalid conversion level: {config['conversion']['level']}")

        # Validate processing mode
        valid_modes = ["streaming", "batch", "interactive"]
        if config["conversion"]["processing_mode"] not in valid_modes:
            raise ValueError(f"Invalid processing mode: {config['conversion']['processing_mode']}")

        # Validate audio parameters
        audio_params = config["audio_parameters"]
        if not (8000 <= audio_params["sample_rate"] <= 48000):
            raise ValueError(f"Invalid sample rate: {audio_params['sample_rate']}")

        if audio_params["channels"] not in [1, 2]:
            raise ValueError(f"Invalid channel count: {audio_params['channels']}")

        # Validate quality thresholds
        quality = config["quality"]
        if not (0 < quality["accuracy_target"] <= 1):
            raise ValueError(f"Invalid accuracy target: {quality['accuracy_target']}")

        logger.info("Configuration validation passed")

    def get_preset_config(self, preset_name: str) -> ConfigModel:
        """
        Get a preset configuration.

        Args:
            preset_name: Name of preset ("default", "fast", "accurate")

        Returns:
            ConfigModel: Preset configuration model
        """
        presets = {
            "default": self._default_preset(),
            "fast": self._fast_preset(),
            "accurate": self._accurate_preset()
        }

        if preset_name not in presets:
            raise ValueError(f"Unknown preset: {preset_name}")

        return self.create_config(presets[preset_name])

    def _default_preset(self) -> Dict[str, Any]:
        """Default preset - balanced between speed and accuracy."""
        return {
            "model": {
                "languages": ["zh", "en"],
                "voice_activity_detection": True,
                "noise_reduction": True
            },
            "conversion": {
                "level": "standard",
                "processing_mode": "batch"
            },
            "audio_parameters": {
                "sample_rate": 16000,
                "format": "wav"
            },
            "asr_parameters": {
                "confidence_threshold": 0.7
            },
            "quality": {
                "accuracy_target": 0.95,
                "speed_target_ms": 200
            }
        }

    def _fast_preset(self) -> Dict[str, Any]:
        """Fast preset - optimized for speed."""
        return {
            "model": {
                "languages": ["zh"],  # Single language for speed
                "voice_activity_detection": True,
                "noise_reduction": False  # Disable for speed
            },
            "conversion": {
                "level": "basic",
                "processing_mode": "streaming"
            },
            "audio_parameters": {
                "sample_rate": 16000,
                "n_mels": 64,  # Reduced features
                "format": "wav"
            },
            "asr_parameters": {
                "confidence_threshold": 0.6,  # Lower threshold
                "max_segment_duration": 10  # Shorter segments
            },
            "processing": {
                "batch_size": 64,  # Larger batch
                "num_workers": 8
            },
            "quality": {
                "accuracy_target": 0.90,
                "speed_target_ms": 100
            }
        }

    def _accurate_preset(self) -> Dict[str, Any]:
        """Accurate preset - optimized for accuracy."""
        return {
            "model": {
                "languages": ["zh", "en", "ja"],  # Multiple languages
                "voice_activity_detection": True,
                "noise_reduction": True
            },
            "conversion": {
                "level": "production",
                "processing_mode": "batch"
            },
            "audio_parameters": {
                "sample_rate": 16000,
                "n_mels": 80,  # Full features
                "fmax": 8000,
                "format": "wav"
            },
            "asr_parameters": {
                "confidence_threshold": 0.8,  # Higher threshold
                "max_segment_duration": 60  # Longer segments
            },
            "processing": {
                "batch_size": 16,  # Smaller batch
                "num_workers": 2
            },
            "quality": {
                "accuracy_target": 0.98,
                "speed_target_ms": 300
            }
        }

    def list_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
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

    def list_supported_audio_formats(self) -> List[str]:
        """Get list of supported audio formats."""
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

    def get_configuration_summary(self, config_model: ConfigModel) -> Dict[str, Any]:
        """
        Get a summary of the configuration.

        Args:
            config_model: Configuration model

        Returns:
            Dict[str, Any]: Configuration summary
        """
        data = config_model.config_data

        return {
            "model_type": data["model"]["type"],
            "version": data["model"]["version"],
            "languages": data["model"]["languages"],
            "conversion_level": data["conversion"]["level"],
            "processing_mode": data["conversion"]["processing_mode"],
            "audio_format": data["audio_parameters"]["format"],
            "sample_rate": data["audio_parameters"]["sample_rate"],
            "accuracy_target": data["quality"]["accuracy_target"],
            "speed_target_ms": data["quality"]["speed_target_ms"],
            "optimizations_enabled": sum(1 for v in data["conversion"]["optimization"].values() if v),
            "validation_enabled": data["validation"]["enable_validation"]
        }


# Create default instance
sensevoice_config = SenseVoiceConfigStrategy()

logger = logging.getLogger(__name__)
