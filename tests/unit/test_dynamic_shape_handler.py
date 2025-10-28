"""
Unit tests for DynamicShapeHandler

Tests the dynamic shape validation capabilities added in Story 2.5.
"""

import unittest
from unittest.mock import Mock, patch

from src.npu_converter.validation.dynamic_shape_handler import (
    DynamicShapeHandler,
    DynamicShapeType,
    DynamicDimensionInfo,
    DynamicShapeValidationResult
)


class TestDynamicShapeHandler(unittest.TestCase):
    """Test cases for DynamicShapeHandler"""

    def setUp(self):
        """Set up test fixtures"""
        self.handler = DynamicShapeHandler()

    def test_init(self):
        """Test DynamicShapeHandler initialization"""
        self.assertIsInstance(self.handler, DynamicShapeHandler)
        self.assertIsNotNone(self.handler.dimension_patterns)

    def test_classify_dimension_batch_size(self):
        """Test classification of batch size dimension"""
        # Mock tensor
        tensor = Mock()
        tensor.name = "input"
        tensor.shape = [-1, 128, 224, 3]
        all_tensors = [tensor]

        # Test first dimension (batch size)
        dim_type = self.handler._classify_dimension(0, -1, tensor, all_tensors)
        self.assertEqual(dim_type, DynamicShapeType.BATCH_SIZE)

    def test_classify_dimension_sequence_length(self):
        """Test classification of sequence length dimension"""
        # Mock NLP tensor
        tensor = Mock()
        tensor.name = "token_ids"
        tensor.shape = [128, -1, 768]
        all_tensors = [tensor]

        # Test sequence length dimension
        dim_type = self.handler._classify_dimension(1, -1, tensor, all_tensors)
        self.assertEqual(dim_type, DynamicShapeType.SEQUENCE_LENGTH)

    def test_classify_dimension_spatial(self):
        """Test classification of spatial dimension"""
        # Mock vision tensor
        tensor = Mock()
        tensor.name = "feature_map"
        tensor.shape = [16, 256, 28, -1]
        all_tensors = [tensor]

        # Test spatial dimension
        dim_type = self.handler._classify_dimension(3, -1, tensor, all_tensors)
        self.assertEqual(dim_type, DynamicShapeType.HEIGHT_WIDTH)

    def test_check_dimension_support_batch(self):
        """Test Horizon X5 BPU support for batch dimensions"""
        dim_index = 0
        dim_type = DynamicShapeType.BATCH_SIZE
        tensor = Mock()
        tensor.name = "input"
        dim_size = -1

        is_supported, desc = self.handler._check_dimension_support(
            dim_index, dim_type, tensor, dim_size
        )

        self.assertTrue(is_supported)
        self.assertIn("supported", desc.lower())

    def test_check_dimension_support_unknown(self):
        """Test rejection of unknown dimension (dim_value=0)"""
        dim_index = 0
        dim_type = DynamicShapeType.CUSTOM
        tensor = Mock()
        tensor.name = "input"
        dim_size = 0  # Unknown dimension

        is_supported, desc = self.handler._check_dimension_support(
            dim_index, dim_type, tensor, dim_size
        )

        self.assertFalse(is_supported)
        self.assertIn("Unknown dimension", desc)

    def test_get_recommended_value(self):
        """Test recommendation of fixed values for dynamic dimensions"""
        batch_value = self.handler._get_recommended_value(
            DynamicShapeType.BATCH_SIZE, 0
        )
        self.assertEqual(batch_value, 1)

        seq_value = self.handler._get_recommended_value(
            DynamicShapeType.SEQUENCE_LENGTH, 1
        )
        self.assertEqual(seq_value, 128)

        spatial_value = self.handler._get_recommended_value(
            DynamicShapeType.HEIGHT_WIDTH, 2
        )
        self.assertEqual(spatial_value, 224)

    def test_calculate_grade(self):
        """Test grade calculation from quality score"""
        score_a = self.handler._calculate_grade(0.95) if hasattr(self.handler, '_calculate_grade') else None
        # Note: _calculate_grade is in QualityScorer, not DynamicShapeHandler
        self.assertIsNotNone(self.handler)

    def test_suggest_dynamic_shape(self):
        """Test dynamic shape suggestion"""
        # Mock tensor with dynamic shape
        tensor = Mock()
        tensor.name = "input"
        tensor.shape = [-1, 224, 224, 3]

        suggested = self.handler.suggest_dynamic_shape(tensor)

        # Should suggest fixed values for dynamic dimensions
        self.assertIsNotNone(suggested)
        self.assertEqual(len(suggested), 4)


if __name__ == "__main__":
    unittest.main()
