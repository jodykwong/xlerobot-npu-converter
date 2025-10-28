#!/usr/bin/env python3
"""
部署验证脚本
Validate Deployment Script

用于验证XLeRobot性能基准测试系统的部署是否正确。
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from npu_converter.performance.benchmark_runner import BenchmarkRunner, BenchmarkConfig
from npu_converter.performance.metrics_collector import MetricsCollector, MetricsConfig
from npu_converter.performance.benchmark_suite import BenchmarkSuite, SuiteConfig

def main():
    """主函数"""
    print("=" * 60)
    print("XLeRobot性能基准测试 - 部署验证")
    print("=" * 60)

    try:
        # 1. 创建配置
        print("\n1. 创建配置...")
        config = BenchmarkConfig(
            max_concurrent=5,
            test_timeout=300,
            output_dir="reports/validation"
        )
        print("✅ 配置创建成功")

        # 2. 创建组件
        print("\n2. 创建组件...")
        runner = BenchmarkRunner(config)
        collector = MetricsCollector(MetricsConfig())
        suite = BenchmarkSuite(SuiteConfig())
        print("✅ 组件创建成功")

        # 3. 获取测试用例
        print("\n3. 获取测试用例...")
        test_case = suite.get_test_case("TC-001")
        print(f"✅ 测试用例: {test_case.id}")

        # 4. 运行测试
        print("\n4. 运行测试...")
        result = runner.run_benchmark(test_case)

        # 5. 验证结果
        print("\n5. 验证结果...")
        print(f"   测试结果: {result.result.status}")
        print(f"   耗时: {result.result.duration:.2f}秒")

        if result.result.status == "success":
            print("\n✅ 部署验证成功！")
            return 0
        else:
            print(f"\n❌ 部署验证失败")
            return 1

    except Exception as e:
        print(f"\n❌ 验证过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
