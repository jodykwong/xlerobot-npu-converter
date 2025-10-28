"""
ONNX Model Loaders

This package provides unified interfaces for loading ONNX models from multiple sources:
- Local file loading (.onnx files)
- Memory object loading (ModelProto objects)
- URL remote loading (HTTP/HTTPS downloads)
- Batch loading for multiple models
"""

from .onnx_loader import ONNXModelLoader
from .metadata_extractor import ModelMetadataExtractor
from ..models.onnx_model import (
    ONNXModel,
    TensorInfo,
    OperatorInfo,
    VersionInfo,
    ModelMetadata
)

__all__ = [
    "ONNXModelLoader",
    "ModelMetadataExtractor",
    "ONNXModel",
    "TensorInfo",
    "OperatorInfo",
    "VersionInfo",
    "ModelMetadata"
]
