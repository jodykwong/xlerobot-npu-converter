"""
Model Metadata Extractor

Extracts structured metadata from ONNX models including:
- Input/output tensor information
- Operator types and attributes
- Version and compatibility information
- Model structure and statistics
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..models.onnx_model import (
    TensorInfo,
    OperatorInfo,
    VersionInfo,
    ModelMetadata,
    ONNXModel
)

logger = logging.getLogger(__name__)


class ModelMetadataExtractor:
    """
    Extracts comprehensive metadata from ONNX models.

    This class analyzes ONNX models and extracts structured information
    about tensors, operators, version compatibility, and model statistics.
    """

    def extract_input_tensors(self, model: ONNXModel) -> List[TensorInfo]:
        """
        Extract information about input tensors from the model.

        Args:
            model: ONNXModel instance

        Returns:
            List of TensorInfo objects for all input tensors
        """
        logger.info(f"Extracting input tensors from {model}")
        input_tensors = []

        if not model.model_proto:
            logger.error("Model proto is None")
            return input_tensors

        try:
            graph = model.model_proto.graph
            if not graph:
                logger.error("Model graph is None")
                return input_tensors

            # Extract input information
            for input_info in graph.input:
                if input_info.name in {init.name for init in graph.initializer}:
                    # Skip initializers (they are parameters, not inputs)
                    continue

                tensor_type = input_info.type.tensor_type
                shape = []
                dtype_str = "unknown"

                # Extract shape
                if tensor_type.HasField("shape"):
                    for dim in tensor_type.shape.dim:
                        if dim.HasField("dim_value"):
                            shape.append(dim.dim_value)
                        elif dim.HasField("dim_param"):
                            shape.append(-1)  # Dynamic dimension
                        else:
                            shape.append(0)

                # Extract data type
                if tensor_type.HasField("elem_type"):
                    dtype_str = self._map_tensor_elem_type(tensor_type.elem_type)

                tensor_info = TensorInfo(
                    name=input_info.name,
                    shape=shape,
                    dtype=dtype_str,
                    data_type=dtype_str,
                    doc_string=getattr(input_info, "doc_string", ""),
                    location="input"
                )
                input_tensors.append(tensor_info)

            logger.info(f"Extracted {len(input_tensors)} input tensors")
            return input_tensors

        except Exception as e:
            logger.error(f"Failed to extract input tensors: {e}")
            return []

    def extract_output_tensors(self, model: ONNXModel) -> List[TensorInfo]:
        """
        Extract information about output tensors from the model.

        Args:
            model: ONNXModel instance

        Returns:
            List of TensorInfo objects for all output tensors
        """
        logger.info(f"Extracting output tensors from {model}")
        output_tensors = []

        if not model.model_proto:
            logger.error("Model proto is None")
            return output_tensors

        try:
            graph = model.model_proto.graph
            if not graph:
                logger.error("Model graph is None")
                return output_tensors

            # Extract output information
            for output_info in graph.output:
                tensor_type = output_info.type.tensor_type
                shape = []
                dtype_str = "unknown"

                # Extract shape
                if tensor_type.HasField("shape"):
                    for dim in tensor_type.shape.dim:
                        if dim.HasField("dim_value"):
                            shape.append(dim.dim_value)
                        elif dim.HasField("dim_param"):
                            shape.append(-1)  # Dynamic dimension
                        else:
                            shape.append(0)

                # Extract data type
                if tensor_type.HasField("elem_type"):
                    dtype_str = self._map_tensor_elem_type(tensor_type.elem_type)

                tensor_info = TensorInfo(
                    name=output_info.name,
                    shape=shape,
                    dtype=dtype_str,
                    data_type=dtype_str,
                    doc_string=getattr(output_info, "doc_string", ""),
                    location="output"
                )
                output_tensors.append(tensor_info)

            logger.info(f"Extracted {len(output_tensors)} output tensors")
            return output_tensors

        except Exception as e:
            logger.error(f"Failed to extract output tensors: {e}")
            return []

    def extract_operators(self, model: ONNXModel) -> List[OperatorInfo]:
        """
        Extract information about operators from the model.

        Args:
            model: ONNXModel instance

        Returns:
            List of OperatorInfo objects for all operators
        """
        logger.info(f"Extracting operators from {model}")
        operators = []

        if not model.model_proto:
            logger.error("Model proto is None")
            return operators

        try:
            graph = model.model_proto.graph
            if not graph:
                logger.error("Model graph is None")
                return operators

            # Extract operators from nodes
            for node in graph.node:
                op_info = OperatorInfo(
                    op_type=node.op_type,
                    domain=node.domain or "",
                    version=0,  # TODO: Extract version if available
                    attributes={attr.name: self._extract_attribute_value(attr) for attr in node.attribute},
                    inputs=list(node.input),
                    outputs=list(node.output),
                    location="main"
                )
                operators.append(op_info)

            logger.info(f"Extracted {len(operators)} operators")
            return operators

        except Exception as e:
            logger.error(f"Failed to extract operators: {e}")
            return []

    def extract_version_info(self, model: ONNXModel) -> VersionInfo:
        """
        Extract version and metadata information from the model.

        Args:
            model: ONNXModel instance

        Returns:
            VersionInfo object containing version details
        """
        logger.info(f"Extracting version info from {model}")
        version_info = VersionInfo()

        if not model.model_proto:
            logger.error("Model proto is None")
            return version_info

        try:
            opset_import = model.model_proto.opset_import
            if opset_import:
                for opset in opset_import:
                    version_info.opset_version = max(version_info.opset_version, opset.version)
                    if opset.domain:
                        version_info.opset_versions[opset.domain] = opset.version
                        if opset.domain not in version_info.opsets_domains:
                            version_info.opsets_domains.append(opset.domain)

            # Extract producer information
            if hasattr(model.model_proto, "producer_name"):
                version_info.producer_name = model.model_proto.producer_name

            if hasattr(model.model_proto, "producer_version"):
                version_info.producer_version = model.model_proto.producer_version

            if hasattr(model.model_proto, "domain"):
                version_info.domain = model.model_proto.domain

            if hasattr(model.model_proto, "model_version"):
                version_info.model_version = str(model.model_proto.model_version)

            if hasattr(model.model_proto, "doc_string"):
                version_info.doc_string = model.model_proto.doc_string

            logger.info(f"Extracted version info: {version_info}")
            return version_info

        except Exception as e:
            logger.error(f"Failed to extract version info: {e}")
            return version_info

    def extract_model_metadata(self, model: ONNXModel) -> ModelMetadata:
        """
        Extract comprehensive model metadata.

        Args:
            model: ONNXModel instance

        Returns:
            ModelMetadata object containing all metadata
        """
        logger.info(f"Extracting model metadata from {model}")
        metadata = ModelMetadata()

        if not model.model_proto:
            logger.error("Model proto is None")
            return metadata

        try:
            graph = model.model_proto.graph

            if hasattr(graph, "name"):
                metadata.model_name = graph.name

            if hasattr(model.model_proto, "ir_version"):
                metadata.ir_version = model.model_proto.ir_version

            # Count total tensors
            metadata.total_tensors = len(graph.input) + len(graph.output) + len(graph.initializer)
            metadata.input_count = len([i for i in graph.input if i.name not in {init.name for init in graph.initializer}])
            metadata.output_count = len(graph.output)
            metadata.initializer_count = len(graph.initializer)

            # Count nodes
            metadata.total_nodes = len(graph.node)

            # Extract opset domains
            for opset in model.model_proto.opset_import:
                if opset.domain and opset.domain not in metadata.opsets_domains:
                    metadata.opsets_domains.append(opset.domain)

            # Set creation time
            metadata.created_at = model.loaded_at

            logger.info(f"Extracted model metadata: {metadata}")
            return metadata

        except Exception as e:
            logger.error(f"Failed to extract model metadata: {e}")
            return metadata

    def _map_tensor_elem_type(self, elem_type: int) -> str:
        """
        Map ONNX tensor element type to string representation.

        Args:
            elem_type: ONNX tensor element type code

        Returns:
            String representation of the tensor type
        """
        # ONNX tensor element types
        type_map = {
            1: "FLOAT",
            2: "UINT8",
            3: "INT8",
            4: "UINT16",
            5: "INT16",
            6: "INT32",
            7: "STRING",
            8: "BOOL",
            9: "FLOAT16",
            10: "DOUBLE",
            11: "UINT32",
            12: "UINT64",
            13: "COMPLEX64",
            14: "COMPLEX128",
            15: "BFLOAT16",
        }
        return type_map.get(elem_type, f"UNKNOWN({elem_type})")

    def _extract_attribute_value(self, attr: Any) -> Any:
        """
        Extract value from an ONNX attribute.

        Args:
            attr: ONNX attribute object

        Returns:
            Extracted attribute value
        """
        # TODO: Implement attribute value extraction
        # This is a placeholder implementation
        return f"<attribute:{attr.name}>"
