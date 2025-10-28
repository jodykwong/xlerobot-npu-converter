"""
Configuration Management System

This package provides a comprehensive configuration management system for the
NPU converter, supporting multiple model types, dynamic configuration updates,
and hot reloading capabilities.

Key Components:
- ConfigurationManager: Main configuration controller
- ConfigValidator: Configuration validation system
- HotReloadManager: Hot reload functionality
- ConfigTemplateManager: Template management
- ConfigRecoveryManager: Backup and recovery system
- Model-specific strategies: VITS-Cantonese (primary), SenseVoice, Piper VITS

Architecture: Layered configuration with strategy pattern
Integration: Extends Story 1.3 core framework
Performance: <100ms load time, <500ms hot reload
"""

from .manager import ConfigurationManager
from .validator import ConfigValidator
from .hot_reload import HotReloadManager
from .templates import ConfigTemplateManager
from .recovery import ConfigRecoveryManager

# Strategy imports
from .strategies.base_strategy import BaseConfigStrategy
from .strategies.sensevoice_strategy import SenseVoiceConfigStrategy
from .strategies.piper_vits_strategy import PiperVITSConfigStrategy
from .strategies.vits_cantonese_strategy import VITSCantoneseConfigStrategy

# Model imports
from .models.conversion_config import ConversionConfigModel
from .models.hardware_config import HardwareConfigModel
from .models.validation_rules import ValidationRules

__all__ = [
    "ConfigurationManager",
    "ConfigValidator",
    "HotReloadManager",
    "ConfigTemplateManager",
    "ConfigRecoveryManager",
    "BaseConfigStrategy",
    "SenseVoiceConfigStrategy",
    "PiperVITSConfigStrategy",
    "VITSCantoneseConfigStrategy",
    "ConversionConfigModel",
    "HardwareConfigModel",
    "ValidationRules",
]