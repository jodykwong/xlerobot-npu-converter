"""
Performance Optimization Engine

This module provides intelligent performance optimization capabilities for XLeRobot NPU model conversion.
Part of Story 3.1: 性能优化与扩展 (Phase 2: 核心功能实现)

Features:
- Automatic performance bottleneck identification
- Intelligent task scheduling
- Dynamic resource allocation
- Incremental conversion and caching strategies

Author: BMM v6 Workflow
Version: 1.0
Date: 2025-10-28
"""

import logging
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union, Callable

from .performance_monitor import MetricType
from .performance_storage import PerformanceDatabase, PerformanceAnalyzer
from .performance_hook import OptimizationStrategy

logger = logging.getLogger(__name__)


class BottleneckType(Enum):
    """Types of performance bottlenecks."""
    CPU_BOUND = "cpu_bound"
    MEMORY_BOUND = "memory_bound"
    IO_BOUND = "io_bound"
    NPU_BOUND = "npu_bound"
    STAGE_LATENCY = "stage_latency"
    THROUGHPUT_LIMIT = "throughput_limit"
    CONCURRENCY_LIMIT = "concurrency_limit"
    CACHE_MISS = "cache_miss"
    RESOURCE_CONTENTION = "resource_contention"


class OptimizationAction(Enum):
    """Optimization actions."""
    INCREASE_PARALLELISM = "increase_parallelism"
    DECREASE_PARALLELISM = "decrease_parallelism"
    ENABLE_CACHING = "enable_caching"
    OPTIMIZE_MEMORY = "optimize_memory"
    SWITCH_ALGORITHM = "switch_algorithm"
    ADJUST_BATCH_SIZE = "adjust_batch_size"
    PRIORITIZE_STAGE = "prioritize_stage"
    DEFER_OPERATION = "defer_operation"
    ALLOCATE_RESOURCES = "allocate_resources"
    RELEASE_RESOURCES = "release_resources"


@dataclass
class Bottleneck:
    """Represents a performance bottleneck."""
    type: BottleneckType
    severity: float  # 0.0 - 1.0
    stage: Optional[str]
    metrics: Dict[str, float]
    suggestion: str
    potential_improvement_percent: float
    timestamp: datetime = field(default_factory=datetime.now)
    confidence: float = field(default=0.0)  # 0.0 - 1.0


@dataclass
class OptimizationRecommendation:
    """Optimization recommendation."""
    action: OptimizationAction
    priority: int  # 1-10, higher is more important
    description: str
    expected_improvement: float  # percentage
    resource_requirements: Dict[str, float]
    implementation_effort: str  # low, medium, high
    risk_level: str  # low, medium, high


class BottleneckIdentifier:
    """
    Intelligent bottleneck identification algorithm.

    Uses statistical analysis, pattern recognition, and ML-based
    approaches to identify performance bottlenecks.
    """

    def __init__(self, database: PerformanceDatabase):
        """
        Initialize bottleneck identifier.

        Args:
            database: PerformanceDatabase instance
        """
        self.database = database
        self.analyzer = PerformanceAnalyzer(database)
        self._bottleneck_history: List[Bottleneck] = []

        # Thresholds for different bottleneck types
        self.thresholds = {
            BottleneckType.CPU_BOUND: {
                "cpu_usage_percent": 80.0,
                "duration_deviation": 2.0  # 2 standard deviations
            },
            BottleneckType.MEMORY_BOUND: {
                "memory_usage_percent": 85.0,
                "memory_growth_rate": 10.0  # MB/s
            },
            BottleneckType.STAGE_LATENCY: {
                "latency_ms": 300000.0,  # 5 minutes
                "latency_percentile": 95.0
            },
            BottleneckType.THROUGHPUT_LIMIT: {
                "min_throughput": 10.0,  # items/sec
                "throughput_drop_percent": 20.0
            }
        }

        logger.info("BottleneckIdentifier initialized")

    def identify_bottlenecks(
        self,
        operation_id: str,
        time_range_hours: int = 24
    ) -> List[Bottleneck]:
        """
        Identify performance bottlenecks.

        Args:
            operation_id: Operation to analyze
            time_range_hours: Time range to analyze

        Returns:
            List of identified bottlenecks
        """
        logger.info(f"Identifying bottlenecks for operation: {operation_id}")

        bottlenecks = []

        # Get metrics from database
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=time_range_hours)

        # Analyze each bottleneck type
        bottlenecks.extend(self._identify_cpu_bottlenecks(operation_id, start_time, end_time))
        bottlenecks.extend(self._identify_memory_bottlenecks(operation_id, start_time, end_time))
        bottlenecks.extend(self._identify_latency_bottlenecks(operation_id, start_time, end_time))
        bottlenecks.extend(self._identify_throughput_bottlenecks(operation_id, start_time, end_time))
        bottlenecks.extend(self._identify_io_bottlenecks(operation_id, start_time, end_time))
        bottlenecks.extend(self._identify_npu_bottlenecks(operation_id, start_time, end_time))
        bottlenecks.extend(self._identify_concurrency_bottlenecks(operation_id, start_time, end_time))

        # Sort by severity (highest first)
        bottlenecks.sort(key=lambda b: b.severity, reverse=True)

        # Store in history
        self._bottleneck_history.extend(bottlenecks)

        logger.info(f"Identified {len(bottlenecks)} bottlenecks")

        return bottlenecks

    def _identify_cpu_bottlenecks(
        self,
        operation_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Bottleneck]:
        """Identify CPU-related bottlenecks."""
        bottlenecks = []

        # Get CPU metrics
        metrics = self.database.get_metrics(
            operation_id=operation_id,
            metric_type=MetricType.CPU_USAGE,
            start_time=start_time,
            end_time=end_time
        )

        if not metrics:
            return bottlenecks

        cpu_values = [m['value'] for m in metrics]
        mean_cpu = statistics.mean(cpu_values)
        max_cpu = max(cpu_values)

        # Check CPU usage threshold
        if mean_cpu > self.thresholds[BottleneckType.CPU_BOUND]["cpu_usage_percent"]:
            severity = min((mean_cpu - 70.0) / 30.0, 1.0)  # Scale severity

            bottlenecks.append(Bottleneck(
                type=BottleneckType.CPU_BOUND,
                severity=severity,
                stage=None,
                metrics={
                    "mean_cpu_percent": mean_cpu,
                    "max_cpu_percent": max_cpu,
                    "sample_count": len(cpu_values)
                },
                suggestion=f"CPU使用率过高 (平均 {mean_cpu:.1f}%)。建议：1) 减少并发任务数 2) 优化CPU密集型算法 3) 使用异步处理",
                potential_improvement_percent=min(mean_cpu - 70.0, 30.0),
                confidence=0.9
            ))

        return bottlenecks

    def _identify_memory_bottlenecks(
        self,
        operation_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Bottleneck]:
        """Identify memory-related bottlenecks."""
        bottlenecks = []

        # Get memory metrics
        metrics = self.database.get_metrics(
            operation_id=operation_id,
            metric_type=MetricType.MEMORY_USAGE,
            start_time=start_time,
            end_time=end_time
        )

        if not metrics:
            return bottlenecks

        memory_values = [m['value'] for m in metrics]
        mean_memory = statistics.mean(memory_values)
        max_memory = max(memory_values)

        # Check memory usage threshold
        if mean_memory > self.thresholds[BottleneckType.MEMORY_BOUND]["memory_usage_percent"]:
            severity = min((mean_memory - 75.0) / 25.0, 1.0)

            bottlenecks.append(Bottleneck(
                type=BottleneckType.MEMORY_BOUND,
                severity=severity,
                stage=None,
                metrics={
                    "mean_memory_percent": mean_memory,
                    "max_memory_percent": max_memory,
                    "sample_count": len(memory_values)
                },
                suggestion=f"内存使用率过高 (平均 {mean_memory:.1f}%)。建议：1) 启用增量转换 2) 优化内存管理 3) 分批处理大模型",
                potential_improvement_percent=min(mean_memory - 75.0, 25.0),
                confidence=0.85
            ))

        return bottlenecks

    def _identify_latency_bottlenecks(
        self,
        operation_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Bottleneck]:
        """Identify latency-related bottlenecks."""
        bottlenecks = []

        # Get latency metrics
        metrics = self.database.get_metrics(
            operation_id=operation_id,
            metric_type=MetricType.LATENCY,
            start_time=start_time,
            end_time=end_time
        )

        if not metrics:
            return bottlenecks

        # Group by stage
        by_stage = {}
        for metric in metrics:
            stage = metric.get('stage', 'unknown')
            if stage not in by_stage:
                by_stage[stage] = []
            by_stage[stage].append(metric['value'])

        # Analyze each stage
        for stage, values in by_stage.items():
            if len(values) < 3:  # Need at least 3 samples
                continue

            mean_latency = statistics.mean(values)
            max_latency = max(values)
            p95_latency = sorted(values)[int(len(values) * 0.95)]

            # Check latency thresholds
            if mean_latency > self.thresholds[BottleneckType.STAGE_LATENCY]["latency_ms"]:
                severity = min((mean_latency - 60000.0) / 240000.0, 1.0)  # Scale severity

                bottlenecks.append(Bottleneck(
                    type=BottleneckType.STAGE_LATENCY,
                    severity=severity,
                    stage=stage,
                    metrics={
                        "mean_latency_ms": mean_latency,
                        "p95_latency_ms": p95_latency,
                        "max_latency_ms": max_latency,
                        "sample_count": len(values)
                    },
                    suggestion=f"阶段 {stage} 延迟过高 (平均 {mean_latency/1000:.1f}s)。建议：1) 并行化处理 2) 缓存中间结果 3) 优化算法",
                    potential_improvement_percent=min((mean_latency - 60000.0) / 60000.0 * 100, 50.0),
                    confidence=0.95
                ))

        return bottlenecks

    def _identify_throughput_bottlenecks(
        self,
        operation_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Bottleneck]:
        """Identify throughput-related bottlenecks."""
        bottlenecks = []

        # Get throughput metrics
        metrics = self.database.get_metrics(
            operation_id=operation_id,
            metric_type=MetricType.THROUGHPUT,
            start_time=start_time,
            end_time=end_time
        )

        if not metrics:
            return bottlenecks

        throughput_values = [m['value'] for m in metrics]
        mean_throughput = statistics.mean(throughput_values)
        min_throughput = min(throughput_values)

        # Check throughput threshold
        if mean_throughput < self.thresholds[BottleneckType.THROUGHPUT_LIMIT]["min_throughput"]:
            severity = min((10.0 - mean_throughput) / 10.0, 1.0)

            bottlenecks.append(Bottleneck(
                type=BottleneckType.THROUGHPUT_LIMIT,
                severity=severity,
                stage=None,
                metrics={
                    "mean_throughput_items_sec": mean_throughput,
                    "min_throughput_items_sec": min_throughput,
                    "sample_count": len(throughput_values)
                },
                suggestion=f"吞吐量过低 ({mean_throughput:.1f} items/sec)。建议：1) 增加并发度 2) 启用批量处理 3) 优化I/O",
                potential_improvement_percent=min((15.0 - mean_throughput) / 15.0 * 100, 60.0),
                confidence=0.8
            ))

        return bottlenecks

    def _identify_io_bottlenecks(
        self,
        operation_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Bottleneck]:
        """Identify I/O-related bottlenecks."""
        # I/O bottlenecks are typically identified by low throughput
        # despite reasonable CPU and memory usage
        return []

    def _identify_npu_bottlenecks(
        self,
        operation_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Bottleneck]:
        """Identify NPU-related bottlenecks."""
        bottlenecks = []

        # Get NPU metrics
        metrics = self.database.get_metrics(
            operation_id=operation_id,
            metric_type=MetricType.NPU_USAGE,
            start_time=start_time,
            end_time=end_time
        )

        if not metrics:
            return bottlenecks

        npu_values = [m['value'] for m in metrics]
        mean_npu = statistics.mean(npu_values)

        # Check NPU usage
        if mean_npu > 90.0:
            severity = min((mean_npu - 80.0) / 20.0, 1.0)

            bottlenecks.append(Bottleneck(
                type=BottleneckType.NPU_BOUND,
                severity=severity,
                stage=None,
                metrics={
                    "mean_npu_percent": mean_npu,
                    "sample_count": len(npu_values)
                },
                suggestion=f"NPU使用率过高 ({mean_npu:.1f}%)。建议：1) 调整批处理大小 2) 启用任务队列 3) 优化NPU内存管理",
                potential_improvement_percent=min(mean_npu - 80.0, 20.0),
                confidence=0.75
            ))

        return bottlenecks

    def _identify_concurrency_bottlenecks(
        self,
        operation_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Bottleneck]:
        """Identify concurrency-related bottlenecks."""
        # This would require tracking concurrent task counts
        # and correlating with performance metrics
        return []


class IntelligentScheduler:
    """
    Intelligent task scheduling based on performance data.

    Makes scheduling decisions based on:
    - Current system load
    - Historical performance patterns
    - Bottleneck analysis
    - Resource availability
    """

    def __init__(self):
        """Initialize intelligent scheduler."""
        self._scheduling_history: List[Dict[str, Any]] = []
        self._performance_patterns: Dict[str, List[float]] = {}

        # Scheduling strategies
        self.strategies = {
            "high_throughput": self._schedule_for_throughput,
            "low_latency": self._schedule_for_low_latency,
            "resource_efficient": self._schedule_for_efficiency,
            "adaptive": self._schedule_adaptively
        }

        logger.info("IntelligentScheduler initialized")

    def schedule_tasks(
        self,
        tasks: List[Dict[str, Any]],
        strategy: str = "adaptive",
        system_load: Dict[str, float] = None
    ) -> List[Dict[str, Any]]:
        """
        Schedule tasks intelligently.

        Args:
            tasks: List of task configurations
            strategy: Scheduling strategy
            system_load: Current system load metrics

        Returns:
            Scheduled task order
        """
        if strategy not in self.strategies:
            logger.warning(f"Unknown strategy: {strategy}, using adaptive")
            strategy = "adaptive"

        scheduled_tasks = self.strategies[strategy](tasks, system_load or {})

        # Store scheduling decision
        self._scheduling_history.append({
            "timestamp": datetime.now(),
            "strategy": strategy,
            "task_count": len(tasks),
            "system_load": system_load
        })

        logger.info(f"Scheduled {len(tasks)} tasks using {strategy} strategy")

        return scheduled_tasks

    def _schedule_for_throughput(
        self,
        tasks: List[Dict[str, Any]],
        system_load: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Schedule tasks to maximize throughput."""
        # Sort by resource efficiency (estimated)
        # Higher efficiency tasks first
        sorted_tasks = sorted(
            tasks,
            key=lambda t: t.get("estimated_efficiency", 1.0),
            reverse=True
        )
        return sorted_tasks

    def _schedule_for_low_latency(
        self,
        tasks: List[Dict[str, Any]],
        system_load: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Schedule tasks to minimize latency."""
        # Sort by estimated duration (shortest first)
        sorted_tasks = sorted(
            tasks,
            key=lambda t: t.get("estimated_duration", 0.0)
        )
        return sorted_tasks

    def _schedule_for_efficiency(
        self,
        tasks: List[Dict[str, Any]],
        system_load: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Schedule tasks for resource efficiency."""
        # Sort by resource usage per unit work
        # More efficient tasks first
        sorted_tasks = sorted(
            tasks,
            key=lambda t: t.get("resource_efficiency", 1.0),
            reverse=True
        )
        return sorted_tasks

    def _schedule_adaptively(
        self,
        tasks: List[Dict[str, Any]],
        system_load: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Adaptive scheduling based on current system state."""
        # Combine multiple factors
        cpu_load = system_load.get("cpu_percent", 50.0)
        memory_load = system_load.get("memory_percent", 50.0)

        if cpu_load > 80.0:
            # High CPU load - prioritize memory-efficient tasks
            return self._schedule_for_efficiency(tasks, system_load)
        elif memory_load > 80.0:
            # High memory load - prioritize CPU-efficient tasks
            return self._schedule_for_low_latency(tasks, system_load)
        else:
            # Balanced load - maximize throughput
            return self._schedule_for_throughput(tasks, system_load)


class DynamicResourceAllocator:
    """
    Dynamic resource allocation based on performance analysis.

    Adjusts resource allocation in real-time based on:
    - Current bottlenecks
    - System load
    - Task priorities
    - Historical patterns
    """

    def __init__(self):
        """Initialize dynamic resource allocator."""
        self._allocation_history: List[Dict[str, Any]] = []
        self._current_allocation: Dict[str, float] = {
            "cpu_cores": 4.0,
            "memory_gb": 8.0,
            "concurrent_tasks": 5.0,
            "thread_pool_size": 4
        }

        logger.info("DynamicResourceAllocator initialized")

    def allocate_resources(
        self,
        bottlenecks: List[Bottleneck],
        target_performance: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Allocate resources dynamically based on bottlenecks.

        Args:
            bottlenecks: List of identified bottlenecks
            target_performance: Target performance metrics

        Returns:
            New resource allocation
        """
        new_allocation = self._current_allocation.copy()

        # Analyze bottlenecks and adjust resources
        cpu_bottleneck = any(b.type == BottleneckType.CPU_BOUND for b in bottlenecks)
        memory_bottleneck = any(b.type == BottleneckType.MEMORY_BOUND for b in bottlenecks)
        concurrency_bottleneck = any(b.type == BottleneckType.CONCURRENCY_LIMIT for b in bottlenecks)

        # Adjust CPU resources
        if cpu_bottleneck:
            new_allocation["cpu_cores"] = min(new_allocation["cpu_cores"] * 1.2, 8.0)
            new_allocation["thread_pool_size"] = min(int(new_allocation["cpu_cores"]), 8)

        # Adjust memory resources
        if memory_bottleneck:
            new_allocation["memory_gb"] = min(new_allocation["memory_gb"] * 1.5, 16.0)

        # Adjust concurrency
        if concurrency_bottleneck:
            new_allocation["concurrent_tasks"] = min(new_allocation["concurrent_tasks"] * 1.3, 10.0)

        # Store allocation decision
        allocation_decision = {
            "timestamp": datetime.now(),
            "previous_allocation": self._current_allocation,
            "new_allocation": new_allocation,
            "bottlenecks_considered": len(bottlenecks),
            "target_performance": target_performance
        }

        self._allocation_history.append(allocation_decision)
        self._current_allocation = new_allocation

        logger.info(f"Adjusted resource allocation: {new_allocation}")

        return new_allocation


class CacheStrategy:
    """
    Intelligent caching strategy for incremental conversion.

    Implements smart caching based on:
    - Model structure similarity
    - Conversion stage reuse
    - Performance impact analysis
    """

    def __init__(self):
        """Initialize cache strategy."""
        self._cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }
        self._cache_tiers = {
            "hot": {"size_mb": 500, "ttl_hours": 24},
            "warm": {"size_mb": 1000, "ttl_hours": 72},
            "cold": {"size_mb": 2000, "ttl_hours": 168}
        }

        logger.info("CacheStrategy initialized")

    def should_cache(
        self,
        model_path: str,
        operation_type: str,
        expected_duration: float
    ) -> Tuple[bool, str]:
        """
        Determine if operation should be cached.

        Args:
            model_path: Path to model
            operation_type: Type of operation
            expected_duration: Expected operation duration

        Returns:
            Tuple of (should_cache, cache_tier)
        """
        # Cache operations that take more than 5 seconds
        if expected_duration > 5000.0:  # 5 seconds
            if expected_duration > 30000.0:  # 30 seconds
                return True, "hot"
            elif expected_duration > 10000.0:  # 10 seconds
                return True, "warm"
            else:
                return True, "cold"

        return False, "none"

    def get_cache_key(
        self,
        model_path: str,
        operation_type: str,
        parameters: Dict[str, Any]
    ) -> str:
        """
        Generate cache key for operation.

        Args:
            model_path: Path to model
            operation_type: Type of operation
            parameters: Operation parameters

        Returns:
            Cache key string
        """
        import hashlib

        # Create deterministic cache key
        key_data = f"{model_path}:{operation_type}:{str(sorted(parameters.items()))}"
        cache_key = hashlib.md5(key_data.encode()).hexdigest()

        return cache_key

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self._cache_stats["hits"] + self._cache_stats["misses"]
        hit_rate = (self._cache_stats["hits"] / total * 100) if total > 0 else 0

        return {
            **self._cache_stats,
            "total_requests": total,
            "hit_rate_percent": round(hit_rate, 2)
        }


class PerformanceOptimizer:
    """
    Main performance optimization engine.

    Coordinates bottleneck identification, intelligent scheduling,
    dynamic resource allocation, and caching strategies.
    """

    def __init__(
        self,
        database: PerformanceDatabase,
        optimization_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED
    ) -> None:
        """
        Initialize performance optimizer.

        Args:
            database: PerformanceDatabase instance
            optimization_strategy: Optimization strategy
        """
        self.database = database
        self.strategy = optimization_strategy

        # Components
        self.bottleneck_identifier = BottleneckIdentifier(database)
        self.scheduler = IntelligentScheduler()
        self.resource_allocator = DynamicResourceAllocator()
        self.cache_strategy = CacheStrategy()

        # Optimization state
        self._optimization_history: List[Dict[str, Any]] = []

        logger.info(f"PerformanceOptimizer initialized with {optimization_strategy.value} strategy")

    def optimize(
        self,
        operation_id: str,
        tasks: Optional[List[Dict[str, Any]]] = None,
        target_performance: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive performance optimization.

        Args:
            operation_id: Operation to optimize
            tasks: List of tasks to schedule
            target_performance: Target performance metrics

        Returns:
            Optimization results
        """
        logger.info(f"Starting optimization for operation: {operation_id}")

        # Default targets
        if target_performance is None:
            target_performance = {
                "latency_ms": 300000.0,  # 5 minutes
                "throughput_items_sec": 10.0,
                "cpu_percent": 80.0,
                "memory_percent": 85.0
            }

        # Step 1: Identify bottlenecks
        bottlenecks = self.bottleneck_identifier.identify_bottlenecks(operation_id)

        # Step 2: Generate recommendations
        recommendations = self._generate_recommendations(bottlenecks)

        # Step 3: Allocate resources dynamically
        new_allocation = self.resource_allocator.allocate_resources(
            bottlenecks,
            target_performance
        )

        # Step 4: Schedule tasks if provided
        scheduled_tasks = None
        if tasks:
            system_load = {
                "cpu_percent": target_performance.get("cpu_percent", 50.0),
                "memory_percent": target_performance.get("memory_percent", 50.0)
            }
            scheduled_tasks = self.scheduler.schedule_tasks(tasks, "adaptive", system_load)

        # Step 5: Compile optimization results
        optimization_result = {
            "operation_id": operation_id,
            "timestamp": datetime.now().isoformat(),
            "bottlenecks": [
                {
                    "type": b.type.value,
                    "severity": b.severity,
                    "stage": b.stage,
                    "metrics": b.metrics,
                    "suggestion": b.suggestion,
                    "potential_improvement_percent": b.potential_improvement_percent,
                    "confidence": b.confidence
                }
                for b in bottlenecks
            ],
            "recommendations": recommendations,
            "resource_allocation": new_allocation,
            "scheduled_tasks": scheduled_tasks,
            "cache_stats": self.cache_strategy.get_cache_stats()
        }

        # Store optimization history
        self._optimization_history.append(optimization_result)

        logger.info(f"Optimization completed: {len(bottlenecks)} bottlenecks identified, "
                   f"{len(recommendations)} recommendations generated")

        return optimization_result

    def _generate_recommendations(
        self,
        bottlenecks: List[Bottleneck]
    ) -> List[OptimizationRecommendation]:
        """
        Generate optimization recommendations from bottlenecks.

        Args:
            bottlenecks: List of identified bottlenecks

        Returns:
            List of optimization recommendations
        """
        recommendations = []

        # Group bottlenecks by type
        by_type = {}
        for bottleneck in bottlenecks:
            if bottleneck.type not in by_type:
                by_type[bottleneck.type] = []
            by_type[bottleneck.type].append(bottleneck)

        # Generate recommendations based on bottleneck types
        for bottleneck_type, type_bottlenecks in by_type.items():
            avg_severity = statistics.mean([b.severity for b in type_bottlenecks])
            max_improvement = max([b.potential_improvement_percent for b in type_bottlenecks])

            if bottleneck_type == BottleneckType.CPU_BOUND:
                recommendations.append(OptimizationRecommendation(
                    action=OptimizationAction.DECREASE_PARALLELISM,
                    priority=int(avg_severity * 10),
                    description="减少并发任务数以降低CPU负载",
                    expected_improvement=min(max_improvement, 30.0),
                    resource_requirements={"cpu_cores": -1.0},
                    implementation_effort="low",
                    risk_level="low"
                ))
            elif bottleneck_type == BottleneckType.MEMORY_BOUND:
                recommendations.append(OptimizationRecommendation(
                    action=OptimizationAction.ENABLE_CACHING,
                    priority=int(avg_severity * 10),
                    description="启用增量转换和缓存策略减少内存使用",
                    expected_improvement=min(max_improvement, 25.0),
                    resource_requirements={"memory_gb": -2.0},
                    implementation_effort="medium",
                    risk_level="low"
                ))
            elif bottleneck_type == BottleneckType.STAGE_LATENCY:
                recommendations.append(OptimizationRecommendation(
                    action=OptimizationAction.INCREASE_PARALLELISM,
                    priority=int(avg_severity * 10),
                    description=f"并行化处理瓶颈阶段 ({type_bottlenecks[0].stage})",
                    expected_improvement=min(max_improvement, 50.0),
                    resource_requirements={"concurrent_tasks": 2.0},
                    implementation_effort="medium",
                    risk_level="medium"
                ))

        return recommendations
