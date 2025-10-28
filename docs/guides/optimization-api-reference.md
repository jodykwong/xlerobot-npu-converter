# Parameter Optimization API Reference

**Version**: 1.0.0
**Author**: Story 2.6 Implementation
**Date**: 2025-10-28

---

## Table of Contents

1. [Overview](#overview)
2. [Core Classes](#core-classes)
3. [Data Models](#data-models)
4. [Enumerations](#enumerations)
5. [Functions](#functions)
6. [Configuration](#configuration)
7. [Complete Examples](#complete-examples)

---

## Overview

The Parameter Optimization module provides a comprehensive set of classes for optimizing NPU model conversion parameters. The API is organized into several key components:

- **ParameterOptimizer**: Main optimization engine
- **ModelAnalyzer**: Model analysis and parameter recommendation
- **OptimizationHistory**: History tracking and versioning
- **ReportGenerator**: Multi-format report generation
- **Strategy Classes**: Various optimization algorithms

---

## Core Classes

### ParameterOptimizer

**Description**: Main parameter optimizer class that orchestrates the optimization process.

**Location**: `src/npu_converter/optimization/parameter_optimizer.py`

#### Constructor

```python
class ParameterOptimizer:
    def __init__(
        self,
        model_analyzer: Optional[ModelAnalyzer] = None,
        tradeoff_calculator: Optional[TradeOffCalculator] = None,
        verbose: bool = True
    ) -> None
```

**Parameters**:
- `model_analyzer`: Optional ModelAnalyzer instance. If None, a new one will be created.
- `tradeoff_calculator`: Optional TradeOffCalculator instance. If None, a new one will be created.
- `verbose`: Enable verbose logging (default: True).

#### Methods

##### optimize()

```python
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
```

**Description**: Run parameter optimization.

**Parameters**:
- `model`: ONNX model or model path
- `param_space`: Dictionary defining parameter search space
  ```python
  {
      'param_name': {
          'type': 'float' | 'int' | 'choice',
          'bounds': (min, max),  # for float/int
          'values': [list],      # for choice
          'default': value       # optional
      }
  }
  ```
- `objective`: Optimization objective (default: BALANCED)
- `strategy`: Optimization strategy (default: BAYESIAN)
- `config`: Optimization configuration (optional)
- ` tradeoff_config`: Trade-off configuration (optional)
- `max_iterations`: Override max iterations (optional)
- `initial_params`: Initial parameter values (optional)

**Returns**: `ParameterOptimizationResult` containing optimized parameters and metrics.

**Example**:

```python
optimizer = ParameterOptimizer()
result = optimizer.optimize(
    model="model.onnx",
    param_space={
        'quantization_bits': {
            'type': 'choice',
            'values': [8, 16]
        }
    },
    strategy=OptimizationStrategy.BAYESIAN
)

print(f"Best params: {result.best_params}")
```

##### get_optimization_history()

```python
def get_optimization_history(self) -> List[ParameterOptimizationResult]
```

**Description**: Get list of past optimization results.

**Returns**: List of `ParameterOptimizationResult` objects.

##### clear_history()

```python
def clear_history(self) -> None
```

**Description**: Clear optimization history.

##### export_results()

```python
def export_results(
    self,
    result: ParameterOptimizationResult,
    format: str = "json"
) -> str
```

**Description**: Export optimization results.

**Parameters**:
- `result`: ParameterOptimizationResult to export
- `format`: "json" or "yaml"

**Returns**: Exported data as string.

---

### ModelAnalyzer

**Description**: Analyzes model characteristics and provides parameter recommendations.

**Location**: `src/npu_converter/optimization/model_analyzer.py`

#### Constructor

```python
class ModelAnalyzer:
    def __init__(self) -> None
```

#### Methods

##### analyze_model()

```python
def analyze_model(self, model: Any) -> ModelCharacteristics
```

**Description**: Analyze model and extract characteristics.

**Parameters**:
- `model`: ONNX model or model path

**Returns**: `ModelCharacteristics` object.

**Example**:

```python
analyzer = ModelAnalyzer()
characteristics = analyzer.analyze_model("model.onnx")

print(f"Model type: {characteristics.model_type.value}")
print(f"Model size: {characteristics.model_size:,} parameters")
```

##### recommend_parameters()

```python
def recommend_parameters(
    self,
    param_space: Dict[str, Any],
    model_characteristics: ModelCharacteristics
) -> Dict[str, Any]
```

**Description**: Recommend optimal parameters for a model.

**Parameters**:
- `param_space`: Parameter space definition
- `model_characteristics`: Model characteristics from analyze_model()

**Returns**: Dictionary of recommended parameter values.

##### get_model_info()

```python
def get_model_info(
    self,
    characteristics: ModelCharacteristics
) -> Dict[str, Any]
```

**Description**: Get formatted model information.

**Parameters**:
- `characteristics`: Model characteristics

**Returns**: Dictionary with formatted model information.

---

### OptimizationHistory

**Description**: Manages optimization history with versioning and rollback capabilities.

**Location**: `src/npu_converter/optimization/history_manager.py`

#### Constructor

```python
class OptimizationHistory:
    def __init__(
        self,
        storage_path: Optional[str] = None,
        format: HistoryStorageFormat = HistoryStorageFormat.YAML,
        auto_save: bool = True
    ) -> None
```

**Parameters**:
- `storage_path`: Path to storage directory (default: ~/.npu_converter/optimization_history)
- `format`: Storage format (YAML or JSON)
- `auto_save`: Automatically save changes to disk

#### Methods

##### record()

```python
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
```

**Description**: Record optimization result in history.

**Parameters**:
- `params`: Parameter values
- `metrics`: Optimization metrics
- `score`: Optimization score
- `strategy`: Optimization strategy used
- `objective`: Optimization objective
- `model_characteristics`: Model characteristics
- `execution_time`: Execution time in seconds
- `recommendations`: Optimization recommendations (optional)
- `user_notes`: User notes (optional)
- `tags`: Version tags (optional)

**Returns**: Version string of the recorded entry.

**Example**:

```python
history = OptimizationHistory()
version = history.record(
    params={'quantization_bits': 16},
    metrics={'accuracy': 0.95},
    score=0.15,
    strategy='bayesian',
    objective='balanced',
    model_characteristics={},
    execution_time=10.5,
    tags=['stable']
)
```

##### get_version()

```python
def get_version(self, version: str) -> Optional[OptimizationEntry]
```

**Description**: Get optimization entry by version.

**Parameters**:
- `version`: Version string

**Returns**: OptimizationEntry or None if not found.

##### get_latest()

```python
def get_latest(self) -> Optional[OptimizationEntry]
```

**Description**: Get latest optimization entry.

**Returns**: Latest OptimizationEntry or None if history is empty.

##### list_versions()

```python
def list_versions(
    self,
    limit: Optional[int] = None,
    tag: Optional[str] = None
) -> List[str]
```

**Description**: List all versions in history.

**Parameters**:
- `limit`: Maximum number of versions to return (optional)
- `tag`: Filter by tag (optional)

**Returns**: List of version strings.

##### compare_versions()

```python
def compare_versions(
    self,
    version1: str,
    version2: str
) -> Optional[VersionComparison]
```

**Description**: Compare two optimization versions.

**Parameters**:
- `version1`: First version
- `version2`: Second version

**Returns**: VersionComparison or None if error.

##### rollback()

```python
def rollback(self, version: str) -> bool
```

**Description**: Rollback to a previous version.

**Parameters**:
- `version`: Target version to rollback to

**Returns**: True if successful, False otherwise.

##### tag_version()

```python
def tag_version(
    self,
    version: str,
    tag: VersionTag,
    note: str = ""
) -> bool
```

**Description**: Tag a version.

**Parameters**:
- `version`: Version to tag
- `tag`: Tag to apply
- `note`: Optional note

**Returns**: True if successful.

##### get_best_version()

```python
def get_best_version(self, metric: str = "score") -> Optional[str]
```

**Description**: Get version with best score for a metric.

**Parameters**:
- `metric`: Metric to optimize (score, accuracy, latency, etc.)

**Returns**: Version string of best entry.

##### export_version()

```python
def export_version(
    self,
    version: str,
    format: str = "yaml"
) -> Optional[str]
```

**Description**: Export specific version to string.

**Parameters**:
- `version`: Version to export
- `format`: Export format (yaml or json)

**Returns**: Exported data as string or None if error.

##### export_all()

```python
def export_all(self, format: str = "yaml") -> str
```

**Description**: Export all history.

**Parameters**:
- `format`: Export format (yaml or json)

**Returns**: Exported data as string.

##### clear()

```python
def clear(self, confirm: bool = False) -> bool
```

**Description**: Clear all history.

**Parameters**:
- `confirm`: Must be True to actually clear

**Returns**: True if successful.

##### save()

```python
def save(self) -> bool
```

**Description**: Save history to disk.

**Returns**: True if successful.

##### get_statistics()

```python
def get_statistics(self) -> Dict[str, Any]
```

**Description**: Get history statistics.

**Returns**: Dictionary with statistics.

---

### OptimizationReportGenerator

**Description**: Generates comprehensive optimization reports.

**Location**: `src/npu_converter/optimization/report_generator.py`

#### Constructor

```python
class OptimizationReportGenerator:
    def __init__(self, output_dir: Optional[str] = None) -> None
```

**Parameters**:
- `output_dir`: Output directory for reports (default: ./reports)

#### Methods

##### generate_report()

```python
def generate_report(
    self,
    result: ParameterOptimizationResult,
    format: str = "html",
    include_charts: bool = True,
    include_recommendations: bool = True
) -> str
```

**Description**: Generate optimization report.

**Parameters**:
- `result`: ParameterOptimizationResult instance
- `format`: Output format (json, html, markdown, pdf)
- `include_charts`: Include visualization charts (default: True)
- `include_recommendations`: Include recommendations section (default: True)

**Returns**: Path to generated report file.

**Example**:

```python
generator = OptimizationReportGenerator()
report_path = generator.generate_report(
    result=result,
    format="html",
    include_charts=True
)

print(f"Report generated: {report_path}")
```

---

### PreprocessingOptimizer

**Description**: Optimizer for preprocessing parameters.

**Location**: `src/npu_converter/optimization/preprocessing_integration.py`

#### Constructor

```python
class PreprocessingOptimizer:
    def __init__(self) -> None
```

#### Methods

##### optimize_preprocessing()

```python
def optimize_preprocessing(
    self,
    model_characteristics: Dict[str, Any],
    target_metric: str = "compatibility",
    config: Optional[PreprocessingOptimizationConfig] = None
) -> Dict[str, Any]
```

**Description**: Optimize preprocessing parameters for a model.

**Parameters**:
- `model_characteristics`: Model characteristics from ModelAnalyzer
- `target_metric`: Metric to optimize (compatibility, accuracy, speed)
- `config`: Optimization configuration (optional)

**Returns**: Dictionary of optimized preprocessing parameters.

##### validate_preprocessing_params()

```python
def validate_preprocessing_params(
    self,
    params: Dict[str, Any],
    model_type: str
) -> List[str]
```

**Description**: Validate preprocessing parameters.

**Parameters**:
- `params`: Preprocessing parameters
- `model_type`: Model type (asr, tts, vision, nlp)

**Returns**: List of validation errors (empty if valid).

##### get_preprocessing_recommendations()

```python
def get_preprocessing_recommendations(
    self,
    model_characteristics: Dict[str, Any]
) -> List[str]
```

**Description**: Get preprocessing recommendations for a model.

**Parameters**:
- `model_characteristics`: Model characteristics

**Returns**: List of recommendations.

---

## Data Models

### ParameterOptimizationResult

**Description**: Result of parameter optimization.

**Fields**:
- `best_params`: Dict[str, Any] - Best parameter values
- `best_metrics`: OptimizationMetrics - Best metrics
- `optimization_result`: OptimizationResult - Optimization details
- `model_characteristics`: ModelCharacteristics - Model characteristics
- `improvement_percentage`: float - Improvement percentage
- `strategy_used`: OptimizationStrategy - Strategy used
- `objective`: OptimizationObjective - Objective
- `execution_time`: float - Execution time
- `recommendations`: List[str] - Optimization recommendations

### ModelCharacteristics

**Description**: Model characteristics and metadata.

**Fields**:
- `model_type`: ModelType - Model type
- `model_size`: int - Number of parameters
- `file_size`: int - File size in bytes
- `layers`: Dict[str, int] - Layer type distribution
- `operators`: Dict[str, int] - Operator distribution
- `input_shapes`: List[Tuple[int, ...]] - Input shapes
- `output_shapes`: List[Tuple[int, ...]] - Output shapes
- `quantization_sensitivity`: float - Quantization sensitivity (0.0-1.0)
- `complexity_score`: float - Complexity score (0.0-1.0)
- `is_transformer`: bool - Has transformer architecture
- `has_conv_layers`: bool - Has convolutional layers
- `has_rnn_layers`: bool - Has RNN layers
- `recommended_quantization`: int - Recommended quantization bits
- `estimated_memory_usage`: float - Estimated memory usage (MB)
- `supported_formats`: List[str] - Supported formats

### OptimizationMetrics

**Description**: Metrics tracked during optimization.

**Fields**:
- `accuracy`: float - Accuracy (0.0-1.0)
- `latency`: float - Latency (milliseconds)
- `throughput`: float - Throughput (samples/sec)
- `memory_usage`: float - Memory usage (MB)
- `compatibility`: float - Compatibility (0.0-1.0)
- `success_rate`: float - Success rate (0.0-1.0)

### OptimizationEntry

**Description**: Single optimization history entry.

**Fields**:
- `version`: str - Version string
- `timestamp`: float - Unix timestamp
- `params`: Dict[str, Any] - Parameter values
- `metrics`: Dict[str, float] - Metrics
- `score`: float - Optimization score
- `strategy`: str - Optimization strategy
- `objective`: str - Optimization objective
- `model_characteristics`: Dict[str, Any] - Model characteristics
- `execution_time`: float - Execution time (seconds)
- `recommendations`: List[str] - Recommendations
- `user_notes`: str - User notes
- `tags`: List[str] - Version tags

### VersionComparison

**Description**: Comparison between two optimization versions.

**Fields**:
- `version1`: str - First version
- `version2`: str - Second version
- `score_difference`: float - Score difference
- `param_differences`: Dict[str, Any] - Parameter differences
- `metric_differences`: Dict[str, float] - Metric differences
- `improvement_percentage`: float - Improvement percentage
- `significant_changes`: List[str] - Significant changes

### OptimizationResult

**Description**: Result of optimization process.

**Fields**:
- `best_params`: Dict[str, Any] - Best parameters
- `best_score`: float - Best score
- `iterations`: int - Number of iterations
- `strategy`: OptimizationStrategy - Strategy used
- `convergence_achieved`: bool - Convergence achieved
- `history`: List[Tuple[Dict[str, Any], float]] - History (params, score)
- `execution_time`: float - Execution time
- `message`: str - Status message

### TradeOffWeights

**Description**: Weight configuration for trade-off objectives.

**Fields**:
- `accuracy`: float - Weight for accuracy (0.0-1.0)
- `latency`: float - Weight for latency (0.0-1.0)
- `throughput`: float - Weight for throughput (0.0-1.0)
- `memory`: float - Weight for memory (0.0-1.0)
- `compatibility`: float - Weight for compatibility (0.0-1.0)
- `success_rate`: float - Weight for success rate (0.0-1.0)

### TradeOffConfig

**Description**: Configuration for trade-off strategy.

**Fields**:
- `strategy`: TradeOffStrategy - Trade-off strategy
- `weights`: TradeOffWeights - Predefined weights
- `custom_weights`: Optional[TradeOffWeights] - Custom weights (if any)

### ParameterRecommendation

**Description**: Parameter recommendation for a model.

**Fields**:
- `param_name`: str - Parameter name
- `recommended_value`: Any - Recommended value
- `confidence`: float - Confidence (0.0-1.0)
- `reason`: str - Reason for recommendation
- `alternatives`: Optional[List[Any]] - Alternative values

---

## Enumerations

### OptimizationStrategy

**Values**:
- `GRID_SEARCH` - Grid search optimization
- `BAYESIAN` - Bayesian optimization
- `GENETIC` - Genetic algorithm
- `RANDOM` - Random search

### OptimizationObjective

**Values**:
- `MAXIMIZE_ACCURACY` - Maximize accuracy
- `MINIMIZE_LATENCY` - Minimize latency
- `MAXIMIZE_THROUGHPUT` - Maximize throughput
- `MINIMIZE_MEMORY` - Minimize memory usage
- `MAXIMIZE_COMPATIBILITY` - Maximize compatibility
- `BALANCED` - Balanced optimization

### TradeOffStrategy

**Values**:
- `QUALITY_FIRST` - Quality first strategy
- `PERFORMANCE_FIRST` - Performance first strategy
- `BALANCED` - Balanced strategy
- `RESOURCE_SAVING` - Resource saving strategy
- `CUSTOM` - Custom strategy

### ModelType

**Values**:
- `ASR` - Automatic speech recognition
- `TTS` - Text to speech
- `VISION` - Computer vision
- `NLP` - Natural language processing
- `AUDIO` - Audio processing
- `GENERIC` - Generic model

### HistoryStorageFormat

**Values**:
- `JSON` - JSON format
- `YAML` - YAML format

### VersionTag

**Values**:
- `STABLE` - Stable version
- `EXPERIMENTAL` - Experimental version
- `BEST` - Best version
- `FAILED` - Failed version
- `BASELINE` - Baseline version

---

## Functions

### create_optimization_strategy()

```python
def create_optimization_strategy(
    strategy_type: OptimizationStrategy,
    config: OptimizationConfig
) -> BaseOptimizationStrategy
```

**Description**: Factory function to create optimization strategy instances.

**Parameters**:
- `strategy_type`: Type of optimization strategy
- `config`: Optimization configuration

**Returns**: Optimization strategy instance.

### get_predefined_strategies()

```python
def get_predefined_strategies() -> List[TradeOffStrategy]
```

**Description**: Get list of all predefined trade-off strategies.

**Returns**: List of TradeOffStrategy values.

### create_custom_config()

```python
def create_custom_config(
    accuracy: float = 0.25,
    latency: float = 0.25,
    throughput: float = 0.15,
    memory: float = 0.15,
    compatibility: float = 0.1,
    success_rate: float = 0.1
) -> TradeOffConfig
```

**Description**: Create custom trade-off configuration.

**Parameters**:
- `accuracy`: Weight for accuracy
- `latency`: Weight for latency
- `throughput`: Weight for throughput
- `memory`: Weight for memory
- `compatibility`: Weight for compatibility
- `success_rate`: Weight for success rate

**Returns**: Custom TradeOffConfig.

---

## Configuration

### OptimizationConfig

**Description**: Configuration for optimization process.

**Fields**:
- `max_iterations`: int - Maximum iterations (default: 100)
- `convergence_threshold`: float - Convergence threshold (default: 0.01)
- `time_limit`: float - Time limit in seconds (default: 600.0)
- `early_stopping`: bool - Enable early stopping (default: True)
- `patience`: int - Patience for early stopping (default: 10)
- `random_seed`: Optional[int] - Random seed (default: None)
- `verbose`: bool - Enable verbose logging (default: True)

### PreprocessingOptimizationConfig

**Description**: Configuration for preprocessing parameter optimization.

**Fields**:
- `optimize_normalization`: bool - Optimize normalization (default: True)
- `optimize_resize`: bool - Optimize resize (default: True)
- `optimize_channel_format`: bool - Optimize channel format (default: True)
- `optimize_data_type`: bool - Optimize data type (default: True)
- `respect_model_constraints`: bool - Respect model constraints (default: True)
- `preset`: Optional[str] - Optimization preset (optional)

---

## Complete Examples

### Example 1: Basic Optimization

```python
from npu_converter.optimization import (
    ParameterOptimizer,
    ModelAnalyzer,
    OptimizationStrategy
)

# Initialize
optimizer = ParameterOptimizer()

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

# Run optimization
result = optimizer.optimize(
    model="model.onnx",
    param_space=param_space,
    strategy=OptimizationStrategy.BAYESIAN
)

# Access results
print(f"Best parameters: {result.best_params}")
print(f"Best metrics: {result.best_metrics}")
print(f"Improvement: {result.improvement_percentage:.1f}%")
```

### Example 2: With Model Analysis and History

```python
from npu_converter.optimization import (
    ParameterOptimizer,
    ModelAnalyzer,
    OptimizationHistory,
    TradeOffStrategy,
    TradeOffConfig
)

# Initialize
analyzer = ModelAnalyzer()
optimizer = ParameterOptimizer()
history = OptimizationHistory()

# Analyze model
model_path = "model.onnx"
characteristics = analyzer.analyze_model(model_path)

print(f"Model type: {characteristics.model_type.value}")

# Define parameter space
param_space = {
    'quantization_bits': {
        'type': 'choice',
        'values': [8, 16]
    }
}

# Configure trade-off
tradeoff_config = TradeOffConfig.from_strategy(
    TradeOffStrategy.BALANCED
)

# Run optimization
result = optimizer.optimize(
    model=model_path,
    param_space=param_space,
    tradeoff_config=tradeoff_config
)

# Record in history
version = history.record(
    params=result.best_params,
    metrics={
        'accuracy': result.best_metrics.accuracy,
        'latency': result.best_metrics.latency
    },
    score=result.optimization_result.best_score,
    strategy=result.strategy_used.value,
    objective=result.objective.value,
    model_characteristics=characteristics.__dict__,
    execution_time=result.execution_time,
    tags=['optimized']
)

print(f"Recorded to history: {version}")
```

### Example 3: Generate Report

```python
from npu_converter.optimization import OptimizationReportGenerator

generator = OptimizationReportGenerator()

# Generate HTML report
html_path = generator.generate_report(
    result=result,
    format="html",
    include_charts=True
)

print(f"HTML report: {html_path}")

# Generate JSON report
json_path = generator.generate_report(
    result=result,
    format="json"
)

print(f"JSON report: {json_path}")
```

### Example 4: Custom Trade-off Strategy

```python
from npu_converter.optimization import (
    TradeOffWeights,
    TradeOffConfig
)

# Create custom weights
weights = TradeOffWeights(
    accuracy=0.6,
    latency=0.3,
    throughput=0.05,
    memory=0.025,
    compatibility=0.015,
    success_rate=0.01
)

# Create configuration
config = TradeOffConfig.from_custom_weights(weights)

# Use in optimization
result = optimizer.optimize(
    model=model_path,
    param_space=param_space,
    tradeoff_config=config
)
```

### Example 5: Compare Versions

```python
# Run multiple optimizations
results = []
for i in range(3):
    result = optimizer.optimize(
        model=model_path,
        param_space=param_space,
        max_iterations=20
    )
    results.append(result)

# Compare first and last
comparison = history.compare_versions(
    history.list_versions()[0],
    history.list_versions()[-1]
)

print(f"Score difference: {comparison.score_difference:.4f}")
print(f"Improvement: {comparison.improvement_percentage:.1f}%")
```

### Example 6: Preprocessing Optimization

```python
from npu_converter.optimization import PreprocessingOptimizer

preprocessor = PreprocessingOptimizer()

# Optimize preprocessing
preproc_params = preprocessor.optimize_preprocessing(
    model_characteristics=characteristics.__dict__,
    target_metric="compatibility"
)

print(f"Preprocessing parameters: {preproc_params}")

# Validate parameters
errors = preprocessor.validate_preprocessing_params(
    preproc_params,
    characteristics.model_type.value
)

if errors:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error}")
else:
    print("All parameters are valid!")
```

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-28
**Status**: ✅ Complete
