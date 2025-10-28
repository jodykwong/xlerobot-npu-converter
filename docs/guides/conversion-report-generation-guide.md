# 转换报告生成指南

**项目**: XLeRobot NPU模型转换工具
**功能**: 转换报告生成系统
**版本**: 1.0.0
**更新日期**: 2025-10-28
**作者**: Claude Code / BMM Method

---

## 📖 概述

本指南详细介绍了如何使用 Story 2.9 的转换报告生成系统，为您的模型转换结果生成详细的分析报告。

### 什么是转换报告？

转换报告是模型转换完成后生成的分析文档，包含以下关键信息：

- **性能指标**: 推理时间、吞吐量、资源使用
- **精度评估**: 模型精度、精度损失分析
- **兼容性评估**: 硬件兼容性、算子支持情况
- **质量评级**: 综合质量评分和等级
- **优化建议**: 基于分析结果的改进建议

---

## 🚀 快速开始

### 基本使用

```python
from npu_converter.complete_flows.conversion_report_generator import ConversionReportGenerator
from npu_converter.complete_flows.model_validator import ValidationResult
from npu_converter.complete_flows.benchmark_system import BenchmarkResult

# 1. 创建报告生成器
generator = ConversionReportGenerator(output_dir='reports')

# 2. 获取转换结果 (假设您已经有了 ResultModel)
conversion_result = ...  # 来自转换流程的结果

# 3. 生成报告
report = generator.generate_report(
    conversion_result=conversion_result,
    report_format='html'  # 可选: json/html/pdf
)

# 4. 保存报告
filepath = generator.save_report(report, format='html')
print(f"报告已保存: {filepath}")
```

### 完整示例

```python
from npu_converter.complete_flows.conversion_report_generator import ConversionReportGenerator

# 创建报告生成器
generator = ConversionReportGenerator(output_dir='conversion_reports')

# 模拟转换结果数据
conversion_result = Mock()
conversion_result.model_name = "VITS_Cantonese_Model"
conversion_result.model_type = "TTS"
conversion_result.conversion_time = 15.0
conversion_result.success = True
conversion_result.resource_usage = {
    'cpu': 55.0,
    'memory': 1100.0,
    'npu': 80.0
}
conversion_result.steps = [
    {"step": 1, "name": "load", "time": 3.0},
    {"step": 2, "name": "convert", "time": 8.0},
    {"step": 3, "name": "optimize", "time": 4.0}
]
conversion_result.config = Mock()
conversion_result.config.quantization = "PTQ"
conversion_result.errors = []
conversion_result.warnings = []

# 生成报告
report = generator.generate_report(
    conversion_result=conversion_result,
    report_format='html',
    include_analysis=True,
    include_recommendations=True
)

# 保存报告
filepath = generator.save_report(report, format='html')
print(f"报告已生成: {filepath}")
print(f"质量等级: {report.quality_grade}")
print(f"整体评分: {report.overall_score:.2%}")
```

---

## 📊 报告内容详解

### 1. 基本信息

报告包含模型的基本信息：

- **模型名称**: 模型的标识名称
- **模型类型**: TTS/ASR/其他
- **转换日期**: 转换完成的日期时间
- **转换时间**: 转换过程耗时 (秒)
- **转换状态**: 成功/失败

### 2. 质量评估

综合质量评估采用加权平均算法：

- **整体评分**: 0-100% 的综合评分
- **质量等级**: A+ (优秀) / A (良好) / B (一般) / C (较差) / D (不合格)

评分权重分配：
- 性能评分: 30%
- 精度评分: 30%
- 兼容性评分: 25%
- 转换成功率: 15%

### 3. 性能指标

**性能评分**: 综合性能评估分数

**推理时间**: 模型推理的耗时 (秒)

**吞吐量**: 每秒处理的样本数 (samples/sec)

**资源使用**: 转换过程的资源消耗
- CPU 使用率 (%)
- 内存使用 (MB)
- NPU 使用率 (%)

### 4. 精度指标

**精度评分**: 模型精度评估分数

**精度损失**: 转换前后精度的差异

### 5. 兼容性指标

**兼容性评分**: 硬件和软件兼容性评估

**算子支持**: 支持的算子统计
- 支持的算子数
- 不支持的算子数
- 已转换的算子数
- 总算子数

**硬件兼容性**: 硬件平台兼容性信息
- NPU 兼容性
- Horizon X5 支持
- 内存需求
- 计算要求

### 6. 优化建议

基于分析结果，系统会生成优化建议：

**性能优化**:
- 性能 < 90%: 建议调整量化参数
- 推理时间 > 1s: 建议模型压缩

**精度优化**:
- 精度 < 95%: 建议增加校准数据
- 精度损失 > 5%: 建议调整量化算法

**兼容性优化**:
- 兼容性 < 90%: 建议检查不支持的算子
- 算子不支持: 建议使用替代方案

**资源优化**:
- 内存 > 2GB: 建议模型压缩或分块处理

---

## ⚙️ 配置选项

### 使用预设配置

```python
from npu_converter.config.conversion_report_config import get_preset_config

# 获取预设配置
config = get_preset_config('detailed')  # basic/detailed/production/quick

# 使用配置
generator = ConversionReportGenerator(output_dir='reports')
generator.config = config
```

### 创建自定义配置

```python
from npu_converter.config.conversion_report_config import create_custom_config

# 创建自定义配置
config = create_custom_config(
    format='html',
    include_performance=True,
    include_accuracy=True,
    include_compatibility=True,
    template_style='detailed',
    output_dir='my_reports'
)

# 使用配置
generator = ConversionReportGenerator(output_dir='my_reports')
```

### 配置文件

您可以修改默认配置文件：`/home/sunrise/xlerobot/src/npu_converter/config/conversion_report_default.yaml`

关键配置项：

```yaml
# 报告内容
include_performance: true
include_accuracy: true
include_compatibility: true
include_resource_usage: true
include_conversion_steps: true

# 质量阈值
performance_threshold: 0.90
accuracy_threshold: 0.95
compatibility_threshold: 0.90

# 输出配置
output_dir: conversion_reports
default_format: html
auto_generate: true
include_recommendations: true
include_analysis: true
```

---

## 📁 报告格式

### JSON 格式

适用于程序化处理和数据交换：

```json
{
  "model_name": "VITS_Cantonese_Model",
  "model_type": "TTS",
  "conversion_date": "2025-10-28",
  "conversion_time": 15.0,
  "success": true,
  "performance_score": 0.93,
  "accuracy_score": 0.987,
  "compatibility_score": 0.95,
  "overall_score": 0.94,
  "quality_grade": "A (良好)",
  "recommendations": [
    "性能优化建议: 考虑调整量化参数"
  ]
}
```

### HTML 格式

适用于人工查看和展示：

- 美观的网页格式
- 表格和图表展示
- 响应式设计
- 易于分享和打印

### PDF 格式

适用于文档存档和正式报告：

- 专业排版
- 固定格式
- 易于打印和存档

**注意**: 当前版本 PDF 功能使用 HTML 代替，后续版本将完善 PDF 生成。

---

## 🔄 批量报告生成

### 基本批量生成

```python
# 创建多个转换结果
conversion_results = [
    result1, result2, result3  # ResultModel 实例列表
]

# 批量生成报告
report_files = generator.batch_generate(
    conversion_results,
    output_format='json'
)

print(f"已生成 {len(report_files)} 个报告")
for filepath in report_files:
    print(f"  - {filepath}")
```

### 高级批量配置

```python
from npu_converter.config.conversion_report_config import get_preset_config

# 使用生产配置进行批量生成
config = get_preset_config('production')
generator.config = config

# 批量生成
report_files = generator.batch_generate(
    conversion_results,
    output_format='html'
)
```

---

## 🔍 高级用法

### 自定义报告内容

```python
# 生成只包含特定维度的报告
report = generator.generate_report(
    conversion_result=conversion_result,
    include_performance=True,
    include_accuracy=True,
    include_compatibility=False,  # 跳过兼容性
    include_resource_usage=False,  # 跳过资源使用
    include_conversion_steps=False,  # 跳过流程
    include_analysis=False,  # 跳过分析
    include_recommendations=False  # 跳过建议
)
```

### 实时监控报告生成

```python
# 集成实时监控
from npu_converter.complete_flows.realtime_monitor import RealtimeMonitor

monitor = RealtimeMonitor()
monitor.start()

# 生成报告
report = generator.generate_report(
    conversion_result=conversion_result
)

# 检查监控状态
status = monitor.get_status()
print(f"报告生成状态: {status}")
```

### 自定义质量评估

```python
# 修改质量评估权重
class CustomReportGenerator(ConversionReportGenerator):
    def _evaluate_quality(self, report):
        # 自定义权重
        scores = []
        weights = []

        if report.performance_score:
            scores.append(report.performance_score)
            weights.append(0.40)  # 性能权重 40%

        if report.accuracy_score:
            scores.append(report.accuracy_score)
            weights.append(0.40)  # 精度权重 40%

        # ... 其他自定义逻辑

        return report
```

---

## 🐛 常见问题

### Q1: 报告生成失败怎么办？

**A**: 检查以下几点：
1. 确认 `conversion_result` 参数不为空
2. 确认 `output_dir` 目录有写入权限
3. 查看日志获取详细错误信息

```python
try:
    report = generator.generate_report(conversion_result)
except Exception as e:
    print(f"报告生成失败: {e}")
    # 查看日志
    import logging
    logging.getLogger('npu_converter').error(str(e))
```

### Q2: 如何调整质量阈值？

**A**: 修改配置文件或使用自定义配置：

```python
from npu_converter.config.conversion_report_config import create_custom_config

config = create_custom_config()
config.performance_threshold = 0.85  # 调整性能阈值
config.accuracy_threshold = 0.90     # 调整精度阈值
```

### Q3: 报告文件太大怎么办？

**A**: 使用简化配置：

```python
config = get_preset_config('quick')  # 快速报告，文件最小
# 或
config = get_preset_config('basic')  # 基础报告
```

### Q4: 如何自定义建议内容？

**A**: 继承并重写 `_add_recommendations` 方法：

```python
class CustomReportGenerator(ConversionReportGenerator):
    def _add_recommendations(self, report):
        # 自定义建议逻辑
        recommendations = []

        if report.performance_score and report.performance_score < 0.90:
            recommendations.append("自定义: 考虑使用不同的量化方法")

        # 调用父类方法
        return super()._add_recommendations(report)
```

---

## 📈 最佳实践

### 1. 使用合适的配置

- **开发阶段**: 使用 `detailed` 配置获取完整信息
- **生产环境**: 使用 `production` 配置获取生产级报告
- **快速测试**: 使用 `quick` 配置快速生成简要报告

### 2. 批量生成效率

- 对于大量模型，使用 `batch_generate()` 提高效率
- 设置合适的并发数 (`concurrent_reports`)
- 使用合适的输出格式 (JSON 最快，HTML 最美观)

### 3. 报告存档

- 按日期组织报告目录结构
- 使用有意义的文件名
- 定期清理旧报告

### 4. 监控质量

- 定期检查报告质量评分
- 关注质量趋势变化
- 及时处理低质量模型

---

## 📚 相关资源

### 文档

- [BMM v6 完成报告](../story-2.9-bmm-v6-completion-report.md)
- [BMM v6 测试报告](../story-2.9-bmm-v6-test-report.md)
- [Epic 2 概览](../epics.md)

### 代码

- [转换报告生成器](../../src/npu_converter/complete_flows/conversion_report_generator.py)
- [配置系统](../../src/npu_converter/config/conversion_report_config.py)
- [默认配置](../../src/npu_converter/config/conversion_report_default.yaml)

### 测试

- [验收测试脚本](../../test_story_2_9_simple.py)
- [单元测试](../../tests/complete_flows/test_conversion_report_generator.py)

---

## 🎉 总结

转换报告生成系统提供了强大的报告生成能力，帮助您：

- 📊 **全面了解** 模型转换质量
- 🎯 **快速识别** 问题和优化点
- 📈 **跟踪趋势** 模型性能变化
- 💡 **获得指导** 优化建议

如有任何问题，请参考本文档或查看相关资源。

---

**文档版本**: 1.0.0
**最后更新**: 2025-10-28
**维护者**: Claude Code / BMM Method
