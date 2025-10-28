"""
Preprocessing Pipeline

Provides configurable preprocessing pipeline for ONNX models:
- Standardization (ImageNet, Custom modes)
- Normalization (Min-Max, Z-Score)
- Image processing (resize, crop, flip, channel conversion)
- Batch dimension conversion (NCHW ↔ NHWC)
"""

import logging
from typing import List, Dict, Any, Optional, Callable, Union
from dataclasses import dataclass, field
import numpy as np
from enum import Enum

logger = logging.getLogger(__name__)


class NormalizeMode(Enum):
    """Normalization mode options."""
    IMAGENET = "imagenet"
    CUSTOM = "custom"
    NONE = "none"


class ChannelFormat(Enum):
    """Channel format options."""
    CHW = "CHW"  # Channel, Height, Width
    HWC = "HWC"  # Height, Width, Channel
    NCHW = "NCHW"  # Batch, Channel, Height, Width
    NHWC = "NHWC"  # Batch, Height, Width, Channel


class DataType(Enum):
    """Data type options."""
    FLOAT32 = "float32"
    FLOAT16 = "float16"
    INT8 = "int8"
    UINT8 = "uint8"


@dataclass
class PreprocessingStep:
    """Individual preprocessing step."""
    name: str
    function: Callable
    params: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True

    def __call__(self, data: np.ndarray) -> np.ndarray:
        """Execute the preprocessing step."""
        if not self.enabled:
            return data
        return self.function(data, **self.params)


@dataclass
class PreprocessingConfig:
    """Configuration for preprocessing pipeline."""
    normalize: bool = False
    normalize_mode: str = "none"
    mean: Optional[List[float]] = None
    std: Optional[List[float]] = None
    resize: Optional[tuple] = None
    crop: Optional[tuple] = None
    flip_horizontal: bool = False
    flip_vertical: bool = False
    channel_format: str = "NCHW"
    target_format: str = "NCHW"
    data_type: str = "float32"
    custom_steps: List[PreprocessingStep] = field(default_factory=list)

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.normalize_mode not in ["none", "imagenet", "custom"]:
            raise ValueError(f"Invalid normalize_mode: {self.normalize_mode}")


class PreprocessingPipeline:
    """
    Configurable preprocessing pipeline for ONNX models.

    This class provides a flexible preprocessing system that can be
    configured to handle various types of input data and requirements.
    """

    def __init__(self, config: Optional[PreprocessingConfig] = None) -> None:
        """
        Initialize the preprocessing pipeline.

        Args:
            config: Optional preprocessing configuration
        """
        self.config = config or PreprocessingConfig()
        self.steps: List[PreprocessingStep] = []
        self.reset()

        logger.info("Initialized PreprocessingPipeline")

    def add_step(self, step: PreprocessingStep) -> None:
        """
        Add a preprocessing step to the pipeline.

        Args:
            step: PreprocessingStep to add
        """
        self.steps.append(step)
        logger.info(f"Added preprocessing step: {step.name}")

    def configure(self, config: PreprocessingConfig) -> None:
        """
        Configure the preprocessing pipeline.

        Args:
            config: PreprocessingConfig with desired settings
        """
        self.config = config
        self.reset()

        # Add built-in steps based on configuration
        if self.config.normalize:
            self._add_normalize_step()

        if self.config.resize:
            self._add_resize_step()

        if self.config.crop:
            self._add_crop_step()

        if self.config.flip_horizontal:
            self._add_flip_step(horizontal=True)

        if self.config.flip_vertical:
            self._add_flip_step(horizontal=False)

        if self.config.channel_format != self.config.target_format:
            self._add_channel_conversion_step()

        if self.config.data_type:
            self._add_dtype_conversion_step()

        # Add custom steps
        for step in self.config.custom_steps:
            self.add_step(step)

        logger.info(f"Pipeline configured with {len(self.steps)} steps")

    def execute(self, data: np.ndarray) -> np.ndarray:
        """
        Execute the preprocessing pipeline on a single data sample.

        Args:
            data: Input data (numpy array)

        Returns:
            Preprocessed data (numpy array)

        Raises:
            ValueError: If data is invalid
        """
        if not isinstance(data, np.ndarray):
            raise TypeError(f"Expected numpy array, got {type(data)}")

        if data.size == 0:
            raise ValueError("Input data is empty")

        result = data.copy()
        logger.debug(f"Executing pipeline on data shape: {result.shape}")

        for step in self.steps:
            try:
                result = step(result)
                logger.debug(f"Applied step '{step.name}', new shape: {result.shape}")
            except Exception as e:
                logger.error(f"Failed to execute step '{step.name}': {e}")
                raise

        logger.info(f"Pipeline execution complete, final shape: {result.shape}")
        return result

    def batch_execute(self, batch_data: List[np.ndarray]) -> List[np.ndarray]:
        """
        Execute the preprocessing pipeline on a batch of data.

        Args:
            batch_data: List of input data arrays

        Returns:
            List of preprocessed data arrays

        Raises:
            ValueError: If batch data is invalid
        """
        if not batch_data:
            raise ValueError("Batch data is empty")

        logger.info(f"Executing batch preprocessing on {len(batch_data)} samples")

        results = []
        for i, data in enumerate(batch_data):
            try:
                result = self.execute(data)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process sample {i}: {e}")
                raise

        logger.info(f"Batch preprocessing complete, {len(results)}/{len(batch_data)} samples processed")
        return results

    def reset(self) -> None:
        """Reset the pipeline to initial state."""
        self.steps = []
        logger.debug("Pipeline reset")

    # Built-in preprocessing steps
    def _add_normalize_step(self) -> None:
        """Add normalization step based on configuration."""
        if self.config.normalize_mode == "imagenet":
            # ImageNet normalization: (data - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
            step = PreprocessingStep(
                name="normalize_imagenet",
                function=self._normalize_imagenet,
                params={}
            )
            self.add_step(step)
        elif self.config.normalize_mode == "custom":
            if self.config.mean is None or self.config.std is None:
                raise ValueError("Custom normalization requires mean and std parameters")
            step = PreprocessingStep(
                name="normalize_custom",
                function=self._normalize_custom,
                params={"mean": self.config.mean, "std": self.config.std}
            )
            self.add_step(step)

    def _add_resize_step(self) -> None:
        """Add resize step."""
        step = PreprocessingStep(
            name="resize",
            function=self._resize,
            params={"size": self.config.resize}
        )
        self.add_step(step)

    def _add_crop_step(self) -> None:
        """Add crop step."""
        step = PreprocessingStep(
            name="crop",
            function=self._crop,
            params={"size": self.config.crop}
        )
        self.add_step(step)

    def _add_flip_step(self, horizontal: bool = True) -> None:
        """Add flip step."""
        step = PreprocessingStep(
            name=f"flip_{'horizontal' if horizontal else 'vertical'}",
            function=self._flip,
            params={"horizontal": horizontal}
        )
        self.add_step(step)

    def _add_channel_conversion_step(self) -> None:
        """Add channel format conversion step."""
        step = PreprocessingStep(
            name="channel_conversion",
            function=self._convert_channels,
            params={"from_format": self.config.channel_format, "to_format": self.config.target_format}
        )
        self.add_step(step)

    def _add_dtype_conversion_step(self) -> None:
        """Add data type conversion step."""
        step = PreprocessingStep(
            name="dtype_conversion",
            function=self._convert_dtype,
            params={"dtype": self.config.data_type}
        )
        self.add_step(step)

    # Preprocessing step implementations
    def _normalize_imagenet(self, data: np.ndarray, **kwargs) -> np.ndarray:
        """Normalize data using ImageNet statistics."""
        # ImageNet mean and std
        mean = np.array([0.485, 0.456, 0.406]).reshape(1, 1, 3)
        std = np.array([0.229, 0.224, 0.225]).reshape(1, 1, 3)

        # Normalize to [0, 1] first if data is in [0, 255]
        if data.max() > 1.0:
            data = data / 255.0

        return (data - mean) / std

    def _normalize_custom(self, data: np.ndarray, mean: List[float], std: List[float], **kwargs) -> np.ndarray:
        """Normalize data using custom mean and std."""
        mean = np.array(mean)
        std = np.array(std)

        if data.max() > 1.0:
            data = data / 255.0

        return (data - mean) / (std + 1e-8)  # Add small epsilon to avoid division by zero

    def _resize(self, data: np.ndarray, size: tuple, **kwargs) -> np.ndarray:
        """Resize data to specified size."""
        try:
            import cv2

            if len(data.shape) == 3:
                # Convert CHW to HWC for OpenCV
                if data.shape[0] in [1, 3]:  # Assume CHW
                    data = data.transpose(1, 2, 0)

                resized = cv2.resize(data, size)
                # Convert back to CHW
                if resized.shape[2] in [1, 3]:
                    return resized.transpose(2, 0, 1)
                return resized
            else:
                return cv2.resize(data, size)

        except ImportError:
            logger.warning("OpenCV not available, skipping resize")
            return data

    def _crop(self, data: np.ndarray, size: tuple, **kwargs) -> np.ndarray:
        """Crop data to specified size."""
        # Simple center crop implementation
        h, w = data.shape[-2:]
        new_h, new_w = size

        start_h = (h - new_h) // 2
        start_w = (w - new_w) // 2

        if len(data.shape) == 4:  # NCHW or NHWC
            if data.shape[1] in [1, 3]:  # NCHW
                return data[:, :, start_h:start_h+new_h, start_w:start_w+new_w]
            else:  # NHWC
                return data[:, start_h:start_h+new_h, start_w:start_w+new_w, :]
        elif len(data.shape) == 3:  # CHW or HWC
            if data.shape[0] in [1, 3]:  # CHW
                return data[:, start_h:start_h+new_h, start_w:start_w+new_w]
            else:  # HWC
                return data[start_h:start_h+new_h, start_w:start_w+new_w, :]

        return data

    def _flip(self, data: np.ndarray, horizontal: bool = True, **kwargs) -> np.ndarray:
        """Flip data horizontally or vertically."""
        if horizontal:
            return np.flip(data, axis=-1)
        else:
            return np.flip(data, axis=-2)

    def _convert_channels(self, data: np.ndarray, from_format: str, to_format: str, **kwargs) -> np.ndarray:
        """Convert channel format."""
        if from_format == "CHW" and to_format == "HWC":
            return data.transpose(1, 2, 0)
        elif from_format == "HWC" and to_format == "CHW":
            return data.transpose(2, 0, 1)
        elif from_format == "NCHW" and to_format == "NHWC":
            return data.transpose(0, 2, 3, 1)
        elif from_format == "NHWC" and to_format == "NCHW":
            return data.transpose(0, 3, 1, 2)
        else:
            logger.warning(f"Unsupported channel conversion: {from_format} -> {to_format}")
            return data

    def _convert_dtype(self, data: np.ndarray, dtype: str, **kwargs) -> np.ndarray:
        """Convert data type."""
        return data.astype(getattr(np, dtype, np.float32))

    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the current pipeline configuration."""
        return {
            "total_steps": len(self.steps),
            "steps": [step.name for step in self.steps],
            "normalize": self.config.normalize,
            "normalize_mode": self.config.normalize_mode,
            "channel_format": self.config.channel_format,
            "target_format": self.config.target_format,
            "data_type": self.config.data_type
        }
