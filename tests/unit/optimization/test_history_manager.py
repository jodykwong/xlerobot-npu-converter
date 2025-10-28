"""
Unit tests for OptimizationHistory.

Tests history tracking, versioning, and rollback functionality.

Author: Story 2.6 Implementation
Version: 1.0.0
Date: 2025-10-28
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import json
import yaml
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from npu_converter.optimization.history_manager import (
    OptimizationHistory,
    OptimizationEntry,
    VersionComparison,
    HistoryStorageFormat,
    VersionTag
)


class TestOptimizationEntry(unittest.TestCase):
    """Test cases for OptimizationEntry dataclass."""

    def test_entry_creation(self):
        """Test entry object creation."""
        entry = OptimizationEntry(
            version="1.0",
            timestamp=1234567890.0,
            params={'quantization_bits': 16, 'batch_size': 32},
            metrics={'accuracy': 0.95, 'latency': 100.0},
            score=0.15,
            strategy="bayesian",
            objective="balanced",
            model_characteristics={'model_type': 'asr'},
            execution_time=10.5,
            recommendations=["Rec 1", "Rec 2"],
            user_notes="Test note",
            tags=["stable", "best"]
        )

        self.assertEqual(entry.version, "1.0")
        self.assertEqual(entry.timestamp, 1234567890.0)
        self.assertEqual(entry.params, {'quantization_bits': 16, 'batch_size': 32})
        self.assertEqual(entry.metrics, {'accuracy': 0.95, 'latency': 100.0})
        self.assertEqual(entry.score, 0.15)
        self.assertEqual(entry.strategy, "bayesian")
        self.assertEqual(entry.objective, "balanced")
        self.assertEqual(entry.model_characteristics, {'model_type': 'asr'})
        self.assertEqual(entry.execution_time, 10.5)
        self.assertEqual(entry.recommendations, ["Rec 1", "Rec 2"])
        self.assertEqual(entry.user_notes, "Test note")
        self.assertEqual(entry.tags, ["stable", "best"])

    def test_entry_defaults(self):
        """Test entry with default values."""
        entry = OptimizationEntry(
            version="1.0",
            timestamp=1234567890.0,
            params={},
            metrics={},
            score=0.0,
            strategy="test",
            objective="test",
            model_characteristics={},
            execution_time=0.0
        )

        self.assertEqual(entry.recommendations, [])
        self.assertEqual(entry.user_notes, "")
        self.assertEqual(entry.tags, [])

    def test_to_dict(self):
        """Test converting entry to dictionary."""
        entry = OptimizationEntry(
            version="1.0",
            timestamp=1234567890.0,
            params={'param': 'value'},
            metrics={'metric': 0.5},
            score=0.1,
            strategy="test",
            objective="test",
            model_characteristics={},
            execution_time=1.0
        )

        data = entry.to_dict()

        self.assertIsInstance(data, dict)
        self.assertEqual(data['version'], "1.0")
        self.assertEqual(data['params'], {'param': 'value'})

    def test_from_dict(self):
        """Test creating entry from dictionary."""
        data = {
            'version': '1.0',
            'timestamp': 1234567890.0,
            'params': {'param': 'value'},
            'metrics': {'metric': 0.5},
            'score': 0.1,
            'strategy': 'test',
            'objective': 'test',
            'model_characteristics': {},
            'execution_time': 1.0,
            'recommendations': [],
            'user_notes': '',
            'tags': []
        }

        entry = OptimizationEntry.from_dict(data)

        self.assertEqual(entry.version, "1.0")
        self.assertEqual(entry.params, {'param': 'value'})

    def test_get_human_timestamp(self):
        """Test getting human-readable timestamp."""
        entry = OptimizationEntry(
            version="1.0",
            timestamp=1234567890.0,  # 2009-02-13 23:31:30 UTC
            params={},
            metrics={},
            score=0.0,
            strategy="test",
            objective="test",
            model_characteristics={},
            execution_time=0.0
        )

        timestamp_str = entry.get_human_timestamp()

        self.assertIsInstance(timestamp_str, str)
        self.assertIn("2009", timestamp_str)
        self.assertIn("23:31", timestamp_str)


class TestVersionComparison(unittest.TestCase):
    """Test cases for VersionComparison dataclass."""

    def test_comparison_creation(self):
        """Test comparison object creation."""
        comparison = VersionComparison(
            version1="1.0",
            version2="2.0",
            score_difference=0.05,
            param_differences={'batch_size': {'old': 16, 'new': 32}},
            metric_differences={'accuracy': 2.0},
            improvement_percentage=10.0,
            significant_changes=['accuracy: +2.0%']
        )

        self.assertEqual(comparison.version1, "1.0")
        self.assertEqual(comparison.version2, "2.0")
        self.assertEqual(comparison.score_difference, 0.05)
        self.assertEqual(comparison.param_differences, {'batch_size': {'old': 16, 'new': 32}})
        self.assertEqual(comparison.metric_differences, {'accuracy': 2.0})
        self.assertEqual(comparison.improvement_percentage, 10.0)
        self.assertEqual(comparison.significant_changes, ['accuracy: +2.0%'])

    def test_comparison_defaults(self):
        """Test comparison with default values."""
        comparison = VersionComparison(
            version1="1.0",
            version2="2.0",
            score_difference=0.0,
            param_differences={},
            metric_differences={},
            improvement_percentage=0.0
        )

        self.assertEqual(comparison.significant_changes, [])

    def test_to_dict(self):
        """Test converting comparison to dictionary."""
        comparison = VersionComparison(
            version1="1.0",
            version2="2.0",
            score_difference=0.05,
            param_differences={},
            metric_differences={},
            improvement_percentage=5.0
        )

        data = comparison.to_dict()

        self.assertIsInstance(data, dict)
        self.assertEqual(data['version1'], "1.0")
        self.assertEqual(data['improvement_percentage'], 5.0)


class TestOptimizationHistory(unittest.TestCase):
    """Test cases for OptimizationHistory class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.history = OptimizationHistory(
            storage_path=self.temp_dir,
            format=HistoryStorageFormat.YAML,
            auto_save=False
        )

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_init(self):
        """Test history initialization."""
        self.assertIsInstance(self.history, OptimizationHistory)
        self.assertEqual(len(self.history.history), 0)
        self.assertEqual(self.history.current_version, "0.0")

    def test_record(self):
        """Test recording optimization result."""
        version = self.history.record(
            params={'quantization_bits': 16},
            metrics={'accuracy': 0.95},
            score=0.15,
            strategy='bayesian',
            objective='balanced',
            model_characteristics={'model_type': 'asr'},
            execution_time=10.5
        )

        self.assertIsInstance(version, str)
        self.assertEqual(len(self.history.history), 1)
        self.assertEqual(self.history.current_version, version)

        entry = self.history.get_version(version)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.params, {'quantization_bits': 16})
        self.assertEqual(entry.metrics['accuracy'], 0.95)

    def test_record_multiple(self):
        """Test recording multiple results."""
        version1 = self.history.record(
            params={'param': 'value1'},
            metrics={'metric': 0.5},
            score=0.1,
            strategy='test',
            objective='test',
            model_characteristics={},
            execution_time=1.0
        )

        version2 = self.history.record(
            params={'param': 'value2'},
            metrics={'metric': 0.6},
            score=0.08,
            strategy='test',
            objective='test',
            model_characteristics={},
            execution_time=1.0
        )

        self.assertEqual(len(self.history.history), 2)
        self.assertEqual(version1, "1.1")
        self.assertEqual(version2, "2.1")

    def test_get_version(self):
        """Test getting specific version."""
        version = self.history.record(
            params={'test': 'value'},
            metrics={},
            score=0.0,
            strategy='test',
            objective='test',
            model_characteristics={},
            execution_time=0.0
        )

        entry = self.history.get_version(version)

        self.assertIsNotNone(entry)
        self.assertEqual(entry.version, version)

    def test_get_nonexistent_version(self):
        """Test getting non-existent version."""
        entry = self.history.get_version("999.0")

        self.assertIsNone(entry)

    def test_get_latest(self):
        """Test getting latest version."""
        self.assertIsNone(self.history.get_latest())

        version = self.history.record(
            params={},
            metrics={},
            score=0.0,
            strategy='test',
            objective='test',
            model_characteristics={},
            execution_time=0.0
        )

        latest = self.history.get_latest()
        self.assertIsNotNone(latest)
        self.assertEqual(latest.version, version)

    def test_list_versions(self):
        """Test listing versions."""
        self.history.record(
            params={},
            metrics={},
            score=0.0,
            strategy='test',
            objective='test',
            model_characteristics={},
            execution_time=0.0
        )

        versions = self.history.list_versions()

        self.assertIsInstance(versions, list)
        self.assertEqual(len(versions), 1)

    def test_list_versions_with_limit(self):
        """Test listing versions with limit."""
        for i in range(5):
            self.history.record(
                params={},
                metrics={},
                score=0.0,
                strategy='test',
                objective='test',
                model_characteristics={},
                execution_time=0.0
            )

        versions = self.history.list_versions(limit=3)

        self.assertEqual(len(versions), 3)

    def test_list_versions_with_tag(self):
        """Test listing versions with tag filter."""
        version1 = self.history.record(
            params={},
            metrics={},
            score=0.0,
            strategy='test',
            objective='test',
            model_characteristics={},
            execution_time=0.0,
            tags=['stable']
        )

        self.history.record(
            params={},
            metrics={},
            score=0.0,
            strategy='test',
            objective='test',
            model_characteristics={},
            execution_time=0.0,
            tags=['experimental']
        )

        stable_versions = self.history.list_versions(tag='stable')
        experimental_versions = self.history.list_versions(tag='experimental')

        self.assertEqual(len(stable_versions), 1)
        self.assertEqual(len(experimental_versions), 1)

    def test_rollback(self):
        """Test rollback to previous version."""
        version = self.history.record(
            params={'param': 'original'},
            metrics={},
            score=0.0,
            strategy='test',
            objective='test',
            model_characteristics={},
            execution_time=0.0
        )

        self.history.record(
            params={'param': 'modified'},
            metrics={},
            score=0.0,
            strategy='test',
            objective='test',
            model_characteristics={},
            execution_time=0.0
        )

        # Rollback should succeed
        result = self.history.rollback(version)
        self.assertTrue(result)

    def test_rollback_nonexistent(self):
        """Test rollback to non-existent version."""
        result = self.history.rollback("999.0")
        self.assertFalse(result)

    def test_compare_versions(self):
        """Test comparing two versions."""
        version1 = self.history.record(
            params={'param': 10},
            metrics={'accuracy': 0.90},
            score=0.20,
            strategy='test',
            objective='test',
            model_characteristics={},
            execution_time=1.0
        )

        version2 = self.history.record(
            params={'param': 20},
            metrics={'accuracy': 0.95},
            score=0.15,
            strategy='test',
            objective='test',
            model_characteristics={},
            execution_time=1.0
        )

        comparison = self.history.compare_versions(version1, version2)

        self.assertIsInstance(comparison, VersionComparison)
        self.assertEqual(comparison.version1, version1)
        self.assertEqual(comparison.version2, version2)
        self.assertIn('param', comparison.param_differences)

    def test_compare_nonexistent_versions(self):
        """Test comparing non-existent versions."""
        comparison = self.history.compare_versions("999.0", "999.1")
        self.assertIsNone(comparison)

    def test_tag_version(self):
        """Test tagging a version."""
        version = self.history.record(
            params={},
            metrics={},
            score=0.0,
            strategy='test',
            objective='test',
            model_characteristics={},
            execution_time=0.0
        )

        result = self.history.tag_version(version, VersionTag.BEST, "Best result")

        self.assertTrue(result)

        entry = self.history.get_version(version)
        self.assertIn('best', entry.tags)
        self.assertIn('Best result', entry.user_notes)

    def test_get_best_version_by_score(self):
        """Test getting best version by score."""
        self.history.record(
            params={'param': 'a'},
            metrics={},
            score=0.20,
            strategy='test',
            objective='test',
            model_characteristics={},
            execution_time=0.0
        )

        self.history.record(
            params={'param': 'b'},
            metrics={},
            score=0.10,  # Best (lowest) score
            strategy='test',
            objective='test',
            model_characteristics={},
            execution_time=0.0
        )

        self.history.record(
            params={'param': 'c'},
            metrics={},
            score=0.30,
            strategy='test',
            objective='test',
            model_characteristics={},
            execution_time=0.0
        )

        best_version = self.history.get_best_version("score")

        self.assertEqual(best_version, "2.1")

    def test_get_best_version_by_accuracy(self):
        """Test getting best version by accuracy."""
        self.history.record(
            params={'param': 'a'},
            metrics={'accuracy': 0.90},
            score=0.0,
            strategy='test',
            objective='test',
            model_characteristics={},
            execution_time=0.0
        )

        self.history.record(
            params={'param': 'b'},
            metrics={'accuracy': 0.95},  # Best accuracy
            score=0.0,
            strategy='test',
            objective='test',
            model_characteristics={},
            execution_time=0.0
        )

        best_version = self.history.get_best_version("accuracy")

        self.assertEqual(best_version, "2.1")

    def test_export_version_yaml(self):
        """Test exporting specific version to YAML."""
        version = self.history.record(
            params={'param': 'value'},
            metrics={'metric': 0.5},
            score=0.1,
            strategy='test',
            objective='test',
            model_characteristics={},
            execution_time=1.0
        )

        exported = self.history.export_version(version, "yaml")

        self.assertIsInstance(exported, str)
        # Should be valid YAML
        data = yaml.safe_load(exported)
        self.assertEqual(data['version'], version)

    def test_export_version_json(self):
        """Test exporting specific version to JSON."""
        version = self.history.record(
            params={'param': 'value'},
            metrics={'metric': 0.5},
            score=0.1,
            strategy='test',
            objective='test',
            model_characteristics={},
            execution_time=1.0
        )

        exported = self.history.export_version(version, "json")

        self.assertIsInstance(exported, str)
        # Should be valid JSON
        data = json.loads(exported)
        self.assertEqual(data['version'], version)

    def test_export_all(self):
        """Test exporting all history."""
        for i in range(3):
            self.history.record(
                params={'param': f'value{i}'},
                metrics={},
                score=0.0,
                strategy='test',
                objective='test',
                model_characteristics={},
                execution_time=0.0
            )

        exported = self.history.export_all("yaml")

        self.assertIsInstance(exported, str)
        data = yaml.safe_load(exported)
        self.assertIn('versions', data)
        self.assertIn('metadata', data)
        self.assertEqual(len(data['versions']), 3)

    def test_clear_without_confirm(self):
        """Test that clear requires confirmation."""
        self.history.record(
            params={},
            metrics={},
            score=0.0,
            strategy='test',
            objective='test',
            model_characteristics={},
            execution_time=0.0
        )

        result = self.history.clear(confirm=False)

        self.assertFalse(result)
        self.assertEqual(len(self.history.history), 1)

    def test_clear_with_confirm(self):
        """Test clearing history with confirmation."""
        self.history.record(
            params={},
            metrics={},
            score=0.0,
            strategy='test',
            objective='test',
            model_characteristics={},
            execution_time=0.0
        )

        result = self.history.clear(confirm=True)

        self.assertTrue(result)
        self.assertEqual(len(self.history.history), 0)

    def test_save_and_load(self):
        """Test saving and loading history."""
        # Add some entries
        for i in range(3):
            self.history.record(
                params={'param': f'value{i}'},
                metrics={'metric': i * 0.1},
                score=0.1 - i * 0.01,
                strategy='test',
                objective='test',
                model_characteristics={},
                execution_time=1.0
            )

        # Save
        result = self.history.save()
        self.assertTrue(result)

        # Create new history instance
        new_history = OptimizationHistory(
            storage_path=self.temp_dir,
            format=HistoryStorageFormat.YAML,
            auto_save=False
        )

        # Check loaded entries
        self.assertEqual(len(new_history.history), 3)
        self.assertEqual(new_history.current_version, "3.1")

    def test_get_statistics_empty(self):
        """Test getting statistics for empty history."""
        stats = self.history.get_statistics()

        self.assertIsInstance(stats, dict)
        self.assertEqual(stats['count'], 0)
        self.assertIsNone(stats['latest_version'])
        self.assertEqual(stats['average_score'], 0)

    def test_get_statistics_with_data(self):
        """Test getting statistics with data."""
        for i in range(3):
            self.history.record(
                params={},
                metrics={'score': 0.1 - i * 0.01},
                score=0.1 - i * 0.01,
                strategy='test',
                objective='test',
                model_characteristics={},
                execution_time=1.0 + i
            )

        stats = self.history.get_statistics()

        self.assertEqual(stats['count'], 3)
        self.assertIsNotNone(stats['latest_version'])
        self.assertAlmostEqual(stats['average_score'], 0.09, places=2)
        self.assertGreater(stats['total_execution_time'], 0)

    def test_generate_version(self):
        """Test version number generation."""
        versions = []
        for i in range(5):
            version = self.history.record(
                params={},
                metrics={},
                score=0.0,
                strategy='test',
                objective='test',
                model_characteristics={},
                execution_time=0.0
            )
            versions.append(version)

        expected_versions = ["1.1", "2.1", "3.1", "4.1", "5.1"]
        self.assertEqual(versions, expected_versions)


if __name__ == '__main__':
    unittest.main()
