"""
Structure Validator for ONNX Models

Performs comprehensive structure validation including:
- Operator dependency analysis (topological sorting, cycle detection)
- Topology validation
- Node connectivity checking
- Weight integrity verification
- Dead node detection
- Model structure completeness
"""

import logging
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass

from ..models.onnx_model import ONNXModel
from .operator_dependency_analyzer import (
    OperatorDependencyAnalyzer,
    DependencyAnalysisResult
)

logger = logging.getLogger(__name__)


@dataclass
class StructureValidationResult:
    """Result of structure validation"""
    is_valid: bool
    issues: List[str]
    warnings: List[str]
    node_count: int
    edge_count: int
    dependency_analysis: Optional[DependencyAnalysisResult] = None
    orphaned_nodes: List[str] = None
    unused_weights: List[str] = None
    disconnected_subgraphs: List[List[str]] = None

    def __post_init__(self):
        if self.orphaned_nodes is None:
            self.orphaned_nodes = []
        if self.unused_weights is None:
            self.unused_weights = []
        if self.disconnected_subgraphs is None:
            self.disconnected_subgraphs = []


class StructureValidator:
    """
    Validates the structural integrity of ONNX models.

    Extends validation capabilities beyond basic compatibility checking
    to ensure model topology is well-formed and complete.

    Features:
    - Operator dependency analysis with cycle detection
    - Dead node and orphaned tensor detection
    - Unused weight and parameter detection
    - Graph connectivity analysis
    """

    def __init__(self):
        """Initialize the StructureValidator"""
        logger.info("Initializing StructureValidator")
        self.dependency_analyzer = OperatorDependencyAnalyzer()

    def validate_structure(self, model: ONNXModel) -> StructureValidationResult:
        """
        Validate the structure of an ONNX model.

        Args:
            model: ONNXModel instance

        Returns:
            StructureValidationResult with validation results
        """
        logger.info(f"Starting structure validation for model: {model}")

        issues = []
        warnings = []

        if not model.model_proto or not model.model_proto.graph:
            issues.append("Model graph is empty or missing")
            return StructureValidationResult(
                is_valid=False,
                issues=issues,
                warnings=warnings,
                node_count=0,
                edge_count=0
            )

        # Step 1: Analyze operator dependencies
        dependency_result = self.dependency_analyzer.analyze_dependencies(model)

        if dependency_result.errors:
            issues.extend(dependency_result.errors)

        if dependency_result.warnings:
            warnings.extend(dependency_result.warnings)

        # Step 2: Check for orphaned nodes (nodes not connected to inputs/outputs)
        orphaned_nodes = self._find_orphaned_nodes(model, dependency_result.dependency_graph)
        if orphaned_nodes:
            warnings.append(f"Found {len(orphaned_nodes)} orphaned nodes (not connected to main graph)")
            issues.append(f"Orphaned nodes: {orphaned_nodes[:5]}")  # Report first 5

        # Step 3: Check for unused weights and parameters
        unused_weights = self._find_unused_weights(model)
        if unused_weights:
            warnings.append(f"Found {len(unused_weights)} unused weights/parameters")
            # Not an error, just wasteful

        # Step 4: Check for disconnected subgraphs
        disconnected = self._find_disconnected_subgraphs(
            dependency_result.dependency_graph,
            dependency_result.topological_order
        )
        if disconnected:
            warnings.append(f"Found {len(disconnected)} disconnected subgraphs")

        # Step 5: Check tensor connectivity
        tensor_issues = self._check_tensor_connectivity(model)
        issues.extend(tensor_issues)

        # Calculate edge count from dependency graph
        edge_count = sum(len(node.dependencies) for node in dependency_result.dependency_graph.values())

        # Compile results
        result = StructureValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            node_count=len(dependency_result.dependency_graph),
            edge_count=edge_count,
            dependency_analysis=dependency_result,
            orphaned_nodes=orphaned_nodes,
            unused_weights=unused_weights,
            disconnected_subgraphs=disconnected
        )

        logger.info(f"Structure validation completed: {result.is_valid} "
                   f"({len(issues)} issues, {len(warnings)} warnings)")
        return result

    def _find_orphaned_nodes(self,
                            model: ONNXModel,
                            dependency_graph: Dict[str, Any]) -> List[str]:
        """
        Find nodes that are not connected to the main graph path.

        Args:
            model: ONNXModel instance
            dependency_graph: Dependency graph from operator analysis

        Returns:
            List of orphaned node names
        """
        orphaned = []

        if not model.model_proto.graph:
            return orphaned

        graph = model.model_proto.graph
        node_names = {getattr(node, "name", f"node_{i}") for i, node in enumerate(graph.node)}

        # Get all nodes that are part of the main graph path (connected to inputs/outputs)
        main_path_nodes = self._find_main_path_nodes(model, dependency_graph)

        # Find nodes not in the main path
        for node_name in node_names:
            if node_name not in main_path_nodes and node_name in dependency_graph:
                orphaned.append(node_name)

        return orphaned

    def _find_main_path_nodes(self,
                             model: ONNXModel,
                             dependency_graph: Dict[str, Any]) -> Set[str]:
        """
        Find nodes that are connected to inputs or outputs.

        Args:
            model: ONNXModel instance
            dependency_graph: Dependency graph

        Returns:
            Set of node names in the main path
        """
        main_path = set()

        if not model.model_proto.graph:
            return main_path

        graph = model.model_proto.graph

        # Get all input tensor names
        input_tensors = set()
        for input_info in graph.input:
            if input_info.name not in {init.name for init in graph.initializer}:
                input_tensors.add(input_info.name)

        # Get all output tensor names
        output_tensors = set()
        for output_info in graph.output:
            output_tensors.add(output_info.name)

        # Map tensor names to producing nodes
        output_to_node = {}
        for node_name, node in dependency_graph.items():
            for output in node.outputs:
                output_to_node[output] = node_name

        # Find nodes that produce output tensors (sink nodes)
        sink_nodes = {output_to_node[output] for output in output_tensors if output in output_to_node}

        # If no sink nodes found, this might be an issue
        if not sink_nodes:
            logger.warning("No sink nodes found (nodes producing outputs)")
            return main_path

        # Perform reverse BFS from sink nodes to find all nodes in main path
        visited = set()
        queue = list(sink_nodes)

        while queue:
            node_name = queue.pop(0)
            if node_name in visited:
                continue

            visited.add(node_name)
            main_path.add(node_name)

            # Add dependencies of this node
            if node_name in dependency_graph:
                for dep in dependency_graph[node_name].dependencies:
                    if dep not in visited:
                        queue.append(dep)

        return main_path

    def _find_unused_weights(self, model: ONNXModel) -> List[str]:
        """
        Find weights and initializers that are not used by any node.

        Args:
            model: ONNXModel instance

        Returns:
            List of unused weight names
        """
        unused = []

        if not model.model_proto.graph:
            return unused

        graph = model.model_proto.graph

        # Get all initializers
        initializers = {init.name for init in graph.initializer}

        # Get all inputs used by nodes
        used_inputs = set()
        for node in graph.node:
            for input_name in node.input:
                used_inputs.add(input_name)

        # Find initializers not used as inputs
        for init_name in initializers:
            if init_name not in used_inputs:
                unused.append(init_name)

        return unused

    def _find_disconnected_subgraphs(self,
                                    dependency_graph: Dict[str, Any],
                                    topological_order: List[str]) -> List[List[str]]:
        """
        Find disconnected subgraphs in the model.

        Args:
            dependency_graph: Dependency graph
            topological_order: Topological ordering of nodes

        Returns:
            List of subgraphs (each subgraph is a list of node names)
        """
        if not topological_order:
            return []

        # Build adjacency list for BFS/DFS
        graph_adj = {}
        for node_name in topological_order:
            if node_name in dependency_graph:
                graph_adj[node_name] = dependency_graph[node_name].dependencies

        visited = set()
        subgraphs = []

        for node_name in topological_order:
            if node_name in visited:
                continue

            # BFS to find connected component
            subgraph = []
            queue = [node_name]

            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue

                visited.add(current)
                subgraph.append(current)

                # Add neighbors (dependencies)
                if current in graph_adj:
                    for neighbor in graph_adj[current]:
                        if neighbor not in visited:
                            queue.append(neighbor)

            # Only consider subgraphs with more than one node
            if len(subgraph) > 1:
                subgraphs.append(subgraph)

        return subgraphs

    def _check_tensor_connectivity(self, model: ONNXModel) -> List[str]:
        """
        Check tensor connectivity throughout the graph.

        Args:
            model: ONNXModel instance

        Returns:
            List of tensor connectivity issues
        """
        issues = []

        if not model.model_proto.graph:
            return issues

        graph = model.model_proto.graph

        # Track all tensors that should exist
        tensor_names = set()

        # Collect from inputs
        for input_info in graph.input:
            if input_info.name not in {init.name for init in graph.initializer}:
                tensor_names.add(input_info.name)

        # Collect from outputs
        for output_info in graph.output:
            tensor_names.add(output_info.name)

        # Collect from node outputs
        for node in graph.node:
            for output in node.output:
                tensor_names.add(output)

        # Check if all tensors are actually defined
        all_defined_tensors = set()
        for node in graph.node:
            for input_tensor in node.input:
                all_defined_tensors.add(input_tensor)

        # Find tensors that are used but not defined
        used_but_undefined = set()
        for tensor_name in tensor_names:
            if tensor_name not in all_defined_tensors and tensor_name not in {
                init.name for init in graph.initializer
            }:
                used_but_undefined.add(tensor_name)

        if used_but_undefined:
            issues.append(f"Found {len(used_but_undefined)} tensors used but not defined")

        return issues
