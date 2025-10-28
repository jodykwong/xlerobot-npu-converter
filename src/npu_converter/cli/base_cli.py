#!/usr/bin/env python3
"""
Base CLI Module

This module defines the abstract base class for all CLI components in Story 1.6.
It provides a foundation for command-line interface implementation with integration
to Story 1.4's configuration management system and Story 1.5's conversion flows.

Key Features:
- Abstract base class for CLI commands
- Integration with ConfigurationManager
- Output formatting and logging integration
- Error handling and user feedback
- Support for verbose/quiet output modes
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import sys
import logging
import argparse
from enum import Enum

try:
    from rich.console import Console
    from rich.text import Text
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from ..config.manager import ConfigurationManager
from ..core.models.config_model import ConfigModel
from ..core.models.progress_model import ProgressModel
from ..converters.base_conversion_flow import BaseConversionFlow

logger = logging.getLogger(__name__)


class OutputMode(Enum):
    """Enumeration of output modes for CLI."""

    NORMAL = "normal"
    VERBOSE = "verbose"
    QUIET = "quiet"
    JSON = "json"


class BaseCLI(ABC):
    """
    Abstract base class for all CLI components.

    This class provides the foundation for CLI commands with integration
    to configuration management, output formatting, and error handling.

    Attributes:
        name: Name of the CLI command
        version: Version of the CLI implementation
        config_manager: Configuration manager instance
        output_mode: Current output mode
        console: Rich console instance (if available)
    """

    def __init__(
        self,
        name: str,
        version: str = "1.0.0",
        config_manager: Optional[ConfigurationManager] = None
    ) -> None:
        """
        Initialize the base CLI.

        Args:
            name: Name of the CLI command
            version: Version of the CLI implementation
            config_manager: Optional configuration manager instance
        """
        self.name = name
        self.version = version
        self.config_manager = config_manager
        self.output_mode = OutputMode.NORMAL

        # Initialize rich console if available
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None

        # Initialize logging
        self._setup_logging()

        logger.debug(f"Initialized BaseCLI: {name} v{version}")

    def _setup_logging(self) -> None:
        """Setup logging configuration for CLI."""
        # Configure logger for CLI output
        self.logger = logging.getLogger(f"cli.{self.name}")

        # Set up console handler if not already present
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stderr)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def set_output_mode(self, mode: OutputMode) -> None:
        """
        Set the output mode for the CLI.

        Args:
            mode: Output mode to set
        """
        self.output_mode = mode

        # Adjust logging level based on output mode
        if mode == OutputMode.VERBOSE:
            self.logger.setLevel(logging.DEBUG)
        elif mode == OutputMode.QUIET:
            self.logger.setLevel(logging.ERROR)
        else:
            self.logger.setLevel(logging.INFO)

        logger.debug(f"Set output mode to {mode.value} for {self.name}")

    def print_message(
        self,
        message: str,
        level: str = "info",
        show_timestamp: bool = False
    ) -> None:
        """
        Print a message to the console based on output mode.

        Args:
            message: Message to print
            level: Log level (info, warning, error, success)
            show_timestamp: Whether to show timestamp
        """
        if self.output_mode == OutputMode.QUIET and level != "error":
            return

        timestamp = f"[{self._get_timestamp()}] " if show_timestamp else ""

        if self.console and self.output_mode != OutputMode.JSON:
            # Use rich formatting
            if level == "error":
                self.console.print(f"{timestamp}❌ {message}", style="bold red")
            elif level == "warning":
                self.console.print(f"{timestamp}⚠️  {message}", style="bold yellow")
            elif level == "success":
                self.console.print(f"{timestamp}✅ {message}", style="bold green")
            elif level == "info":
                self.console.print(f"{timestamp}ℹ️  {message}", style="blue")
            else:
                self.console.print(f"{timestamp}{message}")
        else:
            # Plain text output
            prefix = {
                "error": "❌ ",
                "warning": "⚠️  ",
                "success": "✅ ",
                "info": "ℹ️  "
            }.get(level, "")

            print(f"{timestamp}{prefix}{message}")

    def print_json(self, data: Dict[str, Any]) -> None:
        """
        Print data as JSON.

        Args:
            data: Data to print as JSON
        """
        import json
        print(json.dumps(data, indent=2, ensure_ascii=False))

    def print_progress(self, message: str, spinner: bool = True) -> None:
        """
        Print a progress message.

        Args:
            message: Progress message
            spinner: Whether to show spinner
        """
        if self.output_mode == OutputMode.QUIET:
            return

        if self.console and spinner:
            # Use rich spinner
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
                transient=True
            ) as progress:
                task = progress.add_task(message, total=None)
                # This is a transient spinner, will disappear when context exits
        else:
            self.print_message(message, "info")

    def _get_timestamp(self) -> str:
        """Get current timestamp string."""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")

    def validate_file_exists(self, file_path: Union[str, Path]) -> bool:
        """
        Validate that a file exists.

        Args:
            file_path: Path to validate

        Returns:
            bool: True if file exists
        """
        path = Path(file_path)
        if not path.exists():
            self.print_message(f"文件不存在: {file_path}", "error")
            return False
        if not path.is_file():
            self.print_message(f"路径不是文件: {file_path}", "error")
            return False
        return True

    def validate_directory_exists(self, dir_path: Union[str, Path]) -> bool:
        """
        Validate that a directory exists.

        Args:
            dir_path: Directory path to validate

        Returns:
            bool: True if directory exists
        """
        path = Path(dir_path)
        if not path.exists():
            self.print_message(f"目录不存在: {dir_path}", "error")
            return False
        if not path.is_dir():
            self.print_message(f"路径不是目录: {dir_path}", "error")
            return False
        return True

    def create_directory_if_not_exists(self, dir_path: Union[str, Path]) -> bool:
        """
        Create directory if it doesn't exist.

        Args:
            dir_path: Directory path to create

        Returns:
            bool: True if directory exists or was created successfully
        """
        path = Path(dir_path)
        try:
            path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            self.print_message(f"创建目录失败 {dir_path}: {e}", "error")
            return False

    @abstractmethod
    def create_parser(self) -> argparse.ArgumentParser:
        """
        Create the argument parser for this CLI command.

        Returns:
            argparse.ArgumentParser: Configured argument parser
        """
        pass

    @abstractmethod
    def execute(self, args: argparse.Namespace) -> int:
        """
        Execute the CLI command.

        Args:
            args: Parsed command line arguments

        Returns:
            int: Exit code (0 for success, non-zero for error)
        """
        pass

    def run(self, argv: Optional[List[str]] = None) -> int:
        """
        Run the CLI command.

        Args:
            argv: Command line arguments (defaults to sys.argv[1:])

        Returns:
            int: Exit code
        """
        try:
            parser = self.create_parser()
            args = parser.parse_args(argv)

            # Set output mode if specified
            if hasattr(args, 'verbose') and args.verbose:
                self.set_output_mode(OutputMode.VERBOSE)
            elif hasattr(args, 'quiet') and args.quiet:
                self.set_output_mode(OutputMode.QUIET)
            elif hasattr(args, 'json') and args.json:
                self.set_output_mode(OutputMode.JSON)

            # Execute the command
            return self.execute(args)

        except KeyboardInterrupt:
            self.print_message("操作被用户中断", "warning")
            return 130
        except Exception as e:
            self.print_message(f"命令执行失败: {e}", "error")
            if self.output_mode == OutputMode.VERBOSE:
                import traceback
                self.print_message(f"详细错误信息:\n{traceback.format_exc()}", "error")
            return 1

    def get_conversion_flow(
        self,
        model_type: str,
        config: Optional[ConfigModel] = None
    ) -> Optional[BaseConversionFlow]:
        """
        Get the appropriate conversion flow for a model type.

        Args:
            model_type: Type of model (sensevoice, vits_cantonese, piper_vits)
            config: Optional configuration

        Returns:
            Optional[BaseConversionFlow]: Conversion flow instance
        """
        try:
            # Import conversion flows dynamically to avoid circular imports
            from ..converters.sensevoice_flow import SenseVoiceConversionFlow
            from ..converters.vits_cantonese_flow import VITSCantoneseConversionFlow
            from ..converters.piper_vits_flow import PiperVITSConversionFlow

            flow_map = {
                "sensevoice": SenseVoiceConversionFlow,
                "vits_cantonese": VITSCantoneseConversionFlow,
                "piper_vits": PiperVITSConversionFlow
            }

            flow_class = flow_map.get(model_type.lower())
            if not flow_class:
                self.print_message(f"不支持的模型类型: {model_type}", "error")
                return None

            return flow_class(config=config)

        except ImportError as e:
            self.print_message(f"无法导入转换流程: {e}", "error")
            return None
        except Exception as e:
            self.print_message(f"创建转换流程失败: {e}", "error")
            return None

    def auto_detect_model_type(self, model_file: Union[str, Path]) -> Optional[str]:
        """
        Auto-detect model type from file name/path.

        Args:
            model_file: Path to model file

        Returns:
            Optional[str]: Detected model type
        """
        file_path = Path(model_file).name.lower()

        if "sensevoice" in file_path:
            return "sensevoice"
        elif "vits" in file_path and "cantonese" in file_path:
            return "vits_cantonese"
        elif "piper" in file_path and "vits" in file_path:
            return "piper_vits"
        elif "asr" in file_path:
            return "sensevoice"
        elif "tts" in file_path:
            return "vits_cantonese"  # Default to cantonese for TTS

        return None

    def __str__(self) -> str:
        """String representation of the CLI."""
        return f"{self.name} CLI v{self.version}"

    def __repr__(self) -> str:
        """Detailed representation of the CLI."""
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"version='{self.version}', "
            f"output_mode='{self.output_mode.value}')"
        )