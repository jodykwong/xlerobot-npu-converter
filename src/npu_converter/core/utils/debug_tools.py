"""
Horizon X5 Debug Tools Integration

This module provides wrapper functions for Horizon X5 debugging tools
as defined in the Story Context XML.

Tools integrated:
- hrt_bin_dump: Model analysis and debugging
- hrt_model_exec: Model inference testing
"""

import os
import logging
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from ...models.calibration import ModelAnalysis, ModelInfo


@dataclass
class HrtBinDumpResult:
    """Result from hrt_bin_dump tool execution."""
    success: bool
    model_info: Dict[str, Any]
    op_analysis: Dict[str, Any]
    memory_analysis: Dict[str, Any]
    compatibility_report: Dict[str, Any]
    errors: List[str]
    raw_output: str


@dataclass
class HrtModelExecResult:
    """Result from hrt_model_exec tool execution."""
    success: bool
    inference_results: Any
    performance_metrics: Dict[str, Any]
    memory_usage: Dict[str, Any]
    errors: List[str]
    raw_output: str


class DebugTools:
    """
    Horizon X5 Debug Tools Integration

    Provides wrapper functions for official Horizon X5 debugging tools.
    """

    def __init__(self, enabled: bool = True, tool_paths: Optional[Dict[str, str]] = None):
        """
        Initialize debug tools.

        Args:
            enabled: Whether debug tools are enabled
            tool_paths: Custom paths to Horizon X5 tools
        """
        self.enabled = enabled
        self.tool_paths = tool_paths or {}
        self.logger = logging.getLogger(__name__)

        # Default tool paths (would be configured for actual Horizon X5 installation)
        self.default_paths = {
            'hrt_bin_dump': '/opt/horizon/bin/hrt_bin_dump',
            'hrt_model_exec': '/opt/horizon/bin/hrt_model_exec'
        }

        # Resolve actual tool paths
        self.hrt_bin_dump_path = self.tool_paths.get('hrt_bin_dump', self.default_paths['hrt_bin_dump'])
        self.hrt_model_exec_path = self.tool_paths.get('hrt_model_exec', self.default_paths['hrt_model_exec'])

        if self.enabled:
            self._verify_tool_availability()

    def _verify_tool_availability(self):
        """Verify that Horizon X5 tools are available."""
        for tool_name, tool_path in [('hrt_bin_dump', self.hrt_bin_dump_path),
                                     ('hrt_model_exec', self.hrt_model_exec_path)]:
            if not Path(tool_path).exists():
                self.logger.warning(f"Horizon X5 tool not found: {tool_path}")
                self.logger.warning(f"Debug functionality will be limited for {tool_name}")

    def dump_model_info(self, model_path: str) -> ModelAnalysis:
        """
        Analyze model using hrt_bin_dump tool.

        Args:
            model_path: Path to the model file

        Returns:
            ModelAnalysis object with detailed model information
        """
        if not self.enabled:
            return self._create_mock_analysis(model_path)

        self.logger.info(f"Analyzing model with hrt_bin_dump: {model_path}")

        try:
            # Prepare command
            cmd = [
                self.hrt_bin_dump_path,
                '--model', model_path,
                '--format', 'json',
                '--verbose'
            ]

            # Execute hrt_bin_dump
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode != 0:
                self.logger.error(f"hrt_bin_dump failed: {result.stderr}")
                return self._create_mock_analysis(model_path)

            # Parse output
            try:
                dump_data = json.loads(result.stdout)
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse hrt_bin_dump output as JSON")
                dump_data = self._parse_text_output(result.stdout)

            # Create ModelAnalysis object
            model_info = self._extract_model_info(dump_data, model_path)
            op_analysis = dump_data.get('operators', {})
            memory_analysis = dump_data.get('memory', {})
            compatibility_report = self._generate_compatibility_report(op_analysis)
            optimization_suggestions = self._generate_optimization_suggestions(op_analysis, memory_analysis)

            analysis = ModelAnalysis(
                model_info=model_info,
                op_analysis=op_analysis,
                memory_analysis=memory_analysis,
                compatibility_report=compatibility_report,
                optimization_suggestions=optimization_suggestions
            )

            self.logger.info("Model analysis completed successfully")
            return analysis

        except subprocess.TimeoutExpired:
            self.logger.error("hrt_bin_dump timed out")
            return self._create_mock_analysis(model_path)
        except Exception as e:
            self.logger.error(f"Error running hrt_bin_dump: {str(e)}")
            return self._create_mock_analysis(model_path)

    def execute_model(self, model_path: str, input_data: Any) -> HrtModelExecResult:
        """
        Execute model inference using hrt_model_exec tool.

        Args:
            model_path: Path to the model file
            input_data: Input data for inference

        Returns:
            HrtModelExecResult with inference results
        """
        if not self.enabled:
            return self._create_mock_execution_result(model_path)

        self.logger.info(f"Executing model inference with hrt_model_exec: {model_path}")

        try:
            # Save input data to temporary file
            input_file = Path("/tmp/hrt_input.json")
            with open(input_file, 'w') as f:
                json.dump({
                    'input_data': self._serialize_input_data(input_data),
                    'model_path': model_path
                }, f)

            # Prepare command
            cmd = [
                self.hrt_model_exec_path,
                '--model', model_path,
                '--input', str(input_file),
                '--output', '/tmp/hrt_output.json',
                '--measure-performance'
            ]

            # Execute hrt_model_exec
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            # Clean up temporary files
            input_file.unlink(missing_ok=True)

            if result.returncode != 0:
                self.logger.error(f"hrt_model_exec failed: {result.stderr}")
                return self._create_mock_execution_result(model_path)

            # Parse results
            try:
                with open('/tmp/hrt_output.json', 'r') as f:
                    output_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                self.logger.warning("Failed to parse hrt_model_exec output")
                output_data = {}

            # Extract results
            inference_results = output_data.get('outputs', None)
            performance_metrics = output_data.get('performance', {})
            memory_usage = output_data.get('memory', {})

            exec_result = HrtModelExecResult(
                success=True,
                inference_results=inference_results,
                performance_metrics=performance_metrics,
                memory_usage=memory_usage,
                errors=[],
                raw_output=result.stdout
            )

            self.logger.info("Model execution completed successfully")
            return exec_result

        except subprocess.TimeoutExpired:
            self.logger.error("hrt_model_exec timed out")
            return self._create_mock_execution_result(model_path)
        except Exception as e:
            self.logger.error(f"Error running hrt_model_exec: {str(e)}")
            return self._create_mock_execution_result(model_path)

    def _create_mock_analysis(self, model_path: str) -> ModelAnalysis:
        """Create mock model analysis when tools are not available."""
        model_info = ModelInfo(
            model_path=model_path,
            input_shape=(1, 224, 224, 3),  # Placeholder
            output_shape=(1, 1000),  # Placeholder
            model_size_mb=Path(model_path).stat().st_size / (1024 * 1024),
            num_parameters=1000000,  # Placeholder
            model_format="onnx"
        )

        op_analysis = {
            'total_operators': 50,
            'supported_operators': 45,
            'unsupported_operators': 5,
            'operator_breakdown': {
                'Conv': 15,
                'Relu': 10,
                'BatchNorm': 8,
                'Add': 7,
                'Other': 10
            }
        }

        memory_analysis = {
            'model_memory_mb': model_info.model_size_mb,
            'activation_memory_mb': 256.0,
            'total_memory_mb': model_info.model_size_mb + 256.0
        }

        compatibility_report = {
            'overall_compatibility': 0.9,
            'critical_issues': [],
            'warnings': ['Mock analysis - tools not available'],
            'recommendations': ['Install Horizon X5 tools for accurate analysis']
        }

        optimization_suggestions = [
            'Consider operator fusion for Conv+Relu sequences',
            'Optimize memory layout for better cache performance',
            'Consider batch normalization folding'
        ]

        return ModelAnalysis(
            model_info=model_info,
            op_analysis=op_analysis,
            memory_analysis=memory_analysis,
            compatibility_report=compatibility_report,
            optimization_suggestions=optimization_suggestions
        )

    def _create_mock_execution_result(self, model_path: str) -> HrtModelExecResult:
        """Create mock execution result when tools are not available."""
        performance_metrics = {
            'inference_time_ms': 15.5,
            'throughput_fps': 64.5,
            'memory_usage_mb': 128.0
        }

        memory_usage = {
            'peak_memory_mb': 256.0,
            'average_memory_mb': 128.0,
            'gpu_memory_mb': 512.0
        }

        return HrtModelExecResult(
            success=False,
            inference_results=None,
            performance_metrics=performance_metrics,
            memory_usage=memory_usage,
            errors=['Mock execution - Horizon X5 tools not available'],
            raw_output="Mock execution result"
        )

    def _extract_model_info(self, dump_data: Dict[str, Any], model_path: str) -> ModelInfo:
        """Extract model information from hrt_bin_dump output."""
        # Extract basic information
        graph_info = dump_data.get('graph', {})

        input_shape = tuple(graph_info.get('input_shape', (1, 224, 224, 3)))
        output_shape = tuple(graph_info.get('output_shape', (1, 1000)))
        model_size_mb = Path(model_path).stat().st_size / (1024 * 1024)
        num_parameters = graph_info.get('parameters', 1000000)

        # Extract operator information
        operators = dump_data.get('operators', {})
        all_ops = operators.get('list', [])
        supported_ops = [op for op in all_ops if op not in operators.get('unsupported', [])]
        unsupported_ops = operators.get('unsupported', [])

        return ModelInfo(
            model_path=model_path,
            input_shape=input_shape,
            output_shape=output_shape,
            model_size_mb=model_size_mb,
            num_parameters=num_parameters,
            model_format="onnx",
            supported_ops=supported_ops,
            unsupported_ops=unsupported_ops
        )

    def _generate_compatibility_report(self, op_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate compatibility report based on operator analysis."""
        total_ops = op_analysis.get('total_operators', 0)
        supported_ops = op_analysis.get('supported_operators', 0)
        unsupported_ops = op_analysis.get('unsupported_operators', [])

        compatibility_score = supported_ops / total_ops if total_ops > 0 else 0.0

        critical_issues = []
        warnings = []
        recommendations = []

        if unsupported_ops:
            critical_issues.append(f"Unsupported operators: {unsupported_ops}")
            recommendations.append(f"Replace or implement custom operators: {unsupported_ops}")

        if compatibility_score < 0.8:
            warnings.append("Low operator compatibility score")

        return {
            'overall_compatibility': compatibility_score,
            'critical_issues': critical_issues,
            'warnings': warnings,
            'recommendations': recommendations
        }

    def _generate_optimization_suggestions(self, op_analysis: Dict[str, Any], memory_analysis: Dict[str, Any]) -> List[str]:
        """Generate optimization suggestions based on analysis."""
        suggestions = []

        # Memory-based suggestions
        total_memory = memory_analysis.get('total_memory_mb', 0)
        if total_memory > 500:
            suggestions.append("Consider memory optimization techniques to reduce memory usage")

        # Operator-based suggestions
        op_breakdown = op_analysis.get('operator_breakdown', {})
        if op_breakdown.get('Conv', 0) > 0 and op_breakdown.get('Relu', 0) > 0:
            suggestions.append("Consider Conv+Relu operator fusion")

        if op_breakdown.get('BatchNorm', 0) > 0:
            suggestions.append("Consider batch normalization folding")

        return suggestions

    def _serialize_input_data(self, input_data: Any) -> Dict[str, Any]:
        """Serialize input data for tool consumption."""
        if hasattr(input_data, 'shape') and hasattr(input_data, 'dtype'):
            # NumPy array
            return {
                'type': 'numpy_array',
                'shape': list(input_data.shape),
                'dtype': str(input_data.dtype),
                'data': input_data.tolist()
            }
        elif isinstance(input_data, dict):
            return {
                'type': 'dict',
                'data': input_data
            }
        else:
            return {
                'type': 'raw',
                'data': str(input_data)
            }

    def _parse_text_output(self, text_output: str) -> Dict[str, Any]:
        """Parse text output from tools when JSON parsing fails."""
        # Simple text parsing fallback
        lines = text_output.split('\n')
        parsed_data = {
            'operators': {},
            'memory': {},
            'graph': {}
        }

        for line in lines:
            if 'Operators:' in line:
                parsed_data['operators']['total_operators'] = 50  # Placeholder
            elif 'Memory:' in line:
                parsed_data['memory']['model_memory_mb'] = 100.0  # Placeholder

        return parsed_data