# XLeRobot CLI 工具使用示例

## 🚀 配置管理 CLI 使用指南

### 1. 基础配置操作

#### 创建配置文件
```bash
# 创建 SenseVoice ASR 配置
xlerobot-config create --model-type sensevoice --output sensevoice_config.yaml

# 创建 VITS-Cantonese TTS 配置
xlerobot-config create --model-type vits_cantonese --output cantonese_tts_config.yaml

# 创建 Piper VITS 配置
xlerobot-config create --model-type piper_vits --output piper_vits_config.yaml

# 从模板创建配置
xlerobot-config create --template sensevoice_default --output my_sensevoice.yaml
```

#### 验证配置文件
```bash
# 验证单个配置文件
xlerobot-config validate --config sensevoice_config.yaml

# 验证多个配置文件
xlerobot-config validate --config *.yaml

# 详细验证模式（显示错误和建议）
xlerobot-config validate --config sensevoice_config.yaml --verbose
```

#### 查看配置信息
```bash
# 显示配置概览
xlerobot-config info --config sensevoice_config.yaml

# 显示特定配置项
xlerobot-config info --config sensevoice_config.yaml --key project.model_type

# 显示所有可用策略
xlerobot-config info --strategies
```

### 2. 配置修改操作

#### 修改配置参数
```bash
# 修改硬件配置
xlerobot-config set --config sensevoice_config.yaml --key hardware.target_device --value horizon_x5

# 修改性能参数
xlerobot-config set --config sensevoice_config.yaml --key performance.target_latency_ms --value 50

# 修改模型特定参数
xlerobot-config set --config sensevoice_config.yaml --key model_specific.sensevoice.sample_rate --value 16000
```

#### 批量修改配置
```bash
# 使用JSON格式批量修改
xlerobot-config set --config sensevoice_config.yaml --json '{
  "hardware.optimization_level": "O3",
  "performance.batch_size": 8,
  "performance.target_latency_ms": 30
}'

# 从文件读取修改内容
xlerobot-config set --config sensevoice_config.yaml --file modifications.json
```

### 3. 配置备份和恢复

#### 创建备份
```bash
# 创建带注释的备份
xlerobot-config backup --config sensevoice_config.yaml --comment "性能优化前备份"

# 创建定期备份
xlerobot-config backup --config sensevoice_config.yaml --schedule daily
```

#### 查看备份历史
```bash
# 列出所有备份
xlerobot-config backup --config sensevoice_config.yaml --list

# 显示备份详情
xlerobot-config backup --config sensevoice_config.yaml --show backup_20231026_150000
```

#### 恢复配置
```bash
# 恢复到指定备份
xlerobot-config restore --config sensevoice_config.yaml --backup backup_20231026_150000

# 恢复到最新备份
xlerobot-config restore --config sensevoice_config.yaml --latest
```

### 4. 配置比较和合并

#### 比较配置文件
```bash
# 比较两个配置文件
xlerobot-config diff --config1 sensevoice_config.yaml --config2 sensevoice_config_v2.yaml

# 仅显示差异概要
xlerobot-config diff --config1 sensevoice_config.yaml --config2 sensevoice_config_v2.yaml --summary
```

#### 合并配置文件
```bash
# 合并配置文件
xlerobot-config merge --base sensevoice_config.yaml --override performance_override.yaml --output merged_config.yaml

# 交互式合并
xlerobot-config merge --base sensevoice_config.yaml --override performance_override.yaml --interactive
```

### 5. 模板管理

#### 列出可用模板
```bash
# 列出所有模板
xlerobot-config template --list

# 按模型类型过滤模板
xlerobot-config template --list --model-type sensevoice
```

#### 创建自定义模板
```bash
# 从现有配置创建模板
xlerobot-config template create --from sensevoice_config.yaml --name my_sensevoice_template

# 创建模板分类
xlerobot-config template create --from sensevoice_config.yaml --name production_sensevoice --category production
```

#### 使用模板
```bash
# 使用模板创建配置
xlerobot-config template use --name sensevoice_default --output new_config.yaml

# 使用模板并应用覆盖
xlerobot-config template use --name sensevoice_default --output config.yaml --override '{
  "hardware.target_device": "horizon_x6",
  "performance.target_latency_ms": 25
}'
```

## 🔧 高级 CLI 操作

### 1. 配置性能测试

```bash
# 运行性能基准测试
xlerobot-config benchmark --config sensevoice_config.yaml

# 运行详细的性能分析
xlerobot-config benchmark --config sensevoice_config.yaml --detailed --iterations 20

# 生成性能报告
xlerobot-config benchmark --config sensevoice_config.yaml --report performance_report.html
```

### 2. 配置热加载监控

```bash
# 启动配置文件监控
xlerobot-config watch --config sensevoice_config.yaml

# 启动监控并执行命令
xlerobot-config watch --config sensevoice_config.yaml --command "echo '配置已更新'"

# 启动监控并通知服务
xlerobot-config watch --config sensevoice_config.yaml --webhook http://localhost:8080/config-updated
```

### 3. 配置格式转换

```bash
# YAML 转 JSON
xlerobot-config convert --config sensevoice_config.yaml --format json --output sensevoice_config.json

# JSON 转 YAML
xlerobot-config convert --config sensevoice_config.json --format yaml --output sensevoice_config.yaml

# 配置压缩
xlerobot-config convert --config sensevoice_config.yaml --compress --output sensevoice_config.yaml.gz
```

## 📊 批量操作示例

### 1. 批量配置验证

```bash
# 验证目录中的所有配置文件
xlerobot-config validate --directory configs/ --recursive

# 验证并生成报告
xlerobot-config validate --directory configs/ --report validation_report.json

# 并行验证（提高性能）
xlerobot-config validate --directory configs/ --parallel --workers 4
```

### 2. 批量配置更新

```bash
# 批量更新硬件配置
xlerobot-config batch-update --directory configs/ --key hardware.optimization_level --value O3

# 使用脚本批量更新
xlerobot-config batch-update --script update_config.py --directory configs/

# 交互式批量更新
xlerobot-config batch-update --directory configs/ --interactive
```

### 3. 批量配置迁移

```bash
# 迁移配置到新版本
xlerobot-config migrate --source v1_configs/ --target v2_configs/ --version 2.0

# 迁移并验证
xlerobot-config migrate --source v1_configs/ --target v2_configs/ --validate --rollback-on-error
```

## 🛠️ 故障排除 CLI

### 1. 配置诊断

```bash
# 诊断配置文件问题
xlerobot-config diagnose --config sensevoice_config.yaml

# 生成详细诊断报告
xlerobot-config diagnose --config sensevoice_config.yaml --report diagnosis_report.html

# 修复常见问题
xlerobot-config diagnose --config sensevoice_config.yaml --auto-fix
```

### 2. 配置清理

```bash
# 清理无效备份
xlerobot-config cleanup --config sensevoice_config.yaml --backups --older-than 30d

# 清理临时文件
xlerobot-config cleanup --temp-files

# 清理并优化配置文件
xlerobot-config cleanup --config sensevoice_config.yaml --optimize
```

## 🚀 模型转换 CLI 使用示例

### 基础转换操作

#### 1. 转换SenseVoice ASR模型
```bash
# 转换SenseVoice模型（中文语音识别）
xlerobot convert -i sensevoice_model.onnx -o sensevoice_bpu.bpu -t sensevoice

# 使用配置文件转换
xlerobot convert -i sensevoice_model.onnx -o output/ -c config/sensevoice_production.yaml

# 详细模式转换
xlerobot convert -i sensevoice_model.onnx -o sensevoice_bpu.bpu -t sensevoice --verbose
```

#### 2. 转换VITS-Cantonese TTS模型
```bash
# 转换VITS-Cantonese模型（粤语语音合成）
xlerobot convert -i vits_cantonese.onnx -o vits_cantonese.bpu -t vits_cantonese

# 使用生产配置
xlerobot convert -i vits_cantonese.onnx -o production_tts.bpu -c config/cantonese_prod.yaml

# 性能优化模式
xlerobot convert -i vits_cantonese.onnx -o optimized_tts.bpu -t vits_cantonese --optimize
```

#### 3. 转换Piper VITS TTS模型
```bash
# 转换Piper VITS模型（通用语音合成）
xlerobot convert -i piper_vits.onnx -o piper_vits.bpu -t piper_vits

# 快速转换（低质量但速度快）
xlerobot convert -i piper_vits.onnx -o quick_tts.bpu -t piper_vits --fast

# 高质量转换（推荐用于生产）
xlerobot convert -i piper_vits.onnx -o high_quality_tts.bpu -t piper_vits --quality high
```

### 高级转换选项

#### 1. 批量转换
```bash
# 批量转换多个模型
for model in sensevoice.onnx vits_cantonese.onnx piper_vits.onnx; do
  xlerobot convert -i "$model" -o "converted/${model%.onnx}.bpu" --verbose
done

# 使用通配符批量转换
xlerobot convert -i models/*.onnx -o output/ -t sensevoice --batch
```

#### 2. 预览模式
```bash
# 预览转换（不实际执行）
xlerobot convert -i model.onnx -o output.bpu --dry-run

# 验证模型兼容性
xlerobot convert -i model.onnx --validate-only

# 估算转换时间
xlerobot convert -i large_model.onnx -o output.bpu --estimate-time
```

#### 3. 特殊输出格式
```bash
# JSON格式输出
xlerobot convert -i model.onnx -o output.bpu --json > conversion_report.json

# 生成详细报告
xlerobot convert -i model.onnx -o output.bpu --report -o report.html

# 输出到目录
xlerobot convert -i model.onnx -o converted_models/ --dir
```

### 错误处理示例

#### 1. 转换失败重试
```bash
# 自动重试机制
xlerobot convert -i model.onnx -o output.bpu --retry 3

# 断点续传
xlerobot convert -i model.onnx -o output.bpu --resume
```

#### 2. 问题诊断
```bash
# 启用调试模式
xlerobot convert -i model.onnx -o output.bpu --debug

# 生成诊断报告
xlerobot convert -i problematic_model.onnx -o output.bpu --diagnose

# 导出调试日志
xlerobot convert -i model.onnx -o output.bpu --verbose --log-file debug.log
```

### 性能优化示例

#### 1. 生产环境转换
```bash
# 生产环境高性能转换
xlerobot convert -i production_model.onnx \
  -o production.bpu \
  -c config/production.yaml \
  --optimization O3 \
  --threads 8 \
  --memory 16GB \
  --verbose

# 批量生产转换
xlerobot convert -i models/production/*.onnx \
  -o output/production/ \
  -c config/production.yaml \
  --batch-size 4 \
  --parallel
```

#### 2. 开发环境快速转换
```bash
# 开发环境快速验证
xlerobot convert -i dev_model.onnx \
  -o dev_output.bpu \
  -t sensevoice \
  --fast \
  --optimization O1 \
  --verbose

# 最小配置转换
xlerobot convert -i simple_model.onnx -o simple.bpu --minimal
```

#### 3. 精度优化转换
```bash
# 高精度转换（适合对精度要求高的场景）
xlerobot convert -i critical_model.onnx \
  -o high_accuracy.bpu \
  --precision float16 \
  --calibration-data ./calib_data/ \
  --accuracy-check

# 平衡精度和性能
xlerobot convert -i balanced_model.onnx \
  -o balanced.bpu \
  --precision int8 \
  --calibration-samples 1000 \
  --accuracy-metric cosine
```

### 实际项目示例

#### 示例1: SenseVoice生产部署
```bash
# 1. 创建生产配置
xlerobot-config create sensevoice -o production_config.yaml \
  --optimization O3 \
  --device horizon_x5 \
  --memory 8GB

# 2. 验证配置
xlerobot-config validate -c production_config.yaml

# 3. 转换模型
xlerobot convert -i sensevoice_base.onnx \
  -o sensevoice_production.bpu \
  -c production_config.yaml \
  --verbose

# 4. 验证转换结果
xlerobot-config info -c production_config.yaml

# 5. 创建备份
xlerobot-config backup -c production_config.yaml --comment "v1.2.0 production"
```

#### 示例2: VITS-Cantonese TTS开发
```bash
# 1. 创建开发配置
xlerobot-config create vits_cantonese -o dev_config.yaml \
  --optimization O1 \
  --device horizon_x5 \
  --memory 4GB

# 2. 快速转换用于测试
xlerobot convert -i cantonese_dev.onnx \
  -o cantonese_test.bpu \
  -c dev_config.yaml \
  --fast \
  --verbose

# 3. 如果测试通过，进行质量优化
xlerobot convert -i cantonese_dev.onnx \
  -o cantonese_optimized.bpu \
  -c dev_config.yaml \
  --quality high \
  --calibration-data ./test_audio/

# 4. 性能测试
xlerobot convert -i cantonese_optimized.bpu \
  --benchmark \
  --test-data ./test_samples/ \
  --output performance_report.json
```

#### 示例3: 多模型批量转换流水线
```bash
#!/bin/bash
# batch_conversion.sh

# 创建转换目录
mkdir -p converted/{sensevoice,vits_cantonese,piper_vits}

# 转换SenseVoice模型
echo "转换SenseVoice模型..."
for model in sensevoice/*.onnx; do
  if [ -f "$model" ]; then
    name=$(basename "$model" .onnx)
    xlerobot convert -i "$model" \
      -o "converted/sensevoice/${name}.bpu" \
      -t sensevoice \
      --config config/sensevoice.yaml \
      --json > "converted/sensevoice/${name}.json" \
      --verbose
  fi
done

# 转换VITS-Cantonese模型
echo "转换VITS-Cantonese模型..."
for model in vits_cantonese/*.onnx; do
  if [ -f "$model" ]; then
    name=$(basename "$model" .onnx)
    xlerobot convert -i "$model" \
      -o "converted/vits_cantonese/${name}.bpu" \
      -t vits_cantonese \
      --config config/cantonese.yaml \
      --json > "converted/vits_cantonese/${name}.json" \
      --verbose
  fi
done

# 转换Piper VITS模型
echo "转换Piper VITS模型..."
for model in piper_vits/*.onnx; do
  if [ -f "$model" ]; then
    name=$(basename "$model" .onnx)
    xlerobot convert -i "$model" \
      -o "converted/piper_vits/${name}.bpu" \
      -t piper_vits \
      --config config/piper_vits.yaml \
      --json > "converted/piper_vits/${name}.json" \
      --verbose
  fi
done

# 生成汇总报告
echo "生成转换汇总报告..."
cat > converted/conversion_summary.json << EOF
{
  "conversion_date": "$(date -Iseconds)",
  "total_models": $(find converted/*/*.bpu | wc -l),
  "success_rate": "100%",
  "output_directory": "converted/"
}
EOF

echo "批量转换完成！"
```

### 故障排除示例

#### 1. 内存不足错误
```bash
# 错误信息
[ERROR] 内存不足: 需要8GB，可用4GB

# 解决方案1: 降低批处理大小
xlerobot convert -i large_model.onnx -o output.bpu --batch-size 1

# 解决方案2: 启用内存优化
xlerobot convert -i large_model.onnx -o output.bpu --memory-optimize

# 解决方案3: 使用外存模式
xlerobot convert -i huge_model.onnx -o output.bpu --disk-cache
```

#### 2. 模型不兼容错误
```bash
# 错误信息
[ERROR] 模型不兼容: 不支持的算子类型 CustomOp

# 解决方案: 查看支持的算子
xlerobot convert -i model.onnx --list-supported-ops

# 解决方案: 预处理模型
python preprocess_model.py --input model.onnx --output preprocessed.onnx
xlerobot convert -i preprocessed.onnx -o output.bpu
```

#### 3. 转换超时错误
```bash
# 错误信息
[ERROR] 转换超时: 超过300秒

# 解决方案: 增加超时时间
xlerobot convert -i complex_model.onnx -o output.bpu --timeout 1800

# 解决方案: 启用多线程
xlerobot convert -i complex_model.onnx -o output.bpu --threads 16
```

## 📝 配置文件示例

### SenseVoice ASR 完整配置示例
```yaml
# sensevoice_production.yaml
project:
  name: "production_sensevoice"
  version: "1.2.0"
  model_type: "sensevoice"
  description: "生产环境中文语音识别模型"

hardware:
  target_device: "horizon_x5"
  optimization_level: "O3"
  memory_limit: "8GB"
  compute_units: 12
  cache_size: "512MB"

conversion_params:
  input_format: "onnx"
  output_format: "bpu"
  precision: "int8"
  calibration_method: "minmax"
  batch_size: 4
  num_workers: 8

performance:
  target_latency_ms: 50
  max_realtime_factor: 0.1
  enable_streaming: true
  chunk_size: 2048
  memory_optimization: true

model_specific:
  sensevoice:
    # 基础音频参数
    sample_rate: 16000
    audio_length: 30
    vocab_size: 10000
    mel_bins: 80

    # 网络架构参数
    encoder_layers: 12
    decoder_layers: 6
    hidden_size: 768
    num_heads: 12

    # ASR特定参数
    language_detection: true
    supported_languages: ["zh", "en", "yue", "ja"]
    confidence_threshold: 0.85
    beam_size: 10

    # 生产环境优化
    use_fast_inference: true
    enable_model_caching: true
    precision: "fp16"

validation:
  enable_model_validation: true
  validate_audio_output: true
  quality_thresholds:
    wer_score: 0.05
    cer_score: 0.02
    confidence_threshold: 0.8

monitoring:
  enable_metrics: true
  log_level: "INFO"
  performance_tracking: true
  error_reporting: true
```

### VITS-Cantonese TTS 完整配置示例
```yaml
# vits_cantonese_production.yaml
project:
  name: "production_vits_cantonese"
  version: "1.1.0"
  model_type: "vits_cantonese"
  description: "生产环境粤语语音合成模型"

hardware:
  target_device: "horizon_x5"
  optimization_level: "O3"
  memory_limit: "16GB"
  compute_units: 16

conversion_params:
  input_format: "onnx"
  output_format: "bpu"
  precision: "int8"
  calibration_method: "percentile"
  batch_size: 2
  num_workers: 4

performance:
  target_latency_ms: 100
  max_realtime_factor: 0.9
  enable_streaming: true
  chunk_size: 1024
  memory_optimization: true

model_specific:
  vits_cantonese:
    # 音频处理参数
    sampling_rate: 22050
    filter_length: 1024
    hop_length: 256
    win_length: 1024
    n_mel_channels: 80

    # VITS架构参数
    inter_channels: 192
    hidden_channels: 192
    filter_channels: 768
    n_heads: 2
    n_layers: 6

    # 粤语特有参数
    tone_embedding: true
    num_tones: 6
    use_jyutping: true
    cantonese_vocab_size: 5000

    # 合成质量参数
    noise_scale: 0.667
    noise_scale_w: 0.8
    length_scale: 1.0

    # 生产环境优化
    use_fast_synthesis: true
    enable_audio_caching: true
    synthesis_quality: "high"

validation:
  enable_model_validation: true
  validate_audio_output: true
  quality_thresholds:
    mos_score: 4.2
    mcd_score: 4.0
    cer_score: 0.01
```

## 🚀 快速开始脚本

```bash
#!/bin/bash
# quick_setup.sh - XLeRobot配置快速设置脚本

echo "🚀 XLeRobot 配置管理系统快速设置"

# 创建配置目录
mkdir -p configs/production
mkdir -p configs/development
mkdir -p configs/testing

# 创建生产环境配置
echo "📝 创建生产环境配置..."
xlerobot-config create --model-type sensevoice --template sensevoice_default \
  --output configs/production/sensevoice_prod.yaml

xlerobot-config create --model-type vits_cantonese --template vits_cantonese_default \
  --output configs/production/vits_cantonese_prod.yaml

# 创建开发环境配置
echo "📝 创建开发环境配置..."
xlerobot-config create --model-type sensevoice --template sensevoice_default \
  --output configs/development/sensevoice_dev.yaml

xlerobot-config set --config configs/development/sensevoice_dev.yaml \
  --key hardware.optimization_level --value O1

xlerobot-config set --config configs/development/sensevoice_dev.yaml \
  --key performance.target_latency_ms --value 200

# 验证所有配置
echo "✅ 验证配置文件..."
xlerobot-config validate --directory configs/ --recursive

# 创建初始备份
echo "💾 创建初始备份..."
for config in configs/**/*.yaml; do
  xlerobot-config backup --config "$config" --comment "初始设置备份"
done

echo "🎉 配置设置完成！"
echo "📁 配置文件位置: configs/"
echo "🔧 使用 'xlerobot-config --help' 查看更多命令"
```

这个CLI使用指南提供了完整的命令行工具使用方法，包括基础操作、高级功能、批量操作和故障排除，帮助用户充分利用XLeRobot配置管理系统的功能。