"""
Unit tests for ModelAnalyzer.

Tests model analysis functionality including model type detection,
characteristic analysis, and parameter recommendations.

Author: Story 2.6 Implementation
Version: 1.0.0
Date: 2025-10-28
"""

import unittest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from npu_converter.optimization import (
    ModelAnalyzer,
    ModelCharacteristics,
    ModelType,
    ParameterRecommendation
)


class TestModelAnalyzer(unittest.TestCase):
    """Test cases for ModelAnalyzer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = ModelAnalyzer()

    def test_init(self):
        """Test analyzer initialization."""
        self.assertIsInstance(self.analyzer.model_patterns, dict)
        self.assertIsInstance(self.analyzer.operator_weights, dict)
        self.assertGreater(len(self.analyzer.model_patterns), 0)

    def test_analyze_model_sensevoice(self):
        """Test analyzing SenseVoice ASR model."""
        model = "path/to/sensevoice_asr_model.onnx"

        characteristics = self.analyzer.analyze_model(model)

        self.assertIsInstance(characteristics, ModelCharacteristics)
        self.assertEqual(characteristics.model_type, ModelType.ASR)
        self.assertGreater(characteristics.model_size, 0)
        self.assertGreater(characteristics.file_size, 0)
        self.assertIsInstance(characteristics.layers, dict)
        self.assertIsInstance(characteristics.operators, dict)
        self.assertIsInstance(characteristics.input_shapes, list)
        self.assertIsInstance(characteristics.output_shapes, list)

    def test_analyze_model_vits(self):
        """Test analyzing VITS TTS model."""
        model = "path/to/vits_cantonese_model.onnx"

        characteristics = self.analyzer.analyze_model(model)

        self.assertIsInstance(characteristics, ModelCharacteristics)
        self.assertEqual(characteristics.model_type, ModelType.TTS)

    def test_analyze_model_resnet(self):
        """Test analyzing ResNet vision model."""
        model = "path/to/resnet_vision_model.onnx"

        characteristics = self.analyzer.analyze_model(model)

        self.assertIsInstance(characteristics, ModelCharacteristics)
        self.assertEqual(characteristics.model_type, ModelType.VISION)

    def test_analyze_model_bert(self):
        """Test analyzing BERT NLP model."""
        model = "path/to/bert_nlp_model.onnx"

        characteristics = self.analyzer.analyze_model(model)

        self.assertIsInstance(characteristics, ModelCharacteristics)
        self.assertEqual(characteristics.model_type, ModelType.NLP)

    def test_analyze_model_generic(self):
        """Test analyzing unknown/generic model."""
        model = "path/to/unknown_model.onnx"

        characteristics = self.analyzer.analyze_model(model)

        self.assertIsInstance(characteristics, ModelCharacteristics)
        # Should default to GENERIC type
        self.assertEqual(characteristics.model_type, ModelType.GENERIC)

    def test_recommend_parameters(self):
        """Test parameter recommendation."""
        characteristics = ModelCharacteristics(
            model_type=ModelType.ASR,
            model_size=100_000_000,
            file_size=400_000_000,
            layers={"Conv1d": 12, "Linear": 20},
            operators={"Conv": 20, "MatMul": 60},
            input_shapes=[(None, None)],
            output_shapes=[(None, None, 14400)],
            quantization_sensitivity=0.6,
            complexity_score=0.5,
            is_transformer=True,
            has_conv_layers=True,
            has_rnn_layers=False,
            recommended_quantization=16,
            estimated_memory_usage=400.0
        )

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

        recommendations = self.analyzer.recommend_parameters(param_space, characteristics)

        self.assertIsInstance(recommendations, dict)
        self.assertIn('quantization_bits', recommendations)
        self.assertIn('learning_rate', recommendations)
        self.assertIn('batch_size', recommendations)

    def test_estimate_model_size(self):
        """Test model size estimation."""
        # Test SenseVoice model
        size = self.analyzer._estimate_model_size("sensevoice_model.onnx")
        self.assertGreater(size, 0)

        # Test VITS model
        size = self.analyzer._estimate_model_size("vits_model.onnx")
        self.assertGreater(size, 0)

        # Test ResNet model
        size = self.analyzer._estimate_model_size("resnet_model.onnx")
        self.assertGreater(size, 0)

        # Test BERT model
        size = self.analyzer._estimate_model_size("bert_model.onnx")
        self.assertGreater(size, 0)

    def test_estimate_file_size(self):
        """Test file size estimation."""
        model_size = 100_000_000  # 100M parameters
        file_size = self.analyzer._estimate_file_size(model_size)

        # File size should be approximately 4x model size (float32)
        expected_size = model_size * 4
        self.assertAlmostEqual(file_size, expected_size, delta=expected_size * 0.1)

    def test_analyze_layers_vits(self):
        """Test layer analysis for VITS model."""
        layers = self.analyzer._analyze_layers("vits_model.onnx")

        self.assertIsInstance(layers, dict)
        self.assertGreater(len(layers), 0)
        # VITS should have typical layers like ResBlock, Conv1d, Linear, LSTM
        self.assertTrue(any("ResBlock" in layer or "Conv" in layer for layer in layers.keys()))

    def test_analyze_layers_sensevoice(self):
        """Test layer analysis for SenseVoice model."""
        layers = self.analyzer._analyze_layers("sensevoice_model.onnx")

        self.assertIsInstance(layers, dict)
        self.assertGreater(len(layers), 0)

    def test_analyze_operators_vits(self):
        """Test operator analysis for VITS model."""
        operators = self.analyzer._analyze_operators("vits_model.onnx")

        self.assertIsInstance(operators, dict)
        self.assertGreater(len(operators), 0)
        # Should include common operators like Conv, MatMul, Add, etc.
        self.assertTrue(any(op in operators for op in ["Conv", "MatMul", "Add"]))

    def test_get_input_shapes_vits(self):
        """Test input shape extraction for VITS model."""
        input_shapes = self.analyzer._get_input_shapes("vits_model.onnx")

        self.assertIsInstance(input_shapes, list)
        self.assertGreater(len(input_shapes), 0)
        # VITS typically has text and audio inputs
        for shape in input_shapes:
            self.assertIsInstance(shape, tuple)

    def test_get_output_shapes_vits(self):
        """Test output shape extraction for VITS model."""
        output_shapes = self.analyzer._get_output_shapes("vits_model.onnx")

        self.assertIsInstance(output_shapes, list)
        self.assertGreater(len(output_shapes), 0)
        for shape in output_shapes:
            self.assertIsInstance(shape, tuple)

    def test_calculate_quantization_sensitivity(self):
        """Test quantization sensitivity calculation."""
        # Test ASR model
        sensitivity = self.analyzer._calculate_quantization_sensitivity(
            ModelType.ASR,
            {"LSTM": 2, "Conv": 10},
            {"LSTM": 2, "Conv": 10}
        )
        self.assertGreaterEqual(sensitivity, 0.0)
        self.assertLessEqual(sensitivity, 1.0)

        # Test TTS model (typically more sensitive)
        sensitivity = self.analyzer._calculate_quantization_sensitivity(
            ModelType.TTS,
            {"ResBlock": 16, "Conv1d": 24},
            {"Conv": 24, "MatMul": 50}
        )
        self.assertGreaterEqual(sensitivity, 0.0)
        self.assertLessEqual(sensitivity, 1.0)

    def test_calculate_complexity_score(self):
        """Test complexity score calculation."""
        complexity = self.analyzer._calculate_complexity_score(
            model_size=100_000_000,
            layers={"Conv": 50, "BatchNorm": 49, "Linear": 1},
            operators={"Conv": 50, "MatMul": 100, "Add": 75}
        )

        self.assertGreaterEqual(complexity, 0.0)
        self.assertLessEqual(complexity, 1.0)

    def test_detect_transformer(self):
        """Test transformer architecture detection."""
        # With transformer layers
        layers = {"MultiHeadAttention": 12, "LayerNormalization": 24}
        operators = {"MatMul": 200, "Add": 150}
        is_transformer = self.analyzer._detect_transformer(layers, operators)
        self.assertTrue(is_transformer)

        # Without transformer layers
        layers = {"Conv": 50, "BatchNorm": 49}
        operators = {"Conv": 50, "Add": 75}
        is_transformer = self.analyzer._detect_transformer(layers, operators)
        self.assertFalse(is_transformer)

    def test_recommend_quantization(self):
        """Test quantization recommendation."""
        # High sensitivity model should recommend 16-bit
        recommended = self.analyzer._recommend_quantization(
            ModelType.TTS,
            complexity_score=0.9,
            quantization_sensitivity=0.8
        )
        self.assertEqual(recommended, 16)

        # Low complexity ASR model might use 8-bit
        recommended = self.analyzer._recommend_quantization(
            ModelType.ASR,
            complexity_score=0.3,
            quantization_sensitivity=0.4
        )
        self.assertIn(recommended, [8, 16])

    def test_estimate_memory_usage(self):
        """Test memory usage estimation."""
        # 16-bit quantization
        memory = self.analyzer._estimate_memory_usage(
            model_size=100_000_000,
            quantization_bits=16
        )
        self.assertGreater(memory, 0)

        # 8-bit quantization should use less memory
        memory_8bit = self.analyzer._estimate_memory_usage(
            model_size=100_000_000,
            quantization_bits=8
        )
        memory_16bit = self.analyzer._estimate_memory_usage(
            model_size=100_000_000,
            quantization_bits=16
        )
        self.assertLess(memory_8bit, memory_16bit)

    def test_get_parameter_recommendation_quantization(self):
        """Test parameter recommendation for quantization."""
        param_config = {
            'type': 'choice',
            'values': [8, 16]
        }

        characteristics = ModelCharacteristics(
            model_type=ModelType.ASR,
            model_size=100_000_000,
            file_size=400_000_000,
            layers={},
            operators={},
            input_shapes=[],
            output_shapes=[],
            quantization_sensitivity=0.6,
            complexity_score=0.5,
            recommended_quantization=16,
            estimated_memory_usage=400.0
        )

        recommendation = self.analyzer._get_parameter_recommendation(
            'quantization_bits',
            param_config,
            characteristics
        )

        self.assertIsInstance(recommendation, ParameterRecommendation)
        self.assertEqual(recommendation.param_name, 'quantization_bits')
        self.assertIn(recommendation.recommended_value, [8, 16])
        self.assertGreater(recommendation.confidence, 0.0)

    def test_get_parameter_recommendation_learning_rate(self):
        """Test parameter recommendation for learning rate."""
        param_config = {
            'type': 'float',
            'bounds': [1e-5, 1e-2]
        }

        characteristics = ModelCharacteristics(
            model_type=ModelType.ASR,
            model_size=100_000_000,
            file_size=400_000_000,
            layers={},
            operators={},
            input_shapes=[],
            output_shapes=[],
            quantization_sensitivity=0.6,
            complexity_score=0.5,
            recommended_quantization=16,
            estimated_memory_usage=400.0
        )

        recommendation = self.analyzer._get_parameter_recommendation(
            'learning_rate',
            param_config,
            characteristics
        )

        self.assertIsInstance(recommendation, ParameterRecommendation)
        self.assertEqual(recommendation.param_name, 'learning_rate')
        self.assertGreater(recommendation.confidence, 0.0)

    def test_get_model_info(self):
        """Test model information formatting."""
        characteristics = ModelCharacteristics(
            model_type=ModelType.ASR,
            model_size=100_000_000,
            file_size=400_000_000,
            layers={"Conv1d": 12, "Linear": 20},
            operators={"Conv": 20, "MatMul": 60},
            input_shapes=[(None, None)],
            output_shapes=[(None, None, 14400)],
            quantization_sensitivity=0.6,
            complexity_score=0.5,
            is_transformer=True,
            has_conv_layers=True,
            has_rnn_layers=False,
            recommended_quantization=16,
            estimated_memory_usage=400.0
        )

        info = self.analyzer.get_model_info(characteristics)

        self.assertIsInstance(info, dict)
        self.assertIn('model_type', info)
        self.assertIn('parameters', info)
        self.assertIn('file_size_mb', info)
        self.assertIn('complexity', info)
        self.assertIn('recommended_quantization', info)
        self.assertIn('architecture', info)

    def test_initialize_model_patterns(self):
        """Test model patterns initialization."""
        patterns = self.analyzer._initialize_model_patterns()

        self.assertIsInstance(patterns, dict)
        self.assertIn(ModelType.ASR, patterns)
        self.assertIn(ModelType.TTS, patterns)
        self.assertIn(ModelType.VISION, patterns)
        self.assertIn(ModelType.NLP, patterns)

        # Check pattern structure
        for model_type, pattern in patterns.items():
            self.assertIn('keywords', pattern)
            self.assertIn('default_configs', pattern)

    def test_initialize_operator_weights(self):
        """Test operator weights initialization."""
        weights = self.analyzer._initialize_operator_weights()

        self.assertIsInstance(weights, dict)
        self.assertGreater(len(weights), 0)

        # Check common operators
        self.assertIn('Conv', weights)
        self.assertIn('MatMul', weights)
        self.assertIn('LSTM', weights)

        # All weights should be positive
        for weight in weights.values():
            self.assertGreaterEqual(weight, 0.0)


class TestModelCharacteristics(unittest.TestCase):
    """Test cases for ModelCharacteristics dataclass."""

    def test_characteristics_creation(self):
        """Test characteristics object creation."""
        characteristics = ModelCharacteristics(
            model_type=ModelType.ASR,
            model_size=100_000_000,
            file_size=400_000_000,
            layers={"Conv1d": 12},
            operators={"Conv": 20},
            input_shapes=[(None, None)],
            output_shapes=[(None, None, 14400)],
            quantization_sensitivity=0.6,
            complexity_score=0.5
        )

        self.assertEqual(characteristics.model_type, ModelType.ASR)
        self.assertEqual(characteristics.model_size, 100_000_000)
        self.assertEqual(characteristics.file_size, 400_000_000)
        self.assertEqual(characteristics.layers, {"Conv1d": 12})
        self.assertEqual(characteristics.operators, {"Conv": 20})
        self.assertEqual(characteristics.input_shapes, [(None, None)])
        self.assertEqual(characteristics.output_shapes, [(None, None, 14400)])
        self.assertEqual(characteristics.quantization_sensitivity, 0.6)
        self.assertEqual(characteristics.complexity_score, 0.5)

    def test_default_supported_formats(self):
        """Test default supported formats."""
        characteristics = ModelCharacteristics(
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

        self.assertIsNotNone(characteristics.supported_formats)
        self.assertIn("ONNX", characteristics.supported_formats)
        self.assertIn("BPU", characteristics.supported_formats)


class TestParameterRecommendation(unittest.TestCase):
    """Test cases for ParameterRecommendation dataclass."""

    def test_recommendation_creation(self):
        """Test recommendation object creation."""
        recommendation = ParameterRecommendation(
            param_name="quantization_bits",
            recommended_value=16,
            confidence=0.9,
            reason="Recommended for ASR models"
        )

        self.assertEqual(recommendation.param_name, "quantization_bits")
        self.assertEqual(recommendation.recommended_value, 16)
        self.assertEqual(recommendation.confidence, 0.9)
        self.assertEqual(recommendation.reason, "Recommended for ASR models")

    def test_recommendation_with_alternatives(self):
        """Test recommendation with alternatives."""
        recommendation = ParameterRecommendation(
            param_name="batch_size",
            recommended_value=32,
            confidence=0.8,
            reason="Good for model size",
            alternatives=[16, 64]
        )

        self.assertEqual(recommendation.param_name, "batch_size")
        self.assertEqual(recommendation.recommended_value, 32)
        self.assertEqual(recommendation.alternatives, [16, 64])


if __name__ == '__main__':
    unittest.main()
