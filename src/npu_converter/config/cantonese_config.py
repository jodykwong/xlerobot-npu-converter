"""
VITS-Cantonese Configuration Module

This module provides configuration templates and strategies for VITS-Cantonese TTS models.
Integrates with Story 1.4 ConfigurationManager and Story 2.2 complete flow.

Author: Story 2.2 Implementation
Version: 1.0.0
Date: 2025-10-27
"""

from typing import Any, Dict, Optional
from pathlib import Path
import yaml

from ..manager import ConfigurationManager
from ...core.models.config_model import ConfigModel


class VITS_CantoneseConfigStrategy:
    """
    Configuration strategy for VITS-Cantonese TTS models.

    Provides complete parameter configuration support for AC3.
    Integrates with ConfigurationManager from Story 1.4.
    """

    def __init__(self):
        """Initialize VITS-Cantonese configuration strategy."""
        self.model_type = "vits_cantonese"
        self.config_template = self._load_default_template()

    def _load_default_template(self) -> Dict[str, Any]:
        """Load default configuration template for VITS-Cantonese."""
        return {
            "model": {
                "type": "vits_cantonese",
                "language": "cantonese",
                "voice_type": "female",  # male, female, child, neutral
                "version": "1.0.0"
            },
            "conversion": {
                "level": "production",  # basic, standard, enhanced, production
                "input_format": "onnx",
                "output_format": "bpu",
                "target_hardware": "horizon_x5",
                "optimization": {
                    "tone_modeling": True,
                    "prosody_optimization": True,
                    "voice_optimization": True
                }
            },
            "parameters": {
                "sample_rate": 44100,
                "bit_depth": 16,
                "channels": 1,
                "batch_size": 1,
                "max_sequence_length": 1000
            },
            "cantonese_specific": {
                "prosody_profile": "neutral",  # neutral, formal, casual, expressive
                "tone_accuracy_target": 0.95,
                "semantic_accuracy_target": 0.90,
                "audio_quality_target": 8.5
            },
            "validation": {
                "strict_mode": True,
                "precision_threshold": 0.98,
                "success_rate_threshold": 0.95,
                "validation_level": "strict"
            },
            "output": {
                "formats": ["json", "html", "pdf"],
                "include_metrics": True,
                "include_optimization_details": True
            }
        }

    def create_config(self, custom_params: Optional[Dict[str, Any]] = None) -> ConfigModel:
        """
        Create VITS-Cantonese configuration model.

        Args:
            custom_params: Optional custom parameters to override defaults

        Returns:
            ConfigModel: Complete VITS-Cantonese configuration

        Raises:
            ValueError: If custom parameters are invalid
        """
        config_dict = self.config_template.copy()

        # Apply custom parameters if provided
        if custom_params:
            self._merge_parameters(config_dict, custom_params)

        # Validate configuration
        self._validate_config(config_dict)

        # Create ConfigModel
        config_model = ConfigModel(**config_dict)

        return config_model

    def _merge_parameters(self, base_config: Dict[str, Any], custom_params: Dict[str, Any]) -> None:
        """Merge custom parameters into base configuration."""
        for key, value in custom_params.items():
            if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                self._merge_parameters(base_config[key], value)
            else:
                base_config[key] = value

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration parameters."""
        # Validate voice_type
        valid_voice_types = ["male", "female", "child", "neutral"]
        if config["model"]["voice_type"] not in valid_voice_types:
            raise ValueError(f"Invalid voice_type: {config['model']['voice_type']}. Must be one of {valid_voice_types}")

        # Validate conversion level
        valid_levels = ["basic", "standard", "enhanced", "production"]
        if config["conversion"]["level"] not in valid_levels:
            raise ValueError(f"Invalid conversion level: {config['conversion']['level']}. Must be one of {valid_levels}")

        # Validate audio parameters
        if config["parameters"]["sample_rate"] < 16000 or config["parameters"]["sample_rate"] > 48000:
            raise ValueError(f"Invalid sample_rate: {config['parameters']['sample_rate']}")

        if config["parameters"]["bit_depth"] not in [16, 32]:
            raise ValueError(f"Invalid bit_depth: {config['parameters']['bit_depth']}")

        # Validate thresholds
        if config["cantonese_specific"]["tone_accuracy_target"] < 0 or config["cantonese_specific"]["tone_accuracy_target"] > 1:
            raise ValueError(f"Invalid tone_accuracy_target: {config['cantonese_specific']['tone_accuracy_target']}")

    def get_preset_configs(self) -> Dict[str, ConfigModel]:
        """
        Get preset configurations for different use cases.

        Returns:
            Dict[str, ConfigModel]: Preset configurations
        """
        presets = {
            "default": self.create_config(),
            "high_quality": self.create_config({
                "conversion": {
                    "level": "production"
                },
                "cantonese_specific": {
                    "prosody_profile": "expressive"
                },
                "validation": {
                    "precision_threshold": 0.99,
                    "strict_mode": True
                }
            }),
            "fast_inference": self.create_config({
                "conversion": {
                    "level": "basic"
                },
                "parameters": {
                    "batch_size": 4
                },
                "validation": {
                    "precision_threshold": 0.95
                }
            }),
            "formal_speech": self.create_config({
                "conversion": {
                    "level": "enhanced"
                },
                "cantonese_specific": {
                    "prosody_profile": "formal",
                    "tone_accuracy_target": 0.98
                }
            }),
            "casual_speech": self.create_config({
                "conversion": {
                    "level": "standard"
                },
                "cantonese_specific": {
                    "prosody_profile": "casual"
                }
            })
        }

        return presets

    def save_config_template(self, output_path: Path) -> None:
        """Save configuration template to file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config_template, f, default_flow_style=False, allow_unicode=True)

        logger.info(f"Configuration template saved to: {output_path}")

    def __repr__(self) -> str:
        """String representation of VITS_CantoneseConfigStrategy."""
        return f"VITS_CantoneseConfigStrategy(model_type='{self.model_type}')"


# Configure logger
import logging
logger = logging.getLogger(__name__)
