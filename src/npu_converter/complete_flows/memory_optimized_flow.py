"""
内存优化转换流程

这是一个示例，展示如何将 Story 3.2 内存优化系统集成到现有转换流程中。
此模块展示了在转换过程中应用内存优化最佳实践的方法。

作者: Claude Code / Story 3.2
版本: 1.0
日期: 2025-10-28
"""

from typing import Any, Dict, List, Optional, Union, Tuple, Callable
from pathlib import Path
import logging
import time
from datetime import datetime

from ..memory import MemoryOptimizationSystem
from ..config.memory_optimization_config import MemoryOptimizationConfig, MemoryOptimizationPresets

logger = logging.getLogger(__name__)


class MemoryOptimizedConversionFlow:
    """
    内存优化的转换流程示例

    此示例展示了如何将内存优化系统集成到转换流程中，
    包括在转换前、转换中和转换后的内存优化应用。

    集成点:
    1. 转换前: 初始化内存优化系统
    2. 转换中: 应用内存优化策略
    3. 转换后: 生成内存优化报告

    用法:
        flow = MemoryOptimizedConversionFlow()
        result = flow.convert_model(model_path, preset='standard')
    """

    def __init__(
        self,
        optimization_preset: str = "standard",
        custom_config: Optional[MemoryOptimizationConfig] = None,
        auto_optimize: bool = True,
        generate_report: bool = True,
    ):
        """
        初始化内存优化转换流程

        Args:
            optimization_preset: 内存优化预设 ('low_memory', 'standard', 'high_performance', 'batch_processing')
            custom_config: 自定义内存优化配置
            auto_optimize: 是否自动应用内存优化
            generate_report: 是否生成优化报告
        """
        self.auto_optimize = auto_optimize
        self.generate_report = generate_report

        # 初始化内存优化系统
        if custom_config:
            self.memory_optimizer = MemoryOptimizationSystem(custom_config)
        else:
            self.memory_optimizer = self._create_optimizer_from_preset(optimization_preset)

        self.optimization_report: Optional[Dict[str, Any]] = None
        self.conversion_stats: Dict[str, Any] = {}

    def _create_optimizer_from_preset(self, preset: str) -> MemoryOptimizationSystem:
        """从预设创建内存优化系统"""
        config = MemoryOptimizationPresets.get_preset(preset)
        if not config:
            raise ValueError(f"无效的优化预设: {preset}")
        return MemoryOptimizationSystem(config)

    def convert_model(
        self,
        model_data: Any,
        model_path: Optional[Union[str, Path]] = None,
        conversion_params: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Any, Dict[str, Any]]:
        """
        执行内存优化的模型转换

        Args:
            model_data: 模型数据
            model_path: 模型文件路径
            conversion_params: 转换参数

        Returns:
            Tuple[转换结果, 优化报告]

        Raises:
            Exception: 转换过程中发生错误
        """
        logger.info("开始内存优化的模型转换")

        # 阶段1: 转换前内存优化
        self._pre_conversion_optimization()

        # 阶段2: 执行转换（模拟）
        conversion_start = time.time()
        try:
            # 启动内存监控
            self.memory_optimizer.start()

            # 应用内存优化到模型数据
            if self.auto_optimize:
                optimized_model_data, optimization_result = self.memory_optimizer.optimize_data(model_data)
            else:
                optimized_model_data = model_data
                optimization_result = None

            # 执行实际转换（这里模拟转换过程）
            conversion_result = self._execute_conversion(optimized_model_data, conversion_params)

            conversion_time = time.time() - conversion_start

            # 记录转换统计
            self.conversion_stats = {
                "conversion_time": conversion_time,
                "model_size": self._estimate_size(model_data),
                "optimized": self.auto_optimize,
                "timestamp": datetime.now().isoformat(),
            }

            # 阶段3: 转换后优化和报告
            if self.generate_report:
                self.optimization_report = self._generate_optimization_report(
                    conversion_result, optimization_result
                )

            logger.info(f"转换完成，耗时: {conversion_time:.2f}秒")

            return conversion_result, self.optimization_report or {}

        finally:
            # 确保停止内存监控
            self.memory_optimizer.stop()

    def _pre_conversion_optimization(self):
        """转换前内存优化"""
        logger.debug("应用转换前内存优化")

        # 可以在这里执行转换前的内存优化操作
        # 例如：清理缓存、预热内存池等

    def _execute_conversion(self, model_data: Any, params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """执行实际的模型转换（示例实现）"""
        logger.debug("执行模型转换")

        # 模拟转换过程
        # 在实际应用中，这里会调用实际的转换逻辑

        # 模拟转换时间
        time.sleep(0.1)

        # 模拟转换结果
        result = {
            "status": "success",
            "input_size": self._estimate_size(model_data),
            "output_format": "optimized_model",
            "conversion_params": params or {},
        }

        return result

    def _generate_optimization_report(
        self,
        conversion_result: Dict[str, Any],
        optimization_result: Optional[Any],
    ) -> Dict[str, Any]:
        """生成内存优化报告"""
        logger.debug("生成内存优化报告")

        # 获取优化系统报告
        optimizer_report = self.memory_optimizer.get_optimization_report()

        # 合并转换统计
        optimizer_report["conversion"] = self.conversion_stats
        optimizer_report["conversion_result"] = conversion_result

        return optimizer_report

    def _estimate_size(self, data: Any) -> int:
        """估算数据大小（字节）"""
        try:
            import sys
            return sys.getsizeof(data)
        except:
            return 0

    def get_optimization_summary(self) -> Optional[Dict[str, Any]]:
        """获取优化摘要"""
        if not self.optimization_report:
            return None

        return {
            "memory_efficiency": self.optimization_report.get("metrics", {}).get("efficiency", 0),
            "optimization_applied": self.optimization_report.get("config", {}).get("strategies", {}),
            "conversion_time": self.conversion_stats.get("conversion_time", 0),
            "recommendations": self.optimization_report.get("recommendations", []),
        }

    def compare_with_baseline(
        self,
        baseline_conversion: Callable[[Any], Dict[str, Any]],
        model_data: Any,
        iterations: int = 5,
    ) -> Dict[str, Any]:
        """
        与基线转换进行性能比较

        Args:
            baseline_conversion: 基线转换函数
            model_data: 模型数据
            iterations: 比较迭代次数

        Returns:
            比较结果字典
        """
        logger.info(f"开始性能比较 ({iterations} 次迭代)")

        # 测试基线转换
        baseline_times = []
        for _ in range(iterations):
            start = time.time()
            baseline_conversion(model_data)
            baseline_times.append(time.time() - start)

        baseline_avg = sum(baseline_times) / len(baseline_times)

        # 测试优化转换
        optimized_times = []
        for _ in range(iterations):
            start = time.time()
            self.convert_model(model_data)
            optimized_times.append(time.time() - start)

        optimized_avg = sum(optimized_times) / len(optimized_times)

        # 计算性能提升
        improvement = ((baseline_avg - optimized_avg) / baseline_avg) * 100

        comparison_result = {
            "baseline_time": baseline_avg,
            "optimized_time": optimized_avg,
            "improvement_percent": improvement,
            "baseline_times": baseline_times,
            "optimized_times": optimized_times,
            "iterations": iterations,
        }

        logger.info(f"性能比较完成，提升: {improvement:.2f}%")

        return comparison_result


# 便捷函数
def convert_with_memory_optimization(
    model_data: Any,
    preset: str = "standard",
    generate_report: bool = True,
) -> Tuple[Any, Dict[str, Any]]:
    """
    使用内存优化进行模型转换的便捷函数

    Args:
        model_data: 模型数据
        preset: 优化预设
        generate_report: 是否生成报告

    Returns:
        Tuple[转换结果, 优化报告]
    """
    flow = MemoryOptimizedConversionFlow(
        optimization_preset=preset,
        generate_report=generate_report,
    )

    return flow.convert_model(model_data)


# 示例基线转换函数
def baseline_conversion(model_data: Any) -> Dict[str, Any]:
    """基线转换函数（无优化）"""
    time.sleep(0.1)  # 模拟转换时间
    return {"status": "success", "method": "baseline"}


if __name__ == "__main__":
    # 使用示例
    print("=" * 60)
    print("内存优化转换流程示例")
    print("=" * 60)

    # 示例1: 使用便捷函数
    print("\n示例1: 使用便捷函数")
    test_data = list(range(10000))
    result, report = convert_with_memory_optimization(test_data, preset='standard')
    print(f"转换状态: {result['status']}")
    print(f"内存效率: {report.get('metrics', {}).get('efficiency', 0):.2%}")

    # 示例2: 使用完整流程
    print("\n示例2: 使用完整流程")
    flow = MemoryOptimizedConversionFlow(
        optimization_preset='high_performance',
        auto_optimize=True,
        generate_report=True,
    )

    result, report = flow.convert_model(test_data)
    summary = flow.get_optimization_summary()

    print(f"转换时间: {summary['conversion_time']:.4f}秒")
    print(f"内存效率: {summary['memory_efficiency']:.2%}")
    print(f"优化策略: {sum(1 for v in summary['optimization_applied'].values() if v)} 项启用")

    # 示例3: 性能比较
    print("\n示例3: 性能比较")
    comparison = flow.compare_with_baseline(
        baseline_conversion=baseline_conversion,
        model_data=test_data,
        iterations=3,
    )

    print(f"基线转换时间: {comparison['baseline_time']:.4f}秒")
    print(f"优化转换时间: {comparison['optimized_time']:.4f}秒")
    print(f"性能提升: {comparison['improvement_percent']:.2f}%")

    print("\n" + "=" * 60)
    print("示例执行完成")
    print("=" * 60)
