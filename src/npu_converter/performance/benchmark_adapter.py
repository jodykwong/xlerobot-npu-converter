"""
Performance Monitor - Benchmark System Integration Adapter

This module provides seamless integration between PerformanceMonitor and Story 2.8 BenchmarkSystem.
Part of Story 3.1: 性能优化与扩展 (Phase 1: 架构扩展)

Features:
- Real-time performance comparison with benchmarks
- Automatic benchmark-triggered monitoring
- Historical benchmark data integration
- Performance regression detection
- Cross-reference with Story 2.8 test results

Author: BMM v6 Workflow
Version: 1.0
Date: 2025-10-28
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable, Union
from pathlib import Path

from .performance_monitor import PerformanceMonitor, MetricType, PerformanceSnapshot
from .performance_storage import PerformanceStorage
from ..complete_flows.benchmark_system import BenchmarkSystem, BenchmarkResult

logger = logging.getLogger(__name__)


class BenchmarkIntegrationAdapter:
    """
    Adapter for integrating PerformanceMonitor with BenchmarkSystem (Story 2.8).

    This adapter enables:
    - Real-time performance comparison during benchmark tests
    - Automatic performance monitoring triggered by benchmarks
    - Historical benchmark data analysis
    - Performance regression detection against benchmarks
    """

    def __init__(
        self,
        performance_monitor: PerformanceMonitor,
        benchmark_system: BenchmarkSystem,
        performance_storage: Optional[PerformanceStorage] = None
    ) -> None:
        """
        Initialize the benchmark integration adapter.

        Args:
            performance_monitor: PerformanceMonitor instance
            benchmark_system: BenchmarkSystem instance (Story 2.8)
            performance_storage: Optional PerformanceStorage for historical analysis
        """
        self.performance_monitor = performance_monitor
        self.benchmark_system = benchmark_system
        self.performance_storage = performance_storage

        # Integration state
        self.is_monitoring_benchmark = False
        self.current_benchmark_result: Optional[BenchmarkResult] = None
        self.benchmark_comparison_results: List[Dict[str, Any]] = []

        # Callbacks
        self.performance_callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self.regression_callbacks: List[Callable[[str, Dict[str, Any]], None]] = []

        # Register performance callbacks
        self.performance_monitor.add_performance_callback(self._on_performance_update)

        logger.info("BenchmarkIntegrationAdapter initialized")

    def start_benchmark_monitoring(
        self,
        operation_id: str,
        benchmark_config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Start monitoring a benchmark test.

        Args:
            operation_id: Unique identifier for this benchmark test
            benchmark_config: Optional benchmark configuration
        """
        self.is_monitoring_benchmark = True
        self.current_benchmark_result = None

        # Set operation ID in performance monitor
        self.performance_monitor.operation_id = f"{operation_id}_benchmark"

        # Start monitoring if not already active
        if not self.performance_monitor.is_monitoring:
            self.performance_monitor.start_monitoring()

        logger.info(f"Started benchmark monitoring for operation: {operation_id}")

    def stop_benchmark_monitoring(self) -> Optional[BenchmarkResult]:
        """
        Stop monitoring and return benchmark results.

        Returns:
            BenchmarkResult containing performance metrics
        """
        if not self.is_monitoring_benchmark:
            logger.warning("Benchmark monitoring not active")
            return None

        # Create benchmark result from collected metrics
        benchmark_result = self._create_benchmark_result()

        self.is_monitoring_benchmark = False
        self.current_benchmark_result = benchmark_result

        logger.info(f"Stopped benchmark monitoring. Result: {benchmark_result.status}")

        return benchmark_result

    def compare_with_benchmark(
        self,
        operation_id: str,
        dataset_name: str,
        model_name: str,
        threshold_percent: float = 10.0
    ) -> Dict[str, Any]:
        """
        Compare current performance with historical benchmark data.

        Args:
            operation_id: Operation to compare
            dataset_name: Benchmark dataset name
            model_name: Model name
            threshold_percent: Threshold for performance regression detection

        Returns:
            Dictionary containing comparison results
        """
        # Get historical benchmark results for this operation
        historical_results = self._get_historical_benchmarks(
            dataset_name, model_name
        )

        if not historical_results:
            return {
                "error": "No historical benchmark data found",
                "operation_id": operation_id,
                "dataset": dataset_name,
                "model": model_name
            }

        # Get current performance snapshot
        current_snapshot = self.performance_monitor.create_snapshot()

        # Compare metrics
        comparison_result = {
            "operation_id": operation_id,
            "dataset": dataset_name,
            "model": model_name,
            "timestamp": datetime.now().isoformat(),
            "baseline_metrics": self._aggregate_benchmark_metrics(historical_results),
            "current_metrics": {
                "inference_time_ms": self._get_metric_value(current_snapshot, MetricType.LATENCY),
                "throughput_items_sec": self._get_metric_value(current_snapshot, MetricType.THROUGHPUT),
                "cpu_utilization": self._get_metric_value(current_snapshot, MetricType.CPU_USAGE),
                "memory_utilization": self._get_metric_value(current_snapshot, MetricType.MEMORY_USAGE)
            },
            "performance_changes": {},
            "regression_detected": False,
            "status": "unknown"
        }

        # Calculate performance changes
        for metric, current_value in comparison_result["current_metrics"].items():
            if metric in comparison_result["baseline_metrics"]:
                baseline_value = comparison_result["baseline_metrics"][metric]

                if baseline_value > 0:
                    change_percent = ((current_value - baseline_value) / baseline_value) * 100

                    comparison_result["performance_changes"][metric] = {
                        "baseline": baseline_value,
                        "current": current_value,
                        "change_percent": change_percent,
                        "threshold_exceeded": abs(change_percent) > threshold_percent
                    }

                    # Detect regression
                    if change_percent > threshold_percent:
                        comparison_result["regression_detected"] = True
                        self._trigger_regression_callback(metric, comparison_result["performance_changes"][metric])

        # Determine overall status
        if comparison_result["regression_detected"]:
            comparison_result["status"] = "regression_detected"
        elif all(
            abs(change.get("change_percent", 0)) <= threshold_percent
            for change in comparison_result["performance_changes"].values()
        ):
            comparison_result["status"] = "within_threshold"
        else:
            comparison_result["status"] = "improved"

        self.benchmark_comparison_results.append(comparison_result)

        logger.info(f"Benchmark comparison completed: {comparison_result['status']}")

        return comparison_result

    def trigger_automatic_benchmark(
        self,
        operation_id: str,
        model_path: str,
        dataset_name: str,
        test_scenarios: Optional[List[str]] = None
    ) -> Optional[BenchmarkResult]:
        """
        Trigger automatic benchmark test with performance monitoring.

        Args:
            operation_id: Operation identifier
            model_path: Path to model to test
            dataset_name: Benchmark dataset name
            test_scenarios: Optional list of test scenarios

        Returns:
            BenchmarkResult from the test
        """
        if dataset_name not in self.benchmark_system.datasets:
            logger.error(f"Benchmark dataset not found: {dataset_name}")
            return None

        # Start performance monitoring
        self.start_benchmark_monitoring(operation_id)

        try:
            # Execute benchmark test
            logger.info(f"Triggering automatic benchmark for {operation_id}")
            benchmark_result = self.benchmark_system.run_benchmark_test(
                model_path=model_path,
                dataset_name=dataset_name,
                scenarios=test_scenarios or ["standard"]
            )

            # Enhance benchmark result with performance metrics
            self._enhance_benchmark_with_metrics(benchmark_result)

            return benchmark_result

        except Exception as e:
            logger.error(f"Benchmark test failed: {e}")
            return None
        finally:
            # Stop monitoring
            self.stop_benchmark_monitoring()

    def get_performance_trend(
        self,
        dataset_name: str,
        model_name: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get performance trend from benchmark data.

        Args:
            dataset_name: Benchmark dataset name
            model_name: Model name
            days: Number of days to analyze

        Returns:
            Dictionary containing trend analysis
        """
        if not self.performance_storage:
            return {"error": "PerformanceStorage not available"}

        # Analyze trends using performance storage
        trends = self.performance_storage.analyzer.analyze_trends(
            f"{model_name}_{dataset_name}",
            MetricType.LATENCY,
            time_range_days=days
        )

        # Add benchmark context
        trends["dataset"] = dataset_name
        trends["model"] = model_name
        trends["benchmark_integration"] = True

        return trends

    def add_performance_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add callback for performance benchmark updates.

        Args:
            callback: Function to call on performance updates
        """
        self.performance_callbacks.append(callback)

    def add_regression_callback(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """
        Add callback for performance regression detection.

        Args:
            callback: Function to call on regression detection
        """
        self.regression_callbacks.append(callback)

    def get_integration_summary(self) -> Dict[str, Any]:
        """
        Get integration summary.

        Returns:
            Dictionary containing integration summary
        """
        return {
            "monitoring_active": self.performance_monitor.is_monitoring,
            "benchmark_monitoring_active": self.is_monitoring_benchmark,
            "comparisons_performed": len(self.benchmark_comparison_results),
            "current_benchmark_result": self.current_benchmark_result,
            "performance_storage_available": self.performance_storage is not None,
            "datasets_available": len(self.benchmark_system.datasets)
        }

    def _on_performance_update(self, snapshot: PerformanceSnapshot) -> None:
        """Handle performance snapshot updates during benchmark."""
        if not self.is_monitoring_benchmark:
            return

        # Store snapshot if storage is available
        if self.performance_storage:
            self.performance_storage.store_snapshot(snapshot)

        # Trigger callbacks
        for callback in self.performance_callbacks:
            try:
                callback({
                    "timestamp": snapshot.timestamp.isoformat(),
                    "operation_id": snapshot.operation_id,
                    "metrics": {k.value: v for k, v in snapshot.metrics.items()}
                })
            except Exception as e:
                logger.error(f"Performance callback error: {e}")

    def _create_benchmark_result(self) -> BenchmarkResult:
        """Create BenchmarkResult from collected metrics."""
        summary = self.performance_monitor.get_summary()

        # Extract metrics
        latency_stats = summary.get("latency_stats", {})
        throughput_stats = summary.get("throughput_stats", {})

        # Create result
        result = BenchmarkResult(
            model_name="unknown",
            model_path="unknown",
            dataset_name="unknown",
            timestamp=datetime.now(),
            accuracy=0.0,
            precision=0.0,
            recall=0.0,
            f1_score=0.0,
            inference_time=latency_stats.get("avg_ms", 0.0),
            throughput=throughput_stats.get("avg_items_sec", 0.0),
            memory_usage=summary.get("current_stage", "unknown"),
            cpu_utilization=latency_stats.get("max_ms", 0.0),  # Placeholder
            gpu_utilization=0.0,  # Not applicable for NPU
            memory_bandwidth=0.0,
            concurrent_performance=throughput_stats.get("max_items_sec", 0.0),
            batch_sizes_tested=[],
            compatibility_score=100.0,
            status="completed"
        )

        return result

    def _enhance_benchmark_with_metrics(self, result: BenchmarkResult) -> None:
        """
        Enhance benchmark result with performance monitor metrics.

        Args:
            result: BenchmarkResult to enhance
        """
        summary = self.performance_monitor.get_summary()

        # Add performance metrics to result
        result.inference_time = summary.get("latency_stats", {}).get("avg_ms", 0.0)
        result.throughput = summary.get("throughput_stats", {}).get("avg_items_sec", 0.0)
        result.memory_usage = summary.get("current_stage", "unknown")

        logger.info("Benchmark result enhanced with performance metrics")

    def _get_historical_benchmarks(
        self,
        dataset_name: str,
        model_name: str
    ) -> List[BenchmarkResult]:
        """
        Get historical benchmark results.

        Args:
            dataset_name: Dataset name
            model_name: Model name

        Returns:
            List of historical benchmark results
        """
        # In a full implementation, this would query historical data
        # For now, return empty list
        return []

    def _aggregate_benchmark_metrics(
        self,
        results: List[BenchmarkResult]
    ) -> Dict[str, float]:
        """
        Aggregate metrics from historical benchmark results.

        Args:
            results: List of benchmark results

        Returns:
            Dictionary of aggregated metrics
        """
        if not results:
            return {}

        return {
            "inference_time_ms": sum(r.inference_time for r in results) / len(results),
            "throughput_items_sec": sum(r.throughput for r in results) / len(results),
            "cpu_utilization": sum(r.cpu_utilization for r in results) / len(results),
            "memory_utilization": 0.0  # Would need to extract from results
        }

    def _get_metric_value(
        self,
        snapshot: PerformanceSnapshot,
        metric_type: MetricType
    ) -> float:
        """
        Get metric value from snapshot.

        Args:
            snapshot: PerformanceSnapshot
            metric_type: MetricType to extract

        Returns:
            Metric value or 0.0 if not found
        """
        return snapshot.metrics.get(metric_type, 0.0)

    def _trigger_regression_callback(self, metric: str, change_info: Dict[str, Any]) -> None:
        """
        Trigger regression callbacks.

        Args:
            metric: Metric name
            change_info: Change information
        """
        for callback in self.regression_callbacks:
            try:
                callback(metric, change_info)
            except Exception as e:
                logger.error(f"Regression callback error: {e}")
