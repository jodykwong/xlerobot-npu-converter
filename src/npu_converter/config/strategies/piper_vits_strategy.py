"""
Piper VITS Configuration Strategy

Model-specific configuration strategy for Piper VITS TTS models.
Implements the strategy pattern as defined in the architecture document.

Handles Piper VITS-specific configuration parameters like:
- Audio synthesis parameters
- Voice characteristics
- Model architecture specifics
- TTS-specific optimization parameters
"""

from typing import Dict, Any, List
from .base_strategy import BaseConfigStrategy, ConfigValidationRule


class PiperVITSConfigStrategy(BaseConfigStrategy):
    """Configuration strategy for Piper VITS TTS models."""

    def get_model_type(self) -> str:
        """Get the model type this strategy handles."""
        return "piper_vits"

    def get_default_template(self) -> Dict[str, Any]:
        """Get the default configuration template for Piper VITS."""
        return {
            "project": {
                "name": "xlerobot",
                "version": "1.0.0",
                "model_type": "piper_vits"
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
                "piper_vits": {
                    # Required basic fields
                    "sample_rate": 22050,
                    "mel_channels": 80,
                    "speaker_embedding": True,
                    "num_speakers": 1,
                    "speaker_id": 0,
                    "embedding_dim": 192,

                    # VITS architecture parameters
                    "inter_channels": 192,
                    "hidden_channels": 192,
                    "filter_channels": 768,
                    "n_heads": 2,
                    "n_layers": 6,
                    "kernel_size": 3,
                    "p_dropout": 0.1,

                    # Audio processing parameters
                    "n_fft": 1024,
                    "hop_size": 256,
                    "win_size": 1024,
                    "n_mels": 80,
                    "f_min": 0.0,
                    "f_max": 8000.0,

                    # Synthesis parameters
                    "noise_scale": 0.667,
                    "noise_scale_d": 0.8,
                    "length_scale": 1.0,
                    "inference_noise_scale": 0.667,
                    "max_wav_value": 32768.0,
                    "max_decoder_steps": 2000,
                    "gate_threshold": 0.5,
                    "temperature": 1.0,

                    # Advanced features
                    "use_sdp": True,
                    "use_spectral_norm": False,
                    "gin_channels": 256,
                    "postnet_embedding_dim": 512,
                    "speaker_embedding_dim": 192
                }
            },
            "performance": {
                "target_latency_ms": 200,
                "max_realtime_factor": 0.3,
                "enable_streaming": True,
                "chunk_size": 1024
            }
        }

    def validate_model_specific_config(self) -> bool:
        """Validate Piper VITS-specific configuration parameters."""
        piper_config = self.config.get("model_specific", {}).get("piper_vits", {})

        if not piper_config:
            raise ValueError("Piper VITS configuration section is missing")

        # Validate required Piper VITS fields
        required_fields = ["sample_rate", "mel_channels", "speaker_embedding"]
        for field in required_fields:
            if field not in piper_config:
                raise ValueError(f"Required Piper VITS field '{field}' is missing")

        # Validate sample rate
        sample_rate = piper_config.get("sample_rate")
        if sample_rate not in [16000, 22050, 44100]:
            raise ValueError(f"Unsupported sample rate: {sample_rate}. Supported rates: 16000, 22050, 44100")

        # Validate mel channels
        mel_channels = piper_config.get("mel_channels")
        if not isinstance(mel_channels, int) or mel_channels <= 0 or mel_channels > 128:
            raise ValueError(f"Mel channels must be positive integer <= 128, got: {mel_channels}")

        # Validate speaker embedding
        speaker_embedding = piper_config.get("speaker_embedding")
        if not isinstance(speaker_embedding, bool):
            raise ValueError(f"Speaker embedding must be boolean, got: {type(speaker_embedding)}")

        # Validate noise scale
        noise_scale = piper_config.get("noise_scale")
        if noise_scale is not None and (not isinstance(noise_scale, (int, float)) or noise_scale < 0 or noise_scale > 2):
            raise ValueError(f"Noise scale must be between 0 and 2, got: {noise_scale}")

        return True

    def get_model_specific_fields(self) -> List[str]:
        """Get list of Piper VITS-specific configuration field paths."""
        return [
            # Required basic fields
            "model_specific.piper_vits.sample_rate",
            "model_specific.piper_vits.mel_channels",
            "model_specific.piper_vits.speaker_embedding",
            "model_specific.piper_vits.num_speakers",
            "model_specific.piper_vits.speaker_id",
            "model_specific.piper_vits.embedding_dim",

            # VITS architecture parameters
            "model_specific.piper_vits.inter_channels",
            "model_specific.piper_vits.hidden_channels",
            "model_specific.piper_vits.filter_channels",
            "model_specific.piper_vits.n_heads",
            "model_specific.piper_vits.n_layers",
            "model_specific.piper_vits.kernel_size",
            "model_specific.piper_vits.p_dropout",

            # Audio processing parameters
            "model_specific.piper_vits.n_fft",
            "model_specific.piper_vits.hop_size",
            "model_specific.piper_vits.win_size",
            "model_specific.piper_vits.n_mels",
            "model_specific.piper_vits.f_min",
            "model_specific.piper_vits.f_max",

            # Synthesis parameters
            "model_specific.piper_vits.noise_scale",
            "model_specific.piper_vits.noise_scale_d",
            "model_specific.piper_vits.length_scale",
            "model_specific.piper_vits.inference_noise_scale",
            "model_specific.piper_vits.max_wav_value",
            "model_specific.piper_vits.max_decoder_steps",
            "model_specific.piper_vits.gate_threshold",
            "model_specific.piper_vits.temperature",

            # Advanced features
            "model_specific.piper_vits.use_sdp",
            "model_specific.piper_vits.use_spectral_norm",
            "model_specific.piper_vits.gin_channels",
            "model_specific.piper_vits.postnet_embedding_dim",
            "model_specific.piper_vits.speaker_embedding_dim"
        ]

    def _setup_validation_rules(self) -> None:
        """Setup Piper VITS-specific validation rules."""
        super()._setup_validation_rules()

        # Add Piper VITS-specific validation rules
        self.validation_rules.extend([
            ConfigValidationRule(
                field_path="model_specific.piper_vits.sample_rate",
                rule_type="required",
                rule_params={},
                error_message="Sample rate is required for Piper VITS"
            ),
            ConfigValidationRule(
                field_path="model_specific.piper_vits.sample_rate",
                rule_type="enum",
                rule_params={"values": [16000, 22050, 44100]},
                error_message="Sample rate must be one of: 16000, 22050, 44100"
            ),
            ConfigValidationRule(
                field_path="model_specific.piper_vits.mel_channels",
                rule_type="range",
                rule_params={"min": 1, "max": 128},
                error_message="Mel channels must be between 1 and 128"
            ),
            ConfigValidationRule(
                field_path="model_specific.piper_vits.inter_channels",
                rule_type="range",
                rule_params={"min": 64, "max": 512},
                error_message="Inter channels must be between 64 and 512"
            ),
            ConfigValidationRule(
                field_path="model_specific.piper_vits.hidden_channels",
                rule_type="range",
                rule_params={"min": 64, "max": 512},
                error_message="Hidden channels must be between 64 and 512"
            ),
            ConfigValidationRule(
                field_path="model_specific.piper_vits.filter_channels",
                rule_type="range",
                rule_params={"min": 256, "max": 2048},
                error_message="Filter channels must be between 256 and 2048"
            ),
            ConfigValidationRule(
                field_path="model_specific.piper_vits.n_heads",
                rule_type="range",
                rule_params={"min": 1, "max": 8},
                error_message="Number of heads must be between 1 and 8"
            ),
            ConfigValidationRule(
                field_path="model_specific.piper_vits.n_layers",
                rule_type="range",
                rule_params={"min": 2, "max": 12},
                error_message="Number of layers must be between 2 and 12"
            ),
            ConfigValidationRule(
                field_path="model_specific.piper_vits.speaker_embedding",
                rule_type="type",
                rule_params={"type": bool},
                error_message="Speaker embedding must be boolean"
            ),
            ConfigValidationRule(
                field_path="model_specific.piper_vits.num_speakers",
                rule_type="range",
                rule_params={"min": 1, "max": 100},
                error_message="Number of speakers must be between 1 and 100"
            ),
            ConfigValidationRule(
                field_path="model_specific.piper_vits.noise_scale",
                rule_type="range",
                rule_params={"min": 0.0, "max": 2.0},
                error_message="Noise scale must be between 0.0 and 2.0"
            ),
            ConfigValidationRule(
                field_path="model_specific.piper_vits.max_decoder_steps",
                rule_type="range",
                rule_params={"min": 100, "max": 5000},
                error_message="Max decoder steps must be between 100 and 5000"
            ),
            ConfigValidationRule(
                field_path="performance.target_latency_ms",
                rule_type="range",
                rule_params={"min": 50, "max": 2000},
                error_message="Target latency must be between 50ms and 2000ms"
            ),
            ConfigValidationRule(
                field_path="performance.max_realtime_factor",
                rule_type="range",
                rule_params={"min": 0.05, "max": 2.0},
                error_message="Max realtime factor must be between 0.05 and 2.0"
            )
        ])

    def get_synthesis_config(self) -> Dict[str, Any]:
        """Get audio synthesis configuration for Piper VITS."""
        piper_config = self.config.get("model_specific", {}).get("piper_vits", {})

        return {
            "sample_rate": piper_config.get("sample_rate", 22050),
            "n_fft": piper_config.get("n_fft", 1024),
            "hop_size": piper_config.get("hop_size", 256),
            "win_size": piper_config.get("win_size", 1024),
            "n_mels": piper_config.get("n_mels", 80),
            "f_min": piper_config.get("f_min", 0.0),
            "f_max": piper_config.get("f_max", 8000.0),
            "noise_scale": piper_config.get("noise_scale", 0.667),
            "noise_scale_d": piper_config.get("noise_scale_d", 0.8),
            "length_scale": piper_config.get("length_scale", 1.0),
            "temperature": piper_config.get("temperature", 1.0)
        }

    def get_validation_rules(self) -> List[ConfigValidationRule]:
        """Get Piper VITS specific validation rules."""
        return self.validation_rules

    def get_model_config(self) -> Dict[str, Any]:
        """Get Piper VITS model configuration."""
        piper_config = self.config.get("model_specific", {}).get("piper_vits", {})

        return {
            "sample_rate": piper_config.get("sample_rate", 22050),
            "mel_channels": piper_config.get("mel_channels", 80),
            "speaker_embedding": piper_config.get("speaker_embedding", True),
            "num_speakers": piper_config.get("num_speakers", 1),
            "embedding_dim": piper_config.get("embedding_dim", 192),
            "postnet_embedding_dim": piper_config.get("postnet_embedding_dim", 512)
        }

    def get_speaker_config(self) -> Dict[str, Any]:
        """Get speaker configuration for multi-speaker support."""
        piper_config = self.config.get("model_specific", {}).get("piper_vits", {})

        return {
            "num_speakers": piper_config.get("num_speakers", 1),
            "speaker_id": piper_config.get("speaker_id", 0),
            "speaker_embedding_dim": piper_config.get("speaker_embedding_dim", 192),
            "speaker_embedding": piper_config.get("speaker_embedding", True)
        }