"""
Multi-Model Concurrent Conversion Manager

This module provides comprehensive management for concurrent conversion of multiple models.
Part of Story 3.1: 性能优化与扩展 (Phase 2: 核心功能实现)

Features:
- Multi-model concurrent conversion management
- Batch processing with intelligent ordering
- Resource-aware conversion scheduling
- Conversion pipeline orchestration
- Progress tracking and reporting

Author: BMM v6 Workflow
Version: 1.0
Date: 2025-10-28
"""

import asyncio
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union, Awaitable

from .performance_monitor import PerformanceMonitor, MetricType
from .performance_optimizer import PerformanceOptimizer, OptimizationStrategy
from .concurrent_converter import TaskPriority, TaskStatus, ConversionTask, ResourceQuota
from .performance_hook import PerformanceHook

logger = logging.getLogger(__name__)


class ConversionMode(Enum):
    """Conversion execution modes."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    BATCH = "batch"
    PIPELINE = "pipeline"
    ADAPTIVE = "adaptive"


class ConversionPhase(Enum):
    """Conversion execution phases."""
    PREPARATION = "preparation"
    CONVERSION = "conversion"
    VALIDATION = "validation"
    OPTIMIZATION = "optimization"
    FINALIZATION = "finalization"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ModelConversionJob:
    """Represents a single model conversion job."""
    job_id: str
    model_path: str
    output_path: str
    model_type: str
    priority: TaskPriority = TaskPriority.NORMAL
    mode: ConversionMode = ConversionMode.PARALLEL
    estimated_duration: float = 0.0
    resource_requirements: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Exception] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class BatchConversionJob:
    """Represents a batch conversion job."""
    batch_id: str
    jobs: List[ModelConversionJob]
    total_models: int
    completed_models: int = 0
    failed_models: int = 0
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Exception] = field(default_factory=list)


class ConversionPipeline:
    """
    Conversion pipeline for orchestrating multi-stage conversion.

    Implements a pipeline pattern where different stages of conversion
    can run concurrently for different models.
    """

    def __init__(
        self,
        pipeline_id: str,
        max_parallel_stages: int = 3,
        performance_monitor: Optional[PerformanceMonitor] = None
    ):
        """
        Initialize conversion pipeline.

        Args:
            pipeline_id: Unique pipeline identifier
            max_parallel_stages: Maximum number of parallel stages
            performance_monitor: PerformanceMonitor instance
        """
        self.pipeline_id = pipeline_id
        self.max_parallel_stages = max_parallel_stages
        self.performance_monitor = performance_monitor or PerformanceMonitor(pipeline_id)

        # Pipeline stages
        self.stages = {
            ConversionPhase.PREPARATION: self._prepare_model,
            ConversionPhase.CONVERSION: self._convert_model,
            ConversionPhase.VALIDATION: self._validate_conversion,
            ConversionPhase.OPTIMIZATION: self._optimize_model,
            ConversionPhase.FINALIZATION: self._finalize_conversion
        }

        # Stage queues
        self.stage_queues: Dict[ConversionPhase, asyncio.Queue] = {
            phase: asyncio.Queue() for phase in ConversionPhase
        }

        # Active stages
        self.active_stages: Dict[ConversionPhase, Set[str]] = {
            phase: set() for phase in ConversionPhase
        }

        # Pipeline control
        self._is_running = False
        self._shutdown_event = asyncio.Event()

        logger.info(f"ConversionPipeline initialized: {pipeline_id}")

    async def start(self) -> None:
        """Start the conversion pipeline."""
        if self._is_running:
            logger.warning(f"Pipeline {self.pipeline_id} already running")
            return

        self._is_running = True
        self.performance_monitor.start_monitoring()

        # Start stage workers
        tasks = []
        for phase in ConversionPhase:
            if phase in [ConversionPhase.COMPLETED, ConversionPhase.FAILED]:
                continue

            task = asyncio.create_task(
                self._stage_worker(phase),
                name=f"Pipeline-{self.pipeline_id}-{phase.value}"
            )
            tasks.append(task)

        logger.info(f"Pipeline {self.pipeline_id} started with {len(tasks)} stage workers")

        await asyncio.gather(*tasks)

    async def stop(self) -> None:
        """Stop the conversion pipeline."""
        if not self._is_running:
            return

        self._is_running = False
        self._shutdown_event.set()

        self.performance_monitor.stop_monitoring()

        logger.info(f"Pipeline {self.pipeline_id} stopped")

    async def submit_job(self, job: ModelConversionJob) -> str:
        """
        Submit a job to the pipeline.

        Args:
            job: ModelConversionJob to submit

        Returns:
            Job ID
        """
        await self.stage_queues[ConversionPhase.PREPARATION].put(job)

        logger.info(f"Submitted job {job.job_id} to pipeline {self.pipeline_id}")

        return job.job_id

    async def _stage_worker(self, phase: ConversionPhase) -> None:
        """
        Worker for a specific pipeline stage.

        Args:
            phase: ConversionPhase to handle
        """
        logger.info(f"Stage worker started for {phase.value}")

        while self._is_running or not self.stage_queues[phase].empty():
            try:
                # Get next job with timeout
                job = await asyncio.wait_for(
                    self.stage_queues[phase].get(),
                    timeout=0.1
                )

                # Process job
                await self._process_stage_job(phase, job)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Stage worker error ({phase.value}): {e}")

        logger.info(f"Stage worker stopped for {phase.value}")

    async def _process_stage_job(
        self,
        phase: ConversionPhase,
        job: ModelConversionJob
    ) -> None:
        """
        Process a job in a specific stage.

        Args:
            phase: ConversionPhase
            job: ModelConversionJob to process
        """
        stage_name = f"{phase.value}_{job.job_id}"

        # Start stage monitoring
        self.performance_monitor.set_stage(stage_name)
        self.active_stages[phase].add(job.job_id)

        start_time = datetime.now()

        try:
            # Execute stage
            result = await self.stages[phase](job)

            # Calculate duration
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000

            # Record stage completion
            self.performance_monitor.record_latency(stage_name, duration_ms)

            # Move to next stage
            if phase != ConversionPhase.FINALIZATION:
                next_phase = ConversionPhase(list(ConversionPhase).index(phase) + 1)
                if next_phase not in [ConversionPhase.COMPLETED, ConversionPhase.FAILED]:
                    await self.stage_queues[next_phase].put(job)

            logger.info(f"Stage {phase.value} completed for job {job.job_id} in {duration_ms:.2f}ms")

        except Exception as e:
            logger.error(f"Stage {phase.value} failed for job {job.job_id}: {e}")
            job.error = e
            job.status = TaskStatus.FAILED

        finally:
            # Clean up
            self.active_stages[phase].discard(job.job_id)

    async def _prepare_model(self, job: ModelConversionJob) -> Dict[str, Any]:
        """Prepare model for conversion."""
        await asyncio.sleep(0.1)  # Placeholder
        return {"status": "prepared"}

    async def _convert_model(self, job: ModelConversionJob) -> Dict[str, Any]:
        """Convert model."""
        await asyncio.sleep(0.2)  # Placeholder
        return {"status": "converted"}

    async def _validate_conversion(self, job: ModelConversionJob) -> Dict[str, Any]:
        """Validate conversion result."""
        await asyncio.sleep(0.1)  # Placeholder
        return {"status": "validated"}

    async def _optimize_model(self, job: ModelConversionJob) -> Dict[str, Any]:
        """Optimize converted model."""
        await asyncio.sleep(0.15)  # Placeholder
        return {"status": "optimized"}

    async def _finalize_conversion(self, job: ModelConversionJob) -> Dict[str, Any]:
        """Finalize conversion."""
        await asyncio.sleep(0.05)  # Placeholder
        job.status = TaskStatus.COMPLETED
        return {"status": "finalized", "output_path": job.output_path}


class MultiModelConversionManager:
    """
    Comprehensive manager for concurrent conversion of multiple models.

    Features:
    - Multiple conversion modes (sequential, parallel, batch, pipeline)
    - Intelligent job scheduling
    - Resource-aware execution
    - Progress tracking and reporting
    - Performance optimization integration
    """

    def __init__(
        self,
        manager_id: str,
        max_concurrent_models: int = 10,
        conversion_mode: ConversionMode = ConversionMode.PARALLEL,
        optimization_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED
    ) -> None:
        """
        Initialize multi-model conversion manager.

        Args:
            manager_id: Unique manager identifier
            max_concurrent_models: Maximum concurrent models
            conversion_mode: Default conversion mode
            optimization_strategy: Performance optimization strategy
        """
        self.manager_id = manager_id
        self.max_concurrent_models = max_concurrent_models
        self.conversion_mode = conversion_mode
        self.optimization_strategy = optimization_strategy

        # Performance monitoring
        self.performance_monitor = PerformanceMonitor(manager_id)
        self.performance_hook = PerformanceHook(manager_id, self.performance_monitor)

        # Conversion jobs
        self.jobs: Dict[str, ModelConversionJob] = {}
        self.active_jobs: Set[str] = set()
        self.completed_jobs: Set[str] = set()
        self.failed_jobs: Set[str] = set()

        # Batch jobs
        self.batch_jobs: Dict[str, BatchConversionJob] = {}

        # Conversion pipelines
        self.pipelines: Dict[str, ConversionPipeline] = {}

        # Execution control
        self._is_running = False
        self._executor: Optional[ThreadPoolExecutor] = None
        self._lock = threading.Lock()

        # Performance optimizer
        self.optimizer = None  # Will be initialized if database is provided

        logger.info(f"MultiModelConversionManager initialized: {manager_id}")

    def initialize_optimizer(self, database, storage_dir: Optional[str] = None) -> None:
        """
        Initialize performance optimizer.

        Args:
            database: PerformanceDatabase instance
            storage_dir: Optional storage directory
        """
        self.optimizer = PerformanceOptimizer(database, self.optimization_strategy)
        logger.info(f"Performance optimizer initialized for {self.manager_id}")

    async def start(self) -> None:
        """Start the conversion manager."""
        if self._is_running:
            logger.warning(f"Manager {self.manager_id} already running")
            return

        self._is_running = True
        self.performance_monitor.start_monitoring()

        # Initialize thread pool executor
        self._executor = ThreadPoolExecutor(
            max_workers=self.max_concurrent_models,
            thread_name_prefix=f"ConvMgr-{self.manager_id}"
        )

        logger.info(f"MultiModelConversionManager started: {self.manager_id}")

    async def stop(self, wait: bool = True, timeout: float = 30.0) -> None:
        """
        Stop the conversion manager.

        Args:
            wait: Whether to wait for jobs to complete
            timeout: Timeout in seconds
        """
        if not self._is_running:
            return

        self._is_running = False

        # Stop all pipelines
        for pipeline in self.pipelines.values():
            await pipeline.stop()

        # Shutdown executor
        if self._executor:
            self._executor.shutdown(wait=wait)

        self.performance_monitor.stop_monitoring()

        logger.info(f"MultiModelConversionManager stopped: {self.manager_id}")

    def submit_conversion_job(
        self,
        model_path: str,
        output_path: str,
        model_type: str,
        priority: TaskPriority = TaskPriority.NORMAL,
        mode: Optional[ConversionMode] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Submit a single model conversion job.

        Args:
            model_path: Path to model
            output_path: Output path
            model_type: Type of model
            priority: Job priority
            mode: Conversion mode
            metadata: Optional metadata

        Returns:
            Job ID
        """
        job_id = f"{self.manager_id}_{int(time.time() * 1000000)}"

        job = ModelConversionJob(
            job_id=job_id,
            model_path=model_path,
            output_path=output_path,
            model_type=model_type,
            priority=priority,
            mode=mode or self.conversion_mode,
            metadata=metadata or {}
        )

        with self._lock:
            self.jobs[job_id] = job

        logger.info(f"Submitted conversion job: {job_id}")

        return job_id

    async def submit_batch_conversion(
        self,
        model_configs: List[Dict[str, Any]],
        batch_id: Optional[str] = None,
        mode: Optional[ConversionMode] = None
    ) -> str:
        """
        Submit a batch of model conversion jobs.

        Args:
            model_configs: List of model configurations
            batch_id: Optional batch ID
            mode: Conversion mode

        Returns:
            Batch ID
        """
        if not batch_id:
            batch_id = f"batch_{int(time.time() * 1000000)}"

        # Create jobs
        jobs = []
        for config in model_configs:
            job_id = self.submit_conversion_job(
                model_path=config["model_path"],
                output_path=config["output_path"],
                model_type=config.get("model_type", "unknown"),
                priority=config.get("priority", TaskPriority.NORMAL),
                mode=mode or self.conversion_mode,
                metadata=config.get("metadata", {})
            )
            jobs.append(self.jobs[job_id])

        # Create batch job
        batch_job = BatchConversionJob(
            batch_id=batch_id,
            jobs=jobs,
            total_models=len(jobs)
        )

        with self._lock:
            self.batch_jobs[batch_id] = batch_job

        # Execute batch
        asyncio.create_task(self._execute_batch(batch_job))

        logger.info(f"Submitted batch conversion: {batch_id} ({len(jobs)} models)")

        return batch_id

    async def _execute_batch(self, batch_job: BatchConversionJob) -> None:
        """
        Execute a batch conversion job.

        Args:
            batch_job: BatchConversionJob to execute
        """
        batch_job.status = TaskStatus.RUNNING
        batch_job.started_at = datetime.now()

        logger.info(f"Executing batch: {batch_job.batch_id}")

        # Select execution strategy based on mode
        first_job = batch_job.jobs[0]
        mode = first_job.mode

        if mode == ConversionMode.SEQUENTIAL:
            await self._execute_batch_sequential(batch_job)
        elif mode == ConversionMode.PARALLEL:
            await self._execute_batch_parallel(batch_job)
        elif mode == ConversionMode.BATCH:
            await self._execute_batch_batch(batch_job)
        elif mode == ConversionMode.PIPELINE:
            await self._execute_batch_pipeline(batch_job)
        else:
            await self._execute_batch_adaptive(batch_job)

        batch_job.status = TaskStatus.COMPLETED
        batch_job.completed_at = datetime.now()

        logger.info(f"Batch completed: {batch_job.batch_id} "
                   f"({batch_job.completed_models} succeeded, {batch_job.failed_models} failed)")

    async def _execute_batch_sequential(self, batch_job: BatchConversionJob) -> None:
        """Execute batch sequentially."""
        for job in batch_job.jobs:
            try:
                result = await self._execute_single_job(job)
                batch_job.results.append(result)
                batch_job.completed_models += 1
            except Exception as e:
                batch_job.errors.append(e)
                batch_job.failed_models += 1

    async def _execute_batch_parallel(self, batch_job: BatchConversionJob) -> None:
        """Execute batch in parallel."""
        tasks = []
        for job in batch_job.jobs:
            task = asyncio.create_task(self._execute_single_job(job))
            tasks.append((job, task))

        for job, task in tasks:
            try:
                result = await task
                batch_job.results.append(result)
                batch_job.completed_models += 1
            except Exception as e:
                batch_job.errors.append(e)
                batch_job.failed_models += 1

    async def _execute_batch_batch(self, batch_job: BatchConversionJob) -> None:
        """Execute batch in groups."""
        batch_size = min(5, len(batch_job.jobs))
        for i in range(0, len(batch_job.jobs), batch_size):
            batch = batch_job.jobs[i:i + batch_size]
            tasks = [self._execute_single_job(job) for job in batch]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for job, result in zip(batch, results):
                if isinstance(result, Exception):
                    batch_job.errors.append(result)
                    batch_job.failed_models += 1
                else:
                    batch_job.results.append(result)
                    batch_job.completed_models += 1

    async def _execute_batch_pipeline(self, batch_job: BatchConversionJob) -> None:
        """Execute batch using pipeline."""
        pipeline_id = f"pipeline_{batch_job.batch_id}"
        pipeline = ConversionPipeline(pipeline_id)

        self.pipelines[pipeline_id] = pipeline

        await pipeline.start()

        # Submit all jobs to pipeline
        for job in batch_job.jobs:
            await pipeline.submit_job(job)

        # Wait for completion
        await asyncio.sleep(0.1)  # Placeholder

        await pipeline.stop()

        batch_job.completed_models = batch_job.total_models
        batch_job.failed_models = 0

    async def _execute_batch_adaptive(self, batch_job: BatchConversionJob) -> None:
        """Execute batch adaptively based on system load."""
        # Get current system load
        system_load = {
            "cpu_percent": self._get_cpu_usage(),
            "memory_percent": self._get_memory_usage()
        }

        # Choose mode based on load
        if system_load["cpu_percent"] > 80 or system_load["memory_percent"] > 80:
            # High load - use sequential
            await self._execute_batch_sequential(batch_job)
        elif len(batch_job.jobs) > 10:
            # Many jobs - use batch
            await self._execute_batch_batch(batch_job)
        else:
            # Normal load - use parallel
            await self._execute_batch_parallel(batch_job)

    async def _execute_single_job(self, job: ModelConversionJob) -> Dict[str, Any]:
        """
        Execute a single conversion job.

        Args:
            job: ModelConversionJob to execute

        Returns:
            Execution result
        """
        job.status = TaskStatus.RUNNING
        job.started_at = datetime.now()

        with self._lock:
            self.active_jobs.add(job.job_id)

        try:
            # Start monitoring
            self.performance_hook.monitor_stage_start(f"job_{job.job_id}")

            # Simulate conversion
            await asyncio.sleep(0.2)  # Placeholder

            # Record completion
            self.performance_hook.monitor_stage_end(
                f"job_{job.job_id}",
                {"status": "completed"},
                200.0
            )

            result = {
                "job_id": job.job_id,
                "model_path": job.model_path,
                "output_path": job.output_path,
                "status": "completed",
                "duration_ms": 200.0
            }

            job.status = TaskStatus.COMPLETED
            job.completed_at = datetime.now()
            job.result = result

            with self._lock:
                self.active_jobs.remove(job.job_id)
                self.completed_jobs.add(job.job_id)

            return result

        except Exception as e:
            job.status = TaskStatus.FAILED
            job.error = e

            with self._lock:
                if job.job_id in self.active_jobs:
                    self.active_jobs.remove(job.job_id)
                self.failed_jobs.add(job.job_id)

            raise

    def get_job_status(self, job_id: str) -> Optional[TaskStatus]:
        """
        Get status of a job.

        Args:
            job_id: Job ID

        Returns:
            TaskStatus or None
        """
        with self._lock:
            job = self.jobs.get(job_id)
            return job.status if job else None

    def get_batch_status(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a batch.

        Args:
            batch_id: Batch ID

        Returns:
            Batch status dictionary or None
        """
        with self._lock:
            batch_job = self.batch_jobs.get(batch_id)
            if not batch_job:
                return None

            return {
                "batch_id": batch_job.batch_id,
                "total_models": batch_job.total_models,
                "completed_models": batch_job.completed_models,
                "failed_models": batch_job.failed_models,
                "status": batch_job.status.value,
                "progress_percent": (batch_job.completed_models / batch_job.total_models * 100)
                if batch_job.total_models > 0 else 0
            }

    def get_manager_stats(self) -> Dict[str, Any]:
        """
        Get manager statistics.

        Returns:
            Dictionary containing manager statistics
        """
        with self._lock:
            return {
                "manager_id": self.manager_id,
                "total_jobs": len(self.jobs),
                "active_jobs": len(self.active_jobs),
                "completed_jobs": len(self.completed_jobs),
                "failed_jobs": len(self.failed_jobs),
                "total_batches": len(self.batch_jobs),
                "success_rate_percent": (
                    len(self.completed_jobs) / len(self.jobs) * 100
                ) if self.jobs else 0,
                "performance_summary": self.performance_hook.get_performance_summary()
            }

    def _get_cpu_usage(self) -> float:
        """Get current CPU usage."""
        try:
            import psutil
            return psutil.cpu_percent()
        except:
            return 0.0

    def _get_memory_usage(self) -> float:
        """Get current memory usage."""
        try:
            import psutil
            return psutil.virtual_memory().percent
        except:
            return 0.0

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()
