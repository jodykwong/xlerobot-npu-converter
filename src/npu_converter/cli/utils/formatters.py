"""
CLI Output Formatting Utilities

This module provides output formatting functions for CLI commands.
"""

import json
import time
from typing import Any, Dict, Optional
from datetime import datetime

try:
    from rich.console import Console
    from rich.text import Text
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
    from rich.table import Table
    from rich.tree import Tree
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class OutputFormatter:
    """Output formatter with support for rich formatting."""

    def __init__(self, use_rich: bool = True):
        """
        Initialize output formatter.

        Args:
            use_rich: Whether to use rich formatting if available
        """
        self.use_rich = use_rich and RICH_AVAILABLE
        self.console = Console() if self.use_rich else None

    def format_success_message(self, message: str, details: Optional[str] = None) -> str:
        """
        Format success message.

        Args:
            message: Success message
            details: Optional details

        Returns:
            str: Formatted message
        """
        if self.console:
            result = f"✅ {message}"
            if details:
                result += f"\n{details}"
            return result
        else:
            return f"✅ {message}" + (f"\n{details}" if details else "")

    def format_error_message(self, message: str, details: Optional[str] = None) -> str:
        """
        Format error message.

        Args:
            message: Error message
            details: Optional details

        Returns:
            str: Formatted message
        """
        if self.console:
            result = f"❌ {message}"
            if details:
                result += f"\n{details}"
            return result
        else:
            return f"❌ {message}" + (f"\n{details}" if details else "")

    def format_warning_message(self, message: str, details: Optional[str] = None) -> str:
        """
        Format warning message.

        Args:
            message: Warning message
            details: Optional details

        Returns:
            str: Formatted message
        """
        if self.console:
            result = f"⚠️  {message}"
            if details:
                result += f"\n{details}"
            return result
        else:
            return f"⚠️  {message}" + (f"\n{details}" if details else "")

    def format_info_message(self, message: str, details: Optional[str] = None) -> str:
        """
        Format info message.

        Args:
            message: Info message
            details: Optional details

        Returns:
            str: Formatted message
        """
        if self.console:
            result = f"ℹ️  {message}"
            if details:
                result += f"\n{details}"
            return result
        else:
            return f"ℹ️  {message}" + (f"\n{details}" if details else "")

    def format_progress(self, current: int, total: int, message: str = "") -> str:
        """
        Format progress bar.

        Args:
            current: Current progress
            total: Total items
            message: Progress message

        Returns:
            str: Formatted progress
        """
        if total <= 0:
            return f"{message} (进行中...)"

        percentage = (current / total) * 100
        bar_length = 30
        filled_length = int(bar_length * current // total)

        if self.console:
            bar = "█" * filled_length + "░" * (bar_length - filled_length)
            return f"[{bar}] {percentage:.1f}% - {message}"
        else:
            bar = "=" * filled_length + "-" * (bar_length - filled_length)
            return f"[{bar}] {percentage:.1f}% - {message}"

    def format_table(self, headers: list, rows: list, title: Optional[str] = None) -> str:
        """
        Format table data.

        Args:
            headers: Table headers
            rows: Table rows
            title: Optional table title

        Returns:
            str: Formatted table
        """
        if self.console:
            table = Table(title=title, show_header=True, header_style="bold magenta")
            for header in headers:
                table.add_column(header, style="cyan", no_wrap=True)
            for row in rows:
                table.add_row(*[str(cell) for cell in row])

            with self.console.capture() as capture:
                self.console.print(table)
            return capture.get()
        else:
            # Simple text table
            result = []
            if title:
                result.append(f"{title}\n" + "=" * len(title))

            # Calculate column widths
            col_widths = [len(str(header)) for header in headers]
            for row in rows:
                for i, cell in enumerate(row):
                    col_widths[i] = max(col_widths[i], len(str(cell)))

            # Format header
            header_row = " | ".join(str(header).ljust(col_widths[i]) for i, header in enumerate(headers))
            result.append(header_row)
            result.append("-" * len(header_row))

            # Format rows
            for row in rows:
                row_str = " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
                result.append(row_str)

            return "\n".join(result)

    def format_json(self, data: Any, indent: int = 2) -> str:
        """
        Format data as JSON.

        Args:
            data: Data to format
            indent: JSON indentation

        Returns:
            str: Formatted JSON
        """
        try:
            return json.dumps(data, indent=indent, ensure_ascii=False, default=str)
        except Exception:
            return str(data)

    def format_timestamp(self, timestamp: Optional[datetime] = None) -> str:
        """
        Format timestamp.

        Args:
            timestamp: Datetime object (defaults to current time)

        Returns:
            str: Formatted timestamp
        """
        if timestamp is None:
            timestamp = datetime.now()
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")

    def format_duration(self, seconds: float) -> str:
        """
        Format duration in seconds to human readable format.

        Args:
            seconds: Duration in seconds

        Returns:
            str: Formatted duration
        """
        if seconds < 1:
            return f"{seconds*1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds:.0f}s"
        else:
            hours = int(seconds // 3600)
            remaining_minutes = int((seconds % 3600) // 60)
            return f"{hours}h {remaining_minutes}m"

    def format_file_size(self, size_bytes: int) -> str:
        """
        Format file size in bytes to human readable format.

        Args:
            size_bytes: Size in bytes

        Returns:
            str: Formatted file size
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"


# Global formatter instance
_default_formatter = OutputFormatter()

def format_success_message(message: str, details: Optional[str] = None) -> str:
    """Format success message using default formatter."""
    return _default_formatter.format_success_message(message, details)

def format_error_message(message: str, details: Optional[str] = None) -> str:
    """Format error message using default formatter."""
    return _default_formatter.format_error_message(message, details)

def format_warning_message(message: str, details: Optional[str] = None) -> str:
    """Format warning message using default formatter."""
    return _default_formatter.format_warning_message(message, details)

def format_info_message(message: str, details: Optional[str] = None) -> str:
    """Format info message using default formatter."""
    return _default_formatter.format_info_message(message, details)

def format_progress(current: int, total: int, message: str = "") -> str:
    """Format progress using default formatter."""
    return _default_formatter.format_progress(current, total, message)

def format_table(headers: list, rows: list, title: Optional[str] = None) -> str:
    """Format table using default formatter."""
    return _default_formatter.format_table(headers, rows, title)

def format_json(data: Any, indent: int = 2) -> str:
    """Format JSON using default formatter."""
    return _default_formatter.format_json(data, indent)

def format_timestamp(timestamp: Optional[datetime] = None) -> str:
    """Format timestamp using default formatter."""
    return _default_formatter.format_timestamp(timestamp)

def format_duration(seconds: float) -> str:
    """Format duration using default formatter."""
    return _default_formatter.format_duration(seconds)

def format_file_size(size_bytes: int) -> str:
    """Format file size using default formatter."""
    return _default_formatter.format_file_size(size_bytes)