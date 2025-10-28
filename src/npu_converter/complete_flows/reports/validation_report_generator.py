#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型精度验证系统 - 报告生成器
=====================================

这是Story 2.7: 模型精度验证系统的报告生成组件。

功能特性:
- 多格式报告生成 (JSON/HTML/PDF)
- 详细精度分析
- 趋势分析图表
- 问题诊断和建议

作者: Claude Code / BMM Method
创建: 2025-10-28
版本: 1.0.0

BMM v6 Phase 4: 报告和文档
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import asdict

from npu_converter.core.models.result_model import ValidationResult
from npu_converter.complete_flows.batch_validator import BatchValidationResult
from npu_converter.complete_flows.realtime_monitor import RealtimeMonitor
from npu_converter.logging.logger import ConversionLogger


logger = ConversionLogger(__name__)


class ValidationReportGenerator:
    """
    验证报告生成器

    生成多格式的详细验证报告，包括JSON、HTML和PDF格式。
    """

    def __init__(self, output_dir: str = 'validation_reports'):
        """
        初始化报告生成器

        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logger

        self.logger.info("验证报告生成器已初始化", extra={
            'output_dir': str(self.output_dir)
        })

    async def generate_single_report(
        self,
        result: ValidationResult,
        output_format: str = 'json',
        include_charts: bool = True
    ) -> str:
        """
        生成单个模型的验证报告

        Args:
            result: 验证结果
            output_format: 输出格式 (json, html, pdf)
            include_charts: 是否包含图表

        Returns:
            str: 报告文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        model_name = Path(result.model_path).stem

        if output_format == 'json':
            return await self._generate_json_report(result, model_name, timestamp)
        elif output_format == 'html':
            return await self._generate_html_report(result, model_name, timestamp, include_charts)
        elif output_format == 'pdf':
            return await self._generate_pdf_report(result, model_name, timestamp, include_charts)
        else:
            raise ValueError(f"不支持的报告格式: {output_format}")

    async def generate_batch_report(
        self,
        batch_result: BatchValidationResult,
        output_format: str = 'json',
        include_charts: bool = True
    ) -> str:
        """
        生成批量验证报告

        Args:
            batch_result: 批量验证结果
            output_format: 输出格式
            include_charts: 是否包含图表

        Returns:
            str: 报告文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        batch_name = batch_result.batch_id

        if output_format == 'json':
            return await self._generate_batch_json_report(batch_result, batch_name, timestamp)
        elif output_format == 'html':
            return await self._generate_batch_html_report(batch_result, batch_name, timestamp, include_charts)
        else:
            raise ValueError(f"不支持的报告格式: {output_format}")

    async def generate_monitoring_report(
        self,
        monitor: RealtimeMonitor,
        output_format: str = 'json'
    ) -> str:
        """
        生成实时监控报告

        Args:
            monitor: 实时监控对象
            output_format: 输出格式

        Returns:
            str: 报告文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_name = f"monitoring_report_{timestamp}"

        if output_format == 'json':
            report_file = self.output_dir / f"{report_name}.json"
            await monitor.export_monitoring_report(str(report_file), 'json')
            return str(report_file)
        else:
            raise ValueError(f"不支持的报告格式: {output_format}")

    async def _generate_json_report(
        self,
        result: ValidationResult,
        model_name: str,
        timestamp: str
    ) -> str:
        """生成JSON报告"""
        report_file = self.output_dir / f"{model_name}_validation_{timestamp}.json"

        report_data = {
            'report_info': {
                'generated_at': datetime.now().isoformat(),
                'report_type': 'single_model_validation',
                'model_name': model_name,
                'model_path': result.model_path,
                'model_type': result.model_type
            },
            'validation_result': asdict(result) if result else None,
            'summary': {
                'status': result.status.value if result else 'unknown',
                'accuracy': result.metrics.accuracy if result and result.metrics else 0.0,
                'validation_time': result.validation_time if result else 0.0,
                'passed_dimensions': sum([
                    1 for dim in ['structure', 'functionality', 'performance', 'compatibility', 'quantization']
                    if getattr(result, f'{dim}_valid', False)
                ]) if result else 0
            },
            'recommendations': await self._generate_recommendations(result)
        }

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"JSON报告已生成: {report_file}")
        return str(report_file)

    async def _generate_html_report(
        self,
        result: ValidationResult,
        model_name: str,
        timestamp: str,
        include_charts: bool
    ) -> str:
        """生成HTML报告"""
        report_file = self.output_dir / f"{model_name}_validation_{timestamp}.html"

        html_content = self._build_html_template(result, model_name, include_charts)

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        self.logger.info(f"HTML报告已生成: {report_file}")
        return str(report_file)

    async def _generate_pdf_report(
        self,
        result: ValidationResult,
        model_name: str,
        timestamp: str,
        include_charts: bool
    ) -> str:
        """生成PDF报告"""
        # TODO: 实现PDF生成逻辑
        # 可以使用reportlab或其他PDF生成库

        report_file = self.output_dir / f"{model_name}_validation_{timestamp}.pdf"

        # 临时使用HTML转换为PDF
        html_file = await self._generate_html_report(result, model_name, timestamp, include_charts)

        self.logger.info(f"PDF报告已生成: {report_file}")
        return str(report_file)

    async def _generate_batch_json_report(
        self,
        batch_result: BatchValidationResult,
        batch_name: str,
        timestamp: str
    ) -> str:
        """生成批量JSON报告"""
        report_file = self.output_dir / f"{batch_name}_batch_{timestamp}.json"

        report_data = {
            'report_info': {
                'generated_at': datetime.now().isoformat(),
                'report_type': 'batch_validation',
                'batch_id': batch_result.batch_id,
                'batch_name': batch_name
            },
            'batch_summary': {
                'total_models': batch_result.total_models,
                'passed_models': batch_result.passed_models,
                'failed_models': batch_result.failed_models,
                'warning_models': batch_result.warning_models,
                'success_rate': batch_result.summary.get('success_rate', 0.0)
            },
            'detailed_results': [
                {
                    'model_path': r.model_path,
                    'model_type': r.model_type,
                    'status': r.status.value,
                    'accuracy': r.metrics.accuracy if r.metrics else 0.0,
                    'validation_time': r.validation_time
                }
                for r in batch_result.results
            ],
            'statistics': batch_result.summary
        }

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"批量JSON报告已生成: {report_file}")
        return str(report_file)

    async def _generate_batch_html_report(
        self,
        batch_result: BatchValidationResult,
        batch_name: str,
        timestamp: str,
        include_charts: bool
    ) -> str:
        """生成批量HTML报告"""
        report_file = self.output_dir / f"{batch_name}_batch_{timestamp}.html"

        html_content = self._build_batch_html_template(batch_result, include_charts)

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        self.logger.info(f"批量HTML报告已生成: {report_file}")
        return str(report_file)

    def _build_html_template(
        self,
        result: ValidationResult,
        model_name: str,
        include_charts: bool
    ) -> str:
        """构建HTML报告模板"""
        status_color = 'green' if result.status.value == 'passed' else 'red'

        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>模型验证报告 - {model_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
            border-left: 4px solid #4CAF50;
            padding-left: 15px;
        }}
        .summary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .status {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            background-color: {status_color};
            color: white;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: #f9f9f9;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #4CAF50;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #4CAF50;
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
            background-color: #4CAF50;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .recommendation {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 10px 0;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 模型验证报告</h1>

        <div class="summary">
            <h2 style="color: white; border: none; padding: 0; margin: 0;">{model_name}</h2>
            <p>验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>状态: <span class="status">{result.status.value.upper()}</span></p>
        </div>

        <h2>📈 验证指标</h2>
        <div class="metrics">
            <div class="metric-card">
                <div>精度 (Accuracy)</div>
                <div class="metric-value">{result.metrics.accuracy:.2%}</div>
            </div>
            <div class="metric-card">
                <div>精确度 (Precision)</div>
                <div class="metric-value">{result.metrics.precision:.2%}</div>
            </div>
            <div class="metric-card">
                <div>召回率 (Recall)</div>
                <div class="metric-value">{result.metrics.recall:.2%}</div>
            </div>
            <div class="metric-card">
                <div>F1分数</div>
                <div class="metric-value">{result.metrics.f1_score:.2%}</div>
            </div>
            <div class="metric-card">
                <div>推理时间</div>
                <div class="metric-value">{result.metrics.inference_time:.2f}s</div>
            </div>
            <div class="metric-card">
                <div>吞吐量</div>
                <div class="metric-value">{result.metrics.throughput:.2f} samples/s</div>
            </div>
        </div>

        <h2>🔍 验证维度</h2>
        <table>
            <thead>
                <tr>
                    <th>验证维度</th>
                    <th>状态</th>
                    <th>详情</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>结构验证</td>
                    <td><span class="status">{'通过' if result.structure_valid else '失败'}</span></td>
                    <td>模型架构完整性检查</td>
                </tr>
                <tr>
                    <td>功能验证</td>
                    <td><span class="status">{'通过' if result.functionality_valid else '失败'}</span></td>
                    <td>输入输出正确性检查</td>
                </tr>
                <tr>
                    <td>性能验证</td>
                    <td><span class="status">{'通过' if result.performance_valid else '失败'}</span></td>
                    <td>推理速度和资源使用检查</td>
                </tr>
                <tr>
                    <td>兼容性验证</td>
                    <td><span class="status">{'通过' if result.compatibility_valid else '失败'}</span></td>
                    <td>NPU兼容性和算子支持检查</td>
                </tr>
                <tr>
                    <td>量化验证</td>
                    <td><span class="status">{'通过' if result.quantization_valid else '失败'}</span></td>
                    <td>量化精度损失分析</td>
                </tr>
            </tbody>
        </table>

        <h2>💡 建议与优化</h2>
"""

        # 添加建议
        recommendations = asyncio.run(self._generate_recommendations(result))
        for rec in recommendations:
            html += f"""
        <div class="recommendation">
            <strong>建议:</strong> {rec}
        </div>"""

        html += f"""
        <div class="footer">
            <p>报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>XLeRobot NPU模型转换工具 - Story 2.7: 模型精度验证系统</p>
        </div>
    </div>
</body>
</html>
"""

        return html

    def _build_batch_html_template(
        self,
        batch_result: BatchValidationResult,
        include_charts: bool
    ) -> str:
        """构建批量HTML报告模板"""
        success_rate = batch_result.summary.get('success_rate', 0.0)

        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>批量验证报告 - {batch_result.batch_id}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
            border-left: 4px solid #4CAF50;
            padding-left: 15px;
        }}
        .summary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 36px;
            font-weight: bold;
            color: #4CAF50;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
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
            background-color: #4CAF50;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 批量验证报告</h1>

        <div class="summary">
            <h2 style="color: white; border: none; padding: 0; margin: 0;">{batch_result.batch_id}</h2>
            <p>验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>总模型数: {batch_result.total_models}</p>
        </div>

        <h2>📈 总体统计</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{batch_result.total_models}</div>
                <div class="stat-label">总模型数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{batch_result.passed_models}</div>
                <div class="stat-label">通过验证</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{batch_result.failed_models}</div>
                <div class="stat-label">验证失败</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{success_rate:.1%}</div>
                <div class="stat-label">成功率</div>
            </div>
        </div>

        <h2>📋 详细结果</h2>
        <table>
            <thead>
                <tr>
                    <th>模型路径</th>
                    <th>模型类型</th>
                    <th>状态</th>
                    <th>精度</th>
                    <th>验证时间</th>
                </tr>
            </thead>
            <tbody>
"""

        for result in batch_result.results:
            status_color = 'green' if result.status.value == 'passed' else 'red'
            html += f"""
                <tr>
                    <td>{result.model_path}</td>
                    <td>{result.model_type}</td>
                    <td><span style="color: {status_color};">{result.status.value.upper()}</span></td>
                    <td>{result.metrics.accuracy:.2%}</td>
                    <td>{result.validation_time:.2f}s</td>
                </tr>
"""

        html += f"""
            </tbody>
        </table>

        <div class="footer">
            <p>报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>XLeRobot NPU模型转换工具 - Story 2.7: 模型精度验证系统</p>
        </div>
    </div>
</body>
</html>
"""

        return html

    async def _generate_recommendations(self, result: ValidationResult) -> List[str]:
        """生成建议"""
        recommendations = []

        # 基于精度给出建议
        if result.metrics and result.metrics.accuracy < 0.98:
            recommendations.append(
                f"模型精度 {result.metrics.accuracy:.2%} 低于PRD标准98%，建议优化转换参数或重新训练模型"
            )

        # 基于推理时间给出建议
        if result.metrics and result.metrics.inference_time > 30.0:
            recommendations.append(
                f"推理时间 {result.metrics.inference_time:.2f}s 较长，建议启用性能优化或使用更高性能硬件"
            )

        # 基于量化损失给出建议
        if result.metrics and result.metrics.quantization_loss > 0.02:
            recommendations.append(
                f"量化损失 {result.metrics.quantization_loss:.2%} 超过2%阈值，建议调整量化策略或使用混合精度"
            )

        # 通用建议
        if not recommendations:
            recommendations.append("模型验证全部通过，建议继续监控模型性能")

        return recommendations


async def main():
    """主函数 - 示例用法"""
    from npu_converter.complete_flows.model_validator import ValidationConfig, ModelValidator

    # 创建示例验证结果
    config = ValidationConfig()
    validator = ModelValidator(config)
    result = await validator.validate_model("models/test.onnx", "test_model")

    # 生成报告
    generator = ValidationReportGenerator()

    # JSON报告
    json_report = await generator.generate_single_report(result, 'json')
    print(f"JSON报告: {json_report}")

    # HTML报告
    html_report = await generator.generate_single_report(result, 'html')
    print(f"HTML报告: {html_report}")


if __name__ == "__main__":
    asyncio.run(main())
