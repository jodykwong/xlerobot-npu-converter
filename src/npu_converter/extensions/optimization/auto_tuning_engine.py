"""
自动调优引擎

提供参数自动优化、调优策略和优化建议功能。
"""

import logging
import time
import random
import numpy as np
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


logger = logging.getLogger(__name__)


class TuningStrategy(Enum):
    """调优策略枚举"""
    GRID_SEARCH = "grid_search"
    RANDOM_SEARCH = "random_search"
    BAYESIAN_OPTIMIZATION = "bayesian"
    GENETIC_ALGORITHM = "genetic"
    PARTICLE_SWARM = "particle_swarm"


class OptimizationObjective(Enum):
    """优化目标枚举"""
    MAXIMIZE_ACCURACY = "maximize_accuracy"
    MINIMIZE_LATENCY = "minimize_latency"
    MAXIMIZE_THROUGHPUT = "maximize_throughput"
    MINIMIZE_MEMORY = "minimize_memory"
    BALANCED = "balanced"


@dataclass
class ParameterSpace:
    """参数空间定义"""
    name: str
    param_type: str  # "int", "float", "categorical", "boolean"
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    choices: Optional[List[Any]] = None
    default: Optional[Any] = None
    distribution: str = "uniform"  # "uniform", "log_uniform", "normal"


@dataclass
class TuningConfig:
    """调优配置"""
    strategy: TuningStrategy
    objective: OptimizationObjective
    parameter_spaces: List[ParameterSpace]
    max_iterations: int = 100
    max_evaluations: int = 1000
    convergence_threshold: float = 0.001
    early_stopping_patience: int = 10
    seed: Optional[int] = None
    parallel_evaluations: int = 1


@dataclass
class TuningResult:
    """调优结果"""
    best_parameters: Dict[str, Any]
    best_score: float
    optimization_history: List[Dict[str, Any]]
    convergence_achieved: bool
    iterations: int
    total_evaluations: int
    start_time: float
    end_time: float


class AutoTuningEngine:
    """
    自动调优引擎

    提供多种调优策略的参数自动优化功能。
    """

    def __init__(self):
        """初始化自动调优引擎"""
        self._tuning_history: List[TuningResult] = []
        self._optimization_cache: Dict[str, float] = {}
        self._statistics = {
            'tuning_sessions': 0,
            'total_iterations': 0,
            'total_evaluations': 0,
            'best_improvements': 0
        }

        # 设置随机种子
        random.seed(42)
        np.random.seed(42)

        logger.info("自动调优引擎已初始化")

    def tune_parameters(
        self,
        config: TuningConfig,
        objective_function: Callable[[Dict[str, Any]], float],
        warm_start: Optional[Dict[str, Any]] = None
    ) -> TuningResult:
        """
        执行参数调优

        Args:
            config: 调优配置
            objective_function: 目标函数 (参数 -> 分数)
            warm_start: 初始参数

        Returns:
            调优结果

        Raises:
            ValueError: 如果配置无效
        """
        try:
            # 验证配置
            if not config.parameter_spaces:
                raise ValueError("参数空间不能为空")

            if config.max_iterations <= 0:
                raise ValueError("最大迭代次数必须大于0")

            # 设置随机种子
            if config.seed is not None:
                random.seed(config.seed)
                np.random.seed(config.seed)

            start_time = time.time()
            self._statistics['tuning_sessions'] += 1

            logger.info(f"开始参数调优: 策略={config.strategy.value}, 目标={config.objective.value}")

            # 根据策略执行调优
            if config.strategy == TuningStrategy.GRID_SEARCH:
                result = self._grid_search_tune(config, objective_function, warm_start)
            elif config.strategy == TuningStrategy.RANDOM_SEARCH:
                result = self._random_search_tune(config, objective_function, warm_start)
            elif config.strategy == TuningStrategy.BAYESIAN_OPTIMIZATION:
                result = self._bayesian_tune(config, objective_function, warm_start)
            elif config.strategy == TuningStrategy.GENETIC_ALGORITHM:
                result = self._genetic_tune(config, objective_function, warm_start)
            else:
                raise ValueError(f"不支持的调优策略: {config.strategy}")

            result.end_time = time.time()
            result.total_evaluations = len(result.optimization_history)

            # 记录调优历史
            self._tuning_history.append(result)
            self._statistics['total_iterations'] += result.iterations
            self._statistics['total_evaluations'] += result.total_evaluations

            logger.info(f"参数调优完成: 迭代={result.iterations}, 评估={result.total_evaluations}, 最佳分数={result.best_score:.4f}")

            return result

        except Exception as e:
            logger.error(f"参数调优失败: {e}")
            raise

    def _grid_search_tune(
        self,
        config: TuningConfig,
        objective_function: Callable,
        warm_start: Optional[Dict[str, Any]]
    ) -> TuningResult:
        """网格搜索调优"""
        logger.info("执行网格搜索调优")

        # 生成网格点
        grid_points = self._generate_grid_points(config.parameter_spaces, config.max_iterations)

        best_score = float('-inf')
        best_params = {}
        optimization_history = []
        no_improvement_count = 0

        for i, params in enumerate(grid_points):
            # 应用warm_start
            if warm_start:
                params.update(warm_start)

            # 评估参数
            try:
                score = self._evaluate_parameters(params, objective_function)
                optimization_history.append({
                    'iteration': i + 1,
                    'parameters': params.copy(),
                    'score': score,
                    'timestamp': time.time()
                })

                # 更新最佳结果
                if self._is_better_score(score, best_score, config.objective):
                    best_score = score
                    best_params = params.copy()
                    no_improvement_count = 0
                else:
                    no_improvement_count += 1

                # 早停检查
                if no_improvement_count >= config.early_stopping_patience:
                    logger.info(f"早停: 连续 {no_improvement_count} 次无改进")
                    break

            except Exception as e:
                logger.warning(f"参数评估失败: {params}, 错误: {e}")
                continue

        return TuningResult(
            best_parameters=best_params,
            best_score=best_score,
            optimization_history=optimization_history,
            convergence_achieved=no_improvement_count < config.early_stopping_patience,
            iterations=len(optimization_history),
            total_evaluations=len(optimization_history),
            start_time=time.time(),
            end_time=0
        )

    def _random_search_tune(
        self,
        config: TuningConfig,
        objective_function: Callable,
        warm_start: Optional[Dict[str, Any]]
    ) -> TuningResult:
        """随机搜索调优"""
        logger.info("执行随机搜索调优")

        best_score = float('-inf')
        best_params = {}
        optimization_history = []
        no_improvement_count = 0

        for i in range(config.max_iterations):
            # 随机生成参数
            params = self._generate_random_parameters(config.parameter_spaces)

            # 应用warm_start
            if warm_start:
                params.update(warm_start)

            # 评估参数
            try:
                score = self._evaluate_parameters(params, objective_function)
                optimization_history.append({
                    'iteration': i + 1,
                    'parameters': params.copy(),
                    'score': score,
                    'timestamp': time.time()
                })

                # 更新最佳结果
                if self._is_better_score(score, best_score, config.objective):
                    best_score = score
                    best_params = params.copy()
                    no_improvement_count = 0
                else:
                    no_improvement_count += 1

                # 早停检查
                if no_improvement_count >= config.early_stopping_patience:
                    logger.info(f"早停: 连续 {no_improvement_count} 次无改进")
                    break

            except Exception as e:
                logger.warning(f"参数评估失败: {params}, 错误: {e}")
                continue

        return TuningResult(
            best_parameters=best_params,
            best_score=best_score,
            optimization_history=optimization_history,
            convergence_achieved=no_improvement_count < config.early_stopping_patience,
            iterations=len(optimization_history),
            total_evaluations=len(optimization_history),
            start_time=time.time(),
            end_time=0
        )

    def _bayesian_tune(
        self,
        config: TuningConfig,
        objective_function: Callable,
        warm_start: Optional[Dict[str, Any]]
    ) -> TuningResult:
        """贝叶斯优化调优（简化实现）"""
        logger.info("执行贝叶斯优化调优")

        best_score = float('-inf')
        best_params = {}
        optimization_history = []
        no_improvement_count = 0

        # 初始采样
        initial_samples = min(10, config.max_iterations // 4)

        # 初始采样阶段
        for i in range(initial_samples):
            params = self._generate_random_parameters(config.parameter_spaces)
            if warm_start:
                params.update(warm_start)

            try:
                score = self._evaluate_parameters(params, objective_function)
                optimization_history.append({
                    'iteration': i + 1,
                    'parameters': params.copy(),
                    'score': score,
                    'timestamp': time.time()
                })

                if self._is_better_score(score, best_score, config.objective):
                    best_score = score
                    best_params = params.copy()
                    no_improvement_count = 0
                else:
                    no_improvement_count += 1

            except Exception as e:
                logger.warning(f"初始采样失败: {e}")
                continue

        # 贝叶斯优化阶段（简化实现）
        for i in range(initial_samples, config.max_iterations):
            # 简化的采集函数：选择最有可能改进的区域
            params = self._select_next_point_bayesian(config.parameter_spaces, optimization_history)

            try:
                score = self._evaluate_parameters(params, objective_function)
                optimization_history.append({
                    'iteration': i + 1,
                    'parameters': params.copy(),
                    'score': score,
                    'timestamp': time.time()
                })

                if self._is_better_score(score, best_score, config.objective):
                    best_score = score
                    best_params = params.copy()
                    no_improvement_count = 0
                else:
                    no_improvement_count += 1

                if no_improvement_count >= config.early_stopping_patience:
                    logger.info(f"早停: 连续 {no_improvement_count} 次无改进")
                    break

            except Exception as e:
                logger.warning(f"贝叶斯优化采样失败: {e}")
                continue

        return TuningResult(
            best_parameters=best_params,
            best_score=best_score,
            optimization_history=optimization_history,
            convergence_achieved=no_improvement_count < config.early_stopping_patience,
            iterations=len(optimization_history),
            total_evaluations=len(optimization_history),
            start_time=time.time(),
            end_time=0
        )

    def _genetic_tune(
        self,
        config: TuningConfig,
        objective_function: Callable,
        warm_start: Optional[Dict[str, Any]]
    ) -> TuningResult:
        """遗传算法调优（简化实现）"""
        logger.info("执行遗传算法调优")

        # 初始化种群
        population_size = min(50, config.max_iterations // 4)
        population = []
        for _ in range(population_size):
            individual = self._generate_random_parameters(config.parameter_spaces)
            if warm_start:
                individual.update(warm_start)
            population.append(individual)

        best_score = float('-inf')
        best_params = {}
        optimization_history = []
        generation = 0

        while generation < config.max_iterations:
            # 评估种群
            evaluated_population = []
            for individual in population:
                try:
                    score = self._evaluate_parameters(individual, objective_function)
                    evaluated_population.append((individual, score))
                except Exception as e:
                    logger.warning(f"个体评估失败: {e}")
                    continue

            # 排序并记录最佳
            evaluated_population.sort(key=lambda x: x[1], reverse=True)
            current_best = evaluated_population[0]

            if self._is_better_score(current_best[1], best_score, config.objective):
                best_score = current_best[1]
                best_params = current_best[0].copy()

            optimization_history.append({
                'generation': generation + 1,
                'best_score': current_best[1],
                'average_score': np.mean([s for _, s in evaluated_population]),
                'timestamp': time.time()
            })

            # 生成下一代
            if generation < config.max_iterations - 1:
                # 选择
                selected = self._tournament_selection(evaluated_population, population_size // 2)

                # 交叉和变异
                new_population = []
                for i in range(0, len(selected) - 1, 2):
                    parent1, parent2 = selected[i], selected[i + 1]
                    child1, child2 = self._crossover_and_mutate(parent1[0], parent2[0], config.parameter_spaces)
                    new_population.extend([child1, child2])

                population = new_population[:population_size]

            generation += 1

        return TuningResult(
            best_parameters=best_params,
            best_score=best_score,
            optimization_history=optimization_history,
            convergence_achieved=True,
            iterations=generation,
            total_evaluations=len(evaluated_population) * generation,
            start_time=time.time(),
            end_time=0
        )

    def _generate_grid_points(self, parameter_spaces: List[ParameterSpace], max_points: int) -> List[Dict[str, Any]]:
        """生成网格点"""
        # 简化的网格生成：每个参数最多取5个值
        grid_configs = []
        for space in parameter_spaces:
            if space.param_type == "int" or space.param_type == "float":
                points = min(5, max_points)
                if space.min_value is not None and space.max_value is not None:
                    grid_configs.append({
                        'name': space.name,
                        'values': np.linspace(space.min_value, space.max_value, points).tolist()
                    })
                else:
                    grid_configs.append({'name': space.name, 'values': [space.default]})
            else:
                grid_configs.append({'name': space.name, 'values': space.choices or [space.default]})

        # 生成笛卡尔积（简化实现）
        from itertools import product
        all_combinations = list(product(*[gc['values'] for gc in grid_configs]))
        all_combinations = all_combinations[:max_points]  # 限制数量

        points = []
        for combination in all_combinations:
            point = {gc['name']: value for gc, value in zip(grid_configs, combination)}
            points.append(point)

        return points

    def _generate_random_parameters(self, parameter_spaces: List[ParameterSpace]) -> Dict[str, Any]:
        """生成随机参数"""
        params = {}
        for space in parameter_spaces:
            if space.param_type == "int":
                if space.min_value is not None and space.max_value is not None:
                    params[space.name] = random.randint(int(space.min_value), int(space.max_value))
                else:
                    params[space.name] = space.default
            elif space.param_type == "float":
                if space.min_value is not None and space.max_value is not None:
                    params[space.name] = random.uniform(space.min_value, space.max_value)
                else:
                    params[space.name] = space.default
            elif space.param_type == "categorical":
                params[space.name] = random.choice(space.choices) if space.choices else space.default
            elif space.param_type == "boolean":
                params[space.name] = random.choice([True, False])

        return params

    def _evaluate_parameters(
        self,
        params: Dict[str, Any],
        objective_function: Callable
    ) -> float:
        """评估参数"""
        # 检查缓存
        cache_key = str(sorted(params.items()))
        if cache_key in self._optimization_cache:
            return self._optimization_cache[cache_key]

        # 评估目标函数
        score = objective_function(params)

        # 缓存结果
        self._optimization_cache[cache_key] = score

        return score

    def _is_better_score(self, score1: float, score2: float, objective: OptimizationObjective) -> bool:
        """判断是否为更好的分数"""
        if objective == OptimizationObjective.MINIMIZE_LATENCY or objective == OptimizationObjective.MINIMIZE_MEMORY:
            return score1 < score2
        else:
            return score1 > score2

    def _select_next_point_bayesian(
        self,
        parameter_spaces: List[ParameterSpace],
        history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """选择下一个采样点（简化实现）"""
        # 简化的采集函数：基于历史最佳点的邻域采样
        if not history:
            return self._generate_random_parameters(parameter_spaces)

        # 找到历史最佳点
        best_history = max(history, key=lambda x: x['score'])
        best_params = best_history['parameters']

        # 在最佳点附近随机采样
        next_params = best_params.copy()
        for space in parameter_spaces:
            if space.param_type in ["int", "float"] and space.min_value is not None and space.max_value is not None:
                # 在最佳值的±10%范围内随机采样
                range_size = (space.max_value - space.min_value) * 0.1
                current_value = best_params.get(space.name, space.default)
                new_value = current_value + random.uniform(-range_size, range_size)
                next_params[space.name] = max(space.min_value, min(space.max_value, new_value))

        return next_params

    def _tournament_selection(
        self,
        evaluated_population: List[Tuple[Dict[str, Any], float]],
        selection_size: int
    ) -> List[Tuple[Dict[str, Any], float]]:
        """锦标赛选择"""
        selected = []
        for _ in range(selection_size):
            tournament_size = 3
            tournament = random.sample(evaluated_population, min(tournament_size, len(evaluated_population)))
            winner = max(tournament, key=lambda x: x[1])
            selected.append(winner)
        return selected

    def _crossover_and_mutate(
        self,
        parent1: Dict[str, Any],
        parent2: Dict[str, Any],
        parameter_spaces: List[ParameterSpace]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """交叉和变异"""
        # 单点交叉
        child1 = parent1.copy()
        child2 = parent2.copy()

        for space in parameter_spaces:
            if space.param_type in ["int", "float"]:
                # 随机交换值
                if random.random() < 0.5:
                    child1[space.name], child2[space.name] = child2[space.name], child1[space.name]

                # 变异
                if random.random() < 0.1:  # 10%变异率
                    if space.min_value is not None and space.max_value is not None:
                        mutation_range = (space.max_value - space.min_value) * 0.05
                        child1[space.name] += random.uniform(-mutation_range, mutation_range)
                        child1[space.name] = max(space.min_value, min(space.max_value, child1[space.name]))

        return child1, child2

    def get_tuning_history(self) -> List[TuningResult]:
        """
        获取调优历史

        Returns:
            调优历史列表
        """
        return self._tuning_history.copy()

    def get_best_parameters(self, algorithm_id: str) -> Optional[Dict[str, Any]]:
        """
        获取最佳参数

        Args:
            algorithm_id: 算法ID

        Returns:
            最佳参数，如果不存在则返回None
        """
        # 这里应该根据算法ID过滤历史记录
        # 简化实现：返回最近的调优结果
        if self._tuning_history:
            latest_tuning = max(self._tuning_history, key=lambda x: x.start_time)
            return latest_tuning.best_parameters

        return None

    def clear_cache(self) -> None:
        """清空优化缓存"""
        self._optimization_cache.clear()
        logger.info("优化缓存已清空")

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            统计信息字典
        """
        return {
            'tuning_sessions': self._statistics['tuning_sessions'],
            'total_iterations': self._statistics['total_iterations'],
            'total_evaluations': self._statistics['total_evaluations'],
            'cache_size': len(self._optimization_cache),
            'average_iterations_per_session': (
                self._statistics['total_iterations'] / self._statistics['tuning_sessions']
                if self._statistics['tuning_sessions'] > 0 else 0
            )
        }
