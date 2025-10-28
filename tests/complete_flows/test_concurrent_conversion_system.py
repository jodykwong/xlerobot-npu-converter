"""
Story 3.3 并发转换系统完整流程验证

这是一个简单的验证脚本，演示并发转换系统的基本功能。

作者: Claude Code / Story 3.3
版本: 1.0
日期: 2025-10-28
"""

import sys
sys.path.insert(0, '/home/sunrise/xlerobot/src')

import time
import threading
from npu_converter.performance.concurrent_conversion_system import (
    create_concurrent_converter,
    TaskPriority,
)


def main():
    """主验证流程"""
    print("=" * 70)
    print("Story 3.3 并发转换系统验证")
    print("=" * 70)
    print()

    # 创建转换器
    print("📝 创建并发转换器...")
    converter = create_concurrent_converter(
        max_concurrent=5,
        max_batch_size=5,
        preset='balanced'
    )
    print(f"✅ 转换器创建成功，最大并发数: {converter.max_concurrent}")
    print()

    # 提交任务
    print("📝 提交转换任务...")
    task_ids = []
    num_tasks = 10

    for i in range(num_tasks):
        task_id = converter.submit_conversion(
            model_data=list(range(1000)),
            conversion_params={
                'model_type': 'test',
                'iteration': i,
                'priority': 'normal'
            },
            priority=TaskPriority.NORMAL,
        )
        task_ids.append(task_id)
        print(f"  任务 {i+1}/{num_tasks}: {task_id}")

    print(f"\n✅ 已提交 {len(task_ids)} 个任务")
    print()

    # 运行并发处理（短暂运行）
    print("🚀 启动并发处理...")
    run_thread = threading.Thread(
        target=converter.run,
        kwargs={'duration': 3.0}
    )
    run_thread.start()
    run_thread.join()
    print("✅ 并发处理完成")
    print()

    # 获取统计信息
    print("📊 获取统计信息...")
    stats = converter.get_stats()
    print(f"  提交任务数: {stats['tasks_submitted']}")
    print(f"  完成任务数: {stats['tasks_completed']}")
    print(f"  活跃任务数: {stats['active_tasks']}")
    print(f"  吞吐量: {stats['throughput_per_minute']:.2f} 任务/分钟")
    print(f"  平均延迟: {stats['average_latency']:.4f} 秒")
    print()

    # 获取指标
    print("📈 获取性能指标...")
    metrics = converter.get_metrics()
    print(f"  当前活跃任务: {metrics.active_tasks}")
    print(f"  待处理任务: {metrics.pending_tasks}")
    print(f"  队列长度: {metrics.queue_length}")
    print(f"  CPU使用率: {metrics.cpu_usage:.2f}%")
    print(f"  内存使用: {metrics.memory_usage / (1024 * 1024):.2f} MB")
    print()

    # 关闭转换器
    print("🛑 关闭转换器...")
    converter.shutdown()
    print("✅ 转换器已关闭")
    print()

    print("=" * 70)
    print("Story 3.3 并发转换系统验证完成!")
    print("=" * 70)


if __name__ == '__main__':
    main()
