"""
指标采集器 (Metrics Collector)

负责采集系统性能指标，支持多种数据源和格式，
提供实时和批量采集功能，进行数据清洗和格式化。

作者: BMAD Method
创建日期: 2025-10-29
版本: v1.0
"""

import time
import psutil
import logging
import threading
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
from queue import Queue, Empty
import yaml

# 可选依赖 - GPU监控
try:
    import GPUtil
    GPU_MONITORING_AVAILABLE = True
except ImportError:
    GPU_MONITORING_AVAILABLE = False
    logging.warning("GPUtil not available, GPU monitoring disabled")

try:
    import pynvml
    NVIDIA_MONITORING_AVAILABLE = True
except ImportError:
    NVIDIA_MONITORING_AVAILABLE = False
    logging.warning("pynvml not available, NVIDIA GPU monitoring disabled")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class MetricsConfig:
    """指标采集配置"""
    collection_interval: int = 1  # 采集间隔（秒）
    buffer_size: int = 1000  # 缓冲区大小
    enable_gpu_monitoring: bool = True  # 启用GPU监控
    enable_npu_monitoring: bool = True  # 启用NPU监控
    enable_disk_io: bool = True  # 启用磁盘I/O监控
    enable_network_io: bool = True  # 启用网络I/O监控
    max_history_size: int = 10000  # 最大历史数据量
    storage_type: str = "memory"  # 存储类型: memory, sqlite
    storage_path: str = "data/metrics.db"  # 存储路径
    realtime_callback: Optional[Callable] = None  # 实时回调函数


@dataclass
class SystemMetrics:
    """系统指标"""
    timestamp: datetime
    cpu_percent: float
    cpu_count: int
    load_average: List[float]
    memory_total: int
    memory_used: int
    memory_free: int
    memory_percent: float
    disk_usage: Dict[str, Any]
    network_io: Dict[str, Any]
    process_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'cpu_percent': self.cpu_percent,
            'cpu_count': self.cpu_count,
            'load_average': self.load_average,
            'memory_total': self.memory_total,
            'memory_used': self.memory_used,
            'memory_free': self.memory_free,
            'memory_percent': self.memory_percent,
            'disk_usage': self.disk_usage,
            'network_io': self.network_io,
            'process_count': self.process_count
        }


@dataclass
class GPUMetrics:
    """GPU指标"""
    timestamp: datetime
    gpu_id: int
    name: str
    utilization_gpu: float
    utilization_memory: float
    memory_used: int
    memory_total: int
    temperature: Optional[float] = None
    power_draw: Optional[float] = None
    fan_speed: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'gpu_id': self.gpu_id,
            'name': self.name,
            'utilization_gpu': self.utilization_gpu,
            'utilization_memory': self.utilization_memory,
            'memory_used': self.memory_used,
            'memory_total': self.memory_total,
            'temperature': self.temperature,
            'power_draw': self.power_draw,
            'fan_speed': self.fan_speed
        }


@dataclass
class NPUMetrics:
    """NPU指标"""
    timestamp: datetime
    npu_id: int
    name: str
    utilization: float
    memory_used: int
    memory_total: int
    temperature: Optional[float] = None
    power_draw: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'npu_id': self.npu_id,
            'name': self.name,
            'utilization': self.utilization,
            'memory_used': self.memory_used,
            'memory_total': self.memory_total,
            'temperature': self.temperature,
            'power_draw': self.power_draw
        }


@dataclass
class ConversionMetrics:
    """转换性能指标"""
    timestamp: datetime
    model_type: str
    model_name: str
    throughput: float  # 模型/分钟
    latency_p50: float
    latency_p95: float
    latency_p99: float
    success_rate: float
    error_count: int
    total_models: int
    completed_models: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'model_type': self.model_type,
            'model_name': self.model_name,
            'throughput': self.throughput,
            'latency_p50': self.latency_p50,
            'latency_p95': self.latency_p95,
            'latency_p99': self.latency_p99,
            'success_rate': self.success_rate,
            'error_count': self.error_count,
            'total_models': self.total_models,
            'completed_models': self.completed_models
        }


class MetricsBuffer:
    """指标缓冲区"""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._buffer: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

    def add(self, metric: Dict[str, Any]):
        """添加指标到缓冲区"""
        with self._lock:
            self._buffer.append(metric)
            if len(self._buffer) > self.max_size:
                self._buffer.pop(0)

    def get_all(self) -> List[Dict[str, Any]]:
        """获取所有指标"""
        with self._lock:
            return self._buffer.copy()

    def clear(self):
        """清空缓冲区"""
        with self._lock:
            self._buffer.clear()

    def size(self) -> int:
        """获取缓冲区大小"""
        with self._lock:
            return len(self._buffer)


class MetricsCollector:
    """
    指标采集器

    负责采集系统性能指标，支持多种数据源，
    提供实时和批量采集，数据清洗和格式化。
    """

    def __init__(self, config: MetricsConfig):
        """
        初始化指标采集器

        Args:
            config: 指标采集配置
        """
        self.config = config
        self.metrics_buffer = MetricsBuffer(max_size=config.buffer_size)
        self._stop_event = threading.Event()
        self._collection_thread: Optional[threading.Thread] = None
        self._storage_lock = threading.Lock()

        # 初始化存储
        if config.storage_type == "sqlite":
            self._init_sqlite_storage()

        # 初始化NVIDIA监控
        if NVIDIA_MONITORING_AVAILABLE and config.enable_gpu_monitoring:
            try:
                pynvml.nvmlInit()
                logger.info("NVIDIA GPU monitoring initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize NVIDIA monitoring: {e}")

        logger.info(f"Metrics Collector initialized with config: {asdict(config)}")

    def _init_sqlite_storage(self):
        """初始化SQLite存储"""
        storage_path = Path(self.config.storage_path)
        storage_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(str(storage_path), check_same_thread=False)

        # 创建表
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                cpu_percent REAL,
                cpu_count INTEGER,
                load_average TEXT,
                memory_total INTEGER,
                memory_used INTEGER,
                memory_free INTEGER,
                memory_percent REAL,
                disk_usage TEXT,
                network_io TEXT,
                process_count INTEGER
            )
        ''')

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS gpu_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                gpu_id INTEGER,
                name TEXT,
                utilization_gpu REAL,
                utilization_memory REAL,
                memory_used INTEGER,
                memory_total INTEGER,
                temperature REAL,
                power_draw REAL,
                fan_speed REAL
            )
        ''')

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS npu_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                npu_id INTEGER,
                name TEXT,
                utilization REAL,
                memory_used INTEGER,
                memory_total INTEGER,
                temperature REAL,
                power_draw REAL
            )
        ''')

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS conversion_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                model_type TEXT,
                model_name TEXT,
                throughput REAL,
                latency_p50 REAL,
                latency_p95 REAL,
                latency_p99 REAL,
                success_rate REAL,
                error_count INTEGER,
                total_models INTEGER,
                completed_models INTEGER
            )
        ''')

        self.conn.commit()
        logger.info(f"SQLite storage initialized: {storage_path}")

    def collect_system_metrics(self) -> SystemMetrics:
        """
        采集系统指标

        Returns:
            SystemMetrics: 系统指标
        """
        timestamp = datetime.now()

        # CPU指标
        cpu_percent = psutil.cpu_percent(interval=None)
        cpu_count = psutil.cpu_count()
        try:
            load_average = list(psutil.getloadavg())
        except AttributeError:
            load_average = [0.0, 0.0, 0.0]  # Windows系统不支持

        # 内存指标
        memory = psutil.virtual_memory()
        memory_total = memory.total
        memory_used = memory.used
        memory_free = memory.free
        memory_percent = memory.percent

        # 磁盘使用情况
        disk_usage = {}
        if self.config.enable_disk_io:
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.mountpoint] = {
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': (usage.used / usage.total) * 100
                    }
                except PermissionError:
                    continue

        # 网络I/O
        network_io = {}
        if self.config.enable_network_io:
            network = psutil.net_io_counters()
            network_io = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }

        # 进程数量
        process_count = len(psutil.pids())

        metrics = SystemMetrics(
            timestamp=timestamp,
            cpu_percent=cpu_percent,
            cpu_count=cpu_count,
            load_average=load_average,
            memory_total=memory_total,
            memory_used=memory_used,
            memory_free=memory_free,
            memory_percent=memory_percent,
            disk_usage=disk_usage,
            network_io=network_io,
            process_count=process_count
        )

        # 保存指标
        self._save_system_metrics(metrics)

        return metrics

    def collect_gpu_metrics(self) -> List[GPUMetrics]:
        """
        采集GPU指标

        Returns:
            List[GPUMetrics]: GPU指标列表
        """
        if not self.config.enable_gpu_monitoring:
            return []

        metrics_list = []

        # 使用GPUtil采集GPU指标
        if GPU_MONITORING_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                for gpu in gpus:
                    metrics = GPUMetrics(
                        timestamp=datetime.now(),
                        gpu_id=gpu.id,
                        name=gpu.name,
                        utilization_gpu=gpu.load * 100,
                        utilization_memory=gpu.memoryUtil * 100,
                        memory_used=gpu.memoryUsed,
                        memory_total=gpu.memoryTotal,
                        temperature=gpu.temperature
                    )
                    metrics_list.append(metrics)

                    # 保存指标
                    self._save_gpu_metrics(metrics)

            except Exception as e:
                logger.error(f"Error collecting GPU metrics: {e}")

        # 使用pynvml采集NVIDIA GPU指标
        if NVIDIA_MONITORING_AVAILABLE:
            try:
                device_count = pynvml.nvmlDeviceGetCount()
                for i in range(device_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')

                    # GPU利用率
                    utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)

                    # 温度和功耗
                    try:
                        temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                    except pynvml.NVMLError:
                        temperature = None

                    try:
                        power_draw = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # 转换为瓦特
                    except pynvml.NVMLError:
                        power_draw = None

                    metrics = GPUMetrics(
                        timestamp=datetime.now(),
                        gpu_id=i,
                        name=name,
                        utilization_gpu=utilization.gpu,
                        utilization_memory=utilization.memory,
                        memory_used=memory_info.used,
                        memory_total=memory_info.total,
                        temperature=temperature,
                        power_draw=power_draw
                    )
                    metrics_list.append(metrics)

                    # 保存指标
                    self._save_gpu_metrics(metrics)

            except Exception as e:
                logger.error(f"Error collecting NVIDIA GPU metrics: {e}")

        return metrics_list

    def collect_npu_metrics(self) -> List[NPUMetrics]:
        """
        采集NPU指标

        Returns:
            List[NPUMetrics]: NPU指标列表
        """
        if not self.config.enable_npu_monitoring:
            return []

        # 注意: NPU监控需要特定的硬件和驱动
        # 这里提供接口，实际实现需要根据硬件厂商的API

        metrics_list = []
        # 示例实现 - 实际需要根据NPU硬件厂商的API实现
        # 例如: 华为昇腾、英特尔NPU等

        logger.debug("NPU metrics collection not implemented (requires vendor-specific API)")
        return metrics_list

    def collect_conversion_metrics(self, model_type: str,
                                  model_name: str) -> ConversionMetrics:
        """
        采集转换性能指标

        Args:
            model_type: 模型类型
            model_name: 模型名称

        Returns:
            ConversionMetrics: 转换性能指标
        """
        # 注意: 这里需要与NPU转换引擎集成
        # 示例实现

        timestamp = datetime.now()

        # 从转换引擎获取指标（示例数据）
        metrics = ConversionMetrics(
            timestamp=timestamp,
            model_type=model_type,
            model_name=model_name,
            throughput=12.5,  # 模型/分钟
            latency_p50=15.2,  # 秒
            latency_p95=28.5,  # 秒
            latency_p99=45.8,  # 秒
            success_rate=100.0,  # 百分比
            error_count=0,
            total_models=10,
            completed_models=10
        )

        # 保存指标
        self._save_conversion_metrics(metrics)

        return metrics

    def start_real_time_collection(self, interval: Optional[int] = None):
        """
        开始实时采集

        Args:
            interval: 采集间隔（秒），默认为配置中的值
        """
        if self._collection_thread and self._collection_thread.is_alive():
            logger.warning("Real-time collection is already running")
            return

        if interval is None:
            interval = self.config.collection_interval

        self._stop_event.clear()
        self._collection_thread = threading.Thread(
            target=self._collection_loop,
            args=(interval,),
            daemon=True
        )
        self._collection_thread.start()

        logger.info(f"Real-time collection started (interval={interval}s)")

    def stop_real_time_collection(self):
        """停止实时采集"""
        if not self._collection_thread or not self._collection_thread.is_alive():
            logger.warning("Real-time collection is not running")
            return

        self._stop_event.set()
        self._collection_thread.join(timeout=5)

        logger.info("Real-time collection stopped")

    def _collection_loop(self, interval: int):
        """
        实时采集循环

        Args:
            interval: 采集间隔（秒）
        """
        logger.info(f"Starting collection loop (interval={interval}s)")

        while not self._stop_event.is_set():
            try:
                # 采集系统指标
                system_metrics = self.collect_system_metrics()
                self._add_to_buffer('system', system_metrics.to_dict())

                # 采集GPU指标
                gpu_metrics = self.collect_gpu_metrics()
                for metric in gpu_metrics:
                    self._add_to_buffer('gpu', metric.to_dict())

                # 采集NPU指标
                npu_metrics = self.collect_npu_metrics()
                for metric in npu_metrics:
                    self._add_to_buffer('npu', metric.to_dict())

                # 回调通知
                if self.config.realtime_callback:
                    self.config.realtime_callback({
                        'system': system_metrics.to_dict(),
                        'gpu': [m.to_dict() for m in gpu_metrics],
                        'npu': [m.to_dict() for m in npu_metrics]
                    })

                # 等待指定间隔
                self._stop_event.wait(timeout=interval)

            except Exception as e:
                logger.error(f"Error in collection loop: {e}")
                time.sleep(1)  # 出错时短暂等待

    def _add_to_buffer(self, metric_type: str, data: Dict[str, Any]):
        """
        添加指标到缓冲区

        Args:
            metric_type: 指标类型
            data: 指标数据
        """
        self.metrics_buffer.add({
            'type': metric_type,
            'data': data
        })

    def _save_system_metrics(self, metrics: SystemMetrics):
        """保存系统指标"""
        if self.config.storage_type == "memory":
            return

        with self._storage_lock:
            self.conn.execute(
                '''INSERT INTO system_metrics (
                    timestamp, cpu_percent, cpu_count, load_average,
                    memory_total, memory_used, memory_free, memory_percent,
                    disk_usage, network_io, process_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    metrics.timestamp.isoformat(),
                    metrics.cpu_percent,
                    metrics.cpu_count,
                    json.dumps(metrics.load_average),
                    metrics.memory_total,
                    metrics.memory_used,
                    metrics.memory_free,
                    metrics.memory_percent,
                    json.dumps(metrics.disk_usage),
                    json.dumps(metrics.network_io),
                    metrics.process_count
                )
            )
            self.conn.commit()

    def _save_gpu_metrics(self, metrics: GPUMetrics):
        """保存GPU指标"""
        if self.config.storage_type == "memory":
            return

        with self._storage_lock:
            self.conn.execute(
                '''INSERT INTO gpu_metrics (
                    timestamp, gpu_id, name, utilization_gpu,
                    utilization_memory, memory_used, memory_total,
                    temperature, power_draw, fan_speed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    metrics.timestamp.isoformat(),
                    metrics.gpu_id,
                    metrics.name,
                    metrics.utilization_gpu,
                    metrics.utilization_memory,
                    metrics.memory_used,
                    metrics.memory_total,
                    metrics.temperature,
                    metrics.power_draw,
                    metrics.fan_speed
                )
            )
            self.conn.commit()

    def _save_npu_metrics(self, metrics: NPUMetrics):
        """保存NPU指标"""
        if self.config.storage_type == "memory":
            return

        with self._storage_lock:
            self.conn.execute(
                '''INSERT INTO npu_metrics (
                    timestamp, npu_id, name, utilization,
                    memory_used, memory_total, temperature, power_draw
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    metrics.timestamp.isoformat(),
                    metrics.npu_id,
                    metrics.name,
                    metrics.utilization,
                    metrics.memory_used,
                    metrics.memory_total,
                    metrics.temperature,
                    metrics.power_draw
                )
            )
            self.conn.commit()

    def _save_conversion_metrics(self, metrics: ConversionMetrics):
        """保存转换指标"""
        if self.config.storage_type == "memory":
            return

        with self._storage_lock:
            self.conn.execute(
                '''INSERT INTO conversion_metrics (
                    timestamp, model_type, model_name, throughput,
                    latency_p50, latency_p95, latency_p99, success_rate,
                    error_count, total_models, completed_models
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    metrics.timestamp.isoformat(),
                    metrics.model_type,
                    metrics.model_name,
                    metrics.throughput,
                    metrics.latency_p50,
                    metrics.latency_p95,
                    metrics.latency_p99,
                    metrics.success_rate,
                    metrics.error_count,
                    metrics.total_models,
                    metrics.completed_models
                )
            )
            self.conn.commit()

    def get_recent_metrics(self, metric_type: str, count: int = 100) -> List[Dict[str, Any]]:
        """
        获取最近的指标

        Args:
            metric_type: 指标类型
            count: 获取数量

        Returns:
            List[Dict]: 指标列表
        """
        if self.config.storage_type == "memory":
            buffer_data = self.metrics_buffer.get_all()
            filtered = [item for item in buffer_data if item['type'] == metric_type]
            return filtered[-count:]

        # SQLite查询
        table_map = {
            'system': 'system_metrics',
            'gpu': 'gpu_metrics',
            'npu': 'npu_metrics',
            'conversion': 'conversion_metrics'
        }

        table_name = table_map.get(metric_type)
        if not table_name:
            return []

        with self._storage_lock:
            cursor = self.conn.execute(
                f'SELECT * FROM {table_name} ORDER BY id DESC LIMIT ?',
                (count,)
            )
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in reversed(rows)]

    def export_metrics(self, metric_type: str, output_file: str,
                      start_time: Optional[datetime] = None,
                      end_time: Optional[datetime] = None):
        """
        导出指标到文件

        Args:
            metric_type: 指标类型
            output_file: 输出文件路径
            start_time: 开始时间
            end_time: 结束时间
        """
        metrics = self.get_recent_metrics(metric_type, count=self.config.max_history_size)

        if start_time:
            metrics = [m for m in metrics if datetime.fromisoformat(m['timestamp']) >= start_time]

        if end_time:
            metrics = [m for m in metrics if datetime.fromisoformat(m['timestamp']) <= end_time]

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)

        logger.info(f"Exported {len(metrics)} {metric_type} metrics to {output_file}")

    def clear_metrics(self, metric_type: Optional[str] = None):
        """
        清空指标数据

        Args:
            metric_type: 指标类型，None表示清空所有
        """
        if self.config.storage_type == "memory":
            self.metrics_buffer.clear()
            logger.info("Metrics buffer cleared")
            return

        table_map = {
            'system': 'system_metrics',
            'gpu': 'gpu_metrics',
            'npu': 'npu_metrics',
            'conversion': 'conversion_metrics'
        }

        if metric_type:
            table_name = table_map.get(metric_type)
            if table_name:
                with self._storage_lock:
                    self.conn.execute(f'DELETE FROM {table_name}')
                    self.conn.commit()
                logger.info(f"Cleared {metric_type} metrics")
        else:
            with self._storage_lock:
                for table_name in table_map.values():
                    self.conn.execute(f'DELETE FROM {table_name}')
                self.conn.commit()
            logger.info("All metrics cleared")

    def get_statistics(self, metric_type: str,
                      metric_name: str,
                      hours: int = 1) -> Dict[str, float]:
        """
        获取指标统计信息

        Args:
            metric_type: 指标类型
            metric_name: 指标名称
            hours: 统计时间范围（小时）

        Returns:
            Dict: 统计信息 {min, max, avg, count}
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)

        metrics = self.get_recent_metrics(metric_type, count=10000)

        # 过滤时间范围
        filtered = []
        for m in metrics:
            try:
                ts = datetime.fromisoformat(m['timestamp'])
                if start_time <= ts <= end_time:
                    filtered.append(m)
            except Exception:
                continue

        # 获取数值
        values = []
        for m in filtered:
            value = m.get(metric_name)
            if isinstance(value, (int, float)):
                values.append(value)

        if not values:
            return {'min': 0, 'max': 0, 'avg': 0, 'count': 0}

        return {
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'count': len(values)
        }

    def close(self):
        """关闭采集器"""
        self.stop_real_time_collection()

        if self.config.storage_type == "sqlite":
            self.conn.close()
            logger.info("SQLite connection closed")

        if NVIDIA_MONITORING_AVAILABLE:
            try:
                pynvml.nvmlShutdown()
                logger.info("NVIDIA monitoring shutdown")
            except Exception as e:
                logger.warning(f"Error shutting down NVIDIA monitoring: {e}")

        logger.info("Metrics Collector closed")


if __name__ == "__main__":
    # 示例使用
    config = MetricsConfig(
        collection_interval=1,
        buffer_size=1000,
        enable_gpu_monitoring=True,
        enable_npu_monitoring=True,
        storage_type="memory"
    )

    collector = MetricsCollector(config)

    # 采集一次指标
    system_metrics = collector.collect_system_metrics()
    print(f"System metrics: {system_metrics.to_dict()}")

    gpu_metrics = collector.collect_gpu_metrics()
    print(f"GPU metrics: {[m.to_dict() for m in gpu_metrics]}")

    # 开始实时采集
    def on_metrics_update(data):
        print(f"Real-time metrics: {len(data)} types")

    config.realtime_callback = on_metrics_update
    collector.start_real_time_collection()

    time.sleep(5)

    collector.stop_real_time_collection()
    collector.close()
