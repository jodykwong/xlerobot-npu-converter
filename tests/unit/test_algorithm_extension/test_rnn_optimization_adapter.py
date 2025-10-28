"""
RNN优化适配器单元测试

测试RNNOptimizationAdapter的所有功能。
"""

import pytest
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../src'))

from npu_converter.extensions.algorithms.rnn_optimization_adapter import (
    RNNOptimizationAdapter
)


class TestRNNOptimizationAdapter:
    """RNN优化适配器测试"""

    def test_initialization(self):
        """测试初始化"""
        adapter = RNNOptimizationAdapter()
        assert adapter._model is None
        assert adapter._config == {}
        assert adapter._attention_weights == {}
        assert adapter._statistics['execution_count'] == 0
        assert adapter._statistics['total_execution_time'] == 0.0
        assert adapter._statistics['sequence_processed_count'] == 0
        assert adapter._statistics['attention_computation_count'] == 0
        assert adapter._statistics['gradient_steps'] == 0

    def test_initialize_lstm_success(self):
        """测试LSTM初始化成功"""
        adapter = RNNOptimizationAdapter()
        success = adapter.initialize(
            rnn_type="lstm",
            num_layers=3,
            hidden_size=256,
            use_bidirectional=True,
            use_attention=True
        )
        assert success
        assert adapter._model is not None
        assert adapter._model['rnn_type'] == 'lstm'
        assert adapter._model['num_layers'] == 3

    def test_initialize_gru_success(self):
        """测试GRU初始化成功"""
        adapter = RNNOptimizationAdapter()
        success = adapter.initialize(
            rnn_type="gru",
            num_layers=2,
            hidden_size=128
        )
        assert success
        assert adapter._model['rnn_type'] == 'gru'

    def test_initialize_vanilla_rnn_success(self):
        """测试Vanilla RNN初始化成功"""
        adapter = RNNOptimizationAdapter()
        success = adapter.initialize(
            rnn_type="rnn",
            num_layers=2,
            hidden_size=64
        )
        assert success
        assert adapter._model['rnn_type'] == 'rnn'

    def test_initialize_transformer_success(self):
        """测试Transformer初始化成功"""
        adapter = RNNOptimizationAdapter()
        success = adapter.initialize(
            rnn_type="transformer",
            num_layers=6,
            hidden_size=512
        )
        assert success
        assert adapter._model['rnn_type'] == 'transformer'

    def test_initialize_with_warning_too_many_layers(self):
        """测试过多层数警告"""
        adapter = RNNOptimizationAdapter()

        # Transformer层数过多
        success = adapter.initialize(
            rnn_type="transformer",
            num_layers=15
        )
        assert success

        # RNN层数过多
        success = adapter.initialize(
            rnn_type="lstm",
            num_layers=10
        )
        assert success

    def test_validate_input_valid_list(self):
        """测试输入验证 - 有效列表"""
        adapter = RNNOptimizationAdapter()
        adapter._config['max_sequence_length'] = 500

        assert adapter.validate_input([1, 2, 3, 4, 5])
        assert adapter.validate_input("test sequence")

    def test_validate_input_valid_dict(self):
        """测试输入验证 - 有效字典"""
        adapter = RNNOptimizationAdapter()
        input_data = {'sequence': [1, 2, 3, 4, 5]}
        assert adapter.validate_input(input_data)

    def test_validate_input_empty_sequence(self):
        """测试输入验证 - 空序列"""
        adapter = RNNOptimizationAdapter()
        assert not adapter.validate_input([])

    def test_validate_input_none(self):
        """测试输入验证 - None"""
        adapter = RNNOptimizationAdapter()
        assert not adapter.validate_input(None)

    def test_validate_input_invalid_dict(self):
        """测试输入验证 - 无效字典"""
        adapter = RNNOptimizationAdapter()
        input_data = {'invalid_field': 'value'}
        assert not adapter.validate_input(input_data)

    def test_validate_output_valid(self):
        """测试输出验证 - 有效输出"""
        adapter = RNNOptimizationAdapter()
        output_data = {
            'rnn_type': 'lstm',
            'layers_processed': 3,
            'applied_optimizations': ['lstm_cell_optimization']
        }
        assert adapter.validate_output(output_data)

    def test_validate_output_invalid_type(self):
        """测试输出验证 - 无效类型"""
        adapter = RNNOptimizationAdapter()
        assert not adapter.validate_output("invalid")
        assert not adapter.validate_output(None)

    def test_validate_output_missing_fields(self):
        """测试输出验证 - 缺少字段"""
        adapter = RNNOptimizationAdapter()
        output_data = {'missing': 'fields'}
        assert not adapter.validate_output(output_data)

    def test_validate_output_invalid_rnn_type(self):
        """测试输出验证 - 无效RNN类型"""
        adapter = RNNOptimizationAdapter()
        output_data = {
            'rnn_type': 'invalid',
            'layers_processed': 3,
            'applied_optimizations': []
        }
        assert not adapter.validate_output(output_data)

    def test_execute_lstm_with_all_features(self):
        """测试执行LSTM所有功能"""
        adapter = RNNOptimizationAdapter()
        adapter.initialize(
            rnn_type="lstm",
            num_layers=3,
            hidden_size=256,
            use_bidirectional=True,
            use_attention=True,
            dropout_rate=0.2
        )

        result = adapter.execute(
            [1, 2, 3, 4, 5],
            max_sequence_length=500,
            learning_rate=0.001
        )

        assert isinstance(result, dict)
        assert 'rnn_type' in result
        assert result['rnn_type'] == 'lstm'
        assert 'applied_optimizations' in result
        assert 'lstm_cell_optimization' in result['applied_optimizations']
        assert 'bidirectional_processing' in result['applied_optimizations']
        assert 'self_attention_mechanism' in result['applied_optimizations']
        assert 'gradient_optimization' in result

    def test_execute_lstm_without_attention(self):
        """测试执行LSTM无注意力"""
        adapter = RNNOptimizationAdapter()
        adapter.initialize(
            rnn_type="lstm",
            num_layers=3,
            hidden_size=256,
            use_bidirectional=False,
            use_attention=False
        )

        result = adapter.execute(
            [1, 2, 3, 4, 5]
        )

        assert isinstance(result, dict)
        assert result['rnn_type'] == 'lstm'
        assert 'self_attention_mechanism' not in result['applied_optimizations']

    def test_execute_gru(self):
        """测试执行GRU"""
        adapter = RNNOptimizationAdapter()
        adapter.initialize(
            rnn_type="gru",
            num_layers=2,
            hidden_size=128,
            use_bidirectional=True,
            use_attention=True
        )

        result = adapter.execute(
            [1, 2, 3, 4, 5]
        )

        assert isinstance(result, dict)
        assert result['rnn_type'] == 'gru'
        assert 'gru_cell_optimization' in result['applied_optimizations']

    def test_execute_vanilla_rnn(self):
        """测试执行Vanilla RNN"""
        adapter = RNNOptimizationAdapter()
        adapter.initialize(
            rnn_type="rnn",
            num_layers=2,
            hidden_size=64,
            use_bidirectional=True
        )

        result = adapter.execute(
            [1, 2, 3, 4, 5]
        )

        assert isinstance(result, dict)
        assert result['rnn_type'] == 'rnn'
        assert 'vanilla_rnn_optimization' in result['applied_optimizations']
        assert 'gradient_clipping' in result['applied_optimizations']
        assert 'tanh_activation_optimization' in result['applied_optimizations']

    def test_execute_transformer(self):
        """测试执行Transformer"""
        adapter = RNNOptimizationAdapter()
        adapter.initialize(
            rnn_type="transformer",
            num_layers=6,
            hidden_size=512,
            use_attention=True
        )

        result = adapter.execute(
            [1, 2, 3, 4, 5]
        )

        assert isinstance(result, dict)
        assert result['rnn_type'] == 'transformer'
        assert 'self_attention' in result['applied_optimizations']
        assert 'positional_encoding' in result['applied_optimizations']
        assert 'multi_head_attention' in result['applied_optimizations']
        assert 'parallel_processing' in result

    def test_execute_with_long_sequence(self):
        """测试长序列执行"""
        adapter = RNNOptimizationAdapter()
        adapter.initialize(rnn_type="lstm", num_layers=3, hidden_size=256)

        # 创建长序列（>200）
        long_sequence = list(range(300))

        result = adapter.execute(long_sequence)

        assert isinstance(result, dict)
        assert 'long_sequence_optimization' in result
        assert 'gradient_optimization' in result

    def test_execute_with_very_long_sequence(self):
        """测试超长序列执行（>1000）"""
        adapter = RNNOptimizationAdapter()
        adapter.initialize(rnn_type="lstm", num_layers=3, hidden_size=256)

        # 创建超长序列（>1000）
        very_long_sequence = list(range(1500))

        result = adapter.execute(very_long_sequence)

        assert isinstance(result, dict)
        long_seq_opt = result['long_sequence_optimization']
        assert 'chunked_processing' in long_seq_opt['applied_optimizations']
        assert 'hierarchical_attention' in long_seq_opt['applied_optimizations']

    def test_execute_with_string_input(self):
        """测试字符串输入"""
        adapter = RNNOptimizationAdapter()
        adapter.initialize(rnn_type="lstm", num_layers=3)

        result = adapter.execute("test sequence string")

        assert isinstance(result, dict)
        assert result['rnn_type'] == 'lstm'

    def test_execute_with_dict_input(self):
        """测试字典输入"""
        adapter = RNNOptimizationAdapter()
        adapter.initialize(rnn_type="lstm", num_layers=3)

        input_data = {'sequence': [1, 2, 3, 4, 5]}
        result = adapter.execute(input_data)

        assert isinstance(result, dict)

    def test_get_model_info(self):
        """测试获取模型信息"""
        adapter = RNNOptimizationAdapter()
        adapter.initialize(
            rnn_type="lstm",
            num_layers=3,
            hidden_size=256,
            use_bidirectional=True,
            use_attention=True
        )

        info = adapter.get_model_info()

        assert isinstance(info, dict)
        assert 'rnn_type' in info
        assert 'num_layers' in info
        assert 'hidden_size' in info
        assert 'bidirectional' in info
        assert 'attention' in info
        assert 'estimated_params' in info
        assert 'model_size_mb' in info

    def test_get_model_info_not_initialized(self):
        """测试未初始化时获取模型信息"""
        adapter = RNNOptimizationAdapter()
        info = adapter.get_model_info()
        assert info == {}

    def test_estimate_parameters_lstm(self):
        """测试LSTM参数估算"""
        adapter = RNNOptimizationAdapter()
        adapter.initialize(
            rnn_type="lstm",
            num_layers=3,
            hidden_size=256,
            use_bidirectional=True
        )

        params = adapter._estimate_parameters()

        assert params > 0
        assert isinstance(params, int)

    def test_estimate_parameters_gru(self):
        """测试GRU参数估算"""
        adapter = RNNOptimizationAdapter()
        adapter.initialize(
            rnn_type="gru",
            num_layers=2,
            hidden_size=128
        )

        params = adapter._estimate_parameters()

        assert params > 0
        assert isinstance(params, int)

    def test_estimate_parameters_vanilla_rnn(self):
        """测试Vanilla RNN参数估算"""
        adapter = RNNOptimizationAdapter()
        adapter.initialize(
            rnn_type="rnn",
            num_layers=2,
            hidden_size=64
        )

        params = adapter._estimate_parameters()

        assert params > 0
        assert isinstance(params, int)

    def test_estimate_parameters_transformer(self):
        """测试Transformer参数估算"""
        adapter = RNNOptimizationAdapter()
        adapter.initialize(
            rnn_type="transformer",
            num_layers=6,
            hidden_size=512
        )

        params = adapter._estimate_parameters()

        assert params > 0
        assert isinstance(params, int)

    def test_estimate_model_size(self):
        """测试模型大小估算"""
        adapter = RNNOptimizationAdapter()
        adapter.initialize(
            rnn_type="lstm",
            num_layers=3,
            hidden_size=256
        )

        size = adapter._estimate_model_size()

        assert size > 0
        assert isinstance(size, float)

    def test_get_performance_metrics(self):
        """测试性能指标"""
        adapter = RNNOptimizationAdapter()
        adapter.initialize(rnn_type="lstm", num_layers=3)

        # 执行一些操作
        adapter.execute([1, 2, 3, 4, 5])

        metrics = adapter.get_performance_metrics()

        assert isinstance(metrics, dict)
        assert 'execution_count' in metrics
        assert 'total_execution_time' in metrics
        assert 'average_execution_time' in metrics
        assert 'sequence_processed_count' in metrics
        assert 'average_sequence_length' in metrics
        assert 'attention_computation_count' in metrics
        assert 'throughput_samples_per_second' in metrics
        assert 'tokens_per_second' in metrics

    def test_benchmark(self):
        """测试基准测试"""
        adapter = RNNOptimizationAdapter()
        adapter.initialize(rnn_type="lstm", num_layers=3)

        result = adapter.benchmark([1, 2, 3, 4, 5], iterations=5)

        assert isinstance(result, dict)
        assert 'iterations' in result
        assert 'success_rate' in result
        assert 'min_time' in result
        assert 'max_time' in result
        assert 'mean_time' in result
        assert result['success_rate'] == 100.0

    def test_get_statistics(self):
        """测试统计信息"""
        adapter = RNNOptimizationAdapter()
        adapter.initialize(rnn_type="lstm", num_layers=3)

        stats = adapter.get_statistics()

        assert isinstance(stats, dict)
        assert stats['adapter_type'] == 'RNNOptimizationAdapter'
        assert stats['version'] == adapter.VERSION
        assert stats['category'] == adapter.CATEGORY
        assert stats['initialized'] is True
        assert 'statistics' in stats
        assert 'performance_metrics' in stats
        assert 'model_info' in stats

    def test_constants(self):
        """测试常量定义"""
        assert RNNOptimizationAdapter.VERSION == "1.0.0"
        assert RNNOptimizationAdapter.DESCRIPTION == "RNN优化算法适配器"
        assert RNNOptimizationAdapter.AUTHOR == "XLeRobot Team"
        assert RNNOptimizationAdapter.CATEGORY == "optimization"
        assert "torch" in RNNOptimizationAdapter.DEPENDENCIES
        assert "onnx" in RNNOptimizationAdapter.SUPPORTED_FORMATS


class TestRNNOptimizationAdapterEdgeCases:
    """RNN优化适配器边界情况测试"""

    def test_execute_without_initialization(self):
        """测试未初始化执行"""
        adapter = RNNOptimizationAdapter()

        with pytest.raises(Exception):
            adapter.execute([1, 2, 3, 4, 5])

    def test_execute_with_invalid_rnn_type(self):
        """测试无效RNN类型"""
        adapter = RNNOptimizationAdapter()
        adapter.initialize(rnn_type="lstm", num_layers=3)

        # 执行时使用不同类型
        result = adapter.execute(
            [1, 2, 3, 4, 5],
            rnn_type="invalid_type"
        )

        # 应该使用默认值lstm
        assert result['rnn_type'] == 'lstm'

    def test_multiple_initializations(self):
        """测试多次初始化"""
        adapter = RNNOptimizationAdapter()

        adapter.initialize(rnn_type="lstm", num_layers=3)
        assert adapter._model['rnn_type'] == 'lstm'

        adapter.initialize(rnn_type="gru", num_layers=2)
        assert adapter._model['rnn_type'] == 'gru'

    def test_execute_with_empty_list(self):
        """测试空列表输入"""
        adapter = RNNOptimizationAdapter()
        adapter.initialize(rnn_type="lstm", num_layers=3)

        # 空列表应该返回False
        assert not adapter.validate_input([])

    def test_execute_with_large_dropout(self):
        """测试大Dropout值"""
        adapter = RNNOptimizationAdapter()
        adapter.initialize(
            rnn_type="lstm",
            num_layers=3,
            dropout_rate=0.8
        )

        result = adapter.execute([1, 2, 3, 4, 5])

        assert isinstance(result, dict)
        assert 'variational_dropout' in result['applied_optimizations']

    def test_execute_with_small_learning_rate(self):
        """测试小学习率"""
        adapter = RNNOptimizationAdapter()
        adapter.initialize(rnn_type="lstm", num_layers=3)

        result = adapter.execute(
            [1, 2, 3, 4, 5],
            learning_rate=0.00001
        )

        assert isinstance(result, dict)
        gradient_opt = result['gradient_optimization']
        assert 'warmup_schedule' in gradient_opt['applied_optimizations']

    def test_execute_with_large_learning_rate(self):
        """测试大学习率"""
        adapter = RNNOptimizationAdapter()
        adapter.initialize(rnn_type="lstm", num_layers=3)

        result = adapter.execute(
            [1, 2, 3, 4, 5],
            learning_rate=0.1
        )

        assert isinstance(result, dict)
        gradient_opt = result['gradient_optimization']
        assert 'gradient_clipping' in gradient_opt['applied_optimizations']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
