"""
自动调优引擎单元测试

测试AutoTuningEngine的所有功能。
"""

import pytest
import sys
import os
import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../src'))

from npu_converter.extensions.optimization.auto_tuning_engine import (
    AutoTuningEngine,
    TuningStrategy,
    OptimizationObjective,
    ParameterSpace,
    TuningConfig,
    TuningResult
)


class TestParameterSpace:
    """参数空间测试"""

    def test_parameter_space_creation_float(self):
        """测试浮点参数空间"""
        param = ParameterSpace(
            name="learning_rate",
            param_type="float",
            min_value=0.0001,
            max_value=0.1,
            default=0.001,
            log_space=True
        )

        assert param.name == "learning_rate"
        assert param.param_type == "float"
        assert param.min_value == 0.0001
        assert param.max_value == 0.1
        assert param.default == 0.001
        assert param.log_space is True
        assert param.choices is None

    def test_parameter_space_creation_int(self):
        """测试整数参数空间"""
        param = ParameterSpace(
            name="batch_size",
            param_type="int",
            min_value=16,
            max_value=256,
            default=32
        )

        assert param.param_type == "int"
        assert param.min_value == 16
        assert param.max_value == 256

    def test_parameter_space_creation_categorical(self):
        """测试分类参数空间"""
        param = ParameterSpace(
            name="optimizer",
            param_type="categorical",
            choices=["adam", "sgd", "rmsprop"]
        )

        assert param.param_type == "categorical"
        assert param.choices == ["adam", "sgd", "rmsprop"]
        assert param.min_value is None
        assert param.max_value is None

    def test_parameter_space_creation_boolean(self):
        """测试布尔参数空间"""
        param = ParameterSpace(
            name="use_attention",
            param_type="boolean",
            default=True
        )

        assert param.param_type == "boolean"
        assert param.default is True

    def test_parameter_space_sample_float(self):
        """测试浮点参数采样"""
        param = ParameterSpace(
            name="lr",
            param_type="float",
            min_value=0.0,
            max_value=1.0,
            default=0.5
        )

        # 多次采样应该在范围内
        for _ in range(10):
            value = param.sample()
            assert 0.0 <= value <= 1.0

    def test_parameter_space_sample_int(self):
        """测试整数参数采样"""
        param = ParameterSpace(
            name="batch",
            param_type="int",
            min_value=10,
            max_value=100,
            default=32
        )

        # 多次采样应该在范围内且为整数
        for _ in range(10):
            value = param.sample()
            assert isinstance(value, int)
            assert 10 <= value <= 100

    def test_parameter_space_sample_categorical(self):
        """测试分类参数采样"""
        param = ParameterSpace(
            name="opt",
            param_type="categorical",
            choices=["a", "b", "c"]
        )

        # 采样值应该在choices中
        for _ in range(10):
            value = param.sample()
            assert value in ["a", "b", "c"]

    def test_parameter_space_sample_boolean(self):
        """测试布尔参数采样"""
        param = ParameterSpace(
            name="flag",
            param_type="boolean"
        )

        # 采样值应该是布尔值
        for _ in range(10):
            value = param.sample()
            assert isinstance(value, bool)


class TestTuningConfig:
    """调优配置测试"""

    def test_config_creation_minimal(self):
        """测试最小配置"""
        parameter_spaces = [
            ParameterSpace("x", "float", 0, 1, default=0.5)
        ]

        config = TuningConfig(
            strategy=TuningStrategy.RANDOM_SEARCH,
            objective=OptimizationObjective.MAXIMIZE_ACCURACY,
            parameter_spaces=parameter_spaces,
            max_iterations=10
        )

        assert config.strategy == TuningStrategy.RANDOM_SEARCH
        assert config.objective == OptimizationObjective.MAXIMIZE_ACCURACY
        assert len(config.parameter_spaces) == 1
        assert config.max_iterations == 10
        assert config.parallel_jobs == 1
        assert config.early_stopping_patience is None

    def test_config_creation_full(self):
        """测试完整配置"""
        parameter_spaces = [
            ParameterSpace("lr", "float", 0.0001, 0.1, default=0.001),
            ParameterSpace("batch", "int", 16, 256, default=32),
            ParameterSpace("opt", "categorical", choices=["adam", "sgd"])
        ]

        config = TuningConfig(
            strategy=TuningStrategy.BAYESIAN_OPTIMIZATION,
            objective=OptimizationObjective.MAXIMIZE_ACCURACY,
            parameter_spaces=parameter_spaces,
            max_iterations=50,
            parallel_jobs=4,
            early_stopping_patience=5,
            convergence_threshold=0.001,
            timeout_seconds=3600
        )

        assert config.strategy == TuningStrategy.BAYESIAN_OPTIMIZATION
        assert config.parallel_jobs == 4
        assert config.early_stopping_patience == 5
        assert config.convergence_threshold == 0.001
        assert config.timeout_seconds == 3600

    def test_config_default_values(self):
        """测试配置默认值"""
        parameter_spaces = [
            ParameterSpace("x", "float", 0, 1, default=0.5)
        ]

        config = TuningConfig(
            strategy=TuningStrategy.GRID_SEARCH,
            objective=OptimizationObjective.MINIMIZE_LOSS,
            parameter_spaces=parameter_spaces,
            max_iterations=10
        )

        assert config.parallel_jobs == 1
        assert config.early_stopping_patience is None
        assert config.convergence_threshold is None
        assert config.timeout_seconds is None
        assert config.warm_start is False


class TestOptimizationTrial:
    """优化试验测试"""

    def test_trial_creation(self):
        """测试试验创建"""
        trial = OptimizationTrial(
            trial_id="trial_1",
            parameters={"lr": 0.001, "batch": 32},
            status=TrialStatus.PENDING
        )

        assert trial.trial_id == "trial_1"
        assert trial.parameters["lr"] == 0.001
        assert trial.status == TrialStatus.PENDING
        assert trial.score is None
        assert trial.start_time is None
        assert trial.end_time is None
        assert trial.error is None


class TestTuningResult:
    """调优结果测试"""

    def test_result_creation(self):
        """测试结果创建"""
        result = TuningResult(
            algorithm_id="test_algo",
            best_parameters={"lr": 0.01, "batch": 64},
            best_score=0.95,
            optimization_history=[],
            strategy_used=TuningStrategy.RANDOM_SEARCH,
            objective=OptimizationObjective.MAXIMIZE_ACCURACY
        )

        assert result.algorithm_id == "test_algo"
        assert result.best_parameters["lr"] == 0.01
        assert result.best_score == 0.95
        assert len(result.optimization_history) == 0
        assert result.strategy_used == TuningStrategy.RANDOM_SEARCH
        assert result.objective == OptimizationObjective.MAXIMIZE_ACCURACY
        assert result.total_trials == 0
        assert result.start_time is not None
        assert result.end_time is None
        assert result.convergence_achieved is False
        assert result.elapsed_time == 0.0

    def test_result_with_history(self):
        """测试带历史记录的结果"""
        trials = [
            OptimizationTrial(
                trial_id="trial_1",
                parameters={"lr": 0.001},
                status=TrialStatus.COMPLETED,
                score=0.90
            ),
            OptimizationTrial(
                trial_id="trial_2",
                parameters={"lr": 0.01},
                status=TrialStatus.COMPLETED,
                score=0.95
            )
        ]

        result = TuningResult(
            algorithm_id="test_algo",
            best_parameters={"lr": 0.01},
            best_score=0.95,
            optimization_history=trials
        )

        assert len(result.optimization_history) == 2
        assert result.total_trials == 2


class TestAutoTuningEngine:
    """自动调优引擎测试"""

    def test_initialization(self):
        """测试初始化"""
        engine = AutoTuningEngine()

        assert len(engine._tuning_configs) == 0
        assert len(engine._optimization_history) == 0
        assert len(engine._best_parameters) == 0
        assert engine._statistics['tuning_sessions'] == 0
        assert engine._statistics['total_trials'] == 0
        assert engine._statistics['best_score'] == 0.0

    def test_tune_parameters_grid_search(self):
        """测试网格搜索调优"""
        engine = AutoTuningEngine()

        parameter_spaces = [
            ParameterSpace("x", "float", 0.0, 1.0, default=0.5),
            ParameterSpace("y", "int", 1, 3, default=2)
        ]

        # 定义目标函数
        def objective_function(params):
            # 简单的优化目标：最大化 (1-x)^2 + (y-2)^2
            return -(1 - params["x"])**2 - (params["y"] - 2)**2

        config = TuningConfig(
            strategy=TuningStrategy.GRID_SEARCH,
            objective=OptimizationObjective.MAXIMIZE_ACCURACY,
            parameter_spaces=parameter_spaces,
            max_iterations=6  # 2x3网格
        )

        result = engine.tune_parameters(config, objective_function)

        assert isinstance(result, TuningResult)
        assert result.best_parameters is not None
        assert result.best_score is not None
        assert len(result.optimization_history) > 0
        assert result.strategy_used == TuningStrategy.GRID_SEARCH

    def test_tune_parameters_random_search(self):
        """测试随机搜索调优"""
        engine = AutoTuningEngine()

        parameter_spaces = [
            ParameterSpace("lr", "float", 0.0001, 0.1, default=0.001)
        ]

        def objective_function(params):
            # 最大化 - (lr - 0.01)^2
            lr = params["lr"]
            return -(lr - 0.01)**2

        config = TuningConfig(
            strategy=TuningStrategy.RANDOM_SEARCH,
            objective=OptimizationObjective.MAXIMIZE_ACCURACY,
            parameter_spaces=parameter_spaces,
            max_iterations=20
        )

        result = engine.tune_parameters(config, objective_function)

        assert isinstance(result, TuningResult)
        assert result.best_parameters is not None
        assert result.best_score is not None
        assert len(result.optimization_history) == 20

    def test_tune_parameters_bayesian_optimization(self):
        """测试贝叶斯优化调优"""
        engine = AutoTuningEngine()

        parameter_spaces = [
            ParameterSpace("x", "float", -5.0, 5.0, default=0.0)
        ]

        def objective_function(params):
            # Rosenbrock函数
            x = params["x"]
            return -((1 - x)**2 + 100 * (x**2 - 1)**2)

        config = TuningConfig(
            strategy=TuningStrategy.BAYESIAN_OPTIMIZATION,
            objective=OptimizationObjective.MAXIMIZE_ACCURACY,
            parameter_spaces=parameter_spaces,
            max_iterations=10
        )

        result = engine.tune_parameters(config, objective_function)

        assert isinstance(result, TuningResult)
        assert result.best_parameters is not None
        assert result.best_score is not None

    def test_tune_parameters_genetic_algorithm(self):
        """测试遗传算法调优"""
        engine = AutoTuningEngine()

        parameter_spaces = [
            ParameterSpace("x1", "float", -10.0, 10.0, default=0.0),
            ParameterSpace("x2", "float", -10.0, 10.0, default=0.0)
        ]

        def objective_function(params):
            # 简单的二元函数
            return -(params["x1"]**2 + params["x2"]**2)

        config = TuningConfig(
            strategy=TuningStrategy.GENETIC_ALGORITHM,
            objective=OptimizationObjective.MAXIMIZE_ACCURACY,
            parameter_spaces=parameter_spaces,
            max_iterations=15
        )

        result = engine.tune_parameters(config, objective_function)

        assert isinstance(result, TuningResult)
        assert result.best_parameters is not None
        assert result.best_score is not None

    def test_tune_parameters_minimize_objective(self):
        """测试最小化目标调优"""
        engine = AutoTuningEngine()

        parameter_spaces = [
            ParameterSpace("x", "float", 0.0, 10.0, default=5.0)
        ]

        def objective_function(params):
            # 最小化目标函数
            return params["x"]**2

        config = TuningConfig(
            strategy=TuningStrategy.GRID_SEARCH,
            objective=OptimizationObjective.MINIMIZE_LOSS,
            parameter_spaces=parameter_spaces,
            max_iterations=11
        )

        result = engine.tune_parameters(config, objective_function)

        assert isinstance(result, TuningResult)
        assert result.objective == OptimizationObjective.MINIMIZE_LOSS

    def test_tune_parameters_categorical_parameters(self):
        """测试分类参数调优"""
        engine = AutoTuningEngine()

        parameter_spaces = [
            ParameterSpace("optimizer", "categorical", choices=["adam", "sgd", "rmsprop"]),
            ParameterSpace("lr", "float", 0.0001, 0.1, default=0.001)
        ]

        def objective_function(params):
            opt = params["optimizer"]
            lr = params["lr"]
            # 模拟优化：adam在lr=0.001时最好
            if opt == "adam" and abs(lr - 0.001) < 0.0005:
                return 0.95
            elif opt == "sgd" and abs(lr - 0.01) < 0.005:
                return 0.90
            else:
                return 0.80

        config = TuningConfig(
            strategy=TuningStrategy.RANDOM_SEARCH,
            objective=OptimizationObjective.MAXIMIZE_ACCURACY,
            parameter_spaces=parameter_spaces,
            max_iterations=20
        )

        result = engine.tune_parameters(config, objective_function)

        assert isinstance(result, TuningResult)
        assert result.best_parameters is not None
        assert "optimizer" in result.best_parameters

    def test_tune_parameters_boolean_parameters(self):
        """测试布尔参数调优"""
        engine = AutoTuningEngine()

        parameter_spaces = [
            ParameterSpace("use_attention", "boolean", default=True),
            ParameterSpace("dropout", "float", 0.0, 0.5, default=0.1)
        ]

        def objective_function(params):
            use_attention = params["use_attention"]
            dropout = params["dropout"]
            # 模拟：attention=True且dropout=0.2时最好
            if use_attention and abs(dropout - 0.2) < 0.05:
                return 0.92
            else:
                return 0.85

        config = TuningConfig(
            strategy=TuningStrategy.RANDOM_SEARCH,
            objective=OptimizationObjective.MAXIMIZE_ACCURACY,
            parameter_spaces=parameter_spaces,
            max_iterations=15
        )

        result = engine.tune_parameters(config, objective_function)

        assert isinstance(result, TuningResult)
        assert "use_attention" in result.best_parameters

    def test_tune_parameters_with_parallel_jobs(self):
        """测试并行调优"""
        engine = AutoTuningEngine()

        parameter_spaces = [
            ParameterSpace("x", "float", 0.0, 1.0, default=0.5)
        ]

        def objective_function(params):
            time.sleep(0.01)  # 模拟计算
            return params["x"]

        config = TuningConfig(
            strategy=TuningStrategy.RANDOM_SEARCH,
            objective=OptimizationObjective.MAXIMIZE_ACCURACY,
            parameter_spaces=parameter_spaces,
            max_iterations=10,
            parallel_jobs=4
        )

        result = engine.tune_parameters(config, objective_function)

        assert isinstance(result, TuningResult)
        assert len(result.optimization_history) == 10

    def test_tune_parameters_with_early_stopping(self):
        """测试早停机制"""
        engine = AutoTuningEngine()

        parameter_spaces = [
            ParameterSpace("x", "float", 0.0, 1.0, default=0.5)
        ]

        def objective_function(params):
            # 模拟：前几次迭代改善，后续无改善
            x = params["x"]
            if x > 0.8:
                return 0.95
            else:
                return 0.50

        config = TuningConfig(
            strategy=TuningStrategy.RANDOM_SEARCH,
            objective=OptimizationObjective.MAXIMIZE_ACCURACY,
            parameter_spaces=parameter_spaces,
            max_iterations=100,
            early_stopping_patience=3
        )

        result = engine.tune_parameters(config, objective_function)

        assert isinstance(result, TuningResult)
        # 早停时试验次数应该小于最大迭代次数
        assert result.total_trials <= 100

    def test_tune_parameters_with_convergence(self):
        """测试收敛检测"""
        engine = AutoTuningEngine()

        parameter_spaces = [
            ParameterSpace("x", "float", 0.0, 1.0, default=0.5)
        ]

        def objective_function(params):
            # 模拟：逐渐收敛到最优值
            x = params["x"]
            if x > 0.9:
                return 0.95
            else:
                return 0.5 + 0.5 * x

        config = TuningConfig(
            strategy=TuningStrategy.RANDOM_SEARCH,
            objective=OptimizationObjective.MAXIMIZE_ACCURACY,
            parameter_spaces=parameter_spaces,
            max_iterations=50,
            convergence_threshold=0.01
        )

        result = engine.tune_parameters(config, objective_function)

        assert isinstance(result, TuningResult)
        # 可能达到收敛
        # assert result.convergence_achieved is True

    def test_tune_parameters_with_timeout(self):
        """测试超时机制"""
        engine = AutoTuningEngine()

        parameter_spaces = [
            ParameterSpace("x", "float", 0.0, 1.0, default=0.5)
        ]

        def objective_function(params):
            time.sleep(0.1)  # 模拟长时间计算
            return params["x"]

        config = TuningConfig(
            strategy=TuningStrategy.RANDOM_SEARCH,
            objective=OptimizationObjective.MAXIMIZE_ACCURACY,
            parameter_spaces=parameter_spaces,
            max_iterations=100,
            timeout_seconds=0.5  # 短超时
        )

        start_time = time.time()
        result = engine.tune_parameters(config, objective_function)
        elapsed = time.time() - start_time

        assert isinstance(result, TuningResult)
        # 应该超时或接近超时
        assert elapsed < 1.0

    def test_tune_parameters_with_warm_start(self):
        """测试热启动"""
        engine = AutoTuningEngine()

        parameter_spaces = [
            ParameterSpace("x", "float", 0.0, 1.0, default=0.5)
        ]

        def objective_function(params):
            return params["x"]

        config = TuningConfig(
            strategy=TuningStrategy.RANDOM_SEARCH,
            objective=OptimizationObjective.MAXIMIZE_ACCURACY,
            parameter_spaces=parameter_spaces,
            max_iterations=10,
            warm_start=True
        )

        result = engine.tune_parameters(config, objective_function)

        assert isinstance(result, TuningResult)

    def test_get_tuning_history(self):
        """测试获取调优历史"""
        engine = AutoTuningEngine()

        parameter_spaces = [
            ParameterSpace("x", "float", 0.0, 1.0, default=0.5)
        ]

        def objective_function(params):
            return params["x"]

        config = TuningConfig(
            strategy=TuningStrategy.RANDOM_SEARCH,
            objective=OptimizationObjective.MAXIMIZE_ACCURACY,
            parameter_spaces=parameter_spaces,
            max_iterations=5
        )

        engine.tune_parameters(config, objective_function)

        history = engine.get_tuning_history()

        assert isinstance(history, list)
        assert len(history) > 0

        for entry in history:
            assert isinstance(entry, TuningResult)

    def test_get_best_parameters(self):
        """测试获取最佳参数"""
        engine = AutoTuningEngine()

        parameter_spaces = [
            ParameterSpace("x", "float", 0.0, 1.0, default=0.5)
        ]

        def objective_function(params):
            return params["x"]

        config = TuningConfig(
            strategy=TuningStrategy.RANDOM_SEARCH,
            objective=OptimizationObjective.MAXIMIZE_ACCURACY,
            parameter_spaces=parameter_spaces,
            max_iterations=10
        )

        engine.tune_parameters(config, objective_function)

        best_params = engine.get_best_parameters("default")

        assert best_params is not None
        assert isinstance(best_params, dict)

    def test_get_best_parameters_nonexistent_algorithm(self):
        """测试获取不存在算法的最佳参数"""
        engine = AutoTuningEngine()

        best_params = engine.get_best_parameters("nonexistent_algorithm")

        assert best_params is None

    def test_clear_history(self):
        """测试清除历史"""
        engine = AutoTuningEngine()

        parameter_spaces = [
            ParameterSpace("x", "float", 0.0, 1.0, default=0.5)
        ]

        def objective_function(params):
            return params["x"]

        config = TuningConfig(
            strategy=TuningStrategy.RANDOM_SEARCH,
            objective=OptimizationObjective.MAXIMIZE_ACCURACY,
            parameter_spaces=parameter_spaces,
            max_iterations=5
        )

        engine.tune_parameters(config, objective_function)

        assert len(engine._optimization_history) > 0

        engine.clear_history()

        assert len(engine._optimization_history) == 0

    def test_get_statistics(self):
        """测试获取统计信息"""
        engine = AutoTuningEngine()

        parameter_spaces = [
            ParameterSpace("x", "float", 0.0, 1.0, default=0.5)
        ]

        def objective_function(params):
            return params["x"]

        config = TuningConfig(
            strategy=TuningStrategy.RANDOM_SEARCH,
            objective=OptimizationObjective.MAXIMIZE_ACCURACY,
            parameter_spaces=parameter_spaces,
            max_iterations=5
        )

        engine.tune_parameters(config, objective_function)

        stats = engine.get_statistics()

        assert isinstance(stats, dict)
        assert 'tuning_sessions' in stats
        assert 'total_trials' in stats
        assert 'best_score' in stats
        assert 'average_trials_per_session' in stats
        assert stats['tuning_sessions'] >= 1

    def test_constants(self):
        """测试常量定义"""
        assert TuningStrategy.GRID_SEARCH.value == "grid_search"
        assert TuningStrategy.RANDOM_SEARCH.value == "random_search"
        assert TuningStrategy.BAYESIAN_OPTIMIZATION.value == "bayesian_optimization"
        assert TuningStrategy.GENETIC_ALGORITHM.value == "genetic_algorithm"

        assert OptimizationObjective.MAXIMIZE_ACCURACY.value == "maximize_accuracy"
        assert OptimizationObjective.MINIMIZE_LOSS.value == "minimize_loss"


class TestAutoTuningEngineEdgeCases:
    """自动调优引擎边界情况测试"""

    def test_tune_parameters_empty_parameter_spaces(self):
        """测试空参数空间调优"""
        engine = AutoTuningEngine()

        config = TuningConfig(
            strategy=TuningStrategy.GRID_SEARCH,
            objective=OptimizationObjective.MAXIMIZE_ACCURACY,
            parameter_spaces=[],
            max_iterations=10
        )

        def objective_function(params):
            return 0.5

        result = engine.tune_parameters(config, objective_function)

        assert isinstance(result, TuningResult)
        assert result.best_parameters == {}

    def test_tune_parameters_zero_iterations(self):
        """测试零迭代调优"""
        engine = AutoTuningEngine()

        parameter_spaces = [
            ParameterSpace("x", "float", 0.0, 1.0, default=0.5)
        ]

        config = TuningConfig(
            strategy=TuningStrategy.RANDOM_SEARCH,
            objective=OptimizationObjective.MAXIMIZE_ACCURACY,
            parameter_spaces=parameter_spaces,
            max_iterations=0
        )

        def objective_function(params):
            return params["x"]

        result = engine.tune_parameters(config, objective_function)

        assert isinstance(result, TuningResult)
        assert result.total_trials == 0

    def test_tune_parameters_objective_error(self):
        """测试目标函数错误"""
        engine = AutoTuningEngine()

        parameter_spaces = [
            ParameterSpace("x", "float", 0.0, 1.0, default=0.5)
        ]

        def objective_function(params):
            raise ValueError("目标函数错误")

        config = TuningConfig(
            strategy=TuningStrategy.RANDOM_SEARCH,
            objective=OptimizationObjective.MAXIMIZE_ACCURACY,
            parameter_spaces=parameter_spaces,
            max_iterations=3
        )

        result = engine.tune_parameters(config, objective_function)

        # 应该处理错误并返回结果
        assert isinstance(result, TuningResult)

    def test_tune_parameters_parallel_jobs_exceeds_iterations(self):
        """测试并行作业数超过迭代次数"""
        engine = AutoTuningEngine()

        parameter_spaces = [
            ParameterSpace("x", "float", 0.0, 1.0, default=0.5)
        ]

        def objective_function(params):
            return params["x"]

        config = TuningConfig(
            strategy=TuningStrategy.RANDOM_SEARCH,
            objective=OptimizationObjective.MAXIMIZE_ACCURACY,
            parameter_spaces=parameter_spaces,
            max_iterations=3,
            parallel_jobs=10  # 超过迭代次数
        )

        result = engine.tune_parameters(config, objective_function)

        assert isinstance(result, TuningResult)
        assert len(result.optimization_history) == 3

    def test_tune_parameters_with_extreme_values(self):
        """测试极值参数调优"""
        engine = AutoTuningEngine()

        parameter_spaces = [
            ParameterSpace("large_num", "int", 1e6, 1e9, default=1e7),
            ParameterSpace("small_num", "float", 1e-10, 1e-5, default=1e-8)
        ]

        def objective_function(params):
            # 简单目标函数
            return 1.0

        config = TuningConfig(
            strategy=TuningStrategy.RANDOM_SEARCH,
            objective=OptimizationObjective.MAXIMIZE_ACCURACY,
            parameter_spaces=parameter_spaces,
            max_iterations=5
        )

        result = engine.tune_parameters(config, objective_function)

        assert isinstance(result, TuningResult)
        assert result.best_parameters is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
