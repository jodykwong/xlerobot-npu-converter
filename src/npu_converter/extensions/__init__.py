"""
NPU Converter Algorithm Extension System

提供算法扩展能力，支持动态算法注册、发现、适配和生命周期管理。
"""

from .algorithm_extension_system import AlgorithmExtensionSystem
from .algorithm_registry import AlgorithmRegistry
from .adapters.algorithm_adapter import BaseAlgorithmAdapter
from .config.algorithm_config_manager import AlgorithmConfigManager
from .lifecycle.algorithm_lifecycle import AlgorithmLifecycle

__all__ = [
    'AlgorithmExtensionSystem',
    'AlgorithmRegistry',
    'BaseAlgorithmAdapter',
    'AlgorithmConfigManager',
    'AlgorithmLifecycle',
]
