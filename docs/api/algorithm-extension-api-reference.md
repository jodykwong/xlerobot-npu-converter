# 算法扩展系统API参考

**版本**: v1.0
**日期**: 2025-10-28

---

## 目录

1. [核心系统API](#1-核心系统api)
2. [算法注册API](#2-算法注册api)
3. [算法适配器API](#3-算法适配器api)
4. [A/B测试API](#4-ab测试api)
5. [性能分析API](#5-性能分析api)
6. [自动调优API](#6-自动调优api)
7. [算法推荐API](#7-算法推荐api)
8. [配置管理API](#8-配置管理api)
9. [生命周期管理API](#9-生命周期管理api)

---

## 1. 核心系统API

### AlgorithmExtensionSystem

系统主入口，提供统一的算法管理接口。

#### 类定义

```python
class AlgorithmExtensionSystem:
    def __init__(self)
    def initialize(self) -> bool
    def shutdown(self) -> bool
    def register_algorithm(self, algorithm_class: Type[BaseAlgorithmAdapter]) -> bool
    def execute_algorithm(self, algorithm_id: str, input_data: Any, **kwargs) -> Any
    def get_algorithm_info(self, algorithm_id: str) -> Dict[str, Any]
    def list_algorithms(self) -> List[str]
    def get_statistics(self) -> Dict[str, Any]
```

#### 方法详解

##### `__init__(self)`

初始化系统实例。

**参数**: 无

**返回值**: 无

**示例**:
```python
system = AlgorithmExtensionSystem()
```

##### `initialize(self) -> bool`

初始化系统。

**参数**: 无

**返回值**: `bool` - 初始化是否成功

**示例**:
```python
if system.initialize():
    print("初始化成功")
```

##### `shutdown(self) -> bool`

关闭系统。

**参数**: 无

**返回值**: `bool` - 关闭是否成功

**示例**:
```python
system.shutdown()
```

##### `register_algorithm(self, algorithm_class: Type[BaseAlgorithmAdapter]) -> bool`

注册算法。

**参数**:
- `algorithm_class`: 算法适配器类

**返回值**: `bool` - 注册是否成功

**示例**:
```python
class MyAdapter(BaseAlgorithmAdapter):
    pass

system.register_algorithm(MyAdapter)
```

##### `execute_algorithm(self, algorithm_id: str, input_data: Any, **kwargs) -> Any`

执行算法。

**参数**:
- `algorithm_id`: 算法ID
- `input_data`: 输入数据
- `**kwargs`: 算法参数

**返回值**: `Any` - 算法执行结果

**示例**:
```python
result = system.execute_algorithm(
    "transformer_variant",
    "Hello",
    optimization_level=2
)
```

##### `get_algorithm_info(self, algorithm_id: str) -> Dict[str, Any]`

获取算法信息。

**参数**:
- `algorithm_id`: 算法ID

**返回值**: `Dict[str, Any]` - 算法信息

**示例**:
```python
info = system.get_algorithm_info("transformer_variant")
print(info)
```

##### `list_algorithms(self) -> List[str]`

列出所有算法。

**参数**: 无

**返回值**: `List[str]` - 算法ID列表

**示例**:
```python
algorithms = system.list_algorithms()
print(algorithms)
```

##### `get_statistics(self) -> Dict[str, Any]`

获取系统统计信息。

**参数**: 无

**返回值**: `Dict[str, Any]` - 统计信息

**示例**:
```python
stats = system.get_statistics()
print(stats)
```

---

## 2. 算法注册API

### AlgorithmRegistry

算法注册中心。

#### 类定义

```python
class AlgorithmRegistry:
    def __init__(self)
    def register(self, algorithm_id: str, algorithm_class: Type[BaseAlgorithmAdapter])
    def unregister(self, algorithm_id: str) -> bool
    def get(self, algorithm_id: str) -> Optional[Type[BaseAlgorithmAdapter]]
    def discover(self) -> Dict[str, AlgorithmMetadata]
    def get_metadata(self, algorithm_id: str) -> Optional[AlgorithmMetadata]
```

#### 方法详解

##### `register(self, algorithm_id: str, algorithm_class: Type[BaseAlgorithmAdapter])`

注册算法。

**参数**:
- `algorithm_id`: 算法ID
- `algorithm_class`: 算法类

**返回值**: 无

##### `unregister(self, algorithm_id: str) -> bool`

注销算法。

**参数**:
- `algorithm_id`: 算法ID

**返回值**: `bool` - 注销是否成功

##### `get(self, algorithm_id: str) -> Optional[Type[BaseAlgorithmAdapter]]`

获取算法类。

**参数**:
- `algorithm_id`: 算法ID

**返回值**: `Optional[Type[BaseAlgorithmAdapter]]` - 算法类或None

##### `discover(self) -> Dict[str, AlgorithmMetadata]`

发现所有算法。

**参数**: 无

**返回值**: `Dict[str, AlgorithmMetadata]` - 算法元数据字典

##### `get_metadata(self, algorithm_id: str) -> Optional[AlgorithmMetadata]`

获取算法元数据。

**参数**:
- `algorithm_id`: 算法ID

**返回值**: `Optional[AlgorithmMetadata]` - 算法元数据或None

---

## 3. 算法适配器API

### BaseAlgorithmAdapter

所有算法适配器的基类。

#### 类定义

```python
class BaseAlgorithmAdapter:
    VERSION: str
    DESCRIPTION: str
    AUTHOR: str
    CATEGORY: str
    DEPENDENCIES: List[str]
    SUPPORTED_FORMATS: List[str]
    PARAMETERS: Dict[str, Dict[str, Any]]

    def __init__(self)
    def initialize(self, **kwargs) -> bool
    def execute(self, input_data: Any, **kwargs) -> Any
    def validate_input(self, input_data: Any) -> bool
    def validate_output(self, output_data: Any) -> bool
    def get_statistics(self) -> Dict[str, Any]
```

### TransformerVariantAdapter

Transformer变种适配器。

#### 类定义

```python
class TransformerVariantAdapter(BaseAlgorithmAdapter):
    def initialize(self, model_size: str = "base", num_layers: int = 12,
                   hidden_size: int = 768, num_attention_heads: int = 12) -> bool
    def execute(self, input_data: Any, optimization_level: int = 2,
                precision: str = "fp16", batch_size: int = 32,
                max_sequence_length: int = 512) -> Dict[str, Any]
    def get_performance_metrics(self) -> Dict[str, Any]
    def benchmark(self, input_data: Any, iterations: int = 100) -> Dict[str, Any]
```

#### 方法详解

##### `initialize(self, model_size: str = "base", num_layers: int = 12, ...) -> bool`

初始化Transformer适配器。

**参数**:
- `model_size`: 模型大小 (small/base/large/xl)
- `num_layers`: 层数 (1-100)
- `hidden_size`: 隐藏层维度 (128-4096)
- `num_attention_heads`: 注意力头数 (1-64)

**返回值**: `bool` - 初始化是否成功

##### `execute(self, input_data: Any, optimization_level: int = 2, ...) -> Dict[str, Any]`

执行Transformer优化。

**参数**:
- `input_data`: 输入数据
- `optimization_level`: 优化级别 (0-3)
- `precision`: 精度 (fp32/fp16/int8)
- `batch_size`: 批处理大小 (1-512)
- `max_sequence_length`: 最大序列长度 (1-8192)

**返回值**: `Dict[str, Any]` - 优化结果

### CNNImprovementAdapter

CNN改进适配器。

#### 类定义

```python
class CNNImprovementAdapter(BaseAlgorithmAdapter):
    def initialize(self, architecture: str = "resnet", num_layers: int = 50,
                   kernel_size: int = 3, use_depthwise: bool = False,
                   use_se_block: bool = True, use_skip_connection: bool = True) -> bool
    def execute(self, input_data: Any, extract_features: bool = True,
                feature_level: str = "all") -> Dict[str, Any]
    def _extract_features(self, input_data: Any, level: str) -> Dict[str, Any]
```

### RNNOptimizationAdapter

RNN优化适配器。

#### 类定义

```python
class RNNOptimizationAdapter(BaseAlgorithmAdapter):
    def initialize(self, rnn_type: str = "lstm", num_layers: int = 3,
                   hidden_size: int = 256, use_bidirectional: bool = False,
                   use_attention: bool = True, dropout_rate: float = 0.2) -> bool
    def execute(self, input_data: Any, max_sequence_length: int = 500,
                learning_rate: float = 0.001, gradient_clipping: float = 1.0) -> Dict[str, Any]
    def _rnn_optimization(self, input_data: Any, kwargs: Dict[str, Any]) -> Any
```

---

## 4. A/B测试API

### AlgorithmABTestingFramework

A/B测试框架。

#### 类定义

```python
class AlgorithmABTestingFramework:
    def __init__(self)
    def create_test(self, config: ABTestConfig) -> str
    def start_test(self, test_id: str) -> bool
    def stop_test(self, test_id: str) -> bool
    def record_result(self, test_id: str, algorithm_id: str,
                     metric_name: str, value: float, sample_size: int) -> bool
    def analyze_results(self, test_id: str) -> List[Dict[str, Any]]
    def export_results(self, test_id: str, output_path: str) -> bool
```

#### 方法详解

##### `create_test(self, config: ABTestConfig) -> str`

创建A/B测试。

**参数**:
- `config`: 测试配置

**返回值**: `str` - 测试ID

##### `start_test(self, test_id: str) -> bool`

启动测试。

**参数**:
- `test_id`: 测试ID

**返回值**: `bool` - 启动是否成功

##### `stop_test(self, test_id: str) -> bool`

停止测试。

**参数**:
- `test_id`: 测试ID

**返回值**: `bool` - 停止是否成功

##### `record_result(self, test_id: str, algorithm_id: str, ...) -> bool`

记录测试结果。

**参数**:
- `test_id`: 测试ID
- `algorithm_id`: 算法ID
- `metric_name`: 指标名称
- `value`: 指标值
- `sample_size`: 样本大小

**返回值**: `bool` - 记录是否成功

##### `analyze_results(self, test_id: str) -> List[Dict[str, Any]]`

分析测试结果。

**参数**:
- `test_id`: 测试ID

**返回值**: `List[Dict[str, Any]]` - 分析结果

##### `export_results(self, test_id: str, output_path: str) -> bool`

导出测试结果。

**参数**:
- `test_id`: 测试ID
- `output_path`: 输出路径

**返回值**: `bool` - 导出是否成功

### ABTestConfig

A/B测试配置。

#### 类定义

```python
@dataclass
class ABTestConfig:
    test_name: str
    algorithm_a: str
    algorithm_b: str
    traffic_split: float = 0.5
    duration_seconds: int = 86400
    metrics: List[str] = field(default_factory=list)
    min_sample_size: int = 30
    confidence_level: float = 0.95
    statistical_power: float = 0.8
    enabled: bool = True
    description: Optional[str] = None
```

---

## 5. 性能分析API

### AlgorithmPerformanceAnalyzer

性能分析器。

#### 类定义

```python
class AlgorithmPerformanceAnalyzer:
    def __init__(self)
    def start_monitoring(self, algorithm_ids: List[str]) -> bool
    def stop_monitoring(self, algorithm_id: str) -> bool
    def record_metric(self, algorithm_id: str, metric_name: str,
                     value: float, unit: str, timestamp: Optional[float] = None) -> bool
    def take_snapshot(self, algorithm_id: str, execution_time: float,
                     **custom_metrics) -> MetricSnapshot
    def analyze_performance(self, algorithm_id: str,
                           time_window_seconds: Optional[int] = None) -> PerformanceReport
    def get_performance_trends(self, algorithm_id: str, metric_name: str) -> Optional[PerformanceTrend]
```

#### 方法详解

##### `start_monitoring(self, algorithm_ids: List[str]) -> bool`

开始监控。

**参数**:
- `algorithm_ids`: 算法ID列表

**返回值**: `bool` - 是否成功

##### `stop_monitoring(self, algorithm_id: str) -> bool`

停止监控。

**参数**:
- `algorithm_id`: 算法ID

**返回值**: `bool` - 是否成功

##### `record_metric(self, algorithm_id: str, metric_name: str, ...) -> bool`

记录指标。

**参数**:
- `algorithm_id`: 算法ID
- `metric_name`: 指标名称
- `value`: 指标值
- `unit`: 单位
- `timestamp`: 时间戳（可选）

**返回值**: `bool` - 是否成功

##### `take_snapshot(self, algorithm_id: str, execution_time: float, ...) -> MetricSnapshot`

拍摄性能快照。

**参数**:
- `algorithm_id`: 算法ID
- `execution_time`: 执行时间
- `**custom_metrics`: 自定义指标

**返回值**: `MetricSnapshot` - 快照对象

##### `analyze_performance(self, algorithm_id: str, ...) -> PerformanceReport`

分析性能。

**参数**:
- `algorithm_id`: 算法ID
- `time_window_seconds`: 时间窗口（秒）

**返回值**: `PerformanceReport` - 性能报告

##### `get_performance_trends(self, algorithm_id: str, metric_name: str) -> Optional[PerformanceTrend]`

获取性能趋势。

**参数**:
- `algorithm_id`: 算法ID
- `metric_name`: 指标名称

**返回值**: `Optional[PerformanceTrend]` - 性能趋势或None

---

## 6. 自动调优API

### AutoTuningEngine

自动调优引擎。

#### 类定义

```python
class AutoTuningEngine:
    def __init__(self)
    def tune_parameters(self, config: TuningConfig,
                       objective_function: Callable[[Dict[str, Any]], float],
                       warm_start: bool = False) -> TuningResult
    def get_tuning_history(self) -> List[TuningResult]
    def get_best_parameters(self, algorithm_id: str) -> Optional[Dict[str, Any]]
    def clear_history(self) -> None
```

#### 方法详解

##### `tune_parameters(self, config: TuningConfig, ...) -> TuningResult`

执行参数调优。

**参数**:
- `config`: 调优配置
- `objective_function`: 目标函数
- `warm_start`: 是否热启动

**返回值**: `TuningResult` - 调优结果

##### `get_tuning_history(self) -> List[TuningResult]`

获取调优历史。

**参数**: 无

**返回值**: `List[TuningResult]` - 调优历史列表

##### `get_best_parameters(self, algorithm_id: str) -> Optional[Dict[str, Any]]`

获取最佳参数。

**参数**:
- `algorithm_id`: 算法ID

**返回值**: `Optional[Dict[str, Any]]` - 最佳参数或None

### ParameterSpace

参数空间定义。

#### 类定义

```python
@dataclass
class ParameterSpace:
    name: str
    param_type: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    default: Any = None
    choices: Optional[List[Any]] = None
    log_space: bool = False

    def sample(self) -> Any
```

#### 方法详解

##### `sample(self) -> Any`

采样参数值。

**参数**: 无

**返回值**: `Any` - 采样的参数值

### TuningConfig

调优配置。

#### 类定义

```python
@dataclass
class TuningConfig:
    strategy: TuningStrategy
    objective: OptimizationObjective
    parameter_spaces: List[ParameterSpace]
    max_iterations: int
    parallel_jobs: int = 1
    early_stopping_patience: Optional[int] = None
    convergence_threshold: Optional[float] = None
    timeout_seconds: Optional[int] = None
    warm_start: bool = False
```

### TuningResult

调优结果。

#### 类定义

```python
@dataclass
class TuningResult:
    algorithm_id: str
    best_parameters: Optional[Dict[str, Any]]
    best_score: float
    optimization_history: List[OptimizationTrial]
    strategy_used: TuningStrategy
    objective: OptimizationObjective
    total_trials: int
    start_time: float
    end_time: Optional[float] = None
    convergence_achieved: bool = False
    elapsed_time: float = 0.0
```

---

## 7. 算法推荐API

### AlgorithmRecommender

算法推荐系统。

#### 类定义

```python
class AlgorithmRecommender:
    def __init__(self)
    def recommend_algorithm(self, use_case: str,
                           requirements: Optional[Dict[str, Any]] = None) -> List[Recommendation]
    def suggest_parameters(self, algorithm_id: str, target_use_case: str,
                          constraints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]
    def get_best_practices(self, category: Optional[str] = None) -> List[Recommendation]
    def analyze_algorithm_compatibility(self, algorithm_id: str,
                                       requirements: Dict[str, Any]) -> Dict[str, Any]
    def register_algorithm_profile(self, profile: AlgorithmProfile) -> None
```

#### 方法详解

##### `recommend_algorithm(self, use_case: str, ...) -> List[Recommendation]`

推荐算法。

**参数**:
- `use_case`: 使用场景
- `requirements`: 需求约束

**返回值**: `List[Recommendation]` - 推荐列表

##### `suggest_parameters(self, algorithm_id: str, ...) -> Dict[str, Any]`

建议参数。

**参数**:
- `algorithm_id`: 算法ID
- `target_use_case`: 目标使用场景
- `constraints`: 约束条件

**返回值**: `Dict[str, Any]` - 参数建议

##### `get_best_practices(self, category: Optional[str] = None) -> List[Recommendation]`

获取最佳实践。

**参数**:
- `category`: 分类

**返回值**: `List[Recommendation]` - 最佳实践列表

##### `analyze_algorithm_compatibility(self, algorithm_id: str, requirements: Dict[str, Any]) -> Dict[str, Any]`

分析算法兼容性。

**参数**:
- `algorithm_id`: 算法ID
- `requirements`: 需求

**返回值**: `Dict[str, Any]` - 兼容性分析结果

### Recommendation

推荐对象。

#### 类定义

```python
@dataclass
class Recommendation:
    type: RecommendationType
    title: str
    description: str
    confidence: ConfidenceLevel
    priority: int
    impact: str
    effort: str
    suggestions: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
```

---

## 8. 配置管理API

### ExtendedAlgorithmConfig

扩展算法配置。

#### 类定义

```python
class ExtendedAlgorithmConfig:
    def __init__(self, algorithm_id: str, parameter_definitions: List[ParameterDefinition],
                 description: str = "", version: str = "1.0.0")
    def configure(self, config: Dict[str, Any], validate: bool = True) -> bool
    def validate_config(self, config: Dict[str, Any]) -> bool
    def get_config(self, param_name: str) -> Any
    def set_config(self, param_name: str, value: Any) -> None
    def get_all_parameters(self) -> Dict[str, Any]
    def export_to_dict(self) -> Dict[str, Any]
    def import_from_dict(self, data: Dict[str, Any]) -> bool
    def export_to_yaml(self, file_path: str) -> bool
    def import_from_yaml(self, file_path: str) -> bool
```

#### 方法详解

##### `configure(self, config: Dict[str, Any], validate: bool = True) -> bool`

配置参数。

**参数**:
- `config`: 配置字典
- `validate`: 是否验证

**返回值**: `bool` - 配置是否成功

##### `validate_config(self, config: Dict[str, Any]) -> bool`

验证配置。

**参数**:
- `config`: 配置字典

**返回值**: `bool` - 配置是否有效

##### `get_config(self, param_name: str) -> Any`

获取参数值。

**参数**:
- `param_name`: 参数名

**返回值**: `Any` - 参数值

##### `set_config(self, param_name: str, value: Any) -> None`

设置参数值。

**参数**:
- `param_name`: 参数名
- `value`: 参数值

**返回值**: 无

##### `export_to_dict(self) -> Dict[str, Any]`

导出为字典。

**参数**: 无

**返回值**: `Dict[str, Any]` - 配置字典

##### `import_from_dict(self, data: Dict[str, Any]) -> bool`

从字典导入。

**参数**:
- `data`: 配置字典

**返回值**: `bool` - 导入是否成功

##### `export_to_yaml(self, file_path: str) -> bool`

导出为YAML文件。

**参数**:
- `file_path`: 文件路径

**返回值**: `bool` - 导出是否成功

##### `import_from_yaml(self, file_path: str) -> bool`

从YAML文件导入。

**参数**:
- `file_path`: 文件路径

**返回值**: `bool` - 导入是否成功

### ParameterDefinition

参数定义。

#### 类定义

```python
@dataclass
class ParameterDefinition:
    name: str
    param_type: str
    required: bool = False
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    choices: Optional[List[Any]] = None
    default: Any = None
    description: str = ""
    must_exist: bool = False

    def validate(self, value: Any) -> bool
```

---

## 9. 生命周期管理API

### AlgorithmLifecycleManager

生命周期管理器。

#### 类定义

```python
class AlgorithmLifecycleManager:
    def __init__(self)
    def initialize_algorithm(self, algorithm_id: str, **kwargs) -> bool
    def execute_algorithm(self, algorithm_id: str, input_data: Any, **kwargs) -> Any
    def shutdown_algorithm(self, algorithm_id: str) -> bool
    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None
    def unsubscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None
    def publish(self, event_type: EventType, event_data: Dict[str, Any]) -> None
```

#### 方法详解

##### `initialize_algorithm(self, algorithm_id: str, **kwargs) -> bool`

初始化算法。

**参数**:
- `algorithm_id`: 算法ID
- `**kwargs`: 初始化参数

**返回值**: `bool` - 初始化是否成功

##### `execute_algorithm(self, algorithm_id: str, input_data: Any, **kwargs) -> Any`

执行算法。

**参数**:
- `algorithm_id`: 算法ID
- `input_data`: 输入数据
- `**kwargs`: 执行参数

**返回值**: `Any` - 执行结果

##### `shutdown_algorithm(self, algorithm_id: str) -> bool`

关闭算法。

**参数**:
- `algorithm_id`: 算法ID

**返回值**: `bool` - 关闭是否成功

##### `subscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None`

订阅事件。

**参数**:
- `event_type`: 事件类型
- `callback`: 回调函数

**返回值**: 无

##### `unsubscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None`

取消订阅。

**参数**:
- `event_type`: 事件类型
- `callback`: 回调函数

**返回值**: 无

##### `publish(self, event_type: EventType, event_data: Dict[str, Any]) -> None`

发布事件。

**参数**:
- `event_type`: 事件类型
- `event_data`: 事件数据

**返回值**: 无

### EventType

事件类型枚举。

```python
class EventType(Enum):
    INITIALIZE_STARTED = "initialize_started"
    INITIALIZE_COMPLETED = "initialize_completed"
    EXECUTE_STARTED = "execute_started"
    EXECUTE_COMPLETED = "execute_completed"
    ERROR_OCCURRED = "error_occurred"
    SHUTDOWN_STARTED = "shutdown_started"
    SHUTDOWN_COMPLETED = "shutdown_completed"
```

---

## 附录A: 枚举类型

### TuningStrategy

调优策略枚举。

```python
class TuningStrategy(Enum):
    GRID_SEARCH = "grid_search"
    RANDOM_SEARCH = "random_search"
    BAYESIAN_OPTIMIZATION = "bayesian_optimization"
    GENETIC_ALGORITHM = "genetic_algorithm"
```

### OptimizationObjective

优化目标枚举。

```python
class OptimizationObjective(Enum):
    MAXIMIZE_ACCURACY = "maximize_accuracy"
    MINIMIZE_LOSS = "minimize_loss"
    MAXIMIZE_THROUGHPUT = "maximize_throughput"
    MINIMIZE_LATENCY = "minimize_latency"
```

### RecommendationType

推荐类型枚举。

```python
class RecommendationType(Enum):
    ALGORITHM_SELECTION = "algorithm_selection"
    PARAMETER_OPTIMIZATION = "parameter_optimization"
    ARCHITECTURE_OPTIMIZATION = "architecture_optimization"
    PERFORMANCE_TUNING = "performance_tuning"
    BEST_PRACTICE = "best_practice"
```

### ConfidenceLevel

置信度枚举。

```python
class ConfidenceLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
```

### TestStatus

测试状态枚举。

```python
class TestStatus(Enum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
```

---

## 附录B: 数据类

### AlgorithmMetadata

算法元数据。

```python
@dataclass
class AlgorithmMetadata:
    algorithm_id: str
    display_name: str
    description: str
    version: str
    author: str
    category: str
    supported_formats: List[str]
    parameters: Dict[str, Any]
```

### PerformanceReport

性能报告。

```python
@dataclass
class PerformanceReport:
    algorithm_id: str
    start_time: float
    end_time: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_latency: float
    min_latency: float
    max_latency: float
    throughput: float
    metrics: Dict[str, Any]
```

### MetricSnapshot

指标快照。

```python
@dataclass
class MetricSnapshot:
    algorithm_id: str
    execution_time: float
    timestamp: float
    custom_metrics: Dict[str, Any]
```

### PerformanceTrend

性能趋势。

```python
@dataclass
class PerformanceTrend:
    algorithm_id: str
    metric_name: str
    time_points: List[float]
    values: List[float]
    unit: str
```

### OptimizationTrial

优化试验。

```python
@dataclass
class OptimizationTrial:
    trial_id: str
    parameters: Dict[str, Any]
    status: TrialStatus
    score: Optional[float] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error: Optional[str] = None
```

---

## 附录C: 异常类型

### ConfigValidationError

配置验证错误。

```python
class ConfigValidationError(Exception):
    pass
```

### TuningError

调优错误。

```python
class TuningError(Exception):
    pass
```

### ABTestError

A/B测试错误。

```python
class ABTestError(Exception):
    pass
```

---

**API参考文档结束**

更多详细信息请参考用户指南和架构文档。
