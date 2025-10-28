"""
CNN改进适配器单元测试

测试CNNImprovementAdapter的所有功能。
"""

import pytest
import sys
import os
import numpy as np

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../src'))

from npu_converter.extensions.algorithms.cnn_improvement_adapter import (
    CNNImprovementAdapter
)


class TestCNNImprovementAdapter:
    """CNN改进适配器测试"""

    def test_initialization(self):
        """测试初始化"""
        adapter = CNNImprovementAdapter()
        assert adapter._model is None
        assert adapter._config == {}
        assert adapter._feature_extractors == {}
        assert adapter._statistics['execution_count'] == 0
        assert adapter._statistics['total_execution_time'] == 0.0
        assert adapter._statistics['feature_extraction_count'] == 0
        assert adapter._statistics['layers_processed'] == 0

    def test_initialize_resnet_success(self):
        """测试ResNet初始化成功"""
        adapter = CNNImprovementAdapter()
        success = adapter.initialize(
            architecture="resnet",
            num_layers=50,
            kernel_size=3,
            use_depthwise=False,
            use_se_block=True,
            use_skip_connection=True
        )
        assert success
        assert adapter._model is not None
        assert adapter._model['architecture'] == 'resnet'
        assert adapter._model['num_layers'] == 50

    def test_initialize_vgg_success(self):
        """测试VGG初始化成功"""
        adapter = CNNImprovementAdapter()
        success = adapter.initialize(
            architecture="vgg",
            num_layers=16,
            kernel_size=3
        )
        assert success
        assert adapter._model['architecture'] == 'vgg'

    def test_initialize_mobilenet_success(self):
        """测试MobileNet初始化成功"""
        adapter = CNNImprovementAdapter()
        success = adapter.initialize(
            architecture="mobilenet",
            num_layers=28,
            use_depthwise=True
        )
        assert success
        assert adapter._model['architecture'] == 'mobilenet'

    def test_initialize_efficientnet_success(self):
        """测试EfficientNet初始化成功"""
        adapter = CNNImprovementAdapter()
        success = adapter.initialize(
            architecture="efficientnet",
            num_layers=24,
            use_se_block=True
        )
        assert success
        assert adapter._model['architecture'] == 'efficientnet'

    def test_initialize_custom_architecture(self):
        """测试自定义架构初始化"""
        adapter = CNNImprovementAdapter()
        success = adapter.initialize(
            architecture="custom",
            num_layers=10
        )
        assert success
        assert adapter._model['architecture'] == 'custom'

    def test_validate_input_valid_numpy_array(self):
        """测试输入验证 - 有效numpy数组"""
        adapter = CNNImprovementAdapter()
        input_data = np.random.rand(224, 224, 3).astype(np.float32)
        assert adapter.validate_input(input_data)

    def test_validate_input_4d_array(self):
        """测试输入验证 - 4D数组"""
        adapter = CNNImprovementAdapter()
        input_data = np.random.rand(10, 224, 224, 3).astype(np.float32)
        assert adapter.validate_input(input_data)

    def test_validate_input_invalid_dtype(self):
        """测试输入验证 - 无效数据类型"""
        adapter = CNNImprovementAdapter()
        input_data = np.random.rand(224, 224, 3).astype(np.int32)
        assert not adapter.validate_input(input_data)

    def test_validate_input_invalid_dimensions(self):
        """测试输入验证 - 无效维度"""
        adapter = CNNImprovementAdapter()
        input_data = np.random.rand(100).astype(np.float32)
        assert not adapter.validate_input(input_data)

    def test_validate_input_none(self):
        """测试输入验证 - None"""
        adapter = CNNImprovementAdapter()
        assert not adapter.validate_input(None)

    def test_validate_output_valid(self):
        """测试输出验证 - 有效输出"""
        adapter = CNNImprovementAdapter()
        output_data = {
            'architecture': 'resnet',
            'layers_processed': 50,
            'applied_optimizations': ['depthwise_convolution']
        }
        assert adapter.validate_output(output_data)

    def test_validate_output_invalid_type(self):
        """测试输出验证 - 无效类型"""
        adapter = CNNImprovementAdapter()
        assert not adapter.validate_output("invalid")
        assert not adapter.validate_output(None)

    def test_validate_output_missing_fields(self):
        """测试输出验证 - 缺少字段"""
        adapter = CNNImprovementAdapter()
        output_data = {'missing': 'fields'}
        assert not adapter.validate_output(output_data)

    def test_execute_resnet_with_optimizations(self):
        """测试执行ResNet优化"""
        adapter = CNNImprovementAdapter()
        adapter.initialize(
            architecture="resnet",
            num_layers=50,
            use_depthwise=True,
            use_se_block=True,
            use_skip_connection=True
        )

        result = adapter.execute(
            "test_image_data",
            extract_features=True,
            feature_level="all"
        )

        assert isinstance(result, dict)
        assert 'architecture' in result
        assert result['architecture'] == 'resnet'
        assert 'applied_optimizations' in result
        assert 'depthwise_convolution' in result['applied_optimizations']
        assert 'squeeze_and_excitation' in result['applied_optimizations']
        assert 'features' in result

    def test_execute_vgg_with_depthwise(self):
        """测试执行VGG深度可分离卷积"""
        adapter = CNNImprovementAdapter()
        adapter.initialize(
            architecture="vgg",
            num_layers=16,
            use_depthwise=True
        )

        result = adapter.execute(
            "test_image_data",
            extract_features=True
        )

        assert isinstance(result, dict)
        assert 'architecture' in result
        assert result['architecture'] == 'vgg'
        assert 'memory_reduction' in result

    def test_execute_mobilenet(self):
        """测试执行MobileNet"""
        adapter = CNNImprovementAdapter()
        adapter.initialize(
            architecture="mobilenet",
            num_layers=28,
            use_depthwise=True,
            use_se_block=True
        )

        result = adapter.execute(
            "test_image_data"
        )

        assert isinstance(result, dict)
        assert result['architecture'] == 'mobilenet'
        assert result['mobile_optimized'] is True
        assert 'memory_reduction' in result

    def test_execute_efficientnet(self):
        """测试执行EfficientNet"""
        adapter = CNNImprovementAdapter()
        adapter.initialize(
            architecture="efficientnet",
            num_layers=24,
            use_depthwise=True,
            use_se_block=True
        )

        result = adapter.execute(
            "test_image_data"
        )

        assert isinstance(result, dict)
        assert result['architecture'] == 'efficientnet'
        assert result['state_of_the_art'] is True
        assert 'compound_scaling' in result['applied_optimizations']

    def test_execute_custom_architecture(self):
        """测试执行自定义架构"""
        adapter = CNNImprovementAdapter()
        adapter.initialize(
            architecture="custom",
            num_layers=10
        )

        result = adapter.execute(
            "test_image_data"
        )

        assert isinstance(result, dict)
        assert result['architecture'] == 'custom'
        assert 'custom_optimization' in result['applied_optimizations']

    def test_execute_with_feature_extraction_all_levels(self):
        """测试全层级特征提取"""
        adapter = CNNImprovementAdapter()
        adapter.initialize(architecture="resnet", num_layers=50)

        result = adapter.execute(
            "test_image_data",
            extract_features=True,
            feature_level="all"
        )

        assert 'features' in result
        features = result['features']
        assert 'low_level' in features
        assert 'mid_level' in features
        assert 'high_level' in features

    def test_execute_with_feature_extraction_low_level(self):
        """测试低层特征提取"""
        adapter = CNNImprovementAdapter()
        adapter.initialize(architecture="resnet", num_layers=50)

        result = adapter.execute(
            "test_image_data",
            extract_features=True,
            feature_level="low"
        )

        assert 'features' in result
        assert 'low_level' in result['features']

    def test_execute_with_feature_extraction_mid_level(self):
        """测试中层特征提取"""
        adapter = CNNImprovementAdapter()
        adapter.initialize(architecture="resnet", num_layers=50)

        result = adapter.execute(
            "test_image_data",
            extract_features=True,
            feature_level="mid"
        )

        assert 'features' in result
        assert 'mid_level' in result['features']

    def test_execute_with_feature_extraction_high_level(self):
        """测试高层特征提取"""
        adapter = CNNImprovementAdapter()
        adapter.initialize(architecture="resnet", num_layers=50)

        result = adapter.execute(
            "test_image_data",
            extract_features=True,
            feature_level="high"
        )

        assert 'features' in result
        assert 'high_level' in result['features']

    def test_extract_features(self):
        """测试特征提取方法"""
        adapter = CNNImprovementAdapter()

        features = adapter._extract_features("test_data", "all")

        assert isinstance(features, dict)
        assert 'low_level' in features
        assert 'mid_level' in features
        assert 'high_level' in features
        assert 'total_features' in features
        assert 'extraction_method' in features

    def test_get_model_info(self):
        """测试获取模型信息"""
        adapter = CNNImprovementAdapter()
        adapter.initialize(
            architecture="resnet",
            num_layers=50,
            kernel_size=3
        )

        info = adapter.get_model_info()

        assert isinstance(info, dict)
        assert 'architecture' in info
        assert 'num_layers' in info
        assert 'kernel_size' in info
        assert 'estimated_params' in info
        assert 'model_size_mb' in info

    def test_get_model_info_not_initialized(self):
        """测试未初始化时获取模型信息"""
        adapter = CNNImprovementAdapter()
        info = adapter.get_model_info()
        assert info == {}

    def test_estimate_parameters_resnet(self):
        """测试ResNet参数估算"""
        adapter = CNNImprovementAdapter()
        adapter.initialize(architecture="resnet", num_layers=50)

        params = adapter._estimate_parameters()

        assert params > 0
        assert isinstance(params, int)

    def test_estimate_parameters_vgg(self):
        """测试VGG参数估算"""
        adapter = CNNImprovementAdapter()
        adapter.initialize(architecture="vgg", num_layers=16)

        params = adapter._estimate_parameters()

        assert params > 0
        assert isinstance(params, int)

    def test_estimate_parameters_mobilenet(self):
        """测试MobileNet参数估算"""
        adapter = CNNImprovementAdapter()
        adapter.initialize(architecture="mobilenet", num_layers=28)

        params = adapter._estimate_parameters()

        assert params > 0
        assert isinstance(params, int)

    def test_estimate_parameters_efficientnet(self):
        """测试EfficientNet参数估算"""
        adapter = CNNImprovementAdapter()
        adapter.initialize(architecture="efficientnet", num_layers=24)

        params = adapter._estimate_parameters()

        assert params > 0
        assert isinstance(params, int)

    def test_estimate_parameters_custom(self):
        """测试自定义架构参数估算"""
        adapter = CNNImprovementAdapter()
        adapter.initialize(architecture="custom", num_layers=10)

        params = adapter._estimate_parameters()

        assert params > 0
        assert isinstance(params, int)

    def test_estimate_model_size(self):
        """测试模型大小估算"""
        adapter = CNNImprovementAdapter()
        adapter.initialize(architecture="resnet", num_layers=50)

        size = adapter._estimate_model_size()

        assert size > 0
        assert isinstance(size, float)

    def test_get_performance_metrics(self):
        """测试性能指标"""
        adapter = CNNImprovementAdapter()
        adapter.initialize(architecture="resnet", num_layers=50)

        # 执行一些操作
        adapter.execute("test_image", extract_features=True)

        metrics = adapter.get_performance_metrics()

        assert isinstance(metrics, dict)
        assert 'execution_count' in metrics
        assert 'total_execution_time' in metrics
        assert 'average_execution_time' in metrics
        assert 'feature_extraction_count' in metrics
        assert 'throughput_samples_per_second' in metrics

    def test_benchmark(self):
        """测试基准测试"""
        adapter = CNNImprovementAdapter()
        adapter.initialize(architecture="resnet", num_layers=50)

        result = adapter.benchmark("test_image", iterations=5)

        assert isinstance(result, dict)
        assert 'iterations' in result
        assert 'success_rate' in result
        assert 'min_time' in result
        assert 'max_time' in result
        assert 'mean_time' in result
        assert result['success_rate'] == 100.0

    def test_get_statistics(self):
        """测试统计信息"""
        adapter = CNNImprovementAdapter()
        adapter.initialize(architecture="resnet", num_layers=50)

        stats = adapter.get_statistics()

        assert isinstance(stats, dict)
        assert stats['adapter_type'] == 'CNNImprovementAdapter'
        assert stats['version'] == adapter.VERSION
        assert stats['category'] == adapter.CATEGORY
        assert stats['initialized'] is True
        assert 'statistics' in stats
        assert 'performance_metrics' in stats
        assert 'model_info' in stats

    def test_constants(self):
        """测试常量定义"""
        assert CNNImprovementAdapter.VERSION == "1.0.0"
        assert CNNImprovementAdapter.DESCRIPTION == "CNN改进算法适配器"
        assert CNNImprovementAdapter.AUTHOR == "XLeRobot Team"
        assert CNNImprovementAdapter.CATEGORY == "optimization"
        assert "torch" in CNNImprovementAdapter.DEPENDENCIES
        assert "onnx" in CNNImprovementAdapter.SUPPORTED_FORMATS


class TestCNNImprovementAdapterEdgeCases:
    """CNN改进适配器边界情况测试"""

    def test_execute_without_initialization(self):
        """测试未初始化执行"""
        adapter = CNNImprovementAdapter()

        with pytest.raises(Exception):
            adapter.execute("test_image")

    def test_execute_without_feature_extraction(self):
        """测试不提取特征"""
        adapter = CNNImprovementAdapter()
        adapter.initialize(architecture="resnet", num_layers=50)

        result = adapter.execute(
            "test_image_data",
            extract_features=False
        )

        assert isinstance(result, dict)
        assert 'features' not in result

    def test_execute_with_invalid_architecture(self):
        """测试无效架构"""
        adapter = CNNImprovementAdapter()
        adapter.initialize(architecture="invalid", num_layers=10)

        result = adapter.execute("test_image_data")

        assert isinstance(result, dict)
        assert result['architecture'] == 'custom'

    def test_multiple_initializations(self):
        """测试多次初始化"""
        adapter = CNNImprovementAdapter()

        adapter.initialize(architecture="resnet", num_layers=50)
        assert adapter._model['architecture'] == 'resnet'

        adapter.initialize(architecture="vgg", num_layers=16)
        assert adapter._model['architecture'] == 'vgg'

    def test_execute_numpy_array_batch(self):
        """测试批量numpy数组"""
        adapter = CNNImprovementAdapter()
        adapter.initialize(architecture="resnet", num_layers=50)

        # 3D array (single image)
        input_data = np.random.rand(224, 224, 3).astype(np.float32)
        result = adapter.execute(input_data)
        assert isinstance(result, dict)

        # 4D array (batch of images)
        input_data = np.random.rand(10, 224, 224, 3).astype(np.float32)
        result = adapter.execute(input_data)
        assert isinstance(result, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
