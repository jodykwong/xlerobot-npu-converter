# Parameter Optimization User Guide

**Version**: 1.0.0
**Author**: Story 2.6 Implementation
**Date**: 2025-10-28

---

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [Core Components](#core-components)
4. [Optimization Strategies](#optimization-strategies)
5. [Trade-off Strategies](#trade-off-strategies)
6. [Model Analysis](#model-analysis)
7. [History Management](#history-management)
8. [Report Generation](#report-generation)
9. [Preprocessing Optimization](#preprocessing-optimization)
10. [Best Practices](#best-practices)
11. [Examples](#examples)
12. [API Reference](#api-reference)
13. [Troubleshooting](#troubleshooting)

---

## Introduction

The Parameter Optimization system provides intelligent, automated optimization of NPU model conversion parameters. It supports multiple optimization algorithms, smart model analysis, flexible quality-performance trade-offs, and comprehensive reporting.

### Key Features

- **4 Optimization Algorithms**: Grid Search, Bayesian Optimization, Genetic Algorithm, Random Search
- **Smart Model Analysis**: Automatic model type detection and parameter recommendations
- **Flexible Trade-offs**: Quality-first, performance-first, balanced, resource-saving, or custom strategies
- **History Management**: Track, compare, and rollback optimization runs
- **Multi-format Reports**: HTML, JSON, Markdown, PDF
- **Preprocessing Optimization**: Optimize normalization, resizing, and other preprocessing parameters

### Supported Models

- **SenseVoice ASR**: Automatic speech recognition models
- **VITS-Cantonese TTS**: Cantonese text-to-speech models (primary)
- **Piper VITS TTS**: Alternative TTS models
- **Vision Models**: ResNet, EfficientNet, etc.
- **NLP Models**: BERT, GPT, etc.

---

## Quick Start

### Basic Usage

```python
from npu_converter.optimization import (
    ParameterOptimizer,
    OptimizationStrategy,
    TradeOffStrategy,
    TradeOffConfig
)

# Initialize optimizer
optimizer = ParameterOptimizer()

# Define parameters to optimize
param_space = {
    'quantization_bits': {
        'type': 'choice',
        'values': [8, 16]
    },
    'batch_size': {
        'type': 'choice',
        'values': [16, 32, 64]
    }
}

# Run optimization
result = optimizer.optimize(
    model="path/to/model.onnx",
    param_space=param_space,
    strategy=OptimizationStrategy.BAYESIAN
)

# View results
print(f"Best parameters: {result.best_params}")
print(f"Best accuracy: {result.best_metrics.accuracy:.2%}")
print(f"Improvement: {result.improvement_percentage:.1f}%")
```

### With Trade-off Strategy

```python
# Use quality-first strategy
tradeoff_config = TradeOffConfig.from_strategy(
    TradeOffStrategy.QUALITY_FIRST
)

result = optimizer.optimize(
    model="model.onnx",
    param_space=param_space,
    strategy=OptimizationStrategy.BAYESIAN,
    tradeoff_config=tradeoff_config
)
```

### Generate Report

```python
from npu_converter.optimization import OptimizationReportGenerator

generator = OptimizationReportGenerator()
report_path = generator.generate_report(
    result=result,
    format="html",
    include_charts=True
)

print(f"Report generated: {report_path}")
```

---

## Core Components

### 1. ParameterOptimizer

Main optimizer class that orchestrates the optimization process.

**Key Methods**:

- `optimize()` - Run parameter optimization
- `get_optimization_history()` - Get past optimization results
- `export_results()` - Export results to JSON/YAML
- `clear_history()` - Clear optimization history

**Example**:

```python
from npu_converter.optimization import ParameterOptimizer

optimizer = ParameterOptimizer(
    model_analyzer=my_analyzer,  # Optional
    tradeoff_calculator=my_calculator,  # Optional
    verbose=True
)
```

### 2. ModelAnalyzer

Analyzes model characteristics and provides parameter recommendations.

**Key Methods**:

- `analyze_model()` - Analyze model and extract characteristics
- `recommend_parameters()` - Get recommended parameters
- `get_model_info()` - Get formatted model information

**Example**:

```python
from npu_converter.optimization import ModelAnalyzer

analyzer = ModelAnalyzer()
characteristics = analyzer.analyze_model("model.onnx")

print(f"Model type: {characteristics.model_type.value}")
print(f"Model size: {characteristics.model_size:,} parameters")
print(f"Recommended quantization: {characteristics.recommended_quantization}-bit")
```

### 3. OptimizationHistory

Manages optimization history, versioning, and rollback.

**Key Methods**:

- `record()` - Record optimization result
- `get_version()` - Get specific version
- `compare_versions()` - Compare two versions
- `rollback()` - Rollback to previous version
- `list_versions()` - List all versions

**Example**:

```python
from npu_converter.optimization import OptimizationHistory

history = OptimizationHistory(
    storage_path="./optimization_history",
    format=HistoryStorageFormat.YAML,
    auto_save=True
)

# Record result
version = history.record(
    params=result.best_params,
    metrics={'accuracy': result.best_metrics.accuracy},
    score=result.optimization_result.best_score,
    strategy=result.strategy_used.value,
    objective=result.objective.value,
    model_characteristics={},
    execution_time=result.execution_time
)

# Compare with previous version
comparison = history.compare_versions(previous_version, version)
print(f"Improvement: {comparison.improvement_percentage:.1f}%")
```

### 4. OptimizationReportGenerator

Generates comprehensive optimization reports.

**Key Methods**:

- `generate_report()` - Generate report in specified format

**Example**:

```python
from npu_converter.optimization import OptimizationReportGenerator

generator = OptimizationReportGenerator(output_dir="./reports")

# Generate HTML report with charts
html_report = generator.generate_report(
    result=result,
    format="html",
    include_charts=True,
    include_recommendations=True
)

# Generate JSON report
json_report = generator.generate_report(
    result=result,
    format="json"
)
```

---

## Optimization Strategies

### 1. Grid Search (网格搜索)

**Description**: Exhaustively tests all parameter combinations in a predefined grid.

**Best For**:
- Small parameter spaces (< 100 combinations)
- When you need guaranteed optimal solution
- Baseline comparison

**Example**:

```python
result = optimizer.optimize(
    strategy=OptimizationStrategy.GRID_SEARCH,
    max_iterations=100
)
```

**Characteristics**:
- ✅ Exhaustive search
- ✅ Guarantees optimal solution
- ❌ Slow for large parameter spaces
- ❌ Does not scale well

### 2. Bayesian Optimization (贝叶斯优化)

**Description**: Uses Gaussian Process to model the objective function and acquisition functions to efficiently explore parameter space.

**Best For**:
- Expensive objective functions (> 1 min per evaluation)
- Medium-sized parameter spaces
- When you need fast convergence

**Example**:

```python
result = optimizer.optimize(
    strategy=OptimizationStrategy.BAYESIAN,
    max_iterations=50
)
```

**Characteristics**:
- ✅ Efficient exploration
- ✅ Fast convergence
- ✅ Good for expensive evaluations
- ❌ Requires more initial samples

### 3. Genetic Algorithm (遗传算法)

**Description**: Uses evolutionary algorithms to search for optimal parameters.

**Best For**:
- Complex, non-linear optimization problems
- Mixed parameter types (continuous and discrete)
- When you need global optimization

**Example**:

```python
result = optimizer.optimize(
    strategy=OptimizationStrategy.GENETIC,
    max_iterations=100,
    population_size=20,
    mutation_rate=0.1
)
```

**Characteristics**:
- ✅ Global optimization
- ✅ Handles mixed types
- ✅ Robust to local minima
- ❌ Slower than Bayesian

### 4. Random Search (随机搜索)

**Description**: Randomly samples parameters from the search space.

**Best For**:
- Quick exploration
- Baseline comparison
- Very large parameter spaces

**Example**:

```python
result = optimizer.optimize(
    strategy=OptimizationStrategy.RANDOM,
    max_iterations=100
)
```

**Characteristics**:
- ✅ Fast
- ✅ Simple
- ✅ Good for initial exploration
- ❌ No guarantee of optimality

---

## Trade-off Strategies

### 1. Quality First (质量优先)

**Priority**: Maximize accuracy and model quality

**Weights**:
- Accuracy: 70%
- Latency: 20%
- Throughput: 5%
- Memory: 3%
- Compatibility: 1%
- Success Rate: 1%

**Best For**:
- Production systems where output quality is critical
- TTS models (voice quality important)
- High-stakes applications

**Example**:

```python
from npu_converter.optimization import TradeOffStrategy, TradeOffConfig

config = TradeOffConfig.from_strategy(
    TradeOffStrategy.QUALITY_FIRST
)

result = optimizer.optimize(
    tradeoff_config=config
)
```

### 2. Performance First (性能优先)

**Priority**: Minimize latency and maximize throughput

**Weights**:
- Accuracy: 30%
- Latency: 40%
- Throughput: 20%
- Memory: 5%
- Compatibility: 3%
- Success Rate: 2%

**Best For**:
- Real-time applications
- ASR models (low latency critical)
- Streaming applications

**Example**:

```python
config = TradeOffConfig.from_strategy(
    TradeOffStrategy.PERFORMANCE_FIRST
)
```

### 3. Balanced (平衡)

**Priority**: Balance all objectives evenly

**Weights**:
- Accuracy: 25%
- Latency: 25%
- Throughput: 15%
- Memory: 15%
- Compatibility: 10%
- Success Rate: 10%

**Best For**:
- General-purpose optimization
- Default choice
- When requirements are unclear

**Example**:

```python
config = TradeOffConfig.from_strategy(
    TradeOffStrategy.BALANCED
)
```

### 4. Resource Saving (资源节约)

**Priority**: Minimize resource usage

**Weights**:
- Accuracy: 20%
- Latency: 15%
- Throughput: 10%
- Memory: 35%
- Compatibility: 10%
- Success Rate: 10%

**Best For**:
- Edge devices
- Constrained environments
- Mobile deployments

**Example**:

```python
config = TradeOffConfig.from_strategy(
    TradeOffStrategy.RESOURCE_SAVING
)
```

### 5. Custom Strategy

**Priority**: User-defined weights

**Example**:

```python
from npu_converter.optimization import TradeOffWeights, TradeOffConfig

weights = TradeOffWeights(
    accuracy=0.6,
    latency=0.3,
    throughput=0.05,
    memory=0.025,
    compatibility=0.015,
    success_rate=0.01
)

config = TradeOffConfig.from_custom_weights(weights)
```

---

## Model Analysis

### Automatic Model Type Detection

The system automatically detects model types:

- **ASR**: SenseVoice, Whisper, speech recognition models
- **TTS**: VITS, speech synthesis models
- **Vision**: ResNet, EfficientNet, CNN models
- **NLP**: BERT, GPT, transformer models

### Model Characteristics

**Detected Characteristics**:

- **Model Size**: Number of parameters
- **File Size**: Model file size in bytes
- **Complexity Score**: 0.0 - 1.0 (higher = more complex)
- **Quantization Sensitivity**: 0.0 - 1.0 (higher = more sensitive to quantization)
- **Layer Types**: Distribution of layer types
- **Operators**: Distribution of operators
- **Input/Output Shapes**: Model I/O shapes
- **Architecture Features**: Transformer, Conv layers, RNN layers

### Parameter Recommendations

The system provides intelligent parameter recommendations:

```python
analyzer = ModelAnalyzer()
characteristics = analyzer.analyze_model("model.onnx")

param_space = {
    'quantization_bits': {'type': 'choice', 'values': [8, 16]},
    'learning_rate': {'type': 'float', 'bounds': [1e-5, 1e-2]}
}

recommendations = analyzer.recommend_parameters(
    param_space,
    characteristics
)

print(f"Recommended quantization: {recommendations['quantization_bits']}")
print(f"Recommended learning rate: {recommendations['learning_rate']}")
```

---

## History Management

### Recording Results

```python
from npu_converter.optimization import OptimizationHistory

history = OptimizationHistory()

version = history.record(
    params=result.best_params,
    metrics={
        'accuracy': result.best_metrics.accuracy,
        'latency': result.best_metrics.latency,
        'throughput': result.best_metrics.throughput
    },
    score=result.optimization_result.best_score,
    strategy=result.strategy_used.value,
    objective=result.objective.value,
    model_characteristics=result.model_characteristics.__dict__,
    execution_time=result.execution_time,
    recommendations=result.recommendations,
    user_notes="Optimization run #1",
    tags=["stable", "production"]
)
```

### Listing Versions

```python
# List all versions
versions = history.list_versions()
print(f"Total versions: {len(versions)}")

# List latest 5 versions
latest_versions = history.list_versions(limit=5)

# Filter by tag
stable_versions = history.list_versions(tag="stable")
```

### Comparing Versions

```python
comparison = history.compare_versions(version1, version2)

print(f"Version {comparison.version1} vs {comparison.version2}")
print(f"Score difference: {comparison.score_difference:.3f}")
print(f"Improvement: {comparison.improvement_percentage:.1f}%")
print(f"Parameter changes: {comparison.param_differences}")
print(f"Metric changes: {comparison.metric_differences}")
print(f"Significant changes: {comparison.significant_changes}")
```

### Rolling Back

```python
# Rollback to previous version
rollback_version = "1.5"
result = history.rollback(rollback_version)

if result:
    print(f"Successfully rolled back to {rollback_version}")
else:
    print(f"Failed to rollback to {rollback_version}")
```

### Tagging Versions

```python
from npu_converter.optimization import VersionTag

# Tag as best result
history.tag_version(version, VersionTag.BEST, "Best accuracy achieved")

# Tag as stable
history.tag_version(version, VersionTag.STABLE, "Passed all tests")

# Tag as failed
history.tag_version(version, VersionTag.FAILED, "Did not meet requirements")
```

### Exporting History

```python
# Export specific version
yaml_export = history.export_version(version, "yaml")
json_export = history.export_version(version, "json")

# Export all history
all_history = history.export_all("yaml")

# Save to file
with open("optimization_history.yaml", "w") as f:
    f.write(all_history)
```

### Statistics

```python
stats = history.get_statistics()

print(f"Total runs: {stats['count']}")
print(f"Latest version: {stats['latest_version']}")
print(f"Average score: {stats['average_score']:.3f}")
print(f"Best score: {stats['best_score']:.3f}")
print(f"Total execution time: {stats['total_execution_time']:.2f}s")
print(f"Average execution time: {stats['average_execution_time']:.2f}s")
print(f"Strategies used: {stats['strategies_used']}")
print(f"Tags used: {stats['tags_used']}")
```

---

## Report Generation

### HTML Report (Recommended)

```python
from npu_converter.optimization import OptimizationReportGenerator

generator = OptimizationReportGenerator(output_dir="./reports")

html_path = generator.generate_report(
    result=result,
    format="html",
    include_charts=True,  # Includes convergence plots and metrics charts
    include_recommendations=True
)

print(f"HTML report: {html_path}")
```

**HTML Report Features**:
- Beautiful styling with CSS
- Interactive charts (if matplotlib available)
- Parameter tables
- Metrics summary
- Recommendations section
- Model characteristics
- Fully self-contained (open in browser)

### JSON Report

```python
json_path = generator.generate_report(
    result=result,
    format="json",
    include_charts=False
)
```

**Use Cases**:
- Machine-readable format
- Integration with other tools
- Data analysis
- Automated processing

### Markdown Report

```python
md_path = generator.generate_report(
    result=result,
    format="markdown"
)
```

**Use Cases**:
- Lightweight documentation
- Version control friendly
- Easy to read
- Convert to PDF

### PDF Report

```python
pdf_path = generator.generate_report(
    result=result,
    format="pdf"
)
```

**Note**: Currently generates HTML and copies to PDF path. Future versions will support actual PDF conversion.

---

## Preprocessing Optimization

### Basic Preprocessing Optimization

```python
from npu_converter.optimization import PreprocessingOptimizer

preprocessor = PreprocessingOptimizer()

# Get model characteristics
analyzer = ModelAnalyzer()
characteristics = analyzer.analyze_model("model.onnx")

# Optimize preprocessing parameters
params = preprocessor.optimize_preprocessing(
    model_characteristics=characteristics.__dict__,
    target_metric="compatibility"  # or "accuracy", "speed"
)

print(f"Optimized parameters: {params}")
```

### Preprocessing Parameters

**Supported Parameters**:

- **normalize**: Enable/disable normalization
- **normalize_mode**: "imagenet", "custom"
- **mean**: Normalization mean values
- **std**: Normalization standard deviation
- **resize**: Image resize dimensions (for vision models)
- **channel_format**: "NCHW", "NHWC", "NC"
- **target_format**: Target channel format
- **data_type**: "float32", "int64", "int32"
- **sample_rate**: Audio sample rate (for audio models)
- **window_size**: FFT window size
- **hop_length**: FFT hop length

### Model-Specific Presets

```python
# For ASR models
params = preprocessor.optimize_preprocessing(
    model_characteristics=characteristics.__dict__,
    preset="asr"  # Audio-specific optimization
)

# For TTS models
params = preprocessor.optimize_preprocessing(
    model_characteristics=characteristics.__dict__,
    preset="tts"  # TTS-specific optimization
)

# For Vision models
params = preprocessor.optimize_preprocessing(
    model_characteristics=characteristics.__dict__,
    preset="vision"  # Vision-specific optimization
)

# For NLP models
params = preprocessor.optimize_preprocessing(
    model_characteristics=characteristics.__dict__,
    preset="nlp"  # NLP-specific optimization
)
```

### Custom Optimization Configuration

```python
from npu_converter.optimization import PreprocessingOptimizationConfig

config = PreprocessingOptimizationConfig(
    optimize_normalization=True,
    optimize_resize=True,
    optimize_channel_format=True,
    optimize_data_type=True,
    respect_model_constraints=True,
    preset="asr"
)

params = preprocessor.optimize_preprocessing(
    model_characteristics=characteristics.__dict__,
    config=config
)
```

### Validation

```python
# Validate optimized parameters
errors = preprocessor.validate_preprocessing_params(
    params,
    model_type="asr"
)

if errors:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error}")
else:
    print("All parameters are valid!")
```

### Recommendations

```python
# Get preprocessing recommendations
recommendations = preprocessor.get_preprocessing_recommendations(
    model_characteristics=characteristics.__dict__
)

print("Recommendations:")
for rec in recommendations:
    print(f"  - {rec}")
```

---

## Best Practices

### 1. Choose the Right Optimization Strategy

| Scenario | Recommended Strategy | Reason |
|----------|---------------------|--------|
| Small parameter space (< 50 combos) | Grid Search | Guarantees optimal solution |
| Expensive evaluation (> 1 min) | Bayesian | Efficient exploration |
| Complex non-linear problem | Genetic Algorithm | Global optimization |
| Quick baseline | Random Search | Fast and simple |
| Default choice | Bayesian | Good balance of speed and quality |

### 2. Set Appropriate Iterations

- **Grid Search**: 10 - 100 (depends on grid size)
- **Bayesian**: 20 - 50 (good convergence)
- **Genetic Algorithm**: 50 - 200 (depends on population)
- **Random Search**: 50 - 200 (more iterations = better coverage)

### 3. Choose Trade-off Strategy Based on Use Case

| Use Case | Strategy | Notes |
|----------|----------|-------|
| Real-time ASR | Performance First | Latency < 100ms critical |
| TTS Production | Quality First | Audio quality paramount |
| General Purpose | Balanced | Good default |
| Edge Device | Resource Saving | Minimize memory |

### 4. Use History Management

- Always record optimization runs
- Use meaningful tags ("stable", "production", "failed")
- Add user notes for context
- Compare versions to track improvement
- Tag best results for easy retrieval

### 5. Validate Results

- Check metrics make sense
- Validate parameters
- Run multiple optimizations
- Compare with manual tuning
- Test on real data

### 6. Use Reports

- Generate HTML reports for analysis
- Include charts for visual inspection
- Share reports with team
- Archive reports for future reference

---

## Examples

### Example 1: SenseVoice ASR Optimization

```python
from npu_converter.optimization import (
    ParameterOptimizer,
    ModelAnalyzer,
    OptimizationStrategy,
    TradeOffStrategy,
    TradeOffConfig,
    OptimizationHistory,
    OptimizationReportGenerator
)

# Initialize components
analyzer = ModelAnalyzer()
optimizer = ParameterOptimizer()
history = OptimizationHistory()
generator = OptimizationReportGenerator()

# Analyze model
model_path = "path/to/sensevoice_asr.onnx"
characteristics = analyzer.analyze_model(model_path)

print(f"Detected model: {characteristics.model_type.value}")
print(f"Model size: {characteristics.model_size:,} parameters")
print(f"Recommended quantization: {characteristics.recommended_quantization}-bit")

# Define parameter space
param_space = {
    'quantization_bits': {
        'type': 'choice',
        'values': [8, 16]
    },
    'batch_size': {
        'type': 'choice',
        'values': [16, 32, 64]
    },
    'sample_rate': {
        'type': 'choice',
        'values': [16000, 22050]
    }
}

# Configure trade-off (ASR needs low latency)
tradeoff_config = TradeOffConfig.from_strategy(
    TradeOffStrategy.PERFORMANCE_FIRST
)

# Run optimization
result = optimizer.optimize(
    model=model_path,
    param_space=param_space,
    strategy=OptimizationStrategy.BAYESIAN,
    tradeoff_config=tradeoff_config,
    max_iterations=50
)

# Print results
print("\n=== Optimization Results ===")
print(f"Best parameters: {result.best_params}")
print(f"Accuracy: {result.best_metrics.accuracy:.2%}")
print(f"Latency: {result.best_metrics.latency:.1f} ms")
print(f"Throughput: {result.best_metrics.throughput:.1f} samples/sec")
print(f"Success rate: {result.best_metrics.success_rate:.2%}")
print(f"Improvement: {result.improvement_percentage:.1f}%")
print(f"Execution time: {result.execution_time:.2f} seconds")

# Record in history
version = history.record(
    params=result.best_params,
    metrics={
        'accuracy': result.best_metrics.accuracy,
        'latency': result.best_metrics.latency,
        'throughput': result.best_metrics.throughput,
        'memory': result.best_metrics.memory_usage,
        'compatibility': result.best_metrics.compatibility,
        'success_rate': result.best_metrics.success_rate
    },
    score=result.optimization_result.best_score,
    strategy=result.strategy_used.value,
    objective=result.objective.value,
    model_characteristics=characteristics.__dict__,
    execution_time=result.execution_time,
    recommendations=result.recommendations,
    tags=["asr", "production"],
    user_notes="ASR optimization for real-time use"
)

print(f"\nRecorded to history: {version}")

# Generate report
report_path = generator.generate_report(
    result=result,
    format="html",
    include_charts=True,
    include_recommendations=True
)

print(f"Report generated: {report_path}")
```

### Example 2: VITS-Cantonese TTS Optimization

```python
# Initialize components
analyzer = ModelAnalyzer()
optimizer = ParameterOptimizer()

# Analyze model
model_path = "path/to/vits_cantonese.onnx"
characteristics = analyzer.analyze_model(model_path)

# Define parameter space
param_space = {
    'quantization_bits': {
        'type': 'choice',
        'values': [8, 16]  # TTS prefers 16-bit for quality
    },
    'sample_rate': {
        'type': 'choice',
        'values': [22050, 44100]
    },
    'n_mels': {
        'type': 'choice',
        'values': [80, 128, 256]
    }
}

# Configure trade-off (TTS prioritizes quality)
tradeoff_config = TradeOffConfig.from_strategy(
    TradeOffStrategy.QUALITY_FIRST
)

# Run optimization
result = optimizer.optimize(
    model=model_path,
    param_space=param_space,
    strategy=OptimizationStrategy.BAYESIAN,
    tradeoff_config=tradeoff_config,
    max_iterations=50
)

# Print results
print("\n=== VITS-Cantonese Optimization Results ===")
print(f"Best parameters: {result.best_params}")
print(f"Audio quality score: {result.best_metrics.accuracy:.2%}")
print(f"Synthesis latency: {result.best_metrics.latency:.1f} ms")
print(f"Quality/performance balance: {result.improvement_percentage:.1f}% improvement")

# Generate report
generator = OptimizationReportGenerator()
report_path = generator.generate_report(
    result=result,
    format="html"
)

print(f"Report: {report_path}")
```

### Example 3: Compare Optimization Strategies

```python
# Compare different strategies
strategies = [
    ("Grid Search", OptimizationStrategy.GRID_SEARCH),
    ("Bayesian", OptimizationStrategy.BAYESIAN),
    ("Random", OptimizationStrategy.RANDOM)
]

results = {}

param_space = {
    'quantization_bits': {
        'type': 'choice',
        'values': [8, 16]
    },
    'batch_size': {
        'type': 'choice',
        'values': [16, 32, 64]
    }
}

model_path = "path/to/model.onnx"

print("\n=== Strategy Comparison ===")
for name, strategy in strategies:
    result = optimizer.optimize(
        model=model_path,
        param_space=param_space,
        strategy=strategy,
        max_iterations=20
    )

    results[name] = result

    print(f"\n{name}:")
    print(f"  Best score: {result.optimization_result.best_score:.4f}")
    print(f"  Iterations: {result.optimization_result.iterations}")
    print(f"  Time: {result.execution_time:.2f}s")
    print(f"  Accuracy: {result.best_metrics.accuracy:.2%}")

# Compare results
print("\n=== Strategy Comparison Summary ===")
for name, result in results.items():
    print(f"{name:15s}: Score={result.optimization_result.best_score:.4f}, "
          f"Time={result.execution_time:.2f}s")
```

### Example 4: Custom Trade-off Strategy

```python
from npu_converter.optimization import TradeOffWeights

# Create custom trade-off: 60% accuracy, 30% latency, 10% others
custom_weights = TradeOffWeights(
    accuracy=0.6,
    latency=0.3,
    throughput=0.05,
    memory=0.025,
    compatibility=0.015,
    success_rate=0.01
)

tradeoff_config = TradeOffConfig.from_custom_weights(custom_weights)

result = optimizer.optimize(
    model=model_path,
    param_space=param_space,
    strategy=OptimizationStrategy.BAYESIAN,
    tradeoff_config=tradeoff_config
)

print(f"Custom trade-off optimization:")
print(f"  Accuracy: {result.best_metrics.accuracy:.2%}")
print(f"  Latency: {result.best_metrics.latency:.1f} ms")
```

### Example 5: Full Workflow with History and Reports

```python
from npu_converter.optimization import (
    ParameterOptimizer,
    ModelAnalyzer,
    OptimizationHistory,
    OptimizationReportGenerator,
    TradeOffStrategy,
    TradeOffConfig,
    OptimizationStrategy,
    VersionTag
)

# Initialize all components
analyzer = ModelAnalyzer()
optimizer = ParameterOptimizer()
history = OptimizationHistory()
generator = OptimizationReportGenerator()

# Model path
model_path = "path/to/model.onnx"

# Run multiple optimizations
for i in range(3):
    print(f"\n=== Optimization Run {i+1} ===")

    # Analyze model
    characteristics = analyzer.analyze_model(model_path)

    # Define parameter space
    param_space = {
        'quantization_bits': {
            'type': 'choice',
            'values': [8, 16]
        },
        'batch_size': {
            'type': 'choice',
            'values': [16, 32, 64]
        }
    }

    # Use balanced strategy
    tradeoff_config = TradeOffConfig.from_strategy(
        TradeOffStrategy.BALANCED
    )

    # Run optimization
    result = optimizer.optimize(
        model=model_path,
        param_space=param_space,
        strategy=OptimizationStrategy.BAYESIAN,
        tradeoff_config=tradeoff_config,
        max_iterations=30
    )

    # Record in history
    version = history.record(
        params=result.best_params,
        metrics={
            'accuracy': result.best_metrics.accuracy,
            'latency': result.best_metrics.latency,
            'throughput': result.best_metrics.throughput
        },
        score=result.optimization_result.best_score,
        strategy=result.strategy_used.value,
        objective=result.objective.value,
        model_characteristics=characteristics.__dict__,
        execution_time=result.execution_time,
        recommendations=result.recommendations,
        tags=[f"run_{i+1}"],
        user_notes=f"Optimization run #{i+1}"
    )

    # Tag best result
    if i == 1:  # Middle run
        history.tag_version(version, VersionTag.BEST, "Best result so far")
        print(f"Tagged as best: {version}")

    # Generate individual report
    report_path = generator.generate_report(
        result=result,
        format="html"
    )

    print(f"Result: {result.best_params}")
    print(f"Report: {report_path}")
    print(f"History: {version}")

# Final history analysis
print("\n=== Final History Analysis ===")

versions = history.list_versions()
print(f"Total runs: {len(versions)}")

# Compare first and last
comparison = history.compare_versions(versions[0], versions[-1])
print(f"\nComparison: {versions[0]} vs {versions[-1]}")
print(f"  Score difference: {comparison.score_difference:.4f}")
print(f"  Improvement: {comparison.improvement_percentage:.1f}%")
print(f"  Significant changes: {comparison.significant_changes}")

# Get statistics
stats = history.get_statistics()
print(f"\nStatistics:")
print(f"  Average score: {stats['average_score']:.4f}")
print(f"  Best score: {stats['best_score']:.4f}")
print(f"  Total time: {stats['total_execution_time']:.2f}s")
print(f"  Strategies used: {stats['strategies_used']}")

# Export all history
export_path = f"{model_path}_history.yaml"
with open(export_path, "w") as f:
    f.write(history.export_all("yaml"))

print(f"\nHistory exported to: {export_path}")

# Generate final report
print("\n=== Generating Final Report ===")
# Use the last result for final report
final_report = generator.generate_report(
    result=result,
    format="html",
    include_charts=True,
    include_recommendations=True
)

print(f"Final report: {final_report}")
print("\n✅ Complete optimization workflow finished!")
```

---

## API Reference

### ParameterOptimizer

```python
class ParameterOptimizer:
    def __init__(
        self,
        model_analyzer: Optional[ModelAnalyzer] = None,
        tradeoff_calculator: Optional[TradeOffCalculator] = None,
        verbose: bool = True
    )

    def optimize(
        self,
        model: Any,
        param_space: Dict[str, Any],
        objective: OptimizationObjective = OptimizationObjective.BALANCED,
        strategy: OptimizationStrategy = OptimizationStrategy.BAYESIAN,
        config: Optional[OptimizationConfig] = None,
        tradeoff_config: Optional[TradeOffConfig] = None,
        max_iterations: Optional[int] = None,
        initial_params: Optional[Dict[str, Any]] = None
    ) -> ParameterOptimizationResult

    def get_optimization_history(self) -> List[ParameterOptimizationResult]

    def clear_history(self) -> None

    def export_results(
        self,
        result: ParameterOptimizationResult,
        format: str = "json"
    ) -> str
```

### ModelAnalyzer

```python
class ModelAnalyzer:
    def __init__(self)

    def analyze_model(
        self,
        model: Any
    ) -> ModelCharacteristics

    def recommend_parameters(
        self,
        param_space: Dict[str, Any],
        model_characteristics: ModelCharacteristics
    ) -> Dict[str, Any]

    def get_model_info(
        self,
        characteristics: ModelCharacteristics
    ) -> Dict[str, Any]
```

### OptimizationHistory

```python
class OptimizationHistory:
    def __init__(
        self,
        storage_path: Optional[str] = None,
        format: HistoryStorageFormat = HistoryStorageFormat.YAML,
        auto_save: bool = True
    )

    def record(
        self,
        params: Dict[str, Any],
        metrics: Dict[str, float],
        score: float,
        strategy: str,
        objective: str,
        model_characteristics: Dict[str, Any],
        execution_time: float,
        recommendations: Optional[List[str]] = None,
        user_notes: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> str

    def get_version(self, version: str) -> Optional[OptimizationEntry]

    def get_latest(self) -> Optional[OptimizationEntry]

    def list_versions(
        self,
        limit: Optional[int] = None,
        tag: Optional[str] = None
    ) -> List[str]

    def compare_versions(
        self,
        version1: str,
        version2: str
    ) -> Optional[VersionComparison]

    def rollback(self, version: str) -> bool

    def tag_version(
        self,
        version: str,
        tag: VersionTag,
        note: str = ""
    ) -> bool

    def export_version(
        self,
        version: str,
        format: str = "yaml"
    ) -> Optional[str]

    def export_all(self, format: str = "yaml") -> str

    def clear(self, confirm: bool = False) -> bool

    def save(self) -> bool

    def get_statistics(self) -> Dict[str, Any]
```

### OptimizationReportGenerator

```python
class OptimizationReportGenerator:
    def __init__(self, output_dir: Optional[str] = None)

    def generate_report(
        self,
        result: ParameterOptimizationResult,
        format: str = "html",
        include_charts: bool = True,
        include_recommendations: bool = True
    ) -> str
```

### PreprocessingOptimizer

```python
class PreprocessingOptimizer:
    def __init__(self)

    def optimize_preprocessing(
        self,
        model_characteristics: Dict[str, Any],
        target_metric: str = "compatibility",
        config: Optional[PreprocessingOptimizationConfig] = None
    ) -> Dict[str, Any]

    def validate_preprocessing_params(
        self,
        params: Dict[str, Any],
        model_type: str
    ) -> List[str]

    def get_preprocessing_recommendations(
        self,
        model_characteristics: Dict[str, Any]
    ) -> List[str]
```

---

## Troubleshooting

### Common Issues

#### 1. Optimization Not Converging

**Symptoms**: Optimization continues for many iterations without improvement

**Solutions**:
- Increase convergence threshold
- Reduce max iterations
- Check parameter space bounds
- Try different strategy

```python
# Reduce iterations and tighten threshold
config = OptimizationConfig(
    max_iterations=50,
    convergence_threshold=0.005,
    early_stopping=True,
    patience=5
)

result = optimizer.optimize(
    strategy=OptimizationStrategy.BAYESIAN,
    config=config
)
```

#### 2. Poor Parameter Recommendations

**Symptoms**: Recommendations don't seem optimal

**Solutions**:
- Provide more training data
- Adjust model analysis settings
- Use custom recommendations

```python
# Provide custom initial parameters
initial_params = {
    'quantization_bits': 16,  # Your preferred value
    'batch_size': 32
}

result = optimizer.optimize(
    initial_params=initial_params
)
```

#### 3. Validation Errors

**Symptoms**: Parameter validation fails

**Solutions**:
- Check parameter space bounds
- Verify model constraints
- Use `respect_model_constraints=True`

```python
config = PreprocessingOptimizationConfig(
    respect_model_constraints=True
)
```

#### 4. History Not Saving

**Symptoms**: Optimization history not persisting

**Solutions**:
- Check storage path permissions
- Enable auto_save
- Call save() manually

```python
history = OptimizationHistory(
    storage_path="/valid/path",
    auto_save=True
)

# Or save manually
history.save()
```

#### 5. Report Generation Fails

**Symptoms**: Error generating reports

**Solutions**:
- Check output directory permissions
- Install optional dependencies (matplotlib)
- Use simpler format (JSON/Markdown)

```python
# Use JSON if HTML fails
report = generator.generate_report(
    result=result,
    format="json"  # More reliable than HTML
)
```

### Debug Tips

#### Enable Verbose Logging

```python
optimizer = ParameterOptimizer(verbose=True)

# Check logs for detailed information
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Inspect Optimization History

```python
# View optimization history
history = optimizer.get_optimization_history()

for result in history:
    print(f"Strategy: {result.strategy_used.value}")
    print(f"Score: {result.optimization_result.best_score}")
    print(f"Time: {result.execution_time:.2f}s")
```

#### Check Model Analysis

```python
# Get detailed model info
analyzer = ModelAnalyzer()
characteristics = analyzer.analyze_model(model)

info = analyzer.get_model_info(characteristics)
print(json.dumps(info, indent=2))
```

---

## Support

For issues, questions, or contributions:

- **Documentation**: This guide
- **Examples**: See `examples/optimization_example.py`
- **Tests**: See `tests/integration/optimization/`

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-28
**Status**: ✅ Complete
