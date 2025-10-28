"""
Optimization Report Generator

Generates detailed optimization reports in multiple formats (JSON, HTML, PDF).
Provides comprehensive analysis of optimization results and recommendations.

Author: Story 2.6 Implementation
Version: 1.0.0
Date: 2025-10-28
"""

import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import asdict

logger = logging.getLogger(__name__)

try:
    import yaml
except ImportError:
    yaml = None

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    logger.warning("Matplotlib not available, charts will not be generated")


class OptimizationReportGenerator:
    """
    Generates comprehensive optimization reports.

    Supports JSON, HTML, and Markdown output formats with visualizations.
    """

    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize report generator.

        Args:
            output_dir: Output directory for reports (default: ./reports)
        """
        self.output_dir = Path(output_dir) if output_dir else Path("./reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initialized OptimizationReportGenerator at {self.output_dir}")

    def generate_report(
        self,
        result,
        format: str = "html",
        include_charts: bool = True,
        include_recommendations: bool = True
    ) -> str:
        """
        Generate optimization report.

        Args:
            result: ParameterOptimizationResult instance
            format: Output format (json, html, markdown, pdf)
            include_charts: Include visualization charts
            include_recommendations: Include recommendations section

        Returns:
            Path to generated report file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_type = result.model_characteristics.model_type.value

        filename = f"optimization_report_{model_type}_{timestamp}.{format}"
        output_path = self.output_dir / filename

        if format.lower() == "json":
            self._generate_json_report(result, output_path)
        elif format.lower() == "html":
            self._generate_html_report(result, output_path, include_charts, include_recommendations)
        elif format.lower() == "markdown":
            self._generate_markdown_report(result, output_path, include_charts, include_recommendations)
        elif format.lower() == "pdf":
            # Generate HTML first, then convert to PDF
            html_path = output_path.with_suffix('.html')
            self._generate_html_report(result, html_path, include_charts, include_recommendations)
            self._convert_html_to_pdf(html_path, output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")

        logger.info(f"Generated {format.upper()} report: {output_path}")

        return str(output_path)

    def _generate_json_report(self, result, output_path: Path) -> None:
        """Generate JSON report."""
        data = {
            'report_info': {
                'generated_at': datetime.now().isoformat(),
                'model_type': result.model_characteristics.model_type.value,
                'optimization_strategy': result.strategy_used.value,
                'objective': result.objective.value
            },
            'best_params': result.best_params,
            'best_metrics': asdict(result.best_metrics),
            'model_characteristics': asdict(result.model_characteristics),
            'optimization_details': {
                'improvement_percentage': result.improvement_percentage,
                'execution_time': result.execution_time,
                'strategy_used': result.strategy_used.value,
                'objective': result.objective.value
            },
            'recommendations': result.recommendations,
            'optimization_history': [
                asdict(entry) for entry in result.optimization_result.history
            ]
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def _generate_html_report(
        self,
        result,
        output_path: Path,
        include_charts: bool,
        include_recommendations: bool
    ) -> None:
        """Generate HTML report with CSS styling."""
        html_content = self._build_html_content(result, include_charts, include_recommendations)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def _generate_markdown_report(
        self,
        result,
        output_path: Path,
        include_charts: bool,
        include_recommendations: bool
    ) -> None:
        """Generate Markdown report."""
        md_content = self._build_markdown_content(result, include_charts, include_recommendations)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

    def _build_html_content(self, result, include_charts: bool, include_recommendations: bool) -> str:
        """Build HTML content."""
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Optimization Report - {result.model_characteristics.model_type.value}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        .metric-card {{
            background-color: #ecf0f1;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }}
        .metric-label {{
            font-weight: bold;
            color: #2c3e50;
        }}
        .metric-value {{
            color: #27ae60;
            font-size: 1.2em;
        }}
        .params-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        .params-table th, .params-table td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        .params-table th {{
            background-color: #3498db;
            color: white;
        }}
        .params-table tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        .recommendation {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }}
        .chart-container {{
            margin: 20px 0;
            text-align: center;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Parameter Optimization Report</h1>

        <h2>📋 Summary</h2>
        <div class="metric-card">
            <p><span class="metric-label">Model Type:</span> <span class="metric-value">{result.model_characteristics.model_type.value.upper()}</span></p>
            <p><span class="metric-label">Strategy:</span> <span class="metric-value">{result.strategy_used.value.replace('_', ' ').title()}</span></p>
            <p><span class="metric-label">Objective:</span> <span class="metric-value">{result.objective.value.replace('_', ' ').title()}</span></p>
            <p><span class="metric-label">Execution Time:</span> <span class="metric-value">{result.execution_time:.2f} seconds</span></p>
            <p><span class="metric-label">Improvement:</span> <span class="metric-value">{result.improvement_percentage:.1f}%</span></p>
        </div>

        <h2>🎯 Best Parameters</h2>
        <table class="params-table">
            <thead>
                <tr>
                    <th>Parameter</th>
                    <th>Value</th>
                </tr>
            </thead>
            <tbody>
"""

        for param, value in result.best_params.items():
            html += f"""
                <tr>
                    <td>{param}</td>
                    <td>{value}</td>
                </tr>
"""

        html += """
            </tbody>
        </table>

        <h2>📊 Performance Metrics</h2>
        <div class="metric-card">
            <p><span class="metric-label">Accuracy:</span> <span class="metric-value">{:.2%}</span></p>
            <p><span class="metric-label">Latency:</span> <span class="metric-value">{:.1f} ms</span></p>
            <p><span class="metric-label">Throughput:</span> <span class="metric-value">{:.1f} samples/sec</span></p>
            <p><span class="metric-label">Memory Usage:</span> <span class="metric-value">{:.1f} MB</span></p>
            <p><span class="metric-label">Compatibility:</span> <span class="metric-value">{:.2%}</span></p>
            <p><span class="metric-label">Success Rate:</span> <span class="metric-value">{:.2%}</span></p>
        </div>
""".format(
            result.best_metrics.accuracy,
            result.best_metrics.latency,
            result.best_metrics.throughput,
            result.best_metrics.memory_usage,
            result.best_metrics.compatibility,
            result.best_metrics.success_rate
        )

        if include_charts and HAS_MATPLOTLIB:
            chart_path = self._generate_charts(result)
            if chart_path:
                html += f"""
        <h2>📈 Optimization Progress</h2>
        <div class="chart-container">
            <img src="{chart_path}" alt="Optimization Charts" style="max-width: 100%;">
        </div>
"""

        if include_recommendations:
            html += """
        <h2>💡 Recommendations</h2>
"""
            for rec in result.recommendations:
                html += f"""
        <div class="recommendation">
            {rec}
        </div>
"""

        html += f"""
        <h2>🔍 Model Characteristics</h2>
        <div class="metric-card">
            <p><span class="metric-label">Model Size:</span> <span class="metric-value">{result.model_characteristics.model_size:,} parameters</span></p>
            <p><span class="metric-label">File Size:</span> <span class="metric-value">{result.model_characteristics.file_size / (1024*1024):.1f} MB</span></p>
            <p><span class="metric-label">Complexity Score:</span> <span class="metric-value">{result.model_characteristics.complexity_score:.2f}</span></p>
            <p><span class="metric-label">Quantization Sensitivity:</span> <span class="metric-value">{result.model_characteristics.quantization_sensitivity:.2f}</span></p>
            <p><span class="metric-label">Recommended Quantization:</span> <span class="metric-value">{result.model_characteristics.recommended_quantization}-bit</span></p>
        </div>

        <div class="footer">
            <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} by NPU Converter Optimization System</p>
        </div>
    </div>
</body>
</html>
"""
        return html

    def _build_markdown_content(self, result, include_charts: bool, include_recommendations: bool) -> str:
        """Build Markdown content."""
        md = f"""# 🚀 Parameter Optimization Report

## 📋 Summary

- **Model Type:** {result.model_characteristics.model_type.value.upper()}
- **Strategy:** {result.strategy_used.value.replace('_', ' ').title()}
- **Objective:** {result.objective.value.replace('_', ' ').title()}
- **Execution Time:** {result.execution_time:.2f} seconds
- **Improvement:** {result.improvement_percentage:.1f}%

## 🎯 Best Parameters

| Parameter | Value |
|-----------|-------|
"""

        for param, value in result.best_params.items():
            md += f"| {param} | {value} |\n"

        md += f"""
## 📊 Performance Metrics

- **Accuracy:** {result.best_metrics.accuracy:.2%}
- **Latency:** {result.best_metrics.latency:.1f} ms
- **Throughput:** {result.best_metrics.throughput:.1f} samples/sec
- **Memory Usage:** {result.best_metrics.memory_usage:.1f} MB
- **Compatibility:** {result.best_metrics.compatibility:.2%}
- **Success Rate:** {result.best_metrics.success_rate:.2%}

## 🔍 Model Characteristics

- **Model Size:** {result.model_characteristics.model_size:,} parameters
- **File Size:** {result.model_characteristics.file_size / (1024*1024):.1f} MB
- **Complexity Score:** {result.model_characteristics.complexity_score:.2f}
- **Quantization Sensitivity:** {result.model_characteristics.quantization_sensitivity:.2f}
- **Recommended Quantization:** {result.model_characteristics.recommended_quantization}-bit

"""

        if include_recommendations and result.recommendations:
            md += "## 💡 Recommendations\n\n"
            for rec in result.recommendations:
                md += f"- {rec}\n"

        md += f"""
---
*Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} by NPU Converter Optimization System*
"""

        return md

    def _generate_charts(self, result) -> Optional[str]:
        """Generate optimization progress charts."""
        if not HAS_MATPLOTLIB:
            return None

        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

            # Plot 1: Convergence curve
            history = result.optimization_result.history
            scores = [score for _, score in history]
            iterations = range(1, len(scores) + 1)

            ax1.plot(iterations, scores, 'b-', linewidth=2, label='Score')
            ax1.set_xlabel('Iteration')
            ax1.set_ylabel('Optimization Score')
            ax1.set_title('Optimization Convergence')
            ax1.grid(True, alpha=0.3)
            ax1.legend()

            # Plot 2: Metrics comparison
            metrics = {
                'Accuracy': result.best_metrics.accuracy * 100,
                'Latency': (1.0 / (1.0 + result.best_metrics.latency / 1000.0)) * 100,  # Normalized
                'Throughput': min(result.best_metrics.throughput, 100),  # Cap at 100
                'Compatibility': result.best_metrics.compatibility * 100,
                'Success Rate': result.best_metrics.success_rate * 100
            }

            ax2.bar(metrics.keys(), metrics.values(), color=['#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c'])
            ax2.set_ylabel('Score (%)')
            ax2.set_title('Performance Metrics')
            ax2.set_ylim(0, 100)

            # Add value labels on bars
            for i, (k, v) in enumerate(metrics.items()):
                ax2.text(i, v + 2, f'{v:.1f}%', ha='center', va='bottom')

            plt.tight_layout()

            # Save chart
            chart_path = self.output_dir / "optimization_charts.png"
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()

            logger.info(f"Generated optimization charts: {chart_path}")
            return str(chart_path)

        except Exception as e:
            logger.error(f"Failed to generate charts: {e}")
            return None

    def _convert_html_to_pdf(self, html_path: Path, pdf_path: Path) -> None:
        """Convert HTML to PDF (placeholder, requires additional tools)."""
        # In production, would use tools like weasyprint or wkhtmltopdf
        logger.warning("PDF conversion not implemented, HTML report generated instead")
        # Copy HTML as PDF for now
        pdf_path.write_text(html_path.read_text())
