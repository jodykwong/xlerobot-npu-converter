"""
Operator Dependency Analyzer

Analyzes operator dependencies in ONNX models including:
- Dependency graph construction
- Topological sorting
- Cycle detection
- Critical path analysis
"""

import logging
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

from ..models.onnx_model import (
    ONNXModel,
    OperatorInfo
)

logger = logging.getLogger(__name__)


class DependencyType(Enum):
    """Types of operator dependencies"""
    DIRECT = "direct"  # Direct input dependency
    CONTROL = "control"  # Control flow dependency
    INITIALIZER = "initializer"  # Weight/parameter dependency


@dataclass
class OperatorNode:
    """Node in the operator dependency graph"""
    operator: OperatorInfo
    node_name: str
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # Names of dependent nodes


@dataclass
class DependencyAnalysisResult:
    """Result of operator dependency analysis"""
    is_valid: bool
    has_cycles: bool
    total_operators: int
    dependency_graph: Dict[str, OperatorNode]
    topological_order: List[str]
    cycles: List[List[str]]
    warnings: List[str]
    errors: List[str]

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.errors is None:
            self.errors = []


class OperatorDependencyAnalyzer:
    """
    Analyzes operator dependencies in ONNX models.

    This analyzer:
    - Builds a dependency graph from operator inputs/outputs
    - Performs topological sorting to ensure correct execution order
    - Detects cycles that would prevent model execution
    - Identifies critical paths for optimization opportunities
    """

    def __init__(self):
        """Initialize the OperatorDependencyAnalyzer"""
        logger.info("Initializing OperatorDependencyAnalyzer")

    def analyze_dependencies(self, model: ONNXModel) -> DependencyAnalysisResult:
        """
        Analyze operator dependencies in the model.

        Args:
            model: ONNXModel instance

        Returns:
            DependencyAnalysisResult with detailed dependency information
        """
        logger.info(f"Starting operator dependency analysis for model: {model}")

        if not model.model_proto:
            logger.error("Model proto is None")
            return DependencyAnalysisResult(
                is_valid=False,
                has_cycles=False,
                total_operators=0,
                dependency_graph={},
                topological_order=[],
                cycles=[],
                warnings=[],
                errors=["Model proto is None"]
            )

        try:
            # Step 1: Build operator nodes from model graph
            operator_nodes = self._build_operator_nodes(model)

            # Step 2: Build dependency graph
            dependency_graph = self._build_dependency_graph(operator_nodes, model)

            # Step 3: Detect cycles
            cycles = self._detect_cycles(dependency_graph)

            # Step 4: Topological sorting (only if no cycles)
            topological_order = []
            has_cycles = len(cycles) > 0

            if not has_cycles:
                topological_order = self._topological_sort(dependency_graph)
                if len(topological_order) != len(dependency_graph):
                    # This shouldn't happen if no cycles, but worth checking
                    logger.warning("Topological sort did not include all nodes")
            else:
                # Still try to get partial order for nodes not in cycles
                partial_order = self._partial_topological_sort(dependency_graph, cycles)

            # Step 5: Compile results
            result = DependencyAnalysisResult(
                is_valid=not has_cycles,
                has_cycles=has_cycles,
                total_operators=len(operator_nodes),
                dependency_graph=dependency_graph,
                topological_order=topological_order,
                cycles=cycles,
                warnings=self._generate_warnings(operator_nodes, dependency_graph, has_cycles),
                errors=self._generate_errors(has_cycles, cycles)
            )

            logger.info(f"Dependency analysis completed: {result.total_operators} operators, "
                       f"{len(result.cycles)} cycles detected")
            return result

        except Exception as e:
            logger.error(f"Failed to analyze dependencies: {e}")
            return DependencyAnalysisResult(
                is_valid=False,
                has_cycles=False,
                total_operators=0,
                dependency_graph={},
                topological_order=[],
                cycles=[],
                warnings=[],
                errors=[f"Analysis failed: {str(e)}"]
            )

    def _build_operator_nodes(self, model: ONNXModel) -> List[OperatorNode]:
        """
        Build operator nodes from the model graph.

        Args:
            model: ONNXModel instance

        Returns:
            List of OperatorNode objects
        """
        operator_nodes = []

        if not model.model_proto.graph:
            logger.warning("Model graph is None")
            return operator_nodes

        graph = model.model_proto.graph

        # Process all nodes in the graph
        for node in graph.node:
            node_name = getattr(node, "name", f"node_{len(operator_nodes)}")

            operator_info = OperatorInfo(
                op_type=node.op_type,
                domain=getattr(node, "domain", ""),
                version=0,  # We'll extract this if available
                inputs=list(node.input),
                outputs=list(node.output),
                location="main"
            )

            operator_node = OperatorNode(
                operator=operator_info,
                node_name=node_name,
                inputs=list(node.input),
                outputs=list(node.output),
                dependencies=[]
            )

            operator_nodes.append(operator_node)

        logger.info(f"Built {len(operator_nodes)} operator nodes")
        return operator_nodes

    def _build_dependency_graph(self,
                               operator_nodes: List[OperatorNode],
                               model: ONNXModel) -> Dict[str, OperatorNode]:
        """
        Build a dependency graph from operator nodes.

        Args:
            operator_nodes: List of OperatorNode objects
            model: ONNXModel instance

        Returns:
            Dictionary mapping node names to OperatorNode with dependencies
        """
        dependency_graph = {}
        output_to_node = {}  # Map outputs to their producing nodes

        # First pass: map outputs to nodes
        for node in operator_nodes:
            output_to_node.update({output: node.node_name for output in node.outputs})
            dependency_graph[node.node_name] = node

        # Second pass: determine dependencies for each node
        for node in operator_nodes:
            dependencies = []

            # Check each input
            for input_tensor in node.inputs:
                # If input is from another node, add that node as dependency
                if input_tensor in output_to_node:
                    producer_node = output_to_node[input_tensor]
                    if producer_node != node.node_name:  # Avoid self-dependency
                        dependencies.append(producer_node)

            # Also check if input is an initializer (constant)
            if model.model_proto.graph:
                initializers = {init.name for init in model.model_proto.graph.initializer}
                for input_tensor in node.inputs:
                    if input_tensor in initializers:
                        # This is an initializer, not a dependency on another node
                        pass  # Don't add to dependencies

            node.dependencies = dependencies

        logger.info(f"Built dependency graph with {len(dependency_graph)} nodes")
        return dependency_graph

    def _detect_cycles(self, dependency_graph: Dict[str, OperatorNode]) -> List[List[str]]:
        """
        Detect cycles in the dependency graph using DFS.

        Args:
            dependency_graph: Dependency graph mapping node names to OperatorNode

        Returns:
            List of cycles (each cycle is a list of node names)
        """
        cycles = []
        visited = set()
        rec_stack = set()
        path = []

        def dfs(node_name: str) -> bool:
            """DFS to detect cycles"""
            if node_name in rec_stack:
                # Found a cycle
                cycle_start = path.index(node_name)
                cycle = path[cycle_start:] + [node_name]
                cycles.append(cycle)
                return True

            if node_name in visited:
                return False

            visited.add(node_name)
            rec_stack.add(node_name)
            path.append(node_name)

            # Visit all dependencies
            if node_name in dependency_graph:
                for dep in dependency_graph[node_name].dependencies:
                    if dfs(dep):
                        # Continue to find more cycles
                        pass

            path.pop()
            rec_stack.remove(node_name)
            return False

        # Start DFS from all nodes
        for node_name in dependency_graph:
            if node_name not in visited:
                dfs(node_name)

        if cycles:
            logger.warning(f"Detected {len(cycles)} cycles in dependency graph")

        return cycles

    def _topological_sort(self, dependency_graph: Dict[str, OperatorNode]) -> List[str]:
        """
        Perform topological sort using Kahn's algorithm.

        Args:
            dependency_graph: Dependency graph mapping node names to OperatorNode

        Returns:
            List of node names in topological order
        """
        # Calculate in-degree for each node
        in_degree = {node_name: 0 for node_name in dependency_graph}

        for node_name, node in dependency_graph.items():
            for dep in node.dependencies:
                if dep in in_degree:
                    in_degree[node_name] += 1

        # Start with nodes that have no dependencies
        queue = [node_name for node_name, degree in in_degree.items() if degree == 0]
        topological_order = []

        while queue:
            # Sort queue for deterministic ordering
            queue.sort()
            node_name = queue.pop(0)
            topological_order.append(node_name)

            # Remove this node and update in-degrees
            if node_name in dependency_graph:
                for dependent in dependency_graph[node_name].dependencies:
                    if dependent in in_degree:
                        in_degree[dependent] -= 1
                        if in_degree[dependent] == 0:
                            queue.append(dependent)

        logger.info(f"Topological sort completed: {len(topological_order)} nodes")
        return topological_order

    def _partial_topological_sort(self,
                                  dependency_graph: Dict[str, OperatorNode],
                                  cycles: List[List[str]]) -> List[str]:
        """
        Perform partial topological sort, excluding nodes in cycles.

        Args:
            dependency_graph: Dependency graph mapping node names to OperatorNode
            cycles: List of cycles

        Returns:
            List of node names in topological order (excluding cycle nodes)
        """
        # Get all nodes in cycles
        cycle_nodes = set()
        for cycle in cycles:
            cycle_nodes.update(cycle)

        # Remove cycle nodes from dependency graph
        filtered_graph = {
            name: node for name, node in dependency_graph.items()
            if name not in cycle_nodes
        }

        # Perform topological sort on filtered graph
        return self._topological_sort(filtered_graph)

    def _generate_warnings(self,
                          operator_nodes: List[OperatorNode],
                          dependency_graph: Dict[str, OperatorNode],
                          has_cycles: bool) -> List[str]:
        """Generate warnings based on analysis"""
        warnings = []

        # Check for nodes with high fan-out (many dependencies)
        high_fan_out = [
            node_name for node_name, node in dependency_graph.items()
            if len(node.dependencies) > 10
        ]
        if high_fan_out:
            warnings.append(f"High fan-out nodes detected: {high_fan_out[:5]}")

        # Check for disconnected nodes
        if len(dependency_graph) != len(operator_nodes):
            warnings.append(f"Some nodes may be disconnected from the main graph")

        return warnings

    def _generate_errors(self, has_cycles: bool, cycles: List[List[str]]) -> List[str]:
        """Generate errors based on analysis"""
        errors = []

        if has_cycles:
            errors.append(f"Circular dependencies detected: {len(cycles)} cycles found")
            for i, cycle in enumerate(cycles[:3]):  # Report first 3 cycles
                errors.append(f"  Cycle {i+1}: {' → '.join(cycle)}")

        return errors

    def get_critical_path(self,
                         dependency_graph: Dict[str, OperatorNode],
                         topological_order: List[str]) -> List[str]:
        """
        Find the critical path (longest dependency chain) in the graph.

        Args:
            dependency_graph: Dependency graph mapping node names to OperatorNode
            topological_order: Topological ordering of nodes

        Returns:
            List of node names representing the critical path
        """
        # Calculate longest path to each node
        longest_path = {node: 0 for node in topological_order}
        predecessor = {node: None for node in topological_order}

        for node_name in topological_order:
            if node_name in dependency_graph:
                for dep in dependency_graph[node_name].dependencies:
                    if dep in longest_path:
                        if longest_path[dep] + 1 > longest_path[node_name]:
                            longest_path[node_name] = longest_path[dep] + 1
                            predecessor[node_name] = dep

        # Find the node with the longest path
        if not longest_path:
            return []

        critical_node = max(longest_path, key=longest_path.get)
        critical_path = []

        # Reconstruct the path
        current = critical_node
        while current is not None:
            critical_path.insert(0, current)
            current = predecessor[current]

        logger.info(f"Critical path found: {len(critical_path)} nodes")
        return critical_path
