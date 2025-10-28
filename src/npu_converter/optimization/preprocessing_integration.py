"""
Preprocessing Pipeline Integration

Integrates parameter optimization with preprocessing pipeline.
Provides seamless optimization of preprocessing parameters.

Author: Story 2.6 Implementation
Version: 1.0.0
Date: 2025-10-28
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PreprocessingOptimizationConfig:
    """Configuration for preprocessing parameter optimization"""
    optimize_normalization: bool = True
    optimize_resize: bool = True
    optimize_channel_format: bool = True
    optimize_data_type: bool = True
    respect_model_constraints: bool = True
    preset: Optional[str] = None  # "vision", "audio", "nlp"


class PreprocessingOptimizer:
    """
    Optimizer specifically for preprocessing parameters.

    Integrates with the preprocessing pipeline to optimize
    normalization, resizing, channel format, and other parameters.
    """

    def __init__(self):
        """Initialize preprocessing optimizer."""
        self.presets = self._initialize_presets()
        logger.info("Initialized PreprocessingOptimizer")

    def optimize_preprocessing(
        self,
        model_characteristics: Dict[str, Any],
        target_metric: str = "compatibility",
        config: Optional[PreprocessingOptimizationConfig] = None
    ) -> Dict[str, Any]:
        """
        Optimize preprocessing parameters for a model.

        Args:
            model_characteristics: Model characteristics from ModelAnalyzer
            target_metric: Metric to optimize (compatibility, accuracy, etc.)
            config: Optimization configuration

        Returns:
            Dictionary of optimized preprocessing parameters
        """
        if config is None:
            config = PreprocessingOptimizationConfig()

        logger.info(f"Optimizing preprocessing parameters for {model_characteristics.get('model_type', 'unknown')} model")

        # Get model type
        model_type = model_characteristics.get('model_type', 'generic').lower()

        # Start with preset
        params = self._get_preset_parameters(model_type, config.preset)

        # Apply model-specific optimizations
        params = self._apply_model_specific_optimizations(params, model_characteristics)

        # Optimize for target metric
        params = self._optimize_for_metric(params, model_characteristics, target_metric)

        # Apply constraints
        if config.respect_model_constraints:
            params = self._apply_constraints(params, model_characteristics)

        logger.info(f"Optimized preprocessing parameters: {params}")

        return params

    def _initialize_presets(self) -> Dict[str, Dict[str, Any]]:
        """Initialize preprocessing parameter presets."""
        return {
            'vision': {
                'normalize': True,
                'normalize_mode': 'imagenet',
                'resize': (224, 224),
                'channel_format': 'NCHW',
                'target_format': 'NCHW',
                'mean': [0.485, 0.456, 0.406],
                'std': [0.229, 0.224, 0.225],
                'data_type': 'float32'
            },
            'audio': {
                'normalize': True,
                'normalize_mode': 'custom',
                'resize': None,
                'channel_format': 'NC',
                'target_format': 'NC',
                'mean': [0.0],
                'std': [1.0],
                'data_type': 'float32',
                'sample_rate': 16000
            },
            'nlp': {
                'normalize': False,
                'resize': None,
                'channel_format': 'NC',
                'target_format': 'NC',
                'mean': None,
                'std': None,
                'data_type': 'int64',
                'max_length': 512
            },
            'asr': {
                'normalize': True,
                'normalize_mode': 'custom',
                'resize': None,
                'channel_format': 'NC',
                'target_format': 'NC',
                'mean': [0.0],
                'std': [1.0],
                'data_type': 'float32',
                'sample_rate': 16000,
                'window_size': 512,
                'hop_length': 256
            },
            'tts': {
                'normalize': True,
                'normalize_mode': 'custom',
                'resize': None,
                'channel_format': 'NC',
                'target_format': 'NC',
                'mean': [0.0],
                'std': [1.0],
                'data_type': 'float32',
                'sample_rate': 22050
            }
        }

    def _get_preset_parameters(
        self,
        model_type: str,
        preset: Optional[str]
    ) -> Dict[str, Any]:
        """Get parameters from preset or model type."""
        if preset and preset in self.presets:
            logger.debug(f"Using preset: {preset}")
            return self.presets[preset].copy()

        # Auto-detect preset from model type
        if 'vision' in model_type or 'image' in model_type:
            return self.presets['vision'].copy()
        elif 'asr' in model_type or 'speech' in model_type:
            return self.presets['asr'].copy()
        elif 'tts' in model_type or 'synthesis' in model_type:
            return self.presets['tts'].copy()
        elif 'nlp' in model_type or 'text' in model_type:
            return self.presets['nlp'].copy()
        else:
            # Default to audio preset
            logger.debug("Using default audio preset")
            return self.presets['audio'].copy()

    def _apply_model_specific_optimizations(
        self,
        params: Dict[str, Any],
        model_characteristics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply model-specific preprocessing optimizations."""
        model_type = model_characteristics.get('model_type', 'generic').lower()
        complexity = model_characteristics.get('complexity_score', 0.5)

        # Adjust normalization based on model complexity
        if complexity > 0.7:
            params['normalize'] = True
            logger.debug("Enabled normalization for high complexity model")

        # Adjust resize for vision models
        if 'vision' in model_type and params.get('resize'):
            if complexity > 0.8:
                # Use higher resolution for complex models
                params['resize'] = (320, 320)
                logger.debug("Using higher resolution for complex vision model")
            elif complexity < 0.3:
                # Use lower resolution for simple models
                params['resize'] = (160, 160)
                logger.debug("Using lower resolution for simple vision model")

        # Adjust sample rate for audio models
        if 'asr' in model_type or 'audio' in model_type:
            if complexity > 0.6:
                # Use higher sample rate for complex audio models
                params['sample_rate'] = 22050
                logger.debug("Using higher sample rate for complex audio model")

        return params

    def _optimize_for_metric(
        self,
        params: Dict[str, Any],
        model_characteristics: Dict[str, Any],
        target_metric: str
    ) -> Dict[str, Any]:
        """Optimize parameters for specific target metric."""
        if target_metric == 'compatibility':
            # Prioritize Horizon X5 BPU compatibility
            params['channel_format'] = 'NCHW'  # Preferred for BPU
            params['data_type'] = 'float32'  # Most compatible

            if params.get('normalize_mode') == 'imagenet':
                # Custom normalization is more flexible
                params['normalize_mode'] = 'custom'

        elif target_metric == 'accuracy':
            # Prioritize accuracy
            params['normalize'] = True

            if 'vision' in model_characteristics.get('model_type', '').lower():
                # Use ImageNet normalization for vision models
                params['normalize_mode'] = 'imagenet'

        elif target_metric == 'speed':
            # Prioritize speed
            params['normalize'] = False  # Skip normalization for speed

            if params.get('resize'):
                # Use smaller resize
                params['resize'] = (128, 128)

        return params

    def _apply_constraints(
        self,
        params: Dict[str, Any],
        model_characteristics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply Horizon X5 BPU constraints."""
        # Ensure channel format is compatible
        supported_formats = ['NCHW', 'NHWC', 'NC']
        current_format = params.get('channel_format', 'NCHW')

        if current_format not in supported_formats:
            logger.warning(f"Unsupported channel format: {current_format}, using NCHW")
            params['channel_format'] = 'NCHW'

        # Ensure data type is supported
        supported_types = ['float32', 'int64', 'int32']
        current_type = params.get('data_type', 'float32')

        if current_type not in supported_types:
            logger.warning(f"Unsupported data type: {current_type}, using float32")
            params['data_type'] = 'float32'

        # Ensure resize dimensions are reasonable
        if params.get('resize'):
            width, height = params['resize']
            if width > 1024 or height > 1024:
                logger.warning(f"Resize dimensions too large: {params['resize']}, using (224, 224)")
                params['resize'] = (224, 224)

        return params

    def validate_preprocessing_params(
        self,
        params: Dict[str, Any],
        model_type: str
    ) -> List[str]:
        """
        Validate preprocessing parameters.

        Args:
            params: Preprocessing parameters
            model_type: Model type

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check resize dimensions
        if params.get('resize'):
            width, height = params['resize']
            if width <= 0 or height <= 0:
                errors.append("Resize dimensions must be positive")
            if width > 2048 or height > 2048:
                errors.append("Resize dimensions too large (max 2048x2048)")

        # Check channel format
        channel_format = params.get('channel_format', 'NCHW')
        if channel_format not in ['NCHW', 'NHWC', 'NC']:
            errors.append(f"Unsupported channel format: {channel_format}")

        # Check data type
        data_type = params.get('data_type', 'float32')
        if data_type not in ['float32', 'float64', 'int32', 'int64']:
            errors.append(f"Unsupported data type: {data_type}")

        # Check mean and std for normalization
        if params.get('normalize', False):
            mean = params.get('mean')
            std = params.get('std')

            if mean is not None:
                if not isinstance(mean, (list, tuple)):
                    errors.append("Mean must be a list or tuple")
                elif len(mean) == 0:
                    errors.append("Mean cannot be empty")

            if std is not None:
                if not isinstance(std, (list, tuple)):
                    errors.append("Std must be a list or tuple")
                elif len(std) == 0:
                    errors.append("Std cannot be empty")
                elif any(s <= 0 for s in std):
                    errors.append("Std values must be positive")

        # Check sample rate for audio models
        if 'audio' in model_type.lower() or 'asr' in model_type.lower():
            sample_rate = params.get('sample_rate')
            if sample_rate and sample_rate not in [8000, 16000, 22050, 44100, 48000]:
                errors.append(f"Non-standard sample rate: {sample_rate}")

        return errors

    def get_preprocessing_recommendations(
        self,
        model_characteristics: Dict[str, Any]
    ) -> List[str]:
        """
        Get preprocessing recommendations for a model.

        Args:
            model_characteristics: Model characteristics

        Returns:
            List of recommendations
        """
        recommendations = []
        model_type = model_characteristics.get('model_type', 'generic').lower()

        if 'vision' in model_type:
            recommendations.append("Use ImageNet normalization for best transfer learning performance")
            recommendations.append("Resize to 224x224 for optimal speed and accuracy balance")
            recommendations.append("Use NCHW format for better BPU performance")

        elif 'asr' in model_type:
            recommendations.append("Use 16kHz sample rate for speech recognition models")
            recommendations.append("Apply pre-emphasis and windowing for better feature extraction")
            recommendations.append("Normalize audio to zero mean and unit variance")

        elif 'tts' in model_type:
            recommendations.append("Use 22.05kHz or 44.1kHz sample rate for high-quality synthesis")
            recommendations.append("Apply mu-law companding for better dynamic range")
            recommendations.append("Normalize mel-spectrogram features")

        else:
            recommendations.append("Validate preprocessing parameters with test data")
            recommendations.append("Monitor accuracy during preprocessing optimization")

        return recommendations
