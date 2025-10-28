"""
基准测试执行器 (Benchmark Runner)

负责管理性能测试的生命周期，协调测试用例的执行，处理并发和分布式测试，
记录测试执行日志。

作者: BMAD Method
创建日期: 2025-10-29
版本: v1.0
"""

import time
import json
import logging
import asyncio
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from pathlib import Path
import yaml

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class BenchmarkConfig:
    """基准测试配置"""
    test_timeout: int = 3600  # 测试超时时间（秒）
    max_concurrent: int = 10  # 最大并发数
    retry_count: int = 3  # 重试次数
    retry_delay: int = 5  # 重试延迟（秒）
    cleanup_after_test: bool = True  # 测试后清理
    save_raw_data: bool = True  # 保存原始数据
    output_dir: str = "reports/performance"  # 输出目录


@dataclass
class TestCase:
    """测试用例"""
    id: str
    name: str
    description: str
    category: str
    model_type: str
    parameters: Dict[str, Any]
    expected_results: Dict[str, Any]
    timeout: Optional[int] = None
    tags: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None

    def __post_init__(self):
        if self.timeout is None:
            self.timeout = 3600
        if self.tags is None:
            self.tags = []
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class TestResult:
    """测试结果"""
    test_id: str
    test_name: str
    status: str  # 'success', 'failure', 'timeout', 'skipped', 'error'
    start_time: datetime
    end_time: datetime
    duration: float
    metrics: Dict[str, Any]
    error_message: Optional[str] = None
    error_trace: Optional[str] = None
    output_data: Optional[Dict[str, Any]] = None

    @property
    def success(self) -> bool:
        return self.status == 'success'


@dataclass
class BenchmarkResult:
    """基准测试结果"""
    benchmark_id: str
    test_case: TestCase
    result: TestResult
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'benchmark_id': self.benchmark_id,
            'test_case': asdict(self.test_case),
            'result': {
                'test_id': self.result.test_id,
                'test_name': self.result.test_name,
                'status': self.result.status,
                'start_time': self.result.start_time.isoformat(),
                'end_time': self.result.end_time.isoformat(),
                'duration': self.result.duration,
                'metrics': self.result.metrics,
                'error_message': self.result.error_message,
                'output_data': self.result.output_data
            },
            'metadata': self.metadata
        }


@dataclass
class ConcurrentBenchmarkResult:
    """并发基准测试结果"""
    batch_id: str
    results: List[BenchmarkResult]
    start_time: datetime
    end_time: datetime
    total_duration: float
    total_tests: int
    successful_tests: int
    failed_tests: int

    @property
    def success_rate(self) -> float:
        if self.total_tests == 0:
            return 0.0
        return (self.successful_tests / self.total_tests) * 100

    def to_dict(self) -> Dict[str, Any]:
        return {
            'batch_id': self.batch_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'total_duration': self.total_duration,
            'total_tests': self.total_tests,
            'successful_tests': self.successful_tests,
            'failed_tests': self.failed_tests,
            'success_rate': self.success_rate,
            'results': [r.to_dict() for r in self.results]
        }


class BenchmarkRunner:
    """
    基准测试执行器

    管理性能测试的生命周期，协调测试用例的执行，
    支持并发和分布式测试，提供详细的执行日志。
    """

    def __init__(self, config: BenchmarkConfig):
        """
        初始化基准测试执行器

        Args:
            config: 基准测试配置
        """
        self.config = config
        self.test_suite = None  # 将由BenchmarkSuite设置
        self.metrics_collector = None  # 将由MetricsCollector设置
        self._lock = threading.Lock()
        self._active_tests: Dict[str, Future] = {}

        # 创建输出目录
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)

        logger.info(f"Benchmark Runner initialized with config: {asdict(config)}")

    def set_test_suite(self, test_suite):
        """
        设置测试用例套件

        Args:
            test_suite: BenchmarkSuite实例
        """
        self.test_suite = test_suite
        logger.info("Test suite registered")

    def set_metrics_collector(self, metrics_collector):
        """
        设置指标采集器

        Args:
            metrics_collector: MetricsCollector实例
        """
        self.metrics_collector = metrics_collector
        logger.info("Metrics collector registered")

    def run_benchmark(self, test_case: TestCase,
                     callback: Optional[Callable] = None) -> BenchmarkResult:
        """
        执行单个基准测试

        Args:
            test_case: 测试用例
            callback: 可选的回调函数，用于进度更新

        Returns:
            BenchmarkResult: 基准测试结果
        """
        benchmark_id = f"{test_case.id}-{int(time.time())}"
        logger.info(f"Starting benchmark: {benchmark_id}")

        start_time = datetime.now()

        try:
            # 开始指标采集
            if self.metrics_collector:
                self.metrics_collector.start_real_time_collection(interval=1)

            # 执行测试
            result = self._execute_test(test_case, callback)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # 停止指标采集
            if self.metrics_collector:
                self.metrics_collector.stop_real_time_collection()

            # 构建测试结果
            test_result = TestResult(
                test_id=test_case.id,
                test_name=test_case.name,
                status=result['status'],
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                metrics=result['metrics'],
                error_message=result.get('error_message'),
                error_trace=result.get('error_trace'),
                output_data=result.get('output_data')
            )

            benchmark_result = BenchmarkResult(
                benchmark_id=benchmark_id,
                test_case=test_case,
                result=test_result,
                metadata={
                    'config': asdict(self.config),
                    'executor': 'BenchmarkRunner'
                }
            )

            # 保存结果
            self._save_result(benchmark_result)

            logger.info(f"Benchmark completed: {benchmark_id}, "
                       f"status={test_result.status}, duration={duration:.2f}s")

            return benchmark_result

        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            logger.error(f"Benchmark failed: {benchmark_id}, error={str(e)}",
                        exc_info=True)

            test_result = TestResult(
                test_id=test_case.id,
                test_name=test_case.name,
                status='error',
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                metrics={},
                error_message=str(e),
                error_trace=traceback.format_exc()
            )

            benchmark_result = BenchmarkResult(
                benchmark_id=benchmark_id,
                test_case=test_case,
                result=test_result,
                metadata={
                    'config': asdict(self.config),
                    'executor': 'BenchmarkRunner',
                    'error': str(e)
                }
            )

            self._save_result(benchmark_result)
            return benchmark_result

    def _execute_test(self, test_case: TestCase,
                     callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        执行单个测试用例

        Args:
            test_case: 测试用例
            callback: 进度回调函数

        Returns:
            Dict: 测试结果
        """
        max_retries = self.config.retry_count
        retry_count = 0

        while retry_count <= max_retries:
            try:
                # 检查依赖
                if test_case.dependencies:
                    self._check_dependencies(test_case.dependencies)

                # 执行测试逻辑
                if callback:
                    callback({'status': 'running', 'test_id': test_case.id})

                # 这里应该调用实际的NPU转换引擎
                # 示例实现
                result = self._run_conversion_test(test_case)

                if callback:
                    callback({'status': 'completed', 'test_id': test_case.id,
                             'result': result})

                return result

            except Exception as e:
                retry_count += 1
                if retry_count > max_retries:
                    logger.error(f"Test {test_case.id} failed after {max_retries} retries: {str(e)}")
                    raise

                logger.warning(f"Test {test_case.id} failed (attempt {retry_count}/{max_retries}), retrying in {self.config.retry_delay}s")
                time.sleep(self.config.retry_delay)

        # 不应该到达这里
        raise Exception(f"Test {test_case.id} failed after {max_retries} retries")

    def _run_conversion_test(self, test_case: TestCase) -> Dict[str, Any]:
        """
        运行转换测试（示例实现）

        Args:
            test_case: 测试用例

        Returns:
            Dict: 测试结果
        """
        logger.info(f"Running conversion test: {test_case.name}")

        # 模拟测试执行
        time.sleep(2)  # 模拟转换时间

        # 构建结果
        metrics = {
            'throughput': 12.5,  # 模型/分钟
            'latency': {'p50': 15.2, 'p95': 28.5, 'p99': 45.8},
            'cpu_utilization': 65.5,
            'memory_usage': 2145.6,  # MB
            'gpu_utilization': 78.2,
            'npu_utilization': 82.1,
            'success_rate': 100.0
        }

        return {
            'status': 'success',
            'metrics': metrics,
            'output_data': {
                'converted_models': 1,
                'total_models': 1,
                'errors': []
            }
        }

    def _check_dependencies(self, dependencies: List[str]):
        """
        检查测试依赖

        Args:
            dependencies: 依赖的测试ID列表

        Raises:
            Exception: 如果依赖不满足
        """
        for dep_id in dependencies:
            if dep_id not in self._active_tests:
                logger.warning(f"Dependency {dep_id} not found, skipping check")

    def run_suite(self, test_suite: List[TestCase],
                  callback: Optional[Callable] = None) -> List[BenchmarkResult]:
        """
        执行测试套件

        Args:
            test_suite: 测试用例列表
            callback: 进度回调函数

        Returns:
            List[BenchmarkResult]: 基准测试结果列表
        """
        logger.info(f"Running test suite with {len(test_suite)} tests")

        results = []

        for i, test_case in enumerate(test_suite, 1):
            logger.info(f"Running test {i}/{len(test_suite)}: {test_case.id}")

            if callback:
                callback({'status': 'running', 'current': i, 'total': len(test_suite),
                         'test_id': test_case.id})

            result = self.run_benchmark(test_case)
            results.append(result)

            # 检查结果，如果失败可以决定是否继续
            if not result.result.success:
                logger.warning(f"Test {test_case.id} failed, but continuing with suite")

        logger.info(f"Test suite completed: {len(results)} tests executed")

        if callback:
            callback({'status': 'completed', 'total': len(results)})

        return results

    def run_concurrent(self, test_cases: List[TestCase],
                      max_workers: Optional[int] = None,
                      callback: Optional[Callable] = None) -> ConcurrentBenchmarkResult:
        """
        并发执行多个测试

        Args:
            test_cases: 测试用例列表
            max_workers: 最大工作线程数（默认为配置中的max_concurrent）
            callback: 进度回调函数

        Returns:
            ConcurrentBenchmarkResult: 并发基准测试结果
        """
        if max_workers is None:
            max_workers = self.config.max_concurrent

        logger.info(f"Running {len(test_cases)} tests concurrently with {max_workers} workers")

        batch_id = f"batch-{int(time.time())}"
        start_time = datetime.now()

        results = []
        successful_tests = 0
        failed_tests = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            futures = {
                executor.submit(self.run_benchmark, test_case): test_case
                for test_case in test_cases
            }

            # 收集结果
            for future in as_completed(futures):
                test_case = futures[future]

                try:
                    result = future.result()
                    results.append(result)

                    if result.result.success:
                        successful_tests += 1
                    else:
                        failed_tests += 1

                    if callback:
                        callback({
                            'status': 'running',
                            'completed': len(results),
                            'total': len(test_cases),
                            'test_id': test_case.id,
                            'success': result.result.success
                        })

                except Exception as e:
                    logger.error(f"Test {test_case.id} raised an exception: {str(e)}")
                    failed_tests += 1

        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()

        concurrent_result = ConcurrentBenchmarkResult(
            batch_id=batch_id,
            results=results,
            start_time=start_time,
            end_time=end_time,
            total_duration=total_duration,
            total_tests=len(test_cases),
            successful_tests=successful_tests,
            failed_tests=failed_tests
        )

        # 保存结果
        self._save_concurrent_result(concurrent_result)

        logger.info(f"Concurrent benchmark completed: batch={batch_id}, "
                   f"success_rate={concurrent_result.success_rate:.2f}%, "
                   f"duration={total_duration:.2f}s")

        if callback:
            callback({
                'status': 'completed',
                'total': len(results),
                'success_rate': concurrent_result.success_rate
            })

        return concurrent_result

    def _save_result(self, result: BenchmarkResult):
        """
        保存单个测试结果

        Args:
            result: 基准测试结果
        """
        if not self.config.save_raw_data:
            return

        output_dir = Path(self.config.output_dir)
        results_dir = output_dir / "results"
        results_dir.mkdir(parents=True, exist_ok=True)

        result_file = results_dir / f"{result.benchmark_id}.json"

        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)

        logger.debug(f"Result saved: {result_file}")

    def _save_concurrent_result(self, result: ConcurrentBenchmarkResult):
        """
        保存并发测试结果

        Args:
            result: 并发基准测试结果
        """
        if not self.config.save_raw_data:
            return

        output_dir = Path(self.config.output_dir)
        results_dir = output_dir / "concurrent_results"
        results_dir.mkdir(parents=True, exist_ok=True)

        result_file = results_dir / f"{result.batch_id}.json"

        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)

        logger.info(f"Concurrent result saved: {result_file}")

    def generate_summary_report(self, results: List[BenchmarkResult],
                               output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        生成汇总报告

        Args:
            results: 测试结果列表
            output_file: 可选的输出文件路径

        Returns:
            Dict: 汇总报告
        """
        if not results:
            return {'error': 'No results to summarize'}

        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.result.success)
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0

        # 计算统计指标
        durations = [r.result.duration for r in results]
        total_duration = sum(durations)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0

        # 收集所有指标
        all_metrics = {}
        for result in results:
            for key, value in result.result.metrics.items():
                if key not in all_metrics:
                    all_metrics[key] = []
                all_metrics[key].append(value)

        # 计算指标统计
        metrics_stats = {}
        for key, values in all_metrics.items():
            if isinstance(values[0], (int, float)):
                metrics_stats[key] = {
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values),
                    'count': len(values)
                }

        summary = {
            'summary': {
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'failed_tests': failed_tests,
                'success_rate': success_rate,
                'total_duration': total_duration,
                'avg_duration': avg_duration
            },
            'metrics': metrics_stats,
            'test_details': [r.to_dict() for r in results]
        }

        # 保存报告
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)

            logger.info(f"Summary report saved: {output_file}")

        return summary

    def cancel_active_tests(self):
        """取消所有活动的测试"""
        with self._lock:
            for test_id, future in list(self._active_tests.items()):
                if not future.done():
                    logger.info(f"Cancelling test: {test_id}")
                    future.cancel()
            self._active_tests.clear()

    def get_status(self) -> Dict[str, Any]:
        """
        获取执行器状态

        Returns:
            Dict: 状态信息
        """
        return {
            'config': asdict(self.config),
            'active_tests': len(self._active_tests),
            'output_dir': self.config.output_dir,
            'timestamp': datetime.now().isoformat()
        }


def load_test_cases_from_yaml(yaml_file: Union[str, Path]) -> List[TestCase]:
    """
    从YAML文件加载测试用例

    Args:
        yaml_file: YAML文件路径

    Returns:
        List[TestCase]: 测试用例列表
    """
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    test_cases = []
    for item in data.get('test_cases', []):
        test_case = TestCase(
            id=item['id'],
            name=item['name'],
            description=item.get('description', ''),
            category=item.get('category', ''),
            model_type=item.get('model_type', ''),
            parameters=item.get('parameters', {}),
            expected_results=item.get('expected_results', {}),
            timeout=item.get('timeout'),
            tags=item.get('tags', []),
            dependencies=item.get('dependencies', [])
        )
        test_cases.append(test_case)

    logger.info(f"Loaded {len(test_cases)} test cases from {yaml_file}")
    return test_cases


if __name__ == "__main__":
    # 示例使用
    config = BenchmarkConfig(
        test_timeout=3600,
        max_concurrent=5,
        retry_count=3,
        output_dir="reports/performance"
    )

    runner = BenchmarkRunner(config)

    # 创建示例测试用例
    test_case = TestCase(
        id="TC-001",
        name="SenseVoice ASR转换测试",
        description="测试SenseVoice ASR模型的转换性能",
        category="single_model",
        model_type="asr",
        parameters={
            "model_path": "/models/sensevoice",
            "batch_size": 4,
            "precision": "fp16"
        },
        expected_results={
            "throughput": "> 10 models/minute",
            "latency_p95": "< 60 seconds"
        }
    )

    # 运行测试
    result = runner.run_benchmark(test_case)
    print(f"Test result: {result.result.status}")
    print(f"Metrics: {result.result.metrics}")
