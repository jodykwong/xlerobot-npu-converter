#!/usr/bin/env python3
"""
Tests for CLI Validation Utilities

This module tests the validation functions according to Story 1.6 AC2.
"""

import pytest
import sys
import tempfile
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from npu_converter.cli.utils.validators import (
    validate_file_path,
    validate_model_type,
    validate_output_path,
    validate_config_file,
    validate_device_type,
    ArgumentValidator
)


class TestFileValidation:
    """Test file validation functions."""

    def test_validate_existing_file(self):
        """Test validation of existing file."""
        with tempfile.NamedTemporaryFile(suffix=".onnx", delete=False) as tmp:
            tmp.write(b"test content")
            tmp_path = tmp.name

        try:
            is_valid, error = validate_file_path(tmp_path)
            assert is_valid == True
            assert error == ""
        finally:
            os.unlink(tmp_path)

    def test_validate_nonexistent_file(self):
        """Test validation of non-existent file."""
        is_valid, error = validate_file_path("nonexistent.onnx")
        assert is_valid == False
        assert "文件不存在" in error

    def test_validate_file_with_extension(self):
        """Test validation with extension check."""
        with tempfile.NamedTemporaryFile(suffix=".onnx", delete=False) as tmp:
            tmp.write(b"test content")
            tmp_path = tmp.name

        try:
            # Valid extension
            is_valid, error = validate_file_path(tmp_path, [".onnx", ".yaml"])
            assert is_valid == True

            # Invalid extension
            is_valid, error = validate_file_path(tmp_path, [".yaml", ".json"])
            assert is_valid == False
            assert "不支持的文件类型" in error
        finally:
            os.unlink(tmp_path)

    def test_validate_directory_as_file(self):
        """Test validation when path is directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            is_valid, error = validate_file_path(tmp_dir)
            assert is_valid == False
            assert "路径不是文件" in error


class TestModelTypeValidation:
    """Test model type validation."""

    def test_valid_model_types(self):
        """Test valid model types."""
        valid_types = ["sensevoice", "vits_cantonese", "piper_vits"]
        for model_type in valid_types:
            is_valid, error = validate_model_type(model_type)
            assert is_valid == True
            assert error == ""

    def test_invalid_model_type(self):
        """Test invalid model type."""
        is_valid, error = validate_model_type("invalid_type")
        assert is_valid == False
        assert "不支持的模型类型" in error

    def test_case_insensitive(self):
        """Test case insensitive validation."""
        is_valid, error = validate_model_type("SENSEVOICE")
        assert is_valid == True


class TestOutputPathValidation:
    """Test output path validation."""

    def test_existing_file_writable(self):
        """Test existing writable file."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name

        try:
            is_valid, error = validate_output_path(tmp_path)
            assert is_valid == True
            assert error == ""
        finally:
            os.unlink(tmp_path)

    def test_create_new_file_path(self):
        """Test creating new file path."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = os.path.join(tmp_dir, "new_file.bpu")
            is_valid, error = validate_output_path(output_path)
            assert is_valid == True
            assert error == ""

    def test_nonexistent_parent_directory(self):
        """Test path with non-existent parent directory."""
        output_path = "/nonexistent/path/output.bpu"
        # This should try to create the directory and succeed
        is_valid, error = validate_output_path(output_path, check_writable=False)
        assert is_valid == True


class TestConfigFileValidation:
    """Test configuration file validation."""

    def test_valid_yaml_config(self):
        """Test valid YAML configuration."""
        valid_yaml_content = """
model_type: sensevoice
device: npu
quantization:
  enabled: true
  bits: 8
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp:
            tmp.write(valid_yaml_content)
            tmp_path = tmp.name

        try:
            is_valid, error = validate_config_file(tmp_path)
            assert is_valid == True
            assert error == ""
        finally:
            os.unlink(tmp_path)

    def test_invalid_yaml_config(self):
        """Test invalid YAML configuration."""
        invalid_yaml_content = """
model_type: sensevoice
device: npu
invalid_yaml: [unclosed array
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp:
            tmp.write(invalid_yaml_content)
            tmp_path = tmp.name

        try:
            is_valid, error = validate_config_file(tmp_path)
            assert is_valid == False
            assert "配置文件格式错误" in error
        finally:
            os.unlink(tmp_path)

    def test_nonexistent_config_file(self):
        """Test non-existent configuration file."""
        is_valid, error = validate_config_file("nonexistent.yaml")
        assert is_valid == False
        assert "文件不存在" in error


class TestDeviceTypeValidation:
    """Test device type validation."""

    def test_valid_device_types(self):
        """Test valid device types."""
        valid_devices = ["npu", "cpu", "gpu"]
        for device in valid_devices:
            is_valid, error = validate_device_type(device)
            assert is_valid == True
            assert error == ""

    def test_invalid_device_type(self):
        """Test invalid device type."""
        is_valid, error = validate_device_type("invalid_device")
        assert is_valid == False
        assert "不支持的设备类型" in error


class TestArgumentValidator:
    """Test ArgumentValidator class."""

    def test_positive_int(self):
        """Test positive integer validation."""
        # Valid positive integers
        assert ArgumentValidator.positive_int("1") == 1
        assert ArgumentValidator.positive_int("42") == 42

        # Invalid values
        with pytest.raises(Exception):  # argparse.ArgumentTypeError
            ArgumentValidator.positive_int("0")
        with pytest.raises(Exception):
            ArgumentValidator.positive_int("-1")
        with pytest.raises(Exception):
            ArgumentValidator.positive_int("invalid")

    def test_positive_float(self):
        """Test positive float validation."""
        # Valid positive floats
        assert ArgumentValidator.positive_float("1.0") == 1.0
        assert ArgumentValidator.positive_float("3.14") == 3.14

        # Invalid values
        with pytest.raises(Exception):
            ArgumentValidator.positive_float("0.0")
        with pytest.raises(Exception):
            ArgumentValidator.positive_float("-1.5")
        with pytest.raises(Exception):
            ArgumentValidator.positive_float("invalid")

    def test_file_exists(self):
        """Test file exists validation."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Valid existing file
            result = ArgumentValidator.file_exists(tmp_path)
            assert result == tmp_path

            # Invalid non-existing file
            with pytest.raises(Exception):
                ArgumentValidator.file_exists("nonexistent.txt")

        finally:
            os.unlink(tmp_path)

    def test_yaml_file(self):
        """Test YAML file validation."""
        valid_yaml = "test: value"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp:
            tmp.write(valid_yaml)
            tmp_path = tmp.name

        try:
            # Valid YAML file
            result = ArgumentValidator.yaml_file(tmp_path)
            assert result == tmp_path

            # Invalid YAML file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp2:
                tmp2.write("invalid: [")
                tmp2_path = tmp2.name

            try:
                with pytest.raises(Exception):
                    ArgumentValidator.yaml_file(tmp2_path)
            finally:
                os.unlink(tmp2_path)

        finally:
            os.unlink(tmp_path)

    def test_output_path_validation(self):
        """Test output path validation."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = os.path.join(tmp_dir, "test_output.bpu")

            # Valid output path
            result = ArgumentValidator.output_path(output_path)
            assert result == output_path


if __name__ == "__main__":
    pytest.main([__file__])