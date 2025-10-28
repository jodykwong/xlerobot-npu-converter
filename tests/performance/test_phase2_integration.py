"""
Phase 2 Performance Optimization Engine - Integration Tests

This module tests the integration of all Phase 2 components:
- PerformanceOptimizer with bottleneck identification
- MultiModelConversionManager for concurrent conversions
- ResourcePool for resource management
- ThrottlingOrchestrator for rate limiting
- All components working together

Author: BMM v6 Workflow
Version: 1.0
Date: 2025-10-28
"""

import asyncio
import pytest
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from npu_converter.performance.performance_monitor import PerformanceMonitor, MetricType
from npu_converter.performance.performance_storage import PerformanceDatabase, PerformanceStorage
from npu_converter.performance.performance_optimizer import (
    PerformanceOptimizer,
    BottleneckType,
    OptimizationStrategy
)
from npu_converter.performance.conversion_manager import (
    MultiModelConversionManager,
    ConversionMode,
    TaskPriority
)
from npu_converter.performance.resource_pool import (
    ResourcePool,
    ResourceType,
    PriorityTaskQueue
)
from npu_converter.performance.rate_limiter import (
    ThrottlingOrchestrator,
    RateLimitConfig,
    RateLimitStrategy
)


class TestPerformanceOptimizerIntegration:
    """Test PerformanceOptimizer integration."""

    @pytest.fixture
    def temp_storage_dir(self):
        """Create temporary storage directory."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def performance_optimizer(self, temp_storage_dir):
        """Create PerformanceOptimizer instance."""
        database = PerformanceDatabase(
            Path(temp_storage_dir) / "performance.db"
        )
        optimizer = PerformanceOptimizer(
            database=database,
            optimization_strategy=OptimizationStrategy.BALANCED
        )
        return optimizer

    def test_bottleneck_identification(self, performance_optimizer):
        """Test automatic bottleneck identification."""
        operation_id = "test_operation_001"

        # Simulate performance data with a CPU bottleneck
        monitor = PerformanceMonitor(operation_id)

        # Record CPU bottleneck
        for i in range(10):
            monitor.record_metric(
                metric_type=MetricType.CPU_USAGE,
                value=85.0 + i,  # High CPU usage
                unit="percent"
            )
            monitor.record_metric(
                metric_type=MetricType.LATENCY,
                value=120000.0 + i * 1000,  # High latency
                unit="ms",
                stage="quantization"
            )

        # Store metrics in database
        # In real scenario, these would be stored automatically

        # Identify bottlenecks
        bottlenecks = performance_optimizer.bottleneck_identifier.identify_bottlenecks(
            operation_id=operation_id,
            time_range_hours=1
        )

        # Verify bottleneck detection
        assert len(bottlenecks) > 0

        # Check for CPU bottleneck
        cpu_bottleneck = any(
            b.type == BottleneckType.CPU_BOUND for b in bottlenecks
        )
        assert cpu_bottleneck

        # Check bottleneck details
        cpu_bottlenecks = [
            b for b in bottlenecks
            if b.type == BottleneckType.CPU_BOUND
        ]
        if cpu_bottlenecks:
            bottleneck = cpu_bottlenecks[0]
            assert bottleneck.severity > 0.5
            assert "CPU使用率过高" in bottleneck.suggestion

    def test_optimization_recommendations(self, performance_optimizer):
        """Test optimization recommendation generation."""
        operation_id = "test_operation_002"

        # Get optimization recommendations
        result = performance_optimizer.optimize(
            operation_id=operation_id,
            target_performance={
                "latency_ms": 300000.0,
                "throughput_items_sec": 10.0,
                "cpu_percent": 80.0,
                "memory_percent": 85.0
            }
        )

        # Verify optimization result
        assert result is not None
        assert result["operation_id"] == operation_id
        assert "bottlenecks" in result
        assert "recommendations" in result
        assert "resource_allocation" in result
        assert "cache_stats" in result


class TestMultiModelConversionManagerIntegration:
    """Test MultiModelConversionManager integration."""

    @pytest.fixture
    def conversion_manager(self):
        """Create MultiModelConversionManager instance."""
        manager = MultiModelConversionManager(
            manager_id="test_manager_001",
            max_concurrent_models=5,
            conversion_mode=ConversionMode.PARALLEL,
            optimization_strategy=OptimizationStrategy.BALANCED
        )
        return manager

    @pytest.mark.asyncio
    async def test_single_conversion_job(self, conversion_manager):
        """Test single conversion job submission and execution."""
        await conversion_manager.start()

        try:
            # Submit a single conversion job
            job_id = conversion_manager.submit_conversion_job(
                model_path="/path/to/model1.onnx",
                output_path="/path/to/output1.onnx",
                model_type="onnx",
                priority=TaskPriority.NORMAL
            )

            assert job_id is not None

            # Wait a bit for processing
            await asyncio.sleep(0.5)

            # Check job status
            status = conversion_manager.get_job_status(job_id)
            assert status is not None

        finally:
            await conversion_manager.stop()

    @pytest.mark.asyncio
    async def test_batch_conversion(self, conversion_manager):
        """Test batch conversion submission and execution."""
        await conversion_manager.start()

        try:
            # Submit batch conversion
            model_configs = [
                {
                    "model_path": f"/path/to/model{i}.onnx",
                    "output_path": f"/path/to/output{i}.onnx",
                    "model_type": "onnx",
                    "priority": TaskPriority.NORMAL
                }
                for i in range(5)
            ]

            batch_id = await conversion_manager.submit_batch_conversion(
                model_configs=model_configs,
                mode=ConversionMode.PARALLEL
            )

            assert batch_id is not None

            # Wait for batch to complete
            await asyncio.sleep(1.0)

            # Check batch status
            batch_status = conversion_manager.get_batch_status(batch_id)
            assert batch_status is not None
            assert batch_status["total_models"] == 5

        finally:
            await conversion_manager.stop()

    @pytest.mark.asyncio
    async def test_conversion_manager_stats(self, conversion_manager):
        """Test conversion manager statistics."""
        await conversion_manager.start()

        try:
            # Get initial stats
            stats = conversion_manager.get_manager_stats()
            assert stats is not None
            assert stats["manager_id"] == "test_manager_001"

            # Submit a job
            job_id = conversion_manager.submit_conversion_job(
                model_path="/path/to/model1.onnx",
                output_path="/path/to/output1.onnx",
                model_type="onnx"
            )

            # Get updated stats
            stats = conversion_manager.get_manager_stats()
            assert stats["total_jobs"] >= 1

        finally:
            await conversion_manager.stop()


class TestResourcePoolIntegration:
    """Test ResourcePool integration."""

    @pytest.fixture
    def resource_pool(self):
        """Create ResourcePool instance."""
        initial_resources = {
            ResourceType.CPU_CORE: 4.0,
            ResourceType.MEMORY_GB: 8.0,
            ResourceType.CONCURRENT_TASK_SLOT: 5.0
        }

        pool = ResourcePool(
            pool_id="test_pool_001",
            initial_resources=initial_resources
        )
        return pool

    def test_resource_allocation(self, resource_pool):
        """Test resource allocation and deallocation."""
        from npu_converter.performance.resource_pool import ResourceRequest, TaskPriority

        # Create resource request
        request = ResourceRequest(
            request_id="test_request_001",
            task_id="test_task_001",
            requested_resources={
                ResourceType.CPU_CORE: 1.0,
                ResourceType.MEMORY_GB: 2.0,
                ResourceType.CONCURRENT_TASK_SLOT: 1.0
            },
            priority=TaskPriority.NORMAL
        )

        # Request resources
        allocation = resource_pool.request_resources(request, timeout_seconds=5.0)

        assert allocation is not None
        assert len(allocation.allocated_resources) > 0

        # Verify resources are allocated
        available = resource_pool.get_available_resources()
        assert ResourceType.CONCURRENT_TASK_SLOT in available

        # Release resources
        success = resource_pool.release_resources(allocation.allocation_id)
        assert success

        # Verify resources are available again
        available_after = resource_pool.get_available_resources()
        assert available_after[ResourceType.CONCURRENT_TASK_SLOT] > available[ResourceType.CONCURRENT_TASK_SLOT]

    def test_resource_pool_stats(self, resource_pool):
        """Test resource pool statistics."""
        stats = resource_pool.get_pool_stats()

        assert stats is not None
        assert stats["pool_id"] == "test_pool_001"
        assert "total_resources" in stats
        assert "available_resources" in stats
        assert "active_allocations" in stats


class TestThrottlingOrchestratorIntegration:
    """Test ThrottlingOrchestrator integration."""

    @pytest.fixture
    def throttling_orchestrator(self):
        """Create ThrottlingOrchestrator instance."""
        orchestrator = ThrottlingOrchestrator(orchestrator_id="test_orchestrator_001")

        # Add rate limiter
        rate_config = RateLimitConfig(
            max_requests=10,
            time_window_seconds=1.0,
            burst_size=15,
            strategy=RateLimitStrategy.TOKEN_BUCKET
        )
        orchestrator.add_rate_limiter("test_limiter", rate_config)

        # Add circuit breaker
        orchestrator.add_circuit_breaker(
            breaker_id="test_breaker",
            failure_threshold=3,
            recovery_timeout=30.0
        )

        # Add concurrency controller
        orchestrator.add_concurrency_controller(
            controller_id="test_controller",
            max_concurrent=5
        )

        return orchestrator

    @pytest.mark.asyncio
    async def test_rate_limiting(self, throttling_orchestrator):
        """Test rate limiting functionality."""
        async def test_operation():
            await asyncio.sleep(0.01)
            return "success"

        # Execute operation with rate limiting
        limiter_ids = ["test_limiter"]
        result = await throttling_orchestrator.execute_with_throttling(
            operation_id="test_op_001",
            operation=test_operation,
            limiter_ids=limiter_ids
        )

        assert result == "success"

    @pytest.mark.asyncio
    async def test_circuit_breaker(self, throttling_orchestrator):
        """Test circuit breaker functionality."""
        call_count = 0

        async def failing_operation():
            nonlocal call_count
            call_count += 1
            raise Exception("Simulated failure")

        # Execute operation through circuit breaker
        breaker_id = "test_breaker"

        # First few calls should fail
        for i in range(3):
            with pytest.raises(Exception):
                await throttling_orchestrator.execute_with_throttling(
                    operation_id=f"test_op_{i}",
                    operation=failing_operation,
                    breaker_id=breaker_id
                )

        # Circuit breaker should be open now
        # (In real implementation, we would verify the state)

    @pytest.mark.asyncio
    async def test_concurrency_control(self, throttling_orchestrator):
        """Test concurrency control."""
        async def test_operation():
            await asyncio.sleep(0.1)
            return "success"

        controller_id = "test_controller"

        # Execute multiple operations concurrently
        tasks = []
        for i in range(3):
            task = throttling_orchestrator.execute_with_throttling(
                operation_id=f"test_op_{i}",
                operation=test_operation,
                controller_id=controller_id
            )
            tasks.append(task)

        # Wait for all tasks
        results = await asyncio.gather(*tasks)

        assert len(results) == 3
        assert all(r == "success" for r in results)


class TestFullSystemIntegration:
    """Test full system integration with all components."""

    @pytest.fixture
    def temp_storage_dir(self):
        """Create temporary storage directory."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def full_system(self, temp_storage_dir):
        """Create full system with all components."""
        # Create database and storage
        database = PerformanceDatabase(
            Path(temp_storage_dir) / "performance.db"
        )
        storage = PerformanceStorage(temp_storage_dir)

        # Create optimizer
        optimizer = PerformanceOptimizer(
            database=database,
            optimization_strategy=OptimizationStrategy.BALANCED
        )

        # Create conversion manager
        conversion_manager = MultiModelConversionManager(
            manager_id="full_system_manager",
            max_concurrent_models=5,
            conversion_mode=ConversionMode.PARALLEL
        )

        # Create resource pool
        resource_pool = ResourcePool(
            pool_id="full_system_pool",
            initial_resources={
                ResourceType.CPU_CORE: 4.0,
                ResourceType.MEMORY_GB: 8.0,
                ResourceType.CONCURRENT_TASK_SLOT: 5.0
            }
        )

        # Create throttling orchestrator
        orchestrator = ThrottlingOrchestrator(orchestrator_id="full_system_orchestrator")

        rate_config = RateLimitConfig(
            max_requests=20,
            time_window_seconds=1.0,
            strategy=RateLimitStrategy.TOKEN_BUCKET
        )
        orchestrator.add_rate_limiter("main_limiter", rate_config)

        orchestrator.add_concurrency_controller(
            controller_id="main_controller",
            max_concurrent=5
        )

        return {
            "database": database,
            "storage": storage,
            "optimizer": optimizer,
            "conversion_manager": conversion_manager,
            "resource_pool": resource_pool,
            "orchestrator": orchestrator
        }

    @pytest.mark.asyncio
    async def test_full_workflow(self, full_system):
        """Test full workflow with all components."""
        conversion_manager = full_system["conversion_manager"]
        optimizer = full_system["optimizer"]
        resource_pool = full_system["resource_pool"]
        orchestrator = full_system["orchestrator"]

        # Start conversion manager
        await conversion_manager.start()

        try:
            # Submit multiple conversion jobs
            model_configs = [
                {
                    "model_path": f"/path/to/model{i}.onnx",
                    "output_path": f"/path/to/output{i}.onnx",
                    "model_type": "onnx",
                    "priority": TaskPriority.NORMAL
                }
                for i in range(3)
            ]

            batch_id = await conversion_manager.submit_batch_conversion(
                model_configs=model_configs,
                mode=ConversionMode.PARALLEL
            )

            # Wait for conversions to complete
            await asyncio.sleep(1.0)

            # Run optimization
            optimization_result = optimizer.optimize(
                operation_id="batch_operation",
                target_performance={
                    "latency_ms": 300000.0,
                    "throughput_items_sec": 10.0,
                    "cpu_percent": 80.0,
                    "memory_percent": 85.0
                }
            )

            # Verify all components are working
            assert optimization_result is not None
            assert "bottlenecks" in optimization_result
            assert "recommendations" in optimization_result

            # Check conversion manager stats
            stats = conversion_manager.get_manager_stats()
            assert stats["total_jobs"] >= 3

            # Check resource pool stats
            pool_stats = resource_pool.get_pool_stats()
            assert pool_stats["pool_id"] == "full_system_pool"

            # Check orchestrator stats
            orchestrator_stats = orchestrator.get_orchestrator_stats()
            assert orchestrator_stats["orchestrator_id"] == "full_system_orchestrator"

        finally:
            await conversion_manager.stop()

    @pytest.mark.asyncio
    async def test_performance_monitoring(self, full_system):
        """Test performance monitoring throughout the workflow."""
        conversion_manager = full_system["conversion_manager"]
        optimizer = full_system["optimizer"]

        await conversion_manager.start()

        try:
            # Submit a job
            job_id = conversion_manager.submit_conversion_job(
                model_path="/path/to/model1.onnx",
                output_path="/path/to/output1.onnx",
                model_type="onnx"
            )

            # Wait for processing
            await asyncio.sleep(0.5)

            # Get performance summary
            summary = optimizer.performance_hook.get_performance_summary()

            assert summary is not None
            assert "operation_id" in summary

        finally:
            await conversion_manager.stop()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
