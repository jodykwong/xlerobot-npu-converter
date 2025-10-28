"""
内存使用优化模块

为Story 3.2: 内存使用优化提供完整的内存管理能力，
包括监控、优化、分析、泄漏检测等功能。

作者: Claude Code / BMM v6
版本: 1.0
日期: 2025-10-28
"""

from .memory_optimization_system import (
    MemoryOptimizationSystem,
    MemoryMonitor,
    MemoryOptimizer,
    MemoryAnalyzer,
    MemoryLeakDetector,
    MemoryMetrics,
    OptimizationResult,
    create_memory_optimizer,
    optimize_memory_usage,
    get_default_optimizer,
    optimize_with_defaults,
)

__all__ = [
    "MemoryOptimizationSystem",
    "MemoryMonitor",
    "MemoryOptimizer",
    "MemoryAnalyzer",
    "MemoryLeakDetector",
    "MemoryMetrics",
    "OptimizationResult",
    "create_memory_optimizer",
    "optimize_memory_usage",
    "get_default_optimizer",
    "optimize_with_defaults",
]

__version__ = "1.0.0"
__author__ = "Claude Code / BMM v6"
