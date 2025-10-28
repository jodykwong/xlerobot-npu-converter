"""
Model Compatibility Checker

Checks ONNX model compatibility with Horizon X5 BPU including:
- Operator support verification
- ONNX version compatibility
- Shape compatibility validation
- Precision support checking
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..models.onnx_model import ONNXModel, TensorInfo, OperatorInfo

logger = logging.getLogger(__name__)


class CompatibilityLevel(Enum):
    """Compatibility levels."""
    FULL = "full"
    PARTIAL = "partial"
    INCOMPATIBLE = "incompatible"


@dataclass
class CompatibilityResult:
    """Result of a compatibility check."""
    is_compatible: bool
    level: CompatibilityLevel
    issues: List[str]
    warnings: List[str]
    details: Dict[str, Any] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}


@dataclass
class FullCompatibilityResult:
    """Complete compatibility check result."""
    operator_check: CompatibilityResult
    version_check: CompatibilityResult
    shape_check: CompatibilityResult
    precision_check: CompatibilityResult
    overall: CompatibilityResult

    @property
    def is_fully_compatible(self) -> bool:
        """Check if model is fully compatible."""
        return self.overall.is_compatible and self.overall.level == CompatibilityLevel.FULL

    @property
    def all_issues(self) -> List[str]:
        """Get all compatibility issues."""
        issues = []
        issues.extend(self.operator_check.issues)
        issues.extend(self.version_check.issues)
        issues.extend(self.shape_check.issues)
        issues.extend(self.precision_check.issues)
        return issues

    @property
    def all_warnings(self) -> List[str]:
        """Get all compatibility warnings."""
        warnings = []
        warnings.extend(self.operator_check.warnings)
        warnings.extend(self.version_check.warnings)
        warnings.extend(self.shape_check.warnings)
        warnings.extend(self.precision_check.warnings)
        return warnings


class CompatibilityChecker:
    """
    Checks ONNX model compatibility with Horizon X5 BPU.

    This class validates ONNX models to ensure they are compatible
    with Horizon X5 BPU toolchain and runtime constraints.
    """

    def __init__(self) -> None:
        """Initialize the compatibility checker."""
        self.supported_operators = self._get_supported_operators()
        self.supported_data_types = self._get_supported_data_types()
        self.max_opset_version = 17
        self.min_opset_version = 8

        logger.info(f"Initialized CompatibilityChecker with {len(self.supported_operators)} supported operators")

    def check_operator_support(self, model: ONNXModel) -> CompatibilityResult:
        """
        Check if all operators in the model are supported by Horizon X5.

        Args:
            model: ONNXModel to check

        Returns:
            CompatibilityResult for operator support
        """
        logger.info(f"Checking operator support for {model}")
        issues = []
        warnings = []
        unsupported_ops = []
        deprecated_ops = []

        for op in model.operators:
            if op.op_type not in self.supported_operators:
                unsupported_ops.append(op.op_type)
                issues.append(f"Unsupported operator: {op.op_type}")
            elif op.op_type in ["Dropout", "BatchNormalization"]:
                # Check if these are being used incorrectly
                if op.op_type == "Dropout" and len(op.outputs) > 1:
                    warnings.append(f"Dropout with multiple outputs detected: {op.op_type}")
                elif op.op_type == "BatchNormalization":
                    warnings.append(f"BatchNormalization detected, ensure training=False for inference")

        # Check for custom operators
        custom_domains = set()
        for op in model.operators:
            if op.domain and op.domain not in ["", "ai.onnx"]:
                custom_domains.add(op.domain)
                issues.append(f"Custom operator domain detected: {op.domain}")

        if custom_domains:
            warnings.append(f"Model contains {len(custom_domains)} custom domains")

        # Check operator count
        if model.operator_count > 10000:
            warnings.append(f"Large model detected: {model.operator_count} operators (may impact performance)")

        is_compatible = len(issues) == 0
        level = CompatibilityLevel.FULL if is_compatible else CompatibilityLevel.PARTIAL

        result = CompatibilityResult(
            is_compatible=is_compatible,
            level=level,
            issues=issues,
            warnings=warnings,
            details={
                "supported_operators": len(self.supported_operators),
                "unsupported_operators": list(set(unsupported_ops)),
                "custom_domains": list(custom_domains),
                "total_operators": model.operator_count
            }
        )

        logger.info(f"Operator check complete: {result.level.value}, issues: {len(issues)}, warnings: {len(warnings)}")
        return result

    def check_version_compatibility(self, model: ONNXModel) -> CompatibilityResult:
        """
        Check if the model uses a compatible ONNX version.

        Args:
            model: ONNXModel to check

        Returns:
            CompatibilityResult for version compatibility
        """
        logger.info(f"Checking version compatibility for {model}")
        issues = []
        warnings = []

        opset_version = model.version_info.opset_version

        # Check opset version
        if opset_version < self.min_opset_version:
            issues.append(f"ONNX opset version {opset_version} is below minimum required {self.min_opset_version}")
        elif opset_version > self.max_opset_version:
            warnings.append(f"ONNX opset version {opset_version} is above recommended maximum {self.max_opset_version}")

        # Check for multiple opset versions
        if len(model.version_info.opset_versions) > 1:
            warnings.append(f"Multiple opset versions detected: {model.version_info.opset_versions}")

        # Check domain compatibility
        for domain, version in model.version_info.opset_versions.items():
            if domain not in ["", "ai.onnx"]:
                if domain == "ai.onnx.contrib":
                    warnings.append(f"Contrib ops detected in domain {domain}")
                else:
                    issues.append(f"Unsupported opset domain: {domain} v{version}")

        is_compatible = len(issues) == 0
        level = CompatibilityLevel.FULL if is_compatible else CompatibilityLevel.PARTIAL

        result = CompatibilityResult(
            is_compatible=is_compatible,
            level=level,
            issues=issues,
            warnings=warnings,
            details={
                "opset_version": opset_version,
                "min_opset": self.min_opset_version,
                "max_opset": self.max_opset_version,
                "opset_domains": model.version_info.opset_versions,
                "producer_name": model.version_info.producer_name,
                "producer_version": model.version_info.producer_version
            }
        )

        logger.info(f"Version check complete: {result.level.value}, issues: {len(issues)}, warnings: {len(warnings)}")
        return result

    def check_shape_compatibility(self, model: ONNXModel) -> CompatibilityResult:
        """
        Check if the model has compatible shapes for BPU execution.

        Args:
            model: ONNXModel to check

        Returns:
            CompatibilityResult for shape compatibility
        """
        logger.info(f"Checking shape compatibility for {model}")
        issues = []
        warnings = []

        # Check for dynamic shapes
        dynamic_shapes = []
        for tensor in model.input_tensors + model.output_tensors:
            for dim in tensor.shape:
                if dim == -1:
                    dynamic_shapes.append(tensor.name)
                    break

        if dynamic_shapes:
            warnings.append(f"Dynamic shapes detected: {len(dynamic_shapes)} tensors have unknown dimensions")
            warnings.append(f"Dynamic tensors: {', '.join(dynamic_shapes[:5])}" + ("..." if len(dynamic_shapes) > 5 else ""))

        # Check for extremely large shapes
        large_shapes = []
        for tensor in model.input_tensors + model.output_tensors:
            total_elements = 1
            for dim in tensor.shape:
                if dim > 0:
                    total_elements *= dim
            if total_elements > 1000000000:  # 1 billion elements
                large_shapes.append(tensor.name)

        if large_shapes:
            warnings.append(f"Large tensors detected: {', '.join(large_shapes[:5])}" + ("..." if len(large_shapes) > 5 else ""))

        # Check for invalid shapes
        invalid_shapes = []
        for tensor in model.input_tensors + model.output_tensors:
            if any(dim == 0 for dim in tensor.shape):
                invalid_shapes.append(tensor.name)

        if invalid_shapes:
            issues.append(f"Invalid shapes detected: {', '.join(invalid_shapes)}")

        # Check batch dimension
        batch_dimensions = []
        for tensor in model.input_tensors:
            if tensor.shape[0] == -1:  # Dynamic batch
                batch_dimensions.append(tensor.name)

        if batch_dimensions:
            warnings.append(f"Dynamic batch dimension in: {', '.join(batch_dimensions[:3])}" + ("..." if len(batch_dimensions) > 3 else ""))

        is_compatible = len(issues) == 0
        level = CompatibilityLevel.FULL if is_compatible else CompatibilityLevel.PARTIAL

        result = CompatibilityResult(
            is_compatible=is_compatible,
            level=level,
            issues=issues,
            warnings=warnings,
            details={
                "dynamic_shapes": dynamic_shapes,
                "large_shapes": large_shapes,
                "invalid_shapes": invalid_shapes,
                "dynamic_batch": batch_dimensions,
                "total_input_tensors": len(model.input_tensors),
                "total_output_tensors": len(model.output_tensors)
            }
        )

        logger.info(f"Shape check complete: {result.level.value}, issues: {len(issues)}, warnings: {len(warnings)}")
        return result

    def check_precision_support(self, model: ONNXModel) -> CompatibilityResult:
        """
        Check if the model uses supported data types.

        Args:
            model: ONNXModel to check

        Returns:
            CompatibilityResult for precision support
        """
        logger.info(f"Checking precision support for {model}")
        issues = []
        warnings = []

        used_data_types = set()
        unsupported_types = []

        # Collect all data types used
        for tensor in model.input_tensors + model.output_tensors:
            dtype = tensor.dtype
            used_data_types.add(dtype)
            if dtype not in self.supported_data_types:
                unsupported_types.append(dtype)

        if unsupported_types:
            issues.append(f"Unsupported data types detected: {', '.join(unsupported_types)}")

        # Check for mixed precision
        if len(used_data_types) > 3:
            warnings.append(f"Multiple data types detected: {', '.join(used_data_types)}")

        # Check for specific high-precision types
        if "FLOAT64" in used_data_types:
            warnings.append("FLOAT64 detected, BPU typically uses FLOAT16 or INT8")

        if "COMPLEX64" in used_data_types or "COMPLEX128" in used_data_types:
            issues.append("Complex data types are not supported by BPU")

        is_compatible = len(issues) == 0
        level = CompatibilityLevel.FULL if is_compatible else CompatibilityLevel.PARTIAL

        result = CompatibilityResult(
            is_compatible=is_compatible,
            level=level,
            issues=issues,
            warnings=warnings,
            details={
                "used_data_types": list(used_data_types),
                "supported_data_types": list(self.supported_data_types),
                "unsupported_types": unsupported_types,
                "mixed_precision": len(used_data_types) > 1
            }
        )

        logger.info(f"Precision check complete: {result.level.value}, issues: {len(issues)}, warnings: {len(warnings)}")
        return result

    def full_compatibility_check(self, model: ONNXModel) -> FullCompatibilityResult:
        """
        Perform a complete compatibility check.

        Args:
            model: ONNXModel to check

        Returns:
            FullCompatibilityResult with all checks
        """
        logger.info(f"Starting full compatibility check for {model}")

        # Perform all checks
        operator_check = self.check_operator_support(model)
        version_check = self.check_version_compatibility(model)
        shape_check = self.check_shape_compatibility(model)
        precision_check = self.check_precision_support(model)

        # Determine overall compatibility
        all_issues = (
            operator_check.issues +
            version_check.issues +
            shape_check.issues +
            precision_check.issues
        )

        all_warnings = (
            operator_check.warnings +
            version_check.warnings +
            shape_check.warnings +
            precision_check.warnings
        )

        is_compatible = len(all_issues) == 0
        level = CompatibilityLevel.FULL if is_compatible else CompatibilityLevel.PARTIAL

        overall = CompatibilityResult(
            is_compatible=is_compatible,
            level=level,
            issues=all_issues,
            warnings=all_warnings,
            details={
                "operator_compatible": operator_check.is_compatible,
                "version_compatible": version_check.is_compatible,
                "shape_compatible": shape_check.is_compatible,
                "precision_compatible": precision_check.is_compatible
            }
        )

        result = FullCompatibilityResult(
            operator_check=operator_check,
            version_check=version_check,
            shape_check=shape_check,
            precision_check=precision_check,
            overall=overall
        )

        logger.info(f"Full compatibility check complete: {result.overall.level.value}")
        return result

    def _get_supported_operators(self) -> set:
        """
        Get the set of operators supported by Horizon X5 BPU.

        Returns:
            Set of supported operator names
        """
        # Base operators supported by Horizon X5 BPU
        supported = {
            # Core operators
            "Add", "Sub", "Mul", "Div",
            "Relu", "Tanh", "Sigmoid", "LeakyRelu",
            "Conv", "ConvTranspose",
            "MaxPool", "AveragePool", "GlobalAveragePool", "GlobalMaxPool",
            "MatMul", "Gemm",
            "Shape", "Reshape", "Transpose", "Squeeze", "Unsqueeze",
            "Concat", "Slice", "Split",
            "Pad", "Constant", "Identity",
            "Softmax", "LogSoftmax", "Log",
            "Exp", "Sqrt", "Reciprocal",
            "Min", "Max",
            "Where", "Equal", "Greater", "Less",
            "Cast", "Resize",
            "BatchNormalization", "Dropout", "LayerNormalization",
            "Gather", "Scatter", "Tile",
            "DepthToSpace", "SpaceToDepth",
            "QuantizeLinear", "DequantizeLinear",
        }
        return supported

    def _get_supported_data_types(self) -> set:
        """
        Get the set of data types supported by Horizon X5 BPU.

        Returns:
            Set of supported data type names
        """
        return {
            "FLOAT", "FLOAT16", "BFLOAT16",
            "INT8", "UINT8",
            "INT16", "UINT16",
            "INT32", "UINT32",
            "INT64", "UINT64",
            "BOOL",
            # Note: STRING and complex types are not supported
        }

    def get_compatibility_summary(self, result: FullCompatibilityResult) -> Dict[str, Any]:
        """
        Get a summary of the compatibility check result.

        Args:
            result: FullCompatibilityResult to summarize

        Returns:
            Dictionary with compatibility summary
        """
        return {
            "overall_compatible": result.is_fully_compatible,
            "overall_level": result.overall.level.value,
            "total_issues": len(result.all_issues),
            "total_warnings": len(result.all_warnings),
            "checks": {
                "operator_support": {
                    "compatible": result.operator_check.is_compatible,
                    "level": result.operator_check.level.value,
                    "issues": len(result.operator_check.issues),
                    "warnings": len(result.operator_check.warnings)
                },
                "version_compatibility": {
                    "compatible": result.version_check.is_compatible,
                    "level": result.version_check.level.value,
                    "issues": len(result.version_check.issues),
                    "warnings": len(result.version_check.warnings)
                },
                "shape_compatibility": {
                    "compatible": result.shape_check.is_compatible,
                    "level": result.shape_check.level.value,
                    "issues": len(result.shape_check.issues),
                    "warnings": len(result.shape_check.warnings)
                },
                "precision_support": {
                    "compatible": result.precision_check.is_compatible,
                    "level": result.precision_check.level.value,
                    "issues": len(result.precision_check.issues),
                    "warnings": len(result.precision_check.warnings)
                }
            }
        }
