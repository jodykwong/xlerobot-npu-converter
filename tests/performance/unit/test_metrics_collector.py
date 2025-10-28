"""
指标采集器单元测试

测试MetricsCollector类的所有功能，包括系统指标采集、
GPU监控、数据存储等功能。

作者: BMAD Method
创建日期: 2025-10-29
版本: v1.0
"""

import pytest
import tempfile
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
import sys
import threading

# 添加源码路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'src'))

from npu_converter.performance.metrics_collector import (
    MetricsCollector,
    MetricsConfig,
    SystemMetrics,
    GPUMetrics,
    NPUMetrics,
    ConversionMetrics,
    MetricsBuffer
)


class TestMetricsConfig:
    """测试MetricsConfig配置类"""

    def test_default_config(self):
        """测试默认配置"""
        config = MetricsConfig()
        assert config.collection_interval == 1
        assert config.buffer_size == 1000
        assert config.enable_gpu_monitoring is True
        assert config.enable_npu_monitoring is True
        assert config.enable_disk_io is True
        assert config.enable_network_io is True
        assert config.max_history_size == 10000
        assert config.storage_type == "memory"
        assert config.storage_path == "data/metrics.db"
        assert config.realtime_callback is None

    def test_custom_config(self):
        """测试自定义配置"""
        def dummy_callback(data):
            pass

        config = MetricsConfig(
            collection_interval=5,
            buffer_size=2000,
            enable_gpu_monitoring=False,
            storage_type="sqlite",
            storage_path="/tmp/test.db",
            realtime_callback=dummy_callback
        )
        assert config.collection_interval == 5
        assert config.buffer_size == 2000
        assert config.enable_gpu_monitoring is False
        assert config.storage_type == "sqlite"
        assert config.storage_path == "/tmp/test.db"
        assert config.realtime_callback == dummy_callback


class TestMetricsBuffer:
    """测试MetricsBuffer缓冲区类"""

    def test_init_buffer(self):
        """测试初始化缓冲区"""
        buffer = MetricsBuffer(max_size=100)
        assert buffer.max_size == 100
        assert buffer.size() == 0

    def test_add_metrics(self):
        """测试添加指标"""
        buffer = MetricsBuffer(max_size=100)
        buffer.add({"type": "cpu", "value": 50.0})
        assert buffer.size() == 1

    def test_add_multiple_metrics(self):
        """测试添加多个指标"""
        buffer = MetricsBuffer(max_size=100)
        for i in range(10):
            buffer.add({"type": "cpu", "value": i * 10})
        assert buffer.size() == 10

    def test_buffer_max_size(self):
        """测试缓冲区大小限制"""
        buffer = MetricsBuffer(max_size=5)
        for i in range(10):
            buffer.add({"type": "cpu", "value": i * 10})
        assert buffer.size() == 5  # 应该保持最大大小

    def test_get_all_metrics(self):
        """测试获取所有指标"""
        buffer = MetricsBuffer(max_size=100)
        data = [{"type": "cpu", "value": i} for i in range(5)]
        for item in data:
            buffer.add(item)

        result = buffer.get_all()
        assert len(result) == 5
        assert result == data

    def test_clear_buffer(self):
        """测试清空缓冲区"""
        buffer = MetricsBuffer(max_size=100)
        buffer.add({"type": "cpu", "value": 50.0})
        buffer.add({"type": "memory", "value": 100.0})
        assert buffer.size() == 2

        buffer.clear()
        assert buffer.size() == 0

    def test_thread_safety(self):
        """测试线程安全性"""
        buffer = MetricsBuffer(max_size=1000)

        def add_metrics(start, count):
            for i in range(count):
                buffer.add({"type": "cpu", "value": start + i})

        threads = []
        for i in range(5):
            thread = threading.Thread(target=add_metrics, args=(i * 100, 100))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        assert buffer.size() == 500  # 5线程 * 100指标


class TestMetricsCollector:
    """测试MetricsCollector采集器类"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path, ignore_errors=True)

    @pytest.fixture
    def collector(self, temp_dir):
        """创建MetricsCollector实例"""
        config = MetricsConfig(
            storage_type="memory",
            collection_interval=1,
            buffer_size=100
        )
        return MetricsCollector(config)

    @pytest.fixture
    def sqlite_collector(self, temp_dir):
        """创建使用SQLite的MetricsCollector实例"""
        config = MetricsConfig(
            storage_type="sqlite",
            storage_path=str(Path(temp_dir) / "test_metrics.db"),
            collection_interval=1,
            buffer_size=100
        )
        return MetricsCollector(config)

    def test_initialize_collector(self, temp_dir):
        """测试初始化采集器"""
        config = MetricsConfig(
            storage_type="memory",
            collection_interval=2,
            buffer_size=200
        )
        collector = MetricsCollector(config)
        assert collector.config.collection_interval == 2
        assert collector.config.buffer_size == 200
        assert collector._stop_event is not None
        assert collector._collection_thread is None

    def test_initialize_sqlite_collector(self, temp_dir):
        """测试初始化SQLite采集器"""
        config = MetricsConfig(
            storage_type="sqlite",
            storage_path=str(Path(temp_dir) / "test.db")
        )
        collector = MetricsCollector(config)
        assert collector.config.storage_type == "sqlite"
        assert hasattr(collector, 'conn')

    def test_collect_system_metrics(self, collector):
        """测试采集系统指标"""
        metrics = collector.collect_system_metrics()

        assert isinstance(metrics, SystemMetrics)
        assert metrics.timestamp is not None
        assert 0 <= metrics.cpu_percent <= 100
        assert metrics.cpu_count > 0
        assert len(metrics.load_average) == 3
        assert metrics.memory_total > 0
        assert metrics.memory_used >= 0
        assert metrics.memory_free >= 0
        assert 0 <= metrics.memory_percent <= 100
        assert isinstance(metrics.disk_usage, dict)
        assert isinstance(metrics.network_io, dict)
        assert metrics.process_count > 0

    def test_collect_system_metrics_to_dict(self, collector):
        """测试系统指标转换为字典"""
        metrics = collector.collect_system_metrics()
        result = metrics.to_dict()

        assert 'timestamp' in result
        assert 'cpu_percent' in result
        assert 'cpu_count' in result
        assert 'memory_total' in result
        assert 'memory_used' in result
        assert 'disk_usage' in result
        assert 'network_io' in result

    def test_collect_gpu_metrics(self, collector):
        """测试采集GPU指标"""
        metrics_list = collector.collect_gpu_metrics()

        assert isinstance(metrics_list, list)
        # 即使没有GPU，也应该返回空列表而不是出错
        for metrics in metrics_list:
            assert isinstance(metrics, GPUMetrics)
            assert metrics.timestamp is not None
            assert metrics.gpu_id >= 0
            assert metrics.name is not None
            assert 0 <= metrics.utilization_gpu <= 100
            assert 0 <= metrics.utilization_memory <= 100
            assert metrics.memory_used >= 0
            assert metrics.memory_total > 0

    def test_collect_gpu_metrics_to_dict(self, collector):
        """测试GPU指标转换为字典"""
        metrics_list = collector.collect_gpu_metrics()
        if metrics_list:
            result = metrics_list[0].to_dict()
            assert 'timestamp' in result
            assert 'gpu_id' in result
            assert 'name' in result
            assert 'utilization_gpu' in result

    def test_collect_npu_metrics(self, collector):
        """测试采集NPU指标"""
        metrics_list = collector.collect_npu_metrics()

        assert isinstance(metrics_list, list)
        # NPU监控可能返回空列表（需要特定硬件）
        for metrics in metrics_list:
            assert isinstance(metrics, NPUMetrics)
            assert metrics.timestamp is not None

    def test_collect_conversion_metrics(self, collector):
        """测试采集转换性能指标"""
        metrics = collector.collect_conversion_metrics("asr", "SenseVoice")

        assert isinstance(metrics, ConversionMetrics)
        assert metrics.model_type == "asr"
        assert metrics.model_name == "SenseVoice"
        assert metrics.throughput >= 0
        assert metrics.latency_p50 >= 0
        assert metrics.latency_p95 >= 0
        assert metrics.latency_p99 >= 0
        assert 0 <= metrics.success_rate <= 100
        assert metrics.error_count >= 0
        assert metrics.total_models >= 0
        assert metrics.completed_models >= 0

    def test_collect_conversion_metrics_to_dict(self, collector):
        """测试转换指标转换为字典"""
        metrics = collector.collect_conversion_metrics("tts", "VITS")
        result = metrics.to_dict()

        assert 'timestamp' in result
        assert 'model_type' in result
        assert 'model_name' in result
        assert 'throughput' in result
        assert 'latency_p50' in result
        assert 'success_rate' in result

    def test_start_real_time_collection(self, collector):
        """测试开始实时采集"""
        assert collector._collection_thread is None or not collector._collection_thread.is_alive()

        collector.start_real_time_collection(interval=0.1)

        assert collector._collection_thread is not None
        assert collector._collection_thread.is_alive()

        # 等待一段时间
        time.sleep(0.5)

        collector.stop_real_time_collection()

    def test_stop_real_time_collection(self, collector):
        """测试停止实时采集"""
        collector.start_real_time_collection(interval=0.1)
        time.sleep(0.2)

        assert collector._collection_thread and collector._collection_thread.is_alive()

        collector.stop_real_time_collection()

        # 等待线程结束
        collector._collection_thread.join(timeout=5)
        assert not collector._collection_thread.is_alive()

    def test_stop_real_time_collection_not_running(self, collector):
        """测试停止未开始的实时采集"""
        # 不应该出错
        collector.stop_real_time_collection()

    def test_real_time_collection_with_callback(self, temp_dir):
        """测试带回调的实时采集"""
        callback_data = []

        def callback(data):
            callback_data.append(data)

        config = MetricsConfig(
            collection_interval=0.1,
            realtime_callback=callback
        )
        collector = MetricsCollector(config)

        collector.start_real_time_collection()
        time.sleep(0.5)
        collector.stop_real_time_collection()

        # 应该有回调数据
        assert len(callback_data) > 0

    def test_get_recent_metrics_memory(self, collector):
        """测试获取最近的指标（内存存储）"""
        # 采集一些指标
        collector.collect_system_metrics()
        collector.collect_gpu_metrics()

        # 获取最近指标
        system_metrics = collector.get_recent_metrics('system', count=10)
        assert isinstance(system_metrics, list)

        gpu_metrics = collector.get_recent_metrics('gpu', count=10)
        assert isinstance(gpu_metrics, list)

    def test_get_recent_metrics_sqlite(self, sqlite_collector):
        """测试获取最近的指标（SQLite存储）"""
        # 采集一些指标
        sqlite_collector.collect_system_metrics()

        # 获取最近指标
        metrics = sqlite_collector.get_recent_metrics('system', count=10)
        assert isinstance(metrics, list)

    def test_export_metrics(self, collector, temp_dir):
        """测试导出指标"""
        # 采集指标
        collector.collect_system_metrics()

        # 导出指标
        output_file = Path(temp_dir) / "exported_metrics.json"
        collector.export_metrics('system', str(output_file))

        # 检查文件是否存在
        assert output_file.exists()

    def test_clear_metrics(self, collector):
        """测试清空指标"""
        # 采集指标
        collector.collect_system_metrics()
        collector.collect_gpu_metrics()

        # 清空所有指标
        collector.clear_metrics()

        # 清空系统指标
        collector.collect_system_metrics()
        collector.clear_metrics('system')

        # 清空GPU指标
        collector.clear_metrics('gpu')

    def test_clear_metrics_sqlite(self, sqlite_collector):
        """测试清空指标（SQLite）"""
        # 采集指标
        sqlite_collector.collect_system_metrics()

        # 清空指标
        sqlite_collector.clear_metrics()

        # 验证指标已清空
        metrics = sqlite_collector.get_recent_metrics('system', count=10)
        assert len(metrics) == 0

    def test_get_statistics(self, collector):
        """测试获取统计信息"""
        # 采集多个指标
        for _ in range(5):
            collector.collect_system_metrics()
            time.sleep(0.01)

        # 获取CPU利用率统计
        stats = collector.get_statistics('system', 'cpu_percent', hours=1)

        assert 'min' in stats
        assert 'max' in stats
        assert 'avg' in stats
        assert 'count' in stats
        assert stats['count'] == 5

    def test_get_statistics_empty(self, collector):
        """测试获取空统计信息"""
        stats = collector.get_statistics('system', 'nonexistent', hours=1)

        assert stats['min'] == 0
        assert stats['max'] == 0
        assert stats['avg'] == 0
        assert stats['count'] == 0

    def test_close_collector(self, collector):
        """测试关闭采集器"""
        # 开始采集
        collector.start_real_time_collection()
        time.sleep(0.1)

        # 关闭采集器
        collector.close()

        # 验证已关闭
        assert not collector._collection_thread or not collector._collection_thread.is_alive()

    def test_close_collector_sqlite(self, sqlite_collector):
        """测试关闭SQLite采集器"""
        sqlite_collector.close()
        # 应该已经关闭连接

    def test_collection_loop(self, collector):
        """测试采集循环"""
        collector._stop_event.clear()
        collector._collection_loop(0.1)

        # 循环应该采集了指标
        buffer_size = collector.metrics_buffer.size()
        assert buffer_size > 0


class TestSystemMetrics:
    """测试SystemMetrics系统指标类"""

    def test_create_system_metrics(self):
        """测试创建系统指标"""
        now = datetime.now()
        metrics = SystemMetrics(
            timestamp=now,
            cpu_percent=50.0,
            cpu_count=8,
            load_average=[1.0, 1.5, 2.0],
            memory_total=16000000000,
            memory_used=8000000000,
            memory_free=7000000000,
            memory_percent=50.0,
            disk_usage={},
            network_io={},
            process_count=100
        )

        assert metrics.timestamp == now
        assert metrics.cpu_percent == 50.0
        assert metrics.cpu_count == 8
        assert metrics.memory_percent == 50.0

    def test_system_metrics_to_dict(self):
        """测试系统指标转换为字典"""
        now = datetime.now()
        metrics = SystemMetrics(
            timestamp=now,
            cpu_percent=50.0,
            cpu_count=8,
            load_average=[1.0, 1.5, 2.0],
            memory_total=16000000000,
            memory_used=8000000000,
            memory_free=7000000000,
            memory_percent=50.0,
            disk_usage={},
            network_io={},
            process_count=100
        )

        result = metrics.to_dict()
        assert result['timestamp'] == now.isoformat()
        assert result['cpu_percent'] == 50.0


class TestGPUMetrics:
    """测试GPUMetrics GPU指标类"""

    def test_create_gpu_metrics(self):
        """测试创建GPU指标"""
        now = datetime.now()
        metrics = GPUMetrics(
            timestamp=now,
            gpu_id=0,
            name="NVIDIA GPU",
            utilization_gpu=75.0,
            utilization_memory=80.0,
            memory_used=4000,
            memory_total=8000,
            temperature=65.0,
            power_draw=150.0,
            fan_speed=60.0
        )

        assert metrics.gpu_id == 0
        assert metrics.utilization_gpu == 75.0
        assert metrics.memory_used == 4000

    def test_gpu_metrics_to_dict(self):
        """测试GPU指标转换为字典"""
        now = datetime.now()
        metrics = GPUMetrics(
            timestamp=now,
            gpu_id=0,
            name="NVIDIA GPU",
            utilization_gpu=75.0,
            utilization_memory=80.0,
            memory_used=4000,
            memory_total=8000
        )

        result = metrics.to_dict()
        assert result['timestamp'] == now.isoformat()
        assert result['gpu_id'] == 0


class TestConversionMetrics:
    """测试ConversionMetrics转换指标类"""

    def test_create_conversion_metrics(self):
        """测试创建转换指标"""
        now = datetime.now()
        metrics = ConversionMetrics(
            timestamp=now,
            model_type="asr",
            model_name="SenseVoice",
            throughput=12.5,
            latency_p50=15.2,
            latency_p95=28.5,
            latency_p99=45.8,
            success_rate=99.5,
            error_count=1,
            total_models=100,
            completed_models=99
        )

        assert metrics.model_type == "asr"
        assert metrics.throughput == 12.5
        assert metrics.success_rate == 99.5

    def test_conversion_metrics_to_dict(self):
        """测试转换指标转换为字典"""
        now = datetime.now()
        metrics = ConversionMetrics(
            timestamp=now,
            model_type="asr",
            model_name="SenseVoice",
            throughput=12.5,
            latency_p50=15.2,
            latency_p95=28.5,
            latency_p99=45.8,
            success_rate=99.5,
            error_count=1,
            total_models=100,
            completed_models=99
        )

        result = metrics.to_dict()
        assert result['timestamp'] == now.isoformat()
        assert result['model_type'] == "asr"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
