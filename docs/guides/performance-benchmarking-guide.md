# 性能基准测试使用指南

**版本**: v1.0
**适用对象**: 开发人员、性能工程师、测试工程师
**最后更新**: 2025-10-29
**项目**: XLeRobot NPU模型转换工具

---

## 📋 目录

1. [概述](#概述)
2. [快速开始](#快速开始)
3. [安装和配置](#安装和配置)
4. [使用指南](#使用指南)
5. [测试用例说明](#测试用例说明)
6. [报告和可视化](#报告和可视化)
7. [告警设置](#告警设置)
8. [最佳实践](#最佳实践)
9. [常见问题](#常见问题)
10. [故障排除](#故障排除)

---

## 概述

### 什么是性能基准测试系统？

XLeRobot性能基准测试系统是一个全面的性能监控和测试工具，专门为NPU模型转换工具设计。它帮助您：

- 📊 **监控性能指标**：实时跟踪CPU、内存、GPU/NPU使用情况
- 🧪 **运行基准测试**：执行标准化的性能测试用例
- 📈 **分析性能趋势**：识别性能瓶颈和优化机会
- 📄 **生成报告**：创建详细的性能分析报告
- ⚠️ **设置告警**：及时发现性能异常

### 系统架构

```
┌─────────────────────────────────────────────┐
│            性能基准测试系统                   │
├─────────────────────────────────────────────┤
│                                             │
│  1. 测试执行层                              │
│     - 基准测试执行器                        │
│     - 测试用例套件                          │
│                                             │
│  2. 数据采集层                              │
│     - 指标采集器                            │
│     - 系统监控                              │
│                                             │
│  3. 分析处理层                              │
│     - 性能分析器                            │
│     - 异常检测                              │
│                                             │
│  4. 展示层                                  │
│     - 报告生成器                            │
│     - 可视化引擎                            │
│     - 告警系统                              │
└─────────────────────────────────────────────┘
```

### 主要功能特性

✅ **多维度监控**
- CPU使用率和负载
- 内存使用量和分配
- GPU/NPU利用率和显存
- 磁盘I/O性能
- 网络I/O性能
- 转换速率和响应时间

✅ **内置测试用例**
- 8个标准化测试用例
- 覆盖单模型、并发、压力、稳定性测试
- 支持自定义测试用例

✅ **智能分析**
- 自动异常检测
- 性能趋势分析
- 性能对比分析
- 优化建议生成

✅ **灵活报告**
- HTML报告（交互式）
- PDF报告（可打印）
- JSON数据（可编程）
- CSV数据（可导入Excel）

✅ **实时告警**
- 多级告警（低、中、高、严重）
- 自定义告警规则
- 多种通知方式

---

## 快速开始

### 5分钟快速体验

让我们通过一个简单的例子来快速了解系统的工作流程。

#### 步骤1：导入必要的模块

```python
# 导入性能基准测试核心组件
from npu_converter.performance import (
    BenchmarkRunner,      # 测试执行器
    MetricsCollector,     # 指标采集器
    BenchmarkSuite,       # 测试用例套件
)

# 导入配置类
from npu_converter.performance import (
    BenchmarkConfig,
    MetricsConfig,
    SuiteConfig
)
```

#### 步骤2：创建配置对象

```python
# 创建基准测试配置
benchmark_config = BenchmarkConfig(
    max_concurrent=10,           # 最大并发数：10
    test_timeout=3600,           # 测试超时：1小时
    output_dir="reports/performance"  # 输出目录
)

# 创建指标采集配置
metrics_config = MetricsConfig(
    collection_interval=1,       # 采集间隔：1秒
    enable_gpu_monitoring=True,  # 启用GPU监控
    enable_npu_monitoring=True   # 启用NPU监控
)

# 创建测试套件配置
suite_config = SuiteConfig()
```

#### 步骤3：创建组件实例

```python
# 创建组件实例
runner = BenchmarkRunner(benchmark_config)
collector = MetricsCollector(metrics_config)
suite = BenchmarkSuite(suite_config)

print("✅ 所有组件创建成功！")
```

#### 步骤4：运行测试用例

```python
# 获取一个测试用例
test_case = suite.get_test_case("TC-001")

# 启动指标采集
collector.start_collection("test-001")

# 运行测试
result = runner.run_benchmark(test_case)

# 停止指标采集
metrics = collector.stop_collection("test-001")

# 打印结果
print(f"测试用例: {result.test_id}")
print(f"状态: {result.status}")
print(f"耗时: {result.duration:.2f}秒")
print(f"CPU使用率: {metrics.cpu_usage:.2f}%")
print(f"内存使用: {metrics.memory_usage:.2f}MB")
```

#### 运行结果示例

```
✅ 所有组件创建成功！
2025-10-29 01:20:15 - npu_converter.performance.benchmark_runner - INFO - Starting test TC-001
2025-10-29 01:20:16 - npu_converter.performance.benchmark_runner - INFO - Test completed successfully

测试用例: TC-001
状态: success
耗时: 1.23秒
CPU使用率: 45.67%
内存使用: 1024.56MB
```

### 下一步

恭喜！您已经成功运行了第一个性能测试。

接下来，您可以：
- 📖 阅读[完整使用指南](#使用指南)
- 🧪 尝试[更多测试用例](#测试用例说明)
- 📊 查看[报告和可视化](#报告和可视化)
- ⚠️ 设置[告警规则](#告警设置)

---

## 安装和配置

### 环境要求

- **Python**: 3.8+ (推荐 3.10)
- **操作系统**: Linux, Windows, macOS
- **依赖库**: 见 requirements.txt

### 安装步骤

#### 1. 安装依赖

```bash
# 克隆项目（如果尚未克隆）
git clone <repository-url>
cd xlerobot

# 安装项目依赖
pip install -r requirements.txt

# 安装性能测试依赖
pip install pytest pytest-benchmark psutil matplotlib plotly pandas numpy

# 以开发模式安装
pip install -e .
```

#### 2. 验证安装

```python
# 验证所有组件可以正常导入
try:
    from npu_converter.performance import (
        BenchmarkRunner,
        MetricsCollector,
        BenchmarkSuite,
        PerformanceAnalyzer,
        ReportGenerator,
        VisualizationEngine,
        AlertSystem
    )
    print("✅ 所有组件安装成功！")
except ImportError as e:
    print(f"❌ 安装失败: {e}")
```

#### 3. 配置系统

##### 默认配置

系统提供默认配置，可以直接使用：

```python
from npu_converter.performance import BenchmarkConfig

config = BenchmarkConfig()  # 使用默认配置
runner = BenchmarkRunner(config)
```

##### 自定义配置

创建自定义配置文件：

```python
# 创建自定义配置
config = BenchmarkConfig(
    max_concurrent=20,              # 增加并发数
    test_timeout=7200,              # 延长超时时间
    retry_count=5,                  # 增加重试次数
    output_dir="my_reports",        # 指定输出目录
    cleanup_after_test=False,       # 保留测试数据
    save_raw_data=True              # 保存原始数据
)
```

##### 配置文件

您也可以使用YAML配置文件：

```yaml
# config/performance/my_config.yaml
benchmark:
  max_concurrent: 15
  test_timeout: 3600
  retry_count: 3
  output_dir: "reports/performance"

metrics:
  collection_interval: 2
  buffer_size: 2000
  enable_gpu_monitoring: true
  enable_npu_monitoring: true
  storage_type: "sqlite"
```

加载配置文件：

```python
import yaml

# 加载配置
with open("config/performance/my_config.yaml", "r") as f:
    config_data = yaml.safe_load(f)

# 创建配置对象
benchmark_config = BenchmarkConfig(**config_data["benchmark"])
metrics_config = MetricsConfig(**config_data["metrics"])
```

### GPU/NPU监控配置

#### GPU监控

```python
metrics_config = MetricsConfig(
    enable_gpu_monitoring=True,  # 启用GPU监控
)

# 检查GPU可用性
try:
    import GPUtil
    print("✅ GPU监控已启用")
except ImportError:
    print("⚠️ GPU监控依赖未安装，使用pip install GPUtil安装")
```

#### NPU监控

```python
metrics_config = MetricsConfig(
    enable_npu_monitoring=True,  # 启用NPU监控
)

# 检查NPU可用性
try:
    # 检查NPU设备
    import subprocess
    result = subprocess.run(["which", " npu-smi"], capture_output=True)
    if result.returncode == 0:
        print("✅ NPU监控已启用")
    else:
        print("⚠️ 未检测到NPU设备")
except Exception as e:
    print(f"⚠️ NPU监控错误: {e}")
```

---

## 使用指南

### 1. 运行单个测试用例

#### 基本用法

```python
# 创建配置和组件
config = BenchmarkConfig()
suite = BenchmarkSuite()

# 获取测试用例
test_case = suite.get_test_case("TC-001")

# 运行测试
runner = BenchmarkRunner(config)
result = runner.run_benchmark(test_case)

# 打印结果
print(f"测试结果: {result.status}")
print(f"耗时: {result.duration:.2f}秒")
```

#### 带参数运行

```python
# 获取测试用例并修改参数
test_case = suite.get_test_case("TC-004")  # 并发测试

# 修改测试参数
test_case.parameters.update({
    "model_count": 5,              # 同时测试5个模型
    "test_duration": 300,          # 测试持续5分钟
    "warmup_time": 30              # 预热30秒
})

result = runner.run_benchmark(test_case)
```

### 2. 运行测试套件

#### 运行多个测试用例

```python
# 创建测试套件
test_suite = suite.create_test_suite([
    "TC-001",  # SenseVoice ASR
    "TC-002",  # VITS-Cantonese TTS
    "TC-003",  # Piper VITS TTS
])

# 运行套件
results = runner.run_suite(test_suite)

# 打印汇总结果
print(f"测试套件完成:")
print(f"  总测试数: {len(results)}")
success_count = sum(1 for r in results if r.status == "success")
print(f"  成功: {success_count}")
print(f"  失败: {len(results) - success_count}")
```

#### 并行运行

```python
# 启用并行执行
results = runner.run_suite(
    test_suite,
    parallel=True,           # 启用并行
    max_workers=10           # 最大工作线程数
)

print("✅ 并行执行完成")
```

### 3. 指标采集

#### 实时监控

```python
# 创建指标采集器
collector = MetricsCollector(MetricsConfig())

# 定义回调函数
def on_metrics_update(metrics):
    print(f"CPU: {metrics.cpu_usage:5.1f}% | "
          f"内存: {metrics.memory_usage:8.1f}MB | "
          f"GPU: {metrics.gpu_usage:5.1f}%")

# 订阅实时更新
collector.subscribe(on_metrics_update)

# 开始采集
test_id = "test-001"
collector.start_collection(test_id)

# 运行测试
result = runner.run_benchmark(test_case)

# 停止采集
collector.stop_collection(test_id)
```

#### 获取历史数据

```python
# 获取测试期间的指标历史
history = collector.get_metrics_history("test-001")

# 计算统计信息
cpu_usage_values = [m.cpu_usage for m in history]
avg_cpu = sum(cpu_usage_values) / len(cpu_usage_values)
max_cpu = max(cpu_usage_values)

print(f"平均CPU使用率: {avg_cpu:.2f}%")
print(f"最大CPU使用率: {max_cpu:.2f}%")
```

### 4. 性能分析

#### 基本分析

```python
from npu_converter.performance import PerformanceAnalyzer, AnalyzerConfig

# 创建分析器
analyzer = PerformanceAnalyzer(AnalyzerConfig())

# 分析测试结果
analysis = analyzer.analyze_results(results)

# 打印分析结果
print(f"分析结果:")
print(f"  总测试数: {analysis.total_tests}")
print(f"  成功率: {analysis.success_rate:.2%}")
print(f"  平均耗时: {analysis.avg_duration:.2f}秒")
print(f"  P95耗时: {analysis.p95_duration:.2f}秒")
print(f"  P99耗时: {analysis.p99_duration:.2f}秒")
```

#### 异常检测

```python
# 检测性能异常
anomalies = analyzer.detect_anomalies(history)

if anomalies:
    print("⚠️ 检测到性能异常:")
    for anomaly in anomalies:
        print(f"  - {anomaly.type}: {anomaly.description}")
        print(f"    指标: {anomaly.metric} = {anomaly.value:.2f}")
        print(f"    阈值: {anomaly.threshold:.2f}")
        print(f"    严重程度: {anomaly.severity}")
else:
    print("✅ 未检测到性能异常")
```

#### 性能对比

```python
# 对比两个测试结果
baseline_results = ...  # 基线测试结果
current_results = ...   # 当前测试结果

comparison = analyzer.compare_benchmarks(
    baseline_results,
    current_results
)

print(f"性能对比:")
print(f"  变化率: {comparison.percentage_change:+.2f}%")
if comparison.is_regression:
    print("  ⚠️ 检测到性能回归")
    print(f"  受影响的指标: {', '.join(comparison.regressed_metrics)}")
elif comparison.is_improvement:
    print("  ✅ 性能有所提升")
```

### 5. 生成报告

```python
from npu_converter.performance import ReportGenerator, ReportConfig

# 创建报告生成器
generator = ReportGenerator(ReportConfig(
    include_charts=True,
    include_recommendations=True
))

# 生成汇总报告
summary = generator.generate_summary_report(analysis)

# 导出报告
generator.export_report(summary, "html", "reports/summary.html")
generator.export_report(summary, "pdf", "reports/summary.pdf")
generator.export_report(summary, "json", "reports/summary.json")

print("✅ 报告已生成")
print("  - HTML: reports/summary.html")
print("  - PDF:  reports/summary.pdf")
print("  - JSON: reports/summary.json")
```

### 6. 可视化

```python
from npu_converter.performance import VisualizationEngine, VisualizationConfig

# 创建可视化引擎
viz = VisualizationEngine(VisualizationConfig(
    width=1200,
    height=800,
    dpi=150
))

# 生成可视化图表
viz.create_time_series_chart(
    metrics_history,
    "charts/time_series.png"
)

viz.create_comparison_chart(
    baseline_results,
    current_results,
    "charts/comparison.png"
)

viz.create_dashboard(
    analysis,
    "dashboard.html"
)

print("✅ 可视化图表已生成")
print("  - 时间序列图: charts/time_series.png")
print("  - 对比图: charts/comparison.png")
print("  - 仪表盘: dashboard.html")
```

### 7. 告警设置

```python
from npu_converter.performance import AlertSystem, AlertConfig, AlertRule

# 创建告警系统
alerts = AlertSystem(AlertConfig(
    check_interval=60,
    default_severity="medium"
))

# 添加告警规则
alerts.add_rule(AlertRule(
    name="高CPU使用率",
    metric="cpu_usage",
    threshold=80.0,
    comparison=">",
    severity="high",
    message="CPU使用率超过80%"
))

alerts.add_rule(AlertRule(
    name="高内存使用率",
    metric="memory_usage",
    threshold=4096.0,  # 4GB
    comparison=">",
    severity="high",
    message="内存使用率超过4GB"
))

# 订阅告警事件
def on_alert(alert):
    print(f"🚨 告警: {alert.title}")
    print(f"   严重程度: {alert.severity}")
    print(f"   消息: {alert.message}")
    print(f"   指标: {alert.metric} = {alert.value:.2f}")

alerts.subscribe(on_alert)

# 检查当前指标
current_metrics = collector.get_current_metrics()
alerts.check_metrics(current_metrics)
```

---

## 测试用例说明

系统提供8个内置测试用例，覆盖各种性能测试场景。

### 单模型测试 (TC-001 to TC-003)

#### TC-001: SenseVoice ASR模型转换性能测试

**用途**: 测试SenseVoice ASR模型的NPU转换性能

**测试参数**:
- `iterations`: 迭代次数（默认100）
- `warmup_iterations`: 预热迭代次数（默认10）
- `model_path`: 模型路径（可选）

```python
test_case = suite.get_test_case("TC-001")
result = runner.run_benchmark(test_case)
```

**预期结果**:
- 转换速率: >10 模型/分钟
- 平均延迟: <30秒
- CPU使用率: <70%
- 内存使用: <2GB

#### TC-002: VITS-Cantonese TTS模型转换性能测试

**用途**: 测试VITS-Cantonese TTS模型的NPU转换性能

```python
test_case = suite.get_test_case("TC-002")
result = runner.run_benchmark(test_case)
```

**预期结果**:
- 转换速率: >8 模型/分钟
- 平均延迟: <35秒
- CPU使用率: <70%
- 内存使用: <2GB

#### TC-003: Piper VITS TTS模型转换性能测试

**用途**: 测试Piper VITS TTS模型的NPU转换性能

```python
test_case = suite.get_test_case("TC-003")
result = runner.run_benchmark(test_case)
```

**预期结果**:
- 转换速率: >8 模型/分钟
- 平均延迟: <35秒
- CPU使用率: <70%
- 内存使用: <2GB

### 并发测试 (TC-004)

#### TC-004: 多模型并发转换性能测试

**用途**: 测试多个模型并发转换的性能

**测试参数**:
- `model_count`: 同时转换的模型数量（默认5）
- `test_duration`: 测试持续时间（秒，默认300）
- `model_types`: 模型类型列表（默认["asr", "tts"]）

```python
test_case = suite.get_test_case("TC-004")
test_case.parameters.update({
    "model_count": 10,
    "test_duration": 600
})
result = runner.run_benchmark(test_case)
```

**预期结果**:
- 并发效率: >80%
- 总吞吐量: 单模型的5-8倍
- CPU使用率: <85%
- 内存使用: 随并发数线性增长

### 压力测试 (TC-005)

#### TC-005: 高压力转换性能测试

**用途**: 在高负载情况下测试转换性能

**测试参数**:
- `stress_level`: 压力级别（1-10，默认5）
- `duration`: 压力测试持续时间（秒，默认600）
- `ramp_up_time`: 负载上升时间（秒，默认60）

```python
test_case = suite.get_test_case("TC-005")
test_case.parameters.update({
    "stress_level": 8,
    "duration": 900
})
result = runner.run_benchmark(test_case)
```

**预期结果**:
- 在高负载下仍能保持稳定转换
- 系统无崩溃或死锁
- 资源使用在合理范围内

### 稳定性测试 (TC-006 to TC-007)

#### TC-006: 24小时长期稳定性测试

**用途**: 测试系统长期运行的稳定性

**测试参数**:
- `duration`: 测试持续时间（小时，默认24）
- `check_interval`: 检查间隔（分钟，默认60）

```python
test_case = suite.get_test_case("TC-006")
test_case.parameters.update({
    "duration": 48  # 测试48小时
})
result = runner.run_benchmark(test_case)
```

**预期结果**:
- 长时间运行无崩溃
- 内存使用无泄漏
- 性能保持稳定

#### TC-007: 内存泄漏测试

**用途**: 检测系统是否存在内存泄漏

**测试参数**:
- `iterations`: 迭代次数（默认1000）
- `memory_threshold`: 内存阈值（MB，默认100）
- `check_interval`: 检查间隔（次，默认10）

```python
test_case = suite.get_test_case("TC-007")
result = runner.run_benchmark(test_case)
```

**预期结果**:
- 内存使用保持稳定
- 无明显内存泄漏
- 内存回收正常

### 回归测试 (TC-008)

#### TC-008: 性能回归测试

**用途**: 对比历史性能数据，检测性能回归

**测试参数**:
- `baseline_path`: 基线数据路径
- `tolerance`: 性能下降容忍度（%，默认5）
- `metrics`: 比较的指标列表

```python
test_case = suite.get_test_case("TC-008")
test_case.parameters.update({
    "baseline_path": "data/baseline.json",
    "tolerance": 10  # 容忍10%的性能下降
})
result = runner.run_benchmark(test_case)
```

**预期结果**:
- 性能与基线对比
- 识别性能回归问题
- 生成对比报告

### 自定义测试用例

#### 创建自定义测试用例

```python
from npu_converter.performance import TestCase

# 定义测试函数
def my_custom_test_function(config, metrics_collector):
    """自定义测试函数"""
    start_time = time.time()

    # 执行您的测试逻辑
    # 例如：运行模型转换

    # 采集指标
    metrics_collector.record_metric("custom_metric", value)

    end_time = time.time()
    return end_time - start_time

# 创建测试用例
custom_test = TestCase(
    test_id="TC-010",
    name="自定义性能测试",
    description="我的自定义测试用例",
    category="custom",
    test_function=my_custom_test_function,
    parameters={
        "iterations": 50,
        "custom_param": "value"
    },
    timeout=3600,
    iterations=50
)

# 添加到套件
suite.add_custom_test(custom_test)

# 运行测试
test_case = suite.get_test_case("TC-010")
result = runner.run_benchmark(test_case)
```

#### 测试用例模板

```python
import time
from npu_converter.performance import TestCase, TestResult

def test_template(config, metrics_collector, **kwargs):
    """
    自定义测试函数模板

    参数:
        config: 测试配置
        metrics_collector: 指标采集器
        **kwargs: 其他参数

    返回:
        float: 测试持续时间
    """
    start_time = time.time()

    # 1. 初始化
    # ...

    # 2. 执行测试逻辑
    for iteration in range(config.get("iterations", 100)):
        # 执行测试步骤

        # 记录指标
        metrics_collector.record_metric("iteration", iteration)

        # 检查是否需要停止
        if config.get("early_stop", False):
            break

    # 3. 清理
    # ...

    end_time = time.time()
    return end_time - start_time
```

---

## 报告和可视化

### 报告类型

#### 1. 汇总报告 (Summary Report)

包含关键性能指标的汇总信息。

```python
# 生成汇总报告
summary = generator.generate_summary_report(analysis)

# 报告内容
print(f"汇总报告:")
print(f"  测试日期: {summary.test_date}")
print(f"  总测试数: {summary.total_tests}")
print(f"  成功测试: {summary.passed_tests}")
print(f"  失败测试: {summary.failed_tests}")
print(f"  成功率: {summary.success_rate:.2%}")
print(f"  平均耗时: {summary.avg_duration:.2f}秒")
print(f"  最短耗时: {summary.min_duration:.2f}秒")
print(f"  最长耗时: {summary.max_duration:.2f}秒")
```

#### 2. 详细报告 (Detailed Report)

包含每个测试用例的详细信息。

```python
# 生成详细报告
detailed = generator.generate_detailed_report(analysis)

# 打印每个测试的结果
for test_result in detailed.test_results:
    print(f"\n测试: {test_result.test_id}")
    print(f"  状态: {test_result.status}")
    print(f"  耗时: {test_result.duration:.2f}秒")
    print(f"  CPU使用率: {test_result.metrics.cpu_usage:.2f}%")
    print(f"  内存使用: {test_result.metrics.memory_usage:.2f}MB")
    if test_result.error_message:
        print(f"  错误: {test_result.error_message}")
```

#### 3. 对比报告 (Comparison Report)

对比两个测试结果或多个版本的性能。

```python
# 生成对比报告
comparison = analyzer.compare_benchmarks(
    baseline_results,
    current_results
)

comparison_report = generator.generate_comparison_report(comparison)
generator.export_report(comparison_report, "html", "reports/comparison.html")

# 打印对比结果
print(f"性能对比:")
print(f"  基线版本: {comparison.baseline_version}")
print(f"  当前版本: {comparison.current_version}")
print(f"  总体变化: {comparison.overall_change:+.2f}%")
for metric, change in comparison.metric_changes.items():
    status = "↑" if change > 0 else "↓" if change < 0 else "="
    print(f"  {metric}: {status} {abs(change):.2f}%")
```

### 报告格式

#### HTML报告

```python
# 生成HTML报告（交互式）
generator.generate_html_report(
    analysis,
    "reports/benchmark_report.html",
    include_charts=True,
    theme="light"  # 或 "dark"
)

print("HTML报告已生成: reports/benchmark_report.html")
```

**HTML报告特性**:
- ✅ 交互式图表
- ✅ 可折叠的章节
- ✅ 数据表格排序
- ✅ 响应式设计
- ✅ 支持打印

#### PDF报告

```python
# 生成PDF报告
generator.export_report(
    summary,
    "pdf",
    "reports/benchmark_report.pdf"
)

print("PDF报告已生成: reports/benchmark_report.pdf")
```

**PDF报告特性**:
- ✅ 适合打印
- ✅ 包含目录
- ✅ 图表清晰
- ✅ 专业排版

#### JSON报告

```python
# 生成JSON报告
generator.export_report(
    analysis,
    "json",
    "reports/benchmark_data.json"
)

print("JSON报告已生成: reports/benchmark_data.json")
```

**JSON报告特性**:
- ✅ 机器可读
- ✅ 易于编程处理
- ✅ 可导入其他系统
- ✅ 包含所有数据

### 可视化图表

#### 1. 时间序列图

显示性能指标随时间的变化趋势。

```python
# 生成时间序列图
viz.create_time_series_chart(
    metrics_history,
    "charts/time_series.png",
    metrics=["cpu_usage", "memory_usage", "gpu_usage"],
    title="系统性能指标趋势"
)

print("时间序列图已生成: charts/time_series.png")
```

#### 2. 对比图

对比两个测试结果的性能差异。

```python
# 生成对比图
viz.create_comparison_chart(
    baseline_results,
    current_results,
    "charts/comparison.png",
    metrics=["duration", "cpu_usage", "memory_usage"],
    title="性能对比分析"
)

print("对比图已生成: charts/comparison.png")
```

#### 3. 分布图

显示性能指标的分布情况。

```python
# 生成分布图
viz.create_distribution_chart(
    duration_values,
    "charts/distribution.png",
    metric="duration",
    bins=20,
    title="耗时分布直方图"
)

print("分布图已生成: charts/distribution.png")
```

#### 4. 热力图

显示不同测试场景下的性能表现。

```python
# 生成热力图
viz.create_heatmap(
    performance_matrix,
    "charts/heatmap.png",
    x_labels=test_names,
    y_labels=metric_names,
    title="性能指标热力图"
)

print("热力图已生成: charts/heatmap.png")
```

#### 5. 仪表盘

创建交互式性能仪表盘。

```python
# 生成仪表盘
viz.create_dashboard(
    analysis,
    "dashboard.html",
    title="XLeRobot性能仪表盘",
    refresh_interval=5  # 每5秒自动刷新
)

print("仪表盘已生成: dashboard.html")
```

**仪表盘特性**:
- ✅ 实时数据更新
- ✅ 可交互图表
- ✅ 多页面导航
- ✅ 告警显示
- ✅ 全屏模式

### 自定义报告

#### 创建自定义报告模板

```python
from jinja2 import Template

# 定义自定义模板
template_content = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .header { background-color: #4CAF50; color: white; padding: 20px; }
        .metric { margin: 10px 0; padding: 10px; background-color: #f0f0f0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ title }}</h1>
        <p>生成时间: {{ timestamp }}</p>
    </div>

    <h2>关键指标</h2>
    {% for metric in metrics %}
    <div class="metric">
        <strong>{{ metric.name }}:</strong> {{ metric.value }} {{ metric.unit }}
    </div>
    {% endfor %}

    <h2>测试结果</h2>
    <table border="1">
        <tr>
            <th>测试用例</th>
            <th>状态</th>
            <th>耗时</th>
        </tr>
        {% for result in results %}
        <tr>
            <td>{{ result.test_id }}</td>
            <td>{{ result.status }}</td>
            <td>{{ "%.2f"|format(result.duration) }}s</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

# 创建模板
template = Template(template_content)

# 准备数据
data = {
    "title": "XLeRobot性能测试报告",
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "metrics": [
        {"name": "平均CPU使用率", "value": "45.6%", "unit": ""},
        {"name": "平均内存使用", "value": "1024", "unit": "MB"},
        {"name": "GPU使用率", "value": "67.8%", "unit": ""},
    ],
    "results": [
        {"test_id": "TC-001", "status": "success", "duration": 1.23},
        {"test_id": "TC-002", "status": "success", "duration": 1.45},
        {"test_id": "TC-003", "status": "success", "duration": 1.38},
    ]
}

# 渲染报告
html_content = template.render(**data)

# 保存报告
with open("reports/custom_report.html", "w") as f:
    f.write(html_content)

print("自定义报告已生成: reports/custom_report.html")
```

---

## 告警设置

### 告警系统概述

告警系统帮助您及时发现性能问题，包括：

- ⚠️ **性能异常**：CPU、内存、GPU使用率过高
- 📉 **性能下降**：转换速率降低
- ⏱️ **响应超时**：转换时间过长
- 💥 **错误率高**：转换失败率过高
- 🔥 **资源耗尽**：系统资源不足

### 预定义告警规则

系统提供一系列预定义的告警规则：

#### 1. CPU告警

```python
from npu_converter.performance import AlertRule

# 高CPU使用率告警
high_cpu = AlertRule(
    name="高CPU使用率",
    metric="cpu_usage",
    threshold=80.0,
    comparison=">",
    severity="high",
    duration=300,  # 持续5分钟才告警
    message="CPU使用率已超过80%，请检查系统负载"
)

alerts.add_rule(high_cpu)

# 极高CPU使用率告警
critical_cpu = AlertRule(
    name="极高CPU使用率",
    metric="cpu_usage",
    threshold=95.0,
    comparison=">",
    severity="critical",
    duration=60,  # 持续1分钟就告警
    message="CPU使用率已超过95%，系统可能过载！"
)

alerts.add_rule(critical_cpu)
```

#### 2. 内存告警

```python
# 高内存使用告警
high_memory = AlertRule(
    name="高内存使用率",
    metric="memory_usage",
    threshold=4096.0,  # 4GB
    comparison=">",
    severity="high",
    message="内存使用已超过4GB"
)

alerts.add_rule(high_memory)

# 内存泄漏告警
memory_leak = AlertRule(
    name="内存泄漏",
    metric="memory_trend",
    threshold=100.0,  # 100MB/小时
    comparison=">",
    severity="medium",
    message="检测到可能的内存泄漏"
)

alerts.add_rule(memory_leak)
```

#### 3. 转换性能告警

```python
# 转换速率过低
low_throughput = AlertRule(
    name="转换速率过低",
    metric="conversion_rate",
    threshold=5.0,  # 5模型/分钟
    comparison="<",
    severity="medium",
    message="转换速率低于预期，请检查系统性能"
)

alerts.add_rule(low_throughput)

# 响应时间过长
slow_response = AlertRule(
    name="响应时间过长",
    metric="response_time",
    threshold=60.0,  # 60秒
    comparison=">",
    severity="high",
    message="平均响应时间超过60秒"
)

alerts.add_rule(slow_response)
```

#### 4. 错误率告警

```python
# 转换失败率高
high_error_rate = AlertRule(
    name="转换失败率高",
    metric="error_rate",
    threshold=5.0,  # 5%
    comparison=">",
    severity="critical",
    message="转换失败率超过5%，请检查系统状态"
)

alerts.add_rule(high_error_rate)

# 连续错误告警
consecutive_errors = AlertRule(
    name="连续错误",
    metric="consecutive_errors",
    threshold=10,  # 连续10次错误
    comparison=">=",
    severity="critical",
    message="检测到连续错误，系统可能存在严重问题"
)

alerts.add_rule(consecutive_errors)
```

### 自定义告警规则

#### 创建自定义告警

```python
# 自定义告警：GPU显存使用过高
gpu_memory_alert = AlertRule(
    name="GPU显存不足",
    metric="gpu_memory_usage",
    threshold=8.0,  # 8GB
    comparison=">",
    severity="high",
    duration=120,  # 持续2分钟
    message="GPU显存使用已超过8GB，可能影响性能",
    action="reduce_concurrent_models"  # 建议操作
)

alerts.add_rule(gpu_memory_alert)
```

#### 告警规则参数说明

```python
rule = AlertRule(
    name="告警名称",              # 告警名称
    metric="指标名称",             # 要监控的指标
    threshold=阈值,               # 触发告警的阈值
    comparison=">",               # 比较操作符
                                 #   ">"  大于
                                 #   "<"  小于
                                 #   ">=" 大于等于
                                 #   "<=" 小于等于
                                 #   "==" 等于
                                 #   "!=" 不等于
    severity="medium",            # 严重程度
                                 #   "low"      低
                                 #   "medium"   中
                                 #   "high"     高
                                 #   "critical" 严重
    duration=60,                  # 持续时间（秒）
                                 # 指标超过阈值持续多长时间才告警
    message="告警消息",             # 告警显示的消息
    action="建议操作",             # 建议的处理操作
    enabled=True                  # 是否启用
)
```

### 告警事件处理

#### 订阅告警事件

```python
# 定义告警处理函数
def handle_alert(alert):
    """处理告警事件"""
    print(f"\n🚨 告警触发!")
    print(f"   告警ID: {alert.alert_id}")
    print(f"   名称: {alert.title}")
    print(f"   严重程度: {alert.severity}")
    print(f"   消息: {alert.message}")
    print(f"   指标: {alert.metric}")
    print(f"   当前值: {alert.value:.2f}")
    print(f"   阈值: {alert.threshold:.2f}")
    print(f"   时间: {alert.created_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # 根据严重程度采取不同措施
    if alert.severity == "critical":
        print("   ⚠️ 严重告警：立即检查系统状态！")
    elif alert.severity == "high":
        print("   ⚠️ 高级告警：建议尽快处理")
    elif alert.severity == "medium":
        print("   ⚠️ 中级告警：稍后处理")
    else:
        print("   ⚠️ 低级告警：记录并监控")

# 订阅告警事件
alerts.subscribe(handle_alert)
```

#### 告警状态管理

```python
# 获取所有活跃告警
active_alerts = alerts.get_active_alerts()
print(f"当前活跃告警数量: {len(active_alerts)}")

# 确认告警
alert_id = "alert-123"
alerts.acknowledge_alert(alert_id)
print(f"告警 {alert_id} 已确认")

# 解决告警
alerts.resolve_alert(alert_id)
print(f"告警 {alert_id} 已解决")

# 获取告警历史
alert_history = alerts.get_alert_history(days=7)
print(f"过去7天的告警数量: {len(alert_history)}")
```

### 告警通知

#### 邮件通知

```python
import smtplib
from email.mime.text import MimeText

def send_email_alert(alert, smtp_config):
    """发送邮件告警"""
    subject = f"[{alert.severity.upper()}] XLeRobot性能告警: {alert.title}"
    body = f"""
告警详情:
名称: {alert.title}
严重程度: {alert.severity}
消息: {alert.message}
指标: {alert.metric}
当前值: {alert.value:.2f}
阈值: {alert.threshold:.2f}
时间: {alert.created_time}
"""

    msg = MimeText(body)
    msg['Subject'] = subject
    msg['From'] = smtp_config['from']
    msg['To'] = smtp_config['to']

    with smtplib.SMTP(smtp_config['host'], smtp_config['port']) as server:
        server.starttls()
        server.login(smtp_config['username'], smtp_config['password'])
        server.send_message(msg)

# 配置邮件
smtp_config = {
    'host': 'smtp.example.com',
    'port': 587,
    'username': 'alert@example.com',
    'password': 'password',
    'from': 'alert@example.com',
    'to': 'admin@example.com'
}

# 在告警处理函数中发送邮件
def handle_alert_with_email(alert):
    if alert.severity in ['high', 'critical']:
        send_email_alert(alert, smtp_config)
        print(f"邮件告警已发送到: {smtp_config['to']}")

alerts.subscribe(handle_alert_with_email)
```

#### Slack通知

```python
import requests

def send_slack_alert(alert, webhook_url):
    """发送Slack告警"""
    color = {
        'low': 'good',
        'medium': 'warning',
        'high': 'danger',
        'critical': 'danger'
    }.get(alert.severity, 'warning')

    payload = {
        "text": f"🚨 XLeRobot性能告警",
        "attachments": [
            {
                "color": color,
                "fields": [
                    {"title": "告警名称", "value": alert.title, "short": True},
                    {"title": "严重程度", "value": alert.severity, "short": True},
                    {"title": "指标", "value": alert.metric, "short": True},
                    {"title": "当前值", "value": f"{alert.value:.2f}", "short": True},
                    {"title": "阈值", "value": f"{alert.threshold:.2f}", "short": True},
                    {"title": "时间", "value": alert.created_time.strftime('%Y-%m-%d %H:%M:%S'), "short": True}
                ]
            }
        ]
    }

    response = requests.post(webhook_url, json=payload)
    return response.status_code == 200

# 配置Slack Webhook
slack_webhook = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"

# 在告警处理函数中发送Slack通知
def handle_alert_with_slack(alert):
    send_slack_alert(alert, slack_webhook)
    print(f"Slack告警已发送")

alerts.subscribe(handle_alert_with_slack)
```

### 告警配置最佳实践

#### 1. 设置合理的阈值

```python
# ❌ 错误：阈值过于严格
AlertRule(
    name="CPU告警",
    metric="cpu_usage",
    threshold=70.0,  # 太严格，会产生大量告警
    comparison=">",
    severity="high"
)

# ✅ 正确：阈值合理
AlertRule(
    name="CPU告警",
    metric="cpu_usage",
    threshold=85.0,  # 合理阈值
    comparison=">",
    severity="high"
)
```

#### 2. 设置持续时间

```python
# ❌ 错误：没有持续时间，可能误报
AlertRule(
    name="CPU告警",
    metric="cpu_usage",
    threshold=80.0,
    comparison=">",
    severity="high"
    # 没有duration参数
)

# ✅ 正确：设置持续时间，避免误报
AlertRule(
    name="CPU告警",
    metric="cpu_usage",
    threshold=80.0,
    comparison=">",
    severity="high",
    duration=300  # 持续5分钟才告警
)
```

#### 3. 分级告警

```python
# 为同一个指标设置多个告警级别
alerts.add_rule(AlertRule(
    name="CPU告警-警告",
    metric="cpu_usage",
    threshold=75.0,
    comparison=">",
    severity="medium",
    duration=600
))

alerts.add_rule(AlertRule(
    name="CPU告警-危险",
    metric="cpu_usage",
    threshold=85.0,
    comparison=">",
    severity="high",
    duration=300
))

alerts.add_rule(AlertRule(
    name="CPU告警-严重",
    metric="cpu_usage",
    threshold=95.0,
    comparison=">",
    severity="critical",
    duration=60
))
```

#### 4. 告警抑制

```python
# 在维护期间抑制告警
def suppress_alerts_during_maintenance():
    """维护期间抑制告警"""
    alerts.suppress_all()
    print("所有告警已抑制")

def resume_alerts():
    """恢复告警"""
    alerts.resume_all()
    print("告警已恢复")
```

---

## 最佳实践

### 1. 测试设计

#### 选择合适的测试用例

```python
# 新功能测试
# 使用单模型测试（TC-001 to TC-003）进行基础功能验证

# 性能验证
# 使用压力测试（TC-005）验证峰值性能

# 稳定性验证
# 使用长期稳定性测试（TC-006）验证系统稳定性

# 回归测试
# 使用性能回归测试（TC-008）验证版本间性能差异
```

#### 测试参数优化

```python
# 根据系统性能调整参数
config = BenchmarkConfig(
    max_concurrent=min(os.cpu_count(), 20),  # 不超过CPU核心数
    test_timeout=3600,  # 1小时超时
    retry_count=3       # 重试3次
)

# 预热测试
test_case = suite.get_test_case("TC-001")
test_case.parameters["warmup_iterations"] = 20  # 增加预热迭代

# 多次迭代
test_case.parameters["iterations"] = 100  # 增加迭代次数以获得更准确的结果
```

### 2. 资源管理

#### 控制资源使用

```python
# 限制并发数
benchmark_config = BenchmarkConfig(
    max_concurrent=10,
    test_timeout=3600
)

# 启用测试后清理
benchmark_config = BenchmarkConfig(
    cleanup_after_test=True,  # 测试后自动清理临时文件
    save_raw_data=False       # 不保存原始数据以节省空间
)

# 使用SQLite减少内存占用
metrics_config = MetricsConfig(
    storage_type="sqlite",
    storage_path="data/metrics.db",
    collection_interval=2,  # 减少采集频率
    buffer_size=500         # 减小缓冲区
)
```

#### 监控系统资源

```python
# 在测试前检查系统资源
import psutil

def check_system_resources():
    """检查系统资源"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    print(f"CPU使用率: {cpu_percent}%")
    print(f"内存使用率: {memory.percent}% ({memory.used/1024/1024/1024:.1f}GB / {memory.total/1024/1024/1024:.1f}GB)")
    print(f"磁盘使用率: {disk.percent}% ({disk.used/1024/1024/1024:.1f}GB / {disk.total/1024/1024/1024:.1f}GB)")

    # 检查是否满足测试要求
    if cpu_percent > 90:
        print("⚠️ CPU使用率过高，建议等待")
        return False
    if memory.percent > 90:
        print("⚠️ 内存使用率过高，建议等待")
        return False
    if disk.percent > 90:
        print("⚠️ 磁盘空间不足，建议清理")
        return False

    return True

# 在运行测试前检查
if check_system_resources():
    print("✅ 系统资源充足，可以开始测试")
    result = runner.run_benchmark(test_case)
else:
    print("❌ 系统资源不足，测试取消")
```

### 3. 结果分析

#### 多角度分析

```python
# 统计分析
analysis = analyzer.analyze_results(results)
print(f"平均性能: {analysis.avg_duration:.2f}秒")
print(f"P50性能: {analysis.p50_duration:.2f}秒")
print(f"P95性能: {analysis.p95_duration:.2f}秒")
print(f"P99性能: {analysis.p99_duration:.2f}秒")
print(f"性能稳定性: {(1 - analysis.std_duration/analysis.avg_duration)*100:.2f}%")

# 趋势分析
trend = analyzer.analyze_trend(metrics_history)
print(f"性能趋势: {trend.direction}")
print(f"变化率: {trend.change_rate:.2f}%")

# 异常检测
anomalies = analyzer.detect_anomalies(metrics_history)
print(f"检测到 {len(anomalies)} 个性能异常")
```

#### 性能对比

```python
# 版本对比
def compare_versions(version1_results, version2_results):
    """对比两个版本的性能"""
    comparison = analyzer.compare_benchmarks(
        version1_results,
        version2_results
    )

    print(f"版本性能对比:")
    print(f"  版本1平均耗时: {comparison.v1_avg_duration:.2f}秒")
    print(f"  版本2平均耗时: {comparison.v2_avg_duration:.2f}秒")
    print(f"  性能变化: {comparison.percentage_change:+.2f}%")

    if comparison.is_regression:
        print("  ⚠️ 检测到性能回归")
        print(f"  受影响指标: {', '.join(comparison.regressed_metrics)}")
    elif comparison.is_improvement:
        print("  ✅ 性能有所提升")
    else:
        print("  ➡️ 性能基本无变化")

# 基线管理
def set_baseline(results, version_name):
    """设置性能基线"""
    baseline_data = {
        "version": version_name,
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    with open(f"baseline_{version_name}.json", "w") as f:
        json.dump(baseline_data, f, indent=2, default=str)

    print(f"✅ 已设置 {version_name} 为性能基线")

# 加载基线
def load_baseline(version_name):
    """加载性能基线"""
    try:
        with open(f"baseline_{version_name}.json", "r") as f:
            baseline_data = json.load(f)
        return baseline_data["results"]
    except FileNotFoundError:
        print(f"❌ 基线文件不存在: baseline_{version_name}.json")
        return None
```

### 4. 自动化测试

#### 批量测试脚本

```python
#!/usr/bin/env python3
"""
性能基准测试批量执行脚本
"""

import os
import json
from datetime import datetime

def run_full_benchmark_suite():
    """运行完整测试套件"""
    print("=" * 60)
    print("XLeRobot性能基准测试")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 创建配置
    config = BenchmarkConfig(
        max_concurrent=10,
        test_timeout=3600,
        output_dir=f"reports/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )

    # 创建组件
    runner = BenchmarkRunner(config)
    suite = BenchmarkSuite()
    collector = MetricsCollector(MetricsConfig())
    analyzer = PerformanceAnalyzer()
    generator = ReportGenerator(ReportConfig(include_charts=True))

    # 获取所有测试用例
    test_cases = suite.list_test_cases()

    print(f"\n共 {len(test_cases)} 个测试用例")
    print("-" * 60)

    results = []
    for i, test_case in enumerate(test_cases, 1):
        print(f"[{i}/{len(test_cases)}] 运行测试: {test_case.test_id}")

        try:
            # 启动指标采集
            collector.start_collection(test_case.test_id)

            # 运行测试
            result = runner.run_benchmark(test_case)

            # 停止指标采集
            collector.stop_collection(test_case.test_id)

            results.append(result)
            status_icon = "✅" if result.status == "success" else "❌"
            print(f"  {status_icon} 结果: {result.status}, 耗时: {result.duration:.2f}秒")

        except Exception as e:
            print(f"  ❌ 测试失败: {e}")

    # 分析结果
    print("\n" + "-" * 60)
    print("测试结果分析")
    print("-" * 60)

    if results:
        analysis = analyzer.analyze_results(results)

        print(f"总测试数: {analysis.total_tests}")
        print(f"成功: {analysis.passed_tests}")
        print(f"失败: {analysis.failed_tests}")
        print(f"成功率: {analysis.success_rate:.2%}")
        print(f"平均耗时: {analysis.avg_duration:.2f}秒")
        print(f"P95耗时: {analysis.p95_duration:.2f}秒")

        # 生成报告
        summary = generator.generate_summary_report(analysis)
        report_dir = config.output_dir

        generator.export_report(summary, "html", f"{report_dir}/summary.html")
        generator.export_report(summary, "json", f"{report_dir}/summary.json")

        # 保存结果
        with open(f"{report_dir}/results.json", "w") as f:
            json.dump([r.__dict__ for r in results], f, default=str, indent=2)

        print(f"\n📊 报告已生成: {report_dir}/")
        print(f"  - HTML报告: {report_dir}/summary.html")
        print(f"  - JSON数据: {report_dir}/summary.json")

    print("\n" + "=" * 60)
    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    run_full_benchmark_suite()
```

#### 定时任务

```python
import schedule
import time

def scheduled_benchmark():
    """定时执行性能测试"""
    print("\n" + "="*60)
    print("定时性能测试开始")
    print("="*60)

    test_suite = suite.create_test_suite(["TC-001", "TC-002", "TC-003"])
    results = runner.run_suite(test_suite)

    analysis = analyzer.analyze_results(results)
    print(f"测试完成: {analysis.total_tests} 个测试, {analysis.success_rate:.2%} 成功率")

# 设置定时任务
schedule.every().day.at("02:00").do(scheduled_benchmark)  # 每天凌晨2点
schedule.every().monday.at("09:00").do(scheduled_benchmark)  # 每周一上午9点

print("定时任务已设置:")
print("  - 每天02:00执行")
print("  - 每周一09:00执行")

# 运行调度器
while True:
    schedule.run_pending()
    time.sleep(60)  # 每分钟检查一次
```

### 5. CI/CD集成

#### GitHub Actions集成

参见[CI/CD配置](../api/performance-benchmark-api-reference.md#cicd-集成)

#### Jenkins集成

```groovy
pipeline {
    agent any

    stages {
        stage('Performance Test') {
            steps {
                sh '''
                    python3 -m pytest tests/performance/ \
                        --benchmark-only \
                        --benchmark-json=benchmark.json \
                        --benchmark-html=report.html
                '''
            }
            post {
                always {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: '.',
                        reportFiles: 'report.html',
                        reportName: 'Performance Benchmark Report'
                    ])

                    archiveArtifacts artifacts: 'benchmark.json', fingerprint: true
                }
            }
        }
    }
}
```

---

## 常见问题

### Q1: 如何选择合适的测试用例？

**A**: 根据测试目的选择：

- **功能验证**: 使用TC-001到TC-003（单模型测试）
- **性能验证**: 使用TC-005（压力测试）
- **稳定性验证**: 使用TC-006（长期稳定性）和TC-007（内存泄漏）
- **并发测试**: 使用TC-004（多模型并发）
- **回归测试**: 使用TC-008（性能回归）

### Q2: 测试结果波动很大怎么办？

**A**: 建议采用以下方法：

1. **增加预热迭代**:
```python
test_case.parameters["warmup_iterations"] = 20
```

2. **增加测试迭代**:
```python
test_case.parameters["iterations"] = 100
```

3. **多次测试取平均值**:
```python
results = []
for _ in range(3):  # 运行3次
    result = runner.run_benchmark(test_case)
    results.append(result)

avg_duration = sum(r.duration for r in results) / len(results)
```

4. **检查系统资源**:
```python
# 确保测试期间系统负载稳定
check_system_resources()
```

### Q3: 如何设置合适的并发数？

**A**: 并发数取决于系统配置：

```python
# 根据CPU核心数设置
import os
cpu_count = os.cpu_count()
max_concurrent = min(cpu_count, 20)

# GPU并发数
gpu_count = torch.cuda.device_count() if torch.cuda.is_available() else 0
max_concurrent = min(max_concurrent, gpu_count * 2)

config = BenchmarkConfig(max_concurrent=max_concurrent)
```

**建议值**:
- 单模型: `max_concurrent = 1`
- 轻量模型: `max_concurrent = CPU核心数`
- 重量模型: `max_concurrent = CPU核心数 / 2`

### Q4: 测试运行时间太长怎么优化？

**A**: 可以通过以下方式优化：

1. **减少迭代次数**:
```python
test_case.parameters["iterations"] = 50  # 从100减少到50
```

2. **缩短测试超时**:
```python
config = BenchmarkConfig(test_timeout=1800)  # 30分钟
```

3. **使用快速模式**:
```python
test_case.parameters["quick_mode"] = True  # 如果测试支持
```

4. **并行执行**:
```python
results = runner.run_suite(test_suite, parallel=True, max_workers=10)
```

### Q5: 如何处理测试失败？

**A**: 建议采用以下策略：

1. **启用重试**:
```python
config = BenchmarkConfig(
    retry_count=3,      # 重试3次
    retry_delay=5       # 重试间隔5秒
)
```

2. **检查错误信息**:
```python
result = runner.run_benchmark(test_case)
if result.status == "failure":
    print(f"错误信息: {result.error_message}")
```

3. **分析错误原因**:
```python
# 常见错误类型：
# - TimeoutError: 测试超时
# - MemoryError: 内存不足
# - GPUError: GPU相关错误
# - ModelError: 模型加载错误
```

4. **调整测试参数**:
```python
# 如果是资源不足
test_case.parameters["model_count"] = 5  # 减少并发数

# 如果是超时
test_case.parameters["iterations"] = 50  # 减少迭代次数
```

### Q6: 如何保存和比较历史测试结果？

**A**: 使用以下方法：

1. **保存测试结果**:
```python
# 保存为JSON
with open("results_20251029.json", "w") as f:
    json.dump(results, f, default=str, indent=2)

# 保存为数据库
import sqlite3
conn = sqlite3.connect("benchmark.db")
# 保存到数据库的逻辑
```

2. **加载历史结果**:
```python
# 从文件加载
with open("results_20251029.json", "r") as f:
    historical_results = json.load(f)
```

3. **对比分析**:
```python
comparison = analyzer.compare_benchmarks(
    historical_results,
    current_results
)
```

### Q7: 告警规则不工作怎么办？

**A**: 检查以下问题：

1. **验证指标名称**:
```python
# 确保metric名称正确
rule = AlertRule(
    metric="cpu_usage",  # 而不是"cpu"或"CPU"
    ...
)
```

2. **检查告警是否启用**:
```python
rule.enabled = True  # 确保告警启用
```

3. **检查阈值设置**:
```python
# 确保阈值合理
rule = AlertRule(
    metric="cpu_usage",
    threshold=80.0,  # 确保不超过100
    ...
)
```

4. **添加调试信息**:
```python
def debug_alert(alert):
    print(f"告警触发: {alert.title}")
    print(f"指标: {alert.metric}")
    print(f"值: {alert.value}")
    print(f"阈值: {alert.threshold}")

alerts.subscribe(debug_alert)
```

### Q8: 内存使用持续增长怎么办？

**A**: 建议采用以下方法：

1. **启用自动清理**:
```python
config = BenchmarkConfig(
    cleanup_after_test=True,  # 测试后清理
    save_raw_data=False       # 不保存原始数据
)
```

2. **定期清理历史数据**:
```python
collector.cleanup_old_data(days=7)  # 清理7天前的数据
```

3. **使用SQLite存储**:
```python
metrics_config = MetricsConfig(
    storage_type="sqlite",  # 使用SQLite而不是内存
    storage_path="data/metrics.db"
)
```

4. **运行内存泄漏测试**:
```python
test_case = suite.get_test_case("TC-007")
result = runner.run_benchmark(test_case)
if result.memory_leak_detected:
    print("⚠️ 检测到内存泄漏")
```

---

## 故障排除

### 常见错误和解决方案

#### 错误1: `ModuleNotFoundError: No module named 'npu_converter.performance'`

**原因**: 模块未安装或路径错误

**解决方案**:
```bash
# 1. 安装项目
pip install -e .

# 2. 或者添加到PYTHONPATH
export PYTHONPATH=$PYTHONPATH:/path/to/xlerobot/src

# 3. 验证安装
python -c "import npu_converter.performance; print('OK')"
```

#### 错误2: `BenchmarkError: Test execution failed`

**原因**: 测试执行过程中出现错误

**解决方案**:
```python
try:
    result = runner.run_benchmark(test_case)
except BenchmarkError as e:
    print(f"错误代码: {e.error_code}")
    print(f"错误消息: {e.message}")
    print(f"是否可重试: {e.retryable}")

    if e.error_code == "TIMEOUT":
        print("解决方案: 增加超时时间或减少迭代次数")
    elif e.error_code == "MEMORY_ERROR":
        print("解决方案: 减少并发数或使用更大的内存")
    elif e.error_code == "GPU_ERROR":
        print("解决方案: 检查GPU状态或禁用GPU监控")
```

#### 错误3: `MetricsError: Failed to collect GPU metrics`

**原因**: GPU监控依赖未安装或GPU不可用

**解决方案**:
```python
# 方案1: 禁用GPU监控
metrics_config = MetricsConfig(enable_gpu_monitoring=False)

# 方案2: 安装GPU监控依赖
# pip install GPUtil nvidia-ml-py

# 方案3: 检查GPU状态
import GPUtil
gpus = GPUtil.getGPUs()
print(f"检测到 {len(gpus)} 个GPU")
```

#### 错误4: `TimeoutError: Test timed out`

**原因**: 测试执行时间超过超时限制

**解决方案**:
```python
# 方案1: 增加超时时间
result = runner.run_benchmark(test_case, timeout=7200)  # 2小时

# 方案2: 减少测试负载
test_case.parameters["iterations"] = 50  # 减少迭代次数

# 方案3: 优化测试逻辑
# 检查测试函数是否有死循环或阻塞操作
```

#### 错误5: 报告生成失败

**原因**: 缺少依赖或权限问题

**解决方案**:
```python
# 方案1: 安装报告生成依赖
# pip install matplotlib plotly jinja2 weasyprint

# 方案2: 检查输出目录权限
import os
output_dir = "reports"
if not os.path.exists(output_dir):
    os.makedirs(output_dir, exist_ok=True)

# 方案3: 使用绝对路径
output_path = os.path.abspath("reports/summary.html")
```

#### 错误6: 指标采集数据异常

**原因**: 指标采集频率过高或数据格式错误

**解决方案**:
```python
# 方案1: 降低采集频率
metrics_config = MetricsConfig(
    collection_interval=5  # 从1秒增加到5秒
)

# 方案2: 减小缓冲区大小
metrics_config = MetricsConfig(
    buffer_size=500  # 减少缓冲区
)

# 方案3: 检查数据格式
history = collector.get_metrics_history("test-001")
for metric in history[:5]:  # 只检查前5条数据
    print(f"时间戳: {metric.timestamp}")
    print(f"CPU: {metric.cpu_usage}")
```

### 调试技巧

#### 1. 启用详细日志

```python
import logging

# 设置日志级别
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('performance_test.log'),
        logging.StreamHandler()
    ]
)

# 创建组件（会自动记录详细日志）
runner = BenchmarkRunner(config)
collector = MetricsCollector(metrics_config)
```

#### 2. 使用调试模式

```python
# 启用调试模式
config = BenchmarkConfig(
    debug_mode=True,        # 启用调试
    save_raw_data=True,     # 保存原始数据
    output_dir="debug_reports"
)

# 运行测试
result = runner.run_benchmark(test_case)

# 检查调试输出
import os
print("调试文件:")
for file in os.listdir(config.output_dir):
    print(f"  - {file}")
```

#### 3. 逐步测试

```python
# 测试单个组件
print("测试1: 验证配置")
config = BenchmarkConfig()
print("✅ 配置创建成功")

print("\n测试2: 验证组件创建")
runner = BenchmarkRunner(config)
collector = MetricsCollector(MetricsConfig())
print("✅ 组件创建成功")

print("\n测试3: 验证测试用例")
suite = BenchmarkSuite()
test_case = suite.get_test_case("TC-001")
print("✅ 测试用例获取成功")

print("\n测试4: 运行测试")
result = runner.run_benchmark(test_case)
print(f"✅ 测试运行成功: {result.status}")
```

#### 4. 检查系统信息

```python
def print_system_info():
    """打印系统信息"""
    import platform
    import psutil
    import sys

    print("=" * 60)
    print("系统信息")
    print("=" * 60)
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {sys.version}")
    print(f"CPU核心数: {psutil.cpu_count()}")
    print(f"内存: {psutil.virtual_memory().total / 1024 / 1024 / 1024:.1f} GB")
    print(f"可用内存: {psutil.virtual_memory().available / 1024 / 1024 / 1024:.1f} GB")

    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        print(f"GPU数量: {len(gpus)}")
        for i, gpu in enumerate(gpus):
            print(f"  GPU {i}: {gpu.name}, {gpu.memoryTotal}MB")
    except ImportError:
        print("GPU信息: 未安装GPUtil")

    print("=" * 60)

print_system_info()
```

### 性能问题诊断

#### 1. CPU性能问题

```python
# 检查CPU使用率
import psutil

# 监控CPU使用率
cpu_percent = psutil.cpu_percent(interval=1)
print(f"当前CPU使用率: {cpu_percent}%")

# 检查CPU频率
cpu_freq = psutil.cpu_freq()
if cpu_freq:
    print(f"CPU频率: {cpu_freq.current:.2f} MHz")

# 检查负载均值
load_avg = psutil.getloadavg()
print(f"系统负载: 1分钟 {load_avg[0]:.2f}, 5分钟 {load_avg[1]:.2f}, 15分钟 {load_avg[2]:.2f}")
```

#### 2. 内存问题

```python
# 检查内存使用
memory = psutil.virtual_memory()
print(f"内存总量: {memory.total / 1024 / 1024 / 1024:.2f} GB")
print(f"内存使用率: {memory.percent}%")
print(f"已用内存: {memory.used / 1024 / 1024 / 1024:.2f} GB")
print(f"可用内存: {memory.available / 1024 / 1024 / 1024:.2f} GB")

# 检查交换分区
swap = psutil.swap_memory()
print(f"交换分区使用率: {swap.percent}%")
```

#### 3. 磁盘I/O问题

```python
# 检查磁盘I/O
disk_io = psutil.disk_io_counters()
if disk_io:
    print(f"磁盘读取: {disk_io.read_bytes / 1024 / 1024:.2f} MB")
    print(f"磁盘写入: {disk_io.write_bytes / 1024 / 1024:.2f} MB")

# 检查磁盘使用
disk_usage = psutil.disk_usage('/')
print(f"磁盘总量: {disk_usage.total / 1024 / 1024 / 1024:.2f} GB")
print(f"磁盘使用: {disk_usage.used / 1024 / 1024 / 1024:.2f} GB")
print(f"磁盘剩余: {disk_usage.free / 1024 / 1024 / 1024:.2f} GB")
```

### 获取帮助

#### 1. 查看日志

```bash
# 查看性能测试日志
tail -f performance_test.log

# 查看错误日志
grep "ERROR" performance_test.log

# 查看特定测试日志
grep "TC-001" performance_test.log
```

#### 2. 社区支持

- **项目仓库**: [GitHub Repository]
- **问题反馈**: [Issues Page]
- **文档**: [Documentation]
- **邮箱**: support@example.com

#### 3. 报告问题

提交问题时，请提供以下信息：

```python
# 生成系统信息报告
import platform
import psutil
import sys

report = f"""
XLeRobot性能测试问题报告
========================

系统信息:
- 操作系统: {platform.system()} {platform.release()}
- Python版本: {sys.version}
- CPU核心数: {psutil.cpu_count()}
- 内存: {psutil.virtual_memory().total / 1024 / 1024 / 1024:.2f} GB

错误信息:
- 错误类型: <your error type>
- 错误消息: <your error message>
- 触发操作: <what you were doing>

重现步骤:
1. <step 1>
2. <step 2>
3. <step 3>

期望结果:
<what you expected>

实际结果:
<what actually happened>
"""

print(report)
```

---

## 总结

恭喜！您已经完成了XLeRobot性能基准测试系统的学习。

### 关键要点回顾

1. **快速开始**: 5分钟即可运行第一个性能测试
2. **测试用例**: 8个内置测试用例覆盖各种场景
3. **性能监控**: 实时采集CPU、内存、GPU/NPU等指标
4. **智能分析**: 自动异常检测、性能对比、优化建议
5. **灵活报告**: 支持HTML、PDF、JSON等多种格式
6. **实时告警**: 多级告警规则，及时发现问题
7. **最佳实践**: 资源管理、自动化测试、CI/CD集成

### 后续学习

- 📖 阅读[API参考文档](../api/performance-benchmark-api-reference.md)
- 🧪 尝试运行更多测试用例
- 📊 学习性能数据分析方法
- ⚙️ 配置适合您环境的告警规则
- 🚀 集成到您的CI/CD流程

### 获取支持

如有问题或建议，请：
- 查看[常见问题](#常见问题)部分
- 提交[GitHub Issue]
- 联系开发团队

祝您使用愉快！🎉

---

*本文档遵循XLeRobot项目文档标准*
*最后更新: 2025-10-29*
