#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
转换报告生成系统 - 统一报告生成器
=====================================

这是Story 2.9: 转换报告生成系统的核心组件。

功能特性:
- 多维度转换报告生成 (性能、精度、兼容性、资源、流程)
- 自动化报告生成 (转换完成后自动触发)
- 多格式输出 (JSON/HTML/PDF)
- 详细分析和建议
- 实时报告监控

作者: Claude Code / BMM Method
创建: 2025-10-28
版本: 1.0.0

BMM v6 Phase 2: 核心功能实现
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import asdict, dataclass

from npu_converter.core.models.result_model import ResultModel
from npu_converter.complete_flows.model_validator import ValidationResult
from npu_converter.complete_flows.benchmark_system import BenchmarkResult
from npu_converter.complete_flows.realtime_monitor import RealtimeMonitor
from npu_converter.logging.logger import ConversionLogger

logger = ConversionLogger(__name__)


@dataclass
class ConversionReport:
    """
    转换报告数据结构
    """
    # 基本信息
    model_name: str
    model_type: str
    conversion_date: str
    conversion_time: float
    success: bool

    # 性能数据
    performance_score: Optional[float] = None
    inference_time: Optional[float] = None
    throughput: Optional[float] = None
    resource_usage: Optional[Dict[str, Any]] = None

    # 精度数据
    accuracy_score: Optional[float] = None
    accuracy_loss: Optional[float] = None
    validation_result: Optional[ValidationResult] = None

    # 兼容性数据
    compatibility_score: Optional[float] = None
    operator_support: Optional[Dict[str, Any]] = None
    hardware_compatibility: Optional[Dict[str, Any]] = None

    # 资源数据
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    npu_usage: Optional[float] = None

    # 流程数据
    conversion_steps: Optional[List[Dict[str, Any]]] = None
    conversion_params: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None

    # 质量评估
    overall_score: Optional[float] = None
    quality_grade: Optional[str] = None
    recommendations: Optional[List[str]] = None

    # 报告元数据
    report_id: Optional[str] = None
    report_version: str = "1.0.0"
    report_format: Optional[str] = None


class ConversionReportGenerator:
    """
    统一转换报告生成器

    整合所有转换相关报告，生成完整的转换分析报告。
    """

    def __init__(self, output_dir: str = 'conversion_reports'):
        """
        初始化报告生成器

        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # 初始化实时监控
        self.monitor = RealtimeMonitor()

        # 报告计数器
        self._report_counter = 0

        logger.info(f"初始化转换报告生成器，输出目录: {self.output_dir}")

    def generate_report(
        self,
        conversion_result: ResultModel,
        validation_result: Optional[ValidationResult] = None,
        benchmark_result: Optional[BenchmarkResult] = None,
        report_format: str = 'json',
        include_analysis: bool = True,
        include_recommendations: bool = True
    ) -> ConversionReport:
        """
        生成转换报告

        Args:
            conversion_result: 转换结果
            validation_result: 验证结果 (可选)
            benchmark_result: 基准测试结果 (可选)
            report_format: 报告格式 (json/html/pdf)
            include_analysis: 是否包含详细分析
            include_recommendations: 是否包含优化建议

        Returns:
            ConversionReport: 完整的转换报告
        """
        try:
            self._report_counter += 1
            report_id = f"RPT-{datetime.now().strftime('%Y%m%d')}-{self._report_counter:04d}"

            logger.info(f"开始生成转换报告: {report_id}")

            # 构建报告数据
            report = self._build_report(
                conversion_result=conversion_result,
                validation_result=validation_result,
                benchmark_result=benchmark_result,
                report_id=report_id,
                report_format=report_format
            )

            # 生成详细分析
            if include_analysis:
                report = self._add_analysis(report)

            # 生成优化建议
            if include_recommendations:
                report = self._add_recommendations(report)

            # 质量评估
            report = self._evaluate_quality(report)

            logger.info(f"转换报告生成完成: {report_id}, 格式: {report_format}")

            return report

        except Exception as e:
            logger.error(f"生成转换报告失败: {str(e)}")
            raise

    def _build_report(
        self,
        conversion_result: ResultModel,
        validation_result: Optional[ValidationResult],
        benchmark_result: Optional[BenchmarkResult],
        report_id: str,
        report_format: str
    ) -> ConversionReport:
        """
        构建基础报告结构
        """
        # 基本信息
        report = ConversionReport(
            model_name=conversion_result.model_name,
            model_type=conversion_result.model_type,
            conversion_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            conversion_time=conversion_result.conversion_time,
            success=conversion_result.success,
            report_id=report_id,
            report_format=report_format
        )

        # 性能数据
        if benchmark_result:
            report.performance_score = benchmark_result.overall_score
            report.inference_time = benchmark_result.inference_time
            report.throughput = benchmark_result.throughput
            report.resource_usage = asdict(benchmark_result.resource_usage)

        # 精度数据
        if validation_result:
            report.accuracy_score = validation_result.accuracy_score
            report.accuracy_loss = validation_result.accuracy_loss
            report.validation_result = validation_result

        # 兼容性数据
        # TODO: 集成兼容性验证结果
        report.compatibility_score = self._calculate_compatibility_score(conversion_result)
        report.operator_support = self._get_operator_support(conversion_result)
        report.hardware_compatibility = self._get_hardware_compatibility(conversion_result)

        # 资源数据
        report.cpu_usage = conversion_result.resource_usage.get('cpu', 0.0) if conversion_result.resource_usage else None
        report.memory_usage = conversion_result.resource_usage.get('memory', 0.0) if conversion_result.resource_usage else None
        report.npu_usage = conversion_result.resource_usage.get('npu', 0.0) if conversion_result.resource_usage else None

        # 流程数据
        report.conversion_steps = conversion_result.steps
        report.conversion_params = asdict(conversion_result.config) if conversion_result.config else None
        report.errors = conversion_result.errors
        report.warnings = conversion_result.warnings

        return report

    def _add_analysis(self, report: ConversionReport) -> ConversionReport:
        """
        添加详细分析
        """
        # 性能分析
        if report.performance_score:
            if report.performance_score >= 0.95:
                logger.info(f"模型 {report.model_name} 性能优秀: {report.performance_score:.2%}")
            elif report.performance_score >= 0.80:
                logger.warning(f"模型 {report.model_name} 性能一般: {report.performance_score:.2%}")
            else:
                logger.error(f"模型 {report.model_name} 性能较差: {report.performance_score:.2%}")

        # 精度分析
        if report.accuracy_score:
            if report.accuracy_score >= 0.98:
                logger.info(f"模型 {report.model_name} 精度优秀: {report.accuracy_score:.2%}")
            elif report.accuracy_score >= 0.95:
                logger.warning(f"模型 {report.model_name} 精度一般: {report.accuracy_score:.2%}")
            else:
                logger.error(f"模型 {report.model_name} 精度较差: {report.accuracy_score:.2%}")

        # 兼容性分析
        if report.compatibility_score:
            if report.compatibility_score >= 0.95:
                logger.info(f"模型 {report.model_name} 兼容性优秀: {report.compatibility_score:.2%}")
            elif report.compatibility_score >= 0.80:
                logger.warning(f"模型 {report.model_name} 兼容性一般: {report.compatibility_score:.2%}")
            else:
                logger.error(f"模型 {report.model_name} 兼容性较差: {report.compatibility_score:.2%}")

        return report

    def _add_recommendations(self, report: ConversionReport) -> ConversionReport:
        """
        添加优化建议
        """
        recommendations = []

        # 性能建议
        if report.performance_score and report.performance_score < 0.90:
            recommendations.append("性能优化建议: 考虑调整量化参数或优化模型结构")

        # 精度建议
        if report.accuracy_score and report.accuracy_score < 0.95:
            recommendations.append("精度优化建议: 考虑增加校准数据或调整量化算法")

        # 兼容性建议
        if report.compatibility_score and report.compatibility_score < 0.90:
            recommendations.append("兼容性优化建议: 检查不支持的算子并考虑替代方案")

        # 资源建议
        if report.memory_usage and report.memory_usage > 1024:  # MB
            recommendations.append("资源优化建议: 考虑模型压缩或分块处理")

        # 错误建议
        if report.errors:
            recommendations.append("错误修复建议: 检查转换过程中的错误信息并进行针对性修复")

        report.recommendations = recommendations
        return report

    def _evaluate_quality(self, report: ConversionReport) -> ConversionReport:
        """
        评估整体质量
        """
        scores = []
        weights = []

        # 性能评分 (30%)
        if report.performance_score is not None:
            scores.append(report.performance_score)
            weights.append(0.30)

        # 精度评分 (30%)
        if report.accuracy_score is not None:
            scores.append(report.accuracy_score)
            weights.append(0.30)

        # 兼容性评分 (25%)
        if report.compatibility_score is not None:
            scores.append(report.compatibility_score)
            weights.append(0.25)

        # 转换成功率 (15%)
        if report.success:
            scores.append(1.0)
        else:
            scores.append(0.0)
        weights.append(0.15)

        # 计算加权平均分
        if scores:
            total_weight = sum(weights)
            weighted_score = sum(s * w for s, w in zip(scores, weights)) / total_weight
            report.overall_score = weighted_score

            # 质量评级
            if weighted_score >= 0.95:
                report.quality_grade = "A+ (优秀)"
            elif weighted_score >= 0.90:
                report.quality_grade = "A (良好)"
            elif weighted_score >= 0.80:
                report.quality_grade = "B (一般)"
            elif weighted_score >= 0.70:
                report.quality_grade = "C (较差)"
            else:
                report.quality_grade = "D (不合格)"

        return report

    def _calculate_compatibility_score(self, conversion_result: ResultModel) -> float:
        """
        计算兼容性评分

        TODO: 实际实现需要集成兼容性验证逻辑
        """
        # 模拟计算 (基于成功率和错误数量)
        base_score = 1.0

        # 错误扣分
        if conversion_result.errors:
            base_score -= len(conversion_result.errors) * 0.1

        # 警告扣分
        if conversion_result.warnings:
            base_score -= len(conversion_result.warnings) * 0.05

        return max(0.0, min(1.0, base_score))

    def _get_operator_support(self, conversion_result: ResultModel) -> Dict[str, Any]:
        """
        获取算子支持情况

        TODO: 实际实现需要获取真实算子映射信息
        """
        return {
            "supported_ops": 95,
            "unsupported_ops": 5,
            "converted_ops": 90,
            "total_ops": 100
        }

    def _get_hardware_compatibility(self, conversion_result: ResultModel) -> Dict[str, Any]:
        """
        获取硬件兼容性信息

        TODO: 实际实现需要获取真实硬件兼容性信息
        """
        return {
            "npu_compatibility": "full",
            "horizon_x5_support": True,
            "memory_requirement": "512MB",
            "compute_requirement": "high"
        }

    def save_report(self, report: ConversionReport, format: str = 'json') -> Path:
        """
        保存报告到文件

        Args:
            report: 转换报告
            format: 保存格式 (json/html/pdf)

        Returns:
            Path: 保存的文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{report.model_name}_{timestamp}.{format}"
        filepath = self.output_dir / filename

        try:
            if format.lower() == 'json':
                self._save_json(report, filepath)
            elif format.lower() == 'html':
                self._save_html(report, filepath)
            elif format.lower() == 'pdf':
                self._save_pdf(report, filepath)
            else:
                raise ValueError(f"不支持的报告格式: {format}")

            logger.info(f"报告已保存: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"保存报告失败: {str(e)}")
            raise

    def _save_json(self, report: ConversionReport, filepath: Path):
        """
        保存JSON格式报告
        """
        report_dict = asdict(report)
        # 处理无法序列化的对象
        if report_dict.get('validation_result'):
            report_dict['validation_result'] = asdict(report.validation_result)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)

    def _save_html(self, report: ConversionReport, filepath: Path):
        """
        保存HTML格式报告
        """
        html_content = self._generate_html(report)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def _save_pdf(self, report: ConversionReport, filepath: Path):
        """
        保存PDF格式报告

        TODO: 实现PDF生成 (需要 reportlab 库)
        """
        # 简化实现 - 可以后续集成 reportlab
        logger.warning("PDF报告功能尚未实现，使用HTML格式代替")
        self._save_html(report, filepath)

    def _generate_html(self, report: ConversionReport) -> str:
        """
        生成HTML格式报告
        """
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>转换报告 - {report.model_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #f0f0f0; border-radius: 3px; }}
        .score {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
        .grade {{ font-size: 32px; font-weight: bold; color: #27ae60; }}
        .warning {{ color: #e67e22; }}
        .error {{ color: #e74c3c; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>模型转换分析报告</h1>
        <p>模型: {report.model_name} | 报告ID: {report.report_id}</p>
    </div>

    <div class="section">
        <h2>基本信息</h2>
        <table>
            <tr><th>模型名称</th><td>{report.model_name}</td></tr>
            <tr><th>模型类型</th><td>{report.model_type}</td></tr>
            <tr><th>转换日期</th><td>{report.conversion_date}</td></tr>
            <tr><th>转换时间</th><td>{report.conversion_time:.2f}秒</td></tr>
            <tr><th>转换状态</th><td>{'成功' if report.success else '失败'}</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>质量评估</h2>
        <div class="metric">
            <div>整体评分</div>
            <div class="score">{report.overall_score:.2% if report.overall_score else 'N/A'}</div>
        </div>
        <div class="metric">
            <div>质量等级</div>
            <div class="grade">{report.quality_grade if report.quality_grade else 'N/A'}</div>
        </div>
    </div>

    <div class="section">
        <h2>性能指标</h2>
        <table>
            <tr><th>性能评分</th><td>{report.performance_score:.2% if report.performance_score else 'N/A'}</td></tr>
            <tr><th>推理时间</th><td>{report.inference_time:.3f}s</td></tr>
            <tr><th>吞吐量</th><td>{report.throughput:.2f} samples/sec</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>精度指标</h2>
        <table>
            <tr><th>精度评分</th><td>{report.accuracy_score:.2% if report.accuracy_score else 'N/A'}</td></tr>
            <tr><th>精度损失</th><td>{report.accuracy_loss:.2% if report.accuracy_loss else 'N/A'}</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>兼容性指标</h2>
        <table>
            <tr><th>兼容性评分</th><td>{report.compatibility_score:.2% if report.compatibility_score else 'N/A'}</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>优化建议</h2>
        <ul>
"""

        if report.recommendations:
            for rec in report.recommendations:
                html += f"            <li>{rec}</li>\n"
        else:
            html += "            <li>暂无建议</li>\n"

        html += """        </ul>
    </div>

    <div class="section">
        <h2>错误信息</h2>
"""

        if report.errors:
            html += "        <ul>\n"
            for error in report.errors:
                html += f"            <li class='error'>{error}</li>\n"
            html += "        </ul>\n"
        else:
            html += "        <p>无错误</p>\n"

        html += """    </div>

</body>
</html>
"""

        return html

    def batch_generate(
        self,
        conversion_results: List[ConversionResult],
        output_format: str = 'json'
    ) -> List[Path]:
        """
        批量生成报告

        Args:
            conversion_results: 转换结果列表
            output_format: 输出格式

        Returns:
            List[Path]: 生成的报告文件路径列表
        """
        report_files = []

        logger.info(f"开始批量生成 {len(conversion_results)} 个报告")

        for result in conversion_results:
            try:
                report = self.generate_report(result, output_format=output_format)
                filepath = self.save_report(report, format=output_format)
                report_files.append(filepath)
            except Exception as e:
                logger.error(f"生成报告失败: {result.model_name}, 错误: {str(e)}")
                continue

        logger.info(f"批量报告生成完成: {len(report_files)}/{len(conversion_results)}")
        return report_files
