# Docker环境使用指南

本文档详细介绍如何使用XLeRobot NPU Converter的Docker开发环境。

## 📋 前提条件

- Docker 20.04 或更高版本
- docker-compose 1.29 或更高版本
- 至少 4GB 可用内存
- 至少 5GB 可用磁盘空间

## 🚀 快速开始

### 1. 一键构建和验证

```bash
# 运行自动化构建脚本
./scripts/build.sh
```

这个脚本将：
- 检查Docker环境
- 构建Docker镜像
- 验证镜像大小 (<5GB)
- 运行容器验证测试
- 显示使用说明

### 2. 手动构建步骤

如果您想手动控制构建过程：

```bash
# 1. 构建镜像
docker build -t xlerobot-npu-converter .

# 2. 验证镜像大小
docker images xlerobot-npu-converter

# 3. 运行容器验证
docker run --rm xlerobot-npu-converter python --version
```

## 🐳 容器使用方法

### 交互式开发

```bash
# 启动交互式shell
docker run -it --rm xlerobot-npu-converter bash

# 在容器内
npuuser@container:/app$ python --version
npuuser@container:/app$ pip list
npuuser@container:/app$ python -m pytest tests/
```

### 开发模式（挂载源代码）

```bash
# 挂载源代码目录进行开发
docker run -it --rm \
  -v $(pwd)/src:/app/src \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/tests:/app/tests \
  xlerobot-npu-converter bash
```

### 运行测试

```bash
# 在容器内运行测试
docker run --rm \
  -v $(pwd)/tests:/app/tests \
  xlerobot-npu-converter python -m pytest tests/ -v

# 生成覆盖率报告
docker run --rm \
  -v $(pwd)/tests:/app/tests \
  -v $(pwd)/htmlcov:/app/htmlcov \
  xlerobot-npu-converter python -m pytest tests/ --cov=src --cov-report=html
```

## 🛠️ Docker Compose使用

### 启动开发环境

```bash
# 启动服务（后台运行）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 进入容器
docker-compose exec npu-converter bash
```

### 停止环境

```bash
# 停止并删除容器
docker-compose down

# 停止但保留容器
docker-compose stop
```

### 运行测试服务

```bash
# 启动测试配置文件
docker-compose --profile testing up test-runner

# 或者直接运行测试
docker-compose run --rm test-runner
```

## 📁 卷挂载说明

### 源代码开发

```bash
# 完整的开发环境挂载
docker run -it --rm \
  -v $(pwd)/src:/app/src \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/docs:/app/docs \
  -v $(pwd)/tests:/app/tests \
  -v pip-cache:/root/.cache/pip \
  xlerobot-npu-converter bash
```

### 数据持久化

```bash
# 挂载数据目录
docker run -it --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  xlerobot-npu-converter python your_script.py
```

## 🔧 常用操作

### 镜像管理

```bash
# 查看镜像
docker images xlerobot-npu-converter

# 删除镜像
docker rmi xlerobot-npu-converter

# 重新构建（无缓存）
docker build --no-cache -t xlerobot-npu-converter .
```

### 容器管理

```bash
# 查看运行中的容器
docker ps

# 查看所有容器
docker ps -a

# 进入运行中的容器
docker exec -it <container_id> bash

# 复制文件到容器
docker cp local_file.txt <container_id>:/app/

# 从容器复制文件
docker cp <container_id>:/app/container_file.txt .
```

### 清理操作

```bash
# 清理停止的容器
docker container prune

# 清理未使用的镜像
docker image prune

# 清理所有未使用的资源
docker system prune -a

# 使用构建脚本清理
./scripts/build.sh clean
```

## 🧪 调试和故障排除

### 查看构建日志

```bash
# 详细构建日志
docker build --no-cache --progress=plain -t xlerobot-npu-converter .
```

### 容器内调试

```bash
# 启动调试模式
docker run -it --rm --entrypoint /bin/bash xlerobot-npu-converter

# 检查环境变量
docker run --rm xlerobot-npu-converter env

# 检查安装的包
docker run --rm xlerobot-npu-converter pip list
```

### 性能监控

```bash
# 查看容器资源使用
docker stats

# 查看容器详细信息
docker inspect <container_id>
```

## 📊 镜像优化说明

我们的Docker镜像经过以下优化：

1. **多阶段构建**: 减少最终镜像大小
2. **包缓存清理**: 删除不必要的包和缓存
3. **.dockerignore**: 排除不需要的文件
4. **层优化**: 合理组织Dockerfile层级

### 镜像大小控制

```bash
# 分析镜像大小
docker history xlerobot-npu-converter

# 查看镜像详细信息
docker inspect xlerobot-npu-converter
```

## 🔒 安全考虑

1. **非root用户**: 容器内使用npuuser (UID:1000)
2. **最小权限**: 只安装必要的包
3. **定期更新**: 定期更新基础镜像
4. **扫描漏洞**: 使用工具扫描镜像漏洞

## 📚 示例工作流

### 开发新功能

```bash
# 1. 启动开发环境
docker-compose up -d

# 2. 进入容器
docker-compose exec npu-converter bash

# 3. 在容器内开发
npuuser@container:/app$ cd src
npuuser@container:/app$ # 编辑代码
npuuser@container:/app$ python -m pytest

# 4. 退出容器
exit

# 5. 停止环境
docker-compose down
```

### 运行完整测试套件

```bash
# 使用docker-compose
docker-compose --profile testing up --abort-on-container-exit

# 或直接使用docker
docker run --rm \
  -v $(pwd)/tests:/app/tests \
  -v $(pwd)/htmlcov:/app/htmlcov \
  xlerobot-npu-converter \
  python -m pytest tests/ --cov=src --cov-report=html
```

### 批量处理

```bash
# 批量处理模型文件
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  xlerobot-npu-converter \
  python -m npu_converter batch --input /app/input --output /app/output
```

## 🆘 获取帮助

如果遇到问题：

1. 查看构建脚本帮助：`./scripts/build.sh help`
2. 检查Docker日志：`docker logs <container_id>`
3. 运行验证测试：`./scripts/build.sh validate`
4. 清理并重建：`./scripts/build.sh clean && ./scripts/build.sh`

---

*最后更新: 2025-10-25*