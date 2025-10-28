"""
VITS-Cantonese Configuration Strategy

Model-specific configuration strategy for VITS-Cantonese TTS models.
Implements the strategy pattern as defined in the architecture document.

Based on technical research from market analysis of VITS-Cantonese specifications.
Handles Cantonese-specific TTS configuration including:
- Cantonese phoneme inventory and tone system
- Audio synthesis parameters optimized for Cantonese
- VITS model architecture configuration
- Jyutping phoneme conversion
- Real-time inference optimization
"""

from typing import Dict, Any, List
from .base_strategy import BaseConfigStrategy, ConfigValidationRule


class VITSCantoneseConfigStrategy(BaseConfigStrategy):
    """Configuration strategy for VITS-Cantonese TTS models."""

    def get_model_type(self) -> str:
        """Get the model type this strategy handles."""
        return "vits_cantonese"

    def get_default_template(self) -> Dict[str, Any]:
        """Get the default configuration template for VITS-Cantonese."""
        return {
            "project": {
                "name": "xlerobot",
                "version": "1.0.0",
                "model_type": "vits_cantonese",
                "description": "VITS-Cantonese Text-to-Speech model"
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
                "vits_cantonese": {
                    # VITS Model Architecture Configuration
                    "inter_channels": 192,
                    "hidden_channels": 192,
                    "filter_channels": 768,
                    "n_heads": 2,
                    "n_layers": 4,
                    "kernel_size": 3,
                    "p_dropout": 0.1,
                    "resblock": "1",
                    "resblock_kernel_sizes": [3, 7, 11],
                    "resblock_dilation_sizes": [[1, 3, 5], [1, 3, 5], [1, 3, 5]],
                    "upsample_rates": [8, 8, 2, 2],
                    "upsample_initial_channel": 512,
                    "upsample_kernel_sizes": [16, 16, 4, 4],
                    "n_layers_q": 3,
                    "use_spectral_norm": False,
                    "gin_channels": 256,

                    # Audio Processing Parameters (Cantonese-optimized)
                    "sampling_rate": 22050,
                    "filter_length": 1024,
                    "hop_length": 256,
                    "win_length": 1024,
                    "n_mel_channels": 80,
                    "mel_fmin": 0.0,
                    "mel_fmax": 8000.0,
                    "max_wav_value": 32768.0,
                    "normalize": True,
                    "trim_silence": True,
                    "trim_threshold": 0.01,

                    # Voice Characteristics
                    "speaker_embedding_size": 192,
                    "num_speakers": 1,
                    "speaker_id": 0,
                    "use_speaker_embedding": True,

                    # Cantonese TTS Synthesis Parameters
                    "noise_scale": 0.667,
                    "noise_scale_w": 0.8,
                    "length_scale": 1.0,
                    "inference_noise_scale": 0.667,

                    # Cantonese Phoneme System Configuration
                    "cantonese_vocab_size": 5000,
                    "phoneme_set": "jyutping_extended",
                    "phoneme_language": "cantonese",
                    "phonemizer": "espeak",
                    "tone_embedding": True,
                    "num_tones": 6,
                    "use_jyutping": True,
                    "character_coverage": 0.995,

                    # Cantonese Phoneme Inventory
                    "phoneme_inventory": {
                        "initials": ["b", "p", "m", "f", "d", "t", "n", "l", "g", "k",
                                   "ng", "h", "gw", "kw", "w", "z", "c", "s", "j"],
                        "finals": ["aa", "aai", "aau", "aam", "aan", "aang", "aap", "aat", "aak",
                                   "ai", "au", "am", "an", "ang", "ap", "at", "ak", "e", "ei",
                                   "eu", "em", "en", "eng", "ep", "et", "i", "iu", "im", "in",
                                   "ing", "ip", "it", "o", "oi", "ou", "on", "ong", "ot", "ok",
                                   "oe", "oeng", "oek", "u", "ui", "un", "ung", "ut", "uk", "oe"],
                        "tones": [1, 2, 3, 4, 5, 6],
                        "tone_values": {
                            "1": 55,  # High level
                            "2": 25,  # High rising
                            "3": 33,  # Mid level
                            "4": 21,  # Low falling
                            "5": 23,  # Low rising
                            "6": 22   # Low level
                        }
                    },

                    # Cantonese Text Processing
                    "text_cleaners": ["cantonese_cleaners"],
                    "jyutping_to_phoneme": True,
                    "tone_normalization": True,
                    "regional_accent": "hong_kong",
                    "regional_variants": {
                        "hong_kong": {
                            "preference": "standard",
                            "tone_contours": "standard",
                            "vowel_system": "9_vowel"
                        },
                        "guangzhou": {
                            "preference": "standard",
                            "tone_contours": "slightly_modified",
                            "vowel_system": "8_vowel"
                        }
                    },

                    # Data Preprocessing Settings
                    "add_blank": True,
                    "n_speakers": 1,
                    "cleaned_text": True
                }
            },
            "performance": {
                "target_latency_ms": 200,  # Real-time TTS target
                "max_realtime_factor": 0.9,
                "enable_streaming": True,
                "enable_caching": True,
                "max_batch_size": 4,
                "synthesis_buffer_size": 2048,
                "execution_mode": "streaming",
                "chunk_size": 1024,
                "overlap_size": 64,
                "buffer_management": {
                    "input_buffer_size": 4,
                    "output_buffer_size": 8,
                    "prefetch_enabled": True
                }
            },
            "optimization": {
                "enable_quantization": True,
                "quantization_precision": "int8",
                "quantization_method": "dynamic_quantization",
                "enable_fusion": True,
                "enable_pruning": False,
                "enable_weight_sharing": False,
                "enable_dynamic_shapes": False,
                "torch_compile": True,
                "gradient_checkpointing": False,
                "use_efficient_attention": True,
                "max_memory_usage": "2GB",
                "model_pruning": {
                    "enabled": False,
                    "method": "magnitude",
                    "sparsity": 0.1
                }
            },
            "export": {
                "format": "onnx",
                "opset_version": 14,
                "dynamic_axes": {
                    "input": {0: "batch_size", 1: "sequence_length"},
                    "output": {0: "batch_size", 1: "audio_length"}
                },
                "optimization": {
                    "constant_folding": True,
                    "shape_inference": True,
                    "model_simplification": True
                }
            },
            "npu_deployment": {
                "target_platform": "generic_npu",
                "compiler_options": {
                    "optimization_level": "O3",
                    "memory_optimization": True,
                    "parallelization": True
                },
                "memory_mapping": {
                    "input_buffer_size": "auto",
                    "output_buffer_size": "auto",
                    "workspace_size": "auto"
                },
                "precision_requirements": {
                    "input_precision": "fp16",
                    "output_precision": "fp16",
                    "internal_precision": "fp16"
                }
            },
            "validation": {
                "strict_validation": True,
                "warn_on_deprecated": True,
                "validate_paths": True,
                "quality_metrics": {
                    "objective_metrics": {
                        "mcd_score": "< 4.5",
                        "f0_rmse": "< 30 Hz",
                        "voicing_decision_error": "< 5%"
                    },
                    "subjective_metrics": {
                        "mos_score": "> 4.0",
                        "similarity_score": "> 4.0"
                    }
                }
            }
        }

    def validate_model_specific_config(self) -> bool:
        """
        Validate VITS-Cantonese specific configuration based on technical specifications.

        Returns:
            True if configuration is valid
        """
        if not self.config:
            return False

        vits_config = self.config.get("model_specific", {}).get("vits_cantonese", {})
        if not vits_config:
            return False

        # Check required VITS architecture fields
        required_vits_fields = [
            "inter_channels", "hidden_channels", "filter_channels",
            "n_heads", "n_layers", "kernel_size"
        ]

        # Check required Cantonese-specific fields
        required_cantonese_fields = [
            "sampling_rate", "filter_length", "hop_length", "win_length",
            "n_mel_channels", "cantonese_vocab_size", "phoneme_set",
            "tone_embedding", "num_tones", "use_jyutping"
        ]

        for field in required_vits_fields + required_cantonese_fields:
            if field not in vits_config:
                return False

        # Validate VITS architecture parameters
        if vits_config["inter_channels"] != 192:
            return False
        if vits_config["n_heads"] != 2:
            return False
        if vits_config["n_layers"] != 4:
            return False

        return True

    def get_model_specific_fields(self) -> List[str]:
        """Get list of VITS-Cantonese specific configuration field paths."""
        return [
            "model_specific.vits_cantonese.inter_channels",
            "model_specific.vits_cantonese.hidden_channels",
            "model_specific.vits_cantonese.filter_channels",
            "model_specific.vits_cantonese.n_heads",
            "model_specific.vits_cantonese.n_layers",
            "model_specific.vits_cantonese.kernel_size",
            "model_specific.vits_cantonese.p_dropout",
            "model_specific.vits_cantonese.resblock",
            "model_specific.vits_cantonese.resblock_kernel_sizes",
            "model_specific.vits_cantonese.resblock_dilation_sizes",
            "model_specific.vits_cantonese.upsample_rates",
            "model_specific.vits_cantonese.upsample_initial_channel",
            "model_specific.vits_cantonese.upsample_kernel_sizes",
            "model_specific.vits_cantonese.n_layers_q",
            "model_specific.vits_cantonese.use_spectral_norm",
            "model_specific.vits_cantonese.gin_channels",
            "model_specific.vits_cantonese.sampling_rate",
            "model_specific.vits_cantonese.filter_length",
            "model_specific.vits_cantonese.hop_length",
            "model_specific.vits_cantonese.win_length",
            "model_specific.vits_cantonese.n_mel_channels",
            "model_specific.vits_cantonese.mel_fmin",
            "model_specific.vits_cantonese.mel_fmax",
            "model_specific.vits_cantonese.max_wav_value",
            "model_specific.vits_cantonese.normalize",
            "model_specific.vits_cantonese.trim_silence",
            "model_specific.vits_cantonese.trim_threshold",
            "model_specific.vits_cantonese.speaker_embedding_size",
            "model_specific.vits_cantonese.num_speakers",
            "model_specific.vits_cantonese.speaker_id",
            "model_specific.vits_cantonese.use_speaker_embedding",
            "model_specific.vits_cantonese.noise_scale",
            "model_specific.vits_cantonese.noise_scale_w",
            "model_specific.vits_cantonese.length_scale",
            "model_specific.vits_cantonese.inference_noise_scale",
            "model_specific.vits_cantonese.cantonese_vocab_size",
            "model_specific.vits_cantonese.phoneme_set",
            "model_specific.vits_cantonese.phoneme_language",
            "model_specific.vits_cantonese.phonemizer",
            "model_specific.vits_cantonese.tone_embedding",
            "model_specific.vits_cantonese.num_tones",
            "model_specific.vits_cantonese.use_jyutping",
            "model_specific.vits_cantonese.character_coverage",
            "model_specific.vits_cantonese.phoneme_inventory",
            "model_specific.vits_cantonese.text_cleaners",
            "model_specific.vits_cantonese.jyutping_to_phoneme",
            "model_specific.vits_cantonese.tone_normalization",
            "model_specific.vits_cantonese.regional_accent",
            "model_specific.vits_cantonese.regional_variants",
            "model_specific.vits_cantonese.add_blank",
            "model_specific.vits_cantonese.n_speakers",
            "model_specific.vits_cantonese.cleaned_text"
        ]

    def get_validation_rules(self) -> List[ConfigValidationRule]:
        """Get VITS-Cantonese specific validation rules."""
        return self.validation_rules

    def _setup_validation_rules(self) -> None:
        """Setup VITS-Cantonese specific validation rules."""
        # Call parent method to setup common rules
        super()._setup_validation_rules()

        # Add VITS-Cantonese specific validation rules
        self.validation_rules.extend([
            ConfigValidationRule(
                field_path="model_specific.vits_cantonese.inter_channels",
                rule_type="enum",
                rule_params={"values": [192]},
                error_message="VITS inter_channels must be 192"
            ),
            ConfigValidationRule(
                field_path="model_specific.vits_cantonese.hidden_channels",
                rule_type="enum",
                rule_params={"values": [192]},
                error_message="VITS hidden_channels must be 192"
            ),
            ConfigValidationRule(
                field_path="model_specific.vits_cantonese.filter_channels",
                rule_type="enum",
                rule_params={"values": [768]},
                error_message="VITS filter_channels must be 768"
            ),
            ConfigValidationRule(
                field_path="model_specific.vits_cantonese.n_heads",
                rule_type="enum",
                rule_params={"values": [2]},
                error_message="VITS n_heads must be 2"
            ),
            ConfigValidationRule(
                field_path="model_specific.vits_cantonese.n_layers",
                rule_type="enum",
                rule_params={"values": [4]},
                error_message="VITS n_layers must be 4"
            ),
            ConfigValidationRule(
                field_path="model_specific.vits_cantonese.sampling_rate",
                rule_type="enum",
                rule_params={"values": [22050]},
                error_message="Sampling rate must be 22050 Hz for VITS-Cantonese"
            ),
            ConfigValidationRule(
                field_path="model_specific.vits_cantonese.filter_length",
                rule_type="enum",
                rule_params={"values": [1024]},
                error_message="Filter length must be 1024"
            ),
            ConfigValidationRule(
                field_path="model_specific.vits_cantonese.hop_length",
                rule_type="enum",
                rule_params={"values": [256]},
                error_message="Hop length must be 256"
            ),
            ConfigValidationRule(
                field_path="model_specific.vits_cantonese.n_mel_channels",
                rule_type="enum",
                rule_params={"values": [80]},
                error_message="Mel channels must be 80"
            ),
            ConfigValidationRule(
                field_path="model_specific.vits_cantonese.cantonese_vocab_size",
                rule_type="range",
                rule_params={"min": 1000, "max": 10000},
                error_message="Cantonese vocabulary size must be between 1000 and 10000"
            ),
            ConfigValidationRule(
                field_path="model_specific.vits_cantonese.num_tones",
                rule_type="enum",
                rule_params={"values": [6]},
                error_message="Number of Cantonese tones must be 6"
            ),
            ConfigValidationRule(
                field_path="model_specific.vits_cantonese.phoneme_set",
                rule_type="enum",
                rule_params={"values": ["jyutping_extended"]},
                error_message="Phoneme set must be jyutping_extended"
            ),
            ConfigValidationRule(
                field_path="model_specific.vits_cantonese.regional_accent",
                rule_type="enum",
                rule_params={"values": ["hong_kong", "guangzhou"]},
                error_message="Regional accent must be hong_kong or guangzhou"
            ),
            ConfigValidationRule(
                field_path="model_specific.vits_cantonese.noise_scale",
                rule_type="range",
                rule_params={"min": 0.1, "max": 2.0},
                error_message="Noise scale must be between 0.1 and 2.0"
            ),
            ConfigValidationRule(
                field_path="model_specific.vits_cantonese.length_scale",
                rule_type="range",
                rule_params={"min": 0.5, "max": 2.0},
                error_message="Length scale must be between 0.5 and 2.0"
            ),
            ConfigValidationRule(
                field_path="model_specific.vits_cantonese.tone_embedding",
                rule_type="required",
                rule_params={},
                error_message="Tone embedding setting is required for VITS-Cantonese"
            ),
            ConfigValidationRule(
                field_path="model_specific.vits_cantonese.use_jyutping",
                rule_type="required",
                rule_params={},
                error_message="Jyutping usage setting is required for VITS-Cantonese"
            ),
            ConfigValidationRule(
                field_path="model_specific.vits_cantonese.phoneme_inventory",
                rule_type="required",
                rule_params={},
                error_message="Phoneme inventory is required for VITS-Cantonese"
            )
        ])

    def get_audio_processing_config(self) -> Dict[str, Any]:
        """Get Cantonese-specific audio processing configuration."""
        vits_config = self.config.get("model_specific", {}).get("vits_cantonese", {})

        return {
            "vits_architecture": {
                "inter_channels": vits_config.get("inter_channels", 192),
                "hidden_channels": vits_config.get("hidden_channels", 192),
                "filter_channels": vits_config.get("filter_channels", 768),
                "n_heads": vits_config.get("n_heads", 2),
                "n_layers": vits_config.get("n_layers", 4),
                "kernel_size": vits_config.get("kernel_size", 3),
                "p_dropout": vits_config.get("p_dropout", 0.1),
                "resblock_kernel_sizes": vits_config.get("resblock_kernel_sizes", [3, 7, 11]),
                "upsample_rates": vits_config.get("upsample_rates", [8, 8, 2, 2])
            },
            "audio_processing": {
                "sampling_rate": vits_config.get("sampling_rate", 22050),
                "filter_length": vits_config.get("filter_length", 1024),
                "hop_length": vits_config.get("hop_length", 256),
                "win_length": vits_config.get("win_length", 1024),
                "n_mel_channels": vits_config.get("n_mel_channels", 80),
                "mel_fmin": vits_config.get("mel_fmin", 0.0),
                "mel_fmax": vits_config.get("mel_fmax", 8000.0),
                "max_wav_value": vits_config.get("max_wav_value", 32768.0),
                "normalize": vits_config.get("normalize", True)
            },
            "cantonese_preprocessing": {
                "jyutping_to_phoneme": vits_config.get("jyutping_to_phoneme", True),
                "tone_normalization": vits_config.get("tone_normalization", True),
                "regional_accent": vits_config.get("regional_accent", "hong_kong"),
                "phoneme_set": vits_config.get("phoneme_set", "jyutping_extended"),
                "tone_embedding": vits_config.get("tone_embedding", True),
                "num_tones": vits_config.get("num_tones", 6),
                "text_cleaners": vits_config.get("text_cleaners", ["cantonese_cleaners"])
            }
        }

    def get_synthesis_config(self) -> Dict[str, Any]:
        """Get Cantonese-specific synthesis configuration."""
        vits_config = self.config.get("model_specific", {}).get("vits_cantonese", {})

        return {
            "synthesis_parameters": {
                "noise_scale": vits_config.get("noise_scale", 0.667),
                "noise_scale_w": vits_config.get("noise_scale_w", 0.8),
                "length_scale": vits_config.get("length_scale", 1.0),
                "inference_noise_scale": vits_config.get("inference_noise_scale", 0.667)
            },
            "speaker_config": {
                "speaker_embedding_size": vits_config.get("speaker_embedding_size", 192),
                "num_speakers": vits_config.get("num_speakers", 1),
                "speaker_id": vits_config.get("speaker_id", 0),
                "use_speaker_embedding": vits_config.get("use_speaker_embedding", True),
                "gin_channels": vits_config.get("gin_channels", 256)
            },
            "cantonese_synthesis": {
                "tone_embedding": vits_config.get("tone_embedding", True),
                "num_tones": vits_config.get("num_tones", 6),
                "cantonese_vocab_size": vits_config.get("cantonese_vocab_size", 5000),
                "phoneme_set": vits_config.get("phoneme_set", "jyutping_extended"),
                "use_jyutping": vits_config.get("use_jyutping", True),
                "character_coverage": vits_config.get("character_coverage", 0.995)
            }
        }

    def get_optimization_config(self) -> Dict[str, Any]:
        """Get VITS-Cantonese specific optimization configuration."""
        optimization_config = self.config.get("optimization", {})
        vits_config = self.config.get("model_specific", {}).get("vits_cantonese", {})

        return {
            "inference_optimization": {
                "torch_compile": optimization_config.get("torch_compile", True),
                "gradient_checkpointing": optimization_config.get("gradient_checkpointing", False),
                "use_efficient_attention": optimization_config.get("use_efficient_attention", True),
                "max_memory_usage": optimization_config.get("max_memory_usage", "2GB")
            },
            "quantization": {
                "enabled": optimization_config.get("enable_quantization", True),
                "precision": optimization_config.get("quantization_precision", "int8"),
                "method": optimization_config.get("quantization_method", "dynamic_quantization"),
                "cantonese_preservation": {
                    "tone_model_quantization": True,  # Quantize tone models carefully
                    "phoneme_embedding_quantization": True,
                    "regional_accent_preservation": True
                }
            },
            "model_optimization": {
                "enable_fusion": optimization_config.get("enable_fusion", True),
                "enable_pruning": optimization_config.get("enable_pruning", False),
                "model_pruning": optimization_config.get("model_pruning", {}),
                "cantonese_constraints": {
                    "tone_pruning_disabled": True,  # Never prune tone-related components
                    "phoneme_preservation": True
                }
            }
        }

    def get_data_preprocessing_config(self) -> Dict[str, Any]:
        """Get Cantonese-specific data preprocessing configuration."""
        vits_config = self.config.get("model_specific", {}).get("vits_cantonese", {})

        return {
            "text_processing": {
                "text_cleaners": vits_config.get("text_cleaners", ["cantonese_cleaners"]),
                "jyutping_conversion": vits_config.get("jyutping_to_phoneme", True),
                "tone_processing": {
                    "tone_normalization": vits_config.get("tone_normalization", True),
                    "tone_embedding": vits_config.get("tone_embedding", True),
                    "num_tones": vits_config.get("num_tones", 6),
                    "tone_values": vits_config.get("phoneme_inventory", {}).get("tone_values", {})
                }
            },
            "phoneme_processing": {
                "phoneme_language": vits_config.get("phoneme_language", "cantonese"),
                "phonemizer": vits_config.get("phonemizer", "espeak"),
                "phoneme_set": vits_config.get("phoneme_set", "jyutping_extended"),
                "cantonese_vocab_size": vits_config.get("cantonese_vocab_size", 5000),
                "character_coverage": vits_config.get("character_coverage", 0.995),
                "phoneme_inventory": vits_config.get("phoneme_inventory", {})
            },
            "regional_settings": {
                "regional_accent": vits_config.get("regional_accent", "hong_kong"),
                "regional_variants": vits_config.get("regional_variants", {}),
                "regional_preferences": {
                    "hong_kong": "standard",
                    "guangzhou": "slightly_modified"
                }
            }
        }

    def get_performance_requirements(self) -> Dict[str, Any]:
        """Get VITS-Cantonese performance requirements."""
        performance_config = self.config.get("performance", {})

        return {
            "latency_targets": {
                "target_latency_ms": performance_config.get("target_latency_ms", 200),
                "max_realtime_factor": performance_config.get("max_realtime_factor", 0.9),
                "streaming_latency": 50  # Additional streaming latency
            },
            "throughput_targets": {
                "realtime_factor": 0.9,
                "max_batch_size": performance_config.get("max_batch_size", 4),
                "synthesis_buffer_size": performance_config.get("synthesis_buffer_size", 2048)
            },
            "quality_metrics": {
                "objective": {
                    "mcd_score_target": "< 4.5",
                    "f0_rmse_target": "< 30 Hz",
                    "voicing_decision_error_target": "< 5%"
                },
                "subjective": {
                    "mos_score_target": "> 4.0",
                    "similarity_score_target": "> 4.0"
                }
            }
        }