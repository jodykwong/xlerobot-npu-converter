#!/usr/bin/env python3
"""
Tests for Convert Command - Story 1.6

This module tests the convert command implementation according to
Story 1.6 acceptance criteria.
"""

import pytest
import sys
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from npu_converter.cli.commands.convert import ConvertCommand
from npu_converter.cli.base_cli import OutputMode


class TestConvertCommand:
    """Test cases for ConvertCommand class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.convert_cmd = ConvertCommand()

    def test_init(self):
        """Test ConvertCommand initialization."""
        assert self.convert_cmd.name == "convert"
        assert self.convert_cmd.version == "1.0.0"
        assert self.convert_cmd.output_mode == OutputMode.NORMAL

    def test_create_parser(self):
        """Test argument parser creation."""
        parser = self.convert_cmd.create_parser()

        # Test that parser has required arguments
        with pytest.raises(SystemExit):
            parser.parse_args([])  # Should fail without required args

        # Test valid arguments
        args = parser.parse_args([
            "-i", "test.onnx",
            "-o", "output.bpu",
            "-t", "sensevoice"
        ])

        assert args.input == "test.onnx"
        assert args.output == "output.bpu"
        assert args.type == "sensevoice"

    def test_validate_file_exists(self):
        """Test file validation."""
        # Test existing file
        with tempfile.NamedTemporaryFile(suffix=".onnx", delete=False) as tmp:
            tmp.write(b"test content")
            tmp_path = tmp.name

        try:
            assert self.convert_cmd.validate_file_exists(tmp_path) == True
        finally:
            os.unlink(tmp_path)

        # Test non-existing file
        assert self.convert_cmd.validate_file_exists("nonexistent.onnx") == False

    def test_validate_directory_exists(self):
        """Test directory validation."""
        # Test existing directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            assert self.convert_cmd.validate_directory_exists(tmp_dir) == True

        # Test non-existing directory
        assert self.convert_cmd.validate_directory_exists("nonexistent_dir") == False

    def test_auto_detect_model_type(self):
        """Test model type auto-detection."""
        # Test different file names
        assert self.convert_cmd.auto_detect_model_type("sensevoice_model.onnx") == "sensevoice"
        assert self.convert_cmd.auto_detect_model_type("vits_cantonese_model.onnx") == "vits_cantonese"
        assert self.convert_cmd.auto_detect_model_type("piper_vits_model.onnx") == "piper_vits"
        assert self.convert_cmd.auto_detect_model_type("asr_model.onnx") == "sensevoice"
        assert self.convert_cmd.auto_detect_model_type("tts_model.onnx") == "vits_cantonese"
        assert self.convert_cmd.auto_detect_model_type("unknown_model.onnx") is None

    def test_get_conversion_flow(self):
        """Test conversion flow creation."""
        # Test valid model types
        flow = self.convert_cmd.get_conversion_flow("sensevoice")
        assert flow is not None
        assert flow.__class__.__name__ == "SenseVoiceConversionFlow"

        flow = self.convert_cmd.get_conversion_flow("vits_cantonese")
        assert flow is not None
        assert flow.__class__.__name__ == "VITSCantoneseConversionFlow"

        flow = self.convert_cmd.get_conversion_flow("piper_vits")
        assert flow is not None
        assert flow.__class__.__name__ == "PiperVITSConversionFlow"

        # Test invalid model type
        flow = self.convert_cmd.get_conversion_flow("invalid_type")
        assert flow is None

    def test_set_output_mode(self):
        """Test output mode setting."""
        # Test different modes
        self.convert_cmd.set_output_mode(OutputMode.VERBOSE)
        assert self.convert_cmd.output_mode == OutputMode.VERBOSE

        self.convert_cmd.set_output_mode(OutputMode.QUIET)
        assert self.convert_cmd.output_mode == OutputMode.QUIET

        self.convert_cmd.set_output_mode(OutputMode.JSON)
        assert self.convert_cmd.output_mode == OutputMode.JSON

    @patch('npu_converter.cli.commands.convert.ConvertCommand.validate_file_exists')
    @patch('npu_converter.cli.commands.convert.ConvertCommand.auto_detect_model_type')
    def test_execute_valid_arguments(self, mock_detect_type, mock_validate_file):
        """Test execute with valid arguments."""
        # Mock validation and detection
        mock_validate_file.return_value = True
        mock_detect_type.return_value = "sensevoice"

        # Create mock arguments
        mock_args = Mock()
        mock_args.input = "test.onnx"
        mock_args.output = "output.bpu"
        mock_args.type = "sensevoice"
        mock_args.config = None
        mock_args.device = "npu"
        mock_args.quantize = False
        mock_args.optimize = False
        mock_args.verbose = False
        mock_args.quiet = False
        mock_args.json = False
        mock_args.progress = False

        # Mock conversion flow
        with patch.object(self.convert_cmd, 'get_conversion_flow') as mock_get_flow:
            mock_flow = Mock()
            mock_get_flow.return_value = mock_flow
            mock_flow.initialize_conversion_components.return_value = None

            # Mock result
            mock_result = Mock()
            mock_result.success = True
            mock_result.message = "Conversion completed"
            mock_result.metadata = {"output_file": "output.bpu"}
            mock_flow.convert.return_value = mock_result

            # Execute
            exit_code = self.convert_cmd.execute(mock_args)
            assert exit_code == 0

    @patch('npu_converter.cli.commands.convert.ConvertCommand.validate_file_exists')
    def test_execute_invalid_input_file(self, mock_validate_file):
        """Test execute with invalid input file."""
        mock_validate_file.return_value = False

        mock_args = Mock()
        mock_args.input = "nonexistent.onnx"
        mock_args.output = "output.bpu"
        mock_args.type = "sensevoice"
        mock_args.config = None

        exit_code = self.convert_cmd.execute(mock_args)
        assert exit_code == 1

    def test_run_with_invalid_arguments(self):
        """Test run with invalid arguments."""
        # Test with no arguments
        exit_code = self.convert_cmd.run([])
        assert exit_code != 0

    def test_print_message_different_modes(self):
        """Test message printing in different output modes."""
        # Test normal mode
        self.convert_cmd.print_message("Test message", "info")

        # Test quiet mode
        self.convert_cmd.set_output_mode(OutputMode.QUIET)
        self.convert_cmd.print_message("Test message", "info")  # Should not print
        self.convert_cmd.print_message("Error message", "error")  # Should print error

        # Test verbose mode
        self.convert_cmd.set_output_mode(OutputMode.VERBOSE)
        self.convert_cmd.print_message("Verbose message", "info")

    def test_create_directory_if_not_exists(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            new_dir = Path(tmp_dir) / "new_subdir"

            # Test creating non-existing directory
            result = self.convert_cmd.create_directory_if_not_exists(new_dir)
            assert result == True
            assert new_dir.exists()

            # Test existing directory
            result = self.convert_cmd.create_directory_if_not_exists(new_dir)
            assert result == True

    def test_check_file_writable(self):
        """Test file writability check."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Test non-existing file in writable directory
            file_path = Path(tmp_dir) / "test_file.txt"
            result = self.convert_cmd._check_file_writable(file_path)
            assert result == True

    def test_check_parent_directory_writable(self):
        """Test parent directory writability check."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Test writable parent directory
            file_path = Path(tmp_dir) / "subdir" / "test_file.txt"
            result = self.convert_cmd._check_parent_directory_writable(file_path)
            assert result == True
            assert file_path.parent.exists()


class TestConvertCommandIntegration:
    """Integration tests for ConvertCommand."""

    def setup_method(self):
        """Set up test fixtures."""
        self.convert_cmd = ConvertCommand()

    def test_complete_conversion_flow_mock(self):
        """Test complete conversion flow with mocks."""
        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix=".onnx", delete=False) as input_file:
            input_file.write(b"mock onnx content")
            input_path = input_file.name

        with tempfile.TemporaryDirectory() as output_dir:
            output_path = Path(output_dir) / "output.bpu"

        try:
            # Mock the conversion process
            with patch.object(self.convert_cmd, 'get_conversion_flow') as mock_get_flow:
                mock_flow = Mock()
                mock_get_flow.return_value = mock_flow
                mock_flow.initialize_conversion_components.return_value = None

                # Mock successful conversion
                mock_result = Mock()
                mock_result.success = True
                mock_result.message = "Conversion completed successfully"
                mock_result.metadata = {"output_file": str(output_path)}
                mock_flow.convert.return_value = mock_result

                # Execute conversion
                args = [
                    "-i", input_path,
                    "-o", str(output_path),
                    "-t", "sensevoice"
                ]

                exit_code = self.convert_cmd.run(args)
                assert exit_code == 0

        finally:
            # Cleanup
            os.unlink(input_path)

    def test_error_handling(self):
        """Test error handling in conversion."""
        with patch.object(self.convert_cmd, 'get_conversion_flow') as mock_get_flow:
            mock_get_flow.return_value = None  # No flow available

            args = [
                "-i", "nonexistent.onnx",
                "-o", "output.bpu",
                "-t", "sensevoice"
            ]

            exit_code = self.convert_cmd.run(args)
            assert exit_code != 0

    def test_keyboard_interrupt_handling(self):
        """Test keyboard interrupt handling."""
        with patch.object(self.convert_cmd, 'execute') as mock_execute:
            mock_execute.side_effect = KeyboardInterrupt()

            exit_code = self.convert_cmd.run(["-i", "test.onnx", "-o", "output.bpu"])
            assert exit_code == 130

    def test_generic_exception_handling(self):
        """Test generic exception handling."""
        with patch.object(self.convert_cmd, 'execute') as mock_execute:
            mock_execute.side_effect = Exception("Test error")

            exit_code = self.convert_cmd.run(["-i", "test.onnx", "-o", "output.bpu"])
            assert exit_code == 1


if __name__ == "__main__":
    pytest.main([__file__])