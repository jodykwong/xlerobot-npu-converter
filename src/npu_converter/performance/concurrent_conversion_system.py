"""
并发转换系统

为Story 3.3: 并行处理能力提供完整的并发转换实现，
包含任务调度、负载均衡、批处理、并发控制等功能。

作者: Claude Code / Story 3.3
版本: 1.0
日期: 2025-10-28
"""

import asyncio
import threading
import queue
import time
from typing import Dict, List, Any, Optional, Callable, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from datetime import datetime
import logging
from contextlib import contextmanager
import psutil

from ..core.exceptions import ConversionError
from ..memory import MemoryOptimizationSystem

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """任务优先级"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class ConversionTask:
    """转换任务"""
    task_id: str
    model_data: Any
    conversion_params: Dict[str, Any]
    priority: TaskPriority = TaskPriority.NORMAL
    created_at: float = field(default_factory=time.time)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    dependencies: Set[str] = field(default_factory=set)
    callback: Optional[Callable] = None


@dataclass
class ConcurrentMetrics:
    """并发指标"""
    timestamp: float
    active_tasks: int
    completed_tasks: int
    failed_tasks: int
    pending_tasks: int
    throughput: float
    average_latency: float
    cpu_usage: float
    memory_usage: float
    queue_length: int


class TaskScheduler:
    """任务调度器"""

    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.task_queue = queue.PriorityQueue()
        self.running_tasks: Dict[str, ConversionTask] = {}
        self.completed_tasks: Dict[str, ConversionTask] = {}
        self.task_counter = 0
        self._lock = threading.Lock()
        self._shutdown = False

    def submit_task(
        self,
        model_data: Any,
        conversion_params: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        task_id: Optional[str] = None,
        dependencies: Optional[Set[str]] = None,
        callback: Optional[Callable] = None,
    ) -> str:
        """提交任务"""
        with self._lock:
            task_id = task_id or f"task_{self.task_counter}"
            self.task_counter += 1

        task = ConversionTask(
            task_id=task_id,
            model_data=model_data,
            conversion_params=conversion_params,
            priority=priority,
            dependencies=dependencies or set(),
            callback=callback,
        )

        # 优先级队列：使用负优先级实现高优先级先执行
        priority_value = -priority.value
        self.task_queue.put((priority_value, time.time(), task_id, task))

        logger.info(f"任务已提交: {task_id}, 优先级: {priority.name}")
        return task_id

    def get_next_task(self) -> Optional[ConversionTask]:
        """获取下一个待执行任务"""
        if self._shutdown or self.task_queue.empty():
            return None

        try:
            priority_value, submit_time, task_id, task = self.task_queue.get_nowait()

            # 检查依赖是否满足
            if not self._dependencies_satisfied(task):
                # 重新放回队列末尾
                self.task_queue.put((priority_value, submit_time, task_id, task))
                return None

            return task
        except queue.Empty:
            return None

    def _dependencies_satisfied(self, task: ConversionTask) -> bool:
        """检查任务依赖是否满足"""
        for dep_id in task.dependencies:
            if dep_id not in self.completed_tasks:
                return False
        return True

    def start_task(self, task: ConversionTask) -> bool:
        """开始执行任务"""
        if len(self.running_tasks) >= self.max_concurrent:
            return False

        if task.task_id in self.running_tasks:
            return False

        task.status = TaskStatus.RUNNING
        task.started_at = time.time()
        self.running_tasks[task.task_id] = task
        return True

    def complete_task(self, task_id: str, result: Any = None, error: str = None):
        """完成任务"""
        if task_id not in self.running_tasks:
            return

        task = self.running_tasks.pop(task_id)
        task.status = TaskStatus.COMPLETED if error is None else TaskStatus.FAILED
        task.completed_at = time.time()
        task.result = result
        task.error = error

        self.completed_tasks[task_id] = task

        # 执行回调
        if task.callback:
            try:
                task.callback(task)
            except Exception as e:
                logger.error(f"任务回调执行失败: {e}")

        logger.info(f"任务完成: {task_id}, 状态: {task.status.value}")

    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        # 从运行中移除
        if task_id in self.running_tasks:
            task = self.running_tasks.pop(task_id)
            task.status = TaskStatus.CANCELLED
            task.completed_at = time.time()
            self.completed_tasks[task_id] = task
            return True

        # 从队列中移除（需要遍历队列）
        temp_queue = queue.PriorityQueue()
        cancelled = False
        while not self.task_queue.empty():
            priority_value, submit_time, tid, task = self.task_queue.get()
            if tid == task_id:
                task.status = TaskStatus.CANCELLED
                self.completed_tasks[task_id] = task
                cancelled = True
                logger.info(f"任务已取消: {task_id}")
            else:
                temp_queue.put((priority_value, submit_time, tid, task))

        # 将剩余任务放回原队列
        while not temp_queue.empty():
            self.task_queue.put(temp_queue.get())

        return cancelled

    def get_task(self, task_id: str) -> Optional[ConversionTask]:
        """获取任务"""
        return (
            self.running_tasks.get(task_id)
            or self.completed_tasks.get(task_id)
        )

    def get_metrics(self) -> ConcurrentMetrics:
        """获取并发指标"""
        now = time.time()
        active_tasks = len(self.running_tasks)
        completed_count = len(self.completed_tasks)
        failed_count = sum(
            1 for t in self.completed_tasks.values() if t.status == TaskStatus.FAILED
        )
        pending_count = self.task_queue.qsize()

        # 计算吞吐量（每分钟完成任务数）
        recent_completed = [
            t for t in self.completed_tasks.values()
            if t.completed_at and now - t.completed_at < 60
        ]
        throughput = len(recent_completed)

        # 计算平均延迟
        completed_with_time = [
            t for t in self.completed_tasks.values()
            if t.started_at and t.completed_at
        ]
        average_latency = (
            sum(t.completed_at - t.started_at for t in completed_with_time)
            / len(completed_with_time) if completed_with_time else 0
        )

        # 系统资源使用
        process = psutil.Process()
        cpu_usage = process.cpu_percent()
        memory_usage = process.memory_info().rss

        return ConcurrentMetrics(
            timestamp=now,
            active_tasks=active_tasks,
            completed_tasks=completed_count,
            failed_tasks=failed_count,
            pending_tasks=pending_count,
            throughput=throughput,
            average_latency=average_latency,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            queue_length=pending_count,
        )

    def shutdown(self):
        """关闭调度器"""
        self._shutdown = True


class LoadBalancer:
    """负载均衡器"""

    def __init__(self):
        self.worker_stats: Dict[str, Dict[str, Any]] = {}

    def select_worker(self, available_workers: List[str]) -> str:
        """选择工作节点"""
        if not available_workers:
            raise ValueError("没有可用的工作节点")

        # 选择负载最低的工作节点
        best_worker = None
        lowest_load = float('inf')

        for worker_id in available_workers:
            load = self._get_worker_load(worker_id)
            if load < lowest_load:
                lowest_load = load
                best_worker = worker_id

        return best_worker or available_workers[0]

    def _get_worker_load(self, worker_id: str) -> float:
        """获取工作节点负载"""
        stats = self.worker_stats.get(worker_id, {})
        active_tasks = stats.get('active_tasks', 0)
        cpu_usage = stats.get('cpu_usage', 0)
        memory_usage = stats.get('memory_usage', 0)

        # 综合负载分数
        load_score = (
            active_tasks * 0.5 +
            cpu_usage * 0.3 +
            (memory_usage / (1024 * 1024 * 1024)) * 0.2  # GB
        )
        return load_score

    def update_worker_stats(self, worker_id: str, stats: Dict[str, Any]):
        """更新工作节点统计"""
        self.worker_stats[worker_id] = stats


class BatchProcessor:
    """批处理器"""

    def __init__(self, max_batch_size: int = 10, max_wait_time: float = 1.0):
        self.max_batch_size = max_batch_size
        self.max_wait_time = max_wait_time
        self.pending_batch: List[ConversionTask] = []
        self._lock = threading.Lock()

    def add_to_batch(self, task: ConversionTask) -> bool:
        """添加到批次"""
        with self._lock:
            if len(self.pending_batch) >= self.max_batch_size:
                return False

            self.pending_batch.append(task)
            return True

    def get_batch(self) -> List[ConversionTask]:
        """获取批次"""
        with self._lock:
            if not self.pending_batch:
                return []

            batch = self.pending_batch[:self.max_batch_size]
            self.pending_batch = self.pending_batch[self.max_batch_size:]
            return batch

    def should_process_batch(self) -> bool:
        """判断是否应该处理批次"""
        with self._lock:
            return (
                len(self.pending_batch) >= self.max_batch_size or
                (
                    self.pending_batch and
                    time.time() - self.pending_batch[0].created_at >= self.max_wait_time
                )
            )


class ConcurrentConversionSystem:
    """并发转换系统主类"""

    def __init__(
        self,
        max_concurrent: int = 10,
        max_batch_size: int = 10,
        enable_memory_optimization: bool = True,
        custom_config: Optional[Dict[str, Any]] = None,
    ):
        self.max_concurrent = max_concurrent
        self.enable_memory_optimization = enable_memory_optimization
        self.custom_config = custom_config or {}

        # 初始化组件
        self.scheduler = TaskScheduler(max_concurrent=max_concurrent)
        self.load_balancer = LoadBalancer()
        self.batch_processor = BatchProcessor(max_batch_size=max_batch_size)

        # 内存优化系统
        if self.enable_memory_optimization:
            from ..memory import MemoryOptimizationSystem
            from ..config.memory_optimization_config import MemoryOptimizationPresets
            memory_config = MemoryOptimizationPresets.get_standard_mode()
            self.memory_optimizer = MemoryOptimizationSystem(memory_config)
        else:
            self.memory_optimizer = None

        # 线程池执行器
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)
        self.active_futures: Dict[str, Future] = {}

        # 指标历史
        self.metrics_history: List[ConcurrentMetrics] = []

        # 回调函数
        self.task_callbacks: Dict[str, List[Callable]] = {}

        # 统计信息
        self.stats = {
            "tasks_submitted": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_processing_time": 0.0,
        }

        logger.info(f"并发转换系统已初始化，最大并发数: {max_concurrent}")

    def submit_conversion(
        self,
        model_data: Any,
        conversion_params: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        batch_mode: bool = False,
        wait_for_completion: bool = False,
        timeout: Optional[float] = None,
    ) -> str:
        """提交转换任务"""
        task_id = self.scheduler.submit_task(
            model_data=model_data,
            conversion_params=conversion_params,
            priority=priority,
        )

        self.stats["tasks_submitted"] += 1

        if wait_for_completion:
            return self._wait_for_task_completion(task_id, timeout)

        return task_id

    def _wait_for_task_completion(self, task_id: str, timeout: Optional[float]) -> Any:
        """等待任务完成"""
        start_time = time.time()
        while True:
            task = self.scheduler.get_task(task_id)
            if not task:
                raise ConversionError(f"任务不存在: {task_id}")

            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                if task.status == TaskStatus.COMPLETED:
                    return task.result
                else:
                    raise ConversionError(f"任务失败: {task.error}")

            if timeout and (time.time() - start_time) > timeout:
                raise ConversionError(f"任务超时: {task_id}")

            time.sleep(0.1)

    def _execute_task(self, task: ConversionTask) -> Tuple[Any, Optional[str]]:
        """执行任务"""
        try:
            # 启动内存优化
            if self.memory_optimizer:
                self.memory_optimizer.start()

            # 执行转换（这里是模拟）
            result = self._perform_conversion(task.model_data, task.conversion_params)

            return result, None

        except Exception as e:
            error_msg = f"转换执行失败: {str(e)}"
            logger.error(error_msg)
            return None, error_msg

        finally:
            # 停止内存优化
            if self.memory_optimizer:
                self.memory_optimizer.stop()

    def _perform_conversion(self, model_data: Any, conversion_params: Dict[str, Any]) -> Dict[str, Any]:
        """执行实际的模型转换（示例实现）"""
        # 模拟转换过程
        time.sleep(0.1)  # 模拟转换时间

        # 模拟转换结果
        result = {
            "status": "success",
            "input_size": self._estimate_size(model_data),
            "output_format": "converted_model",
            "conversion_params": conversion_params,
            "timestamp": datetime.now().isoformat(),
        }

        return result

    def _estimate_size(self, data: Any) -> int:
        """估算数据大小"""
        try:
            import sys
            return sys.getsizeof(data)
        except:
            return 0

    def process_batch(self, batch: List[ConversionTask]) -> List[Tuple[str, Any, Optional[str]]]:
        """批处理任务"""
        results = []
        futures = {}

        # 提交所有任务到线程池
        for task in batch:
            future = self.executor.submit(self._execute_task, task)
            futures[future] = task.task_id

        # 等待所有任务完成
        for future in as_completed(futures):
            task_id = futures[future]
            try:
                result, error = future.result()
                results.append((task_id, result, error))
            except Exception as e:
                results.append((task_id, None, str(e)))

        return results

    def run(self, duration: Optional[float] = None):
        """运行并发转换系统"""
        start_time = time.time()
        logger.info("并发转换系统开始运行")

        try:
            while True:
                # 检查是否应该停止
                if duration and (time.time() - start_time) > duration:
                    break

                # 获取并发指标
                metrics = self.scheduler.get_metrics()
                self.metrics_history.append(metrics)

                # 保持历史记录大小
                if len(self.metrics_history) > 1000:
                    self.metrics_history = self.metrics_history[-1000:]

                # 处理批次
                if self.batch_processor.should_process_batch():
                    batch = self.batch_processor.get_batch()
                    if batch:
                        logger.info(f"处理批次，任务数: {len(batch)}")
                        results = self.process_batch(batch)

                        # 完成批次任务
                        for task_id, result, error in results:
                            self.scheduler.complete_task(task_id, result, error)

                # 启动新任务
                while len(self.scheduler.running_tasks) < self.max_concurrent:
                    task = self.scheduler.get_next_task()
                    if not task:
                        break

                    if self.scheduler.start_task(task):
                        future = self.executor.submit(self._execute_task, task)
                        self.active_futures[task.task_id] = future
                    else:
                        break

                # 清理已完成的任务
                completed_task_ids = []
                for task_id, future in self.active_futures.items():
                    if future.done():
                        completed_task_ids.append(task_id)

                        try:
                            result, error = future.result()
                            self.scheduler.complete_task(task_id, result, error)
                        except Exception as e:
                            self.scheduler.complete_task(task_id, None, str(e))

                for task_id in completed_task_ids:
                    self.active_futures.pop(task_id, None)

                # 短暂休眠
                time.sleep(0.01)

        except KeyboardInterrupt:
            logger.info("接收到停止信号")

        finally:
            self.shutdown()

    def shutdown(self):
        """关闭系统"""
        logger.info("正在关闭并发转换系统")

        # 停止调度器
        self.scheduler.shutdown()

        # 关闭线程池
        self.executor.shutdown(wait=True)

        # 停止内存优化
        if self.memory_optimizer:
            self.memory_optimizer.stop()

        logger.info("并发转换系统已关闭")

    def get_metrics(self) -> ConcurrentMetrics:
        """获取当前指标"""
        return self.scheduler.get_metrics()

    def get_metrics_history(self, count: int = 100) -> List[ConcurrentMetrics]:
        """获取历史指标"""
        return self.metrics_history[-count:]

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        metrics = self.get_metrics()
        return {
            **self.stats,
            "active_tasks": metrics.active_tasks,
            "pending_tasks": metrics.pending_tasks,
            "queue_length": metrics.queue_length,
            "throughput_per_minute": metrics.throughput,
            "average_latency": metrics.average_latency,
        }

    @contextmanager
    def concurrent_context(self):
        """并发上下文管理器"""
        try:
            self.memory_optimizer.start() if self.memory_optimizer else None
            yield self
        finally:
            self.shutdown()


# 工厂函数
def create_concurrent_converter(
    max_concurrent: int = 10,
    max_batch_size: int = 10,
    enable_memory_optimization: bool = True,
    preset: Optional[str] = None,
) -> ConcurrentConversionSystem:
    """
    创建并发转换系统实例

    Args:
        max_concurrent: 最大并发数
        max_batch_size: 最大批大小
        enable_memory_optimization: 是否启用内存优化
        preset: 预设配置 ('high_throughput', 'low_latency', 'balanced')

    Returns:
        ConcurrentConversionSystem实例
    """
    config_map = {
        'high_throughput': {'max_concurrent': 20, 'max_batch_size': 20},
        'low_latency': {'max_concurrent': 5, 'max_batch_size': 5},
        'balanced': {'max_concurrent': 10, 'max_batch_size': 10},
    }

    if preset and preset in config_map:
        preset_config = config_map[preset]
        max_concurrent = preset_config.get('max_concurrent', max_concurrent)
        max_batch_size = preset_config.get('max_batch_size', max_batch_size)

    return ConcurrentConversionSystem(
        max_concurrent=max_concurrent,
        max_batch_size=max_batch_size,
        enable_memory_optimization=enable_memory_optimization,
    )


# 便捷函数
def convert_concurrent(
    model_data: Any,
    conversion_params: Dict[str, Any],
    max_concurrent: int = 10,
    priority: TaskPriority = TaskPriority.NORMAL,
) -> str:
    """
    并发转换便捷函数

    Args:
        model_data: 模型数据
        conversion_params: 转换参数
        max_concurrent: 最大并发数
        priority: 任务优先级

    Returns:
        任务ID
    """
    converter = create_concurrent_converter(max_concurrent=max_concurrent)
    return converter.submit_conversion(
        model_data=model_data,
        conversion_params=conversion_params,
        priority=priority,
    )


if __name__ == "__main__":
    # 使用示例
    print("=" * 60)
    print("并发转换系统示例")
    print("=" * 60)

    # 示例1: 基本使用
    print("\n示例1: 基本使用")
    converter = create_concurrent_converter(
        max_concurrent=5,
        max_batch_size=5,
        preset='balanced'
    )

    # 提交多个任务
    test_data = list(range(100))
    task_ids = []
    for i in range(10):
        task_id = converter.submit_conversion(
            model_data=test_data,
            conversion_params={'model_type': 'test', 'iteration': i},
            priority=TaskPriority.NORMAL,
        )
        task_ids.append(task_id)

    print(f"已提交 {len(task_ids)} 个任务")
    print(f"任务ID: {task_ids[:3]}...")

    # 运行系统（短暂运行）
    import threading
    run_thread = threading.Thread(target=converter.run, kwargs={'duration': 2.0})
    run_thread.start()
    run_thread.join()

    # 获取统计信息
    stats = converter.get_stats()
    print(f"\n统计信息:")
    print(f"  提交任务数: {stats['tasks_submitted']}")
    print(f"  完成任务数: {stats['tasks_completed']}")
    print(f"  活跃任务数: {stats['active_tasks']}")
    print(f"  吞吐量: {stats['throughput_per_minute']:.2f} 任务/分钟")

    print("\n" + "=" * 60)
    print("示例执行完成")
    print("=" * 60)
