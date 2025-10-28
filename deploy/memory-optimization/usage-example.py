#!/usr/bin/env python3
"""
Story 3.2 内存优化系统使用示例
"""

import sys
sys.path.insert(0, '/home/sunrise/xlerobot/src')

from npu_converter.memory import (
    MemoryOptimizationSystem,
    optimize_memory_usage,
)
from npu_converter.config.memory_optimization_config import MemoryOptimizationPresets

def example_1_convenience_function():
    """示例1: 使用便捷函数"""
    print("=" * 60)
    print("示例1: 使用便捷函数")
    print("=" * 60)
    
    # 准备测试数据
    data = list(range(10000))
    print(f"原始数据大小: {len(data)}")
    
    # 使用便捷函数优化
    optimized_data, report = optimize_memory_usage(data, 'standard')
    
    print(f"优化后数据大小: {len(optimized_data)}")
    print(f"应用优化策略: {len(report['config']['strategies'])} 项")
    print(f"优化建议: {len(report['recommendations'])} 条")
    print()

def example_2_full_system():
    """示例2: 使用完整系统"""
    print("=" * 60)
    print("示例2: 使用完整系统")
    print("=" * 60)
    
    # 创建配置
    config = MemoryOptimizationPresets.get_high_performance_mode()
    print(f"配置模式: {config.memory_mode.value}")
    print(f"优化级别: {config.optimization_level.value}")
    
    # 创建系统
    system = MemoryOptimizationSystem(config)
    
    # 启动系统
    system.start()
    print("系统已启动")
    
    # 优化数据
    test_data = {'models': list(range(1000)), 'params': {'batch_size': 32}}
    optimized_data, result = system.optimize_data(test_data)
    
    print(f"原始内存: {result.original_memory} 字节")
    print(f"优化后内存: {result.optimized_memory} 字节")
    print(f"效率提升: {result.efficiency_gain:.2%}")
    print(f"处理时间: {result.time_taken:.4f} 秒")
    
    # 生成报告
    report = system.get_optimization_report()
    print(f"当前内存效率: {report['metrics']['efficiency']:.2%}")
    
    # 停止系统
    system.stop()
    print("系统已停止")
    print()

def example_3_batch_processing():
    """示例3: 批处理模式"""
    print("=" * 60)
    print("示例3: 批处理模式")
    print("=" * 60)
    
    # 创建批处理配置
    config = MemoryOptimizationPresets.get_batch_processing_mode()
    print(f"批处理配置已创建")
    print(f"批大小: {config.batch_size}")
    print(f"批处理内存限制: {config.batch_memory_limit / 1024 / 1024:.0f} MB")
    
    # 创建系统
    system = MemoryOptimizationSystem(config)
    system.start()
    
    # 批处理多个数据集
    datasets = [
        list(range(1000)),
        list(range(2000)),
        list(range(1500)),
        list(range(3000)),
    ]
    
    results = []
    for i, dataset in enumerate(datasets):
        optimized, result = system.optimize_data(dataset)
        results.append(result)
        print(f"数据集 {i+1}: 优化完成 ({len(dataset)} 项)")
    
    # 汇总结果
    total_time = sum(r.time_taken for r in results)
    avg_efficiency = sum(r.efficiency_gain for r in results) / len(results)
    
    print(f"总处理时间: {total_time:.4f} 秒")
    print(f"平均效率提升: {avg_efficiency:.2%}")
    
    system.stop()
    print()

if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "Story 3.2 内存优化系统使用示例" + " " * 11 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    # 运行示例
    example_1_convenience_function()
    example_2_full_system()
    example_3_batch_processing()
    
    print("=" * 60)
    print("🎉 所有示例执行完成！")
    print("=" * 60)
