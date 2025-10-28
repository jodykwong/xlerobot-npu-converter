"""
CLI主模块单元测试 - Story 1.8 Subtask 1.1

测试CLI主入口点的命令解析、参数验证和错误处理功能。
遵循pytest 7.x框架和AAA测试模式。
"""

import pytest
import sys
import argparse
from unittest.mock import patch, MagicMock
from pathlib import Path

# 添加项目路径到sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from npu_converter.cli.main import (
    main, print_banner, print_version, config_command,
    convert_command, info_command, Colors
)


class TestCLIMain:
    """CLI主模块测试类"""

    def test_print_banner(self):
        """测试横幅打印功能"""
        # 测试横幅打印不抛出异常
        with patch('builtins.print') as mock_print:
            print_banner()
            mock_print.assert_called_once()
            # 验证包含关键信息
            call_args = mock_print.call_args[0][0]
            assert "XLeRobot NPU转换器" in call_args
            assert "版本: 1.0.0" in call_args

    def test_print_version(self):
        """测试版本信息打印"""
        with patch('builtins.print') as mock_print:
            print_version()
            mock_print.assert_called()
            # 验证版本信息
            all_calls = [str(call[0][0]) for call in mock_print.call_args_list]
            version_text = ''.join(all_calls)
            assert "XLeRobot NPU转换器 CLI工具" in version_text
            assert "版本: 1.0.0" in version_text

    @patch('npu_converter.cli.main.config_main')
    def test_config_command_success(self, mock_config_main):
        """测试配置命令成功执行"""
        mock_config_main.return_value = 0

        # 创建模拟args对象
        mock_args = MagicMock()
        mock_args.args = ['create', 'vits_cantonese', '-o', 'config.yaml']

        result = config_command(mock_args)

        assert result == 0
        mock_config_main.assert_called_once()

    @patch('npu_converter.cli.main.config_main')
    def test_config_command_failure(self, mock_config_main):
        """测试配置命令执行失败"""
        mock_config_main.return_value = 1

        mock_args = MagicMock()
        mock_args.args = ['validate', 'config.yaml']

        result = config_command(mock_args)

        assert result == 1

    @patch('npu_converter.cli.main.ConvertCommand')
    @patch('sys.argv', ['xlerobot', 'convert', '--input', 'model.onnx', '--output', 'model.bpu'])
    def test_convert_command_success(self, mock_convert_command_class):
        """测试转换命令成功执行"""
        mock_convert_cmd = MagicMock()
        mock_convert_cmd.run.return_value = 0
        mock_convert_command_class.return_value = mock_convert_cmd

        mock_args = MagicMock()

        result = convert_command(mock_args)

        assert result == 0
        mock_convert_cmd.run.assert_called_once_with(['--input', 'model.onnx', '--output', 'model.bpu'])

    @patch('npu_converter.cli.main.ConvertCommand')
    @patch('sys.argv', ['xlerobot', 'convert', '--input', 'model.onnx'])
    def test_convert_command_with_partial_args(self, mock_convert_command_class):
        """测试转换命令部分参数"""
        mock_convert_cmd = MagicMock()
        mock_convert_cmd.run.return_value = 0
        mock_convert_command_class.return_value = mock_convert_cmd

        mock_args = MagicMock()

        result = convert_command(mock_args)

        assert result == 0
        mock_convert_cmd.run.assert_called_once_with(['--input', 'model.onnx'])

    @patch('npu_converter.cli.main.ConvertCommand')
    @patch('sys.argv', ['xlerobot', 'other', 'command'])
    def test_convert_command_no_convert_args(self, mock_convert_command_class):
        """测试转换命令没有convert参数时的默认行为"""
        mock_convert_cmd = MagicMock()
        mock_convert_cmd.run.return_value = 0
        mock_convert_command_class.return_value = mock_convert_cmd

        mock_args = MagicMock()

        result = convert_command(mock_args)

        assert result == 0
        mock_convert_cmd.run.assert_called_once_with()

    @patch('builtins.print')
    def test_info_command(self, mock_print):
        """测试信息命令"""
        mock_args = MagicMock()

        result = info_command(mock_args)

        assert result is None  # info_command没有返回值
        mock_print.assert_called()
        # 验证关键信息
        all_calls = [str(call[0][0]) for call in mock_print.call_args_list]
        info_text = ''.join(all_calls)
        assert "XLeRobot项目信息" in info_text
        assert "支持的模型类型" in info_text
        assert "VITS-Cantonese" in info_text
        assert "SenseVoice" in info_text

    @patch('npu_converter.cli.main.print_banner')
    @patch('npu_converter.cli.main.print_version')
    @patch('sys.argv', ['xlerobot', '--version'])
    def test_main_version_flag(self, mock_print_version, mock_print_banner):
        """测试主函数版本标志"""
        result = main()

        assert result == 0
        mock_print_version.assert_called_once()
        mock_print_banner.assert_not_called()

    @patch('npu_converter.cli.main.print_banner')
    @patch('argparse.ArgumentParser.print_help')
    @patch('sys.argv', ['xlerobot'])
    def test_main_no_command(self, mock_print_help, mock_print_banner):
        """测试主函数无命令时显示帮助"""
        result = main()

        assert result == 0
        mock_print_banner.assert_called_once()
        mock_print_help.assert_called_once()

    @patch('npu_converter.cli.main.print_banner')
    @patch('npu_converter.cli.main.info_command')
    @patch('sys.argv', ['xlerobot', 'info'])
    def test_main_info_command(self, mock_info_command, mock_print_banner):
        """测试主函数info命令"""
        mock_info_command.return_value = None

        result = main()

        assert result == 0
        mock_print_banner.assert_called_once()
        mock_info_command.assert_called_once()

    @patch('npu_converter.cli.main.print_banner')
    @patch('builtins.print')
    @patch('sys.argv', ['xlerobot', '--quiet'])
    def test_main_quiet_mode(self, mock_print, mock_print_banner):
        """测试主函数静默模式"""
        result = main()

        assert result == 0
        mock_print_banner.assert_not_called()

    @patch('npu_converter.cli.main.print_banner')
    @patch('builtins.print')
    @patch('sys.argv', ['xlerobot', 'invalid_command'])
    def test_main_invalid_command(self, mock_print, mock_print_banner):
        """测试主函数无效命令"""
        result = main()

        assert result == 1
        mock_print_banner.assert_called_once()
        # 验证错误消息
        error_calls = [str(call[0][0]) for call in mock_print.call_args_list]
        error_text = ''.join(error_calls)
        assert "命令执行异常" in error_text

    @patch('npu_converter.cli.main.print_banner')
    @patch('builtins.print')
    @patch('sys.argv', ['xlerobot'])
    @patch('sys.exit')
    def test_main_keyboard_interrupt(self, mock_exit, mock_print, mock_print_banner):
        """测试主函数键盘中断"""
        # 模拟KeyboardInterrupt异常
        with patch.object(argparse.ArgumentParser, 'parse_args', side_effect=KeyboardInterrupt):
            result = main()

            assert result == 130
            mock_print_banner.assert_called_once()
            # 验证取消消息
            mock_print.assert_called_with("\n👋 操作已取消")

    @patch('npu_converter.cli.main.print_banner')
    @patch('builtins.print')
    @patch('sys.argv', ['xlerobot', 'info'])
    def test_main_exception_handling(self, mock_print, mock_print_banner):
        """测试主函数异常处理"""
        # 模拟info_command抛出异常
        with patch('npu_converter.cli.main.info_command', side_effect=Exception("Test error")):
            result = main()

            assert result == 1
            mock_print_banner.assert_called_once()
            # 验证错误消息
            error_calls = [str(call[0][0]) for call in mock_print.call_args_list]
            error_text = ''.join(error_calls)
            assert "命令执行异常: Test error" in error_text

    def test_colors_class(self):
        """测试颜色类常量"""
        assert hasattr(Colors, 'HEADER')
        assert hasattr(Colors, 'BLUE')
        assert hasattr(Colors, 'GREEN')
        assert hasattr(Colors, 'WARNING')
        assert hasattr(Colors, 'FAIL')
        assert hasattr(Colors, 'ENDC')
        assert hasattr(Colors, 'BOLD')
        assert hasattr(Colors, 'UNDERLINE')

        # 验证颜色代码格式
        assert Colors.HEADER.startswith('\033[')
        assert Colors.ENDC == '\033[0m'


class TestCLIArgumentParsing:
    """CLI参数解析测试类"""

    @patch('npu_converter.cli.main.print_banner')
    @patch('npu_converter.cli.main.config_command')
    @patch('sys.argv', ['xlerobot', 'config', 'create', 'vits_cantonese'])
    def test_config_command_parsing(self, mock_config_command, mock_print_banner):
        """测试config命令参数解析"""
        mock_config_command.return_value = 0

        result = main()

        assert result == 0
        mock_config_command.assert_called_once()
        # 验证传递的参数
        call_args = mock_config_command.call_args[0][0]
        assert hasattr(call_args, 'args')
        assert call_args.args == ['create', 'vits_cantonese']

    @patch('npu_converter.cli.main.print_banner')
    @patch('npu_converter.cli.main.ConvertCommand')
    @patch('sys.argv', ['xlerobot', 'convert', '--input', 'model.onnx', '--output', 'model.bpu'])
    def test_convert_command_parsing(self, mock_convert_command_class, mock_print_banner):
        """测试convert命令参数解析"""
        mock_convert_cmd = MagicMock()
        mock_convert_cmd.run.return_value = 0
        mock_convert_command_class.return_value = mock_convert_cmd

        result = main()

        assert result == 0
        mock_convert_cmd.run.assert_called_once()

    @patch('npu_converter.cli.main.print_banner')
    @patch('npu_converter.cli.main.info_command')
    @patch('sys.argv', ['xlerobot', 'info'])
    def test_info_command_parsing(self, mock_info_command, mock_print_banner):
        """测试info命令参数解析"""
        mock_info_command.return_value = None

        result = main()

        assert result == 0
        mock_info_command.assert_called_once()

    @patch('npu_converter.cli.main.print_banner')
    @patch('builtins.print')
    @patch('sys.argv', ['xlerobot', 'convert', '--invalid-flag'])
    def test_invalid_argument_handling(self, mock_print, mock_print_banner):
        """测试无效参数处理"""
        result = main()

        # argparse会处理无效参数并退出，但我们要确保异常被正确捕获
        assert result == 1