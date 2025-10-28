#!/usr/bin/env python3
"""
Convert Command Implementation

This module implements the convert command for Story 1.6, providing
complete model conversion functionality with integration to Story 1.5's
conversion flows and Story 1.4's configuration management.

Features:
- Model type auto-detection
- Parameter validation
- Progress tracking integration
- Multiple output formats
- Error handling and user feedback
"""

import sys
import argparse
from typing import Optional, Union, Dict, Any
from pathlib import Path
import json
import logging

from ..base_cli import BaseCLI, OutputMode
from ...config.manager import ConfigurationManager
from ...core.models.conversion_model import ConversionModel
from ...core.models.config_model import ConfigModel

logger = logging.getLogger(__name__)


class ConvertCommand(BaseCLI):
    """
    Convert command implementation.

    This command handles model conversion with full integration to the
    conversion flows from Story 1.5 and configuration management from Story 1.4.
    """

    def __init__(self, config_manager: Optional[ConfigurationManager] = None):
        """
        Initialize the convert command.

        Args:
            config_manager: Optional configuration manager instance
        """
        super().__init__("convert", "1.0.0", config_manager)

    def create_parser(self) -> argparse.ArgumentParser:
        """
        Create the argument parser for the convert command.

        Returns:
            argparse.ArgumentParser: Configured argument parser
        """
        parser = argparse.ArgumentParser(
            prog="xlerobot convert",
            description="转换AI模型到NPU格式",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
使用示例:
  xlerobot convert -i model.onnx -o output.bpu
  xlerobot convert -i model.onnx -o output/ -t sensevoice --verbose
  xlerobot convert -i model.onnx -c config.yaml --json
  xlerobot convert -i model.onnx -o output.bpu -t vits_cantonese --quiet

支持的模型类型:
  sensevoice     - SenseVoice ASR模型 (语音识别)
  vits_cantonese - VITS粤语TTS模型 (语音合成)
  piper_vits     - Piper VITS TTS模型 (通用语音合成)
            """
        )

        # Required arguments
        parser.add_argument(
            "-i", "--input",
            type=str,
            required=True,
            help="输入模型文件路径 (.onnx格式)"
        )

        parser.add_argument(
            "-o", "--output",
            type=str,
            required=True,
            help="输出模型文件路径或目录"
        )

        # Optional arguments
        parser.add_argument(
            "-t", "--type",
            type=str,
            choices=["sensevoice", "vits_cantonese", "piper_vits"],
            help="模型类型 (如不指定将自动检测)"
        )

        parser.add_argument(
            "-c", "--config",
            type=str,
            help="配置文件路径 (.yaml格式)"
        )

        parser.add_argument(
            "--device",
            type=str,
            default="npu",
            choices=["npu", "cpu", "gpu"],
            help="目标设备类型 (默认: npu)"
        )

        parser.add_argument(
            "--quantize",
            action="store_true",
            help="启用模型量化"
        )

        parser.add_argument(
            "--optimize",
            action="store_true",
            help="启用模型优化"
        )

        # Output mode options
        parser.add_argument(
            "-v", "--verbose",
            action="store_true",
            help="详细输出模式"
        )

        parser.add_argument(
            "-q", "--quiet",
            action="store_true",
            help="静默模式"
        )

        parser.add_argument(
            "--json",
            action="store_true",
            help="JSON格式输出"
        )

        parser.add_argument(
            "--progress",
            action="store_true",
            help="显示详细进度信息"
        )

        return parser

    def execute(self, args: argparse.Namespace) -> int:
        """
        Execute the convert command.

        Args:
            args: Parsed command line arguments

        Returns:
            int: Exit code (0 for success, non-zero for error)
        """
        try:
            # Validate arguments
            if not self._validate_arguments(args):
                return 1

            # Load configuration
            config = self._load_configuration(args.config)
            if config is None and args.config:
                return 1

            # Detect model type if not specified
            model_type = args.type or self.auto_detect_model_type(args.input)
            if not model_type:
                self.print_message("无法检测模型类型，请使用 --type 参数指定", "error")
                return 1

            self.print_message(f"开始转换模型: {model_type}", "info")
            if self.output_mode == OutputMode.VERBOSE:
                self.print_message(f"输入文件: {args.input}")
                self.print_message(f"输出路径: {args.output}")
                self.print_message(f"配置文件: {args.config or '使用默认配置'}")

            # Prepare conversion model
            conversion_model = self._prepare_conversion_model(args, config, model_type)
            if not conversion_model:
                return 1

            # Get conversion flow
            conversion_flow = self.get_conversion_flow(model_type, config)
            if not conversion_flow:
                return 1

            # Execute conversion
            return self._execute_conversion(conversion_flow, conversion_model, args)

        except Exception as e:
            self.print_message(f"转换失败: {e}", "error")
            if self.output_mode == OutputMode.VERBOSE:
                import traceback
                self.print_message(f"详细错误信息:\n{traceback.format_exc()}", "error")
            return 1

    def _validate_arguments(self, args: argparse.Namespace) -> bool:
        """
        Validate command arguments.

        Args:
            args: Parsed command line arguments

        Returns:
            bool: True if arguments are valid
        """
        # Validate input file
        if not self.validate_file_exists(args.input):
            return False

        # Validate config file if provided
        if args.config and not self.validate_file_exists(args.config):
            return False

        # Validate output path
        output_path = Path(args.output)
        if output_path.is_file():
            # Check if output file is writable
            if not self._check_file_writable(output_path):
                return False
        else:
            # Check if parent directory exists and is writable
            if not self._check_parent_directory_writable(output_path):
                return False

        # Check for conflicting output modes
        if args.verbose and args.quiet:
            self.print_message("--verbose 和 --quiet 选项不能同时使用", "error")
            return False

        if args.json and args.quiet:
            self.print_message("--json 和 --quiet 选项不能同时使用", "error")
            return False

        return True

    def _check_file_writable(self, file_path: Path) -> bool:
        """Check if file is writable."""
        try:
            if file_path.exists():
                return file_path.is_file() and oct(file_path.stat().st_mode)[-3:] in ['666', '777', '644', '755']
            else:
                return file_path.parent.is_dir() and oct(file_path.parent.stat().st_mode)[-3:] in ['777', '755']
        except Exception:
            return False

    def _check_parent_directory_writable(self, file_path: Path) -> bool:
        """Check if parent directory is writable."""
        try:
            parent = file_path.parent if file_path.is_file() else file_path
            if not parent.exists():
                parent.mkdir(parents=True, exist_ok=True)
            return oct(parent.stat().st_mode)[-3:] in ['777', '755']
        except Exception:
            return False

    def _load_configuration(self, config_path: Optional[str]) -> Optional[ConfigModel]:
        """
        Load configuration from file.

        Args:
            config_path: Path to configuration file

        Returns:
            Optional[ConfigModel]: Loaded configuration or None
        """
        if not config_path:
            # Use default configuration
            if self.output_mode == OutputMode.VERBOSE:
                self.print_message("使用默认配置", "info")
            return None

        try:
            if not self.config_manager:
                self.config_manager = ConfigurationManager()

            config = self.config_manager.load_config(config_path)
            if self.output_mode == OutputMode.VERBOSE:
                self.print_message(f"已加载配置文件: {config_path}", "success")
            return config

        except Exception as e:
            self.print_message(f"加载配置文件失败: {e}", "error")
            return None

    def _prepare_conversion_model(
        self,
        args: argparse.Namespace,
        config: Optional[ConfigModel],
        model_type: str
    ) -> Optional[ConversionModel]:
        """
        Prepare conversion model with all parameters.

        Args:
            args: Parsed command line arguments
            config: Loaded configuration
            model_type: Detected model type

        Returns:
            Optional[ConversionModel]: Prepared conversion model
        """
        try:
            # Prepare input/output paths
            input_path = Path(args.input).resolve()
            output_path = Path(args.output).resolve()

            # If output is a directory, generate filename
            if output_path.is_dir():
                output_file = output_path / f"{input_path.stem}_converted.bpu"
            else:
                output_file = output_path

            # Create output directory if needed
            self.create_directory_if_not_exists(output_file.parent)

            # Build conversion parameters
            conversion_params = {
                "input_file": str(input_path),
                "output_file": str(output_file),
                "model_type": model_type,
                "device": args.device,
                "quantize": args.quantize,
                "optimize": args.optimize,
                "config": config,
                "verbose": self.output_mode == OutputMode.VERBOSE,
                "show_progress": args.progress or self.output_mode == OutputMode.VERBOSE
            }

            # Create conversion model
            conversion_model = ConversionModel(
                input_path=str(input_path),
                output_path=str(output_file),
                model_type=model_type,
                conversion_params=conversion_params
            )

            if self.output_mode == OutputMode.VERBOSE:
                self.print_message(f"准备转换模型: {model_type}", "info")
                self.print_message(f"输入: {conversion_model.input_path}")
                self.print_message(f"输出: {conversion_model.output_path}")

            return conversion_model

        except Exception as e:
            self.print_message(f"准备转换模型失败: {e}", "error")
            return None

    def _execute_conversion(
        self,
        conversion_flow,
        conversion_model: ConversionModel,
        args: argparse.Namespace
    ) -> int:
        """
        Execute the model conversion.

        Args:
            conversion_flow: Conversion flow instance
            conversion_model: Prepared conversion model
            args: Command line arguments

        Returns:
            int: Exit code
        """
        try:
            # Initialize conversion flow
            conversion_flow.initialize_conversion_components()

            # Set up progress callback if requested
            def progress_callback(progress_model):
                if args.progress or self.output_mode == OutputMode.VERBOSE:
                    self._display_progress(progress_model)

            # Execute conversion
            self.print_message("开始模型转换...", "info")
            if self.output_mode == OutputMode.JSON:
                self.print_json({
                    "status": "started",
                    "message": "开始模型转换",
                    "input_file": conversion_model.input_path,
                    "output_file": conversion_model.output_path,
                    "model_type": conversion_model.model_type
                })

            result = conversion_flow.convert(conversion_model, progress_callback)

            # Handle result
            if result.success:
                self.print_message(f"转换完成: {conversion_model.output_path}", "success")

                if self.output_mode == OutputMode.JSON:
                    self.print_json({
                        "status": "completed",
                        "success": True,
                        "message": "转换成功完成",
                        "output_file": result.metadata.get("output_file"),
                        "metadata": result.metadata
                    })
                elif self.output_mode == OutputMode.VERBOSE:
                    self.print_message(f"转换详情: {result.metadata}", "info")

                return 0
            else:
                self.print_message(f"转换失败: {result.message}", "error")
                if self.output_mode == OutputMode.JSON:
                    self.print_json({
                        "status": "failed",
                        "success": False,
                        "message": result.message,
                        "error": result.data
                    })
                return 1

        except Exception as e:
            self.print_message(f"转换过程异常: {e}", "error")
            if self.output_mode == OutputMode.JSON:
                self.print_json({
                    "status": "error",
                    "success": False,
                    "message": str(e),
                    "error_type": type(e).__name__
                })
            return 1

    def _display_progress(self, progress_model) -> None:
        """
        Display conversion progress.

        Args:
            progress_model: Progress model with current status
        """
        if self.output_mode == OutputMode.QUIET:
            return

        try:
            if hasattr(progress_model, 'current_step') and hasattr(progress_model, 'total_progress'):
                current_step = progress_model.current_step or "未知步骤"
                progress = progress_model.total_progress or 0

                if self.console:
                    # Use rich progress display
                    self.print_message(f"进度: {progress:.1f}% - {current_step}", "info")
                else:
                    # Simple text progress
                    bar_length = 30
                    filled_length = int(bar_length * progress / 100)
                    bar = "█" * filled_length + "░" * (bar_length - filled_length)
                    self.print_message(f"[{bar}] {progress:.1f}% - {current_step}")

        except Exception as e:
            # Fallback to simple message
            self.print_message("转换进行中...", "info")