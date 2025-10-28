"""
Transformer变种适配器单元测试

测试TransformerVariantAdapter的所有功能。
"""

import pytest
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../src'))

from npu_converter.extensions.algorithms.transformer_variant_adapter import (
    TransformerVariantAdapter
)


class TestTransformerVariantAdapter:
    """Transformer变种适配器测试"""

    def test_initialization(self):
        """测试初始化"""
        adapter = TransformerVariantAdapter()
        assert adapter._model is None
        assert adapter._cache == {}
        assert adapter._config == {}
        assert adapter._statistics['execution_count'] == 0
        assert adapter._statistics['total_execution_time'] == 0.0
        assert adapter._statistics['cache_hit_count'] == 0

    def test_initialize_success(self):
        """测试初始化成功"""
        adapter = TransformerVariantAdapter()
        success = adapter.initialize(
            model_size="base",
            num_layers=12,
            hidden_size=768,
            num_attention_heads=12
        )
        assert success
        assert adapter._model is not None
        assert adapter._model['model_size'] == 'base'
        assert adapter._model['num_layers'] == 12

    def test_initialize_with_invalid_parameters(self):
        """测试无效参数初始化"""
        adapter = TransformerVariantAdapter()
        # 隐藏层维度不能被注意力头数整除
        success = adapter.initialize(
            hidden_size=100,
            num_attention_heads=12
        )
        # 应该成功，但会有警告
        assert success

    def test_validate_input_valid_string(self):
        """测试输入验证 - 有效字符串"""
        adapter = TransformerVariantAdapter()
        adapter._config['max_sequence_length'] = 512

        assert adapter.validate_input("test input")
        assert adapter.validate_input("x" * 100)

    def test_validate_input_valid_dict(self):
        """测试输入验证 - 有效字典"""
        adapter = TransformerVariantAdapter()
        input_data = {
            'input_ids': [1, 2, 3, 4, 5],
            'attention_mask': [1, 1, 1, 1, 1]
        }
        assert adapter.validate_input(input_data)

    def test_validate_input_invalid_dict(self):
        """测试输入验证 - 无效字典"""
        adapter = TransformerVariantAdapter()
        input_data = {'invalid_field': 'value'}
        assert not adapter.validate_input(input_data)

    def test_validate_input_none(self):
        """测试输入验证 - None"""
        adapter = TransformerVariantAdapter()
        assert not adapter.validate_input(None)

    def test_validate_output_valid(self):
        """测试输出验证 - 有效输出"""
        adapter = TransformerVariantAdapter()
        output_data = {
            'transformed_data': 'result',
            'transform_type': 'basic',
            'optimization_level': 0
        }
        assert adapter.validate_output(output_data)

    def test_validate_output_invalid_type(self):
        """测试输出验证 - 无效类型"""
        adapter = TransformerVariantAdapter()
        assert not adapter.validate_output("invalid")
        assert not adapter.validate_output(None)

    def test_validate_output_missing_fields(self):
        """测试输出验证 - 缺少字段"""
        adapter = TransformerVariantAdapter()
        output_data = {'missing': 'fields'}
        assert not adapter.validate_output(output_data)

    def test_execute_basic_transform(self):
        """测试执行基础变换"""
        adapter = TransformerVariantAdapter()
        adapter.initialize(model_size="base")

        result = adapter.execute(
            "test input",
            optimization_level=0,
            precision="fp32"
        )

        assert isinstance(result, dict)
        assert 'transformed_data' in result
        assert 'transform_type' in result
        assert result['transform_type'] == 'basic'
        assert adapter._statistics['execution_count'] == 1

    def test_execute_basic_optimize_transform(self):
        """测试执行基本优化变换"""
        adapter = TransformerVariantAdapter()
        adapter.initialize(model_size="base")

        result = adapter.execute(
            "test input",
            optimization_level=1,
            precision="fp16"
        )

        assert isinstance(result, dict)
        assert 'transform_type' in result
        assert result['transform_type'] == 'basic_optimize'
        assert 'applied_optimizations' in result

    def test_execute_advanced_optimize_transform(self):
        """测试执行高级优化变换"""
        adapter = TransformerVariantAdapter()
        adapter.initialize(model_size="base")

        result = adapter.execute(
            "test input",
            optimization_level=2
        )

        assert isinstance(result, dict)
        assert 'transform_type' in result
        assert result['transform_type'] == 'advanced_optimize'
        assert 'performance_gain' in result

    def test_execute_extreme_optimize_transform(self):
        """测试执行极限优化变换"""
        adapter = TransformerVariantAdapter()
        adapter.initialize(model_size="base")

        result = adapter.execute(
            "test input",
            optimization_level=3
        )

        assert isinstance(result, dict)
        assert 'transform_type' in result
        assert result['transform_type'] == 'extreme_optimize'
        assert 'performance_gain' in result

    def test_execute_with_fp16_optimization(self):
        """测试FP16优化"""
        adapter = TransformerVariantAdapter()
        adapter.initialize(model_size="base")

        result = adapter.execute(
            "test input",
            optimization_level=2,
            precision="fp16"
        )

        assert result['precision'] == 'fp16'
        assert 'memory_reduction' in result

    def test_execute_with_int8_optimization(self):
        """测试INT8优化"""
        adapter = TransformerVariantAdapter()
        adapter.initialize(model_size="base")

        result = adapter.execute(
            "test input",
            optimization_level=2,
            precision="int8"
        )

        assert result['precision'] == 'int8'
        assert 'memory_reduction' in result
        assert 'accuracy_loss' in result

    def test_execute_with_cache(self):
        """测试缓存功能"""
        adapter = TransformerVariantAdapter()
        adapter._config['enable_cache'] = True
        adapter.initialize(model_size="base")

        # 第一次执行
        result1 = adapter.execute("test input", optimization_level=1)

        # 第二次执行相同输入
        result2 = adapter.execute("test input", optimization_level=1)

        assert result1 == result2
        assert adapter._statistics['cache_hit_count'] == 1

    def test_execute_cache_disabled(self):
        """测试禁用缓存"""
        adapter = TransformerVariantAdapter()
        adapter._config['enable_cache'] = False
        adapter.initialize(model_size="base")

        result = adapter.execute("test input", optimization_level=1)

        assert adapter._statistics['cache_hit_count'] == 0

    def test_get_model_info(self):
        """测试获取模型信息"""
        adapter = TransformerVariantAdapter()
        adapter.initialize(
            model_size="base",
            num_layers=12,
            hidden_size=768
        )

        info = adapter.get_model_info()

        assert isinstance(info, dict)
        assert 'model_size' in info
        assert 'num_layers' in info
        assert 'hidden_size' in info
        assert 'estimated_params' in info
        assert 'model_size_mb' in info

    def test_get_model_info_not_initialized(self):
        """测试未初始化时获取模型信息"""
        adapter = TransformerVariantAdapter()
        info = adapter.get_model_info()
        assert info == {}

    def test_estimate_parameters(self):
        """测试参数估算"""
        adapter = TransformerVariantAdapter()
        adapter.initialize(
            hidden_size=768,
            num_layers=12,
            num_attention_heads=12
        )

        params = adapter._estimate_parameters()

        assert params > 0
        assert isinstance(params, int)

    def test_estimate_model_size(self):
        """测试模型大小估算"""
        adapter = TransformerVariantAdapter()
        adapter.initialize(
            hidden_size=768,
            num_layers=12
        )

        size = adapter._estimate_model_size()

        assert size > 0
        assert isinstance(size, float)

    def test_get_performance_metrics(self):
        """测试性能指标"""
        adapter = TransformerVariantAdapter()
        adapter.initialize(model_size="base")

        # 执行一些操作
        adapter.execute("test", optimization_level=1)

        metrics = adapter.get_performance_metrics()

        assert isinstance(metrics, dict)
        assert 'execution_count' in metrics
        assert 'total_execution_time' in metrics
        assert 'average_execution_time' in metrics
        assert 'throughput_samples_per_second' in metrics

    def test_benchmark(self):
        """测试基准测试"""
        adapter = TransformerVariantAdapter()
        adapter.initialize(model_size="base")

        result = adapter.benchmark("test input", iterations=5)

        assert isinstance(result, dict)
        assert 'iterations' in result
        assert 'success_rate' in result
        assert 'min_time' in result
        assert 'max_time' in result
        assert 'mean_time' in result
        assert result['success_rate'] == 100.0

    def test_clear_cache(self):
        """测试清空缓存"""
        adapter = TransformerVariantAdapter()
        adapter._config['enable_cache'] = True
        adapter.initialize(model_size="base")

        # 添加缓存
        adapter._cache['test_key'] = 'test_value'

        # 清空缓存
        adapter.clear_cache()

        assert adapter._cache == {}
        assert adapter._statistics['cache_hit_count'] == 0

    def test_get_statistics(self):
        """测试统计信息"""
        adapter = TransformerVariantAdapter()
        adapter.initialize(model_size="base")

        stats = adapter.get_statistics()

        assert isinstance(stats, dict)
        assert stats['adapter_type'] == 'TransformerVariantAdapter'
        assert stats['version'] == adapter.VERSION
        assert stats['category'] == adapter.CATEGORY
        assert stats['initialized'] is True
        assert 'statistics' in stats
        assert 'performance_metrics' in stats
        assert 'model_info' in stats

    def test_get_cache_key(self):
        """测试缓存键生成"""
        adapter = TransformerVariantAdapter()
        adapter.initialize(model_size="base")

        input_data = "test input"
        kwargs = {'optimization_level': 2}

        key = adapter._get_cache_key(input_data, kwargs)

        assert isinstance(key, str)
        assert len(key) == 32  # MD5 hash length

    def test_constants(self):
        """测试常量定义"""
        assert TransformerVariantAdapter.VERSION == "1.0.0"
        assert TransformerVariantAdapter.DESCRIPTION == "Transformer变种算法适配器"
        assert TransformerVariantAdapter.AUTHOR == "XLeRobot Team"
        assert TransformerVariantAdapter.CATEGORY == "transformation"
        assert "torch" in TransformerVariantAdapter.DEPENDENCIES
        assert "onnx" in TransformerVariantAdapter.SUPPORTED_FORMATS


class TestTransformerVariantAdapterEdgeCases:
    """Transformer变种适配器边界情况测试"""

    def test_execute_with_invalid_optimization_level(self):
        """测试无效优化级别"""
        adapter = TransformerVariantAdapter()
        adapter.initialize(model_size="base")

        # 优化级别超出范围
        result = adapter.execute(
            "test input",
            optimization_level=10
        )

        # 应该使用默认优化级别
        assert isinstance(result, dict)

    def test_execute_with_long_input(self):
        """测试长输入"""
        adapter = TransformerVariantAdapter()
        adapter.initialize(model_size="base")

        long_input = "x" * 10000

        # 长输入应该被允许但会有警告
        result = adapter.execute(long_input)

        assert isinstance(result, dict)
        assert adapter._statistics['execution_count'] == 1

    def test_execute_cache_size_limit(self):
        """测试缓存大小限制"""
        adapter = TransformerVariantAdapter()
        adapter._config['enable_cache'] = True
        adapter._config['cache_size'] = 2
        adapter.initialize(model_size="base")

        # 添加多个缓存项
        adapter.execute("input1", optimization_level=1)
        adapter.execute("input2", optimization_level=1)
        adapter.execute("input3", optimization_level=1)

        # 缓存应该被限制在指定大小
        assert len(adapter._cache) <= 2

    def test_multiple_initializations(self):
        """测试多次初始化"""
        adapter = TransformerVariantAdapter()

        adapter.initialize(model_size="base", num_layers=6)
        assert adapter._model['model_size'] == 'base'

        adapter.initialize(model_size="large", num_layers=24)
        assert adapter._model['model_size'] == 'large'
        assert adapter._model['num_layers'] == 24

    def test_execute_without_initialization(self):
        """测试未初始化执行"""
        adapter = TransformerVariantAdapter()

        # 应该引发异常
        with pytest.raises(Exception):
            adapter.execute("test input")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
