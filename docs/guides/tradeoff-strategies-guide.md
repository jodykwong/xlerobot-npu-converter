# Trade-off Strategies Guide

**Version**: 1.0.0
**Author**: Story 2.6 Implementation
**Date**: 2025-10-28

---

## Table of Contents

1. [Introduction](#introduction)
2. [Understanding Trade-offs](#understanding-trade-offs)
3. [Predefined Strategies](#predefined-strategies)
4. [Custom Strategies](#custom-strategies)
5. [Strategy Selection Guide](#strategy-selection-guide)
6. [Use Case Examples](#use-case-examples)
7. [Advanced Configuration](#advanced-configuration)
8. [Performance Implications](#performance-implications)
9. [Best Practices](#best-practices)
10. [API Reference](#api-reference)

---

## Introduction

Trade-off strategies allow you to balance different optimization objectives based on your specific use case. The system provides predefined strategies for common scenarios and supports custom weight configurations for specialized requirements.

### What Are Trade-offs?

In model optimization, there are multiple competing objectives:

- **Accuracy**: How correct the model's outputs are
- **Latency**: Time to produce results (lower is better)
- **Throughput**: Number of results per second (higher is better)
- **Memory**: RAM/VRAM usage (lower is better)
- **Compatibility**: How well the model works with target hardware
- **Success Rate**: Probability of successful conversion

Trade-off strategies let you prioritize these objectives according to your needs.

---

## Understanding Trade-offs

### The Optimization Problem

```
Optimization Score = w₁×accuracy + w₂×latency_score + w₃×throughput_score
                   + w₄×memory_score + w₅×compatibility + w₆×success_rate
```

Where:
- `wi` = weight for objective i
- All weights sum to 1.0
- Latency and Memory are inverted (lower is better)

### Weight Normalization

Weights are automatically normalized to sum to 1.0:

```python
weights = TradeOffWeights(
    accuracy=0.7,
    latency=0.2,
    throughput=0.1,
    memory=0.0,
    compatibility=0.0,
    success_rate=0.0
)

# After normalization:
# accuracy=0.7/(0.7+0.2+0.1)=0.7
# latency=0.2/(0.7+0.2+0.1)=0.2
# throughput=0.1/(0.7+0.2+0.1)=0.1
```

### Metric Normalization

Metrics are normalized to 0.0-1.0 scale:

| Metric | Original Scale | Normalized (Higher is Better) |
|--------|----------------|------------------------------|
| Accuracy | 0.0 - 1.0 | As-is |
| Latency | 0 - ∞ ms | 1/(1 + latency/1000) |
| Throughput | 0 - ∞ samples/s | min(throughput/100, 1.0) |
| Memory | 0 - ∞ MB | 1/(1 + memory/1000) |
| Compatibility | 0.0 - 1.0 | As-is |
| Success Rate | 0.0 - 1.0 | As-is |

---

## Predefined Strategies

### 1. Quality First (质量优先)

**Philosophy**: Maximize output quality above all else

**Weight Distribution**:
- Accuracy: 70%
- Latency: 20%
- Throughput: 5%
- Memory: 3%
- Compatibility: 1%
- Success Rate: 1%

**When to Use**:
- Production TTS systems where audio quality is critical
- Medical or safety-critical applications
- When accuracy >95% is required
- Voice synthesis for final products

**Example**:
```python
from npu_converter.optimization import TradeOffStrategy, TradeOffConfig

config = TradeOffConfig.from_strategy(
    TradeOffStrategy.QUALITY_FIRST
)

result = optimizer.optimize(
    tradeoff_config=config,
    # ... other parameters
)
```

**Expected Outcomes**:
- ✅ Highest accuracy (96-98%)
- ✅ Best audio/output quality
- ✅ Most conservative quantization (prefers 16-bit)
- ⚠️ Higher latency
- ⚠️ Higher memory usage

### 2. Performance First (性能优先)

**Philosophy**: Minimize latency and maximize throughput

**Weight Distribution**:
- Accuracy: 30%
- Latency: 40%
- Throughput: 20%
- Memory: 5%
- Compatibility: 3%
- Success Rate: 2%

**When to Use**:
- Real-time ASR systems
- Streaming applications
- Interactive voice assistants
- Live transcription
- Gaming or real-time applications

**Example**:
```python
config = TradeOffConfig.from_strategy(
    TradeOffStrategy.PERFORMANCE_FIRST
)
```

**Expected Outcomes**:
- ✅ Lowest latency (<100ms)
- ✅ Highest throughput
- ✅ Faster inference
- ⚠️ Slightly lower accuracy (92-95%)
- ⚠️ May use aggressive quantization (8-bit)

### 3. Balanced (平衡)

**Philosophy**: Balance all objectives evenly

**Weight Distribution**:
- Accuracy: 25%
- Latency: 25%
- Throughput: 15%
- Memory: 15%
- Compatibility: 10%
- Success Rate: 10%

**When to Use**:
- General-purpose optimization
- Default choice when requirements unclear
- Batch processing systems
- Prototype development
- Multi-purpose models

**Example**:
```python
config = TradeOffConfig.from_strategy(
    TradeOffStrategy.BALANCED
)
```

**Expected Outcomes**:
- ✅ Good balance of all metrics
- ✅ Moderate accuracy (94-96%)
- ✅ Reasonable latency
- ✅ Moderate memory usage
- ✅ Good compatibility

### 4. Resource Saving (资源节约)

**Philosophy**: Minimize resource usage

**Weight Distribution**:
- Accuracy: 20%
- Latency: 15%
- Throughput: 10%
- Memory: 35%
- Compatibility: 10%
- Success Rate: 10%

**When to Use**:
- Edge devices with limited memory
- Mobile deployments
- IoT devices
- Raspberry Pi or similar
- Battery-powered devices

**Example**:
```python
config = TradeOffConfig.from_strategy(
    TradeOffStrategy.RESOURCE_SAVING
)
```

**Expected Outcomes**:
- ✅ Lowest memory usage
- ✅ Efficient resource utilization
- ✅ Works on constrained hardware
- ⚠️ Lower accuracy (92-94%)
- ⚠️ May sacrifice some quality

---

## Custom Strategies

### Creating Custom Weights

```python
from npu_converter.optimization import TradeOffWeights, TradeOffConfig

# Create custom weights (must sum to positive value)
weights = TradeOffWeights(
    accuracy=0.6,      # 60% weight on accuracy
    latency=0.3,        # 30% weight on latency
    throughput=0.05,     # 5% weight on throughput
    memory=0.025,       # 2.5% weight on memory
    compatibility=0.015, # 1.5% weight on compatibility
    success_rate=0.01   # 1% weight on success rate
)

# Create configuration
config = TradeOffConfig.from_custom_weights(weights)
```

### Custom Strategy Examples

#### Example 1: Real-time TTS (Hybrid)

For a TTS system that needs good quality but low latency:

```python
weights = TradeOffWeights(
    accuracy=0.5,      # Quality important
    latency=0.35,      # Low latency important
    throughput=0.1,     # Some throughput needed
    memory=0.025,      # Memory not critical
    compatibility=0.015,
    success_rate=0.01
)

config = TradeOffConfig.from_custom_weights(weights)
```

#### Example 2: Batch ASR Processing

For processing large batches of audio files:

```python
weights = TradeOffWeights(
    accuracy=0.4,      # Good accuracy
    latency=0.1,        # Latency not critical
    throughput=0.35,    # High throughput critical
    memory=0.1,         # Some memory concern
    compatibility=0.025,
    success_rate=0.025
)

config = TradeOffConfig.from_custom_weights(weights)
```

#### Example 3: Research/Development

For experimentation where various metrics are important:

```python
weights = TradeOffWeights(
    accuracy=0.3,
    latency=0.2,
    throughput=0.2,
    memory=0.15,
    compatibility=0.075,
    success_rate=0.075
)

config = TradeOffConfig.from_custom_weights(weights)
```

### Weight Guidelines

| Objective | Minimum Weight | Recommended Range | Maximum Weight |
|-----------|---------------|------------------|----------------|
| Accuracy | 0.1 | 0.3 - 0.7 | 0.9 |
| Latency | 0.05 | 0.1 - 0.4 | 0.6 |
| Throughput | 0.05 | 0.05 - 0.35 | 0.5 |
| Memory | 0.05 | 0.05 - 0.35 | 0.5 |
| Compatibility | 0.01 | 0.01 - 0.1 | 0.2 |
| Success Rate | 0.01 | 0.01 - 0.1 | 0.2 |

**Tips**:
- Don't set any weight to 0.0 (except in special cases)
- Ensure weights sum to a reasonable value (>0.1)
- Test different configurations
- Use statistics to guide decisions

---

## Strategy Selection Guide

### Decision Tree

```
Is low latency critical? (real-time, streaming)
├─ YES → Performance First
└─ NO ↓

Is high accuracy critical? (production, quality-focused)
├─ YES → Quality First
└─ NO ↓

Is memory limited? (edge device, mobile)
├─ YES → Resource Saving
└─ NO ↓

Default → Balanced
```

### Use Case Matrix

| Use Case | Recommended Strategy | Custom Weights Needed |
|----------|---------------------|----------------------|
| **Real-time ASR** | Performance First | - |
| **TTS Production** | Quality First | - |
| **Edge Deployment** | Resource Saving | - |
| **General Purpose** | Balanced | - |
| **Real-time TTS** | Custom | accuracy=0.5, latency=0.35 |
| **Batch ASR** | Custom | accuracy=0.4, throughput=0.35 |
| **Mobile App** | Resource Saving | - |
| **Cloud Service** | Balanced | - |
| **Research** | Custom | Balanced weights |
| **Prototype** | Balanced | - |

### Model Type Considerations

#### ASR Models

| Priority | Strategy | Rationale |
|----------|----------|-----------|
| Real-time | Performance First | Latency < 100ms critical |
| Batch | Custom | accuracy=0.4, throughput=0.35 |
| Quality-focused | Quality First | Accuracy important |
| Mobile | Resource Saving | Memory constraints |

#### TTS Models

| Priority | Strategy | Rationale |
|----------|----------|-----------|
| Production | Quality First | Audio quality paramount |
| Real-time | Custom | accuracy=0.5, latency=0.35 |
| Mobile | Resource Saving | Battery/performance |
| General | Balanced | Good default |

#### Vision Models

| Priority | Strategy | Rationale |
|----------|----------|-----------|
| Real-time | Performance First | Frame rate critical |
| Accuracy-critical | Quality First | Classification accuracy |
| Mobile | Resource Saving | Limited resources |
| General | Balanced | Good default |

#### NLP Models

| Priority | Strategy | Rationale |
|----------|----------|-----------|
| Real-time chat | Performance First | Response time |
| Translation | Quality First | Accuracy critical |
| Batch processing | Custom | throughput focused |
| General | Balanced | Good default |

---

## Use Case Examples

### Example 1: Voice Assistant (Real-time ASR)

**Requirements**:
- Latency < 100ms
- Accuracy > 93%
- Real-time processing

**Solution**:

```python
config = TradeOffConfig.from_strategy(
    TradeOffStrategy.PERFORMANCE_FIRST
)

# Override max latency constraint
result = optimizer.optimize(
    tradeoff_config=config,
    constraints={'max_latency': 100.0}
)
```

**Expected Results**:
- Latency: 80-95ms
- Accuracy: 93-95%
- Throughput: 10-15 samples/sec

### Example 2: Podcast Transcription (Batch ASR)

**Requirements**:
- Process large audio files
- High accuracy > 96%
- Speed less critical

**Solution**:

```python
weights = TradeOffWeights(
    accuracy=0.5,      # High accuracy priority
    latency=0.1,        # Latency not critical
    throughput=0.25,    # Some speed needed
    memory=0.1,
    compatibility=0.025,
    success_rate=0.025
)

config = TradeOffConfig.from_custom_weights(weights)

result = optimizer.optimize(
    tradeoff_config=config,
    max_iterations=100  # More iterations for quality
)
```

**Expected Results**:
- Accuracy: 96-98%
- Latency: 150-200ms (acceptable for batch)
- Throughput: 5-8 samples/sec

### Example 3: TTS for Audiobook (Production)

**Requirements**:
- Highest audio quality
- Natural sounding speech
- Quality > 8.5/10

**Solution**:

```python
config = TradeOffConfig.from_strategy(
    TradeOffStrategy.QUALITY_FIRST
)

# Use 16-bit quantization
param_space = {
    'quantization_bits': {
        'type': 'choice',
        'values': [16]  # Force 16-bit
    },
    # ... other parameters
}

result = optimizer.optimize(
    tradeoff_config=config,
    param_space=param_space
)
```

**Expected Results**:
- Audio Quality: 8.5-9.0/10
- Accuracy: 96-98%
- Latency: 120-180ms

### Example 4: TTS for Mobile Game

**Requirements**:
- Low latency < 50ms
- Moderate quality
- Low memory usage

**Solution**:

```python
weights = TradeOffWeights(
    accuracy=0.35,      # Moderate quality
    latency=0.45,       # Very low latency priority
    throughput=0.1,
    memory=0.05,         # Some memory concern
    compatibility=0.025,
    success_rate=0.025
)

config = TradeOffConfig.from_custom_weights(weights)

result = optimizer.optimize(
    tradeoff_config=config,
    constraints={'max_latency': 50.0}
)
```

**Expected Results**:
- Latency: 40-48ms
- Quality: 7.5-8.0/10
- Memory: < 200MB

### Example 5: Smart Speaker (Edge Device)

**Requirements**:
- Run on Raspberry Pi
- Limited memory (512MB)
- Always-on capability

**Solution**:

```python
config = TradeOffConfig.from_strategy(
    TradeOffStrategy.RESOURCE_SAVING
)

# Constrain memory
result = optimizer.optimize(
    tradeoff_config=config,
    constraints={'max_memory': 400.0}
)
```

**Expected Results**:
- Memory: 300-380MB
- Accuracy: 92-94%
- Latency: 120-160ms

### Example 6: Cloud TTS Service

**Requirements**:
- Handle many concurrent requests
- Balanced quality and speed
- Scalable

**Solution**:

```python
weights = TradeOffWeights(
    accuracy=0.4,       # Good quality
    latency=0.3,        # Reasonable latency
    throughput=0.2,      # High throughput
    memory=0.05,         # Memory not critical in cloud
    compatibility=0.025,
    success_rate=0.025
)

config = TradeOffConfig.from_custom_weights(weights)

result = optimizer.optimize(
    tradeoff_config=config,
    max_iterations=75
)
```

**Expected Results**:
- Accuracy: 95-97%
- Latency: 100-140ms
- Throughput: 8-12 samples/sec

---

## Advanced Configuration

### Strategy with Constraints

```python
from npu_converter.optimization import TradeOffStrategy, TradeOffConfig, TradeOffWeights

# Define custom strategy
weights = TradeOffWeights(
    accuracy=0.6,
    latency=0.3,
    throughput=0.05,
    memory=0.025,
    compatibility=0.015,
    success_rate=0.01
)

config = TradeOffConfig.from_custom_weights(weights)

# Apply constraints
constraints = {
    'max_latency': 100.0,      # ms
    'min_accuracy': 0.93,       # 93%
    'max_memory': 500.0,        # MB
    'min_success_rate': 0.9      # 90%
}

result = optimizer.optimize(
    tradeoff_config=config,
    constraints=constraints
)
```

### Multiple Strategy Comparison

```python
strategies = [
    TradeOffStrategy.QUALITY_FIRST,
    TradeOffStrategy.PERFORMANCE_FIRST,
    TradeOffStrategy.BALANCED,
    TradeOffStrategy.RESOURCE_SAVING
]

results = {}

for strategy in strategies:
    config = TradeOffConfig.from_strategy(strategy)

    result = optimizer.optimize(
        tradeoff_config=config,
        max_iterations=50
    )

    results[strategy.value] = {
        'accuracy': result.best_metrics.accuracy,
        'latency': result.best_metrics.latency,
        'throughput': result.best_metrics.throughput,
        'memory': result.best_metrics.memory_usage,
        'score': result.optimization_result.best_score
    }

# Print comparison
for strategy, metrics in results.items():
    print(f"\n{strategy}:")
    print(f"  Accuracy: {metrics['accuracy']:.2%}")
    print(f"  Latency: {metrics['latency']:.1f} ms")
    print(f"  Score: {metrics['score']:.4f}")
```

### Dynamic Strategy Adjustment

```python
def adaptive_strategy(base_accuracy, target_latency):
    """Adjust strategy based on current performance."""
    if base_accuracy < 0.9:
        # Need more accuracy
        weights = TradeOffWeights(
            accuracy=0.7,
            latency=0.15,
            throughput=0.1,
            memory=0.025,
            compatibility=0.015,
            success_rate=0.01
        )
    elif target_latency < 80:
        # Need less latency
        weights = TradeOffWeights(
            accuracy=0.4,
            latency=0.45,
            throughput=0.1,
            memory=0.025,
            compatibility=0.015,
            success_rate=0.01
        )
    else:
        # Balanced
        weights = TradeOffWeights(
            accuracy=0.5,
            latency=0.3,
            throughput=0.15,
            memory=0.025,
            compatibility=0.015,
            success_rate=0.01
        )

    return TradeOffConfig.from_custom_weights(weights)


# Use adaptive strategy
current_accuracy = 0.88
target_latency = 75.0

config = adaptive_strategy(current_accuracy, target_latency)

result = optimizer.optimize(tradeoff_config=config)
```

---

## Performance Implications

### Optimization Speed

| Strategy | Relative Speed | Notes |
|----------|---------------|-------|
| Quality First | Same | No difference in speed |
| Performance First | Same | No difference in speed |
| Balanced | Same | No difference in speed |
| Resource Saving | Same | No difference in speed |
| Custom | Same | No difference in speed |

**Note**: Trade-off strategy does NOT affect optimization speed. It only affects which parameters are preferred.

### Result Characteristics

#### Quality First
- **Best For**: Output quality, accuracy
- **Worst For**: Speed, memory efficiency
- **Typical Values**:
  - Accuracy: 96-98%
  - Latency: +20-30% vs Performance First
  - Memory: +10-20% vs Balanced

#### Performance First
- **Best For**: Speed, throughput
- **Worst For**: Accuracy
- **Typical Values**:
  - Latency: 60-90ms (ASR)
  - Throughput: +30-50% vs Balanced
  - Accuracy: -2-3% vs Quality First

#### Balanced
- **Best For**: General purpose
- **Worst For**: Specialized needs
- **Typical Values**:
  - All metrics: 85-95% of optimal

#### Resource Saving
- **Best For**: Memory, constrained devices
- **Worst For**: Accuracy, speed
- **Typical Values**:
  - Memory: -30-50% vs Balanced
  - Accuracy: -2-4% vs Balanced

---

## Best Practices

### 1. Start with Predefined Strategies

```python
# Try predefined first
config = TradeOffConfig.from_strategy(
    TradeOffStrategy.BALANCED
)

# If results aren't satisfactory, try custom
```

### 2. Measure Current Performance

```python
# Get baseline before optimization
baseline_metrics = evaluate_model(model)

# Use these to inform strategy choice
if baseline_metrics['accuracy'] < 0.9:
    config = TradeOffConfig.from_strategy(
        TradeOffStrategy.QUALITY_FIRST
    )
```

### 3. Use Multiple Strategies

```python
# Try all strategies
for strategy in [
    TradeOffStrategy.QUALITY_FIRST,
    TradeOffStrategy.PERFORMANCE_FIRST,
    TradeOffStrategy.BALANCED
]:
    result = optimizer.optimize(
        tradeoff_config=TradeOffConfig.from_strategy(strategy)
    )
    # Compare results
```

### 4. Document Strategy Choice

```python
history.record(
    # ... other parameters
    user_notes="""
    Strategy: Quality First
    Rationale: Production TTS system requires high audio quality.
    Constraints: Latency < 200ms acceptable.
    """,
    tags=["production", "tts", "quality_first"]
)
```

### 5. Validate Results

```python
# Check if strategy achieved goals
if result.best_metrics.latency > target_latency:
    print("WARNING: Latency exceeds target!")
    print("Consider Performance First strategy")

if result.best_metrics.accuracy < min_accuracy:
    print("WARNING: Accuracy below minimum!")
    print("Consider Quality First strategy")
```

### 6. Use Constraints

```python
# Always set realistic constraints
constraints = {
    'max_latency': 100.0,    # Realistic for your use case
    'min_accuracy': 0.93,      # Minimum acceptable
    'max_memory': 500.0         # Hardware limit
}

result = optimizer.optimize(
    tradeoff_config=config,
    constraints=constraints
)
```

---

## API Reference

### TradeOffWeights

```python
@dataclass
class TradeOffWeights:
    accuracy: float              # 0.0 - 1.0
    latency: float               # 0.0 - 1.0
    throughput: float            # 0.0 - 1.0
    memory: float               # 0.0 - 1.0
    compatibility: float         # 0.0 - 1.0
    success_rate: float          # 0.0 - 1.0

    def validate(self) -> bool
    def normalize(self) -> TradeOffWeights
```

### TradeOffConfig

```python
@dataclass
class TradeOffConfig:
    strategy: TradeOffStrategy
    weights: TradeOffWeights
    custom_weights: Optional[TradeOffWeights] = None

    @classmethod
    def from_strategy(cls, strategy: TradeOffStrategy) -> TradeOffConfig

    @classmethod
    def from_custom_weights(cls, weights: TradeOffWeights) -> TradeOffConfig

    @classmethod
    def default(cls) -> TradeOffConfig

    def get_weights(self) -> TradeOffWeights
    def get_description(self) -> str
```

### TradeOffCalculator

```python
class TradeOffCalculator:
    def calculate_score(
        self,
        metrics: Dict[str, float],
        config: TradeOffConfig
    ) -> float

    def estimate_outcome(
        self,
        model_type: str,
        config: TradeOffConfig,
        model_complexity: float = 0.5
    ) -> Dict[str, Any]

    def compare_strategies(
        self,
        model_type: str,
        strategies: List[TradeOffStrategy],
        model_complexity: float = 0.5
    ) -> Dict[str, Dict[str, Any]]

    def get_strategy_recommendation(
        self,
        use_case: str,
        constraints: Optional[Dict[str, float]] = None
    ) -> TradeOffStrategy
```

### Helper Functions

```python
def get_predefined_strategies() -> List[TradeOffStrategy]:
    """Get all predefined trade-off strategies."""

def create_custom_config(
    accuracy: float = 0.25,
    latency: float = 0.25,
    throughput: float = 0.15,
    memory: float = 0.15,
    compatibility: float = 0.1,
    success_rate: float = 0.1
) -> TradeOffConfig:
    """Create custom trade-off configuration."""
```

---

## Conclusion

Trade-off strategies are powerful tools for aligning optimization with your specific requirements. Start with predefined strategies, and use custom weights when you need fine-grained control. Always validate results against your goals and constraints.

**Summary**:
- **Quality First**: Best quality, slower
- **Performance First**: Fastest speed, lower accuracy
- **Balanced**: Good all-around
- **Resource Saving**: Least memory
- **Custom**: Full control

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-28
**Status**: ✅ Complete
