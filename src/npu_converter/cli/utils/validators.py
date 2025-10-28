"""
CLI Validation Utilities

This module provides validation functions for CLI arguments and parameters.
"""

import os
import argparse
from pathlib import Path
from typing import Optional, List, Tuple


def validate_file_path(file_path: str, extensions: Optional[List[str]] = None) -> Tuple[bool, str]:
    """
    Validate that a file path exists and has correct extension.

    Args:
        file_path: File path to validate
        extensions: List of allowed extensions (e.g., ['.onnx', '.yaml'])

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    try:
        path = Path(file_path)

        # Check if file exists
        if not path.exists():
            return False, f"文件不存在: {file_path}"

        # Check if it's a file
        if not path.is_file():
            return False, f"路径不是文件: {file_path}"

        # Check extension if specified
        if extensions:
            if path.suffix.lower() not in [ext.lower() for ext in extensions]:
                return False, f"不支持的文件类型: {path.suffix}. 支持的类型: {', '.join(extensions)}"

        return True, ""

    except Exception as e:
        return False, f"验证文件路径失败: {e}"


def validate_model_type(model_type: str) -> Tuple[bool, str]:
    """
    Validate model type parameter.

    Args:
        model_type: Model type string

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    valid_types = ["sensevoice", "vits_cantonese", "piper_vits"]

    if model_type.lower() not in valid_types:
        return False, f"不支持的模型类型: {model_type}. 支持的类型: {', '.join(valid_types)}"

    return True, ""


def validate_output_path(output_path: str, check_writable: bool = True) -> Tuple[bool, str]:
    """
    Validate output path for file creation.

    Args:
        output_path: Output path to validate
        check_writable: Whether to check if the path is writable

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    try:
        path = Path(output_path)

        # If path exists and is a file
        if path.exists():
            if path.is_file():
                if check_writable and not os.access(path, os.W_OK):
                    return False, f"输出文件不可写: {output_path}"
                return True, ""
            else:
                return False, f"输出路径是目录，不是文件: {output_path}"

        # Check if parent directory exists and is writable
        parent = path.parent
        if not parent.exists():
            try:
                parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                return False, f"无法创建输出目录: {e}"

        if check_writable and not os.access(parent, os.W_OK):
            return False, f"输出目录不可写: {parent}"

        return True, ""

    except Exception as e:
        return False, f"验证输出路径失败: {e}"


def validate_config_file(config_path: str) -> Tuple[bool, str]:
    """
    Validate configuration file.

    Args:
        config_path: Configuration file path

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    try:
        # Check file existence and extension
        is_valid, error = validate_file_path(config_path, ['.yaml', '.yml'])
        if not is_valid:
            return False, error

        # Try to parse YAML file
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            yaml.safe_load(f)

        return True, ""

    except ImportError:
        return False, "需要安装 PyYAML 来验证配置文件"
    except yaml.YAMLError as e:
        return False, f"配置文件格式错误: {e}"
    except Exception as e:
        return False, f"验证配置文件失败: {e}"


def validate_device_type(device: str) -> Tuple[bool, str]:
    """
    Validate device type parameter.

    Args:
        device: Device type string

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    valid_devices = ["npu", "cpu", "gpu"]

    if device.lower() not in valid_devices:
        return False, f"不支持的设备类型: {device}. 支持的类型: {', '.join(valid_devices)}"

    return True, ""


def validate_positive_number(value: str) -> Tuple[bool, str]:
    """
    Validate that a value is a positive number.

    Args:
        value: String value to validate

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    try:
        num_value = float(value)
        if num_value <= 0:
            return False, "值必须大于0"
        return True, ""
    except ValueError:
        return False, f"无效的数字: {value}"


def validate_range(value: str, min_val: float, max_val: float) -> Tuple[bool, str]:
    """
    Validate that a value is within a specified range.

    Args:
        value: String value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    try:
        num_value = float(value)
        if not (min_val <= num_value <= max_val):
            return False, f"值必须在 {min_val} 到 {max_val} 范围内"
        return True, ""
    except ValueError:
        return False, f"无效的数字: {value}"


class ArgumentValidator:
    """Custom argument validator for argparse."""

    @staticmethod
    def positive_int(value: str) -> int:
        """Validate positive integer."""
        try:
            int_value = int(value)
            if int_value <= 0:
                raise argparse.ArgumentTypeError(f"值必须为正整数: {value}")
            return int_value
        except ValueError:
            raise argparse.ArgumentTypeError(f"无效的整数: {value}")

    @staticmethod
    def positive_float(value: str) -> float:
        """Validate positive float."""
        try:
            float_value = float(value)
            if float_value <= 0:
                raise argparse.ArgumentTypeError(f"值必须为正数: {value}")
            return float_value
        except ValueError:
            raise argparse.ArgumentTypeError(f"无效的数字: {value}")

    @staticmethod
    def file_exists(value: str) -> str:
        """Validate that file exists."""
        is_valid, error = validate_file_path(value)
        if not is_valid:
            raise argparse.ArgumentTypeError(error)
        return value

    @staticmethod
    def yaml_file(value: str) -> str:
        """Validate YAML file."""
        is_valid, error = validate_config_file(value)
        if not is_valid:
            raise argparse.ArgumentTypeError(error)
        return value

    @staticmethod
    def output_path(value: str) -> str:
        """Validate output path."""
        is_valid, error = validate_output_path(value)
        if not is_valid:
            raise argparse.ArgumentTypeError(error)
        return value