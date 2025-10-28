"""
Performance Data Storage and Historical Analysis Module

This module provides persistent storage and analysis capabilities for performance metrics.
Part of Story 3.1: 性能优化与扩展 (Phase 1: 架构扩展)

Features:
- Persistent storage of performance metrics
- Historical trend analysis
- Performance baseline comparison
- Bottleneck pattern detection
- Aggregation and statistical analysis
- Integration with Story 2.8 benchmark system

Author: BMM v6 Workflow
Version: 1.0
Date: 2025-10-28
"""

import json
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from collections import defaultdict
import statistics

from .performance_monitor import PerformanceSnapshot, PerformanceMetric, MetricType

logger = logging.getLogger(__name__)


class PerformanceDatabase:
    """
    SQLite-based persistent storage for performance metrics.

    Provides efficient storage and retrieval of historical performance data.
    """

    def __init__(self, db_path: Union[str, Path]) -> None:
        """
        Initialize the performance database.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_database()
        logger.info(f"Performance database initialized: {self.db_path}")

    def _init_database(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    operation_id TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    stage TEXT,
                    tags TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    operation_id TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp
                ON metrics(timestamp)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_operation
                ON metrics(operation_id)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp
                ON snapshots(timestamp)
            """)

            conn.commit()

    def store_metric(self, metric: PerformanceMetric) -> None:
        """
        Store a performance metric.

        Args:
            metric: PerformanceMetric to store
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO metrics
                (timestamp, operation_id, metric_type, value, unit, stage, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                metric.timestamp.isoformat(),
                metric.operation_id,
                metric.metric_type.value,
                metric.value,
                metric.unit,
                metric.stage,
                json.dumps(metric.tags) if metric.tags else None
            ))
            conn.commit()

    def store_snapshot(self, snapshot: PerformanceSnapshot) -> None:
        """
        Store a performance snapshot.

        Args:
            snapshot: PerformanceSnapshot to store
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO snapshots
                (timestamp, operation_id, data)
                VALUES (?, ?, ?)
            """, (
                snapshot.timestamp.isoformat(),
                snapshot.operation_id,
                json.dumps({
                    "metrics": {k.value: v for k, v in snapshot.metrics.items()},
                    "stages": snapshot.stages,
                    "system_info": snapshot.system_info
                })
            ))
            conn.commit()

    def get_metrics(
        self,
        operation_id: Optional[str] = None,
        metric_type: Optional[MetricType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        stage: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve metrics based on filters.

        Args:
            operation_id: Filter by operation ID
            metric_type: Filter by metric type
            start_time: Filter metrics after this time
            end_time: Filter metrics before this time
            stage: Filter by conversion stage
            limit: Maximum number of results

        Returns:
            List of metric dictionaries
        """
        query = "SELECT * FROM metrics WHERE 1=1"
        params = []

        if operation_id:
            query += " AND operation_id = ?"
            params.append(operation_id)

        if metric_type:
            query += " AND metric_type = ?"
            params.append(metric_type.value)

        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())

        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())

        if stage:
            query += " AND stage = ?"
            params.append(stage)

        query += " ORDER BY timestamp DESC"

        if limit:
            query += f" LIMIT {limit}"

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)

            results = []
            for row in cursor.fetchall():
                result = dict(row)
                result['timestamp'] = datetime.fromisoformat(result['timestamp'])
                if result['tags']:
                    result['tags'] = json.loads(result['tags'])
                results.append(result)

            return results

    def get_snapshots(
        self,
        operation_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve snapshots based on filters.

        Args:
            operation_id: Filter by operation ID
            start_time: Filter snapshots after this time
            end_time: Filter snapshots before this time
            limit: Maximum number of results

        Returns:
            List of snapshot dictionaries
        """
        query = "SELECT * FROM snapshots WHERE 1=1"
        params = []

        if operation_id:
            query += " AND operation_id = ?"
            params.append(operation_id)

        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())

        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())

        query += " ORDER BY timestamp DESC"

        if limit:
            query += f" LIMIT {limit}"

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)

            results = []
            for row in cursor.fetchall():
                result = dict(row)
                result['timestamp'] = datetime.fromisoformat(result['timestamp'])
                result['data'] = json.loads(result['data'])
                results.append(result)

            return results


class PerformanceAnalyzer:
    """
    Historical performance analysis and trend detection.

    Provides statistical analysis, trend detection, and bottleneck identification.
    """

    def __init__(self, database: PerformanceDatabase) -> None:
        """
        Initialize the performance analyzer.

        Args:
            database: PerformanceDatabase instance
        """
        self.database = database
        logger.info("PerformanceAnalyzer initialized")

    def analyze_trends(
        self,
        operation_id: str,
        metric_type: MetricType,
        time_range_days: int = 7
    ) -> Dict[str, Any]:
        """
        Analyze performance trends over time.

        Args:
            operation_id: Operation to analyze
            metric_type: Metric type to analyze
            time_range_days: Number of days to analyze

        Returns:
            Dictionary containing trend analysis
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(days=time_range_days)

        metrics = self.database.get_metrics(
            operation_id=operation_id,
            metric_type=metric_type,
            start_time=start_time,
            end_time=end_time
        )

        if not metrics:
            return {"error": "No metrics found for analysis"}

        values = [m['value'] for m in metrics]

        # Calculate statistics
        trend = {
            "operation_id": operation_id,
            "metric_type": metric_type.value,
            "time_range_days": time_range_days,
            "count": len(values),
            "statistics": {
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "stdev": statistics.stdev(values) if len(values) > 1 else 0.0
            },
            "time_span": {
                "start": metrics[-1]['timestamp'].isoformat(),
                "end": metrics[0]['timestamp'].isoformat()
            }
        }

        # Detect trend direction
        if len(values) >= 10:
            early_mean = statistics.mean(values[:len(values)//2])
            late_mean = statistics.mean(values[len(values)//2:])

            change_percent = ((late_mean - early_mean) / early_mean) * 100

            if change_percent > 5:
                trend["trend"] = "increasing"
                trend["change_percent"] = change_percent
            elif change_percent < -5:
                trend["trend"] = "decreasing"
                trend["change_percent"] = change_percent
            else:
                trend["trend"] = "stable"
                trend["change_percent"] = change_percent

        return trend

    def identify_bottlenecks(
        self,
        operation_id: str,
        time_range_hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Identify performance bottlenecks.

        Args:
            operation_id: Operation to analyze
            time_range_hours: Number of hours to analyze

        Returns:
            List of identified bottlenecks
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=time_range_hours)

        # Get all metric types
        metrics = self.database.get_metrics(
            operation_id=operation_id,
            start_time=start_time,
            end_time=end_time
        )

        if not metrics:
            return []

        bottlenecks = []

        # Group by metric type
        by_type = defaultdict(list)
        for metric in metrics:
            by_type[metric['metric_type']].append(metric['value'])

        # Check each metric type
        for metric_type, values in by_type.items():
            if not values:
                continue

            # Calculate statistical thresholds
            mean = statistics.mean(values)
            stdev = statistics.stdev(values) if len(values) > 1 else 0

            # Define thresholds for different metric types
            thresholds = {
                'latency': mean + (2 * stdev),
                'cpu_usage': 80.0,
                'memory_usage': 85.0,
                'npu_usage': 90.0
            }

            metric_key = metric_type
            threshold = thresholds.get(metric_key, mean + (2 * stdev))

            # Find outliers
            outliers = [v for v in values if v > threshold]

            if outliers:
                bottlenecks.append({
                    "metric_type": metric_type,
                    "outliers_count": len(outliers),
                    "outliers_percentage": (len(outliers) / len(values)) * 100,
                    "threshold": threshold,
                    "max_value": max(values),
                    "mean": mean
                })

        return bottlenecks

    def compare_baseline(
        self,
        operation_id: str,
        baseline_days: int = 30
    ) -> Dict[str, Any]:
        """
        Compare current performance against historical baseline.

        Args:
            operation_id: Operation to analyze
            baseline_days: Number of days for baseline

        Returns:
            Dictionary containing baseline comparison
        """
        end_time = datetime.now()

        # Get baseline period
        baseline_start = end_time - timedelta(days=baseline_days * 2)
        baseline_end = end_time - timedelta(days=baseline_days)

        # Get recent period
        recent_start = end_time - timedelta(days=baseline_days)

        comparison = {
            "operation_id": operation_id,
            "baseline_period": {
                "start": baseline_start.isoformat(),
                "end": baseline_end.isoformat()
            },
            "recent_period": {
                "start": recent_start.isoformat(),
                "end": end_time.isoformat()
            },
            "metric_comparisons": {}
        }

        # Analyze each metric type
        for metric_type in MetricType:
            # Get baseline metrics
            baseline_metrics = self.database.get_metrics(
                operation_id=operation_id,
                metric_type=metric_type,
                start_time=baseline_start,
                end_time=baseline_end
            )

            # Get recent metrics
            recent_metrics = self.database.get_metrics(
                operation_id=operation_id,
                metric_type=metric_type,
                start_time=recent_start,
                end_time=end_time
            )

            if baseline_metrics and recent_metrics:
                baseline_values = [m['value'] for m in baseline_metrics]
                recent_values = [m['value'] for m in recent_metrics]

                baseline_mean = statistics.mean(baseline_values)
                recent_mean = statistics.mean(recent_values)

                change_percent = ((recent_mean - baseline_mean) / baseline_mean) * 100

                comparison["metric_comparisons"][metric_type.value] = {
                    "baseline_mean": baseline_mean,
                    "recent_mean": recent_mean,
                    "change_percent": change_percent,
                    "trend": "worse" if change_percent > 10 else "better" if change_percent < -10 else "stable"
                }

        return comparison

    def get_aggregated_stats(
        self,
        operation_id: str,
        group_by: str = "hour"
    ) -> List[Dict[str, Any]]:
        """
        Get aggregated statistics grouped by time period.

        Args:
            operation_id: Operation to analyze
            group_by: Group by "hour", "day", or "week"

        Returns:
            List of aggregated statistics
        """
        # This is a simplified implementation
        # In production, you might use more sophisticated SQL queries

        end_time = datetime.now()
        start_time = end_time - timedelta(days=30)

        metrics = self.database.get_metrics(
            operation_id=operation_id,
            start_time=start_time,
            end_time=end_time
        )

        if not metrics:
            return []

        # Group metrics by time period
        grouped = defaultdict(list)
        for metric in metrics:
            timestamp = metric['timestamp']
            if group_by == "hour":
                key = timestamp.strftime("%Y-%m-%d %H:00")
            elif group_by == "day":
                key = timestamp.strftime("%Y-%m-%d")
            else:  # week
                key = timestamp.strftime("%Y-W%U")

            grouped[key].append(metric['value'])

        # Calculate statistics for each group
        results = []
        for period, values in sorted(grouped.items()):
            results.append({
                "period": period,
                "count": len(values),
                "mean": statistics.mean(values),
                "min": min(values),
                "max": max(values)
            })

        return results


class PerformanceStorage:
    """
    High-level performance storage interface.

    Combines database storage and analysis capabilities.
    """

    def __init__(
        self,
        storage_dir: Union[str, Path],
        db_filename: str = "performance.db"
    ) -> None:
        """
        Initialize performance storage.

        Args:
            storage_dir: Directory to store performance data
            db_filename: Database filename
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        db_path = self.storage_dir / db_filename
        self.database = PerformanceDatabase(db_path)
        self.analyzer = PerformanceAnalyzer(self.database)

        logger.info(f"PerformanceStorage initialized: {self.storage_dir}")

    def store_metrics(self, metrics: List[PerformanceMetric]) -> None:
        """
        Store multiple metrics.

        Args:
            metrics: List of PerformanceMetric objects
        """
        for metric in metrics:
            self.database.store_metric(metric)

    def store_snapshot(self, snapshot: PerformanceSnapshot) -> None:
        """
        Store a performance snapshot.

        Args:
            snapshot: PerformanceSnapshot object
        """
        self.database.store_snapshot(snapshot)

    def analyze_performance(
        self,
        operation_id: str,
        analysis_type: str = "trends"
    ) -> Dict[str, Any]:
        """
        Analyze performance data.

        Args:
            operation_id: Operation to analyze
            analysis_type: Type of analysis ("trends", "bottlenecks", "baseline", "aggregated")

        Returns:
            Analysis results
        """
        if analysis_type == "trends":
            return self.analyzer.analyze_trends(operation_id, MetricType.LATENCY)
        elif analysis_type == "bottlenecks":
            return {"bottlenecks": self.analyzer.identify_bottlenecks(operation_id)}
        elif analysis_type == "baseline":
            return self.analyzer.compare_baseline(operation_id)
        elif analysis_type == "aggregated":
            return {"stats": self.analyzer.get_aggregated_stats(operation_id)}
        else:
            return {"error": f"Unknown analysis type: {analysis_type}"}

    def export_analysis(
        self,
        operation_id: str,
        output_path: Union[str, Path],
        analysis_types: Optional[List[str]] = None
    ) -> None:
        """
        Export comprehensive performance analysis.

        Args:
            operation_id: Operation to analyze
            output_path: Path to export file
            analysis_types: List of analysis types to include
        """
        if analysis_types is None:
            analysis_types = ["trends", "bottlenecks", "baseline", "aggregated"]

        export_data = {
            "operation_id": operation_id,
            "export_timestamp": datetime.now().isoformat(),
            "analyses": {}
        }

        for analysis_type in analysis_types:
            export_data["analyses"][analysis_type] = self.analyze_performance(
                operation_id, analysis_type
            )

        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)

        logger.info(f"Exported performance analysis to: {output_path}")
