# Performance Benchmark Deployment Guide

**版本**: v1.0
**适用对象**: 运维工程师、系统管理员、DevOps工程师
**最后更新**: 2025-10-29
**项目**: XLeRobot NPU模型转换工具

---

## 📋 目录

1. [部署概述](#部署概述)
2. [系统要求](#系统要求)
3. [环境准备](#环境准备)
4. [安装步骤](#安装步骤)
5. [配置管理](#配置管理)
6. [验证部署](#验证部署)
7. [运行性能测试](#运行性能测试)
8. [CI/CD集成](#cicd集成)
9. [监控和告警](#监控和告警)
10. [维护和更新](#维护和更新)
11. [故障排除](#故障排除)
12. [最佳实践](#最佳实践)

---

## 部署概述

### 部署架构图

```
┌──────────────────────────────────────────────────────────────┐
│                    部署架构                                   │
├──────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐    ┌──────────────────┐                  │
│  │   GitHub Actions  │    │   本地部署环境    │                  │
│  │   CI/CD 流水线     │    │                  │                  │
│  └────────┬─────────┘    └────────┬─────────┘                  │
│           │                       │                            │
│           ▼                       ▼                            │
│  ┌─────────────────────────────────────┐                      │
│  │       性能基准测试系统                │                      │
│  │                                     │                      │
│  │  ┌──────┐ ┌──────┐ ┌──────┐         │                      │
│  │  │测试  │ │指标  │ │分析  │         │                      │
│  │  │执行  │ │采集  │ │器    │         │                      │
│  │  └──────┘ └──────┘ └──────┘         │                      │
│  │                                     │                      │
│  │  ┌──────┐ ┌──────┐ ┌──────┐         │                      │
│  │  │报告  │ │可视化│ │告警  │         │                      │
│  │  │生成  │ │引擎  │ │系统  │         │                      │
│  │  └──────┘ └──────┘ └──────┘         │                      │
│  └─────────────────────────────────────┘                      │
│                     │                                          │
│                     ▼                                          │
│  ┌──────────────────────────────────────────┐                │
│  │          报告和输出                       │                │
│  │  - HTML/PDF 报告                         │                │
│  │  - JSON 数据                            │                │
│  │  - 图表和可视化                          │                │
│  │  - 告警通知                              │                │
│  └──────────────────────────────────────────┘                │
│                                                                  │
└────────────────────────────────────────────────────────────────┘
```

### 部署模式

#### 1. 开发环境部署

用于开发和调试，配置简单，快速启动。

```bash
# 快速安装
pip install -e .

# 使用默认配置
python -m npu_converter.performance
```

#### 2. 生产环境部署

用于生产环境，配置完整，性能优化。

```bash
# 完整安装
pip install -r requirements.txt
pip install -e .

# 配置优化
# - 使用SQLite或专用数据库
# - 启用所有监控指标
# - 配置完整的告警规则
```

#### 3. CI/CD集成部署

集成到CI/CD流水线，自动执行性能测试。

```yaml
# .github/workflows/performance-benchmark.yml
name: Performance Benchmark
on: [push, pull_request]
jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Benchmark
        run: python -m pytest tests/performance/
```

---

## 系统要求

### 最低要求

#### 硬件要求

| 组件 | 最低配置 | 推荐配置 |
|------|----------|----------|
| CPU | 4核心 | 8核心或更多 |
| 内存 | 8GB | 16GB或更多 |
| 存储 | 10GB可用空间 | 50GB或更多 SSD |
| GPU | 可选 | NVIDIA GPU 8GB+ 显存 |
| 网络 | 1Mbps | 10Mbps或更快 |

#### 软件要求

- **操作系统**: Linux (Ubuntu 20.04+), macOS 10.15+, Windows 10+
- **Python**: 3.8+ (推荐 3.10)
- **依赖库**: 见 `requirements.txt`

#### 依赖库列表

```txt
# 核心依赖
numpy>=1.20.0
pandas>=1.3.0
matplotlib>=3.5.0
plotly>=5.0.0

# 测试依赖
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-benchmark>=4.0.0

# 监控依赖
psutil>=5.9.0

# 可选依赖
GPUtil>=1.4.0        # GPU监控
nvidia-ml-py>=12.535 # NVIDIA GPU监控
```

### GPU/NPU支持

#### NVIDIA GPU

```bash
# 安装CUDA (11.0+)
# 下载地址: https://developer.nvidia.com/cuda-downloads

# 安装GPU监控依赖
pip install GPUtil nvidia-ml-py

# 验证GPU
python -c "import GPUtil; print(f'GPU数量: {len(GPUtil.getGPUs())}')"
```

#### 华为NPU

```bash
# 安装NPU驱动
# 下载地址: https://www.huawei.com/cannonball/

# 安装NPU监控工具
pip install ascend-npu-ddk

# 验证NPU
npu-smi info
```

---

## 环境准备

### 1. 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv venv_performance

# 激活虚拟环境
# Linux/macOS:
source venv_performance/bin/activate

# Windows:
# venv_performance\Scripts\activate

# 升级pip
pip install --upgrade pip
```

### 2. 克隆项目

```bash
# 克隆仓库
git clone <repository-url>
cd xlerobot

# 或解压源码包
# unzip xlerobot.zip
# cd xlerobot
```

### 3. 安装依赖

```bash
# 安装基础依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt

# 安装性能测试依赖
pip install pytest pytest-benchmark pytest-cov
pip install psutil matplotlib plotly pandas numpy

# 以开发模式安装项目
pip install -e .
```

### 4. 创建目录结构

```bash
# 创建必要的目录
mkdir -p data/metrics
mkdir -p reports/performance
mkdir -p charts
mkdir -p logs

# 设置权限
chmod 755 data/metrics
chmod 755 reports/performance
chmod 755 logs
```

### 5. 验证环境

```python
# 验证Python环境
python --version
# 输出: Python 3.10.x

# 验证依赖
python -c "import numpy, pandas, matplotlib, plotly, psutil; print('✅ 所有依赖已安装')"

# 验证项目
python -c "import npu_converter.performance; print('✅ 项目模块可导入')"
```

---

## 安装步骤

### 方式1: pip安装 (推荐)

```bash
# 从PyPI安装 (尚未发布，此处为示例)
pip install npu-converter-performance

# 验证安装
python -c "import npu_converter.performance; print('安装成功')"
```

### 方式2: 从源码安装

```bash
# 克隆仓库
git clone <repository-url>
cd xlerobot

# 安装依赖
pip install -r requirements.txt

# 安装项目
pip install -e .

# 验证安装
python -m pytest tests/performance/unit/ -v
```

### 方式3: Docker安装

#### 创建Dockerfile

```dockerfile
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 安装项目
RUN pip install -e .

# 创建必要目录
RUN mkdir -p data/metrics reports/performance logs

# 设置环境变量
ENV PYTHONPATH=/app/src:$PYTHONPATH

# 默认命令
CMD ["python", "-m", "npu_converter.performance", "--help"]
```

#### 构建镜像

```bash
# 构建Docker镜像
docker build -t xlerobot-performance:latest .

# 运行容器
docker run -it \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/reports:/app/reports \
  xlerobot-performance:latest
```

#### 使用docker-compose

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  performance-benchmark:
    build: .
    container_name: xlerobot-performance
    volumes:
      - ./data:/app/data
      - ./reports:/app/reports
      - ./logs:/app/logs
    environment:
      - PYTHONPATH=/app/src
    command: python -m npu_converter.performance --config config/production.yaml
```

运行:

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 方式4: Kubernetes部署

创建 `performance-benchmark.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: performance-benchmark
spec:
  replicas: 1
  selector:
    matchLabels:
      app: performance-benchmark
  template:
    metadata:
      labels:
        app: performance-benchmark
    spec:
      containers:
      - name: performance-benchmark
        image: xlerobot-performance:latest
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        volumeMounts:
        - name: data-volume
          mountPath: /app/data
        - name: reports-volume
          mountPath: /app/reports
      volumes:
      - name: data-volume
        persistentVolumeClaim:
          claimName: performance-data-pvc
      - name: reports-volume
        persistentVolumeClaim:
          claimName: performance-reports-pvc
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: performance-data-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: performance-reports-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
```

部署:

```bash
# 应用配置
kubectl apply -f performance-benchmark.yaml

# 查看Pod状态
kubectl get pods -l app=performance-benchmark

# 查看日志
kubectl logs -f deployment/performance-benchmark
```

---

## 配置管理

### 配置文件结构

```
config/
├── performance/
│   ├── default.yaml          # 默认配置
│   ├── development.yaml      # 开发环境配置
│   ├── testing.yaml          # 测试环境配置
│   ├── production.yaml       # 生产环境配置
│   └── benchmarks/           # 基准测试配置
│       ├── test_cases.yaml   # 测试用例配置
│       └── alert_rules.yaml  # 告警规则配置
```

### 配置文件示例

#### 默认配置 (default.yaml)

```yaml
# 默认配置 - 适用于开发和测试
benchmark:
  max_concurrent: 5
  test_timeout: 1800  # 30分钟
  retry_count: 2
  retry_delay: 5
  cleanup_after_test: true
  save_raw_data: true
  output_dir: "reports/performance"

metrics:
  collection_interval: 2  # 每2秒采集一次
  buffer_size: 1000
  enable_gpu_monitoring: true
  enable_npu_monitoring: true
  enable_disk_io: true
  enable_network_io: true
  max_history_size: 10000
  storage_type: "memory"  # 使用内存存储
  storage_path: "data/metrics.db"

suite:
  default_timeout: 1800
  default_iterations: 100
  parallel_execution: true
  max_workers: 5

analyzer:
  anomaly_threshold: 2.0
  trend_window: 10
  percentile_levels: [50, 90, 95, 99]
  enable_anomaly_detection: true
  enable_trend_analysis: true
  enable_recommendations: true

report:
  output_dir: "reports/performance"
  include_charts: true
  include_recommendations: true
  include_trends: true
  template: "default"
  theme: "light"

visualization:
  width: 800
  height: 600
  dpi: 150
  theme: "default"
  color_palette: "viridis"
  font_size: 12
  output_format: "png"

alert:
  check_interval: 60
  default_severity: "medium"
  max_alerts: 100
  alert_retention_days: 30
  enable_notifications: false

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "logs/performance.log"
  max_size: "100MB"
  backup_count: 5
```

#### 生产环境配置 (production.yaml)

```yaml
# 生产环境配置 - 性能优化
benchmark:
  max_concurrent: 20  # 增加并发数
  test_timeout: 7200  # 2小时超时
  retry_count: 3
  retry_delay: 5
  cleanup_after_test: true
  save_raw_data: true
  output_dir: "/var/lib/xlerobot/reports"

metrics:
  collection_interval: 1  # 更频繁的采集
  buffer_size: 5000      # 更大的缓冲区
  enable_gpu_monitoring: true
  enable_npu_monitoring: true
  enable_disk_io: true
  enable_network_io: true
  max_history_size: 100000  # 更多历史数据
  storage_type: "sqlite"    # 使用SQLite
  storage_path: "/var/lib/xlerobot/data/metrics.db"

suite:
  default_timeout: 3600
  default_iterations: 200  # 更多迭代
  parallel_execution: true
  max_workers: 20

analyzer:
  anomaly_threshold: 2.5  # 更严格的异常检测
  trend_window: 20
  percentile_levels: [50, 90, 95, 99, 99.9]
  enable_anomaly_detection: true
  enable_trend_analysis: true
  enable_recommendations: true

report:
  output_dir: "/var/lib/xlerobot/reports"
  include_charts: true
  include_recommendations: true
  include_trends: true
  template: "professional"
  theme: "dark"

visualization:
  width: 1920
  height: 1080
  dpi: 300  # 更高分辨率
  theme: "professional"
  color_palette: "plotly"
  font_size: 14
  output_format: "png"

alert:
  check_interval: 30  # 更频繁的检查
  default_severity: "medium"
  max_alerts: 500
  alert_retention_days: 90
  enable_notifications: true

# 生产环境告警配置
notifications:
  email:
    enabled: true
    smtp_server: "smtp.company.com"
    smtp_port: 587
    username: "alerts@company.com"
    password: "${EMAIL_PASSWORD}"
    recipients:
      - "admin@company.com"
      - "ops@company.com"

  slack:
    enabled: true
    webhook_url: "${SLACK_WEBHOOK_URL}"
    channel: "#alerts"
    username: "XLeRobot Alerts"

logging:
  level: "WARNING"  # 生产环境减少日志输出
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "/var/log/xlerobot/performance.log"
  max_size: "500MB"
  backup_count: 10
```

### 加载配置

```python
import yaml
from npu_converter.performance import (
    BenchmarkConfig, MetricsConfig, SuiteConfig,
    AnalyzerConfig, ReportConfig, VisualizationConfig, AlertConfig
)

def load_config(config_file="config/performance/default.yaml"):
    """从YAML文件加载配置"""
    with open(config_file, "r") as f:
        config_data = yaml.safe_load(f)

    # 创建配置对象
    benchmark_config = BenchmarkConfig(**config_data["benchmark"])
    metrics_config = MetricsConfig(**config_data["metrics"])
    suite_config = SuiteConfig(**config_data["suite"])
    analyzer_config = AnalyzerConfig(**config_data["analyzer"])
    report_config = ReportConfig(**config_data["report"])
    viz_config = VisualizationConfig(**config_data["visualization"])
    alert_config = AlertConfig(**config_data["alert"])

    return {
        "benchmark": benchmark_config,
        "metrics": metrics_config,
        "suite": suite_config,
        "analyzer": analyzer_config,
        "report": report_config,
        "visualization": viz_config,
        "alert": alert_config
    }

# 使用配置
configs = load_config("config/performance/production.yaml")
runner = BenchmarkRunner(configs["benchmark"])
collector = MetricsCollector(configs["metrics"])
```

### 环境变量配置

使用环境变量管理敏感配置:

```python
import os
from typing import Optional

def load_config_from_env():
    """从环境变量加载配置"""
    config = {
        "max_concurrent": int(os.getenv("MAX_CONCURRENT", "10")),
        "test_timeout": int(os.getenv("TEST_TIMEOUT", "3600")),
        "email_password": os.getenv("EMAIL_PASSWORD"),
        "slack_webhook": os.getenv("SLACK_WEBHOOK_URL"),
    }
    return config

# 使用示例
config = load_config_from_env()
print(f"最大并发数: {config['max_concurrent']}")
```

---

## 验证部署

### 1. 验证安装

```bash
# 验证Python模块
python -c "import npu_converter.performance; print('✅ 模块导入成功')"

# 验证依赖库
python -c "
import sys
required = ['pytest', 'psutil', 'matplotlib', 'plotly', 'pandas', 'numpy']
missing = [m for m in required if m not in sys.modules]
if missing:
    print(f'❌ 缺少依赖: {missing}')
else:
    print('✅ 所有依赖已安装')
"

# 验证测试文件
python -m pytest tests/performance/unit/ --collect-only -q
```

### 2. 运行快速测试

```python
#!/usr/bin/env python3
"""
快速验证部署
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from npu_converter.performance import (
    BenchmarkRunner, MetricsCollector, BenchmarkSuite,
    BenchmarkConfig, MetricsConfig, SuiteConfig
)

def quick_test():
    """运行快速验证测试"""
    print("=" * 60)
    print("XLeRobot性能基准测试 - 部署验证")
    print("=" * 60)

    # 1. 创建配置
    print("\n1. 创建配置...")
    config = BenchmarkConfig(
        max_concurrent=5,
        test_timeout=300,
        output_dir="reports/validation"
    )
    print("✅ 配置创建成功")

    # 2. 创建组件
    print("\n2. 创建组件...")
    runner = BenchmarkRunner(config)
    collector = MetricsCollector(MetricsConfig())
    suite = BenchmarkSuite(SuiteConfig())
    print("✅ 组件创建成功")

    # 3. 获取测试用例
    print("\n3. 获取测试用例...")
    test_case = suite.get_test_case("TC-001")
    print(f"✅ 测试用例: {test_case.test_id}")

    # 4. 运行测试
    print("\n4. 运行测试...")
    start_time = time.time()
    collector.start_collection("validation-test")
    result = runner.run_benchmark(test_case)
    collector.stop_collection("validation-test")
    duration = time.time() - start_time

    # 5. 验证结果
    print("\n5. 验证结果...")
    print(f"   测试状态: {result.status}")
    print(f"   耗时: {result.duration:.2f}秒")
    print(f"   总耗时: {duration:.2f}秒")

    if result.status == "success":
        print("\n✅ 部署验证成功！")
        return True
    else:
        print(f"\n❌ 部署验证失败: {result.error_message}")
        return False

if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1)
```

运行验证:

```bash
# 运行验证脚本
python scripts/validate_deployment.py

# 预期输出:
# ================================
# XLeRobot性能基准测试 - 部署验证
# ================================
#
# 1. 创建配置...
# ✅ 配置创建成功
#
# 2. 创建组件...
# ✅ 组件创建成功
#
# 3. 获取测试用例...
# ✅ 测试用例: TC-001
#
# 4. 运行测试...
# [INFO] Starting test TC-001
# [INFO] Test completed successfully
#
# 5. 验证结果...
#    测试状态: success
#    耗时: 1.23秒
#    总耗时: 1.45秒
#
# ✅ 部署验证成功！
```

### 3. 性能测试

```python
#!/usr/bin/env python3
"""
性能基准测试
"""

import time
import json
from pathlib import Path

from npu_converter.performance import (
    BenchmarkRunner, MetricsCollector, BenchmarkSuite,
    PerformanceAnalyzer, ReportGenerator,
    BenchmarkConfig, MetricsConfig, SuiteConfig,
    AnalyzerConfig, ReportConfig
)

def performance_benchmark():
    """运行完整性能基准测试"""
    print("=" * 60)
    print("XLeRobot性能基准测试 - 完整测试")
    print("=" * 60)

    # 创建配置
    config = BenchmarkConfig(
        max_concurrent=10,
        test_timeout=3600,
        output_dir=f"reports/benchmark_{int(time.time())}"
    )

    runner = BenchmarkRunner(config)
    collector = MetricsCollector(MetricsConfig())
    suite = BenchmarkSuite(SuiteConfig())
    analyzer = PerformanceAnalyzer(AnalyzerConfig())
    generator = ReportGenerator(ReportConfig(include_charts=True))

    # 获取测试用例
    test_cases = suite.list_test_cases()
    print(f"\n测试用例数量: {len(test_cases)}")

    results = []
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] 运行测试: {test_case.test_id}")
        start_time = time.time()

        try:
            collector.start_collection(test_case.test_id)
            result = runner.run_benchmark(test_case)
            collector.stop_collection(test_case.test_id)

            results.append(result)
            status = "✅" if result.status == "success" else "❌"
            print(f"   {status} 状态: {result.status}, 耗时: {result.duration:.2f}秒")

        except Exception as e:
            print(f"   ❌ 测试失败: {e}")

    # 分析结果
    print("\n" + "=" * 60)
    print("测试结果分析")
    print("=" * 60)

    if results:
        analysis = analyzer.analyze_results(results)

        print(f"总测试数: {analysis.total_tests}")
        print(f"成功: {analysis.passed_tests}")
        print(f"失败: {analysis.failed_tests}")
        print(f"成功率: {analysis.success_rate:.2%}")
        print(f"平均耗时: {analysis.avg_duration:.2f}秒")
        print(f"P95耗时: {analysis.p95_duration:.2f}秒")

        # 生成报告
        summary = generator.generate_summary_report(analysis)
        generator.export_report(summary, "html", f"{config.output_dir}/summary.html")
        generator.export_report(summary, "json", f"{config.output_dir}/summary.json")

        # 保存原始结果
        with open(f"{config.output_dir}/results.json", "w") as f:
            json.dump([r.__dict__ for r in results], f, default=str, indent=2)

        print(f"\n✅ 报告已生成: {config.output_dir}/")

    print("\n" + "=" * 60)
    print("性能基准测试完成")
    print("=" * 60)

if __name__ == "__main__":
    performance_benchmark()
```

### 4. 健康检查

```bash
#!/bin/bash
# 健康检查脚本 - health_check.sh

echo "XLeRobot性能基准测试 - 健康检查"
echo "=================================="

# 检查Python
if command -v python3 &> /dev/null; then
    echo "✅ Python已安装: $(python3 --version)"
else
    echo "❌ Python未安装"
    exit 1
fi

# 检查依赖
echo ""
echo "检查依赖..."
python3 -c "
import sys
missing = []
for mod in ['pytest', 'psutil', 'matplotlib', 'plotly', 'pandas', 'numpy']:
    try:
        __import__(mod)
    except ImportError:
        missing.append(mod)

if missing:
    print(f'❌ 缺少依赖: {missing}')
    sys.exit(1)
else:
    print('✅ 所有依赖已安装')
"

# 检查GPU (如果可用)
echo ""
echo "检查GPU..."
python3 -c "
try:
    import GPUtil
    gpus = GPUtil.getGPUs()
    print(f'✅ 检测到 {len(gpus)} 个GPU')
    for gpu in gpus:
        print(f'   - {gpu.name}: {gpu.memoryTotal}MB')
except ImportError:
    print('⚠️ GPU监控依赖未安装 (可选)')
"

# 检查目录
echo ""
echo "检查目录..."
for dir in data/metrics reports/performance logs; do
    if [ -d "$dir" ]; then
        echo "✅ 目录存在: $dir"
    else
        echo "❌ 目录不存在: $dir"
        mkdir -p "$dir"
        echo "   已创建: $dir"
    fi
done

# 运行快速测试
echo ""
echo "运行快速测试..."
python3 scripts/validate_deployment.py

echo ""
echo "=================================="
echo "健康检查完成"
```

运行健康检查:

```bash
# 使脚本可执行
chmod +x scripts/health_check.sh

# 运行健康检查
./scripts/health_check.sh
```

---

## 运行性能测试

### 1. 命令行工具

创建命令行工具:

```python
#!/usr/bin/env python3
"""
性能基准测试命令行工具
"""

import argparse
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from npu_converter.performance import (
    BenchmarkRunner, MetricsCollector, BenchmarkSuite,
    PerformanceAnalyzer, ReportGenerator,
    BenchmarkConfig, MetricsConfig, SuiteConfig,
    AnalyzerConfig, ReportConfig
)

def run_test(test_id, config_file, output_dir):
    """运行单个测试用例"""
    # 加载配置
    with open(config_file, "r") as f:
        config_data = json.load(f)

    benchmark_config = BenchmarkConfig(**config_data["benchmark"])
    if output_dir:
        benchmark_config.output_dir = output_dir

    # 创建组件
    runner = BenchmarkRunner(benchmark_config)
    collector = MetricsCollector(MetricsConfig())
    suite = BenchmarkSuite(SuiteConfig())

    # 运行测试
    test_case = suite.get_test_case(test_id)
    collector.start_collection(test_id)
    result = runner.run_benchmark(test_case)
    collector.stop_collection(test_id)

    return result

def run_suite(config_file, output_dir):
    """运行测试套件"""
    # 加载配置
    with open(config_file, "r") as f:
        config_data = json.load(f)

    benchmark_config = BenchmarkConfig(**config_data["benchmark"])
    if output_dir:
        benchmark_config.output_dir = output_dir

    runner = BenchmarkRunner(benchmark_config)
    suite = BenchmarkSuite(SuiteConfig())
    analyzer = PerformanceAnalyzer(AnalyzerConfig())
    generator = ReportGenerator(ReportConfig(include_charts=True))

    # 运行所有测试
    test_cases = suite.list_test_cases()
    results = [runner.run_benchmark(tc) for tc in test_cases]

    # 分析和报告
    analysis = analyzer.analyze_results(results)
    summary = generator.generate_summary_report(analysis)
    generator.export_report(summary, "html", f"{benchmark_config.output_dir}/summary.html")

    return analysis

def main():
    parser = argparse.ArgumentParser(description="XLeRobot性能基准测试")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # run命令 - 运行单个测试
    run_parser = subparsers.add_parser("run", help="运行单个测试用例")
    run_parser.add_argument("--test-id", required=True, help="测试用例ID")
    run_parser.add_argument("--config", default="config/performance/default.json", help="配置文件")
    run_parser.add_argument("--output", help="输出目录")

    # suite命令 - 运行测试套件
    suite_parser = subparsers.add_parser("suite", help="运行测试套件")
    suite_parser.add_argument("--config", default="config/performance/default.json", help="配置文件")
    suite_parser.add_argument("--output", help="输出目录")

    # list命令 - 列出测试用例
    list_parser = subparsers.add_parser("list", help="列出可用测试用例")

    args = parser.parse_args()

    if args.command == "run":
        result = run_test(args.test_id, args.config, args.output)
        print(f"测试结果: {result.status}")
        print(f"耗时: {result.duration:.2f}秒")
    elif args.command == "suite":
        analysis = run_suite(args.config, args.output)
        print(f"测试套件完成:")
        print(f"  总测试数: {analysis.total_tests}")
        print(f"  成功率: {analysis.success_rate:.2%}")
    elif args.command == "list":
        suite = BenchmarkSuite()
        test_cases = suite.list_test_cases()
        print("可用测试用例:")
        for tc in test_cases:
            print(f"  {tc.test_id}: {tc.description}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
```

安装命令行工具:

```bash
# 创建符号链接
ln -s /path/to/xlerobot/scripts/perf_benchmark.py /usr/local/bin/perf-benchmark

# 使用
perf-benchmark --help
perf-benchmark list
perf-benchmark run --test-id TC-001 --config config/production.json
perf-benchmark suite --config config/production.json --output reports/latest
```

### 2. 批量测试

```python
#!/usr/bin/env python3
"""
批量性能测试脚本
"""

import argparse
import json
import time
from datetime import datetime
from pathlib import Path

from npu_converter.performance import (
    BenchmarkRunner, BenchmarkSuite, PerformanceAnalyzer,
    BenchmarkConfig, SuiteConfig, AnalyzerConfig
)

def batch_test(test_suite_ids, config_file, output_dir):
    """批量运行测试"""
    # 加载配置
    with open(config_file, "r") as f:
        config_data = json.load(f)

    benchmark_config = BenchmarkConfig(**config_data["benchmark"])
    benchmark_config.output_dir = output_dir

    runner = BenchmarkRunner(benchmark_config)
    suite = BenchmarkSuite(SuiteConfig())
    analyzer = PerformanceAnalyzer(AnalyzerConfig())

    # 创建测试套件
    test_suite = suite.create_test_suite(test_suite_ids)

    # 运行测试
    print(f"开始批量测试: {len(test_suite_ids)} 个测试用例")
    start_time = time.time()

    results = runner.run_suite(test_suite, parallel=True)

    duration = time.time() - start_time

    # 分析结果
    analysis = analyzer.analyze_results(results)

    # 打印结果
    print(f"\n批量测试完成")
    print(f"  总耗时: {duration:.2f}秒")
    print(f"  测试数量: {analysis.total_tests}")
    print(f"  成功: {analysis.passed_tests}")
    print(f"  失败: {analysis.failed_tests}")
    print(f"  成功率: {analysis.success_rate:.2%}")
    print(f"  平均耗时: {analysis.avg_duration:.2f}秒")

    # 保存结果
    with open(f"{output_dir}/batch_results.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "duration": duration,
            "analysis": analysis.__dict__
        }, f, indent=2, default=str)

    return analysis

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="批量性能测试")
    parser.add_argument("--suite", nargs="+", required=True, help="测试套件ID列表")
    parser.add_argument("--config", default="config/performance/default.json", help="配置文件")
    parser.add_argument("--output", required=True, help="输出目录")

    args = parser.parse_args()

    batch_test(args.suite, args.config, args.output)
```

运行批量测试:

```bash
# 运行ASR相关测试
python scripts/batch_test.py \
  --suite TC-001 TC-002 \
  --config config/production.json \
  --output reports/asr_tests_$(date +%Y%m%d)

# 运行TTS相关测试
python scripts/batch_test.py \
  --suite TC-002 TC-003 \
  --config config/production.json \
  --output reports/tts_tests_$(date +%Y%m%d)

# 运行并发测试
python scripts/batch_test.py \
  --suite TC-004 TC-005 \
  --config config/production.json \
  --output reports/concurrent_tests_$(date +%Y%m%d)
```

### 3. 定时任务

使用cron设置定时任务:

```bash
# 编辑crontab
crontab -e

# 添加定时任务
# 每天凌晨2点运行完整测试套件
0 2 * * * /usr/bin/python3 /path/to/xlerobot/scripts/batch_test.py --suite TC-001 TC-002 TC-003 --config /path/to/xlerobot/config/production.json --output /path/to/xlerobot/reports/daily/$(date +\%Y\%m\%d)

# 每周一上午9点运行压力测试
0 9 * * 1 /usr/bin/python3 /path/to/xlerobot/scripts/batch_test.py --suite TC-005 --config /path/to/xlerobot/config/production.json --output /path/to/xlerobot/reports/weekly/$(date +\%Y\%m\%d)
```

使用systemd服务:

创建服务文件 `/etc/systemd/system/xlerobot-performance.service`:

```ini
[Unit]
Description=XLeRobot Performance Benchmark
After=network.target

[Service]
Type=simple
User=xlerobot
WorkingDirectory=/opt/xlerobot
ExecStart=/opt/xlerobot/venv/bin/python -m npu_converter.performance server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

创建定时器 `/etc/systemd/system/xlerobot-performance.timer`:

```ini
[Unit]
Description=Run XLeRobot Performance Benchmark daily
Requires=xlerobot-performance.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

启用服务:

```bash
# 重新加载systemd
sudo systemctl daemon-reload

# 启用并启动服务
sudo systemctl enable xlerobot-performance.service
sudo systemctl start xlerobot-performance.service

# 启用定时器
sudo systemctl enable xlerobot-performance.timer
sudo systemctl start xlerobot-performance.timer

# 查看状态
sudo systemctl status xlerobot-performance.service
sudo systemctl status xlerobot-performance.timer

# 查看日志
sudo journalctl -u xlerobot-performance.service -f
```

---

## CI/CD集成

### GitHub Actions

参见之前创建的 `.github/workflows/performance-benchmark.yml`

### Jenkins

#### Jenkinsfile

```groovy
pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.10'
        VIRTUAL_ENV = 'venv'
    }

    stages {
        stage('Setup') {
            steps {
                sh '''
                    python3 -m venv $VIRTUAL_ENV
                    source $VIRTUAL_ENV/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install -e .
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    source $VIRTUAL_ENV/bin/activate
                    python -m pytest tests/performance/unit/ -v --cov=src/npu_converter/performance --cov-report=xml
                '''
            }
            post {
                always {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])

                    publishTestResults testResultsPattern: 'test-results.xml'
                    publishCoverage adapters: [coberturaAdapter('coverage.xml')], sourceFileResolver: sourceFiles('STORE_LAST_BUILD')
                }
            }
        }

        stage('Benchmark') {
            steps {
                sh '''
                    source $VIRTUAL_ENV/bin/activate
                    python scripts/performance_benchmark.py \
                        --config config/ci.json \
                        --output reports/ci/$(date +%Y%m%d_%H%M%S)
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/ci/**', fingerprint: true

                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'reports/ci',
                        reportFiles: '**/summary.html',
                        reportName: 'Performance Benchmark Report'
                    ])
                }
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    # 部署到生产环境的逻辑
                    echo "Deploying to production..."
                '''
            }
        }
    }

    post {
        always {
            sh '''
                source $VIRTUAL_ENV/bin/activate
                deactivate
                rm -rf $VIRTUAL_ENV
            '''
        }
        failure {
            emailext (
                subject: "Build Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: "Build failed. Check console output at ${env.BUILD_URL}",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
        success {
            emailext (
                subject: "Build Success: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: "Build completed successfully. View results at ${env.BUILD_URL}",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
    }
}
```

### GitLab CI

创建 `.gitlab-ci.yml`:

```yaml
stages:
  - test
  - benchmark
  - deploy

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip/
    - venv/

before_script:
  - python3 -V
  - python3 -m venv venv
  - source venv/bin/activate
  - pip install --upgrade pip
  - pip install -r requirements.txt
  - pip install -e .

test:
  stage: test
  script:
    - source venv/bin/activate
    - python -m pytest tests/performance/unit/ -v --junitxml=test-results.xml
  artifacts:
    when: always
    reports:
      junit: test-results.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

benchmark:
  stage: benchmark
  script:
    - source venv/bin/activate
    - python scripts/performance_benchmark.py --config config/ci.json --output reports/
  artifacts:
    when: always
    paths:
      - reports/
    expire_in: 1 week

deploy:
  stage: deploy
  script:
    - echo "Deploy to production"
  only:
    - main
```

---

## 监控和告警

### 1. 系统监控

创建监控系统:

```python
#!/usr/bin/env python3
"""
性能基准测试监控系统
"""

import time
import json
import psutil
import smtplib
from datetime import datetime
from email.mime.text import MimeText

from npu_converter.performance import (
    MetricsCollector, MetricsConfig,
    AlertSystem, AlertConfig, AlertRule
)

class SystemMonitor:
    """系统监控器"""

    def __init__(self, config_file="config/monitoring.json"):
        with open(config_file, "r") as f:
            self.config = json.load(f)

        self.collector = MetricsCollector(MetricsConfig())
        self.alerts = AlertSystem(AlertConfig(
            check_interval=30,
            default_severity="medium"
        ))

        # 添加告警规则
        self._setup_alerts()

        # 通知配置
        self.smtp_config = self.config.get("smtp", {})
        self.slack_config = self.config.get("slack", {})

    def _setup_alerts(self):
        """设置告警规则"""
        # CPU使用率告警
        self.alerts.add_rule(AlertRule(
            name="高CPU使用率",
            metric="cpu_usage",
            threshold=85.0,
            comparison=">",
            severity="high",
            duration=300
        ))

        # 内存使用率告警
        self.alerts.add_rule(AlertRule(
            name="高内存使用率",
            metric="memory_usage",
            threshold=90.0,
            comparison=">",
            severity="high",
            duration=300
        ))

        # 磁盘使用率告警
        self.alerts.add_rule(AlertRule(
            name="高磁盘使用率",
            metric="disk_usage",
            threshold=85.0,
            comparison=">",
            severity="medium",
            duration=600
        ))

    def check_system_health(self):
        """检查系统健康状态"""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()

        # 内存
        memory = psutil.virtual_memory()

        # 磁盘
        disk = psutil.disk_usage('/')

        # 构建指标
        metrics = type('Metrics', (), {
            'cpu_usage': cpu_percent,
            'memory_usage': memory.percent,
            'disk_usage': disk.percent,
            'timestamp': datetime.now()
        })()

        # 检查告警
        self.alerts.check_metrics(metrics)

        # 返回状态
        return {
            "cpu": {
                "usage": cpu_percent,
                "count": cpu_count,
                "status": "healthy" if cpu_percent < 80 else "warning"
            },
            "memory": {
                "usage": memory.percent,
                "total": memory.total / 1024 / 1024 / 1024,
                "used": memory.used / 1024 / 1024 / 1024,
                "status": "healthy" if memory.percent < 85 else "warning"
            },
            "disk": {
                "usage": disk.percent,
                "total": disk.total / 1024 / 1024 / 1024,
                "used": disk.used / 1024 / 1024 / 1024,
                "status": "healthy" if disk.percent < 80 else "warning"
            }
        }

    def send_notification(self, alert):
        """发送通知"""
        subject = f"[{alert.severity.upper()}] XLeRobot监控告警"
        message = f"""
告警详情:
名称: {alert.title}
严重程度: {alert.severity}
消息: {alert.message}
指标: {alert.metric}
当前值: {alert.value}
阈值: {alert.threshold}
时间: {alert.created_time}
        """

        # 邮件通知
        if self.smtp_config.get("enabled", False):
            self._send_email(subject, message)

        # Slack通知
        if self.slack_config.get("enabled", False):
            self._send_slack(alert)

    def _send_email(self, subject, message):
        """发送邮件"""
        try:
            msg = MimeText(message)
            msg['Subject'] = subject
            msg['From'] = self.smtp_config['from']
            msg['To'] = ", ".join(self.smtp_config['to'])

            server = smtplib.SMTP(
                self.smtp_config['host'],
                self.smtp_config['port']
            )
            server.starttls()
            server.login(
                self.smtp_config['username'],
                self.smtp_config['password']
            )
            server.send_message(msg)
            server.quit()
            print(f"✅ 邮件通知已发送")
        except Exception as e:
            print(f"❌ 邮件发送失败: {e}")

    def _send_slack(self, alert):
        """发送Slack通知"""
        try:
            import requests

            color = {
                'low': 'good',
                'medium': 'warning',
                'high': 'danger',
                'critical': 'danger'
            }.get(alert.severity, 'warning')

            payload = {
                "text": "🚨 XLeRobot监控告警",
                "attachments": [{
                    "color": color,
                    "fields": [
                        {"title": "告警", "value": alert.title, "short": True},
                        {"title": "严重程度", "value": alert.severity, "short": True},
                        {"title": "消息", "value": alert.message, "short": False},
                    ]
                }]
            }

            response = requests.post(
                self.slack_config['webhook_url'],
                json=payload
            )
            if response.status_code == 200:
                print(f"✅ Slack通知已发送")
        except Exception as e:
            print(f"❌ Slack发送失败: {e}")

    def run(self):
        """运行监控"""
        print("启动系统监控...")

        # 订阅告警事件
        self.alerts.subscribe(self.send_notification)

        while True:
            try:
                health = self.check_system_health()

                # 打印状态
                print(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"CPU: {health['cpu']['usage']:.1f}% ({health['cpu']['status']})")
                print(f"内存: {health['memory']['usage']:.1f}% ({health['memory']['status']})")
                print(f"磁盘: {health['disk']['usage']:.1f}% ({health['disk']['status']})")

                # 检查所有组件是否健康
                if all(
                    health[key]['status'] == 'healthy'
                    for key in health.keys()
                ):
                    print("✅ 系统健康")

                time.sleep(60)  # 每分钟检查一次

            except KeyboardInterrupt:
                print("\n监控已停止")
                break
            except Exception as e:
                print(f"❌ 监控错误: {e}")
                time.sleep(5)

if __name__ == "__main__":
    monitor = SystemMonitor()
    monitor.run()
```

### 2. Prometheus监控

创建Prometheus指标:

```python
#!/usr/bin/env python3
"""
Prometheus指标导出器
"""

from prometheus_client import (
    Gauge, Counter, Histogram, start_http_server
)
import time

# 定义指标
cpu_usage_gauge = Gauge('xlerobot_cpu_usage_percent', 'CPU usage percentage')
memory_usage_gauge = Gauge('xlerobot_memory_usage_percent', 'Memory usage percentage')
disk_usage_gauge = Gauge('xlerobot_disk_usage_percent', 'Disk usage percentage')

test_runs_total = Counter('xlerobot_test_runs_total', 'Total test runs', ['test_id'])
test_duration = Histogram('xlerobot_test_duration_seconds', 'Test duration', ['test_id'])
test_failures_total = Counter('xlerobot_test_failures_total', 'Total test failures', ['test_id'])

benchmark_results_gauge = Gauge('xlerobot_benchmark_result', 'Benchmark result', ['test_id', 'metric'])

class PrometheusExporter:
    """Prometheus指标导出器"""

    def __init__(self, port=8000):
        self.port = port

    def update_system_metrics(self):
        """更新系统指标"""
        import psutil

        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_usage_gauge.set(cpu_percent)

        # 内存
        memory = psutil.virtual_memory()
        memory_usage_gauge.set(memory.percent)

        # 磁盘
        disk = psutil.disk_usage('/')
        disk_usage_gauge.set(disk.percent)

    def record_test_result(self, test_id, duration, success):
        """记录测试结果"""
        test_runs_total.labels(test_id=test_id).inc()
        test_duration.labels(test_id=test_id).observe(duration)

        if not success:
            test_failures_total.labels(test_id=test_id).inc()

    def record_benchmark_result(self, test_id, metric, value):
        """记录基准测试结果"""
        benchmark_results_gauge.labels(
            test_id=test_id,
            metric=metric
        ).set(value)

    def start(self):
        """启动Prometheus服务器"""
        print(f"启动Prometheus指标服务器: http://localhost:{self.port}/metrics")
        start_http_server(self.port)

        while True:
            try:
                self.update_system_metrics()
                time.sleep(60)
            except KeyboardInterrupt:
                print("\n服务器已停止")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")
                time.sleep(5)

if __name__ == "__main__":
    exporter = PrometheusExporter()
    exporter.start()
```

配置Prometheus:

创建 `prometheus.yml`:

```yaml
global:
  scrape_interval: 60s

scrape_configs:
  - job_name: 'xlerobot-performance'
    static_configs:
      - targets: ['localhost:8000']
    scrape_interval: 60s
```

运行:

```bash
# 启动Prometheus服务器
python scripts/prometheus_exporter.py &

# 启动Prometheus
prometheus --config.file=prometheus.yml

# 查看指标
curl http://localhost:8000/metrics
```

### 3. Grafana仪表盘

创建Grafana仪表盘配置 `grafana-dashboard.json`:

```json
{
  "dashboard": {
    "id": null,
    "title": "XLeRobot Performance Benchmark",
    "tags": ["performance", "benchmark"],
    "style": "dark",
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "System CPU Usage",
        "type": "stat",
        "targets": [
          {
            "expr": "xlerobot_cpu_usage_percent",
            "legendFormat": "CPU"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "thresholds": {
              "steps": [
                {"color": "green", "value": 0},
                {"color": "yellow", "value": 70},
                {"color": "red", "value": 85}
              ]
            }
          }
        }
      },
      {
        "id": 2,
        "title": "System Memory Usage",
        "type": "stat",
        "targets": [
          {
            "expr": "xlerobot_memory_usage_percent",
            "legendFormat": "Memory"
          }
        ]
      },
      {
        "id": 3,
        "title": "Test Duration",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(xlerobot_test_duration_seconds_sum[5m]) / rate(xlerobot_test_duration_seconds_count[5m])",
            "legendFormat": "{{test_id}}"
          }
        ]
      }
    ]
  }
}
```

---

## 维护和更新

### 1. 日志管理

配置日志轮转:

创建 `logrotate.conf`:

```
/var/log/xlerobot/performance.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 xlerobot xlerobot
    postrotate
        systemctl reload xlerobot-performance
    endscript
}
```

安装配置:

```bash
sudo cp logrotate.conf /etc/logrotate.d/xlerobot-performance
```

### 2. 数据备份

```bash
#!/bin/bash
# 备份脚本 - backup.sh

BACKUP_DIR="/backup/xlerobot/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# 备份配置文件
cp -r config "$BACKUP_DIR/"

# 备份报告
cp -r reports "$BACKUP_DIR/"

# 备份指标数据
cp -r data/metrics "$BACKUP_DIR/"

# 备份日志
cp /var/log/xlerobot/performance.log "$BACKUP_DIR/"

# 压缩备份
tar -czf "${BACKUP_DIR}.tar.gz" -C "$(dirname $BACKUP_DIR)" "$(basename $BACKUP_DIR)"
rm -rf "$BACKUP_DIR"

echo "✅ 备份完成: ${BACKUP_DIR}.tar.gz"
```

设置定时备份:

```bash
# 添加到crontab
0 3 * * * /path/to/backup.sh
```

### 3. 更新流程

```bash
#!/bin/bash
# 更新脚本 - update.sh

VERSION="$1"
if [ -z "$VERSION" ]; then
    echo "用法: $0 <版本号>"
    exit 1
fi

echo "开始更新到版本: $VERSION"

# 1. 备份当前版本
echo "1. 备份当前版本..."
./backup.sh

# 2. 停止服务
echo "2. 停止服务..."
sudo systemctl stop xlerobot-performance

# 3. 更新代码
echo "3. 更新代码..."
git fetch origin
git checkout "v$VERSION"

# 4. 安装依赖
echo "4. 安装依赖..."
pip install -r requirements.txt
pip install -e .

# 5. 运行测试
echo "5. 运行测试..."
python -m pytest tests/performance/ -v

# 6. 启动服务
echo "6. 启动服务..."
sudo systemctl start xlerobot-performance

# 7. 验证部署
echo "7. 验证部署..."
python scripts/validate_deployment.py

echo "✅ 更新完成"
```

### 4. 健康检查

```bash
#!/bin/bash
# 健康检查脚本 - health_check.sh

echo "XLeRobot性能基准测试 - 系统健康检查"
echo "=================================="

# 检查服务状态
if systemctl is-active --quiet xlerobot-performance; then
    echo "✅ 服务运行正常"
else
    echo "❌ 服务未运行"
    exit 1
fi

# 检查端口
if netstat -tuln | grep -q ":8000 "; then
    echo "✅ 监控端口正常 (8000)"
else
    echo "⚠️ 监控端口未监听"
fi

# 检查磁盘空间
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    echo "✅ 磁盘空间充足 (${DISK_USAGE}%)"
else
    echo "⚠️ 磁盘空间不足 (${DISK_USAGE}%)"
fi

# 检查内存使用
MEM_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ "$MEM_USAGE" -lt 80 ]; then
    echo "✅ 内存使用正常 (${MEM_USAGE}%)"
else
    echo "⚠️ 内存使用率过高 (${MEM_USAGE}%)"
fi

# 检查最近测试
LAST_TEST=$(find reports/ -name "*.json" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
if [ -n "$LAST_TEST" ]; then
    TEST_TIME=$(stat -c %Y "$LAST_TEST")
    NOW=$(date +%s)
    ELAPSED=$(( (NOW - TEST_TIME) / 3600 ))
    echo "✅ 最近测试: $ELAPSED 小时前"
else
    echo "⚠️ 无历史测试记录"
fi

echo "=================================="
echo "健康检查完成"
```

---

## 故障排除

### 常见问题

#### 1. 服务无法启动

**症状**: `systemctl start xlerobot-performance` 失败

**诊断**:
```bash
# 查看服务状态
sudo systemctl status xlerobot-performance

# 查看日志
sudo journalctl -u xlerobot-performance -n 100

# 手动启动测试
python scripts/validate_deployment.py
```

**解决方案**:
- 检查Python环境
- 检查依赖库
- 检查配置文件
- 检查文件权限

#### 2. 测试执行缓慢

**症状**: 测试运行时间过长

**诊断**:
```bash
# 查看系统负载
top
htop

# 查看I/O状态
iotop

# 查看网络状态
netstat -i
```

**解决方案**:
- 减少并发数
- 优化测试参数
- 增加系统资源
- 检查网络延迟

#### 3. 内存不足

**症状**: `MemoryError` 或系统卡顿

**诊断**:
```bash
# 查看内存使用
free -h
ps aux --sort=-%mem | head

# 检查内存泄漏
valgrind --leak-check=full python script.py
```

**解决方案**:
- 减少并发数
- 减少缓冲区大小
- 使用SQLite存储
- 增加系统内存

#### 4. GPU监控失败

**症状**: GPU相关错误

**诊断**:
```bash
# 检查GPU状态
nvidia-smi

# 检查GPU驱动
cat /proc/driver/nvidia/version

# 测试GPU监控
python -c "import GPUtil; print(GPUtil.getGPUs())"
```

**解决方案**:
- 安装GPU驱动
- 安装GPU监控依赖
- 禁用GPU监控

### 日志分析

```bash
# 查看错误日志
grep -i error /var/log/xlerobot/performance.log | tail -20

# 查看最近的日志
tail -f /var/log/xlerobot/performance.log

# 按级别过滤
grep "ERROR" /var/log/xlerobot/performance.log
grep "WARNING" /var/log/xlerobot/performance.log

# 查看特定测试的日志
grep "TC-001" /var/log/xlerobot/performance.log
```

---

## 最佳实践

### 1. 安全配置

```yaml
# 生产环境安全配置 - production.yaml
security:
  # 限制访问IP
  allowed_ips:
    - "192.168.1.0/24"
    - "10.0.0.0/8"

  # API认证
  api_key_required: true
  api_key_file: "/etc/xlerobot/api_key"

  # 日志敏感信息过滤
  filter_secrets: true

  # HTTPS配置
  https:
    enabled: true
    cert_file: "/etc/ssl/certs/xlerobot.crt"
    key_file: "/etc/ssl/private/xlerobot.key"
```

### 2. 性能优化

```python
# 性能优化配置
optimization_config = {
    # 使用进程池而非线程池
    "use_process_pool": True,
    "process_pool_size": 4,

    # 启用异步I/O
    "use_async_io": True,

    # 批量处理
    "batch_size": 100,

    # 内存映射文件
    "use_memory_mapping": True,

    # 压缩存储
    "compress_data": True,
}
```

### 3. 高可用配置

```yaml
# 高可用配置 - ha.yaml
ha:
  # 主从配置
  mode: "active-passive"

  # 健康检查
  health_check:
    interval: 30
    timeout: 10
    retries: 3

  # 故障转移
  failover:
    automatic: true
    threshold: 3  # 连续3次失败后切换

  # 数据同步
  sync:
    method: "rsync"
    interval: 60
```

### 4. 灾备恢复

```bash
#!/bin/bash
# 灾难恢复脚本 - disaster_recovery.sh

RECOVERY_DIR="/recovery/xlerobot"
BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
    echo "用法: $0 <备份文件路径>"
    exit 1
fi

echo "开始灾难恢复..."

# 1. 停止服务
sudo systemctl stop xlerobot-performance

# 2. 清理当前数据
rm -rf /opt/xlerobot/data/*
rm -rf /opt/xlerobot/reports/*

# 3. 解压备份
tar -xzf "$BACKUP_FILE" -C /

# 4. 恢复权限
chown -R xlerobot:xlerobot /opt/xlerobot

# 5. 启动服务
sudo systemctl start xlerobot-performance

# 6. 验证恢复
python scripts/validate_deployment.py

echo "✅ 灾难恢复完成"
```

---

## 总结

恭喜！您已经完成了XLeRobot性能基准测试系统的部署。

### 关键要点回顾

1. **环境准备**: 确保满足系统要求，安装所有依赖
2. **安装部署**: 选择合适的安装方式（pip/源码/Docker/K8s）
3. **配置管理**: 使用YAML配置文件管理所有设置
4. **验证部署**: 运行验证脚本确保部署成功
5. **监控告警**: 配置Prometheus、Grafana和告警系统
6. **维护更新**: 建立定期备份和更新流程

### 后续建议

- 📊 **持续监控**: 设置定期健康检查
- 🔄 **自动化更新**: 使用CI/CD流水线自动更新
- 📈 **性能优化**: 根据使用情况调整配置
- 🛡️ **安全加固**: 实施安全最佳实践
- 📚 **文档维护**: 保持文档与实际部署同步

### 获取支持

如有问题，请参考：
- [故障排除](#故障排除)部分
- 项目仓库的Issues页面
- 联系技术支持团队

祝您部署顺利！🎉

---

*本文档遵循XLeRobot项目部署标准*
*最后更新: 2025-10-29*
