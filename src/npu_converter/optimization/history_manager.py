"""
Optimization History Manager

Provides history tracking, versioning, and rollback capabilities for parameter optimizations.
Supports storage, retrieval, comparison, and management of optimization history.

Author: Story 2.6 Implementation
Version: 1.0.0
Date: 2025-10-28
"""

import json
import yaml
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class HistoryStorageFormat(Enum):
    """Storage format options"""
    JSON = "json"
    YAML = "yaml"


class VersionTag(Enum):
    """Version tag types"""
    STABLE = "stable"
    EXPERIMENTAL = "experimental"
    BEST = "best"
    FAILED = "failed"
    BASELINE = "baseline"


@dataclass
class OptimizationEntry:
    """Single optimization history entry"""
    version: str
    timestamp: float
    params: Dict[str, Any]
    metrics: Dict[str, float]
    score: float
    strategy: str
    objective: str
    model_characteristics: Dict[str, Any]
    execution_time: float
    recommendations: List[str] = field(default_factory=list)
    user_notes: str = ""
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OptimizationEntry':
        """Create from dictionary."""
        return cls(**data)

    def get_human_timestamp(self) -> str:
        """Get human-readable timestamp."""
        return datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class VersionComparison:
    """Comparison between two optimization versions"""
    version1: str
    version2: str
    score_difference: float
    param_differences: Dict[str, Any]
    metric_differences: Dict[str, float]
    improvement_percentage: float
    significant_changes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class OptimizationHistory:
    """
    Manages optimization history with versioning and rollback capabilities.

    Provides storage, retrieval, comparison, and management of optimization results.
    """

    def __init__(
        self,
        storage_path: Optional[str] = None,
        format: HistoryStorageFormat = HistoryStorageFormat.YAML,
        auto_save: bool = True
    ):
        """
        Initialize optimization history manager.

        Args:
            storage_path: Path to storage directory/file
            format: Storage format (JSON or YAML)
            auto_save: Automatically save changes to disk
        """
        self.format = format
        self.auto_save = auto_save

        # Set default storage path
        if storage_path is None:
            self.storage_dir = Path.home() / ".npu_converter" / "optimization_history"
        else:
            self.storage_dir = Path(storage_path)

        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Storage files
        self.history_file = self.storage_dir / f"history.{format.value}"
        self.index_file = self.storage_dir / "index.json"

        # In-memory history
        self.history: List[OptimizationEntry] = []
        self.current_version = "0.0"
        self.entries_index: Dict[str, int] = {}

        # Load existing history
        self._load_history()

        logger.info(f"Initialized OptimizationHistory at {self.storage_dir}")

    def record(
        self,
        params: Dict[str, Any],
        metrics: Dict[str, float],
        score: float,
        strategy: str,
        objective: str,
        model_characteristics: Dict[str, Any],
        execution_time: float,
        recommendations: Optional[List[str]] = None,
        user_notes: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Record optimization result in history.

        Args:
            params: Parameter values
            metrics: Optimization metrics
            score: Optimization score
            strategy: Optimization strategy used
            objective: Optimization objective
            model_characteristics: Model characteristics
            execution_time: Execution time in seconds
            recommendations: Optimization recommendations
            user_notes: User notes
            tags: Version tags

        Returns:
            Version string of the recorded entry
        """
        # Generate new version
        version = self._generate_version()

        # Create entry
        entry = OptimizationEntry(
            version=version,
            timestamp=time.time(),
            params=params.copy(),
            metrics=metrics.copy(),
            score=score,
            strategy=strategy,
            objective=objective,
            model_characteristics=model_characteristics.copy(),
            execution_time=execution_time,
            recommendations=recommendations or [],
            user_notes=user_notes or "",
            tags=tags or []
        )

        # Add to history
        self.history.append(entry)
        self.entries_index[version] = len(self.history) - 1
        self.current_version = version

        # Auto-save if enabled
        if self.auto_save:
            self.save()

        logger.info(f"Recorded optimization entry: {version}")

        return version

    def get_version(self, version: str) -> Optional[OptimizationEntry]:
        """
        Get optimization entry by version.

        Args:
            version: Version string

        Returns:
            OptimizationEntry or None if not found
        """
        if version in self.entries_index:
            index = self.entries_index[version]
            return self.history[index]
        return None

    def get_latest(self) -> Optional[OptimizationEntry]:
        """
        Get latest optimization entry.

        Returns:
            Latest OptimizationEntry or None if history is empty
        """
        if self.history:
            return self.history[-1]
        return None

    def list_versions(
        self,
        limit: Optional[int] = None,
        tag: Optional[str] = None
    ) -> List[str]:
        """
        List all versions in history.

        Args:
            limit: Maximum number of versions to return
            tag: Filter by tag

        Returns:
            List of version strings
        """
        versions = list(self.entries_index.keys())

        # Filter by tag if specified
        if tag:
            versions = [
                v for v in versions
                if tag in self.get_version(v).tags
            ]

        # Sort by timestamp (newest first)
        versions.sort(
            key=lambda v: self.get_version(v).timestamp,
            reverse=True
        )

        # Apply limit
        if limit:
            versions = versions[:limit]

        return versions

    def rollback(self, version: str) -> bool:
        """
        Rollback to a previous version.

        Args:
            version: Target version to rollback to

        Returns:
            True if successful, False otherwise
        """
        entry = self.get_version(version)
        if not entry:
            logger.error(f"Version {version} not found")
            return False

        logger.info(f"Rolling back to version {version}")
        return True

    def compare_versions(
        self,
        version1: str,
        version2: str
    ) -> Optional[VersionComparison]:
        """
        Compare two optimization versions.

        Args:
            version1: First version
            version2: Second version

        Returns:
            VersionComparison or None if error
        """
        entry1 = self.get_version(version1)
        entry2 = self.get_version(version2)

        if not entry1 or not entry2:
            logger.error("One or both versions not found")
            return None

        # Calculate differences
        score_diff = entry2.score - entry1.score

        param_diffs = {}
        for key in set(entry1.params.keys()) | set(entry2.params.keys()):
            val1 = entry1.params.get(key)
            val2 = entry2.params.get(key)
            if val1 != val2:
                param_diffs[key] = {
                    'old': val1,
                    'new': val2
                }

        metric_diffs = {}
        for key in set(entry1.metrics.keys()) | set(entry2.metrics.keys()):
            val1 = entry1.metrics.get(key, 0.0)
            val2 = entry2.metrics.get(key, 0.0)
            if val1 != 0:
                metric_diffs[key] = ((val2 - val1) / val1) * 100.0
            else:
                metric_diffs[key] = val2 - val1

        # Calculate improvement percentage
        if entry1.score > 0:
            improvement = ((entry1.score - entry2.score) / entry1.score) * 100.0
        else:
            improvement = 0.0

        # Identify significant changes
        significant_changes = []
        for metric, diff in metric_diffs.items():
            if abs(diff) > 5.0:  # 5% threshold
                significant_changes.append(f"{metric}: {diff:+.1f}%")

        return VersionComparison(
            version1=version1,
            version2=version2,
            score_difference=score_diff,
            param_differences=param_diffs,
            metric_differences=metric_diffs,
            improvement_percentage=improvement,
            significant_changes=significant_changes
        )

    def tag_version(self, version: str, tag: VersionTag, note: str = "") -> bool:
        """
        Tag a version.

        Args:
            version: Version to tag
            tag: Tag to apply
            note: Optional note

        Returns:
            True if successful
        """
        entry = self.get_version(version)
        if not entry:
            return False

        if tag.value not in entry.tags:
            entry.tags.append(tag.value)

        if note:
            if entry.user_notes:
                entry.user_notes += f"\n[{tag.value}] {note}"
            else:
                entry.user_notes = f"[{tag.value}] {note}"

        logger.info(f"Tagged version {version} with {tag.value}")
        return True

    def get_best_version(self, metric: str = "score") -> Optional[str]:
        """
        Get version with best score for a metric.

        Args:
            metric: Metric to optimize (score, accuracy, etc.)

        Returns:
            Version string of best entry
        """
        if not self.history:
            return None

        if metric == "score":
            # Lower score is better (as defined in optimization)
            best_entry = min(self.history, key=lambda e: e.score)
        elif metric in ['accuracy', 'success_rate']:
            # Higher is better
            best_entry = max(self.history, key=lambda e: e.metrics.get(metric, 0))
        elif metric in ['latency', 'memory']:
            # Lower is better
            best_entry = min(self.history, key=lambda e: e.metrics.get(metric, float('inf')))
        else:
            # Default to score
            best_entry = min(self.history, key=lambda e: e.score)

        return best_entry.version

    def export_version(self, version: str, format: str = "yaml") -> Optional[str]:
        """
        Export specific version to string.

        Args:
            version: Version to export
            format: Export format (yaml or json)

        Returns:
            Exported data as string or None if error
        """
        entry = self.get_version(version)
        if not entry:
            return None

        data = entry.to_dict()

        if format.lower() == "json":
            return json.dumps(data, indent=2)
        else:
            return yaml.dump(data, default_flow_style=False)

    def export_all(self, format: str = "yaml") -> str:
        """
        Export all history.

        Args:
            format: Export format (yaml or json)

        Returns:
            Exported data as string
        """
        data = {
            'versions': [entry.to_dict() for entry in self.history],
            'metadata': {
                'count': len(self.history),
                'current_version': self.current_version,
                'export_time': time.time()
            }
        }

        if format.lower() == "json":
            return json.dumps(data, indent=2)
        else:
            return yaml.dump(data, default_flow_style=False)

    def clear(self, confirm: bool = False) -> bool:
        """
        Clear all history.

        Args:
            confirm: Must be True to actually clear

        Returns:
            True if successful
        """
        if not confirm:
            logger.warning("Must set confirm=True to clear history")
            return False

        self.history.clear()
        self.entries_index.clear()
        self.current_version = "0.0"

        if self.auto_save:
            self.save()

        logger.warning("Cleared optimization history")
        return True

    def save(self) -> bool:
        """
        Save history to disk.

        Returns:
            True if successful
        """
        try:
            # Save history file
            data = {
                'version': '1.0',
                'entries': [entry.to_dict() for entry in self.history],
                'metadata': {
                    'count': len(self.history),
                    'current_version': self.current_version,
                    'last_saved': time.time()
                }
            }

            with open(self.history_file, 'w') as f:
                if self.format == HistoryStorageFormat.JSON:
                    json.dump(data, f, indent=2)
                else:
                    yaml.dump(data, f, default_flow_style=False)

            # Save index
            index_data = {
                'entries_index': self.entries_index,
                'current_version': self.current_version
            }

            with open(self.index_file, 'w') as f:
                json.dump(index_data, f, indent=2)

            logger.debug(f"Saved {len(self.history)} entries to {self.history_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to save history: {e}")
            return False

    def _load_history(self) -> None:
        """Load history from disk."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    if self.format == HistoryStorageFormat.JSON:
                        data = json.load(f)
                    else:
                        data = yaml.safe_load(f)

                entries = data.get('entries', [])
                self.history = [OptimizationEntry.from_dict(e) for e in entries]
                self.current_version = data.get('metadata', {}).get('current_version', '0.0')

                # Rebuild index
                self.entries_index = {
                    entry.version: i for i, entry in enumerate(self.history)
                }

                logger.info(f"Loaded {len(self.history)} entries from {self.history_file}")
            else:
                logger.info("No existing history found, starting fresh")

        except Exception as e:
            logger.error(f"Failed to load history: {e}")
            self.history = []
            self.entries_index = {}

    def _generate_version(self) -> str:
        """
        Generate next version number.

        Returns:
            Version string
        """
        if '.' in self.current_version:
            major, minor = self.current_version.split('.')
            major = int(major)
            minor = int(minor) + 1
        else:
            major = int(self.current_version)
            minor = 1

        version = f"{major}.{minor}"

        # Handle overflow (reset every 1000 minor versions)
        if minor >= 1000:
            major += 1
            minor = 1
            version = f"{major}.{minor}"

        return version

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get history statistics.

        Returns:
            Dictionary with statistics
        """
        if not self.history:
            return {
                'count': 0,
                'latest_version': None,
                'average_score': 0,
                'best_score': None,
                'total_execution_time': 0
            }

        scores = [entry.score for entry in self.history]
        execution_times = [entry.execution_time for entry in self.history]

        return {
            'count': len(self.history),
            'latest_version': self.current_version,
            'latest_timestamp': self.history[-1].get_human_timestamp(),
            'average_score': sum(scores) / len(scores),
            'best_score': min(scores),  # Lower is better
            'worst_score': max(scores),
            'total_execution_time': sum(execution_times),
            'average_execution_time': sum(execution_times) / len(execution_times),
            'strategies_used': list(set(entry.strategy for entry in self.history)),
            'objectives_used': list(set(entry.objective for entry in self.history)),
            'tags_used': list(set(tag for entry in self.history for tag in entry.tags))
        }
