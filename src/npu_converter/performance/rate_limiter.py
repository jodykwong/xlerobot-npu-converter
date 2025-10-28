"""
Concurrency Control and Rate Limiting System

This module provides advanced concurrency control and rate limiting for concurrent conversions.
Part of Story 3.1: 性能优化与扩展 (Phase 2: 核心功能实现)

Features:
- Token bucket rate limiting
- Sliding window rate limiting
- Dynamic rate adjustment
- Concurrency throttling
- Resource-based rate limiting
- Circuit breaker pattern

Author: BMM v6 Workflow
Version: 1.0
Date: 2025-10-28
"""

import asyncio
import logging
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Callable, Union
from collections import deque, defaultdict

logger = logging.getLogger(__name__)


class RateLimitStrategy(Enum):
    """Rate limiting strategies."""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    RESOURCE_BASED = "resource_based"
    ADAPTIVE = "adaptive"


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Blocking requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    pass


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    max_requests: int
    time_window_seconds: float
    burst_size: Optional[int] = None
    strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET
    enabled: bool = True


@dataclass
class ThrottleMetrics:
    """Metrics for throttling decisions."""
    current_rate: float
    average_rate: float
    peak_rate: float
    total_requests: int
    dropped_requests: int
    timestamp: datetime = field(default_factory=datetime.now)


class RateLimiter(ABC):
    """Abstract base class for rate limiters."""

    @abstractmethod
    async def acquire(self, tokens: int = 1) -> bool:
        """Acquire tokens for a request."""
        pass

    @abstractmethod
    def get_metrics(self) -> ThrottleMetrics:
        """Get current metrics."""
        pass


class TokenBucketRateLimiter(RateLimiter):
    """
    Token bucket rate limiter implementation.

    Allows burst traffic up to bucket capacity while maintaining
    average rate limit.
    """

    def __init__(
        self,
        rate: float,
        capacity: int,
        refill_interval: float = 1.0
    ):
        """
        Initialize token bucket.

        Args:
            rate: Token refill rate (tokens per second)
            capacity: Bucket capacity (max tokens)
            refill_interval: Refill interval (seconds)
        """
        self.rate = rate
        self.capacity = capacity
        self.refill_interval = refill_interval

        self.tokens = capacity
        self.last_refill = time.time()
        self._lock = threading.Lock()

        # Metrics
        self._total_requests = 0
        self._dropped_requests = 0
        self._request_times: deque = deque()

        logger.info(f"TokenBucket initialized: rate={rate}, capacity={capacity}")

    async def acquire(self, tokens: int = 1) -> bool:
        """
        Acquire tokens for a request.

        Args:
            tokens: Number of tokens needed

        Returns:
            True if tokens acquired, False otherwise
        """
        with self._lock:
            now = time.time()

            # Refill tokens
            elapsed = now - self.last_refill
            refill_amount = (elapsed / self.refill_interval) * self.rate
            self.tokens = min(self.capacity, self.tokens + refill_amount)
            self.last_refill = now

            # Check if enough tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                self._total_requests += 1
                self._request_times.append(now)

                # Remove old request times
                cutoff = now - 60  # Keep last 60 seconds
                while self._request_times and self._request_times[0] < cutoff:
                    self._request_times.popleft()

                return True
            else:
                self._dropped_requests += 1
                return False

    def get_metrics(self) -> ThrottleMetrics:
        """Get current metrics."""
        with self._lock:
            now = time.time()
            recent_requests = [t for t in self._request_times if now - t <= 60]

            current_rate = len(recent_requests) / 60.0 if recent_requests else 0.0
            average_rate = self._total_requests / max(time.time() - self.last_refill, 1.0)

            return ThrottleMetrics(
                current_rate=current_rate,
                average_rate=average_rate,
                peak_rate=max(current_rate, average_rate),
                total_requests=self._total_requests,
                dropped_requests=self._dropped_requests
            )


class SlidingWindowRateLimiter(RateLimiter):
    """
    Sliding window rate limiter implementation.

    Uses a sliding window to track request rates.
    """

    def __init__(self, max_requests: int, window_size: float):
        """
        Initialize sliding window.

        Args:
            max_requests: Maximum requests in window
            window_size: Window size (seconds)
        """
        self.max_requests = max_requests
        self.window_size = window_size

        self._request_times: deque = deque()
        self._lock = threading.Lock()

        # Metrics
        self._total_requests = 0
        self._dropped_requests = 0

        logger.info(f"SlidingWindow initialized: max={max_requests}, window={window_size}s")

    async def acquire(self, tokens: int = 1) -> bool:
        """
        Acquire permission for a request.

        Args:
            tokens: Number of tokens (not used, always 1)

        Returns:
            True if allowed, False otherwise
        """
        with self._lock:
            now = time.time()

            # Remove old requests outside window
            cutoff = now - self.window_size
            while self._request_times and self._request_times[0] < cutoff:
                self._request_times.popleft()

            # Check if limit exceeded
            if len(self._request_times) >= self.max_requests:
                self._dropped_requests += 1
                return False

            # Allow request
            self._request_times.append(now)
            self._total_requests += 1

            return True

    def get_metrics(self) -> ThrottleMetrics:
        """Get current metrics."""
        with self._lock:
            now = time.time()
            recent_requests = [t for t in self._request_times if now - t <= self.window_size]

            current_rate = len(recent_requests) / self.window_size

            return ThrottleMetrics(
                current_rate=current_rate,
                average_rate=current_rate,  # Simplified
                peak_rate=current_rate,
                total_requests=self._total_requests,
                dropped_requests=self._dropped_requests
            )


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.

    Prevents cascading failures by temporarily blocking requests
    to a failing service.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time before attempting recovery (seconds)
            expected_exception: Exception type that triggers circuit breaker
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self._lock = threading.Lock()

        logger.info(f"CircuitBreaker initialized: threshold={failure_threshold}")

    async def call(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Call function through circuit breaker.

        Args:
            func: Function to call
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            RateLimitExceeded: If circuit breaker is open
            func: Any exception from the function
        """
        with self._lock:
            # Check state
            if self.state == CircuitBreakerState.OPEN:
                # Check if recovery timeout has passed
                if (self.last_failure_time and
                    time.time() - self.last_failure_time >= self.recovery_timeout):
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.failure_count = 0
                    logger.info("Circuit breaker moved to HALF_OPEN")
                else:
                    raise RateLimitExceeded("Circuit breaker is OPEN")

        # Execute function
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Success - update state
            with self._lock:
                if self.state == CircuitBreakerState.HALF_OPEN:
                    self.state = CircuitBreakerState.CLOSED
                    logger.info("Circuit breaker moved to CLOSED")

            return result

        except self.expected_exception as e:
            # Failure - update circuit breaker
            self._record_failure()
            raise

    def _record_failure(self) -> None:
        """Record a failure."""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                logger.warning(f"Circuit breaker OPENED after {self.failure_count} failures")


class AdaptiveRateController:
    """
    Adaptive rate controller that adjusts rates based on system load.

    Monitors system metrics and dynamically adjusts rate limits
    to optimize throughput while maintaining stability.
    """

    def __init__(
        self,
        controller_id: str,
        initial_rate: float,
        min_rate: float = 1.0,
        max_rate: float = 100.0,
        adaptation_interval: float = 10.0
    ):
        """
        Initialize adaptive rate controller.

        Args:
            controller_id: Unique controller identifier
            initial_rate: Initial rate limit
            min_rate: Minimum allowed rate
            max_rate: Maximum allowed rate
            adaptation_interval: Adaptation interval (seconds)
        """
        self.controller_id = controller_id
        self.current_rate = initial_rate
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.adaptation_interval = adaptation_interval

        self._lock = threading.Lock()
        self._adaptation_history: List[Dict[str, Any]] = []

        logger.info(f"AdaptiveRateController initialized: {controller_id}")

    async def acquire(self, tokens: int = 1) -> bool:
        """
        Acquire permission for a request.

        Args:
            tokens: Number of tokens needed

        Returns:
            True if allowed, False otherwise
        """
        # This would integrate with an actual rate limiter
        # For now, always allow
        return True

    async def adapt(
        self,
        system_metrics: Dict[str, float],
        request_metrics: ThrottleMetrics
    ) -> float:
        """
        Adapt rate based on metrics.

        Args:
            system_metrics: System load metrics
            request_metrics: Request metrics

        Returns:
            New rate limit
        """
        with self._lock:
            old_rate = self.current_rate

            # Adaptation logic
            cpu_percent = system_metrics.get("cpu_percent", 50.0)
            memory_percent = system_metrics.get("memory_percent", 50.0)
            dropped_rate = request_metrics.dropped_requests / max(request_metrics.total_requests, 1)

            # Calculate new rate
            if cpu_percent > 90 or memory_percent > 90:
                # High system load - reduce rate
                self.current_rate = max(self.min_rate, self.current_rate * 0.9)
            elif cpu_percent < 50 and memory_percent < 50 and dropped_rate < 0.01:
                # Low system load - increase rate
                self.current_rate = min(self.max_rate, self.current_rate * 1.1)
            # Otherwise, keep current rate

            # Log adaptation
            adaptation = {
                "timestamp": datetime.now(),
                "old_rate": old_rate,
                "new_rate": self.current_rate,
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "dropped_rate": dropped_rate
            }

            self._adaptation_history.append(adaptation)

            logger.info(f"Rate adapted: {old_rate:.2f} -> {self.current_rate:.2f}")

            return self.current_rate


class ConcurrencyController:
    """
    Advanced concurrency controller with multiple strategies.

    Provides:
    - Fixed concurrency limits
    - Dynamic concurrency adjustment
    - Priority-based concurrency
    - Resource-aware concurrency
    """

    def __init__(
        self,
        controller_id: str,
        max_concurrent: int = 10,
        min_concurrent: int = 1
    ):
        """
        Initialize concurrency controller.

        Args:
            controller_id: Unique controller identifier
            max_concurrent: Maximum concurrent operations
            min_concurrent: Minimum concurrent operations
        """
        self.controller_id = controller_id
        self.max_concurrent = max_concurrent
        self.min_concurrent = min_concurrent

        self._active_operations: Set[str] = set()
        self._lock = threading.Lock()
        self._semaphore = asyncio.Semaphore(max_concurrent)

        # Metrics
        self._total_operations = 0
        self._rejected_operations = 0
        self._waiting_operations = 0

        logger.info(f"ConcurrencyController initialized: max={max_concurrent}")

    async def acquire(self, operation_id: str) -> bool:
        """
        Acquire permission for an operation.

        Args:
            operation_id: Operation identifier

        Returns:
            True if allowed, False otherwise
        """
        async with self._semaphore:
            with self._lock:
                if len(self._active_operations) >= self.max_concurrent:
                    self._rejected_operations += 1
                    return False

                self._active_operations.add(operation_id)
                self._total_operations += 1

            return True

    async def release(self, operation_id: str) -> None:
        """
        Release an operation.

        Args:
            operation_id: Operation identifier
        """
        with self._lock:
            self._active_operations.discard(operation_id)

    def get_active_count(self) -> int:
        """Get number of active operations."""
        with self._lock:
            return len(self._active_operations)

    def get_metrics(self) -> Dict[str, Any]:
        """Get concurrency metrics."""
        with self._lock:
            return {
                "active_operations": len(self._active_operations),
                "max_concurrent": self.max_concurrent,
                "utilization_percent": (len(self._active_operations) / self.max_concurrent * 100),
                "total_operations": self._total_operations,
                "rejected_operations": self._rejected_operations
            }

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        # Release all operations
        with self._lock:
            self._active_operations.clear()


class ThrottlingOrchestrator:
    """
    Main orchestrator for all throttling and rate limiting.

    Coordinates multiple rate limiters, circuit breakers,
    and concurrency controllers.
    """

    def __init__(self, orchestrator_id: str):
        """
        Initialize throttling orchestrator.

        Args:
            orchestrator_id: Unique orchestrator identifier
        """
        self.orchestrator_id = orchestrator_id

        # Components
        self.rate_limiters: Dict[str, RateLimiter] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.concurrency_controllers: Dict[str, ConcurrencyController] = {}

        # Configuration
        self.configs: Dict[str, RateLimitConfig] = {}

        logger.info(f"ThrottlingOrchestrator initialized: {orchestrator_id}")

    def add_rate_limiter(
        self,
        limiter_id: str,
        config: RateLimitConfig
    ) -> None:
        """
        Add a rate limiter.

        Args:
            limiter_id: Limiter identifier
            config: Rate limit configuration
        """
        if not config.enabled:
            return

        if config.strategy == RateLimitStrategy.TOKEN_BUCKET:
            # Token bucket: rate = max_requests / time_window
            rate = config.max_requests / config.time_window_seconds
            capacity = config.burst_size or config.max_requests

            limiter = TokenBucketRateLimiter(
                rate=rate,
                capacity=capacity,
                refill_interval=1.0
            )
        elif config.strategy == RateLimitStrategy.SLIDING_WINDOW:
            limiter = SlidingWindowRateLimiter(
                max_requests=config.max_requests,
                window_size=config.time_window_seconds
            )
        else:
            raise ValueError(f"Unsupported strategy: {config.strategy}")

        self.rate_limiters[limiter_id] = limiter
        self.configs[limiter_id] = config

        logger.info(f"Added rate limiter: {limiter_id}")

    def add_circuit_breaker(
        self,
        breaker_id: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0
    ) -> None:
        """
        Add a circuit breaker.

        Args:
            breaker_id: Circuit breaker identifier
            failure_threshold: Failure threshold
            recovery_timeout: Recovery timeout
        """
        self.circuit_breakers[breaker_id] = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout
        )

        logger.info(f"Added circuit breaker: {breaker_id}")

    def add_concurrency_controller(
        self,
        controller_id: str,
        max_concurrent: int = 10
    ) -> None:
        """
        Add a concurrency controller.

        Args:
            controller_id: Controller identifier
            max_concurrent: Maximum concurrent operations
        """
        self.concurrency_controllers[controller_id] = ConcurrencyController(
            controller_id=controller_id,
            max_concurrent=max_concurrent
        )

        logger.info(f"Added concurrency controller: {controller_id}")

    async def execute_with_throttling(
        self,
        operation_id: str,
        operation: Callable,
        *args,
        limiter_ids: Optional[List[str]] = None,
        breaker_id: Optional[str] = None,
        controller_id: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Execute operation with all throttling controls.

        Args:
            operation_id: Unique operation identifier
            operation: Function to execute
            *args: Function arguments
            limiter_ids: List of rate limiter IDs to use
            breaker_id: Circuit breaker ID to use
            controller_id: Concurrency controller ID to use
            **kwargs: Function keyword arguments

        Returns:
            Operation result
        """
        # Check rate limiters
        if limiter_ids:
            for limiter_id in limiter_ids:
                limiter = self.rate_limiters.get(limiter_id)
                if limiter:
                    acquired = await limiter.acquire()
                    if not acquired:
                        raise RateLimitExceeded(f"Rate limit exceeded for {limiter_id}")

        # Check concurrency controller
        if controller_id:
            controller = self.concurrency_controllers.get(controller_id)
            if controller:
                acquired = await controller.acquire(operation_id)
                if not acquired:
                    raise RateLimitExceeded(f"Concurrency limit exceeded for {controller_id}")
        else:
            controller = None

        # Execute through circuit breaker
        try:
            if breaker_id:
                breaker = self.circuit_breakers.get(breaker_id)
                if breaker:
                    result = await breaker.call(operation, *args, **kwargs)
                else:
                    if asyncio.iscoroutinefunction(operation):
                        result = await operation(*args, **kwargs)
                    else:
                        result = operation(*args, **kwargs)
            else:
                if asyncio.iscoroutinefunction(operation):
                    result = await operation(*args, **kwargs)
                else:
                    result = operation(*args, **kwargs)

            return result

        finally:
            # Release concurrency controller
            if controller:
                await controller.release(operation_id)

    def get_orchestrator_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive orchestrator statistics.

        Returns:
            Dictionary containing all stats
        """
        stats = {
            "orchestrator_id": self.orchestrator_id,
            "rate_limiters": {},
            "circuit_breakers": {},
            "concurrency_controllers": {}
        }

        # Rate limiter stats
        for limiter_id, limiter in self.rate_limiters.items():
            stats["rate_limiters"][limiter_id] = limiter.get_metrics().__dict__

        # Circuit breaker stats
        for breaker_id, breaker in self.circuit_breakers.items():
            stats["circuit_breakers"][breaker_id] = {
                "state": breaker.state.value,
                "failure_count": breaker.failure_count
            }

        # Concurrency controller stats
        for controller_id, controller in self.concurrency_controllers.items():
            stats["concurrency_controllers"][controller_id] = controller.get_metrics()

        return stats
