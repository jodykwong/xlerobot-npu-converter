# Performance Benchmark API Reference

**版本**: v1.0
**最后更新**: 2025-10-29
**项目**: XLeRobot NPU模型转换工具

---

## 概述 (Overview)

性能基准测试API提供了完整的性能测试、监控、分析和报告功能。本文档详细介绍了所有可用的组件、类和方法。

## 目录 (Table of Contents)

1. [核心组件 (Core Components)](#核心组件-core-components)
2. [基准测试执行器 (Benchmark Runner)](#基准测试执行器-benchmark-runner)
3. [指标采集器 (Metrics Collector)](#指标采集器-metrics-collector)
4. [测试用例套件 (Benchmark Suite)](#测试用例套件-benchmark-suite)
5. [性能分析器 (Performance Analyzer)](#性能分析器-performance-analyzer)
6. [报告生成器 (Report Generator)](#报告生成器-report-generator)
7. [可视化引擎 (Visualization Engine)](#可视化引擎-visualization-engine)
8. [告警系统 (Alert System)](#告警系统-alert-system)
9. [配置类 (Configuration Classes)](#配置类-configuration-classes)
10. [数据模型 (Data Models)](#数据模型-data-models)

---

## 核心组件 (Core Components)

### 组件架构图

```
┌─────────────────────────────────────────────┐
│            Performance Benchmark             │
│                System                      │
├─────────────────────────────────────────────┤
│  1. BenchmarkRunner - 测试执行管理           │
│  2. MetricsCollector - 指标采集             │
│  3. BenchmarkSuite - 测试用例管理           │
│  4. PerformanceAnalyzer - 性能分析          │
│  5. ReportGenerator - 报告生成              │
│  6. VisualizationEngine - 可视化            │
│  7. AlertSystem - 告警管理                  │
└─────────────────────────────────────────────┘
```

### 快速开始 (Quick Start)

```python
from npu_converter.performance import (
    BenchmarkRunner,
    MetricsCollector,
    BenchmarkSuite,
    PerformanceAnalyzer,
    ReportGenerator,
    VisualizationEngine,
    AlertSystem
)

# 导入配置
from npu_converter.performance import (
    BenchmarkConfig,
    MetricsConfig,
    SuiteConfig
)

# 创建配置对象
benchmark_config = BenchmarkConfig(
    max_concurrent=10,
    test_timeout=3600,
    retry_count=3
)

metrics_config = MetricsConfig(
    collection_interval=1,
    buffer_size=1000,
    enable_gpu_monitoring=True
)

suite_config = SuiteConfig()

# 创建组件实例
runner = BenchmarkRunner(benchmark_config)
collector = MetricsCollector(metrics_config)
suite = BenchmarkSuite(suite_config)
analyzer = PerformanceAnalyzer()
generator = ReportGenerator()
visualization = VisualizationEngine()
alerts = AlertSystem()
```

---

## 基准测试执行器 (Benchmark Runner)

### 类: `BenchmarkRunner`

负责执行基准测试，管理工作流和结果。

#### 构造函数 (Constructor)

```python
from npu_converter.performance import BenchmarkRunner, BenchmarkConfig

runner = BenchmarkRunner(config: BenchmarkConfig)
```

**参数**:
- `config` (BenchmarkConfig): 基准测试配置对象

#### 主要方法 (Methods)

##### `run_benchmark(test_case, **kwargs)`

执行单个基准测试用例。

```python
test_case = suite.get_test_case("TC-001")
result = runner.run_benchmark(
    test_case,
    metrics_collector=collector,
    timeout=3600
)
```

**参数**:
- `test_case` (TestCase): 测试用例对象
- `metrics_collector` (MetricsCollector, 可选): 指标采集器实例
- `timeout` (int, 可选): 测试超时时间（秒）

**返回**: `BenchmarkResult` - 基准测试结果对象

**异常**:
- `BenchmarkError`: 测试执行失败
- `TimeoutError`: 测试超时

##### `run_suite(test_suite, **kwargs)`

执行测试套件。

```python
test_suite = suite.get_test_suite("performance")
results = runner.run_suite(
    test_suite,
    parallel=True,
    max_workers=10
)
```

**参数**:
- `test_suite` (TestSuite): 测试套件对象
- `parallel` (bool, 可选): 是否并行执行，默认为True
- `max_workers` (int, 可选): 最大工作线程数

**返回**: `List[BenchmarkResult]` - 结果列表

##### `cancel_test(test_id)`

取消正在运行的测试。

```python
runner.cancel_test("test-123")
```

##### `get_status(test_id)`

获取测试状态。

```python
status = runner.get_status("test-123")
print(status.status)  # running, completed, failed, cancelled
```

### 类: `BenchmarkConfig`

基准测试配置类。

```python
config = BenchmarkConfig(
    max_concurrent=10,          # 最大并发数
    test_timeout=3600,          # 测试超时（秒）
    retry_count=3,              # 重试次数
    retry_delay=5,              # 重试延迟（秒）
    cleanup_after_test=True,    # 测试后清理
    save_raw_data=True,         # 保存原始数据
    output_dir="reports/performance"  # 输出目录
)
```

---

## 指标采集器 (Metrics Collector)

### 类: `MetricsCollector`

负责采集系统性能指标和转换性能数据。

#### 构造函数 (Constructor)

```python
from npu_converter.performance import MetricsCollector, MetricsConfig

collector = MetricsCollector(config: MetricsConfig)
```

#### 主要方法 (Methods)

##### `start_collection(test_id)`

开始采集指标。

```python
test_id = "test-123"
collector.start_collection(test_id)
```

##### `stop_collection(test_id)`

停止采集指标。

```python
metrics_data = collector.stop_collection(test_id)
```

##### `get_current_metrics()`

获取当前系统指标。

```python
metrics = collector.get_current_metrics()
print(f"CPU: {metrics.cpu_usage}%")
print(f"Memory: {metrics.memory_usage}MB")
```

##### `get_metrics_history(test_id, start_time=None, end_time=None)`

获取指标历史数据。

```python
history = collector.get_metrics_history("test-123")
for metric in history:
    print(f"{metric.timestamp}: CPU={metric.cpu_usage}%")
```

##### `subscribe(callback)`

订阅实时指标更新。

```python
def on_metrics_update(metrics):
    print(f"CPU: {metrics.cpu_usage}%")

collector.subscribe(on_metrics_update)
```

### 类: `MetricsConfig`

指标采集配置类。

```python
config = MetricsConfig(
    collection_interval=1,      # 采集间隔（秒）
    buffer_size=1000,           # 缓冲区大小
    enable_gpu_monitoring=True, # 启用GPU监控
    enable_npu_monitoring=True, # 启用NPU监控
    enable_disk_io=True,        # 启用磁盘I/O监控
    enable_network_io=True,     # 启用网络I/O监控
    max_history_size=10000,     # 最大历史记录数
    storage_type="memory",      # 存储类型 (memory/sqlite)
    storage_path="data/metrics.db"  # 存储路径
)
```

---

## 测试用例套件 (Benchmark Suite)

### 类: `BenchmarkSuite`

管理和提供标准化的性能测试用例。

#### 构造函数 (Constructor)

```python
from npu_converter.performance import BenchmarkSuite, SuiteConfig

suite = BenchmarkSuite(config: SuiteConfig)
```

#### 主要方法 (Methods)

##### `get_test_case(test_id)`

获取指定测试用例。

```python
test_case = suite.get_test_case("TC-001")
```

**参数**:
- `test_id` (str): 测试用例ID

**返回**: `TestCase` - 测试用例对象

**异常**:
- `KeyError`: 测试用例不存在

##### `list_test_cases()`

列出所有可用测试用例。

```python
test_cases = suite.list_test_cases()
for tc in test_cases:
    print(f"{tc.test_id}: {tc.description}")
```

##### `add_custom_test(test_case)`

添加自定义测试用例。

```python
custom_test = TestCase(
    test_id="TC-010",
    name="Custom Performance Test",
    description="Custom test description",
    test_function=my_test_function,
    parameters={"iterations": 100}
)
suite.add_custom_test(custom_test)
```

##### `create_test_suite(test_ids)`

创建测试套件。

```python
test_suite = suite.create_test_suite(
    ["TC-001", "TC-002", "TC-003"]
)
```

### 内置测试用例 (Built-in Test Cases)

#### TC-001: SenseVoice ASR模型转换性能测试

```python
test_case = suite.get_test_case("TC-001")
# 测试SenseVoice ASR模型的NPU转换性能
```

#### TC-002: VITS-Cantonese TTS模型转换性能测试

```python
test_case = suite.get_test_case("TC-002")
# 测试VITS-Cantonese TTS模型的NPU转换性能
```

#### TC-003: Piper VITS TTS模型转换性能测试

```python
test_case = suite.get_test_case("TC-003")
# 测试Piper VITS TTS模型的NPU转换性能
```

#### TC-004: 多模型并发转换性能测试

```python
test_case = suite.get_test_case("TC-004")
# 测试多个模型并发转换的性能
```

#### TC-005: 高压力转换性能测试

```python
test_case = suite.get_test_case("TC-005")
# 在高负载情况下测试转换性能
```

#### TC-006: 24小时长期稳定性测试

```python
test_case = suite.get_test_case("TC-006")
# 测试系统长期运行的稳定性
```

#### TC-007: 内存泄漏测试

```python
test_case = suite.get_test_case("TC-007")
# 检测内存泄漏问题
```

#### TC-008: 性能回归测试

```python
test_case = suite.get_test_case("TC-008")
# 对比历史性能数据，检测性能回归
```

---

## 性能分析器 (Performance Analyzer)

### 类: `PerformanceAnalyzer`

分析性能数据，生成统计信息和优化建议。

#### 构造函数 (Constructor)

```python
from npu_converter.performance import PerformanceAnalyzer, AnalyzerConfig

analyzer = PerformanceAnalyzer(config: AnalyzerConfig)
```

#### 主要方法 (Methods)

##### `analyze_results(results)`

分析性能测试结果。

```python
results = runner.run_suite(test_suite)
analysis = analyzer.analyze_results(results)
```

##### `calculate_statistics(metrics_data)`

计算统计指标。

```python
stats = analyzer.calculate_statistics(metrics_data)
print(f"Mean: {stats.mean}")
print(f"Median: {stats.median}")
print(f"P95: {stats.p95}")
print(f"P99: {stats.p99}")
```

##### `detect_anomalies(metrics_data)`

检测性能异常。

```python
anomalies = analyzer.detect_anomalies(metrics_data)
for anomaly in anomalies:
    print(f"Anomaly detected: {anomaly.type}")
    print(f"Severity: {anomaly.severity}")
    print(f"Description: {anomaly.description}")
```

##### `compare_benchmarks(baseline_results, current_results)`

对比两个基准测试结果。

```python
comparison = analyzer.compare_benchmarks(
    baseline_results,
    current_results
)
print(f"Performance change: {comparison.percentage_change}%")
```

##### `generate_recommendations(analysis)`

生成性能优化建议。

```python
recommendations = analyzer.generate_recommendations(analysis)
for rec in recommendations:
    print(f"Recommendation: {rec.title}")
    print(f"Impact: {rec.impact}")
    print(f"Action: {rec.action}")
```

### 类: `AnalyzerConfig`

分析器配置类。

```python
config = AnalyzerConfig(
    anomaly_threshold=2.0,      # 异常检测阈值（标准差倍数）
    trend_window=10,            # 趋势分析窗口大小
    percentile_levels=[50, 90, 95, 99],  # 百分位数
    enable_anomaly_detection=True,  # 启用异常检测
    enable_trend_analysis=True,     # 启用趋势分析
    enable_recommendations=True     # 启用建议生成
)
```

---

## 报告生成器 (Report Generator)

### 类: `ReportGenerator`

生成性能测试报告。

#### 构造函数 (Constructor)

```python
from npu_converter.performance import ReportGenerator, ReportConfig

generator = ReportGenerator(config: ReportConfig)
```

#### 主要方法 (Methods)

##### `generate_summary_report(data)`

生成汇总报告。

```python
summary = generator.generate_summary_report(analysis_data)
print(summary.total_tests)
print(summary.pass_rate)
print(summary.avg_duration)
```

##### `generate_detailed_report(data)`

生成详细报告。

```python
detailed = generator.generate_detailed_report(analysis_data)
print(detailed.test_results)
print(detailed.performance_metrics)
```

##### `export_report(report, format, output_path)`

导出报告为指定格式。

```python
# 导出为HTML
generator.export_report(summary, "html", "reports/summary.html")

# 导出为PDF
generator.export_report(detailed, "pdf", "reports/detailed.pdf")

# 导出为JSON
generator.export_report(analysis_data, "json", "reports/data.json")
```

##### `generate_html_report(data, output_path)`

生成HTML报告。

```python
generator.generate_html_report(
    analysis_data,
    "reports/benchmark_report.html"
)
```

##### `generate_json_report(data, output_path)`

生成JSON报告。

```python
generator.generate_json_report(
    analysis_data,
    "reports/benchmark_data.json"
)
```

### 类: `ReportConfig`

报告生成配置类。

```python
config = ReportConfig(
    output_dir="reports/performance",   # 输出目录
    include_charts=True,                # 包含图表
    include_recommendations=True,       # 包含建议
    include_trends=True,                # 包含趋势分析
    template="default",                 # 模板名称
    theme="light"                       # 主题 (light/dark)
)
```

---

## 可视化引擎 (Visualization Engine)

### 类: `VisualizationEngine`

生成性能数据可视化图表。

#### 构造函数 (Constructor)

```python
from npu_converter.performance import VisualizationEngine, VisualizationConfig

viz = VisualizationEngine(config: VisualizationConfig)
```

#### 主要方法 (Methods)

##### `create_time_series_chart(metrics_data, output_path)`

创建时间序列图表。

```python
viz.create_time_series_chart(
    metrics_data,
    "charts/time_series.png"
)
```

##### `create_comparison_chart(baseline, current, output_path)`

创建对比图表。

```python
viz.create_comparison_chart(
    baseline_data,
    current_data,
    "charts/comparison.png"
)
```

##### `create_distribution_chart(metrics_data, output_path)`

创建分布图表。

```python
viz.create_distribution_chart(
    metrics_data,
    "charts/distribution.png"
)
```

##### `create_dashboard(metrics_data, output_path)`

创建交互式仪表盘。

```python
viz.create_dashboard(
    metrics_data,
    "dashboard.html"
)
```

##### `export_chart(chart, format, output_path)`

导出图表为指定格式。

```python
chart = viz.create_time_series_chart(metrics_data)
viz.export_chart(chart, "png", "chart.png")
viz.export_chart(chart, "svg", "chart.svg")
viz.export_chart(chart, "html", "chart.html")
```

### 类: `VisualizationConfig`

可视化配置类。

```python
config = VisualizationConfig(
    width=800,                   # 图表宽度
    height=600,                  # 图表高度
    dpi=300,                     # 图片DPI
    theme="default",             # 图表主题
    color_palette="viridis",     # 颜色方案
    font_size=12,                # 字体大小
    output_format="png"          # 默认输出格式
)
```

---

## 告警系统 (Alert System)

### 类: `AlertSystem`

监控性能指标，触发告警。

#### 构造函数 (Constructor)

```python
from npu_converter.performance import AlertSystem, AlertConfig

alerts = AlertSystem(config: AlertConfig)
```

#### 主要方法 (Methods)

##### `add_rule(rule)`

添加告警规则。

```python
from npu_converter.performance import AlertRule

rule = AlertRule(
    name="High CPU Usage",
    metric="cpu_usage",
    threshold=80.0,
    comparison=">",
    severity="high",
    duration=300  # 5分钟
)
alerts.add_rule(rule)
```

##### `check_metrics(metrics)`

检查指标是否触发告警。

```python
alerts.check_metrics(current_metrics)
```

##### `subscribe(callback)`

订阅告警事件。

```python
def on_alert(alert):
    print(f"Alert: {alert.title}")
    print(f"Severity: {alert.severity}")
    print(f"Message: {alert.message}")

alerts.subscribe(on_alert)
```

##### `get_active_alerts()`

获取当前活跃的告警。

```python
active_alerts = alerts.get_active_alerts()
for alert in active_alerts:
    print(f"{alert.title}: {alert.status}")
```

##### `acknowledge_alert(alert_id)`

确认告警。

```python
alerts.acknowledge_alert("alert-123")
```

##### `resolve_alert(alert_id)`

解决告警。

```python
alerts.resolve_alert("alert-123")
```

### 类: `AlertRule`

告警规则类。

```python
rule = AlertRule(
    name="High Memory Usage",
    metric="memory_usage",      # 指标名称
    threshold=85.0,             # 阈值
    comparison=">",             # 比较操作符 (>, <, >=, <=, ==)
    severity="medium",          # 严重程度 (low, medium, high, critical)
    duration=600,               # 持续时间（秒）
    message="Memory usage exceeded threshold",  # 告警消息
    enabled=True                # 是否启用
)
```

### 预定义告警规则 (Predefined Rules)

```python
# CPU使用率过高
alerts.add_rule(AlertRule(
    name="High CPU Usage",
    metric="cpu_usage",
    threshold=80.0,
    comparison=">",
    severity="high"
))

# 内存使用率过高
alerts.add_rule(AlertRule(
    name="High Memory Usage",
    metric="memory_usage",
    threshold=85.0,
    comparison=">",
    severity="high"
))

# 转换失败率过高
alerts.add_rule(AlertRule(
    name="High Failure Rate",
    metric="failure_rate",
    threshold=5.0,
    comparison=">",
    severity="critical"
))

# 响应时间过长
alerts.add_rule(AlertRule(
    name="Slow Response Time",
    metric="response_time",
    threshold=60.0,
    comparison=">",
    severity="medium"
))
```

---

## 配置类 (Configuration Classes)

### BenchmarkConfig

基准测试配置。

```python
from npu_converter.performance import BenchmarkConfig

config = BenchmarkConfig(
    max_concurrent=10,                    # 最大并发数
    test_timeout=3600,                    # 测试超时（秒）
    retry_count=3,                        # 重试次数
    retry_delay=5,                        # 重试延迟（秒）
    cleanup_after_test=True,              # 测试后清理
    save_raw_data=True,                   # 保存原始数据
    output_dir="reports/performance"      # 输出目录
)
```

### MetricsConfig

指标采集配置。

```python
from npu_converter.performance import MetricsConfig

config = MetricsConfig(
    collection_interval=1,                # 采集间隔（秒）
    buffer_size=1000,                     # 缓冲区大小
    enable_gpu_monitoring=True,           # 启用GPU监控
    enable_npu_monitoring=True,           # 启用NPU监控
    enable_disk_io=True,                  # 启用磁盘I/O监控
    enable_network_io=True,               # 启用网络I/O监控
    max_history_size=10000,               # 最大历史记录数
    storage_type="memory",                # 存储类型
    storage_path="data/metrics.db",       # 存储路径
    realtime_callback=None                # 实时回调函数
)
```

### SuiteConfig

测试套件配置。

```python
from npu_converter.performance import SuiteConfig

config = SuiteConfig(
    default_timeout=3600,                 # 默认超时
    default_iterations=100,               # 默认迭代次数
    parallel_execution=True,              # 并行执行
    max_workers=10                        # 最大工作线程数
)
```

### AnalyzerConfig

分析器配置。

```python
from npu_converter.performance import AnalyzerConfig

config = AnalyzerConfig(
    anomaly_threshold=2.0,                # 异常检测阈值
    trend_window=10,                      # 趋势分析窗口
    percentile_levels=[50, 90, 95, 99],   # 百分位数
    enable_anomaly_detection=True,        # 启用异常检测
    enable_trend_analysis=True,           # 启用趋势分析
    enable_recommendations=True           # 启用建议生成
)
```

### ReportConfig

报告生成配置。

```python
from npu_converter.performance import ReportConfig

config = ReportConfig(
    output_dir="reports/performance",     # 输出目录
    include_charts=True,                  # 包含图表
    include_recommendations=True,         # 包含建议
    include_trends=True,                  # 包含趋势分析
    template="default",                   # 模板名称
    theme="light"                         # 主题
)
```

### VisualizationConfig

可视化配置。

```python
from npu_converter.performance import VisualizationConfig

config = VisualizationConfig(
    width=800,                            # 图表宽度
    height=600,                           # 图表高度
    dpi=300,                              # 图片DPI
    theme="default",                      # 图表主题
    color_palette="viridis",              # 颜色方案
    font_size=12,                         # 字体大小
    output_format="png"                   # 默认输出格式
)
```

### AlertConfig

告警系统配置。

```python
from npu_converter.performance import AlertConfig

config = AlertConfig(
    check_interval=60,                    # 检查间隔（秒）
    default_severity="medium",            # 默认严重程度
    max_alerts=100,                       # 最大告警数
    alert_retention_days=30,              # 告警保留天数
    enable_notifications=True             # 启用通知
)
```

---

## 数据模型 (Data Models)

### TestCase

测试用例数据模型。

```python
class TestCase:
    test_id: str                         # 测试用例ID
    name: str                           # 测试名称
    description: str                    # 测试描述
    category: str                       # 测试类别
    test_function: Callable             # 测试函数
    parameters: Dict                    # 测试参数
    timeout: int                        # 超时时间
    iterations: int                     # 迭代次数
```

### BenchmarkResult

基准测试结果数据模型。

```python
class BenchmarkResult:
    test_id: str                        # 测试用例ID
    status: str                         # 测试状态 (success/failure)
    start_time: datetime                # 开始时间
    end_time: datetime                  # 结束时间
    duration: float                     # 持续时间（秒）
    metrics: MetricsData                # 指标数据
    error_message: str                  # 错误信息（如果有）
    iterations: int                     # 实际迭代次数
    success_rate: float                 # 成功率
```

### MetricsData

指标数据模型。

```python
class MetricsData:
    timestamp: datetime                 # 时间戳
    cpu_usage: float                    # CPU使用率
    memory_usage: float                 # 内存使用量
    gpu_usage: float                    # GPU使用率
    gpu_memory: float                   # GPU内存
    npu_usage: float                    # NPU使用率
    conversion_rate: float              # 转换速率
    response_time: float                # 响应时间
    throughput: float                   # 吞吐量
    error_count: int                    # 错误计数
```

### AnalysisResult

分析结果数据模型。

```python
class AnalysisResult:
    total_tests: int                    # 总测试数
    passed_tests: int                   # 通过测试数
    failed_tests: int                   # 失败测试数
    avg_duration: float                 # 平均持续时间
    p50_duration: float                 # P50持续时间
    p95_duration: float                 # P95持续时间
    p99_duration: float                 # P99持续时间
    success_rate: float                 # 成功率
    anomalies: List[Anomaly]            # 异常列表
    recommendations: List[Recommendation]  # 建议列表
```

### Anomaly

异常数据模型。

```python
class Anomaly:
    type: str                           # 异常类型
    metric: str                         # 指标名称
    value: float                        # 异常值
    threshold: float                    # 阈值
    severity: str                       # 严重程度
    description: str                    # 描述
    timestamp: datetime                 # 时间戳
```

### Recommendation

建议数据模型。

```python
class Recommendation:
    title: str                          # 建议标题
    description: str                    # 建议描述
    impact: str                         # 影响程度
    effort: str                         # 实施难度
    action: str                         # 行动建议
    metric_affected: str                # 受影响的指标
```

### Alert

告警数据模型。

```python
class Alert:
    alert_id: str                       # 告警ID
    rule_name: str                      # 规则名称
    title: str                          # 告警标题
    message: str                        # 告警消息
    severity: str                       # 严重程度
    metric: str                         # 指标名称
    value: float                        # 当前值
    threshold: float                    # 阈值
    status: str                         # 状态 (active/acknowledged/resolved)
    created_time: datetime              # 创建时间
    acknowledged_time: datetime         # 确认时间
    resolved_time: datetime             # 解决时间
```

---

## 完整示例 (Complete Example)

### 示例1: 运行完整的基准测试套件

```python
from npu_converter.performance import (
    BenchmarkRunner,
    MetricsCollector,
    BenchmarkSuite,
    PerformanceAnalyzer,
    ReportGenerator,
    VisualizationEngine,
    AlertSystem,
    BenchmarkConfig,
    MetricsConfig,
    SuiteConfig,
    AnalyzerConfig,
    ReportConfig,
    VisualizationConfig,
    AlertConfig
)

# 1. 创建配置
benchmark_config = BenchmarkConfig(
    max_concurrent=10,
    test_timeout=3600,
    output_dir="reports/performance"
)

metrics_config = MetricsConfig(
    collection_interval=1,
    buffer_size=1000,
    enable_gpu_monitoring=True
)

suite_config = SuiteConfig()

analyzer_config = AnalyzerConfig(
    anomaly_threshold=2.0,
    enable_anomaly_detection=True
)

report_config = ReportConfig(
    include_charts=True,
    include_recommendations=True
)

viz_config = VisualizationConfig(
    width=1200,
    height=800,
    dpi=150
)

alert_config = AlertConfig(
    check_interval=60,
    default_severity="medium"
)

# 2. 创建组件实例
runner = BenchmarkRunner(benchmark_config)
collector = MetricsCollector(metrics_config)
suite = BenchmarkSuite(suite_config)
analyzer = PerformanceAnalyzer(analyzer_config)
generator = ReportGenerator(report_config)
visualization = VisualizationEngine(viz_config)
alerts = AlertSystem(alert_config)

# 3. 添加告警规则
alerts.add_rule(AlertRule(
    name="High CPU Usage",
    metric="cpu_usage",
    threshold=80.0,
    comparison=">",
    severity="high"
))

# 4. 获取测试用例
test_suite = suite.create_test_suite([
    "TC-001", "TC-002", "TC-003", "TC-004"
])

# 5. 运行测试
print("Starting benchmark suite...")
results = runner.run_suite(test_suite)

# 6. 分析结果
print("Analyzing results...")
analysis = analyzer.analyze_results(results)

# 7. 生成报告
print("Generating reports...")
summary = generator.generate_summary_report(analysis)
generator.export_report(summary, "html", "reports/summary.html")
generator.export_report(summary, "json", "reports/summary.json")

# 8. 生成可视化图表
print("Creating visualizations...")
viz.create_dashboard(analysis, "dashboard.html")

# 9. 打印结果
print("\n" + "="*50)
print("BENCHMARK RESULTS")
print("="*50)
print(f"Total Tests: {analysis.total_tests}")
print(f"Passed: {analysis.passed_tests}")
print(f"Failed: {analysis.failed_tests}")
print(f"Success Rate: {analysis.success_rate:.2%}")
print(f"Average Duration: {analysis.avg_duration:.2f}s")
print(f"P95 Duration: {analysis.p95_duration:.2f}s")
print("="*50)
```

### 示例2: 运行单个测试用例

```python
# 获取单个测试用例
test_case = suite.get_test_case("TC-001")

# 启动指标采集
collector.start_collection("test-001")

# 运行测试
result = runner.run_benchmark(test_case)

# 停止指标采集
metrics = collector.stop_collection("test-001")

# 分析结果
analysis = analyzer.analyze_results([result])

# 打印结果
print(f"Test: {result.test_id}")
print(f"Status: {result.status}")
print(f"Duration: {result.duration:.2f}s")
print(f"CPU Usage: {metrics.cpu_usage:.2f}%")
print(f"Memory Usage: {metrics.memory_usage:.2f}MB")
```

### 示例3: 性能回归检测

```python
# 获取当前结果
current_results = runner.run_suite(test_suite)

# 加载基线结果
with open("baseline.json", "r") as f:
    baseline_data = json.load(f)

# 对比分析
comparison = analyzer.compare_benchmarks(
    baseline_data,
    current_results
)

# 打印对比结果
print(f"Performance Change: {comparison.percentage_change:+.2f}%")
print(f"Status: {'REGRESSION' if comparison.is_regression else 'NORMAL'}")

if comparison.is_regression:
    print("⚠️ Performance regression detected!")
    print(f"Affected metrics: {', '.join(comparison.regressed_metrics)}")
```

### 示例4: 自定义告警

```python
# 创建自定义告警规则
custom_rule = AlertRule(
    name="Custom Memory Alert",
    metric="memory_usage",
    threshold=1024.0,  # 1GB
    comparison=">",
    severity="medium",
    message="Memory usage exceeded 1GB"
)

# 添加规则
alerts.add_rule(custom_rule)

# 检查告警
current_metrics = collector.get_current_metrics()
alerts.check_metrics(current_metrics)

# 获取活跃告警
active_alerts = alerts.get_active_alerts()
if active_alerts:
    print(f"Active alerts: {len(active_alerts)}")
    for alert in active_alerts:
        print(f"- {alert.title}: {alert.message}")
```

---

## 错误处理 (Error Handling)

### 常见异常类型

#### BenchmarkError

基准测试执行错误。

```python
try:
    result = runner.run_benchmark(test_case)
except BenchmarkError as e:
    print(f"Benchmark failed: {e.error_code}")
    print(f"Message: {e.message}")
    print(f"Retryable: {e.retryable}")
```

#### TimeoutError

测试超时错误。

```python
try:
    result = runner.run_benchmark(test_case, timeout=30)
except TimeoutError:
    print("Test timed out after 30 seconds")
```

#### ConfigurationError

配置错误。

```python
try:
    config = BenchmarkConfig(max_concurrent=-1)
except ConfigurationError as e:
    print(f"Invalid configuration: {e.message}")
```

#### MetricsError

指标采集错误。

```python
try:
    metrics = collector.get_current_metrics()
except MetricsError as e:
    print(f"Failed to collect metrics: {e.message}")
```

### 错误恢复策略

```python
def run_with_retry(runner, test_case, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = runner.run_benchmark(test_case)
            return result
        except BenchmarkError as e:
            if e.retryable and attempt < max_retries - 1:
                print(f"Retryable error, retrying (attempt {attempt + 1}/{max_retries})")
                time.sleep(5)
                continue
            else:
                print(f"Failed after {attempt + 1} attempts: {e.message}")
                raise

    return None
```

---

## 最佳实践 (Best Practices)

### 1. 配置管理

```python
# 使用配置文件
from npu_converter.performance import load_config

config = load_config("config/performance/benchmark_config.yaml")
runner = BenchmarkRunner(config.benchmark)
collector = MetricsCollector(config.metrics)
```

### 2. 日志记录

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

runner = BenchmarkRunner(config)
try:
    result = runner.run_benchmark(test_case)
    logger.info(f"Test completed: {result.test_id}")
except Exception as e:
    logger.error(f"Test failed: {e}", exc_info=True)
```

### 3. 资源清理

```python
class BenchmarkContext:
    def __init__(self, config):
        self.runner = BenchmarkRunner(config)
        self.collector = MetricsCollector(config)
        self.alerts = AlertSystem(config)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 清理资源
        self.collector.cleanup()
        self.alerts.shutdown()

with BenchmarkContext(config) as ctx:
    result = ctx.runner.run_benchmark(test_case)
```

### 4. 并发控制

```python
# 控制并发数
config = BenchmarkConfig(
    max_concurrent=10,
    test_timeout=3600
)

# 使用Semaphore限制并发
from threading import Semaphore

semaphore = Semaphore(5)  # 最多5个并发测试

def run_with_limit(test_case):
    with semaphore:
        return runner.run_benchmark(test_case)
```

### 5. 性能监控

```python
# 监控组件性能
import time

start_time = time.time()
result = runner.run_benchmark(test_case)
end_time = time.time()

overhead = end_time - start_time - result.duration
print(f"Test overhead: {overhead:.3f}s")
```

---

## 集成示例 (Integration Examples)

### 与pytest集成

```python
import pytest
from npu_converter.performance import BenchmarkSuite

@pytest.mark.benchmark
def test_performance(benchmark):
    suite = BenchmarkSuite()
    test_case = suite.get_test_case("TC-001")

    # 使用pytest-benchmark
    result = benchmark.pedantic(
        runner.run_benchmark,
        args=(test_case,),
        iterations=10,
        rounds=100
    )

    assert result.status == "success"
```

### 与CI/CD集成

```python
# GitHub Actions示例
import os
import json

# 从环境变量获取配置
config = BenchmarkConfig(
    max_concurrent=int(os.getenv("MAX_CONCURRENT", "10")),
    output_dir=os.getenv("GITHUB_WORKSPACE", ".") + "/reports"
)

# 运行测试
runner = BenchmarkRunner(config)
results = runner.run_suite(test_suite)

# 保存结果
with open("benchmark_results.json", "w") as f:
    json.dump(results, f, default=str)
```

### 与监控平台集成

```python
import requests

def send_metrics_to_monitoring(metrics):
    """发送指标到监控系统"""
    data = {
        "cpu_usage": metrics.cpu_usage,
        "memory_usage": metrics.memory_usage,
        "timestamp": metrics.timestamp.isoformat()
    }
    response = requests.post(
        "http://monitoring-server/api/metrics",
        json=data
    )
    return response.status_code == 200

# 订阅指标更新
collector.subscribe(send_metrics_to_monitoring)
```

---

## 性能优化提示 (Performance Optimization Tips)

### 1. 减少采集开销

```python
# 减少采集频率
metrics_config = MetricsConfig(
    collection_interval=5,  # 从1秒增加到5秒
    buffer_size=100
)

# 只采集关键指标
metrics_config.enable_gpu_monitoring = True
metrics_config.enable_npu_monitoring = False  # 禁用NPU监控
```

### 2. 优化并发配置

```python
# 根据CPU核心数设置并发
import os

cpu_count = os.cpu_count()
benchmark_config = BenchmarkConfig(
    max_concurrent=min(cpu_count, 10)  # 限制最大并发数
)
```

### 3. 使用SQLite存储历史数据

```python
metrics_config = MetricsConfig(
    storage_type="sqlite",
    storage_path="data/metrics.db",
    max_history_size=100000  # 增加历史记录数
)
```

### 4. 启用批量处理

```python
collector.start_collection("test", batch_size=100)
# 采集100个指标点后再处理，减少开销
```

---

## 故障排除 (Troubleshooting)

### 常见问题

#### Q1: 导入模块失败

**错误**: `ModuleNotFoundError: No module named 'npu_converter.performance'`

**解决**:
```bash
# 确保项目已安装
pip install -e .

# 或添加到PYTHONPATH
export PYTHONPATH=$PYTHONPATH:/path/to/xlerobot/src
```

#### Q2: 指标采集失败

**错误**: `MetricsError: Failed to collect GPU metrics`

**解决**:
```python
# 禁用GPU监控
metrics_config = MetricsConfig(enable_gpu_monitoring=False)
```

#### Q3: 测试超时

**错误**: `TimeoutError: Test timed out`

**解决**:
```python
# 增加超时时间
result = runner.run_benchmark(test_case, timeout=7200)  # 2小时

# 或优化测试参数
test_case.parameters["iterations"] = 10  # 减少迭代次数
```

#### Q4: 内存使用过高

**问题**: 长时间运行后内存使用持续增长

**解决**:
```python
# 启用自动清理
benchmark_config = BenchmarkConfig(
    cleanup_after_test=True,
    save_raw_data=False
)

# 定期清理历史数据
collector.cleanup_old_data(days=7)
```

---

## 版本更新日志 (Changelog)

### v1.0.0 (2025-10-29)

#### 新增功能
- ✅ 基准测试执行器 (Benchmark Runner)
- ✅ 指标采集器 (Metrics Collector)
- ✅ 测试用例套件 (Benchmark Suite) - 8个内置测试用例
- ✅ 性能分析器 (Performance Analyzer)
- ✅ 报告生成器 (Report Generator)
- ✅ 可视化引擎 (Visualization Engine)
- ✅ 告警系统 (Alert System)
- ✅ 配置管理系统
- ✅ 数据模型定义
- ✅ 完整API文档

#### 技术特性
- 支持多种指标采集（CPU、内存、GPU、NPU等）
- 内置8个标准测试用例
- 支持自定义测试用例
- 并行测试执行
- 异常检测和趋势分析
- 多格式报告输出（HTML、PDF、JSON）
- 可视化图表生成
- 灵活的配置系统
- 完善的错误处理
- CI/CD集成支持

---

## 联系信息 (Contact Information)

**开发团队**: Claude Code
**项目负责人**: Jody
**文档版本**: v1.0
**最后更新**: 2025-10-29

---

*本文档遵循XLeRobot项目文档标准*
*如有问题或建议，请查看项目仓库或联系开发团队*
