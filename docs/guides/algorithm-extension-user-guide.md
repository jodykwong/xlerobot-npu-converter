# 算法扩展系统用户指南

**版本**: v1.0
**日期**: 2025-10-28

---

## 目录

1. [快速开始](#1-快速开始)
2. [基本使用](#2-基本使用)
3. [算法适配器](#3-算法适配器)
4. [A/B测试](#4-ab测试)
5. [性能分析](#5-性能分析)
6. [自动调优](#6-自动调优)
7. [算法推荐](#7-算法推荐)
8. [配置管理](#8-配置管理)
9. [高级功能](#9-高级功能)
10. [常见问题](#10-常见问题)

---

## 1. 快速开始

### 1.1 安装和设置

首先，确保您已经安装了XLeRobot NPU模型转换工具。

```bash
# 检查安装
python -c "import npu_converter; print(npu_converter.__version__)"
```

### 1.2 第一个示例

让我们从一个简单的示例开始：

```python
from npu_converter.extensions.algorithms.transformer_variant_adapter import TransformerVariantAdapter

# 创建适配器实例
adapter = TransformerVariantAdapter()

# 初始化
adapter.initialize(
    model_size="base",
    num_layers=12,
    hidden_size=768
)

# 执行算法
result = adapter.execute(
    "Hello, XLeRobot!",
    optimization_level=2,
    precision="fp16"
)

print(result)
```

**输出**:
```
{
    'transformed_data': 'Hello, XLeRobot!',
    'transform_type': 'advanced_optimize',
    'applied_optimizations': [...],
    'performance_gain': '3.8x'
}
```

### 1.3 查看可用算法

```python
from npu_converter.extensions.algorithm_extension_system import AlgorithmExtensionSystem

# 创建系统实例
system = AlgorithmExtensionSystem()
system.initialize()

# 获取所有可用算法
algorithms = system.discover_algorithms()
print("可用算法:", list(algorithms.keys()))
```

---

## 2. 基本使用

### 2.1 系统初始化

```python
from npu_converter.extensions.algorithm_extension_system import AlgorithmExtensionSystem

# 创建系统实例
extension_system = AlgorithmExtensionSystem()

# 初始化
if extension_system.initialize():
    print("算法扩展系统初始化成功")
else:
    print("初始化失败")
```

### 2.2 注册算法

```python
from npu_converter.extensions.algorithm_registry import AlgorithmRegistry

registry = AlgorithmRegistry()

# 注册自定义算法
registry.register("my_algorithm", MyCustomAdapter)

# 验证注册
if registry.get("my_algorithm"):
    print("算法注册成功")
```

### 2.3 执行算法

```python
# 执行算法
result = extension_system.execute_algorithm(
    algorithm_id="transformer_variant",
    input_data="test input",
    optimization_level=2,
    precision="fp16"
)

print(f"执行结果: {result}")
```

### 2.4 获取算法信息

```python
# 获取算法信息
info = extension_system.get_algorithm_info("transformer_variant")
print(f"算法信息: {info}")
```

---

## 3. 算法适配器

### 3.1 Transformer变种适配器

适用于文本处理、序列建模等任务。

**基本使用**:

```python
from npu_converter.extensions.algorithms.transformer_variant_adapter import TransformerVariantAdapter

adapter = TransformerVariantAdapter()

# 初始化参数
adapter.initialize(
    model_size="base",          # small/base/large/xl
    num_layers=12,               # 1-100
    hidden_size=768,             # 128-4096
    num_attention_heads=12       # 1-64
)

# 执行优化
result = adapter.execute(
    input_data="您的输入文本",
    optimization_level=2,        # 0-3 (0=无优化, 3=极限优化)
    precision="fp16",            # fp32/fp16/int8
    batch_size=32,
    max_sequence_length=512
)

print(f"优化结果: {result}")
```

**优化级别说明**:
- **级别0 (basic)**: 无优化，使用默认配置
- **级别1 (basic_optimize)**: 基础优化，包括注意力和层归一化
- **级别2 (advanced_optimize)**: 高级优化，包括多头注意力、位置编码、前馈网络和残差连接
- **级别3 (extreme_optimize)**: 极限优化，包括核融合、内存合并、张量核心加速等

**性能基准**:
- 级别1: 1.5-2.0x 性能提升
- 级别2: 3.0-4.0x 性能提升
- 级别3: 5.0-6.0x 性能提升

### 3.2 CNN改进适配器

适用于图像处理、计算机视觉等任务。

**基本使用**:

```python
from npu_converter.extensions.algorithms.cnn_improvement_adapter import CNNImprovementAdapter

adapter = CNNImprovementAdapter()

# 初始化参数
adapter.initialize(
    architecture="resnet",        # resnet/vgg/mobilenet/efficientnet/custom
    num_layers=50,                # 1-200
    kernel_size=3,                # 1-15
    use_depthwise=True,           # 使用深度可分离卷积
    use_se_block=True,            # 使用SE模块
    use_skip_connection=True      # 使用跳跃连接
)

# 执行优化
result = adapter.execute(
    input_data=your_image_data,   # numpy数组
    extract_features=True,        # 是否提取特征
    feature_level="all"           # low/mid/high/all
)

print(f"优化结果: {result}")
```

**架构选择指南**:
- **ResNet**: 通用性强，准确性高，适合大多数任务
- **VGG**: 结构简单，特征提取能力强
- **MobileNet**: 轻量级，适合移动设备和实时应用
- **EfficientNet**: 高效性最强，适合资源受限环境

### 3.3 RNN优化适配器

适用于序列建模、时间序列预测等任务。

**基本使用**:

```python
from npu_converter.extensions.algorithms.rnn_optimization_adapter import RNNOptimizationAdapter

adapter = RNNOptimizationAdapter()

# 初始化参数
adapter.initialize(
    rnn_type="lstm",              # lstm/gru/rnn/transformer
    num_layers=3,                 # 1-10
    hidden_size=256,              # 16-4096
    use_bidirectional=True,       # 双向处理
    use_attention=True,           # 使用注意力机制
    dropout_rate=0.2              # 0.0-1.0
)

# 执行优化
result = adapter.execute(
    input_data=[1, 2, 3, 4, 5],   # 序列数据
    max_sequence_length=500,
    learning_rate=0.001,
    gradient_clipping=1.0,
    use_truncated_bptt=True,      # 使用截断BPTT
    truncation_length=100
)

print(f"优化结果: {result}")
```

**RNN类型选择**:
- **LSTM**: 长期依赖建模能力强，适合长序列
- **GRU**: 参数较少，训练速度快
- **Vanilla RNN**: 简单快速，但梯度问题
- **Transformer**: 并行处理，适合长序列

---

## 4. A/B测试

A/B测试框架允许您比较不同算法或参数的效果。

### 4.1 创建A/B测试

```python
from npu_converter.extensions.features.ab_testing_framework import AlgorithmABTestingFramework, ABTestConfig

framework = AlgorithmABTestingFramework()

# 创建测试配置
config = ABTestConfig(
    test_name="算法比较测试",
    algorithm_a="transformer_v1",
    algorithm_b="transformer_v2",
    traffic_split=0.5,          # 50%流量到A，50%到B
    duration_seconds=3600,      # 测试持续1小时
    metrics=["accuracy", "latency", "throughput"],
    min_sample_size=100,        # 最少样本数
    confidence_level=0.95       # 置信度95%
)

# 创建测试
test_id = framework.create_test(config)
print(f"测试ID: {test_id}")
```

### 4.2 启动和管理测试

```python
# 启动测试
framework.start_test(test_id)

# 记录结果
framework.record_result(test_id, "transformer_v1", "accuracy", 0.92, 100)
framework.record_result(test_id, "transformer_v1", "latency", 0.05, 100)
framework.record_result(test_id, "transformer_v2", "accuracy", 0.95, 100)
framework.record_result(test_id, "transformer_v2", "latency", 0.04, 100)

# 停止测试
framework.stop_test(test_id)
```

### 4.3 分析结果

```python
# 分析测试结果
analysis = framework.analyze_results(test_id)

for metric_analysis in analysis:
    print(f"\n指标: {metric_analysis['metric_name']}")
    print(f"算法A: {metric_analysis['algorithm_a_stats']}")
    print(f"算法B: {metric_analysis['algorithm_b_stats']}")
    print(f"统计显著性: {metric_analysis['statistical_significance']}")
```

### 4.4 导出结果

```python
# 导出测试结果
framework.export_results(test_id, "ab_test_results.json")
```

---

## 5. 性能分析

性能分析器帮助您监控和分析算法性能。

### 5.1 启动监控

```python
from npu_converter.extensions.analysis.algorithm_performance_analyzer import AlgorithmPerformanceAnalyzer

analyzer = AlgorithmPerformanceAnalyzer()

# 开始监控算法
analyzer.start_monitoring(["transformer_variant", "cnn_improvement"])
```

### 5.2 记录指标

```python
# 记录性能指标
analyzer.record_metric("transformer_variant", "latency", 0.05, "s")
analyzer.record_metric("transformer_variant", "accuracy", 0.92, "%")
analyzer.record_metric("transformer_variant", "throughput", 100, "req/s")

# 拍摄性能快照
analyzer.take_snapshot(
    "transformer_variant",
    execution_time=0.05,
    accuracy=0.92,
    memory_usage=120
)
```

### 5.3 分析性能

```python
# 分析性能
report = analyzer.analyze_performance("transformer_variant", time_window_seconds=300)

print(f"总请求数: {report.total_requests}")
print(f"平均延迟: {report.average_latency:.3f}s")
print(f"最小延迟: {report.min_latency:.3f}s")
print(f"最大延迟: {report.max_latency:.3f}s")
print(f"吞吐率: {report.throughput:.2f} req/s")
```

### 5.4 获取性能趋势

```python
# 获取延迟趋势
trend = analyzer.get_performance_trends("transformer_variant", "latency")

print(f"趋势数据点: {len(trend.values)}")
print(f"延迟变化: {trend.values}")
```

### 5.5 识别瓶颈

```python
# 识别性能瓶颈
bottlenecks = analyzer.identify_bottlenecks("transformer_variant")

for bottleneck in bottlenecks:
    print(f"瓶颈: {bottleneck['type']}")
    print(f"影响: {bottleneck['impact']}")
    print(f"建议: {bottleneck['recommendation']}")
```

---

## 6. 自动调优

自动调优引擎帮助您找到最优参数配置。

### 6.1 定义参数空间

```python
from npu_converter.extensions.optimization.auto_tuning_engine import (
    AutoTuningEngine,
    ParameterSpace,
    TuningConfig,
    TuningStrategy,
    OptimizationObjective
)

engine = AutoTuningEngine()

# 定义参数空间
parameter_spaces = [
    ParameterSpace("learning_rate", "float", 0.0001, 0.1, default=0.001),
    ParameterSpace("batch_size", "int", 16, 256, default=32),
    ParameterSpace("optimizer", "categorical", choices=["adam", "sgd", "rmsprop"]),
    ParameterSpace("use_attention", "boolean", default=True)
]
```

### 6.2 定义目标函数

```python
def objective_function(params):
    """
    目标函数返回得分（越高越好）
    """
    # 根据参数训练模型
    # 返回验证集准确率
    accuracy = train_and_evaluate(params)
    return accuracy
```

### 6.3 执行调优

```python
# 创建调优配置
config = TuningConfig(
    strategy=TuningStrategy.BAYESIAN_OPTIMIZATION,  # 策略选择
    objective=OptimizationObjective.MAXIMIZE_ACCURACY,
    parameter_spaces=parameter_spaces,
    max_iterations=50,              # 最大迭代次数
    parallel_jobs=4,                # 并行作业数
    early_stopping_patience=5,      # 早停耐心值
    convergence_threshold=0.001     # 收敛阈值
)

# 执行调优
result = engine.tune_parameters(config, objective_function)

print(f"最佳参数: {result.best_parameters}")
print(f"最佳得分: {result.best_score:.4f}")
print(f"总试验次数: {result.total_trials}")
```

### 6.4 调优策略选择

**网格搜索 (Grid Search)**:
- 适用场景: 参数空间小，维度低
- 优点: 系统化，不遗漏
- 缺点: 计算量大

**随机搜索 (Random Search)**:
- 适用场景: 参数空间大，高维度
- 优点: 效率高，覆盖面广
- 缺点: 可能遗漏最优解

**贝叶斯优化 (Bayesian Optimization)**:
- 适用场景: 评估成本高的场景
- 优点: 样本效率高
- 缺点: 实现复杂

**遗传算法 (Genetic Algorithm)**:
- 适用场景: 非凸优化问题
- 优点: 全局搜索能力强
- 缺点: 参数多，调优复杂

### 6.5 查看调优历史

```python
# 获取调优历史
history = engine.get_tuning_history()

for trial in history.optimization_history:
    print(f"试验 {trial.trial_id}: 参数={trial.parameters}, 得分={trial.score}")
```

### 6.6 保存和加载最佳参数

```python
# 获取最佳参数
best_params = engine.get_best_parameters("default")
print(f"保存的最佳参数: {best_params}")

# 在新实验中使用
config.configure(best_params)
```

---

## 7. 算法推荐

算法推荐系统帮助您选择合适的算法和参数。

### 7.1 基本推荐

```python
from npu_converter.extensions.recommendation.algorithm_recommender import AlgorithmRecommender

recommender = AlgorithmRecommender()

# 基于使用场景推荐
recommendations = recommender.recommend_algorithm(
    use_case="图像分类",
    requirements={
        "accuracy": 0.95,
        "speed": 100,
        "memory_limit": 200
    }
)

for rec in recommendations:
    print(f"\n推荐: {rec.title}")
    print(f"描述: {rec.description}")
    print(f"置信度: {rec.confidence}")
    print(f"影响: {rec.impact}")
    print(f"建议: {rec.suggestions}")
```

### 7.2 参数建议

```python
# 获取参数建议
params = recommender.suggest_parameters(
    algorithm_id="cnn_improvement",
    target_use_case="图像分类",
    constraints={
        "input_size": 224,
        "batch_size": 64
    }
)

for param_name, param_info in params.items():
    print(f"\n参数: {param_name}")
    print(f"推荐值: {param_info['recommended_value']}")
    print(f"取值范围: {param_info['range']}")
    print(f"说明: {param_info['description']}")
```

### 7.3 最佳实践

```python
# 获取最佳实践
practices = recommender.get_best_practices(category="performance")

for practice in practices:
    print(f"\n{practice.title}: {practice.description}")
```

### 7.4 算法兼容性分析

```python
# 分析算法兼容性
compatibility = recommender.analyze_algorithm_compatibility(
    algorithm_id="transformer_variant",
    requirements={
        "use_case": "机器翻译",
        "accuracy": 0.95,
        "speed": 50,
        "memory_limit": 500
    }
)

print(f"\n兼容性得分: {compatibility['score']}/100")
print(f"是否推荐: {compatibility['compatible']}")
print(f"原因: {compatibility['reasons']}")
```

---

## 8. 配置管理

### 8.1 使用扩展配置系统

```python
from npu_converter.extensions.config.extended_algorithm_config import (
    ExtendedAlgorithmConfig,
    ParameterDefinition
)

# 定义参数
params = [
    ParameterDefinition("learning_rate", "float", required=True, min_value=0.0001, max_value=1.0, default=0.001),
    ParameterDefinition("batch_size", "int", required=True, min_value=1, max_value=1024, default=32),
    ParameterDefinition("optimizer", "str", required=False, choices=["adam", "sgd", "rmsprop"], default="adam")
]

# 创建配置
config = ExtendedAlgorithmConfig(
    algorithm_id="my_algorithm",
    parameter_definitions=params,
    description="我的算法配置",
    version="1.0.0"
)

# 配置参数
config.configure({
    "learning_rate": 0.01,
    "batch_size": 64
})

# 获取参数值
lr = config.get_config("learning_rate")
print(f"学习率: {lr}")
```

### 8.2 验证配置

```python
# 验证配置
is_valid = config.validate_config({
    "learning_rate": 0.01,
    "batch_size": 64
})

if is_valid:
    print("配置有效")
else:
    print("配置无效")
```

### 8.3 导入导出配置

```python
# 导出配置
exported = config.export_to_dict()
print(f"导出配置: {exported}")

# 从字典导入
config.import_from_dict({
    "algorithm_id": "my_algorithm",
    "parameters": {
        "learning_rate": 0.02,
        "batch_size": 128
    }
})

# 导出到YAML文件
config.export_to_yaml("my_config.yaml")

# 从YAML文件导入
config.import_from_yaml("my_config.yaml")
```

---

## 9. 高级功能

### 9.1 缓存使用

```python
# 启用缓存
adapter._config['enable_cache'] = True
adapter._config['cache_size'] = 1000

# 第一次执行
result1 = adapter.execute("test input", optimization_level=2)

# 第二次执行相同输入（命中缓存）
result2 = adapter.execute("test input", optimization_level=2)

# 清空缓存
adapter.clear_cache()
```

### 9.2 并行处理

```python
from concurrent.futures import ThreadPoolExecutor

def execute_algorithm_batch(inputs):
    """批量执行算法"""
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(lambda x: adapter.execute(x), inputs))
    return results

# 批量处理
batch_inputs = ["input1", "input2", "input3", "input4"]
results = execute_algorithm_batch(batch_inputs)
```

### 9.3 生命周期管理

```python
from npu_converter.extensions.lifecycle.algorithm_lifecycle import AlgorithmLifecycleManager

lifecycle = AlgorithmLifecycleManager()

# 注册生命周期回调
@lifecycle.on_initialize
def on_initialize(algorithm_id):
    print(f"算法 {algorithm_id} 初始化")

@lifecycle.on_execute
def on_execute(algorithm_id, input_data):
    print(f"算法 {algorithm_id} 开始执行")

@lifecycle.on_complete
def on_complete(algorithm_id, result):
    print(f"算法 {algorithm_id} 执行完成")

@lifecycle.on_error
def on_error(algorithm_id, error):
    print(f"算法 {algorithm_id} 执行错误: {error}")
```

### 9.4 事件监听

```python
from npu_converter.extensions.lifecycle.algorithm_lifecycle import EventType

# 监听特定事件
lifecycle.subscribe(EventType.EXECUTE_STARTED, lambda event: print("执行开始"))
lifecycle.subscribe(EventType.EXECUTE_COMPLETED, lambda event: print("执行完成"))

# 发布事件
lifecycle.publish(EventType.EXECUTE_STARTED, {"algorithm_id": "transformer_variant"})
```

---

## 10. 常见问题

### 10.1 如何选择合适的算法？

**根据任务类型**:
- 文本处理 → Transformer变种适配器
- 图像处理 → CNN改进适配器
- 序列预测 → RNN优化适配器

**根据性能要求**:
- 高精度 → 选择高精度算法，使用高级优化
- 高速度 → 选择轻量级算法，使用低精度
- 低内存 → 选择MobileNet等轻量级架构

**使用推荐系统**:
```python
recommendations = recommender.recommend_algorithm(
    use_case="您的任务",
    requirements={"accuracy": 0.95, "speed": 100}
)
```

### 10.2 如何优化性能？

**使用优化级别**:
```python
# 逐步提高优化级别
for level in [0, 1, 2, 3]:
    result = adapter.execute(input, optimization_level=level)
    print(f"级别 {level}: 耗时 {result['execution_time']}")
```

**使用自动调优**:
```python
# 自动寻找最优参数
engine.tune_parameters(config, objective_function)
```

**监控性能**:
```python
# 实时监控性能
analyzer.start_monitoring(["your_algorithm"])
analyzer.record_metric("your_algorithm", "latency", value, "s")
```

### 10.3 如何处理长序列？

**RNN优化**:
```python
adapter.initialize(
    rnn_type="lstm",
    use_truncated_bptt=True,      # 截断BPTT
    truncation_length=100,
    max_sequence_length=10000
)
```

**Transformer优化**:
```python
result = adapter.execute(
    long_sequence,
    optimization_level=3,          # 使用最高优化级别
    precision="fp16"              # 使用混合精度
)
```

### 10.4 如何调试问题？

**启用详细日志**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**检查输入输出**:
```python
# 验证输入
if not adapter.validate_input(input_data):
    print("输入验证失败")

# 验证输出
if not adapter.validate_output(result):
    print("输出验证失败")
```

**查看统计信息**:
```python
stats = adapter.get_statistics()
print(f"执行次数: {stats['statistics']['execution_count']}")
print(f"错误次数: {stats['statistics']['error_count']}")
```

### 10.5 如何处理内存不足？

**使用轻量级算法**:
```python
adapter.initialize(
    architecture="mobilenet",      # 轻量级架构
    use_depthwise=True,           # 深度可分离卷积
    num_layers=10                 # 减少层数
)
```

**使用低精度**:
```python
result = adapter.execute(input, precision="int8")  # INT8量化
```

**分批处理**:
```python
for batch in batches:
    results = execute_algorithm_batch(batch)
    process_results(results)
```

### 10.6 如何实现自定义算法？

**继承基类**:
```python
from npu_converter.extensions.adapters.algorithm_adapter import BaseAlgorithmAdapter

class MyCustomAdapter(BaseAlgorithmAdapter):
    def initialize(self, **kwargs) -> bool:
        # 初始化逻辑
        self.model = load_model(kwargs.get('model_path'))
        return True

    def execute(self, input_data: Any, **kwargs) -> Any:
        # 执行逻辑
        output = self.model.predict(input_data)
        return output

    def validate_input(self, input_data: Any) -> bool:
        # 输入验证
        return isinstance(input_data, np.ndarray)

    def validate_output(self, output_data: Any) -> bool:
        # 输出验证
        return isinstance(output_data, np.ndarray)
```

**注册算法**:
```python
from npu_converter.extensions.algorithm_registry import AlgorithmRegistry

registry = AlgorithmRegistry()
registry.register("my_custom", MyCustomAdapter)
```

**使用算法**:
```python
system = AlgorithmExtensionSystem()
system.initialize()
result = system.execute_algorithm("my_custom", input_data)
```

---

## 参考资料

- [架构文档](../technical/algorithm-extension-system-architecture.md)
- [API参考](../api/algorithm-extension-api.md)
- [示例代码仓库](https://github.com/xlerobot/examples)

---

**用户指南结束**

如有问题，请参考常见问题部分或提交Issue。
