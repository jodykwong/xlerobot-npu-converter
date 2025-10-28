#!/bin/bash
# 健康检查脚本 - Health Check Script

echo "XLeRobot性能基准测试 - 系统健康检查"
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
