"""
Strategy Recommender for Preprocessing

Recommends optimal preprocessing strategies based on model characteristics.
Extends Story 2.1.2's preprocessing capabilities with intelligent recommendations.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class PreprocessingStrategy(Enum):
    """Preprocessing strategy types"""
    NORMALIZE = "normalize"
    RESIZE = "resize"
    CROP = "crop"
    FLIP = "flip"
    CHANNEL_CONVERT = "channel_convert"
    NORMALIZE_CUSTOM = "normalize_custom"
    DENOISE = "denoise"
    PADDING = "padding"
    STANDARDIZE = "standardize"


@dataclass
class StrategyRecommendation:
    """Recommendation for a preprocessing strategy"""
    strategy: PreprocessingStrategy
    priority: int  # 1-10 (10 = highest priority)
    confidence: float  # 0.0 - 1.0
    description: str
    parameters: Dict[str, Any]
    expected_improvement: float  # Percentage
    reasoning: str


@dataclass
class StrategyAnalysisResult:
    """Result of strategy analysis"""
    model_type: str
    total_recommendations: int
    recommendations: List[StrategyRecommendation]
    best_config: Dict[str, Any]
    warnings: List[str]
    notes: List[str]


class StrategyRecommender:
    """
    Recommends preprocessing strategies based on model features.

    Analyzes model characteristics and recommends optimal preprocessing
    strategies for vision, NLP, and audio models.

    Part of the intelligent preprocessing optimization system (AC2).
    """

    def __init__(self):
        """Initialize the StrategyRecommender"""
        logger.info("Initializing StrategyRecommender")
        self.strategy_database = self._initialize_strategy_database()

    def _initialize_strategy_database(self) -> Dict[str, Dict[str, Any]]:
        """Initialize strategy recommendations database"""
        return {
            "vision": {
                "description": "Computer vision models (CNNs, ResNets, etc.)",
                "default_strategies": [
                    {
                        "strategy": PreprocessingStrategy.NORMALIZE,
                        "priority": 10,
                        "description": "Normalize using ImageNet statistics",
                        "parameters": {"mean": [0.485, 0.456, 0.406], "std": [0.229, 0.224, 0.225]},
                        "reasoning": "Standard for vision models, improves convergence"
                    },
                    {
                        "strategy": PreprocessingStrategy.RESIZE,
                        "priority": 9,
                        "description": "Resize to model input size",
                        "parameters": {"size": (224, 224)},
                        "reasoning": "Required for most vision models"
                    },
                    {
                        "strategy": PreprocessingStrategy.CHANNEL_CONVERT,
                        "priority": 7,
                        "description": "Convert channel format",
                        "parameters": {"from": "HWC", "to": "CHW"},
                        "reasoning": "Many models expect CHW format"
                    },
                    {
                        "strategy": PreprocessingStrategy.CROP,
                        "priority": 6,
                        "description": "Center crop to target size",
                        "parameters": {"size": (224, 224)},
                        "reasoning": "Improves object detection accuracy"
                    }
                ]
            },
            "nlp": {
                "description": "Natural language processing models (BERT, etc.)",
                "default_strategies": [
                    {
                        "strategy": PreprocessingStrategy.NORMALIZE_CUSTOM,
                        "priority": 10,
                        "description": "Token normalization",
                        "parameters": {"method": "lower"},
                        "reasoning": "Standardizes text input"
                    },
                    {
                        "strategy": PreprocessingStrategy.PADDING,
                        "priority": 9,
                        "description": "Pad sequences to same length",
                        "parameters": {"max_length": 512, "pad_value": 0},
                        "reasoning": "Required for batch processing"
                    },
                    {
                        "strategy": PreprocessingStrategy.STANDARDIZE,
                        "priority": 8,
                        "description": "Standardize input format",
                        "parameters": {"method": "tokenize"},
                        "reasoning": "Ensures consistent tokenization"
                    }
                ]
            },
            "audio": {
                "description": "Audio processing models (Speech, etc.)",
                "default_strategies": [
                    {
                        "strategy": PreprocessingStrategy.NORMALIZE,
                        "priority": 10,
                        "description": "Audio amplitude normalization",
                        "parameters": {"method": "peak", "peak": 1.0},
                        "reasoning": "Prevents clipping, improves SNR"
                    },
                    {
                        "strategy": PreprocessingStrategy.RESIZE,
                        "priority": 9,
                        "description": "Resize audio to target duration",
                        "parameters": {"target_duration": 3.0},
                        "reasoning": "Standardizes input length"
                    },
                    {
                        "strategy": PreprocessingStrategy.DENOISE,
                        "priority": 8,
                        "description": "Noise reduction",
                        "parameters": {"method": "spectral_gating"},
                        "reasoning": "Improves signal quality"
                    }
                ]
            },
            "generic": {
                "description": "Generic model strategies",
                "default_strategies": [
                    {
                        "strategy": PreprocessingStrategy.NORMALIZE,
                        "priority": 7,
                        "description": "General normalization",
                        "parameters": {"method": "minmax"},
                        "reasoning": "Helps with numerical stability"
                    }
                ]
            }
        }

    def recommend_strategy(self,
                          model: Any,
                          model_type: Optional[str] = None,
                          target_metric: str = "accuracy") -> StrategyAnalysisResult:
        """
        Recommend preprocessing strategies for a model.

        Args:
            model: ONNXModel instance
            model_type: Type of the model (vision, nlp, audio). Auto-detected if None
            target_metric: Target metric to optimize for (accuracy, latency, etc.)

        Returns:
            StrategyAnalysisResult with recommendations
        """
        logger.info(f"Recommending preprocessing strategies (target: {target_metric})")

        # Step 1: Detect model type if not provided
        detected_type = model_type or self._detect_model_type(model)
        logger.info(f"Model type detected: {detected_type}")

        # Step 2: Get recommendations from database
        strategies = self.strategy_database.get(detected_type, self.strategy_database["generic"])

        # Step 3: Filter and prioritize based on target metric
        filtered_strategies = self._filter_strategies(strategies, target_metric)

        # Step 4: Analyze and create recommendations
        recommendations = self._create_recommendations(filtered_strategies, target_metric, model)

        # Step 5: Generate best configuration
        best_config = self._generate_best_config(recommendations)

        # Step 6: Generate warnings and notes
        warnings, notes = self._generate_context(detected_type, recommendations, model)

        result = StrategyAnalysisResult(
            model_type=detected_type,
            total_recommendations=len(recommendations),
            recommendations=recommendations,
            best_config=best_config,
            warnings=warnings,
            notes=notes
        )

        logger.info(f"Strategy recommendation completed: {len(recommendations)} strategies recommended")
        return result

    def _detect_model_type(self, model: Any) -> str:
        """
        Detect model type from model characteristics.

        Args:
            model: ONNXModel instance

        Returns:
            Detected model type
        """
        # Extract model information
        model_info = self._extract_model_info(model)

        # Score model types
        scores = {"vision": 0, "nlp": 0, "audio": 0}

        # Check operators
        for op_type in model_info.get("operators", []):
            op_lower = op_type.lower()
            if any(keyword in op_lower for keyword in ["conv", "pool", "batch_norm", "relu"]):
                scores["vision"] += 2
            if any(keyword in op_lower for keyword in ["embedding", "attention", "transformer"]):
                scores["nlp"] += 2
            if any(keyword in op_lower for keyword in ["fft", "mfcc", "mel"]):
                scores["audio"] += 2

        # Check tensor names
        for tensor_name in model_info.get("tensor_names", []):
            tensor_lower = tensor_name.lower()
            if any(keyword in tensor_lower for keyword in ["image", "img", "pixel"]):
                scores["vision"] += 1
            if any(keyword in tensor_lower for keyword in ["token", "text", "seq"]):
                scores["nlp"] += 1
            if any(keyword in tensor_lower for keyword in ["audio", "wave", "spec"]):
                scores["audio"] += 1

        # Return type with highest score
        best_type = max(scores, key=scores.get)
        if scores[best_type] == 0:
            logger.warning("Could not detect model type, defaulting to generic")
            return "generic"

        logger.info(f"Model type scores: {scores}")
        return best_type

    def _extract_model_info(self, model: Any) -> Dict[str, Any]:
        """Extract model information for analysis"""
        model_info = {
            "operators": [],
            "tensor_names": [],
            "input_shapes": []
        }

        try:
            if hasattr(model, 'model_proto') and model.model_proto:
                if hasattr(model.model_proto, 'graph') and model.model_proto.graph:
                    graph = model.model_proto.graph

                    # Extract operators
                    for node in graph.node:
                        model_info["operators"].append(node.op_type)

                    # Extract tensor names
                    for input_info in graph.input:
                        model_info["tensor_names"].append(input_info.name)

                    # Extract input shapes
                    for input_info in graph.input:
                        if hasattr(input_info.type, 'tensor_type'):
                            shape = []
                            for dim in input_info.type.tensor_type.shape.dim:
                                if dim.HasField("dim_value"):
                                    shape.append(dim.dim_value)
                                else:
                                    shape.append(-1)  # Dynamic
                            model_info["input_shapes"].append(shape)

        except Exception as e:
            logger.warning(f"Failed to extract model info: {e}")

        return model_info

    def _filter_strategies(self, strategies: Dict[str, Any], target_metric: str) -> List[Dict[str, Any]]:
        """Filter strategies based on target metric"""
        default_strategies = strategies["default_strategies"]

        # Adjust priorities based on target metric
        for strategy in default_strategies:
            if target_metric == "accuracy":
                # Keep all normalization and resize strategies
                pass
            elif target_metric == "latency":
                # Prefer simpler strategies
                if strategy["strategy"] == PreprocessingStrategy.RESIZE:
                    strategy["priority"] -= 1
            elif target_metric == "throughput":
                # Prefer batch-friendly strategies
                pass

        # Sort by priority (descending)
        return sorted(default_strategies, key=lambda x: x["priority"], reverse=True)

    def _create_recommendations(self,
                               strategies: List[Dict[str, Any]],
                               target_metric: str,
                               model: Any) -> List[StrategyRecommendation]:
        """Create StrategyRecommendation objects"""
        recommendations = []

        for strategy_dict in strategies:
            strategy = strategy_dict["strategy"]
            priority = strategy_dict["priority"]
            description = strategy_dict["description"]
            parameters = strategy_dict["parameters"]
            reasoning = strategy_dict["reasoning"]

            # Calculate confidence based on priority and strategy
            confidence = min(1.0, priority / 10.0)

            # Estimate expected improvement
            if target_metric == "accuracy":
                expected_improvement = 2.0 + (priority / 10.0) * 8.0  # 2-10%
            elif target_metric == "latency":
                expected_improvement = 5.0 + (priority / 10.0) * 15.0  # 5-20%
            else:
                expected_improvement = 3.0 + (priority / 10.0) * 7.0  # 3-10%

            recommendation = StrategyRecommendation(
                strategy=strategy,
                priority=priority,
                confidence=confidence,
                description=description,
                parameters=parameters,
                expected_improvement=expected_improvement,
                reasoning=reasoning
            )

            recommendations.append(recommendation)

        return recommendations

    def _generate_best_config(self, recommendations: List[StrategyRecommendation]) -> Dict[str, Any]:
        """Generate best configuration from recommendations"""
        config = {}

        for rec in recommendations:
            if rec.priority >= 7:  # High priority only
                strategy_name = rec.strategy.value

                if strategy_name == "normalize":
                    config["normalize"] = True
                    if "mean" in rec.parameters:
                        config["mean"] = rec.parameters["mean"]
                    if "std" in rec.parameters:
                        config["std"] = rec.parameters["std"]
                elif strategy_name == "resize":
                    config["resize"] = rec.parameters.get("size")
                elif strategy_name == "crop":
                    config["crop"] = rec.parameters.get("size")
                elif strategy_name == "channel_convert":
                    config["channel_format"] = rec.parameters.get("to", "NCHW")

        return config

    def _generate_context(self,
                         model_type: str,
                         recommendations: List[StrategyRecommendation],
                         model: Any) -> tuple:
        """Generate warnings and notes"""
        warnings = []
        notes = []

        # Check for conflicting strategies
        resize_count = sum(1 for r in recommendations if r.strategy == PreprocessingStrategy.RESIZE)
        crop_count = sum(1 for r in recommendations if r.strategy == PreprocessingStrategy.CROP)

        if resize_count > 0 and crop_count > 0:
            warnings.append("Both resize and crop strategies recommended - may cause performance issues")

        # Add notes based on model type
        if model_type == "vision":
            notes.append("Vision models benefit greatly from normalization")
            notes.append("Consider using random augmentation for training")
        elif model_type == "nlp":
            notes.append("NLP models may need sequence padding/truncation")
            notes.append("Ensure consistent tokenization across batches")
        elif model_type == "audio":
            notes.append("Audio models require careful normalization to prevent clipping")
            notes.append("Consider noise reduction for noisy environments")

        # Add notes about model characteristics
        model_info = self._extract_model_info(model)
        if model_info.get("input_shapes"):
            first_shape = model_info["input_shapes"][0]
            if any(dim == -1 for dim in first_shape):
                notes.append("Model has dynamic input shapes - preprocessing should handle variable sizes")

        return warnings, notes

    def get_strategy_comparison(self,
                               model: Any,
                               strategies: List[str]) -> Dict[str, StrategyAnalysisResult]:
        """
        Compare multiple strategy sets.

        Args:
            model: ONNXModel instance
            strategies: List of strategy names to compare

        Returns:
            Dictionary mapping strategy name to analysis result
        """
        logger.info(f"Comparing {len(strategies)} strategy sets")

        results = {}
        for strategy_name in strategies:
            result = self.recommend_strategy(
                model=model,
                model_type=strategy_name,
                target_metric="accuracy"
            )
            results[strategy_name] = result

        return results

    def export_recommendations(self,
                              result: StrategyAnalysisResult,
                              output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Export recommendations to structured format.

        Args:
            result: StrategyAnalysisResult to export
            output_path: Optional path to save the report

        Returns:
            Dictionary with exported recommendations
        """
        export_data = {
            "model_type": result.model_type,
            "total_recommendations": result.total_recommendations,
            "best_config": result.best_config,
            "recommendations": [
                {
                    "strategy": rec.strategy.value,
                    "priority": rec.priority,
                    "confidence": rec.confidence,
                    "description": rec.description,
                    "parameters": rec.parameters,
                    "expected_improvement": rec.expected_improvement,
                    "reasoning": rec.reasoning
                }
                for rec in result.recommendations
            ],
            "warnings": result.warnings,
            "notes": result.notes
        }

        if output_path:
            try:
                import json
                with open(output_path, 'w') as f:
                    json.dump(export_data, f, indent=2)
                logger.info(f"Recommendations exported to: {output_path}")
            except Exception as e:
                logger.error(f"Failed to export recommendations: {e}")

        return export_data

