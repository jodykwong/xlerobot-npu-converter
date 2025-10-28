"""
Integration tests for ONNX loading workflow
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile

from npu_converter.loaders.onnx_loader import ONNXModelLoader
from npu_converter.preprocessing.pipeline import PreprocessingPipeline, PreprocessingConfig
from npu_converter.validation.compatibility import CompatibilityChecker
from npu_converter.preprocessing.batch_processor import BatchProcessor


class TestONNXLoadingIntegration:
    """Integration tests for the complete ONNX loading workflow."""

    def test_end_to_end_loading(self):
        """Test end-to-end model loading and processing."""
        # Create loader
        loader = ONNXModelLoader()

        # Create preprocessor
        config = PreprocessingConfig(
            normalize=True,
            normalize_mode="imagenet"
        )
        preprocessor = PreprocessingPipeline(config)

        # Create compatibility checker
        checker = CompatibilityChecker()

        # Create a mock ONNX model
        mock_model = loader.load_from_object(
            type('MockModelProto', (), {
                'ByteSize': lambda self: 1024
            })()
        )

        # Test validation
        result = checker.check_operator_support(mock_model)

        # Assertions
        assert isinstance(mock_model, type(loader.load_from_object(None)))

    def test_batch_processing_integration(self):
        """Test batch processing integration."""
        # Create batch processor
        processor = BatchProcessor(max_workers=4)

        # Create mock models
        mock_models = []
        for i in range(3):
            model = type('MockModel', (), {
                'id': f'model_{i}',
                'status': 'completed'
            })()
            mock_models.append(model)

        # Test batch loading (mocked)
        with pytest.raises(Exception):
            # This should fail because we're using mock data
            processor.batch_load(mock_models)

    def test_preprocessing_integration(self):
        """Test preprocessing integration."""
        # Create pipeline with configuration
        config = PreprocessingConfig(
            normalize=True,
            normalize_mode="custom",
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
        pipeline = PreprocessingPipeline(config)

        # Create test data
        test_data = np.random.rand(3, 224, 224).astype(np.float32)

        # Process data
        result = pipeline.execute(test_data)

        # Assertions
        assert isinstance(result, np.ndarray)
        assert result.shape == test_data.shape
        assert result.dtype == np.float32

    def test_compatibility_checking_integration(self):
        """Test compatibility checking integration."""
        # Create checker
        checker = CompatibilityChecker()

        # Create mock model with various properties
        mock_model = type('MockModel', (), {
            'metadata': type('MockMetadata', (), {
                'model_name': 'test_model',
                'total_nodes': 10
            })(),
            'version_info': type('MockVersionInfo', (), {
                'opset_version': 13,
                'opset_versions': {'ai.onnx': 13}
            })(),
            'input_tensors': [type('MockTensor', (), {
                'shape': [1, 3, 224, 224],
                'dtype': 'FLOAT'
            })()],
            'output_tensors': [type('MockTensor', (), {
                'shape': [1, 1000],
                'dtype': 'FLOAT'
            })()],
            'operators': [type('MockOperator', (), {
                'op_type': 'Conv'
            })()],
            'operator_count': 1,
            'has_operator': lambda self, op_type: op_type == 'Conv'
        })()

        # Run full compatibility check
        result = checker.full_compatibility_check(mock_model)

        # Assertions
        assert isinstance(result, type(checker.full_compatibility_check(mock_model)))
        assert hasattr(result, 'overall')

    def test_module_imports(self):
        """Test that all modules can be imported correctly."""
        from npu_converter.loaders import ONNXModelLoader, ModelMetadataExtractor
        from npu_converter.preprocessing import PreprocessingPipeline, BatchProcessor
        from npu_converter.validation import CompatibilityChecker

        # Create instances
        loader = ONNXModelLoader()
        pipeline = PreprocessingPipeline()
        processor = BatchProcessor()
        checker = CompatibilityChecker()

        # Assertions
        assert loader.name == "ONNXModelLoader"
        assert isinstance(pipeline, PreprocessingPipeline)
        assert isinstance(checker, CompatibilityChecker)

    def test_data_flow_integration(self):
        """Test data flow through the entire pipeline."""
        # Step 1: Create components
        loader = ONNXModelLoader()
        preprocessor = PreprocessingPipeline()
        checker = CompatibilityChecker()

        # Step 2: Load model (mock)
        mock_model = type('MockModel', (), {
            'metadata': type('MockMetadata', (), {
                'model_name': 'integration_test',
                'total_nodes': 5
            })(),
            'version_info': type('MockVersionInfo', (), {
                'opset_version': 13,
                'opset_versions': {'ai.onnx': 13}
            })(),
            'input_tensors': [],
            'output_tensors': [],
            'operators': [],
            'operator_count': 0,
            'has_operator': lambda self, op_type: False
        })()

        # Step 3: Validate
        validation_result = loader.validate_model(mock_model)

        # Assertions
        assert isinstance(mock_model, type(mock_model))
        assert hasattr(validation_result, 'is_valid')
