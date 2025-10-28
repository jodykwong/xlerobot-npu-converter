# XLeRobot NPU模型转换工具 - 生产环境部署指南

**文档版本**: 1.0
**最后更新**: 2025-10-27
**适用版本**: v1.0.0+

---

## 📋 概述

本指南提供XLeRobot NPU模型转换工具在生产环境中的完整部署方案，涵盖Docker容器化部署、配置管理、监控和故障排除。

### 生产环境特性

- **容器化部署** - 完全Docker化，支持Kubernetes和Docker Swarm
- **高可用性** - 支持负载均衡和故障转移
- **安全加固** - 完整的安全配置和访问控制
- **监控集成** - 实时监控、日志聚合和告警
- **版本管理** - 支持蓝绿部署和滚动更新

---

## 🚀 快速部署

### 1. 准备生产镜像

```bash
# 构建生产镜像
docker build -t xlerobot-npu-converter:v1.0.0 .

# 标记最新版本
docker tag xlerobot-npu-converter:v1.0.0 xlerobot-npu-converter:latest

# 推送到镜像仓库
docker push xlerobot-npu-converter:v1.0.0
docker push xlerobot-npu-converter:latest
```

### 2. 运行容器

```bash
# 单容器部署
docker run -d \
  --name xlerobot-converter \
  --restart unless-stopped \
  -p 8080:8080 \
  -v /data/models:/app/models \
  -v /data/output:/app/output \
  -v /data/logs:/app/logs \
  -e ENV=production \
  -e LOG_LEVEL=INFO \
  xlerobot-npu-converter:latest
```

---

## ⚙️ 生产配置

### Docker Compose 部署

创建 `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  xlerobot-converter:
    image: xlerobot-npu-converter:v1.0.0
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      - ENV=production
      - LOG_LEVEL=INFO
      - MAX_CONCURRENT_CONVERSIONS=4
      - MODEL_CACHE_SIZE=10
      - ENABLE_METRICS=true
    volumes:
      - /data/models:/app/models:ro
      - /data/output:/app/output
      - /data/logs:/app/logs
      - /data/config:/app/config
    networks:
      - converter-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  # 可选：日志收集
  fluentd:
    image: fluent/fluentd:v1.16-1
    volumes:
      - /data/logs:/fluentd/log
    networks:
      - converter-network

  # 可选：监控
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - converter-network

networks:
  converter-network:
    driver: bridge
```

### 环境变量配置

| 变量名 | 默认值 | 说明 | 安全性 |
|--------|--------|------|--------|
| `ENV` | development | 运行环境 (production/staging) | - |
| `LOG_LEVEL` | INFO | 日志级别 (DEBUG/INFO/WARN/ERROR) | - |
| `MAX_CONCURRENT_CONVERSIONS` | 2 | 最大并发转换数 | - |
| `MODEL_CACHE_SIZE` | 5 | 模型缓存大小 | - |
| `ENABLE_METRICS` | false | 启用性能指标 | - |
| `METRICS_PORT` | 9090 | 指标端口 | - |
| `MODEL_STORAGE_PATH` | /app/models | 模型存储路径 | - |
| `OUTPUT_STORAGE_PATH` | /app/output | 输出存储路径 | - |
| `DB_URL` | - | 数据库连接字符串 | 🔒 敏感 |
| `REDIS_URL` | - | Redis连接字符串 | 🔒 敏感 |
| `API_KEY` | - | API访问密钥 | 🔒 敏感 |
| `JWT_SECRET` | - | JWT签名密钥 | 🔒 敏感 |

### 配置文件示例

创建 `config/production.yaml`:

```yaml
# 生产环境配置
environment: production

# 日志配置
logging:
  level: INFO
  format: json
  output: /app/logs/app.log
  max_size: 100MB
  max_files: 10

# 转换配置
conversion:
  max_concurrent: 4
  model_cache_size: 10
  temp_dir: /tmp/xlerobot
  cleanup_after: 3600  # 秒

# 性能配置
performance:
  enable_metrics: true
  metrics_port: 9090
  profile_mode: false

# 安全配置
security:
  api_key_required: true
  rate_limit: 100  # 每分钟请求数
  cors_origins:
    - "https://api.example.com"
    - "https://app.example.com"

# Horizon X5 配置
horizon_x5:
  toolchain_path: /opt/horizon
  temp_dir: /tmp/horizon
  cleanup_after: 7200

# 模型配置
models:
  default_type: sensevoice
  supported_types:
    - sensevoice
    - vits_cantonese
    - piper_vits
  validation:
    max_model_size: 500MB
    allowed_formats:
      - onnx

# 存储配置
storage:
  models_dir: /app/models
  output_dir: /app/output
  temp_dir: /tmp/xlerobot
  cleanup_interval: 86400  # 24小时

# 监控配置
monitoring:
  enable_health_check: true
  health_check_interval: 30
  enable_performance_metrics: true
  enable_error_tracking: true
```

---

## 🔒 安全配置

### 1. 容器安全

```dockerfile
# Dockerfile 中的安全配置
FROM ubuntu:20.04

# 创建非root用户
RUN groupadd -r xlerobot && useradd -r -g xlerobot xlerobot

# 设置工作目录
WORKDIR /app

# 复制应用文件
COPY --chown=xlerobot:xlerobot . .

# 切换到非root用户
USER xlerobot

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

CMD ["xlerobot-converter"]
```

### 2. 网络安全

```yaml
# docker-compose.prod.yml 中的安全配置
services:
  xlerobot-converter:
    # 仅暴露必要端口
    ports:
      - "127.0.0.1:8080:8080"  # 仅本地访问

    # 安全选项
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp:noexec,nosuid,size=100m

    # 资源限制
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

### 3. 访问控制

```bash
# 使用API密钥验证
export API_KEY="your-secure-api-key-here"

# 运行容器
docker run -d \
  -e API_KEY=${API_KEY} \
  xlerobot-npu-converter:latest

# 使用JWT令牌
export JWT_SECRET="your-jwt-secret-here"
```

### 4. SSL/TLS 配置

```yaml
# 使用Nginx反向代理
nginx:
  image: nginx:alpine
  ports:
    - "443:443"
    - "80:80"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
    - ./ssl:/etc/ssl/certs
  depends_on:
    - xlerobot-converter
```

Nginx配置 (`nginx.conf`):

```nginx
events {
    worker_connections 1024;
}

http {
    upstream xlerobot {
        server xlerobot-converter:8080;
    }

    server {
        listen 443 ssl http2;
        server_name api.xlerobot.com;

        ssl_certificate /etc/ssl/certs/server.crt;
        ssl_certificate_key /etc/ssl/private/server.key;

        # 安全头
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        location / {
            proxy_pass http://xlerobot;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

---

## 📊 监控和日志

### 1. 日志配置

```yaml
# logging.yaml
version: 1
formatters:
  detailed:
    format: '%(asctime)s %(name)s %(levelname)s %(message)s'
  json:
    format: '{"time": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: json
    stream: ext://sys.stdout

  file:
    class: logging.handlers.RotatingFileHandler
    level: INFO
    formatter: detailed
    filename: /app/logs/app.log
    maxBytes: 104857600  # 100MB
    backupCount: 10

  error_file:
    class: logging.handlers.RotatingFileHandler
    level: ERROR
    formatter: json
    filename: /app/logs/error.log
    maxBytes: 104857600  # 100MB
    backupCount: 10

loggers:
  npu_converter:
    level: INFO
    handlers: [console, file, error_file]
    propagate: false

root:
  level: INFO
  handlers: [console, file]
```

### 2. 性能监控

```python
# 监控中间件示例
from prometheus_client import Counter, Histogram, generate_latest

# 指标定义
CONVERSION_REQUESTS = Counter('conversion_requests_total', 'Total conversion requests', ['model_type', 'status'])
CONVERSION_DURATION = Histogram('conversion_duration_seconds', 'Conversion duration')
MODEL_LOAD_TIME = Histogram('model_load_time_seconds', 'Model load time')

# 在转换代码中使用
@CONVERSION_DURATION.time()
def convert_model(model_path):
    # 转换逻辑
    pass
```

### 3. 健康检查

```python
# health_check.py
from flask import Flask, jsonify
import psutil
import requests

app = Flask(__name__)

@app.route('/health')
def health_check():
    """健康检查端点"""
    try:
        # 检查磁盘空间
        disk_usage = psutil.disk_usage('/')
        if disk_usage.percent > 90:
            return jsonify(status='unhealthy', reason='Disk usage > 90%'), 503

        # 检查内存使用
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            return jsonify(status='unhealthy', reason='Memory usage > 90%'), 503

        # 检查Horizon X5工具链
        horizon_status = check_horizon_toolchain()
        if not horizon_status:
            return jsonify(status='unhealthy', reason='Horizon toolchain not available'), 503

        return jsonify(status='healthy', version='1.0.0')

    except Exception as e:
        return jsonify(status='error', error=str(e)), 500

def check_horizon_toolchain():
    """检查Horizon X5工具链可用性"""
    try:
        result = subprocess.run(['hrt_model_exec', '--help'],
                              capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False
```

### 4. Prometheus 监控

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'xlerobot-converter'
    static_configs:
      - targets: ['xlerobot-converter:9090']
    metrics_path: /metrics
    scrape_interval: 5s
```

---

## 🔧 Kubernetes 部署

### 1. Deployment 配置

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: xlerobot-converter
  labels:
    app: xlerobot-converter
spec:
  replicas: 3
  selector:
    matchLabels:
      app: xlerobot-converter
  template:
    metadata:
      labels:
        app: xlerobot-converter
    spec:
      containers:
      - name: xlerobot-converter
        image: xlerobot-npu-converter:v1.0.0
        ports:
        - containerPort: 8080
        env:
        - name: ENV
          value: "production"
        - name: LOG_LEVEL
          value: "INFO"
        - name: MAX_CONCURRENT_CONVERSIONS
          value: "4"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
        volumeMounts:
        - name: models-volume
          mountPath: /app/models
        - name: output-volume
          mountPath: /app/output
        - name: logs-volume
          mountPath: /app/logs
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
      volumes:
      - name: models-volume
        persistentVolumeClaim:
          claimName: xlerobot-models-pvc
      - name: output-volume
        persistentVolumeClaim:
          claimName: xlerobot-output-pvc
      - name: logs-volume
        persistentVolumeClaim:
          claimName: xlerobot-logs-pvc
```

### 2. Service 配置

```yaml
# k8s-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: xlerobot-converter-service
spec:
  selector:
    app: xlerobot-converter
  ports:
  - name: http
    port: 80
    targetPort: 8080
  type: ClusterIP

---
apiVersion: v1
kind: Service
metadata:
  name: xlerobot-converter-metrics
spec:
  selector:
    app: xlerobot-converter
  ports:
  - name: metrics
    port: 9090
    targetPort: 9090
  type: ClusterIP
```

### 3. Ingress 配置

```yaml
# k8s-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: xlerobot-converter-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - api.xlerobot.com
    secretName: xlerobot-tls-secret
  rules:
  - host: api.xlerobot.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: xlerobot-converter-service
            port:
              number: 80
```

---

## 📦 升级和回滚

### 1. 蓝绿部署

```bash
#!/bin/bash
# blue-green-deploy.sh

# 部署新版本到绿环境
docker-compose -f docker-compose.prod.yml -f docker-compose.green.yml up -d --scale xlerobot-converter=0

# 运行健康检查
sleep 30
if curl -f http://localhost:8080/health; then
    echo "Green environment is healthy"

    # 切换流量到绿环境
    docker-compose -f docker-compose.prod.yml exec haproxy pkill haproxy
    # 更新HAProxy配置指向绿环境

    # 停止蓝环境
    docker-compose -f docker-compose.blue.yml down
    echo "Deployment successful"
else
    echo "Health check failed, rolling back"
    # 停止绿环境
    docker-compose -f docker-compose.green.yml down
    exit 1
fi
```

### 2. 滚动更新

```bash
# Kubernetes 滚动更新
kubectl set image deployment/xlerobot-converter xlerobot-converter=xlerobot-npu-converter:v1.1.0

# 检查更新状态
kubectl rollout status deployment/xlerobot-converter

# 回滚到上一版本
kubectl rollout undo deployment/xlerobot-converter
```

---

## 🐛 故障排除

### 1. 常见问题

#### 问题1: 容器启动失败

```bash
# 检查容器日志
docker logs xlerobot-converter

# 检查资源使用
docker stats xlerobot-converter

# 进入容器调试
docker exec -it xlerobot-converter bash
```

#### 问题2: Horizon X5 工具链不可用

```bash
# 检查工具链安装
docker exec xlerobot-converter which hrt_model_exec
docker exec xlerobot-converter hrt_model_exec --help

# 重新安装工具链
docker exec xlerobot-converter /opt/horizon/install.sh
```

#### 问题3: 模型转换失败

```bash
# 检查模型文件
docker exec xlerobot-converter ls -la /app/models/

# 检查输出目录权限
docker exec xlerobot-converter ls -la /app/output/

# 启用详细日志
docker exec xlerobot-converter ENV=DEBUG xlerobot convert -i model.onnx -o output.bpu --verbose
```

### 2. 日志分析

```bash
# 实时查看日志
tail -f /data/logs/app.log

# 分析错误日志
grep ERROR /data/logs/app.log | tail -20

# 统计错误类型
grep ERROR /data/logs/app.log | awk '{print $5}' | sort | uniq -c | sort -nr
```

### 3. 性能调优

```bash
# 检查CPU和内存使用
docker exec xlerobot-converter top
docker exec xlerobot-converter free -h

# 分析转换性能
docker exec xlerobot-converter cat /app/logs/performance.log
```

---

## 📝 运维清单

### 日常检查

- [ ] 检查容器健康状态
- [ ] 监控磁盘空间使用
- [ ] 检查日志中的错误
- [ ] 验证API响应时间
- [ ] 检查模型缓存命中率

### 定期维护

- [ ] 每周：清理过期日志文件
- [ ] 每周：检查容器镜像更新
- [ ] 每月：性能指标分析
- [ ] 每季度：安全补丁更新
- [ ] 每季度：容量规划审查

### 备份策略

```bash
# 每日备份配置和模型
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf /backup/config-$DATE.tar.gz /data/config/
tar -czf /backup/models-$DATE.tar.gz /data/models/

# 清理30天前的备份
find /backup/ -name "*.tar.gz" -mtime +30 -delete
```

---

## 📞 支持和联系

### 获取帮助

- **文档**: https://docs.xlerobot.com
- **问题跟踪**: https://github.com/xlerobot/xlerobot/issues
- **技术支持**: support@xlerobot.com
- **社区论坛**: https://community.xlerobot.com

### 紧急联系

- **24/7热线**: +1-800-XLEROBOT
- **紧急邮箱**: emergency@xlerobot.com
- **Slack频道**: #xlerobot-support

---

*最后更新: 2025-10-27*
*文档维护者: XLeRobot Team*
*版本: v1.0.0*
