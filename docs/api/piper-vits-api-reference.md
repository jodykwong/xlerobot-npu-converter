# Piper VITS API 参考文档

**版本**: 1.0.0
**日期**: 2025-10-28
**项目**: xlerobot - Story 2.4

---

## 目录

1. [概述](#概述)
2. [PiperVITSConversionFlow](#pipervitsconversionflow)
3. [BPUToolchainSimulator](#bputoolchainsimulator)
4. [ONNXModelSimulator](#onnxmodelsimulator)
5. [PiperVITSConfigStrategy](#pipervitsconfigstrategy)
6. [数据类型](#数据类型)
7. [异常处理](#异常处理)
8. [示例代码](#示例代码)

---

## 概述

Piper VITS API提供了完整的模型转换功能，包括：

- 模型转换流程管理
- BPU工具链集成
- ONNX模型处理
- 配置管理
- 量化优化

### 导入方式

```python
from npu_converter.converters.piper_vits_flow import PiperVITSConversionFlow
from npu_converter.tools.bpu_toolchain_simulator import BPUToolchainSimulator
from npu_converter.tools.onnx_model_simulator import ONNXModelSimulator
from npu_converter.config.strategies.piper_vits_strategy import PiperVITSConfigStrategy
```

---

## PiperVITSConversionFlow

转换流程的主要类，负责管理完整的Piper VITS模型转换流程。

### 类定义

```python
class PiperVITSConversionFlow(BaseConversionFlow)
```

### 初始化

#### `__init__(config=None, operation_id=None)`

创建新的转换流实例。

**参数**:
- `config` (ConfigModel | None): 配置对象，可选
- `operation_id` (str | None): 操作标识符，可选

**示例**:
```python
from npu_converter.converters.piper_vits_flow import PiperVITSConversionFlow

# 基本初始化
flow = PiperVITSConversionFlow()

# 带配置初始化
config = {...}  # 配置字典
flow = PiperVITSConversionFlow(config=config)

# 带操作ID初始化
flow = PiperVITSConversionFlow(operation_id="conversion_001")
```

### 主要方法

#### `convert_model(model_path, output_path, **kwargs) -> ConversionResult`

执行模型转换。

**参数**:
- `model_path` (str | Path): 输入ONNX模型路径
- `output_path` (str | Path): 输出BPU模型路径
- `**kwargs`: 附加参数

**返回**:
- `ConversionResult`: 转换结果对象

**示例**:
```python
result = flow.convert_model(
    model_path="input.onnx",
    output_path="output.bpu"
)

print(f"转换成功: {result.success}")
print(f"输出路径: {result.output_path}")
```

#### `create_progress_steps() -> List[ProgressStep]`

创建转换进度步骤。

**返回**:
- `List[ProgressStep]`: 进度步骤列表

**示例**:
```python
steps = flow.create_progress_steps()
for step in steps:
    print(f"步骤: {step.name}, 权重: {step.weight}")
```

#### `execute_conversion_stage(stage, conversion_model) -> bool`

执行单个转换阶段。

**参数**:
- `stage` (ConversionStage): 转换阶段
- `conversion_model` (ConversionModel): 转换模型对象

**返回**:
- `bool`: 阶段执行成功返回True

**示例**:
```python
from npu_converter.core.models.conversion_model import ConversionStage

success = flow.execute_conversion_stage(
    stage=ConversionStage.INITIALIZATION,
    conversion_model=model
)
```

#### `export_results(conversion_model, output_dir, **kwargs) -> ExportResult`

导出转换结果。

**参数**:
- `conversion_model` (ConversionModel): 转换模型对象
- `output_dir` (str | Path): 输出目录
- `**kwargs`: 附加参数

**返回**:
- `ExportResult`: 导出结果对象

**示例**:
```python
result = flow.export_results(
    conversion_model=model,
    output_dir="output/"
)
```

#### `get_conversion_summary(conversion_model) -> dict`

获取转换摘要。

**参数**:
- `conversion_model` (ConversionModel): 转换模型对象

**返回**:
- `dict`: 转换摘要字典

**示例**:
```python
summary = flow.get_conversion_summary(model)
print(f"模型类型: {summary['model_type']}")
print(f"转换状态: {summary['status']}")
```

### 属性

#### `model_architecture`

模型架构类型。

**类型**: `str`
**值**: `"piper_vits"`

#### `target_hardware`

目标硬件。

**类型**: `str`
**值**: `"horizon_x5"`

#### `language`

当前语言。

**类型**: `str`
**默认值**: `"cantonese"`

#### `piper_config`

Piper VITS特定配置。

**类型**: `dict`
**默认**: `{}`

#### `bpu_toolchain`

BPU工具链实例。

**类型**: `BPUToolchainSimulator | None`

---

## BPUToolchainSimulator

BPU工具链模拟器，提供BPU工具链功能的模拟实现。

### 类定义

```python
class BPUToolchainSimulator
```

### 初始化

#### `__init__(toolchain_path=None)`

创建模拟器实例。

**参数**:
- `toolchain_path` (str | None): 工具链路径，可选

**示例**:
```python
from npu_converter.tools.bpu_toolchain_simulator import BPUToolchainSimulator

# 基本初始化
simulator = BPUToolchainSimulator()

# 指定路径
simulator = BPUToolchainSimulator(toolchain_path="/opt/bpu")
```

### 主要方法

#### `check_environment() -> Dict[str, Any]`

检查工具链环境。

**返回**:
```python
{
    "status": "ready",
    "version": "5.0.0-simulator",
    "toolchain_path": "/opt/horizon_x5_bpu",
    "simulation_mode": True,
    "checks": {
        "toolchain_available": True,
        "environment_variables": {...},
        "compiler_availability": True,
        "library_availability": True,
        "hardware_compatibility": True
    }
}
```

#### `compile_model(model_path, model_type, optimization_level=2, output_path=None) -> Dict[str, Any]`

编译模型。

**参数**:
- `model_path` (str): 输入模型路径
- `model_type` (str): 模型类型
- `optimization_level` (int): 优化级别 (0-3)
- `output_path` (str | None): 输出路径

**返回**:
```python
{
    "status": "success",
    "input_model": "input.onnx",
    "output_model": "output.bpu",
    "model_type": "piper_vits",
    "optimization_level": 2,
    "compilation_time_seconds": 120,
    "simulated_metrics": {
        "model_size_mb": 85.5,
        "peak_memory_mb": 512,
        "inference_latency_ms": 150.0,
        "throughput_fps": 15.0
    }
}
```

#### `quantize_model(model_path, quantization_bits=8, calibration_data=None) -> Dict[str, Any]`

量化模型。

**参数**:
- `model_path` (str): 模型路径
- `quantization_bits` (int): 量化位数 (8或16)
- `calibration_data` (Dict | None): 校准数据

**返回**:
```python
{
    "status": "success",
    "input_model": "input.onnx",
    "quantization_bits": 8,
    "accuracy_degradation_percent": 2.5,
    "simulated_metrics": {
        "model_size_reduction_percent": 75,
        "inference_speedup": 2.3
    }
}
```

#### `optimize_model(model_path, optimization_level=2) -> Dict[str, Any]`

优化模型。

**参数**:
- `model_path` (str): 模型路径
- `optimization_level` (int): 优化级别 (0-3)

**返回**:
```python
{
    "status": "success",
    "input_model": "input.onnx",
    "optimization_level": 2,
    "optimizations_applied": [
        "basic_constant_folding",
        "operator_fusion",
        "graph_optimization"
    ],
    "simulated_metrics": {
        "latency_reduction_percent": 50,
        "speedup_factor": 1.5
    }
}
```

#### `get_toolchain_info() -> Dict[str, Any]`

获取工具链信息。

**返回**:
```python
{
    "name": "Horizon X5 BPU Toolchain",
    "version": "5.0.0-simulator",
    "simulation_mode": True,
    "supported_models": ["piper_vits", "sensevoice", "vits_cantonese"],
    "capabilities": [
        "ONNX to BPU compilation",
        "PTQ quantization (8-bit, 16-bit)",
        "Model optimization (levels 0-3)"
    ]
}
```

---

## ONNXModelSimulator

ONNX模型模拟器，提供ONNX模型的加载、验证和分析功能。

### 类定义

```python
class ONNXModelSimulator
```

### 初始化

#### `__init__()`

创建模拟器实例。

**示例**:
```python
from npu_converter.tools.onnx_model_simulator import ONNXModelSimulator

simulator = ONNXModelSimulator()
```

### 主要方法

#### `load_model(model_path, model_type) -> Dict[str, Any]`

加载模型。

**参数**:
- `model_path` (str): 模型路径
- `model_type` (str): 模型类型

**返回**:
```python
{
    "model_type": "piper_vits",
    "opset_version": 14,
    "inputs": [...],
    "outputs": [...],
    "nodes": [...],
    "file_size_bytes": 89473280
}
```

#### `validate_model(model_metadata) -> Dict[str, Any]`

验证模型。

**参数**:
- `model_metadata` (Dict): 模型元数据

**返回**:
```python
{
    "is_valid": True,
    "missing_fields": [],
    "warnings": [],
    "errors": []
}
```

#### `analyze_model(model_metadata) -> Dict[str, Any]`

分析模型。

**参数**:
- `model_metadata` (Dict): 模型元数据

**返回**:
```python
{
    "model_type": "piper_vits",
    "total_nodes": 45,
    "operators": {
        "Conv": 12,
        "Relu": 8,
        "LayerNormalization": 3
    },
    "parameters": {
        "total_parameters": 15000000,
        "trainable_parameters": 15000000
    },
    "complexity": "high"
}
```

---

## PiperVITSConfigStrategy

Piper VITS配置策略类，负责配置管理和验证。

### 类定义

```python
class PiperVITSConfigStrategy(BaseConfigStrategy)
```

### 初始化

#### `__init__()`

创建策略实例。

**示例**:
```python
from npu_converter.config.strategies.piper_vits_strategy import PiperVITSConfigStrategy

strategy = PiperVITSConfigStrategy()
```

### 主要方法

#### `create_default_template() -> dict`

创建默认配置模板。

**返回**:
```python
{
    "project": {
        "name": "piper_vits_conversion",
        "version": "1.0.0",
        "model_type": "piper_vits"
    },
    "hardware": {
        "target_device": "horizon_x5",
        "optimization_level": 2
    },
    "conversion_params": {
        "input_format": "onnx",
        "output_format": "bpu",
        "precision": "int8"
    },
    "model_specific": {
        "piper_vits": {
            "sample_rate": 22050,
            "mel_channels": 80,
            "speaker_embedding": True
        }
    }
}
```

#### `validate(config, strict=True) -> ValidationResult`

验证配置。

**参数**:
- `config` (dict): 配置字典
- `strict` (bool): 严格模式

**返回**:
```python
{
    "is_valid": True,
    "errors": [],
    "warnings": []
}
```

#### `merge(base, overrides) -> dict`

合并配置。

**参数**:
- `base` (dict): 基础配置
- `overrides` (dict): 覆盖配置

**返回**:
- `dict`: 合并后的配置

**示例**:
```python
base = strategy.create_default_template()
overrides = {"sample_rate": 44100}
config = strategy.merge(base, overrides)
```

### 配置字段

#### 基础配置

| 字段 | 类型 | 描述 | 默认值 |
|------|------|------|--------|
| sample_rate | int | 采样率 (Hz) | 22050 |
| mel_channels | int | Mel通道数 | 80 |
| voice_name | str | 声音名称 | "default" |

#### 语言配置

| 字段 | 类型 | 描述 | 默认值 |
|------|------|------|--------|
| language | str | 语言代码 | "cantonese" |
| phoneme_system | str | 音素系统 | "jyutping" |

#### 说话人配置

| 字段 | 类型 | 描述 | 默认值 |
|------|------|------|--------|
| speaker_embedding | bool | 启用说话人嵌入 | True |
| num_speakers | int | 说话人数量 | 1 |
| embedding_dim | int | 嵌入维度 | 192 |

#### 量化配置

| 字段 | 类型 | 描述 | 默认值 |
|------|------|------|--------|
| quantization_bits | int | 量化位数 | 8 |
| optimization_level | int | 优化级别 | 2 |

#### 音频处理

| 字段 | 类型 | 描述 | 默认值 |
|------|------|------|--------|
| n_fft | int | FFT大小 | 1024 |
| hop_size | int | 跳跃长度 | 256 |
| win_size | int | 窗口大小 | 1024 |

#### 合成参数

| 字段 | 类型 | 描述 | 默认值 |
|------|------|------|--------|
| noise_scale | float | 噪声尺度 | 0.5 |
| length_scale | float | 长度尺度 | 1.0 |
| temperature | float | 温度 | 1.0 |
| max_decoder_steps | int | 最大解码步数 | 1000 |

#### VITS架构

| 字段 | 类型 | 描述 | 默认值 |
|------|------|------|--------|
| inter_channels | int | 中间通道数 | 192 |
| hidden_channels | int | 隐藏通道数 | 192 |
| filter_channels | int | 滤波器通道数 | 768 |
| n_heads | int | 注意力头数 | 2 |
| n_layers | int | 层数 | 6 |

#### 高级特性

| 字段 | 类型 | 描述 | 默认值 |
|------|------|------|--------|
| use_sdp | bool | 使用SDP | True |
| use_spectral_norm | bool | 使用谱归一化 | False |
| gin_channels | int | GIN通道数 | 256 |

---

## 数据类型

### ConversionStage

转换阶段枚举。

```python
class ConversionStage(Enum):
    INITIALIZATION = "initialization"
    VALIDATION = "validation"
    PREPROCESSING = "preprocessing"
    PHONEME_MAPPING = "phoneme_mapping"
    QUANTIZATION = "quantization"
    COMPILATION = "compilation"
    OPTIMIZATION = "optimization"
    VALIDATION_POST = "validation_post"
    EXPORT = "export"
```

### ConversionResult

转换结果对象。

**属性**:
- `success` (bool): 转换是否成功
- `output_path` (Path): 输出路径
- `model_size_mb` (float): 模型大小 (MB)
- `inference_latency_ms` (float): 推理延迟 (ms)
- `throughput_fps` (float): 吞吐量 (FPS)
- `error` (str | None): 错误信息

### ValidationResult

验证结果对象。

**属性**:
- `is_valid` (bool): 是否有效
- `errors` (List[str]): 错误列表
- `warnings` (List[str]): 警告列表

### ExportResult

导出结果对象。

**属性**:
- `success` (bool): 导出是否成功
- `output_dir` (Path): 输出目录
- `files` (List[Path]): 输出文件列表
- `error` (str | None): 错误信息

---

## 异常处理

### ConversionError

转换错误异常。

```python
from npu_converter.exceptions.conversion_errors import ConversionError

try:
    result = flow.convert_model(...)
except ConversionError as e:
    print(f"转换错误: {e}")
```

### ValidationError

验证错误异常。

```python
from npu_converter.exceptions.conversion_errors import ValidationError

try:
    strategy.validate(config)
except ValidationError as e:
    print(f"验证错误: {e}")
```

### ConfigurationError

配置错误异常。

```python
from npu_converter.exceptions.conversion_errors import ConfigurationError

try:
    flow.piper_config = config
except ConfigurationError as e:
    print(f"配置错误: {e}")
```

---

## 示例代码

### 基本使用

```python
#!/usr/bin/env python3
"""
基本使用示例
"""

from npu_converter.converters.piper_vits_flow import PiperVITSConversionFlow

# 创建转换流程
flow = PiperVITSConversionFlow()

# 配置参数
flow.piper_config = {
    "sample_rate": 22050,
    "language": "cantonese",
    "quantization_bits": 8
}

# 转换模型
result = flow.convert_model(
    model_path="input.onnx",
    output_path="output.bpu"
)

print(f"转换成功: {result.success}")
```

### 完整示例

```python
#!/usr/bin/env python3
"""
完整示例：带错误处理的模型转换
"""

from npu_converter.converters.piper_vits_flow import PiperVITSConversionFlow
from npu_converter.exceptions.conversion_errors import ConversionError

def convert_piper_vits(input_path, output_path, language="cantonese"):
    """转换Piper VITS模型"""
    try:
        # 创建转换流程
        flow = PiperVITSConversionFlow()

        # 配置参数
        flow.piper_config = {
            "sample_rate": 22050,
            "mel_channels": 80,
            "language": language,
            "quantization_bits": 8,
            "optimization_level": 2,
            "speaker_embedding": True
        }

        print(f"开始转换: {input_path}")
        print(f"语言: {language}")
        print(f"量化: 8-bit")

        # 执行转换
        result = flow.convert_model(
            model_path=input_path,
            output_path=output_path
        )

        if result.success:
            print("\n✅ 转换成功！")
            print(f"输出路径: {result.output_path}")
            print(f"模型大小: {result.model_size_mb:.1f} MB")
            print(f"推理延迟: {result.inference_latency_ms:.1f} ms")
            print(f"吞吐量: {result.throughput_fps:.1f} FPS")
            return True
        else:
            print(f"\n❌ 转换失败: {result.error}")
            return False

    except ConversionError as e:
        print(f"\n❌ 转换错误: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 未知错误: {e}")
        return False

if __name__ == "__main__":
    convert_piper_vits(
        input_path="input.onnx",
        output_path="output.bpu",
        language="cantonese"
    )
```

### 多语言示例

```python
#!/usr/bin/env python3
"""
多语言转换示例
"""

from npu_converter.converters.piper_vits_flow import PiperVITSConversionFlow

def convert_multilingual():
    """转换多种语言模型"""
    languages = [
        ("cantonese", "cantonese_model.onnx", "cantonese_model.bpu"),
        ("mandarin", "mandarin_model.onnx", "mandarin_model.bpu"),
        ("english", "english_model.onnx", "english_model.bpu")
    ]

    for lang, input_file, output_file in languages:
        print(f"\n{'='*50}")
        print(f"转换 {lang} 模型")
        print(f"{'='*50}")

        flow = PiperVITSConversionFlow()
        flow.language = lang
        flow.piper_config = {
            "sample_rate": 22050,
            "quantization_bits": 8
        }

        result = flow.convert_model(
            model_path=input_file,
            output_path=output_file
        )

        if result.success:
            print(f"✅ {lang} 转换成功")
        else:
            print(f"❌ {lang} 转换失败: {result.error}")

if __name__ == "__main__":
    convert_multilingual()
```

### 批处理示例

```python
#!/usr/bin/env python3
"""
批处理转换示例
"""

from npu_converter.converters.piper_vits_flow import PiperVITSConversionFlow
from pathlib import Path

def batch_convert(input_dir, output_dir):
    """批量转换模型"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # 查找所有ONNX文件
    onnx_files = list(input_path.glob("*.onnx"))

    print(f"找到 {len(onnx_files)} 个模型文件")
    print(f"输入目录: {input_path}")
    print(f"输出目录: {output_path}")

    success_count = 0
    failed_count = 0

    for onnx_file in onnx_files:
        output_file = output_path / f"{onnx_file.stem}.bpu"

        flow = PiperVITSConversionFlow()
        result = flow.convert_model(
            model_path=onnx_file,
            output_path=output_file
        )

        if result.success:
            print(f"✅ {onnx_file.name} -> {output_file.name}")
            success_count += 1
        else:
            print(f"❌ {onnx_file.name} 转换失败")
            failed_count += 1

    print(f"\n批处理完成:")
    print(f"成功: {success_count}")
    print(f"失败: {failed_count}")
    print(f"总计: {len(onnx_files)}")

if __name__ == "__main__":
    batch_convert(
        input_dir="input_models",
        output_dir="output_models"
    )
```

### 配置验证示例

```python
#!/usr/bin/env python3
"""
配置验证示例
"""

from npu_converter.config.strategies.piper_vits_strategy import PiperVITSConfigStrategy

def validate_config():
    """验证配置"""
    strategy = PiperVITSConfigStrategy()

    # 创建配置
    config = {
        "sample_rate": 22050,
        "mel_channels": 80,
        "language": "cantonese",
        "quantization_bits": 8
    }

    print("验证配置:")
    print(config)

    # 验证配置
    result = strategy.validate(config)

    print(f"\n验证结果:")
    print(f"是否有效: {result.is_valid}")

    if result.errors:
        print(f"错误: {result.errors}")

    if result.warnings:
        print(f"警告: {result.warnings}")

    # 应用默认值
    template = strategy.create_default_template()
    print(f"\n默认配置:")
    print(template)

if __name__ == "__main__":
    validate_config()
```

---

**API参考文档结束**

如需更多信息，请参阅：
- [技术文档](../technical/piper-vits-technical-guide.md)
- [用户指南](../user/piper-vits-user-guide.md)
- [项目仓库](https://github.com/your-org/xlerobot)
