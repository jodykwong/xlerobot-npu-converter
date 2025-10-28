"""
Convert命令单元测试 - Story 1.8 Subtask 1.1

测试模型转换命令的参数验证、转换流程和错误处理功能。
遵循pytest 7.x框架和AAA测试模式。
"""

import pytest
import argparse
import sys
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import tempfile
import os

# 添加项目路径到sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from npu_converter.cli.commands.convert import ConvertCommand
    from npu_converter.config.manager import ConfigurationManager
    from npu_converter.core.models.conversion_model import ConversionModel
    from npu_converter.core.models.config_model import ConfigModel
except ImportError as e:
    # 如果导入失败，跳过测试
    pytest.skip(f"无法导入ConvertCommand: {e}", allow_module_level=True)


class TestConvertCommand:
    """Convert命令测试类"""

    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建临时目录用于测试
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = MagicMock(spec=ConfigurationManager)
        self.convert_cmd = ConvertCommand(self.config_manager)

    def teardown_method(self):
        """每个测试方法后的清理"""
        # 清理临时目录
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_convert_command_initialization(self):
        """测试ConvertCommand初始化"""
        # 测试无配置管理器的初始化
        cmd = ConvertCommand()
        assert cmd.name == "convert"
        assert cmd.version == "1.0.0"

        # 测试有配置管理器的初始化
        cmd_with_config = ConvertCommand(self.config_manager)
        assert cmd_with_config.name == "convert"
        assert cmd_with_config.version == "1.0.0"

    def test_create_parser(self):
        """测试命令解析器创建"""
        parser = self.convert_cmd.create_parser()

        assert isinstance(parser, argparse.ArgumentParser)
        assert parser.prog == "convert"
        assert "模型转换工具" in parser.description

    def test_parser_arguments(self):
        """测试命令行参数解析"""
        parser = self.convert_cmd.create_parser()

        # 测试必需参数
        with pytest.raises(SystemExit):
            parser.parse_args([])  # 没有参数应该失败

        # 测试基本参数
        args = parser.parse_args([
            '--input', 'model.onnx',
            '--output', 'model.bpu',
            '--config', 'config.yaml'
        ])

        assert args.input == 'model.onnx'
        assert args.output == 'model.bpu'
        assert args.config == 'config.yaml'

    def test_parser_optional_arguments(self):
        """测试可选参数解析"""
        parser = self.convert_cmd.create_parser()

        args = parser.parse_args([
            '--input', 'model.onnx',
            '--output', 'model.bpu',
            '--device', 'rdk_x5',
            '--verbose',
            '--quiet'
        ])

        assert args.device == 'rdk_x5'
        assert args.verbose is True
        assert args.quiet is True

    def test_validate_arguments_success(self):
        """测试参数验证成功"""
        # 创建有效文件路径
        input_file = os.path.join(self.temp_dir, 'model.onnx')
        output_file = os.path.join(self.temp_dir, 'model.bpu')
        config_file = os.path.join(self.temp_dir, 'config.yaml')

        # 创建测试文件
        Path(input_file).touch()
        Path(config_file).touch()

        # 模拟参数
        args = argparse.Namespace(
            input=input_file,
            output=output_file,
            config=config_file,
            device='rdk_x5',
            verbose=False,
            quiet=False
        )

        # 验证参数
        result = self.convert_cmd._validate_arguments(args)
        assert result is True

    def test_validate_arguments_missing_input(self):
        """测试缺少输入文件参数验证"""
        input_file = os.path.join(self.temp_dir, 'missing.onnx')
        output_file = os.path.join(self.temp_dir, 'model.bpu')
        config_file = os.path.join(self.temp_dir, 'config.yaml')

        Path(config_file).touch()

        args = argparse.Namespace(
            input=input_file,
            output=output_file,
            config=config_file,
            device='rdk_x5',
            verbose=False,
            quiet=False
        )

        result = self.convert_cmd._validate_arguments(args)
        assert result is False

    def test_validate_arguments_missing_config(self):
        """测试缺少配置文件参数验证"""
        input_file = os.path.join(self.temp_dir, 'model.onnx')
        output_file = os.path.join(self.temp_dir, 'model.bpu')
        config_file = os.path.join(self.temp_dir, 'missing.yaml')

        Path(input_file).touch()

        args = argparse.Namespace(
            input=input_file,
            output=output_file,
            config=config_file,
            device='rdk_x5',
            verbose=False,
            quiet=False
        )

        result = self.convert_cmd._validate_arguments(args)
        assert result is False

    def test_validate_arguments_invalid_device(self):
        """测试无效设备参数验证"""
        input_file = os.path.join(self.temp_dir, 'model.onnx')
        output_file = os.path.join(self.temp_dir, 'model.bpu')
        config_file = os.path.join(self.temp_dir, 'config.yaml')

        Path(input_file).touch()
        Path(config_file).touch()

        args = argparse.Namespace(
            input=input_file,
            output=output_file,
            config=config_file,
            device='invalid_device',
            verbose=False,
            quiet=False
        )

        result = self.convert_cmd._validate_arguments(args)
        assert result is False

    @patch('npu_converter.cli.commands.convert.ConversionModel')
    def test_load_conversion_model_success(self, mock_conversion_model):
        """测试加载转换模型成功"""
        # 模拟ConversionModel
        mock_model = MagicMock(spec=ConversionModel)
        mock_conversion_model.from_file.return_value = mock_model

        input_file = os.path.join(self.temp_dir, 'model.onnx')
        result = self.convert_cmd._load_conversion_model(input_file)

        assert result == mock_model
        mock_conversion_model.from_file.assert_called_once_with(input_file)

    @patch('npu_converter.cli.commands.convert.ConversionModel')
    def test_load_conversion_model_failure(self, mock_conversion_model):
        """测试加载转换模型失败"""
        mock_conversion_model.from_file.side_effect = Exception("模型加载失败")

        input_file = os.path.join(self.temp_dir, 'model.onnx')
        result = self.convert_cmd._load_conversion_model(input_file)

        assert result is None

    @patch('npu_converter.cli.commands.convert.ConfigModel')
    def test_load_config_model_success(self, mock_config_model):
        """测试加载配置模型成功"""
        # 模拟ConfigModel
        mock_config = MagicMock(spec=ConfigModel)
        mock_config_model.from_file.return_value = mock_config

        config_file = os.path.join(self.temp_dir, 'config.yaml')
        result = self.convert_cmd._load_config_model(config_file)

        assert result == mock_config
        mock_config_model.from_file.assert_called_once_with(config_file)

    @patch('npu_converter.cli.commands.convert.ConfigModel')
    def test_load_config_model_failure(self, mock_config_model):
        """测试加载配置模型失败"""
        mock_config_model.from_file.side_effect = Exception("配置加载失败")

        config_file = os.path.join(self.temp_dir, 'config.yaml')
        result = self.convert_cmd._load_config_model(config_file)

        assert result is None

    @patch('npu_converter.cli.commands.convert.BaseCLI')
    def test_execute_conversion_success(self, mock_base_cli):
        """测试执行转换成功"""
        mock_conversion_model = MagicMock(spec=ConversionModel)
        mock_config_model = MagicMock(spec=ConfigModel)
        mock_base_cli.execute_conversion.return_value = True

        result = self.convert_cmd._execute_conversion(
            mock_conversion_model,
            mock_config_model,
            'output.bpu'
        )

        assert result is True
        mock_base_cli.execute_conversion.assert_called_once()

    @patch('npu_converter.cli.commands.convert.BaseCLI')
    def test_execute_conversion_failure(self, mock_base_cli):
        """测试执行转换失败"""
        mock_conversion_model = MagicMock(spec=ConversionModel)
        mock_config_model = MagicMock(spec=ConfigModel)
        mock_base_cli.execute_conversion.return_value = False

        result = self.convert_cmd._execute_conversion(
            mock_conversion_model,
            mock_config_model,
            'output.bpu'
        )

        assert result is False

    @patch('builtins.print')
    def test_run_success(self, mock_print):
        """测试运行命令成功"""
        # 创建测试文件
        input_file = os.path.join(self.temp_dir, 'model.onnx')
        output_file = os.path.join(self.temp_dir, 'model.bpu')
        config_file = os.path.join(self.temp_dir, 'config.yaml')

        Path(input_file).touch()
        Path(config_file).touch()

        # 模拟依赖方法
        with patch.object(self.convert_cmd, '_validate_arguments', return_value=True), \
             patch.object(self.convert_cmd, '_load_conversion_model', return_value=MagicMock()), \
             patch.object(self.convert_cmd, '_load_config_model', return_value=MagicMock()), \
             patch.object(self.convert_cmd, '_execute_conversion', return_value=True):

            args = [
                '--input', input_file,
                '--output', output_file,
                '--config', config_file
            ]

            result = self.convert_cmd.run(args)

            assert result == 0

    @patch('builtins.print')
    def test_run_validation_failure(self, mock_print):
        """测试运行命令验证失败"""
        # 创建测试文件
        input_file = os.path.join(self.temp_dir, 'model.onnx')
        output_file = os.path.join(self.temp_dir, 'model.bpu')
        config_file = os.path.join(self.temp_dir, 'config.yaml')

        # 不创建文件，让验证失败

        args = [
            '--input', input_file,
            '--output', output_file,
            '--config', config_file
        ]

        result = self.convert_cmd.run(args)

        assert result == 1

    def test_run_invalid_arguments(self):
        """测试运行命令无效参数"""
        args = ['--invalid-argument']

        result = self.convert_cmd.run(args)

        # argparse应该处理无效参数并返回错误码
        assert result != 0

    @patch('builtins.print')
    def test_run_conversion_failure(self, mock_print):
        """测试运行命令转换失败"""
        # 创建测试文件
        input_file = os.path.join(self.temp_dir, 'model.onnx')
        output_file = os.path.join(self.temp_dir, 'model.bpu')
        config_file = os.path.join(self.temp_dir, 'config.yaml')

        Path(input_file).touch()
        Path(config_file).touch()

        # 模拟转换失败
        with patch.object(self.convert_cmd, '_validate_arguments', return_value=True), \
             patch.object(self.convert_cmd, '_load_conversion_model', return_value=MagicMock()), \
             patch.object(self.convert_cmd, '_load_config_model', return_value=MagicMock()), \
             patch.object(self.convert_cmd, '_execute_conversion', return_value=False):

            args = [
                '--input', input_file,
                '--output', output_file,
                '--config', config_file
            ]

            result = self.convert_cmd.run(args)

            assert result == 1

    def test_verbose_mode(self):
        """测试详细模式"""
        input_file = os.path.join(self.temp_dir, 'model.onnx')
        output_file = os.path.join(self.temp_dir, 'model.bpu')
        config_file = os.path.join(self.temp_dir, 'config.yaml')

        Path(input_file).touch()
        Path(config_file).touch()

        args = [
            '--input', input_file,
            '--output', output_file,
            '--config', config_file,
            '--verbose'
        ]

        # 验证verbose参数被正确解析
        parser = self.convert_cmd.create_parser()
        parsed_args = parser.parse_args(args)
        assert parsed_args.verbose is True

    def test_quiet_mode(self):
        """测试静默模式"""
        input_file = os.path.join(self.temp_dir, 'model.onnx')
        output_file = os.path.join(self.temp_dir, 'model.bpu')
        config_file = os.path.join(self.temp_dir, 'config.yaml')

        Path(input_file).touch()
        Path(config_file).touch()

        args = [
            '--input', input_file,
            '--output', output_file,
            '--config', config_file,
            '--quiet'
        ]

        # 验证quiet参数被正确解析
        parser = self.convert_cmd.create_parser()
        parsed_args = parser.parse_args(args)
        assert parsed_args.quiet is True