"""
Performance Monitor Module

This module provides the core performance monitoring infrastructure for XLeRobot NPU model conversion.
Part of Story 3.1: 性能优化与扩展 (Phase 1: 架构扩展)

The PerformanceMonitor class provides:
- Real-time performance metrics collection (latency, throughput, CPU, memory, NPU)
- Integration with Story 2.8 performance benchmark system
- Performance bottleneck identification and diagnosis
- Historical performance data storage and analysis
- Fine-grained conversion process monitoring

Author: BMM v6 Workflow
Version: 1.0
Date: 2025-10-28
"""

import time
import psutil
import threading
import json
import logging
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Union
from enum import Enum

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Enumeration of performance metric types."""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    NPU_USAGE = "npu_usage"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"


class MetricLevel(Enum):
    """Metric collection granularity levels."""
    COARSE = "coarse"
    NORMAL = "normal"
    FINE = "fine"


@dataclass
class PerformanceMetric:
    """Data structure for a single performance metric."""
    timestamp: datetime
    metric_type: MetricType
    value: Union[float, int]
    unit: str
    operation_id: Optional[str] = None
    stage: Optional[str] = None
    tags: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceSnapshot:
    """Complete performance snapshot at a point in time."""
    timestamp: datetime
    operation_id: str
    metrics: Dict[MetricType, float] = field(default_factory=dict)
    stages: Dict[str, Dict[MetricType, float]] = field(default_factory=dict)
    system_info: Dict[str, Any] = field(default_factory=dict)


class MetricsCollector(ABC):
    """Abstract base class for metric collectors."""

    @abstractmethod
    def collect(self) -> Dict[str, Union[float, int]]:
        """Collect metrics and return as dictionary."""
        pass


class CPUMetricsCollector(MetricsCollector):
    """CPU and system metrics collector using psutil."""

    def collect(self) -> Dict[str, float]:
        """Collect CPU and system metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            cpu_count = psutil.cpu_count()
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)

            return {
                'cpu_percent': cpu_percent,
                'cpu_count': cpu_count,
                'cpu_load_1m': load_avg[0],
                'cpu_load_5m': load_avg[1],
                'cpu_load_15m': load_avg[2]
            }
        except Exception as e:
            logger.error(f"Failed to collect CPU metrics: {e}")
            return {}


class MemoryMetricsCollector(MetricsCollector):
    """Memory metrics collector using psutil."""

    def collect(self) -> Dict[str, Union[float, int]]:
        """Collect memory metrics."""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()

            return {
                'memory_total': memory.total,
                'memory_used': memory.used,
                'memory_free': memory.free,
                'memory_percent': memory.percent,
                'swap_total': swap.total,
                'swap_used': swap.used,
                'swap_percent': swap.percent
            }
        except Exception as e:
            logger.error(f"Failed to collect memory metrics: {e}")
            return {}


class NPUMetricsCollector(MetricsCollector):
    """NPU-specific metrics collector (placeholder for Horizon X5 BPU integration)."""

    def collect(self) -> Dict[str, Union[float, int]]:
        """Collect NPU metrics."""
        try:
            # Placeholder for Horizon X5 BPU integration
            # In real implementation, this would interface with Horizon BPU SDK
            return {
                'npu_utilization': 0.0,
                'npu_memory_used': 0,
                'npu_memory_total': 0,
                'npu_temperature': 0.0,
                'npu_power': 0.0
            }
        except Exception as e:
            logger.error(f"Failed to collect NPU metrics: {e}")
            return {}


class PerformanceMonitor:
    """
    Core performance monitoring class for XLeRobot conversion flows.

    This class provides comprehensive performance monitoring capabilities:
    - Real-time metrics collection
    - Historical data storage
    - Performance bottleneck identification
    - Integration with Story 2.8 benchmark system
    - Fine-grained conversion stage monitoring

    Attributes:
        operation_id: Unique identifier for monitored operation
        collectors: List of metric collectors
        metrics_history: Circular buffer for metric storage
        snapshot_interval: Interval between performance snapshots
        is_monitoring: Whether monitoring is active
        callbacks: Performance event callbacks
    """

    def __init__(
        self,
        operation_id: str,
        snapshot_interval: float = 1.0,
        max_history_size: int = 10000,
        level: MetricLevel = MetricLevel.NORMAL
    ) -> None:
        """
        Initialize the PerformanceMonitor.

        Args:
            operation_id: Unique identifier for the operation to monitor
            snapshot_interval: Time between automatic snapshots (seconds)
            max_history_size: Maximum number of metrics to store
            level: Collection granularity level
        """
        self.operation_id = operation_id
        self.snapshot_interval = snapshot_interval
        self.max_history_size = max_history_size
        self.level = level

        # Initialize metric collectors
        self.collectors: List[MetricsCollector] = [
            CPUMetricsCollector(),
            MemoryMetricsCollector(),
            NPUMetricsCollector()
        ]

        # Metrics storage
        self.metrics_history: deque = deque(maxlen=max_history_size)
        self.snapshots: deque = deque(maxlen=max_history_size)

        # Monitoring state
        self.is_monitoring = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

        # Stage tracking
        self.current_stage: Optional[str] = None
        self.stage_times: Dict[str, List[float]] = defaultdict(list)

        # Callbacks
        self.performance_callbacks: List[Callable[[PerformanceSnapshot], None]] = []
        self.bottleneck_callbacks: List[Callable[[str, Dict[str, Any]], None]] = []

        logger.info(f"PerformanceMonitor initialized for operation: {operation_id}")

    def start_monitoring(self) -> None:
        """Start performance monitoring."""
        if self.is_monitoring:
            logger.warning("Performance monitoring already active")
            return

        self.start_time = datetime.now()
        self.is_monitoring = True

        # Start monitoring thread
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            name=f"PerfMon-{self.operation_id}",
            daemon=True
        )
        self.monitoring_thread.start()

        logger.info(f"Started performance monitoring for operation: {self.operation_id}")

    def stop_monitoring(self) -> None:
        """Stop performance monitoring."""
        if not self.is_monitoring:
            logger.warning("Performance monitoring not active")
            return

        self.end_time = datetime.now()
        self.is_monitoring = False

        # Wait for monitoring thread to complete
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=2.0)

        logger.info(f"Stopped performance monitoring for operation: {self.operation_id}")

    def record_metric(
        self,
        metric_type: MetricType,
        value: Union[float, int],
        unit: str,
        stage: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record a performance metric.

        Args:
            metric_type: Type of metric
            value: Metric value
            unit: Unit of measurement
            stage: Optional conversion stage name
            tags: Optional additional tags
        """
        metric = PerformanceMetric(
            timestamp=datetime.now(),
            metric_type=metric_type,
            value=value,
            unit=unit,
            operation_id=self.operation_id,
            stage=stage or self.current_stage,
            tags=tags or {}
        )

        self.metrics_history.append(metric)

        # Trigger callbacks for critical metrics
        self._check_thresholds(metric)

    def record_latency(self, stage: str, duration: float) -> None:
        """Record stage latency in milliseconds."""
        self.record_metric(MetricType.LATENCY, duration, "ms", stage)
        self.stage_times[stage].append(duration)

    def record_throughput(self, items_per_second: float) -> None:
        """Record throughput (items processed per second)."""
        self.record_metric(MetricType.THROUGHPUT, items_per_second, "items/sec")

    def set_stage(self, stage_name: str) -> None:
        """
        Set the current conversion stage.

        Args:
            stage_name: Name of the current stage
        """
        self.current_stage = stage_name
        logger.debug(f"Performance monitoring stage set to: {stage_name}")

    def create_snapshot(self) -> PerformanceSnapshot:
        """
        Create a comprehensive performance snapshot.

        Returns:
            PerformanceSnapshot containing current metrics
        """
        snapshot = PerformanceSnapshot(
            timestamp=datetime.now(),
            operation_id=self.operation_id,
            system_info=self._collect_system_metrics()
        )

        # Collect current metrics
        current_metrics = self._collect_current_metrics()
        snapshot.metrics = current_metrics

        # Add stage-specific metrics
        if self.current_stage:
            snapshot.stages[self.current_stage] = current_metrics

        self.snapshots.append(snapshot)

        # Trigger performance callbacks
        for callback in self.performance_callbacks:
            try:
                callback(snapshot)
            except Exception as e:
                logger.error(f"Performance callback error: {e}")

        return snapshot

    def add_performance_callback(self, callback: Callable[[PerformanceSnapshot], None]) -> None:
        """
        Add a performance event callback.

        Args:
            callback: Function to call on performance events
        """
        self.performance_callbacks.append(callback)

    def add_bottleneck_callback(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """
        Add a bottleneck detection callback.

        Args:
            callback: Function to call when bottlenecks are detected
        """
        self.bottleneck_callbacks.append(callback)

    def get_summary(self) -> Dict[str, Any]:
        """
        Get performance summary.

        Returns:
            Dictionary containing performance summary
        """
        if not self.start_time:
            return {"error": "Monitoring not started"}

        duration = (self.end_time or datetime.now()) - self.start_time

        # Calculate aggregated metrics
        latencies = [m.value for m in self.metrics_history if m.metric_type == MetricType.LATENCY]
        throughputs = [m.value for m in self.metrics_history if m.metric_type == MetricType.THROUGHPUT]

        summary = {
            "operation_id": self.operation_id,
            "duration_seconds": duration.total_seconds(),
            "total_metrics": len(self.metrics_history),
            "snapshots_count": len(self.snapshots),
            "current_stage": self.current_stage,
            "stage_times": dict(self.stage_times)
        }

        if latencies:
            summary["latency_stats"] = {
                "min_ms": min(latencies),
                "max_ms": max(latencies),
                "avg_ms": sum(latencies) / len(latencies)
            }

        if throughputs:
            summary["throughput_stats"] = {
                "min_items_sec": min(throughputs),
                "max_items_sec": max(throughputs),
                "avg_items_sec": sum(throughputs) / len(throughputs)
            }

        return summary

    def export_metrics(self, filepath: Union[str, Path]) -> None:
        """
        Export metrics to JSON file.

        Args:
            filepath: Path to export file
        """
        data = {
            "operation_id": self.operation_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "metrics": [asdict(m) for m in self.metrics_history],
            "snapshots": [asdict(s) for s in self.snapshots],
            "summary": self.get_summary()
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        logger.info(f"Exported {len(self.metrics_history)} metrics to: {filepath}")

    def _monitoring_loop(self) -> None:
        """Internal monitoring loop (runs in separate thread)."""
        while self.is_monitoring:
            try:
                self.create_snapshot()
                time.sleep(self.snapshot_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.snapshot_interval)

    def _collect_current_metrics(self) -> Dict[MetricType, float]:
        """Collect current metrics from all collectors."""
        metrics = {}

        for collector in self.collectors:
            collected = collector.collect()
            for key, value in collected.items():
                # Map to MetricType enum
                if 'cpu' in key.lower():
                    metrics[MetricType.CPU_USAGE] = value
                elif 'memory' in key.lower():
                    metrics[MetricType.MEMORY_USAGE] = value
                elif 'npu' in key.lower():
                    metrics[MetricType.NPU_USAGE] = value

        return metrics

    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system information."""
        try:
            return {
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "python_version": psutil.sys.version,
                "platform": psutil.sys.platform
            }
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {}

    def _check_thresholds(self, metric: PerformanceMetric) -> None:
        """
        Check if metric exceeds thresholds and trigger callbacks.

        Args:
            metric: Metric to check
        """
        # Define default thresholds
        thresholds = {
            MetricType.CPU_USAGE: 80.0,
            MetricType.MEMORY_USAGE: 85.0,
            MetricType.LATENCY: 300000.0,  # 5 minutes in ms
        }

        if metric.metric_type in thresholds:
            threshold = thresholds[metric.metric_type]
            if metric.value > threshold:
                bottleneck_info = {
                    "metric_type": metric.metric_type.value,
                    "value": metric.value,
                    "threshold": threshold,
                    "timestamp": metric.timestamp.isoformat(),
                    "stage": metric.stage
                }

                for callback in self.bottleneck_callbacks:
                    try:
                        callback(f"{metric.metric_type.value}_threshold_exceeded", bottleneck_info)
                    except Exception as e:
                        logger.error(f"Bottleneck callback error: {e}")

    def __enter__(self):
        """Context manager entry."""
        self.start_monitoring()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_monitoring()
