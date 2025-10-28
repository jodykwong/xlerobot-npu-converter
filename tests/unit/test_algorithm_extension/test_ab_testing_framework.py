"""
A/B测试框架单元测试

测试AlgorithmABTestingFramework的所有功能。
"""

import pytest
import sys
import os
import time
from datetime import datetime

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../src'))

from npu_converter.extensions.features.ab_testing_framework import (
    AlgorithmABTestingFramework,
    ABTestConfig,
    TestResult,
    TestStatus,
    TestPhase,
    MetricType
)


class TestABTestConfig:
    """A/B测试配置测试"""

    def test_config_creation(self):
        """测试配置创建"""
        config = ABTestConfig(
            test_name="test_comparison",
            algorithm_a="algo_a",
            algorithm_b="algo_b",
            traffic_split=0.5,
            duration_seconds=3600,
            metrics=["accuracy", "latency"]
        )

        assert config.test_name == "test_comparison"
        assert config.algorithm_a == "algo_a"
        assert config.algorithm_b == "algo_b"
        assert config.traffic_split == 0.5
        assert config.duration_seconds == 3600
        assert config.metrics == ["accuracy", "latency"]
        assert config.enabled is True

    def test_config_with_all_parameters(self):
        """测试配置所有参数"""
        config = ABTestConfig(
            test_name="full_test",
            algorithm_a="algo_a",
            algorithm_b="algo_b",
            traffic_split=0.3,
            duration_seconds=7200,
            metrics=["accuracy", "latency", "throughput"],
            description="完整测试配置",
            min_sample_size=100,
            confidence_level=0.95,
            statistical_power=0.8,
            enabled=True
        )

        assert config.description == "完整测试配置"
        assert config.min_sample_size == 100
        assert config.confidence_level == 0.95
        assert config.statistical_power == 0.8

    def test_config_default_values(self):
        """测试配置默认值"""
        config = ABTestConfig(
            test_name="default_test",
            algorithm_a="algo_a",
            algorithm_b="algo_b"
        )

        assert config.traffic_split == 0.5
        assert config.duration_seconds == 86400
        assert config.metrics == []
        assert config.enabled is True


class TestAlgorithmABTestingFramework:
    """A/B测试框架测试"""

    def test_initialization(self):
        """测试初始化"""
        framework = AlgorithmABTestingFramework()
        assert framework._tests == {}
        assert len(framework._active_tests) == 0
        assert len(framework._results) == 0
        assert framework._statistics['tests_created'] == 0
        assert framework._statistics['tests_completed'] == 0

    def test_create_test(self):
        """测试创建测试"""
        framework = AlgorithmABTestingFramework()

        config = ABTestConfig(
            test_name="test_1",
            algorithm_a="algo_a",
            algorithm_b="algo_b"
        )

        test_id = framework.create_test(config)

        assert test_id is not None
        assert test_id in framework._tests
        assert framework._statistics['tests_created'] == 1

    def test_create_multiple_tests(self):
        """测试创建多个测试"""
        framework = AlgorithmABTestingFramework()

        config1 = ABTestConfig(
            test_name="test_1",
            algorithm_a="algo_a",
            algorithm_b="algo_b"
        )

        config2 = ABTestConfig(
            test_name="test_2",
            algorithm_a="algo_c",
            algorithm_b="algo_d"
        )

        test_id1 = framework.create_test(config1)
        test_id2 = framework.create_test(config2)

        assert test_id1 != test_id2
        assert len(framework._tests) == 2
        assert framework._statistics['tests_created'] == 2

    def test_start_test(self):
        """测试启动测试"""
        framework = AlgorithmABTestingFramework()

        config = ABTestConfig(
            test_name="test_1",
            algorithm_a="algo_a",
            algorithm_b="algo_b"
        )

        test_id = framework.create_test(config)
        success = framework.start_test(test_id)

        assert success
        assert test_id in framework._active_tests
        assert framework._tests[test_id].status == TestStatus.RUNNING

    def test_start_nonexistent_test(self):
        """测试启动不存在的测试"""
        framework = AlgorithmABTestingFramework()

        success = framework.start_test("nonexistent_id")

        assert not success

    def test_start_already_running_test(self):
        """测试启动已运行的测试"""
        framework = AlgorithmABTestingFramework()

        config = ABTestConfig(
            test_name="test_1",
            algorithm_a="algo_a",
            algorithm_b="algo_b"
        )

        test_id = framework.create_test(config)
        framework.start_test(test_id)

        # 再次启动应该失败
        success = framework.start_test(test_id)

        assert not success

    def test_stop_test(self):
        """测试停止测试"""
        framework = AlgorithmABTestingFramework()

        config = ABTestConfig(
            test_name="test_1",
            algorithm_a="algo_a",
            algorithm_b="algo_b"
        )

        test_id = framework.create_test(config)
        framework.start_test(test_id)
        success = framework.stop_test(test_id)

        assert success
        assert test_id not in framework._active_tests
        assert framework._tests[test_id].status == TestStatus.COMPLETED
        assert framework._statistics['tests_completed'] == 1

    def test_stop_nonexistent_test(self):
        """测试停止不存在的测试"""
        framework = AlgorithmABTestingFramework()

        success = framework.stop_test("nonexistent_id")

        assert not success

    def test_record_result_algo_a(self):
        """测试记录算法A结果"""
        framework = AlgorithmABTestingFramework()

        config = ABTestConfig(
            test_name="test_1",
            algorithm_a="algo_a",
            algorithm_b="algo_b",
            metrics=["accuracy"]
        )

        test_id = framework.create_test(config)
        framework.start_test(test_id)

        success = framework.record_result(
            test_id,
            "algo_a",
            "accuracy",
            0.92,
            100
        )

        assert success

        results = framework._results[test_id]
        assert "algo_a" in results
        assert "accuracy" in results["algo_a"]
        assert results["algo_a"]["accuracy"]["mean"] == 0.92
        assert results["algo_a"]["accuracy"]["count"] == 100

    def test_record_result_algo_b(self):
        """测试记录算法B结果"""
        framework = AlgorithmABTestingFramework()

        config = ABTestConfig(
            test_name="test_1",
            algorithm_a="algo_a",
            algorithm_b="algo_b",
            metrics=["accuracy"]
        )

        test_id = framework.create_test(config)
        framework.start_test(test_id)

        success = framework.record_result(
            test_id,
            "algo_b",
            "accuracy",
            0.95,
            100
        )

        assert success

        results = framework._results[test_id]
        assert "algo_b" in results

    def test_record_result_invalid_algorithm(self):
        """测试记录无效算法结果"""
        framework = AlgorithmABTestingFramework()

        config = ABTestConfig(
            test_name="test_1",
            algorithm_a="algo_a",
            algorithm_b="algo_b"
        )

        test_id = framework.create_test(config)
        framework.start_test(test_id)

        # 记录不在配置中的算法
        success = framework.record_result(
            test_id,
            "invalid_algo",
            "accuracy",
            0.92,
            100
        )

        # 应该允许记录，但会记录warning
        assert success

    def test_record_multiple_results(self):
        """测试记录多个结果"""
        framework = AlgorithmABTestingFramework()

        config = ABTestConfig(
            test_name="test_1",
            algorithm_a="algo_a",
            algorithm_b="algo_b",
            metrics=["accuracy", "latency"]
        )

        test_id = framework.create_test(config)
        framework.start_test(test_id)

        # 记录准确率
        framework.record_result(test_id, "algo_a", "accuracy", 0.92, 100)
        framework.record_result(test_id, "algo_b", "accuracy", 0.95, 100)

        # 记录延迟
        framework.record_result(test_id, "algo_a", "latency", 0.05, 100)
        framework.record_result(test_id, "algo_b", "latency", 0.04, 100)

        results = framework._results[test_id]
        assert len(results["algo_a"]) == 2
        assert len(results["algo_b"]) == 2

    def test_analyze_results(self):
        """测试分析结果"""
        framework = AlgorithmABTestingFramework()

        config = ABTestConfig(
            test_name="test_1",
            algorithm_a="algo_a",
            algorithm_b="algo_b",
            metrics=["accuracy"]
        )

        test_id = framework.create_test(config)
        framework.start_test(test_id)

        # 记录结果
        for _ in range(100):
            framework.record_result(test_id, "algo_a", "accuracy", 0.92 + 0.01 * (0.5 - 0.5), 1)
            framework.record_result(test_id, "algo_b", "accuracy", 0.95 + 0.01 * (0.5 - 0.5), 1)

        framework.stop_test(test_id)

        analysis = framework.analyze_results(test_id)

        assert isinstance(analysis, list)
        assert len(analysis) > 0

        # 验证分析结果结构
        for metric_analysis in analysis:
            assert 'metric_name' in metric_analysis
            assert 'algorithm_a_stats' in metric_analysis
            assert 'algorithm_b_stats' in metric_analysis
            assert 'statistical_significance' in metric_analysis

    def test_analyze_results_without_enough_data(self):
        """测试数据不足时分析结果"""
        framework = AlgorithmABTestingFramework()

        config = ABTestConfig(
            test_name="test_1",
            algorithm_a="algo_a",
            algorithm_b="algo_b",
            metrics=["accuracy"]
        )

        test_id = framework.create_test(config)
        framework.start_test(test_id)

        # 只记录少量数据
        framework.record_result(test_id, "algo_a", "accuracy", 0.92, 1)
        framework.record_result(test_id, "algo_b", "accuracy", 0.95, 1)

        framework.stop_test(test_id)

        analysis = framework.analyze_results(test_id)

        assert isinstance(analysis, list)
        # 数据不足时可能没有足够的数据进行分析

    def test_get_test_status(self):
        """测试获取测试状态"""
        framework = AlgorithmABTestingFramework()

        config = ABTestConfig(
            test_name="test_1",
            algorithm_a="algo_a",
            algorithm_b="algo_b"
        )

        test_id = framework.create_test(config)

        status = framework.get_test_status(test_id)

        assert status == TestStatus.CREATED

        framework.start_test(test_id)
        status = framework.get_test_status(test_id)

        assert status == TestStatus.RUNNING

        framework.stop_test(test_id)
        status = framework.get_test_status(test_id)

        assert status == TestStatus.COMPLETED

    def test_get_test_status_nonexistent(self):
        """测试获取不存在测试的状态"""
        framework = AlgorithmABTestingFramework()

        status = framework.get_test_status("nonexistent_id")

        assert status is None

    def test_list_tests(self):
        """测试列出所有测试"""
        framework = AlgorithmABTestingFramework()

        config1 = ABTestConfig(
            test_name="test_1",
            algorithm_a="algo_a",
            algorithm_b="algo_b"
        )

        config2 = ABTestConfig(
            test_name="test_2",
            algorithm_a="algo_c",
            algorithm_b="algo_d"
        )

        test_id1 = framework.create_test(config1)
        test_id2 = framework.create_test(config2)

        tests = framework.list_tests()

        assert len(tests) == 2
        assert test_id1 in tests
        assert test_id2 in tests

    def test_list_active_tests(self):
        """测试列出活跃测试"""
        framework = AlgorithmABTestingFramework()

        config1 = ABTestConfig(
            test_name="test_1",
            algorithm_a="algo_a",
            algorithm_b="algo_b"
        )

        config2 = ABTestConfig(
            test_name="test_2",
            algorithm_a="algo_c",
            algorithm_b="algo_d"
        )

        test_id1 = framework.create_test(config1)
        test_id2 = framework.create_test(config2)

        framework.start_test(test_id1)
        # test_id2不启动

        active_tests = framework.list_active_tests()

        assert len(active_tests) == 1
        assert test_id1 in active_tests
        assert test_id2 not in active_tests

    def test_export_results(self):
        """测试导出结果"""
        framework = AlgorithmABTestingFramework()

        config = ABTestConfig(
            test_name="test_1",
            algorithm_a="algo_a",
            algorithm_b="algo_b",
            metrics=["accuracy"]
        )

        test_id = framework.create_test(config)
        framework.start_test(test_id)

        framework.record_result(test_id, "algo_a", "accuracy", 0.92, 100)
        framework.record_result(test_id, "algo_b", "accuracy", 0.95, 100)

        framework.stop_test(test_id)

        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            output_path = f.name

        try:
            success = framework.export_results(test_id, output_path)
            assert success

            # 验证文件存在
            import os
            assert os.path.exists(output_path)

            # 验证文件内容
            import json
            with open(output_path, 'r') as f:
                data = json.load(f)

            assert 'test_config' in data
            assert 'results' in data
            assert 'analysis' in data

        finally:
            import os
            if os.path.exists(output_path):
                os.remove(output_path)

    def test_delete_test(self):
        """测试删除测试"""
        framework = AlgorithmABTestingFramework()

        config = ABTestConfig(
            test_name="test_1",
            algorithm_a="algo_a",
            algorithm_b="algo_b"
        )

        test_id = framework.create_test(config)

        success = framework.delete_test(test_id)

        assert success
        assert test_id not in framework._tests
        assert test_id not in framework._results

    def test_delete_nonexistent_test(self):
        """测试删除不存在的测试"""
        framework = AlgorithmABTestingFramework()

        success = framework.delete_test("nonexistent_id")

        assert not success

    def test_delete_active_test(self):
        """测试删除活跃测试"""
        framework = AlgorithmABTestingFramework()

        config = ABTestConfig(
            test_name="test_1",
            algorithm_a="algo_a",
            algorithm_b="algo_b"
        )

        test_id = framework.create_test(config)
        framework.start_test(test_id)

        # 不允许删除活跃测试
        success = framework.delete_test(test_id)

        assert not success

    def test_get_statistics(self):
        """测试获取统计信息"""
        framework = AlgorithmABTestingFramework()

        config = ABTestConfig(
            test_name="test_1",
            algorithm_a="algo_a",
            algorithm_b="algo_b"
        )

        test_id = framework.create_test(config)
        framework.start_test(test_id)
        framework.record_result(test_id, "algo_a", "accuracy", 0.92, 100)
        framework.stop_test(test_id)

        stats = framework.get_statistics()

        assert isinstance(stats, dict)
        assert stats['total_tests'] == 1
        assert stats['active_tests'] == 0
        assert stats['completed_tests'] == 1
        assert stats['total_results_recorded'] > 0

    def test_constants(self):
        """测试常量定义"""
        assert TestResult.__name__ == "TestResult"
        assert TestStatus.__name__ == "TestStatus"
        assert TestPhase.__name__ == "TestPhase"
        assert MetricType.__name__ == "MetricType"


class TestAlgorithmABTestingFrameworkEdgeCases:
    """A/B测试框架边界情况测试"""

    def test_traffic_split_zero(self):
        """测试流量分配为0"""
        framework = AlgorithmABTestingFramework()

        config = ABTestConfig(
            test_name="test_1",
            algorithm_a="algo_a",
            algorithm_b="algo_b",
            traffic_split=0.0
        )

        test_id = framework.create_test(config)

        assert test_id is not None

    def test_traffic_split_one(self):
        """测试流量分配为1"""
        framework = AlgorithmABTestingFramework()

        config = ABTestConfig(
            test_name="test_1",
            algorithm_a="algo_a",
            algorithm_b="algo_b",
            traffic_split=1.0
        )

        test_id = framework.create_test(config)

        assert test_id is not None

    def test_stop_test_not_started(self):
        """测试停止未启动的测试"""
        framework = AlgorithmABTestingFramework()

        config = ABTestConfig(
            test_name="test_1",
            algorithm_a="algo_a",
            algorithm_b="algo_b"
        )

        test_id = framework.create_test(config)

        # 不启动直接停止应该失败
        success = framework.stop_test(test_id)

        assert not success

    def test_record_result_before_start(self):
        """测试在启动前记录结果"""
        framework = AlgorithmABTestingFramework()

        config = ABTestConfig(
            test_name="test_1",
            algorithm_a="algo_a",
            algorithm_b="algo_b"
        )

        test_id = framework.create_test(config)

        # 不启动直接记录结果应该失败
        success = framework.record_result(
            test_id,
            "algo_a",
            "accuracy",
            0.92,
            100
        )

        assert not success

    def test_record_result_after_stop(self):
        """测试在停止后记录结果"""
        framework = AlgorithmABTestingFramework()

        config = ABTestConfig(
            test_name="test_1",
            algorithm_a="algo_a",
            algorithm_b="algo_b"
        )

        test_id = framework.create_test(config)
        framework.start_test(test_id)
        framework.stop_test(test_id)

        # 停止后记录结果应该失败
        success = framework.record_result(
            test_id,
            "algo_a",
            "accuracy",
            0.92,
            100
        )

        assert not success

    def test_long_test_duration(self):
        """测试长时间测试"""
        framework = AlgorithmABTestingFramework()

        config = ABTestConfig(
            test_name="test_1",
            algorithm_a="algo_a",
            algorithm_b="algo_b",
            duration_seconds=86400 * 365  # 一年
        )

        test_id = framework.create_test(config)

        assert test_id is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
