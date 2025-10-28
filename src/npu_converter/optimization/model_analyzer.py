"""
Model Analyzer

Analyzes model characteristics and recommends optimal parameters.
Supports various model types including ASR, TTS, and other AI models.

Author: Story 2.6 Implementation
Version: 1.0.0
Date: 2025-10-28
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Model type classification"""
    ASR = "automatic_speech_recognition"
    TTS = "text_to_speech"
    VISION = "computer_vision"
    NLP = "natural_language_processing"
    AUDIO = "audio_processing"
    GENERIC = "generic"


@dataclass
class ModelCharacteristics:
    """Model characteristics and metadata"""
    model_type: ModelType
    model_size: int  # number of parameters
    file_size: int  # bytes
    layers: Dict[str, int]  # layer type -> count
    operators: Dict[str, int]  # operator type -> count
    input_shapes: List[Tuple[int, ...]]  # list of input shapes
    output_shapes: List[Tuple[int, ...]]  # list of output shapes
    quantization_sensitivity: float  # 0.0 - 1.0
    complexity_score: float  # 0.0 - 1.0
    is_transformer: bool = False
    has_conv_layers: bool = False
    has_rnn_layers: bool = False
    recommended_quantization: int = 16
    estimated_memory_usage: float = 0.0  # MB
    supported_formats: List[str] = None

    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = ["ONNX", "BPU"]


@dataclass
class ParameterRecommendation:
    """Parameter recommendation for a model"""
    param_name: str
    recommended_value: Any
    confidence: float  # 0.0 - 1.0
    reason: str
    alternatives: List[Any] = None


class ModelAnalyzer:
    """
    Analyzes model characteristics and provides parameter recommendations.

    Supports automatic model type detection and intelligent parameter
    recommendations based on model characteristics.
    """

    def __init__(self):
        """Initialize model analyzer."""
        self.model_patterns = self._initialize_model_patterns()
        self.operator_weights = self._initialize_operator_weights()

        logger.info("Initialized ModelAnalyzer")

    def analyze_model(self, model: Any) -> ModelCharacteristics:
        """
        Analyze model and extract characteristics.

        Args:
            model: ONNX model or model path

        Returns:
            ModelCharacteristics containing model analysis
        """
        logger.info("Starting model analysis")

        # In production, would load and analyze actual ONNX model
        # For now, provide simplified analysis

        # Detect model type
        model_type = self._detect_model_type(model)

        # Extract characteristics
        model_size = self._estimate_model_size(model)
        file_size = self._estimate_file_size(model)
        layers = self._analyze_layers(model)
        operators = self._analyze_operators(model)
        input_shapes = self._get_input_shapes(model)
        output_shapes = self._get_output_shapes(model)

        # Calculate derived metrics
        quantization_sensitivity = self._calculate_quantization_sensitivity(
            model_type, layers, operators
        )
        complexity_score = self._calculate_complexity_score(
            model_size, layers, operators
        )

        # Determine architecture features
        is_transformer = self._detect_transformer(layers, operators)
        has_conv_layers = "Conv" in layers or "conv" in str(operators).lower()
        has_rnn_layers = any("rnn" in op.lower() for op in operators.keys())

        # Generate recommendations
        recommended_quantization = self._recommend_quantization(
            model_type, complexity_score, quantization_sensitivity
        )
        estimated_memory_usage = self._estimate_memory_usage(
            model_size, recommended_quantization
        )

        characteristics = ModelCharacteristics(
            model_type=model_type,
            model_size=model_size,
            file_size=file_size,
            layers=layers,
            operators=operators,
            input_shapes=input_shapes,
            output_shapes=output_shapes,
            quantization_sensitivity=quantization_sensitivity,
            complexity_score=complexity_score,
            is_transformer=is_transformer,
            has_conv_layers=has_conv_layers,
            has_rnn_layers=has_rnn_layers,
            recommended_quantization=recommended_quantization,
            estimated_memory_usage=estimated_memory_usage
        )

        logger.info(
            f"Model analysis complete: {model_type.value}, "
            f"size: {model_size} params, complexity: {complexity_score:.2f}"
        )

        return characteristics

    def recommend_parameters(
        self,
        param_space: Dict[str, Any],
        model_characteristics: ModelCharacteristics
    ) -> Dict[str, Any]:
        """
        Recommend optimal parameters for a model.

        Args:
            param_space: Parameter space definition
            model_characteristics: Model characteristics

        Returns:
            Dictionary of recommended parameter values
        """
        logger.info("Generating parameter recommendations")

        recommendations = {}

        # Analyze each parameter in the parameter space
        for param_name, param_config in param_space.items():
            param_type = param_config.get('type', 'float')

            # Get recommendation for this parameter
            recommendation = self._get_parameter_recommendation(
                param_name,
                param_config,
                model_characteristics
            )

            recommendations[param_name] = recommendation.recommended_value

        logger.info(f"Generated {len(recommendations)} parameter recommendations")

        return recommendations

    def _detect_model_type(self, model: Any) -> ModelType:
        """
        Detect model type based on model characteristics.

        Args:
            model: ONNX model

        Returns:
            ModelType enum
        """
        # In production, would analyze actual model structure
        # For now, provide simplified detection

        # Check model path/name for hints
        model_name = str(model).lower() if hasattr(model, '__str__') else ""

        # ASR model indicators
        asr_keywords = ["sensevoice", "whisper", "asr", "speech", "audio"]
        if any(keyword in model_name for keyword in asr_keywords):
            return ModelType.ASR

        # TTS model indicators
        tts_keywords = ["vits", "tts", "synthesis", "voice"]
        if any(keyword in model_name for keyword in tts_keywords):
            return ModelType.TTS

        # Vision model indicators
        vision_keywords = ["resnet", "efficientnet", "cnn", "vision", "image"]
        if any(keyword in model_name for keyword in vision_keywords):
            return ModelType.VISION

        # NLP model indicators
        nlp_keywords = ["bert", "gpt", "transformer", "nlp", "text"]
        if any(keyword in model_name for keyword in nlp_keywords):
            return ModelType.NLP

        # Default to generic
        return ModelType.GENERIC

    def _estimate_model_size(self, model: Any) -> int:
        """Estimate number of parameters in the model."""
        # In production, would calculate actual parameter count
        # For now, provide reasonable estimates

        model_name = str(model).lower()

        if "sensevoice" in model_name:
            return 100_000_000  # ~100M parameters
        elif "vits" in model_name:
            return 50_000_000  # ~50M parameters
        elif "resnet" in model_name:
            return 25_000_000  # ~25M parameters
        elif "bert" in model_name:
            return 110_000_000  # ~110M parameters
        else:
            return 10_000_000  # Default estimate

    def _estimate_file_size(self, model: Any) -> int:
        """Estimate model file size in bytes."""
        # In production, would check actual file size
        model_size = self._estimate_model_size(model)

        # Assume 4 bytes per parameter (float32)
        return model_size * 4

    def _analyze_layers(self, model: Any) -> Dict[str, int]:
        """Analyze layer types in the model."""
        # In production, would parse actual model structure
        # For now, provide typical distributions

        model_name = str(model).lower()

        if "vits" in model_name:
            # VITS typically has: ResBlock, Conv1d, Linear, LSTM
            return {
                "ResBlock": 16,
                "Conv1d": 24,
                "Linear": 8,
                "LSTM": 2
            }
        elif "sensevoice" in model_name:
            # SenseVoice has: Conv1d, Linear, Transformer
            return {
                "Conv1d": 12,
                "Linear": 20,
                "Transformer": 24
            }
        elif "resnet" in model_name:
            # ResNet has: Conv2d, BatchNorm, Linear
            return {
                "Conv2d": 50,
                "BatchNorm": 49,
                "Linear": 1
            }
        else:
            return {
                "Linear": 10,
                "Conv": 5
            }

    def _analyze_operators(self, model: Any) -> Dict[str, int]:
        """Analyze operator types in the model."""
        # In production, would extract from ONNX model
        # For now, provide typical distributions

        model_name = str(model).lower()

        if "vits" in model_name:
            return {
                "Conv": 24,
                "MatMul": 50,
                "Add": 30,
                "Relu": 20,
                "Tanh": 10,
                "LSTM": 2
            }
        elif "sensevoice" in model_name:
            return {
                "Conv": 20,
                "MatMul": 60,
                "Add": 40,
                "Relu": 30,
                "LayerNormalization": 12,
                "Gelu": 12
            }
        else:
            return {
                "Conv": 10,
                "MatMul": 20,
                "Add": 15,
                "Relu": 10
            }

    def _get_input_shapes(self, model: Any) -> List[Tuple[int, ...]]:
        """Get input shapes of the model."""
        # In production, would extract from ONNX model
        # For now, provide typical shapes

        model_name = str(model).lower()

        if "vits" in model_name:
            # VITS TTS: [batch, text_length], [batch, mel_channels, mel_length]
            return [(None, None), (None, 80, None)]
        elif "sensevoice" in model_name:
            # SenseVoice ASR: [batch, audio_length]
            return [(None, None)]
        elif "resnet" in model_name:
            # ResNet: [batch, channels, height, width]
            return [(None, 3, 224, 224)]
        else:
            return [(None, None)]

    def _get_output_shapes(self, model: Any) -> List[Tuple[int, ...]]:
        """Get output shapes of the model."""
        # In production, would extract from ONNX model
        # For now, provide typical shapes

        model_name = str(model).lower()

        if "vits" in model_name:
            # VITS TTS: [batch, audio_length]
            return [(None, None)]
        elif "sensevoice" in model_name:
            # SenseVoice ASR: [batch, text_length, num_classes]
            return [(None, None, 14400)]
        elif "resnet" in model_name:
            # ResNet: [batch, num_classes]
            return [(None, 1000)]
        else:
            return [(None, None)]

    def _calculate_quantization_sensitivity(
        self,
        model_type: ModelType,
        layers: Dict[str, int],
        operators: Dict[str, int]
    ) -> float:
        """
        Calculate quantization sensitivity score.

        Args:
            model_type: Type of model
            layers: Layer distribution
            operators: Operator distribution

        Returns:
            Quantization sensitivity (0.0 - 1.0, higher = more sensitive)
        """
        # Base sensitivity by model type
        base_sensitivity = {
            ModelType.ASR: 0.6,
            ModelType.TTS: 0.7,  # TTS is more sensitive to quality
            ModelType.VISION: 0.4,
            ModelType.NLP: 0.5,
            ModelType.GENERIC: 0.5
        }.get(model_type, 0.5)

        # Adjust based on layer types
        layer_adjustment = 0.0

        # RNN/LSTM layers are more sensitive
        if any("LSTM" in layer or "RNN" in layer for layer in layers.keys()):
            layer_adjustment += 0.2

        # Normalization layers are sensitive
        if any("Norm" in layer for layer in layers.keys()):
            layer_adjustment += 0.1

        # Calculate final sensitivity
        sensitivity = min(1.0, base_sensitivity + layer_adjustment)

        return sensitivity

    def _calculate_complexity_score(
        self,
        model_size: int,
        layers: Dict[str, int],
        operators: Dict[str, int]
    ) -> float:
        """
        Calculate model complexity score.

        Args:
            model_size: Number of parameters
            layers: Layer distribution
            operators: Operator distribution

        Returns:
            Complexity score (0.0 - 1.0)
        """
        # Normalize model size (log scale)
        size_score = min(1.0, np.log10(max(1, model_size)) / 8.0)

        # Layer complexity
        layer_types = len(layers)
        layer_score = min(1.0, layer_types / 20.0)

        # Operator diversity
        operator_types = len(operators)
        operator_score = min(1.0, operator_types / 30.0)

        # Weighted combination
        complexity = (0.5 * size_score + 0.3 * layer_score + 0.2 * operator_score)

        return complexity

    def _detect_transformer(self, layers: Dict[str, int], operators: Dict[str, int]) -> bool:
        """Detect if model uses transformer architecture."""
        # Check for transformer indicators
        transformer_indicators = [
            "MultiHeadAttention",
            "LayerNormalization",
            "Gelu",
            "Attention"
        ]

        has_transformer_layers = any(
            indicator.lower() in layer.lower()
            for layer in layers.keys()
            for indicator in transformer_indicators
        )

        has_transformer_operators = any(
            indicator.lower() in op.lower()
            for op in operators.keys()
            for indicator in transformer_indicators
        )

        return has_transformer_layers or has_transformer_operators

    def _recommend_quantization(
        self,
        model_type: ModelType,
        complexity_score: float,
        quantization_sensitivity: float
    ) -> int:
        """
        Recommend quantization precision.

        Args:
            model_type: Model type
            complexity_score: Model complexity
            quantization_sensitivity: Quantization sensitivity

        Returns:
            Recommended quantization bits (8 or 16)
        """
        # If model is very sensitive, recommend 16-bit
        if quantization_sensitivity > 0.7:
            return 16

        # If complexity is high, recommend 16-bit for stability
        if complexity_score > 0.8:
            return 16

        # For TTS models, prioritize quality (16-bit)
        if model_type == ModelType.TTS:
            return 16

        # For ASR models, balance quality and speed
        if model_type == ModelType.ASR:
            if quantization_sensitivity < 0.5 and complexity_score < 0.6:
                return 8
            else:
                return 16

        # Default recommendation
        return 16

    def _estimate_memory_usage(
        self,
        model_size: int,
        quantization_bits: int
    ) -> float:
        """
        Estimate memory usage.

        Args:
            model_size: Number of parameters
            quantization_bits: Quantization precision

        Returns:
            Estimated memory usage in MB
        """
        # Calculate bytes per parameter
        if quantization_bits == 8:
            bytes_per_param = 1.0
        elif quantization_bits == 16:
            bytes_per_param = 2.0
        else:
            bytes_per_param = 4.0

        # Calculate memory (add overhead for activations, etc.)
        memory_bytes = model_size * bytes_per_param * 1.5  # 50% overhead

        # Convert to MB
        memory_mb = memory_bytes / (1024 * 1024)

        return memory_mb

    def _get_parameter_recommendation(
        self,
        param_name: str,
        param_config: Dict[str, Any],
        model_characteristics: ModelCharacteristics
    ) -> ParameterRecommendation:
        """
        Get recommendation for a specific parameter.

        Args:
            param_name: Parameter name
            param_config: Parameter configuration
            model_characteristics: Model characteristics

        Returns:
            ParameterRecommendation
        """
        param_type = param_config.get('type', 'float')
        model_type = model_characteristics.model_type

        # Quantization parameter
        if "quant" in param_name.lower() or "bits" in param_name.lower():
            recommended_value = model_characteristics.recommended_quantization
            confidence = 0.9
            reason = f"Recommended based on {model_type.value} model characteristics"

        # Learning rate parameter
        elif "lr" in param_name.lower() or "learning" in param_name.lower():
            if model_type == ModelType.ASR:
                recommended_value = 1e-4
                confidence = 0.8
            elif model_type == ModelType.TTS:
                recommended_value = 1e-4
                confidence = 0.8
            else:
                recommended_value = 1e-3
                confidence = 0.6
            reason = f"Typical learning rate for {model_type.value} models"

        # Batch size parameter
        elif "batch" in param_name.lower():
            if model_characteristics.model_size > 50_000_000:
                recommended_value = 16
                confidence = 0.7
            else:
                recommended_value = 32
                confidence = 0.7
            reason = "Adjusted for model size"

        # Generic parameter
        else:
            if param_type == 'choice':
                values = param_config.get('values', [0])
                recommended_value = values[0]
                confidence = 0.5
            elif param_type == 'int':
                bounds = param_config.get('bounds', (0, 100))
                recommended_value = (bounds[0] + bounds[1]) // 2
                confidence = 0.5
            elif param_type == 'float':
                bounds = param_config.get('bounds', (0.0, 1.0))
                recommended_value = (bounds[0] + bounds[1]) / 2.0
                confidence = 0.5
            else:
                recommended_value = None
                confidence = 0.0
            reason = "Default recommendation"

        return ParameterRecommendation(
            param_name=param_name,
            recommended_value=recommended_value,
            confidence=confidence,
            reason=reason
        )

    def _initialize_model_patterns(self) -> Dict[ModelType, Dict[str, Any]]:
        """Initialize model type patterns."""
        return {
            ModelType.ASR: {
                "keywords": ["speech", "audio", "asr", "recognition", "sensevoice"],
                "default_configs": {
                    "sample_rate": 16000,
                    "quantization": 16,
                    "normalize": True
                }
            },
            ModelType.TTS: {
                "keywords": ["tts", "synthesis", "voice", "vits"],
                "default_configs": {
                    "sample_rate": 22050,
                    "quantization": 16,
                    "quality": "high"
                }
            },
            ModelType.VISION: {
                "keywords": ["image", "vision", "cnn", "resnet", "conv"],
                "default_configs": {
                    "input_size": 224,
                    "quantization": 8,
                    "normalize": True
                }
            },
            ModelType.NLP: {
                "keywords": ["text", "nlp", "bert", "transformer", "token"],
                "default_configs": {
                    "max_length": 512,
                    "quantization": 8,
                    "normalize": False
                }
            }
        }

    def _initialize_operator_weights(self) -> Dict[str, float]:
        """Initialize operator importance weights."""
        return {
            "Conv": 1.0,
            "MatMul": 1.0,
            "Add": 0.5,
            "Relu": 0.3,
            "Tanh": 0.5,
            "LSTM": 1.5,
            "LayerNormalization": 0.8,
            "MultiHeadAttention": 1.2
        }

    def get_model_info(self, characteristics: ModelCharacteristics) -> Dict[str, Any]:
        """
        Get formatted model information.

        Args:
            characteristics: Model characteristics

        Returns:
            Formatted model information dictionary
        """
        return {
            "model_type": characteristics.model_type.value,
            "parameters": characteristics.model_size,
            "file_size_mb": characteristics.file_size / (1024 * 1024),
            "complexity": f"{characteristics.complexity_score:.2f}",
            "quantization_sensitivity": f"{characteristics.quantization_sensitivity:.2f}",
            "recommended_quantization": characteristics.recommended_quantization,
            "estimated_memory_mb": f"{characteristics.estimated_memory_usage:.1f}",
            "architecture": {
                "transformer": characteristics.is_transformer,
                "conv_layers": characteristics.has_conv_layers,
                "rnn_layers": characteristics.has_rnn_layers
            },
            "top_layers": sorted(
                characteristics.layers.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }
