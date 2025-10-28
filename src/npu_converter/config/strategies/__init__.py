"""
Configuration Strategies Package

Implements the strategy pattern for different model types (SenseVoice, Piper VITS).
Each strategy handles model-specific configuration requirements and validation.
"""

from .base_strategy import BaseConfigStrategy
from .vits_cantonese_strategy import VITSCantoneseConfigStrategy
from .sensevoice_strategy import SenseVoiceConfigStrategy
from .piper_vits_strategy import PiperVITSConfigStrategy

__all__ = [
    "BaseConfigStrategy",
    "VITSCantoneseConfigStrategy",
    "SenseVoiceConfigStrategy",
    "PiperVITSConfigStrategy",
]