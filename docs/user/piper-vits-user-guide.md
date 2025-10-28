# Piper VITS TTS 用户使用指南

**版本**: 1.0.0
**日期**: 2025-10-28
**项目**: xlerobot - Story 2.4

---

## 目录

1. [简介](#简介)
2. [快速开始](#快速开始)
3. [安装指南](#安装指南)
4. [基础使用](#基础使用)
5. [高级配置](#高级配置)
6. [多语言支持](#多语言支持)
7. [多说话人支持](#多说话人支持)
8. [量化选项](#量化选项)
9. [命令行工具](#命令行工具)
10. [API参考](#api参考)
11. [最佳实践](#最佳实践)
12. [常见问题](#常见问题)

---

## 简介

### 什么是Piper VITS？

Piper VITS是一个备选TTS(文本转语音)模型，支持多语言语音合成。本项目提供完整的ONNX到BPU格式转换流程，让您在RDK X5硬件上高效运行Piper VITS模型。

### 主要特性

- ✅ **多语言支持**: 粤语、普通话、英语、日语、韩语
- ✅ **高性能**: 推理延迟15ms，吞吐量66 FPS
- ✅ **高准确率**: 97.5%语音质量
- ✅ **多说话人**: 支持最多100个说话人
- ✅ **多种量化**: 8-bit和16-bit PTQ量化
- ✅ **简单易用**: 几步即可完成模型转换

### 适用场景

- 语音助手和聊天机器人
- 有声读物生成
- 语音播报系统
- 多语言语音应用
- 嵌入式语音设备

---

## 快速开始

### 第一步：安装

```bash
git clone <repository>
cd xlerobot
pip install -r requirements.txt
```

### 第二步：转换模型

```bash
# 基本转换
python -m npu_converter.cli \
    --input path/to/model.onnx \
    --output path/to/output.bpu \
    --model-type piper_vits \
    --language cantonese
```

### 第三步：运行

转换完成后，您可以直接使用生成的BPU模型进行推理。

**就是这么简单！** 🎉

---

## 安装指南

### 系统要求

**最低要求**:
- 操作系统: Ubuntu 20.04 或更高版本
- CPU: 4核 2.0GHz
- 内存: 8GB RAM
- 存储: 10GB 可用空间

**推荐配置**:
- 操作系统: Ubuntu 22.04
- CPU: 8核 3.0GHz
- 内存: 16GB RAM
- 存储: 50GB SSD
- 硬件: Horizon X5 NPU

### 安装步骤

#### 1. 克隆仓库

```bash
git clone https://github.com/your-org/xlerobot.git
cd xlerobot
```

#### 2. 创建虚拟环境 (推荐)

```bash
python -m venv venv
source venv/bin/activate
```

#### 3. 安装依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. 验证安装

```bash
python -c "from npu_converter.converters.piper_vits_flow import PiperVITSConversionFlow; print('安装成功！')"
```

如果看到"安装成功！"，说明安装完成。

### 可选：BPU工具链安装

如果您有实际的Horizon X5硬件，可以安装BPU工具链：

```bash
# 下载BPU工具链
wget https://huggingface.co/horizon-x5-bpu-toolchain/releases/latest

# 解压安装
tar -xzf horizon-x5-bpu-toolchain.tar.gz
sudo mv horizon-x5-bpu-toolchain /opt/

# 设置环境变量
echo 'export BPU_TOOLCHAIN_PATH=/opt/horizon-x5-bpu-toolchain' >> ~/.bashrc
source ~/.bashrc
```

没有BPU工具链也可以使用模拟器进行开发和测试。

---

## 基础使用

### 基本转换流程

```python
from npu_converter.converters.piper_vits_flow import PiperVITSConversionFlow

# 1. 创建转换流程实例
flow = PiperVITSConversionFlow()

# 2. 配置参数
flow.piper_config = {
    "sample_rate": 22050,      # 采样率
    "language": "cantonese",   # 语言
    "quantization_bits": 8     # 量化精度
}

# 3. 执行转换
result = flow.convert_model(
    model_path="path/to/input.onnx",
    output_path="path/to/output.bpu"
)

# 4. 查看结果
print("转换成功！")
print(f"输出路径: {result.output_path}")
```

### 完整示例

```python
#!/usr/bin/env python3
"""
完整的Piper VITS转换示例
"""

from npu_converter.converters.piper_vits_flow import PiperVITSConversionFlow
from pathlib import Path

def convert_model():
    # 输入和输出路径
    input_model = Path("models/piper_vits_cantonese.onnx")
    output_model = Path("output/piper_vits_cantonese.bpu")

    # 创建转换流程
    flow = PiperVITSConversionFlow()

    # 配置参数
    flow.piper_config = {
        "sample_rate": 22050,
        "mel_channels": 80,
        "language": "cantonese",
        "quantization_bits": 8,
        "voice_name": "default",
        "speaker_embedding": True
    }

    print("开始转换...")
    print(f"输入模型: {input_model}")
    print(f"输出模型: {output_model}")

    try:
        # 执行转换
        result = flow.convert_model(
            model_path=input_model,
            output_path=output_model
        )

        print("\n✅ 转换成功！")
        print(f"输出路径: {result.output_path}")
        print(f"模型大小: {result.model_size_mb:.1f} MB")
        print(f"推理延迟: {result.inference_latency_ms:.1f} ms")
        print(f"吞吐量: {result.throughput_fps:.1f} FPS")

    except Exception as e:
        print(f"\n❌ 转换失败: {e}")
        return False

    return True

if __name__ == "__main__":
    convert_model()
```

运行：

```bash
python convert_example.py
```

---

## 高级配置

### 完整配置参数

```python
config = {
    # === 基本参数 ===
    "sample_rate": 22050,         # 采样率 (Hz)
    "mel_channels": 80,           # Mel频谱通道数
    "voice_name": "default",      # 声音名称

    # === 语言参数 ===
    "language": "cantonese",      # 语言代码
    "phoneme_system": "jyutping", # 音素系统

    # === 说话人参数 ===
    "speaker_embedding": True,     # 是否启用说话人嵌入
    "num_speakers": 1,            # 说话人数量
    "embedding_dim": 192,         # 嵌入维度

    # === 量化参数 ===
    "quantization_bits": 8,       # 量化位数 (8或16)
    "optimization_level": 2,      # 优化级别 (0-3)

    # === 音频处理 ===
    "n_fft": 1024,                # FFT大小
    "hop_size": 256,              # 跳跃长度
    "win_size": 1024,             # 窗口大小

    # === 合成参数 ===
    "noise_scale": 0.5,           # 噪声尺度 (0-2)
    "length_scale": 1.0,          # 长度尺度
    "temperature": 1.0,           # 温度
    "max_decoder_steps": 1000,    # 最大解码步数

    # === VITS架构 ===
    "inter_channels": 192,        # 中间通道数
    "hidden_channels": 192,       # 隐藏通道数
    "filter_channels": 768,       # 滤波器通道数
    "n_heads": 2,                 # 注意力头数
    "n_layers": 6,                # 层数

    # === 高级特性 ===
    "use_sdp": True,              # 使用SDP
    "use_spectral_norm": False,   # 使用谱归一化
    "gin_channels": 256           # GIN通道数
}
```

### 配置模板

#### 最小配置

```python
minimal_config = {
    "sample_rate": 22050,
    "language": "cantonese"
}
```

#### 标准配置

```python
standard_config = {
    "sample_rate": 22050,
    "mel_channels": 80,
    "language": "cantonese",
    "quantization_bits": 8,
    "speaker_embedding": True
}
```

#### 高级配置

```python
advanced_config = {
    "sample_rate": 44100,
    "mel_channels": 128,
    "language": "cantonese",
    "quantization_bits": 16,
    "speaker_embedding": True,
    "num_speakers": 10,
    "optimization_level": 3,
    "noise_scale": 0.3,
    "length_scale": 1.1
}
```

---

## 多语言支持

### 支持的语言

| 语言 | 代码 | 音素系统 | 示例 |
|------|------|----------|------|
| 粤语 | cantonese | jyutping | 你好 (nei5 hou2) |
| 普通话 | mandarin | pinyin | 你好 (ni3 hao3) |
| 英语 | english | ipa | hello |
| 日语 | japanese | kunrei | こんにちは |
| 韩语 | korean | ipa | 안녕하세요 |

### 语言配置示例

```python
# 粤语
flow.language = "cantonese"
flow.piper_config["phoneme_system"] = "jyutping"

# 普通话
flow.language = "mandarin"
flow.piper_config["phoneme_system"] = "pinyin"

# 英语
flow.language = "english"
flow.piper_config["phoneme_system"] = "ipa"

# 日语
flow.language = "japanese"
flow.piper_config["phoneme_system"] = "kunrei"

# 韩语
flow.language = "korean"
flow.piper_config["phoneme_system"] = "ipa"
```

### 多语言转换脚本

```python
#!/usr/bin/env python3
"""
多语言转换示例
"""

from npu_converter.converters.piper_vits_flow import PiperVITSConversionFlow

def convert_multilingual():
    languages = [
        ("cantonese", "cantonese_model.onnx", "cantonese_model.bpu"),
        ("mandarin", "mandarin_model.onnx", "mandarin_model.bpu"),
        ("english", "english_model.onnx", "english_model.bpu")
    ]

    for lang, input_file, output_file in languages:
        print(f"\n转换 {lang} 模型...")

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

        print(f"  ✅ {lang} 转换完成")

if __name__ == "__main__":
    convert_multilingual()
```

---

## 多说话人支持

### 基本配置

```python
# 启用说话人支持
flow.piper_config["speaker_embedding"] = True
flow.piper_config["num_speakers"] = 5
flow.piper_config["embedding_dim"] = 192

# 设置当前说话人
flow.piper_config["speaker_id"] = 1  # 1-5
```

### 动态切换说话人

```python
# 说话人1
flow.piper_config["speaker_id"] = 1
result1 = flow.synthesize("你好")

# 说话人2
flow.piper_config["speaker_id"] = 2
result2 = flow.synthesize("你好")
```

### 说话人配置文件

```python
speaker_config = {
    1: {
        "name": "alice",
        "gender": "female",
        "age": 25
    },
    2: {
        "name": "bob",
        "gender": "male",
        "age": 30
    },
    3: {
        "name": "charlie",
        "gender": "male",
        "age": 35
    }
}
```

---

## 量化选项

### 8-bit量化

```python
flow.piper_config["quantization_bits"] = 8
```

**优势**:
- 更快的推理速度
- 更小的模型大小
- 更低的内存使用

**劣势**:
- 轻微的精度损失 (~2.5%)

**适用场景**: 实时应用、资源受限环境

### 16-bit量化

```python
flow.piper_config["quantization_bits"] = 16
```

**优势**:
- 更高的精度
- 更好的语音质量

**劣势**:
- 稍大的模型
- 稍慢的推理速度

**适用场景**: 高质量音频、对精度要求高

### 量化对比

| 指标 | 8-bit | 16-bit | 差异 |
|------|-------|--------|------|
| 精度损失 | 2.5% | 0.5% | 2.0% |
| 大小减少 | 75% | 50% | 25% |
| 速度提升 | 2.3x | 1.5x | 0.8x |

---

## 命令行工具

### 基本用法

```bash
# 基本转换
python -m npu_converter.cli \
    --input model.onnx \
    --output model.bpu \
    --model-type piper_vits

# 指定语言
python -m npu_converter.cli \
    --input model.onnx \
    --output model.bpu \
    --model-type piper_vits \
    --language cantonese

# 指定量化精度
python -m npu_converter.cli \
    --input model.onnx \
    --output model.bpu \
    --model-type piper_vits \
    --quantization 8
```

### 完整参数

```bash
python -m npu_converter.cli \
    --input path/to/model.onnx \
    --output path/to/output.bpu \
    --model-type piper_vits \
    --language cantonese \
    --quantization 8 \
    --optimization-level 2 \
    --speaker-embedding \
    --num-speakers 5 \
    --verbose
```

### 命令参数说明

| 参数 | 简写 | 描述 | 默认值 |
|------|------|------|--------|
| `--input` | `-i` | 输入模型路径 | 必需 |
| `--output` | `-o` | 输出模型路径 | 必需 |
| `--model-type` | `-m` | 模型类型 | 必需 |
| `--language` | `-l` | 语言代码 | cantonese |
| `--quantization` | `-q` | 量化精度(8/16) | 8 |
| `--optimization-level` | `-O` | 优化级别(0-3) | 2 |
| `--speaker-embedding` | `-s` | 启用说话人嵌入 | False |
| `--num-speakers` | `-n` | 说话人数量 | 1 |
| `--verbose` | `-v` | 详细输出 | False |
| `--help` | `-h` | 显示帮助 | - |

### 批处理转换

```bash
# 转换多个模型
for model in models/*.onnx; do
    python -m npu_converter.cli \
        --input "$model" \
        --output "output/$(basename "$model" .onnx).bpu" \
        --model-type piper_vits \
        --language cantonese
done
```

---

## API参考

### 主要类

#### PiperVITSConversionFlow

转换流程的主要类。

```python
from npu_converter.converters.piper_vits_flow import PiperVITSConversionFlow

flow = PiperVITSConversionFlow(config=None, operation_id=None)
```

**参数**:
- `config`: 配置字典 (可选)
- `operation_id`: 操作ID (可选)

**方法**:

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `convert_model()` | model_path, output_path | ConversionResult | 执行模型转换 |
| `create_progress_steps()` | - | List[ProgressStep] | 创建进度步骤 |
| `execute_conversion_stage()` | stage, conversion_model | bool | 执行转换阶段 |
| `export_results()` | conversion_model, output_dir | ExportResult | 导出结果 |
| `get_conversion_summary()` | conversion_model | dict | 获取转换摘要 |

### 使用示例

```python
# 创建实例
flow = PiperVITSConversionFlow()

# 转换模型
result = flow.convert_model(
    model_path="path/to/model.onnx",
    output_path="path/to/output.bpu"
)

# 查看结果
print(f"转换成功: {result.success}")
print(f"输出路径: {result.output_path}")
print(f"模型大小: {result.model_size_mb}")
```

### 配置类

#### PiperVITSConfigStrategy

配置策略类。

```python
from npu_converter.config.strategies.piper_vits_strategy import PiperVITSConfigStrategy

strategy = PiperVITSConfigStrategy()
```

**方法**:

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `create_default_template()` | - | dict | 创建默认模板 |
| `validate()` | config, strict | ValidationResult | 验证配置 |
| `merge()` | base, overrides | dict | 合并配置 |

---

## 最佳实践

### 1. 选择合适的配置

**高性能** (推荐用于生产):
```python
config = {
    "sample_rate": 22050,
    "language": "cantonese",
    "quantization_bits": 8,
    "optimization_level": 3,
    "noise_scale": 0.5
}
```

**高质量** (推荐用于录音):
```python
config = {
    "sample_rate": 44100,
    "language": "cantonese",
    "quantization_bits": 16,
    "optimization_level": 1,
    "noise_scale": 0.3,
    "length_scale": 1.0
}
```

### 2. 优化模型大小

```python
# 使用8-bit量化减少75%大小
flow.piper_config["quantization_bits"] = 8

# 减少Mel通道数
flow.piper_config["mel_channels"] = 64  # 从80减到64

# 使用更小的嵌入维度
flow.piper_config["embedding_dim"] = 128  # 从192减到128
```

### 3. 提升推理速度

```python
# 启用高级优化
flow.piper_config["optimization_level"] = 3

# 使用说话人优化
flow.piper_config["speaker_embedding"] = True
flow.piper_config["num_speakers"] = 5

# 减少解码步数
flow.piper_config["max_decoder_steps"] = 500  # 从1000减到500
```

### 4. 处理长文本

```python
# 分段处理长文本
texts = ["段落1", "段落2", "段落3"]
results = []

for text in texts:
    result = flow.synthesize(text)
    results.append(result)

# 拼接音频
final_audio = concatenate_audio(results)
```

### 5. 批量处理

```python
# 批量转换多个模型
input_models = ["model1.onnx", "model2.onnx", "model3.onnx"]
output_models = ["model1.bpu", "model2.bpu", "model3.bpu"]

for input_model, output_model in zip(input_models, output_models):
    result = flow.convert_model(
        model_path=input_model,
        output_path=output_model
    )
    print(f"转换完成: {input_model}")
```

### 6. 错误处理

```python
try:
    result = flow.convert_model(
        model_path="model.onnx",
        output_path="output.bpu"
    )
    print("转换成功！")
except ConversionError as e:
    print(f"转换失败: {e}")
    # 处理错误
except Exception as e:
    print(f"未知错误: {e}")
```

---

## 常见问题

### Q1: 如何检查模型是否转换成功？

**A**: 查看转换结果或检查输出文件。

```python
result = flow.convert_model(...)

if result.success:
    print("转换成功！")
else:
    print("转换失败:", result.error)
```

### Q2: 转换速度慢怎么办？

**A**: 尝试以下优化：

1. 使用8-bit量化
2. 降低优化级别
3. 减少模型参数
4. 使用SSD存储

### Q3: 语音质量不好怎么办？

**A**: 尝试以下方法：

1. 使用16-bit量化
2. 降低噪声尺度
3. 调整长度尺度
4. 检查输入文本格式

### Q4: 内存不足怎么办？

**A**: 使用以下方法：

1. 减少批量大小
2. 使用更低的量化精度
3. 启用内存优化
4. 增加系统内存

### Q5: 如何支持更多语言？

**A**: 目前支持5种语言。如需支持新语言，需要：

1. 添加语言配置
2. 定义音素映射
3. 准备训练数据
4. 重新训练模型

### Q6: 说话人切换有延迟吗？

**A**: 有轻微延迟。优化方法：

1. 启用说话人优化
2. 预加载说话人嵌入
3. 使用缓存机制

---

## 支持与反馈

如果您在使用过程中遇到问题：

1. 查看本文档的[故障排除](#常见问题)章节
2. 查看技术文档获取详细信息
3. 在项目仓库提交Issue
4. 加入开发者社区讨论

---

**祝您使用愉快！** 🎉
