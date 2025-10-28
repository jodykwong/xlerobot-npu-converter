"""
扩展算法配置系统单元测试

测试ExtendedAlgorithmConfig的所有功能。
"""

import pytest
import sys
import os
import tempfile
import yaml
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../src'))

from npu_converter.extensions.config.extended_algorithm_config import (
    ExtendedAlgorithmConfig,
    ParameterDefinition,
    ConfigValidationError
)


class TestParameterDefinition:
    """参数定义测试"""

    def test_int_parameter_creation(self):
        """测试整数参数创建"""
        param = ParameterDefinition(
            name="num_layers",
            param_type="int",
            required=True,
            min_value=1,
            max_value=100,
            default=10
        )

        assert param.name == "num_layers"
        assert param.param_type == ParameterType.INTEGER
        assert param.required is True
        assert param.min_value == 1
        assert param.max_value == 100
        assert param.default == 10
        assert param.choices is None

    def test_float_parameter_creation(self):
        """测试浮点参数创建"""
        param = ParameterDefinition(
            name="learning_rate",
            param_type="float",
            required=False,
            min_value=0.0001,
            max_value=1.0,
            default=0.001
        )

        assert param.param_type == "float"
        assert param.required is False

    def test_string_parameter_creation(self):
        """测试字符串参数创建"""
        param = ParameterDefinition(
            name="optimizer",
            param_type="str",
            required=True,
            choices=["adam", "sgd", "rmsprop"],
            default="adam"
        )

        assert param.param_type == "str"
        assert param.choices == ["adam", "sgd", "rmsprop"]
        assert param.default == "adam"

    def test_boolean_parameter_creation(self):
        """测试布尔参数创建"""
        param = ParameterDefinition(
            name="use_attention",
            param_type="bool",
            required=False,
            default=True
        )

        assert param.param_type == "bool"
        assert param.default is True

    def test_list_parameter_creation(self):
        """测试列表参数创建"""
        param = ParameterDefinition(
            name="hidden_sizes",
            param_type="list",
            required=False,
            default=[256, 128, 64]
        )

        assert param.param_type == "list"
        assert param.default == [256, 128, 64]

    def test_dict_parameter_creation(self):
        """测试字典参数创建"""
        param = ParameterDefinition(
            name="model_config",
            param_type="dict",
            required=False,
            default={"key1": "value1", "key2": "value2"}
        )

        assert param.param_type == "dict"
        assert isinstance(param.default, dict)

    def test_path_parameter_creation(self):
        """测试路径参数创建"""
        param = ParameterDefinition(
            name="model_path",
            param_type="path",
            required=True,
            must_exist=False
        )

        assert param.param_type == "path"
        assert param.must_exist is False

    def test_validate_int_valid(self):
        """测试整数参数验证 - 有效值"""
        param = ParameterDefinition(
            name="num_layers",
            param_type="int",
            min_value=1,
            max_value=100
        )

        # 有效值
        param._validate_value(10)
        param._validate_value(50)
        param._validate_value(1)
        param._validate_value(100)

    def test_validate_int_below_min(self):
        """测试整数参数验证 - 低于最小值"""
        param = ParameterDefinition(
            name="num_layers",
            param_type="int",
            min_value=1,
            max_value=100
        )

        with pytest.raises(ValidationError, match="小于最小值"):
            param._validate_value(0)

    def test_validate_int_above_max(self):
        """测试整数参数验证 - 超过最大值"""
        param = ParameterDefinition(
            name="num_layers",
            param_type="int",
            min_value=1,
            max_value=100
        )

        with pytest.raises(ValidationError, match="大于最大值"):
            param._validate_value(101)

    def test_validate_int_invalid_type(self):
        """测试整数参数验证 - 无效类型"""
        param = ParameterDefinition(
            name="num_layers",
            param_type=ParameterType.INTEGER
        )

        with pytest.raises(ValidationError, match="类型不匹配"):
            param._validate_value("10")

    def test_validate_string_valid(self):
        """测试字符串参数验证 - 有效值"""
        param = ParameterDefinition(
            name="optimizer",
            param_type="str",
            choices=["adam", "sgd", "rmsprop"]
        )

        param._validate_value("adam")
        param._validate_value("sgd")

    def test_validate_string_not_in_choices(self):
        """测试字符串参数验证 - 不在选择列表中"""
        param = ParameterDefinition(
            name="optimizer",
            param_type="str",
            choices=["adam", "sgd", "rmsprop"]
        )

        with pytest.raises(ValidationError, match="不在允许的选择中"):
            param._validate_value("adamw")

    def test_validate_boolean_valid(self):
        """测试布尔参数验证"""
        param = ParameterDefinition(
            name="use_attention",
            param_type="bool"
        )

        param._validate_value(True)
        param._validate_value(False)
        param._validate_value(1)
        param._validate_value(0)

    def test_validate_list_valid(self):
        """测试列表参数验证"""
        param = ParameterDefinition(
            name="sizes",
            param_type="list"
        )

        param._validate_value([1, 2, 3])
        param._validate_value(["a", "b", "c"])

    def test_validate_dict_valid(self):
        """测试字典参数验证"""
        param = ParameterDefinition(
            name="config",
            param_type="dict"
        )

        param._validate_value({"key": "value"})


class TestExtendedAlgorithmConfig:
    """扩展算法配置测试"""

    def test_config_creation_minimal(self):
        """测试最小配置创建"""
        params = [
            ParameterDefinition("param1", ParameterType.INTEGER, default=10)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)

        assert config.algorithm_id == "test_algo"
        assert len(config._parameters) == 1
        assert config.get_config("param1") == 10

    def test_config_creation_full(self):
        """测试完整配置创建"""
        params = [
            ParameterDefinition("layers", ParameterType.INTEGER, required=True, min_value=1, max_value=100, default=10),
            ParameterDefinition("lr", "float", required=True, min_value=0.0001, max_value=1.0, default=0.001),
            ParameterDefinition("optimizer", "str", required=False, choices=["adam", "sgd"], default="adam"),
            ParameterDefinition("use_attention", "bool", required=False, default=True),
            ParameterDefinition("sizes", "list", required=False, default=[256, 128]),
            ParameterDefinition("config", "dict", required=False, default={})
        ]

        config = ExtendedAlgorithmConfig(
            "test_algo",
            params,
            description="测试算法配置",
            version="1.0.0"
        )

        assert config.algorithm_id == "test_algo"
        assert config.description == "测试算法配置"
        assert config.version == "1.0.0"

    def test_configure_valid_config(self):
        """测试配置有效参数"""
        params = [
            ParameterDefinition("layers", ParameterType.INTEGER, required=True, min_value=1, max_value=100, default=10),
            ParameterDefinition("lr", "float", required=True, min_value=0.0001, max_value=1.0, default=0.001)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)

        success = config.configure({
            "layers": 20,
            "lr": 0.002
        })

        assert success
        assert config.get_config("layers") == 20
        assert config.get_config("lr") == 0.002

    def test_configure_invalid_config_missing_required(self):
        """测试配置无效参数 - 缺少必需参数"""
        params = [
            ParameterDefinition("param1", ParameterType.INTEGER, required=True),
            ParameterDefinition("param2", "float", required=True)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)

        with pytest.raises(ConfigValidationError, match="缺少必需参数"):
            config.configure({"param1": 10})

    def test_configure_invalid_config_type_mismatch(self):
        """测试配置无效参数 - 类型不匹配"""
        params = [
            ParameterDefinition("param1", ParameterType.INTEGER, required=True)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)

        with pytest.raises(ConfigValidationError, match="类型不匹配"):
            config.configure({"param1": "not_an_int"})

    def test_configure_invalid_config_value_out_of_range(self):
        """测试配置无效参数 - 值超出范围"""
        params = [
            ParameterDefinition("param1", ParameterType.INTEGER, required=True, min_value=1, max_value=100)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)

        with pytest.raises(ConfigValidationError, match="值超出范围"):
            config.configure({"param1": 200})

    def test_configure_with_validation_disabled(self):
        """测试禁用验证的配置"""
        params = [
            ParameterDefinition("param1", ParameterType.INTEGER, required=True, min_value=1, max_value=100)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)

        # 禁用验证，应该不会抛出异常
        success = config.configure(
            {"param1": 200},
            validate=False
        )

        assert success
        assert config.get_config("param1") == 200

    def test_validate_config_valid(self):
        """测试验证配置 - 有效配置"""
        params = [
            ParameterDefinition("layers", ParameterType.INTEGER, required=True, min_value=1, max_value=100, default=10)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)

        is_valid = config.validate_config({"layers": 20})

        assert is_valid is True

    def test_validate_config_invalid(self):
        """测试验证配置 - 无效配置"""
        params = [
            ParameterDefinition("layers", ParameterType.INTEGER, required=True, min_value=1, max_value=100, default=10)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)

        is_valid = config.validate_config({"layers": 200})

        assert is_valid is False

    def test_get_config(self):
        """测试获取配置"""
        params = [
            ParameterDefinition("param1", ParameterType.INTEGER, default=10)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)

        assert config.get_config("param1") == 10
        assert config.get_config("nonexistent") is None

    def test_get_config_with_default_override(self):
        """测试获取配置并覆盖默认值"""
        params = [
            ParameterDefinition("param1", ParameterType.INTEGER, default=10)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)
        config.configure({"param1": 20})

        assert config.get_config("param1") == 20

    def test_set_config(self):
        """测试设置配置"""
        params = [
            ParameterDefinition("param1", ParameterType.INTEGER, required=False)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)

        config.set_config("param1", 30)

        assert config.get_config("param1") == 30

    def test_set_config_invalid(self):
        """测试设置无效配置"""
        params = [
            ParameterDefinition("param1", ParameterType.INTEGER, min_value=1, max_value=100)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)

        with pytest.raises(ConfigValidationError):
            config.set_config("param1", 200)

    def test_add_parameter(self):
        """测试添加参数"""
        params = [
            ParameterDefinition("param1", ParameterType.INTEGER, default=10)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)

        new_param = ParameterDefinition("param2", "float", default=1.5)
        config.add_parameter(new_param)

        assert len(config._parameters) == 2
        assert config.get_config("param2") == 1.5

    def test_add_parameter_duplicate(self):
        """测试添加重复参数"""
        params = [
            ParameterDefinition("param1", ParameterType.INTEGER, default=10)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)

        duplicate_param = ParameterDefinition("param1", "float", default=1.5)

        with pytest.raises(ConfigValidationError, match="参数已存在"):
            config.add_parameter(duplicate_param)

    def test_remove_parameter(self):
        """测试删除参数"""
        params = [
            ParameterDefinition("param1", ParameterType.INTEGER, default=10),
            ParameterDefinition("param2", "float", default=1.5)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)

        success = config.remove_parameter("param1")

        assert success is True
        assert len(config._parameters) == 1
        assert "param1" not in config._parameters

    def test_remove_nonexistent_parameter(self):
        """测试删除不存在的参数"""
        params = [
            ParameterDefinition("param1", ParameterType.INTEGER, default=10)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)

        success = config.remove_parameter("param2")

        assert success is False
        assert len(config._parameters) == 1

    def test_get_all_parameters(self):
        """测试获取所有参数"""
        params = [
            ParameterDefinition("param1", ParameterType.INTEGER, default=10),
            ParameterDefinition("param2", "float", default=1.5)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)

        all_params = config.get_all_parameters()

        assert isinstance(all_params, dict)
        assert "param1" in all_params
        assert "param2" in all_params

    def test_get_parameter_definitions(self):
        """测试获取参数定义"""
        params = [
            ParameterDefinition("param1", ParameterType.INTEGER, default=10)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)

        param_defs = config.get_parameter_definitions()

        assert isinstance(param_defs, list)
        assert len(param_defs) == 1
        assert isinstance(param_defs[0], ParameterDefinition)

    def test_export_to_dict(self):
        """测试导出为字典"""
        params = [
            ParameterDefinition("layers", ParameterType.INTEGER, required=True, default=10),
            ParameterDefinition("lr", "float", required=False, default=0.001)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)
        config.configure({"layers": 20})

        exported = config.export_to_dict()

        assert isinstance(exported, dict)
        assert exported["algorithm_id"] == "test_algo"
        assert exported["version"] == config.version
        assert exported["parameters"]["layers"] == 20
        assert exported["parameters"]["lr"] == 0.001

    def test_import_from_dict(self):
        """测试从字典导入"""
        params = [
            ParameterDefinition("layers", ParameterType.INTEGER, required=True, default=10),
            ParameterDefinition("lr", "float", required=False, default=0.001)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)

        data = {
            "algorithm_id": "test_algo",
            "parameters": {
                "layers": 30,
                "lr": 0.002
            }
        }

        success = config.import_from_dict(data)

        assert success is True
        assert config.get_config("layers") == 30
        assert config.get_config("lr") == 0.002

    def test_export_to_yaml(self):
        """测试导出为YAML"""
        params = [
            ParameterDefinition("layers", ParameterType.INTEGER, required=True, default=10)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)
        config.configure({"layers": 20})

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            output_path = f.name

        try:
            success = config.export_to_yaml(output_path)

            assert success is True

            # 验证文件存在
            assert os.path.exists(output_path)

            # 验证文件内容
            with open(output_path, 'r') as f:
                data = yaml.safe_load(f)

            assert data["algorithm_id"] == "test_algo"
            assert data["parameters"]["layers"] == 20

        finally:
            if os.path.exists(output_path):
                os.remove(output_path)

    def test_import_from_yaml(self):
        """测试从YAML导入"""
        params = [
            ParameterDefinition("layers", ParameterType.INTEGER, required=True, default=10),
            ParameterDefinition("lr", "float", required=False, default=0.001)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)

        # 创建临时YAML文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            output_path = f.name
            yaml.dump({
                "algorithm_id": "test_algo",
                "parameters": {
                    "layers": 40,
                    "lr": 0.003
                }
            }, f)

        try:
            success = config.import_from_yaml(output_path)

            assert success is True
            assert config.get_config("layers") == 40
            assert config.get_config("lr") == 0.003

        finally:
            if os.path.exists(output_path):
                os.remove(output_path)

    def test_reset_to_defaults(self):
        """测试重置为默认值"""
        params = [
            ParameterDefinition("param1", ParameterType.INTEGER, default=10),
            ParameterDefinition("param2", "float", default=1.5)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)
        config.configure({"param1": 20, "param2": 2.5})

        config.reset_to_defaults()

        assert config.get_config("param1") == 10
        assert config.get_config("param2") == 1.5

    def test_get_required_parameters(self):
        """测试获取必需参数"""
        params = [
            ParameterDefinition("param1", ParameterType.INTEGER, required=True),
            ParameterDefinition("param2", ParameterType.INTEGER, required=False),
            ParameterDefinition("param3", ParameterType.INTEGER, required=True)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)

        required = config.get_required_parameters()

        assert len(required) == 2
        assert "param1" in required
        assert "param3" in required
        assert "param2" not in required

    def test_get_optional_parameters(self):
        """测试获取可选参数"""
        params = [
            ParameterDefinition("param1", ParameterType.INTEGER, required=True),
            ParameterDefinition("param2", ParameterType.INTEGER, required=False),
            ParameterDefinition("param3", ParameterType.INTEGER, required=False)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)

        optional = config.get_optional_parameters()

        assert len(optional) == 2
        assert "param2" in optional
        assert "param3" in optional
        assert "param1" not in optional

    def test_has_parameter(self):
        """测试检查参数存在"""
        params = [
            ParameterDefinition("param1", ParameterType.INTEGER, default=10)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)

        assert config.has_parameter("param1") is True
        assert config.has_parameter("param2") is False

    def test_get_config_summary(self):
        """测试获取配置摘要"""
        params = [
            ParameterDefinition("layers", ParameterType.INTEGER, required=True, default=10),
            ParameterDefinition("lr", "float", required=False, default=0.001)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)
        config.configure({"layers": 20})

        summary = config.get_config_summary()

        assert isinstance(summary, dict)
        assert summary["algorithm_id"] == "test_algo"
        assert summary["total_parameters"] == 2
        assert summary["configured_parameters"] == 1
        assert summary["parameters"]["layers"]["configured"] is True
        assert summary["parameters"]["layers"]["value"] == 20


class TestExtendedAlgorithmConfigEdgeCases:
    """扩展算法配置边界情况测试"""

    def test_configure_empty_dict(self):
        """测试配置空字典"""
        params = [
            ParameterDefinition("param1", ParameterType.INTEGER, required=False, default=10)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)

        success = config.configure({})

        assert success is True
        assert config.get_config("param1") == 10

    def test_config_with_type_conversion(self):
        """测试类型自动转换"""
        params = [
            ParameterDefinition("param1", ParameterType.INTEGER, required=True)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)

        # 传入浮点数，应该转换为整数
        success = config.configure({"param1": 10.7})

        assert success is True
        assert config.get_config("param1") == 10

    def test_config_with_path_type(self):
        """测试路径类型参数"""
        params = [
            ParameterDefinition("model_path", "path", required=False, must_exist=False)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)

        config.configure({"model_path": "/tmp/test_model.pth"})

        assert config.get_config("model_path") == "/tmp/test_model.pth"

    def test_multiple_configure_calls(self):
        """测试多次配置调用"""
        params = [
            ParameterDefinition("param1", ParameterType.INTEGER, required=False, default=10)
        ]

        config = ExtendedAlgorithmConfig("test_algo", params)

        config.configure({"param1": 20})
        assert config.get_config("param1") == 20

        config.configure({"param1": 30})
        assert config.get_config("param1") == 30


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
