#!/usr/bin/env python3
"""
Parameter Optimization Example

This example demonstrates how to use the NPU Converter Parameter Optimization System
to optimize parameters for various AI models.

Author: Story 2.6 Implementation
Version: 1.0.0
Date: 2025-10-28
"""

import sys
import logging
from pathlib import Path
from dataclasses import asdict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from npu_converter.optimization import (
    ParameterOptimizer,
    ModelAnalyzer,
    OptimizationHistory,
    TradeOffStrategy,
    TradeOffConfig,
    OptimizationStrategy,
    OptimizationReportGenerator,
    PreprocessingOptimizer,
    PreprocessingOptimizationConfig
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_basic_optimization():
    """Example 1: Basic parameter optimization"""
    logger.info("=" * 60)
    logger.info("Example 1: Basic Parameter Optimization")
    logger.info("=" * 60)

    # Initialize optimizer
    optimizer = ParameterOptimizer(verbose=True)
    analyzer = ModelAnalyzer()

    # Define parameter space
    param_space = {
        'quantization_bits': {
            'type': 'choice',
            'values': [8, 16]
        },
        'learning_rate': {
            'type': 'float',
            'bounds': [1e-5, 1e-2]
        },
        'batch_size': {
            'type': 'choice',
            'values': [16, 32, 64]
        }
    }

    # Simulate model (in production, would be actual ONNX model)
    model = "path/to/sensevoice_model.onnx"

    # Run optimization
    result = optimizer.optimize(
        model=model,
        param_space=param_space,
        strategy=OptimizationStrategy.BAYESIAN
    )

    logger.info(f"Optimization completed!")
    logger.info(f"Best parameters: {result.best_params}")
    logger.info(f"Best metrics: {result.best_metrics}")
    logger.info(f"Improvement: {result.improvement_percentage:.1f}%")

    return result


def example_with_tradeoff():
    """Example 2: Optimization with trade-off strategy"""
    logger.info("\n" + "=" * 60)
    logger.info("Example 2: Optimization with Trade-off Strategy")
    logger.info("=" * 60)

    # Initialize optimizer with trade-off calculator
    optimizer = ParameterOptimizer(verbose=True)

    # Define parameter space
    param_space = {
        'quantization_bits': {
            'type': 'choice',
            'values': [8, 16]
        },
        'batch_size': {
            'type': 'choice',
            'values': [8, 16, 32]
        }
    }

    # Use quality-first trade-off strategy
    tradeoff_config = TradeOffConfig.from_strategy(
        TradeOffStrategy.QUALITY_FIRST
    )

    # Simulate model
    model = "path/to/vits_cantonese_model.onnx"

    # Run optimization
    result = optimizer.optimize(
        model=model,
        param_space=param_space,
        strategy=OptimizationStrategy.GRID_SEARCH,
        tradeoff_config=tradeoff_config
    )

    logger.info(f"Optimization completed with quality-first strategy!")
    logger.info(f"Best parameters: {result.best_params}")

    return result


def example_model_analysis():
    """Example 3: Model analysis and parameter recommendation"""
    logger.info("\n" + "=" * 60)
    logger.info("Example 3: Model Analysis and Recommendations")
    logger.info("=" * 60)

    # Initialize analyzer
    analyzer = ModelAnalyzer()

    # Analyze a model
    model = "path/to/piper_vits_model.onnx"
    characteristics = analyzer.analyze_model(model)

    logger.info(f"Model type: {characteristics.model_type.value}")
    logger.info(f"Model size: {characteristics.model_size:,} parameters")
    logger.info(f"Complexity score: {characteristics.complexity_score:.2f}")
    logger.info(f"Recommended quantization: {characteristics.recommended_quantization}-bit")

    # Get parameter recommendations
    param_space = {
        'quantization_bits': {'type': 'choice', 'values': [8, 16]},
        'learning_rate': {'type': 'float', 'bounds': [1e-5, 1e-2]}
    }

    recommendations = analyzer.recommend_parameters(param_space, characteristics)
    logger.info(f"Recommended parameters: {recommendations}")

    return characteristics


def example_history_management():
    """Example 4: History management and rollback"""
    logger.info("\n" + "=" * 60)
    logger.info("Example 4: History Management and Rollback")
    logger.info("=" * 60)

    # Initialize history manager
    history = OptimizationHistory(auto_save=True)

    # Record optimization results
    version1 = history.record(
        params={'quantization_bits': 16, 'batch_size': 32},
        metrics={'accuracy': 0.95, 'latency': 100.0},
        score=0.15,
        strategy='bayesian',
        objective='balanced',
        model_characteristics={'model_type': 'asr'},
        execution_time=10.5
    )

    version2 = history.record(
        params={'quantization_bits': 8, 'batch_size': 64},
        metrics={'accuracy': 0.93, 'latency': 80.0},
        score=0.12,
        strategy='bayesian',
        objective='balanced',
        model_characteristics={'model_type': 'asr'},
        execution_time=8.2
    )

    logger.info(f"Recorded version: {version1}")
    logger.info(f"Recorded version: {version2}")

    # Compare versions
    comparison = history.compare_versions(version1, version2)
    logger.info(f"Comparison: {comparison}")

    # Get history statistics
    stats = history.get_statistics()
    logger.info(f"History statistics: {stats}")

    return history


def example_preprocessing_optimization():
    """Example 5: Preprocessing parameter optimization"""
    logger.info("\n" + "=" * 60)
    logger.info("Example 5: Preprocessing Optimization")
    logger.info("=" * 60)

    # Initialize preprocessing optimizer
    preprocessor = PreprocessingOptimizer()

    # Get model characteristics
    analyzer = ModelAnalyzer()
    model = "path/to/sensevoice_asr.onnx"
    characteristics = analyzer.analyze_model(model)

    # Optimize preprocessing parameters
    params = preprocessor.optimize_preprocessing(
        model_characteristics=asdict(characteristics),
        target_metric="compatibility"
    )

    logger.info(f"Optimized preprocessing parameters: {params}")

    # Validate parameters
    errors = preprocessor.validate_preprocessing_params(
        params,
        characteristics.model_type.value
    )

    if errors:
        logger.warning(f"Validation errors: {errors}")
    else:
        logger.info("Preprocessing parameters are valid!")

    return params


def example_report_generation():
    """Example 6: Report generation"""
    logger.info("\n" + "=" * 60)
    logger.info("Example 6: Report Generation")
    logger.info("=" * 60)

    # Run a quick optimization
    optimizer = ParameterOptimizer(verbose=False)
    param_space = {
        'quantization_bits': {'type': 'choice', 'values': [8, 16]},
        'batch_size': {'type': 'choice', 'values': [16, 32]}
    }

    result = optimizer.optimize(
        model="path/to/test_model.onnx",
        param_space=param_space,
        strategy=OptimizationStrategy.RANDOM,
        max_iterations=10
    )

    # Generate report
    generator = OptimizationReportGenerator(output_dir="./examples/reports")

    # Generate HTML report
    html_path = generator.generate_report(
        result=result,
        format="html",
        include_charts=True,
        include_recommendations=True
    )
    logger.info(f"HTML report generated: {html_path}")

    # Generate JSON report
    json_path = generator.generate_report(
        result=result,
        format="json",
        include_charts=False,
        include_recommendations=True
    )
    logger.info(f"JSON report generated: {json_path}")

    # Generate Markdown report
    md_path = generator.generate_report(
        result=result,
        format="markdown",
        include_charts=False,
        include_recommendations=True
    )
    logger.info(f"Markdown report generated: {md_path}")

    return html_path, json_path, md_path


def example_comprehensive():
    """Example 7: Comprehensive optimization workflow"""
    logger.info("\n" + "=" * 60)
    logger.info("Example 7: Comprehensive Optimization Workflow")
    logger.info("=" * 60)

    # Initialize all components
    analyzer = ModelAnalyzer()
    optimizer = ParameterOptimizer()
    history = OptimizationHistory()
    preprocessor = PreprocessingOptimizer()
    generator = OptimizationReportGenerator()

    # Step 1: Analyze model
    model = "path/to/complete_model.onnx"
    characteristics = analyzer.analyze_model(model)
    logger.info(f"Model analysis complete: {characteristics.model_type.value}")

    # Step 2: Optimize preprocessing
    preproc_params = preprocessor.optimize_preprocessing(
        model_characteristics=asdict(characteristics)
    )
    logger.info(f"Preprocessing optimized")

    # Step 3: Define parameter space
    param_space = {
        'quantization_bits': {'type': 'choice', 'values': [8, 16]},
        'batch_size': {'type': 'choice', 'values': [16, 32, 64]},
        'learning_rate': {'type': 'float', 'bounds': [1e-5, 1e-2]}
    }

    # Step 4: Run optimization with balanced strategy
    tradeoff_config = TradeOffConfig.from_strategy(TradeOffStrategy.BALANCED)
    result = optimizer.optimize(
        model=model,
        param_space=param_space,
        strategy=OptimizationStrategy.BAYESIAN,
        tradeoff_config=tradeoff_config
    )

    logger.info(f"Optimization complete: {result.improvement_percentage:.1f}% improvement")

    # Step 5: Record in history
    version = history.record(
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
        model_characteristics=asdict(result.model_characteristics),
        execution_time=result.execution_time,
        recommendations=result.recommendations
    )
    logger.info(f"Recorded to history: {version}")

    # Step 6: Generate report
    report_path = generator.generate_report(
        result=result,
        format="html",
        include_charts=True,
        include_recommendations=True
    )
    logger.info(f"Report generated: {report_path}")

    # Step 7: Display summary
    logger.info("\n" + "=" * 60)
    logger.info("Optimization Summary")
    logger.info("=" * 60)
    logger.info(f"Model Type: {characteristics.model_type.value}")
    logger.info(f"Best Parameters: {result.best_params}")
    logger.info(f"Accuracy: {result.best_metrics.accuracy:.2%}")
    logger.info(f"Latency: {result.best_metrics.latency:.1f} ms")
    logger.info(f"Improvement: {result.improvement_percentage:.1f}%")
    logger.info(f"Report: {report_path}")

    return result


def main():
    """Run all examples"""
    logger.info("\n" + "=" * 60)
    logger.info("NPU Converter Parameter Optimization Examples")
    logger.info("=" * 60)

    try:
        # Run examples
        example_basic_optimization()
        example_with_tradeoff()
        example_model_analysis()
        example_history_management()
        example_preprocessing_optimization()
        example_report_generation()
        example_comprehensive()

        logger.info("\n" + "=" * 60)
        logger.info("All examples completed successfully!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Error running examples: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
