# XLeRobot NPU模型转换工具 - 决策架构文档

## Executive Summary

本架构文档为XLeRobot NPU模型转换工具提供了完整的技术决策框架，专注于将SenseVoice ASR和Piper VITS TTS模型从ONNX格式转换为NPU可执行的BPU格式。基于Python CLI工具和Docker化部署，集成Horizon X5 BPU工具链，实现2-5倍性能提升和>95%转换成功率的目标。

## Project Initialization

本项目采用手动构建方式，无启动模板依赖。第一个实现故事应创建项目基础结构：

```bash
mkdir xlerobot-npu-converter
cd xlerobot-npu-converter
# 创建基础项目结构（详见Project Structure部分）
```

## Decision Summary

| Category | Decision | Version | Affects Epics | Rationale |
| -------- | -------- | ------- | ------------- | --------- |
| CLI框架 | Click | 8.x | Epic 1, Epic 2 | 专业CLI工具需要复杂命令结构和参数验证 |
| 项目结构 | 标准包结构 | - | Epic 1, Epic 2 | 符合Python最佳实践，便于包管理和分发 |
| Docker基础镜像 | Ubuntu 20.04官方镜像 | - | Epic 1 | 与Horizon X5 BPU工具链最佳兼容性 |
| 配置管理 | YAML配置文件 | - | Epic 1, Epic 2 | 支持注释，层次结构清晰，AI/ML生态标准 |
| 错误处理 | 混合方式 | - | Epic 1, Epic 2 | 针对不同错误类型提供最合适的处理机制 |
| 日志格式 | 结构化文本日志 | - | Epic 1, Epic 2 | 人眼可读且便于工具过滤，包含丰富上下文信息 |
| 测试框架 | pytest | 7.x | Epic 1, Epic 2 | 丰富插件生态，强大fixture系统，详细调试信息 |
| 代码质量 | 企业级工具集 | - | Epic 1, Epic 2 | 高性能检查，类型安全，Git钩子确保一致性 |

## Project Structure

```
xlerobot-npu-converter/
├── .github/
│   └── workflows/
│       └── ci.yml                    # CI/CD流水线
├── .pre-commit-config.yaml            # Git钩子配置
├── pyproject.toml                     # 项目配置和依赖
├── README.md                          # 项目文档
├── LICENSE                            # 开源许可证
├── Dockerfile                         # Ubuntu 20.04基础镜像
├── docker-compose.yml                 # 开发环境配置
├── requirements.txt                   # 生产依赖
├── requirements-dev.txt               # 开发依赖
├── config/
│   ├── npu-converter.yaml            # 默认配置
│   └── models/
│       ├── sensevoice.yaml           # SenseVoice模型配置
│       └── piper-vits.yaml           # Piper VITS模型配置
├── src/
│   └── npu_converter/
│       ├── __init__.py
│       ├── cli.py                    # Click CLI入口点
│       ├── core/
│       │   ├── __init__.py
│       │   ├── converter.py          # 核心转换逻辑
│       │   ├── validator.py          # 模型验证
│       │   ├── benchmark.py          # 性能测试
│       │   └── reporter.py           # 报告生成
│       ├── models/
│       │   ├── __init__.py
│       │   ├── conversion_result.py  # 转换结果模型
│       │   ├── validation_result.py  # 验证结果模型
│       │   └── benchmark_result.py   # 基准测试结果
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── logger.py             # 结构化日志
│       │   ├── config.py             # 配置管理
│       │   ├── exceptions.py         # 自定义异常
│       │   └── result.py             # Result对象
│       └── bpu_toolchain/
│           ├── __init__.py
│           ├── horizon_x5.py         # Horizon X5工具链接口
│           └── model_optimizer.py    # 模型优化器
├── tests/
│   ├── __init__.py
│   ├── conftest.py                   # pytest fixtures
│   ├── unit/
│   │   ├── test_converter.py
│   │   ├── test_validator.py
│   │   └── test_utils.py
│   ├── integration/
│   │   ├── test_conversion_flow.py
│   │   └── test_bpu_toolchain.py
│   └── fixtures/
│       ├── sample_models/
│       └── test_configs/
├── docs/
│   ├── api/                          # API文档
│   ├── user_guide/                   # 用户指南
│   └── developer_guide/              # 开发者指南
├── examples/
│   ├── basic_conversion.py           # 基础转换示例
│   └── batch_processing.py           # 批量处理示例
└── scripts/
    ├── setup_dev.sh                  # 开发环境搭建
    └── run_tests.sh                  # 测试运行脚本
```

## Epic to Architecture Mapping

| Epic | 组件位置 | 主要功能 | 依赖关系 |
| ---- | -------- | -------- | -------- |
| Epic 1: 基础设施 | `Dockerfile`, `pyproject.toml`, `src/npu_converter/cli.py` | Docker环境、CLI框架、配置系统 | 无前置依赖 |
| Epic 1: 工具链集成 | `src/npu_converter/bpu_toolchain/` | Horizon X5 BPU工具链接口 | 基础设施完成后 |
| Epic 2: 核心转换 | `src/npu_converter/core/converter.py` | 模型转换核心逻辑 | 工具链集成完成后 |
| Epic 2: 验证系统 | `src/npu_converter/core/validator.py` | 模型验证和精度检查 | 核心转换完成后 |
| Epic 2: 性能测试 | `src/npu_converter/core/benchmark.py` | NPU vs CPU性能对比 | 验证系统完成后 |
| Epic 2: 报告生成 | `src/npu_converter/core/reporter.py` | 转换报告和结果文档 | 性能测试完成后 |

## Technology Stack Details

### Core Technologies

**运行时环境:**
- Python 3.10
- Ubuntu 20.04 (Docker)
- Horizon X5 BPU工具链

**核心框架:**
- Click 8.x (CLI框架)
- PyYAML (配置管理)
- pytest 7.x (测试框架)

**代码质量工具:**
- black (代码格式化)
- ruff (代码检查)
- mypy (类型检查)
- pre-commit (Git钩子)

### Integration Points

**CLI接口:**
- 主命令: `npu-converter`
- 子命令: `convert`, `validate`, `benchmark`, `ptq-analyze`
- 参数格式: `--input-model`, `--output-dir`, `--config`, `--calibration-data`

**Horizon X5工具链深度集成:**
- PTQ转换流程: 模型准备 → 模型验证 → 校准数据准备 → 模型量化&编译 → 性能分析 → 精度分析
- 集成hrt_bin_dump调试工具用于模型分析
- 集成hrt_model_exec用于推理测试
- 算子兼容性检查基于官方算子支持约束列表
- 性能基准测试使用AI Benchmark工具

**数据流架构:**
```
ONNX输入 → 兼容性检查 → 校准数据准备 → PTQ量化 → 编译优化 → 精度验证 → 性能测试 → BPU输出
```

**配置系统:**
- 默认配置: `config/npu-converter.yaml`
- 模型配置: `config/models/{model_name}.yaml`
- 用户配置: `~/.npu-converter/config.yaml`

## Implementation Patterns

这些模式确保所有AI代理实现一致：

### 命名模式
- Python文件: `snake_case.py`
- 测试文件: `test_*.py`
- 配置文件: `kebab-case.yaml`
- 类名: `PascalCase`
- 异常类: `PascalCase + Error`
- 函数: `snake_case` (公共), `_snake_case` (私有)

### 结构模式
**导入顺序:**
```python
# 标准库
import os
import sys
from pathlib import Path

# 第三方库
import click
import yaml
import numpy as np

# 本地模块
from npu_converter.core.converter import ModelConverter
from npu_converter.utils.logger import get_logger
```

**错误处理模式:**
```python
from npu_converter.utils.result import Result
from npu_converter.utils.exceptions import NPUConversionError

def convert_model(model_path: str) -> Result:
    try:
        # 转换逻辑
        return Result(success=True, data=result)
    except ModelCompatibilityError as e:
        logger.error(f"Model compatibility failed: {e}")
        return Result(success=False, error=str(e))
```

## Consistency Rules

### Naming Conventions

**命令约定:**
- 主命令: `npu-converter`
- 子命令: `convert`, `validate`, `benchmark`
- 参数: `--input-model`, `--output-dir`, `--config`

**错误码标准:**
- 格式: `NPUEXXX` (如NPUE001表示模型兼容性错误)
- 统一错误消息: `[NPUE001] Model incompatible: {details}`

### Code Organization

**目录职责:**
- CLI定义: `src/npu_converter/cli.py`
- 核心逻辑: `src/npu_converter/core/`
- 工具链接口: `src/npu_converter/bpu_toolchain/`
- 配置文件: `config/models/`
- 测试文件: `tests/unit/`, `tests/integration/`

### Error Handling

**异常层次结构:**
```python
class NPUConversionError(Exception):
    """NPU转换基础异常"""
    pass

class ModelCompatibilityError(NPUConversionError):
    """模型兼容性错误"""
    pass

class ToolchainError(NPUConversionError):
    """工具链错误"""
    pass
```

**Result对象模式:**
```python
@dataclass
class Result:
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Optional[Dict] = None
```

### Logging Strategy

**日志格式:**
```
[2024-01-01 10:00:00] INFO [model_conversion] Starting model conversion
[2024-01-01 10:00:01] DEBUG [validation] Model input shape: (1, 80, 300)
[2024-01-01 10:00:02] ERROR [conversion] Toolchain execution failed: timeout
```

**日志级别使用:**
- DEBUG: 详细的转换步骤信息
- INFO: 主要阶段进度
- WARNING: 兼容性警告
- ERROR: 转换失败和异常

## Data Architecture

### 核心数据模型

**转换结果模型:**
```python
@dataclass
class ConversionResult:
    input_model: str
    output_model: str
    conversion_time: float
    success: bool
    error_message: Optional[str] = None
    optimization_level: int = 2
```

**验证结果模型:**
```python
@dataclass
class ValidationResult:
    model_path: str
    accuracy_retention: float
    input_shape: Tuple[int, ...]
    output_shape: Tuple[int, ...]
    compatibility_issues: List[str]
    passed: bool
```

**配置数据结构:**
```yaml
models:
  sensevoice:
    input_format: "onnx"
    output_format: "bpu"
    optimization:
      level: 2
      target_device: "rdk_x5"
    validation:
      accuracy_threshold: 0.98
      performance_target: "2-5x"
```

## API Contracts

### CLI接口规范

**主命令组:**
```bash
npu-converter [OPTIONS] COMMAND [ARGS]...
```

**convert子命令:**
```bash
npu-converter convert [OPTIONS] INPUT_MODEL OUTPUT_DIR
  --config TEXT          配置文件路径
  --model-type TEXT      模型类型 (sensevoice|piper-vits)
  --optimization INTEGER 优化级别 (1-3)
  --validate             转换后自动验证
  --benchmark            转换后性能测试
```

**validate子命令:**
```bash
npu-converter validate [OPTIONS] MODEL_PATH
  --reference-model TEXT 参考模型路径（精度对比）
  --test-data TEXT       测试数据路径
  --output-format TEXT   输出格式 (json|yaml|html)
```

**benchmark子命令:**
```bash
npu-converter benchmark [OPTIONS] ONNX_MODEL BPU_MODEL
  --iterations INTEGER   推理测试次数
  --warmup INTEGER       预热次数
  --test-data TEXT       测试数据
  --output-file TEXT     结果输出文件
```

## Security Architecture

### 安全考虑

**容器安全:**
- 使用非root用户运行容器
- 最小化容器镜像攻击面
- 禁用不必要的服务和端口

**文件安全:**
- 输入文件类型验证
- 文件大小限制
- 临时文件安全清理

**数据保护:**
- 配置文件敏感信息加密
- 日志中不记录敏感数据
- 模型文件完整性校验

## Performance Considerations

### 性能策略

**转换性能:**
- 模型预处理优化
- 并行处理支持
- 内存使用优化
- 缓存机制

**验证性能:**
- 增量验证支持
- 批量测试优化
- 结果缓存

**基准测试:**
- 多轮测试取平均值
- 预热机制
- 资源监控集成

## Deployment Architecture

### 部署方式

**Docker容器部署:**
```dockerfile
FROM ubuntu:20.04

# 安装Python 3.10和依赖
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-pip \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 安装Horizon X5 BPU工具链
COPY horizon-x5-toolchain/ /opt/horizon/
ENV PATH="/opt/horizon/bin:$PATH"

# 安装Python依赖
COPY requirements.txt .
RUN pip3.10 install -r requirements.txt

# 复制源代码
COPY src/ ./src/
COPY config/ ./config/

# 设置入口点
ENTRYPOINT ["python3.10", "-m", "npu_converter.cli"]
```

**开发环境:**
```yaml
# docker-compose.yml
version: '3.8'
services:
  npu-converter:
    build: .
    volumes:
      - ./src:/app/src
      - ./config:/app/config
      - ./models:/app/models
      - ./logs:/app/logs
    environment:
      - LOG_LEVEL=DEBUG
      - NPU_TOOLCHAIN_PATH=/opt/horizon
```

## Development Environment

### Prerequisites

**系统要求:**
- Ubuntu 20.04 或兼容的Linux发行版
- Python 3.10+
- Docker 20.10+
- Git 2.25+

**硬件要求:**
- RDK X5开发板（用于测试）
- 至少8GB RAM
- 50GB可用磁盘空间

### Setup Commands

```bash
# 1. 克隆仓库
git clone <repository-url>
cd xlerobot-npu-converter

# 2. 创建虚拟环境
python3.10 -m venv venv
source venv/bin/activate

# 3. 安装开发依赖
pip install -r requirements-dev.txt

# 4. 安装pre-commit钩子
pre-commit install

# 5. 构建Docker镜像
docker build -t npu-converter:dev .

# 6. 运行测试
pytest

# 7. 验证安装
python -m npu_converter.cli --help
```

## Architecture Decision Records (ADRs)

### ADR-001: CLI框架选择
**决策:** 选择Click作为CLI框架
**理由:** 需要处理复杂的命令结构和参数验证，Click提供专业的CLI开发体验
**后果:** 增加了外部依赖，但提供了更好的用户体验和开发效率

### ADR-002: 项目结构标准
**决策:** 采用标准包结构 (src/npu_converter/)
**理由:** 符合Python社区最佳实践，便于包管理和分发
**后果:** 增加了目录层级，但提供了更好的代码组织

### ADR-003: Docker基础镜像
**决策:** 使用Ubuntu 20.04官方镜像
**理由:** 与Horizon X5 BPU工具链最佳兼容性，完全控制Python环境
**后果:** 镜像体积较大，但确保了硬件工具链的稳定性

### ADR-004: 配置管理格式
**决策:** 使用YAML配置文件
**理由:** 支持注释，层次结构清晰，AI/ML生态标准
**后果:** 解析性能略低于JSON，但可读性和维护性更好

### ADR-005: 错误处理策略
**决策:** 混合方式（自定义异常 + Result对象）
**理由:** 针对不同错误类型提供最合适的处理机制
**后果:** 增加了复杂性，但提供了更好的错误处理体验

### ADR-006: 测试框架选择
**决策:** 使用pytest作为测试框架
**理由:** 丰富插件生态，强大fixture系统，详细调试信息
**后果:** 外部依赖，但显著提升了测试开发体验

---

_Generated by BMAD Decision Architecture Workflow v1.3.2_
_Date: 2025-10-25_
_For: Jody_