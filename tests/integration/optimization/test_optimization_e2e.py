"""
End-to-end integration tests for parameter optimization system.

Tests complete workflows from model analysis through optimization,
reporting, and history management.

Author: Story 2.6 Implementation
Version: 1.0.0
Date: 2025-10-28
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from npu_converter.optimization import (
    ParameterOptimizer,
    ModelAnalyzer,
    OptimizationHistory,
    TradeOffStrategy,
    TradeOffConfig,
    OptimizationStrategy,
    OptimizationReportGenerator,
    PreprocessingOptimizer,
    ModelType
)


class TestSenseVoiceOptimizationE2E(unittest.TestCase):
    """End-to-end test for SenseVoice ASR model optimization."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

        # Initialize components
        self.analyzer = ModelAnalyzer()
        self.optimizer = ParameterOptimizer(
            model_analyzer=self.analyzer,
            verbose=False
        )
        self.history = OptimizationHistory(
            storage_path=self.temp_dir,
            auto_save=False
        )
        self.preprocessor = PreprocessingOptimizer()
        self.reporter = OptimizationReportGenerator(
            output_dir=self.temp_dir
        )

        # SenseVoice model path
        self.model_path = "path/to/sensevoice_asr_model.onnx"

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_complete_optimization_workflow(self):
        """Test complete optimization workflow for SenseVoice ASR model."""
        # Step 1: Analyze model
        characteristics = self.analyzer.analyze_model(self.model_path)

        self.assertEqual(characteristics.model_type, ModelType.ASR)
        self.assertGreater(characteristics.model_size, 0)
        self.assertIsInstance(characteristics.complexity_score, float)

        # Step 2: Optimize preprocessing parameters
        preproc_params = self.preprocessor.optimize_preprocessing(
            model_characteristics=characteristics.__dict__,
            target_metric="compatibility"
        )

        self.assertIsInstance(preproc_params, dict)
        self.assertIn('normalize', preproc_params)

        # Step 3: Define parameter space
        param_space = {
            'quantization_bits': {
                'type': 'choice',
                'values': [8, 16]
            },
            'batch_size': {
                'type': 'choice',
                'values': [16, 32, 64]
            },
            'learning_rate': {
                'type': 'float',
                'bounds': [1e-5, 1e-2]
            }
        }

        # Step 4: Run optimization with balanced strategy
        tradeoff_config = TradeOffConfig.from_strategy(
            TradeOffStrategy.PERFORMANCE_FIRST  # ASR needs low latency
        )

        result = self.optimizer.optimize(
            model=self.model_path,
            param_space=param_space,
            strategy=OptimizationStrategy.BAYESIAN,
            tradeoff_config=tradeoff_config,
            max_iterations=20  # Reduced for test speed
        )

        # Verify optimization results
        self.assertIsNotNone(result.best_params)
        self.assertIn('quantization_bits', result.best_params)
        self.assertIn('batch_size', result.best_params)

        # Verify metrics
        self.assertGreater(result.best_metrics.accuracy, 0.9)
        self.assertLess(result.best_metrics.latency, 200.0)
        self.assertGreater(result.best_metrics.success_rate, 0.9)

        # Verify optimization details
        self.assertGreater(result.execution_time, 0)
        self.assertGreater(result.improvement_percentage, 0)
        self.assertIsInstance(result.recommendations, list)

        # Step 5: Record in history
        version = self.history.record(
            params=result.best_params,
            metrics={
                'accuracy': result.best_metrics.accuracy,
                'latency': result.best_metrics.latency,
                'throughput': result.best_metrics.throughput,
                'memory': result.best_metrics.memory_usage,
                'compatibility': result.best_metrics.compatibility,
                'success_rate': result.best_metrics.success_rate
            },
            score=result.optimization_result.best_score,
            strategy=result.strategy_used.value,
            objective=result.objective.value,
            model_characteristics=characteristics.__dict__,
            execution_time=result.execution_time,
            recommendations=result.recommendations,
            tags=['asr', 'performance_first']
        )

        self.assertIsNotNone(version)

        # Verify history
        self.assertEqual(len(self.history.history), 1)
        self.assertEqual(self.history.current_version, version)

        # Step 6: Generate report
        report_path = self.reporter.generate_report(
            result=result,
            format="html",
            include_charts=True,
            include_recommendations=True
        )

        self.assertTrue(Path(report_path).exists())

        # Verify report content
        report_content = Path(report_path).read_text()
        self.assertIn("SenseVoice", report_content)
        self.assertIn("Performance", report_content)

    def test_optimization_with_different_strategies(self):
        """Test optimization with different strategies."""
        param_space = {
            'quantization_bits': {
                'type': 'choice',
                'values': [8, 16]
            },
            'batch_size': {
                'type': 'choice',
                'values': [16, 32]
            }
        }

        strategies_to_test = [
            OptimizationStrategy.BAYESIAN,
            OptimizationStrategy.GRID_SEARCH,
            OptimizationStrategy.RANDOM
        ]

        results = []

        for strategy in strategies_to_test:
            result = self.optimizer.optimize(
                model=self.model_path,
                param_space=param_space,
                strategy=strategy,
                max_iterations=10
            )

            results.append(result)

            # Verify each result
            self.assertIsNotNone(result.best_params)
            self.assertEqual(result.strategy_used, strategy)

        # All results should have valid parameters
        for result in results:
            self.assertGreater(result.best_metrics.accuracy, 0.9)

    def test_tradeoff_strategies_comparison(self):
        """Test different trade-off strategies."""
        param_space = {
            'quantization_bits': {
                'type': 'choice',
                'values': [8, 16]
            }
        }

        strategies = [
            TradeOffStrategy.QUALITY_FIRST,
            TradeOffStrategy.PERFORMANCE_FIRST,
            TradeOffStrategy.BALANCED,
            TradeOffStrategy.RESOURCE_SAVING
        ]

        results = []

        for strategy in strategies:
            tradeoff_config = TradeOffConfig.from_strategy(strategy)

            result = self.optimizer.optimize(
                model=self.model_path,
                param_space=param_space,
                strategy=OptimizationStrategy.RANDOM,
                tradeoff_config=tradeoff_config,
                max_iterations=5
            )

            results.append(result)

        # All strategies should produce valid results
        for result in results:
            self.assertIsNotNone(result.best_params)

    def test_history_comparison_and_rollback(self):
        """Test history comparison and rollback functionality."""
        param_space = {
            'quantization_bits': {
                'type': 'choice',
                'values': [8, 16]
            }
        }

        # Run first optimization
        result1 = self.optimizer.optimize(
            model=self.model_path,
            param_space=param_space,
            strategy=OptimizationStrategy.RANDOM,
            max_iterations=5
        )

        version1 = self.history.record(
            params=result1.best_params,
            metrics={'accuracy': result1.best_metrics.accuracy},
            score=result1.optimization_result.best_score,
            strategy=result1.strategy_used.value,
            objective=result1.objective.value,
            model_characteristics=result1.model_characteristics.__dict__,
            execution_time=result1.execution_time
        )

        # Run second optimization
        result2 = self.optimizer.optimize(
            model=self.model_path,
            param_space=param_space,
            strategy=OptimizationStrategy.RANDOM,
            max_iterations=5
        )

        version2 = self.history.record(
            params=result2.best_params,
            metrics={'accuracy': result2.best_metrics.accuracy},
            score=result2.optimization_result.best_score,
            strategy=result2.strategy_used.value,
            objective=result2.objective.value,
            model_characteristics=result2.model_characteristics.__dict__,
            execution_time=result2.execution_time
        )

        # Compare versions
        comparison = self.history.compare_versions(version1, version2)

        self.assertIsNotNone(comparison)
        self.assertEqual(comparison.version1, version1)
        self.assertEqual(comparison.version2, version2)

        # Test rollback
        rollback_result = self.history.rollback(version1)
        self.assertTrue(rollback_result)

    def test_multiple_model_types(self):
        """Test optimization with different model types."""
        model_types = {
            "SenseVoice ASR": "path/to/sensevoice_model.onnx",
            "VITS TTS": "path/to/vits_model.onnx",
            "Piper VITS": "path/to/piper_vits_model.onnx",
            "Vision Model": "path/to/resnet_model.onnx"
        }

        param_space = {
            'quantization_bits': {
                'type': 'choice',
                'values': [8, 16]
            }
        }

        for model_name, model_path in model_types.items():
            result = self.optimizer.optimize(
                model=model_path,
                param_space=param_space,
                strategy=OptimizationStrategy.RANDOM,
                max_iterations=5
            )

            self.assertIsNotNone(result.best_params)
            self.assertGreater(result.best_metrics.accuracy, 0.85)

    def test_preprocessing_optimization_for_different_models(self):
        """Test preprocessing optimization for different model types."""
        model_characteristics = {
            "SenseVoice ASR": {
                'model_type': 'asr',
                'complexity_score': 0.6,
                'has_conv_layers': True
            },
            "VITS TTS": {
                'model_type': 'tts',
                'complexity_score': 0.7,
                'has_conv_layers': True
            },
            "Vision Model": {
                'model_type': 'vision',
                'complexity_score': 0.5,
                'has_conv_layers': True
            }
        }

        for model_name, characteristics in model_characteristics.items():
            params = self.preprocessor.optimize_preprocessing(
                model_characteristics=characteristics,
                target_metric="compatibility"
            )

            self.assertIsInstance(params, dict)
            self.assertIn('normalize', params)

            # Validate parameters
            errors = self.preprocessor.validate_preprocessing_params(
                params,
                characteristics['model_type']
            )

            self.assertEqual(len(errors), 0, f"Validation errors for {model_name}: {errors}")


class TestVITSOptimizationE2E(unittest.TestCase):
    """End-to-end test for VITS TTS model optimization."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

        self.analyzer = ModelAnalyzer()
        self.optimizer = ParameterOptimizer(verbose=False)
        self.history = OptimizationHistory(storage_path=self.temp_dir, auto_save=False)
        self.reporter = OptimizationReportGenerator(output_dir=self.temp_dir)

        self.model_path = "path/to/vits_cantonese_model.onnx"

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_vits_quality_first_optimization(self):
        """Test VITS optimization with quality-first strategy."""
        # VITS TTS prioritizes quality
        param_space = {
            'quantization_bits': {
                'type': 'choice',
                'values': [8, 16]
            },
            'sample_rate': {
                'type': 'choice',
                'values': [22050, 44100]
            },
            'batch_size': {
                'type': 'choice',
                'values': [8, 16]
            }
        }

        tradeoff_config = TradeOffConfig.from_strategy(
            TradeOffStrategy.QUALITY_FIRST
        )

        result = self.optimizer.optimize(
            model=self.model_path,
            param_space=param_space,
            strategy=OptimizationStrategy.BAYESIAN,
            tradeoff_config=tradeoff_config,
            max_iterations=15
        )

        # Verify TTS-specific requirements
        self.assertGreater(result.best_metrics.accuracy, 0.93)
        self.assertGreater(result.best_metrics.compatibility, 0.9)

        # Quality-first should prefer 16-bit quantization
        self.assertEqual(result.best_params['quantization_bits'], 16)

    def test_vits_report_generation(self):
        """Test report generation for VITS optimization."""
        param_space = {
            'quantization_bits': {
                'type': 'choice',
                'values': [8, 16]
            }
        }

        result = self.optimizer.optimize(
            model=self.model_path,
            param_space=param_space,
            strategy=OptimizationStrategy.RANDOM,
            max_iterations=5
        )

        # Generate HTML report
        html_report = self.reporter.generate_report(
            result=result,
            format="html"
        )

        self.assertTrue(Path(html_report).exists())

        # Generate JSON report
        json_report = self.reporter.generate_report(
            result=result,
            format="json"
        )

        self.assertTrue(Path(json_report).exists())

        # Generate Markdown report
        md_report = self.reporter.generate_report(
            result=result,
            format="markdown"
        )

        self.assertTrue(Path(md_report).exists())


class TestPiperVITSOptimizationE2E(unittest.TestCase):
    """End-to-end test for Piper VITS model optimization."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

        self.analyzer = ModelAnalyzer()
        self.optimizer = ParameterOptimizer(verbose=False)
        self.history = OptimizationHistory(storage_path=self.temp_dir, auto_save=False)

        self.model_path = "path/to/piper_vits_model.onnx"

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_piper_balanced_optimization(self):
        """Test Piper VITS optimization with balanced strategy."""
        param_space = {
            'quantization_bits': {
                'type': 'choice',
                'values': [8, 16]
            },
            'batch_size': {
                'type': 'choice',
                'values': [16, 32, 64]
            }
        }

        tradeoff_config = TradeOffConfig.from_strategy(
            TradeOffStrategy.BALANCED
        )

        result = self.optimizer.optimize(
            model=self.model_path,
            param_space=param_space,
            strategy=OptimizationStrategy.GRID_SEARCH,
            tradeoff_config=tradeoff_config,
            max_iterations=20
        )

        # Verify balanced optimization
        self.assertGreater(result.best_metrics.accuracy, 0.92)
        self.assertGreater(result.best_metrics.throughput, 5.0)

        # Verify optimization completed
        self.assertGreater(result.optimization_result.iterations, 0)


class TestOptimizationWithHistory(unittest.TestCase):
    """Test optimization with complete history management."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.analyzer = ModelAnalyzer()
        self.optimizer = ParameterOptimizer(verbose=False)
        self.history = OptimizationHistory(
            storage_path=self.temp_dir,
            auto_save=True  # Enable auto-save for this test
        )
        self.model_path = "path/to/test_model.onnx"

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_complete_optimization_with_history(self):
        """Test complete optimization workflow with history management."""
        param_space = {
            'quantization_bits': {
                'type': 'choice',
                'values': [8, 16]
            }
        }

        # Run multiple optimizations
        for i in range(3):
            result = self.optimizer.optimize(
                model=self.model_path,
                param_space=param_space,
                strategy=OptimizationStrategy.RANDOM,
                max_iterations=5
            )

            # Record in history
            version = self.history.record(
                params=result.best_params,
                metrics={
                    'accuracy': result.best_metrics.accuracy,
                    'latency': result.best_metrics.latency
                },
                score=result.optimization_result.best_score,
                strategy=result.strategy_used.value,
                objective=result.objective.value,
                model_characteristics=result.model_characteristics.__dict__,
                execution_time=result.execution_time,
                tags=[f'run_{i+1}']
            )

            # Tag best version
            if i == 1:  # Middle run
                self.history.tag_version(version, 'best', "Best result so far")

        # Verify history
        self.assertEqual(len(self.history.history), 3)

        # Test history operations
        versions = self.history.list_versions()
        self.assertEqual(len(versions), 3)

        # Test version comparison
        comparison = self.history.compare_versions(versions[0], versions[-1])
        self.assertIsNotNone(comparison)

        # Test statistics
        stats = self.history.get_statistics()
        self.assertEqual(stats['count'], 3)
        self.assertIn('average_score', stats)

        # Test export
        exported = self.history.export_all("json")
        self.assertIsInstance(exported, str)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = ModelAnalyzer()
        self.optimizer = ParameterOptimizer(verbose=False)
        self.model_path = "path/to/test_model.onnx"

    def test_optimization_with_invalid_param_space(self):
        """Test optimization with invalid parameter space."""
        param_space = {
            'invalid_param': {
                'type': 'unknown_type',
                'values': [1, 2, 3]
            }
        }

        # Should handle gracefully
        result = self.optimizer.optimize(
            model=self.model_path,
            param_space=param_space,
            strategy=OptimizationStrategy.RANDOM,
            max_iterations=5
        )

        # Should still return a result (may be degraded)
        self.assertIsNotNone(result)

    def test_optimization_with_empty_param_space(self):
        """Test optimization with empty parameter space."""
        param_space = {}

        result = self.optimizer.optimize(
            model=self.model_path,
            param_space=param_space,
            strategy=OptimizationStrategy.RANDOM,
            max_iterations=5
        )

        # Should handle gracefully
        self.assertIsNotNone(result)

    def test_analyze_invalid_model(self):
        """Test analyzing invalid/unknown model."""
        # Should still return characteristics
        characteristics = self.analyzer.analyze_model("unknown_model.onnx")

        self.assertIsNotNone(characteristics)
        self.assertEqual(characteristics.model_type, ModelType.GENERIC)

    def test_preprocessing_with_invalid_model_type(self):
        """Test preprocessing optimization with invalid model type."""
        preprocessor = PreprocessingOptimizer()

        characteristics = {
            'model_type': 'invalid_type',
            'complexity_score': 0.5
        }

        params = preprocessor.optimize_preprocessing(
            model_characteristics=characteristics
        )

        self.assertIsInstance(params, dict)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
