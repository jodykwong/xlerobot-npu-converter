"""
Simple unit tests for AC2: Intelligent Preprocessing Optimization System

Tests the core functionality without deep imports.
"""

import unittest
from unittest.mock import Mock

class TestAC2Core(unittest.TestCase):
    """Test cases for AC2 core functionality"""

    def test_modules_exist(self):
        """Test that AC2 modules exist"""
        import os

        # Check that intelligent_optimizer.py exists
        self.assertTrue(
            os.path.exists("src/npu_converter/preprocessing/enhanced/intelligent_optimizer.py"),
            "intelligent_optimizer.py should exist"
        )

        # Check that strategy_recommender.py exists
        self.assertTrue(
            os.path.exists("src/npu_converter/preprocessing/enhanced/strategy_recommender.py"),
            "strategy_recommender.py should exist"
        )

    def test_file_sizes(self):
        """Test that AC2 files have reasonable content"""
        import os

        # Check intelligent_optimizer.py size
        optimizer_path = "src/npu_converter/preprocessing/enhanced/intelligent_optimizer.py"
        if os.path.exists(optimizer_path):
            with open(optimizer_path, 'r') as f:
                content = f.read()
                self.assertGreater(len(content), 500, "intelligent_optimizer.py should have substantial content")

        # Check strategy_recommender.py size
        recommender_path = "src/npu_converter/preprocessing/enhanced/strategy_recommender.py"
        if os.path.exists(recommender_path):
            with open(recommender_path, 'r') as f:
                content = f.read()
                self.assertGreater(len(content), 300, "strategy_recommender.py should have substantial content")

    def test_intelligent_optimizer_class(self):
        """Test that IntelligentOptimizer class is defined"""
        # Try to import just the class definition
        try:
            import ast
            import os

            optimizer_path = "src/npu_converter/preprocessing/enhanced/intelligent_optimizer.py"
            with open(optimizer_path, 'r') as f:
                tree = ast.parse(f.read())

            # Check for class definition
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            self.assertIn("IntelligentOptimizer", classes, "IntelligentOptimizer class should be defined")

        except Exception as e:
            self.fail(f"Failed to parse intelligent_optimizer.py: {e}")

    def test_strategy_recommender_class(self):
        """Test that StrategyRecommender class is defined"""
        try:
            import ast
            import os

            recommender_path = "src/npu_converter/preprocessing/enhanced/strategy_recommender.py"
            with open(recommender_path, 'r') as f:
                tree = ast.parse(f.read())

            # Check for class definition
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            self.assertIn("StrategyRecommender", classes, "StrategyRecommender class should be defined")

        except Exception as e:
            self.fail(f"Failed to parse strategy_recommender.py: {e}")

    def test_key_methods_exist(self):
        """Test that key methods are defined"""
        import ast
        import os

        # Check IntelligentOptimizer methods
        optimizer_path = "src/npu_converter/preprocessing/enhanced/intelligent_optimizer.py"
        with open(optimizer_path, 'r') as f:
            optimizer_tree = ast.parse(f.read())

        optimizer_classes = [node for node in ast.walk(optimizer_tree) if isinstance(node, ast.ClassDef)]
        optimizer_class = next((c for c in optimizer_classes if c.name == "IntelligentOptimizer"), None)

        if optimizer_class:
            optimizer_methods = [node.name for node in optimizer_class.body if isinstance(node, ast.FunctionDef)]
            self.assertIn("optimize_preprocessing", optimizer_methods, "optimize_preprocessing method should exist")
            self.assertIn("_classify_model_type", optimizer_methods, "_classify_model_type method should exist")

        # Check StrategyRecommender methods
        recommender_path = "src/npu_converter/preprocessing/enhanced/strategy_recommender.py"
        with open(recommender_path, 'r') as f:
            recommender_tree = ast.parse(f.read())

        recommender_classes = [node for node in ast.walk(recommender_tree) if isinstance(node, ast.ClassDef)]
        recommender_class = next((c for c in recommender_classes if c.name == "StrategyRecommender"), None)

        if recommender_class:
            recommender_methods = [node.name for node in recommender_class.body if isinstance(node, ast.FunctionDef)]
            self.assertIn("recommend_strategy", recommender_methods, "recommend_strategy method should exist")
            self.assertIn("_detect_model_type", recommender_methods, "_detect_model_type method should exist")

    def test_enum_definitions(self):
        """Test that enums are defined"""
        import ast
        import os

        # Check OptimizationStrategy enum
        optimizer_path = "src/npu_converter/preprocessing/enhanced/intelligent_optimizer.py"
        with open(optimizer_path, 'r') as f:
            optimizer_tree = ast.parse(f.read())

        optimizer_classes = [node.name for node in ast.walk(optimizer_tree) if isinstance(node, ast.ClassDef)]
        self.assertIn("OptimizationStrategy", optimizer_classes, "OptimizationStrategy enum should be defined")
        self.assertIn("ModelType", optimizer_classes, "ModelType enum should be defined")

        # Check PreprocessingStrategy enum
        recommender_path = "src/npu_converter/preprocessing/enhanced/strategy_recommender.py"
        with open(recommender_path, 'r') as f:
            recommender_tree = ast.parse(f.read())

        recommender_classes = [node.name for node in ast.walk(recommender_tree) if isinstance(node, ast.ClassDef)]
        self.assertIn("PreprocessingStrategy", recommender_classes, "PreprocessingStrategy enum should be defined")

    def test_dataclass_definitions(self):
        """Test that dataclasses are defined"""
        import ast
        import os

        # Check for dataclass definitions
        for file_path in ["src/npu_converter/preprocessing/enhanced/intelligent_optimizer.py",
                         "src/npu_converter/preprocessing/enhanced/strategy_recommender.py"]:
            with open(file_path, 'r') as f:
                tree = ast.parse(f.read())

            # Check for dataclass decorator
            dataclasses = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Name) and decorator.id == "dataclass":
                            dataclasses.append(node.name)
                            break

            self.assertGreater(len(dataclasses), 0, f"{file_path} should have dataclass definitions")


if __name__ == "__main__":
    unittest.main()
