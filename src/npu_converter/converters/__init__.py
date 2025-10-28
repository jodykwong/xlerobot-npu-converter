"""
Model Conversion Flow Implementations

This package provides high-level conversion flow implementations that extend
the core BaseConverter framework from Story 1.3 and integrate with the
configuration management system from Story 1.4.

Key Components:
- BaseConversionFlow: Abstract base class for conversion flows
- SenseVoiceConversionFlow: ASR model conversion implementation
- VITSCantoneseConversionFlow: Primary TTS model conversion implementation
- PiperVITSConversionFlow: Alternative TTS model conversion implementation
- ProgressTracker: Enhanced progress monitoring system
- StatusCallback: Real-time status feedback system
- ConversionLogger: Detailed logging and audit trail system

Architecture: Story 1.5 implements conversion flows on top of Stories 1.3-1.4
Integration: Full integration with Horizon X5 BPU toolchain
Thread Safety: All components are thread-safe for concurrent operations
"""

from .base_conversion_flow import BaseConversionFlow, ConversionStage
from .progress_tracker import ProgressTracker, StageProgress
from .status_callback import StatusCallback, ConsoleStatusCallback, FileStatusCallback, MemoryStatusCallback, CompositeStatusCallback
from .conversion_logger import ConversionLogger, ConversionLogLevel

# Model-specific imports
from .sensevoice_flow import SenseVoiceConversionFlow
from .vits_cantonese_flow import VITSCantoneseConversionFlow
from .piper_vits_flow import PiperVITSConversionFlow

__version__ = "1.0.0"
__author__ = "NPU Converter Team"

__all__ = [
    # Base Architecture
    "BaseConversionFlow",
    "ConversionStage",
    "ProgressTracker",
    "StageProgress",
    "StatusCallback",
    "ConsoleStatusCallback",
    "FileStatusCallback",
    "MemoryStatusCallback",
    "CompositeStatusCallback",
    "ConversionLogger",
    "ConversionLogLevel",

    # Model-specific Converters
    "SenseVoiceConversionFlow",
    "VITSCantoneseConversionFlow",
    "PiperVITSConversionFlow",
]