"""
SenseVoice ASR Report Generator

This module generates comprehensive conversion reports for SenseVoice ASR models.
Reports are available in multiple formats: JSON, HTML, and PDF.

Key Features:
- Comprehensive conversion metrics
- Multi-dimensional validation results
- Performance analysis and benchmarks
- Optimization details and recommendations
- Multi-language support summary
- Audio format compatibility matrix

Author: Story 2.3 Implementation
Version: 1.0.0
Date: 2025-10-28
"""

from typing import Any, Dict, List, Optional, Union
import logging
from pathlib import Path
from datetime import datetime
import json
import base64
from io import BytesIO

from ...core.models.config_model import ConfigModel
from ...core.models.result_model import ResultModel
from ...core.interfaces.validator import ValidationResult
from ...complete_flows.sensevoice_complete_flow import (
    SenseVoiceConversionLevel,
    SenseVoiceProcessingMode
)

logger = logging.getLogger(__name__)


class SenseVoiceReportGenerator:
    """
    SenseVoice ASR conversion report generator.

    This class generates comprehensive reports for SenseVoice ASR model conversions,
    including validation results, performance metrics, optimization details,
    and recommendations.
    """

    def __init__(
        self,
        config: Optional[ConfigModel] = None,
        conversion_level: SenseVoiceConversionLevel = SenseVoiceConversionLevel.PRODUCTION,
        output_formats: Optional[List[str]] = None
    ):
        """
        Initialize the report generator.

        Args:
            config: Configuration model
            conversion_level: Conversion level
            output_formats: List of output formats (json, html, pdf)
        """
        self.config = config
        self.conversion_level = conversion_level
        self.output_formats = output_formats or ["json", "html"]

        logger.info(
            f"Initialized SenseVoiceReportGenerator: "
            f"level={conversion_level.value}, formats={self.output_formats}"
        )

    async def generate_report(
        self,
        conversion_id: str,
        conversion_result: ResultModel,
        validation_result: Optional[ValidationResult] = None,
        optimization_result: Optional[Dict[str, Any]] = None,
        processing_mode: Optional[SenseVoiceProcessingMode] = None,
        conversion_level: Optional[SenseVoiceConversionLevel] = None,
        output_path: Optional[Union[str, Path]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive conversion report.

        Args:
            conversion_id: Unique conversion identifier
            conversion_result: Conversion result data
            validation_result: Validation result (optional)
            optimization_result: Optimization results (optional)
            processing_mode: Processing mode (optional)
            conversion_level: Conversion level (optional)
            output_path: Optional output path for report files

        Returns:
            Dict[str, Any]: Report data with file paths and summary
        """
        mode = processing_mode or SenseVoiceProcessingMode.BATCH
        level = conversion_level or self.conversion_level
        timestamp = datetime.now()

        logger.info(f"Generating SenseVoice conversion report: {conversion_id}")

        report_data = {
            "report_metadata": {
                "report_id": f"{conversion_id}_report",
                "conversion_id": conversion_id,
                "timestamp": timestamp.isoformat(),
                "report_version": "1.0.0",
                "generator": "SenseVoiceReportGenerator",
                "formats": self.output_formats
            },
            "conversion_summary": self._generate_conversion_summary(
                conversion_result, mode, level
            ),
            "model_information": self._generate_model_information(conversion_result),
            "validation_results": self._generate_validation_results(validation_result),
            "optimization_details": self._generate_optimization_details(optimization_result),
            "performance_analysis": self._generate_performance_analysis(conversion_result),
            "language_support": self._generate_language_support_summary(conversion_result),
            "audio_formats": self._generate_audio_formats_summary(conversion_result),
            "recommendations": self._generate_recommendations(
                validation_result, optimization_result, mode, level
            ),
            "technical_details": self._generate_technical_details(conversion_result)
        }

        # Generate files for each format
        report_files = {}
        base_output_path = Path(output_path) if output_path else Path(".")

        for fmt in self.output_formats:
            try:
                if fmt.lower() == "json":
                    file_path = await self._generate_json_report(
                        report_data, base_output_path, conversion_id
                    )
                    report_files["json"] = str(file_path)
                elif fmt.lower() == "html":
                    file_path = await self._generate_html_report(
                        report_data, base_output_path, conversion_id
                    )
                    report_files["html"] = str(file_path)
                elif fmt.lower() == "pdf":
                    file_path = await self._generate_pdf_report(
                        report_data, base_output_path, conversion_id
                    )
                    report_files["pdf"] = str(file_path)
                else:
                    logger.warning(f"Unsupported format: {fmt}")
            except Exception as e:
                logger.error(f"Failed to generate {fmt} report: {e}")
                report_files[fmt] = None

        report_data["report_files"] = report_files
        report_data["summary"] = self._generate_report_summary(report_data)

        logger.info(f"Report generation completed: {list(report_files.keys())}")

        return report_data

    def _generate_conversion_summary(
        self,
        conversion_result: ResultModel,
        mode: SenseVoiceProcessingMode,
        level: SenseVoiceConversionLevel
    ) -> Dict[str, Any]:
        """Generate conversion summary section."""
        return {
            "status": "success" if conversion_result.success else "failed",
            "conversion_time_seconds": getattr(conversion_result, "conversion_time", 0),
            "processing_mode": mode.value,
            "conversion_level": level.value,
            "input_model": {
                "path": conversion_result.input_path,
                "size_mb": self._get_file_size_mb(conversion_result.input_path),
                "format": "ONNX"
            },
            "output_model": {
                "path": conversion_result.output_path,
                "size_mb": self._get_file_size_mb(conversion_result.output_path),
                "format": "NPU"
            },
            "optimization_applied": conversion_result.metadata.get("enable_optimizations", False),
            "validation_enabled": conversion_result.metadata.get("enable_validation", False),
            "report_generated": conversion_result.metadata.get("enable_reports", False)
        }

    def _generate_model_information(
        self,
        conversion_result: ResultModel
    ) -> Dict[str, Any]:
        """Generate model information section."""
        return {
            "model_type": "SenseVoice ASR",
            "version": conversion_result.metadata.get("sensevoice_version", "1.0.0"),
            "input_shape": conversion_result.metadata.get("input_shape"),
            "output_shape": conversion_result.metadata.get("output_shape"),
            "input_dtype": conversion_result.metadata.get("input_dtype"),
            "output_dtype": conversion_result.metadata.get("output_dtype"),
            "supported_languages": conversion_result.metadata.get("supported_languages", []),
            "supported_audio_formats": conversion_result.metadata.get("supported_audio_formats", []),
            "parameters": {
                "total_parameters": conversion_result.metadata.get("total_parameters"),
                "trainable_parameters": conversion_result.metadata.get("trainable_parameters"),
                "model_size_mb": self._get_file_size_mb(conversion_result.output_path)
            }
        }

    def _generate_validation_results(
        self,
        validation_result: Optional[ValidationResult]
    ) -> Dict[str, Any]:
        """Generate validation results section."""
        if not validation_result:
            return {
                "validation_performed": False,
                "message": "Validation was not performed"
            }

        return {
            "validation_performed": True,
            "overall_score": validation_result.overall_score,
            "is_valid": validation_result.is_valid,
            "validation_dimensions": validation_result.details.get("validation_dimensions", []),
            "dimension_scores": validation_result.metrics.get("dimension_scores", {}),
            "warnings": validation_result.warnings,
            "errors": [validation_result.error_message] if validation_result.error_message else [],
            "quality_gates": self._check_quality_gates(validation_result),
            "recommendations": self._generate_validation_recommendations(validation_result)
        }

    def _generate_optimization_details(
        self,
        optimization_result: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate optimization details section."""
        if not optimization_result:
            return {
                "optimization_performed": False,
                "message": "Optimization was not performed"
            }

        return {
            "optimization_performed": optimization_result.get("optimized", False),
            "optimization_level": optimization_result.get("optimization_level"),
            "processing_mode": optimization_result.get("processing_mode"),
            "optimizations_applied": optimization_result.get("optimizations_applied", []),
            "optimization_score": optimization_result.get("optimization_metrics", {}).get("optimization_score", 0),
            "language_specific": optimization_result.get("language_specific_optimizations", {}),
            "audio_optimizations": optimization_result.get("audio_optimizations", {}),
            "performance_optimizations": optimization_result.get("performance_optimizations", {}),
            "optimization_metrics": optimization_result.get("optimization_metrics", {})
        }

    def _generate_performance_analysis(
        self,
        conversion_result: ResultModel
    ) -> Dict[str, Any]:
        """Generate performance analysis section."""
        metadata = conversion_result.metadata

        return {
            "conversion_performance": {
                "total_time_seconds": getattr(conversion_result, "conversion_time", 0),
                "throughput_models_per_hour": self._calculate_throughput(conversion_result),
                "bottleneck_analysis": self._analyze_bottlenecks(conversion_result)
            },
            "inference_performance": {
                "inference_speed_ms": metadata.get("inference_speed_ms"),
                "real_time_factor": metadata.get("real_time_factor"),
                "latency_ms": metadata.get("latency_ms"),
                "throughput_samples_per_second": metadata.get("throughput_samples_per_second")
            },
            "resource_usage": {
                "memory_usage_mb": metadata.get("memory_usage_mb"),
                "peak_memory_mb": metadata.get("peak_memory_mb"),
                "cpu_usage_percent": metadata.get("cpu_usage_percent"),
                "gpu_usage_percent": metadata.get("gpu_usage_percent", 0)
            },
            "benchmark_results": {
                "cpu_baseline_ms": metadata.get("cpu_baseline_ms"),
                "npu_speed_ms": metadata.get("npu_speed_ms"),
                "speedup_factor": metadata.get("speedup_factor"),
                "accuracy_retention": metadata.get("accuracy_retention")
            }
        }

    def _generate_language_support_summary(
        self,
        conversion_result: ResultModel
    ) -> Dict[str, Any]:
        """Generate language support summary."""
        languages = conversion_result.metadata.get("supported_languages", [])

        language_info = {
            "zh": {"name": "Chinese (Mandarin)", "native_name": "中文（普通话）", "supported": True},
            "en": {"name": "English", "native_name": "English", "supported": True},
            "ja": {"name": "Japanese", "native_name": "日本語", "supported": True},
            "ko": {"name": "Korean", "native_name": "한국어", "supported": False},
            "es": {"name": "Spanish", "native_name": "Español", "supported": False},
            "fr": {"name": "French", "native_name": "Français", "supported": False},
            "de": {"name": "German", "native_name": "Deutsch", "supported": False},
            "it": {"name": "Italian", "native_name": "Italiano", "supported": False},
            "pt": {"name": "Portuguese", "native_name": "Português", "supported": False},
            "ru": {"name": "Russian", "native_name": "Русский", "supported": False}
        }

        supported_languages = [
            lang for lang in languages if language_info.get(lang, {}).get("supported", False)
        ]

        return {
            "total_languages": len(languages),
            "supported_languages": supported_languages,
            "language_matrix": {lang: language_info.get(lang, {"supported": False}) for lang in languages},
            "multi_language_capability": len(supported_languages) > 1,
            "primary_language": supported_languages[0] if supported_languages else None
        }

    def _generate_audio_formats_summary(
        self,
        conversion_result: ResultModel
    ) -> Dict[str, Any]:
        """Generate audio formats summary."""
        formats = conversion_result.metadata.get("supported_audio_formats", [])

        format_info = {
            "wav": {"name": "WAV", "type": "lossless", "compression": "none", "quality": "excellent"},
            "mp3": {"name": "MP3", "type": "lossy", "compression": "high", "quality": "good"},
            "flac": {"name": "FLAC", "type": "lossless", "compression": "medium", "quality": "excellent"},
            "m4a": {"name": "M4A", "type": "lossy", "compression": "high", "quality": "good"},
            "aac": {"name": "AAC", "type": "lossy", "compression": "high", "quality": "good"},
            "ogg": {"name": "OGG", "type": "lossy", "compression": "high", "quality": "good"},
            "wma": {"name": "WMA", "type": "lossy", "compression": "medium", "quality": "fair"},
            "aiff": {"name": "AIFF", "type": "lossless", "compression": "none", "quality": "excellent"}
        }

        supported_formats = [fmt for fmt in formats if fmt in format_info]

        return {
            "total_formats": len(formats),
            "supported_formats": supported_formats,
            "format_matrix": {fmt: format_info.get(fmt, {"supported": False}) for fmt in formats},
            "lossless_support": any(format_info.get(fmt, {}).get("type") == "lossless" for fmt in supported_formats),
            "preferred_format": "wav" if "wav" in supported_formats else supported_formats[0] if supported_formats else None
        }

    def _generate_recommendations(
        self,
        validation_result: Optional[ValidationResult],
        optimization_result: Optional[Dict[str, Any]],
        mode: SenseVoiceProcessingMode,
        level: SenseVoiceConversionLevel
    ) -> List[Dict[str, Any]]:
        """Generate recommendations based on validation and optimization results."""
        recommendations = []

        # Performance recommendations
        if validation_result and validation_result.overall_score < 80:
            recommendations.append({
                "category": "Performance",
                "priority": "High",
                "title": "Low Performance Score",
                "description": f"Validation score is {validation_result.overall_score:.1f}. Consider optimizing model parameters.",
                "action": "Adjust conversion parameters and re-convert"
            })

        # Mode-specific recommendations
        if mode == SenseVoiceProcessingMode.STREAMING:
            recommendations.append({
                "category": "Streaming",
                "priority": "Medium",
                "title": "Streaming Mode Optimization",
                "description": "Ensure streaming optimizations are applied for real-time performance.",
                "action": "Enable streaming-specific optimizations in configuration"
            })

        # Language recommendations
        if optimization_result and optimization_result.get("language_specific_optimizations", {}).get("language_support", {}).get("multi_language"):
            recommendations.append({
                "category": "Language",
                "priority": "Low",
                "title": "Multi-language Support",
                "description": "Model supports multiple languages. Consider language-specific optimization.",
                "action": "Test with different language inputs to verify performance"
            })

        # Quality recommendations
        if validation_result and validation_result.warnings:
            recommendations.append({
                "category": "Quality",
                "priority": "Medium",
                "title": "Validation Warnings",
                "description": f"Found {len(validation_result.warnings)} validation warnings.",
                "action": "Review warnings and address potential issues"
            })

        return recommendations

    def _generate_technical_details(
        self,
        conversion_result: ResultModel
    ) -> Dict[str, Any]:
        """Generate technical details section."""
        return {
            "conversion_metadata": conversion_result.metadata,
            "system_information": {
                "timestamp": datetime.now().isoformat(),
                "timezone": "UTC",
                "python_version": "3.10+",
                "framework_version": "XLeRobot 1.0.0"
            },
            "hardware_compatibility": {
                "npu_support": conversion_result.metadata.get("npu_compatible", False),
                "horizon_x5_compatible": conversion_result.metadata.get("horizon_x5_compatible", False),
                "recommended_memory_gb": 8,
                "minimum_memory_gb": 4
            },
            "integration_details": {
                "epic_1_integrated": True,
                "story_2_2_reference": True,
                "configuration_manager": "Story 1.4",
                "error_handling": "Story 1.7",
                "logging_system": "Story 1.7"
            }
        }

    def _generate_report_summary(
        self,
        report_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate executive summary for the report."""
        summary = {
            "title": "SenseVoice ASR Conversion Report",
            "status": report_data["conversion_summary"]["status"],
            "overall_score": 0
        }

        # Calculate overall score
        validation_score = report_data["validation_results"].get("overall_score", 0)
        optimization_score = report_data["optimization_details"].get("optimization_score", 0)
        performance_score = self._calculate_performance_score(report_data["performance_analysis"])

        summary["overall_score"] = (validation_score * 0.4 + optimization_score * 0.3 + performance_score * 0.3)

        # Key metrics
        summary["key_metrics"] = {
            "conversion_time": f"{report_data['conversion_summary']['conversion_time_seconds']:.2f}s",
            "languages_supported": report_data["language_support"]["total_languages"],
            "audio_formats_supported": report_data["audio_formats"]["total_formats"],
            "validation_passed": report_data["validation_results"]["is_valid"],
            "optimizations_applied": len(report_data["optimization_details"]["optimizations_applied"])
        }

        # Status indicators
        summary["status_indicators"] = {
            "conversion": "✓" if summary["status"] == "success" else "✗",
            "validation": "✓" if report_data["validation_results"]["is_valid"] else "✗",
            "optimization": "✓" if report_data["optimization_details"]["optimization_performed"] else "✗",
            "multi_language": "✓" if report_data["language_support"]["multi_language_capability"] else "✗",
            "lossless_support": "✓" if report_data["audio_formats"]["lossless_support"] else "✗"
        }

        return summary

    async def _generate_json_report(
        self,
        report_data: Dict[str, Any],
        output_path: Path,
        conversion_id: str
    ) -> Path:
        """Generate JSON format report."""
        file_path = output_path / f"{conversion_id}_sensevoice_report.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        logger.debug(f"JSON report generated: {file_path}")
        return file_path

    async def _generate_html_report(
        self,
        report_data: Dict[str, Any],
        output_path: Path,
        conversion_id: str
    ) -> Path:
        """Generate HTML format report."""
        file_path = output_path / f"{conversion_id}_sensevoice_report.html"

        html_content = self._generate_html_content(report_data)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.debug(f"HTML report generated: {file_path}")
        return file_path

    async def _generate_pdf_report(
        self,
        report_data: Dict[str, Any],
        output_path: Path,
        conversion_id: str
    ) -> Path:
        """Generate PDF format report."""
        file_path = output_path / f"{conversion_id}_sensevoice_report.pdf"

        # For PDF generation, we would typically use libraries like reportlab or weasyprint
        # For now, we'll generate a placeholder or use HTML-to-PDF conversion
        try:
            # This is a placeholder - in production, implement actual PDF generation
            # Example: using weasyprint or reportlab

            # For now, create a simple text-based PDF or skip
            logger.warning("PDF generation not fully implemented, creating placeholder")

            # Create a simple text version as PDF placeholder
            with open(file_path.with_suffix('.txt'), 'w', encoding='utf-8') as f:
                f.write(f"SenseVoice ASR Conversion Report\n")
                f.write(f"Conversion ID: {conversion_id}\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n\n")
                f.write(json.dumps(report_data, indent=2, ensure_ascii=False))

            # Rename to PDF (this is a workaround - in production, generate proper PDF)
            file_path.with_suffix('.txt').rename(file_path)

        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise

        logger.debug(f"PDF report generated: {file_path}")
        return file_path

    def _generate_html_content(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML content for the report."""
        summary = report_data["summary"]

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SenseVoice ASR Conversion Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
            padding-left: 10px;
        }}
        .summary-box {{
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .status-ok {{ color: #27ae60; font-weight: bold; }}
        .status-error {{ color: #e74c3c; font-weight: bold; }}
        .metric {{
            display: inline-block;
            margin: 10px;
            padding: 10px 20px;
            background-color: #3498db;
            color: white;
            border-radius: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        .recommendation {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 10px 0;
        }}
        .footer {{
            margin-top: 50px;
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>SenseVoice ASR Conversion Report</h1>

        <div class="summary-box">
            <h2>Executive Summary</h2>
            <p><strong>Status:</strong> <span class="{'status-ok' if summary['status'] == 'success' else 'status-error'}">{summary['status'].upper()}</span></p>
            <p><strong>Overall Score:</strong> {summary['overall_score']:.1f}/100</p>
            <p><strong>Conversion Time:</strong> {summary['key_metrics']['conversion_time']}</p>
        </div>

        <h2>Status Indicators</h2>
        <table>
            <tr>
                <th>Category</th>
                <th>Status</th>
            </tr>
            <tr>
                <td>Conversion</td>
                <td>{summary['status_indicators']['conversion']}</td>
            </tr>
            <tr>
                <td>Validation</td>
                <td>{summary['status_indicators']['validation']}</td>
            </tr>
            <tr>
                <td>Optimization</td>
                <td>{summary['status_indicators']['optimization']}</td>
            </tr>
            <tr>
                <td>Multi-language Support</td>
                <td>{summary['status_indicators']['multi_language']}</td>
            </tr>
            <tr>
                <td>Lossless Audio Support</td>
                <td>{summary['status_indicators']['lossless_support']}</td>
            </tr>
        </table>

        <h2>Key Metrics</h2>
        <div class="metric">Languages: {summary['key_metrics']['languages_supported']}</div>
        <div class="metric">Audio Formats: {summary['key_metrics']['audio_formats_supported']}</div>
        <div class="metric">Optimizations: {summary['key_metrics']['optimizations_applied']}</div>

        <h2>Recommendations</h2>
        {self._generate_recommendations_html(report_data.get('recommendations', []))}

        <div class="footer">
            <p>Generated by XLeRobot SenseVoice Report Generator v1.0.0</p>
            <p>Timestamp: {datetime.now().isoformat()}</p>
        </div>
    </div>
</body>
</html>
        """

        return html

    def _generate_recommendations_html(self, recommendations: List[Dict[str, Any]]) -> str:
        """Generate HTML for recommendations section."""
        if not recommendations:
            return "<p>No recommendations at this time.</p>"

        html = ""
        for rec in recommendations:
            html += f"""
            <div class="recommendation">
                <strong>{rec.get('category', 'General')} [{rec.get('priority', 'Medium')} Priority]</strong>
                <h3>{rec.get('title', 'Recommendation')}</h3>
                <p>{rec.get('description', '')}</p>
                <p><em>Action:</em> {rec.get('action', '')}</p>
            </div>
            """

        return html

    def _get_file_size_mb(self, file_path: Optional[str]) -> float:
        """Get file size in MB."""
        if not file_path:
            return 0.0
        try:
            return Path(file_path).stat().st_size / (1024 * 1024)
        except Exception:
            return 0.0

    def _calculate_throughput(self, conversion_result: ResultModel) -> float:
        """Calculate conversion throughput."""
        time_seconds = getattr(conversion_result, "conversion_time", 0)
        if time_seconds > 0:
            return 3600 / time_seconds  # models per hour
        return 0.0

    def _analyze_bottlenecks(self, conversion_result: ResultModel) -> List[str]:
        """Analyze conversion bottlenecks."""
        bottlenecks = []

        time_seconds = getattr(conversion_result, "conversion_time", 0)
        if time_seconds > 300:
            bottlenecks.append("Long conversion time")

        memory_usage = conversion_result.metadata.get("memory_usage_mb", 0)
        if memory_usage > 2048:
            bottlenecks.append("High memory usage")

        return bottlenecks

    def _check_quality_gates(self, validation_result: ValidationResult) -> Dict[str, bool]:
        """Check quality gates."""
        gates = {
            "overall_score_gt_75": validation_result.overall_score > 75,
            "no_critical_errors": validation_result.error_message is None,
            "validation_passed": validation_result.is_valid
        }
        return gates

    def _generate_validation_recommendations(
        self,
        validation_result: ValidationResult
    ) -> List[str]:
        """Generate validation-specific recommendations."""
        recommendations = []

        if validation_result.overall_score < 75:
            recommendations.append("Consider re-running conversion with different parameters")

        if validation_result.warnings:
            recommendations.append(f"Address {len(validation_result.warnings)} validation warnings")

        return recommendations

    def _calculate_performance_score(
        self,
        performance_analysis: Dict[str, Any]
    ) -> float:
        """Calculate performance score (0-100)."""
        score = 100

        # Penalize for long conversion time
        conv_time = performance_analysis.get("conversion_performance", {}).get("total_time_seconds", 0)
        if conv_time > 300:
            score -= 20
        elif conv_time > 120:
            score -= 10

        # Penalize for high memory usage
        memory = performance_analysis.get("resource_usage", {}).get("memory_usage_mb", 0)
        if memory > 4096:
            score -= 20
        elif memory > 2048:
            score -= 10

        return max(0, score)
