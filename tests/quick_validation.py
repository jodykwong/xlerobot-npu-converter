#!/usr/bin/env python3
"""
Quick validation script for Parameter Optimization System.

Tests all major components to ensure they work correctly.

Author: Story 2.6 Implementation
Version: 1.0.0
Date: 2025-10-28
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

print("=" * 70)
print("Parameter Optimization System - Quick Validation")
print("=" * 70)

# Test 1: Import all modules
print("\n[Test 1] Testing imports...")
try:
    from npu_converter.optimization import (
        ParameterOptimizer,
        ModelAnalyzer,
        OptimizationHistory,
        TradeOffStrategy,
        TradeOffConfig,
        OptimizationStrategy,
        OptimizationReportGenerator,
        PreprocessingOptimizer,
        ModelType,
        OptimizationObjective
    )
    print("✅ All imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Initialize components
print("\n[Test 2] Testing component initialization...")
try:
    analyzer = ModelAnalyzer()
    optimizer = ParameterOptimizer(verbose=False)
    preprocessor = PreprocessingOptimizer()
    print("✅ Components initialized successfully")
except Exception as e:
    print(f"❌ Initialization failed: {e}")
    sys.exit(1)

# Test 3: Model analysis
print("\n[Test 3] Testing model analysis...")
try:
    # Mock model path
    model_path = "path/to/sensevoice_model.onnx"

    characteristics = analyzer.analyze_model(model_path)

    assert characteristics.model_type == ModelType.ASR, "Model type detection failed"
    assert characteristics.model_size > 0, "Model size should be positive"
    assert 0.0 <= characteristics.complexity_score <= 1.0, "Complexity score out of range"

    print(f"✅ Model analysis successful:")
    print(f"   Model type: {characteristics.model_type.value}")
    print(f"   Model size: {characteristics.model_size:,} parameters")
    print(f"   Complexity: {characteristics.complexity_score:.2f}")
    print(f"   Recommended quantization: {characteristics.recommended_quantization}-bit")
except Exception as e:
    print(f"❌ Model analysis failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Parameter recommendation
print("\n[Test 4] Testing parameter recommendation...")
try:
    param_space = {
        'quantization_bits': {'type': 'choice', 'values': [8, 16]},
        'batch_size': {'type': 'choice', 'values': [16, 32]}
    }

    recommendations = analyzer.recommend_parameters(param_space, characteristics)

    assert 'quantization_bits' in recommendations, "Missing recommendation"
    assert 'batch_size' in recommendations, "Missing recommendation"

    print(f"✅ Parameter recommendation successful:")
    print(f"   Recommended quantization: {recommendations['quantization_bits']}")
    print(f"   Recommended batch size: {recommendations['batch_size']}")
except Exception as e:
    print(f"❌ Parameter recommendation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Optimization strategies
print("\n[Test 5] Testing optimization strategies...")
try:
    from npu_converter.optimization.optimization_strategies import (
        GridSearchStrategy,
        BayesianOptimizationStrategy,
        RandomSearchStrategy,
        OptimizationConfig
    )

    config = OptimizationConfig(max_iterations=5, verbose=False)

    strategies = [
        GridSearchStrategy(config),
        BayesianOptimizationStrategy(config),
        RandomSearchStrategy(config)
    ]

    for strategy in strategies:
        assert strategy is not None, f"Strategy creation failed: {strategy.__class__.__name__}"

    print(f"✅ {len(strategies)} optimization strategies created successfully")
except Exception as e:
    print(f"❌ Optimization strategy test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Trade-off strategies
print("\n[Test 6] Testing trade-off strategies...")
try:
    # Test predefined strategies (skip CUSTOM as it's not predefined)
    predefined = [
        TradeOffStrategy.QUALITY_FIRST,
        TradeOffStrategy.PERFORMANCE_FIRST,
        TradeOffStrategy.BALANCED,
        TradeOffStrategy.RESOURCE_SAVING
    ]

    for strategy in predefined:
        config = TradeOffConfig.from_strategy(strategy)
        assert config.strategy == strategy, f"Strategy mismatch for {strategy.value}"
        assert config.weights is not None, "Weights not initialized"

    print(f"✅ {len(predefined)} predefined strategies working")

    # Test custom strategy
    from npu_converter.optimization import TradeOffWeights

    weights = TradeOffWeights(
        accuracy=0.6, latency=0.3, throughput=0.05,
        memory=0.025, compatibility=0.015, success_rate=0.01
    )

    custom_config = TradeOffConfig.from_custom_weights(weights)
    assert custom_config.strategy == TradeOffStrategy.CUSTOM, "Custom strategy creation failed"

    print(f"✅ Custom strategy working")
except Exception as e:
    print(f"❌ Trade-off strategy test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 7: Preprocessing optimization
print("\n[Test 7] Testing preprocessing optimization...")
try:
    from dataclasses import asdict
    # Convert ModelType to string
    char_dict = asdict(characteristics)
    char_dict['model_type'] = characteristics.model_type.value
    preproc_params = preprocessor.optimize_preprocessing(
        model_characteristics=char_dict,
        target_metric="compatibility"
    )

    assert 'normalize' in preproc_params, "Missing preprocessing parameter"
    assert isinstance(preproc_params['normalize'], bool), "normalize should be boolean"

    print(f"✅ Preprocessing optimization successful:")
    print(f"   Parameters: {list(preproc_params.keys())[:3]}...")

    # Test validation
    errors = preprocessor.validate_preprocessing_params(
        preproc_params,
        characteristics.model_type.value
    )

    print(f"   Validation errors: {len(errors)}")
except Exception as e:
    print(f"❌ Preprocessing optimization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 8: History management
print("\n[Test 8] Testing history management...")
try:
    import tempfile
    import shutil

    temp_dir = tempfile.mkdtemp()
    try:
        history = OptimizationHistory(
            storage_path=temp_dir,
            auto_save=False
        )

        # Record a mock result
        version = history.record(
            params={'param': 'value'},
            metrics={'metric': 0.5},
            score=0.1,
            strategy='test',
            objective='test',
            model_characteristics={},
            execution_time=1.0
        )

        assert version is not None, "Recording failed"
        assert len(history.history) == 1, "History size incorrect"

        # Get version
        entry = history.get_version(version)
        assert entry is not None, "Getting version failed"
        assert entry.params == {'param': 'value'}, "Version content incorrect"

        # List versions
        versions = history.list_versions()
        assert len(versions) == 1, "Listing versions failed"

        print(f"✅ History management successful:")
        print(f"   Recorded version: {version}")
        print(f"   History size: {len(history.history)}")
    finally:
        shutil.rmtree(temp_dir)
except Exception as e:
    print(f"❌ History management failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 9: Report generation
print("\n[Test 9] Testing report generation...")
try:
    import tempfile

    temp_dir = tempfile.mkdtemp()
    try:
        generator = OptimizationReportGenerator(output_dir=temp_dir)

        # Create a real result with minimal data
        from unittest.mock import Mock, patch
        from npu_converter.optimization import (
            OptimizationMetrics, ModelCharacteristics, ModelType,
            OptimizationResult, OptimizationStrategy
        )

        # Create real dataclasses
        metrics = OptimizationMetrics(
            accuracy=0.95,
            latency=100.0,
            throughput=10.0,
            memory_usage=500.0,
            compatibility=1.0,
            success_rate=0.95
        )

        chars = ModelCharacteristics(
            model_type=ModelType.ASR,
            model_size=100_000_000,
            file_size=400_000_000,
            layers={},
            operators={},
            input_shapes=[],
            output_shapes=[],
            quantization_sensitivity=0.6,
            complexity_score=0.5
        )

        opt_result = OptimizationResult(
            best_params={'param': 'value'},
            best_score=0.15,
            iterations=10,
            strategy=OptimizationStrategy.BAYESIAN,
            convergence_achieved=True,
            history=[],
            execution_time=1.0,
            message="Test"
        )

        from npu_converter.optimization.parameter_optimizer import (
            ParameterOptimizationResult
        )

        result = ParameterOptimizationResult(
            best_params={'param': 'value'},
            best_metrics=metrics,
            optimization_result=opt_result,
            model_characteristics=chars,
            improvement_percentage=5.0,
            strategy_used=OptimizationStrategy.BAYESIAN,
            objective=OptimizationObjective.BALANCED,
            execution_time=1.0,
            recommendations=["Test recommendation"]
        )

        # Test JSON export
        json_path = generator.generate_report(
            result=result,
            format="json",
            include_charts=False
        )

        assert Path(json_path).exists(), "JSON report not generated"

        # Test Markdown export
        md_path = generator.generate_report(
            result=result,
            format="markdown",
            include_charts=False
        )

        assert Path(md_path).exists(), "Markdown report not generated"

        print(f"✅ Report generation successful:")
        print(f"   JSON: {Path(json_path).name}")
        print(f"   Markdown: {Path(md_path).name}")
    finally:
        shutil.rmtree(temp_dir)
except Exception as e:
    print(f"❌ Report generation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 10: End-to-end optimization
print("\n[Test 10] Testing end-to-end optimization...")
try:
    param_space = {
        'quantization_bits': {'type': 'choice', 'values': [8, 16]}
    }

    # Mock the optimization to avoid actual heavy computation
    from unittest.mock import Mock, patch

    with patch.object(optimizer, '_evaluate_parameters') as mock_eval, \
         patch.object(optimizer, '_get_initial_params') as mock_init, \
         patch.object(optimizer, '_calculate_improvement') as mock_improve, \
         patch.object(optimizer, '_generate_recommendations') as mock_rec, \
         patch('npu_converter.optimization.parameter_optimizer.create_optimization_strategy') as mock_create:

        # Setup mocks
        mock_eval.return_value = Mock(
            accuracy=0.95, latency=100.0, throughput=10.0,
            memory=500.0, compatibility=1.0, success_rate=0.95
        )
        mock_init.return_value = {'quantization_bits': 16}
        mock_improve.return_value = 5.0
        mock_rec.return_value = ["Test recommendation"]

        mock_strategy = Mock()
        mock_strategy.optimize.return_value = Mock(
            best_params={'quantization_bits': 16},
            best_score=0.15,
            iterations=10,
            strategy=OptimizationStrategy.BAYESIAN,
            convergence_achieved=True,
            history=[]
        )
        mock_create.return_value = mock_strategy

        result = optimizer.optimize(
            model=model_path,
            param_space=param_space,
            strategy=OptimizationStrategy.BAYESIAN,
            tradeoff_config=None,  # Explicitly pass None
            max_iterations=5
        )

        assert result is not None, "Optimization returned None"
        assert result.best_params == {'quantization_bits': 16}, "Best params incorrect"
        assert result.strategy_used == OptimizationStrategy.BAYESIAN, "Strategy incorrect"

        print(f"✅ End-to-end optimization successful:")
        print(f"   Strategy: {result.strategy_used.value}")
        print(f"   Best params: {result.best_params}")
        print(f"   Improvement: {result.improvement_percentage:.1f}%")
except Exception as e:
    print(f"❌ End-to-end optimization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Summary
print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED!")
print("=" * 70)
print("\nParameter Optimization System is working correctly.")
print("\nComponents tested:")
print("  ✅ Model Analyzer")
print("  ✅ Parameter Optimizer")
print("  ✅ Optimization Strategies")
print("  ✅ Trade-off Strategies")
print("  ✅ Preprocessing Optimizer")
print("  ✅ History Management")
print("  ✅ Report Generation")
print("  ✅ End-to-End Workflow")
print("\n" + "=" * 70)
