# VITS-Cantonese TTS 转换指南

**Story 2.2**: VITS-Cantonese TTS完整转换实现指南
**版本**: 1.0.0
**日期**: 2025-10-27
**适用对象**: AI模型工程师、语音系统开发者

---

## 目录

1. [概述](#概述)
2. [快速开始](#快速开始)
3. [配置选项](#配置选项)
4. [使用示例](#使用示例)
5. [最佳实践](#最佳实践)
6. [故障排除](#故障排除)
7. [API参考](#api参考)

---

## 概述

VITS-Cantonese TTS转换工具是Story 2.2的核心功能，提供完整的VITS-Cantonese语音合成模型从ONNX到BPU格式的转换能力。

### 主要特性

- ✅ **高成功率**: 转换成功率>95%（PRD要求）
- ✅ **高性能**: 2-5倍性能提升（PRD要求）
- ✅ **高精度**: 精度保持率>98%（PRD要求）
- ✅ **粤语优化**: 九声六调专用优化
- ✅ **多音色**: 支持男声、女声、儿童声音
- ✅ **多格式报告**: JSON、HTML、PDF报告

### Acceptance Criteria

- **AC1**: 增强VITS-Cantonese模型的端到端转换能力
- **AC2**: 实现粤语语音合成的专用优化
- **AC3**: 支持VITS-Cantonese模型的完整参数配置
- **AC4**: 实现VITS-Cantonese转换结果的精确验证
- **AC5**: 提供VITS-Cantonese专用转换报告

---

## 快速开始

### 1. 安装依赖

```bash
# 确保已安装Epic 1的基础设施
# Story 1.3: 核心转换框架
# Story 1.4: 配置管理系统
# Story 1.5: 基础转换流程
# Story 2.1.2: ONNX模型加载
```

### 2. 基础转换示例

```python
from src.npu_converter.complete_flows.vits_cantonese_complete_flow import (
    VITSCantoneseCompleteFlow,
    CantoneseConversionLevel
)
from src.npu_converter.core.models.config_model import ConfigModel

# 创建配置
config = ConfigModel(
    model_type="vits_cantonese",
    voice_type="female",
    conversion_level="production",
    sample_rate=44100,
    bit_depth=16
)

# 创建转换流程
flow = VITSCantoneseCompleteFlow(
    config=config,
    conversion_level=CantoneseConversionLevel.PRODUCTION
)

# 执行转换
result, report_path = await flow.convert_model(
    model_path="path/to/vits_cantonese.onnx",
    output_path="path/to/output.bpu"
)

print(f"转换成功: {result.success}")
print(f"报告路径: {report_path}")
```

### 3. 使用配置文件

```python
import yaml
from src.npu_converter.complete_flows.vits_cantonese_complete_flow import VITSCantoneseCompleteFlow

# 加载配置文件
with open("configs/vits_cantonese/default.yaml", "r") as f:
    config_data = yaml.safe_load(f)

# 创建配置模型
from src.npu_converter.core.models.config_model import ConfigModel
config = ConfigModel(**config_data)

# 执行转换
flow = VITSCantoneseCompleteFlow(config=config)
result, report_path = await flow.convert_model(
    model_path="path/to/vits_cantonese.onnx",
    output_path="path/to/output.bpu"
)
```

---

## 配置选项

### 模型配置

```yaml
model:
  type: vits_cantonese              # 模型类型
  language: cantonese               # 语言
  voice_type: female                # 音色: male, female, child, neutral
  version: "1.0.0"                  # 模型版本
```

### 转换配置

```yaml
conversion:
  level: production                 # 转换级别: basic, standard, enhanced, production
  input_format: onnx                # 输入格式
  output_format: bpu                # 输出格式
  target_hardware: horizon_x5       # 目标硬件
  optimization:
    tone_modeling: true             # 声调建模
    prosody_optimization: true      # 韵律优化
    voice_optimization: true        # 音色优化
```

### 粤语专用配置

```yaml
cantonese_specific:
  prosody_profile: neutral          # 韵律模式: neutral, formal, casual, expressive
  tone_accuracy_target: 0.95        # 声调准确率目标
  semantic_accuracy_target: 0.90    # 语义准确率目标
  audio_quality_target: 8.5         # 音频质量目标
```

### 验证配置

```yaml
validation:
  strict_mode: true                 # 严格模式
  precision_threshold: 0.98         # 精度阈值
  success_rate_threshold: 0.95      # 成功率阈值
  validation_level: strict          # 验证级别
```

---

## 使用示例

### 示例 1: 基本转换

```python
import asyncio
from src.npu_converter.complete_flows.vits_cantonese_complete_flow import VITSCantoneseCompleteFlow

async def basic_conversion():
    flow = VITSCantoneseCompleteFlow(
        conversion_level=CantoneseConversionLevel.PRODUCTION
    )

    result, report_path = await flow.convert_model(
        model_path="models/vits_cantonese.onnx",
        output_path="output/vits_cantonese.bpu"
    )

    if result.success:
        print("转换成功!")
        print(f"报告: {report_path}")
    else:
        print("转换失败")
        print(f"错误: {result.error_message}")

asyncio.run(basic_conversion())
```

### 示例 2: 使用预设配置

```python
from src.npu_converter.config.cantonese_config import VITS_CantoneseConfigStrategy

# 获取预设配置
strategy = VITS_CantoneseConfigStrategy()
presets = strategy.get_preset_configs()

# 使用高质量配置
high_quality_config = presets["high_quality"]

flow = VITSCantoneseCompleteFlow(config=high_quality_config)
result, report_path = await flow.convert_model(
    model_path="models/vits_cantonese.onnx",
    output_path="output/vits_cantonese_hq.bpu"
)
```

### 示例 3: 自定义配置

```python
from src.npu_converter.core.models.config_model import ConfigModel

# 创建自定义配置
custom_config = ConfigModel(
    model_type="vits_cantonese",
    voice_type="male",
    conversion_level="enhanced",
    sample_rate=44100,
    bit_depth=16,
    prosody_profile="formal",
    tone_accuracy_target=0.98
)

flow = VITSCantoneseCompleteFlow(config=custom_config)
result, report_path = await flow.convert_model(
    model_path="models/vits_cantonese.onnx",
    output_path="output/vits_cantonese_custom.bpu"
)
```

---

## 最佳实践

### 1. 选择合适的转换级别

- **Basic**: 快速转换，适合测试
- **Standard**: 平衡性能和质量的日常使用
- **Enhanced**: 高质量转换，适合生产环境
- **Production**: 最高质量，完整功能（推荐）

### 2. 音色选择指南

| 音色 | 适用场景 | 特点 |
|------|----------|------|
| **Female** | 对话、助手 | 自然、清脆 |
| **Male** | 新闻、播报 | 沉稳、权威 |
| **Child** | 儿童内容 | 活泼、可爱 |
| **Neutral** | 通用场景 | 平衡、自然 |

### 3. 韵律模式选择

| 模式 | 适用场景 | 特点 |
|------|----------|------|
| **Neutral** | 通用场景 | 标准、平衡 |
| **Formal** | 正式场合 | 严谨、清晰 |
| **Casual** | 日常对话 | 轻松、自然 |
| **Expressive** | 情感表达 | 丰富、动态 |

### 4. 性能优化建议

1. **批量处理**: 使用`batch_size`参数优化吞吐量
2. **并发转换**: 支持多模型并发转换
3. **缓存优化**: 重复使用配置对象
4. **资源管理**: 及时释放转换流程对象

### 5. 质量保证

1. **验证报告**: 始终检查生成的报告文件
2. **精度监控**: 监控转换精度指标
3. **性能测试**: 定期测试性能指标
4. **A/B测试**: 比较不同配置的效果

---

## 故障排除

### 常见问题

#### 问题 1: 转换失败

**症状**: `ConversionError: Model validation failed`

**解决方案**:
```python
# 检查模型格式
from src.npu_converter.loaders.onnx_loader import ONNXModelLoader

loader = ONNXModelLoader()
model = await loader.load_model("path/to/model.onnx")
print(f"模型格式: {model.format}")
print(f"输入形状: {model.input_shape}")
print(f"输出形状: {model.output_shape}")
```

#### 问题 2: 精度不达标

**症状**: 精度验证失败

**解决方案**:
```python
# 提高转换级别
config = ConfigModel(
    conversion_level="production",  # 使用最高级别
    validation_level="strict"
)
```

#### 问题 3: 转换速度慢

**症状**: 转换时间超过5分钟

**解决方案**:
```python
# 使用快速模式
config = ConfigModel(
    conversion_level="basic",
    batch_size=4  # 增加批处理大小
)
```

### 调试模式

```python
import logging

# 启用详细日志
logging.basicConfig(level=logging.DEBUG)

# 创建转换流程并启用调试
flow = VITSCantoneseCompleteFlow(
    config=config,
    debug=True
)

# 获取详细指标
metrics = flow.get_conversion_metrics()
print(json.dumps(metrics, indent=2))
```

---

## API参考

### VITSCantoneseCompleteFlow

#### 构造函数

```python
VITSCantoneseCompleteFlow(
    config: Optional[ConfigModel] = None,
    operation_id: Optional[str] = None,
    conversion_level: CantoneseConversionLevel = CantoneseConversionLevel.PRODUCTION
)
```

**参数**:
- `config`: 配置模型（可选）
- `operation_id`: 操作ID（可选）
- `conversion_level`: 转换级别

#### 主要方法

##### convert_model()

```python
async def convert_model(
    self,
    model_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    **kwargs
) -> Tuple[ResultModel, Path]
```

执行完整的VITS-Cantonese模型转换。

**参数**:
- `model_path`: 输入ONNX模型路径
- `output_path`: 输出BPU模型路径（可选）
- `**kwargs`: 其他转换参数

**返回**:
- `ResultModel`: 转换结果
- `Path`: 报告文件路径

##### execute_cantonese_optimization()

```python
async def execute_cantonese_optimization(
    self,
    model: ConversionModel
) -> ConversionModel
```

执行粤语专用优化。

##### validate_conversion_precision()

```python
async def validate_conversion_precision(
    self,
    original_model: ConversionModel,
    converted_model: ConversionModel
) -> ValidationResult
```

验证转换精度。

##### generate_conversion_report()

```python
async def generate_conversion_report(
    self,
    conversion_result: ResultModel
) -> Path
```

生成转换报告。

### 配置类

#### VITS_CantoneseConfigStrategy

##### create_config()

```python
def create_config(
    self,
    custom_params: Optional[Dict[str, Any]] = None
) -> ConfigModel
```

创建VITS-Cantonese配置。

##### get_preset_configs()

```python
def get_preset_configs(self) -> Dict[str, ConfigModel]
```

获取预设配置。

**预设配置**:
- `default`: 默认配置
- `high_quality`: 高质量配置
- `fast_inference`: 快速推理配置
- `formal_speech`: 正式语音配置
- `casual_speech`: 日常语音配置

---

## 技术支持

### 性能指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 转换成功率 | >95% | 成功转换的模型比例 |
| 性能提升 | 2-5倍 | NPU vs CPU性能对比 |
| 精度保持率 | >98% | 转换前后精度对比 |
| 转换时间 | <5分钟 | 中等规模模型转换时间 |
| 音频质量评分 | >8.5/10 | 主观质量评估 |

### 系统要求

- **Python**: 3.10+
- **硬件**: RDK X5 NPU (目标)
- **内存**: 8GB+ 推荐
- **存储**: 2GB+ 可用空间
- **Docker**: Ubuntu 20.04 环境

### 相关文档

- [Epic 1 文档](../README.md): 基础设施说明
- [Story 1.5 文档](../stories/story-1.5.md): 基础转换流程
- [PRD文档](../PRD.md): 产品需求文档
- [技术决策文档](../technical-decisions.md): 技术决策记录

---

**文档版本**: 1.0.0
**最后更新**: 2025-10-27
**Story**: 2.2
**作者**: Story 2.2 Implementation Team
