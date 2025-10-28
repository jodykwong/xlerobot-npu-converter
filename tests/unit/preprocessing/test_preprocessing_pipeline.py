"""
Unit tests for PreprocessingPipeline
"""

import pytest
import numpy as np

from npu_converter.preprocessing.pipeline import (
    PreprocessingPipeline,
    PreprocessingConfig,
    PreprocessingStep,
    NormalizeMode,
    ChannelFormat,
    DataType
)


class TestPreprocessingPipeline:
    """Test cases for PreprocessingPipeline."""

    @pytest.fixture
    def pipeline(self):
        """Create a test pipeline instance."""
        return PreprocessingPipeline()

    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        return np.random.rand(3, 224, 224).astype(np.float32)

    def test_init(self, pipeline):
        """Test pipeline initialization."""
        assert isinstance(pipeline.config, PreprocessingConfig)
        assert len(pipeline.steps) == 0

    def test_add_step(self, pipeline):
        """Test adding a preprocessing step."""
        def mock_step(data, **kwargs):
            return data

        step = PreprocessingStep(name="test_step", function=mock_step)
        pipeline.add_step(step)

        assert len(pipeline.steps) == 1
        assert pipeline.steps[0].name == "test_step"

    def test_configure(self, pipeline):
        """Test pipeline configuration."""
        config = PreprocessingConfig(
            normalize=True,
            normalize_mode="imagenet",
            resize=(256, 256),
            flip_horizontal=True
        )

        pipeline.configure(config)

        assert pipeline.config.normalize is True
        assert len(pipeline.steps) > 0

    def test_execute_single_sample(self, pipeline, sample_data):
        """Test executing pipeline on a single sample."""
        # Add a simple step
        def mock_step(data, **kwargs):
            return data * 2

        step = PreprocessingStep(name="multiply", function=mock_step)
        pipeline.add_step(step)

        result = pipeline.execute(sample_data)

        assert isinstance(result, np.ndarray)
        assert result.shape == sample_data.shape
        np.testing.assert_array_equal(result, sample_data * 2)

    def test_batch_execute(self, pipeline):
        """Test batch execution."""
        # Create batch data
        batch_data = [
            np.random.rand(3, 224, 224).astype(np.float32) for _ in range(3)
        ]

        # Add a simple step
        def mock_step(data, **kwargs):
            return data * 2

        step = PreprocessingStep(name="multiply", function=mock_step)
        pipeline.add_step(step)

        results = pipeline.batch_execute(batch_data)

        assert len(results) == 3
        for i, result in enumerate(results):
            assert isinstance(result, np.ndarray)
            np.testing.assert_array_equal(result, batch_data[i] * 2)

    def test_reset(self, pipeline):
        """Test pipeline reset."""
        # Add steps
        def mock_step(data, **kwargs):
            return data

        pipeline.add_step(PreprocessingStep(name="step1", function=mock_step))
        pipeline.add_step(PreprocessingStep(name="step2", function=mock_step))

        assert len(pipeline.steps) == 2

        # Reset
        pipeline.reset()

        assert len(pipeline.steps) == 0

    def test_imagenet_normalization(self, pipeline, sample_data):
        """Test ImageNet normalization."""
        config = PreprocessingConfig(
            normalize=True,
            normalize_mode="imagenet"
        )

        pipeline.configure(config)

        # Data should be in [0, 1] range for ImageNet normalization
        test_data = sample_data

        result = pipeline.execute(test_data)

        # After ImageNet normalization, values should be roughly in [-2, 2] range
        assert result.min() > -3
        assert result.max() < 3

    def test_channel_conversion(self, pipeline):
        """Test channel format conversion."""
        # Create CHW data (3, 224, 224)
        chw_data = np.random.rand(3, 224, 224).astype(np.float32)

        config = PreprocessingConfig(
            channel_format="CHW",
            target_format="HWC"
        )

        pipeline.configure(config)

        result = pipeline.execute(chw_data)

        # Should be converted to HWC (224, 224, 3)
        assert result.shape == (224, 224, 3)

    def test_invalid_config(self):
        """Test invalid configuration."""
        with pytest.raises(ValueError):
            config = PreprocessingConfig(normalize_mode="invalid_mode")

    def test_empty_batch(self, pipeline):
        """Test empty batch processing."""
        with pytest.raises(ValueError):
            pipeline.batch_execute([])

    def test_get_config_summary(self, pipeline):
        """Test configuration summary."""
        config = PreprocessingConfig(
            normalize=True,
            normalize_mode="imagenet"
        )

        pipeline.configure(config)

        summary = pipeline.get_config_summary()

        assert "total_steps" in summary
        assert "normalize" in summary
        assert "normalize_mode" in summary
        assert summary["normalize"] is True
        assert summary["normalize_mode"] == "imagenet"
