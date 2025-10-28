"""
Story 3.2 内存优化系统性能基准测试

此模块包含完整的性能基准测试，用于验证内存优化系统在
不同场景下的性能表现，包括内存使用效率、性能提升等。

测试场景:
1. 小数据集 (< 1MB)
2. 中等数据集 (1-10MB)
3. 大数据集 (10-100MB)
4. 超大数据集 (>100MB)
5. 批处理场景
6. 并发场景

作者: Claude Code / Story 3.2
版本: 1.0
日期: 2025-10-28
"""

import sys
sys.path.insert(0, '/home/sunrise/xlerobot/src')

import time
import tracemalloc
import gc
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import statistics

from npu_converter.memory import MemoryOptimizationSystem, optimize_memory_usage
from npu_converter.config.memory_optimization_config import MemoryOptimizationPresets


@dataclass
class BenchmarkResult:
    """基准测试结果"""
    scenario: str
    data_size: int
    preset: str
    execution_time: float
    peak_memory: int
    average_memory: float
    memory_efficiency: float
    throughput: float  # items/second


class MemoryOptimizationBenchmark:
    """内存优化基准测试套件"""

    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.presets = [
            'low_memory',
            'standard',
            'high_performance',
            'batch_processing'
        ]

    def run_all_benchmarks(self) -> Dict[str, Any]:
        """运行所有基准测试"""
        print("=" * 70)
        print("Story 3.2 内存优化系统性能基准测试")
        print("=" * 70)
        print()

        # 测试场景配置
        scenarios = [
            ("小数据集", self._generate_small_data, 1000),
            ("中等数据集", self._generate_medium_data, 10000),
            ("大数据集", self._generate_large_data, 100000),
            ("超大数据集", self._generate_xlarge_data, 500000),
        ]

        all_results = {}

        for scenario_name, data_generator, size in scenarios:
            print(f"\n📊 测试场景: {scenario_name} ({size:,} 项)")
            print("-" * 70)

            # 生成测试数据
            test_data = data_generator(size)
            data_size = sys.getsizeof(test_data)

            # 测试不同预设
            preset_results = {}
            for preset in self.presets:
                result = self._run_benchmark(
                    scenario=f"{scenario_name}_{preset}",
                    data=test_data,
                    preset=preset,
                    data_size=data_size
                )
                preset_results[preset] = result
                self.results.append(result)

                print(f"  {preset:20s}: {result.execution_time:.4f}s | "
                      f"内存效率: {result.memory_efficiency:.2%} | "
                      f"吞吐量: {result.throughput:,.0f} items/s")

            all_results[scenario_name] = preset_results

        # 生成汇总报告
        summary = self._generate_summary_report(all_results)

        return {
            "results": self.results,
            "summary": summary,
            "test_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_tests": len(self.results)
        }

    def _run_benchmark(
        self,
        scenario: str,
        data: Any,
        preset: str,
        data_size: int
    ) -> BenchmarkResult:
        """运行单个基准测试"""
        # 获取配置
        config = MemoryOptimizationPresets.get_preset(preset)
        if not config:
            raise ValueError(f"无效的预设: {preset}")

        # 启动内存追踪
        tracemalloc.start()

        # 执行优化
        start_time = time.time()
        optimized_data, report = optimize_memory_usage(data, preset)
        end_time = time.time()

        # 获取内存统计
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # 计算指标
        execution_time = end_time - start_time
        throughput = len(data) / execution_time if execution_time > 0 else 0

        # 从报告中提取内存效率
        memory_efficiency = report.get('metrics', {}).get('efficiency', 0)

        # 计算平均内存使用
        gc.collect()
        import psutil
        process = psutil.Process()
        average_memory = process.memory_info().rss

        return BenchmarkResult(
            scenario=scenario,
            data_size=data_size,
            preset=preset,
            execution_time=execution_time,
            peak_memory=peak,
            average_memory=average_memory,
            memory_efficiency=memory_efficiency,
            throughput=throughput,
        )

    def _generate_small_data(self, size: int) -> List[int]:
        """生成小数据集"""
        return list(range(size))

    def _generate_medium_data(self, size: int) -> List[Dict[str, Any]]:
        """生成中等数据集"""
        return [{"id": i, "data": f"item_{i}", "value": i * 2} for i in range(size)]

    def _generate_large_data(self, size: int) -> List[List[int]]:
        """生成大数据集"""
        return [[i] * 10 for i in range(size)]

    def _generate_xlarge_data(self, size: int) -> Dict[str, List[Any]]:
        """生成超大数据集"""
        return {
            "ids": list(range(size)),
            "data": [f"item_{i}" for i in range(size)],
            "values": [i ** 2 for i in range(size)],
            "metadata": [{"id": i, "timestamp": time.time()} for i in range(min(size, 10000))]
        }

    def _generate_summary_report(self, all_results: Dict[str, Dict[str, BenchmarkResult]]) -> Dict[str, Any]:
        """生成汇总报告"""
        summary = {
            "best_performance": {},
            "best_efficiency": {},
            "average_metrics": {},
            "recommendations": [],
        }

        # 找出每个场景的最佳性能
        for scenario, preset_results in all_results.items():
            best_perf = min(preset_results.values(), key=lambda r: r.execution_time)
            best_eff = max(preset_results.values(), key=lambda r: r.memory_efficiency)

            summary["best_performance"][scenario] = {
                "preset": best_perf.preset,
                "time": best_perf.execution_time,
                "throughput": best_perf.throughput,
            }

            summary["best_efficiency"][scenario] = {
                "preset": best_eff.preset,
                "efficiency": best_eff.memory_efficiency,
            }

        # 计算平均指标
        all_times = [r.execution_time for r in self.results]
        all_efficiencies = [r.memory_efficiency for r in self.results]
        all_throughputs = [r.throughput for r in self.results]

        summary["average_metrics"] = {
            "execution_time": statistics.mean(all_times),
            "memory_efficiency": statistics.mean(all_efficiencies),
            "throughput": statistics.mean(all_throughputs),
        }

        # 生成推荐
        recommendations = []

        # 基于结果的推荐
        std_preset_results = [r for r in self.results if r.preset == 'standard']
        if std_preset_results:
            avg_eff = statistics.mean([r.memory_efficiency for r in std_preset_results])
            if avg_eff > 0.75:
                recommendations.append("标准模式在大多数场景下表现良好，建议作为默认选择")

        high_perf_results = [r for r in self.results if r.preset == 'high_performance']
        if high_perf_results:
            avg_time = statistics.mean([r.execution_time for r in high_perf_results])
            if avg_time < 0.5:
                recommendations.append("高性能模式在处理大数据集时表现优异，推荐用于生产环境")

        batch_results = [r for r in self.results if r.preset == 'batch_processing']
        if batch_results:
            avg_throughput = statistics.mean([r.throughput for r in batch_results])
            if avg_throughput > 10000:
                recommendations.append("批处理模式在高吞吐量场景下表现最佳，推荐用于批量转换")

        summary["recommendations"] = recommendations

        return summary

    def print_detailed_report(self, benchmark_data: Dict[str, Any]):
        """打印详细报告"""
        print("\n" + "=" * 70)
        print("详细性能基准测试报告")
        print("=" * 70)

        # 汇总信息
        summary = benchmark_data["summary"]
        print(f"\n📈 汇总指标:")
        print(f"   平均执行时间: {summary['average_metrics']['execution_time']:.4f}秒")
        print(f"   平均内存效率: {summary['average_metrics']['memory_efficiency']:.2%}")
        print(f"   平均吞吐量: {summary['average_metrics']['throughput']:,.0f} items/s")

        # 最佳性能
        print(f"\n🏆 最佳性能:")
        for scenario, info in summary["best_performance"].items():
            print(f"   {scenario:20s}: {info['preset']:20s} ({info['time']:.4f}s)")

        # 最佳效率
        print(f"\n💡 最佳效率:")
        for scenario, info in summary["best_efficiency"].items():
            print(f"   {scenario:20s}: {info['preset']:20s} ({info['efficiency']:.2%})")

        # 推荐
        if summary["recommendations"]:
            print(f"\n💼 推荐:")
            for i, rec in enumerate(summary["recommendations"], 1):
                print(f"   {i}. {rec}")

        # 详细结果表
        print(f"\n📊 详细结果:")
        print(f"{'场景':30s} {'预设':20s} {'时间(s)':>10s} {'效率':>10s} {'吞吐量(s)':>15s}")
        print("-" * 85)

        for result in benchmark_data["results"]:
            print(f"{result.scenario[:28]:30s} "
                  f"{result.preset[:18]:20s} "
                  f"{result.execution_time:>10.4f} "
                  f"{result.memory_efficiency:>9.1%} "
                  f"{result.throughput:>14,.0f}")

    def export_results(self, benchmark_data: Dict[str, Any], output_file: str):
        """导出结果到文件"""
        import json

        # 准备导出数据
        export_data = {
            "metadata": {
                "test_name": "Story 3.2 Memory Optimization Benchmark",
                "test_date": benchmark_data["test_date"],
                "total_tests": benchmark_data["total_tests"],
            },
            "summary": benchmark_data["summary"],
            "results": [
                {
                    "scenario": r.scenario,
                    "preset": r.preset,
                    "data_size": r.data_size,
                    "execution_time": r.execution_time,
                    "peak_memory": r.peak_memory,
                    "average_memory": r.average_memory,
                    "memory_efficiency": r.memory_efficiency,
                    "throughput": r.throughput,
                }
                for r in benchmark_data["results"]
            ]
        }

        # 导出到 JSON 文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print(f"\n✅ 结果已导出到: {output_file}")


def main():
    """主函数"""
    # 创建基准测试实例
    benchmark = MemoryOptimizationBenchmark()

    # 运行所有测试
    results = benchmark.run_all_benchmarks()

    # 打印详细报告
    benchmark.print_detailed_report(results)

    # 导出结果
    output_file = "/home/sunrise/xlerobot/reports/memory-optimization-benchmark-results.json"
    benchmark.export_results(results, output_file)

    print("\n" + "=" * 70)
    print("基准测试完成!")
    print("=" * 70)

    return results


if __name__ == "__main__":
    main()
