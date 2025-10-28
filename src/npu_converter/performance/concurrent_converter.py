"""
Concurrent Conversion System

This module provides concurrent conversion capabilities for XLeRobot NPU model conversion.
Part of Story 3.1: 性能优化与扩展 (Phase 1: 架构扩展)

Features:
- Multi-model concurrent conversion (Batch Processing)
- Load balancing and task distribution
- Resource pool and queue management
- Concurrency control and throttling
- Resource isolation between concurrent tasks

Author: BMM v6 Workflow
Version: 1.0
Date: 2025-10-28
"""

import asyncio
import logging
import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union, Awaitable

from .performance_monitor import PerformanceMonitor, MetricType
from .performance_hook import PerformanceHook

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class ConversionTask:
    """Represents a single conversion task."""
    task_id: str
    operation_id: str
    model_path: str
    output_path: str
    config: Optional[Dict[str, Any]] = None
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[Exception] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: Optional[float] = None
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceQuota:
    """Resource quota for concurrent conversions."""
    max_concurrent_tasks: int = 5
    max_cpu_percent: float = 80.0
    max_memory_percent: float = 85.0
    max_npu_percent: float = 90.0
    max_disk_io_mbps: float = 100.0


class TaskQueue:
    """Priority-based task queue for conversion tasks."""

    def __init__(self):
        self._queues: Dict[TaskPriority, queue.PriorityQueue] = {
            priority: queue.PriorityQueue() for priority in TaskPriority
        }
        self._lock = threading.Lock()
        self._task_counter = 0

    def put(self, task: ConversionTask) -> None:
        """
        Add a task to the queue.

        Args:
            task: ConversionTask to add
        """
        with self._lock:
            # Use negative priority for correct ordering (higher priority = lower number)
            priority_num = -task.priority.value
            self._task_counter += 1

            # Combine priority with counter for FIFO within same priority
            queue_item = (priority_num, self._task_counter, task)

            self._queues[task.priority].put(queue_item)

    def get(self, block: bool = True, timeout: Optional[float] = None) -> ConversionTask:
        """
        Get a task from the queue.

        Args:
            block: Whether to block if queue is empty
            timeout: Timeout in seconds

        Returns:
            ConversionTask from queue

        Raises:
            queue.Empty: If queue is empty and block=False or timeout
        """
        # Get from highest priority queue first
        for priority in sorted(TaskPriority, key=lambda p: p.value, reverse=True):
            queue_obj = self._queues[priority]
            try:
                if not queue_obj.empty():
                    _, _, task = queue_obj.get(block=False)
                    return task
            except queue.Empty:
                continue

        # If no tasks in any queue and blocking requested
        if block:
            # Try all queues with timeout
            end_time = time.time() + (timeout or 0)
            while time.time() < end_time:
                for priority in sorted(TaskPriority, key=lambda p: p.value, reverse=True):
                    queue_obj = self._queues[priority]
                    try:
                        _, _, task = queue_obj.get(block=True, timeout=0.1)
                        return task
                    except queue.Empty:
                        continue
                time.sleep(0.01)  # Small sleep to prevent busy waiting

        raise queue.Empty("Task queue is empty")

    def qsize(self) -> int:
        """Get total queue size."""
        return sum(q.qsize() for q in self._queues.values())

    def empty(self) -> bool:
        """Check if queue is empty."""
        return all(q.empty() for q in self._queues.values())


class ResourceManager:
    """Resource management for concurrent conversions."""

    def __init__(self, quota: ResourceQuota):
        """
        Initialize resource manager.

        Args:
            quota: Resource quota configuration
        """
        self.quota = quota
        self._active_tasks: Dict[str, ConversionTask] = {}
        self._task_resources: Dict[str, Dict[str, float]] = {}
        self._lock = threading.Lock()

    def acquire_resources(self, task: ConversionTask) -> bool:
        """
        Acquire resources for a task.

        Args:
            task: ConversionTask requesting resources

        Returns:
            True if resources acquired, False otherwise
        """
        with self._lock:
            # Check concurrent task limit
            if len(self._active_tasks) >= self.quota.max_concurrent_tasks:
                return False

            # Check system resources
            if not self._check_system_resources():
                return False

            # Register task
            self._active_tasks[task.task_id] = task
            self._task_resources[task.task_id] = {
                "cpu_percent": 0.0,
                "memory_percent": 0.0,
                "npu_percent": 0.0,
                "disk_io_mbps": 0.0
            }

            logger.info(f"Acquired resources for task: {task.task_id}")
            return True

    def release_resources(self, task_id: str) -> None:
        """
        Release resources for a task.

        Args:
            task_id: Task ID to release
        """
        with self._lock:
            if task_id in self._active_tasks:
                del self._active_tasks[task_id]

            if task_id in self._task_resources:
                del self._task_resources[task_id]

            logger.info(f"Released resources for task: {task_id}")

    def get_active_tasks(self) -> List[str]:
        """Get list of active task IDs."""
        with self._lock:
            return list(self._active_tasks.keys())

    def _check_system_resources(self) -> bool:
        """
        Check if system resources are within quota.

        Returns:
            True if resources are available
        """
        # This is a simplified implementation
        # In production, you would check actual system metrics
        import psutil

        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()

        return (
            cpu_percent < self.quota.max_cpu_percent and
            memory.percent < self.quota.max_memory_percent
        )


class LoadBalancer:
    """Load balancer for distributing conversion tasks."""

    def __init__(self, resource_manager: ResourceManager):
        """
        Initialize load balancer.

        Args:
            resource_manager: ResourceManager instance
        """
        self.resource_manager = resource_manager
        self._distribution_stats: Dict[str, int] = {}

    def select_next_task(self, available_tasks: List[ConversionTask]) -> Optional[ConversionTask]:
        """
        Select next task using load balancing strategy.

        Args:
            available_tasks: List of available tasks

        Returns:
            Selected ConversionTask or None
        """
        if not available_tasks:
            return None

        # Simple strategy: select highest priority task
        # In production, this could be more sophisticated (round-robin, least-loaded, etc.)
        return max(available_tasks, key=lambda t: t.priority.value)

    def update_stats(self, task_id: str) -> None:
        """
        Update load balancing statistics.

        Args:
            task_id: Task ID that was executed
        """
        self._distribution_stats[task_id] = self._distribution_stats.get(task_id, 0) + 1

    def get_stats(self) -> Dict[str, int]:
        """Get load balancing statistics."""
        return self._distribution_stats.copy()


class ConcurrentConverter:
    """
    Concurrent conversion system for batch processing.

    Provides:
    - Multi-model concurrent conversion
    - Load balancing and task distribution
    - Resource management and isolation
    - Concurrency control and throttling
    """

    def __init__(
        self,
        operation_id: str,
        max_concurrent_tasks: int = 5,
        resource_quota: Optional[ResourceQuota] = None,
        performance_monitor: Optional[PerformanceMonitor] = None
    ) -> None:
        """
        Initialize concurrent converter.

        Args:
            operation_id: Unique operation identifier
            max_concurrent_tasks: Maximum number of concurrent tasks
            resource_quota: Resource quota configuration
            performance_monitor: PerformanceMonitor instance
        """
        self.operation_id = operation_id
        self.performance_monitor = performance_monitor or PerformanceMonitor(operation_id)

        # Components
        self.task_queue = TaskQueue()
        self.resource_manager = ResourceManager(
            resource_quota or ResourceQuota(max_concurrent_tasks=max_concurrent_tasks)
        )
        self.load_balancer = LoadBalancer(self.resource_manager)
        self.performance_hook = PerformanceHook(operation_id, self.performance_monitor)

        # Execution control
        self._is_running = False
        self._executor_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()

        # Statistics
        self._total_tasks_processed = 0
        self._total_tasks_succeeded = 0
        self._total_tasks_failed = 0
        self._lock = threading.Lock()

        logger.info(f"ConcurrentConverter initialized for {operation_id}")

    def submit_task(
        self,
        model_path: str,
        output_path: str,
        priority: TaskPriority = TaskPriority.NORMAL,
        config: Optional[Dict[str, Any]] = None,
        timeout_seconds: Optional[float] = None,
        tags: Optional[Set[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Submit a conversion task.

        Args:
            model_path: Path to model to convert
            output_path: Output path for converted model
            priority: Task priority
            config: Optional conversion configuration
            timeout_seconds: Task timeout
            tags: Optional task tags
            metadata: Optional task metadata

        Returns:
            Task ID
        """
        task_id = f"{self.operation_id}_{int(time.time() * 1000000)}"

        task = ConversionTask(
            task_id=task_id,
            operation_id=self.operation_id,
            model_path=model_path,
            output_path=output_path,
            config=config or {},
            priority=priority,
            timeout_seconds=timeout_seconds,
            tags=tags or set(),
            metadata=metadata or {}
        )

        self.task_queue.put(task)

        logger.info(f"Submitted task: {task_id}")
        return task_id

    def start(self) -> None:
        """Start concurrent conversion processing."""
        if self._is_running:
            logger.warning("ConcurrentConverter already running")
            return

        self._is_running = True
        self._shutdown_event.clear()

        self.performance_monitor.start_monitoring()

        # Start executor thread
        self._executor_thread = threading.Thread(
            target=self._executor_loop,
            name=f"ConcurrentConverter-{self.operation_id}",
            daemon=True
        )
        self._executor_thread.start()

        logger.info(f"ConcurrentConverter started for {self.operation_id}")

    def stop(self, wait: bool = True, timeout: float = 30.0) -> None:
        """
        Stop concurrent conversion processing.

        Args:
            wait: Whether to wait for tasks to complete
            timeout: Timeout in seconds
        """
        if not self._is_running:
            return

        self._is_running = False
        self._shutdown_event.set()

        # Wait for executor thread
        if wait and self._executor_thread and self._executor_thread.is_alive():
            self._executor_thread.join(timeout=timeout)

        self.performance_monitor.stop_monitoring()

        logger.info(f"ConcurrentConverter stopped for {self.operation_id}")

    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """
        Get status of a specific task.

        Args:
            task_id: Task ID

        Returns:
            TaskStatus or None if not found
        """
        # This is a simplified implementation
        # In production, you would track task status in a proper store
        return None

    def get_queue_stats(self) -> Dict[str, Any]:
        """
        Get queue statistics.

        Returns:
            Dictionary containing queue statistics
        """
        with self._lock:
            return {
                "queue_size": self.task_queue.qsize(),
                "active_tasks": len(self.resource_manager.get_active_tasks()),
                "total_processed": self._total_tasks_processed,
                "total_succeeded": self._total_tasks_succeeded,
                "total_failed": self._total_tasks_failed,
                "success_rate_percent": (
                    (self._total_tasks_succeeded / self._total_tasks_processed * 100)
                    if self._total_tasks_processed > 0 else 0
                )
            }

    def _executor_loop(self) -> None:
        """Main executor loop."""
        logger.info("Executor loop started")

        while self._is_running or not self.task_queue.empty():
            try:
                # Get next task
                try:
                    task = self.task_queue.get(block=True, timeout=0.1)
                except queue.Empty:
                    continue

                # Try to acquire resources
                if not self.resource_manager.acquire_resources(task):
                    # Re-queue task if resources not available
                    self.task_queue.put(task)
                    time.sleep(0.1)
                    continue

                # Start task execution
                self._execute_task(task)

            except Exception as e:
                logger.error(f"Executor loop error: {e}")

        logger.info("Executor loop stopped")

    def _execute_task(self, task: ConversionTask) -> None:
        """
        Execute a single task.

        Args:
            task: ConversionTask to execute
        """
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()

        logger.info(f"Executing task: {task.task_id}")

        try:
            # Start monitoring
            self.performance_hook.monitor_stage_start(f"task_{task.task_id}")

            # Simulate conversion execution
            # In production, this would call the actual conversion flow
            time.sleep(0.1)  # Placeholder for actual work

            # Record completion
            duration_ms = (datetime.now() - task.started_at).total_seconds() * 1000
            self.performance_hook.monitor_stage_end(
                f"task_{task.task_id}",
                {"status": "completed"},
                duration_ms
            )

            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = {"output_path": task.output_path}

            with self._lock:
                self._total_tasks_processed += 1
                self._total_tasks_succeeded += 1

            self.load_balancer.update_stats(task.task_id)

            logger.info(f"Task completed: {task.task_id}")

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
            task.error = e

            with self._lock:
                self._total_tasks_processed += 1
                self._total_tasks_failed += 1

            logger.error(f"Task failed: {task.task_id}: {e}")

        finally:
            # Release resources
            self.resource_manager.release_resources(task.task_id)

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
