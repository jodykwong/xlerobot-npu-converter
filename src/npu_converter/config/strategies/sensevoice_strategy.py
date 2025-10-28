"""
SenseVoice Configuration Strategy

Model-specific configuration strategy for SenseVoice ASR models.
Implements the strategy pattern as defined in the architecture document.

Handles SenseVoice-specific configuration parameters like:
- Audio processing parameters
- Vocabulary settings
- Model architecture specifics
- ASR-specific optimization parameters
"""

from typing import Dict, Any, List
from .base_strategy import BaseConfigStrategy, ConfigValidationRule


class SenseVoiceConfigStrategy(BaseConfigStrategy):
    """Configuration strategy for SenseVoice ASR models."""

    def get_model_type(self) -> str:
        """Get the model type this strategy handles."""
        return "sensevoice"

    def get_default_template(self) -> Dict[str, Any]:
        """Get the default configuration template for SenseVoice."""
        return {
            "project": {
                "name": "xlerobot",
                "version": "1.0.0",
                "model_type": "sensevoice"
            },
            "hardware": {
                "target_device": "horizon_x5",
                "optimization_level": "O2",
                "memory_limit": "8GB",
                "compute_units": 10,
                "cache_size": "256MB"
            },
            "conversion_params": {
                "input_format": "onnx",
                "output_format": "bpu",
                "precision": "int8",
                "calibration_method": "minmax",
                "batch_size": 1,
                "num_workers": 4
            },
            "model_specific": {
                "sensevoice": {
                    # Basic ASR parameters
                    "sample_rate": 16000,
                    "audio_length": 30,
                    "vocab_size": 10000,
                    "mel_bins": 80,
                    "frame_length": 25,
                    "frame_shift": 10,
                    "normalize": True,
                    "preemphasis": 0.97,
                    "n_fft": 512,
                    "hop_length": 160,
                    "win_length": 400,
                    "n_mels": 80,
                    "f_min": 0.0,
                    "f_max": 8000.0,

                    # ASR-specific parameters
                    "language_detection": True,
                    "supported_languages": ["zh", "en", "yue", "ja"],
                    "confidence_threshold": 0.8,
                    "segmentation": True,
                    "vad_enabled": True,

                    # Model optimization parameters
                    "beam_size": 5,
                    "length_penalty": 1.0,
                    "coverage_penalty": 1.0,
                    "repetition_penalty": 1.0
                }
            },
            "performance": {
                "target_latency_ms": 100,
                "max_realtime_factor": 0.1,
                "enable_streaming": False
            }
        }

    def validate_model_specific_config(self) -> bool:
        """Validate SenseVoice-specific configuration parameters."""
        sensevoice_config = self.config.get("model_specific", {}).get("sensevoice", {})

        if not sensevoice_config:
            raise ValueError("SenseVoice configuration section is missing")

        # Validate required SenseVoice fields
        required_fields = ["sample_rate", "audio_length", "vocab_size"]
        for field in required_fields:
            if field not in sensevoice_config:
                raise ValueError(f"Required SenseVoice field '{field}' is missing")

        # Validate sample rate
        sample_rate = sensevoice_config.get("sample_rate")
        if sample_rate not in [8000, 16000, 22050, 44100]:
            raise ValueError(f"Unsupported sample rate: {sample_rate}. Supported rates: 8000, 16000, 22050, 44100")

        # Validate audio length
        audio_length = sensevoice_config.get("audio_length")
        if not isinstance(audio_length, (int, float)) or audio_length <= 0 or audio_length > 300:
            raise ValueError(f"Audio length must be positive and <= 300 seconds, got: {audio_length}")

        # Validate vocabulary size
        vocab_size = sensevoice_config.get("vocab_size")
        if not isinstance(vocab_size, int) or vocab_size <= 0 or vocab_size > 100000:
            raise ValueError(f"Vocabulary size must be positive integer <= 100000, got: {vocab_size}")

        return True

    def get_model_specific_fields(self) -> List[str]:
        """Get list of SenseVoice-specific configuration field paths."""
        return [
            "model_specific.sensevoice.sample_rate",
            "model_specific.sensevoice.audio_length",
            "model_specific.sensevoice.vocab_size",
            "model_specific.sensevoice.mel_bins",
            "model_specific.sensevoice.frame_length",
            "model_specific.sensevoice.frame_shift",
            "model_specific.sensevoice.normalize",
            "model_specific.sensevoice.preemphasis",
            "model_specific.sensevoice.n_fft",
            "model_specific.sensevoice.hop_length",
            "model_specific.sensevoice.win_length",
            "model_specific.sensevoice.n_mels",
            "model_specific.sensevoice.f_min",
            "model_specific.sensevoice.f_max",
            # ASR-specific fields
            "model_specific.sensevoice.language_detection",
            "model_specific.sensevoice.supported_languages",
            "model_specific.sensevoice.confidence_threshold",
            "model_specific.sensevoice.segmentation",
            "model_specific.sensevoice.vad_enabled",
            "model_specific.sensevoice.beam_size",
            "model_specific.sensevoice.length_penalty",
            "model_specific.sensevoice.coverage_penalty",
            "model_specific.sensevoice.repetition_penalty"
        ]

    def _setup_validation_rules(self) -> None:
        """Setup SenseVoice-specific validation rules."""
        super()._setup_validation_rules()

        # Add SenseVoice-specific validation rules
        self.validation_rules.extend([
            ConfigValidationRule(
                field_path="model_specific.sensevoice.sample_rate",
                rule_type="required",
                rule_params={},
                error_message="Sample rate is required for SenseVoice"
            ),
            ConfigValidationRule(
                field_path="model_specific.sensevoice.sample_rate",
                rule_type="enum",
                rule_params={"values": [8000, 16000, 22050, 44100]},
                error_message="Sample rate must be one of: 8000, 16000, 22050, 44100"
            ),
            ConfigValidationRule(
                field_path="model_specific.sensevoice.audio_length",
                rule_type="range",
                rule_params={"min": 0.1, "max": 300.0},
                error_message="Audio length must be between 0.1 and 300 seconds"
            ),
            ConfigValidationRule(
                field_path="model_specific.sensevoice.vocab_size",
                rule_type="range",
                rule_params={"min": 100, "max": 100000},
                error_message="Vocabulary size must be between 100 and 100000"
            ),
            ConfigValidationRule(
                field_path="performance.target_latency_ms",
                rule_type="range",
                rule_params={"min": 10, "max": 1000},
                error_message="Target latency must be between 10ms and 1000ms"
            ),
            ConfigValidationRule(
                field_path="performance.max_realtime_factor",
                rule_type="range",
                rule_params={"min": 0.01, "max": 1.0},
                error_message="Max realtime factor must be between 0.01 and 1.0"
            ),
            ConfigValidationRule(
                field_path="model_specific.sensevoice.language_detection",
                rule_type="type",
                rule_params={"type": bool},
                error_message="Language detection must be a boolean"
            ),
            ConfigValidationRule(
                field_path="model_specific.sensevoice.confidence_threshold",
                rule_type="range",
                rule_params={"min": 0.0, "max": 1.0},
                error_message="Confidence threshold must be between 0.0 and 1.0"
            )
        ])

    def get_audio_processing_config(self) -> Dict[str, Any]:
        """Get audio processing configuration for SenseVoice."""
        sensevoice_config = self.config.get("model_specific", {}).get("sensevoice", {})

        return {
            "sample_rate": sensevoice_config.get("sample_rate", 16000),
            "frame_length": sensevoice_config.get("frame_length", 25),
            "frame_shift": sensevoice_config.get("frame_shift", 10),
            "n_fft": sensevoice_config.get("n_fft", 512),
            "hop_length": sensevoice_config.get("hop_length", 160),
            "win_length": sensevoice_config.get("win_length", 400),
            "n_mels": sensevoice_config.get("n_mels", 80),
            "f_min": sensevoice_config.get("f_min", 0.0),
            "f_max": sensevoice_config.get("f_max", 8000.0),
            "normalize": sensevoice_config.get("normalize", True),
            "preemphasis": sensevoice_config.get("preemphasis", 0.97)
        }

    def get_validation_rules(self) -> List[ConfigValidationRule]:
        """Get SenseVoice specific validation rules."""
        return self.validation_rules

    def get_model_config(self) -> Dict[str, Any]:
        """Get SenseVoice model configuration."""
        sensevoice_config = self.config.get("model_specific", {}).get("sensevoice", {})

        return {
            "sample_rate": sensevoice_config.get("sample_rate", 16000),
            "audio_length": sensevoice_config.get("audio_length", 30),
            "vocab_size": sensevoice_config.get("vocab_size", 10000),
            "mel_bins": sensevoice_config.get("mel_bins", 80)
        }