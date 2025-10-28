"""
XLeRobot NPU模型转换工具 - 转换失败诊断系统测试
================================================

该模块提供转换失败诊断系统的单元测试和集成测试。

作者: XLeRobot 开发团队
日期: 2025-10-28
版本: 1.0.0
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from src.npu_converter.complete_flows.failure_diagnostic_system import (
    FailureDiagnosticSystem,
    FailureDiagnostic,
    DiagnosticSummary
)
from src.npu_converter.core.models.result_model import ResultStatus
from src.npu_converter.config.failure_diagnostic_config import (
    FailureDiagnosticConfig,
    FailureDiagnosticConfigStrategy
)
from src.npu_converter.core.exceptions.conversion_errors import (
    ModelLoadError,
    QuantizationError,
    OptimizationError,
    ExportError
)


class TestFailureDiagnosticSystem:
    """转换失败诊断系统测试类"""

    @pytest.fixture
    def diagnostic_system(self):
        """创建测试用的诊断系统实例"""
        # 模拟配置管理器
        config_manager = Mock()
        config_manager.get_config.return_value = {
            'include_stack_trace': True,
            'max_suggestions': 5,
            'max_fix_steps': 10,
            'severity_thresholds': {
                'critical': 0.8,
                'high': 0.6,
                'medium': 0.4,
                'low': 0.2
            }
        }

        # 模拟报告生成器
        report_generator = Mock()

        # 创建诊断系统实例
        return FailureDiagnosticSystem(
            config_manager=config_manager,
            report_generator=report_generator
        )

    @pytest.fixture
    def sample_model_load_error(self):
        """创建示例模型加载错误"""
        return ModelLoadError("模型文件不存在")

    @pytest.fixture
    def sample_quantization_error(self):
        """创建示例量化错误"""
        return QuantizationError("校准数据不足")

    @pytest.fixture
    def sample_optimization_error(self):
        """创建示例优化错误"""
        return OptimizationError("优化策略不匹配")

    @pytest.fixture
    def sample_export_error(self):
        """创建示例导出错误"""
        return ExportError("导出路径不存在")

    def test_diagnose_model_load_error(self, diagnostic_system, sample_model_load_error):
        """测试模型加载错误诊断"""
        result = diagnostic_system.diagnose_failure(
            error=sample_model_load_error,
            model_name="test_model"
        )

        assert isinstance(result, FailureDiagnostic)
        assert result.model_name == "test_model"
        assert result.failure_type == "model_load_error"
        assert result.failure_stage == "model_loading"
        assert result.severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        assert len(result.suggestions) > 0
        assert len(result.fix_steps) > 0
        assert len(result.prevention_measures) > 0
        assert result.error_code is not None

    def test_diagnose_quantization_error(self, diagnostic_system, sample_quantization_error):
        """测试量化错误诊断"""
        result = diagnostic_system.diagnose_failure(
            error=sample_quantization_error,
            model_name="test_model"
        )

        assert isinstance(result, FailureDiagnostic)
        assert result.failure_type == "quantization_error"
        assert result.failure_stage == "quantization"
        assert len(result.suggestions) > 0

    def test_diagnose_optimization_error(self, diagnostic_system, sample_optimization_error):
        """测试优化错误诊断"""
        result = diagnostic_system.diagnose_failure(
            error=sample_optimization_error,
            model_name="test_model"
        )

        assert isinstance(result, FailureDiagnostic)
        assert result.failure_type == "optimization_error"
        assert result.failure_stage == "optimization"
        assert len(result.fix_steps) > 0

    def test_diagnose_export_error(self, diagnostic_system, sample_export_error):
        """测试导出错误诊断"""
        result = diagnostic_system.diagnose_failure(
            error=sample_export_error,
            model_name="test_model"
        )

        assert isinstance(result, FailureDiagnostic)
        assert result.failure_type == "export_error"
        assert result.failure_stage == "model_export"
        assert len(result.prevention_measures) > 0

    def test_diagnose_generic_error(self, diagnostic_system):
        """测试通用错误诊断"""
        generic_error = ValueError("配置参数无效")
        result = diagnostic_system.diagnose_failure(
            error=generic_error,
            model_name="test_model"
        )

        assert isinstance(result, FailureDiagnostic)
        assert result.failure_type == "configuration_error"
        assert result.failure_stage == "unknown_stage"

    def test_generate_diagnostic_report_json(self, diagnostic_system, sample_model_load_error):
        """测试生成JSON格式诊断报告"""
        diagnostic = diagnostic_system.diagnose_failure(
            error=sample_model_load_error,
            model_name="test_model"
        )

        report = diagnostic_system.generate_diagnostic_report(
            diagnostic=diagnostic,
            output_format='json'
        )

        # 验证报告是有效的JSON
        report_data = json.loads(report)
        assert report_data['model_name'] == "test_model"
        assert report_data['failure_type'] == "model_load_error"
        assert 'suggestions' in report_data
        assert 'fix_steps' in report_data
        assert 'prevention_measures' in report_data

    def test_generate_diagnostic_report_html(self, diagnostic_system, sample_model_load_error):
        """测试生成HTML格式诊断报告"""
        diagnostic = diagnostic_system.diagnose_failure(
            error=sample_model_load_error,
            model_name="test_model"
        )

        report = diagnostic_system.generate_diagnostic_report(
            diagnostic=diagnostic,
            output_format='html'
        )

        # 验证HTML报告格式
        assert '<!DOCTYPE html>' in report
        assert '<title>转换失败诊断报告</title>' in report
        assert diagnostic.model_name in report
        assert diagnostic.failure_type in report

    def test_analyze_diagnostic_history_empty(self, diagnostic_system):
        """测试空诊断历史的分析"""
        summary = diagnostic_system.analyze_diagnostic_history()

        assert isinstance(summary, DiagnosticSummary)
        assert summary.total_failures == 0
        assert summary.critical_failures == 0
        assert summary.high_failures == 0
        assert summary.medium_failures == 0
        assert summary.low_failures == 0

    def test_analyze_diagnostic_history_with_data(self, diagnostic_system):
        """测试有数据诊断历史的分析"""
        # 模拟多个诊断结果
        errors = [
            (ModelLoadError("模型文件不存在"), "model1"),
            (QuantizationError("校准数据不足"), "model2"),
            (ModelLoadError("ONNX格式不支持"), "model3"),
            (OptimizationError("优化策略不匹配"), "model4"),
            (ExportError("导出路径不存在"), "model5")
        ]

        for error, model_name in errors:
            diagnostic_system.diagnose_failure(error, model_name)

        summary = diagnostic_system.analyze_diagnostic_history()

        assert isinstance(summary, DiagnosticSummary)
        assert summary.total_failures == 5
        assert summary.critical_failures >= 0
        assert summary.high_failures >= 0
        assert summary.medium_failures >= 0
        assert summary.low_failures >= 0
        assert summary.most_common_failure_type != ""

    def test_batch_diagnose(self, diagnostic_system):
        """测试批量诊断"""
        errors = [
            (ModelLoadError("模型文件不存在"), "model1"),
            (QuantizationError("校准数据不足"), "model2"),
            (ExportError("导出路径不存在"), "model3")
        ]

        diagnostics = diagnostic_system.batch_diagnose(errors)

        assert len(diagnostics) == 3
        for diagnostic in diagnostics:
            assert isinstance(diagnostic, FailureDiagnostic)
            assert diagnostic.error_code is not None

    def test_save_diagnostic_report(self, diagnostic_system, sample_model_load_error, tmp_path):
        """测试保存诊断报告"""
        diagnostic = diagnostic_system.diagnose_failure(
            error=sample_model_load_error,
            model_name="test_model"
        )

        output_path = tmp_path / "diagnostic_report.json"
        diagnostic_system.save_diagnostic_report(diagnostic, output_path, 'json')

        assert output_path.exists()

        # 验证报告内容
        with open(output_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
            assert report_data['model_name'] == "test_model"

    def test_export_diagnostic_history(self, diagnostic_system, tmp_path):
        """测试导出诊断历史"""
        # 添加一些诊断记录
        errors = [
            (ModelLoadError("模型文件不存在"), "model1"),
            (QuantizationError("校准数据不足"), "model2")
        ]

        for error, model_name in errors:
            diagnostic_system.diagnose_failure(error, model_name)

        output_path = tmp_path / "diagnostic_history.json"
        diagnostic_system.export_diagnostic_history(output_path)

        assert output_path.exists()

        # 验证历史记录
        with open(output_path, 'r', encoding='utf-8') as f:
            history_data = json.load(f)
            assert len(history_data) == 2

    def test_classify_error(self, diagnostic_system):
        """测试错误分类"""
        assert diagnostic_system._classify_error(ModelLoadError("错误")) == "model_load_error"
        assert diagnostic_system._classify_error(QuantizationError("错误")) == "quantization_error"
        assert diagnostic_system._classify_error(OptimizationError("错误")) == "optimization_error"
        assert diagnostic_system._classify_error(ExportError("错误")) == "export_error"

    def test_determine_failure_stage(self, diagnostic_system):
        """测试失败阶段确定"""
        # 使用模拟的转换结果
        mock_result = {'current_stage': 'quantization'}

        stage = diagnostic_system._determine_failure_stage(
            QuantizationError("错误"),
            mock_result
        )
        assert stage == "quantization"

    def test_generate_error_code(self, diagnostic_system):
        """测试错误代码生成"""
        code = diagnostic_system._generate_error_code("model_load_error", "model_loading")
        assert code.startswith("MOD-MOD-")
        assert len(code) > 10  # 包含时间戳

    def test_analyze_root_cause(self, diagnostic_system):
        """测试根因分析"""
        root_cause = diagnostic_system._analyze_root_cause(
            ModelLoadError("模型文件不存在"),
            "model_load_error"
        )
        assert "模型文件不存在" in root_cause or "文件" in root_cause

    def test_assess_severity(self, diagnostic_system):
        """测试严重程度评估"""
        severity1 = diagnostic_system._assess_severity(
            ModelLoadError("错误"),
            "model_load_error"
        )
        severity2 = diagnostic_system._assess_severity(
            ExportError("错误"),
            "export_error"
        )

        assert severity1 in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        assert severity2 in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

    def test_generate_suggestions(self, diagnostic_system):
        """测试修复建议生成"""
        suggestions = diagnostic_system._generate_suggestions(
            "model_load_error",
            ModelLoadError("模型文件不存在")
        )
        assert len(suggestions) > 0
        assert len(suggestions) <= 5  # 限制建议数量

    def test_generate_fix_steps(self, diagnostic_system):
        """测试修复步骤生成"""
        fix_steps = diagnostic_system._generate_fix_steps(
            "quantization_error",
            QuantizationError("校准数据不足")
        )
        assert len(fix_steps) > 0

    def test_generate_prevention_measures(self, diagnostic_system):
        """测试预防措施生成"""
        prevention_measures = diagnostic_system._generate_prevention_measures(
            "model_load_error"
        )
        assert len(prevention_measures) > 0

    def test_generate_recommended_actions(self, diagnostic_system):
        """测试推荐行动生成"""
        failure_type_counts = {
            "model_load_error": 5,
            "quantization_error": 3,
            "export_error": 2
        }

        actions = diagnostic_system._generate_recommended_actions(failure_type_counts)
        assert len(actions) > 0


class TestFailureDiagnosticConfig:
    """转换失败诊断配置测试类"""

    def test_default_config(self):
        """测试默认配置"""
        config = FailureDiagnosticConfig()
        assert config.include_stack_trace is True
        assert config.max_suggestions == 5
        assert config.report_format == 'json'
        assert config.enable_smart_suggestions is True

    def test_config_validation(self):
        """测试配置验证"""
        # 测试有效配置
        valid_config = FailureDiagnosticConfig(
            max_suggestions=10,
            suggestion_confidence_threshold=0.8
        )
        valid_config.validate()  # 不应抛出异常

        # 测试无效配置
        with pytest.raises(Exception):  # ConfigurationError
            invalid_config = FailureDiagnosticConfig(
                max_suggestions=-1  # 无效值
            )
            invalid_config.validate()

    def test_config_to_dict(self):
        """测试配置转换为字典"""
        config = FailureDiagnosticConfig(
            max_suggestions=10,
            report_format='html'
        )
        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert config_dict['max_suggestions'] == 10
        assert config_dict['report_format'] == 'html'

    def test_config_from_dict(self):
        """测试从字典创建配置"""
        config_dict = {
            'max_suggestions': 15,
            'report_format': 'pdf',
            'enable_smart_suggestions': False
        }

        config = FailureDiagnosticConfig.from_dict(config_dict)
        assert config.max_suggestions == 15
        assert config.report_format == 'pdf'
        assert config.enable_smart_suggestions is False


class TestFailureDiagnosticConfigStrategy:
    """转换失败诊断配置策略测试类"""

    @pytest.fixture
    def config_strategy(self):
        """创建测试用的配置策略实例"""
        config_manager = Mock()
        return FailureDiagnosticConfigStrategy(config_manager)

    def test_get_preset_config_names(self, config_strategy):
        """测试获取预设配置名称"""
        preset_names = config_strategy.get_preset_config_names()
        assert 'basic' in preset_names
        assert 'detailed' in preset_names
        assert 'production' in preset_names
        assert 'quick' in preset_names
        assert 'development' in preset_names

    def test_load_basic_preset(self, config_strategy):
        """测试加载基础预设配置"""
        config = config_strategy.load_config(preset_name='basic')
        assert config.include_stack_trace is False
        assert config.max_suggestions == 3
        assert config.enable_smart_suggestions is False

    def test_load_detailed_preset(self, config_strategy):
        """测试加载详细预设配置"""
        config = config_strategy.load_config(preset_name='detailed')
        assert config.include_stack_trace is True
        assert config.max_suggestions == 10
        assert config.enable_smart_suggestions is True

    def test_load_production_preset(self, config_strategy):
        """测试加载生产预设配置"""
        config = config_strategy.load_config(preset_name='production')
        assert config.report_format == 'pdf'
        assert config.auto_save_reports is True
        assert config.integrate_with_monitoring is True

    def test_load_quick_preset(self, config_strategy):
        """测试加载快速预设配置"""
        config = config_strategy.load_config(preset_name='quick')
        assert config.max_suggestions == 2
        assert config.auto_save_reports is False

    def test_load_development_preset(self, config_strategy):
        """测试加载开发预设配置"""
        config = config_strategy.load_config(preset_name='development')
        assert config.include_stack_trace is True
        assert config.debug_mode is True
        assert config.save_debug_info is True

    def test_update_config(self, config_strategy):
        """测试更新配置"""
        config_strategy.load_config(preset_name='basic')

        updates = {
            'max_suggestions': 20,
            'enable_smart_suggestions': True
        }

        updated_config = config_strategy.update_config(updates)
        assert updated_config.max_suggestions == 20
        assert updated_config.enable_smart_suggestions is True

    def test_merge_with_preset(self, config_strategy):
        """测试合并预设配置"""
        preset_name = 'basic'
        custom_updates = {
            'max_suggestions': 15,
            'report_format': 'html'
        }

        merged_config = config_strategy.merge_with_preset(preset_name, custom_updates)
        assert merged_config.max_suggestions == 15  # 自定义值
        assert merged_config.report_format == 'html'  # 自定义值
        assert merged_config.include_stack_trace is False  # 预设值

    def test_validate_config_file(self, config_strategy, tmp_path):
        """测试验证配置文件"""
        # 创建有效配置文件
        valid_config_path = tmp_path / "valid_config.yaml"
        with open(valid_config_path, 'w', encoding='utf-8') as f:
            yaml_content = """
            max_suggestions: 10
            report_format: json
            enable_smart_suggestions: true
            severity_thresholds:
              critical: 0.8
              high: 0.6
              medium: 0.4
              low: 0.2
            """
            f.write(yaml_content)

        assert config_strategy.validate_config_file(valid_config_path) is True

        # 创建无效配置文件
        invalid_config_path = tmp_path / "invalid_config.yaml"
        with open(invalid_config_path, 'w', encoding='utf-8') as f:
            f.write("invalid: yaml: content: [")

        assert config_strategy.validate_config_file(invalid_config_path) is False


if __name__ == '__main__':
    pytest.main([__file__])