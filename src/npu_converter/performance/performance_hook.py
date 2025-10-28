"""
Performance Optimization Hook for BaseConversionFlow

This module provides performance monitoring and optimization hooks for BaseConversionFlow.
Part of Story 3.1: 性能优化与扩展 (Phase 1: 架构扩展)

Features:
- Performance monitoring hooks for conversion stages
- Asynchronous conversion support
- Performance optimization callbacks
- Fine-grained conversion process monitoring
- Integration with PerformanceMonitor

Author: BMM v6 Workflow
Version: 1.0
Date: 2025-10-28
"""

import asyncio
import logging
import threading
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Union
from functools import wraps
from enum import Enum

from .performance_monitor import PerformanceMonitor, MetricType
from .performance_storage import PerformanceStorage
from .benchmark_adapter import BenchmarkIntegrationAdapter
from ..converters.base_conversion_flow import ConversionStage

logger = logging.getLogger(__name__)


class OptimizationStrategy(Enum):
    """Performance optimization strategies."""
    AGGRESSIVE = "aggressive"
    BALANCED = "balanced"
    CONSERVATIVE = "conservative"
    ADAPTIVE = "adaptive"


class PerformanceHook:
    """
    Performance monitoring and optimization hook for BaseConversionFlow.

    This class provides:
    - Performance monitoring for conversion stages
    - Optimization callback integration
    - Asynchronous conversion support
    - Fine-grained performance tracking
    """

    def __init__(
        self,
        operation_id: str,
        performance_monitor: Optional[PerformanceMonitor] = None,
        optimization_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED
    ) -> None:
        """
        Initialize the performance hook.

        Args:
            operation_id: Unique operation identifier
            performance_monitor: Optional PerformanceMonitor instance
            optimization_strategy: Performance optimization strategy
        """
        self.operation_id = operation_id
        self.performance_monitor = performance_monitor or PerformanceMonitor(operation_id)
        self.optimization_strategy = optimization_strategy

        # Optimization state
        self.is_optimization_enabled = True
        self.is_async_mode = False
        self._optimization_callbacks: List[Callable] = []
        self._stage_hooks: Dict[str, Callable] = {}
        self._performance_thresholds: Dict[str, float] = {
            "stage_latency_ms": 300000.0,  # 5 minutes
            "cpu_usage_percent": 80.0,
            "memory_usage_percent": 85.0
        }

        # Caching and optimization
        self._cache: Dict[str, Any] = {}
        self._optimization_cache_enabled = True
        self._cache_hits = 0
        self._cache_misses = 0

        # Asynchronous execution
        self._executor_thread_pool_size = 4
        self._executor = None

        logger.info(f"PerformanceHook initialized for {operation_id}")

    def enable_optimization(self, strategy: OptimizationStrategy) -> None:
        """
        Enable performance optimization.

        Args:
            strategy: Optimization strategy to use
        """
        self.optimization_strategy = strategy
        self.is_optimization_enabled = True
        logger.info(f"Performance optimization enabled: {strategy.value}")

    def disable_optimization(self) -> None:
        """Disable performance optimization."""
        self.is_optimization_enabled = False
        logger.info("Performance optimization disabled")

    def enable_async_mode(self, thread_pool_size: int = 4) -> None:
        """
        Enable asynchronous conversion mode.

        Args:
            thread_pool_size: Size of thread pool for async execution
        """
        self.is_async_mode = True
        self._executor_thread_pool_size = thread_pool_size
        logger.info(f"Asynchronous mode enabled with thread pool size: {thread_pool_size}")

    def add_optimization_callback(self, callback: Callable) -> None:
        """
        Add optimization callback.

        Args:
            callback: Function to call for optimization
        """
        self._optimization_callbacks.append(callback)

    def add_stage_hook(
        self,
        stage: Union[str, ConversionStage],
        hook: Callable[[str, Dict[str, Any]], Any]
    ) -> None:
        """
        Add a stage-specific performance hook.

        Args:
            stage: Stage name or ConversionStage enum
            hook: Hook function to execute for this stage
        """
        stage_name = stage.value if isinstance(stage, ConversionStage) else stage
        self._stage_hooks[stage_name] = hook

    def monitor_stage_start(self, stage_name: str) -> None:
        """
        Monitor the start of a conversion stage.

        Args:
            stage_name: Name of the stage
        """
        # Set stage in performance monitor
        self.performance_monitor.set_stage(stage_name)

        # Record stage start latency
        self.performance_monitor.record_latency(stage_name, 0.0)

        # Trigger stage hook
        if stage_name in self._stage_hooks:
            try:
                self._stage_hooks[stage_name]("start", {"stage": stage_name})
            except Exception as e:
                logger.error(f"Stage hook error for {stage_name}: {e}")

        logger.debug(f"Monitoring started for stage: {stage_name}")

    def monitor_stage_end(self, stage_name: str, result: Any, duration_ms: float) -> None:
        """
        Monitor the end of a conversion stage.

        Args:
            stage_name: Name of the stage
            result: Stage execution result
            duration_ms: Stage execution duration in milliseconds
        """
        # Record stage latency
        self.performance_monitor.record_latency(stage_name, duration_ms)

        # Trigger optimization callbacks
        if self.is_optimization_enabled:
            self._trigger_optimization_callbacks(stage_name, result, duration_ms)

        # Check performance thresholds
        self._check_performance_thresholds(stage_name, duration_ms)

        # Trigger stage hook
        if stage_name in self._stage_hooks:
            try:
                self._stage_hooks[stage_name](
                    "end",
                    {"stage": stage_name, "result": result, "duration_ms": duration_ms}
                )
            except Exception as e:
                logger.error(f"Stage hook error for {stage_name}: {e}")

        logger.debug(f"Monitoring completed for stage: {stage_name} ({duration_ms:.2f}ms)")

    def get_cached_result(self, cache_key: str) -> Optional[Any]:
        """
        Get result from cache.

        Args:
            cache_key: Cache key

        Returns:
            Cached result or None
        """
        if not self._optimization_cache_enabled:
            return None

        if cache_key in self._cache:
            self._cache_hits += 1
            logger.debug(f"Cache hit for key: {cache_key}")
            return self._cache[cache_key]

        self._cache_misses += 1
        return None

    def cache_result(self, cache_key: str, result: Any) -> None:
        """
        Cache a result.

        Args:
            cache_key: Cache key
            result: Result to cache
        """
        if not self._optimization_cache_enabled:
            return

        self._cache[cache_key] = result
        logger.debug(f"Cached result for key: {cache_key}")

    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.

        Returns:
            Dictionary containing cache statistics
        """
        total = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total * 100) if total > 0 else 0

        return {
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "total": total,
            "hit_rate_percent": round(hit_rate, 2)
        }

    def clear_cache(self) -> None:
        """Clear the performance cache."""
        self._cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        logger.info("Performance cache cleared")

    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive performance summary.

        Returns:
            Dictionary containing performance summary
        """
        summary = self.performance_monitor.get_summary()
        summary["cache_stats"] = self.get_cache_stats()
        summary["optimization_enabled"] = self.is_optimization_enabled
        summary["optimization_strategy"] = self.optimization_strategy.value
        summary["async_mode"] = self.is_async_mode

        return summary

    def _trigger_optimization_callbacks(
        self,
        stage_name: str,
        result: Any,
        duration_ms: float
    ) -> None:
        """
        Trigger optimization callbacks.

        Args:
            stage_name: Stage name
            result: Stage result
            duration_ms: Duration in milliseconds
        """
        for callback in self._optimization_callbacks:
            try:
                callback(stage_name, result, duration_ms)
            except Exception as e:
                logger.error(f"Optimization callback error: {e}")

    def _check_performance_thresholds(
        self,
        stage_name: str,
        duration_ms: float
    ) -> None:
        """
        Check if stage performance exceeds thresholds.

        Args:
            stage_name: Stage name
            duration_ms: Duration in milliseconds
        """
        threshold = self._performance_thresholds.get("stage_latency_ms", 300000.0)

        if duration_ms > threshold:
            logger.warning(
                f"Stage {stage_name} exceeded latency threshold: "
                f"{duration_ms:.2f}ms > {threshold:.2f}ms"
            )

    def __enter__(self):
        """Context manager entry."""
        self.performance_monitor.start_monitoring()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.performance_monitor.stop_monitoring()


def performance_monitored(
    stage_name: str,
    hook: Optional[PerformanceHook] = None,
    use_cache: bool = True,
    cache_key_prefix: str = "stage"
):
    """
    Decorator for monitoring conversion stages with performance hooks.

    Args:
        stage_name: Name of the conversion stage
        hook: PerformanceHook instance
        use_cache: Whether to use caching for this stage
        cache_key_prefix: Prefix for cache keys

    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get or create hook
            if hook is None:
                # Create a default hook if not provided
                operation_id = f"func_{func.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                hook = PerformanceHook(operation_id)

            # Generate cache key
            cache_key = f"{cache_key_prefix}:{stage_name}:{hash(str(args) + str(kwargs))}"

            # Check cache
            if use_cache:
                cached_result = hook.get_cached_result(cache_key)
                if cached_result is not None:
                    return cached_result

            # Monitor stage start
            hook.monitor_stage_start(stage_name)
            start_time = datetime.now()

            try:
                # Execute function
                result = func(*args, **kwargs)

                # Calculate duration
                duration_ms = (datetime.now() - start_time).total_seconds() * 1000

                # Monitor stage end
                hook.monitor_stage_end(stage_name, result, duration_ms)

                # Cache result
                if use_cache:
                    hook.cache_result(cache_key, result)

                return result

            except Exception as e:
                # Calculate duration for error case
                duration_ms = (datetime.now() - start_time).total_seconds() * 1000

                # Log error
                logger.error(
                    f"Stage {stage_name} failed after {duration_ms:.2f}ms: {e}"
                )

                raise

        return wrapper
    return decorator


class AsyncConversionExecutor:
    """
    Asynchronous conversion executor for improved performance.

    Provides parallel execution of independent conversion stages.
    """

    def __init__(
        self,
        max_workers: int = 4,
        performance_hook: Optional[PerformanceHook] = None
    ) -> None:
        """
        Initialize async executor.

        Args:
            max_workers: Maximum number of worker threads
            performance_hook: PerformanceHook instance
        """
        self.max_workers = max_workers
        self.performance_hook = performance_hook
        self._lock = threading.Lock()

    async def execute_parallel_stages(
        self,
        stages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Execute multiple stages in parallel.

        Args:
            stages: List of stage configurations

        Returns:
            Dictionary of stage results
        """
        logger.info(f"Executing {len(stages)} stages in parallel")

        # Execute stages concurrently
        tasks = []
        for stage_config in stages:
            stage_name = stage_config["name"]
            stage_func = stage_config["func"]
            stage_args = stage_config.get("args", ())
            stage_kwargs = stage_config.get("kwargs", {})

            task = asyncio.create_task(
                self._execute_single_stage(stage_name, stage_func, stage_args, stage_kwargs)
            )
            tasks.append((stage_name, task))

        # Wait for all tasks to complete
        results = {}
        for stage_name, task in tasks:
            try:
                result = await task
                results[stage_name] = result
            except Exception as e:
                logger.error(f"Stage {stage_name} failed: {e}")
                results[stage_name] = {"error": str(e)}

        return results

    async def _execute_single_stage(
        self,
        stage_name: str,
        stage_func: Callable,
        args: tuple,
        kwargs: dict
    ) -> Any:
        """
        Execute a single stage with monitoring.

        Args:
            stage_name: Stage name
            stage_func: Stage function
            args: Function arguments
            kwargs: Function keyword arguments

        Returns:
            Stage execution result
        """
        if self.performance_hook:
            self.performance_hook.monitor_stage_start(stage_name)

        start_time = datetime.now()

        try:
            # Execute stage function
            if asyncio.iscoroutinefunction(stage_func):
                result = await stage_func(*args, **kwargs)
            else:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: stage_func(*args, **kwargs)
                )

            # Calculate duration
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000

            if self.performance_hook:
                self.performance_hook.monitor_stage_end(stage_name, result, duration_ms)

            return result

        except Exception as e:
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000

            if self.performance_hook:
                self.performance_hook.monitor_stage_end(stage_name, None, duration_ms)

            raise
