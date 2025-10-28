"""
算法建议系统

提供算法推荐、参数优化建议和最佳实践功能。
"""

import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json


logger = logging.getLogger(__name__)


class RecommendationType(Enum):
    """建议类型枚举"""
    ALGORITHM_SELECTION = "algorithm_selection"
    PARAMETER_OPTIMIZATION = "parameter_optimization"
    ARCHITECTURE_OPTIMIZATION = "architecture_optimization"
    PERFORMANCE_TUNING = "performance_tuning"
    BEST_PRACTICE = "best_practice"


class ConfidenceLevel(Enum):
    """置信度枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class Recommendation:
    """建议"""
    type: RecommendationType
    title: str
    description: str
    confidence: ConfidenceLevel
    priority: int  # 1-10, 10为最高优先级
    impact: str  # "low", "medium", "high"
    effort: str  # "low", "medium", "high"
    suggestions: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AlgorithmProfile:
    """算法画像"""
    algorithm_id: str
    category: str
    characteristics: Dict[str, Any]
    performance_metrics: Dict[str, float]
    use_cases: List[str]
    success_rate: float
    last_used: Optional[float] = None
    usage_count: int = 0


class AlgorithmRecommender:
    """
    算法建议系统

    提供智能算法推荐和优化建议功能。
    """

    def __init__(self):
        """初始化算法建议系统"""
        self._algorithm_profiles: Dict[str, AlgorithmProfile] = {}
        self._recommendation_history: List[Dict[str, Any]] = []
        self._statistics = {
            'recommendations_generated': 0,
            'algorithms_analyzed': 0,
            'knowledge_base_size': 0
        }
        self._knowledge_base = self._load_knowledge_base()

        # 初始化内置算法画像
        self._initialize_builtin_profiles()

        logger.info("算法建议系统已初始化")

    def _load_knowledge_base(self) -> Dict[str, Any]:
        """
        加载知识库

        Returns:
            知识库字典
        """
        knowledge_base = {
            'algorithm_characteristics': {
                'transformer': {
                    'best_for': ['nlp', 'sequence_modeling', 'long_sequences'],
                    'performance': {'accuracy': 0.95, 'speed': 0.6, 'memory': 0.4},
                    'parameters': {
                        'num_layers': {'recommended': 6, 'range': [1, 24]},
                        'hidden_size': {'recommended': 512, 'range': [128, 2048]},
                        'num_attention_heads': {'recommended': 8, 'range': [1, 64]}
                    },
                    'optimization_tips': [
                        "使用混合精度训练加速",
                        "启用梯度检查点节省内存",
                        "使用分布式训练处理大模型"
                    ]
                },
                'cnn': {
                    'best_for': ['image_processing', 'computer_vision', 'feature_extraction'],
                    'performance': {'accuracy': 0.93, 'speed': 0.8, 'memory': 0.6},
                    'parameters': {
                        'num_layers': {'recommended': 18, 'range': [5, 152]},
                        'kernel_size': {'recommended': 3, 'range': [1, 15]},
                        'input_size': {'recommended': 224, 'range': [32, 1024]}
                    },
                    'optimization_tips': [
                        "使用深度可分离卷积减少参数",
                        "启用批归一化提升训练稳定性",
                        "使用跳跃连接避免梯度消失"
                    ]
                },
                'rnn': {
                    'best_for': ['time_series', 'sequence_modeling', 'real_time'],
                    'performance': {'accuracy': 0.88, 'speed': 0.5, 'memory': 0.7},
                    'parameters': {
                        'num_layers': {'recommended': 3, 'range': [1, 8]},
                        'hidden_size': {'recommended': 256, 'range': [16, 2048]},
                        'max_sequence_length': {'recommended': 500, 'range': [1, 10000]}
                    },
                    'optimization_tips': [
                        "使用LSTM或GRU替代Vanilla RNN",
                        "启用梯度裁剪避免梯度爆炸",
                        "使用截断BPTT处理长序列"
                    ]
                }
            },
            'parameter_optimization_rules': {
                'performance_tradeoffs': {
                    'accuracy_vs_speed': "更高的准确率通常需要更复杂的模型和更长的推理时间",
                    'memory_vs_speed': "更快的推理速度通常需要更多的内存",
                    'batch_size_effect': "更大的批处理大小可以提高吞吐量，但会增加延迟"
                },
                'optimization_strategies': {
                    'precision': {
                        'fp32': {'accuracy': 1.0, 'speed': 1.0, 'memory': 1.0},
                        'fp16': {'accuracy': 0.995, 'speed': 1.5, 'memory': 0.5},
                        'int8': {'accuracy': 0.98, 'speed': 2.0, 'memory': 0.25}
                    }
                }
            },
            'best_practices': {
                'general': [
                    "根据具体任务选择合适的算法类型",
                    "从简单模型开始，逐步增加复杂度",
                    "使用交叉验证评估模型性能",
                    "监控模型在生产环境中的表现",
                    "定期更新和重新训练模型"
                ],
                'performance': [
                    "使用性能分析工具定位瓶颈",
                    "优化数据预处理管道",
                    "启用并行处理提升吞吐量",
                    "使用缓存减少重复计算",
                    "监控系统资源使用情况"
                ]
            }
        }

        self._statistics['knowledge_base_size'] = len(str(knowledge_base))
        return knowledge_base

    def _initialize_builtin_profiles(self) -> None:
        """初始化内置算法画像"""
        profiles = [
            AlgorithmProfile(
                algorithm_id="transformer_variant",
                category="transformation",
                characteristics={
                    "supports_long_sequences": True,
                    "parallelizable": True,
                    "memory_intensive": True,
                    "high_accuracy": True
                },
                performance_metrics={
                    "accuracy": 0.95,
                    "throughput": 50,
                    "latency": 100,
                    "memory_usage": 80
                },
                use_cases=[
                    "机器翻译",
                    "文本摘要",
                    "问答系统",
                    "代码生成"
                ],
                success_rate=0.92
            ),
            AlgorithmProfile(
                algorithm_id="cnn_improvement",
                category="optimization",
                characteristics={
                    "good_for_images": True,
                    "fast_inference": True,
                    "mobile_friendly": True,
                    "transferable": True
                },
                performance_metrics={
                    "accuracy": 0.93,
                    "throughput": 200,
                    "latency": 20,
                    "memory_usage": 40
                },
                use_cases=[
                    "图像分类",
                    "目标检测",
                    "语义分割",
                    "特征提取"
                ],
                success_rate=0.89
            ),
            AlgorithmProfile(
                algorithm_id="rnn_optimization",
                category="optimization",
                characteristics={
                    "good_for_sequences": True,
                    "real_time_capable": True,
                    "low_latency": True,
                    "sequential_dependency": True
                },
                performance_metrics={
                    "accuracy": 0.88,
                    "throughput": 30,
                    "latency": 50,
                    "memory_usage": 60
                },
                use_cases=[
                    "语音识别",
                    "时间序列预测",
                    "文本生成",
                    "情感分析"
                ],
                success_rate=0.85
            )
        ]

        for profile in profiles:
            self._algorithm_profiles[profile.algorithm_id] = profile

        logger.info(f"已初始化 {len(profiles)} 个内置算法画像")

    def register_algorithm_profile(self, profile: AlgorithmProfile) -> None:
        """
        注册算法画像

        Args:
            profile: 算法画像
        """
        self._algorithm_profiles[profile.algorithm_id] = profile
        logger.info(f"算法画像已注册: {profile.algorithm_id}")

    def recommend_algorithm(
        self,
        use_case: str,
        requirements: Optional[Dict[str, Any]] = None
    ) -> List[Recommendation]:
        """
        推荐算法

        Args:
            use_case: 使用场景
            requirements: 需求约束

        Returns:
            推荐列表

        Raises:
            ValueError: 如果需求无效
        """
        try:
            recommendations = []

            # 基于使用场景推荐
            use_case_recommendations = self._recommend_by_use_case(use_case)
            recommendations.extend(use_case_recommendations)

            # 基于需求约束推荐
            if requirements:
                requirement_recommendations = self._recommend_by_requirements(requirements)
                recommendations.extend(requirement_recommendations)

            # 基于性能特征推荐
            performance_recommendations = self._recommend_by_performance(requirements or {})
            recommendations.extend(performance_recommendations)

            # 去重并排序
            unique_recommendations = self._deduplicate_recommendations(recommendations)
            sorted_recommendations = sorted(
                unique_recommendations,
                key=lambda x: (x.priority, x.confidence.value),
                reverse=True
            )

            self._statistics['recommendations_generated'] += len(sorted_recommendations)

            logger.info(f"生成了 {len(sorted_recommendations)} 个算法推荐")
            return sorted_recommendations

        except Exception as e:
            logger.error(f"算法推荐失败: {e}")
            raise

    def _recommend_by_use_case(self, use_case: str) -> List[Recommendation]:
        """
        基于使用场景推荐

        Args:
            use_case: 使用场景

        Returns:
            推荐列表
        """
        recommendations = []

        # 匹配使用场景
        matched_profiles = []
        for profile in self._algorithm_profiles.values():
            if use_case.lower() in [uc.lower() for uc in profile.use_cases]:
                matched_profiles.append(profile)

        # 为每个匹配的图片生成推荐
        for profile in matched_profiles:
            algorithm_chars = self._knowledge_base['algorithm_characteristics'].get(
                profile.category, {}
            )

            tips = algorithm_chars.get('optimization_tips', [])
            best_for = algorithm_chars.get('best_for', [])

            recommendation = Recommendation(
                type=RecommendationType.ALGORITHM_SELECTION,
                title=f"推荐使用 {profile.algorithm_id}",
                description=f"该算法在'{use_case}'场景下表现良好，成功率: {profile.success_rate:.2%}",
                confidence=ConfidenceLevel.HIGH if profile.success_rate > 0.9 else ConfidenceLevel.MEDIUM,
                priority=9 if profile.success_rate > 0.9 else 7,
                impact="high",
                effort="medium",
                suggestions=tips[:3],  # 最多3个建议
                metadata={
                    "algorithm_id": profile.algorithm_id,
                    "success_rate": profile.success_rate,
                    "matched_use_case": use_case
                }
            )

            recommendations.append(recommendation)

        return recommendations

    def _recommend_by_requirements(self, requirements: Dict[str, Any]) -> List[Recommendation]:
        """
        基于需求推荐

        Args:
            requirements: 需求字典

        Returns:
            推荐列表
        """
        recommendations = []

        # 性能需求
        if 'accuracy' in requirements:
            accuracy_req = requirements['accuracy']
            if accuracy_req > 0.95:
                recommendations.append(Recommendation(
                    type=RecommendationType.ALGORITHM_SELECTION,
                    title="高精度需求推荐",
                    description="高精度需求建议使用Transformer系列算法",
                    confidence=ConfidenceLevel.HIGH,
                    priority=8,
                    impact="high",
                    effort="high",
                    suggestions=[
                        "选择具有高准确率的算法变体",
                        "增加模型容量提升准确率",
                        "使用集成学习提升性能"
                    ],
                    metadata={"accuracy_requirement": accuracy_req}
                ))

        # 速度需求
        if 'speed' in requirements:
            speed_req = requirements['speed']
            if speed_req > 100:  # RPS
                recommendations.append(Recommendation(
                    type=RecommendationType.PERFORMANCE_TUNING,
                    title="高速度需求优化",
                    description="高速度需求建议优化推理流程",
                    confidence=ConfidenceLevel.MEDIUM,
                    priority=7,
                    impact="medium",
                    effort="medium",
                    suggestions=[
                        "使用混合精度推理",
                        "启用批处理提升吞吐量",
                        "优化模型结构减少计算量"
                    ],
                    metadata={"speed_requirement": speed_req}
                ))

        # 内存约束
        if 'memory_limit' in requirements:
            memory_limit = requirements['memory_limit']
            if memory_limit < 100:  # MB
                recommendations.append(Recommendation(
                    type=RecommendationType.PERFORMANCE_TUNING,
                    title="内存约束优化",
                    description="内存限制下建议使用轻量级算法",
                    confidence=ConfidenceLevel.HIGH,
                    priority=8,
                    impact="high",
                    effort="medium",
                    suggestions=[
                        "选择MobileNet等轻量级架构",
                        "使用模型压缩技术",
                        "启用量化减少内存占用"
                    ],
                    metadata={"memory_limit": memory_limit}
                ))

        return recommendations

    def _recommend_by_performance(self, context: Dict[str, Any]) -> List[Recommendation]:
        """
        基于性能特征推荐

        Args:
            context: 上下文信息

        Returns:
            推荐列表
        """
        recommendations = []

        # 基于已使用的算法推荐优化
        if 'current_algorithm' in context:
            current_algo = context['current_algorithm']
            if current_algo in self._algorithm_profiles:
                profile = self._algorithm_profiles[current_algo]
                category = profile.category

                algorithm_chars = self._knowledge_base['algorithm_characteristics'].get(category, {})
                tips = algorithm_chars.get('optimization_tips', [])

                # 生成个性化建议
                recommendations.append(Recommendation(
                    type=RecommendationType.PERFORMANCE_TUNING,
                    title=f"{current_algo} 性能优化建议",
                    description=f"针对当前使用的{current_algo}算法",
                    confidence=ConfidenceLevel.MEDIUM,
                    priority=6,
                    impact="medium",
                    effort="low",
                    suggestions=tips[:2],
                    metadata={"algorithm_id": current_algo}
                ))

        return recommendations

    def _deduplicate_recommendations(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        """
        去重推荐

        Args:
            recommendations: 推荐列表

        Returns:
            去重后的推荐列表
        """
        seen = set()
        unique_recommendations = []

        for rec in recommendations:
            key = (rec.type, rec.title)
            if key not in seen:
                seen.add(key)
                unique_recommendations.append(rec)

        return unique_recommendations

    def suggest_parameters(
        self,
        algorithm_id: str,
        target_use_case: str,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        建议参数

        Args:
            algorithm_id: 算法ID
            target_use_case: 目标使用场景
            constraints: 参数约束

        Returns:
            参数建议
        """
        try:
            # 获取算法特征
            algorithm_chars = self._knowledge_base['algorithm_characteristics'].get(
                algorithm_id, {}
            )
            param_rules = algorithm_chars.get('parameters', {})

            if not param_rules:
                logger.warning(f"算法 {algorithm_id} 没有参数规则")
                return {}

            # 生成参数建议
            suggestions = {}
            for param_name, rule in param_rules.items():
                recommended = rule.get('recommended', None)
                range_info = rule.get('range', None)

                if recommended is not None:
                    # 应用约束
                    if constraints and param_name in constraints:
                        constraint_value = constraints[param_name]
                        if isinstance(constraint_value, (int, float)):
                            if range_info:
                                min_val, max_val = range_info
                                # 调整推荐值
                                if constraint_value < min_val:
                                    recommended = min_val
                                elif constraint_value > max_val:
                                    recommended = max_val

                    suggestions[param_name] = {
                        'recommended_value': recommended,
                        'range': range_info,
                        'description': f"推荐值: {recommended}"
                    }

            logger.info(f"为算法 {algorithm_id} 生成了 {len(suggestions)} 个参数建议")
            return suggestions

        except Exception as e:
            logger.error(f"参数建议失败: {e}")
            return {}

    def get_best_practices(self, category: Optional[str] = None) -> List[Recommendation]:
        """
        获取最佳实践

        Args:
            category: 分类

        Returns:
            最佳实践列表
        """
        practices = self._knowledge_base['best_practices']
        all_practices = practices.get('general', [])

        if category:
            category_practices = practices.get(category, [])
            all_practices.extend(category_practices)

        recommendations = []
        for i, practice in enumerate(all_practices):
            recommendation = Recommendation(
                type=RecommendationType.BEST_PRACTICE,
                title=f"最佳实践 #{i+1}",
                description=practice,
                confidence=ConfidenceLevel.HIGH,
                priority=5,
                impact="medium",
                effort="low",
                metadata={"category": category}
            )
            recommendations.append(recommendation)

        return recommendations

    def analyze_algorithm_compatibility(
        self,
        algorithm_id: str,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        分析算法兼容性

        Args:
            algorithm_id: 算法ID
            requirements: 需求字典

        Returns:
            兼容性分析结果
        """
        try:
            if algorithm_id not in self._algorithm_profiles:
                return {
                    'compatible': False,
                    'score': 0,
                    'reasons': [f"算法 {algorithm_id} 不存在"]
                }

            profile = self._algorithm_profiles[algorithm_id]
            score = 0
            reasons = []

            # 匹配使用场景
            if 'use_case' in requirements:
                use_case = requirements['use_case']
                if use_case in profile.use_cases:
                    score += 30
                    reasons.append(f"支持使用场景: {use_case}")
                else:
                    score -= 10
                    reasons.append(f"不完全匹配使用场景: {use_case}")

            # 性能需求匹配
            if 'accuracy' in requirements:
                accuracy_req = requirements['accuracy']
                profile_accuracy = profile.performance_metrics.get('accuracy', 0)
                if profile_accuracy >= accuracy_req:
                    score += 25
                    reasons.append(f"准确率满足需求: {profile_accuracy:.2%}")
                else:
                    score -= 20
                    reasons.append(f"准确率不足: 需要{accuracy_req:.2%}, 实际{profile_accuracy:.2%}")

            if 'speed' in requirements:
                speed_req = requirements['speed']
                profile_speed = profile.performance_metrics.get('throughput', 0)
                if profile_speed >= speed_req:
                    score += 20
                    reasons.append(f"速度满足需求: {profile_speed} RPS")
                else:
                    score -= 15
                    reasons.append(f"速度不足: 需要{speed_req} RPS, 实际{profile_speed} RPS")

            if 'memory_limit' in requirements:
                memory_req = requirements['memory_limit']
                profile_memory = profile.performance_metrics.get('memory_usage', 0)
                if profile_memory <= memory_req:
                    score += 15
                    reasons.append(f"内存使用符合约束: {profile_memory}%")
                else:
                    score -= 25
                    reasons.append(f"内存使用过高: 需要<{memory_req}%, 实际{profile_memory}%")

            # 计算最终分数
            score = max(0, min(100, score))
            compatible = score >= 50

            return {
                'compatible': compatible,
                'score': score,
                'reasons': reasons,
                'recommendations': [
                    f"兼容性分数: {score}/100",
                    f"是否推荐: {'是' if compatible else '否'}"
                ]
            }

        except Exception as e:
            logger.error(f"算法兼容性分析失败: {e}")
            return {'compatible': False, 'score': 0, 'reasons': [str(e)]}

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            统计信息字典
        """
        return {
            'registered_algorithms': len(self._algorithm_profiles),
            'recommendations_generated': self._statistics['recommendations_generated'],
            'algorithms_analyzed': self._statistics['algorithms_analyzed'],
            'knowledge_base_size_kb': self._statistics['knowledge_base_size'] / 1024,
            'recommendation_history_count': len(self._recommendation_history)
        }
