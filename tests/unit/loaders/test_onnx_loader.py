"""
Unit tests for ONNXModelLoader
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile
from unittest.mock import Mock, patch, MagicMock

from npu_converter.loaders.onnx_loader import ONNXModelLoader
from npu_converter.models.onnx_model import ONNXModel
from npu_converter.models.config_model import ConfigModel


class TestONNXModelLoader:
    """Test cases for ONNXModelLoader."""

    @pytest.fixture
    def loader(self):
        """Create a test loader instance."""
        return ONNXModelLoader()

    @pytest.fixture
    def mock_model_proto(self):
        """Create a mock ONNX model proto."""
        mock_proto = MagicMock()
        mock_proto.ByteSize.return_value = 1024
        return mock_proto

    def test_init(self, loader):
        """Test loader initialization."""
        assert loader.name == "ONNXModelLoader"
        assert loader.version == "1.0.0"
        assert loader.status == "initialized"

    def test_load_from_file(self, loader):
        """Test loading from file."""
        # Create a temporary ONNX file
        with tempfile.NamedTemporaryFile(suffix=".onnx", delete=False) as f:
            temp_path = Path(f.name)

        try:
            # Mock the onnx.load function
            with patch("npu_converter.loaders.onnx_loader.onnx.load") as mock_load:
                mock_proto = MagicMock()
                mock_proto.ByteSize.return_value = 1024
                mock_load.return_value = mock_proto

                # Mock the metadata extractor
                with patch.object(loader, "_extract_all_metadata"):
                    model = loader.load_from_file(temp_path)

                    assert isinstance(model, ONNXModel)
                    assert model.model_proto == mock_proto
                    assert model.model_path == temp_path
                    assert model.status == "loaded"

        finally:
            # Clean up
            temp_path.unlink(missing_ok=True)

    def test_load_from_object(self, loader, mock_model_proto):
        """Test loading from ModelProto object."""
        with patch.object(loader, "_extract_all_metadata"):
            model = loader.load_from_object(mock_model_proto)

            assert isinstance(model, ONNXModel)
            assert model.model_proto == mock_model_proto
            assert model.status == "loaded"

    def test_load_from_url(self, loader):
        """Test loading from URL."""
        with patch("npu_converter.loaders.onnx_loader.requests.get") as mock_get, \
             patch.object(loader, "_extract_all_metadata"):

            # Mock response
            mock_response = MagicMock()
            mock_response.content = b"mock model data"
            mock_get.return_value = mock_response

            # Mock the cache directory
            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = Path("/tmp")

                model = loader.load_from_url("https://example.com/model.onnx")

                assert isinstance(model, ONNXModel)
                assert model.status == "loaded"

    def test_batch_load(self, loader):
        """Test batch loading."""
        # Create test sources
        sources = ["model1.onnx", "model2.onnx", "model3.onnx"]

        # Mock the _load_single_model method
        with patch.object(loader, "_load_single_model") as mock_load:
            # Return different mock models
            mock_load.side_effect = [
                MagicMock(status="completed"),
                MagicMock(status="completed"),
                MagicMock(status="completed")
            ]

            result = loader.batch_load(sources)

            assert result.total_items == 3
            assert result.successful_items == 3
            assert result.failed_items == 0

    def test_validate_model(self, loader):
        """Test model validation."""
        # Create a mock model
        model = MagicMock()
        model.is_loaded = True
        model.input_tensors = [MagicMock()]
        model.output_tensors = [MagicMock()]
        model.operator_count = 5

        result = loader.validate_model(model)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_model_no_operators(self, loader):
        """Test model validation with no operators."""
        model = MagicMock()
        model.is_loaded = True
        model.input_tensors = [MagicMock()]
        model.output_tensors = [MagicMock()]
        model.operator_count = 0

        result = loader.validate_model(model)

        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_extract_all_metadata(self, loader):
        """Test metadata extraction."""
        # Create a mock model
        model = MagicMock()

        # Mock the metadata extractor
        with patch.object(loader.metadata_extractor, "extract_model_metadata") as mock_extract_meta, \
             patch.object(loader.metadata_extractor, "extract_input_tensors") as mock_extract_input, \
             patch.object(loader.metadata_extractor, "extract_output_tensors") as mock_extract_output, \
             patch.object(loader.metadata_extractor, "extract_operators") as mock_extract_ops, \
             patch.object(loader.metadata_extractor, "extract_version_info") as mock_extract_ver:

            # Set up return values
            mock_extract_meta.return_value = MagicMock()
            mock_extract_input.return_value = []
            mock_extract_output.return_value = []
            mock_extract_ops.return_value = []
            mock_extract_ver.return_value = MagicMock()

            # Call the method
            loader._extract_all_metadata(model)

            # Verify calls
            mock_extract_meta.assert_called_once()
            mock_extract_input.assert_called_once()
            mock_extract_output.assert_called_once()
            mock_extract_ops.assert_called_once()
            mock_extract_ver.assert_called_once()
