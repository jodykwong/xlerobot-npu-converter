"""
Unit tests for AC2: Intelligent Preprocessing Optimization

This test module validates:
1. IntelligentOptimizer functionality
2. StrategyRecommender functionality
3. Integration with ComprehensiveValidator
4. A/B testing and comparison features

Author: BMM v6 Test System
Date: 2025-10-28
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the source directory to the path
sys.path.insert(0, '/home/sunrise/xlerobot/src')

from npu_converter.preprocessing.enhanced.intelligent_optimizer import (
    IntelligentOptimizer,
    OptimizationStrategy,
    ModelType,
    OptimizationResult,
    OptimizationMetrics
)
from npu_converter.preprocessing.enhanced.strategy_recommender import (
    StrategyRecommender,
    PreprocessingStrategy,
    StrategyRecommendation,
    StrategyAnalysisResult
)


class TestIntelligentOptimizer(unittest.TestCase):
    """Test cases for IntelligentOptimizer"""

    def setUp(self):
        """Set up test fixtures"""
        self.optimizer = IntelligentOptimizer()
        self.mock_model = Mock()

    def test_initialization(self):
        """Test IntelligentOptimizer initialization"""
        self.assertIsInstance(self.optimizer, IntelligentOptimizer)
        self.assertIsNotNone(self.optimizer.optimization_strategies)
        self.assertIsNotNone(self.optimizer.model_patterns)

    def test_optimization_strategies(self):
        """Test that all optimization strategies are initialized"""
        strategies = list(OptimizationStrategy)
        for strategy in strategies:
            self.assertIn(strategy, self.optimizer.optimization_strategies)
            
    def test_model_type_classification(self):
        """Test model type classification"""
        # Test Vision model
        vision_keywords = self.optimizer.model_patterns[ModelType.VISION]["keywords"]
        self.assertIn("cnn", vision_keywords)
        self.assertIn("resnet", vision_keywords)
        
        # Test NLP model
        nlp_keywords = self.optimizer.model_patterns[ModelType.NLP]["keywords"]
        self.assertIn("bert", nlp_keywords)
        self.assertIn("transformer", nlp_keywords)
        
        # Test Audio model
        audio_keywords = self.optimizer.model_patterns[ModelType.AUDIO]["keywords"]
        self.assertIn("audio", audio_keywords)
        self.assertIn("mfcc", audio_keywords)

    @patch('npu_converter.preprocessing.enhanced.intelligent_optimizer.logger')
    def test_optimize_preprocessing(self, mock_logger):
        """Test preprocessing optimization"""
        from npu_converter.preprocessing.pipeline import PreprocessingConfig
        
        # Create a mock configuration
        base_config = PreprocessingConfig()
        
        # Mock the optimization process
        with patch.object(self.optimizer, '_optimize_parameters') as mock_optimize:
            mock_optimize.return_value = OptimizationResult(
                best_config=base_config,
                best_score=0.85,
                iterations=50,
                strategy=OptimizationStrategy.BAYESIAN,
                model_type=ModelType.VISION,
                improvement_percentage=15.0,
                history=[]
            )
            
            result = self.optimizer.optimize_preprocessing(
                model=self.mock_model,
                current_config=base_config,
                strategy=OptimizationStrategy.BAYESIAN,
                max_iterations=50
            )
            
            self.assertIsInstance(result, OptimizationResult)
            self.assertEqual(result.strategy, OptimizationStrategy.BAYESIAN)
            self.assertGreater(result.best_score, 0.0)

    def test_compare_strategies(self):
        """Test strategy comparison (A/B testing)"""
        from npu_converter.preprocessing.pipeline import PreprocessingConfig
        
        base_config = PreprocessingConfig()
        strategies = [OptimizationStrategy.GRID_SEARCH, OptimizationStrategy.BAYESIAN]
        
        # Mock the optimization method
        with patch.object(self.optimizer, 'optimize_preprocessing') as mock_opt:
            mock_opt.return_value = OptimizationResult(
                best_config=base_config,
                best_score=0.80,
                iterations=30,
                strategy=OptimizationStrategy.GRID_SEARCH,
                model_type=ModelType.GENERIC,
                improvement_percentage=10.0,
                history=[]
            )
            
            results = self.optimizer.compare_strategies(
                model=self.mock_model,
                base_config=base_config,
                strategies=strategies
            )
            
            self.assertIsInstance(results, dict)
            self.assertEqual(len(results), len(strategies))


class TestStrategyRecommender(unittest.TestCase):
    """Test cases for StrategyRecommender"""

    def setUp(self):
        """Set up test fixtures"""
        self.recommender = StrategyRecommender()
        self.mock_model = Mock()

    def test_initialization(self):
        """Test StrategyRecommender initialization"""
        self.assertIsInstance(self.recommender, StrategyRecommender)
        self.assertIsNotNone(self.recommender.strategy_database)

    def test_strategy_database(self):
        """Test that strategy database contains expected strategies"""
        db = self.recommender.strategy_database
        
        # Check vision strategies
        self.assertIn('vision', db)
        self.assertIn('nlp', db)
        self.assertIn('audio', db)
        
        vision_strategies = db['vision']['default_strategies']
        self.assertGreater(len(vision_strategies), 0)

    @patch('npu_converter.preprocessing.enhanced.strategy_recommender.logger')
    def test_recommend_strategies(self, mock_logger):
        """Test strategy recommendation"""
        # Mock model characteristics
        self.mock_model.model_path = Mock()
        self.mock_model.model_path.name = "test_model.onnx"
        self.mock_model.operators = [Mock(op_type="Conv"), Mock(op_type="Relu")]
        
        result = self.recommender.recommend_strategies(self.mock_model)
        
        # Result should be a StrategyAnalysisResult
        self.assertIsInstance(result, StrategyAnalysisResult)
        self.assertGreaterEqual(result.total_recommendations, 0)

    def test_recommendation_structure(self):
        """Test recommendation data structure"""
        recommendation = StrategyRecommendation(
            strategy=PreprocessingStrategy.NORMALIZE,
            priority=10,
            confidence=0.9,
            description="Normalize image data",
            parameters={"mean": [0.485, 0.456, 0.406], "std": [0.229, 0.224, 0.225]},
            expected_improvement=15.0,
            reasoning="Standard for vision models"
        )
        
        self.assertEqual(recommendation.strategy, PreprocessingStrategy.NORMALIZE)
        self.assertEqual(recommendation.priority, 10)
        self.assertGreater(recommendation.confidence, 0.0)


class TestAC2Integration(unittest.TestCase):
    """Test AC2 integration with ComprehensiveValidator"""

    def setUp(self):
        """Set up test fixtures"""
        from npu_converter.validation.comprehensive_validator import ComprehensiveValidator
        self.validator = ComprehensiveValidator()
        self.mock_model = Mock()

    def test_validator_initialization(self):
        """Test that ComprehensiveValidator initializes AC2 components"""
        self.assertIsNotNone(self.validator.intelligent_optimizer)
        self.assertIsNotNone(self.validator.strategy_recommender)
        self.assertIsInstance(self.validator.intelligent_optimizer, IntelligentOptimizer)
        self.assertIsInstance(self.validator.strategy_recommender, StrategyRecommender)

    def test_run_intelligent_optimization(self):
        """Test the _run_intelligent_optimization method"""
        # Mock the recommendation method
        with patch.object(self.validator.strategy_recommender, 'recommend_strategies') as mock_rec:
            mock_result = StrategyAnalysisResult(
                model_type='vision',
                total_recommendations=3,
                recommendations=[
                    StrategyRecommendation(
                        strategy=PreprocessingStrategy.NORMALIZE,
                        priority=10,
                        confidence=0.9,
                        description="Normalize",
                        parameters={},
                        expected_improvement=10.0,
                        reasoning="Test"
                    )
                ],
                best_config={},
                warnings=[],
                notes=[]
            )
            mock_rec.return_value = mock_result
            
            # Mock the optimization method
            from npu_converter.preprocessing.pipeline import PreprocessingConfig
            with patch.object(self.validator.intelligent_optimizer, 'optimize_preprocessing') as mock_opt:
                mock_opt.return_value = OptimizationResult(
                    best_config=PreprocessingConfig(),
                    best_score=0.85,
                    iterations=50,
                    strategy=OptimizationStrategy.BAYESIAN,
                    model_type=ModelType.VISION,
                    improvement_percentage=15.0,
                    history=[]
                )
                
                result = self.validator._run_intelligent_optimization(self.mock_model)
                
                self.assertIsInstance(result, dict)
                self.assertTrue(result.get('success', False))
                self.assertGreaterEqual(result.get('total_recommendations', 0), 0)


if __name__ == '__main__':
    # Create a test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestIntelligentOptimizer))
    suite.addTest(unittest.makeSuite(TestStrategyRecommender))
    suite.addTest(unittest.makeSuite(TestAC2Integration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("AC2 测试摘要")
    print("=" * 60)
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"成功率: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.wasSuccessful():
        print("\n✅ 所有 AC2 测试通过!")
    else:
        print("\n⚠️ 部分测试失败")
        if result.failures:
            print("\n失败的测试:")
            for test, traceback in result.failures:
                print(f"  - {test}")
        if result.errors:
            print("\n错误的测试:")
            for test, traceback in result.errors:
                print(f"  - {test}")
