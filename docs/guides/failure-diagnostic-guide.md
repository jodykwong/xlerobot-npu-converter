# 转换失败诊断系统用户指南

**版本**: 1.0.0
**日期**: 2025-10-28
**作者**: XLeRobot 开发团队

---

## 📖 目录

1. [简介](#简介)
2. [快速开始](#快速开始)
3. [功能特性](#功能特性)
4. [配置管理](#配置管理)
5. [使用示例](#使用示例)
6. [最佳实践](#最佳实践)
7. [故障排除](#故障排除)
8. [常见问题](#常见问题)
9. [API参考](#api参考)
10. [附录](#附录)

---

## 简介

### 概述

转换失败诊断系统是 XLeRobot NPU模型转换工具的核心组件之一，专门用于诊断和分析转换失败的原因。该系统提供多维度诊断、智能错误分析、修复建议和失败预防等功能，帮助用户快速定位问题并解决转换失败。

### 主要功能

- **多维度失败诊断**: 支持转换流程、模型结构、兼容性、配置、环境五个维度的诊断
- **智能错误分析**: 基于关键词和模式的智能错误分类和根因分析
- **修复建议系统**: 提供详细的修复建议和步骤指导
- **失败预防系统**: 基于历史数据提供预防措施和最佳实践
- **报告生成**: 支持JSON和HTML格式的详细诊断报告
- **配置管理**: 提供灵活的配置文件管理和预设配置

### 适用场景

- 转换失败时快速定位问题
- 分析转换失败的根本原因
- 获取修复建议和步骤指导
- 预防未来可能发生的失败
- 生成详细的失败分析报告

---

## 快速开始

### 安装和设置

转换失败诊断系统已经集成在 XLeRobot NPU模型转换工具中，无需单独安装。

### 基本使用

#### 1. 导入模块

```python
from src.npu_converter.complete_flows.failure_diagnostic_system import (
    FailureDiagnosticSystem,
    FailureDiagnostic
)
from src.npu_converter.config.failure_diagnostic_config import (
    FailureDiagnosticConfig,
    FailureDiagnosticConfigStrategy
)
```

#### 2. 创建诊断系统实例

```python
from src.npu_converter.config.manager import ConfigurationManager

# 创建配置管理器
config_manager = ConfigurationManager()

# 创建诊断系统
diagnostic_system = FailureDiagnosticSystem(config_manager=config_manager)
```

#### 3. 诊断转换失败

```python
try:
    # 执行转换操作
    perform_conversion()
except Exception as e:
    # 诊断失败
    diagnostic = diagnostic_system.diagnose_failure(
        error=e,
        model_name="my_model"
    )

    # 打印诊断结果
    print(f"失败类型: {diagnostic.failure_type}")
    print(f"严重程度: {diagnostic.severity}")
    print(f"根因分析: {diagnostic.root_cause}")
    print(f"修复建议: {diagnostic.suggestions}")
```

#### 4. 生成诊断报告

```python
# 生成JSON报告
json_report = diagnostic_system.generate_diagnostic_report(
    diagnostic=diagnostic,
    output_format='json'
)

# 生成HTML报告
html_report = diagnostic_system.generate_diagnostic_report(
    diagnostic=diagnostic,
    output_format='html'
)

# 保存报告
diagnostic_system.save_diagnostic_report(
    diagnostic=diagnostic,
    output_path=Path("reports/failure_diagnostic.json"),
    output_format='json'
)
```

---

## 功能特性

### 多维度失败诊断

系统支持五个维度的诊断：

1. **转换流程维度**
   - 检查转换步骤是否正确
   - 验证参数设置
   - 分析转换状态

2. **模型结构维度**
   - 分析算子支持
   - 检查数据类型
   - 验证模型形状

3. **兼容性维度**
   - 硬件兼容性检查
   - 算子支持分析
   - 版本兼容性验证

4. **配置维度**
   - 参数设置验证
   - 资源需求检查
   - 环境配置分析

5. **环境维度**
   - 依赖库检查
   - 权限验证
   - 路径有效性

### 智能错误分析

系统使用基于关键词的智能算法进行错误分类：

```python
# 错误分类示例
if 'file' in error_msg or 'model' in error_msg:
    return 'model_load_error'
elif 'quant' in error_msg:
    return 'quantization_error'
elif 'optim' in error_msg:
    return 'optimization_error'
```

### 修复建议系统

系统提供三层修复建议：

1. **知识库建议**: 基于知识库的通用建议
2. **特定建议**: 基于错误消息的特定建议
3. **通用建议**: 适用于所有错误的通用建议

### 失败预防系统

系统提供以下预防措施：

- 转换前检查清单
- 最佳实践建议
- 风险评估和预警
- 历史数据分析

---

## 配置管理

### 默认配置

系统提供以下默认设置：

```yaml
# 诊断设置
include_stack_trace: true
max_suggestions: 5
max_fix_steps: 10
max_prevention_measures: 5

# 报告设置
report_format: json
report_output_dir: reports/failure_diagnostics
auto_save_reports: true

# 严重程度阈值
severity_thresholds:
  critical: 0.8
  high: 0.6
  medium: 0.4
  low: 0.2
```

### 预设配置

系统提供5种预设配置：

1. **basic**: 基础配置，最小化输出
2. **detailed**: 详细配置，完整输出
3. **production**: 生产配置，稳定可靠
4. **quick**: 快速配置，简化处理
5. **development**: 开发配置，调试友好

#### 使用预设配置

```python
from src.npu_converter.config.manager import ConfigurationManager
from src.npu_converter.config.failure_diagnostic_config import (
    FailureDiagnosticConfigStrategy
)

config_manager = ConfigurationManager()
config_strategy = FailureDiagnosticConfigStrategy(config_manager)

# 加载预设配置
config = config_strategy.load_config(preset_name='production')
```

### 自定义配置

```python
from src.npu_converter.config.failure_diagnostic_config import (
    FailureDiagnosticConfig
)

# 创建自定义配置
config = FailureDiagnosticConfig(
    max_suggestions=10,
    report_format='html',
    auto_save_reports=True
)

# 验证配置
config.validate()
```

---

## 使用示例

### 示例1: 基本失败诊断

```python
from src.npu_converter.complete_flows.failure_diagnostic_system import (
    FailureDiagnosticSystem
)
from src.npu_converter.config.manager import ConfigurationManager

# 创建诊断系统
config_manager = ConfigurationManager()
diagnostic_system = FailureDiagnosticSystem(config_manager=config_manager)

# 模拟转换失败
try:
    # 模拟文件不存在错误
    raise FileNotFoundError("模型文件不存在: model.onnx")
except FileNotFoundError as e:
    # 诊断失败
    diagnostic = diagnostic_system.diagnose_failure(
        error=e,
        model_name="my_voice_model"
    )

    # 输出诊断结果
    print(f"错误代码: {diagnostic.error_code}")
    print(f"失败类型: {diagnostic.failure_type}")
    print(f"严重程度: {diagnostic.severity}")
    print(f"根因分析: {diagnostic.root_cause}")

    # 打印修复建议
    print("\n修复建议:")
    for i, suggestion in enumerate(diagnostic.suggestions, 1):
        print(f"{i}. {suggestion}")
```

### 示例2: 量化失败诊断

```python
try:
    # 模拟量化失败
    raise ValueError("校准数据不足，无法进行量化")
except ValueError as e:
    diagnostic = diagnostic_system.diagnose_failure(
        error=e,
        model_name="my_asr_model"
    )

    # 打印诊断结果
    print(f"失败阶段: {diagnostic.failure_stage}")
    print(f"失败类型: {diagnostic.failure_type}")

    # 打印修复步骤
    print("\n修复步骤:")
    for i, step in enumerate(diagnostic.fix_steps, 1):
        print(f"{i}. {step}")
```

### 示例3: 批量失败诊断

```python
# 准备多个失败案例
errors = [
    (FileNotFoundError("模型文件不存在"), "model1"),
    (ValueError("配置参数无效"), "model2"),
    (RuntimeError("优化策略不匹配"), "model3")
]

# 批量诊断
diagnostics = diagnostic_system.batch_diagnose(errors)

# 分析诊断历史
summary = diagnostic_system.analyze_diagnostic_history()
print(f"总失败数: {summary.total_failures}")
print(f"严重失败数: {summary.critical_failures}")
print(f"最常见失败类型: {summary.most_common_failure_type}")

# 推荐行动
print("\n推荐行动:")
for action in summary.recommended_actions:
    print(f"- {action}")
```

### 示例4: 生成详细报告

```python
# 生成JSON报告
json_report = diagnostic_system.generate_diagnostic_report(
    diagnostic=diagnostic,
    output_format='json'
)

# 保存JSON报告
diagnostic_system.save_diagnostic_report(
    diagnostic=diagnostic,
    output_path=Path("reports/diagnostic_report.json"),
    output_format='json'
)

# 生成HTML报告
html_report = diagnostic_system.generate_diagnostic_report(
    diagnostic=diagnostic,
    output_format='html'
)

# 保存HTML报告
diagnostic_system.save_diagnostic_report(
    diagnostic=diagnostic,
    output_path=Path("reports/diagnostic_report.html"),
    output_format='html'
)
```

### 示例5: 导出诊断历史

```python
# 执行多次诊断
for i in range(5):
    try:
        raise ValueError(f"测试错误 {i+1}")
    except ValueError as e:
        diagnostic_system.diagnose_failure(
            error=e,
            model_name=f"test_model_{i+1}"
        )

# 导出诊断历史
diagnostic_system.export_diagnostic_history(
    output_path=Path("reports/diagnostic_history.json")
)
```

---

## 最佳实践

### 1. 早期集成

在转换流程的早期阶段集成失败诊断系统，以便及时发现和解决问题。

```python
# 在转换流程中集成诊断
def convert_model(model_path, output_path):
    try:
        # 执行转换
        result = perform_conversion(model_path, output_path)
        return result
    except Exception as e:
        # 立即诊断失败
        diagnostic = diagnostic_system.diagnose_failure(
            error=e,
            model_name=get_model_name(model_path)
        )

        # 保存诊断报告
        diagnostic_system.save_diagnostic_report(
            diagnostic=diagnostic,
            output_path=Path(f"reports/{get_timestamp()}_diagnostic.json")
        )

        # 重新抛出异常
        raise
```

### 2. 分类处理

根据失败类型采用不同的处理策略。

```python
# 根据失败类型处理
if diagnostic.failure_type == 'model_load_error':
    # 处理模型加载错误
    handle_model_load_error(diagnostic)
elif diagnostic.failure_type == 'quantization_error':
    # 处理量化错误
    handle_quantization_error(diagnostic)
elif diagnostic.failure_type == 'optimization_error':
    # 处理优化错误
    handle_optimization_error(diagnostic)
```

### 3. 严重程度分级

根据严重程度采取不同的响应措施。

```python
# 根据严重程度响应
if diagnostic.severity == 'CRITICAL':
    # 严重失败，立即停止并告警
    send_alert(diagnostic)
    exit(1)
elif diagnostic.severity == 'HIGH':
    # 高级失败，记录并通知
    log_error(diagnostic)
    notify_team(diagnostic)
elif diagnostic.severity in ['MEDIUM', 'LOW']:
    # 中低级失败，记录并继续
    log_warning(diagnostic)
```

### 4. 预防措施

根据诊断结果采取预防措施，避免未来发生类似失败。

```python
# 执行预防措施
for measure in diagnostic.prevention_measures:
    execute_prevention_measure(measure)

# 更新知识库
update_knowledge_base(diagnostic)
```

### 5. 定期分析

定期分析诊断历史，识别模式和趋势。

```python
# 每周分析诊断历史
summary = diagnostic_system.analyze_diagnostic_history()
if summary.critical_failures > 10:
    # 失败数过多，需要改进
    improve_conversion_process(summary)

if summary.most_common_failure_type:
    # 针对最常见失败类型进行优化
    optimize_for_failure_type(summary.most_common_failure_type)
```

---

## 故障排除

### 问题1: 无法导入模块

**症状**:
```
ImportError: No module named 'npu_converter'
```

**解决方案**:
确保设置了正确的Python路径：
```bash
export PYTHONPATH=/path/to/xlerobot/src:$PYTHONPATH
```

### 问题2: 诊断结果为空

**症状**: 生成的诊断结果缺少关键信息

**解决方案**:
1. 检查错误对象是否正确传递
2. 确认配置管理器已正确初始化
3. 验证知识库是否正确加载

### 问题3: 报告生成失败

**症状**: 生成报告时出现错误

**解决方案**:
1. 检查输出路径是否有写入权限
2. 确认输出目录是否存在
3. 验证报告格式是否正确

### 问题4: 配置验证失败

**症状**: 配置验证时抛出异常

**解决方案**:
1. 检查配置值是否符合要求
2. 确认配置格式正确
3. 验证必需字段是否存在

---

## 常见问题

### Q1: 支持哪些错误类型？

**A**: 系统支持以下错误类型：
- `model_load_error`: 模型加载错误
- `quantization_error`: 量化错误
- `optimization_error`: 优化错误
- `export_error`: 导出错误
- `environment_error`: 环境错误
- `configuration_error`: 配置错误

### Q2: 如何自定义修复建议？

**A**: 可以通过修改知识库来自定义修复建议：
```python
# 扩展知识库
diagnostic_system.knowledge_base['custom_error'] = {
    'root_causes': ['自定义根因1', '自定义根因2'],
    'fix_steps': ['修复步骤1', '修复步骤2'],
    'prevention_measures': ['预防措施1', '预防措施2']
}
```

### Q3: 如何调整严重程度阈值？

**A**: 可以修改配置文件中的`severity_thresholds`设置：
```yaml
severity_thresholds:
  critical: 0.9   # 提高严重失败的阈值
  high: 0.7
  medium: 0.5
  low: 0.3
```

### Q4: 如何批量处理失败？

**A**: 使用`batch_diagnose`方法：
```python
errors = [(error1, model1), (error2, model2)]
diagnostics = diagnostic_system.batch_diagnose(errors)
```

### Q5: 如何集成到CI/CD流水线？

**A**: 在CI/CD流水线中添加失败诊断步骤：
```yaml
- name: Run model conversion
  run: |
    python convert_model.py
    if [ $? -ne 0 ]; then
      python diagnostic_script.py
    fi
```

---

## API参考

### FailureDiagnosticSystem

#### `__init__(config_manager, report_generator=None)`

初始化诊断系统。

**参数**:
- `config_manager`: 配置管理器实例
- `report_generator`: 报告生成器实例（可选）

#### `diagnose_failure(error, model_name, conversion_result=None, context=None)`

诊断转换失败。

**参数**:
- `error`: 错误对象
- `model_name`: 模型名称
- `conversion_result`: 转换结果（可选）
- `context`: 错误上下文（可选）

**返回**: `FailureDiagnostic`对象

#### `generate_diagnostic_report(diagnostic, output_format='json')`

生成诊断报告。

**参数**:
- `diagnostic`: 诊断结果对象
- `output_format`: 输出格式（'json' 或 'html'）

**返回**: 报告内容字符串

#### `save_diagnostic_report(diagnostic, output_path, output_format='json')`

保存诊断报告到文件。

**参数**:
- `diagnostic`: 诊断结果对象
- `output_path`: 输出文件路径
- `output_format`: 输出格式

#### `batch_diagnose(errors, context_data=None)`

批量诊断失败。

**参数**:
- `errors`: 错误列表，每个元素为(error, model_name)元组
- `context_data`: 上下文数据（可选）

**返回**: 诊断结果列表

#### `analyze_diagnostic_history()`

分析诊断历史记录。

**返回**: `DiagnosticSummary`对象

### FailureDiagnostic

诊断结果数据类，包含以下字段：
- `model_name`: 模型名称
- `failure_stage`: 失败阶段
- `failure_type`: 失败类型
- `failure_message`: 失败消息
- `root_cause`: 根因分析
- `severity`: 严重程度
- `diagnosis_time`: 诊断时间
- `suggestions`: 修复建议列表
- `fix_steps`: 修复步骤列表
- `prevention_measures`: 预防措施列表
- `error_code`: 错误代码
- `stack_trace`: 堆栈跟踪（可选）
- `context`: 错误上下文（可选）

### FailureDiagnosticConfig

配置数据类，包含以下字段：
- `include_stack_trace`: 是否包含堆栈跟踪
- `max_suggestions`: 最大建议数量
- `max_fix_steps`: 最大修复步骤数量
- `max_prevention_measures`: 最大预防措施数量
- `report_format`: 报告格式
- `report_output_dir`: 报告输出目录
- `auto_save_reports`: 是否自动保存报告
- `severity_thresholds`: 严重程度阈值
- `error_classification_rules`: 错误分类规则

---

## 附录

### 错误代码格式

错误代码格式：`[TYPE]-[STAGE]-[TIMESTAMP]`

示例：`MOD-MOD-20251028101656`
- `MOD`: 失败类型代码
- `MOD`: 失败阶段代码
- `20251028101656`: 时间戳

### 严重程度说明

- **CRITICAL**: 严重失败，需要立即处理
- **HIGH**: 高级失败，需要尽快处理
- **MEDIUM**: 中级失败，需要处理
- **LOW**: 低级失败，建议处理

### 报告字段说明

#### JSON报告字段

- `model_name`: 模型名称
- `failure_stage`: 失败阶段
- `failure_type`: 失败类型
- `failure_message`: 失败消息
- `root_cause`: 根因分析
- `severity`: 严重程度
- `diagnosis_time`: 诊断时间
- `suggestions`: 修复建议列表
- `fix_steps`: 修复步骤列表
- `prevention_measures`: 预防措施列表
- `error_code`: 错误代码
- `stack_trace`: 堆栈跟踪
- `context`: 错误上下文

#### HTML报告内容

HTML报告包含以下部分：
- 标题和基本信息
- 失败信息
- 根因分析
- 修复建议
- 修复步骤
- 预防措施
- 堆栈跟踪

### 知识库结构

```python
knowledge_base = {
    'failure_type': {
        'root_causes': ['根因1', '根因2'],
        'fix_steps': ['步骤1', '步骤2'],
        'prevention_measures': ['措施1', '措施2']
    }
}
```

### 性能基准

- 单次诊断时间: < 100ms
- 批量诊断性能: > 10个并发
- JSON报告生成: < 50ms
- HTML报告生成: < 100ms
- 配置加载: < 20ms

---

## 支持与反馈

如果您在使用过程中遇到问题或有任何建议，请：

1. 查看本文档的故障排除部分
2. 提交Issue到项目仓库
3. 联系技术支持团队

---

**文档版本**: 1.0.0
**最后更新**: 2025-10-28