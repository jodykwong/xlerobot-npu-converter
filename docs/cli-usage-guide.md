# XLeRobot CLI工具使用指南

## 概述

XLeobot CLI工具提供了强大的命令行界面，用于管理NPU模型转换的配置文件和执行转换任务。该工具支持多种模型类型，包括VITS-Cantonese TTS、SenseVoice ASR和Piper VITS TTS。

## 🚀 快速开始

### 安装和设置

```bash
# 确保Python环境已设置
cd /home/sunrise/xlerobot

# 设置环境变量
export PYTHONPATH="${PYTHONPATH}:/home/sunrise/xlerobot/src"

# 创建CLI工具的软链接（可选）
sudo ln -s /home/sunrise/xlerobot/src/npu_converter/cli/main.py /usr/local/bin/xlerobot
sudo ln -s /home/sunrise/xlerobot/src/npu_converter/cli/config_cli.py /usr/local/bin/xlerobot-config
```

### 基本使用

```bash
# 显示帮助
xlerobot --help

# 显示项目信息
xlerobot info

# 配置管理帮助
xlerobot config --help
```

## 📋 命令参考

### 主命令 (xlerobot)

#### 概览
```bash
xlerobot [全局选项] <命令> [命令选项]
```

#### 全局选项
- `--version`: 显示版本信息
- `--quiet, -q`: 静默模式

#### 子命令
- `config`: 配置管理工具
- `convert`: 模型转换工具 (Story 1.6完成)
- `info`: 显示项目信息

### 配置管理命令 (xlerobot-config)

#### 创建配置文件
```bash
xlerobot-config create <model_type> -o <output_file> [选项]
```

**模型类型:**
- `vits_cantonese`: 粤语语音合成模型
- `sensevoice`: 多语言语音识别模型
- `piper_vits`: 通用语音合成模型

**选项:**
- `-o, --output`: 输出配置文件路径 (必需)
- `--name`: 项目名称
- `--description`: 项目描述
- `--device`: 目标设备
- `--optimization`: 优化级别
- `--memory`: 内存限制
- `--force`: 强制覆盖已存在的文件
- `--show`: 显示创建的配置内容

**示例:**
```bash
# 创建VITS-Cantonese配置
xlerobot-config create vits_cantonese -o vits_config.yaml \
  --name "粤语TTS模型" \
  --device horizon_x5 \
  --optimization O3

# 创建SenseVoice配置
xlerobot-config create sensevoice -o asr_config.yaml \
  --name "多语言ASR模型" \
  --show
```

#### 验证配置文件
```bash
xlerobot-config validate <config_file>
```

**示例:**
```bash
xlerobot-config validate vits_config.yaml
```

#### 显示配置内容
```bash
xlerobot-config show <config_file> [--format FORMAT]
```

**格式选项:**
- `yaml`: YAML格式 (默认)
- `json`: JSON格式
- `summary`: 摘要格式

**示例:**
```bash
# 显示完整YAML配置
xlerobot-config show vits_config.yaml

# 显示JSON格式配置
xlerobot-config show vits_config.yaml --format json

# 显示配置摘要
xlerobot-config show vits_config.yaml --format summary
```

#### 修改配置参数
```bash
xlerobot-config modify <config_file> --set KEY=VALUE [选项]
```

**选项:**
- `--set`: 设置键值对 (可多次使用)
- `--save`: 保存修改到文件
- `--show`: 显示修改后的配置摘要

**示例:**
```bash
# 修改单个参数
xlerobot-config modify vits_config.yaml \
  --set hardware.optimization_level=O3 \
  --save

# 批量修改参数
xlerobot-config modify vits_config.yaml \
  --set hardware.optimization_level=O3 \
  --set performance.target_latency_ms=100 \
  --set debug.enabled=true \
  --save --show

# 使用数组值
xlerobot-config modify config.yaml \
  --set 'supported_languages=["zh","en","yue"]' \
  --save
```

#### 备份配置文件
```bash
xlerobot-config backup <config_file> [--name NAME] [--list]
```

**选项:**
- `--name`: 备份名称
- `--list`: 列出所有备份

**示例:**
```bash
# 创建备份
xlerobot-config backup vits_config.yaml --name before_optimization

# 创建备份并列出所有备份
xlerobot-config backup vits_config.yaml --name backup_001 --list
```

#### 恢复配置文件
```bash
xlerobot-config restore <backup_file> [--config CONFIG_FILE]
```

**选项:**
- `--config`: 目标配置文件路径

**示例:**
```bash
# 恢复到指定配置文件
xlerobot-config restore backup_vits_config.yaml --config vits_config.yaml

# 恢复到原始位置
xlerobot-config restore backup_config.yaml
```

#### 列出备份文件
```bash
xlerobot-config list-backups [--config CONFIG_FILE]
```

**示例:**
```bash
# 列出指定配置的所有备份
xlerobot-config list-backups vits_config.yaml

# 列出默认位置的备份
xlerobot-config list-backups
```

#### 监控配置文件变更
```bash
xlerobot-config watch <config_file> [--auto-rollback]
```

**选项:**
- `--auto-rollback`: 自动回滚无效配置

**示例:**
```bash
# 监控配置文件变更
xlerobot-config watch vits_config.yaml

# 启用自动回滚功能
xlerobot-config watch vits_config.yaml --auto-rollback
```

### 模型转换命令 (xlerobot convert)

#### 概述
`xlerobot convert` 命令用于将AI模型（ONNX格式）转换为NPU可执行的BPU格式。支持SenseVoice ASR、VITS-Cantonese TTS和Piper VITS TTS模型。

#### 基本语法
```bash
xlerobot convert [选项] -i INPUT -o OUTPUT
```

#### 必需参数
- `-i, --input INPUT`: 输入模型文件路径 (.onnx格式)
- `-o, --output OUTPUT`: 输出模型文件路径或目录

#### 可选参数
- `-t, --type TYPE`: 模型类型 (sensevoice/vits_cantonese/piper_vits)
- `-c, --config CONFIG`: 配置文件路径 (.yaml格式)
- `-v, --verbose`: 详细输出模式
- `-q, --quiet`: 静默模式
- `--json`: JSON格式输出
- `--dry-run`: 预览模式，不实际执行转换
- `--force`: 强制覆盖已存在的输出文件

#### 支持的模型类型
| 类型 | 说明 | 适用场景 |
|------|------|----------|
| `sensevoice` | SenseVoice ASR模型 (语音识别) | 多语言语音识别 |
| `vits_cantonese` | VITS粤语TTS模型 (语音合成) | 粤语语音合成 |
| `piper_vits` | Piper VITS TTS模型 (通用语音合成) | 通用语音合成 |

#### 使用示例

**基础转换**
```bash
# 转换SenseVoice模型
xlerobot convert -i sensevoice.onnx -o sensevoice.bpu -t sensevoice

# 转换VITS-Cantonese模型
xlerobot convert -i vits_cantonese.onnx -o vits_cantonese.bpu -t vits_cantonese

# 转换Piper VITS模型
xlerobot convert -i piper_vits.onnx -o piper_vits.bpu -t piper_vits
```

**使用配置文件**
```bash
# 使用配置进行转换
xlerobot convert -i model.onnx -o output.bpu -c config.yaml

# 转换并生成详细日志
xlerobot convert -i model.onnx -o output.bpu -c config.yaml --verbose
```

**高级选项**
```bash
# 预览转换（不实际执行）
xlerobot convert -i model.onnx -o output.bpu --dry-run

# JSON格式输出
xlerobot convert -i model.onnx -o output.bpu --json

# 强制覆盖已存在的输出
xlerobot convert -i model.onnx -o output.bpu --force

# 静默模式（仅显示错误）
xlerobot convert -i model.onnx -o output.bpu --quiet
```

#### 输出说明

**标准输出模式**
```
[INFO] 开始模型转换...
[INFO] 加载输入模型: model.onnx
[INFO] 模型类型: SenseVoice ASR
[INFO] 验证模型兼容性...
[INFO] 模型验证通过
[INFO] 开始量化转换...
[INFO] 转换进度: 50%
[INFO] 转换进度: 100%
[INFO] 转换完成
[INFO] 输出文件: output.bpu
[SUCCESS] 模型转换成功完成
```

**JSON输出模式**
```json
{
  "status": "success",
  "input_model": "model.onnx",
  "output_model": "output.bpu",
  "model_type": "sensevoice",
  "conversion_time": 45.2,
  "performance": {
    "latency_ms": 25.6,
    "fps": 39.1,
    "cpu_usage": "15%",
    "memory_usage": "512MB"
  },
  "metrics": {
    "accuracy_retention": 0.985,
    "compression_ratio": 4.2
  },
  "timestamp": "2025-10-27T10:30:00Z"
}
```

#### 错误处理

**常见错误及解决方案**

1. **模型文件不存在**
   ```
   [ERROR] 输入模型文件不存在: model.onnx
   [HINT] 请检查文件路径是否正确
   ```

   解决方案: 检查输入路径是否正确
   ```bash
   ls -la model.onnx  # 验证文件存在
   ```

2. **不支持的模型格式**
   ```
   [ERROR] 不支持的模型格式: .pb
   [HINT] 仅支持ONNX格式(.onnx)
   ```

   解决方案: 确认模型为ONNX格式
   ```bash
   file model.onnx  # 检查文件格式
   ```

3. **配置验证失败**
   ```
   [ERROR] 配置验证失败: 无效参数值
   [HINT] 请检查配置文件: config.yaml:15
   ```

   解决方案: 验证并修正配置文件
   ```bash
   xlerobot-config validate config.yaml  # 检查配置
   ```

4. **输出目录权限不足**
   ```
   [ERROR] 无法创建输出文件: 权限被拒绝
   [HINT] 请检查输出目录权限
   ```

   解决方案: 修正目录权限
   ```bash
   chmod 755 output_dir  # 设置适当权限
   ```

#### 转换进度监控

**实时进度显示**
```bash
xlerobot convert -i large_model.onnx -o output.bpu --verbose
```

转换过程会显示:
- 加载进度
- 验证进度
- 量化进度
- 编译进度
- 分析进度

#### 性能优化建议

1. **选择合适的模型类型**
   - 自动检测模型类型可减少手动配置
   - 指定类型可确保最佳兼容性

2. **使用配置文件**
   - 预定义的配置可提供最佳性能
   - 支持批量参数调整

3. **启用详细模式**
   - 详细模式提供更多调试信息
   - 有助于问题诊断和性能分析

4. **合理设置输出路径**
   - SSD存储可提高转换速度
   - 确保有足够磁盘空间

## 🎯 使用场景和最佳实践

### 开发环境设置

1. **创建初始配置**
```bash
# 为VITS-Cantonese模型创建配置
xlerobot-config create vits_cantonese -o dev_config.yaml \
  --name "开发环境配置" \
  --device horizon_x5 \
  --optimization O1
```

2. **验证配置**
```bash
xlerobot-config validate dev_config.yaml
```

3. **启用热加载监控**
```bash
# 在一个终端中监控配置变更
xlerobot-config watch dev_config.yaml --auto-rollback
```

### 生产环境部署

1. **创建生产配置**
```bash
xlerobot-config create vits_cantonese -o prod_config.yaml \
  --name "生产环境配置" \
  --optimization O3 \
  --memory 16GB
```

2. **性能优化调整**
```bash
xlerobot-config modify prod_config.yaml \
  --set performance.target_latency_ms=100 \
  --set performance.max_realtime_factor=0.8 \
  --set hardware.cache_size=512MB \
  --save
```

3. **创建安全备份**
```bash
xlerobot-config backup prod_config.yaml --name production_backup
```

### 配置版本管理

1. **创建不同环境的配置**
```bash
# 开发环境
xlerobot-config create vits_cantonese -o config_dev.yaml --name "开发环境"

# 测试环境
xlerobot-config create vits_cantonese -o config_test.yaml --name "测试环境"

# 生产环境
xlerobot-config create vits_cantonese -o config_prod.yaml --name "生产环境"
```

2. **配置比较和同步**
```bash
# 比较配置差异
diff config_test.yaml config_prod.yaml

# 同步配置
xlerobot-config modify config_test.yaml \
  --set performance.target_latency_ms=$(xlerobot-config show config_prod.yaml --format json | jq '.performance.target_latency_ms') \
  --save
```

### 故障排除

1. **配置验证失败**
```bash
# 详细验证
xlerobot-config validate problem_config.yaml

# 查看配置内容
xlerobot-config show problem_config.yaml --format yaml

# 回滚到上一个工作版本
xlerobot-config list-backups problem_config.yaml
xlerobot-config restore backup_working.yaml
```

2. **性能调优**
```bash
# 监控配置变更
xlerobot-config watch config.yaml

# 调整性能参数
xlerobot-config modify config.yaml \
  --set hardware.optimization_level=O3 \
  --set conversion_params.batch_size=4 \
  --save
```

## 🔧 高级功能

### 批量配置管理

创建脚本批量管理多个配置：

```bash
#!/bin/bash
# batch_config_management.sh

CONFIGS=("vits_config.yaml" "sensevoice_config.yaml" "piper_config.yaml")

for config in "${CONFIGS[@]}"; do
    echo "处理配置: $config"

    # 验证配置
    if xlerobot-config validate "$config"; then
        echo "✅ $config 验证通过"

        # 创建备份
        xlerobot-config backup "$config" --name "batch_backup_$(date +%Y%m%d_%H%M%S)"
    else
        echo "❌ $config 验证失败"
    fi
done
```

### 配置模板系统

创建自定义配置模板：

```bash
#!/bin/bash
# create_config_template.sh

MODEL_TYPE=$1
PROJECT_NAME=$2
OUTPUT_FILE=$3

if [ -z "$MODEL_TYPE" ] || [ -z "$PROJECT_NAME" ] || [ -z "$OUTPUT_FILE" ]; then
    echo "用法: $0 <模型类型> <项目名称> <输出文件>"
    echo "模型类型: vits_cantonese, sensevoice, piper_vits"
    exit 1
fi

xlerobot-config create "$MODEL_TYPE" -o "$OUTPUT_FILE" \
  --name "$PROJECT_NAME" \
  --device horizon_x5 \
  --optimization O2 \
  --memory 8GB \
  --show

echo "配置模板已创建: $OUTPUT_FILE"
```

### 自动化配置部署

```bash
#!/bin/bash
# deploy_config.sh

SOURCE_CONFIG=$1
TARGET_ENV=$2

case $TARGET_ENV in
    "dev")
        xlerobot-config modify "$SOURCE_CONFIG" \
            --set hardware.optimization_level=O1 \
            --set debug.enabled=true \
            --save
        ;;
    "test")
        xlerobot-config modify "$SOURCE_CONFIG" \
            --set hardware.optimization_level=O2 \
            --set debug.enabled=false \
            --save
        ;;
    "prod")
        xlerobot-config modify "$SOURCE_CONFIG" \
            --set hardware.optimization_level=O3 \
            --set performance.target_latency_ms=100 \
            --save
        ;;
    *)
        echo "未知环境: $TARGET_ENV"
        exit 1
        ;;
esac

echo "配置已部署到 $TARGET_ENV 环境"
```

## 🚨 错误处理和故障排除

### 常见错误

1. **配置文件不存在**
```bash
❌ 配置文件不存在: config.yaml
```
**解决方案:** 检查文件路径，或使用 `create` 命令创建新配置

2. **配置验证失败**
```bash
❌ 配置验证失败
```
**解决方案:** 使用 `show` 命令查看配置内容，检查必填字段

3. **权限错误**
```bash
❌ 无法写入配置文件
```
**解决方案:** 检查文件权限，使用 `chmod` 修改权限

4. **参数格式错误**
```bash
❌ 无效的键值对格式: hardware.optimization_levelO3
```
**解决方案:** 使用正确的格式 `key=value`

### 调试技巧

1. **使用详细输出**
```bash
# 显示配置摘要
xlerobot-config show config.yaml --format summary

# 显示JSON格式便于脚本处理
xlerobot-config show config.yaml --format json
```

2. **启用配置监控**
```bash
# 监控配置变更
xlerobot-config watch config.yaml --auto-rollback
```

3. **创建备份点**
```bash
# 重要操作前创建备份
xlerobot-config backup config.yaml --name before_changes
```

## 📚 相关文档

- [配置管理系统使用指南](configuration-management-guide.md)
- [API参考文档](api-reference.md)
- [技术架构文档](architecture-story-1.4.md)
- [使用示例](examples/)

---

**版本**: v1.0.0
**更新时间**: 2025-10-26
**维护者**: XLeRobot开发团队