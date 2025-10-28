"""
Dynamic Shape Handler for ONNX Models

This module extends the ModelMetadataExtractor (Story 2.1.2) to provide
enhanced dynamic shape validation and analysis capabilities.

Features:
- Deep dynamic dimension analysis
- Dynamic shape constraint validation
- Unsupported dynamic shape detection
- Batch size independence verification
"""

import logging
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum

from ..models.onnx_model import (
    TensorInfo,
    ONNXModel
)

logger = logging.getLogger(__name__)


class DynamicShapeType(Enum):
    """Types of dynamic shapes in ONNX models"""
    UNKNOWN_DIMENSION = "unknown"  # dim_value = 0
    BATCH_SIZE = "batch_size"  # First dimension, typically variable
    SEQUENCE_LENGTH = "sequence_length"  # NLP models
    HEIGHT_WIDTH = "spatial"  # Height/Width for vision models
    CHANNELS = "channels"  # Usually fixed
    CUSTOM = "custom"  # Model-specific dynamic dimension


@dataclass
class DynamicDimensionInfo:
    """Information about a dynamic dimension"""
    dimension_index: int
    dimension_type: DynamicShapeType
    is_supported: bool
    constraint_description: str
    recommended_value: Optional[int] = None
    warnings: List[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


@dataclass
class DynamicShapeValidationResult:
    """Result of dynamic shape validation"""
    is_valid: bool
    has_unsupported_dynamic_dims: bool
    dynamic_dimensions: List[DynamicDimensionInfo]
    batch_independent: bool
    total_dynamic_dims: int
    warnings: List[str] = None
    errors: List[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.errors is None:
            self.errors = []

    def get_summary(self) -> str:
        """Get a human-readable summary of the validation result"""
        summary = [
            f"Dynamic Shape Validation Result:",
            f"  Total Dynamic Dimensions: {self.total_dynamic_dims}",
            f"  Batch Independent: {self.batch_independent}",
            f"  Valid: {self.is_valid}"
        ]

        if self.warnings:
            summary.append(f"  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                summary.append(f"    - {warning}")

        if self.errors:
            summary.append(f"  Errors ({len(self.errors)}):")
            for error in self.errors:
                summary.append(f"    - {error}")

        return "\n".join(summary)


class DynamicShapeHandler:
    """
    Enhanced dynamic shape validator extending Story 2.1.2's ModelMetadataExtractor.

    This class provides:
    - Classification of dynamic dimension types
    - Constraint validation for Horizon X5 BPU compatibility
    - Detection of unsupported dynamic shapes
    - Recommendations for fixing dynamic shape issues
    """

    # Horizon X5 BPU supported dynamic dimensions
    SUPPORTED_BATCH_DIMS = {0, 1}  # Can be 0 or 1 for batch
    MAX_SEQUENCE_LENGTH = 512  # For NLP models
    MAX_SPATIAL_DIM = 224  # For vision models (e.g., ImageNet standard)
    MIN_SPATIAL_DIM = 16  # Minimum spatial dimension

    def __init__(self):
        """Initialize the DynamicShapeHandler"""
        logger.info("Initializing DynamicShapeHandler")
        self._initialize_dimension_patterns()

    def _initialize_dimension_patterns(self):
        """Initialize patterns for detecting dimension types"""
        self.dimension_patterns = {
            DynamicShapeType.BATCH_SIZE: {
                "positions": {0, 1},
                "typical_values": [None, -1, "dynamic"],
                "description": "Batch size dimension (usually first or second)"
            },
            DynamicShapeType.SEQUENCE_LENGTH: {
                "positions": {1, 2},
                "typical_values": [None, -1, "dynamic"],
                "description": "Sequence length for NLP models"
            },
            DynamicShapeType.HEIGHT_WIDTH: {
                "positions": {2, 3},
                "typical_values": [None, -1, "dynamic"],
                "description": "Spatial dimensions (height, width)"
            },
            DynamicShapeType.CHANNELS: {
                "positions": {-1},
                "typical_values": [3, 64, 128, 256, 512],
                "description": "Channel dimension (usually fixed)"
            }
        }

    def validate_dynamic_shapes(self,
                               model: ONNXModel,
                               input_tensors: Optional[List[TensorInfo]] = None,
                               output_tensors: Optional[List[TensorInfo]] = None) -> DynamicShapeValidationResult:
        """
        Validate dynamic shapes in the model.

        Args:
            model: ONNXModel instance
            input_tensors: List of input tensor info (from Story 2.1.2)
            output_tensors: List of output tensor info (from Story 2.1.2)

        Returns:
            DynamicShapeValidationResult with detailed analysis
        """
        logger.info(f"Starting dynamic shape validation for model: {model}")

        if input_tensors is None:
            logger.warning("input_tensors not provided, extracting from model")
            # This would integrate with Story 2.1.2's ModelMetadataExtractor
            from ..loaders.metadata_extractor import ModelMetadataExtractor
            extractor = ModelMetadataExtractor()
            input_tensors = extractor.extract_input_tensors(model)
            output_tensors = extractor.extract_output_tensors(model)

        # Analyze dynamic dimensions in all tensors
        all_dynamic_dims = self._analyze_tensor_dynamic_shapes(input_tensors, output_tensors)

        # Validate Horizon X5 BPU compatibility
        bpu_compatibility = self._validate_bpu_compatibility(all_dynamic_dims)

        # Check batch independence
        batch_independent = self._check_batch_independence(all_dynamic_dims)

        # Compile results
        result = DynamicShapeValidationResult(
            is_valid=bpu_compatibility["valid"],
            has_unsupported_dynamic_dims=not bpu_compatibility["valid"],
            dynamic_dimensions=all_dynamic_dims,
            batch_independent=batch_independent,
            total_dynamic_dims=len(all_dynamic_dims),
            warnings=bpu_compatibility["warnings"],
            errors=bpu_compatibility["errors"]
        )

        logger.info(f"Dynamic shape validation completed: {result.is_valid}")
        return result

    def _analyze_tensor_dynamic_shapes(self,
                                       input_tensors: List[TensorInfo],
                                       output_tensors: List[TensorInfo]) -> List[DynamicDimensionInfo]:
        """
        Analyze dynamic dimensions in a list of tensors.

        Args:
            input_tensors: List of input TensorInfo objects
            output_tensors: List of output TensorInfo objects

        Returns:
            List of DynamicDimensionInfo objects
        """
        dynamic_dims = []

        # Process all tensors
        all_tensors = input_tensors + output_tensors

        for tensor in all_tensors:
            if tensor.shape is None:
                continue

            for idx, dim_size in enumerate(tensor.shape):
                # Check for dynamic dimensions (dim_size == -1 or dim_size == 0)
                if dim_size == -1 or dim_size == 0:
                    dim_type = self._classify_dimension(idx, dim_size, tensor, all_tensors)
                    is_supported, constraint_desc = self._check_dimension_support(
                        idx, dim_type, tensor, dim_size
                    )

                    dim_info = DynamicDimensionInfo(
                        dimension_index=idx,
                        dimension_type=dim_type,
                        is_supported=is_supported,
                        constraint_description=constraint_desc,
                        recommended_value=self._get_recommended_value(dim_type, idx),
                        warnings=[]
                    )
                    dynamic_dims.append(dim_info)

        return dynamic_dims

    def _classify_dimension(self,
                           dim_index: int,
                           dim_size: int,
                           tensor: TensorInfo,
                           all_tensors: List[TensorInfo]) -> DynamicShapeType:
        """
        Classify the type of a dynamic dimension.

        Args:
            dim_index: Index of the dimension in the shape
            dim_size: Size of the dimension (-1 for dynamic)
            tensor: TensorInfo containing the dimension
            all_tensors: List of all tensors for context

        Returns:
            DynamicShapeType classification
        """
        # Check if this looks like sequence length (common in NLP) - check BEFORE batch
        # because dim_index 1 could be either batch or sequence
        if dim_index == 1 or dim_index == 2:
            # Check if tensor name suggests NLP
            if any(keyword in tensor.name.lower()
                   for keyword in ["token", "seq", "embed", "mask"]):
                return DynamicShapeType.SEQUENCE_LENGTH

        # Check if this looks like batch dimension (usually first dimension only)
        if dim_index == 0:
            # First dimension is typically batch
            return DynamicShapeType.BATCH_SIZE

        # Check if this looks like spatial dimension (height/width)
        if dim_index >= 2:
            # Check if tensor name suggests image/vision
            if any(keyword in tensor.name.lower()
                   for keyword in ["image", "img", "feature", "conv", "pool"]):
                return DynamicShapeType.HEIGHT_WIDTH

        # Check if it's a channel dimension (usually at the end)
        if dim_index == len(tensor.shape) - 1 and tensor.shape[dim_index] in [3, 64, 128, 256, 512]:
            return DynamicShapeType.CHANNELS

        # Default to custom if we can't classify
        return DynamicShapeType.CUSTOM

    def _check_dimension_support(self,
                                dim_index: int,
                                dim_type: DynamicShapeType,
                                tensor: TensorInfo,
                                dim_size: int) -> Tuple[bool, str]:
        """
        Check if a dynamic dimension is supported by Horizon X5 BPU.

        Args:
            dim_index: Index of the dimension
            dim_type: Type of the dynamic dimension
            tensor: TensorInfo containing the dimension
            dim_size: Size of the dimension

        Returns:
            Tuple of (is_supported, constraint_description)
        """
        # Check if dim_size is 0 (unknown dimension)
        if dim_size == 0:
            return False, "Unknown dimension (dim_value=0) is not supported. Use dynamic shape (-1) or fixed value."

        # Check dimension type
        if dim_type == DynamicShapeType.BATCH_SIZE:
            if dim_index in self.SUPPORTED_BATCH_DIMS:
                return True, f"Batch dimension at position {dim_index} is supported by Horizon X5 BPU."
            else:
                return False, f"Batch dimension at position {dim_index} is not in supported positions {self.SUPPORTED_BATCH_DIMS}."

        elif dim_type == DynamicShapeType.SEQUENCE_LENGTH:
            return True, f"Sequence length dimension is supported (max recommended: {self.MAX_SEQUENCE_LENGTH})."

        elif dim_type == DynamicShapeType.HEIGHT_WIDTH:
            if self.MIN_SPATIAL_DIM <= self.MAX_SPATIAL_DIM:
                return True, f"Spatial dimension is supported (recommended range: {self.MIN_SPATIAL_DIM}-{self.MAX_SPATIAL_DIM})."
            else:
                return False, f"Spatial dimension {dim_index} may cause performance issues on Horizon X5 BPU."

        elif dim_type == DynamicShapeType.CHANNELS:
            return True, "Channel dimension (usually fixed) is supported."

        elif dim_type == DynamicShapeType.CUSTOM:
            return False, f"Custom dynamic dimension at position {dim_index} may not be supported on Horizon X5 BPU."

        return False, f"Unknown dynamic dimension at position {dim_index}."

    def _check_batch_independence(self, dynamic_dims: List[DynamicDimensionInfo]) -> bool:
        """
        Check if the model is batch-size independent.
        A batch-independent model can handle variable batch sizes.

        Args:
            dynamic_dims: List of dynamic dimension information

        Returns:
            True if model is batch-independent
        """
        # Check if the first dimension is dynamic (batch size)
        batch_dims = [d for d in dynamic_dims if d.dimension_type == DynamicShapeType.BATCH_SIZE]

        if batch_dims:
            # If batch dimension is supported, model is batch-independent
            return all(dim.is_supported for dim in batch_dims)

        return False

    def _validate_bpu_compatibility(self,
                                   dynamic_dims: List[DynamicDimensionInfo]) -> Dict[str, Any]:
        """
        Validate dynamic dimensions against Horizon X5 BPU constraints.

        Args:
            dynamic_dims: List of dynamic dimension information

        Returns:
            Dict with validation results
        """
        warnings = []
        errors = []
        valid = True

        for dim in dynamic_dims:
            if not dim.is_supported:
                valid = False
                errors.append(f"Unsupported dynamic dimension {dim.dimension_index} "
                            f"({dim.dimension_type.value}): {dim.constraint_description}")

            # Add warnings for potentially problematic dimensions
            if dim.dimension_type == DynamicShapeType.CUSTOM:
                warnings.append(f"Custom dynamic dimension at position {dim.dimension_index} "
                              f"may require special handling on Horizon X5 BPU.")

            if dim.dimension_type == DynamicShapeType.HEIGHT_WIDTH:
                warnings.append(f"Spatial dynamic dimension at position {dim.dimension_index} "
                              f"may impact inference performance.")

        return {
            "valid": valid,
            "warnings": warnings,
            "errors": errors
        }

    def _get_recommended_value(self, dim_type: DynamicShapeType, dim_index: int) -> Optional[int]:
        """
        Get recommended fixed value for a dynamic dimension type.

        Args:
            dim_type: Type of dynamic dimension
            dim_index: Position of the dimension

        Returns:
            Recommended fixed value, or None
        """
        recommendations = {
            DynamicShapeType.BATCH_SIZE: 1,
            DynamicShapeType.SEQUENCE_LENGTH: 128,
            DynamicShapeType.HEIGHT_WIDTH: 224,
            DynamicShapeType.CHANNELS: None  # Should remain dynamic
        }

        return recommendations.get(dim_type)

    def suggest_dynamic_shape(self, tensor: TensorInfo) -> List[Optional[int]]:
        """
        Suggest a concrete dynamic shape for a tensor.

        Args:
            tensor: TensorInfo object

        Returns:
            List of shape values (None for dynamic, int for fixed)
        """
        if tensor.shape is None:
            return []

        suggested_shape = []
        for idx, dim_size in enumerate(tensor.shape):
            if dim_size == -1 or dim_size == 0:
                # Find matching dynamic dimension info
                dim_info = next((d for d in self._analyze_tensor_dynamic_shapes([tensor], [])),
                               None)
                if dim_info:
                    suggested_shape.append(self._get_recommended_value(
                        dim_info.dimension_type, idx
                    ))
                else:
                    suggested_shape.append(None)
            else:
                suggested_shape.append(dim_size)

        return suggested_shape
