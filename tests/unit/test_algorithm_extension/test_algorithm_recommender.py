"""
算法建议系统单元测试

测试AlgorithmRecommender的所有功能。
"""

import pytest
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../src'))

from npu_converter.extensions.recommendation.algorithm_recommender import (
    AlgorithmRecommender,
    RecommendationType,
    ConfidenceLevel,
    Recommendation,
    AlgorithmProfile
)


class TestRecommendation:
    """建议测试"""

    def test_recommendation_creation(self):
        """测试建议创建"""
        recommendation = Recommendation(
            type=RecommendationType.ALGORITHM_SELECTION,
            title="推荐测试",
            description="这是一个测试建议",
            confidence=ConfidenceLevel.HIGH,
            priority=8,
            impact="high",
            effort="medium"
        )

        assert recommendation.type == RecommendationType.ALGORITHM_SELECTION
        assert recommendation.title == "推荐测试"
        assert recommendation.description == "这是一个测试建议"
        assert recommendation.confidence == ConfidenceLevel.HIGH
        assert recommendation.priority == 8
        assert recommendation.impact == "high"
        assert recommendation.effort == "medium"
        assert isinstance(recommendation.suggestions, list)
        assert isinstance(recommendation.references, list)

    def test_recommendation_with_suggestions(self):
        """测试带建议的建议"""
        recommendation = Recommendation(
            type=RecommendationType.PARAMETER_OPTIMIZATION,
            title="参数优化",
            description="建议优化参数",
            confidence=ConfidenceLevel.MEDIUM,
            priority=7,
            impact="medium",
            effort="low",
            suggestions=["建议1", "建议2", "建议3"]
        )

        assert len(recommendation.suggestions) == 3

    def test_recommendation_with_references(self):
        """测试带引用的建议"""
        recommendation = Recommendation(
            type=RecommendationType.BEST_PRACTICE,
            title="最佳实践",
            description="遵循最佳实践",
            confidence=ConfidenceLevel.HIGH,
            priority=6,
            impact="medium",
            effort="low",
            references=["参考文献1", "参考文献2"]
        )

        assert len(recommendation.references) == 2


class TestAlgorithmProfile:
    """算法画像测试"""

    def test_profile_creation(self):
        """测试画像创建"""
        profile = AlgorithmProfile(
            algorithm_id="test_algo",
            category="optimization",
            characteristics={"fast": True, "accurate": False},
            performance_metrics={"accuracy": 0.85, "speed": 100},
            use_cases=["case1", "case2"],
            success_rate=0.90
        )

        assert profile.algorithm_id == "test_algo"
        assert profile.category == "optimization"
        assert profile.characteristics["fast"] is True
        assert profile.performance_metrics["accuracy"] == 0.85
        assert len(profile.use_cases) == 2
        assert profile.success_rate == 0.90

    def test_profile_with_optional_fields(self):
        """测试带可选字段的画像"""
        profile = AlgorithmProfile(
            algorithm_id="test_algo",
            category="optimization",
            characteristics={},
            performance_metrics={},
            use_cases=[],
            success_rate=0.90,
            last_used=1234567890.0,
            usage_count=100
        )

        assert profile.last_used == 1234567890.0
        assert profile.usage_count == 100


class TestAlgorithmRecommender:
    """算法建议系统测试"""

    def test_initialization(self):
        """测试初始化"""
        recommender = AlgorithmRecommender()

        assert len(recommender._algorithm_profiles) > 0
        assert "transformer_variant" in recommender._algorithm_profiles
        assert "cnn_improvement" in recommender._algorithm_profiles
        assert "rnn_optimization" in recommender._algorithm_profiles
        assert recommender._knowledge_base is not None
        assert recommender._statistics['knowledge_base_size'] > 0

    def test_register_algorithm_profile(self):
        """测试注册算法画像"""
        recommender = AlgorithmRecommender()

        profile = AlgorithmProfile(
            algorithm_id="custom_algo",
            category="custom",
            characteristics={"custom": True},
            performance_metrics={"accuracy": 0.88},
            use_cases=["custom_case"],
            success_rate=0.85
        )

        recommender.register_algorithm_profile(profile)

        assert "custom_algo" in recommender._algorithm_profiles
        assert recommender._algorithm_profiles["custom_algo"].algorithm_id == "custom_algo"

    def test_recommend_algorithm_by_use_case(self):
        """测试基于使用场景推荐"""
        recommender = AlgorithmRecommender()

        recommendations = recommender.recommend_algorithm(
            use_case="图像分类"
        )

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

        for rec in recommendations:
            assert isinstance(rec, Recommendation)
            assert rec.type == RecommendationType.ALGORITHM_SELECTION

    def test_recommend_algorithm_by_use_case_with_requirements(self):
        """测试基于使用场景和需求推荐"""
        recommender = AlgorithmRecommender()

        recommendations = recommender.recommend_algorithm(
            use_case="机器翻译",
            requirements={"accuracy": 0.95}
        )

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

    def test_recommend_algorithm_with_high_accuracy_requirement(self):
        """测试高精度需求推荐"""
        recommender = AlgorithmRecommender()

        recommendations = recommender.recommend_algorithm(
            use_case="文本处理",
            requirements={"accuracy": 0.98}
        )

        assert isinstance(recommendations, list)

        # 应该有高精度相关建议
        high_accuracy_recs = [
            rec for rec in recommendations
            if rec.type == RecommendationType.ALGORITHM_SELECTION
            and "高精度" in rec.title
        ]
        assert len(high_accuracy_recs) > 0

    def test_recommend_algorithm_with_speed_requirement(self):
        """测试高速度需求推荐"""
        recommender = AlgorithmRecommender()

        recommendations = recommender.recommend_algorithm(
            use_case="实时处理",
            requirements={"speed": 200}
        )

        assert isinstance(recommendations, list)

        # 应该有速度相关建议
        speed_recs = [
            rec for rec in recommendations
            if rec.type == RecommendationType.PERFORMANCE_TUNING
            and "速度" in rec.title
        ]
        assert len(speed_recs) > 0

    def test_recommend_algorithm_with_memory_constraint(self):
        """测试内存约束推荐"""
        recommender = AlgorithmRecommender()

        recommendations = recommender.recommend_algorithm(
            use_case="移动应用",
            requirements={"memory_limit": 50}
        )

        assert isinstance(recommendations, list)

        # 应该有内存优化建议
        memory_recs = [
            rec for rec in recommendations
            if rec.type == RecommendationType.PERFORMANCE_TUNING
            and "内存" in rec.title
        ]
        assert len(memory_recs) > 0

    def test_recommend_algorithm_with_current_algorithm(self):
        """测试基于当前算法推荐"""
        recommender = AlgorithmRecommender()

        recommendations = recommender.recommend_algorithm(
            use_case="序列建模",
            requirements={"current_algorithm": "transformer_variant"}
        )

        assert isinstance(recommendations, list)

    def test_suggest_parameters_transformer(self):
        """测试Transformer参数建议"""
        recommender = AlgorithmRecommender()

        params = recommender.suggest_parameters(
            algorithm_id="transformer_variant",
            target_use_case="文本分类"
        )

        assert isinstance(params, dict)
        assert len(params) > 0

        # 检查推荐参数
        if "num_layers" in params:
            assert "recommended_value" in params["num_layers"]
            assert "range" in params["num_layers"]

        if "hidden_size" in params:
            assert "recommended_value" in params["hidden_size"]

    def test_suggest_parameters_cnn(self):
        """测试CNN参数建议"""
        recommender = AlgorithmRecommender()

        params = recommender.suggest_parameters(
            algorithm_id="cnn_improvement",
            target_use_case="图像分类"
        )

        assert isinstance(params, dict)
        assert len(params) > 0

    def test_suggest_parameters_rnn(self):
        """测试RNN参数建议"""
        recommender = AlgorithmRecommender()

        params = recommender.suggest_parameters(
            algorithm_id="rnn_optimization",
            target_use_case="时间序列预测"
        )

        assert isinstance(params, dict)
        assert len(params) > 0

    def test_suggest_parameters_with_constraints(self):
        """测试带约束的参数建议"""
        recommender = AlgorithmRecommender()

        params = recommender.suggest_parameters(
            algorithm_id="transformer_variant",
            target_use_case="文本分类",
            constraints={"hidden_size": 256}
        )

        assert isinstance(params, dict)

    def test_suggest_parameters_invalid_algorithm(self):
        """测试无效算法ID参数建议"""
        recommender = AlgorithmRecommender()

        params = recommender.suggest_parameters(
            algorithm_id="invalid_algo",
            target_use_case="测试"
        )

        assert params == {}

    def test_get_best_practices_general(self):
        """测试获取通用最佳实践"""
        recommender = AlgorithmRecommender()

        practices = recommender.get_best_practices()

        assert isinstance(practices, list)
        assert len(practices) > 0

        for practice in practices:
            assert isinstance(practice, Recommendation)
            assert practice.type == RecommendationType.BEST_PRACTICE

    def test_get_best_practices_performance(self):
        """测试获取性能最佳实践"""
        recommender = AlgorithmRecommender()

        practices = recommender.get_best_practices(category="performance")

        assert isinstance(practices, list)

    def test_get_best_practices_with_category(self):
        """测试获取特定分类最佳实践"""
        recommender = AlgorithmRecommender()

        general_practices = recommender.get_best_practices()
        performance_practices = recommender.get_best_practices(category="performance")

        # 性能实践可能与通用实践重叠
        assert isinstance(performance_practices, list)

    def test_analyze_algorithm_compatibility_high_score(self):
        """测试高兼容性分析"""
        recommender = AlgorithmRecommender()

        result = recommender.analyze_algorithm_compatibility(
            algorithm_id="transformer_variant",
            requirements={
                "use_case": "机器翻译",
                "accuracy": 0.90,
                "speed": 50,
                "memory_limit": 200
            }
        )

        assert isinstance(result, dict)
        assert 'compatible' in result
        assert 'score' in result
        assert 'reasons' in result
        assert 'recommendations' in result

    def test_analyze_algorithm_compatibility_low_score(self):
        """测试低兼容性分析"""
        recommender = AlgorithmRecommender()

        # 提出不兼容的需求
        result = recommender.analyze_algorithm_compatibility(
            algorithm_id="rnn_optimization",
            requirements={
                "use_case": "图像分类",  # RNN不适合图像分类
                "accuracy": 0.99,
                "speed": 1000,
                "memory_limit": 1  # 极低内存限制
            }
        )

        assert isinstance(result, dict)
        assert result['score'] >= 0
        assert isinstance(result['reasons'], list)

    def test_analyze_algorithm_compatibility_nonexistent(self):
        """测试分析不存在的算法"""
        recommender = AlgorithmRecommender()

        result = recommender.analyze_algorithm_compatibility(
            algorithm_id="nonexistent_algo",
            requirements={}
        )

        assert isinstance(result, dict)
        assert result['compatible'] is False
        assert result['score'] == 0

    def test_deduplicate_recommendations(self):
        """测试建议去重"""
        recommender = AlgorithmRecommender()

        # 创建重复建议
        rec1 = Recommendation(
            type=RecommendationType.ALGORITHM_SELECTION,
            title="重复标题",
            description="描述1",
            confidence=ConfidenceLevel.HIGH,
            priority=8,
            impact="high",
            effort="medium"
        )

        rec2 = Recommendation(
            type=RecommendationType.ALGORITHM_SELECTION,
            title="重复标题",  # 相同标题
            description="描述2",
            confidence=ConfidenceLevel.MEDIUM,
            priority=7,
            impact="medium",
            effort="medium"
        )

        rec3 = Recommendation(
            type=RecommendationType.PERFORMANCE_TUNING,
            title="不同标题",
            description="描述3",
            confidence=ConfidenceLevel.HIGH,
            priority=8,
            impact="high",
            effort="medium"
        )

        recommendations = [rec1, rec2, rec3]
        unique_recs = recommender._deduplicate_recommendations(recommendations)

        assert len(unique_recs) == 2

    def test_get_statistics(self):
        """测试获取统计信息"""
        recommender = AlgorithmRecommender()

        # 执行一些操作
        recommender.recommend_algorithm("图像分类")
        recommender.register_algorithm_profile(
            AlgorithmProfile(
                algorithm_id="test",
                category="test",
                characteristics={},
                performance_metrics={},
                use_cases=[],
                success_rate=0.9
            )
        )

        stats = recommender.get_statistics()

        assert isinstance(stats, dict)
        assert 'registered_algorithms' in stats
        assert 'recommendations_generated' in stats
        assert 'knowledge_base_size_kb' in stats
        assert stats['registered_algorithms'] >= 3  # 至少有3个内置画像

    def test_load_knowledge_base(self):
        """测试知识库加载"""
        recommender = AlgorithmRecommender()

        kb = recommender._knowledge_base

        assert isinstance(kb, dict)
        assert 'algorithm_characteristics' in kb
        assert 'parameter_optimization_rules' in kb
        assert 'best_practices' in kb

        # 检查算法特征
        algo_chars = kb['algorithm_characteristics']
        assert 'transformer' in algo_chars
        assert 'cnn' in algo_chars
        assert 'rnn' in algo_chars

    def test_initialize_builtin_profiles(self):
        """测试初始化内置画像"""
        recommender = AlgorithmRecommender()

        # 验证内置画像
        assert "transformer_variant" in recommender._algorithm_profiles
        assert "cnn_improvement" in recommender._algorithm_profiles
        assert "rnn_optimization" in recommender._algorithm_profiles

        # 验证画像属性
        transformer_profile = recommender._algorithm_profiles["transformer_variant"]
        assert transformer_profile.algorithm_id == "transformer_variant"
        assert transformer_profile.category == "transformation"
        assert len(transformer_profile.use_cases) > 0


class TestAlgorithmRecommenderEdgeCases:
    """算法建议系统边界情况测试"""

    def test_recommend_algorithm_empty_use_case(self):
        """测试空使用场景推荐"""
        recommender = AlgorithmRecommender()

        recommendations = recommender.recommend_algorithm(
            use_case=""
        )

        assert isinstance(recommendations, list)

    def test_recommend_algorithm_nonexistent_use_case(self):
        """测试不存在使用场景推荐"""
        recommender = AlgorithmRecommender()

        recommendations = recommender.recommend_algorithm(
            use_case="完全不存在的使用场景"
        )

        assert isinstance(recommendations, list)

    def test_recommend_algorithm_empty_requirements(self):
        """测试空需求推荐"""
        recommender = AlgorithmRecommender()

        recommendations = recommender.recommend_algorithm(
            use_case="文本分类",
            requirements={}
        )

        assert isinstance(recommendations, list)

    def test_suggest_parameters_empty_constraints(self):
        """测试空约束参数建议"""
        recommender = AlgorithmRecommender()

        params = recommender.suggest_parameters(
            algorithm_id="transformer_variant",
            target_use_case="文本分类",
            constraints={}
        )

        assert isinstance(params, dict)

    def test_recommend_algorithm_with_all_requirements(self):
        """测试带全部需求的推荐"""
        recommender = AlgorithmRecommender()

        recommendations = recommender.recommend_algorithm(
            use_case="序列建模",
            requirements={
                "accuracy": 0.95,
                "speed": 100,
                "memory_limit": 100,
                "current_algorithm": "transformer_variant"
            }
        )

        assert isinstance(recommendations, list)

    def test_multiple_recommendation_calls(self):
        """测试多次调用推荐"""
        recommender = AlgorithmRecommender()

        # 第一次推荐
        recs1 = recommender.recommend_algorithm("图像分类")
        count1 = recommender._statistics['recommendations_generated']

        # 第二次推荐
        recs2 = recommender.recommend_algorithm("文本分类")
        count2 = recommender._statistics['recommendations_generated']

        assert count2 > count1

    def test_get_best_practices_none_category(self):
        """测试无分类最佳实践"""
        recommender = AlgorithmRecommender()

        practices = recommender.get_best_practices(category=None)

        assert isinstance(practices, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
