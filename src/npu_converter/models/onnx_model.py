"""
ONNX Model Data Structures

This module defines data models for ONNX model handling, including:
- ONNXModel: Main model container with metadata
- TensorInfo: Input/output tensor information
- OperatorInfo: Operator information
- VersionInfo: ONNX version information
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime


@dataclass
class TensorInfo:
    """Information about an input or output tensor."""
    name: str
    shape: List[int]
    dtype: str
    data_type: str = ""
    doc_string: str = ""
    location: str = ""  # e.g., "input", "output"

    def __str__(self) -> str:
        return f"{self.name}: {self.shape} {self.dtype}"


@dataclass
class OperatorInfo:
    """Information about an operator in the ONNX graph."""
    op_type: str
    domain: str = ""
    version: int = 0
    attributes: Dict[str, Any] = field(default_factory=dict)
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    location: str = ""  # e.g., "main", "initializer"

    def __str__(self) -> str:
        return f"{self.domain}.{self.op_type} v{self.version}"


@dataclass
class VersionInfo:
    """ONNX version and metadata information."""
    onnx_version: str = ""
    opset_version: int = 0
    producer_name: str = ""
    producer_version: str = ""
    domain: str = ""
    model_version: str = ""
    doc_string: str = ""
    generated_by: str = ""
    model_location: str = ""

    def __str__(self) -> str:
        return f"ONNX {self.onnx_version} (opset {self.opset_version})"


@dataclass
class ModelMetadata:
    """Complete metadata extracted from an ONNX model."""
    model_name: str = ""
    graph_name: str = ""
    total_nodes: int = 0
    total_tensors: int = 0
    input_count: int = 0
    output_count: int = 0
    initializer_count: int = 0
    opset_domains: List[str] = field(default_factory=list)
    ir_version: int = 0
    opset_versions: Dict[str, int] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    description: str = ""
    created_at: Optional[datetime] = None

    def __str__(self) -> str:
        return f"{self.model_name} - {self.total_nodes} nodes, {self.total_tensors} tensors"


@dataclass
class ONNXModel:
    """
    Container for an ONNX model with complete metadata.

    This class wraps the ONNX ModelProto and provides structured
    access to model information, metadata, and operations.
    """
    model_proto: Any
    model_path: Optional[Path] = None
    metadata: ModelMetadata = field(default_factory=ModelMetadata)
    input_tensors: List[TensorInfo] = field(default_factory=list)
    output_tensors: List[TensorInfo] = field(default_factory=list)
    operators: List[OperatorInfo] = field(default_factory=list)
    version_info: VersionInfo = field(default_factory=VersionInfo)
    raw_size: int = 0  # Size in bytes
    loaded_at: Optional[datetime] = field(default_factory=datetime.now)

    @property
    def is_loaded(self) -> bool:
        """Check if the model is properly loaded."""
        return self.model_proto is not None

    @property
    def input_count(self) -> int:
        """Get the number of input tensors."""
        return len(self.input_tensors)

    @property
    def output_count(self) -> int:
        """Get the number of output tensors."""
        return len(self.output_tensors)

    @property
    def operator_count(self) -> int:
        """Get the number of operators."""
        return len(self.operators)

    def get_tensor_by_name(self, name: str) -> Optional[TensorInfo]:
        """Get a tensor by name from input or output tensors."""
        for tensor in self.input_tensors + self.output_tensors:
            if tensor.name == name:
                return tensor
        return None

    def get_operators_by_type(self, op_type: str) -> List[OperatorInfo]:
        """Get all operators of a specific type."""
        return [op for op in self.operators if op.op_type == op_type]

    def has_operator(self, op_type: str) -> bool:
        """Check if the model contains an operator of the given type."""
        return any(op.op_type == op_type for op in self.operators)

    def __str__(self) -> str:
        model_name = self.metadata.model_name or self.model_path.name if self.model_path else "Unnamed Model"
        return f"{model_name} - {self.operator_count} operators, {self.input_count} inputs, {self.output_count} outputs"
